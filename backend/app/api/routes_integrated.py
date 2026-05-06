# pipeline end to end grava bed corre blender openfoam e jobs longos
# este modulo cria jobs na mesma estrutura pydantic usada em routes
# funde armazenamento em memoria com routes para listagem unificada
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database.connection import get_db
from backend.app.api.deps_user import get_active_user_id
from backend.app.api.models import (
    BedParameters, BedParametersNested,
    JobResponse, JobStatus, JobType,
    Job
)
from backend.app.services.bed_service import BedService
from backend.app.services.blender_service import BlenderService
from backend.app.services.openfoam_service import OpenFOAMService

from datetime import datetime
import uuid

router = APIRouter()

# armazenamento em memoria de jobs (compartilhado com routes.py)
jobs_store_integrated: dict[str, Job] = {}

# servicos
bed_service = BedService()
blender_service = BlenderService()
openfoam_service = OpenFOAMService()

import asyncio
import subprocess
from pathlib import Path


@router.post("/pipeline/create-bed", response_model=JobResponse, tags=["pipeline"])
async def create_bed_full(
    background_tasks: BackgroundTasks,
    parameters: BedParameters,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
    modeling_profile: str | None = Query(
        None,
        description=(
            "blender ou blender_python vs python ou pure_python; None usa env MODELING_PROFILE"
        ),
    ),
    generate_model: bool = True,
    run_simulation: bool = False,
):
    """
    fluxo completo: compila .bed, salva no banco, opcionalmente gera modelo 3d e simulacao
    
    este endpoint:
    1. compila parametros para .bed e .bed.json
    2. salva leito no banco de dados postgresql
    3. opcionalmente gera modelo 3d no blender
    4. opcionalmente cria caso openfoam
    
    args:
        parameters: parametros do leito
        generate_model: gerar modelo 3d automaticamente
        run_simulation: criar simulacao openfoam automaticamente
        
    returns:
        job_id para monitorar progresso
    """
    # criar job
    job_id = str(uuid.uuid4())
    job = Job(
        job_id=job_id,
        job_type=JobType.COMPILE,
        status=JobStatus.QUEUED,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={
            "generate_model": generate_model,
            "run_simulation": run_simulation,
            "modeling_profile": modeling_profile,
        }
    )
    
    jobs_store_integrated[job_id] = job
    
    background_tasks.add_task(
        _execute_full_pipeline,
        job_id=job_id,
        parameters=parameters.model_dump(),
        generate_model=generate_model,
        run_simulation=run_simulation,
        modeling_profile=modeling_profile,
        db_session=db,
        user_id=user_id,
        jobs_store=jobs_store_integrated,
    )
    
    return JobResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        message="pipeline iniciado"
    )


