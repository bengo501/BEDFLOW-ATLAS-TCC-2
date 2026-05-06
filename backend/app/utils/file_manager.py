# abstrai listagens sobre local_data (e pastas legadas) para inventario e downloads
from pathlib import Path
from typing import List
from datetime import datetime

from bedflow_local_paths import (
    beds_dir,
    iter_search_roots_for_beds,
    iter_search_roots_for_models_3d,
    iter_search_roots_for_simulations,
    models_3d_dir,
    simulations_dir,
)

from backend.app.api.models import FileInfo


class FileManager:
    # guarda raiz do repo e caminhos derivados uma vez por instancia
    def __init__(self):
        # sobe quatro niveis de utils ate à pasta do repositorio
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.dsl_dir = self.project_root / "dsl"

    def list_files(self, directory: str, extensions: List[str]) -> List[FileInfo]:
        roots: List[Path] = []
        if directory == ".":
            roots = iter_search_roots_for_beds()
        elif directory == "models":
            roots = iter_search_roots_for_models_3d()
        else:
            roots = [self.project_root / "generated" / directory]
            roots = [p for p in roots if p.exists()]

        if not roots:
            return []

        files: List[FileInfo] = []
        seen: set[str] = set()

        for base_dir in roots:
            for file_path in base_dir.rglob("*"):
                if not file_path.is_file():
                    continue
                if extensions and file_path.suffix not in extensions:
                    continue
                key = str(file_path.resolve())
                if key in seen:
                    continue
                seen.add(key)
                stat = file_path.stat()
                files.append(
                    FileInfo(
                        filename=file_path.name,
                        path=str(file_path.relative_to(self.project_root)),
                        size=stat.st_size,
                        created_at=datetime.fromtimestamp(stat.st_ctime),
                        file_type=file_path.suffix[1:],
                    )
                )

        files.sort(key=lambda x: x.created_at, reverse=True)
        return files

    def list_directories(self, directory: str) -> List[FileInfo]:
        if directory != "cfd":
            base_dir = self.project_root / "generated" / directory
            if not base_dir.exists():
                return []
            roots = [base_dir]
        else:
            roots = iter_search_roots_for_simulations()

        dirs: List[FileInfo] = []
        seen_names: set[str] = set()

        for base_dir in roots:
            if not base_dir.exists():
                continue
            for dir_path in base_dir.iterdir():
                if not dir_path.is_dir():
                    continue
                name = dir_path.name
                if name in seen_names:
                    continue
                seen_names.add(name)
                stat = dir_path.stat()
                total_size = sum(
                    f.stat().st_size for f in dir_path.rglob("*") if f.is_file()
                )
                dirs.append(
                    FileInfo(
                        filename=name,
                        path=str(dir_path.relative_to(self.project_root)),
                        size=total_size,
                        created_at=datetime.fromtimestamp(stat.st_ctime),
                        file_type="directory",
                    )
                )

        dirs.sort(key=lambda x: x.created_at, reverse=True)
        return dirs

    def get_file_path(self, file_type: str, filename: str) -> Path:
        if file_type == "bed":
            for base in iter_search_roots_for_beds():
                p = base / filename
                if p.is_file():
                    return p
            return beds_dir() / filename
        if file_type == "json":
            for base in iter_search_roots_for_beds():
                p = base / filename
                if p.is_file():
                    return p
            return beds_dir() / filename
        if file_type in ("blend", "stl"):
            for base in iter_search_roots_for_models_3d():
                p = base / filename
                if p.is_file():
                    return p
            return models_3d_dir() / filename
        if file_type == "simulation":
            leg = self.project_root / "generated" / "cfd" / filename
            if leg.is_dir() or leg.is_file():
                return leg
            return simulations_dir() / filename
        return self.project_root / filename
