# fluxo guiado testes rapidos do bed wizard com rich preview e progresso
# este ficheiro so orquestra menus e chama metodos ja existentes no bed wizard
# nao implementa algoritmos de esferas isso fica em pure generation e packed bed science
# passo tipico copiar json de trabalho ou compilar bed depois apply quick test overrides
# depois opcionalmente gerar bed completo compilar patch e correr pure python ou blender
# o utilizador escolhe cinco grupos entrada backend packing execucao pos execucao
# integracao bed wizard chama run com self ui e params atualizados
# integracao typer chama execute quick test noninteractive com caminhos e flags
# spherical packing e hexagonal tres d escolhidos no menu viram packing method no json
# rigid body so no blender com fisica queda e colisao de malhas
# comentarios em minusculas sem acentos sem pontuacao final por linha
from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from quick_test_preview import (
    ascii_cross_section_schematic,
    ascii_cross_section_with_particles,
    centers_for_histogram,
    centers_from_sidecar,
    height_distribution_lines,
    load_sidecar,
    sidecar_path_for_stl,
)
from quick_test_rich import (
    get_console,
    load_packing_report,
    progress_phase,
    render_ascii_section,
    render_blender_open_confirmation,
    render_choice_table,
    render_coordinate_table,
    render_error_panel,
    render_height_distribution,
    render_result_panel,
    render_step_title,
    render_technical_before,
    render_test_header,
    rich_available,
)
from wizard_json_loader import (
    apply_quick_test_overrides,
    export_formats_for_blender,
    json_to_wizard_params,
    load_wizard_json,
    parse_spec,
    patch_compiled_json_export,
    patch_compiled_json_slice,
    patch_compiled_json_metadata,
    patch_compiled_json_packing,
    resolve_repo_path,
)

if TYPE_CHECKING:
    from bed_wizard import BedWizard

# pasta dsl onde vive este script
_DSL_DIR = Path(__file__).resolve().parent
# raiz do repositorio um nivel acima
_REPO_ROOT = _DSL_DIR.parent
# pasta dos exemplos json de teste do empacotamento
_FIX_DIR = _REPO_ROOT / "scripts" / "python_modeling"

# tuplos tecla texto mostrado no menu packing deve bater certo com normalize packing mode
_PACKING_MENU = (
    ("1", "spherical_packing"),
    ("2", "hexagonal_3d"),
    ("3", "rigid_body"),
)


def _json_from_bed(bed_path: Path) -> Path:
    # o compilador antlr escreve json com nome bed absoluto mais sufixo json
    # exemplo foo bed vira foo bed json e nao foo json
    return Path(f"{Path(bed_path).resolve()}.json")


def _copy_work_json(src: Path) -> Path:
    # copia para cwd para nao estragar fixtures originais ao aplicar overrides
    dest = Path.cwd() / f"_quick_work_{src.stem}.json"
    shutil.copy2(src, dest)
    return dest.resolve()


def _glob_beds() -> List[Path]:
    # junta bed de dsl cwd e raiz sem duplicar caminho absoluto
    seen: Dict[str, Path] = {}
    for base in (_DSL_DIR, Path.cwd(), _REPO_ROOT):
        if not base.is_dir():
            continue
        for p in sorted(base.glob("*.bed")):
            seen[str(p.resolve())] = p.resolve()
    return sorted(seen.values(), key=lambda x: x.name.lower())


def _glob_test_jsons() -> List[Path]:
    # aceita dois padroes glob para nao perder ficheiros que nao comecam por underscore
    if not _FIX_DIR.is_dir():
        return []
    found: Dict[str, Path] = {}
    for pat in ("test*.json", "_test_*.json"):
        for p in _FIX_DIR.glob(pat):
            found[str(p.resolve())] = p.resolve()
    return sorted(found.values(), key=lambda x: x.name.lower())


def _default_backend_key(data: Optional[Dict[str, Any]]) -> str:
    # devolve tecla 1 pure ou 2 blender conforme campo generation backend no json
    if not data:
        return "1"
    gb = str(data.get("generation_backend") or "").strip().lower()
    if gb == "blender":
        return "2"
    return "1"


