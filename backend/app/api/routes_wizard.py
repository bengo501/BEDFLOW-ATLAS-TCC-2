# gera bed a partir do wizard compila template e ajuda cli local
# tambem tenta abrir terminal do sistema com comandos uteis em dev
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile

from bedflow_local_paths import beds_dir

router = APIRouter()


def _repo_root() -> Path:
    """raiz do repositorio (pai de backend/)."""
    return Path(__file__).resolve().parents[3]

# modelos pydantic para validação
class BedParams(BaseModel):
    diameter: str
    height: str
    wall_thickness: str
    clearance: str
    material: str
    roughness: str = "0.0"

class LidsParams(BaseModel):
    top_type: str
    bottom_type: str
    top_thickness: str
    bottom_thickness: str
    seal_clearance: str = "0.001"

class ParticlesParams(BaseModel):
    kind: str
    diameter: str
    count: str
    target_porosity: str = "0.4"
    density: str
    mass: str = "0.0"
    restitution: str = "0.3"
    friction: str = "0.5"
    rolling_friction: str = "0.1"
    linear_damping: str = "0.1"
    angular_damping: str = "0.1"
    seed: str = "42"

class PackingParams(BaseModel):
    method: str
    gravity: str
    substeps: str = "10"
    iterations: str = "10"
    damping: str = "0.1"
    rest_velocity: str = "0.01"
    max_time: str = "5.0"
    collision_margin: str = "0.001"

class ExportParams(BaseModel):
    formats: List[str]
    units: str = "m"
    scale: str = "1.0"
    wall_mode: str
    fluid_mode: str
    manifold_check: bool = True
    merge_distance: str = "0.001"

class CFDParams(BaseModel):
    regime: str
    inlet_velocity: str = "0.1"
    fluid_density: str = "1000.0"
    fluid_viscosity: str = "0.001"
    max_iterations: str = "1000"
    convergence_criteria: str = "1e-6"
    write_fields: bool = False

class WizardParams(BaseModel):
    bed: BedParams
    lids: LidsParams
    particles: ParticlesParams
    packing: PackingParams
    export: ExportParams
    cfd: Optional[CFDParams] = None

class WizardRequest(BaseModel):
    mode: str  # interactive, blender, blender_interactive
    fileName: str
    params: WizardParams