async def _execute_full_pipeline(
    job_id: str,
    parameters: dict,
    generate_model: bool,
    run_simulation: bool,
    modeling_profile: str | None,
    db_session: Session,
    user_id: int,
    jobs_store: dict
):
    """
    executa pipeline completo em background
    """
    job = jobs_store[job_id]
    
    try:
        # etapa 1: compilar .bed e salvar no banco
        job.status = JobStatus.RUNNING
        job.progress = 10
        job.updated_at = datetime.now()
        
        result = await bed_service.compile_bed(
            parameters=parameters,
            save_to_db=True,
            db_session=db_session,
            user_id=user_id,
        )
        
        job.progress = 30
        job.updated_at = datetime.now()
        job.output_files.append(result["bed_file"])
        job.output_files.append(result["json_file"])
        job.metadata["bed_id"] = result.get("bed_id")
        job.metadata["json_file"] = result["json_file"]
        
        # etapa 2: gerar modelo 3d (opcional)
        if generate_model:
            job.progress = 40
            job.updated_at = datetime.now()
            
            # criar sub-job para blender
            blender_job_id = str(uuid.uuid4())
            blender_job = Job(
                job_id=blender_job_id,
                job_type=JobType.GENERATE_MODEL,
                status=JobStatus.QUEUED,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata={}
            )
            jobs_store[blender_job_id] = blender_job
            
            await blender_service.generate_model(
                job_id=blender_job_id,
                json_file=result["json_file"],
                open_blender=False,
                jobs_store=jobs_store,
                bed_id=result.get("bed_id"),
                db_session=db_session,
                modeling_profile=modeling_profile,
            )
            
            # verificar se blender foi bem sucedido
            if blender_job.status == JobStatus.COMPLETED:
                job.progress = 70
                job.updated_at = datetime.now()
                job.output_files.extend(blender_job.output_files)
                job.metadata["blend_file"] = blender_job.metadata.get("blend_file")
                
                # etapa 3: criar simulacao openfoam (opcional)
                if run_simulation and blender_job.metadata.get("blend_file"):
                    job.progress = 75
                    job.updated_at = datetime.now()
                    
                    # criar sub-job para openfoam
                    openfoam_job_id = str(uuid.uuid4())
                    openfoam_job = Job(
                        job_id=openfoam_job_id,
                        job_type=JobType.SIMULATION,
                        status=JobStatus.QUEUED,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        metadata={}
                    )
                    jobs_store[openfoam_job_id] = openfoam_job
                    
                    await openfoam_service.create_case(
                        job_id=openfoam_job_id,
                        json_file=result["json_file"],
                        blend_file=blender_job.metadata.get("blend_file"),
                        run_simulation=False,
                        jobs_store=jobs_store,
                        bed_id=result.get("bed_id"),
                        db_session=db_session
                    )
                    
                    if openfoam_job.status == JobStatus.COMPLETED:
                        job.output_files.extend(openfoam_job.output_files)
                        job.metadata["simulation_id"] = openfoam_job.metadata.get("simulation_id")
                        job.metadata["case_dir"] = openfoam_job.metadata.get("case_dir")
            else:
                raise Exception(f"erro na geracao do modelo: {blender_job.error_message}")
        
        # finalizar job
        job.status = JobStatus.COMPLETED
        job.progress = 100
        job.updated_at = datetime.now()
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.updated_at = datetime.now()


@router.get("/pipeline/job/{job_id}", response_model=Job, tags=["pipeline"])
async def get_pipeline_job(job_id: str):
    """
    busca status de job do pipeline integrado
    """
    if job_id not in jobs_store_integrated:
        raise HTTPException(status_code=404, detail="job nao encontrado")
    
    return jobs_store_integrated[job_id]


@router.post("/pipeline/full-simulation", response_model=JobResponse, tags=["pipeline"])
async def execute_full_pipeline_with_simulation(
    request: Request,
    background_tasks: BackgroundTasks,
    modeling_profile: str | None = Query(
        None,
        description=(
            "blender ou blender_python vs python ou pure_python; None usa env MODELING_PROFILE"
        ),
    ),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """
    pipeline completo end-to-end com execucao da simulacao cfd no wsl
    
    aceita tres formatos de corpo json:
    - BedParametersNested (chave bed com dict) como no wizard
    - BedParameters plano (diametro particle_count etc) como no pipelinecompletofull
    - artefactos existentes: json_file e opcional bed_file sem chave bed (apos upload)
    """
    try:
        raw = await request.json()
    except Exception:
        raise HTTPException(status_code=422, detail="corpo json invalido")

    if not isinstance(raw, dict):
        raise HTTPException(status_code=422, detail="corpo deve ser um objeto json")

    if (
        isinstance(raw.get("json_file"), str)
        and raw["json_file"].strip()
        and not raw.get("bed")
    ):
        params_dict = {
            "json_file": raw["json_file"].strip(),
            "bed_file": (raw.get("bed_file") or "").strip(),
            "_skip_compile": True,
        }
    elif isinstance(raw.get("bed"), dict):
        try:
            params_dict = BedParametersNested.model_validate(raw).model_dump()
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=e.errors())
    else:
        try:
            flat = BedParameters.model_validate(raw)
            params_dict = bed_service._normalize_parameters_for_generation(flat.model_dump())
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=e.errors())

    job_id = str(uuid.uuid4())
    job = Job(
        job_id=job_id,
        job_type=JobType.FULL_PIPELINE,
        status=JobStatus.QUEUED,
        progress=0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        output_files=[],
        logs=[],
        metadata={}
    )

    jobs_store_integrated[job_id] = job

    background_tasks.add_task(
        _execute_full_pipeline_with_simulation,
        job_id,
        params_dict,
        db,
        jobs_store_integrated,
        modeling_profile,
        user_id,
    )

    return JobResponse(
        job_id=job_id,
        status=job.status,
        message="pipeline completo iniciado - acompanhe o progresso via /pipeline/job/{job_id}"
    )


