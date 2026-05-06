import bpy
import math
import random
import json
import sys
import argparse
import time
from pathlib import Path

# o blender executa este arquivo como script entao o diretorio do arquivo precisa estar no sys path
# assim o python acha a pasta packed_bed_science ao lado deste arquivo
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

# modulos sem bpy definem matematica validacao e algoritmos de posicao
from packed_bed_science.geometry_math import AnnulusBedDomain, estimate_porosity
from packed_bed_science.packing_modes import merge_root_packing_mode, packing_method_from_section
from packed_bed_science.validation import validate_configuration
from packed_bed_science.packing_spherical import generate_spherical_packing
from packed_bed_science.packing_hexagonal import generate_hexagonal_packing

# blender_build usa bpy para criar tubo tampas e esferas ja posicionadas
from packed_bed_science.blender_build import (
    create_hollow_cylinder,
    create_caps,
    create_spheres,
)

# =============
# Limpar cena =
# =========================================================================================
def limpar_cena():
    #remove todos os objetos da cena
    bpy.ops.object.select_all(action='SELECT') #selecionar todos os objetos da cena
    bpy.ops.object.delete(use_global=False) # deletar todos os objetos da cena
    print("cena limpa")
# =========================================================================================

# ====================
# Criar cilindro oco =
# =========================================================================================
def criar_cilindro_oco(altura=0.1, diametro_externo=0.025, espessura_parede=0.002):
    # cria um cilindro oco (leito de extracao)
    # parametros: altura: altura do leito em metros
    #             diametro_externo: diametro externo em metros  
    #             espessura_parede: espessura da parede em metros
    
    # calcular raios
    raio_externo = diametro_externo / 2 # calcular raio externo baseado no diametro externo dividido por 2
    raio_interno = raio_externo - espessura_parede # calcular raio interno baseado no raio externo e espessura da parede
    
    # criar cilindro externo
    bpy.ops.mesh.primitive_cylinder_add( # criar cilindro com tamanho especifico e localizacao 0,0,0 (centro)
        radius=raio_externo, # raio do cilindro baseado no raio externo
        depth=altura, # altura do cilindro baseado na altura
        location=(0, 0, altura/2) # localizacao do cilindro baseada na altura dividida por 2
    )
    cilindro_externo = bpy.context.active_object # objeto ativo atual
    cilindro_externo.name = "leito_extracao" # nome do objeto leito_extracao
    
    # criar cilindro interno para fazer o furo
    bpy.ops.mesh.primitive_cylinder_add( # criar cilindro com tamanho especifico e localizacao 0,0,0 (centro)
        radius=raio_interno, # raio do cilindro baseado no raio interno
        depth=altura + 0.01,  # um pouco maior para cortar bem
        location=(0, 0, altura/2) # localizacao do cilindro baseada na altura dividida por 2
    )
    cilindro_interno = bpy.context.active_object # objeto ativo atual
    cilindro_interno.name = "furo_temporario" # nome do objeto furo_temporario
    
    # fazer operacao booleana (subtracao)
    bool_mod = cilindro_externo.modifiers.new(name="Boolean", type='BOOLEAN') # criar modificador booleano
    bool_mod.operation = 'DIFFERENCE' # operacao booleana (subtracao)
    bool_mod.object = cilindro_interno # objeto interno para subtrair
    
    # aplicar o modificador
    bpy.context.view_layer.objects.active = cilindro_externo # objeto ativo atual
    bpy.ops.object.modifier_apply(modifier="Boolean") # aplicar o modificador booleano
    
    # remover cilindro interno temporario
    bpy.data.objects.remove(cilindro_interno, do_unlink=True) # remover o cilindro interno
    
    print(f"leito criado: altura={altura}m, diametro={diametro_externo}m")
    return cilindro_externo # retornar o cilindro externo
# =========================================================================================

# =============
# Criar tampa =
# =========================================================================================
def criar_tampa(posicao_z, diametro=0.025, espessura=0.003, nome="tampa", tem_colisao=True):
    # cria uma tampa circular
    # parametros: posicao_z: posicao vertical da tampa
    #             diametro: diametro da tampa
    #             espessura: espessura da tampa
    #             nome: nome do objeto
    #             tem_colisao: se false, particulas atravessam (tampa superior)
    bpy.ops.mesh.primitive_cylinder_add( # criar cilindro com tamanho especifico e localizacao 0,0,0 (centro)
        radius=diametro/2,
        depth=espessura, # espessura do cilindro
        location=(0, 0, posicao_z) # localizacao do cilindro baseada na posicao z
    )
    tampa = bpy.context.active_object # objeto ativo atual
    tampa.name = nome # nome do objeto
    tampa["tem_colisao"] = tem_colisao  # marcar se tem colisao
    
    print(f"{nome} criada na posicao z={posicao_z}m (colisao: {tem_colisao})")
    return tampa
