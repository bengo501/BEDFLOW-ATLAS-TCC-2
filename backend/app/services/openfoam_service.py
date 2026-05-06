# lanca subprocessos para montar caso openfoam e opcionalmente correr solver
# espera script setup python no repositorio e paths relativos gravados no job
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from bedflow_local_paths import resolve_existing_artifact, simulations_dir

from backend.app.api.models import JobStatus

class OpenFOAMService:
    """gerencia criação de casos openfoam"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.scripts_dir = self.project_root / "scripts" / "openfoam_scripts"
        self.setup_script = self.scripts_dir / "setup_openfoam_case.py"
        self.output_dir = simulations_dir()
    
    def check_availability(self) -> bool:
        """verifica se openfoam está disponível"""
        # verifica se script existe
        if not self.setup_script.exists():
            return False
        
        # em produção, verificar wsl/openfoam
        # por enquanto, apenas verifica script
        return True
    
    async def create_case(
        self,
        job_id: str,
        json_file: str,
        blend_file: str,
        run_simulation: bool,
        jobs_store: Dict[str, Any],
        bed_id: Optional[int] = None,
        db_session = None
    ):
        """
        cria caso openfoam (executado em background)
        
        args:
            job_id: id do job
            json_file: caminho do arquivo json
            blend_file: caminho do arquivo blend
            run_simulation: executar simulação após criar
            jobs_store: armazenamento de jobs
        """
        job = jobs_store[job_id]
        
        try:
            # atualizar status
            job.status = JobStatus.RUNNING
            job.progress = 10
            job.updated_at = datetime.now()
            
            # preparar caminhos
            json_path = self.project_root / json_file
            blend_path = self.project_root / blend_file
            if not json_path.exists():
                alt = resolve_existing_artifact(str(json_file).replace("\\", "/").lstrip("/"))
                if alt and alt.is_file():
                    json_path = alt
            if not blend_path.exists():
                altb = resolve_existing_artifact(str(blend_file).replace("\\", "/").lstrip("/"))
                if altb and altb.is_file():
                    blend_path = altb

            if not json_path.exists():
                raise FileNotFoundError(f"arquivo json não encontrado: {json_file}")
            
            if not blend_path.exists():
                raise FileNotFoundError(f"arquivo blend não encontrado: {blend_file}")
            
            # executar script de setup
            job.progress = 30
            job.updated_at = datetime.now()
            
            cmd = [
                sys.executable,
                str(self.setup_script),
                str(json_path),
                str(blend_path)
            ]
            
            if run_simulation:
                cmd.append("--run")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos
            )
            
            job.progress = 80
            job.updated_at = datetime.now()
            
            if result.returncode != 0:
                raise Exception(f"erro no openfoam: {result.stderr}")
            
            # extrair nome do caso do output (assumindo formato padrão)
            case_name = blend_path.stem  # nome do arquivo sem extensão
            case_dir = self.output_dir / case_name
            
            # criar/atualizar simulacao no banco se fornecido
            simulation_id = None
            if bed_id:
                from backend.app.database import crud, schemas
                from backend.app.database.connection import DatabaseConnection
                
                # ler parametros do json
                with open(json_path, 'r', encoding='utf-8') as f:
                    params = json.load(f)

                own_session = None
                session = db_session
                if session is None:
                    own_session = DatabaseConnection.get_session()
                    session = own_session
                
                # criar simulacao no banco
                sim_data = schemas.SimulationCreate(
                    bed_id=bed_id,
                    name=f"sim_{case_name}",
                    description=f"simulacao criada automaticamente",
                    regime=params.get('cfd', {}).get('regime', 'laminar'),
                    inlet_velocity=params.get('cfd', {}).get('inlet_velocity', 0.01),
                    fluid_density=params.get('cfd', {}).get('fluid_density', 1000.0),
                    fluid_viscosity=params.get('cfd', {}).get('fluid_viscosity', 0.001),
                    solver='simpleFoam',
                    max_iterations=params.get('cfd', {}).get('max_iterations', 1000),
                    convergence_criteria=params.get('cfd', {}).get('convergence_criteria', 1e-4),
                    parameters_json=params,
                    created_by='api'
                )
                bed_row = crud.BedCRUD.get(session, bed_id)
                scope_uid = bed_row.user_id if bed_row else 1
                db_simulation = crud.SimulationCRUD.create(
                    session,
                    sim_data,
                    user_id=scope_uid,
                    case_directory=str(case_dir.relative_to(self.project_root)),
                    status='completed' if not run_simulation else 'running',
                    progress=100 if not run_simulation else 50,
                )
                simulation_id = db_simulation.id
                if own_session is not None:
                    own_session.close()
            
            # atualizar job com sucesso
            job.status = JobStatus.COMPLETED
            job.progress = 100
            job.updated_at = datetime.now()
            job.output_files = [str(case_dir.relative_to(self.project_root))]
            job.metadata["case_dir"] = str(case_dir.relative_to(self.project_root))
            job.metadata["ran_simulation"] = run_simulation
            if simulation_id:
                job.metadata["simulation_id"] = simulation_id
            
        except subprocess.TimeoutExpired:
            job.status = JobStatus.FAILED
            job.error_message = "timeout na criação do caso (>10min)"
            job.updated_at = datetime.now()
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.updated_at = datetime.now()