def _default_packing_key(data: Dict[str, Any]) -> str:
    # escolhe linha do menu que casa com packing mode ou method dentro de packing
    pm = str(
        data.get("packing_mode")
        or (data.get("packing") or {}).get("method")
        or "spherical_packing"
    ).strip()
    for key, val in _PACKING_MENU:
        if val == pm:
            return key
    return "1"


def _prompt_choice(ui: Any, default_key: str, valid: List[str]) -> str:
    # loop ate o utilizador dar tecla valida ou enter vazio para default
    keys = ", ".join(valid)
    while True:
        raw = ui.ask_line(f"opcao [{default_key}] ({keys}): ").strip()
        if not raw:
            return default_key
        if raw in valid:
            return raw
        ui.warn(f"use uma opcao valida: {keys}")


def _map_packing(menu_key: str) -> str:
    # traduz numero do menu para string canonica usada no json
    for k, val in _PACKING_MENU:
        if k == menu_key:
            return val
    return "spherical_packing"


def _map_backend(menu_key: str) -> str:
    # tecla 2 e blender qualquer outra coisa vira pure python
    return "blender" if menu_key == "2" else "pure_python"


def _resolve_json_input(raw: str, files: List[Path]) -> Optional[Path]:
    # tres vias arroba parse spec indice na lista ou caminho directo
    raw = raw.strip()
    if not raw:
        return None
    if "@" in raw:
        _label, jpath = parse_spec(raw, base=Path.cwd())
        return jpath.resolve() if jpath.is_file() else None
    if raw.isdigit() and files:
        idx = int(raw) - 1
        if 0 <= idx < len(files):
            return files[idx].resolve()
    try:
        p = resolve_repo_path(raw, base=Path.cwd())
        return p.resolve() if p.is_file() else None
    except Exception:
        return None


def _resolve_bed_input(raw: str, beds: List[Path]) -> Optional[Path]:
    # igual ao json mas sem sintaxe arroba neste fluxo
    raw = raw.strip()
    if not raw:
        return None
    if raw.isdigit() and beds:
        idx = int(raw) - 1
        if 0 <= idx < len(beds):
            return beds[idx].resolve()
    try:
        p = resolve_repo_path(raw, base=Path.cwd())
        return p.resolve() if p.is_file() else None
    except Exception:
        return None


def _post_label(key: str) -> str:
    # texto longo para o resumo tecnico antes de confirmar
    if key == "1":
        return "perguntar se abre o blender apos sucesso"
    if key == "2":
        return "abrir blender automaticamente apos sucesso"
    return "nao abrir o blender"


def _exec_label(key: str) -> str:
    # resume se vamos regenerar bed ou so consumir json atual
    return "completa (.bed + json + modelo)" if key == "2" else "rapida (apenas modelo 3d)"


def _ask_slice(ui: Any) -> Dict[str, Any]:
    # thin slice opcional para testes rapidos
    if not ui.confirm("ativar thin slice (pseudo 2d)?", default=False):
        return {}
    axis = "y"
    while True:
        raw = ui.ask_line(
            "eixo do corte: 1=x 2=y 3=z (ou letra) [2]: ",
            default="2",
        ).strip().lower()
        if raw in ("1", "x"):
            axis = "x"
            break
        if raw in ("2", "y"):
            axis = "y"
            break
        if raw in ("3", "z"):
            axis = "z"
            break
        ui.warn("use 1 ou x, 2 ou y, 3 ou z")
    thick = ui.ask_line("espessura da fatia (m) [0.002]: ", default="0.002").strip() or "0.002"
    pos = ui.ask_line("posicao central (m) [0.0]: ", default="0.0").strip() or "0.0"
    keep_only = ui.confirm("manter apenas particulas que intersectam?", default=True)
    preserve = ui.confirm("preservar coordenadas originais?", default=True)
    try:
        thick_f = float(thick)
    except Exception:
        thick_f = 0.002
    try:
        pos_f = float(pos)
    except Exception:
        pos_f = 0.0
    return {
        "slice_enabled": True,
        "slice_thickness": thick_f,
        "slice_axis": str(axis).strip().lower(),
        "slice_position": pos_f,
        "keep_only_intersecting_particles": bool(keep_only),
        "preserve_original_packing": bool(preserve),
    }


