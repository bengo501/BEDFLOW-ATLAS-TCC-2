# estado cfd em memoria e subprocess setup openfoam
# complementa routes simulation com ids uuid proprios e fila simples
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict
from pathlib import Path
import subprocess
import json
import uuid
from datetime import datetime

from bedflow_local_paths import find_wizard_json_and_blend, simulations_dir

router = APIRouter()

# armazenar status das simulacoes em memoria
# em producao, usar redis ou banco de dados
simulations_status: Dict[str, dict] = {}


class CFDRequest(BaseModel):
    bed_json_path: str
    blend_file_path: str
    output_dir: Optional[str] = None
    run_simulation: bool = True


class CFDStatus(BaseModel):
    simulation_id: str
    status: str  # 'queued', 'preparing', 'meshing', 'running', 'completed', 'error'
    progress: int  # 0-100
    message: str
    created_at: str
    completed_at: Optional[str] = None
    case_dir: Optional[str] = None
    error: Optional[str] = None


class RunFromWizardBody(BaseModel):
    """corpo json igual ao enviado pelo frontend wizard e cfdsimulation"""

    fileName: str = Field(..., description="nome base do ficheiro bed no wizard")
    runSimulation: bool = True


class CreateCaseBody(BaseModel):
    blend_file: str
    json_file: str
    case_name: str


class CreateCaseJsonOnlyBody(BaseModel):
    json_file: str
    case_name: str


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def _resolve_repo_path(project_root: Path, path_str: str) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    return (project_root / p).resolve()


@router.post("/cfd/create")
async def create_cfd_case(request: CFDRequest, background_tasks: BackgroundTasks):
    """
    criar caso openfoam e opcionalmente executar simulacao
    """
    try:
        # gerar id unico para simulacao
        simulation_id = str(uuid.uuid4())[:8]
        
        # definir caminhos
        project_root = Path(__file__).parent.parent.parent.parent
        script_path = project_root / "scripts" / "openfoam_scripts" / "setup_openfoam_case.py"
        
        # verificar se arquivos existem
        bed_json = project_root / request.bed_json_path
        blend_file = project_root / request.blend_file_path
        
        if not bed_json.exists():
            raise HTTPException(status_code=404, detail=f"arquivo json nao encontrado: {bed_json}")
        
        if not blend_file.exists():
            raise HTTPException(status_code=404, detail=f"arquivo blend nao encontrado: {blend_file}")
        
        # definir diretorio de saida
        if request.output_dir:
            output_dir = project_root / request.output_dir
        else:
            output_dir = simulations_dir() / f"sim_{simulation_id}"
        
        # criar entrada de status
        simulations_status[simulation_id] = {
            "simulation_id": simulation_id,
            "status": "queued",
            "progress": 0,
            "message": "simulacao na fila",
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "case_dir": str(output_dir),
            "error": None,
            "bed_json": str(bed_json),
            "blend_file": str(blend_file)
        }
        
        # executar em background
        background_tasks.add_task(
            run_cfd_simulation,
            simulation_id,
            script_path,
            bed_json,
            blend_file,
            output_dir,
            request.run_simulation
        )
        
        return {
            "success": True,
            "simulation_id": simulation_id,
            "message": "simulacao criada com sucesso",
            "status_url": f"/api/cfd/status/{simulation_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao criar caso cfd: {str(e)}")


@router.get("/cfd/status/{simulation_id}")
async def get_cfd_status(simulation_id: str):
    """
    obter status de uma simulacao
    """
    if simulation_id not in simulations_status:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    
    return simulations_status[simulation_id]


@router.get("/cfd/list")
async def list_cfd_simulations():
    """
    listar todas as simulacoes
    """
    return {
        "simulations": list(simulations_status.values()),
        "count": len(simulations_status)
    }


@router.delete("/cfd/{simulation_id}")
async def delete_cfd_simulation(simulation_id: str):
    """
    deletar simulacao (apenas status, nao deleta arquivos)
    """
    if simulation_id not in simulations_status:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    
    del simulations_status[simulation_id]
    
    return {
        "success": True,
        "message": "simulacao deletada"
    }


