# este arquivo verifica se uma lista de centros de esferas obedece as regras geometricas
# regra 1 cada centro precisa cair dentro do anel e entre as tampas com folga
# regra 2 cada par de esferas precisa estar longe o suficiente para nao penetrar

from __future__ import annotations

import math
from typing import List, Tuple, Dict, Any, Optional

from .geometry_math import (
    AnnulusBedDomain,
    euclidean_distance,
    sphere_center_clearance,
    point_in_domain,
)


def validate_position(
    p: Tuple[float, float, float],
    domain: AnnulusBedDomain,
) -> Tuple[bool, Optional[str]]:
    # testa um unico centro p contra o dominio
    # devolve uma tupla onde o primeiro item e true se ok
    # o segundo item e None se ok ou uma string curta explicando o problema
    if not point_in_domain(p, domain):
        x, y, z = p
        rho = math.hypot(x, y)
        rho_min, rho_max = domain.radial_bounds()
        z_min, z_max = domain.z_bounds()
        # se os limites estao invertidos o proprio dominio e impossivel
        if rho_min > rho_max or z_min > z_max:
            return False, "dominio_vazio_parametros"
        if rho < rho_min:
            return False, "abaixo_rho_min"
        # centro longe demais do eixo: esfera invadiria a parede em r_int
        if rho > rho_max:
            return False, "muito_perto_da_parede_do_leito"
        # z baixo demais bate na tampa inferior por dentro
        if z < z_min:
            return False, "abaixo_tampa_inferior"
        # z alto demais bate na tampa superior por dentro
        if z > z_max:
            return False, "acima_tampa_superior"
        return False, "fora_dominio"
    return True, None


def check_collision_pair(
    p1: Tuple[float, float, float],
    r1: float,
    p2: Tuple[float, float, float],
    r2: float,
    gap: float,
) -> bool:
    # devolve true se o par esta em colisao ou viola a folga gap
    # p1 e p2 sao centros
    # r1 e r2 sao raios
    # calculamos a distancia minima exigida entre centros
    need = sphere_center_clearance(r1, r2, gap)
    # se a distancia real for menor que need entao retornamos true para colisao
    return euclidean_distance(p1, p2) < need


def validate_configuration(
    centers: List[Tuple[float, float, float]],
    radii: List[float],
    domain: AnnulusBedDomain,
    gap: float,
) -> Dict[str, Any]:
    # percorre toda a lista de esferas e monta um relatorio
    # centers lista de posicoes
    # radii um raio por posicao para permitir futuro polidisperso
    # domain limites do leito
    # gap folga entre superficies
    report: Dict[str, Any] = {
        "ok": True,
        "n_spheres": len(centers),
        "pair_violations": 0,
        "domain_violations": 0,
        "messages": [],
    }
    n = len(centers)
    # se o tamanho de radii nao bater nao da para validar pares com sentido
    if len(radii) != n:
        report["ok"] = False
        report["messages"].append("radii_len_difere_de_centers")
        return report

    # fase 1 checar cada centro contra paredes e tampas
    for i, p in enumerate(centers):
        ok, why = validate_position(p, domain)
        if not ok:
            report["ok"] = False
            report["domain_violations"] += 1
            report["messages"].append(f"dominio i={i} {why}")

    # fase 2 checar todos os pares i j com j maior que i
    # complexidade o de n ao quadrado aceitavel para n modesto de tcc
    for i in range(n):
        for j in range(i + 1, n):
            if check_collision_pair(centers[i], radii[i], centers[j], radii[j], gap):
                report["ok"] = False
                report["pair_violations"] += 1
                d = euclidean_distance(centers[i], centers[j])
                need = sphere_center_clearance(radii[i], radii[j], gap)
                report["messages"].append(
                    f"colisao par ({i},{j}) d={d:.6e} need>={need:.6e}"
                )

    return report
