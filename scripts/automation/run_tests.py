#!/usr/bin/env python3
# script de testes automatizados completos do projeto
import os
import sys
import subprocess
import platform
from pathlib import Path
import json
import time

class AutomatedTests:
    """classe para executar testes automatizados de todo o pipeline"""
    
    def __init__(self):
        self.system = platform.system()
        self.project_root = Path(__file__).parent.parent.parent
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': [],
            'skipped': []
        }
        
    def print_header(self, title):
        """imprime cabecalho formatado"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def test_python_imports(self):
        """testa se todas as dependencias python estao disponiveis"""
        self.print_header("teste 1: importacoes python")
        
        required_modules = [
            ('pathlib', 'pathlib'),
            ('json', 'json'),
            ('subprocess', 'subprocess'),
            ('argparse', 'argparse'),
            ('urllib.request', 'urllib'),
        ]
        
        all_ok = True
        for module_name, import_name in required_modules:
            try:
                __import__(import_name)
                print(f"[ok] {module_name}")
                self.results['passed'].append(f"python: {module_name}")
            except ImportError as e:
                print(f"[erro] {module_name}: {e}")
                self.results['failed'].append(f"python: {module_name}")
                all_ok = False
        
        return all_ok
    
    def test_java_installation(self):
        """testa instalacao do java"""
        self.print_header("teste 2: java")
        
        # tentar caminhos comuns
        java_paths = ["java"]
        
        if self.system == "Windows":
            java_paths.extend([
                r"C:\Program Files\Microsoft\jdk-17.0.16.8-hotspot\bin\java.exe",
                r"C:\Program Files\Java\jdk-17\bin\java.exe",
            ])
        
        java_found = False
        for java_path in java_paths:
            try:
                result = subprocess.run(
                    [java_path, "-version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    version = result.stderr.split('\n')[0]
                    print(f"[ok] java encontrado: {version}")
                    self.results['passed'].append("java instalado")
                    java_found = True
                    break
                    
            except (FileNotFoundError, Exception):
                continue
        
        if not java_found:
            print("[erro] java nao encontrado")
            self.results['failed'].append("java nao instalado")
            return False
        
        return True
    
    def test_antlr_jar(self):
        """testa se antlr jar existe"""
        self.print_header("teste 3: antlr jar")
        
        antlr_jar = self.project_root / "dsl" / "antlr-4.13.1-complete.jar"
        
        if antlr_jar.exists():
            size_mb = antlr_jar.stat().st_size / (1024 * 1024)
            print(f"[ok] antlr jar encontrado: {size_mb:.2f} mb")
            self.results['passed'].append("antlr jar existe")
            return True
        else:
            print(f"[erro] antlr jar nao encontrado: {antlr_jar}")
            self.results['failed'].append("antlr jar ausente")
            return False
    
    def test_antlr_generated_files(self):
        """testa se arquivos do parser foram gerados"""
        self.print_header("teste 4: parser antlr gerado")
        
        generated_dir = self.project_root / "dsl" / "generated"
        required_files = [
            "BedLexer.py",
            "BedParser.py",
            "BedListener.py"
        ]
        
        all_ok = True
        for filename in required_files:
            filepath = generated_dir / filename
            if filepath.exists():
                print(f"[ok] {filename}")
                self.results['passed'].append(f"parser: {filename}")
            else:
                print(f"[erro] {filename} nao encontrado")
                self.results['failed'].append(f"parser: {filename}")
                all_ok = False
        
        return all_ok
    
    def test_dsl_compiler(self):
        """testa compilador dsl"""
        self.print_header("teste 5: compilador dsl")
        
        compiler = self.project_root / "dsl" / "compiler" / "bed_compiler_antlr_standalone.py"
        
        if not compiler.exists():
            print(f"[erro] compilador nao encontrado: {compiler}")
            self.results['failed'].append("compilador ausente")
            return False
        
        # criar arquivo .bed de teste
        test_bed = self.project_root / "temp" / "test.bed"
        test_bed.parent.mkdir(parents=True, exist_ok=True)
        
        test_content = """bed {
    diameter = 5cm
    height = 10cm
    wall_thickness = 2mm
}

particles {
    count = 10
    diameter = 5mm
}

packing {
    method = "rigid_body"
}

export {
    formats = ["blend"]
}