@router.post("/bed/wizard")
async def create_bed_from_wizard(request: WizardRequest):
    """
    criar arquivo .bed a partir dos parâmetros do wizard web
    """
    try:
        # definir caminhos
        project_root = Path(__file__).parent.parent.parent.parent
        dsl_dir = project_root / "dsl"
        output_dir = beds_dir()
        
        # gerar conteúdo do arquivo .bed
        bed_content = generate_bed_content(request.params, request.mode)
        
        # salvar arquivo .bed
        bed_file_path = output_dir / request.fileName
        with open(bed_file_path, 'w', encoding='utf-8') as f:
            f.write(bed_content)
        
        # compilar com ANTLR
        json_file_path = bed_file_path.with_suffix('.bed.json')
        compiler_script = dsl_dir / "compiler" / "bed_compiler_antlr_standalone.py"
        
        result = subprocess.run([
            sys.executable,
            str(compiler_script),
            str(bed_file_path),
            "-o", str(json_file_path),
            "-v"
        ], capture_output=True, text=True, cwd=dsl_dir)
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=400,
                detail=f"erro na compilação: {result.stderr}"
            )
        
        return {
            "success": True,
            "bed_file": str(bed_file_path.relative_to(project_root)),
            "json_file": str(json_file_path.relative_to(project_root)),
            "message": "arquivo .bed criado e compilado com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_bed_content(params: WizardParams, mode: str) -> str:
    """
    gerar conteúdo do arquivo .bed a partir dos parâmetros
    """
    lines = ["// arquivo .bed gerado pelo wizard web"]
    lines.append(f"// modo: {mode}")
    lines.append("")
    
    # seção bed
    lines.append("bed {")
    lines.append(f"    diameter = {params.bed.diameter} m;")
    lines.append(f"    height = {params.bed.height} m;")
    lines.append(f"    wall_thickness = {params.bed.wall_thickness} m;")
    lines.append(f"    clearance = {params.bed.clearance} m;")
    lines.append(f"    material = \"{params.bed.material}\";")
    if params.bed.roughness and float(params.bed.roughness) > 0:
        lines.append(f"    roughness = {params.bed.roughness} m;")
    lines.append("}")
    lines.append("")
    
    # seção lids
    lines.append("lids {")
    lines.append(f"    top_type = \"{params.lids.top_type}\";")
    lines.append(f"    bottom_type = \"{params.lids.bottom_type}\";")
    lines.append(f"    top_thickness = {params.lids.top_thickness} m;")
    lines.append(f"    bottom_thickness = {params.lids.bottom_thickness} m;")
    if params.lids.seal_clearance and float(params.lids.seal_clearance) > 0:
        lines.append(f"    seal_clearance = {params.lids.seal_clearance} m;")
    lines.append("}")
    lines.append("")
    
    # seção particles
    lines.append("particles {")
    lines.append(f"    kind = \"{params.particles.kind}\";")
    lines.append(f"    diameter = {params.particles.diameter} m;")
    lines.append(f"    count = {params.particles.count};")
    if params.particles.target_porosity and float(params.particles.target_porosity) > 0:
        lines.append(f"    target_porosity = {params.particles.target_porosity};")
    lines.append(f"    density = {params.particles.density} kg/m3;")
    if params.particles.mass and float(params.particles.mass) > 0:
        lines.append(f"    mass = {params.particles.mass} g;")
    if params.particles.restitution:
        lines.append(f"    restitution = {params.particles.restitution};")
    if params.particles.friction:
        lines.append(f"    friction = {params.particles.friction};")
    if params.particles.rolling_friction:
        lines.append(f"    rolling_friction = {params.particles.rolling_friction};")
    if params.particles.linear_damping:
        lines.append(f"    linear_damping = {params.particles.linear_damping};")
    if params.particles.angular_damping:
        lines.append(f"    angular_damping = {params.particles.angular_damping};")
    if params.particles.seed:
        lines.append(f"    seed = {params.particles.seed};")
    lines.append("}")
    lines.append("")
    
    # seção packing
    lines.append("packing {")
    lines.append(f"    method = \"{params.packing.method}\";")
    lines.append(f"    gravity = {params.packing.gravity} m/s2;")
    if params.packing.substeps:
        lines.append(f"    substeps = {params.packing.substeps};")
    if params.packing.iterations:
        lines.append(f"    iterations = {params.packing.iterations};")
    if params.packing.damping:
        lines.append(f"    damping = {params.packing.damping};")
    if params.packing.rest_velocity:
        lines.append(f"    rest_velocity = {params.packing.rest_velocity} m/s;")
    if params.packing.max_time:
        lines.append(f"    max_time = {params.packing.max_time} s;")
    if params.packing.collision_margin:
        lines.append(f"    collision_margin = {params.packing.collision_margin} m;")
    lines.append("}")
    lines.append("")
    
    # seção export
    lines.append("export {")
    formats_str = ", ".join([f'"{fmt}"' for fmt in params.export.formats])
    lines.append(f"    formats = [{formats_str}];")
    if params.export.units:
        lines.append(f"    units = \"{params.export.units}\";")
    if params.export.scale:
        lines.append(f"    scale = {params.export.scale};")
    lines.append(f"    wall_mode = \"{params.export.wall_mode}\";")
    lines.append(f"    fluid_mode = \"{params.export.fluid_mode}\";")
    if params.export.manifold_check is not None:
        lines.append(f"    manifold_check = {str(params.export.manifold_check).lower()};")
    if params.export.merge_distance:
        lines.append(f"    merge_distance = {params.export.merge_distance} m;")
    lines.append("}")
    lines.append("")
    
    # seção cfd (se presente e modo não for blender)
    if params.cfd and mode not in ['blender', 'blender_interactive']:
        lines.append("cfd {")
        lines.append(f"    regime = \"{params.cfd.regime}\";")
        if params.cfd.inlet_velocity:
            lines.append(f"    inlet_velocity = {params.cfd.inlet_velocity} m/s;")
        if params.cfd.fluid_density:
            lines.append(f"    fluid_density = {params.cfd.fluid_density} kg/m3;")
        if params.cfd.fluid_viscosity:
            lines.append(f"    fluid_viscosity = {params.cfd.fluid_viscosity} Pa.s;")
        if params.cfd.max_iterations:
            lines.append(f"    max_iterations = {params.cfd.max_iterations};")
        if params.cfd.convergence_criteria:
            lines.append(f"    convergence_criteria = {params.cfd.convergence_criteria};")
        if params.cfd.write_fields is not None:
            lines.append(f"    write_fields = {str(params.cfd.write_fields).lower()};")
        lines.append("}")
    
    return "\n".join(lines)

@router.get("/bed/wizard/help/{section}")
async def get_wizard_help(section: str):
    """
    obter informações de ajuda para uma seção específica
    """
    help_info = {
        "bed": {
            "title": "geometria do leito",
            "params": {
                "diameter": {
                    "desc": "diâmetro interno do leito cilíndrico",
                    "min": 0.01, "max": 2.0, "unit": "m",
                    "exemplo": "leito de 5cm = 0.05m"
                },
                "height": {
                    "desc": "altura total do leito cilíndrico",
                    "min": 0.01, "max": 5.0, "unit": "m",
                    "exemplo": "leito de 10cm = 0.1m"
                }
            }
        },
        "particles": {
            "title": "partículas",
            "params": {
                "count": {
                    "desc": "quantidade total de partículas",
                    "min": 1, "max": 10000,
                    "exemplo": "100 = rápido, 1000 = detalhado"
                },
                "diameter": {
                    "desc": "diâmetro das partículas",
                    "min": 0.0001, "max": 0.5, "unit": "m",
                    "exemplo": "5mm = 0.005m"
                }
            }
        }
    }
    
    if section not in help_info:
        raise HTTPException(status_code=404, detail="seção não encontrada")
    
    return help_info[section]


# modelo para template
class TemplateRequest(BaseModel):
    template: str


@router.post("/bed/template")
async def compile_template(request: TemplateRequest):
    """
    compilar template .bed editado manualmente
    """
    try:
        # criar arquivo temporário com o template
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bed', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(request.template)
            temp_bed_path = Path(temp_file.name)
        
        # definir caminho para o json de saída
        temp_json_path = temp_bed_path.with_suffix('.json')
        
        # compilar usando antlr
        compiler_path = Path(__file__).parent.parent.parent.parent / "dsl" / "compiler" / "bed_compiler_antlr_standalone.py"
        
        if not compiler_path.exists():
            raise HTTPException(status_code=500, detail="compilador não encontrado")
        
        result = subprocess.run([
            sys.executable,
            str(compiler_path),
            str(temp_bed_path),
            "-o", str(temp_json_path),
            "-v"
        ], capture_output=True, text=True, timeout=30)
        
        # limpar arquivo temporário .bed
        temp_bed_path.unlink()
        
        if result.returncode == 0:
            # ler json gerado
            if temp_json_path.exists():
                with open(temp_json_path, 'r', encoding='utf-8') as f:
                    params_json = json.load(f)
                
                # limpar arquivo json temporário
                temp_json_path.unlink()
                
                return {
                    "success": True,
                    "message": "template compilado com sucesso!",
                    "params": params_json,
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "message": "compilação executou mas json não foi gerado",
                    "error": result.stdout
                }
        else:
            return {
                "success": False,
                "message": "erro na compilação do template",
                "error": result.stderr
            }
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="timeout na compilação")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro: {str(e)}")

