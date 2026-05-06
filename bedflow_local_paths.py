# caminhos canonicos para artefactos locais (cli, fastapi, wizard)
# raiz = pasta do repositorio (pai deste ficheiro)
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_REPO_ROOT = Path(__file__).resolve().parent

# extensoes de malha que o visualizador web e desktop tentam carregar
VIEWER_MESH_EXTENSIONS: Tuple[str, ...] = (
    ".stl",
    ".obj",
    ".ply",
    ".gltf",
    ".glb",
)

# ficheiros de cena blender (so desktop / blender, nao three direto)
VIEWER_SCENE_EXTENSIONS: Tuple[str, ...] = (".blend",)

# prefixos relativos à raiz do repo onde procurar malhas
VIEWER_MESH_PATH_PREFIXES: Tuple[str, ...] = (
    "local_data/models_3d/",
    "local_data/aux/",
    "local_data/simulations/",
    "generated/3d/output/",
    "generated/batch/",
    "generated/cfd/",
)


def project_root() -> Path:
    return _REPO_ROOT


def local_data_root() -> Path:
    p = project_root() / "local_data"
    p.mkdir(parents=True, exist_ok=True)
    return p


def beds_dir() -> Path:
    d = local_data_root() / "beds"
    d.mkdir(parents=True, exist_ok=True)
    return d


def models_3d_dir() -> Path:
    d = local_data_root() / "models_3d"
    d.mkdir(parents=True, exist_ok=True)
    return d


def simulations_dir() -> Path:
    d = local_data_root() / "simulations"
    d.mkdir(parents=True, exist_ok=True)
    return d


def reports_dir() -> Path:
    d = local_data_root() / "reports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def aux_dir() -> Path:
    d = local_data_root() / "aux"
    d.mkdir(parents=True, exist_ok=True)
    return d


def legacy_generated_root() -> Path:
    p = project_root() / "generated"
    p.mkdir(parents=True, exist_ok=True)
    return p


def legacy_output_root() -> Path:
    p = project_root() / "output"
    p.mkdir(parents=True, exist_ok=True)
    return p


def ensure_local_data_layout() -> None:
    for fn in (beds_dir, models_3d_dir, simulations_dir, reports_dir, aux_dir):
        fn()


def resolve_repo_relative(rel: str) -> Path:
    r = (rel or "").replace("\\", "/").lstrip("/")
    return project_root() / r


def resolve_existing_artifact(rel: str) -> Optional[Path]:
    """
    devolve path absoluto se existir no disco; tenta localizacoes legadas
    (generated/configs, generated/3d/output, generated/cfd, output/).
    """
    r = (rel or "").replace("\\", "/").lstrip("/")
    if not r:
        return None
    direct = project_root() / r
    if direct.is_file() or direct.is_dir():
        return direct.resolve()

    name = Path(r).name

    if r.startswith("generated/configs/"):
        cand = beds_dir() / name
        if cand.exists():
            return cand.resolve()

    if r.startswith("generated/3d/output/"):
        cand = models_3d_dir() / name
        if cand.exists():
            return cand.resolve()

    if r.startswith("generated/cfd/"):
        tail = r[len("generated/cfd/") :].strip("/")
        if tail:
            cand = simulations_dir() / Path(tail)
            if cand.exists():
                return cand.resolve()
            leg = legacy_generated_root() / "cfd" / tail
            if leg.exists():
                return leg.resolve()

    if r.startswith("output/"):
        cand = beds_dir() / name
        if cand.exists():
            return cand.resolve()

    return None


def iter_search_roots_for_beds() -> List[Path]:
    roots: List[Path] = [beds_dir(), legacy_generated_root() / "configs", legacy_output_root()]
    return [p for p in roots if p.exists()]


def iter_search_roots_for_models_3d() -> List[Path]:
    roots: List[Path] = [models_3d_dir(), legacy_generated_root() / "3d" / "output"]
    return [p for p in roots if p.exists()]