def format_equivalent_test_command(
    *,
    input_path: Path,
    backend: str,
    packing: str,
    quick: bool,
    open_blender: bool,
) -> str:
    # monta linha sugerida para repetir o mesmo teste em modo nao interativo
    parts = [
        "bedwizard",
        "test",
        "--input",
        str(input_path.resolve()),
        "--backend",
        backend,
        "--mode",
        packing,
    ]
    if not quick:
        parts.append("--full")
    if open_blender:
        parts.append("--open-blender")
    return " ".join(parts)


def execute_quick_test_noninteractive(
    wizard: "BedWizard",
    *,
    input_path: Path,
    backend: Optional[str] = None,
    packing: Optional[str] = None,
    quick: bool = True,
    open_blender: bool = False,
    verbose: bool = False,
    slice_cfg: Optional[Dict[str, Any]] = None,
) -> Tuple[int, str, str]:
    # mesmo pipeline do run interativo sem perguntas nem pausa no fim
    # usado pelo comando typer bedwizard test
    # tuplo devolve codigo saida zero ok um erro backend final packing final para montar comando equivalente
    # passo um resolver tipo de ficheiro json ou bed
    # passo dois obter work json sempre via copia ou compilacao
    # passo tres aplicar overrides de packing e generation backend no disco
    # passo quatro ramo quick so modelo ou full regerar bed patch json
    # passo cinco pure python gera stl e sidecar ou blender gera blend
    # passo seis open blender opcional segundo flags
    console = get_console(wizard.ui)
    path = input_path.resolve()
    suffix = path.suffix.lower()
    if suffix == ".json":
        input_is_json = True
        original = path
        # copia para cwd para nao corromper fixtures ao reescrever packing
        with progress_phase(console, "copiar json de trabalho"):
            work_json = _copy_work_json(original)
            data_preview = load_wizard_json(work_json)
    elif suffix == ".bed":
        input_is_json = False
        original = path
        wizard.output_file = str(original)
        with progress_phase(console, "compilar bed"):
            if not wizard.verify_and_compile():
                render_error_panel(console, "falha compilacao bed")
                return 1, "", ""
        work_json = _json_from_bed(Path(wizard.output_file))
        if not work_json.is_file():
            render_error_panel(console, f"json ausente {work_json}")
            return 1, "", ""
        data_preview = load_wizard_json(work_json)
    else:
        render_error_panel(console, "input deve ser ficheiro json ou bed")
        return 1, "", ""

    # se flags omitidas usamos defaults inferidos do conteudo do json
    backend_final = backend if backend is not None else _map_backend(
        _default_backend_key(data_preview)
    )
    packing_final = packing if packing is not None else _map_packing(
        _default_packing_key(data_preview)
    )

    # esta funcao reescreve packing method e generation backend e normaliza dict
    with progress_phase(console, "aplicar overrides packing e generation_backend"):
        apply_quick_test_overrides(
            work_json,
            packing_method=packing_final,
            generation_backend=backend_final,
        )
        data_final = load_wizard_json(work_json)
        if slice_cfg:
            data_final["slice"] = slice_cfg
            with work_json.open("w", encoding="utf-8") as f:
                json.dump(data_final, f, indent=2, ensure_ascii=False)
        wizard.params = json_to_wizard_params(data_final)
        if slice_cfg:
            wizard.params["slice"] = slice_cfg

    if verbose:
        render_technical_before(
            console,
            data_final,
            input_label="json" if input_is_json else "bed",
            input_path=str(original),
            backend=backend_final,
            packing=packing_final,
            exec_label=_exec_label("2" if not quick else "1"),
            post_label="abrir blender" if open_blender else "nao abrir",
        )
        ascii_pre = ascii_cross_section_schematic(
            dict(data_final.get("bed") or {}),
            dict(data_final.get("particles") or {}),
            str(
                data_final.get("packing_mode")
                or (data_final.get("packing") or {}).get("method")
                or "?"
            ),
            backend_final,
        )
        render_ascii_section(console, ascii_pre)

    run_json = work_json
    t_run0 = time.perf_counter()

    if not quick:
        with progress_phase(console, "gerar bed compilar patch"):
            if input_is_json:
                out_bed = (Path.cwd() / f"{original.stem}.bed").resolve()
            else:
                out_bed = original
            wizard.output_file = str(out_bed)
            if not wizard.generate_bed_file():
                render_error_panel(console, "falha ao gerar bed")
                return 1, backend_final, packing_final
            if not wizard.verify_and_compile():
                render_error_panel(console, "falha na compilacao")
                return 1, backend_final, packing_final
            run_json = _json_from_bed(Path(wizard.output_file))
            patch_compiled_json_packing(run_json, wizard.params)
            patch_compiled_json_export(run_json, wizard.params)
            patch_compiled_json_metadata(run_json, wizard.params)
            patch_compiled_json_slice(run_json, wizard.params)

    # post key dois abre gui logo tres nunca abre um modo cli nao pergunta interativamente
    post_key = "2" if open_blender else "3"

    if backend_final == "pure_python":
        out_stl = (Path.cwd() / f"{run_json.stem}_pure.stl").resolve()
        with progress_phase(console, "gerar stl python puro"):
            ok, stl = wizard.run_pure_python_with_json_path(run_json, out_stl=out_stl)
        wall = time.perf_counter() - t_run0
        if not ok or not stl:
            render_error_panel(console, "falha na geracao python pura")
            return 1, backend_final, packing_final
        bd = float((dict(data_final.get("bed") or {}).get("diameter") or 0) or 0)
        _render_after_pure(
            console,
            sidecar_path=sidecar_path_for_stl(stl),
            stl_path=stl,
            wall_s=wall,
            backend_effective="pure_python",
            packing_effective=packing_final,
            bed_diameter=bd,
        )
        _open_blender_after(wizard, console=console, post_key=post_key, stl=stl, blend=None)
    else:
        fmt = export_formats_for_blender(wizard.params.get("export") or {})
        with progress_phase(console, "executar blender"):
            ok, blend, bout = wizard.run_blender_with_json_path(
                run_json, open_after=False, formats=fmt
            )
        wall = time.perf_counter() - t_run0
        if not ok:
            render_error_panel(console, "falha no blender")
            return 1, backend_final, packing_final
        _render_after_blender(
            console,
            stdout=bout or "",
            blend_path=blend,
            wall_s=wall,
            backend_effective="blender",
            packing_effective=packing_final,
        )
        _open_blender_after(wizard, console=console, post_key=post_key, stl=None, blend=blend)

    return 0, backend_final, packing_final