# =========================================================================================

# ==================
# Criar particulas =
# =========================================================================================
def criar_particulas(quantidade=30, raio_leito=0.0125, altura_leito=0.1, raio_particula=0.001):
    # cria particulas esfericas que vao cair no leito    
    # parametros: quantidade: numero de particulas
    #             raio_leito: raio interno do leito
    #             altura_leito: altura do leito
    #             raio_particula: raio de cada particula
    particulas = []
    
    #criar particulas 
    for i in range(quantidade):
        # posicao aleatoria acima do leito para as particulas cairem
        x = random.uniform(-raio_leito * 0.7, raio_leito * 0.7)
        y = random.uniform(-raio_leito * 0.7, raio_leito * 0.7)
        z = altura_leito + 0.02 + (i * 0.005)  # espacar verticalmente para evitar sobreposicao
        
        # criar particula esferica
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=raio_particula,
            location=(x, y, z)
        )
        particula = bpy.context.active_object
        particula.name = f"particula_{i+1:02d}"
        particulas.append(particula)
    
    print(f"{quantidade} particulas criadas")
    return particulas
# =========================================================================================

# ================
# Aplicar fisica =
# =========================================================================================
def aplicar_fisica(objeto, eh_movel=True, tem_colisao=True):
    # aplica fisica de corpo rigido aos objetos    
    # parametros: objeto: objeto do blender
    #             eh_movel: se true, objeto pode se mover (particulas)
    #             se false, objeto eh estatico (leito e tampas)
    #             tem_colisao: se false, objeto nao colide (tampa superior)

    # selecionar o objeto
    bpy.context.view_layer.objects.active = objeto
    
    # verificar se objeto tem marcacao de colisao customizada
    if "tem_colisao" in objeto and not objeto["tem_colisao"]:
        print(f"fisica nao aplicada (sem colisao): {objeto.name}")
        return
    
    #aplicar fisica de acordo com o tipo de objeto
    if eh_movel:
        # particulas: corpo rigido com gravidade
        bpy.ops.rigidbody.object_add(type='ACTIVE')
        objeto.rigid_body.mass = 0.01  # massa pequena
        objeto.rigid_body.friction = 0.5  # atrito medio
        objeto.rigid_body.restitution = 0.3  # pouco elastica
        objeto.rigid_body.linear_damping = 0.1  # amortecimento linear
        objeto.rigid_body.angular_damping = 0.1  # amortecimento angular
        print(f"fisica aplicada (movel): {objeto.name}")
    else:
        # leito e tampas: corpo rigido sem gravidade (estatico)
        bpy.ops.rigidbody.object_add(type='PASSIVE')
        objeto.rigid_body.friction = 0.8  # muito atrito para segurar particulas
        objeto.rigid_body.restitution = 0.1  # pouco elastico
        
        # importante: usar mesh collision para cilindro oco
        objeto.rigid_body.collision_shape = 'MESH'
        objeto.rigid_body.mesh_source = 'FINAL'  # usar geometria final (pos-boolean)
        
        print(f"fisica aplicada (estatico, mesh collision): {objeto.name}")
# =========================================================================================

# =============================
# Configurar simulacao fisica =
# =========================================================================================
def configurar_simulacao_fisica(gravidade=-9.81, substeps=10, iterations=10):
    #configura parametros globais da simulacao fisica
    scene = bpy.context.scene
    
    # configurar mundo da fisica
    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    
    # configurar propriedades do mundo da fisica
    if scene.rigidbody_world:
        try:
            # configurar gravidade
            if hasattr(scene.rigidbody_world, 'effector_weights'):
                scene.rigidbody_world.effector_weights.gravity = abs(gravidade) / 9.81
            
            # configurar qualidade da simulacao
            if hasattr(scene.rigidbody_world, 'substeps_per_frame'):
                scene.rigidbody_world.substeps_per_frame = substeps
            
            if hasattr(scene.rigidbody_world, 'solver_iterations'):
                scene.rigidbody_world.solver_iterations = iterations
            
            # configurar velocidade de repouso
            if hasattr(scene.rigidbody_world, 'use_split_impulse'):
                scene.rigidbody_world.use_split_impulse = True
                
            print(f"simulacao fisica configurada (gravidade: {gravidade}, substeps: {substeps}, iterations: {iterations})")
            
        except AttributeError as e:
            print(f"aviso: nao foi possivel configurar todas as propriedades da fisica: {e}")
            print("usando configuracao padrao do blender")
    else:
        print("erro: nao foi possivel criar mundo da fisica")
