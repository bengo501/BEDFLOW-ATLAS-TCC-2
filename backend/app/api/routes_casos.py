# inspeciona pastas generated cfd e apaga caso no disco
# endpoints pensados para manutencao manual quando openfoam gera muitas pastas
from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List, Dict, Optional
import os
from datetime import datetime

from bedflow_local_paths import iter_search_roots_for_simulations, resolve_simulation_case_dir, simulations_dir

router = APIRouter()


@router.get("/casos/list")
async def listar_casos():
    """
    listar casos cfd em local_data/simulations e pasta legada generated/cfd
    """
    try:
        roots = iter_search_roots_for_simulations()
        if not roots:
            return {
                "casos": [],
                "count": 0,
                "message": "diretório cfd não existe ainda",
            }
        casos = []
        seen = set()
        for cfd_dir in roots:
            if not cfd_dir.exists():
                continue
            for item in cfd_dir.iterdir():
                if not item.is_dir():
                    continue
                key = item.name
                if key in seen:
                    continue
                seen.add(key)
                caso_info = analisar_caso(item)
                if caso_info:
                    casos.append(caso_info)
        
        # ordenar por data (mais recente primeiro)
        casos.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            "casos": casos,
            "count": len(casos),
            "directory": str(simulations_dir()),
            "legacy_directories": [str(p) for p in roots],
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao listar casos: {str(e)}")


def analisar_caso(caso_dir: Path) -> Optional[Dict]:
    """
    analisar um caso cfd e extrair informações
    """
    try:
        info = {
            "nome": caso_dir.name,
            "caminho": str(caso_dir),
            "caminho_relativo": str(caso_dir.relative_to(Path(__file__).parent.parent.parent.parent)),
            "created_at": datetime.fromtimestamp(caso_dir.stat().st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(caso_dir.stat().st_mtime).isoformat(),
            "tamanho_mb": calcular_tamanho_diretorio(caso_dir),
            "status": determinar_status_caso(caso_dir),
            "pastas_tempo": contar_pastas_tempo(caso_dir),
            "tem_allrun": (caso_dir / "Allrun").exists(),
            "tem_stl": (caso_dir / "constant" / "triSurface" / "leito.stl").exists(),
            "tem_malha": (caso_dir / "constant" / "polyMesh" / "points").exists(),
            "logs": listar_logs(caso_dir)
        }
        
        return info
        
    except Exception as e:
        print(f"erro ao analisar caso {caso_dir.name}: {e}")
        return None


def determinar_status_caso(caso_dir: Path) -> str:
    """
    determinar status de um caso baseado nos arquivos presentes
    """
    # verificar se tem resultados (pastas numeradas > 0)
    pastas_tempo = contar_pastas_tempo(caso_dir)
    
    if pastas_tempo > 0:
        # verificar se simulação completou
        log_simplefoam = caso_dir / "log.simpleFoam"
        if log_simplefoam.exists():
            with open(log_simplefoam, 'r') as f:
                content = f.read()
                if 'End' in content or 'Finalising' in content:
                    return 'completed'
                else:
                    return 'running'
        return 'completed'
    
    # verificar se tem malha
    if (caso_dir / "constant" / "polyMesh" / "points").exists():
        return 'meshed'
    
    # apenas configurado
    if (caso_dir / "system" / "controlDict").exists():
        return 'configured'
    
    return 'unknown'


def contar_pastas_tempo(caso_dir: Path) -> int:
    """
    contar quantas pastas de tempo existem (resultados)
    """
    count = 0
    for item in caso_dir.iterdir():
        if item.is_dir() and item.name.isdigit() and item.name != '0':
            count += 1
    return count


def calcular_tamanho_diretorio(diretorio: Path) -> float:
    """
    calcular tamanho total do diretório em mb
    """
    total = 0
    try:
        for item in diretorio.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
    except:
        pass
    return round(total / (1024 * 1024), 2)


def listar_logs(caso_dir: Path) -> List[str]:
    """
    listar todos os arquivos de log presentes
    """
    logs = []
    log_files = ['log.blockMesh', 'log.snappyHexMesh', 'log.checkMesh', 'log.simpleFoam']
    
    for log_file in log_files:
        if (caso_dir / log_file).exists():
            logs.append(log_file)
    
    return logs


@router.get("/casos/{nome_caso}/detalhes")
async def obter_detalhes_caso(nome_caso: str):
    """
    obter detalhes completos de um caso específico
    """
    try:
        caso_dir = resolve_simulation_case_dir(nome_caso)
        if caso_dir is None:
            raise HTTPException(status_code=404, detail="caso não encontrado")
        
        # informações básicas
        info = analisar_caso(caso_dir)
        
        # ler parâmetros do controlDict
        control_dict = caso_dir / "system" / "controlDict"
        if control_dict.exists():
            info["configuracao"] = ler_control_dict(control_dict)
        
        # listar todos os tempos disponíveis
        tempos = []
        for item in sorted(caso_dir.iterdir()):
            if item.is_dir() and item.name.replace('.', '').isdigit():
                tempos.append(item.name)
        info["tempos_disponiveis"] = tempos
        
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro: {str(e)}")


def ler_control_dict(control_dict_path: Path) -> Dict:
    """
    ler informações básicas do controlDict
    """
    try:
        with open(control_dict_path, 'r') as f:
            content = f.read()
        
        # extrair valores principais (parsing simples)
        info = {}
        
        for line in content.split('\n'):
            if 'startTime' in line and not line.strip().startswith('//'):
                info['startTime'] = line.split()[-1].rstrip(';')
            elif 'endTime' in line and not line.strip().startswith('//'):
                info['endTime'] = line.split()[-1].rstrip(';')
            elif 'deltaT' in line and not line.strip().startswith('//'):
                info['deltaT'] = line.split()[-1].rstrip(';')
            elif 'writeInterval' in line and not line.strip().startswith('//'):
                info['writeInterval'] = line.split()[-1].rstrip(';')
        
        return info
        
    except Exception as e:
        return {"error": str(e)}


@router.delete("/casos/{nome_caso}")
async def deletar_caso(nome_caso: str):
    """
    deletar um caso cfd (cuidado! operação irreversível)
    """
    try:
        caso_dir = resolve_simulation_case_dir(nome_caso)
        if caso_dir is None:
            raise HTTPException(status_code=404, detail="caso não encontrado")
        
        # remover diretório recursivamente
        import shutil
        shutil.rmtree(caso_dir)
        
        return {
            "success": True,
            "message": f"caso {nome_caso} deletado"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao deletar: {str(e)}")


@router.post("/casos/{nome_caso}/executar")
async def executar_caso_existente(nome_caso: str):
    """
    executar um caso cfd que já foi configurado mas não executado
    """
    try:
        caso_dir = resolve_simulation_case_dir(nome_caso)
        if caso_dir is None:
            raise HTTPException(status_code=404, detail="caso não encontrado")
        
        # verificar se Allrun existe
        allrun = caso_dir / "Allrun"
        if not allrun.exists():
            raise HTTPException(status_code=400, detail="script Allrun não encontrado")
        
        # criar simulação via endpoint cfd
        # (reutilizar lógica existente)
        
        return {
            "success": True,
            "message": f"simulação do caso {nome_caso} iniciada",
            "instructions": f"execute no wsl: cd {caso_dir} && ./Allrun"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro: {str(e)}")