def _open_blender_after(
    wizard: "BedWizard",
    *,
    console: Optional[Any],
    post_key: str,
    stl: Optional[Path],
    blend: Optional[Path],
) -> None:
    # post key 3 nunca abre 2 abre logo 1 pergunta com confirm do ui
    # stl e blend nunca devem vir os dois preenchidos no mesmo ramo mas o elif trata prioridade
    ui = wizard.ui
    if post_key == "3":
        return
    if post_key == "2":
        if stl and stl.is_file():
            wizard.open_blender_gui_with_stl(stl)
            render_blender_open_confirmation(console, stl, "stl")
        elif blend and blend.is_file():
            wizard.open_blender_gui_with_blend(blend)
            render_blender_open_confirmation(console, blend, "blend")
        return
    if stl and stl.is_file() and ui.confirm(
        "gostaria de abrir o blender apos a geracao", default=False
    ):
        wizard.open_blender_gui_with_stl(stl)
        render_blender_open_confirmation(console, stl, "stl")
    elif blend and blend.is_file() and ui.confirm(
        "gostaria de abrir o blender apos a geracao", default=False
    ):
        wizard.open_blender_gui_with_blend(blend)
        render_blender_open_confirmation(console, blend, "blend")


def _render_after_pure(
    console: Optional[Any],
    *,
    sidecar_path: Path,
    stl_path: Path,
    wall_s: float,
    backend_effective: str,
    packing_effective: str,
    bed_diameter: float,
) -> None:
    # le o json lateral escrito por pure generation com metricas e preview de centros
    # wall s e tempo total do subprocesso incluindo fases de menu antes se houver
    obj = load_sidecar(sidecar_path)
    if not obj:
        render_error_panel(console, f"sidecar nao encontrado: {sidecar_path}")
        return
    val = obj.get("validation") if isinstance(obj.get("validation"), dict) else {}
    gen = obj.get("generation") if isinstance(obj.get("generation"), dict) else {}
    # linhas chave valor para painel rich
    rows_out: List[Tuple[str, str]] = [
        ("situacao", "sucesso"),
        ("tempo geracao (s)", f"{float(obj.get('generation_wall_time_sec') or wall_s):.4f}"),
        ("tempo total fluxo (s)", f"{wall_s:.4f}"),
        ("particulas colocadas", str(obj.get("n_spheres_placed", "?"))),
        ("particulas pedidas", str(obj.get("n_spheres_requested", "?"))),
        ("validacao ok", str(val.get("ok", "?"))),
        ("violacoes par a par", str(val.get("pair_violations", obj.get("pair_violations", "?")))),
        ("violacoes dominio", str(val.get("domain_violations", obj.get("domain_violations", "?")))),
        ("tentativas colocacao", str(obj.get("placement_attempts_total", gen.get("attempts", "—")))),
        ("rejeicoes aproximadas", str(obj.get("placement_rejections_approx", "—"))),
        ("saida stl", str(stl_path)),
        ("sidecar json", str(sidecar_path)),
        ("backend usado", backend_effective),
        ("modo usado", str(obj.get("packing_method", packing_effective))),
    ]
    render_result_panel(console, True, rows_out, title="resultado — python puro")

    centers_tbl = centers_from_sidecar(obj)
    tab_rows = [(i + 1, c[0], c[1], c[2]) for i, c in enumerate(centers_tbl[:10])]
    render_coordinate_table(console, tab_rows)

    zc = centers_for_histogram(obj)
    z_lo, z_hi = 0.0, 0.1
    # expande um pouco o intervalo em z para as barras nao cortarem no limite exacto
    if zc:
        z_lo = min(t[2] for t in zc)
        z_hi = max(t[2] for t in zc)
        pad = max((z_hi - z_lo) * 0.05, 1e-6)
        z_lo -= pad
        z_hi += pad
    hlines = height_distribution_lines(zc, z_lo, z_hi, nbins=6)
    render_height_distribution(console, hlines)

    d = float(bed_diameter) if bed_diameter > 0 else 0.05
    # so precisamos do diametro para escalar o desenho topo
    bed_dummy: Dict[str, Any] = {"diameter": d}
    ascii_top = ascii_cross_section_with_particles(bed_dummy, zc, grid=29)
    render_ascii_section(console, ascii_top)