# novos endpoints para arquivos .bed
@router.get("/bed/template/default", tags=["bed"])
async def get_default_bed_template():
    """
    retorna um template padrão de arquivo .bed
    """
    default_template = """bed {
    diameter = 0.05 m;
    height = 0.1 m;
    wall_thickness = 0.002 m;
    clearance = 0.01 m;
    material = "steel";
    roughness = 0.0 m;
}

lids {
    top_type = "flat";
    bottom_type = "flat";
    top_thickness = 0.003 m;
    bottom_thickness = 0.003 m;
    seal_clearance = 0.001 m;
}

particles {
    kind = "sphere";
    diameter = 0.005 m;
    count = 100;
    target_porosity = 0.4;
    density = 2500.0 kg/m3;
    mass = 0.0 g;
    restitution = 0.3;
    friction = 0.5;
    rolling_friction = 0.1;
    linear_damping = 0.1;
    angular_damping = 0.1;
    seed = 42;
}

packing {
    method = "rigid_body";
    gravity = -9.81 m/s2;
    substeps = 10;
    iterations = 10;
    damping = 0.1;
    rest_velocity = 0.01 m/s;
    max_time = 5.0 s;
    collision_margin = 0.001 m;
}

export {
    formats = ["stl_binary", "blend"];
    units = "m";
    scale = 1.0;
    wall_mode = "surface";
    fluid_mode = "none";
    manifold_check = true;
    merge_distance = 0.001 m;
}"""
    
    return {
        "content": default_template,
        "filename": "template_padrao.bed"
    }