# =========================================================================================

# =====================
# Executar simulacao =
# =========================================================================================
def executar_simulacao_fisica(tempo_simulacao=5.0, fps=24):
    """
    executa a animacao de fisica para fazer particulas cairem
    
    parametros:
        tempo_simulacao: tempo em segundos da simulacao
        fps: frames por segundo (padrao 24)
    """
    scene = bpy.context.scene
    
    # configurar range de frames
    total_frames = int(tempo_simulacao * fps)
    scene.frame_start = 1
    scene.frame_end = total_frames
    scene.frame_current = 1
    
    print(f"\nexecutando simulacao fisica...")
    print(f"tempo: {tempo_simulacao}s | frames: {total_frames} | fps: {fps}")
    
    # executar frame por frame para garantir fisica
    for frame in range(1, total_frames + 1):
        scene.frame_set(frame)
        
        # mostrar progresso a cada 10%
        if frame % (total_frames // 10) == 0 or frame == 1 or frame == total_frames:
            progresso = (frame / total_frames) * 100
            print(f"  progresso: {progresso:.0f}% (frame {frame}/{total_frames})")
    
    print("simulacao fisica executada com sucesso!")
    print("particulas acomodadas no leito\n")
# =========================================================================================

# ==================
# Bake da fisica =
# =========================================================================================
def _temp_override_view3d():
    """
    em --background muitas vezes nao ha area VIEW_3D; bake_to_keyframes e keyframe_insert
    exigem contexto 3d valido. devolve (dict_para_temp_override ou None, area_promovida_ou_None, tipo_anterior).
    """
    wm = bpy.context.window_manager
    if not wm.windows:
        return None, None, None
    win = wm.windows[0]
    for area in win.screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "WINDOW":
                    ctx = dict(
                        window=win,
                        screen=win.screen,
                        area=area,
                        region=region,
                        scene=bpy.context.scene,
                        view_layer=bpy.context.view_layer,
                    )
                    return ctx, None, None
    area = win.screen.areas[0]
    prev = area.type
    area.type = "VIEW_3D"
    region = None
    for r in area.regions:
        if r.type == "WINDOW":
            region = r
            break
    if region is None:
        area.type = prev
        return None, None, None
    ctx = dict(
        window=win,
        screen=win.screen,
        area=area,
        region=region,
        scene=bpy.context.scene,
        view_layer=bpy.context.view_layer,
    )
    return ctx, area, prev


def _congelar_particulas_depsgraph(particulas):
    """
    fallback headless: copia matrix_world avaliada no frame atual e remove rigid body
    sem depender de bake_to_keyframes.
    """
    depsgraph = bpy.context.evaluated_depsgraph_get()
    bpy.context.view_layer.update()
    for obj in particulas:
        ev = obj.evaluated_get(depsgraph)
        obj.matrix_world = ev.matrix_world.copy()
    ovr, promoted_area, promoted_prev = _temp_override_view3d()
    if ovr is None:
        print("aviso: sem override 3d; posicoes copiadas mas rigid body pode permanecer")
        return
    try:
        with bpy.context.temp_override(**ovr):
            for obj in particulas:
                if not obj.rigid_body:
                    continue
                bpy.ops.object.select_all(action="DESELECT")
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.rigidbody.object_remove()
        print("congelamento alternativo: matriz avaliada aplicada e rigid body removido")
    except Exception as e:
        print(f"aviso: congelamento alternativo incompleto: {e}")
    finally:
        if promoted_area is not None and promoted_prev is not None:
            promoted_area.type = promoted_prev


def fazer_bake_fisica(particulas):
    """
    faz bake (congelamento) da fisica nas particulas
    isso converte a simulacao em keyframes fixos
    """
    print("\nfazendo bake da fisica...")

    ovr, promoted_area, promoted_prev = _temp_override_view3d()
    try:
        if ovr is not None:
            with bpy.context.temp_override(**ovr):
                bpy.ops.object.select_all(action="DESELECT")
                for particula in particulas:
                    particula.select_set(True)
                if particulas:
                    bpy.context.view_layer.objects.active = particulas[0]
                bpy.ops.rigidbody.bake_to_keyframes(
                    frame_start=bpy.context.scene.frame_start,
                    frame_end=bpy.context.scene.frame_end,
                    step=1,
                )
            print("bake concluido - fisica convertida em keyframes")
            with bpy.context.temp_override(**ovr):
                for particula in particulas:
                    if particula.rigid_body:
                        bpy.ops.object.select_all(action="DESELECT")
                        particula.select_set(True)
                        bpy.context.view_layer.objects.active = particula
                        bpy.ops.rigidbody.object_remove()
            print("rigid body removido - particulas estao fixas nas posicoes finais")
        else:
            raise RuntimeError("sem contexto VIEW_3D para bake")
    except Exception as e:
        print(f"aviso: erro no bake: {e}")
        print("tentando congelar posicoes via depsgraph (modo background)...")
        _congelar_particulas_depsgraph(particulas)
    finally:
        if promoted_area is not None and promoted_prev is not None:
            promoted_area.type = promoted_prev
# =========================================================================================

# ======
# Main =
# =========================================================================================
def main():
    #funcao principal - cria tudo e configura fisica
    print("======criando leito de extracao com fisica=======")
    # limpar tudo
    limpar_cena()
    # parametros do leito
    altura = 0.1          # 10 cm
    diametro = 0.025      # 2.5 cm  
    espessura = 0.002     # 2 mm
    # criar geometria
    print("criando geometria...")
    leito = criar_cilindro_oco(altura, diametro, espessura)
    tampa_inferior = criar_tampa(-espessura/2, diametro, espessura, "tampa_inferior", tem_colisao=True)
    tampa_superior = criar_tampa(altura + espessura/2, diametro, espessura, "tampa_superior", tem_colisao=False)
    # criar particulas
    particulas = criar_particulas(30, diametro/2, altura, 0.001)
    # configurar fisica
    print("configurando fisica...")
    configurar_simulacao_fisica()
    # aplicar fisica ao leito e tampas (estaticos)
    aplicar_fisica(leito, eh_movel=False)
    aplicar_fisica(tampa_inferior, eh_movel=False)
    # tampa superior sem colisao (particulas atravessam)
    aplicar_fisica(tampa_superior, eh_movel=False)
    # aplicar fisica as particulas (moveis)
    for particula in particulas:
        aplicar_fisica(particula, eh_movel=True)
    
    # executar simulacao para particulas cairem
    executar_simulacao_fisica(tempo_simulacao=5.0, fps=24)
    
    # fazer bake para fixar posicoes finais
    fazer_bake_fisica(particulas)
    
    print()
    print("=====pronto=====")
    print(f"objetos criados:")
    print(f"- leito cilindrico oco (colisao: mesh)")
    print(f"- tampa inferior (colisao: ativa)")
    print(f"- tampa superior (colisao: desativada)")
    print(f"- {len(particulas)} particulas (posicoes finais apos fisica)")
    print()
    print("particulas ja estao acomodadas dentro do leito!")
    print("abra o arquivo para ver o resultado final")

def ler_parametros_json(json_path):
    """ler parametros do arquivo json"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            params = json.load(f)
        if isinstance(params, dict):
            merge_root_packing_mode(params)
        print(f"parametros carregados de: {json_path}")
        return params
    except Exception as e:
        print(f"erro ao ler json: {e}")
        return None


def _coerce_float(v, default=0.0):
    # o json do compilador as vezes vem com numeros como texto
    # esta funcao devolve sempre float usando default se v for none
    if v is None:
        return float(default)
    if isinstance(v, (int, float)):
        return float(v)
    return float(str(v).strip())


def _coerce_int(v, default=0):
    # igual ao float mas arredonda para inteiro no final
    if v is None:
        return int(default)
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return int(v)
    return int(float(str(v).strip()))


def _packing_method_name(packing):
    return packing_method_from_section(packing)


def _coerce_bool(v, default=True):
    # json pode trazer true false como string em alguns fluxos manuais
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


def aplicar_thin_slice(slice_cfg: dict, *, altura: float, raio_ext: float) -> None:
    # aplica um corte booleano (intersect) com um cubo fino para manter apenas uma fatia 3d
    # eixo do corte define o eixo normal da fatia (x/y/z)
    if not isinstance(slice_cfg, dict):
        return
    if not _coerce_bool(slice_cfg.get("slice_enabled"), False):
        return
    axis = str(slice_cfg.get("slice_axis") or "y").strip().lower()
    if axis not in ("x", "y", "z"):
        axis = "y"
    thickness = _coerce_float(slice_cfg.get("slice_thickness"), 0.002)
    if thickness <= 0:
        thickness = 0.002
    pos = _coerce_float(slice_cfg.get("slice_position"), 0.0)

    # dimensoes grandes para cobrir o modelo todo, exceto na direcao do corte
    big = max(altura * 2.0, raio_ext * 4.0, 1.0)
    dims = [big, big, big]
    ai = 0 if axis == "x" else (1 if axis == "y" else 2)
    dims[ai] = thickness
    loc = [0.0, 0.0, altura / 2.0]
    loc[ai] = pos

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=tuple(loc))
    cutter = bpy.context.active_object
    cutter.name = "thin_slice_cutter"
    cutter.scale = (dims[0] / 2.0, dims[1] / 2.0, dims[2] / 2.0)

    # aplicar boolean intersect em todos os meshes exceto o cutter
    targets = [o for o in bpy.data.objects if o.type == "MESH" and o.name != cutter.name]
    for obj in targets:
        try:
            mod = obj.modifiers.new(name="thin_slice", type="BOOLEAN")
            mod.operation = "INTERSECT"
            mod.object = cutter
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception as e:
            print(f"aviso: boolean falhou em {obj.name}: {e}")

    # remover cutter
    try:
        bpy.data.objects.remove(cutter, do_unlink=True)
    except Exception:
        pass


def _salvar_relatorio_packing(output_path: Path, relatorio: dict):
    # grava metricas de empacotamento ao lado do arquivo blend pedido
    # o nome segue o stem do blend mais sufixo packing report
    try:
        p = output_path.parent / f"{output_path.stem}_packing_report.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        print(f"relatorio de empacotamento: {p}")
    except Exception as e:
        print(f"aviso: nao foi possivel salvar relatorio json: {e}")


def export_outputs(args, output_path: Path):
    # centraliza exportacao para nao repetir o mesmo codigo em cada ramo do main
    print(f"\nsalvando arquivo em: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # args formats e uma string separada por virgula tipo blend gltf glb
    formats = [f.strip().lower() for f in args.formats.split(",")]
    print(f"formatos selecionados: {', '.join(formats)}")
    # cada bloco abaixo tenta exportar e imprime erro sem derrubar o script inteiro
    # se o destino for .blend, gravar sempre o ficheiro principal (json pode pedir so stl/obj)
    save_blend = "blend" in formats or output_path.suffix.lower() == ".blend"
    if save_blend:
        try:
            bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
            print(f"arquivo .blend salvo: {output_path}")
        except Exception as e:
            print(f"erro ao salvar .blend: {e}")
    if "gltf" in formats:
        try:
            gltf_path = output_path.with_suffix(".gltf")
            bpy.ops.export_scene.gltf(
                filepath=str(gltf_path),
                export_format="GLTF_SEPARATE",
                export_apply=True,
                export_yup=True,
                export_lights=True,
                export_extras=True,
            )
            print(f"arquivo .gltf exportado: {gltf_path}")
        except Exception as e:
            print(f"erro ao exportar .gltf: {e}")
    if "glb" in formats:
        try:
            glb_path = output_path.with_suffix(".glb")
            bpy.ops.export_scene.gltf(
                filepath=str(glb_path),
                export_format="GLB",
                export_apply=True,
                export_yup=True,
                export_lights=True,
                export_extras=True,
            )
            print(f"arquivo .glb exportado: {glb_path}")
        except Exception as e:
            print(f"erro ao exportar .glb: {e}")
    if "obj" in formats:
        try:
            obj_path = output_path.with_suffix(".obj")
            bpy.ops.wm.obj_export(
                filepath=str(obj_path),
                export_selected_objects=False,
                apply_modifiers=True,
                export_normals=True,
                export_uv=True,
                export_materials=True,
            )
            print(f"arquivo .obj exportado: {obj_path}")
        except Exception as e:
            print(f"erro ao exportar .obj: {e}")
    if "fbx" in formats:
        try:
            fbx_path = output_path.with_suffix(".fbx")
            bpy.ops.export_scene.fbx(
                filepath=str(fbx_path),
                use_selection=False,
                apply_scale_options="FBX_SCALE_ALL",
                axis_forward="-Z",
                axis_up="Y",
                apply_unit_scale=True,
                mesh_smooth_type="FACE",
            )
            print(f"arquivo .fbx exportado: {fbx_path}")
        except Exception as e:
            print(f"erro ao exportar .fbx: {e}")
    if "stl" in formats:
        try:
            stl_path = output_path.with_suffix(".stl")
            # blender 4.0.x: wm.stl_export pode nao existir; export_mesh.stl e o operador estavel
            try:
                bpy.ops.wm.stl_export(
                    filepath=str(stl_path),
                    export_selected_objects=False,
                    apply_modifiers=True,
                    ascii_format=False,
                )
            except Exception:
                bpy.ops.export_mesh.stl(
                    filepath=str(stl_path),
                    check_existing=False,
                    use_selection=False,
                    use_mesh_modifiers=True,
                    ascii=False,
                    global_scale=1.0,
                )
            print(f"arquivo .stl exportado: {stl_path}")
        except Exception as e:
            print(f"erro ao exportar .stl: {e}")
    print(f"\nexportacao concluida {len(formats)} formato(s) processado(s)")


def main_com_parametros():
    # ponto de entrada quando o blender chama python leito_extracao py depois de --
    # fluxo resumido
    # passo 1 ler json com bed particles lids packing
    # passo 2 descobrir packing method rigid body ou modos cientificos
    # passo 3 limpar cena e criar geometria
    # passo 4 se cientifico gera centros valida e cria esferas sem fisica
    # passo 5 se rigid body usa fisica antiga com bake
    # passo 6 exportar formatos pedidos
    argv = sys.argv
    if '--' in argv:
        argv = argv[argv.index('--') + 1:]
    else:
        # se nao houver argumentos, usar valores padrao
        print("executando com parametros padrao...")
        main()
        return
    
    # criar parser de argumentos
    parser = argparse.ArgumentParser(description='gerar leito empacotado no blender')
    parser.add_argument('--params', type=str, help='caminho do arquivo json com parametros')
    parser.add_argument('--output', type=str, help='caminho do arquivo de saida .blend')
    parser.add_argument('--formats', type=str, default='blend,gltf,glb', 
                        help='formatos de exportacao separados por virgula (blend,gltf,glb,obj,fbx,stl)')
    
    try:
        args = parser.parse_args(argv)
    except:
        # se falhar ao processar argumentos, usar padrao
        print("erro ao processar argumentos, usando padrao...")
        main()
        return
    
    # sem arquivo json voltamos ao demo interno main que usa numeros fixos no codigo
    if not args.params:
        print("sem --params json executando main padrao...")
        main()
        return

    params = ler_parametros_json(args.params)
    if not params:
        print("falha ao ler json executando main padrao...")
        main()
        return

    # cada secao do json alimenta um pedaco do modelo
    bed_raw = params.get("bed") or {}
    particles_raw = params.get("particles") or {}
    lids_raw = params.get("lids") or {}
    packing_raw = params.get("packing") or {}
    slice_cfg = params.get("slice") if isinstance(params, dict) else None
    if not isinstance(slice_cfg, dict):
        slice_cfg = {}

    # geometria do tubo e particulas com defaults seguros se faltar chave
    altura = _coerce_float(bed_raw.get("height"), 0.1)
    diametro = _coerce_float(bed_raw.get("diameter"), 0.05)
    espessura = _coerce_float(bed_raw.get("wall_thickness"), 0.002)
    num_particulas = _coerce_int(particles_raw.get("count"), 100)
    diametro_particula = _coerce_float(particles_raw.get("diameter"), 0.005)
    esp_tampa_inf = _coerce_float(lids_raw.get("bottom_thickness"), 0.003)
    esp_tampa_sup = _coerce_float(lids_raw.get("top_thickness"), 0.003)

    print("parametros do json:")
    print(f"  altura: {altura}m")
    print(f"  diametro: {diametro}m")
    print(f"  espessura parede: {espessura}m")
    print(f"  particulas: {num_particulas}")
    print(f"  diametro particula: {diametro_particula}m")

    metodo = _packing_method_name(packing_raw)
    print(f"  metodo empacotamento: {metodo}")

    try:
        limpar_cena()

        # raios usados igual no ramo cientifico e no ramo fisico para coerencia
        raio_ext = diametro / 2.0
        raio_int = raio_ext - espessura
        raio_particula = diametro_particula / 2.0
        # gap explicito vence se nao existir usamos collision margin do packing fisico antigo
        if packing_raw.get("gap") is not None:
            gap = _coerce_float(packing_raw.get("gap"), 0.0)
        else:
            gap = _coerce_float(packing_raw.get("collision_margin"), 0.0)

        # ramo cientifico spherical packing ou hexagonal tres d
        # diferente do rigid body nao ha queda nem bake de fisica blender
        # passos mentais ler parametros montar domain igual ao pure generation
        # chamar generate spherical packing ou generate hexagonal packing
        # validate configuration confere pares e dominio com a mesma matematica python
        # depois create hollow cylinder create caps e create spheres materializam na cena
        # gap e distancia extra entre superficies exigida entre centros usamos sphere center clearance no gerador
        if metodo in ("spherical_packing", "hexagonal_3d"):
            # aqui nao rodamos rigid body nem bake porque as posicoes ja sao finais
            print("modo cientifico: sem simulacao fisica rigid body")

            # domain encapsula todas as desigualdades geometricas em um so objeto
            domain = AnnulusBedDomain(
                r_int=raio_int,
                r_ext=raio_ext,
                height=altura,
                bottom_cap_thickness=esp_tampa_inf,
                top_cap_thickness=esp_tampa_sup,
                r_sphere=raio_particula,
                gap=gap,
            )

            # mede tempo de cpu do gerador para comparar metodos no relatorio
            t0_gen = time.perf_counter()
            if metodo == "spherical_packing":
                # monte carlo com rejeicao ver packed bed science packing spherical
                # seed pode vir do packing ou cair no seed das particles do dsl
                seed = packing_raw.get("random_seed")
                if seed is None:
                    seed = particles_raw.get("seed")
                seed_i = _coerce_int(seed, 42) if seed is not None else None
                max_att = _coerce_int(packing_raw.get("max_placement_attempts"), 500_000)
                gen = generate_spherical_packing(
                    domain,
                    num_particulas,
                    raio_particula,
                    gap,
                    random_seed=seed_i,
                    max_placement_attempts=max_att,
                )
            else:
                # grade hexagonal filtrada ver packed bed science packing hexagonal
                # passo opcional da grade se ausente o modulo usa dois r mais gap
                step_x_opt = packing_raw.get("step_x")
                step_x_f = (
                    _coerce_float(step_x_opt, 0.0)
                    if step_x_opt is not None
                    else None
                )
                if step_x_f is not None and step_x_f <= 0:
                    step_x_f = None
                gen = generate_hexagonal_packing(
                    domain,
                    num_particulas,
                    raio_particula,
                    gap,
                    step_x=step_x_f,
                )
            t_gen = time.perf_counter() - t0_gen
            centers = gen["centers"]
            # lista de raios repetidos prepara validacao para futuro raio variavel
            radii = [raio_particula] * len(centers)

            # strict true faz o script levantar erro se geometria invalida ou faltar esferas no modo esferico
            strict = _coerce_bool(packing_raw.get("strict_validation"), True)
            # validate configuration percorre pares e checa point in domain de novo
            report_val = validate_configuration(centers, radii, domain, gap)

            poros = estimate_porosity(domain, centers, raio_particula)
            # dicionario serializado no json lateral sem incluir a lista enorme de centros duas vezes
            relatorio = {
                "packing_method": metodo,
                "generation": {k: v for k, v in gen.items() if k != "centers"},
                "generation_wall_time_sec": t_gen,
                "gap_convention": "center_distance >= r1+r2+gap",
                "validation": report_val,
                "porosity_estimate": poros,
                "annulus_void_volume_m3": domain.annulus_volume_void(),
                "n_spheres_placed": len(centers),
                "n_spheres_requested": num_particulas,
            }

            if args.output:
                _salvar_relatorio_packing(Path(args.output), relatorio)

            # falhas de dominio ou par colidente disparam erro opcional
            if report_val["ok"] is not True:
                print("validacao geometrica falhou:", report_val["messages"][:10])
                if strict:
                    raise RuntimeError("strict_validation true e configuracao invalida")

            if metodo == "spherical_packing" and len(centers) < num_particulas:
                msg = f"spherical_packing colocou apenas {len(centers)}/{num_particulas}"
                print("aviso:", msg)
                if strict:
                    raise RuntimeError(msg)

            if metodo == "hexagonal_3d" and len(centers) < num_particulas:
                print(
                    "aviso hexagonal_3d: pontos validos",
                    len(centers),
                    "menor que solicitado",
                    num_particulas,
                )

            # agora materializa no blender o mesmo dominio usado na matematica
            print("criando geometria leito oco e tampas")
            leito = create_hollow_cylinder(raio_ext, raio_int, altura)
            tampa_inferior, tampa_superior = create_caps(
                altura,
                diametro,
                esp_tampa_inf,
                esp_tampa_sup,
                top_has_collision=True,
            )
            print(f"esferas: {len(centers)} malhas mesh compartilhada")
            particulas = create_spheres(centers, raio_particula)

        else:
            # fluxo legado com corpos rigidos para quem ainda quer queda e bake
            print("criando geometria fluxo rigid_body")
            leito = criar_cilindro_oco(altura, diametro, espessura)
            print(f"leito criado: altura={altura}m, diametro={diametro}m")

            tampa_inferior = criar_tampa(
                posicao_z=0,
                diametro=diametro,
                espessura=esp_tampa_inf,
                nome="tampa_inferior",
                tem_colisao=True,
            )
            print("tampa inferior criada com colisao")

            tampa_superior = criar_tampa(
                posicao_z=altura,
                diametro=diametro,
                espessura=esp_tampa_sup,
                nome="tampa_superior",
                tem_colisao=True,
            )
            print("tampa superior com colisao alinhada a inferior leito fechado")

            # criar particulas antigas sorteia posicoes acima do leito para a gravidade puxar
            raio_leito = raio_int
            particulas = criar_particulas(
                quantidade=num_particulas,
                raio_leito=raio_leito,
                altura_leito=altura,
                raio_particula=raio_particula,
            )
            print(f"{len(particulas)} particulas criadas")

            print("configurando fisica")
            configurar_simulacao_fisica()

            print("aplicando fisica ao leito")
            aplicar_fisica(leito, eh_movel=False)

            print("aplicando fisica as tampas")
            aplicar_fisica(tampa_inferior, eh_movel=False)
            aplicar_fisica(tampa_superior, eh_movel=False)

            print("aplicando fisica as particulas")
            for i, particula in enumerate(particulas):
                aplicar_fisica(particula, eh_movel=True)
                if (i + 1) % 20 == 0:
                    print(f"  {i + 1}/{num_particulas} particulas processadas")

            print("fisica aplicada a todas as particulas")

            tempo_sim = _coerce_float(packing_raw.get("max_time"), 20.0)
            gravidade = _coerce_float(packing_raw.get("gravity"), -9.81)
            substeps = _coerce_int(packing_raw.get("substeps"), 10)
            iterations = _coerce_int(packing_raw.get("iterations"), 10)

            print("\nreconfigurando fisica com parametros do arquivo")
            print(f"  gravidade: {gravidade} m/s2")
            print(f"  tempo simulacao: {tempo_sim}s")
            print(f"  substeps: {substeps}")
            print(f"  iterations: {iterations}")

            configurar_simulacao_fisica(
                gravidade=gravidade, substeps=substeps, iterations=iterations
            )

            sep = "=" * 60
            print(f"\n{sep}")
            print("  executando animacao de fisica")
            print(f"{sep}")
            print(f"tempo de simulacao: {tempo_sim}s")
            print("fps: 24")
            print(f"total de frames: {int(tempo_sim * 24)}")
            print("\naguarde particulas caindo no leito")
            print("pode levar minutos conforme quantidade\n")

            executar_simulacao_fisica(tempo_simulacao=tempo_sim, fps=24)

            print(f"\n{sep}")
            print("  congelando posicoes finais")
            print(f"{sep}")
            fazer_bake_fisica(particulas)

            print(f"\n{sep}")
            print("  animacao completa")
            print(f"{sep}")
            print("particulas acomodadas bake aplicado pronto exportacao\n")

        # aplicar thin slice no fim (ambos os ramos ja criaram os meshes)
        aplicar_thin_slice(slice_cfg, altura=altura, raio_ext=raio_ext)

        # ambos os ramos chegam aqui com objetos na cena prontos para salvar
        if args.output:
            export_outputs(args, Path(args.output))
        else:
            print("\naviso caminho saida nao especificado arquivo nao salvo")

        print("\nmodelo 3d gerado com sucesso!")

        
    except Exception as e:
        print(f"\nerro ao gerar modelo: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main_com_parametros()
# =========================================================================================