async def run_cfd_simulation(
    simulation_id: str,
    script_path: Path,
    bed_json: Path,
    blend_file: Path,
    output_dir: Path,
    run_simulation: bool
):
    """
    executar simulacao cfd em background
    """
    import sys
    
    try:
        # atualizar status: preparando
        simulations_status[simulation_id].update({
            "status": "preparing",
            "progress": 10,
            "message": "preparando caso openfoam..."
        })
        
        # construir comando
        cmd = [
            sys.executable,
            str(script_path),
            str(bed_json),
            str(blend_file),
            "--output-dir", str(output_dir)
        ]
        
        if run_simulation:
            cmd.append("--run")
        
        # executar script de setup
        simulations_status[simulation_id].update({
            "status": "meshing",
            "progress": 30,
            "message": "criando caso e gerando malha..."
        })
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos timeout
        )
        
        if result.returncode != 0:
            simulations_status[simulation_id].update({
                "status": "error",
                "progress": 0,
                "message": "erro ao criar caso openfoam",
                "error": result.stderr,
                "completed_at": datetime.now().isoformat()
            })
            return
        
        # caso criado com sucesso
        if run_simulation:
            simulations_status[simulation_id].update({
                "status": "running",
                "progress": 60,
                "message": "executando simulacao cfd..."
            })
            
            # monitorar simulacao (simulado - em producao ler log)
            # aqui poderiamos ler o log.simpleFoam e atualizar progresso real
            
            simulations_status[simulation_id].update({
                "status": "completed",
                "progress": 100,
                "message": "simulacao concluida com sucesso!",
                "completed_at": datetime.now().isoformat()
            })
        else:
            simulations_status[simulation_id].update({
                "status": "completed",
                "progress": 100,
                "message": "caso openfoam criado (simulacao nao executada)",
                "completed_at": datetime.now().isoformat()
            })
            
    except subprocess.TimeoutExpired:
        simulations_status[simulation_id].update({
            "status": "error",
            "progress": 0,
            "message": "timeout na criacao do caso",
            "error": "execucao excedeu 10 minutos",
            "completed_at": datetime.now().isoformat()
        })
    except Exception as e:
        simulations_status[simulation_id].update({
            "status": "error",
            "progress": 0,
            "message": "erro inesperado",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })


@router.post("/cfd/run-from-wizard")
async def run_cfd_from_wizard(
    background_tasks: BackgroundTasks,
    body: RunFromWizardBody,
):
    """
    executar cfd a partir de arquivo gerado pelo wizard
    busca automaticamente os arquivos .bed.json e .blend
    """
    try:
        project_root = _project_root()

        file_base = body.fileName.replace(".bed", "")

        bed_json, blend_file = find_wizard_json_and_blend(file_base)

        if bed_json is None or not bed_json.is_file():
            raise HTTPException(
                status_code=404,
                detail="arquivo json nao encontrado. compile o .bed primeiro",
            )

        if blend_file is None or not blend_file.is_file():
            raise HTTPException(
                status_code=404,
                detail="modelo 3d nao encontrado. gere o modelo no blender primeiro",
            )

        request = CFDRequest(
            bed_json_path=str(bed_json.relative_to(project_root)),
            blend_file_path=str(blend_file.relative_to(project_root)),
            run_simulation=body.runSimulation,
        )

        return await create_cfd_case(request, background_tasks)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro: {str(e)}")