cfd {
    regime = "laminar"
}
"""
        
        with open(test_bed, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # tentar compilar
        try:
            result = subprocess.run(
                [sys.executable, str(compiler), str(test_bed)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # verificar se json foi gerado
            test_json = test_bed.with_suffix('.bed.json')
            
            if test_json.exists():
                with open(test_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"[ok] compilador funcionando")
                print(f"  json gerado: {test_json.name}")
                print(f"  parametros: {len(data)} secoes")
                self.results['passed'].append("compilador dsl funcional")
                
                # limpar arquivos de teste
                test_bed.unlink()
                test_json.unlink()
                
                return True
            else:
                print("[erro] json nao foi gerado")
                print(result.stderr)
                self.results['failed'].append("compilador nao gera json")
                return False
                
        except Exception as e:
            print(f"[erro] falha ao executar compilador: {e}")
            self.results['failed'].append("compilador com erro")
            return False
    
    def test_blender_installation(self):
        """testa instalacao do blender"""
        self.print_header("teste 6: blender")
        
        try:
            result = subprocess.run(
                ["blender", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                print(f"[ok] {version}")
                self.results['passed'].append("blender instalado")
                return True
            else:
                print("[erro] blender retornou erro")
                self.results['failed'].append("blender com erro")
                return False
                
        except FileNotFoundError:
            print("[aviso] blender nao encontrado no path")
            self.results['warnings'].append("blender nao no path")
            return False
        except Exception as e:
            print(f"[erro] falha ao verificar blender: {e}")
            self.results['failed'].append("blender erro verificacao")
            return False
    
    def test_blender_script(self):
        """testa script de geracao 3d do blender"""
        self.print_header("teste 7: script blender")
        
        script = self.project_root / "scripts" / "blender_scripts" / "leito_extracao.py"
        
        if not script.exists():
            print(f"[erro] script nao encontrado: {script}")
            self.results['failed'].append("script blender ausente")
            return False
        
        # verificar sintaxe python
        try:
            with open(script, 'r', encoding='utf-8') as f:
                content = f.read()
            
            compile(content, str(script), 'exec')
            print(f"[ok] sintaxe python valida")
            print(f"  linhas: {len(content.splitlines())}")
            self.results['passed'].append("script blender sintaxe ok")
            return True
            
        except SyntaxError as e:
            print(f"[erro] erro de sintaxe: {e}")
            self.results['failed'].append("script blender sintaxe invalida")
            return False
    
    def test_openfoam_setup_script(self):
        """testa script de configuracao openfoam"""
        self.print_header("teste 8: script openfoam")
        
        script = self.project_root / "scripts" / "openfoam_scripts" / "setup_openfoam_case.py"
        
        if not script.exists():
            print(f"[erro] script nao encontrado: {script}")
            self.results['failed'].append("script openfoam ausente")
            return False
        
        # testar help
        try:
            result = subprocess.run(
                [sys.executable, str(script), "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "usage:" in result.stdout.lower():
                print(f"[ok] script openfoam funcional")
                self.results['passed'].append("script openfoam ok")
                return True
            else:
                print("[erro] script com problemas")
                self.results['failed'].append("script openfoam erro")
                return False
                
        except Exception as e:
            print(f"[erro] falha ao testar script: {e}")
            self.results['failed'].append("script openfoam falha teste")
            return False
    
    def test_wsl_installation(self):
        """testa instalacao do wsl (windows apenas)"""
        self.print_header("teste 9: wsl2 (windows)")
        
        if self.system != "Windows":
            print("[skip] teste apenas para windows")
            self.results['skipped'].append("wsl teste (nao windows)")
            return True
        
        try:
            result = subprocess.run(
                ["wsl", "--status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("[ok] wsl2 instalado")
                self.results['passed'].append("wsl2 instalado")
                return True
            else:
                print("[aviso] wsl2 nao encontrado")
                self.results['warnings'].append("wsl2 ausente")
                return False
                
        except FileNotFoundError:
            print("[aviso] comando wsl nao encontrado")
            self.results['warnings'].append("wsl comando ausente")
            return False
        except Exception as e:
            print(f"[erro] falha ao verificar wsl: {e}")
            self.results['warnings'].append("wsl erro verificacao")
            return False
    
    def test_openfoam_commands(self):
        """testa comandos openfoam no wsl"""
        self.print_header("teste 10: comandos openfoam")
        
        if self.system != "Windows":
            print("[skip] teste apenas para windows com wsl")
            self.results['skipped'].append("openfoam comandos (nao windows)")
            return True
        
        commands = [
            "which blockMesh",
            "which simpleFoam",
            "which snappyHexMesh"
        ]
        
        all_ok = True
        for cmd in commands:
            try:
                full_cmd = f"source /opt/openfoam11/etc/bashrc && {cmd}"
                result = subprocess.run(
                    ["wsl", "-e", "bash", "-c", full_cmd],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    print(f"[ok] {cmd.split()[-1]} encontrado")
                    self.results['passed'].append(f"openfoam: {cmd.split()[-1]}")
                else:
                    print(f"[aviso] {cmd.split()[-1]} nao encontrado")
                    self.results['warnings'].append(f"openfoam: {cmd.split()[-1]}")
                    all_ok = False
                    
            except Exception as e:
                print(f"[aviso] erro ao testar {cmd}: {e}")
                self.results['warnings'].append(f"openfoam: {cmd.split()[-1]} erro")
                all_ok = False
        
        return all_ok
    
    def test_project_structure(self):
        """testa estrutura de diretorios do projeto"""
        self.print_header("teste 11: estrutura do projeto")
        
        required_dirs = [
            "dsl",
            "dsl/grammar",
            "dsl/compiler",
            "scripts",
            "scripts/automation",
            "scripts/blender_scripts",
            "scripts/openfoam_scripts",
            "docs",
            "generated",
            "generated/3d",
            "generated/3d/blender",
            "generated/3d/exports",
            "generated/3d/output",
            "generated/cfd",
            "generated/configs"
        ]
        
        all_ok = True
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                print(f"[ok] {dir_path}/")
                self.results['passed'].append(f"estrutura: {dir_path}")
            else:
                print(f"[aviso] {dir_path}/ nao existe")
                self.results['warnings'].append(f"estrutura: {dir_path}")
                all_ok = False
        
        return all_ok
    
    def test_documentation(self):
        """testa presenca de documentacao"""
        self.print_header("teste 12: documentacao")
        
        required_docs = [
            "README.md",
            "docs/README.md",
            "docs/UML_COMPLETO.md",
            "docs/OPENFOAM_WINDOWS_GUIA.md",
            "scripts/automation/README.md",
            "dsl/documentacao.html"
        ]
        
        all_ok = True
        for doc_path in required_docs:
            full_path = self.project_root / doc_path
            if full_path.exists():
                size_kb = full_path.stat().st_size / 1024
                print(f"[ok] {doc_path} ({size_kb:.1f} kb)")
                self.results['passed'].append(f"docs: {doc_path}")
            else:
                print(f"[aviso] {doc_path} nao encontrado")
                self.results['warnings'].append(f"docs: {doc_path}")
                all_ok = False
        
        return all_ok
    
    def generate_report(self):
        """gera relatorio final dos testes"""
        self.print_header("relatorio final")
        
        total = (len(self.results['passed']) + 
                len(self.results['failed']) + 
                len(self.results['warnings']) + 
                len(self.results['skipped']))
        
        print(f"\ntotal de testes: {total}")
        print(f"[ok] passou: {len(self.results['passed'])}")
        print(f"[erro] falhou: {len(self.results['failed'])}")
        print(f"[aviso] avisos: {len(self.results['warnings'])}")
        print(f"[skip] pulados: {len(self.results['skipped'])}")
        
        if self.results['failed']:
            print("\ntestes que falharam:")
            for item in self.results['failed']:
                print(f"  - {item}")
        
        if self.results['warnings']:
            print("\navisos:")
            for item in self.results['warnings']:
                print(f"  - {item}")
        
        # calcular score
        if total > 0:
            score = (len(self.results['passed']) / (total - len(self.results['skipped']))) * 100
            print(f"\nscore: {score:.1f}%")
            
            if score >= 90:
                print("status: [excelente] projeto totalmente funcional")
            elif score >= 70:
                print("status: [bom] projeto funcional com avisos")
            elif score >= 50:
                print("status: [regular] projeto parcialmente funcional")
            else:
                print("status: [critico] projeto com problemas serios")
        
        # salvar relatorio em json
        report_file = self.project_root / "test_report.json"
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'system': self.system,
            'total_tests': total,
            'results': self.results,
            'score': score if total > 0 else 0
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nrelatorio salvo em: {report_file}")
    
    def run_all_tests(self):
        """executa todos os testes"""
        print("="*70)
        print("  TESTES AUTOMATIZADOS - BEDFLOW-ATLAS")
        print("="*70)
        print(f"sistema: {self.system}")
        print(f"projeto: {self.project_root}")
        
        # executar testes
        self.test_python_imports()
        self.test_java_installation()
        self.test_antlr_jar()
        self.test_antlr_generated_files()
        self.test_dsl_compiler()
        self.test_blender_installation()
        self.test_blender_script()
        self.test_openfoam_setup_script()
        self.test_wsl_installation()
        self.test_openfoam_commands()
        self.test_project_structure()
        self.test_documentation()
        
        # gerar relatorio
        self.generate_report()
        
        # retornar se teve falhas criticas
        return len(self.results['failed']) == 0

def main():
    """funcao principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='testes automatizados do projeto')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='saida detalhada')
    
    args = parser.parse_args()
    
    # executar testes
    tests = AutomatedTests()
    success = tests.run_all_tests()
    
    if success:
        print("\n[sucesso] todos os testes passaram!")
        sys.exit(0)
    else:
        print("\n[falha] alguns testes falharam")
        sys.exit(1)

if __name__ == "__main__":
    main()

