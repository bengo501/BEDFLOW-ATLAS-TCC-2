# corre blender ou script python conforme MODELING_PROFILE para gerar geometria
# atualiza objeto job mutavel partilhado pelo router e pela tarefa em background
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from bedflow_local_paths import models_3d_dir, resolve_existing_artifact

from backend.app.api.models import JobStatus
from backend.app import config as app_config


def _normalize_modeling_profile(modeling_profile: Optional[str]) -> str:
    # converte texto da api ou do config para um de dois motores internos
    # modeling profile pode ser none entao cai no default global
    # raw fica em minusculas sem espacos laterais
    # pure python e python disparam o script packed bed stl sem blender
    # blender python e blender disparam leito extracao com blender
    # qualquer outro valor levanta erro cedo para o cliente corrigir o json
    raw = (modeling_profile or app_config.MODELING_PROFILE or "blender").strip().lower()
    if raw in ("pure_python", "python"):
        return "python"
    if raw in ("blender_python", "blender"):
        return "blender"
    raise ValueError(
        f"modeling_profile invalido: {raw} "
        "(use blender blender_python python ou pure_python)"
    )


class BlenderService:
    # prepara caminhos de saida tipicos generated 3d output
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.scripts_dir = self.project_root / "scripts" / "blender_scripts"
        self.leito_script = self.scripts_dir / "leito_extracao.py"
        self.output_dir = models_3d_dir()
        self.python_stl_script = (
            self.project_root / "scripts" / "python_modeling" / "packed_bed_stl.py"
        )
        
        # detectar blender
        self.blender_exe = self._find_blender()
    
    def _find_blender(self) -> str:
        """encontra executável do blender"""
        import platform
        
        system = platform.system()
        
        # caminhos comuns
        if system == "Windows":
            common_paths = [
                r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            ]
        elif system == "Linux":
            common_paths = [
                "/usr/bin/blender",
                "/usr/local/bin/blender",
            ]
        else:  # macOS
            common_paths = [
                "/Applications/Blender.app/Contents/MacOS/Blender",
            ]
        
        for path in common_paths:
            if Path(path).exists():
                return path
        
        # tentar comando simples
        return "blender"
    
    def check_availability(self) -> bool:
        """verifica se blender está disponível"""
        try:
            result = subprocess.run(
                [self.blender_exe, "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    async def generate_model(
        self,
        job_id: str,
        json_file: str,
        open_blender: bool,
        jobs_store: Dict[str, Any],
        bed_id: Optional[int] = None,
        db_session = None,
        modeling_profile: Optional[str] = None,
    ):
        """
        gera modelo 3d (executado em background)
        
        args:
            job_id: id do job
            json_file: caminho do arquivo json
            open_blender: abrir blender gui após gerar
            jobs_store: armazenamento de jobs
        """
        job = jobs_store[job_id]
        
        try:
            profile = _normalize_modeling_profile(modeling_profile)

            # atualizar status
            job.status = JobStatus.RUNNING
            job.progress = 10
            job.updated_at = datetime.now()
            job.metadata["modeling_profile"] = profile
            
            # preparar caminhos
            json_path = self.project_root / json_file
            if not json_path.exists():
                alt = resolve_existing_artifact(str(json_file).replace("\\", "/").lstrip("/"))
                if alt and alt.is_file():
                    json_path = alt

            if not json_path.exists():
                raise FileNotFoundError(f"arquivo json não encontrado: {json_file}")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if profile == "python":
                if not self.python_stl_script.exists():
                    raise FileNotFoundError(f"script python modeling nao encontrado: {self.python_stl_script}")
                stl_filename = f"leito_{timestamp}.stl"
                stl_path = self.output_dir / stl_filename
                job.progress = 30
                job.updated_at = datetime.now()
                result = subprocess.run(
                    [
                        sys.executable,
                        str(self.python_stl_script),
                        str(json_path),
                        str(stl_path),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=600,
                    cwd=str(self.project_root),
                )
                job.progress = 80
                job.updated_at = datetime.now()
                if result.returncode != 0:
                    raise Exception(f"erro na geracao python/stl: {result.stderr or result.stdout}")
                if not stl_path.exists():
                    raise Exception("arquivo .stl nao foi gerado")
                rel = str(stl_path.relative_to(self.project_root))
                job.status = JobStatus.COMPLETED
                job.progress = 100
                job.updated_at = datetime.now()
                job.output_files = [rel]
                job.metadata["geometry_file"] = rel
                job.metadata["blend_file"] = rel
            else:
                if not self.check_availability():
                    raise RuntimeError(
                        "perfil blender mas blender nao disponivel; use MODELING_PROFILE=python ou instale blender"
                    )
                blend_filename = f"leito_{timestamp}.blend"
                blend_path = self.output_dir / blend_filename
                job.progress = 30
                job.updated_at = datetime.now()
                cmd = [
                    self.blender_exe,
                    "--background",
                    "--python", str(self.leito_script),
                    "--",
                    "--params", str(json_path),
                    "--output", str(blend_path)
                ]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                job.progress = 80
                job.updated_at = datetime.now()
                if result.returncode != 0:
                    raise Exception(f"erro no blender: {result.stderr}")
                if not blend_path.exists():
                    raise Exception("arquivo .blend não foi gerado")
                rel = str(blend_path.relative_to(self.project_root))
                job.status = JobStatus.COMPLETED
                job.progress = 100
                job.updated_at = datetime.now()
                job.output_files = [rel]
                job.metadata["geometry_file"] = rel
                job.metadata["blend_file"] = rel
            
            # atualizar bed no banco se fornecido
            if bed_id:
                from backend.app.database import crud, schemas
                from backend.app.database.connection import DatabaseConnection

                own_session = None
                session = db_session
                if session is None:
                    own_session = DatabaseConnection.get_session()
                    session = own_session

                geom_rel = job.metadata.get("geometry_file") or job.metadata.get("blend_file")
                update_kwargs = {}
                if geom_rel:
                    if str(geom_rel).lower().endswith(".stl"):
                        update_kwargs["stl_file_path"] = geom_rel
                    else:
                        update_kwargs["blend_file_path"] = geom_rel
                if update_kwargs:
                    update_data = schemas.BedUpdate(**update_kwargs)
                    crud.BedCRUD.update(session, bed_id, update_data)
                if own_session is not None:
                    own_session.close()
            
            if profile == "blender" and open_blender:
                bp = self.project_root / (job.metadata.get("blend_file") or "")
                if bp.suffix.lower() == ".blend" and bp.exists():
                    subprocess.Popen([self.blender_exe, str(bp)])
            
        except subprocess.TimeoutExpired:
            job.status = JobStatus.FAILED
            job.error_message = "timeout na geração do modelo (>5min)"
            job.updated_at = datetime.now()
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.updated_at = datetime.now()