def iter_search_roots_for_simulations() -> List[Path]:
    roots: List[Path] = [simulations_dir(), legacy_generated_root() / "cfd"]
    return [p for p in roots if p.exists()]


def resolve_simulation_case_dir(case_name: str) -> Optional[Path]:
    for base in iter_search_roots_for_simulations():
        d = (base / case_name).resolve()
        if d.is_dir():
            return d
    return None


def find_wizard_json_and_blend(file_base: str) -> Tuple[Optional[Path], Optional[Path]]:
    """
    localiza json compilado e .blend pelo nome base do wizard (sem .bed).
    procura local_data primeiro depois pastas legadas generated/*.
    """
    stem = (file_base or "").replace(".bed", "").strip()
    json_name = f"{stem}.bed.json"
    blend_name = f"{stem}.blend"
    bed_json: Optional[Path] = None
    for base in (beds_dir(), legacy_generated_root() / "configs"):
        p = base / json_name
        if p.is_file():
            bed_json = p
            break
    blend_file: Optional[Path] = None
    for base in (models_3d_dir(), legacy_generated_root() / "3d" / "output"):
        p = base / blend_name
        if p.is_file():
            blend_file = p
            break
    return bed_json, blend_file


def mesh_id_for_relative_path(rel: str) -> str:
    r = (rel or "").replace("\\", "/").lstrip("/")
    return hashlib.sha256(r.encode("utf-8")).hexdigest()[:16]


def iter_mesh_scan_roots() -> List[Path]:
    roots: List[Path] = []
    for base in iter_search_roots_for_models_3d():
        roots.append(base)
    ax = aux_dir()
    if ax.exists():
        roots.append(ax)
    leg = legacy_generated_root()
    for sub in ("batch",):
        p = leg / sub
        if p.exists():
            roots.append(p)
    for base in iter_search_roots_for_simulations():
        if base.exists():
            roots.append(base)
    # dedupe preservando ordem
    seen: set[str] = set()
    out: List[Path] = []
    for r in roots:
        k = str(r.resolve())
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


def scan_project_mesh_files(*, max_files: int = 2000) -> List[Dict[str, Any]]:
    """
    lista ficheiros de malha conhecidos sob raizes de modelo/simulacao.
    ordenado por mtime decrescente; limita quantidade para evitar travar em arvores enormes.
    """
    root = project_root()
    items: List[Dict[str, Any]] = []
    exts = {e.lower() for e in VIEWER_MESH_EXTENSIONS} | {e.lower() for e in VIEWER_SCENE_EXTENSIONS}
    for base in iter_mesh_scan_roots():
        try:
            for fp in base.rglob("*"):
                if not fp.is_file():
                    continue
                if fp.suffix.lower() not in exts:
                    continue
                try:
                    rel = str(fp.resolve().relative_to(root.resolve())).replace("\\", "/")
                except ValueError:
                    continue
                if not is_viewer_mesh_relative_path(rel):
                    continue
                st = fp.stat()
                items.append(
                    {
                        "relative_path": rel,
                        "filename": fp.name,
                        "mesh_id": mesh_id_for_relative_path(rel),
                        "size_bytes": st.st_size,
                        "mtime": st.st_mtime,
                        "format": fp.suffix.lower().lstrip("."),
                    }
                )
        except OSError:
            continue
    items.sort(key=lambda x: x["mtime"], reverse=True)
    return items[:max_files]


def is_viewer_mesh_relative_path(rel: str) -> bool:
    r = (rel or "").replace("\\", "/").lstrip("/")
    if ".." in r or r.startswith("/"):
        return False
    return any(r.startswith(pref) for pref in VIEWER_MESH_PATH_PREFIXES)


def resolve_validated_mesh_path(rel: str) -> Optional[Path]:
    if not is_viewer_mesh_relative_path(rel):
        return None
    p = (project_root() / rel.replace("\\", "/").lstrip("/")).resolve()
    try:
        p.relative_to(project_root().resolve())
    except ValueError:
        return None
    if not p.is_file():
        return None
    return p
