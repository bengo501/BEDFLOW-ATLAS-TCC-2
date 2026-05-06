# ficheiro de utilidades geometricas puras
# nao depende de numpy nem trimesh para manter dependencias minimas
# junta malhas e escreve stl binario com normais por triangulo
from __future__ import annotations

import math
import struct
from pathlib import Path
from typing import List, Tuple

# vec3 representa um ponto ou vetor em tres dimensoes em metros
vec3 = Tuple[float, float, float]
# tri e um triangulo como tres indices inteiros na lista global de vertices
tri = Tuple[int, int, int]


def uv_sphere(
    cx: float,
    cy: float,
    cz: float,
    r: float,
    lat: int = 5,
    lon: int = 8,
) -> Tuple[List[vec3], List[tri]]:
    # funcao uv_sphere
    # devolve vertices e faces que aproximam uma esfera por malha tipo globo
    # cx cy cz centro da esfera
    # r raio
    # lat numero de faixas ao longo do meridiano quanto maior mais suave
    # lon numero de fatias em volta do eixo z quanto maior mais suave
    verts: List[vec3] = []
    faces: List[tri] = []
    # passo um percorre da base ao topo th vai de zero a pi radianos
    for j in range(lat + 1):
        th = math.pi * j / lat
        sin_t = math.sin(th)
        cos_t = math.cos(th)
        # passo dois percorre o azimute ph vai de zero a dois pi
        for i in range(lon):
            ph = 2 * math.pi * i / lon
            # conversao de coordenadas esfericas para cartesianas x y z
            x = cx + r * sin_t * math.cos(ph)
            y = cy + r * sin_t * math.sin(ph)
            z = cz + r * cos_t
            verts.append((x, y, z))
    # para cada quadrilatero da grelha criamos dois triangulos
    # indices a b d e b c d cobrem o quadrilatero sem buracos
    for j in range(lat):
        for i in range(lon):
            a = j * lon + i
            b = j * lon + (i + 1) % lon
            c = (j + 1) * lon + (i + 1) % lon
            d = (j + 1) * lon + i
            faces.append((a, b, d))
            faces.append((b, c, d))
    return verts, faces


def merge_mesh(
    va: List[vec3], fa: List[tri], vb: List[vec3], fb: List[tri]
) -> Tuple[List[vec3], List[tri]]:
    # funcao merge_mesh
    # concatena a malha b depois da malha a
    # va fa vertices e faces da primeira parte
    # vb fb vertices e faces da segunda parte
    # off numero de vertices ja existentes antes de colar b
    off = len(va)
    # somamos listas de vertices
    # somamos faces da segunda malha com indices deslocados por off
    return va + vb, fa + [(a + off, b + off, c + off) for a, b, c in fb]


def cylinder_axis(
    cx: float,
    cy: float,
    cz: float,
    radius: float,
    height: float,
    *,
    axis: str = "y",
    segments: int = 24,
) -> Tuple[List[vec3], List[tri]]:
    # cilindro com tampas, orientado ao longo de x/y/z
    # usado para representar a fatia fina (disco/cilindro achatado) de uma esfera
    if radius <= 0 or height <= 0 or segments < 3:
        return [], []
    a = axis.strip().lower()
    if a not in ("x", "y", "z"):
        a = "y"
    h2 = height / 2.0

    def make_point(ang: float, t: float) -> vec3:
        c = math.cos(ang) * radius
        s = math.sin(ang) * radius
        if a == "y":
            return (cx + c, cy + t, cz + s)
        if a == "x":
            return (cx + t, cy + c, cz + s)
        return (cx + c, cy + s, cz + t)

    verts: List[vec3] = []
    faces: List[tri] = []
    # centros das tampas
    if a == "y":
        cb = (cx, cy - h2, cz)
        ct = (cx, cy + h2, cz)
    elif a == "x":
        cb = (cx - h2, cy, cz)
        ct = (cx + h2, cy, cz)
    else:
        cb = (cx, cy, cz - h2)
        ct = (cx, cy, cz + h2)
    verts.append(cb)  # 0
    verts.append(ct)  # 1

    base_ring = 2
    # aneis inferior e superior
    for i in range(segments):
        ang = 2 * math.pi * i / segments
        verts.append(make_point(ang, -h2))
    for i in range(segments):
        ang = 2 * math.pi * i / segments
        verts.append(make_point(ang, +h2))

    def ni(i: int) -> int:
        return (i + 1) % segments

    rb = lambda i: base_ring + i
    rt = lambda i: base_ring + segments + i
    # disco inferior
    for i in range(segments):
        j = ni(i)
        faces.append((0, rb(i), rb(j)))
    # disco superior
    for i in range(segments):
        j = ni(i)
        faces.append((1, rt(j), rt(i)))
    # lateral
    for i in range(segments):
        j = ni(i)
        faces.append((rb(i), rt(i), rt(j)))
        faces.append((rb(i), rt(j), rb(j)))

    return verts, faces