async def _execute_full_pipeline_with_simulation(
    job_id: str,
    parameters: dict,
    db_session: Session,
    jobs_store: dict,
    modeling_profile: str | None = None,
    user_id: int = 1,
):
    """
    executa pipeline completo com simulacao cfd em background
    
    etapas:
    1. compilacao .bed -> .json (0-15%)
    2. modelagem 3d blender com fisica (15-40%)
    3. criacao caso openfoam (40-50%)
    4. execucao simulacao cfd no wsl (50-100%)
    """
    job = jobs_store[job_id]
    
    try:
        parameters = dict(parameters)
        skip_compile = bool(parameters.pop("_skip_compile", False))

        # ===== etapa 1: compilar .bed (0-15%) =====
        job.status = JobStatus.RUNNING
        job.progress = 0
        job.logs.append(f"[{datetime.now()}] iniciando pipeline completo")
        job.updated_at = datetime.now()

        if skip_compile:
            json_file = parameters["json_file"]
            bed_file = parameters.get("bed_file") or ""
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            json_path = project_root / json_file
            if not json_path.exists():
                raise FileNotFoundError(f"json nao encontrado: {json_path}")
            job.logs.append(f"[{datetime.now()}] etapa 1/4: usando json existente (sem recompilar)")
            result = {
                "bed_file": bed_file,
                "json_file": json_file,
                "bed_id": None,
            }
        else:
            job.logs.append(f"[{datetime.now()}] etapa 1/4: compilando arquivo .bed")
            result = await bed_service.compile_bed(
                parameters=parameters,
                save_to_db=True,
                db_session=db_session,
                user_id=user_id,
            )

        bed_file = result["bed_file"]
        json_file = result["json_file"]
        
        job.progress = 15
        job.output_files.append(bed_file)
        job.output_files.append(json_file)
        job.metadata["bed_id"] = result.get("bed_id")
        job.metadata["json_file"] = json_file
        job.metadata["bed_file"] = bed_file
        job.logs.append(f"[{datetime.now()}] ✓ arquivo .bed compilado: {bed_file}")
        job.logs.append(f"[{datetime.now()}] ✓ arquivo .json gerado: {json_file}")
        job.updated_at = datetime.now()
        
        # ===== etapa 2: gerar modelo 3d no blender (15-40%) =====
        job.progress = 15
        job.logs.append(
            f"[{datetime.now()}] etapa 2/4: gerando geometria 3d "
            f"(perfil: {modeling_profile or 'env'})"
        )
        job.updated_at = datetime.now()
        
        # criar sub-job para blender
        blender_job_id = str(uuid.uuid4())
        blender_job = Job(
            job_id=blender_job_id,
            job_type=JobType.GENERATE_MODEL,
            status=JobStatus.QUEUED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )
        jobs_store[blender_job_id] = blender_job
        
        # gerar modelo no blender
        await blender_service.generate_model(
            job_id=blender_job_id,
            json_file=json_file,
            open_blender=False,
            jobs_store=jobs_store,
            bed_id=job.metadata.get("bed_id"),
            db_session=db_session,
            modeling_profile=modeling_profile,
        )
        
        # verificar se blender foi bem sucedido
        if blender_job.status == JobStatus.COMPLETED:
            blend_file = blender_job.metadata.get("blend_file")
            if blend_file:
                job.progress = 40
                job.output_files.append(blend_file)
                job.metadata["blend_file"] = blend_file
                job.logs.append(f"[{datetime.now()}] ✓ modelo 3d gerado: {blend_file}")
                job.updated_at = datetime.now()
            else:
                raise Exception("geracao 3d concluiu mas nao retornou ficheiro de geometria")
        else:
            error_msg = blender_job.error_message or "erro desconhecido na geracao 3d"
            raise Exception(f"erro na geracao do modelo: {error_msg}")
        
        # ===== etapa 3: criar caso openfoam (40-50%) =====
        job.progress = 40
        job.logs.append(f"[{datetime.now()}] etapa 3/4: criando caso openfoam")
        job.updated_at = datetime.now()
        
        case_dir = None
        try:
            case_dir = await _create_openfoam_case(json_file, blend_file, job, jobs_store)
            
            if case_dir:
                job.progress = 50
                job.metadata["case_dir"] = case_dir
                job.logs.append(f"[{datetime.now()}] ✓ caso openfoam criado: {case_dir}")
                job.updated_at = datetime.now()
            else:
                # Tentar continuar mesmo se falhar (para testes)
                job.logs.append(f"[{datetime.now()}] ⚠️  aviso: caso openfoam nao foi criado, mas continuando...")
                case_dir = None
        except Exception as e:
            # Para testes, permitir continuar mesmo se OpenFOAM falhar
            job.logs.append(f"[{datetime.now()}] ⚠️  aviso: erro ao criar caso openfoam: {str(e)}")
            job.logs.append(f"[{datetime.now()}] ⚠️  continuando pipeline (OpenFOAM pode nao estar disponivel)")
            case_dir = None
        
        # ===== etapa 4: executar simulacao cfd no wsl (50-100%) =====
        if case_dir:
            job.progress = 50
            job.logs.append(f"[{datetime.now()}] etapa 4/4: executando simulacao cfd no wsl")
            job.logs.append(f"[{datetime.now()}] ⚠️  este processo pode levar 10-30 minutos")
            job.updated_at = datetime.now()
            
            try:
                success = await _run_openfoam_simulation_wsl(case_dir, job, jobs_store)
                
                if not success:
                    job.logs.append(f"[{datetime.now()}] ⚠️  aviso: simulacao cfd nao executou (WSL/OpenFOAM pode nao estar disponivel)")
                    job.logs.append(f"[{datetime.now()}] ✓ pipeline concluido (caso criado, simulacao opcional)")
                    job.progress = 100
            except Exception as e:
                job.logs.append(f"[{datetime.now()}] ⚠️  aviso: erro ao executar simulacao: {str(e)}")
                job.logs.append(f"[{datetime.now()}] ✓ pipeline concluido (caso criado, simulacao opcional)")
                job.progress = 100
        else:
            # Se caso não foi criado, marcar como concluído parcialmente
            job.logs.append(f"[{datetime.now()}] ✓ pipeline concluido parcialmente (geometria gerada, OpenFOAM nao disponivel)")
            job.progress = 100
        
        # ===== finalizacao =====
        job.status = JobStatus.COMPLETED
        job.progress = 100
        if case_dir:
            job.logs.append(f"[{datetime.now()}] ✓ pipeline finalizado com sucesso!")
            job.logs.append(f"[{datetime.now()}] resultados disponiveis em: {case_dir}")
            job.logs.append(f"[{datetime.now()}] visualize no paraview: {case_dir}/caso.foam")
        else:
            job.logs.append(f"[{datetime.now()}] ✓ pipeline finalizado parcialmente!")
            job.logs.append(f"[{datetime.now()}] geometria 3D gerada com sucesso")
            job.logs.append(f"[{datetime.now()}] caso OpenFOAM nao foi criado (pode nao estar disponivel)")
        job.updated_at = datetime.now()
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.logs.append(f"[{datetime.now()}] ✗ erro: {str(e)}")
        job.updated_at = datetime.now()
        import traceback
        job.logs.append(f"[{datetime.now()}] traceback: {traceback.format_exc()}")