# novos endpoints para modos específicos
@router.post("/cfd/create-case", tags=["cfd"])
async def create_case_only(
    body: CreateCaseBody,
    background_tasks: BackgroundTasks,
):
    """
    criar caso CFD a partir de arquivo blend existente
    """
    try:
        project_root = _project_root()
        blend_path = _resolve_repo_path(project_root, body.blend_file)
        json_path = _resolve_repo_path(project_root, body.json_file)

        if not blend_path.exists():
            raise HTTPException(status_code=404, detail="arquivo blend não encontrado")

        if not json_path.exists():
            raise HTTPException(status_code=404, detail="arquivo json não encontrado")

        case_dir = simulations_dir() / body.case_name
        case_dir.mkdir(parents=True, exist_ok=True)

        await _setup_cfd_case(blend_path, json_path, case_dir)

        rel_case = str(case_dir.relative_to(project_root))
        return {
            "success": True,
            "message": "caso CFD criado com sucesso",
            "case_dir": rel_case,
            "case_name": body.case_name,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro: {str(e)}")

@router.post("/cfd/create-case-only", tags=["cfd"])
async def create_case_from_json_only(
    body: CreateCaseJsonOnlyBody,
    background_tasks: BackgroundTasks,
):
    """
    criar caso CFD apenas a partir de arquivo json (sem modelo 3D)
    """
    try:
        project_root = _project_root()
        json_path = _resolve_repo_path(project_root, body.json_file)

        if not json_path.exists():
            raise HTTPException(status_code=404, detail="arquivo json não encontrado")

        case_dir = simulations_dir() / body.case_name
        case_dir.mkdir(parents=True, exist_ok=True)

        await _setup_cfd_case_from_json(json_path, case_dir)

        rel_case = str(case_dir.relative_to(project_root))
        return {
            "success": True,
            "message": "caso CFD criado com sucesso",
            "case_dir": rel_case,
            "case_name": body.case_name,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro: {str(e)}")

async def _setup_cfd_case(blend_path: Path, json_path: Path, case_dir: Path):
    """
    configurar caso CFD a partir de arquivo blend
    """
    try:
        # copiar arquivo blend para o caso
        import shutil
        shutil.copy2(blend_path, case_dir / "geometry.blend")
        
        # configurar arquivos do OpenFOAM
        await _create_openfoam_files(case_dir, json_path)
        
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao configurar caso CFD: {str(e)}")

async def _setup_cfd_case_from_json(json_path: Path, case_dir: Path):
    """
    configurar caso CFD apenas a partir de arquivo json
    """
    try:
        # configurar arquivos do OpenFOAM
        await _create_openfoam_files(case_dir, json_path)
        
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao configurar caso CFD: {str(e)}")

async def _create_openfoam_files(case_dir: Path, json_path: Path):
    """
    criar arquivos de configuração do OpenFOAM
    """
    try:
        # ler parâmetros do JSON
        with open(json_path, 'r') as f:
            params = json.load(f)
        
        # criar estrutura de diretórios do OpenFOAM
        system_dir = case_dir / "system"
        constant_dir = case_dir / "constant"
        zero_dir = case_dir / "0"
        
        system_dir.mkdir(exist_ok=True)
        constant_dir.mkdir(exist_ok=True)
        zero_dir.mkdir(exist_ok=True)
        
        # criar arquivos de configuração básicos
        await _create_controlDict(system_dir)
        await _create_meshDict(system_dir)
        await _create_transportProperties(constant_dir)
        await _create_turbulenceProperties(constant_dir)
        await _create_initial_conditions(zero_dir, params)
        
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao criar arquivos OpenFOAM: {str(e)}")

async def _create_controlDict(system_dir: Path):
    """criar controlDict"""
    control_dict = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      controlDict;
}

application     simpleFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         1000;

deltaT          1;

writeControl    timeStep;

writeInterval   100;

purgeWrite      2;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;
"""
    with open(system_dir / "controlDict", 'w') as f:
        f.write(control_dict)

async def _create_meshDict(system_dir: Path):
    """criar meshDict"""
    mesh_dict = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      meshDict;
}

snapControls
{
    nSmoothPatch    3;
    tolerance       2.0;
    nSolveIter      30;
    nRelaxIter      5;
}

castellatedMeshControls
{
    maxLocalCells   1000000;
    maxGlobalCells  2000000;
    minRefinementCells 10;
    nCellsBetweenLevels 1;
    
    resolveFeatureAngle 30;
    
    refinementRegions
    {
    }
    
    locationInMesh (0 0 0);
}

mergeTolerance 1e-6;
"""
    with open(system_dir / "meshDict", 'w') as f:
        f.write(mesh_dict)

async def _create_transportProperties(constant_dir: Path):
    """criar transportProperties"""
    transport_props = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      transportProperties;
}

transportModel  Newtonian;

nu              [0 2 -1 0 0 0 0] 1e-05;
"""
    with open(constant_dir / "transportProperties", 'w') as f:
        f.write(transport_props)

async def _create_turbulenceProperties(constant_dir: Path):
    """criar turbulenceProperties"""
    turbulence_props = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      turbulenceProperties;
}

simulationType  RAS;

RAS
{
    RASModel        kEpsilon;
    turbulence      on;
    printCoeffs     on;
}
"""
    with open(constant_dir / "turbulenceProperties", 'w') as f:
        f.write(turbulence_props)

async def _create_initial_conditions(zero_dir: Path, params: dict):
    """criar condições iniciais"""
    # arquivo p
    p_content = """FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      p;
}

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 100;
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            zeroGradient;
    }
}
"""
    with open(zero_dir / "p", 'w') as f:
        f.write(p_content)
    
    # arquivo U
    u_content = """FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    location    "0";
    object      U;
}

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (1 0 0);
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            noSlip;
    }
}
"""
    with open(zero_dir / "U", 'w') as f:
        f.write(u_content)