def filter_faces_by_slab(
    vertices: List[vec3],
    faces: List[tri],
    *,
    axis: str,
    min_v: float,
    max_v: float,
) -> Tuple[List[vec3], List[tri]]:
    # mantem triangulos que intersectam a faixa [min_v, max_v]
    # criterio simples: intervalo dos 3 vertices sobrepoe o intervalo da fatia
    # isto corta a parede e tampas para formar uma fatia fina (sem cap automatico)
    a = axis.strip().lower()
    if a not in ("x", "y", "z"):
        a = "y"
    ai = 0 if a == "x" else (1 if a == "y" else 2)
    keep_faces: List[tri] = []
    used: List[int] = []
    used_set = set()
    for (i, j, k) in faces:
        vi = vertices[i][ai]
        vj = vertices[j][ai]
        vk = vertices[k][ai]
        tri_min = min(vi, vj, vk)
        tri_max = max(vi, vj, vk)
        if tri_max >= min_v and tri_min <= max_v:
            keep_faces.append((i, j, k))
            for idx in (i, j, k):
                if idx not in used_set:
                    used_set.add(idx)
                    used.append(idx)
    # remap compacto
    remap = {old: new for new, old in enumerate(used)}
    new_verts = [vertices[i] for i in used]
    new_faces = [(remap[i], remap[j], remap[k]) for (i, j, k) in keep_faces]
    return new_verts, new_faces


def write_stl_binary(path: Path, vertices: List[vec3], faces: List[tri]) -> None:
    # funcao write_stl_binary
    # grava ficheiro stl binario padrao com uma normal por triangulo
    # path caminho de saida
    # vertices lista de todos os pontos
    # faces lista de triplos de indices
    # cria pastas pais se ainda nao existirem
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        # cabecalho de oitenta bytes reservado muitos leitores ignoram conteudo
        f.write(b"\0" * 80)
        # contagem de triangulos em uint32 little endian
        f.write(struct.pack("<I", len(faces)))
        # para cada triangulo calculamos a normal pela regra da mao direita
        for i, j, k in faces:
            x0, y0, z0 = vertices[i]
            x1, y1, z1 = vertices[j]
            x2, y2, z2 = vertices[k]
            # vetor u ao longo de uma aresta
            ux, uy, uz = x1 - x0, y1 - y0, z1 - z0
            # vetor v ao longo da outra aresta a partir do mesmo vertice
            vx, vy, vz = x2 - x0, y2 - y0, z2 - z0
            # produto vetorial u x v aponta para fora se a ordem i j k for coerente
            nx = uy * vz - uz * vy
            ny = uz * vx - ux * vz
            nz = ux * vy - uy * vx
            # comprimento para normalizar evita divisao por zero com or um
            ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            nx, ny, nz = nx / ln, ny / ln, nz / ln
            # doze floats em little endian mais atributo uint16 zero com padding
            f.write(
                struct.pack(
                    "<12fHxx",
                    nx,
                    ny,
                    nz,
                    x0,
                    y0,
                    z0,
                    x1,
                    y1,
                    z1,
                    x2,
                    y2,
                    z2,
                    0,
                )
            )
