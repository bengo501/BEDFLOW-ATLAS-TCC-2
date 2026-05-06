# modo terminal: listar malhas geradas e abrir no browser, open3d ou blender
from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from bed_wizard import BedWizard

_REPO = Path(__file__).resolve().parent.parent
_DSL_DIR = Path(__file__).resolve().parent
# dsl/ antes da raiz: em sys.path[0] existe bed_wizard.py atalho sem _WizardCancelled
for _p in (_REPO, _DSL_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from bedflow_local_paths import resolve_validated_mesh_path, scan_project_mesh_files  # noqa: E402
from bed_wizard import _WizardCancelled  # noqa: E402


def _env_frontend_url() -> str:
    return os.environ.get("BEDFLOW_VIEWER_FRONTEND_URL", "http://localhost:5173").rstrip("/")


def _env_api_url() -> str:
    return os.environ.get("BEDFLOW_API_URL", "http://localhost:8000").rstrip("/")


def _try_http_ok(url: str, timeout: float = 1.5) -> bool:
    try:
        from urllib.request import urlopen

        with urlopen(url, timeout=timeout) as r:
            return 200 <= (getattr(r, "status", 200) or 200) < 500
    except Exception:
        return False


def _format_size(n: int) -> str:
    if n < 1024:
        return f"{n} b"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} kb"
    return f"{n / (1024 * 1024):.1f} mb"


