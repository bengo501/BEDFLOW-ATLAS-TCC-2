#!/usr/bin/env python3
"""
wizard interativo para criar arquivos .bed
permite ao usuario parametrizar leitos empacotados de duas formas:
1. questionario interativo - usuario responde perguntas passo a passo
2. edicao de template padrao - usuario edita um arquivo template
este wizard gera arquivos .bed que sao compilados pelo antlr
"""

# importar bibliotecas necessarias
import os  # para operacoes do sistema operacional (limpar tela, arquivos)
import sys  # para acessar argumentos e sair do programa
import shutil
import subprocess  # para executar comandos externos (editores, compilador)
import tempfile  # para criar arquivos temporarios
from pathlib import Path  # para trabalhar com caminhos de arquivos
# dict mapeia chave string para valor qualquer
# any aceita qualquer tipo quando o valor e misto
# list sequencia ordenada por exemplo lista de strings do menu
# optional t significa valor do tipo t ou none quando algo e opcional
# tuple par ou tupla fixa por exemplo atalho titulo descricao do menu
from typing import Any, Callable, Dict, List, Optional, Tuple

# pasta onde este ficheiro bed wizard py vive normalmente dsl na raiz do repo
_DSL_DIR = Path(__file__).resolve().parent
# raiz do repositorio um nivel acima de dsl usada para achar scripts blender
_REPO_ROOT = _DSL_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
from bedflow_local_paths import beds_dir, models_3d_dir, simulations_dir
# caminho para packed bed science e leito extracao dentro de scripts blender scripts
_BLENDER_SCRIPTS = _REPO_ROOT / "scripts" / "blender_scripts"
# inserir esse caminho no inicio de sys path para importar packed bed science como pacote
if str(_BLENDER_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_BLENDER_SCRIPTS))
# gerador stl python puro packed bed stl
_PY_MODEL = _REPO_ROOT / "scripts" / "python_modeling"
if str(_PY_MODEL) not in sys.path:
    sys.path.insert(0, str(_PY_MODEL))

# ignorar aviso e402 imports apos codigo sao intencionais porque o path vem antes
from packed_bed_science.packing_modes import (
    PACKING_MODE_CHOICES,
    normalize_packing_mode,
)
# carregar json mesclar packing mode raiz e corrigir json compilado
from wizard_json_loader import (
    export_formats_for_blender,
    json_to_wizard_params,
    load_wizard_json,
    normalize_loaded_dict,
    patch_compiled_json_export,
    patch_compiled_json_slice,
    patch_compiled_json_metadata,
    patch_compiled_json_packing,
    resolve_repo_path,
)
# listar nomes de templates json e carregar um template por nome
from wizard_quick_tests import run as wizard_quick_tests_run
from wizard_template_engine import list_template_names, load_template
from wizard_terminal_ui import (
    make_terminal_ui,
    prompt_toolkit_available,
    rich_available,
)

class _WizardCancelled(Exception):
    """sinal interno: o utilizador pediu para cancelar e voltar ao menu."""


# fluxo geral do wizard em memoria
# self params guarda bed particles lids packing export cfd como dicts aninhados
# generate bed content transforma self params em texto linguagem bed
# save bed file grava esse texto no disco
# verify and compile chama o antlr que produz um json ao lado do bed
# patch compiled json packing export recoloca gap e formats que a gramatica bed nao suporta
# run blender with json path chama o executavel blender com leito extracao py
# modos spherical packing e hexagonal 3d no blender usam packed bed science sem rigid body
# modo rigid body usa fisica antiga com queda e nao passa pela validacao fechada dos modos cientificos