@router.post("/bed/process", tags=["bed"])
async def process_bed_file(request: Dict[str, Any]):
    """
    processa um arquivo .bed carregado
    """
    try:
        content = request.get("content", "")
        filename = request.get("filename", "leito_custom.bed")
        
        if not content.strip():
            raise HTTPException(status_code=400, detail="conteúdo do arquivo .bed está vazio")
        
        # criar arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bed', delete=False) as temp_file:
            temp_file.write(content)
            temp_bed_path = temp_file.name
        
        # compilar arquivo .bed
        compiler_script = Path(__file__).parent.parent.parent / "dsl" / "compiler" / "bed_compiler_antlr_standalone.py"
        
        if not compiler_script.exists():
            raise HTTPException(status_code=500, detail="compilador não encontrado")
        
        result = subprocess.run([
            sys.executable, str(compiler_script), temp_bed_path
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # arquivo compilado com sucesso
            json_path = temp_bed_path.replace('.bed', '.json')
            
            return {
                "success": True,
                "message": "arquivo .bed processado com sucesso",
                "bed_file": temp_bed_path,
                "json_file": json_path,
                "filename": filename
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"erro na compilação: {result.stderr}"
            )
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="timeout na compilação")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro: {str(e)}")


@router.get("/wizard/cli-instructions")
async def wizard_cli_instructions():
    """
    comandos para correr o bed wizard no terminal (fora do browser).
    """
    root = _repo_root()
    script = root / "bed_wizard.py"
    py = shutil.which("python") or shutil.which("python3") or sys.executable
    win = f'cd /d "{root}" && "{py}" bed_wizard.py'
    unix = f'cd "{root}" && "{py}" bed_wizard.py'
    return {
        "project_root": str(root),
        "script": str(script),
        "script_exists": script.is_file(),
        "python": py,
        "windows_cmd": win,
        "unix_sh": unix,
        "hint": "recomendado: pip install -r dsl/requirements-terminal.txt (rich)",
    }


@router.post("/wizard/launch-cli-terminal")
async def wizard_launch_cli_terminal():
    """
    tenta abrir uma nova janela de terminal com o wizard cli.
    windows: cmd /k; linux: gnome-terminal ou xterm se existir.
    """
    root = _repo_root()
    script = root / "bed_wizard.py"
    if not script.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"bed_wizard.py nao encontrado em {script}",
        )
    py = shutil.which("python") or shutil.which("python3") or sys.executable
    inner = f'cd /d "{root}" && "{py}" "{script}"' if os.name == "nt" else f'cd "{root}" && "{py}" "{script}"'

    try:
        if os.name == "nt":
            subprocess.Popen(
                [
                    "cmd.exe",
                    "/c",
                    "start",
                    "bed wizard cli",
                    "cmd.exe",
                    "/k",
                    inner,
                ],
                cwd=str(root),
                shell=False,
            )
        else:
            launched = False
            for cmd in (
                [
                    "gnome-terminal",
                    "--",
                    "bash",
                    "-lc",
                    f'{inner}; exec bash',
                ],
                [
                    "xterm",
                    "-e",
                    f'bash -lc "{inner}; read"',
                ],
            ):
                try:
                    subprocess.Popen(cmd, cwd=str(root))
                    launched = True
                    break
                except FileNotFoundError:
                    continue
            if not launched:
                raise HTTPException(
                    status_code=503,
                    detail="terminal grafico nao encontrado (gnome-terminal ou xterm)",
                )
        return {"ok": True, "message": "terminal solicitado; se nada abrir, copie o comando de /api/wizard/cli-instructions"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

