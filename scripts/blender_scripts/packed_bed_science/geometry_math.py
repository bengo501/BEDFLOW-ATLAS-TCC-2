# matematica do espaco onde os centros das esferas podem existir
# tubo de parede fina: a cavidade e o cilindro interior ate a face interna da parede
# r int e o raio interno da cavidade (superficie interna do metal) em metros
# r ext e o raio externo do leito (referencia geometrica; empacotamento usa so a cavidade)
# gap e folga extra entre superficies de duas esferas vizinhas

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple, List


def euclidean_distance(
    a: Tuple[float, float, float], b: Tuple[float, float, float]
) -> float:
    # mede distancia entre dois pontos no espaco tridimensional
    # a e b sao tuplas x y z em metros
    # o resultado e um unico numero em metros
    # subtrai coordenada por coordenada
    # eleva cada diferenca ao quadrado
    # soma os tres quadrados
    # raiz quadrada da soma e a distancia
    # mesmo principio de pitagoras estendido para tres eixos
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def sphere_center_clearance(radius_a: float, radius_b: float, gap: float) -> float:
    # devolve distancia minima permitida entre dois centros de esfera
    # radius a e raio da primeira esfera em metros
    # radius b e raio da segunda esfera em metros
    # gap e folga extra entre as superficies em metros
    # centros mais proximos que esse valor significam colisao ou violacao de folga
    return radius_a + radius_b + gap


@dataclass
class AnnulusBedDomain:
    # agrupa numeros que descrevem o leito e as tampas para testar posicoes
    # r int raio da cavidade (parede interna do tubo) em metros
    # r ext raio externo do corpo do leito em metros
    # height altura total do trecho do cilindro no eixo z em metros
    # bottom cap thickness espessura da tampa de baixo em metros
    # top cap thickness espessura da tampa de cima em metros
    # r sphere raio de cada esfera em metros
    # gap folga minima entre superficies de esferas em metros

    r_int: float
    r_ext: float
    height: float
    bottom_cap_thickness: float
    top_cap_thickness: float
    r_sphere: float
    gap: float

    def radial_bounds(self) -> Tuple[float, float]:
        # distancia do eixo z ao centro no plano xy: 0 <= rho <= rho_max
        # a esfera nao pode ultrapassar a superficie interna em r_int
        rho_min = 0.0
        rho_max = self.r_int - self.r_sphere - self.gap
        return rho_min, rho_max

    def z_bounds(self) -> Tuple[float, float]:
        # devolve z min e z max permitidos para o centro da esfera no eixo vertical
        # as tampas sao discos finos centrados em z zero e z height
        # face interna da tampa de baixo fica aproximadamente em metade da espessura acima do zero
        # face interna da tampa de cima fica aproximadamente em height menos metade da espessura
        # o centro precisa ficar acima da face inferior com folga r sphere mais gap
        # e abaixo da face superior com folga r sphere mais gap
        z_in_bottom = self.bottom_cap_thickness / 2.0
        z_in_top = self.height - self.top_cap_thickness / 2.0
        z_min = z_in_bottom + self.r_sphere + self.gap
        z_max = z_in_top - self.r_sphere - self.gap
        return z_min, z_max

    def bbox_for_sampling(self) -> Tuple[float, float, float, float, float, float]:
        # devolve caixa retangular alinhada aos eixos que cobre o dominio valido
        # usada para sortear pontos aleatorios no modo spherical packing
        # os seis numeros sao xmin xmax ymin ymax zmin zmax
        # em xy usamos quadrado simetrico que contem o anel ate rho max
        rho_min, rho_max = self.radial_bounds()
        z_min, z_max = self.z_bounds()
        # parametros fisicos impossiveis deixam dominio vazio
        if rho_min > rho_max or z_min > z_max:
            return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        return (-rho_max, rho_max, -rho_max, rho_max, z_min, z_max)

    def annulus_volume_void(self) -> float:
        # volume do cilindro interior util entre as faces internas das tampas
        # (volume da cavidade onde fluido e particulas se encontram)
        z_in_bottom = self.bottom_cap_thickness / 2.0
        z_in_top = self.height - self.top_cap_thickness / 2.0
        h = max(0.0, z_in_top - z_in_bottom)
        return math.pi * (self.r_int**2) * h


def point_in_domain(p: Tuple[float, float, float], domain: AnnulusBedDomain) -> bool:
    # true se p pode ser centro de esfera sem furar parede nem tampa
    # p e tupla x y z em metros
    # domain traz raios espessuras r sphere e gap via radial bounds e z bounds
    x, y, z = p
    # rho mede quanto o centro se afasta do eixo z no plano horizontal
    rho = math.hypot(x, y)
    # limites radiais derivados da geometria do anel e do raio da esfera
    rho_min, rho_max = domain.radial_bounds()
    # limites verticais derivados das tampas e do raio da esfera
    z_min, z_max = domain.z_bounds()
    # se nao existe faixa valida nenhum ponto passa
    if rho_min > rho_max or z_min > z_max:
        return False
    # exige rho e z dentro dos intervalos fechados
    return rho_min <= rho <= rho_max and z_min <= z <= z_max


def estimate_porosity(
    domain: AnnulusBedDomain, centers: List[Tuple[float, float, float]], r_sphere: float
) -> float:
    # porosidade aproximada um menos volume das esferas sobre volume do vazio
    # assume centros ja validados sem sobreposicao grave
    # serve como indicador rapido no relatorio
    v_void = domain.annulus_volume_void()
    if v_void <= 0:
        return 0.0
    n = len(centers)
    v_s = n * (4.0 / 3.0) * math.pi * r_sphere**3
    return max(0.0, min(1.0, 1.0 - v_s / v_void))


# notas de metodologia em texto simples
# problema colocar n esferas na cavidade cilindrica sem atravessar parede nem vizinho
# condicao de nao colisao distancia entre centros maior ou igual soma dos raios mais gap
# modo spherical sorteia pontos ate encher ou esgotar tentativas
# modo hexagonal usa grade regular depois corta o que cai fora do cilindro
# validacao percorre pares para conferir distancias e checa cada centro no dominio
# limitacao custo quadratico no numero de esferas e raios iguais neste fluxo