def _render_after_blender(
    console: Optional[Any],
    *,
    stdout: str,
    blend_path: Optional[Path],
    wall_s: float,
    backend_effective: str,
    packing_effective: str,
) -> None:
    # relatorio packing e opcional stdout ajuda quando nao ha json lateral
    rep = load_packing_report(blend_path)
    n_placed = rep.get("n_spheres_placed") if rep else None
    n_req = rep.get("n_spheres_requested") if rep else None
    val_ok = None
    if rep and isinstance(rep.get("validation"), dict):
        val_ok = rep["validation"].get("ok")
    rows_out: List[Tuple[str, str]] = [
        ("situacao", "sucesso" if blend_path else "verificar saida"),
        ("tempo subprocesso (s)", f"{wall_s:.4f}"),
        ("saida blend", str(blend_path) if blend_path else "—"),
        ("particulas colocadas (relatorio)", str(n_placed if n_placed is not None else "—")),
        ("particulas pedidas (relatorio)", str(n_req if n_req is not None else "—")),
        ("validacao (relatorio)", str(val_ok if val_ok is not None else "—")),
        ("backend usado", backend_effective),
        ("modo usado", str(rep.get("packing_method", packing_effective)) if rep else packing_effective),
    ]
    render_result_panel(console, True, rows_out, title="resultado — blender")
    tail = stdout.strip().splitlines()[-16:] if stdout else []
    body = "\n".join(tail) if tail else "(sem stdout capturado)"
    render_ascii_section(console, "trecho saida blender:\n" + body)


