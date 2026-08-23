#!/usr/bin/env python3
# script mestre de configuracao completa do projeto
import os
import sys
import subprocess
import platform
from pathlib import Path
import time

class CompleteSetup:
    """classe para configuracao completa do projeto bedflow-atlas"""
    
    def __init__(self):
        self.system = platform.system()
        self.project_root = Path(__file__).parent.parent.parent
        self.scripts_dir = self.project_root / "scripts" / "automation"
        self.components = {
            'python': False,
            'java': False,
            'antlr': False,
            'blender': False,
            'wsl': False,
            'openfoam': False
        }
        
    def print_header(self):
        """imprime cabecalho"""
        print("="*70)
        print("  CONFIGURADOR COMPLETO - BEDFLOW-ATLAS")
        print("="*70)
        print(f"sistema operacional: {self.system}")
        print(f"diretorio do projeto: {self.project_root}")
        print()
    
    def check_python(self):
        """verifica python"""
        print("\n[componente 1/6] python")
        print("-" * 50)
        
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                print(f"[ok] python {version.major}.{version.minor}.{version.micro}")
                self.components['python'] = True
                return True
            else:
                print(f"[erro] python {version.major}.{version.minor} muito antigo")
                print("  requer python 3.8+")
                return False
                
        except Exception as e:
            print(f"[erro] falha ao verificar python: {e}")
            return False
    
    def setup_java_antlr(self):
        """configura java e antlr"""
        print("\n[componente 2/6] java + antlr")
        print("-" * 50)
        
        try:
            # executar instalador antlr
            installer_path = self.scripts_dir / "install_antlr.py"
            
            if not installer_path.exists():
                print(f"[erro] instalador nao encontrado: {installer_path}")
                return False
            
            print("  executando instalador antlr...")
            result = subprocess.run(
                [sys.executable, str(installer_path)],
                timeout=600
            )
            
            if result.returncode == 0:
                print("[ok] java + antlr configurados")
                self.components['java'] = True
                self.components['antlr'] = True
                return True
            else:
                print("[erro] falha na configuracao java/antlr")
                return False
                
        except Exception as e:
            print(f"[erro] erro ao configurar java/antlr: {e}")
            return False
    
    def setup_blender(self):
        """configura blender"""
        print("\n[componente 3/6] blender")
        print("-" * 50)
        
        try:
            # verificar se blender ja existe
            try:
                result = subprocess.run(
                    ["blender", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    print("[ok] blender ja instalado")
                    self.components['blender'] = True
                    return True
                    
            except FileNotFoundError:
                pass
            
            # executar instalador blender
            installer_path = self.scripts_dir / "install_blender.py"
            
            if not installer_path.exists():
                print(f"[aviso] instalador nao encontrado: {installer_path}")
                print("  blender deve ser instalado manualmente")
                return False
            
            print("  executando instalador blender...")
            result = subprocess.run(
                [sys.executable, str(installer_path)],
                timeout=1200
            )
            
            if result.returncode == 0:
                print("[ok] blender configurado")
                self.components['blender'] = True
                return True
            else:
                print("[aviso] falha na configuracao do blender")
                print("  instale manualmente de: https://www.blender.org/download/")
                return False
                
        except Exception as e:
            print(f"[aviso] erro ao configurar blender: {e}")
            return False
    
    def setup_wsl_openfoam(self):
        """configura wsl e openfoam (apenas windows)"""
        print("\n[componente 4/6] wsl + openfoam")
        print("-" * 50)
        
        if self.system != "Windows":
            print("[skip] wsl apenas necessario no windows")
            print("  para linux: sudo apt install openfoam")
            return True
        
        # perguntar ao usuario
        print("\n  openfoam requer wsl2 (subsistema windows para linux)")
        print("  a instalacao pode levar 30-60 minutos")
        response = input("\n  deseja instalar wsl2 + openfoam agora? (s/n) [n]: ").strip().lower()
        
        if response not in ['s', 'sim', 'y', 'yes']:
            print("[skip] instalacao do openfoam pulada")
            print("  para instalar depois: python scripts/automation/install_openfoam.py")
            return True
        
        try:
            # executar instalador openfoam
            installer_path = self.scripts_dir / "install_openfoam.py"
            
            if not installer_path.exists():
                print(f"[erro] instalador nao encontrado: {installer_path}")
                return False
            
            print("\n  executando instalador openfoam...")
            print("  isso pode levar muito tempo, seja paciente...")
            
            result = subprocess.run(
                [sys.executable, str(installer_path)],
                timeout=3600  # 1 hora
            )
            
            if result.returncode == 0:
                print("[ok] wsl + openfoam configurados")
                self.components['wsl'] = True
                self.components['openfoam'] = True
                return True
            else:
                print("[aviso] falha na configuracao openfoam")
                return False
                
        except Exception as e:
            print(f"[aviso] erro ao configurar openfoam: {e}")
            return False
    
    def create_directories(self):
        """cria diretorios do projeto"""
        print("\n[componente 5/6] estrutura de diretorios")
        print("-" * 50)
        
        directories = [
            "generated",
            "generated/3d",
            "generated/3d/blender",
            "generated/3d/exports",
            "generated/3d/output",
            "generated/cfd",
            "generated/configs",
            "dsl/examples",
            "dsl/generated",
            "temp",
            "logs"
        ]
        
        try:
            for dir_name in directories:
                dir_path = self.project_root / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"[ok] {dir_name}")
            
            return True
            
        except Exception as e:
            print(f"[erro] falha ao criar diretorios: {e}")
            return False
    
    def create_config_file(self):
        """cria arquivo de configuracao"""
        print("\n[componente 6/6] arquivo de configuracao")
        print("-" * 50)
        
        config_content = f"""# configuracao do projeto bedflow-atlas
# arquivo gerado automaticamente em {time.strftime('%Y-%m-%d %H:%M:%S')}

[project]
name = BEDFLOW-ATLAS
version = 1.0.0
root = {self.project_root}

[paths]
dsl_dir = dsl
scripts_dir = scripts
generated_dir = generated
configs_dir = generated/configs
models_dir = generated/3d/output
exports_dir = generated/3d/exports
blender_dir = generated/3d/blender
cfd_dir = generated/cfd
temp_dir = temp
logs_dir = logs

[components]
python = {self.components['python']}
java = {self.components['java']}
antlr = {self.components['antlr']}
blender = {self.components['blender']}
wsl = {self.components['wsl']}
openfoam = {self.components['openfoam']}

[bed_defaults]
# parametros padrao para leitos
altura = 0.1
diametro = 0.05
espessura_parede = 0.002
num_particulas = 100
diametro_particula = 0.005
massa_particula = 0.1

[cfd_defaults]
# parametros padrao para cfd
regime = laminar
inlet_velocity = 0.1
fluid_density = 1000
fluid_viscosity = 0.001
max_iterations = 1000
convergence_criteria = 1e-6

[export_defaults]
# formatos de exportacao padrao
formats = blend,stl
output_dir = generated/3d/output
"""
        
        try:
            # garantir que a pasta .config exista
            config_dir = self.project_root / ".config"
            config_dir.mkdir(parents=True, exist_ok=True)

            config_file = config_dir / "config.ini"
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            print(f"[ok] config.ini criado em {config_file}")
            return True
            
        except Exception as e:
            print(f"[erro] falha ao criar config: {e}")
            return False
    
    def run_tests(self):
        """executa testes basicos"""
        print("\n" + "="*70)
        print("  TESTES DE VERIFICACAO")
        print("="*70)
        
        tests = []
        
        # teste python
        tests.append(("python", self.components['python']))
        
        # teste java
        if self.components['java']:
            try:
                result = subprocess.run(
                    ["java", "-version"],
                    capture_output=True,
                    timeout=5
                )
                tests.append(("java", result.returncode == 0))
            except:
                tests.append(("java", False))
        
        # teste antlr
        antlr_jar = self.project_root / "dsl" / "antlr-4.13.1-complete.jar"
        tests.append(("antlr", antlr_jar.exists()))
        
        # teste blender
        if self.components['blender']:
            try:
                result = subprocess.run(
                    ["blender", "--version"],
                    capture_output=True,
                    timeout=5
                )
                tests.append(("blender", result.returncode == 0))
            except:
                tests.append(("blender", False))
        
        # teste compilador
        compiler = self.project_root / "dsl" / "compiler" / "bed_compiler_antlr_standalone.py"
        tests.append(("compilador dsl", compiler.exists()))
        
        # teste wizard
        wizard = self.project_root / "dsl" / "bed_wizard.py"
        tests.append(("bed wizard", wizard.exists()))
        
        # teste openfoam setup
        openfoam_setup = self.project_root / "scripts" / "openfoam_scripts" / "setup_openfoam_case.py"
        tests.append(("openfoam setup", openfoam_setup.exists()))
        
        # imprimir resultados
        print()
        all_passed = True
        for test_name, passed in tests:
            status = "[ok]" if passed else "[falhou]"
            print(f"{status:10} {test_name}")
            if not passed:
                all_passed = False
        
        return all_passed
    
    def print_summary(self):
        """imprime resumo da instalacao"""
        print("\n" + "="*70)
        print("  RESUMO DA CONFIGURACAO")
        print("="*70)
        
        print("\ncomponentes instalados:")
        for component, status in self.components.items():
            status_str = "[ok]" if status else "[nao instalado]"
            print(f"  {status_str:15} {component}")
        
        print("\nproximos passos:")
        print("1. testar wizard:")
        print("   python dsl/bed_wizard.py")
        print()
        print("2. criar um leito:")
        print("   - escolher modo interativo ou blender")
        print("   - definir parametros")
        print("   - gerar modelo 3d")
        print()
        print("3. executar simulacao cfd (requer openfoam):")
        print("   python scripts/openfoam_scripts/setup_openfoam_case.py \\")
        print("     generated/configs/leito.bed.json \\")
        print("     generated/3d/output/leito.blend \\")
        print("     --output-dir generated/cfd")
        print()
        print("4. documentacao:")
        print("   - docs/UML_COMPLETO.md - diagramas do projeto")
        print("   - docs/OPENFOAM_WINDOWS_GUIA.md - guia openfoam")
        print("   - dsl/documentacao.html - documentacao web")
        print()
    
    def setup(self, skip_openfoam=False):
        """executa configuracao completa"""
        self.print_header()
        
        # verificar python
        if not self.check_python():
            print("\n[erro critico] python invalido")
            return False
        
        # configurar java + antlr
        print("\n" + "="*70)
        if not self.setup_java_antlr():
            print("\n[aviso] java/antlr nao configurados")
            print("  compilador dsl pode nao funcionar")
        
        # configurar blender
        print("\n" + "="*70)
        if not self.setup_blender():
            print("\n[aviso] blender nao configurado")
            print("  geracao de modelos 3d nao funcionara")
        
        # configurar wsl + openfoam
        if not skip_openfoam:
            print("\n" + "="*70)
            if not self.setup_wsl_openfoam():
                print("\n[aviso] openfoam nao configurado")
                print("  simulacoes cfd nao funcionarao")
        
        # criar diretorios
        print("\n" + "="*70)
        self.create_directories()
        
        # criar config
        print("\n" + "="*70)
        self.create_config_file()
        
        # executar testes
        self.run_tests()
        
        # resumo
        self.print_summary()
        
        print("\n[sucesso] configuracao completa finalizada!")
        return True

def main():
    """funcao principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='configuracao completa do projeto bedflow-atlas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
exemplos:
  python setup_complete.py                    # configuracao completa
  python setup_complete.py --skip-openfoam    # pular openfoam
  python setup_complete.py --help             # mostrar ajuda
        """
    )
    
    parser.add_argument('--skip-openfoam', action='store_true',
                       help='pular instalacao do openfoam')
    
    args = parser.parse_args()
    
    # criar setup
    setup = CompleteSetup()
    
    # executar
    try:
        success = setup.setup(skip_openfoam=args.skip_openfoam)
        
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n[cancelado] configuracao interrompida pelo usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n[erro] erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

