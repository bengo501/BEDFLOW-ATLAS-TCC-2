# gera texto bed corre subprocesso antlr e opcional grava linha na base
# traduz dict flat ou aninhado em sintaxe dsl e chama compilador externo
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from bedflow_local_paths import beds_dir

class BedService:
    def __init__(self):
        # quatro niveis acima leva a raiz do repo onde existem dsl e output
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.dsl_dir = self.project_root / "dsl"
        self.compiler_script = self.dsl_dir / "compiler" / "bed_compiler_antlr_standalone.py"
        # ficheiros .bed e .bed.json canonicos em local_data/beds
        self.output_dir = beds_dir()

    def check_availability(self) -> bool:
        # true se o script python do compilador existir no disco
        return self.compiler_script.exists()

    def _merge_packing_into_compiled_json(
        self, json_file: str, parameters: Dict[str, Any]
    ) -> None:
        # o compilador antlr gera json so com chaves que existem na gramatica bed
        # campos novos como gap random_seed strict_validation ficam no dict python apos normalizar
        # esta funcao reescreve o json final juntando essas chaves em packing
        # o blender le o arquivo ja mesclado quando o backend chama generate model
        jp = Path(json_file)
        if not jp.is_file():
            alt = beds_dir() / jp.name
            if alt.is_file():
                jp = alt
            else:
                return
        try:
            data = json.loads(jp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        extra = parameters.get("packing")
        if not isinstance(extra, dict):
            return
        if "packing" not in data or not isinstance(data["packing"], dict):
            data["packing"] = {}
        for k, v in extra.items():
            if v is not None:
                data["packing"][k] = v
        try:
            jp.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except OSError:
            pass
    
    async def compile_bed(
        self,
        parameters: Dict[str, Any],
        filename: Optional[str] = None,
        save_to_db: bool = False,
        db_session = None,
        user_id: int = 1,
    ) -> Dict[str, Any]:
        """
        compila parâmetros em arquivo .bed e .bed.json
        
        args:
            parameters: dicionário com parâmetros do leito
            filename: nome do arquivo (opcional, gera automaticamente se None)
            save_to_db: salvar leito no banco de dados
            db_session: sessão do banco (necessário se save_to_db=True)
        
        returns:
            dict com caminhos dos arquivos gerados e opcionalmente bed_id
        """
        parameters = self._normalize_parameters_for_generation(parameters)

        # gerar nome de arquivo se não fornecido
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"leito_{timestamp}"
        
        # garantir que não tem extensão
        filename = filename.replace(".bed", "").replace(".json", "")
        
        # criar arquivo .bed
        bed_content = self._generate_bed_content(parameters)
        bed_file = self.output_dir / f"{filename}.bed"
        
        bed_file.write_text(bed_content, encoding="utf-8")
        
        # compilar usando script existente
        json_file = await self._run_compiler(str(bed_file))

        # garante que o arquivo consumido pelo script blender tenha packing completo
        self._merge_packing_into_compiled_json(json_file, parameters)

        result = {
            "bed_file": str(bed_file.relative_to(self.project_root)),
            "json_file": str(Path(json_file).relative_to(self.project_root))
        }
        
        # salvar no banco se solicitado (opcional - falha graciosamente se banco não disponível)
        if save_to_db:
            try:
                from backend.app.database import crud, schemas
                from backend.app.database.connection import DatabaseConnection
                
                p_bed = parameters.get("bed") or {}
                p_part = parameters.get("particles") or {}
                p_pack = parameters.get("packing") or {}
                bed_data = schemas.BedCreate(
                    name=filename,
                    description=f"leito gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    diameter=p_bed.get("diameter", 0.05),
                    height=p_bed.get("height", 0.1),
                    wall_thickness=p_bed.get("wall_thickness", 0.002),
                    particle_count=int(p_part.get("count", 100)),
                    particle_diameter=p_part.get("diameter", 0.005),
                    particle_kind=p_part.get("kind", "sphere"),
                    packing_method=p_pack.get("method", "rigid_body"),
                    porosity=p_part.get("target_porosity"),
                    bed_file_path=result["bed_file"],
                    json_file_path=result["json_file"],
                    parameters_json=parameters,
                    created_by='api'
                )

                own_session = None
                session = db_session
                if session is None:
                    own_session = DatabaseConnection.get_session()
                    session = own_session

                db_bed = crud.BedCRUD.create(session, bed_data, user_id=user_id)
                result["bed_id"] = db_bed.id
                if own_session is not None:
                    own_session.close()
            except Exception as db_error:
                # Falha graciosamente - banco não é obrigatório para compilação
                # Log do erro mas continua o processo
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Falha ao salvar no banco de dados (continuando sem salvar): {str(db_error)}")
                # Não adiciona bed_id ao resultado, mas continua normalmente
        
        return result

    def _normalize_parameters_for_generation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """converte BedParameters plano (api compile) na estrutura aninhada do template .bed"""
        if not isinstance(params, dict):
            return {}
        out = dict(params)
        bed = out.get("bed")
        if isinstance(bed, dict) and bed:
            return out
        if "diameter" not in out and "particle_count" not in out:
            return out

        out["bed"] = {
            "diameter": out.get("diameter", 0.05),
            "height": out.get("height", 0.1),
            "wall_thickness": out.get("wall_thickness", 0.002),
            "clearance": out.get("clearance", 0.01),
            "material": out.get("material", "steel"),
            "roughness": out.get("roughness", 0.0),
        }
        out["lids"] = {
            "top_type": out.get("lid_top", "flat"),
            "bottom_type": out.get("lid_bottom", "flat"),
            "top_thickness": out.get("lid_thickness", 0.003),
            "bottom_thickness": out.get("lid_thickness", 0.003),
            "seal_clearance": out.get("seal_clearance", 0.001),
        }
        out["particles"] = {
            "kind": out.get("particle_type", "sphere"),
            "diameter": out.get("particle_diameter", 0.005),
            "count": out.get("particle_count", 100),
            "target_porosity": out.get("target_porosity", 0.4),
            "density": out.get("density", 2500.0),
            "mass": out.get("mass", 0.0),
            "restitution": out.get("restitution", 0.3),
            "friction": out.get("friction", 0.5),
            "rolling_friction": out.get("rolling_friction", 0.1),
            "linear_damping": out.get("linear_damping", 0.1),
            "angular_damping": out.get("angular_damping", 0.1),
            "seed": out.get("seed", 42),
        }
        p_pack = {
            "method": out.get("packing_method", "rigid_body"),
            "gravity": out.get("gravity", -9.81),
            "substeps": out.get("substeps", 10),
            "iterations": out.get("iterations", 10),
            "damping": out.get("damping", 0.1),
            "rest_velocity": out.get("rest_velocity", 0.01),
            "max_time": out.get("max_time", 5.0),
            "collision_margin": out.get("collision_margin", 0.001),
            "gap": out.get("packing_gap", 0.0),
            "max_placement_attempts": out.get("max_placement_attempts", 500_000),
            "strict_validation": out.get("strict_validation", True),
        }
        if out.get("packing_random_seed") is not None:
            p_pack["random_seed"] = out["packing_random_seed"]
        if out.get("hex_step_x") is not None:
            p_pack["step_x"] = out["hex_step_x"]
        out["packing"] = p_pack
        if not isinstance(out.get("export"), dict):
            out["export"] = {}
        return out
    
    def _generate_bed_content(self, params: Dict[str, Any]) -> str:
        """gera conteúdo do arquivo .bed"""
        # extrair parâmetros da estrutura aninhada
        bed_params = params.get('bed', {})
        lids_params = params.get('lids', {})
        particles_params = params.get('particles', {})
        packing_params = params.get('packing', {})
        
        content = f"""bed {{
    diameter = {bed_params.get('diameter', 0.05)} m;
    height = {bed_params.get('height', 0.1)} m;
    wall_thickness = {bed_params.get('wall_thickness', 0.002)} m;
    clearance = {bed_params.get('clearance', 0.01)} m;
    material = "{bed_params.get('material', 'steel')}";
    roughness = {bed_params.get('roughness', 0.0)} m;
}}

lids {{
    top_type = "{lids_params.get('top_type', 'flat')}";
    bottom_type = "{lids_params.get('bottom_type', 'flat')}";
    top_thickness = {lids_params.get('top_thickness', 0.003)} m;
    bottom_thickness = {lids_params.get('bottom_thickness', 0.003)} m;
    seal_clearance = {lids_params.get('seal_clearance', 0.001)} m;
}}

particles {{
    kind = "{particles_params.get('kind', 'sphere')}";
    diameter = {particles_params.get('diameter', 0.005)} m;
    count = {particles_params.get('count', 100)};
    target_porosity = {particles_params.get('target_porosity', 0.4)};
    density = {particles_params.get('density', 2500.0)} kg/m3;
    mass = {particles_params.get('mass', 0.0)} g;
    restitution = {particles_params.get('restitution', 0.3)};
    friction = {particles_params.get('friction', 0.5)};
    rolling_friction = {particles_params.get('rolling_friction', 0.1)};
    linear_damping = {particles_params.get('linear_damping', 0.1)};
    angular_damping = {particles_params.get('angular_damping', 0.1)};
    seed = {particles_params.get('seed', 42)};
}}

packing {{
    method = "{packing_params.get('method', 'rigid_body')}";
    gravity = {packing_params.get('gravity', -9.81)} m/s2;
    substeps = {packing_params.get('substeps', 10)};
    iterations = {packing_params.get('iterations', 10)};
    damping = {packing_params.get('damping', 0.1)};
    rest_velocity = {packing_params.get('rest_velocity', 0.01)} m/s;
    max_time = {packing_params.get('max_time', 5.0)} s;
    collision_margin = {packing_params.get('collision_margin', 0.001)} m;
}}

export {{
    formats = ["stl_binary", "blend"];
    units = "m";
    scale = 1.0;
    wall_mode = "surface";
    fluid_mode = "none";
    manifold_check = true;
    merge_distance = 0.001 m;
}}
"""
        
        # adicionar seção cfd se parâmetros fornecidos
        if 'cfd_regime' in params:
            content += f"""
cfd {{
    regime = "{params['cfd_regime']}";
    inlet_velocity = {params.get('inlet_velocity', 0.01)} m/s;
    fluid_density = {params.get('fluid_density', 1000.0)} kg/m3;
    fluid_viscosity = {params.get('fluid_viscosity', 0.001)} Pa.s;
}}
"""
        
        return content
    
    async def _run_compiler(self, bed_file: str) -> str:
        """executa compilador antlr"""
        try:
            # arquivo json gerado tem mesmo nome + .json
            json_file = f"{bed_file}.json"
            
            # executar compilador com parâmetro -o para especificar saída
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.compiler_script),
                    bed_file,
                    "-o", json_file,
                    "-v"  # modo verbose para debug
                ],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.dsl_dir)
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else result.stdout
                raise Exception(f"erro na compilação: {error_msg}")
            
            # verificar se arquivo foi gerado
            json_path = Path(json_file)
            if not json_path.exists():
                # tentar caminho absoluto
                json_path = Path(bed_file).parent / Path(json_file).name
                if not json_path.exists():
                    raise Exception(f"arquivo json não foi gerado. stdout: {result.stdout}, stderr: {result.stderr}")
                json_file = str(json_path)
            
            return json_file
            
        except subprocess.TimeoutExpired:
            raise Exception("timeout na compilação (>30s)")
        except Exception as e:
            raise Exception(f"erro ao executar compilador: {str(e)}")
    
    async def validate_bed(self, filename: str) -> Dict[str, Any]:
        """valida arquivo .bed existente"""
        bed_file = self.output_dir / filename
        
        if not bed_file.exists():
            raise FileNotFoundError(f"arquivo {filename} não encontrado")
        
        try:
            # tentar compilar para validar sintaxe
            json_file = await self._run_compiler(str(bed_file))
            
            return {
                "valid": True,
                "bed_file": str(bed_file.relative_to(self.project_root)),
                "json_file": str(Path(json_file).relative_to(self.project_root)),
                "message": "arquivo válido"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "bed_file": str(bed_file.relative_to(self.project_root)),
                "message": str(e)
            }

