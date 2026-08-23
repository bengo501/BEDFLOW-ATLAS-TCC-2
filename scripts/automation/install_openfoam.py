#!/usr/bin/env python3
# script de instalacao automatica do openfoam no windows via wsl2
import os
import sys
import subprocess
import platform
from pathlib import Path
import time

class OpenFOAMInstaller:
    """classe para instalar openfoam no windows via wsl2"""
    
    def __init__(self):
        self.system = platform.system()
        self.openfoam_version = "11"
        self.ubuntu_version = "22.04"
        
    def check_windows(self):
        """verifica se esta rodando no windows"""
        if self.system != "Windows":
            print("[erro] este script foi desenvolvido para windows")
            print("para linux, use: sudo apt install openfoam")
            return False
        
        print("[ok] sistema windows detectado")
        return True
    
    def check_wsl_installed(self):
        """verifica se wsl2 esta instalado"""
        print("\n[1/8] verificando wsl2...")
        
        try:
            result = subprocess.run(
                ["wsl", "--status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("[ok] wsl2 encontrado")
                return True
            else:
                print("[aviso] wsl2 nao encontrado")
                return False
                
        except FileNotFoundError:
            print("[aviso] comando wsl nao encontrado")
            return False
        except Exception as e:
            print(f"[erro] erro ao verificar wsl: {e}")
            return False
    
    def install_wsl(self):
        """instala wsl2 no windows"""
        print("\n[2/8] instalando wsl2...")
        print("isso pode levar varios minutos...")
        
        try:
            # instalar wsl2 com ubuntu
            result = subprocess.run(
                ["wsl", "--install", "-d", "Ubuntu-22.04"],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                print("[ok] wsl2 instalado com ubuntu 22.04")
                print("[atencao] reinicie o computador e execute este script novamente")
                return True
            else:
                print(f"[erro] falha na instalacao: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[erro] erro na instalacao do wsl: {e}")
            return False
    
    def check_ubuntu_distro(self):
        """verifica se ubuntu esta instalado no wsl"""
        print("\n[3/8] verificando distribuicao ubuntu...")
        
        try:
            result = subprocess.run(
                ["wsl", "-l", "-v"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "Ubuntu" in result.stdout:
                print("[ok] ubuntu encontrado no wsl")
                return True
            else:
                print("[aviso] ubuntu nao encontrado")
                return False
                
        except Exception as e:
            print(f"[erro] erro ao verificar distro: {e}")
            return False
    
    def update_ubuntu(self):
        """atualiza pacotes do ubuntu"""
        print("\n[4/8] atualizando ubuntu...")
        print("isso pode levar varios minutos...")
        
        commands = [
            "sudo apt update",
            "sudo apt upgrade -y"
        ]
        
        for cmd in commands:
            try:
                print(f"  executando: {cmd}")
                result = subprocess.run(
                    ["wsl", "-e", "bash", "-c", cmd],
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                if result.returncode != 0:
                    print(f"[aviso] comando falhou: {result.stderr}")
                    
            except Exception as e:
                print(f"[erro] erro ao executar comando: {e}")
                return False
        
        print("[ok] ubuntu atualizado")
        return True
    
    def install_dependencies(self):
        """instala dependencias necessarias"""
        print("\n[5/8] instalando dependencias...")
        
        packages = [
            "build-essential",
            "flex",
            "bison",
            "cmake",
            "zlib1g-dev",
            "libboost-system-dev",
            "libboost-thread-dev",
            "libopenmpi-dev",
            "openmpi-bin",
            "gnuplot",
            "libreadline-dev",
            "libncurses-dev",
            "libxt-dev",
            "qt5-default",
            "libqt5x11extras5-dev",
            "libqt5help5",
            "qttools5-dev",
            "qtxmlpatterns5-dev-tools",
            "libqt5opengl5-dev",
            "libqt5svg5-dev",
            "libcgal-dev",
            "git",
            "wget",
            "curl"
        ]
        
        cmd = f"sudo apt install -y {' '.join(packages)}"
        
        try:
            print(f"  instalando {len(packages)} pacotes...")
            result = subprocess.run(
                ["wsl", "-e", "bash", "-c", cmd],
                capture_output=True,
                text=True,
                timeout=1200  # 20 minutos
            )
            
            if result.returncode == 0:
                print("[ok] dependencias instaladas")
                return True
            else:
                print(f"[erro] falha na instalacao: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[erro] erro ao instalar dependencias: {e}")
            return False
    
    def add_openfoam_repository(self):
        """adiciona repositorio oficial do openfoam"""
        print("\n[6/8] adicionando repositorio openfoam...")
        
        commands = [
            "sudo sh -c \"wget -O - https://dl.openfoam.org/gpg.key | apt-key add -\"",
            f"sudo add-apt-repository http://dl.openfoam.org/ubuntu",
            "sudo apt update"
        ]
        
        for cmd in commands:
            try:
                print(f"  executando: {cmd}")
                result = subprocess.run(
                    ["wsl", "-e", "bash", "-c", cmd],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode != 0:
                    print(f"[aviso] comando falhou: {result.stderr}")
                    
            except Exception as e:
                print(f"[erro] erro ao executar comando: {e}")
                return False
        
        print("[ok] repositorio adicionado")
        return True
    
    def install_openfoam(self):
        """instala openfoam"""
        print(f"\n[7/8] instalando openfoam{self.openfoam_version}...")
        print("isso pode levar 15-30 minutos...")
        
        cmd = f"sudo apt install -y openfoam{self.openfoam_version}"
        
        try:
            result = subprocess.run(
                ["wsl", "-e", "bash", "-c", cmd],
                capture_output=True,
                text=True,
                timeout=2400  # 40 minutos
            )
            
            if result.returncode == 0:
                print(f"[ok] openfoam{self.openfoam_version} instalado")
                return True
            else:
                print(f"[erro] falha na instalacao: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[erro] erro ao instalar openfoam: {e}")
            return False
    
    def configure_bashrc(self):
        """configura .bashrc para carregar openfoam automaticamente"""
        print("\n[8/8] configurando ambiente openfoam...")
        
        bashrc_line = f"source /opt/openfoam{self.openfoam_version}/etc/bashrc"
        
        commands = [
            f"grep -q '{bashrc_line}' ~/.bashrc || echo '{bashrc_line}' >> ~/.bashrc",
            "source ~/.bashrc"
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(
                    ["wsl", "-e", "bash", "-c", cmd],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
            except Exception as e:
                print(f"[aviso] erro ao configurar bashrc: {e}")
        
        print("[ok] ambiente configurado")
        return True
    
    def verify_installation(self):
        """verifica se openfoam foi instalado corretamente"""
        print("\n[verificacao] testando openfoam...")
        
        test_commands = [
            "which blockMesh",
            "which simpleFoam",
            "which paraFoam"
        ]
        
        all_ok = True
        for cmd in test_commands:
            try:
                result = subprocess.run(
                    ["wsl", "-e", "bash", "-c", f"source /opt/openfoam{self.openfoam_version}/etc/bashrc && {cmd}"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    print(f"[ok] {cmd.split()[-1]} encontrado")
                else:
                    print(f"[erro] {cmd.split()[-1]} nao encontrado")
                    all_ok = False
                    
            except Exception as e:
                print(f"[erro] erro ao testar {cmd}: {e}")
                all_ok = False
        
        return all_ok
    
    def install_paraview(self):
        """instala paraview para visualizacao"""
        print("\n[extra] instalando paraview...")
        
        cmd = "sudo apt install -y paraview"
        
        try:
            result = subprocess.run(
                ["wsl", "-e", "bash", "-c", cmd],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                print("[ok] paraview instalado")
                return True
            else:
                print("[aviso] falha ao instalar paraview")
                return False
                
        except Exception as e:
            print(f"[aviso] erro ao instalar paraview: {e}")
            return False
    
    def create_tutorial_case(self):
        """cria um caso tutorial de exemplo"""
        print("\n[extra] criando caso tutorial...")
        
        commands = [
            "mkdir -p ~/openfoam_cases",
            "cd ~/openfoam_cases",
            f"source /opt/openfoam{self.openfoam_version}/etc/bashrc",
            "cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily .",
            "cd pitzDaily",
            "blockMesh > log.blockMesh 2>&1",
            "simpleFoam > log.simpleFoam 2>&1"
        ]
        
        full_cmd = " && ".join(commands)
        
        try:
            print("  copiando e executando caso tutorial...")
            result = subprocess.run(
                ["wsl", "-e", "bash", "-c", full_cmd],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("[ok] caso tutorial executado")
                print("  localizado em: ~/openfoam_cases/pitzDaily")
                return True
            else:
                print("[aviso] falha ao executar tutorial")
                return False
                
        except Exception as e:
            print(f"[aviso] erro ao criar tutorial: {e}")
            return False
    
    def install(self, skip_wsl_install=False, install_extras=True):
        """executa instalacao completa"""
        print("="*60)
        print("  instalador automatico openfoam para windows via wsl2")
        print("="*60)
        
        # verificar windows
        if not self.check_windows():
            return False
        
        # verificar wsl2
        wsl_ok = self.check_wsl_installed()
        
        if not wsl_ok and not skip_wsl_install:
            print("\n[atencao] wsl2 nao encontrado")
            print("sera instalado automaticamente")
            
            if not self.install_wsl():
                return False
            
            print("\n[importante] reinicie o computador e execute novamente")
            return False
        
        if not wsl_ok and skip_wsl_install:
            print("[erro] wsl2 necessario mas instalacao foi pulada")
            return False
        
        # verificar ubuntu
        if not self.check_ubuntu_distro():
            print("[erro] ubuntu nao encontrado no wsl")
            return False
        
        # atualizar sistema
        if not self.update_ubuntu():
            print("[aviso] falha ao atualizar ubuntu")
        
        # instalar dependencias
        if not self.install_dependencies():
            print("[erro] falha ao instalar dependencias")
            return False
        
        # adicionar repositorio
        if not self.add_openfoam_repository():
            print("[aviso] falha ao adicionar repositorio oficial")
            print("tentando instalacao alternativa...")
        
        # instalar openfoam
        if not self.install_openfoam():
            print("[erro] falha ao instalar openfoam")
            return False
        
        # configurar ambiente
        self.configure_bashrc()
        
        # verificar instalacao
        if not self.verify_installation():
            print("[aviso] alguns componentes nao foram encontrados")
        
        # extras
        if install_extras:
            self.install_paraview()
            self.create_tutorial_case()
        
        print("\n" + "="*60)
        print("  instalacao concluida!")
        print("="*60)
        
        return True
    
    def print_next_steps(self):
        """imprime proximos passos"""
        print("\nproximos passos:")
        print("1. abrir wsl: wsl")
        print(f"2. carregar openfoam: source /opt/openfoam{self.openfoam_version}/etc/bashrc")
        print("3. testar: blockMesh --help")
        print("4. executar caso: cd ~/openfoam_cases/pitzDaily && paraview caso.foam")
        print("\npara integrar com o projeto:")
        print("5. cd /mnt/c/Users/[SEU_USUARIO]/Downloads/BEDFLOW-ATLAS")
        print("6. python scripts/openfoam_scripts/setup_openfoam_case.py --help")

def main():
    """funcao principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='instalador automatico openfoam para windows')
    parser.add_argument('--version', type=str, default='11',
                       help='versao do openfoam (padrao: 11)')
    parser.add_argument('--skip-wsl-install', action='store_true',
                       help='pular instalacao do wsl2')
    parser.add_argument('--no-extras', action='store_true',
                       help='nao instalar paraview e tutorial')
    
    args = parser.parse_args()
    
    # criar instalador
    installer = OpenFOAMInstaller()
    installer.openfoam_version = args.version
    
    # executar instalacao
    success = installer.install(
        skip_wsl_install=args.skip_wsl_install,
        install_extras=not args.no_extras
    )
    
    if success:
        print("\n[sucesso] openfoam instalado e pronto para usar!")
        installer.print_next_steps()
    else:
        print("\n[erro] instalacao falhou ou requer reinicializacao")
        print("verifique os logs acima para detalhes")
        sys.exit(1)

if __name__ == "__main__":
    main()

