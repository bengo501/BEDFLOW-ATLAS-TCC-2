# nucleo de geracao geometrica stl em python puro
# o ficheiro packed bed stl chama este modulo depois de validar o json
#
# ha dois grandes caminhos conforme o campo packing method no ficheiro json
# caminho um chamado cientifico usa spherical packing ou hexagonal 3d
# caminho dois chamado legacy usa rigid body com simulacao de queda
#
# no caminho cientifico nao ha motor fisico blender dentro deste ficheiro
# as posicoes das esferas vem de funcoes em packed bed science
# depois pure bed mesh constroi o cilindro tampas e esferas como malha triangular
# no fim exportamos stl binario e um json lateral com metadados
#
# o dominio geometrico chama se annulus bed domain
# ele descreve o anel entre raio interno e externo e a faixa vertical entre tampas
# validate configuration verifica se cada centro respeita paredes e se pares nao colidem
#
# modo spherical packing em palavras simples
# imagina lancar pontos aleatorios dentro do volume permitido
# cada novo ponto so fica se estiver longe o suficiente dos anteriores
# longe significa distancia entre centros maior ou igual a soma dos raios mais gap
# se falhar muitas vezes seguidas o algoritmo pode parar antes do numero pedido
#
# modo hexagonal 3d em palavras simples
# imagina uma grade regular tipo favo cortada pelo cilindro
# os centros validos sao os nos da grade que caem dentro do dominio
# o passo horizontal opcional step x mexe na densidade horizontal da grade
#
# integracao backend
# quando o utilizador escolhe motor python no api o servico corre este script
# quando escolhe blender outro caminho usa leito extracao dentro do blender
#
from __future__ import annotations

import json
import sys
import time
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

# diretorio deste ficheiro serve para imports relativos sem instalar pacote
_PMDIR = Path(__file__).resolve().parent
if str(_PMDIR) not in sys.path:
    sys.path.insert(0, str(_PMDIR))

# raiz do repositorio sobe dois niveis a partir de scripts python modeling
_ROOT = Path(__file__).resolve().parents[2]
# ferramenta opcional de visualizacao noutra pasta
_VIS_CIL = _ROOT / "tools" / "vis_cilindro"
if str(_VIS_CIL) not in sys.path:
    sys.path.insert(0, str(_VIS_CIL))

# pasta scripts contem o pacote packed bed science como codigo fonte local
_SCRIPTS = Path(__file__).resolve().parents[1]
_BLENDER_SCRIPTS_DIR = _SCRIPTS / "blender_scripts"
if str(_BLENDER_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_BLENDER_SCRIPTS_DIR))

from modelo_cilindro import (  # noqa: E402
    gera_malha_tubo_com_tampas,
    mesh,
    params_cilindro,
    params_particulas,
    simula_ate_tampa_fechar,
)

from packed_bed_science.geometry_math import AnnulusBedDomain, estimate_porosity  # noqa: E402
from packed_bed_science.packing_hexagonal import generate_hexagonal_packing  # noqa: E402
from packed_bed_science.packing_modes import (  # noqa: E402
    merge_root_packing_mode,
    packing_method_from_section,
)
from packed_bed_science.packing_spherical import generate_spherical_packing  # noqa: E402
from packed_bed_science.validation import validate_configuration  # noqa: E402

from bed_config import (  # noqa: E402
    merge_root_generation_backend,
    normalize_generation_backend,
    resolve_bed_geometry_numbers,
)
from pure_bed_mesh import build_packed_bed_model, export_model_data  # noqa: E402
from stl_mesh_utils import (  # noqa: E402
    cylinder_axis,
    filter_faces_by_slab,
    merge_mesh,
    uv_sphere,
    write_stl_binary,
)

# alias de tipo para tripla de floats xyz
vec3 = Tuple[float, float, float]
# alias de tipo para triangulo como tres indices
tri = Tuple[int, int, int]