def run_visualization_mode(wizard: BedWizard) -> None:
    ui = wizard.ui
    rows = scan_project_mesh_files(max_files=500)
    if not rows:
        ui.warn(
            "nenhuma malha encontrada em local_data/models_3d, generated/3d/output, "
            "simulations, aux ou batch. gere um modelo primeiro."
        )
        ui.pause("enter...")
        return

    try:
        from rich.table import Table
        from rich.panel import Panel
        from rich import box as rich_box
    except ImportError:
        Table = None  # type: ignore

    while True:
        ui.clear()
        wizard.print_header(
            wizard._t("view3d.title", "visualizacao 3d"),
            wizard._t("view3d.subtitle", "malhas geradas pelo projeto"),
        )
        ui.breadcrumbs("wizard", wizard._t("view3d.crumb", "visualizacao 3d"))
        ui.println()
        ui.muted(wizard._t("view3d.scan_hint", ""))
        ui.println()

        q = ui.ask_line(
            wizard._t(
                "view3d.search",
                "pesquisar (vazio=tudo, l=lista, c=menu principal): ",
            )
        ).strip()
        if q.lower() == "c":
            return
        filtered: List[Dict[str, Any]] = list(rows)
        qnorm = q.lower()
        # "lista" e sinonimos nao sao filtro — o utilizador espera ver todos os ficheiros
        if q and qnorm not in ("lista", "list", "l", "todos", "all", "*"):
            ql = qnorm
            filtered = [
                r
                for r in rows
                if ql in r["relative_path"].lower() or ql in r["filename"].lower()
            ]

        filtered = filtered[:80]
        _console = getattr(ui, "console", None)
        if Table is not None and _console is not None:
            table = Table(
                box=rich_box.ROUNDED,
                title=wizard._t("view3d.table_title", "modelos"),
                show_lines=True,
            )
            table.add_column("#", style="bold", justify="right")
            table.add_column("ficheiro")
            table.add_column("formato", justify="center")
            table.add_column("tamanho", justify="right")
            table.add_column("mesh_id", overflow="fold")
            for i, r in enumerate(filtered, start=1):
                table.add_row(
                    str(i),
                    r["filename"],
                    r["format"],
                    _format_size(int(r["size_bytes"])),
                    r["mesh_id"],
                )
            _console.print(table)
        else:
            for i, r in enumerate(filtered, start=1):
                ui.println(f"  {i:2}  [{r['format']}]  {r['filename']}  ({r['mesh_id']})")

        ui.println()
        pick = ui.ask_line(
            wizard._t("view3d.pick", "numero do modelo (0=rever lista, c=menu principal): ")
        ).strip()
        if pick.lower() == "c":
            return
        if pick == "0" or not pick:
            continue
        if not pick.isdigit() or int(pick) < 1 or int(pick) > len(filtered):
            ui.warn("numero invalido")
            ui.pause("enter...")
            continue
        chosen = filtered[int(pick) - 1]
        rel = chosen["relative_path"]
        mid = chosen["mesh_id"]
        abs_path = resolve_validated_mesh_path(rel)
        if abs_path is None:
            ui.err("caminho invalido")
            ui.pause("enter...")
            continue

        ui.println()
        if Table is not None and getattr(ui, "console", None) is not None:
            ui.console.print(
                Panel.fit(
                    f"[bold]{chosen['filename']}[/bold]\n"
                    f"path: {rel}\n"
                    f"id: {mid}\n"
                    f"tamanho: {_format_size(int(chosen['size_bytes']))}",
                    title=wizard._t("view3d.preview", "preview"),
                )
            )
        else:
            ui.println(f"ficheiro: {chosen['filename']}\npath: {rel}\nid: {mid}")

        ui.println()
        lab_web = wizard._t("view3d.opt.web", "navegador (three.js no frontend)")
        lab_desk = wizard._t("view3d.opt.desktop", "visualizador desktop (open3d, stl/obj/ply)")
        lab_blend = wizard._t("view3d.opt.blender", "abrir no blender")
        lab_back = wizard._t("view3d.opt.back", "voltar a lista")
        try:
            dest = wizard.get_choice(
                wizard._t("view3d.choose_dest", "onde visualizar"),
                [lab_web, lab_desk, lab_blend, lab_back],
                0,
            )
        except _WizardCancelled:
            continue
        if dest == lab_back:
            continue

        ext = abs_path.suffix.lower()
        if dest == lab_web:
            if ext == ".blend":
                ui.warn(
                    "ficheiro .blend nao carrega no three.js diretamente. "
                    "exporte gltf/glb ou use blender."
                )
                ui.pause("enter...")
                continue
            if ext not in (".stl", ".obj", ".ply", ".gltf", ".glb"):
                ui.warn("formato nao suportado no visualizador web.")
                ui.pause("enter...")
                continue
            fe = _env_frontend_url()
            api = _env_api_url()
            if not _try_http_ok(f"{api}/api/status"):
                ui.warn(
                    f"api nao respondeu em {api}. inicie: uvicorn backend.app.main:app "
                    f"e o frontend (npm run dev). url usada: {fe}"
                )
            url = f"{fe}/?meshViewerId={mid}"
            ui.ok(f"abrindo: {url}")
            webbrowser.open(url)
            ui.pause("enter...")

        elif dest == lab_desk:
            if ext == ".blend":
                ui.warn("use a opcao blender para ficheiros .blend.")
                ui.pause("enter...")
                continue
            script = _REPO / "scripts" / "python_modeling" / "mesh_viewer_desktop.py"
            if not script.is_file():
                ui.err(f"script nao encontrado: {script}")
                ui.pause("enter...")
                continue
            ui.muted(f"executando: python {script.name} {abs_path}")
            rc = subprocess.call([sys.executable, str(script), str(abs_path)])
            if rc == 2:
                ui.warn(
                    "open3d nao disponivel: na raiz do repo execute "
                    "pip install -r requirements-visualizacao.txt "
                    "(no windows pode precisar de caminhos longos ou venv curto — ver comentarios nesse ficheiro)"
                )
            elif rc != 0:
                ui.warn(f"visualizador terminou com codigo {rc}")
            ui.pause("enter...")

        elif dest == lab_blend:
            exe = wizard.find_blender_executable()
            if not exe:
                ui.warn("blender nao encontrado no path.")
                ui.pause("enter...")
                continue
            wizard.open_blender_with_file(exe, abs_path)
            ui.pause("enter...")