@dataclass
class QuickTestConfig:
    # snapshot das escolhas antes da execucao hoje serve so para futura extensao
    input_is_json: bool
    original_source: Path
    work_json_path: Path
    generation_backend: str
    packing_method: str
    exec_full: bool
    post_key: str


def run(wizard: "BedWizard") -> None:
    # funcao principal chamada pelo tests quick menu do bed wizard
    # ordem fixa cinco passos depois resumo depois confirmar depois ramo pure ou blender
    # passo um tipo entrada json fixture ou bed local
    # passo dois backend pure python valida geometria rapido ou blender cena completa
    # passo tres packing method alinha com packed bed science
    # passo quatro execucao rapida ou completa
    # passo cinco pos execucao abrir blender ou nao
    # packing spherical e hexagonal usam distancia minima entre centros no motor cientifico
    # packing rigid body delega colisao ao motor de fisica blender
    ui = wizard.ui
    console = get_console(ui)
    wizard.clear_screen()
    ui.breadcrumbs("wizard", "testes rapidos")
    if console and rich_available():
        render_test_header(console, "validacao rapida — 5 passos — enter aceita o padrao")
    else:
        wizard.print_header("testes rapidos", "validacao rapida com preview no terminal")

    render_step_title(console, "1", "tipo de entrada")
    render_choice_table(
        console,
        "como carregar o cenario?",
        [
            ("1", "json existente (test*.json na pasta de exemplos ou caminho)"),
            ("2", "arquivo .bed (compilar antes da execucao)"),
        ],
        "1",
    )
    in_key = _prompt_choice(ui, "1", ["1", "2"])

    data_preview: Optional[Dict[str, Any]] = None
    original: Path
    work_json: Path
    input_is_json = in_key == "1"

    if input_is_json:
        files = _glob_test_jsons()
        if files:
            # tabela rich opcional com metadados lidos de cada fixture
            if console and rich_available():
                from rich.table import Table as RT
                from rich import box as rbox

                t = RT(
                    title=f"exemplos em {_FIX_DIR.name}",
                    box=rbox.SIMPLE,
                    border_style="dim",
                )
                t.add_column("#", justify="right", width=4)
                t.add_column("ficheiro", style="cyan")
                t.add_column("packing", style="dim")
                t.add_column("backend", style="dim")
                for i, p in enumerate(files, 1):
                    try:
                        d = load_wizard_json(p)
                        pm = d.get("packing_mode") or (d.get("packing") or {}).get("method") or "?"
                        gb = d.get("generation_backend") or "?"
                    except OSError:
                        pm = "?"
                        gb = "?"
                    t.add_row(str(i), p.name, str(pm), str(gb))
                console.print(t)
            else:
                ui.println("ficheiros test*.json / _test_*.json:")
                for i, p in enumerate(files, 1):
                    try:
                        d = load_wizard_json(p)
                        pm = d.get("packing_mode") or (d.get("packing") or {}).get("method") or "?"
                        gb = d.get("generation_backend") or "?"
                    except OSError:
                        pm = "?"
                        gb = "?"
                    ui.muted(f"  {i}. {p.name}  | {pm}  | {gb}")
        else:
            ui.warn(f"nenhum test*.json em {_FIX_DIR}")
        ui.muted("caminho manual ou etiqueta@caminho exemplo: _test_hex.json@scripts/python_modeling/_test_hex.json")
        raw = ui.ask_line("numero ou caminho .json (vazio ou c cancelar): ").strip()
        if not raw or raw.lower() in ("c", "cancel", "cancelar", "voltar", "back"):
            ui.pause()
            return
        chosen = _resolve_json_input(raw, files)
        if not chosen or chosen.suffix.lower() != ".json":
            render_error_panel(console, "json invalido ou inexistente")
            ui.pause()
            return
        original = chosen
        with progress_phase(console, "carregar / copiar json de trabalho"):
            work_json = _copy_work_json(original)
            data_preview = load_wizard_json(work_json)
    else:
        beds = _glob_beds()
        if beds:
            if console and rich_available():
                from rich.table import Table as RT
                from rich import box as rbox

                t = RT(title="ficheiros .bed (dsl / cwd / repo)", box=rbox.SIMPLE, border_style="dim")
                t.add_column("#", justify="right", width=4)
                t.add_column("caminho", style="cyan")
                for i, p in enumerate(beds, 1):
                    t.add_row(str(i), str(p))
                console.print(t)
            else:
                ui.println("ficheiros .bed:")
                for i, p in enumerate(beds, 1):
                    ui.muted(f"  {i}. {p}")
        raw = ui.ask_line("numero ou caminho .bed (vazio ou c cancelar): ").strip()
        if not raw or raw.lower() in ("c", "cancel", "cancelar", "voltar", "back"):
            ui.pause()
            return
        chosen_b = _resolve_bed_input(raw, beds)
        if not chosen_b or chosen_b.suffix.lower() != ".bed":
            render_error_panel(console, ".bed invalido ou inexistente")
            ui.pause()
            return
        original = chosen_b
        wizard.output_file = str(original)
        with progress_phase(console, "compilar .bed para json"):
            if not wizard.verify_and_compile():
                render_error_panel(console, "falha na compilacao do bed")
                ui.pause()
                return
        work_json = _json_from_bed(Path(wizard.output_file))
        if not work_json.is_file():
            render_error_panel(console, f"json esperado ausente: {work_json}")
            ui.pause()
            return
        with progress_phase(console, "ler json compilado"):
            data_preview = load_wizard_json(work_json)

    render_step_title(console, "2", "backend de geracao")
    render_choice_table(
        console,
        "motor de geometria",
        [
            ("1", "pure_python — stl rapido ideal para validar colisao geometrica"),
            ("2", "blender — cena completa rigid body mais realista"),
        ],
        _default_backend_key(data_preview),
    )
    bk = _prompt_choice(ui, _default_backend_key(data_preview), ["1", "2"])
    backend = _map_backend(bk)

    render_step_title(console, "3", "modo de distribuicao")
    render_choice_table(
        console,
        "packing.method aplicado ao json de trabalho",
        [(k, v) for k, v in _PACKING_MENU],
        _default_packing_key(data_preview),
    )
    pk = _prompt_choice(ui, _default_packing_key(data_preview), ["1", "2", "3"])
    packing = _map_packing(pk)

    render_step_title(console, "3b", "thin slice (pseudo 2d)")
    slice_cfg = _ask_slice(ui)

    render_step_title(console, "4", "tipo de execucao")
    render_choice_table(
        console,
        "profundidade do fluxo",
        [
            ("1", "rapida — so modelo 3d a partir do json atual"),
            ("2", "completa — gerar .bed a partir dos params compilar patch e modelo"),
        ],
        "1",
    )
    ex_key = _prompt_choice(ui, "1", ["1", "2"])
    exec_full = ex_key == "2"

    render_step_title(console, "5", "pos execucao (blender gui)")
    render_choice_table(
        console,
        "abrir o blender no fim?",
        [
            ("1", "perguntar antes de abrir (padrao)"),
            ("2", "abrir automaticamente com o modelo gerado"),
            ("3", "nao abrir"),
        ],
        "1",
    )
    po_key = _prompt_choice(ui, "1", ["1", "2", "3"])

    with progress_phase(console, "aplicar overrides packing e generation_backend"):
        # reescreve disco e recarrega dict alinhado ao que o motor vai ler
        apply_quick_test_overrides(
            work_json,
            packing_method=packing,
            generation_backend=backend,
        )
        data_final = load_wizard_json(work_json)
        if slice_cfg:
            data_final["slice"] = slice_cfg
            # persistir no json de trabalho para blender/pure python lerem
            with work_json.open("w", encoding="utf-8") as f:
                json.dump(data_final, f, indent=2, ensure_ascii=False)
        wizard.params = json_to_wizard_params(data_final)
        if slice_cfg:
            wizard.params["slice"] = slice_cfg

    cfg = QuickTestConfig(
        input_is_json=input_is_json,
        original_source=original,
        work_json_path=work_json,
        generation_backend=backend,
        packing_method=packing,
        exec_full=exec_full,
        post_key=po_key,
    )

    input_lbl = "json" if cfg.input_is_json else "bed"
    render_technical_before(
        console,
        data_final,
        input_label=input_lbl,
        input_path=str(cfg.original_source),
        backend=cfg.generation_backend,
        packing=cfg.packing_method,
        exec_label=_exec_label(ex_key),
        post_label=_post_label(po_key),
    )
    bed = dict(data_final.get("bed") or {})
    particles = dict(data_final.get("particles") or {})
    pm = str(data_final.get("packing_mode") or (data_final.get("packing") or {}).get("method") or "?")
    ascii_pre = ascii_cross_section_schematic(bed, particles, pm, backend)
    render_ascii_section(console, ascii_pre)

    # texto mostrado ao utilizador sobre onde a colisao e verificada
    collision_note = (
        "regras: spherical_packing e hexagonal_3d validam sem sobreposicao no motor cientifico; "
        "rigid_body no blender usa corpos rigidos com colisao em paredes e tampas."
    )
    if console and rich_available():
        from rich.panel import Panel as RP
        from rich import box as rbox

        console.print(RP(collision_note, title="colisao", border_style="dim", box=rbox.ROUNDED))
    else:
        print(collision_note)

    if not ui.confirm("confirmar execucao", default=True):
        ui.muted("cancelado")
        ui.pause()
        return

    run_json = work_json
    t_run0 = time.perf_counter()

    if exec_full:
        # ramo completo sobrescreve bed no cwd para json ou o proprio ficheiro se veio bed
        with progress_phase(console, "gerar .bed a partir dos parametros"):
            if input_is_json:
                out_bed = (Path.cwd() / f"{original.stem}.bed").resolve()
            else:
                out_bed = original
            wizard.output_file = str(out_bed)
            if not wizard.generate_bed_file():
                render_error_panel(console, "falha ao gerar .bed")
                ui.pause()
                return
        with progress_phase(console, "compilar .bed e aplicar patch no json"):
            if not wizard.verify_and_compile():
                render_error_panel(console, "falha na compilacao")
                ui.pause()
                return
            run_json = _json_from_bed(Path(wizard.output_file))
            patch_compiled_json_packing(run_json, wizard.params)
            patch_compiled_json_export(run_json, wizard.params)
            patch_compiled_json_metadata(run_json, wizard.params)
            patch_compiled_json_slice(run_json, wizard.params)

    if backend == "pure_python":
        # stem inclui sufixo bed no json compilado entao o nome stl pode ser longo
        out_stl = (Path.cwd() / f"{run_json.stem}_pure.stl").resolve()
        with progress_phase(console, "gerar malha stl (python puro) e validar"):
            ok, stl = wizard.run_pure_python_with_json_path(run_json, out_stl=out_stl)
        wall = time.perf_counter() - t_run0
        if ok and stl:
            sc = sidecar_path_for_stl(stl)
            bd = float((dict(data_final.get("bed") or {}).get("diameter") or 0) or 0)
            _render_after_pure(
                console,
                sidecar_path=sc,
                stl_path=stl,
                wall_s=wall,
                backend_effective="pure_python",
                packing_effective=packing,
                bed_diameter=bd,
            )
            _open_blender_after(wizard, console=console, post_key=po_key, stl=stl, blend=None)
        elif ok:
            ui.ok("stl gerado")
        else:
            render_error_panel(console, "falha na geracao python pura")
    else:
        fmt = export_formats_for_blender(wizard.params.get("export") or {})
        with progress_phase(console, "executar blender em segundo plano e exportar"):
            ok, blend, bout = wizard.run_blender_with_json_path(
                run_json, open_after=False, formats=fmt
            )
        wall = time.perf_counter() - t_run0
        if ok:
            _render_after_blender(
                console,
                stdout=bout or "",
                blend_path=blend,
                wall_s=wall,
                backend_effective="blender",
                packing_effective=packing,
            )
            _open_blender_after(wizard, console=console, post_key=po_key, stl=None, blend=blend)
        else:
            render_error_panel(console, "falha no blender — ver stderr na consola acima")

    ui.pause("enter para voltar ao menu...")