def _to_float(v: Any, default: float = 0.0) -> float:
    # converte entrada solta do json para float seguro
    # v e o valor bruto que pode ser none numero ou texto
    # default e o numero de recurso quando v e invalido ou none
    # passo um none devolve default
    # passo dois tipos numericos nativos viram float direto
    # passo tres texto limpa virgula europeia e chama float de novo
    # isto evita falhas quando o wizard grava numeros como string
    if v is None:
        return float(default)
    if isinstance(v, (int, float)):
        return float(v)
    return float(str(v).replace(",", "."))


def _to_int(v: Any, default: int = 0) -> int:
    # igual ao float mas o resultado final e inteiro
    # contagens e seeds devem ser inteiros para os geradores
    if v is None:
        return int(default)
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return int(v)
    return int(float(str(v).replace(",", ".")))


def _packing_method_name(packing: Dict[str, Any]) -> str:
    return packing_method_from_section(packing)


def _coerce_bool(v: Any, default: bool = True) -> bool:
    # strict validation e outros flags chegam como texto ou booleano
    # normalizamos para nao depender do tipo exato vindo do json
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in ("true", "1", "yes", "sim"):
        return True
    if s in ("false", "0", "no", "nao"):
        return False
    return default


def load_bed_json(path: Path) -> Dict[str, Any]:
    # le o ficheiro json e devolve um dicionario unico com chaves fixas
    # path e o caminho para o ficheiro gerado pelo wizard ou editado a mao
    # o objetivo e esconder a estrutura aninhada do json do resto do codigo
    # aplicamos merge de packing e generation no topo antes de ler seccoes
    # resolve bed geometry numbers aceita diameter ou r outer r inner
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        merge_root_packing_mode(data)
        merge_root_generation_backend(data)
    bed = dict(data.get("bed") or {})
    particles = data.get("particles") or {}
    lids = data.get("lids") or {}
    packing = data.get("packing") or {}

    # diameter altura e parede ja normalizados em metros
    diameter, height, wall = resolve_bed_geometry_numbers(bed)

    # count numero pedido de particulas pode vir como string
    count = particles.get("count", 100)
    # particle count final e usado pelos algoritmos de distribuicao
    count_i = _to_int(count, 100)

    # diametro da particula esferica
    pd = particles.get("diameter", 0.005)
    # particle diameter e o diametro fisico da esfera
    # depois o algoritmo converte para raio para o dominio
    particle_d = _to_float(pd, 0.005)

    # gravidade usada so no modo legacy rigid body
    grav = packing.get("gravity", -9.81)
    grav_f = _to_float(grav, -9.81)

    # espessuras fisicas das tampas inferior e superior
    bottom_t = _to_float(lids.get("bottom_thickness"), 0.003)
    top_t = _to_float(lids.get("top_thickness"), 0.003)

    # gap e folga minima entre superficies de duas esferas vizinhas
    gap = packing.get("gap")
    if gap is not None:
        gap_f = _to_float(gap, 0.0)
    else:
        gap_f = _to_float(packing.get("collision_margin"), 0.0)
    # gap e o valor que define a folga minima entre esferas
    # ele entra tanto na geracao como na validacao

    slice_raw = data.get("slice") if isinstance(data, dict) else None
    slice_cfg = dict(slice_raw) if isinstance(slice_raw, dict) else {}
    # compatibilidade: aceitar chaves soltas na raiz
    for k in (
        "slice_enabled",
        "slice_thickness",
        "slice_axis",
        "slice_position",
        "keep_only_intersecting_particles",
        "preserve_original_packing",
    ):
        if isinstance(data, dict) and k in data and k not in slice_cfg:
            slice_cfg[k] = data.get(k)

    # chaves abaixo alimentam tanto o modo cientifico como o legacy
    return {
        "diameter": diameter,
        "height": height,
        "wall_thickness": wall,
        "particle_count": max(1, count_i),
        "particle_diameter": particle_d,
        "gravity": grav_f,
        "bottom_thickness": bottom_t,
        "top_thickness": top_t,
        "packing": packing,
        "packing_method": packing_method_from_section(packing),
        "gap": gap_f,
        "random_seed": packing.get("random_seed"),
        "max_placement_attempts": _to_int(packing.get("max_placement_attempts"), 500_000),
        "strict_validation": _coerce_bool(packing.get("strict_validation"), True),
        "step_x": packing.get("step_x"),
        "particles_seed": particles.get("seed"),
        "mesh_segmentos": _to_int(packing.get("mesh_segmentos"), 48),
        "sphere_lat": _to_int(packing.get("sphere_lat"), 4),
        "sphere_lon": _to_int(packing.get("sphere_lon"), 6),
        "generation_backend": normalize_generation_backend(
            data.get("generation_backend") if isinstance(data, dict) else None
        ),
        "slice": slice_cfg,
    }


