# router central do pipeline expoe compilacao geometria jobs e downloads
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
from pathlib import Path
import uuid
from datetime import datetime

from backend.app.api.models import (
    CompileRequest, CompileResponse,
    GenerateModelRequest, SimulationRequest,
    Job, JobResponse, JobStatus, JobType,
    FileInfo, FileListResponse
)
from backend.app.services.bed_service import BedService
from backend.app.services.blender_service import BlenderService
from backend.app.services.openfoam_service import OpenFOAMService
from backend.app.utils.file_manager import FileManager

router = APIRouter()

# memoria volatil partilhada entre pedidos para estado de jobs simples
jobs_store: dict[str, Job] = {}

# servicos stateless reutilizaveis em varios endpoints
bed_service = BedService()
blender_service = BlenderService()
openfoam_service = OpenFOAMService()
file_manager = FileManager()

@router.post("/bed/compile", response_model=CompileResponse, tags=["bed"])
async def compile_bed(request: CompileRequest):
    # passo um valida pydantic automaticamente
    # passo dois delega geracao de ficheiros ao bed service
    try:
        result = await bed_service.compile_bed(
            parameters=request.parameters.model_dump(),
            filename=request.filename
        )
        
        return CompileResponse(
            success=True,
            bed_file=result["bed_file"],
            json_file=result["json_file"],
            message="compilação bem-sucedida"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro na compilação: {str(e)}")

@router.get("/bed/validate/{filename}", tags=["bed"])
async def validate_bed(filename: str):
    """
    valida arquivo .bed existente
    """
    try:
        result = await bed_service.validate_bed(filename)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="arquivo não encontrado")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"erro de validação: {str(e)}")

@router.post("/model/generate", response_model=JobResponse, tags=["model"])
async def generate_model(request: GenerateModelRequest, background_tasks: BackgroundTasks):
    """
    gera modelo 3d no blender (assíncrono)
    """
    # uuid garante id unico sem coordenacao entre workers
    job_id = str(uuid.uuid4())
    job = Job(
        job_id=job_id,
        job_type=JobType.GENERATE_MODEL,
        status=JobStatus.QUEUED,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"json_file": request.json_file, "open_blender": request.open_blender}
    )
    
    jobs_store[job_id] = job
    
    # background tasks corre depois da resposta http devolver 202 implicitamente aqui e 200 com body
    background_tasks.add_task(
        blender_service.generate_model,
        job_id=job_id,
        json_file=request.json_file,
        open_blender=request.open_blender,
        jobs_store=jobs_store,
        modeling_profile=request.modeling_profile,
    )
    
    return JobResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        message="geração de modelo iniciada"
    )

@router.get("/model/list", response_model=FileListResponse, tags=["model"])
async def list_models():
    """
    lista modelos 3d gerados
    """
    files = file_manager.list_files("models", [".blend", ".stl"])
    return FileListResponse(files=files, total=len(files))

@router.post("/simulation/create", response_model=JobResponse, tags=["simulation"])
async def create_simulation(request: SimulationRequest, background_tasks: BackgroundTasks):
    """
    cria caso openfoam (assíncrono)
    """
    job_id = str(uuid.uuid4())
    job = Job(
        job_id=job_id,
        job_type=JobType.SIMULATION,
        status=JobStatus.QUEUED,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={
            "json_file": request.json_file,
            "blend_file": request.blend_file,
            "run_simulation": request.run_simulation
        }
    )
    
    jobs_store[job_id] = job
    
    background_tasks.add_task(
        openfoam_service.create_case,
        job_id=job_id,
        json_file=request.json_file,
        blend_file=request.blend_file,
        run_simulation=request.run_simulation,
        jobs_store=jobs_store
    )
    
    return JobResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        message="criação de simulação iniciada"
    )

@router.get("/simulation/list", response_model=FileListResponse, tags=["simulation"])
async def list_simulations():
    """
    lista simulações criadas
    """
    files = file_manager.list_directories("cfd")
    return FileListResponse(files=files, total=len(files))

@router.get("/job/{job_id}", response_model=Job, tags=["jobs"])
async def get_job(job_id: str):
    """
    busca status de job
    """
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail="job não encontrado")
    
    return jobs_store[job_id]

@router.get("/jobs", response_model=List[Job], tags=["jobs"])
async def list_jobs(status: str = None, job_type: str = None):
    """
    lista jobs com filtros opcionais
    inclui jobs regulares e jobs do pipeline completo
    """
    from backend.app.api.routes_integrated import jobs_store_integrated
    
    # concatena listas mantendo referencia aos mesmos objetos job em memoria
    all_jobs = list(jobs_store.values()) + list(jobs_store_integrated.values())
    
    if status:
        all_jobs = [j for j in all_jobs if j.status == status]
    
    if job_type:
        all_jobs = [j for j in all_jobs if j.job_type == job_type]
    
    # ordenacao por created at decrescente melhora ux em paineis
    all_jobs.sort(key=lambda x: x.created_at, reverse=True)
    
    return all_jobs

@router.get("/files/{file_type}", response_model=FileListResponse, tags=["files"])
async def list_files(file_type: str):
    """
    lista arquivos por tipo
    tipos: bed, json, blend, stl, simulations (pastas em local_data/simulations e legado generated/cfd)
    """
    type_mapping = {
        "bed": (".", [".bed"]),
        "json": (".", [".bed.json"]),
        "blend": ("models", [".blend"]),
        "stl": ("models", [".stl"]),
        "simulations": ("cfd", [])
    }
    
    if file_type not in type_mapping:
        raise HTTPException(status_code=400, detail="tipo de arquivo inválido")
    
    directory, extensions = type_mapping[file_type]
    
    if file_type == "simulations":
        files = file_manager.list_directories(directory)
    else:
        files = file_manager.list_files(directory, extensions)
    
    return FileListResponse(files=files, total=len(files))

@router.get("/files/download/{file_type}/{filename}", tags=["files"])
async def download_file(file_type: str, filename: str):
    """
    baixa arquivo
    """
    try:
        file_path = file_manager.get_file_path(file_type, filename)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="arquivo não encontrado")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/octet-stream"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao baixar arquivo: {str(e)}")

@router.get("/status", tags=["system"])
async def get_system_status():
    """
    verifica status do sistema e serviços
    """
    return {
        "api": "running",
        "services": {
            "bed_compiler": bed_service.check_availability(),
            "blender": blender_service.check_availability(),
            "openfoam": openfoam_service.check_availability()
        },
        "jobs": {
            "total": len(jobs_store),
            "queued": len([j for j in jobs_store.values() if j.status == JobStatus.QUEUED]),
            "running": len([j for j in jobs_store.values() if j.status == JobStatus.RUNNING]),
            "completed": len([j for j in jobs_store.values() if j.status == JobStatus.COMPLETED]),
            "failed": len([j for j in jobs_store.values() if j.status == JobStatus.FAILED])
        }
    }