class BedWizard:
    """classe principal do wizard para criacao de arquivos .bed"""

    _I18N: Dict[str, Dict[str, str]] = {
        "pt": {
            "app.title": "wizard de parametrizacao",
            "app.subtitle": "leitos empacotados — arquivos .bed / antlr / blender / openfoam",
            "menu.title.main": "opcoes",
            "menu.title.start": "comecar",
            "menu.main.start.title": "comecar",
            "menu.main.start.desc": "questionario, templates, testes rapidos, geracao 3d no blender ou pipeline completo",
            "menu.main.view3d.title": "visualizacao 3d",
            "menu.main.view3d.desc": "listar malhas geradas; ver no browser (three.js), open3d ou blender",
            "menu.main.help.title": "ajuda",
            "menu.main.help.desc": "resumo dos parametros do ficheiro .bed por secao",
            "menu.main.docs.title": "documentacao",
            "menu.main.docs.desc": "guia do projeto neste terminal (texto extraido do html)",
            "menu.main.lang.title": "idioma",
            "menu.main.lang.desc": "trocar portugues/ingles",
            "menu.main.exit.title": "sair",
            "menu.main.exit.desc": "encerrar o wizard",
            "menu.start.smart.title": "assistente inteligente",
            "menu.start.smart.desc": "perguntas curtas para guiar ao .bed, modelo 3d no blender ou pipeline openfoam",
            "menu.start.q.title": "questionario interativo",
            "menu.start.q.desc": "passo a passo; gera .bed; cfd opcional; export configuravel",
            "menu.start.tpl.title": "templates, editor e testes rapidos",
            "menu.start.tpl.desc": "json em dsl/wizard_templates, editor .bed classico, ou fluxo guiado com ficheiros existentes",
            "menu.start.blender.title": "geracao 3d (blender)",
            "menu.start.blender.desc": "sem cfd; export como no questionario; escolhe como abrir o blender no fim",
            "menu.start.pipe.title": "pipeline completo (avancado)",
            "menu.start.pipe.desc": "bed + blender + caso openfoam + simulacao no wsl; longo; requisitos elevados",
            "menu.start.back.title": "voltar",
            "menu.start.back.desc": "regressa ao menu principal",
            "prompt.main.choice": "opcao (1-6): ",
            "prompt.start.choice": "opcao (0-5): ",
            "lang.header": "idioma",
            "lang.subtitle": "trocar idioma do wizard",
            "lang.current": "idioma atual",
            "lang.choose": "escolha o idioma",
            "lang.pt": "portugues",
            "lang.en": "ingles",
            "lang.ok": "idioma atualizado",
            "view3d.title": "visualizacao 3d",
            "view3d.subtitle": "malhas geradas pelo projeto (python, blender, pipeline)",
            "view3d.crumb": "visualizacao 3d",
            "view3d.search": "pesquisar (vazio=tudo, l=lista, c=menu principal): ",
            "view3d.scan_hint": "origem da lista: scan em local_data/models_3d (prioridade), depois aux, simulations, generated/* e ficheiros *.stl/*.obj/*.blend na raiz do repo (ver bedflow_local_paths.scan_project_mesh_files).",
            "view3d.table_title": "modelos",
            "view3d.pick": "numero do modelo (0=rever lista, c=menu principal): ",
            "view3d.preview": "resumo",
            "view3d.choose_dest": "onde visualizar",
            "view3d.opt.web": "navegador (three.js no frontend)",
            "view3d.opt.desktop": "visualizador desktop (open3d: stl/obj/ply)",
            "view3d.opt.blender": "abrir no blender",
            "view3d.opt.back": "voltar a lista",
        },
        "en": {
            "app.title": "parameter wizard",
            "app.subtitle": "packed beds — .bed / antlr / blender / openfoam",
            "menu.title.main": "options",
            "menu.title.start": "start",
            "menu.main.start.title": "start",
            "menu.main.start.desc": "questionnaire, templates, quick tests, 3d generation in blender or full pipeline",
            "menu.main.view3d.title": "3d visualization",
            "menu.main.view3d.desc": "list generated meshes; open in browser (three.js), open3d or blender",
            "menu.main.help.title": "help",
            "menu.main.help.desc": "summary of .bed parameters by section",
            "menu.main.docs.title": "documentation",
            "menu.main.docs.desc": "project guide in this terminal (text extracted from html)",
            "menu.main.lang.title": "language",
            "menu.main.lang.desc": "toggle portuguese/english",
            "menu.main.exit.title": "exit",
            "menu.main.exit.desc": "close the wizard",
            "menu.start.smart.title": "smart assistant",
            "menu.start.smart.desc": "short questions to guide to .bed, 3d blender model, or openfoam pipeline",
            "menu.start.q.title": "interactive questionnaire",
            "menu.start.q.desc": "step-by-step; generates .bed; optional cfd; configurable export",
            "menu.start.tpl.title": "templates, editor and quick tests",
            "menu.start.tpl.desc": "json templates, classic .bed editor, or guided runs with existing files",
            "menu.start.blender.title": "3d generation (blender)",
            "menu.start.blender.desc": "no cfd; export like questionnaire; choose blender open policy at end",
            "menu.start.pipe.title": "full pipeline (advanced)",
            "menu.start.pipe.desc": "bed + blender + openfoam case + wsl simulation; long; heavy requirements",
            "menu.start.back.title": "back",
            "menu.start.back.desc": "return to main menu",
            "prompt.main.choice": "choice (1-6): ",
            "prompt.start.choice": "choice (0-5): ",
            "lang.header": "language",
            "lang.subtitle": "change wizard language",
            "lang.current": "current language",
            "lang.choose": "choose language",
            "lang.pt": "portuguese",
            "lang.en": "english",
            "lang.ok": "language updated",
            "view3d.title": "3d visualization",
            "view3d.subtitle": "meshes from python, blender or full pipeline",
            "view3d.crumb": "3d view",
            "view3d.search": "search (empty=all, l=list, c=main menu): ",
            "view3d.scan_hint": "list source: scan local_data/models_3d first, then aux, simulations, generated/* and mesh files at repo root (see bedflow_local_paths.scan_project_mesh_files).",
            "view3d.table_title": "models",
            "view3d.pick": "model number (0=refresh list, c=main menu): ",
            "view3d.preview": "summary",
            "view3d.choose_dest": "open in",
            "view3d.opt.web": "browser (three.js)",
            "view3d.opt.desktop": "desktop viewer (open3d: stl/obj/ply)",
            "view3d.opt.blender": "open in blender",
            "view3d.opt.back": "back to list",
        },
    }

    def _t(self, key: str, default_pt: str = "") -> str:
        d = self._I18N.get(getattr(self, "lang", "pt"), {})
        if key in d:
            return d[key]
        # fallback pt se existir, senao default_pt
        return self._I18N.get("pt", {}).get(key, default_pt)

    def _main_menu_rows(self) -> List[Tuple[str, str, str]]:
        return [
            ("1", self._t("menu.main.start.title", "comecar"), self._t("menu.main.start.desc", "")),
            ("2", self._t("menu.main.view3d.title", "visualizacao 3d"), self._t("menu.main.view3d.desc", "")),
            ("3", self._t("menu.main.help.title", "ajuda"), self._t("menu.main.help.desc", "")),
            ("4", self._t("menu.main.docs.title", "documentacao"), self._t("menu.main.docs.desc", "")),
            ("5", self._t("menu.main.lang.title", "idioma"), self._t("menu.main.lang.desc", "")),
            ("6", self._t("menu.main.exit.title", "sair"), self._t("menu.main.exit.desc", "")),
        ]

    def _start_menu_rows(self) -> List[Tuple[str, str, str]]:
        return [
            ("1", self._t("menu.start.smart.title", ""), self._t("menu.start.smart.desc", "")),
            ("2", self._t("menu.start.q.title", ""), self._t("menu.start.q.desc", "")),
            ("3", self._t("menu.start.tpl.title", ""), self._t("menu.start.tpl.desc", "")),
            ("4", self._t("menu.start.blender.title", ""), self._t("menu.start.blender.desc", "")),
            ("5", self._t("menu.start.pipe.title", ""), self._t("menu.start.pipe.desc", "")),
            ("0", self._t("menu.start.back.title", "voltar"), self._t("menu.start.back.desc", "")),
        ]

    # valores iniciais do questionario (para marcar [alt] na lista de revisao)
    _QUESTIONNAIRE_DEFAULTS_FLAT: Dict[str, str] = {
        "bed.diameter": "0.05",
        "bed.height": "0.1",
        "bed.wall_thickness": "0.002",
        "bed.clearance": "0.01",
        "bed.material": "steel",
        "bed.roughness": "0.0",
        "lids.top_type": "flat",
        "lids.bottom_type": "flat",
        "lids.top_thickness": "0.003",
        "lids.bottom_thickness": "0.003",
        "lids.seal_clearance": "0.001",
        "particles.kind": "sphere",
        "particles.diameter": "0.005",
        "particles.count": "100",
        "particles.target_porosity": "0.4",
        "particles.density": "2500.0",
        "particles.mass": "0.0",
        "particles.restitution": "0.3",
        "particles.friction": "0.5",
        "particles.rolling_friction": "0.1",
        "particles.linear_damping": "0.1",
        "particles.angular_damping": "0.1",
        "particles.seed": "42",
        "packing.method": "rigid_body",
        "packing.gravity": "-9.81",
        "packing.substeps": "10",
        "packing.iterations": "10",
        "packing.damping": "0.1",
        "packing.rest_velocity": "0.01",
        "packing.max_time": "5.0",
        "packing.collision_margin": "0.001",
        "packing.gap": "0.0001",
        "packing.random_seed": "42",
        "packing.max_placement_attempts": "500000",
        "packing.strict_validation": "true",
        "export.formats": "stl_binary,obj",
        "export.units": "m",
        "export.scale": "1.0",
        "export.wall_mode": "surface",
        "export.fluid_mode": "none",
        "export.manifold_check": "true",
        "export.merge_distance": "0.001",
        "cfd.regime": "laminar",
        "cfd.inlet_velocity": "0.1",
        "cfd.fluid_density": "1.225",
        "cfd.fluid_viscosity": "1.8e-5",
        "cfd.max_iterations": "1000",
        "cfd.convergence_criteria": "1e-6",
        "cfd.write_fields": "false",
    }
    
    def __init__(self):
        """inicializar wizard com parametros vazios"""
        self.params = {}  # dicionario para armazenar parametros do leito
        self.output_file = None  # nome do arquivo de saida
        self.ui = make_terminal_ui()
        self._cancel_enabled = True
        # true apos carregar .bed e o utilizador pedir saltar o questionario
        self.skip_questionnaire_after_load = False
        self.lang = "pt"
        
        # dicionario com informacoes de ajuda para cada parametro
        self.param_help = {
            # secao bed
            'bed.diameter': {
                'desc': 'diametro interno do leito cilindrico',
                'min': 0.01, 'max': 2.0, 'unit': 'm',
                'exemplo': 'leito de 5cm = 0.05m'
            },
            'bed.height': {
                'desc': 'altura total do leito cilindrico',
                'min': 0.01, 'max': 5.0, 'unit': 'm',
                'exemplo': 'leito de 10cm = 0.1m'
            },
            'bed.wall_thickness': {
                'desc': 'espessura da parede do cilindro',
                'min': 0.0001, 'max': 0.1, 'unit': 'm',
                'exemplo': 'parede de 2mm = 0.002m'
            },
            'bed.clearance': {
                'desc': 'espaco livre acima das particulas',
                'min': 0.0, 'max': 1.0, 'unit': 'm',
                'exemplo': 'folga de 1cm = 0.01m'
            },
            'bed.material': {
                'desc': 'material da parede do leito',
                'exemplo': 'steel, aluminum, glass, plastic'
            },
            'bed.roughness': {
                'desc': 'rugosidade da superficie interna',
                'min': 0.0, 'max': 0.01, 'unit': 'm',
                'exemplo': 'superficie lisa = 0.0m'
            },
            # secao lids
            'lids.top_type': {
                'desc': 'formato da tampa superior',
                'exemplo': 'flat (plana), hemispherical (semiesferica), none (sem tampa)'
            },
            'lids.bottom_type': {
                'desc': 'formato da tampa inferior',
                'exemplo': 'flat (plana), hemispherical (semiesferica), none (sem tampa)'
            },
            'lids.top_thickness': {
                'desc': 'espessura da tampa superior',
                'min': 0.0001, 'max': 0.1, 'unit': 'm',
                'exemplo': 'tampa de 3mm = 0.003m'
            },
            'lids.bottom_thickness': {
                'desc': 'espessura da tampa inferior',
                'min': 0.0001, 'max': 0.1, 'unit': 'm',
                'exemplo': 'tampa de 3mm = 0.003m'
            },
            'lids.seal_clearance': {
                'desc': 'folga entre tampa e parede',
                'min': 0.0, 'max': 0.01, 'unit': 'm',
                'exemplo': 'folga de 1mm = 0.001m'
            },
            # secao particles
            'particles.kind': {
                'desc': 'formato geometrico das particulas',
                'exemplo': 'sphere (esfera), cube (cubo), cylinder (cilindro)'
            },
            'particles.diameter': {
                'desc': 'diametro das particulas esfericas',
                'min': 0.0001, 'max': 0.5, 'unit': 'm',
                'exemplo': 'particula de 5mm = 0.005m'
            },
            'particles.count': {
                'desc': 'quantidade total de particulas',
                'min': 1, 'max': 10000, 'unit': '',
                'exemplo': '100 particulas = empacotamento rapido'
            },
            'particles.target_porosity': {
                'desc': 'porosidade desejada (0-1)',
                'min': 0.1, 'max': 0.9, 'unit': '',
                'exemplo': '0.4 = 40% de vazios'
            },
            'particles.density': {
                'desc': 'densidade do material das particulas',
                'min': 100.0, 'max': 20000.0, 'unit': 'kg/m3',
                'exemplo': 'vidro = 2500 kg/m3, aco = 7850 kg/m3'
            },
            'particles.mass': {
                'desc': 'massa individual de cada particula',
                'min': 0.0, 'max': 1000.0, 'unit': 'g',
                'exemplo': '0.0 = calculado automaticamente'
            },
            'particles.restitution': {
                'desc': 'coeficiente de restituicao (quique)',
                'min': 0.0, 'max': 1.0, 'unit': '',
                'exemplo': '0.0 = sem quique, 1.0 = quique total'
            },
            'particles.friction': {
                'desc': 'coeficiente de atrito entre particulas',
                'min': 0.0, 'max': 1.0, 'unit': '',
                'exemplo': '0.5 = atrito moderado'
            },
            'particles.rolling_friction': {
                'desc': 'resistencia ao rolamento',
                'min': 0.0, 'max': 1.0, 'unit': '',
                'exemplo': '0.1 = rolamento facil'
            },
            'particles.linear_damping': {
                'desc': 'amortecimento do movimento linear',
                'min': 0.0, 'max': 1.0, 'unit': '',
                'exemplo': '0.1 = amortecimento leve'
            },
            'particles.angular_damping': {
                'desc': 'amortecimento da rotacao',
                'min': 0.0, 'max': 1.0, 'unit': '',
                'exemplo': '0.1 = rotacao com leve resistencia'
            },
            'particles.seed': {
                'desc': 'semente para geracao aleatoria',
                'min': 0, 'max': 99999, 'unit': '',
                'exemplo': '42 = resultado reproduzivel'
            },
            # secao packing
            'packing.method': {
                'desc': 'metodo de simulacao do empacotamento',
                'exemplo': 'rigid_body (corpo rigido com fisica)'
            },
            'packing.gravity': {
                'desc': 'aceleracao da gravidade',
                'min': -50.0, 'max': 50.0, 'unit': 'm/s2',
                'exemplo': 'terra = -9.81 m/s2, lua = -1.62 m/s2'
            },
            'packing.substeps': {
                'desc': 'subdivisoes de cada frame',
                'min': 1, 'max': 100, 'unit': '',
                'exemplo': '10 = boa precisao, 50 = alta precisao'
            },
            'packing.iterations': {
                'desc': 'iteracoes do solver por substep',
                'min': 1, 'max': 100, 'unit': '',
                'exemplo': '10 = boa convergencia'
            },
            'packing.damping': {
                'desc': 'amortecimento global da simulacao',
                'min': 0.0, 'max': 1.0, 'unit': '',
                'exemplo': '0.1 = sistema estabiliza rapido'
            },
            'packing.rest_velocity': {
                'desc': 'velocidade considerada repouso',
                'min': 0.0001, 'max': 1.0, 'unit': 'm/s',
                'exemplo': '0.01 = particula parada se < 1cm/s'
            },
            'packing.max_time': {
                'desc': 'tempo maximo de simulacao',
                'min': 0.1, 'max': 60.0, 'unit': 's',
                'exemplo': '5.0s = suficiente para empacotamento'
            },
            'packing.collision_margin': {
                'desc': 'margem de deteccao de colisao',
                'min': 0.00001, 'max': 0.01, 'unit': 'm',
                'exemplo': '0.001m = 1mm de margem'
            },
            'packing.gap': {
                'desc': 'folga minima entre superficies das esferas (modos cientificos)',
                'min': 0.0, 'max': 0.01, 'unit': 'm',
                'exemplo': '0.0001m = 0.1 mm entre esferas'
            },
            'packing.random_seed': {
                'desc': 'seed para spherical_packing',
                'min': 0, 'max': 999999, 'unit': '',
                'exemplo': '7 = colocacao reproduzivel'
            },
            'packing.max_placement_attempts': {
                'desc': 'tentativas max. de colocacao aleatoria (spherical_packing)',
                'min': 1000, 'max': 5000000, 'unit': '',
                'exemplo': '200000'
            },
            'packing.strict_validation': {
                'desc': 'se true, falha se geometria invalida ou faltam esferas',
                'exemplo': 'true recomendado para cfd'
            },
            'packing.step_x': {
                'desc': 'passo horizontal da grade hexagonal (vazio = 2*r+gap)',
                'min': 0.00001, 'max': 0.5, 'unit': 'm',
                'exemplo': 'deixe vazio para automatico'
            },
            # secao export
            'export.formats': {
                'desc': 'formatos de arquivo para exportar',
                'exemplo': 'stl_binary, stl_ascii, obj, blend'
            },
            'export.units': {
                'desc': 'unidade de medida na exportacao',
                'exemplo': 'm (metros), cm (centimetros), mm (milimetros)'
            },
            'export.scale': {
                'desc': 'fator de escala na exportacao',
                'min': 0.001, 'max': 1000.0, 'unit': '',
                'exemplo': '1.0 = tamanho original, 1000 = mm para m'
            },
            'export.wall_mode': {
                'desc': 'modo de exportacao da parede',
                'exemplo': 'surface (superficie), solid (solido)'
            },
            'export.fluid_mode': {
                'desc': 'modo de exportacao do fluido',
                'exemplo': 'none (sem fluido), cavity (com cavidade)'
            },
            'export.manifold_check': {
                'desc': 'verificar se malha e manifold',
                'exemplo': 'true = verifica integridade da malha'
            },
            'export.merge_distance': {
                'desc': 'distancia para mesclar vertices',
                'min': 0.0, 'max': 0.1, 'unit': 'm',
                'exemplo': '0.001m = mescla vertices proximos'
            },
            # secao cfd
            'cfd.regime': {
                'desc': 'regime de escoamento do fluido',
                'exemplo': 'laminar (baixa velocidade), turbulent_rans (alta velocidade)'
            },
            'cfd.inlet_velocity': {
                'desc': 'velocidade do fluido na entrada',
                'min': 0.001, 'max': 100.0, 'unit': 'm/s',
                'exemplo': '0.1 m/s = escoamento lento'
            },
            'cfd.fluid_density': {
                'desc': 'densidade do fluido',
                'min': 0.1, 'max': 2000.0, 'unit': 'kg/m3',
                'exemplo': 'ar = 1.225 kg/m3, agua = 1000 kg/m3'
            },
            'cfd.fluid_viscosity': {
                'desc': 'viscosidade dinamica do fluido',
                'min': 1e-6, 'max': 1.0, 'unit': 'Pa.s',
                'exemplo': 'ar = 1.8e-5 Pa.s, agua = 1e-3 Pa.s'
            },
            'cfd.max_iterations': {
                'desc': 'numero maximo de iteracoes',
                'min': 10, 'max': 100000, 'unit': '',
                'exemplo': '1000 = simulacao rapida, 10000 = precisa'
            },
            'cfd.convergence_criteria': {
                'desc': 'criterio de convergencia (residuo)',
                'min': 1e-10, 'max': 1e-2, 'unit': '',
                'exemplo': '1e-6 = convergencia boa'
            },
            'cfd.write_fields': {
                'desc': 'salvar campos de velocidade/pressao',
                'exemplo': 'true = salva resultados, false = nao salva'
            }
        }
        
    def clear_screen(self):
        """limpar tela do terminal para melhor visualizacao"""
        self.ui.clear()
    
    def print_header(self, title: str, subtitle: str = ""):
        """imprimir cabecalho formatado com titulo"""
        self.ui.header(title, subtitle)
    
    def print_section(self, title: str):
        """imprimir titulo de secao formatado"""
        self.ui.section(title)
    
    def _hint_controles_entrada(self) -> None:
        """texto curto reutilizado nos fluxos com perguntas."""
        extra = ""
        if prompt_toolkit_available():
            extra = (
                " linha de comando com prompt_toolkit: setas, ctrl+r no historico, tab completa "
                "? * n p q s sim nao."
            )
        extra = (
            extra
            + " c = cancelar / voltar (nos menus com lista numerada tambem; "
            "interrompe o fluxo e sobe ate ao menu onde o cancelamento esta tratado)."
        )
        self.ui.hint(
            "controles: enter aceita o padrao entre [colchetes]; ? ajuda contextual; "
            "* abre a lista de parametros ja definidos para rever ou editar (depois continua aqui)."
            + extra
        )

    def _maybe_cancel(self, raw: str) -> None:
        """se o wizard estiver em modo interativo, permite cancelar com c/cancel."""
        if not self._cancel_enabled:
            return
        tok = (raw or "").strip().lower()
        if tok in ("c", "cancel", "cancelar", "voltar", "back"):
            raise _WizardCancelled()

    def _flatten_params_for_defaults(self) -> Dict[str, str]:
        # devolve um mapa "secao.campo" -> string para usar como default nas perguntas
        out: Dict[str, str] = {}
        for sec, d in (self.params or {}).items():
            if not isinstance(d, dict):
                continue
            for k, v in d.items():
                key = f"{sec}.{k}"
                if isinstance(v, bool):
                    out[key] = "true" if v else "false"
                elif isinstance(v, (int, float)):
                    out[key] = str(v)
                elif isinstance(v, list):
                    out[key] = ",".join(str(x) for x in v)
                elif v is None:
                    continue
                else:
                    out[key] = str(v)
        return out

    def _default_from_loaded(self, key: str, fallback: str) -> str:
        # se ja temos params carregados, usa-os como default; caso contrario usa fallback
        flat = self._flatten_params_for_defaults()
        got = flat.get(key)
        return got if got not in (None, "") else fallback

    def _default_bool_from_loaded(self, key: str, fallback: bool) -> bool:
        flat = self._flatten_params_for_defaults()
        v = flat.get(key)
        if v is None or str(v).strip() == "":
            return fallback
        return str(v).strip().lower() in ("true", "1", "sim", "yes", "s")

    def _default_choice_index(
        self,
        options: List[str],
        param_key: str,
        fallback: int = 0,
    ) -> int:
        flat = self._flatten_params_for_defaults()
        val = flat.get(param_key)
        if val is None or str(val).strip() == "":
            return fallback
        opts = list(options)
        if param_key == "packing.method":
            needle = normalize_packing_mode(val)
        else:
            needle = str(val).strip().lower()
        try:
            return opts.index(needle)
        except ValueError:
            return fallback

    def _load_params_from_bed_path(self, bed_path: Path) -> bool:
        # compila .bed -> .json e preenche self.params com json_to_wizard_params
        try:
            bed_path = Path(bed_path).resolve()
            if not bed_path.exists():
                self.ui.err(f"ficheiro nao encontrado: {bed_path}")
                return False
            self.output_file = str(bed_path)
            if not self.verify_and_compile():
                self.ui.err("nao foi possivel compilar o .bed fornecido")
                return False
            jpath = Path(str(bed_path.resolve()) + ".json")
            if not jpath.exists():
                self.ui.err(f"json nao encontrado apos compilar: {jpath}")
                return False
            data = load_wizard_json(jpath)
            normalize_loaded_dict(data)
            self.params = json_to_wizard_params(data)
            return True
        except Exception as e:
            self.ui.err(f"falha ao carregar .bed: {e}")
            return False

    def _discover_bed_files(self) -> List[Path]:
        # procura .bed em local_data/beds, cwd, raiz do repo e pasta dsl
        beds: List[Path] = []
        for base in (
            beds_dir(),
            Path.cwd(),
            Path(__file__).resolve().parents[1],
            Path(__file__).resolve().parent,
        ):
            try:
                beds.extend(base.glob("*.bed"))
            except Exception:
                pass
        uniq: Dict[str, Path] = {}
        for p in beds:
            try:
                r = p.resolve()
                uniq[str(r)] = r
            except Exception:
                continue
        return sorted(uniq.values(), key=lambda x: (x.name.lower(), str(x).lower()))

    def _print_bed_files_list(self, beds: List[Path]) -> None:
        if not beds:
            self.ui.warn(
                "nenhum .bed encontrado (pastas: local_data/beds, cwd, raiz do repo, dsl)"
            )
            return
        self.ui.println("ficheiros .bed encontrados (use o numero ou o caminho):")
        for i, p in enumerate(beds, start=1):
            self.ui.muted(f"  {i:3}  {p}")

    def _maybe_load_existing_bed(self, *, caption: str) -> None:
        self.skip_questionnaire_after_load = False
        # pergunta ao utilizador se quer carregar um .bed para pre-preencher o questionario
        self.ui.hint("opcional: carregar um .bed existente para pre-preencher as perguntas")
        if not self.get_boolean(f"carregar .bed existente neste modo ({caption})?", default=False):
            return
        beds = self._discover_bed_files()
        if self.get_boolean("mostrar lista numerada de ficheiros .bed encontrados?", default=True):
            self._print_bed_files_list(beds)
        self.ui.muted(
            "dica: l ou lista = rever lista; numero ou caminho = escolher; "
            "n ou enter vazio = continuar sem carregar .bed; "
            "c = voltar ao menu (cancela o fluxo atual)"
        )
        bed_path: Optional[Path] = None
        while True:
            raw = self.ui.ask_line(
                "caminho .bed (numero, l=lista, n/vazio sem carregar, c=menu): "
            ).strip()
            if not raw:
                return
            low = raw.lower()
            if low in ("c", "cancel", "cancelar", "voltar", "back"):
                raise _WizardCancelled()
            if low in (
                "n",
                "nao",
                "não",
                "nao carregar",
                "sem",
                "pular",
                "skip",
                "no",
            ):
                return
            if low in ("l", "lista"):
                self._print_bed_files_list(beds)
                continue
            candidate: Optional[Path] = None
            if raw.isdigit() and beds:
                idx = int(raw) - 1
                if 0 <= idx < len(beds):
                    candidate = beds[idx]
            if candidate is None:
                try:
                    candidate = resolve_repo_path(raw, base=Path.cwd())
                except Exception:
                    candidate = None
            if candidate is None or not candidate.exists():
                self.ui.warn(
                    "ficheiro nao encontrado ou indice invalido; tente de novo ou l para lista"
                )
                continue
            bed_path = candidate
            break
        if self._load_params_from_bed_path(bed_path):
            self.ui.ok(f"carregado: {bed_path.name}")
            self.ui.muted(
                "os valores do ficheiro aparecem como padrao entre [colchetes]; "
                "enter em cada pergunta mantem o que foi carregado."
            )
            if self.get_boolean(
                "saltar o questionario e manter só o carregado "
                "(nome de ficheiro e confirmacao em seguida)?",
                default=False,
            ):
                self.skip_questionnaire_after_load = True
                self.ui.muted(
                    "fluxo curto: parametros iguais ao ficheiro; "
                    "exportacao, fatia e cfd nao serao repedidos nesta sessao."
                )
        else:
            self.ui.warn("nao foi possivel carregar; a seguir sem carregar")

    def _hint_fluxo_questionario(self) -> None:
        self.ui.muted(
            "ordem: geometria do leito → tampas → particulas → empacotamento → export → "
            "cfd (opcional) → nome do ficheiro → confirmacao."
        )

    def _hint_fluxo_template(self) -> None:
        self.ui.muted(
            "ordem: escolher origem (json pronto ou .bed em editor) → nome de saida → "
            "gravar/compilar (e stl python se o template pedir)."
        )

    def _hint_fluxo_blender(self) -> None:
        self.ui.muted(
            "ordem: leito → tampas → particulas → empacotamento → export → nome .bed → "
            "como abrir o blender → confirmacao e geracao."
        )

    def show_param_help(self, param_key: str):
        """mostrar ajuda detalhada sobre um parametro"""
        if param_key in self.param_help:
            info = self.param_help[param_key]
            lines = [f"descricao: {info['desc']}"]
            if 'min' in info and 'max' in info:
                unit = info.get('unit', '')
                lines.append(f"range: minimo {info['min']}{unit} — maximo {info['max']}{unit}")
            if 'exemplo' in info:
                lines.append(f"exemplo: {info['exemplo']}")
            self.ui.param_help(lines)
    
    def get_input(
        self,
        prompt: str,
        default: str = "",
        required: bool = True,
        param_key: str = "",
    ) -> str:
        """obter entrada de texto do usuario com validacao (? ajuda, * revisao)"""
        while True:
            suf = " (? * revisao)"
            if default:
                full_prompt = f"{prompt} [{default}]{suf}: "
            else:
                full_prompt = f"{prompt}{suf}: "
            value = self.ui.ask_line(full_prompt, default=default or "")
            self._maybe_cancel(value)
            if value.strip() == "?" and param_key:
                if param_key in self.param_help:
                    self.show_param_help(param_key)
                else:
                    self.ui.hint("ajuda nao disponivel para este campo")
                continue
            if value.strip() == "?":
                self.ui.hint("ajuda nao disponivel para este campo")
                continue
            if value.strip() == "*":
                self._param_review_and_edit_menu()
                continue
            if not value.strip() and default:
                return default
            value = value.strip()
            if value:
                return value
            elif default and not required:
                return default
            elif not required:
                return ""
            else:
                self.ui.warn("campo obrigatorio!")
    
    def get_number_input(self, prompt: str, default: str = "", unit: str = "", required: bool = True, param_key: str = "") -> str:
        """obter entrada numerica com unidade e validacao (? ajuda, * revisao)"""
        min_val = None
        max_val = None
        if param_key and param_key in self.param_help:
            info = self.param_help[param_key]
            min_val = info.get('min')
            max_val = info.get('max')
        
        while True:
            if default:
                full_prompt = (
                    f"{prompt} [{default} {unit}] (? ajuda, * lista; setas ajusta): "
                )
            else:
                full_prompt = f"{prompt} ({unit}) (? ajuda, * lista; setas ajusta): "

            # se prompt_toolkit estiver ativo, oferece ajuste com setas
            ask_num = getattr(self.ui, "ask_number", None)
            if callable(ask_num):
                value = ask_num(
                    full_prompt,
                    default=default or "",
                    step=0.1 if unit in ("m", "mm") else 1.0,
                    min_val=min_val,
                    max_val=max_val,
                )
            else:
                value = self.ui.ask_line(full_prompt, default=default or "")
            self._maybe_cancel(value)
            if value.strip() == '?':
                if param_key and param_key in self.param_help:
                    self.show_param_help(param_key)
                else:
                    self.ui.hint("ajuda nao disponivel para este parametro")
                continue
            if value.strip() == '*':
                self._param_review_and_edit_menu()
                continue
            if not value.strip() and default:
                return default
            
            # remover espacos para validacao
            value = value.strip()
            
            # validar entrada
            if value:
                try:
                    # tentar converter para float para validar se e numero
                    num_value = float(value)
                    
                    # validar limites se especificados
                    if min_val is not None and num_value < min_val:
                        self.ui.warn(f"valor muito baixo! minimo: {min_val}{unit}")
                        continue
                    if max_val is not None and num_value > max_val:
                        self.ui.warn(f"valor muito alto! maximo: {max_val}{unit}")
                        continue
                    
                    return value  # retornar valor se valido
                except ValueError:
                    self.ui.warn("digite um numero valido!")
                    continue
            elif default and not required:
                return default  # retornar padrao se nao obrigatorio
            elif not required:
                return ""  # retornar vazio se nao obrigatorio
            else:
                self.ui.warn("campo obrigatorio!")
    
    def get_choice(
        self,
        prompt: str,
        options: List[str],
        default: int = 0,
        param_key: str = "",
    ) -> str:
        """obter escolha do usuario (? ajuda, * revisao)"""
        def _help() -> None:
            if param_key and param_key in self.param_help:
                self.show_param_help(param_key)
            else:
                self.ui.hint("opcoes validas: " + ", ".join(options))
        def _cancel() -> None:
            raise _WizardCancelled()
        return self.ui.pick_from_list(
            prompt,
            options,
            default,
            help_callback=_help,
            review_callback=self._param_review_and_edit_menu,
            cancel_callback=_cancel,
        )
    
    def get_boolean(self, prompt: str, default: bool = True) -> bool:
        """obter entrada booleana (sim/nao) do usuario"""
        def _cancel() -> None:
            raise _WizardCancelled()

        return self.ui.confirm(
            prompt,
            default,
            cancel_callback=_cancel,
        )
    
    def get_list_input(
        self, prompt: str, separator: str = ",", param_key: str = ""
    ) -> List[str]:
        """obter entrada de lista separada por delimitador (? * revisao)"""
        while True:
            value = self.ui.ask_line(
                f"{prompt} (separado por '{separator}') (? * lista): "
            ).strip()
            self._maybe_cancel(value)
            if value == "?":
                if param_key and param_key in self.param_help:
                    self.show_param_help(param_key)
                else:
                    self.ui.hint("liste valores separados por virgula, ex: stl_binary, obj")
                continue
            if value == "*":
                self._param_review_and_edit_menu()
                continue
        if value:
            return [item.strip() for item in value.split(separator)]
            return []

    def _is_questionnaire_value_changed(self, path: str, val: Any) -> bool:
        if path not in self._QUESTIONNAIRE_DEFAULTS_FLAT:
            return True
        ds = self._QUESTIONNAIRE_DEFAULTS_FLAT[path]
        if path == "export.formats" and isinstance(val, list):
            cur = ",".join(str(x).strip() for x in val)
            return (
                cur.replace(" ", "").lower()
                != ds.replace(" ", "").lower()
            )
        if isinstance(val, bool):
            return val != (ds.lower() in ("true", "1", "sim", "yes"))
        try:
            return float(val) != float(ds)
        except (TypeError, ValueError):
            return str(val).strip().lower() != ds.strip().lower()

    def _iter_filled_param_paths(self) -> List[Tuple[str, Any]]:
        out: List[Tuple[str, Any]] = []

        def walk(d: Any, prefix: str) -> None:
            if not isinstance(d, dict):
                return
            for k, v in d.items():
                p = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    walk(v, p)
                else:
                    out.append((p, v))

        walk(self.params, "")
        return sorted(out, key=lambda x: x[0])

    def _param_review_and_edit_menu(self) -> None:
        _rev = [
            x
            for x in self._iter_filled_param_paths()
            if x[0].count(".") == 1
        ]
        if not _rev:
            self.ui.warn("ainda nao ha parametros definidos nesta sessao")
            self.ui.pause("enter...")
            return
        while True:
            self.clear_screen()
            self.print_header("rever parametros", "0 = voltar ao questionario")
            self.ui.breadcrumbs("wizard", "revisao")
            items = [
                x
                for x in self._iter_filled_param_paths()
                if x[0].count(".") == 1
            ]
            if not items:
                self.ui.warn("lista vazia")
                self.ui.pause("enter...")
                return
            for i, (path, val) in enumerate(items, start=1):
                ch = self._is_questionnaire_value_changed(path, val)
                tag = "alt" if ch else "pad"
                if isinstance(val, list):
                    disp = ", ".join(str(x) for x in val)
                else:
                    disp = str(val)
                if len(disp) > 56:
                    disp = disp[:53] + "..."
                self.ui.muted(f"  {i:2} [{tag}] {path} = {disp}")
            self.ui.println()
            self.ui.hint("digite o numero para editar, ou 0 / enter para continuar o fluxo")
            raw = self.ui.ask_line("opcao: ").strip()
            self._maybe_cancel(raw)
            if not raw or raw == "0":
                break
            try:
                n = int(raw)
            except ValueError:
                self.ui.warn("numero invalido")
                self.ui.pause("enter...")
                continue
            if 1 <= n <= len(items):
                self._edit_single_questionnaire_param(items[n - 1][0])
            else:
                self.ui.warn("fora da lista")
                self.ui.pause("enter...")

    def _edit_single_questionnaire_param(self, path: str) -> None:
        """redefine um campo ja existente em self.params (questionario)."""
        parts = path.split(".")
        if len(parts) != 2:
            self.ui.warn(f"edicao automatica nao suportada para {path}")
            self.ui.pause("enter...")
            return
        sec, field = parts[0], parts[1]
        lid_types = ["flat", "hemispherical", "none"]
        particle_kinds = ["sphere", "cube", "cylinder"]
        wall_modes = ["surface", "solid"]
        fluid_modes = ["none", "cavity"]
        cfd_regimes = ["laminar", "turbulent_rans"]
        opts = list(PACKING_MODE_CHOICES)

        if sec == "bed" and "bed" in self.params:
            b = self.params["bed"]
            if field == "diameter":
                b["diameter"] = self.get_number_input(
                    "diametro do leito", str(b["diameter"]), "m", True, "bed.diameter"
                )
            elif field == "height":
                b["height"] = self.get_number_input(
                    "altura do leito", str(b["height"]), "m", True, "bed.height"
                )
            elif field == "wall_thickness":
                b["wall_thickness"] = self.get_number_input(
                    "espessura da parede",
                    str(b["wall_thickness"]),
                    "m",
                    True,
                    "bed.wall_thickness",
                )
            elif field == "clearance":
                b["clearance"] = self.get_number_input(
                    "folga superior", str(b["clearance"]), "m", True, "bed.clearance"
                )
            elif field == "material":
                b["material"] = self.get_input(
                    "material da parede", str(b.get("material", "steel")), True, "bed.material"
                )
            elif field == "roughness":
                b["roughness"] = self.get_number_input(
                    "rugosidade", str(b.get("roughness", "0.0")), "m", False, "bed.roughness"
                )
        elif sec == "lids" and "lids" in self.params:
            li = self.params["lids"]
            if field == "top_type":
                d = lid_types.index(li["top_type"]) if li["top_type"] in lid_types else 0
                li["top_type"] = self.get_choice(
                    "tipo da tampa superior", lid_types, d, "lids.top_type"
                )
            elif field == "bottom_type":
                d = lid_types.index(li["bottom_type"]) if li["bottom_type"] in lid_types else 0
                li["bottom_type"] = self.get_choice(
                    "tipo da tampa inferior", lid_types, d, "lids.bottom_type"
                )
            elif field == "top_thickness":
                li["top_thickness"] = self.get_number_input(
                    "espessura tampa superior",
                    str(li["top_thickness"]),
                    "m",
                    True,
                    "lids.top_thickness",
                )
            elif field == "bottom_thickness":
                li["bottom_thickness"] = self.get_number_input(
                    "espessura tampa inferior",
                    str(li["bottom_thickness"]),
                    "m",
                    True,
                    "lids.bottom_thickness",
                )
            elif field == "seal_clearance":
                li["seal_clearance"] = self.get_number_input(
                    "folga do selo",
                    str(li.get("seal_clearance", "0.001")),
                    "m",
                    False,
                    "lids.seal_clearance",
                )
        elif sec == "particles" and "particles" in self.params:
            pt = self.params["particles"]
            if field == "kind":
                d = particle_kinds.index(pt["kind"]) if pt["kind"] in particle_kinds else 0
                pt["kind"] = self.get_choice(
                    "tipo de particula", particle_kinds, d, "particles.kind"
                )
            elif field == "diameter":
                pt["diameter"] = self.get_number_input(
                    "diametro das particulas",
                    str(pt["diameter"]),
                    "m",
                    True,
                    "particles.diameter",
                )
            elif field == "count":
                pt["count"] = int(
                    self.get_number_input(
                        "numero de particulas",
                        str(pt["count"]),
                        "",
                        True,
                        "particles.count",
                    )
                )
            elif field == "target_porosity":
                pt["target_porosity"] = self.get_number_input(
                    "porosidade alvo",
                    str(pt.get("target_porosity", "0.4")),
                    "",
                    False,
                    "particles.target_porosity",
                )
            elif field == "density":
                pt["density"] = self.get_number_input(
                    "densidade do material",
                    str(pt["density"]),
                    "kg/m3",
                    True,
                    "particles.density",
                )
            elif field == "mass":
                pt["mass"] = self.get_number_input(
                    "massa das particulas",
                    str(pt.get("mass", "0.0")),
                    "g",
                    False,
                    "particles.mass",
                )
            elif field == "restitution":
                pt["restitution"] = self.get_number_input(
                    "coeficiente de restituicao",
                    str(pt.get("restitution", "0.3")),
                    "",
                    False,
                    "particles.restitution",
                )
            elif field == "friction":
                pt["friction"] = self.get_number_input(
                    "coeficiente de atrito",
                    str(pt.get("friction", "0.5")),
                    "",
                    False,
                    "particles.friction",
                )
            elif field == "rolling_friction":
                pt["rolling_friction"] = self.get_number_input(
                    "atrito de rolamento",
                    str(pt.get("rolling_friction", "0.1")),
                    "",
                    False,
                    "particles.rolling_friction",
                )
            elif field == "linear_damping":
                pt["linear_damping"] = self.get_number_input(
                    "amortecimento linear",
                    str(pt.get("linear_damping", "0.1")),
                    "",
                    False,
                    "particles.linear_damping",
                )
            elif field == "angular_damping":
                pt["angular_damping"] = self.get_number_input(
                    "amortecimento angular",
                    str(pt.get("angular_damping", "0.1")),
                    "",
                    False,
                    "particles.angular_damping",
                )
            elif field == "seed":
                pt["seed"] = int(
                    self.get_number_input(
                        "seed para reproducibilidade",
                        str(pt.get("seed", 42)),
                        "",
                        False,
                        "particles.seed",
                    )
                )
        elif sec == "packing" and "packing" in self.params:
            pk = self.params["packing"]
            if field == "method":
                mi = opts.index(pk["method"]) if pk["method"] in opts else 0
                pk["method"] = normalize_packing_mode(
                    self.get_choice("metodo de empacotamento", opts, mi, "packing.method")
                )
            elif field == "gravity":
                pk["gravity"] = self.get_number_input(
                    "gravidade", str(pk.get("gravity", "-9.81")), "m/s2", True, "packing.gravity"
                )
            elif field == "substeps":
                pk["substeps"] = int(
                    self.get_number_input(
                        "sub-passos de simulacao",
                        str(pk.get("substeps", 10)),
                        "",
                        False,
                        "packing.substeps",
                    )
                )
            elif field == "iterations":
                pk["iterations"] = int(
                    self.get_number_input(
                        "iteracoes",
                        str(pk.get("iterations", 10)),
                        "",
                        False,
                        "packing.iterations",
                    )
                )
            elif field == "damping":
                pk["damping"] = self.get_number_input(
                    "amortecimento",
                    str(pk.get("damping", "0.1")),
                    "",
                    False,
                    "packing.damping",
                )
            elif field == "rest_velocity":
                pk["rest_velocity"] = self.get_number_input(
                    "velocidade de repouso",
                    str(pk.get("rest_velocity", "0.01")),
                    "m/s",
                    False,
                    "packing.rest_velocity",
                )
            elif field == "max_time":
                pk["max_time"] = self.get_number_input(
                    "tempo maximo",
                    str(pk.get("max_time", "5.0")),
                    "s",
                    False,
                    "packing.max_time",
                )
            elif field == "collision_margin":
                pk["collision_margin"] = self.get_number_input(
                    "margem de colisao",
                    str(pk.get("collision_margin", "0.001")),
                    "m",
                    False,
                    "packing.collision_margin",
                )
            elif field == "gap":
                pk["gap"] = float(
                    self.get_number_input(
                        "gap entre esferas",
                        str(pk.get("gap", "0.0001")),
                        "m",
                        False,
                        "packing.gap",
                    )
                )
            elif field == "random_seed":
                pk["random_seed"] = int(
                    self.get_number_input(
                        "random_seed",
                        str(pk.get("random_seed", 42)),
                        "",
                        False,
                        "packing.random_seed",
                    )
                )
            elif field == "max_placement_attempts":
                pk["max_placement_attempts"] = int(
                    self.get_number_input(
                        "max tentativas colocacao",
                        str(pk.get("max_placement_attempts", 500000)),
                        "",
                        False,
                        "packing.max_placement_attempts",
                    )
                )
            elif field == "strict_validation":
                pk["strict_validation"] = self.get_boolean(
                    "strict_validation (falhar se invalido)?",
                    bool(pk.get("strict_validation", True)),
                )
            elif field == "step_x":
                step_raw = self.get_number_input(
                    "step_x grade hex (vazio=auto)",
                    str(pk.get("step_x", "")),
                    "m",
                    False,
                    "packing.step_x",
                )
                if step_raw.strip():
                    pk["step_x"] = float(step_raw)
                elif "step_x" in pk:
                    del pk["step_x"]
        elif sec == "export" and "export" in self.params:
            ex = self.params["export"]
            if field == "formats":
                ex["formats"] = self.get_list_input(
                    "formatos de exportacao", ",", "export.formats"
                ) or ["stl_binary", "obj"]
            elif field == "units":
                ex["units"] = self.get_input(
                    "unidades de saida", str(ex.get("units", "m")), False, "export.units"
                )
            elif field == "scale":
                ex["scale"] = self.get_number_input(
                    "escala", str(ex.get("scale", "1.0")), "", False, "export.scale"
                )
            elif field == "wall_mode":
                wi = wall_modes.index(ex["wall_mode"]) if ex["wall_mode"] in wall_modes else 0
                ex["wall_mode"] = self.get_choice(
                    "modo da parede", wall_modes, wi, "export.wall_mode"
                )
            elif field == "fluid_mode":
                fi = fluid_modes.index(ex["fluid_mode"]) if ex["fluid_mode"] in fluid_modes else 0
                ex["fluid_mode"] = self.get_choice(
                    "modo do fluido", fluid_modes, fi, "export.fluid_mode"
                )
            elif field == "manifold_check":
                ex["manifold_check"] = self.get_boolean(
                    "verificar manifold", bool(ex.get("manifold_check", True))
                )
            elif field == "merge_distance":
                ex["merge_distance"] = self.get_number_input(
                    "distancia de fusao",
                    str(ex.get("merge_distance", "0.001")),
                    "m",
                    False,
                    "export.merge_distance",
                )
        elif sec == "cfd" and "cfd" in self.params:
            cf = self.params["cfd"]
            if field == "regime":
                ri = cfd_regimes.index(cf["regime"]) if cf["regime"] in cfd_regimes else 0
                cf["regime"] = self.get_choice("regime cfd", cfd_regimes, ri, "cfd.regime")
            elif field == "inlet_velocity":
                cf["inlet_velocity"] = self.get_number_input(
                    "velocidade de entrada",
                    str(cf.get("inlet_velocity", "0.1")),
                    "m/s",
                    False,
                    "cfd.inlet_velocity",
                )
            elif field == "fluid_density":
                cf["fluid_density"] = self.get_number_input(
                    "densidade do fluido",
                    str(cf.get("fluid_density", "1.225")),
                    "kg/m3",
                    False,
                    "cfd.fluid_density",
                )
            elif field == "fluid_viscosity":
                cf["fluid_viscosity"] = self.get_number_input(
                    "viscosidade do fluido",
                    str(cf.get("fluid_viscosity", "1.8e-5")),
                    "Pa.s",
                    False,
                    "cfd.fluid_viscosity",
                )
            elif field == "max_iterations":
                cf["max_iterations"] = int(
                    self.get_number_input(
                        "iteracoes maximas",
                        str(cf.get("max_iterations", 1000)),
                        "",
                        False,
                        "cfd.max_iterations",
                    )
                )
            elif field == "convergence_criteria":
                cf["convergence_criteria"] = self.get_number_input(
                    "criterio de convergencia",
                    str(cf.get("convergence_criteria", "1e-6")),
                    "",
                    False,
                    "cfd.convergence_criteria",
                )
            elif field == "write_fields":
                cf["write_fields"] = self.get_boolean(
                    "escrever campos", bool(cf.get("write_fields", False))
                )
        else:
            self.ui.warn(f"secao {sec} nao disponivel para edicao")
        self.ui.pause("enter para voltar a lista...")
    
    def _collect_packing_params(self, with_param_help: bool = False) -> Dict[str, Any]:
        # pergunta ao utilizador qual dos tres modos usar e recolhe campos extra
        # with param help true liga textos de ajuda ricos nos campos numericos do modo blender
        # with param help false usa questionario simples sem chaves param help
        # ph e uma funcao que ou devolve a chave de ajuda ou string vazia
        # primeiro bloco gravidade substeps etc serve para rigid body e fica no dict mesmo nos modos cientificos
        # segundo bloco gap random seed tentativas strict so para spherical packing
        # terceiro bloco gap step x strict so para hexagonal 3d
        opts = list(PACKING_MODE_CHOICES)
        ph = (lambda k: k) if with_param_help else (lambda _k: "")
        self.print_section("empacotamento")
        method_raw = self.get_choice(
            "metodo de empacotamento",
            opts,
            self._default_choice_index(list(opts), "packing.method", 0),
            "packing.method",
        )
        method = normalize_packing_mode(method_raw)
        pack: Dict[str, Any] = {
            "method": method,
            "gravity": self.get_number_input(
                "gravidade",
                self._default_from_loaded("packing.gravity", "-9.81"),
                "m/s2",
                True,
                ph("packing.gravity"),
            ),
            "substeps": int(
                self.get_number_input(
                    "sub-passos de simulacao",
                    self._default_from_loaded("packing.substeps", "10"),
                    "",
                    False,
                    ph("packing.substeps"),
                )
            ),
            "iterations": int(
                self.get_number_input(
                    "iteracoes",
                    self._default_from_loaded("packing.iterations", "10"),
                    "",
                    False,
                    ph("packing.iterations"),
                )
            ),
            "damping": self.get_number_input(
                "amortecimento",
                self._default_from_loaded("packing.damping", "0.1"),
                "",
                False,
                ph("packing.damping"),
            ),
            "rest_velocity": self.get_number_input(
                "velocidade de repouso",
                self._default_from_loaded("packing.rest_velocity", "0.01"),
                "m/s",
                False,
                ph("packing.rest_velocity"),
            ),
            "max_time": self.get_number_input(
                "tempo maximo",
                self._default_from_loaded("packing.max_time", "5.0"),
                "s",
                False,
                ph("packing.max_time"),
            ),
            "collision_margin": self.get_number_input(
                "margem de colisao",
                self._default_from_loaded("packing.collision_margin", "0.001"),
                "m",
                False,
                ph("packing.collision_margin"),
            ),
        }
        if method == "spherical_packing":
            pack["gap"] = float(
                self.get_number_input(
                    "gap entre esferas",
                    self._default_from_loaded("packing.gap", "0.0001"),
                    "m",
                    False,
                    ph("packing.gap"),
                )
            )
            pack["random_seed"] = int(
                self.get_number_input(
                    "random_seed",
                    self._default_from_loaded("packing.random_seed", "42"),
                    "",
                    False,
                    ph("packing.random_seed"),
                )
            )
            pack["max_placement_attempts"] = int(
                self.get_number_input(
                    "max tentativas colocacao",
                    self._default_from_loaded("packing.max_placement_attempts", "500000"),
                    "",
                    False,
                    ph("packing.max_placement_attempts"),
                )
            )
            sv = self.get_boolean(
                "strict_validation (falhar se invalido)?",
                self._default_bool_from_loaded("packing.strict_validation", True),
            )
            pack["strict_validation"] = sv
        elif method == "hexagonal_3d":
            pack["gap"] = float(
                self.get_number_input(
                    "gap entre esferas",
                    self._default_from_loaded("packing.gap", "0.0001"),
                    "m",
                    False,
                    ph("packing.gap"),
                )
            )
            step_raw = self.get_number_input(
                "step_x grade hex (vazio=auto)",
                self._default_from_loaded("packing.step_x", ""),
                "m",
                False,
                ph("packing.step_x"),
            )
            if step_raw.strip():
                pack["step_x"] = float(step_raw)
            sv = self.get_boolean(
                "strict_validation (falhar se invalido)?",
                self._default_bool_from_loaded("packing.strict_validation", True),
            )
            pack["strict_validation"] = sv
        return pack

    def _questionnaire_export_section(self) -> None:
        """mesma secao export do questionario completo — reutilizada pelo modo blender."""
        self.print_section("exportacao")
        wall_modes = ["surface", "solid"]
        fluid_modes = ["none", "cavity"]
        self.params.setdefault("export", {})
        e = self.params["export"]
        got_fmt = self.get_list_input(
            "formatos de exportacao", ",", "export.formats"
        )
        if got_fmt:
            e["formats"] = got_fmt
        else:
            fed = self._default_from_loaded("export.formats", "")
            if fed.strip():
                e["formats"] = [x.strip() for x in fed.split(",") if x.strip()]
            else:
                e["formats"] = ["stl_binary", "obj"]
        e["units"] = self.get_input(
            "unidades de saida",
            self._default_from_loaded("export.units", "m"),
            False,
            "export.units",
        )
        e["scale"] = self.get_number_input(
            "escala",
            self._default_from_loaded("export.scale", "1.0"),
            "",
            False,
            "export.scale",
        )
        e["wall_mode"] = self.get_choice(
            "modo da parede",
            wall_modes,
            self._default_choice_index(wall_modes, "export.wall_mode", 0),
            "export.wall_mode",
        )
        e["fluid_mode"] = self.get_choice(
            "modo do fluido",
            fluid_modes,
            self._default_choice_index(fluid_modes, "export.fluid_mode", 0),
            "export.fluid_mode",
        )
        e["manifold_check"] = self.get_boolean(
            "verificar manifold",
            self._default_bool_from_loaded("export.manifold_check", True),
        )
        e["merge_distance"] = self.get_number_input(
            "distancia de fusao",
            self._default_from_loaded("export.merge_distance", "0.001"),
            "m",
            False,
            "export.merge_distance",
        )

    def _questionnaire_slice_section(self) -> None:
        # thin slice (pseudo 2d) opcional
        self.print_section("thin slice (pseudo 2d)")
        if not self.get_boolean("ativar thin slice (fatia fina 3d)?", False):
            if "slice" in self.params:
                self.params.pop("slice", None)
            return
        axis = self.get_choice("eixo normal do corte", ["x", "y", "z"], 1)
        thickness = self.get_number_input("espessura da fatia", "0.002", "m", False, "")
        pos = self.get_number_input("posicao central da fatia", "0.0", "m", False, "")
        keep_only = self.get_boolean("manter apenas particulas que intersectam a fatia?", True)
        preserve = self.get_boolean("preservar coordenadas originais (nao recentrar na fatia)?", True)
        self.params["slice"] = {
            "slice_enabled": True,
            "slice_thickness": float(thickness),
            "slice_axis": axis,
            "slice_position": float(pos),
            "keep_only_intersecting_particles": bool(keep_only),
            "preserve_original_packing": bool(preserve),
        }
    
    def _fill_params_from_questionnaire(self) -> None:
        """preenche self.params com todas as secoes do questionario (sem nome de arquivo nem salvar)."""
        self.print_section("geometria do leito")
        self.params.setdefault("bed", {})
        bd = self.params["bed"]
        bd["diameter"] = self.get_number_input(
            "diametro do leito",
            self._default_from_loaded("bed.diameter", "0.05"),
            "m",
            True,
            "bed.diameter",
        )
        bd["height"] = self.get_number_input(
            "altura do leito",
            self._default_from_loaded("bed.height", "0.1"),
            "m",
            True,
            "bed.height",
        )
        bd["wall_thickness"] = self.get_number_input(
            "espessura da parede",
            self._default_from_loaded("bed.wall_thickness", "0.002"),
            "m",
            True,
            "bed.wall_thickness",
        )
        bd["clearance"] = self.get_number_input(
            "folga superior",
            self._default_from_loaded("bed.clearance", "0.01"),
            "m",
            True,
            "bed.clearance",
        )
        bd["material"] = self.get_input(
            "material da parede",
            self._default_from_loaded("bed.material", "steel"),
            True,
            "bed.material",
        )
        bd["roughness"] = self.get_number_input(
            "rugosidade",
            self._default_from_loaded("bed.roughness", "0.0"),
            "m",
            False,
            "bed.roughness",
        )

        self.print_section("tampas")
        lid_types = ["flat", "hemispherical", "none"]
        self.params.setdefault("lids", {})
        ld = self.params["lids"]
        ld["top_type"] = self.get_choice(
            "tipo da tampa superior",
            lid_types,
            self._default_choice_index(lid_types, "lids.top_type", 0),
            "lids.top_type",
        )
        ld["bottom_type"] = self.get_choice(
            "tipo da tampa inferior",
            lid_types,
            self._default_choice_index(lid_types, "lids.bottom_type", 0),
            "lids.bottom_type",
        )
        ld["top_thickness"] = self.get_number_input(
            "espessura tampa superior",
            self._default_from_loaded("lids.top_thickness", "0.003"),
            "m",
            True,
            "lids.top_thickness",
        )
        ld["bottom_thickness"] = self.get_number_input(
            "espessura tampa inferior",
            self._default_from_loaded("lids.bottom_thickness", "0.003"),
            "m",
            True,
            "lids.bottom_thickness",
        )
        ld["seal_clearance"] = self.get_number_input(
            "folga do selo",
            self._default_from_loaded("lids.seal_clearance", "0.001"),
            "m",
            False,
            "lids.seal_clearance",
        )

        self.print_section("particulas")
        particle_kinds = ["sphere", "cube", "cylinder"]
        self.params.setdefault("particles", {})
        pt = self.params["particles"]
        pt["kind"] = self.get_choice(
            "tipo de particula",
            particle_kinds,
            self._default_choice_index(particle_kinds, "particles.kind", 0),
            "particles.kind",
        )
        pt["diameter"] = self.get_number_input(
            "diametro das particulas",
            self._default_from_loaded("particles.diameter", "0.005"),
            "m",
            True,
            "particles.diameter",
        )
        pt["count"] = int(
            self.get_number_input(
                "numero de particulas",
                self._default_from_loaded("particles.count", "100"),
                "",
                True,
                "particles.count",
            )
        )
        pt["target_porosity"] = self.get_number_input(
            "porosidade alvo",
            self._default_from_loaded("particles.target_porosity", "0.4"),
            "",
            False,
            "particles.target_porosity",
        )
        pt["density"] = self.get_number_input(
            "densidade do material",
            self._default_from_loaded("particles.density", "2500.0"),
            "kg/m3",
            True,
            "particles.density",
        )
        pt["mass"] = self.get_number_input(
            "massa das particulas",
            self._default_from_loaded("particles.mass", "0.0"),
            "g",
            False,
            "particles.mass",
        )
        pt["restitution"] = self.get_number_input(
            "coeficiente de restituicao",
            self._default_from_loaded("particles.restitution", "0.3"),
            "",
            False,
            "particles.restitution",
        )
        pt["friction"] = self.get_number_input(
            "coeficiente de atrito",
            self._default_from_loaded("particles.friction", "0.5"),
            "",
            False,
            "particles.friction",
        )
        pt["rolling_friction"] = self.get_number_input(
            "atrito de rolamento",
            self._default_from_loaded("particles.rolling_friction", "0.1"),
            "",
            False,
            "particles.rolling_friction",
        )
        pt["linear_damping"] = self.get_number_input(
            "amortecimento linear",
            self._default_from_loaded("particles.linear_damping", "0.1"),
            "",
            False,
            "particles.linear_damping",
        )
        pt["angular_damping"] = self.get_number_input(
            "amortecimento angular",
            self._default_from_loaded("particles.angular_damping", "0.1"),
            "",
            False,
            "particles.angular_damping",
        )
        pt["seed"] = int(
            self.get_number_input(
                "seed para reproducibilidade",
                self._default_from_loaded("particles.seed", "42"),
                "",
                False,
                "particles.seed",
            )
        )

        self.params["packing"] = self._collect_packing_params(with_param_help=True)
        self._questionnaire_export_section()
        self._questionnaire_slice_section()

        self.print_section("parametros cfd (opcional)")
        if self.get_boolean("incluir parametros cfd?", False):
            cfd_regimes = ["laminar", "turbulent_rans"]
            self.params.setdefault("cfd", {})
            cf = self.params["cfd"]
            cf["regime"] = self.get_choice(
                "regime cfd", cfd_regimes, 0, "cfd.regime"
            )
            cf["inlet_velocity"] = self.get_number_input(
                "velocidade de entrada", "0.1", "m/s", False, "cfd.inlet_velocity"
            )
            cf["fluid_density"] = self.get_number_input(
                "densidade do fluido", "1.225", "kg/m3", False, "cfd.fluid_density"
            )
            cf["fluid_viscosity"] = self.get_number_input(
                "viscosidade do fluido", "1.8e-5", "Pa.s", False, "cfd.fluid_viscosity"
            )
            cf["max_iterations"] = int(
                self.get_number_input(
                    "iteracoes maximas", "1000", "", False, "cfd.max_iterations"
                )
            )
            cf["convergence_criteria"] = self.get_number_input(
                "criterio de convergencia", "1e-6", "", False, "cfd.convergence_criteria"
            )
            cf["write_fields"] = self.get_boolean("escrever campos", False)
    
    def interactive_questionnaire(self) -> None:
        """apenas coleta parametros (usado pelo pipeline completo, sem salvar .bed aqui)."""
        old = self._cancel_enabled
        self._cancel_enabled = True
        try:
            self._fill_params_from_questionnaire()
        except _WizardCancelled:
            # deixa a interrupcao ser tratada pelo chamador (pipeline ou modo interativo)
            raise
        finally:
            self._cancel_enabled = old
    
    def interactive_mode(self):
        """modo questionario interativo - usuario responde perguntas passo a passo"""
        old = self._cancel_enabled
        self._cancel_enabled = True
        try:
            self.clear_screen()
            self.print_header(
                "questionario interativo", "parametrizacao do leito passo a passo"
            )
            self.ui.breadcrumbs("wizard", "questionario")
            self._hint_fluxo_questionario()
            self._hint_controles_entrada()
            self.ui.println()
            self._maybe_load_existing_bed(caption="questionario")
            if not self.skip_questionnaire_after_load:
                self._fill_params_from_questionnaire()
            _out_default = "meu_leito.bed"
            if self.output_file:
                _out_default = Path(self.output_file).name
            self.output_file = self.get_input("nome do arquivo de saida", _out_default)
            self.confirm_and_save()
        except _WizardCancelled:
            self.ui.muted("cancelado. a voltar ao menu inicial")
            self.params = {}
            self.output_file = None
            return
        finally:
            self._cancel_enabled = old
    
    def template_mode(self, prefer: Optional[str] = None) -> None:
        """modo edicao de template - usuario edita um arquivo template padrao.

        prefer:
          None — comportamento original (escolha json vs editor se existirem templates).
          "json" — forcar fluxo de templates json em dsl/wizard_templates (se existir).
          "editor" — saltar para o editor .bed classico.
        """
        self.clear_screen()
        self.print_header("editor de template", "edicao de modelo .bed")
        self.ui.breadcrumbs("wizard", "template")
        self._hint_fluxo_template()
        self._hint_controles_entrada()
        self.ui.println()

        # nomes dos ficheiros json em dsl wizard templates sem extensao
        json_names = list_template_names()
        # se existir pelo menos um template json oferecemos fluxo rapido sem editor externo
        if json_names and prefer != "editor":
            if prefer == "json":
                modo = "ficheiros json em dsl/wizard_templates"
            else:
                modo = self.get_choice(
                    "origem do template",
                    ["ficheiros json em dsl/wizard_templates", "editor .bed classico"],
                    0,
                )
            # ramo json carrega dict ja estruturado converte para params do wizard e compila
            if modo.startswith("ficheiros"):
                # pick e o identificador do template por exemplo default spherical
                pick = self.get_choice("template", json_names, 0)
                # data e o dicionario python lido do ficheiro json do template
                data = load_template(pick)
                # normalizar chaves aninhadas e tipos antes de mapear para o wizard
                normalize_loaded_dict(data)
                # self params fica no mesmo formato que o questionario interativo preencheria
                self.params = json_to_wizard_params(data)
                # sugestao de nome troca prefixo default por leito para o bed de saida
                self.output_file = self.get_input(
                    "nome do arquivo de saida", f"{pick.replace('default_', 'leito_')}.bed"
                )
                # grava o texto bed no disco a partir de self params
                self.save_bed_file()
                # se o compilador antlr passar aplicamos patches no json gerado
                if self.verify_and_compile():
                    # jpath e o json compilado ao lado do bed mesmo nome com sufixo json
                    jpath = Path(str(Path(self.output_file).resolve()) + ".json")
                    # recoloca packing mode e campos que a gramatica bed nao serializa
                    patch_compiled_json_packing(jpath, self.params)
                    # recoloca formatos de export pedidos pelo usuario stl obj etc
                    patch_compiled_json_export(jpath, self.params)
                    patch_compiled_json_metadata(jpath, self.params)
                    patch_compiled_json_slice(jpath, self.params)
                    # aqui usamos o metadado generation_backend
                    # se ele for pure_python entao o pipeline pode gerar o stl em python puro
                    # isso evita depender de um passo extra dentro do blender
                    gb = str(self.params.get("generation_backend") or "")
                    if gb == "pure_python" and self.ui.confirm(
                        "gerar stl em python puro agora?", default=True
                    ):
                        out_stl = (
                            Path.cwd() / f"{Path(self.output_file).stem}_pure.stl"
                        ).resolve()
                        ok, stl = self.run_pure_python_with_json_path(jpath, out_stl=out_stl)
                        if ok and stl and self.ui.confirm(
                            "gostaria de abrir o blender com o stl gerado?", default=False
                        ):
                            self.open_blender_gui_with_stl(stl)
                # termina template mode neste fluxo sem abrir editor temporario
                return
        if prefer == "json" and not json_names:
            self.ui.warn(
                "nao ha ficheiros json em dsl/wizard_templates; a seguir para o editor .bed classico."
            )
            self.ui.println()
        
        # criar template padrao com valores exemplo
        template = self.create_default_template()
        
        # obter nome do arquivo de saida
        self.output_file = self.get_input("nome do arquivo de saida", "meu_leito.bed")
        
        # criar arquivo temporario para edicao
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bed', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(template)  # escrever template no arquivo temporario
            temp_file_path = temp_file.name  # obter caminho do arquivo temporario
        
        self.ui.println()
        self.ui.muted(f"template temporario: {temp_file_path}")
        self.ui.println("editores sugeridos:")
        self.ui.muted("notepad (windows) | nano / vim (linux ou mac) | ou continuar sem editar")
        
        # obter escolha do editor
        editor_choice = self.get_choice("escolha um editor", 
                                      ["notepad", "nano", "vim", "continuar sem editar"], 3)
        
        # abrir editor se escolhido
        if editor_choice != "continuar sem editar":
            try:
                # executar editor com arquivo temporario
                if editor_choice == "notepad":
                    subprocess.run([editor_choice, temp_file_path], check=True)
                else:
                    subprocess.run([editor_choice, temp_file_path], check=True)
            except subprocess.CalledProcessError:
                self.ui.warn(f"erro ao abrir editor {editor_choice}; continuando sem edicao")
            except FileNotFoundError:
                self.ui.warn(f"editor {editor_choice} nao encontrado; continuando sem edicao")
        
        # ler conteudo editado do arquivo temporario
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # limpar arquivo temporario
        os.unlink(temp_file_path)
        
        # salvar arquivo final com conteudo editado
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.ui.ok(f"arquivo salvo: {self.output_file}")
        
        # verificar sintaxe e compilar arquivo
        self.verify_and_compile()
    
    def create_default_template(self) -> str:
        """criar template padrao com valores exemplo para edicao"""
        return '''// template padrao para leito empacotado
// edite os valores conforme necessario

bed {
    diameter = 0.05 m;           // diametro do leito
    height = 0.1 m;              // altura do leito
    wall_thickness = 0.002 m;    // espessura da parede
    clearance = 0.01 m;          // folga superior
    material = "steel";          // material da parede
    roughness = 0.0 m;           // rugosidade (opcional)
}

lids {
    top_type = "flat";           // tipo da tampa superior
    bottom_type = "flat";        // tipo da tampa inferior
    top_thickness = 0.003 m;     // espessura tampa superior
    bottom_thickness = 0.003 m;  // espessura tampa inferior
    seal_clearance = 0.001 m;    // folga do selo (opcional)
}

particles {
    kind = "sphere";             // tipo de particula
    diameter = 0.005 m;          // diametro das particulas
    count = 100;                 // numero de particulas
    target_porosity = 0.4;       // porosidade alvo (opcional)
    density = 2500.0 kg/m3;      // densidade do material
    mass = 0.0 g;                // massa das particulas (opcional)
    restitution = 0.3;           // coeficiente de restituicao (opcional)
    friction = 0.5;              // coeficiente de atrito (opcional)
    rolling_friction = 0.1;      // atrito de rolamento (opcional)
    linear_damping = 0.1;        // amortecimento linear (opcional)
    angular_damping = 0.1;       // amortecimento angular (opcional)
    seed = 42;                   // seed para reproducibilidade (opcional)
}

packing {
    method = "rigid_body";       // metodo de empacotamento
    gravity = -9.81 m/s2;        // gravidade
    substeps = 10;               // sub-passos de simulacao (opcional)
    iterations = 10;             // iteracoes (opcional)
    damping = 0.1;               // amortecimento (opcional)
    rest_velocity = 0.01 m/s;    // velocidade de repouso (opcional)
    max_time = 5.0 s;            // tempo maximo (opcional)
    collision_margin = 0.001 m;  // margem de colisao (opcional)
}

export {
    formats = ["stl_binary", "obj"];  // formatos de exportacao
    units = "m";                      // unidades de saida (opcional)
    scale = 1.0;                      // escala (opcional)
    wall_mode = "surface";            // modo da parede
    fluid_mode = "none";              // modo do fluido
    manifold_check = true;            // verificar manifold (opcional)
    merge_distance = 0.001 m;         // distancia de fusao (opcional)
}

// secao CFD (opcional - descomente se necessario)
/*
cfd {
    regime = "laminar";               // regime CFD
    inlet_velocity = 0.1 m/s;         // velocidade de entrada (opcional)
    fluid_density = 1.225 kg/m3;      // densidade do fluido (opcional)
    fluid_viscosity = 1.8e-5 Pa.s;   // viscosidade do fluido (opcional)
    max_iterations = 1000;            // iteracoes maximas (opcional)
    convergence_criteria = 1e-6;      // criterio de convergencia (opcional)
    write_fields = false;             // escrever campos (opcional)
}
*/
'''
    
    def confirm_and_save(self):
        """confirmar parametros configurados e salvar arquivo"""
        self.clear_screen()
        self.print_header("confirmacao", "revise antes de salvar o .bed")
        self.ui.breadcrumbs("wizard", "questionario", "confirmacao")
        self.ui.println("parametros configurados:")
        self.ui.println()
        self.ui.println(f"  leito: {self.params['bed']['diameter']} m x {self.params['bed']['height']} m")
        self.ui.println(f"  particulas: {self.params['particles']['count']} {self.params['particles']['kind']} ({self.params['particles']['diameter']} m)")
        self.ui.println(f"  empacotamento: {self.params['packing']['method']}")
        self.ui.println(f"  exportacao: {', '.join(self.params['export']['formats'])}")
        if 'cfd' in self.params:
            self.ui.println(f"  cfd: {self.params['cfd']['regime']}")
        self.ui.println()
        
        # confirmar se usuario quer salvar
        if self.get_boolean("salvar arquivo .bed?", True):
            self.save_bed_file()
            self.verify_and_compile()
        else:
            self.ui.muted("operacao cancelada.")
    
    def _normalize_bed_output_path(self) -> None:
        # caminhos relativos gravam em local_data/beds
        if not self.output_file:
            return
        p = Path(self.output_file)
        if p.is_absolute():
            return
        self.output_file = str((beds_dir() / p).resolve())
    
    def save_bed_file(self):
        """salvar arquivo .bed com conteudo gerado"""
        self._normalize_bed_output_path()
        content = self.generate_bed_content()  # gerar conteudo do arquivo
        
        # escrever arquivo com codificacao utf-8
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.ui.ok(f"arquivo salvo: {self.output_file}")

    def generate_bed_file(self) -> bool:
        # usado pelo pipeline completo e menu de testes rapidos
        # nao mostra confirmacao rica apenas grava e devolve bool
        # parent mkdir garante pastas intermediarias se output bed tiver caminho profundo
        try:
            self._normalize_bed_output_path()
            content = self.generate_bed_content()
            Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except OSError as e:
            self.ui.err(f"falha ao gravar .bed: {e}")
            return False

    def generate_bed_content(self) -> str:
        """gerar conteudo do arquivo .bed a partir dos parametros configurados"""
        lines = ["// arquivo .bed gerado pelo wizard"]
        lines.append("")
        
        # secao bed - parametros geometricos do leito
        lines.append("bed {")
        bed = self.params['bed']
        lines.append(f"    diameter = {bed['diameter']} m;")
        lines.append(f"    height = {bed['height']} m;")
        lines.append(f"    wall_thickness = {bed['wall_thickness']} m;")
        lines.append(f"    clearance = {bed['clearance']} m;")
        lines.append(f"    material = \"{bed['material']}\";")
        # adicionar rugosidade apenas se especificada
        if bed['roughness']:
            lines.append(f"    roughness = {bed['roughness']} m;")
        lines.append("}")
        lines.append("")
        
        # secao lids - parametros das tampas
        lines.append("lids {")
        lids = self.params['lids']
        lines.append(f"    top_type = \"{lids['top_type']}\";")
        lines.append(f"    bottom_type = \"{lids['bottom_type']}\";")
        lines.append(f"    top_thickness = {lids['top_thickness']} m;")
        lines.append(f"    bottom_thickness = {lids['bottom_thickness']} m;")
        # adicionar folga do selo apenas se especificada
        if lids['seal_clearance']:
            lines.append(f"    seal_clearance = {lids['seal_clearance']} m;")
        lines.append("}")
        lines.append("")
        
        # secao particles - parametros das particulas
        lines.append("particles {")
        particles = self.params['particles']
        lines.append(f"    kind = \"{particles['kind']}\";")
        lines.append(f"    diameter = {particles['diameter']} m;")
        lines.append(f"    count = {particles['count']};")
        # adicionar parametros opcionais apenas se especificados
        if particles['target_porosity']:
            lines.append(f"    target_porosity = {particles['target_porosity']};")
        lines.append(f"    density = {particles['density']} kg/m3;")
        if particles['mass']:
            lines.append(f"    mass = {particles['mass']} g;")
        if particles['restitution']:
            lines.append(f"    restitution = {particles['restitution']};")
        if particles['friction']:
            lines.append(f"    friction = {particles['friction']};")
        if particles['rolling_friction']:
            lines.append(f"    rolling_friction = {particles['rolling_friction']};")
        if particles['linear_damping']:
            lines.append(f"    linear_damping = {particles['linear_damping']};")
        if particles['angular_damping']:
            lines.append(f"    angular_damping = {particles['angular_damping']};")
        if particles['seed']:
            lines.append(f"    seed = {particles['seed']};")
        lines.append("}")
        lines.append("")
        
        # secao packing - parametros do empacotamento fisico
        lines.append("packing {")
        packing = self.params['packing']
        lines.append(f"    method = \"{packing['method']}\";")
        lines.append(f"    gravity = {packing['gravity']} m/s2;")
        # adicionar parametros opcionais apenas se especificados
        if packing['substeps']:
            lines.append(f"    substeps = {packing['substeps']};")
        if packing['iterations']:
            lines.append(f"    iterations = {packing['iterations']};")
        if packing['damping']:
            lines.append(f"    damping = {packing['damping']};")
        if packing['rest_velocity']:
            lines.append(f"    rest_velocity = {packing['rest_velocity']} m/s;")
        if packing['max_time']:
            lines.append(f"    max_time = {packing['max_time']} s;")
        if packing['collision_margin']:
            lines.append(f"    collision_margin = {packing['collision_margin']} m;")
        lines.append("}")
        lines.append("")
        
        # secao export - parametros de exportacao
        lines.append("export {")
        export = self.params['export']
        # formatar lista de formatos com aspas
        formats_str = ", ".join([f'"{fmt}"' for fmt in export['formats']])
        lines.append(f"    formats = [{formats_str}];")
        # adicionar parametros opcionais apenas se especificados
        if export['units']:
            lines.append(f"    units = \"{export['units']}\";")
        if export['scale']:
            lines.append(f"    scale = {export['scale']};")
        lines.append(f"    wall_mode = \"{export['wall_mode']}\";")
        lines.append(f"    fluid_mode = \"{export['fluid_mode']}\";")
        # converter boolean para string minuscula
        if export['manifold_check'] is not None:
            lines.append(f"    manifold_check = {str(export['manifold_check']).lower()};")
        if export['merge_distance']:
            lines.append(f"    merge_distance = {export['merge_distance']} m;")
        lines.append("}")
        lines.append("")
        
        # secao cfd (se presente)
        if 'cfd' in self.params:
            lines.append("cfd {")
            cfd = self.params['cfd']
            lines.append(f"    regime = \"{cfd['regime']}\";")
            if cfd['inlet_velocity']:
                lines.append(f"    inlet_velocity = {cfd['inlet_velocity']} m/s;")
            if cfd['fluid_density']:
                lines.append(f"    fluid_density = {cfd['fluid_density']} kg/m3;")
            if cfd['fluid_viscosity']:
                lines.append(f"    fluid_viscosity = {cfd['fluid_viscosity']} Pa.s;")
            if cfd['max_iterations']:
                lines.append(f"    max_iterations = {cfd['max_iterations']};")
            if cfd['convergence_criteria']:
                lines.append(f"    convergence_criteria = {cfd['convergence_criteria']};")
            if cfd['write_fields'] is not None:
                lines.append(f"    write_fields = {str(cfd['write_fields']).lower()};")
            lines.append("}")
        
        return "\n".join(lines)
    
    def verify_and_compile(self):
        """verificar sintaxe e compilar arquivo .bed"""
        print(f"\nverificando arquivo: {self.output_file}")
        
        # verificar se arquivo existe
        if not os.path.exists(self.output_file):
            print(f"  erro: arquivo nao encontrado: {self.output_file}")
            return False
        
        # caminho absoluto: o subprocess do compilador usa cwd=dsl/; paths relativos
        # gravados na raiz do repo nao seriam encontrados sem isso
        bed_abs = str(Path(self.output_file).resolve())
        json_abs = f"{bed_abs}.json"
        
        # tentar compilar com ANTLR
        try:
            result = subprocess.run([
                sys.executable, 
                "compiler/bed_compiler_antlr_standalone.py", 
                bed_abs, 
                "-o", json_abs,
                "-v"
            ], capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                print("  sucesso: sintaxe valida!")
                print("  sucesso: compilacao bem-sucedida!")
                print(f"  arquivo json gerado: {json_abs}")
                print(f"  resultado: {result.stdout}")
                return True
            else:
                print("  erro: erro na compilacao:")
                if result.stderr:
                    print(f"  {result.stderr}")
                if result.stdout:
                    print(f"  {result.stdout}")
                return False
                
        except FileNotFoundError:
            print("  aviso: compilador antlr nao encontrado!")
            print("  verifique se o arquivo bed_compiler_antlr_standalone.py existe")
            return False
        except Exception as e:
            print(f"  erro: erro inesperado: {e}")
            return False
    
    def _questionnaire_blender_bed_lids_particles_packing(self) -> None:
        """geometria, tampas, particulas e empacotamento com ajuda rica (modo blender)."""
        self.print_section("geometria do leito")
        self.params.setdefault("bed", {})
        bd = self.params["bed"]
        bd["diameter"] = self.get_number_input(
            "diametro do leito",
            self._default_from_loaded("bed.diameter", "0.05"),
            "m",
            True,
            "bed.diameter",
        )
        bd["height"] = self.get_number_input(
            "altura do leito",
            self._default_from_loaded("bed.height", "0.1"),
            "m",
            True,
            "bed.height",
        )
        bd["wall_thickness"] = self.get_number_input(
            "espessura da parede",
            self._default_from_loaded("bed.wall_thickness", "0.002"),
            "m",
            True,
            "bed.wall_thickness",
        )
        bd["clearance"] = self.get_number_input(
            "folga superior",
            self._default_from_loaded("bed.clearance", "0.01"),
            "m",
            True,
            "bed.clearance",
        )
        bd["material"] = self.get_input(
            "material da parede",
            self._default_from_loaded("bed.material", "steel"),
            True,
            "bed.material",
        )
        bd["roughness"] = self.get_number_input(
            "rugosidade",
            self._default_from_loaded("bed.roughness", "0.0"),
            "m",
            False,
            "bed.roughness",
        )

        self.print_section("tampas")
        lid_types = ["flat", "hemispherical", "none"]
        self.params.setdefault("lids", {})
        ld = self.params["lids"]
        ld["top_type"] = self.get_choice(
            "tipo da tampa superior",
            lid_types,
            self._default_choice_index(lid_types, "lids.top_type", 0),
            "lids.top_type",
        )
        ld["bottom_type"] = self.get_choice(
            "tipo da tampa inferior",
            lid_types,
            self._default_choice_index(lid_types, "lids.bottom_type", 0),
            "lids.bottom_type",
        )
        ld["top_thickness"] = self.get_number_input(
            "espessura tampa superior",
            self._default_from_loaded("lids.top_thickness", "0.003"),
            "m",
            True,
            "lids.top_thickness",
        )
        ld["bottom_thickness"] = self.get_number_input(
            "espessura tampa inferior",
            self._default_from_loaded("lids.bottom_thickness", "0.003"),
            "m",
            True,
            "lids.bottom_thickness",
        )
        ld["seal_clearance"] = self.get_number_input(
            "folga do selo",
            self._default_from_loaded("lids.seal_clearance", "0.001"),
            "m",
            False,
            "lids.seal_clearance",
        )

        self.print_section("particulas")
        particle_kinds = ["sphere", "cube", "cylinder"]
        self.params.setdefault("particles", {})
        pt = self.params["particles"]
        pt["kind"] = self.get_choice(
            "tipo de particula",
            particle_kinds,
            self._default_choice_index(particle_kinds, "particles.kind", 0),
            "particles.kind",
        )
        pt["diameter"] = self.get_number_input(
            "diametro das particulas",
            self._default_from_loaded("particles.diameter", "0.005"),
            "m",
            True,
            "particles.diameter",
        )
        pt["count"] = int(
            self.get_number_input(
                "numero de particulas",
                self._default_from_loaded("particles.count", "100"),
                "",
                True,
                "particles.count",
            )
        )
        pt["target_porosity"] = self.get_number_input(
            "porosidade alvo",
            self._default_from_loaded("particles.target_porosity", "0.4"),
            "",
            False,
            "particles.target_porosity",
        )
        pt["density"] = self.get_number_input(
            "densidade do material",
            self._default_from_loaded("particles.density", "2500.0"),
            "kg/m3",
            True,
            "particles.density",
        )
        pt["mass"] = self.get_number_input(
            "massa das particulas",
            self._default_from_loaded("particles.mass", "0.0"),
            "g",
            False,
            "particles.mass",
        )
        pt["restitution"] = self.get_number_input(
            "coeficiente de restituicao",
            self._default_from_loaded("particles.restitution", "0.3"),
            "",
            False,
            "particles.restitution",
        )
        pt["friction"] = self.get_number_input(
            "coeficiente de atrito",
            self._default_from_loaded("particles.friction", "0.5"),
            "",
            False,
            "particles.friction",
        )
        pt["rolling_friction"] = self.get_number_input(
            "atrito de rolamento",
            self._default_from_loaded("particles.rolling_friction", "0.1"),
            "",
            False,
            "particles.rolling_friction",
        )
        pt["linear_damping"] = self.get_number_input(
            "amortecimento linear",
            self._default_from_loaded("particles.linear_damping", "0.1"),
            "",
            False,
            "particles.linear_damping",
        )
        pt["angular_damping"] = self.get_number_input(
            "amortecimento angular",
            self._default_from_loaded("particles.angular_damping", "0.1"),
            "",
            False,
            "particles.angular_damping",
        )
        pt["seed"] = int(
            self.get_number_input(
                "seed para reproducibilidade",
                self._default_from_loaded("particles.seed", "42"),
                "",
                False,
                "particles.seed",
            )
        )
        self.params["packing"] = self._collect_packing_params(with_param_help=True)

    def blender_generation_mode(self) -> None:
        """questionario 3d sem cfd; export igual ao questionario; escolha de abertura do blender."""
        try:
            self.clear_screen()
            self.print_header("geracao 3d (blender)", "sem cfd; export configuravel como no questionario")
            self.ui.breadcrumbs("wizard", "blender-3d")
            self.ui.muted("parametros cfd nao sao pedidos neste modo.")
            self._hint_fluxo_blender()
            self._hint_controles_entrada()
            self.ui.println()
            self._maybe_load_existing_bed(caption="geracao 3d (blender)")
            if not self.skip_questionnaire_after_load:
                self._questionnaire_blender_bed_lids_particles_packing()
                self._questionnaire_export_section()
                self._questionnaire_slice_section()
            self.ui.hint("secao cfd omitida neste modo")
            _blend_out = "leito_blender.bed"
            if self.output_file:
                _blend_out = Path(self.output_file).name
            self.output_file = self.get_input("nome do arquivo de saida", _blend_out)
            opt_nunca = "nao abrir o blender apos gerar"
            opt_perg = "perguntar se deseja abrir o blender apos gerar"
            opt_auto = "abrir o blender automaticamente apos gerar"
            escolha = self.get_choice(
                "comportamento apos gerar o modelo",
                [opt_nunca, opt_perg, opt_auto],
                1,
            )
            if escolha == opt_auto:
                policy = "always"
            elif escolha == opt_perg:
                policy = "ask"
            else:
                policy = "never"
            self._confirm_and_generate_blender(open_policy=policy)
        except _WizardCancelled:
            self.ui.muted("cancelado.")

    def _confirm_and_generate_blender(self, open_policy: str) -> None:
        """open_policy: never | ask | always — gera .bed, compila, executa blender."""
        self.clear_screen()
        self.print_header("confirmacao", "geracao 3d no blender")
        self.ui.breadcrumbs("wizard", "blender", "confirmar")
        fmts = self.params.get("export", {}).get("formats") or []
        fmt_s = ", ".join(str(x) for x in fmts)
        self.ui.println("resumo:")
        self.ui.muted(
            f"  leito: {self.params['bed']['diameter']} m x {self.params['bed']['height']} m"
        )
        self.ui.muted(
            f"  particulas: {self.params['particles']['count']} {self.params['particles']['kind']}"
        )
        self.ui.muted(f"  empacotamento: {self.params['packing']['method']} | export: {fmt_s}")
        self.ui.println()
        if open_policy == "always":
            self.ui.hint("apos gerar, o blender abre automaticamente (se o executavel existir)")
            self.ui.println()
        if not self.get_boolean("continuar com geracao no blender?", True):
            self.ui.muted("operacao cancelada.")
            return
        self.save_bed_file()
        self.ui.section("compilando .bed")
        if not self.verify_and_compile():
            self.ui.err("nao foi possivel compilar o arquivo")
            return
        jpath = Path(str(Path(self.output_file).resolve()) + ".json")
        patch_compiled_json_packing(jpath, self.params)
        patch_compiled_json_export(jpath, self.params)
        patch_compiled_json_metadata(jpath, self.params)
        patch_compiled_json_slice(jpath, self.params)
        self.ui.section("executando blender")
        open_after = open_policy == "always"
        ok, blend_path = self.execute_blender(open_after=open_after)
        if not ok:
            return
        if open_policy == "always":
            self.ui.section("concluido")
            if blend_path:
                self.ui.ok(f"modelo: {blend_path}")
            self.ui.muted(
                "blender em segundo plano — zoom: scroll; orbita: botao do meio; topo: numpad 7; shading: z"
            )
            return
        if open_policy == "ask" and blend_path:
            if self.get_boolean(
                "gostaria de abrir o blender com o modelo gerado?", False
            ):
                self.open_blender_gui_with_blend(blend_path)
    
    def find_blender_executable(self) -> Optional[str]:
        # procura instalacoes tipicas no windows por caminho absoluto
        # se nenhuma existir tenta blender no path via shutil which
        # retorno none significa que run blender with json path vai falhar cedo
        candidates = [
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender\blender.exe",
            r"C:\Steam\steamapps\common\Blender\blender.exe",
        ]
        for path in candidates:
            if Path(path).exists():
                return path
        w = shutil.which("blender")
        return w

    def run_blender_with_json_path(
        self,
        json_file: Path,
        open_after: bool = False,
        formats: Optional[str] = None,
        output_blend: Optional[Path] = None,
    ) -> Tuple[bool, Optional[Path], str]:
        # subprocesso blender background python leito extracao py
        # terceiro elemento e stdout para preview no modo testes rapidos
        # json file e o params json ja com patch de packing cientifico
        # formats string virgula blend stl glb se none le do proprio json export
        # output blend destino do ficheiro principal se none derivado do stem do json
        # open after true chama open blender with file no fim
        # timeout 600 segundos para leitos grandes ou muitas esferas rigid body
        try:
            project_root = Path(__file__).parent.parent
            blender_script = project_root / "scripts" / "blender_scripts" / "leito_extracao.py"
            output_dir = models_3d_dir()

            json_file = Path(json_file).resolve()
            if output_blend is None:
                stem = json_file.name.replace(".bed.json", "").replace(".json", "")
                output_blend = output_dir / f"{stem}.blend"
            else:
                output_blend = Path(output_blend)

            print(f"script blender: {blender_script}")
            print(f"arquivo json: {json_file}")
            print(f"saida .blend: {output_blend}")

            if not blender_script.exists():
                print(f"erro: script blender nao encontrado: {blender_script}")
                return False, None, ""
            if not json_file.exists():
                print(f"erro: arquivo json nao encontrado: {json_file}")
                return False, None, ""

            blender_exe = self.find_blender_executable()
            if not blender_exe:
                print("erro: blender nao encontrado")
                return False, None, ""

            if formats is None:
                try:
                    import json as _json

                    with open(json_file, "r", encoding="utf-8") as f:
                        d = _json.load(f)
                    formats = export_formats_for_blender(d.get("export") or {})
                except Exception:
                    formats = "blend,stl"

            print(f"blender encontrado: {blender_exe}")
            print(f"formatos: {formats}")
            print("\niniciando geracao do modelo 3d...")

            cmd = [
                blender_exe,
                "--background",
                "--python",
                str(blender_script),
                "--",
                "--params",
                str(json_file),
                "--output",
                str(output_blend),
                "--formats",
                formats,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.stdout:
                print("\nsaida do blender:")
                print(result.stdout)

            if result.returncode == 0 and output_blend.exists():
                print("\nsucesso: modelo 3d gerado!")
                if open_after:
                    print("\nabrindo modelo no blender...")
                    self.open_blender_with_file(blender_exe, output_blend)
                return True, output_blend, result.stdout or ""

            print("\nerro: falha na geracao do modelo")
            print(f"codigo: {result.returncode}")
            if result.stderr:
                print(result.stderr)
            return False, None, result.stdout or ""

        except subprocess.TimeoutExpired:
            print("erro: timeout na execucao do blender (limite: 10 minutos)")
            return False, None, ""
        except Exception as e:
            print(f"erro: {e}")
            return False, None, ""

    def open_blender_gui_with_blend(self, blend_file: Path) -> None:
        # atalho que resolve o executavel outra vez e delega em open blender with file
        exe = self.find_blender_executable()
        if exe:
            self.open_blender_with_file(exe, blend_file)
        else:
            print("aviso: blender nao encontrado para abrir o ficheiro")

    def run_pure_python_with_json_path(
        self,
        json_file: Path,
        out_stl: Optional[Path] = None,
        max_passos: int = 12000,
    ) -> Tuple[bool, Optional[Path]]:
        # esta funcao e o ponto unico para gerar geometria 3d
        # em modo pure python
        #
        # ela recebe um json que contem os parametros do leito
        # esse json pode ser um json compilado pelo antlr
        # ou pode ser um json criado no modo skip compile
        #
        # depois ela chama o modulo packed bed stl
        # esse modulo escolhe o gerador certo com base em packing method
        # depois ele faz validacao de colisoes e limites
        # e no final ele exporta um ficheiro stl
        from packed_bed_stl import generate_packed_bed_stl

        # resolve para um caminho absoluto
        # isso evita problemas quando o cwd muda
        json_file = Path(json_file).resolve()
        if not json_file.is_file():
            print(f"erro: json nao encontrado: {json_file}")
            return False, None
        if out_stl is None:
            # se o usuario nao escolheu destino usamos um nome derivado do json
            out_stl = (Path.cwd() / f"{json_file.stem}_pure.stl").resolve()
        else:
            # se foi passado destino usamos esse valor
            out_stl = Path(out_stl).resolve()
        # garantimos que a pasta destino existe
        out_stl.parent.mkdir(parents=True, exist_ok=True)
        try:
            # aqui ocorre a geracao de stl em python puro
            print(f"geracao python puro: json={json_file}")
            print(f"saida stl: {out_stl}")
            generate_packed_bed_stl(json_file, out_stl, max_passos=max_passos)
            print("sucesso: stl gerado em python puro")
            return True, out_stl
        except Exception as e:
            # em caso de erro devolvemos falha e nao bloqueamos o menu
            print(f"erro na geracao python pura: {e}")
            return False, None

    def open_blender_gui_with_stl(self, stl_file: Path) -> None:
        exe = self.find_blender_executable()
        if exe:
            self.open_blender_with_file(exe, stl_file)
        else:
            print("aviso: blender nao encontrado para abrir o stl")

    def execute_blender(self, open_after=False):
        # compatibilidade com fluxos antigos que assumem self output file bed
        # o json e sempre output file absoluto mais sufixo json
        # le export do json para montar lista de formatos
        bed_resolved = Path(self.output_file).resolve()
        json_file = Path(str(bed_resolved) + ".json")
        fmt = None
        if json_file.exists():
            try:
                import json as _json

                with open(json_file, "r", encoding="utf-8") as f:
                    fmt = export_formats_for_blender(_json.load(f).get("export") or {})
            except Exception:
                fmt = None
        ok, blend, _stdout = self.run_blender_with_json_path(
            json_file, open_after=open_after, formats=fmt
        )
        return ok, blend
    
    def open_blender_with_file(self, blender_exe, blend_file):
        """abrir blender com arquivo especifico em modo gui"""
        try:
            print(f"executando: {blender_exe} {blend_file}")
            
            # abrir blender em modo gui (sem --background)
            # usar Popen para nao bloquear o terminal
            subprocess.Popen([blender_exe, str(blend_file)], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            print("\nsucesso: blender aberto!")
            print("o blender esta rodando em segundo plano")
            print("voce pode fechar esta janela sem afetar o blender")
            
        except Exception as e:
            print(f"\nerro ao abrir blender: {e}")
            print(f"\nabra manualmente executando:")
            print(f"{blender_exe} {blend_file}")
    
    def tests_quick_menu(self) -> None:
        # delega no fluxo guiado wizard_quick_tests entrada backend modo execucao pos
        wizard_quick_tests_run(self)

    def show_help_menu(self):
        """mostrar menu de ajuda com informacoes sobre parametros"""
        self.clear_screen()
        self.print_header("ajuda", "parametros do arquivo .bed")
        self.ui.breadcrumbs("wizard", "ajuda")
        self.ui.hint("escolha 1-6 para ver campos da secao; 0 regressa ao menu principal.")
        
        sections = {
            '1': ('bed', 'geometria do leito'),
            '2': ('lids', 'tampas'),
            '3': ('particles', 'particulas'),
            '4': ('packing', 'empacotamento'),
            '5': ('export', 'exportacao'),
            '6': ('cfd', 'simulacao cfd')
        }
        
        entries = [(k, v[1]) for k, v in sections.items()]
        self.ui.render_help_section_menu(entries, back_key="0")
        choice = self.ui.ask_line("opcao (0-6): ").strip()
        
        if choice == "0" or choice.lower() in ("c", "cancel", "cancelar", "voltar"):
            return
        elif choice in sections:
            section_key, section_desc = sections[choice]
            self.clear_screen()
            self.print_header(f"ajuda: {section_desc}", "detalhes dos campos")
            self.ui.breadcrumbs("wizard", "ajuda", section_key)
            
            for param_key, param_info in sorted(self.param_help.items()):
                if param_key.startswith(f"{section_key}."):
                    param_name = param_key.split('.')[1]
                    lines = [
                        f"parametro: {param_name}",
                        f"descricao: {param_info['desc']}",
                    ]
                    if 'min' in param_info and 'max' in param_info:
                        unit = param_info.get('unit', '')
                        lines.append(f"range: {param_info['min']}{unit} .. {param_info['max']}{unit}")
                    if 'exemplo' in param_info:
                        lines.append(f"exemplo: {param_info['exemplo']}")
                    self.ui.param_help(lines)
            
            self.ui.pause()
            self.show_help_menu()
        else:
            self.ui.warn("opcao invalida")
            self.ui.pause()
            self.show_help_menu()
    
    def pipeline_completo_mode(self):
        """modo pipeline completo - gera modelo 3d, cria caso cfd e executa simulacao"""
        self.clear_screen()
        self.print_header("pipeline completo", "modelagem 3d + caso openfoam + simulacao")
        self.ui.breadcrumbs("wizard", "pipeline")
        self.ui.println("etapas resumidas:")
        self.ui.muted(
            "1) questionario do leito  2) gerar e compilar .bed  3) blender  "
            "4) caso openfoam  5) simulacao no wsl (longo)"
        )
        self._hint_controles_entrada()
        self.ui.println()
        self.ui.warn("tempo estimado 10-30 min | blender | wsl2 + openfoam | ~2 gb disco")
        self.ui.println()
        
        def _pipe_cancel() -> None:
            raise _WizardCancelled()

        try:
            continuar = self.ui.confirm(
                "deseja continuar?",
                default=False,
                cancel_callback=_pipe_cancel,
            )
        except _WizardCancelled:
            self.ui.muted("cancelado.")
            return
        if not continuar:
            self.ui.muted("operacao cancelada")
            return
        
        # usar questionario interativo para coletar parametros
        self.ui.section("etapa 1/5 — parametrizacao do leito")
        try:
            self._maybe_load_existing_bed(caption="pipeline completo")
            if not self.skip_questionnaire_after_load:
                self.interactive_questionnaire()
        except _WizardCancelled:
            self.ui.muted("cancelado. a voltar ao menu inicial")
            self.params = {}
            self.output_file = None
            return
        
        if not self.params:
            self.ui.err("parametros nao definidos")
            return
        
        # gerar arquivo .bed
        self.ui.section("etapa 2/5 — geracao e compilacao do .bed")
        
        _pipe_stem = "leito_pipeline"
        if self.skip_questionnaire_after_load and self.output_file:
            _pipe_stem = Path(self.output_file).stem
        try:
            output_name = self.ui.ask_line(
                "nome do arquivo .bed (sem extensao) [leito_pipeline]: ",
                default=_pipe_stem,
            ).strip()
            self._maybe_cancel(output_name)
        except _WizardCancelled:
            self.ui.muted("cancelado.")
            return
        if not output_name:
            output_name = _pipe_stem or "leito_pipeline"
        
        self.output_file = f"{output_name}.bed"
        
        if not self.generate_bed_file():
            self.ui.err("falha ao gerar arquivo .bed")
            return
        
        self.ui.section("compilando .bed")
        if not self.verify_and_compile():
            self.ui.err("falha na compilacao do arquivo .bed")
            return
        json_path = Path(str(Path(self.output_file).resolve()) + ".json")
        patch_compiled_json_packing(json_path, self.params)
        patch_compiled_json_export(json_path, self.params)
        patch_compiled_json_metadata(json_path, self.params)
        patch_compiled_json_slice(json_path, self.params)
        self.ui.ok(f"arquivo compilado: {json_path}")

        # gerar modelo 3d no blender
        self.ui.section("etapa 3/5 — modelo 3d no blender")
        fmt = export_formats_for_blender(self.params.get("export") or {})
        success, blend_file, _blender_out = self.run_blender_with_json_path(
            json_path, open_after=False, formats=fmt
        )
        
        if not success:
            self.ui.err("falha na geracao do modelo 3d")
            return
        
        self.ui.ok(f"modelo 3d: {blend_file}")
        
        # criar caso openfoam
        self.ui.section("etapa 4/5 — caso openfoam")
        
        success, case_dir = self.create_openfoam_case(json_path, blend_file)
        if not success:
            self.ui.err("falha na criacao do caso openfoam")
            return
        
        self.ui.ok(f"caso cfd: {case_dir}")
        
        # executar simulacao cfd
        self.ui.section("etapa 5/5 — simulacao cfd")
        
        success = self.run_openfoam_simulation(case_dir)
        if not success:
            self.ui.err("falha na execucao da simulacao cfd")
            return
        
        # resumo final
        self.ui.section("pipeline concluido")
        self.ui.ok("resumo dos artefatos:")
        self.ui.muted(f"  .bed: {self.output_file}")
        self.ui.muted(f"  json: {json_path}")
        self.ui.muted(f"  blend: {blend_file}")
        self.ui.muted(f"  caso: {case_dir}")
        self.ui.println()
        self.ui.muted("proximo passo: paraview — abrir caso.foam no diretorio do caso")
        self.ui.muted(f"  {case_dir / 'caso.foam'}")
    
    def create_openfoam_case(self, json_path, blend_file):
        """
        criar caso openfoam a partir do modelo blender
        
        returns:
            (success, case_dir) - tupla com sucesso e diretorio do caso
        """
        try:
            self.ui.println("")
            self.ui.muted("criando caso openfoam...")
            self.ui.muted("  [1/3] validando arquivos de entrada")
            
            # validar arquivos
            json_path = Path(json_path)
            blend_file = Path(blend_file)
            
            if not json_path.exists():
                self.ui.err(f"arquivo json nao encontrado: {json_path}")
                return False, None
            
            if not blend_file.exists():
                self.ui.err(f"arquivo blend nao encontrado: {blend_file}")
                return False, None
            
            self.ui.ok("  arquivos validados")
            
            # determinar diretorio de saida
            output_root = simulations_dir()
            output_root.mkdir(parents=True, exist_ok=True)
            
            # encontrar script de setup
            script_path = Path(__file__).parent.parent / "scripts" / "openfoam_scripts" / "setup_openfoam_case.py"
            
            if not script_path.exists():
                self.ui.err("script setup_openfoam_case.py nao encontrado")
                self.ui.muted(f"  procurado em: {script_path}")
                return False, None
            
            self.ui.muted("  [2/3] executando script de setup do openfoam")
            self.ui.muted(f"  script: {script_path}")
            self.ui.muted(f"  json: {json_path}")
            self.ui.muted(f"  blend: {blend_file}")
            self.ui.println()
            
            # executar script de setup (sem --run ainda)
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    str(json_path),
                    str(blend_file),
                    "--output-dir", str(output_root)
                ],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos
            )
            
            # mostrar saida do comando
            if result.stdout:
                self.ui.println(result.stdout)
            
            if result.returncode == 0:
                self.ui.ok("  caso openfoam criado com sucesso")
                
                # determinar diretorio do caso
                case_name = json_path.stem.replace('.bed', '')
                case_dir = output_root / case_name
                
                self.ui.muted(f"  [3/3] caso criado em: {case_dir}")
                
                return True, case_dir
            else:
                self.ui.err("falha na criacao do caso openfoam")
                self.ui.muted(f"  codigo de erro: {result.returncode}")
                if result.stderr:
                    self.ui.muted("  detalhes do erro:")
                    self.ui.println(result.stderr)
                return False, None
                
        except subprocess.TimeoutExpired:
            self.ui.err("timeout na criacao do caso (limite: 5 minutos)")
            return False, None
        except Exception as e:
            self.ui.err(f"erro inesperado: {e}")
            return False, None
    
    def run_openfoam_simulation(self, case_dir):
        """
        executar simulacao openfoam no wsl
        
        args:
            case_dir: diretorio do caso openfoam
            
        returns:
            success - boolean indicando sucesso
        """
        try:
            case_dir = Path(case_dir)
            
            if not case_dir.exists():
                self.ui.err(f"diretorio do caso nao encontrado: {case_dir}")
                return False
            
            self.ui.println("")
            self.ui.muted("executando simulacao cfd no wsl/ubuntu...")
            self.ui.warn("este processo pode levar varios minutos")
            self.ui.println()
            
            # converter caminho windows para wsl
            # C:\Users\... -> /mnt/c/Users/...
            wsl_path = str(case_dir).replace('\\', '/')
            if len(wsl_path) > 1 and wsl_path[1] == ':':
                drive = wsl_path[0].lower()
                wsl_path = f"/mnt/{drive}{wsl_path[2:]}"
            
            self.ui.muted(f"  caminho wsl: {wsl_path}")
            self.ui.println()
            
            # verificar se wsl esta instalado
            self.ui.muted("  [1/4] verificando wsl...")
            result = subprocess.run(
                ["wsl", "--list", "--quiet"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.ui.err("wsl nao esta instalado ou configurado")
                self.ui.muted("  instale o wsl2 com ubuntu e openfoam")
                return False
            
            self.ui.ok("  wsl detectado")
            
            # executar script Allrun no wsl
            self.ui.muted("  [2/4] executando ./Allrun no wsl...")
            self.ui.muted(f"  diretorio: {wsl_path}")
            self.ui.println()
            
            # comando para executar no wsl
            wsl_command = f"cd '{wsl_path}' && chmod +x Allrun && ./Allrun"
            
            self.ui.muted(f"  comando: {wsl_command}")
            self.ui.println()
            self.ui.muted("  aguarde... (isto pode levar 10-30 minutos)")
            self.ui.muted("  " + "=" * 50)
            self.ui.println()
            
            # executar com output em tempo real
            process = subprocess.Popen(
                ["wsl", "bash", "-c", wsl_command],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # mostrar output em tempo real
            for line in process.stdout:
                self.ui.println(f"  {line.rstrip()}")
            
            # aguardar conclusao
            return_code = process.wait()
            
            self.ui.println()
            self.ui.muted("  " + "=" * 50)
            self.ui.println()
            
            if return_code == 0:
                self.ui.ok("  [3/4] simulacao concluida com sucesso")
                
                # verificar se arquivo de resultados existe
                self.ui.muted("  [4/4] verificando resultados...")
                
                # criar arquivo .foam para paraview
                foam_file = case_dir / "caso.foam"
                foam_file.touch()
                
                self.ui.ok(f"  arquivo paraview criado: {foam_file}")
                self.ui.println()
                self.ui.muted("  resultados disponiveis em:")
                self.ui.muted(f"  {case_dir}")
                
                return True
            else:
                self.ui.err(f"  [3/4] simulacao falhou com codigo {return_code}")
                self.ui.println()
                self.ui.muted("  verifique os logs em:")
                self.ui.muted(f"  {case_dir}/log.*")
                
                return False
                
        except subprocess.TimeoutExpired:
            self.ui.err("timeout na verificacao do wsl")
            return False
        except FileNotFoundError:
            self.ui.err("comando 'wsl' nao encontrado")
            self.ui.muted("  instale o wsl2 no windows")
            return False
        except Exception as e:
            self.ui.err(f"erro inesperado: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def show_documentation(self, standalone: bool = False) -> None:
        """mostra documentacao (extraida do html) paginada neste terminal."""
        from wizard_doc_terminal import html_file_to_plain, paginate_plain

        doc_path = Path(__file__).parent / "documentacao.html"
        if not doc_path.exists():
            self.ui.err("arquivo de documentacao nao encontrado")
            self.ui.muted(f"caminho esperado: {doc_path}")
            self.ui.pause()
            return
        
        texto = html_file_to_plain(doc_path)
        paginas = paginate_plain(texto, lines_per_page=32)
        total = len(paginas)
        idx = 0
        edge_msg = ""
        while idx < total:
            self.clear_screen()
            self.print_header(
                "documentacao",
                "texto extraido do html — teclas: p pagina anterior, enter ou n seguinte, q sair",
            )
            self.ui.breadcrumbs("wizard", "documentacao")
            if edge_msg:
                self.ui.warn(edge_msg)
                edge_msg = ""
            bloco = paginas[idx]
            is_last = idx >= total - 1
            if is_last:
                ctl = (
                    "ultima pagina — enter fecha."
                    if standalone
                    else "ultima pagina — enter volta ao menu principal."
                )
            else:
                ctl = (
                    "enter ou n = pagina seguinte | p = pagina anterior | q = sair"
                )
            self.ui.render_documentation_page(bloco, idx, total, ctl)
            if is_last:
                fim = (
                    "enter para sair..."
                    if standalone
                    else "enter para voltar ao menu principal..."
                )
                self.ui.pause(fim)
                break
            raw = self.ui.ask_line("acao (enter/n/p/q): ", default="n").strip().lower()
            if raw == "q":
                break
            if raw == "p":
                if idx > 0:
                    idx -= 1
                else:
                    edge_msg = "ja esta na primeira pagina."
                continue
            idx += 1

    def _draw_start_menu(self) -> None:
        """submenu comecar (fluxos operacionais)."""
        self.ui.clear()
        self.ui.header(
            self._t("app.title", "wizard de parametrizacao"),
            self._t("app.subtitle", "leitos empacotados — arquivos .bed / antlr / blender / openfoam"),
        )
        self.ui.breadcrumbs("wizard", self._t("menu.title.start", "comecar"))
        if not rich_available():
            self.ui.hint("instale rich para cores e tabelas: pip install rich")
            self.ui.println()
        if not prompt_toolkit_available():
            self.ui.hint(
                "opcional: pip install prompt_toolkit — edicao de linha tipo ide "
                "(setas, historico, tab)."
            )
            self.ui.println()
        self.ui.render_main_menu(self._start_menu_rows(), title=self._t("menu.title.start", "comecar"))

    def run_start_menu(self) -> None:
        """loop do submenu comecar ate o utilizador escolher 0 voltar."""
        while True:
            self._draw_start_menu()
            choice = self.ui.ask_line(self._t("prompt.start.choice", "opcao (0-5): ")).strip()
            if choice.lower() in ("c", "cancel", "cancelar", "voltar"):
                return
            if choice == "0":
                return
            try:
                if choice == "1":
                    self.smart_start_flow()
                elif choice == "2":
                    self.interactive_mode()
                elif choice == "3":
                    self.templates_e_testes_menu()
                elif choice == "4":
                    self.blender_generation_mode()
                elif choice == "5":
                    self.pipeline_completo_mode()
                else:
                    self.ui.warn("escolha um numero de 0 a 5")
                    self.ui.pause("enter...")
                    continue
            except _WizardCancelled:
                self.ui.muted("cancelado.")
            self.ui.pause("enter para voltar ao submenu comecar...")

    def templates_e_testes_menu(self) -> None:
        """une templates/editor com testes rapidos (submenu)."""
        while True:
            self.clear_screen()
            self.print_header(
                "templates, editor e testes rapidos",
                "escolha o fluxo desejado",
            )
            self.ui.breadcrumbs("wizard", "comecar", "templates-testes")
            self.ui.println()
            try:
                fluxo = self.get_choice(
                    "fluxo",
                    [
                        "carregar template json (dsl/wizard_templates)",
                        "editor .bed classico (template + editor externo)",
                        "testes rapidos (ficheiro .bed ou .json ja existente)",
                        "voltar ao submenu comecar",
                    ],
                    3,
                )
            except _WizardCancelled:
                return
            if fluxo.startswith("voltar"):
                return
            try:
                if fluxo.startswith("testes"):
                    self.tests_quick_menu()
                    self.ui.pause("enter para voltar...")
                    continue
                if fluxo.startswith("carregar"):
                    self.template_mode(prefer="json")
                    self.ui.pause("enter para voltar...")
                    continue
                if fluxo.startswith("editor"):
                    self.template_mode(prefer="editor")
                    self.ui.pause("enter para voltar...")
                    continue
            except _WizardCancelled:
                self.ui.muted("cancelado.")
                continue
            self.ui.warn("opcao nao reconhecida")
            self.ui.pause("enter...")

    def smart_start_flow(self) -> None:
        """assistente curto: encaminha para questionario, 3d no blender ou pipeline."""
        self.clear_screen()
        self.print_header(
            "assistente inteligente",
            "encaminhamento rapido (os modos explicitos continuam no submenu)",
        )
        self.ui.breadcrumbs("wizard", "comecar", "assistente")
        self.ui.println()
        try:
            objetivo = self.get_choice(
                "o que pretende fazer agora",
                [
                    "gerar .bed com questionario completo (cfd opcional)",
                    "gerar modelo 3d sem cfd (mesmo questionario que o modo blender)",
                    "pipeline completo (questionario + blender + openfoam no wsl)",
                ],
                0,
            )
            if objetivo.startswith("gerar .bed"):
                self.interactive_mode()
                return
            if objetivo.startswith("gerar modelo 3d"):
                backend = self.get_choice(
                    "backend preferido para o modelo 3d",
                    [
                        "blender (recomendado para o leito completo neste projeto)",
                        "python puro (gera .bed no questionario; depois use testes rapidos com o .json)",
                    ],
                    0,
                )
                if backend.startswith("blender"):
                    self.blender_generation_mode()
                else:
                    self.ui.hint(
                        "fluxo sugerido: questionario interativo para gerar e compilar o .bed; "
                        "depois menu comecar > templates e testes > testes rapidos com o .json."
                    )
                    self.ui.println()
                    self.interactive_mode()
                return
            if objetivo.startswith("pipeline"):
                self.ui.warn(
                    "requer blender, wsl2 e openfoam; tempo longo e uso elevado de disco."
                )
                if self.get_boolean("confirmo requisitos e quero continuar", default=False):
                    self.pipeline_completo_mode()
                else:
                    self.ui.muted("cancelado no assistente.")
                return
            self.ui.warn("opcao nao reconhecida no assistente.")
        except _WizardCancelled:
            self.ui.muted("cancelado.")
    
    def _draw_main_menu(self) -> None:
        """tela inicial estilo navegador (barra + tabela de modos)."""
        self.ui.clear()
        self.ui.header(
            self._t("app.title", "wizard de parametrizacao"),
            self._t("app.subtitle", "leitos empacotados — arquivos .bed / antlr / blender / openfoam"),
        )
        if not rich_available():
            self.ui.hint("instale rich para cores e tabelas: pip install rich")
            self.ui.println()
        if not prompt_toolkit_available():
            self.ui.hint(
                "opcional: pip install prompt_toolkit — edicao de linha tipo ide "
                "(setas, historico, tab)."
            )
            self.ui.println()
        self.ui.render_main_menu(self._main_menu_rows(), title=self._t("menu.title.main", "opcoes"))

    def language_mode(self) -> None:
        self.clear_screen()
        self.print_header(self._t("lang.header", "idioma"), self._t("lang.subtitle", "trocar idioma do wizard"))
        self.ui.breadcrumbs("wizard", self._t("lang.header", "idioma"))
        self.ui.println()
        cur = self._t("lang.pt", "portugues") if self.lang == "pt" else self._t("lang.en", "ingles")
        self.ui.muted(f"{self._t('lang.current', 'idioma atual')}: {cur}")
        self.ui.println()
        try:
            pick = self.get_choice(
                self._t("lang.choose", "escolha o idioma"),
                [self._t("lang.pt", "portugues"), self._t("lang.en", "ingles")],
                0 if self.lang == "pt" else 1,
            )
        except _WizardCancelled:
            self.ui.muted("cancelado.")
            return
        self.lang = "pt" if pick == self._t("lang.pt", "portugues") else "en"
        self.ui.ok(self._t("lang.ok", "idioma atualizado"))

    def visualization_3d_mode(self) -> None:
        from wizard_3d_viewer import run_visualization_mode

        run_visualization_mode(self)
    
    def run(self):
        """executar wizard"""
        while True:
            self._draw_main_menu()
            choice = self.ui.ask_line(self._t("prompt.main.choice", "opcao (1-6): ")).strip()
            if choice.lower() in ("c", "cancel", "cancelar", "voltar"):
                self.ui.muted("no menu principal nao ha nivel acima; use 6 para sair.")
                self.ui.pause("enter...")
                continue
            
            if choice == "1":
                self.run_start_menu()
                self.ui.pause("enter para voltar ao menu principal...")
            elif choice == "2":
                self.visualization_3d_mode()
                self.ui.pause("enter para voltar ao menu principal...")
            elif choice == "3":
                self.show_help_menu()
            elif choice == "4":
                self.show_documentation()
            elif choice == "5":
                self.language_mode()
                self.ui.pause("enter para voltar ao menu principal...")
            elif choice == "6":
                self.ui.muted("ate logo!")
                sys.exit(0)
            else:
                self.ui.warn("escolha um numero de 1 a 6")
                self.ui.pause("enter para voltar ao menu...")

def main():
    """entrada unifica typer rich comandos e legado argparse via dispatch main"""
    if str(_DSL_DIR) not in sys.path:
        sys.path.insert(0, str(_DSL_DIR))
    from cli.app import dispatch_main

    sys.exit(dispatch_main())

# quando executas python bed wizard py diretamente este bloco corre
# quando importas bed wizard como modulo este bloco nao corre
if __name__ == "__main__":
    main()