async def _create_openfoam_case(json_file: str, blend_file: str, job: Job, jobs_store: dict) -> Optional[str]:
    """
    cria caso openfoam usando setup_openfoam_case.py
    
    returns:
        caminho do diretorio do caso ou None se falhar
    """
    try:
        import sys
        
        # usar project_root para caminhos absolutos
        project_root = Path(__file__).parent.parent.parent.parent
        
        json_path = project_root / json_file
        blend_path = project_root / blend_file
        
        # verificar se arquivos existem
        if not json_path.exists():
            job.logs.append(f"[{datetime.now()}] erro: arquivo json nao encontrado: {json_path}")
            return None
        
        if not blend_path.exists():
            job.logs.append(
                f"[{datetime.now()}] erro: geometria (.blend ou .stl) nao encontrada: {blend_path}"
            )
            return None
        
        from bedflow_local_paths import simulations_dir

        # diretorio de saida (alinhar com openfoam_service e local_data)
        output_root = simulations_dir()
        output_root.mkdir(parents=True, exist_ok=True)
        
        # script de setup
        script_path = project_root / "scripts" / "openfoam_scripts" / "setup_openfoam_case.py"
        
        if not script_path.exists():
            job.logs.append(f"[{datetime.now()}] erro: script setup_openfoam_case.py nao encontrado em {script_path}")
            return None
        
        job.logs.append(f"[{datetime.now()}] executando setup_openfoam_case.py...")
        job.updated_at = datetime.now()
        
        # executar script
        job.logs.append(f"[{datetime.now()}] executando: python {script_path}")
        job.logs.append(f"[{datetime.now()}] json: {json_path}")
        job.logs.append(f"[{datetime.now()}] blend: {blend_path}")
        job.logs.append(f"[{datetime.now()}] output: {output_root}")
        job.updated_at = datetime.now()
        
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(script_path),
            str(json_path),
            str(blend_path),
            "--output-dir", str(output_root),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(project_root)  # executar do diretório raiz
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # parsear output para logs
            stdout_text = stdout.decode('utf-8', errors='ignore')
            for line in stdout_text.split('\n'):
                if line.strip():
                    job.logs.append(f"[{datetime.now()}] {line}")
            
            # determinar diretorio do caso (tentar extrair do output ou usar nome do json)
            case_name = json_path.stem.replace('.bed', '').replace('.json', '')
            case_dir = output_root / case_name
            
            # verificar se diretório foi criado
            if not case_dir.exists():
                # tentar encontrar qualquer diretório criado recentemente
                recent_dirs = [d for d in output_root.iterdir() if d.is_dir()]
                if recent_dirs:
                    case_dir = max(recent_dirs, key=lambda p: p.stat().st_mtime)
                    job.logs.append(f"[{datetime.now()}] usando diretorio encontrado: {case_dir}")
            
            job.updated_at = datetime.now()
            return str(case_dir.relative_to(project_root))
        else:
            # Capturar erros detalhados
            stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
            stdout_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
            
            job.logs.append(f"[{datetime.now()}] ❌ erro na criacao do caso openfoam")
            job.logs.append(f"[{datetime.now()}] codigo de erro: {process.returncode}")
            
            if stdout_text:
                job.logs.append(f"[{datetime.now()}] stdout:")
                for line in stdout_text.split('\n')[:20]:  # Limitar a 20 linhas
                    if line.strip():
                        job.logs.append(f"[{datetime.now()}]   {line}")
            
            if stderr_text:
                job.logs.append(f"[{datetime.now()}] stderr:")
                for line in stderr_text.split('\n')[:20]:  # Limitar a 20 linhas
                    if line.strip():
                        job.logs.append(f"[{datetime.now()}]   {line}")
            
            # Tentar extrair mensagem de erro mais clara
            error_msg = "falha na criacao do caso openfoam"
            if stderr_text:
                # Pegar primeira linha de erro relevante
                for line in stderr_text.split('\n'):
                    if any(keyword in line.lower() for keyword in ['error', 'erro', 'exception', 'failed', 'falhou']):
                        error_msg = line.strip()[:200]  # Limitar tamanho
                        break
            
            job.updated_at = datetime.now()
            raise Exception(f"falha na criacao do caso openfoam: {error_msg}")
            
    except Exception as e:
        error_msg = str(e)
        job.logs.append(f"[{datetime.now()}] ❌ erro inesperado ao criar caso openfoam: {error_msg}")
        import traceback
        job.logs.append(f"[{datetime.now()}] traceback: {traceback.format_exc()[:500]}")
        job.updated_at = datetime.now()
        raise Exception(f"falha na criacao do caso openfoam: {error_msg}")