def _mesh_to_lists(m: mesh) -> Tuple[List[vec3], List[tri]]:
    # traduz o tipo mesh do modelo cilindro legado para listas python simples
    # vertices sao pontos xyz
    # indices agrupam tres inteiros por triangulo
    return list(m.vertices), list(m.indices)


def _legacy_generate_stl(p: Dict[str, Any], out_stl: Path, max_passos: int) -> None:
    # modo legacy rigid body
    # p e o dicionario devolvido por load bed json
    # out stl e o caminho de escrita do ficheiro final
    # max passos limita o loop da simulacao simples de queda
    # primeiro calculamos raios do tubo e altura
    # depois geramos malha do tubo com tampas
    # depois simulamos particulas ate parar
    # depois validamos com packed bed science se strict pedir
    # por fim fundimos esferas uv ao tubo e escrevemos stl
    r_ext = p["diameter"] / 2.0
    # r int raio interno nunca menor que um pouco mais que raio da particula para nao ficar impossivel
    r_int = max(r_ext - p["wall_thickness"], p["particle_diameter"] * 0.51)
    # altura cilindro
    altura = p["height"]

    # parametros do tubo para malha com tampas incluidas no legacy
    p_cil = params_cilindro(
        raio_externo=r_ext,
        raio_interno=r_int,
        altura=altura,
        segmentos=min(64, max(12, p.get("mesh_segmentos", 48))),
    )
    # parametros das particulas numero raio passos e dt
    p_par = params_particulas(
        num_particulas=p["particle_count"],
        raio_particula=p["particle_diameter"] / 2.0,
        gravidade=p["gravity"],
        dt=0.004,
        max_passos=max_passos,
    )

    t_wall0 = time.perf_counter()
    # gera malha do tubo com tampas como no fluxo antigo
    malha_tubo = gera_malha_tubo_com_tampas(p_cil)
    verts, faces = _mesh_to_lists(malha_tubo)

    # simula ate as particulas pararem ou fechar tampa conforme funcao legacy
    particulas_finais, _ = simula_ate_tampa_fechar(p_cil, p_par)
    # raio esferico igual ao usado na simulacao
    r_s = p_par.raio_particula
    # validacao best effort fisica legacy e aproximada pode haver falsos positivos
    tb = p["bottom_thickness"]
    tt = p["top_thickness"]
    gap_v = p["gap"]
    domain_chk = AnnulusBedDomain(
        r_int=r_int,
        r_ext=r_ext,
        height=altura,
        bottom_cap_thickness=tb,
        top_cap_thickness=tt,
        r_sphere=r_s,
        gap=gap_v,
    )
    centers_chk = [tuple(part.pos) for part in particulas_finais]
    radii_chk = [r_s] * len(centers_chk)
    report_legacy = validate_configuration(centers_chk, radii_chk, domain_chk, gap_v)
    if p["strict_validation"] and not report_legacy.get("ok", False):
        raise RuntimeError(
            "validacao pos simulacao rigid body falhou: "
            + str(report_legacy.get("messages", []))[:500]
        )
    # para cada particula final adiciona esfera uv
    for part in particulas_finais:
        x, y, z = part.pos
        sv, sf = uv_sphere(x, y, z, r_s, lat=p["sphere_lat"], lon=p["sphere_lon"])
        verts, faces = merge_mesh(verts, faces, sv, sf)

    write_stl_binary(out_stl, verts, faces)
    elapsed = time.perf_counter() - t_wall0
    preview_n = 12
    # json lateral para o modo testes rapidos e para inspecao humana sem abrir stl
    # report legacy vem de validate configuration que compara pares e limites do dominio
    # sphere centers preview sao poucas linhas para tabela id x y z no terminal
    # sphere centers histogram sao ate quinhentos pontos para barras de altura aproximadas
    # isto nao repete a lista completa de centros para poupar tamanho em leitos grandes
    sidecar: Dict[str, Any] = {
        "packing_method": "rigid_body",
        "validation": report_legacy,
        "generation_wall_time_sec": elapsed,
        "n_spheres_requested": p["particle_count"],
        "n_spheres_placed": len(centers_chk),
        "sphere_centers_preview": [
            [float(c[0]), float(c[1]), float(c[2])] for c in centers_chk[:preview_n]
        ],
        "sphere_centers_histogram": [
            [float(c[0]), float(c[1]), float(c[2])]
            for c in centers_chk[: min(len(centers_chk), 500)]
        ],
        "generation": {
            "mode": "legacy_python_rigid",
            "max_passos": max_passos,
        },
        "pair_violations": report_legacy.get("pair_violations"),
        "domain_violations": report_legacy.get("domain_violations"),
    }
    out_json = out_stl.parent / f"{out_stl.stem}_pure_bed.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as fp:
        json.dump(sidecar, fp, indent=2, ensure_ascii=False)


