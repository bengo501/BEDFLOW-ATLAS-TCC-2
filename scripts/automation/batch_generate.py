#!/usr/bin/env python3
# script para geracao em lote de multiplos leitos com variacoes parametricas
import os
import sys
import subprocess
import json
from pathlib import Path
import itertools
import time

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
from bedflow_local_paths import aux_dir

class BatchGenerator:
    """classe para gerar multiplos leitos variando parametros"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.output_dir = aux_dir() / "batch"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dsl_dir = self.project_root / "dsl"
        self.wizard = self.dsl_dir / "bed_wizard.py"
        self.compiler = self.dsl_dir / "compiler" / "bed_compiler_antlr_standalone.py"
        
    def create_bed_file(self, params, output_name):
        """cria arquivo .bed com parametros especificos"""
        bed_content = f"""bed {{
    diameter = {params['diameter']}m
    height = {params['height']}m
    wall_thickness = {params['wall_thickness']}m
    shape = "cylinder"
}}

lids {{
    top_type = "flat"
    bottom_type = "flat"
    thickness = 0.003m
}}

particles {{
    count = {params['particle_count']}
    kind = "sphere"
    diameter = {params['particle_diameter']}m
    mass = {params['particle_mass']}kg
    friction = 0.5
    restitution = 0.3
}}

packing {{
    method = "rigid_body"
    seed = {params.get('seed', 42)}
    substeps = 10
    iterations = 100
    gravity = (0, 0, -9.81) m/s2
}}

export {{
    formats = ["blend", "stl"]
    output_dir = "generated/batch/{output_name}"
}}

cfd {{
    regime = "laminar"
    inlet_velocity = {params.get('inlet_velocity', 0.1)} m/s
    outlet_pressure = 0 Pa
    fluid_density = {params.get('fluid_density', 1000)} kg/m3
    fluid_viscosity = {params.get('fluid_viscosity', 0.001)} Pa.s
    max_iterations = 1000
    convergence_criteria = 1e-6
}}
"""
        
        bed_file = self.output_dir / f"{output_name}.bed"
        bed_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(bed_file, 'w', encoding='utf-8') as f:
            f.write(bed_content)
        
        return bed_file
    
    def compile_bed_file(self, bed_file):
        """compila arquivo .bed"""
        try:
            result = subprocess.run(
                [sys.executable, str(self.compiler), str(bed_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            json_file = bed_file.with_suffix('.bed.json')
            if json_file.exists():
                return json_file
            else:
                print(f"[erro] compilacao falhou: {bed_file.name}")
                return None
                
        except Exception as e:
            print(f"[erro] erro ao compilar {bed_file.name}: {e}")
            return None
    
    def generate_parametric_study(self, parameter_ranges):
        """gera estudo parametrico variando parametros"""
        print("="*70)
        print("  GERACAO EM LOTE - ESTUDO PARAMETRICO")
        print("="*70)
        
        # calcular total de combinacoes
        total_combinations = 1
        for values in parameter_ranges.values():
            total_combinations *= len(values)
        
        print(f"\nparametros a variar:")
        for param, values in parameter_ranges.items():
            print(f"  {param}: {values}")
        
        print(f"\ntotal de combinacoes: {total_combinations}")
        
        # confirmar
        if total_combinations > 10:
            response = input(f"\ngerar {total_combinations} leitos? (s/n) [n]: ").strip().lower()
            if response not in ['s', 'sim', 'y', 'yes']:
                print("operacao cancelada")
                return []
        
        # gerar todas as combinacoes
        param_names = list(parameter_ranges.keys())
        param_values = list(parameter_ranges.values())
        
        generated_files = []
        
        print(f"\ngerando {total_combinations} arquivos .bed...")
        
        for i, combination in enumerate(itertools.product(*param_values), 1):
            # criar dict de parametros
            params = dict(zip(param_names, combination))
            
            # criar nome do arquivo
            name_parts = [f"{k}{v}".replace('.', 'p') for k, v in params.items()]
            output_name = "leito_" + "_".join(name_parts)
            
            # criar arquivo .bed
            bed_file = self.create_bed_file(params, output_name)
            
            # compilar
            json_file = self.compile_bed_file(bed_file)
            
            if json_file:
                generated_files.append({
                    'name': output_name,
                    'bed': bed_file,
                    'json': json_file,
                    'params': params
                })
                print(f"[{i}/{total_combinations}] {output_name}")
            else:
                print(f"[{i}/{total_combinations}] [falha] {output_name}")
        
        print(f"\n[ok] {len(generated_files)} arquivos gerados")
        
        # salvar manifesto
        manifest = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total': len(generated_files),
            'parameter_ranges': parameter_ranges,
            'files': generated_files
        }
        
        manifest_file = self.output_dir / "manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, default=str)
        
        print(f"manifesto salvo: {manifest_file}")
        
        return generated_files
    
    def generate_from_template(self, template_params, variations):
        """gera leitos a partir de template com variacoes"""
        print("="*70)
        print("  GERACAO EM LOTE - A PARTIR DE TEMPLATE")
        print("="*70)
        
        print(f"\ntemplate base:")
        for key, value in template_params.items():
            print(f"  {key}: {value}")
        
        print(f"\nvariacoes: {len(variations)}")
        
        generated_files = []
        
        for i, variation in enumerate(variations, 1):
            # mesclar template com variacao
            params = {**template_params, **variation}
            
            # criar nome
            variation_id = variation.get('name', f"var{i:03d}")
            output_name = f"leito_{variation_id}"
            
            # criar arquivo .bed
            bed_file = self.create_bed_file(params, output_name)
            
            # compilar
            json_file = self.compile_bed_file(bed_file)
            
            if json_file:
                generated_files.append({
                    'name': output_name,
                    'bed': bed_file,
                    'json': json_file,
                    'params': params
                })
                print(f"[{i}/{len(variations)}] {output_name}")
        
        print(f"\n[ok] {len(generated_files)} arquivos gerados")
        
        return generated_files

def main():
    """funcao principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='geracao em lote de leitos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