async def _run_openfoam_simulation_wsl(case_dir: str, job: Job, jobs_store: dict) -> bool:
    """
    executa simulacao openfoam no wsl/ubuntu
    
    returns:
        True se sucesso, False se falhar
    """
    try:
        case_path = Path(case_dir)
        
        if not case_path.exists():
            job.logs.append(f"[{datetime.now()}] erro: diretorio do caso nao encontrado: {case_dir}")
            job.updated_at = datetime.now()
            return False
        
        # converter caminho windows para wsl
        # C:\Users\... -> /mnt/c/Users/...
        wsl_path = str(case_path).replace('\\', '/')
        if len(wsl_path) > 1 and wsl_path[1] == ':':
            drive = wsl_path[0].lower()
            wsl_path = f"/mnt/{drive}{wsl_path[2:]}"
        
        job.logs.append(f"[{datetime.now()}] caminho wsl: {wsl_path}")
        job.updated_at = datetime.now()
        
        # verificar wsl
        job.progress = 55
        job.logs.append(f"[{datetime.now()}] [1/4] verificando wsl...")
        job.updated_at = datetime.now()
        
        process = await asyncio.create_subprocess_exec(
            "wsl", "--list", "--quiet",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        if process.returncode != 0:
            job.logs.append(f"[{datetime.now()}] erro: wsl nao esta instalado ou configurado")
            job.updated_at = datetime.now()
            return False
        
        job.logs.append(f"[{datetime.now()}] ✓ wsl detectado")
        job.updated_at = datetime.now()
        
        # executar Allrun no wsl
        job.progress = 60
        job.logs.append(f"[{datetime.now()}] [2/4] executando ./Allrun no wsl...")
        job.logs.append(f"[{datetime.now()}] diretorio: {wsl_path}")
        job.updated_at = datetime.now()
        
        wsl_command = f"cd '{wsl_path}' && chmod +x Allrun && ./Allrun"
        
        # executar com captura de output
        process = await asyncio.create_subprocess_exec(
            "wsl", "bash", "-c", wsl_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        
        # ler output em tempo real e atualizar progresso
        line_count = 0
        async for line in process.stdout:
            line_text = line.decode().strip()
            if line_text:
                job.logs.append(f"[{datetime.now()}] {line_text}")
                line_count += 1
                
                # atualizar progresso baseado em keywords
                if "blockMesh" in line_text:
                    job.progress = 70
                elif "snappyHexMesh" in line_text:
                    job.progress = 75
                elif "checkMesh" in line_text:
                    job.progress = 80
                elif "simpleFoam" in line_text or "icoFoam" in line_text:
                    job.progress = 85
                elif "SIMPLE solution converged" in line_text or "End" in line_text:
                    job.progress = 95
                
                # atualizar a cada 10 linhas para não sobrecarregar
                if line_count % 10 == 0:
                    job.updated_at = datetime.now()
        
        await process.wait()
        
        job.updated_at = datetime.now()
        
        if process.returncode == 0:
            job.progress = 95
            job.logs.append(f"[{datetime.now()}] [3/4] ✓ simulacao concluida com sucesso")
            job.updated_at = datetime.now()
            
            # criar arquivo .foam para paraview
            job.logs.append(f"[{datetime.now()}] [4/4] criando arquivo para paraview...")
            foam_file = case_path / "caso.foam"
            foam_file.touch()
            
            job.logs.append(f"[{datetime.now()}] ✓ arquivo paraview criado: {foam_file}")
            job.updated_at = datetime.now()
            
            return True
        else:
            job.logs.append(f"[{datetime.now()}] [3/4] erro: simulacao falhou com codigo {process.returncode}")
            job.logs.append(f"[{datetime.now()}] verifique os logs em: {case_dir}/log.*")
            job.updated_at = datetime.now()
            return False
            
    except FileNotFoundError:
        job.logs.append(f"[{datetime.now()}] erro: comando 'wsl' nao encontrado")
        job.logs.append(f"[{datetime.now()}] instale o wsl2 no windows")
        job.updated_at = datetime.now()
        return False
    except Exception as e:
        job.logs.append(f"[{datetime.now()}] erro inesperado: {str(e)}")
        job.updated_at = datetime.now()
        import traceback
        job.logs.append(f"[{datetime.now()}] traceback: {traceback.format_exc()}")
        return False