def _science_generate_stl(p: Dict[str, Any], out_stl: Path) -> None:
    # modo cientifico sem fisica tipo blender
    # passo um calcula raios e altura e monta annulus bed domain
    # passo dois escolhe gerador conforme packing method
    # passo tres valida centros e estima porosidade
    # passo quatro constroi malha com pure bed mesh e exporta
    # colisao entre esferas e checagem de paredes usam validate configuration
    # a ideia e distancia entre centros maior ou igual soma raios mais gap
    r_ext = p["diameter"] / 2.0
    # r int raio interno parede menos espessura
    r_int = r_ext - p["wall_thickness"]
    # checagem basica de sanidade antes de continuar
    if r_int <= 0 or r_int >= r_ext:
        raise ValueError("raio interno invalido verifique diameter e wall thickness")
    # altura util
    altura = p["height"]
    # raio da esfera metade do diametro da particula
    r_s = p["particle_diameter"] / 2.0
    # gap copiado do dicionario
    gap = p["gap"]
    # espessuras de tampa inferior e superior
    tb = p["bottom_thickness"]
    tt = p["top_thickness"]

    # domain encapsula limites radiais em xy e limites em z com tampas
    # o pacote packed bed science usa a mesma definicao no blender e aqui
    domain = AnnulusBedDomain(
        r_int=r_int,
        r_ext=r_ext,
        height=altura,
        bottom_cap_thickness=tb,
        top_cap_thickness=tt,
        r_sphere=r_s,
        gap=gap,
    )

    # method ja veio normalizado pelo loader
    method = p["packing_method"]
    # medimos tempo de cpu para o json lateral
    t0 = time.perf_counter()
    if method == "spherical_packing":
        # ramo spherical packing
        # o gerador interno tenta varias vezes ate aceitar cada centro
        # seed controla repetibilidade dos sorteios
        seed = p.get("random_seed")
        if seed is None:
            seed = p.get("particles_seed")
        # seed none deixa o gerador escolher comportamento proprio
        seed_i = _to_int(seed, 42) if seed is not None else None
        # generate spherical packing devolve dict com centros e estatisticas
        gen = generate_spherical_packing(
            domain,
            p["particle_count"],
            r_s,
            gap,
            random_seed=seed_i,
            max_placement_attempts=p["max_placement_attempts"],
        )
    else:
        # ramo hexagonal 3d
        # a grade e deterministica e rapida comparada ao sorteio
        # step x controla distancia horizontal entre colunas
        step_x_opt = p.get("step_x")
        step_x_f = _to_float(step_x_opt, 0.0) if step_x_opt is not None else None
        # valor zero ou negativo vira none para automatico
        if step_x_f is not None and step_x_f <= 0:
            step_x_f = None
        # generate hexagonal packing devolve dict parecido ao spherical
        gen = generate_hexagonal_packing(
            domain,
            p["particle_count"],
            r_s,
            gap,
            step_x=step_x_f,
        )
    # tempo decorrido em segundos
    elapsed = time.perf_counter() - t0

    # centers e lista de tuplos xyz em metros
    centers = gen["centers"]
    # radii repete o mesmo raio porque todas as esferas sao iguais neste fluxo
    radii = [r_s] * len(centers)
    # validate configuration percorre pares e dominio
    # para cada par compara distancia com soma raios mais gap
    # para cada centro verifica se ainda esta dentro do volume permitido para a esfera inteira
    report_val = validate_configuration(centers, radii, domain, gap)
    # porosidade aproximada por volume
    poros = estimate_porosity(domain, centers, r_s)

    # strict true transforma avisos de validacao em excecao
    strict = p["strict_validation"]
    if not report_val.get("ok", False):
        if strict:
            raise RuntimeError(
                "validacao geometrica falhou: " + str(report_val.get("messages", []))[:500]
            )
    # spherical pode falhar em atingir o numero pedido por esgotar tentativas
    if method == "spherical_packing" and len(centers) < p["particle_count"] and strict:
        raise RuntimeError(
            f"spherical packing so colocou {len(centers)} de {p['particle_count']}"
        )

    # segmentos do cilindro limitados para nao explodir memoria
    seg = min(64, max(12, p.get("mesh_segmentos", 48)))
    slice_cfg = dict(p.get("slice") or {})
    slice_enabled = _coerce_bool(slice_cfg.get("slice_enabled"), False)
    if not slice_enabled:
        packed = build_packed_bed_model(
            r_ext=r_ext,
            r_int=r_int,
            height=altura,
            bottom_cap_thickness=tb,
            top_cap_thickness=tt,
            sphere_centers=centers,
            sphere_radius=r_s,
            segmentos_cil=seg,
            lat_sphere=p["sphere_lat"],
            lon_sphere=p["sphere_lon"],
        )
    else:
        axis = str(slice_cfg.get("slice_axis") or "y").strip().lower()
        if axis not in ("x", "y", "z"):
            axis = "y"
        thickness = _to_float(slice_cfg.get("slice_thickness"), r_s * 0.6)
        if thickness <= 0:
            thickness = r_s * 0.6
        pos = _to_float(slice_cfg.get("slice_position"), 0.0)
        keep_only = _coerce_bool(slice_cfg.get("keep_only_intersecting_particles"), True)
        preserve = _coerce_bool(slice_cfg.get("preserve_original_packing"), True)

        # parede+tampas
        shell = build_packed_bed_model(
            r_ext=r_ext,
            r_int=r_int,
            height=altura,
            bottom_cap_thickness=tb,
            top_cap_thickness=tt,
            sphere_centers=[],
            sphere_radius=r_s,
            segmentos_cil=seg,
            lat_sphere=p["sphere_lat"],
            lon_sphere=p["sphere_lon"],
        )
        min_v = pos - thickness / 2.0
        max_v = pos + thickness / 2.0
        v_shell, f_shell = filter_faces_by_slab(
            shell.mesh.vertices,
            shell.mesh.faces,
            axis=axis,
            min_v=min_v,
            max_v=max_v,
        )

        # particulas como cilindros achatados (discos)
        ai = 0 if axis == "x" else (1 if axis == "y" else 2)
        v_all: List[vec3] = list(v_shell)
        f_all: List[tri] = list(f_shell)
        for (x, y, z) in centers:
            coord = (x, y, z)[ai]
            d = abs(coord - pos)
            if d > (r_s + thickness / 2.0):
                if keep_only:
                    continue
                continue
            rs = math.sqrt(max(0.0, r_s * r_s - d * d))
            if rs <= 0:
                continue
            if preserve:
                cx, cy, cz = x, y, z
            else:
                if axis == "x":
                    cx, cy, cz = pos, y, z
                elif axis == "y":
                    cx, cy, cz = x, pos, z
                else:
                    cx, cy, cz = x, y, pos
            cv, cf = cylinder_axis(
                cx,
                cy,
                cz,
                rs,
                thickness,
                axis=axis,
                segments=max(12, int(seg)),
            )
            v_all, f_all = merge_mesh(v_all, f_all, cv, cf)

        # packed minimal para sidecar
        packed = type(shell)(mesh=type(shell.mesh)(vertices=v_all, faces=f_all), meta=shell.meta)  # type: ignore

    preview_n = 12
    gen_public = {k: v for k, v in gen.items() if k != "centers"}
    attempts_i = gen.get("attempts")
    reject_approx = None
    if isinstance(attempts_i, (int, float)):
        # no spherical packing cada tentativa falha conta como rejeicao aproximada
        # tentativas aceites mais rejeicoes somam o total attempts do gerador
        reject_approx = max(0, int(attempts_i) - len(centers))
    # extra junta metadados ao packed bed model antes de export model data
    # export escreve stl binario e opcionalmente este extra como ficheiro json lateral
    # spherical e hexagonal passam por validate configuration depois dos geradores
    # a validacao verifica cada par de esferas com distancia maior ou igual dois r mais gap
    # tambem verifica cada centro dentro do anel cilindrico com folga para tampas
    extra: Dict[str, Any] = {
        "packing_method": method,
        "validation": report_val,
        "porosity_estimate": poros,
        "generation": gen_public,
        "generation_wall_time_sec": elapsed,
        "gap_convention": "center_distance >= r1+r2+gap",
        "n_spheres_requested": p["particle_count"],
        "n_spheres_placed": len(centers),
        "sphere_centers_preview": [
            [float(c[0]), float(c[1]), float(c[2])] for c in centers[:preview_n]
        ],
        "sphere_centers_histogram": [
            [float(c[0]), float(c[1]), float(c[2])]
            for c in centers[: min(len(centers), 500)]
        ],
        "pair_violations": report_val.get("pair_violations"),
        "domain_violations": report_val.get("domain_violations"),
        "placement_attempts_total": attempts_i,
        "placement_rejections_approx": reject_approx,
    }
    # json opcional com mesmo nome base que stl mais sufixo pure bed
    out_json = out_stl.parent / f"{out_stl.stem}_pure_bed.json"
    if slice_enabled:
        extra["slice"] = slice_cfg
    export_model_data(packed, out_stl, out_json=out_json, extra=extra)


def generate_packed_bed_stl(
    bed_json: Path, out_stl: Path, max_passos: int = 12000
) -> None:
    # entrada publica unica para testes e para o servico fastapi
    # bed json e o ficheiro de parametros
    # out stl e o destino do triangulos
    # max passos so entra no fluxo legacy
    p = load_bed_json(bed_json)
    # despacho simples por nome do metodo
    if p["packing_method"] in ("spherical_packing", "hexagonal_3d"):
        _science_generate_stl(p, out_stl)
    else:
        _legacy_generate_stl(p, out_stl, max_passos)


# resumo final para quem le o ficheiro inteiro
# tubo oco vem de malha parametrizada por segmentos
# tampas sao volumes curtos
# esferas sao uv sphere com lat e lon controlaveis
# spherical e aleatorio com rejeicao
# hexagonal e grade cortada ao cilindro
# validate configuration fecha o ciclo de seguranca geometrica
# motor python escolhido na api aponta para este script
# motor blender escolhido na api aponta para o projeto blender