exemplos:

  # estudo parametrico (varia diametro e altura)
  python batch_generate.py --parametric \\
    --diameter 0.05 0.1 0.15 \\
    --height 0.1 0.2 0.3

  # a partir de json de configuracao
  python batch_generate.py --config batch_config.json
        """
    )
    
    parser.add_argument('--parametric', action='store_true',
                       help='gerar estudo parametrico')
    parser.add_argument('--diameter', nargs='+', type=float,
                       help='valores de diametro (m)')
    parser.add_argument('--height', nargs='+', type=float,
                       help='valores de altura (m)')
    parser.add_argument('--particle-count', nargs='+', type=int,
                       help='valores de numero de particulas')
    parser.add_argument('--particle-diameter', nargs='+', type=float,
                       help='valores de diametro de particula (m)')
    parser.add_argument('--config', type=str,
                       help='arquivo json de configuracao')
    
    args = parser.parse_args()
    
    generator = BatchGenerator()
    
    if args.parametric:
        # estudo parametrico
        parameter_ranges = {}
        
        if args.diameter:
            parameter_ranges['diameter'] = args.diameter
        else:
            parameter_ranges['diameter'] = [0.05, 0.1]
        
        if args.height:
            parameter_ranges['height'] = args.height
        else:
            parameter_ranges['height'] = [0.1, 0.2]
        
        if args.particle_count:
            parameter_ranges['particle_count'] = args.particle_count
        else:
            parameter_ranges['particle_count'] = [50, 100]
        
        if args.particle_diameter:
            parameter_ranges['particle_diameter'] = args.particle_diameter
        else:
            parameter_ranges['particle_diameter'] = [0.005]
        
        # parametros fixos
        parameter_ranges['wall_thickness'] = [0.002]
        parameter_ranges['particle_mass'] = [0.1]
        
        files = generator.generate_parametric_study(parameter_ranges)
        
        print(f"\nproximos passos:")
        print(f"1. gerar modelos 3d:")
        print(f"   for f in generated/batch/*.bed.json; do")
        print(f"     python scripts/blender_scripts/leito_extracao.py --params $f")
        print(f"   done")
        print(f"2. executar simulacoes cfd em cada modelo")
        
    elif args.config:
        # a partir de arquivo de configuracao
        config_file = Path(args.config)
        
        if not config_file.exists():
            print(f"[erro] arquivo nao encontrado: {config_file}")
            sys.exit(1)
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        template_params = config.get('template', {})
        variations = config.get('variations', [])
        
        files = generator.generate_from_template(template_params, variations)
        
    else:
        # exemplo padrao
        print("executando exemplo padrao...")
        print("use --help para ver opcoes")
        
        parameter_ranges = {
            'diameter': [0.05, 0.1],
            'height': [0.1, 0.2],
            'particle_count': [50, 100],
            'particle_diameter': [0.005],
            'wall_thickness': [0.002],
            'particle_mass': [0.1]
        }
        
        files = generator.generate_parametric_study(parameter_ranges)

if __name__ == "__main__":
    main()

