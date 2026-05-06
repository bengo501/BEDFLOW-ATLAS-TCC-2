# caminhos canonicos para artefactos locais (cli, fastapi, wizard)
# raiz = pasta do repositorio (pai deste ficheiro)
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

_REPO_ROOT = Path(__file__).resolve().parent


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
