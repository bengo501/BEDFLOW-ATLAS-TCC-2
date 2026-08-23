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
import signal
import shlex
import subprocess  # para executar comandos externos (editores, compilador)
import tempfile  # para criar arquivos temporarios
import time
import webbrowser
from pathlib import Path  # para trabalhar com caminhos de arquivos
# dict mapeia chave string para valor qualquer
# any aceita qualquer tipo quando o valor e misto
# list sequencia ordenada por exemplo lista de strings do menu
# optional t significa valor do tipo t ou none quando algo e opcional
# tuple par ou tupla fixa por exemplo atalho titulo descricao do menu
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

# pasta onde este ficheiro bed wizard py vive normalmente dsl na raiz do repo
_DSL_DIR = Path(__file__).resolve().parent
if str(_DSL_DIR) not in sys.path:
    sys.path.insert(0, str(_DSL_DIR))
# raiz do repositorio um nivel acima de dsl usada para achar scripts blender
_REPO_ROOT = _DSL_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
from bedflow_local_paths import beds_dir, local_data_root, models_3d_dir, simulations_dir
# caminho para packed bed science e leito extracao dentro de scripts blender scripts
_BLENDER_SCRIPTS = _REPO_ROOT / "scripts" / "blender_scripts"
# inserir esse caminho no inicio de sys path para importar packed bed science como pacote
if str(_BLENDER_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_BLENDER_SCRIPTS))
# gerador stl python puro packed bed stl
_PY_MODEL = _REPO_ROOT / "scripts" / "python_modeling"
if str(_PY_MODEL) not in sys.path:
    sys.path.insert(0, str(_PY_MODEL))
# garantir que dsl_dir tenha prioridade sobre a raiz do repo em sys.path. sem
# isto, "import bed_wizard" (usado em dsl/cli/app.py) pode resolver para o
# atalho bed_wizard.py da raiz (que nao define BedWizard) quando o wizard e
# executado a partir da pasta dsl.
if str(_DSL_DIR) in sys.path:
    sys.path.remove(str(_DSL_DIR))
sys.path.insert(0, str(_DSL_DIR))
from bed_config import normalize_generation_backend

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
    patch_compiled_json_bed,
    patch_compiled_json_export,
    patch_compiled_json_slice,
    patch_compiled_json_statistical,
    patch_compiled_json_metadata,
    patch_compiled_json_packing,
    resolve_repo_path,
)
# listar nomes de templates json e carregar um template por nome
from wizard_quick_tests import run as wizard_quick_tests_run
from param_help_en import PARAM_HELP_EN
from wizard_template_engine import (
    list_saved_template_names,
    list_template_names,
    load_saved_template,
    load_template,
    save_saved_template,
    saved_templates_dir,
)
from wizard_terminal_ui import (
    MenuRow,
    _internal_prompt_aux_lines,
    global_keys_hint,
    make_terminal_ui,
    prompt_toolkit_available,
    render_menu_table_plain,
    render_menu_table_rich,
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
            "app.title": "setup de parametrizacao",
            "app.subtitle": "leitos empacotados — arquivos .bed / antlr / blender / openfoam",
            "menu.title.main": "opcoes",
            "menu.title.start": "comecar",
            "menu.main.start.title": "comecar",
            "menu.main.start.desc": "criar, templates, testes rapidos, visualizacao 3d, simulacao cfd guardada",
            "menu.main.webapp.title": "comecar aplicacao web",
            "menu.main.webapp.desc": "submenu para subir ou parar api (uvicorn) e interface (vite) em segundo plano",
            "menu.main.view3d.title": "visualizacao 3d",
            "menu.main.view3d.desc": "listar malhas geradas; ver no browser (three.js), open3d ou blender",
            "menu.main.help.title": "ajuda",
            "menu.main.help.desc": "resumo dos parametros do ficheiro .bed por secao",
            "menu.main.docs.title": "documentacao",
            "menu.main.docs.desc": "guia do projeto neste terminal (texto extraido do html)",
            "menu.main.lang.title": "idioma",
            "menu.main.lang.desc": "trocar portugues/ingles",
            "menu.main.exit.title": "sair",
            "menu.main.exit.desc": "encerrar o setup",
            "menu.start.create.title": "criar",
            "menu.start.create.desc": "criar basico, geracao 3d ou pipeline completo (um unico fluxo por opcao)",
            "create.subtitle": "escolha criar basico, geracao 3d ou pipeline completo",
            "create.prompt": "fluxo:",
            "menu.start.q.title": "criar basico",
            "menu.start.q.desc": "passo a passo; gera .bed; cfd opcional; export configuravel",
            "menu.start.tpl.title": "templates e editor",
            "menu.start.tpl.desc": "templates embutidos ou salvos em local_data; editar .bed antes de gravar e compilar",
            "menu.start.quick.title": "testes rapidos",
            "menu.start.quick.desc": "validar json ou .bed existente; preview rich; python puro ou blender; sem misturar com templates",
            "menu.start.blender.title": "geracao 3d",
            "menu.start.blender.desc": "sem cfd; primeiro escolhes blender ou python; mesmo questionario; compila e gera no fim",
            "menu.start.pipe.title": "pipeline completo",
            "menu.start.pipe.desc": "bed + blender + caso openfoam + simulacao no wsl; longo; requisitos elevados",
            "menu.start.cfd.title": "simulacao cfd",
            "menu.start.cfd.desc": "casos openfoam em local_data/simulations; executar no wsl",
            "cfd.list.title": "casos em local_data/simulations",
            "cfd.pick_hint": "numero da lista, caminho absoluto/relativo, ou l para rever a tabela.",
            "cfd.pick_prompt": "caso (numero ou caminho): ",
            "cfd.confirm_run": "executar simulacao openfoam neste caso (wsl, pode demorar)?",
            "cfd.warn_none": "nenhum caso encontrado (pastas com Allrun ou system/controlDict).",
            "cfd.done": "simulacao terminada; veja log.* e caso.foam no diretorio do caso.",
            "cfd.err_failed": "falha na simulacao.",
            "menu.start.back.title": "voltar",
            "menu.start.back.desc": "regressa ao menu principal",
            "prompt.main.choice": "opcao (1-5 ou 0 sair, h ajuda): ",
            "main.warn_empty": "indique 1 a 5 ou 0 para sair.",
            "webapp.title": "aplicacao web (dev)",
            "webapp.subtitle": "uvicorn backend.app.main:app em :8000 e npm run dev (vite) em :5173; no windows cada servico abre numa consola nova com os logs; saida nao e misturada com este menu",
            "webapp.actions": "accoes",
            "webapp.prompt": "opcao (0-9, c voltar, h ajuda): ",
            "webapp.back_row": "0 ou c regressa ao menu principal",
            "webapp.warn_invalid": "indique 0 a 9 ou c para voltar.",
            "webapp.status.back.on": "backend (uvicorn :8000): em execucao, pid {pid}",
            "webapp.status.back.off": "backend: parado",
            "webapp.status.front.on": "frontend (vite :5173): em execucao, pid {pid}",
            "webapp.status.front.off": "frontend: parado",
            "webapp.opt.both_start.t": "iniciar backend e frontend",
            "webapp.opt.both_start.d": "sobe uvicorn e npm run dev em segundo plano",
            "webapp.opt.back_start.t": "iniciar so backend",
            "webapp.opt.back_start.d": "so uvicorn na raiz do repo",
            "webapp.opt.front_start.t": "iniciar so frontend",
            "webapp.opt.front_start.d": "so vite em frontend/ (precisa de npm no path)",
            "webapp.opt.back_stop.t": "parar backend",
            "webapp.opt.back_stop.d": "termina o processo uvicorn (arvore no windows)",
            "webapp.opt.front_stop.t": "parar frontend",
            "webapp.opt.front_stop.d": "termina o processo npm/vite",
            "webapp.opt.both_stop.t": "parar backend e frontend",
            "webapp.opt.both_stop.d": "para os dois servicos",
            "webapp.opt.back_restart.t": "reiniciar backend",
            "webapp.opt.back_restart.d": "parar e voltar a iniciar so o uvicorn",
            "webapp.opt.front_restart.t": "reiniciar frontend",
            "webapp.opt.front_restart.d": "parar e voltar a iniciar so o vite",
            "webapp.opt.both_restart.t": "reiniciar backend e frontend",
            "webapp.opt.both_restart.d": "reinicia os dois em sequencia",
            "webapp.ok_start_back": "backend iniciado.",
            "webapp.ok_start_front": "frontend iniciado.",
            "webapp.ok_start_both": "backend e frontend iniciados.",
            "webapp.ok_stop_back": "backend terminado.",
            "webapp.ok_stop_front": "frontend terminado.",
            "webapp.ok_stop_both": "backend e frontend terminados.",
            "webapp.muted_idle_back": "backend ja estava parado.",
            "webapp.muted_idle_front": "frontend ja estava parado.",
            "webapp.warn_back_running": "backend ja esta em execucao.",
            "webapp.warn_front_running": "frontend ja esta em execucao.",
            "webapp.err_no_npm": "comando npm nao encontrado no path.",
            "webapp.err_start_back": "falha ao iniciar backend: {err}",
            "webapp.err_start_front": "falha ao iniciar frontend: {err}",
            "main.warn_exit_key": "use 0 para sair da aplicacao.",
            "main.bye": "ate logo!",
            "prompt.start.choice": "opcao (0-5, h ajuda): ",
            "lang.header": "idioma",
            "lang.subtitle": "trocar idioma do setup",
            "lang.current": "idioma atual",
            "lang.choose": "escolha o idioma",
            "lang.pt": "portugues",
            "lang.en": "ingles",
            "lang.ok": "idioma atualizado",
            "help.title": "ajuda",
            "help.subtitle": "parametros do arquivo .bed",
            "help.top_hint": "escolha 1-7 para ver cada seccao ou visualizacao 3d; 0 regressa ao menu principal; h ajuda global.",
            "help.prompt": "opcao (1-7, 0 voltar, h ajuda): ",
            "help.use0": "use 0 para regressar ao menu principal.",
            "help.detail_sub": "detalhes dos campos",
            "help.view3d_title": "ajuda: visualizacao 3d",
            "help.view3d_subtitle": "modos web, desktop e blender",
            "help.sec.bed": "geometria do leito",
            "help.sec.lids": "tampas",
            "help.sec.particles": "particulas",
            "help.sec.packing": "empacotamento",
            "help.sec.export": "exportacao",
            "help.sec.cfd": "simulacao cfd",
            "help.sec.view3d": "visualizacao 3d (modos e formatos)",
            "docs.title": "documentacao",
            "docs.page_panel_title": "{heading} — pagina {n}/{total}",
            "docs.subtitle": "texto extraido do html — teclas no rodape desta pagina",
            "docs.ctl_last_standalone": "ultima pagina — prima enter para fechar.",
            "docs.ctl_last_menu": "ultima pagina — prima enter para voltar ao menu principal.",
            "docs.ctl_nav": "c sair · ? ajuda do campo · h ajuda global · enter ou n pagina seguinte · p pagina anterior",
            "docs.pause_exit_standalone": "enter para sair...",
            "docs.pause_exit_menu": "enter para voltar ao menu principal...",
            "docs.action_prompt": "acao: ",
            "docs.edge_first": "ja esta na primeira pagina.",
            "docs.field_help": "documentacao: enter ou n avanca; p recua; c ou q termina; h mostra ajuda global do setup.",
            "docs.err_missing": "arquivo de documentacao nao encontrado",
            "docs.err_expected": "caminho esperado",
            "help.detail_prefix": "ajuda:",
            "help.invalid": "opcao invalida",
            "help.field.param": "parametro:",
            "help.field.description": "descricao:",
            "help.field.range": "range:",
            "help.field.example": "exemplo:",
            "help.pause_continue": "pressione enter para continuar...",
            "view3d.title": "visualizacao 3d",
            "view3d.subtitle": "malhas geradas pelo projeto (python, blender, pipeline)",
            "view3d.crumb": "visualizacao 3d",
            "view3d.search": "pesquisar:",
            "view3d.scan_hint": "origem da lista: scan em local_data/models_3d (prioridade), depois aux, simulations, generated/* e ficheiros *.stl/*.obj/*.blend na raiz do repo (ver bedflow_local_paths.scan_project_mesh_files).",
            "view3d.footer_hint": "0 ou c voltar ao submenu comecar  ·  l lista  ·  ? ajuda do campo  ·  h ajuda global",
            "view3d.table_title": "modelos",
            "view3d.pick": "numero do modelo:",
            "view3d.preview": "resumo",
            "view3d.choose_dest": "onde visualizar",
            "view3d.opt.web": "navegador (three.js no frontend)",
            "view3d.opt.desktop": "visualizador desktop (open3d: stl/obj/ply)",
            "view3d.opt.blender": "abrir no blender",
            "view3d.opt.back": "voltar a lista",
            "view3d.warn_none": "nenhuma malha encontrada em local_data/models_3d, generated/3d/output, simulations, aux ou batch. gere um modelo primeiro.",
            "view3d.warn_pick_idx": "indique um numero da lista ou 0/c para voltar a pesquisa.",
            "view3d.warn_num_invalid": "numero invalido",
            "view3d.err_path_invalid": "caminho invalido",
            "view3d.warn_blend_web": "ficheiro .blend nao carrega no three.js diretamente. exporte gltf/glb ou use blender.",
            "view3d.warn_web_fmt": "formato nao suportado no visualizador web.",
            "view3d.warn_api": "api nao respondeu em {api}. inicie: uvicorn backend.app.main:app e o frontend (npm run dev). url usada: {fe}",
            "view3d.warn_blend_desk": "use a opcao blender para ficheiros .blend.",
            "view3d.err_script": "script nao encontrado: {path}",
            "view3d.warn_open3d": "open3d nao disponivel: na raiz do repo execute pip install -r requirements-visualizacao.txt (no windows pode precisar de caminhos longos ou venv curto — ver comentarios nesse ficheiro)",
            "view3d.warn_viewer_rc": "visualizador terminou com codigo {rc}",
            "view3d.warn_blender_missing": "blender nao encontrado no path.",
            "view3d.col.file": "ficheiro",
            "view3d.col.format": "formato",
            "view3d.col.size": "tamanho",
            "view3d.col.origin": "origem",
            "view3d.col.rec": "recomendado",
            "view3d.ok_opening": "abrindo: {url}",
            "view3d.exec_viewer": "executando: python {script} {path}",
        },
        "en": {
            "app.title": "parameter setup",
            "app.subtitle": "packed beds — .bed / antlr / blender / openfoam",
            "menu.title.main": "options",
            "menu.title.start": "start",
            "menu.main.start.title": "start",
            "menu.main.start.desc": "create, templates, quick tests, 3d mesh viewer, run saved cfd case",
            "menu.main.webapp.title": "web app",
            "menu.main.webapp.desc": "submenu to start or stop the api (uvicorn) and ui (vite) in the background",
            "menu.main.view3d.title": "3d visualization",
            "menu.main.view3d.desc": "list generated meshes; open in browser (three.js), open3d or blender",
            "menu.main.help.title": "help",
            "menu.main.help.desc": "summary of .bed parameters by section",
            "menu.main.docs.title": "documentation",
            "menu.main.docs.desc": "project guide in this terminal (text extracted from html)",
            "menu.main.lang.title": "language",
            "menu.main.lang.desc": "toggle portuguese/english",
            "menu.main.exit.title": "exit",
            "menu.main.exit.desc": "close setup",
            "menu.start.create.title": "create",
            "menu.start.create.desc": "basic create, 3d generation, or full pipeline (one flow per choice)",
            "create.subtitle": "choose basic create, 3d generation, or full pipeline",
            "create.prompt": "flow:",
            "menu.start.q.title": "basic create",
            "menu.start.q.desc": "step-by-step; generates .bed; optional cfd; configurable export",
            "menu.start.tpl.title": "templates and editor",
            "menu.start.tpl.desc": "built-in or saved templates in local_data; edit .bed before save and compile",
            "menu.start.quick.title": "quick tests",
            "menu.start.quick.desc": "validate existing json or .bed; rich preview; pure python or blender; separate from templates",
            "menu.start.blender.title": "3d generation",
            "menu.start.blender.desc": "no cfd; pick blender or python first; same questionnaire; compile and generate at end",
            "menu.start.pipe.title": "full pipeline",
            "menu.start.pipe.desc": "bed + blender + openfoam case + wsl simulation; long; heavy requirements",
            "menu.start.cfd.title": "cfd simulation",
            "menu.start.cfd.desc": "openfoam cases under local_data/simulations; run in wsl",
            "cfd.list.title": "cases under local_data/simulations",
            "cfd.pick_hint": "list index, absolute/relative path, or l to show the table again.",
            "cfd.pick_prompt": "case (number or path): ",
            "cfd.confirm_run": "run openfoam simulation for this case in wsl (may take a long time)?",
            "cfd.warn_none": "no case found (folders with Allrun or system/controlDict).",
            "cfd.done": "simulation finished; see log.* and caso.foam in the case directory.",
            "cfd.err_failed": "simulation failed.",
            "menu.start.back.title": "back",
            "menu.start.back.desc": "return to main menu",
            "prompt.main.choice": "choice (1-5 or 0 exit, h help): ",
            "main.warn_empty": "enter 1 to 5 or 0 to exit.",
            "webapp.title": "web app (dev)",
            "webapp.subtitle": "uvicorn backend.app.main:app on :8000 and npm run dev (vite) on :5173; on windows each service opens in a new console with logs; output is not mixed into this menu",
            "webapp.actions": "actions",
            "webapp.prompt": "option (0-9, c back, h help): ",
            "webapp.back_row": "0 or c return to main menu",
            "webapp.warn_invalid": "enter 0 to 9 or c to go back.",
            "webapp.status.back.on": "backend (uvicorn :8000): running, pid {pid}",
            "webapp.status.back.off": "backend: stopped",
            "webapp.status.front.on": "frontend (vite :5173): running, pid {pid}",
            "webapp.status.front.off": "frontend: stopped",
            "webapp.opt.both_start.t": "start backend and frontend",
            "webapp.opt.both_start.d": "starts uvicorn and npm run dev in the background",
            "webapp.opt.back_start.t": "start backend only",
            "webapp.opt.back_start.d": "uvicorn only from repo root",
            "webapp.opt.front_start.t": "start frontend only",
            "webapp.opt.front_start.d": "vite in frontend/ (npm must be on path)",
            "webapp.opt.back_stop.t": "stop backend",
            "webapp.opt.back_stop.d": "terminates uvicorn (process tree on windows)",
            "webapp.opt.front_stop.t": "stop frontend",
            "webapp.opt.front_stop.d": "terminates npm/vite",
            "webapp.opt.both_stop.t": "stop backend and frontend",
            "webapp.opt.both_stop.d": "stops both services",
            "webapp.opt.back_restart.t": "restart backend",
            "webapp.opt.back_restart.d": "stop and start uvicorn only",
            "webapp.opt.front_restart.t": "restart frontend",
            "webapp.opt.front_restart.d": "stop and start vite only",
            "webapp.opt.both_restart.t": "restart backend and frontend",
            "webapp.opt.both_restart.d": "restarts both in sequence",
            "webapp.ok_start_back": "backend started.",
            "webapp.ok_start_front": "frontend started.",
            "webapp.ok_start_both": "backend and frontend started.",
            "webapp.ok_stop_back": "backend stopped.",
            "webapp.ok_stop_front": "frontend stopped.",
            "webapp.ok_stop_both": "backend and frontend stopped.",
            "webapp.muted_idle_back": "backend was already stopped.",
            "webapp.muted_idle_front": "frontend was already stopped.",
            "webapp.warn_back_running": "backend is already running.",
            "webapp.warn_front_running": "frontend is already running.",
            "webapp.err_no_npm": "npm not found on path.",
            "webapp.err_start_back": "failed to start backend: {err}",
            "webapp.err_start_front": "failed to start frontend: {err}",
            "main.warn_exit_key": "use 0 to exit the application.",
            "main.bye": "goodbye!",
            "prompt.start.choice": "choice (0-5, h help): ",
            "lang.header": "language",
            "lang.subtitle": "change setup language",
            "lang.current": "current language",
            "lang.choose": "choose language",
            "lang.pt": "portuguese",
            "lang.en": "english",
            "lang.ok": "language updated",
            "help.title": "help",
            "help.subtitle": ".bed file parameters",
            "help.top_hint": "choose 1-7 for each section or 3d view; 0 returns to main menu; h global help.",
            "help.prompt": "option (1-7, 0 back, h help): ",
            "help.use0": "use 0 to return to the main menu.",
            "help.detail_sub": "field details",
            "help.view3d_title": "help: 3d visualization",
            "help.view3d_subtitle": "web, desktop and blender modes",
            "help.sec.bed": "bed geometry",
            "help.sec.lids": "lids",
            "help.sec.particles": "particles",
            "help.sec.packing": "packing",
            "help.sec.export": "export",
            "help.sec.cfd": "cfd simulation",
            "help.sec.view3d": "3d visualization (modes and formats)",
            "docs.title": "documentation",
            "docs.page_panel_title": "{heading} — page {n}/{total}",
            "docs.subtitle": "text extracted from html — keys in the footer of this page",
            "docs.ctl_last_standalone": "last page — press enter to close.",
            "docs.ctl_last_menu": "last page — press enter to return to the main menu.",
            "docs.ctl_nav": "c exit · ? field help · h global help · enter or n next page · p previous page",
            "docs.pause_exit_standalone": "enter to exit...",
            "docs.pause_exit_menu": "enter to return to the main menu...",
            "docs.action_prompt": "action: ",
            "docs.edge_first": "already on the first page.",
            "docs.field_help": "documentation: enter or n forward; p back; c or q quit; h shows global setup help.",
            "docs.err_missing": "documentation file not found",
            "docs.err_expected": "expected path",
            "help.detail_prefix": "help:",
            "help.invalid": "invalid option",
            "help.field.param": "parameter:",
            "help.field.description": "description:",
            "help.field.range": "range:",
            "help.field.example": "example:",
            "help.pause_continue": "press enter to continue...",
            "view3d.title": "3d visualization",
            "view3d.subtitle": "meshes from python, blender or full pipeline",
            "view3d.crumb": "3d view",
            "view3d.search": "search:",
            "view3d.scan_hint": "list source: scan local_data/models_3d first, then aux, simulations, generated/* and mesh files at repo root (see bedflow_local_paths.scan_project_mesh_files).",
            "view3d.footer_hint": "0 or c back to start submenu  ·  l list  ·  ? field help  ·  h global help",
            "view3d.table_title": "models",
            "view3d.pick": "model number:",
            "view3d.preview": "summary",
            "view3d.choose_dest": "open in",
            "view3d.opt.web": "browser (three.js)",
            "view3d.opt.desktop": "desktop viewer (open3d: stl/obj/ply)",
            "view3d.opt.blender": "open in blender",
            "view3d.opt.back": "back to list",
            "view3d.warn_none": "no meshes found under local_data/models_3d, generated/3d/output, simulations, aux or batch. generate a model first.",
            "view3d.warn_pick_idx": "enter a list number or 0/c to return to search.",
            "view3d.warn_num_invalid": "invalid number",
            "view3d.err_path_invalid": "invalid path",
            "view3d.warn_blend_web": ".blend does not load in three.js directly. export gltf/glb or use blender.",
            "view3d.warn_web_fmt": "format not supported in the web viewer.",
            "view3d.warn_api": "api did not respond at {api}. start: uvicorn backend.app.main:app and the frontend (npm run dev). url used: {fe}",
            "view3d.warn_blend_desk": "use the blender option for .blend files.",
            "view3d.err_script": "script not found: {path}",
            "view3d.warn_open3d": "open3d unavailable: at repo root run pip install -r requirements-visualizacao.txt (on windows you may need long paths or a short venv — see comments in that file)",
            "view3d.warn_viewer_rc": "viewer exited with code {rc}",
            "view3d.warn_blender_missing": "blender not found on path.",
            "view3d.col.file": "file",
            "view3d.col.format": "format",
            "view3d.col.size": "size",
            "view3d.col.origin": "source",
            "view3d.col.rec": "recommended",
            "view3d.ok_opening": "opening: {url}",
            "view3d.exec_viewer": "running: python {script} {path}",
        },
    }

    _PARAM_HELP_EN: Dict[str, Dict[str, str]] = PARAM_HELP_EN

    @staticmethod
    def _normalize_lang_code(code: Optional[str]) -> str:
        c = (code or "pt").strip().lower()
        return c if c in ("pt", "en") else "pt"

    def _t(self, key: str, default_pt: str = "") -> str:
        loc = BedWizard._normalize_lang_code(getattr(self, "lang", None))
        d = self._I18N.get(loc, {})
        if key in d:
            return d[key]
        # fallback pt se existir, senao default_pt
        return self._I18N.get("pt", {}).get(key, default_pt)

    def _localized_param_help_texts(
        self, param_key: str, info: Dict[str, Any]
    ) -> Tuple[str, Optional[str]]:
        """descricao e exemplo do param_help conforme idioma (en usa param_help_en)."""
        loc = BedWizard._normalize_lang_code(getattr(self, "lang", None))
        if loc != "en":
            ex = info.get("exemplo")
            return str(info.get("desc", "")), str(ex) if ex is not None else None
        en = BedWizard._PARAM_HELP_EN.get(param_key, {})
        desc = str(en.get("desc") or info.get("desc", ""))
        if "exemplo" not in info:
            return desc, None
        merged = en.get("exemplo") or info.get("exemplo")
        return desc, str(merged) if merged is not None else None

    def _main_menu_rows(self) -> List[Tuple[str, str, str]]:
        return [
            ("1", self._t("menu.main.start.title", "comecar"), self._t("menu.main.start.desc", "")),
            ("2", self._t("menu.main.webapp.title", ""), self._t("menu.main.webapp.desc", "")),
            ("3", self._t("menu.main.help.title", "ajuda"), self._t("menu.main.help.desc", "")),
            ("4", self._t("menu.main.docs.title", "documentacao"), self._t("menu.main.docs.desc", "")),
            ("5", self._t("menu.main.lang.title", "idioma"), self._t("menu.main.lang.desc", "")),
            ("0", self._t("menu.main.exit.title", "sair"), self._t("menu.main.exit.desc", "")),
        ]

    def _start_menu_rows(self) -> List[Tuple[str, str, str]]:
        return [
            ("1", self._t("menu.start.create.title", ""), self._t("menu.start.create.desc", "")),
            ("2", self._t("menu.start.tpl.title", ""), self._t("menu.start.tpl.desc", "")),
            ("3", self._t("menu.start.quick.title", ""), self._t("menu.start.quick.desc", "")),
            ("4", self._t("menu.main.view3d.title", ""), self._t("menu.main.view3d.desc", "")),
            ("5", self._t("menu.start.cfd.title", ""), self._t("menu.start.cfd.desc", "")),
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
        self._web_backend_proc: Optional[subprocess.Popen] = None
        self._web_frontend_proc: Optional[subprocess.Popen] = None
        # true apos carregar .bed e o utilizador pedir saltar o questionario
        self.skip_questionnaire_after_load = False
        self._active_creation_mode = "terminal"
        self.lang = BedWizard._normalize_lang_code("pt")
        self._load_wizard_ui_lang()
        if hasattr(self.ui, "set_ui_lang"):
            self.ui.set_ui_lang(self.lang)
        from graceful_shutdown import set_shutdown_lang

        set_shutdown_lang(self.lang)
        
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
            'bed.internal_cylinder_mode': {
                'desc': (
                    'o que ocupa o interior do leito (o empacotamento continua no anel '
                    'r_int=diametro/2-espessura): [1] normal = leito oco com as particulas '
                    'soltas no interior; [2] interior solido = cilindro macico r_int com as '
                    'particulas embutidas/grudadas; [3] interior solido com furos = o cilindro '
                    'macico e perfurado pelas particulas (efeito queijo) e as particulas somem'
                ),
                'exemplo': 'normal (oco) | solido+particulas | solido furado (queijo)'
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
                'desc': 'diametro caracteristico da particula (esfera: diametro; cubo/cilindro: referencia da malha)',
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
                'desc': 'folga minima entre superficies das particulas nos modos cientificos (colisao aproximada por esfera circunscrita)',
                'min': 0.0, 'max': 0.01, 'unit': 'm',
                'exemplo': '0.0001m = 0.1 mm entre superficies'
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
                'desc': 'se true, falha se geometria invalida ou faltam particulas face ao pedido',
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
        
    def _wizard_lang_pref_path(self) -> Path:
        return local_data_root() / "setup_ui_lang.txt"

    def _load_wizard_ui_lang(self) -> None:
        try:
            p_new = local_data_root() / "setup_ui_lang.txt"
            p_old = local_data_root() / "wizard_ui_lang.txt"
            p = p_new if p_new.is_file() else p_old
            if not p.is_file():
                return
            self.lang = BedWizard._normalize_lang_code(p.read_text(encoding="utf-8"))
        except OSError:
            pass

    def _save_wizard_ui_lang(self) -> None:
        try:
            self._wizard_lang_pref_path().write_text(
                BedWizard._normalize_lang_code(self.lang), encoding="utf-8"
            )
        except OSError:
            pass

    def _lang_code_from_choice_label(self, pick: str) -> Optional[str]:
        """mapeia o texto mostrado no menu (pt ou en) para codigo pt/en."""
        pick = (pick or "").strip()
        if not pick:
            return None
        for code in ("pt", "en"):
            k = f"lang.{code}"
            for loc in ("pt", "en"):
                lab = self._I18N.get(loc, {}).get(k)
                if lab is not None and pick == lab:
                    return str(code)
        return None

    def clear_screen(self):
        """limpar tela do terminal para melhor visualizacao"""
        self.ui.clear()
    
    def print_header(self, title: str, subtitle: str = ""):
        """imprimir cabecalho formatado com titulo"""
        self.ui.header(title, subtitle)
    
    def print_section(self, title: str):
        """imprimir titulo de secao formatado"""
        self.ui.section(title)
    
    def _maybe_cancel(self, raw: str) -> None:
        """cancela o fluxo actual nos prompts internos (menus numerados usam 0 na tabela)."""
        if not self._cancel_enabled:
            return
        tok = (raw or "").strip().lower()
        if tok in ("c", "cancel", "cancelar", "voltar", "back", "q"):
            raise _WizardCancelled()

    def _print_internal_field_aux(
        self, *, review: bool = True, extras: Sequence[str] = ()
    ) -> None:
        fn = getattr(self.ui, "print_aux_internal_prompt", None)
        eb = tuple(x for x in extras if (x or "").strip())
        if callable(fn):
            fn(
                cancel=self._cancel_enabled,
                review=review,
                require_explicit=False,
                extra_bits=eb,
            )
        else:
            for ln in _internal_prompt_aux_lines(
                cancel=self._cancel_enabled,
                review=review,
                require_explicit=False,
                extra_bits=eb,
            ):
                print(ln)

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
        rows: List[MenuRow] = []
        for i, p in enumerate(beds, start=1):
            try:
                full = str(p.resolve())
            except Exception:
                full = str(p)
            rows.append((str(i), p.name, full))
        if rich_available() and getattr(self.ui, "_rich", False):
            render_menu_table_rich(self.ui.console, rows, title="ficheiros .bed")
        else:
            render_menu_table_plain(rows, title="ficheiros .bed")

    def _print_caminho_bed_help(self) -> None:
        """texto que antes estava na linha 'dica:'; mostrado so quando o utilizador prem h."""
        self.ui.println()
        self.ui.muted("l ou lista — rever a tabela de ficheiros .bed encontrados.")
        self.ui.muted("numero ou caminho — escolher pela lista ou por caminho relativo/absoluto.")
        self.ui.muted("n — continuar sem carregar .bed.")
        self.ui.muted("enter vazio neste prompt — igual a n (sair deste passo sem carregar).")
        self.ui.muted("c — cancelar e regressar ao menu anterior.")
        self.ui.println()

    def _maybe_load_existing_bed(self, *, caption: str) -> None:
        self.skip_questionnaire_after_load = False
        # pergunta ao utilizador se quer carregar um .bed para pre-preencher o questionario
        self.ui.hint("opcional: pre-preencher a partir de um .bed existente")
        if not self.get_boolean(
            f"carregar um .bed existente para {caption}?", default=False
        ):
            return
        beds = self._discover_bed_files()
        bed_path: Optional[Path] = None
        while True:
            self.ui.println()
            self._print_internal_field_aux(review=False, extras=("l lista",))
            self.ui.println()
            raw = self.ui.ask_line("caminho .bed (numero ou caminho): ").strip()
            if not raw:
                return
            low = raw.lower()
            if low == "h":
                self._print_caminho_bed_help()
                continue
            if low in ("c", "cancel", "cancelar", "voltar", "back", "q"):
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
                    "ficheiro nao encontrado ou indice invalido; l=lista, h=ajuda, tente de novo"
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
                    "fluxo curto: parametros iguais ao ficheiro; packing, geometria, motor, export e "
                    "propriedades extra das particulas nao serao repedidos nesta sessao."
                )
        else:
            self.ui.warn("nao foi possivel carregar; a seguir sem carregar")

    def _hint_fluxo_questionario(self) -> None:
        self.ui.muted(
            "ordem: leito e tampas → tipo/count/diametro da particula → packing_method e detalhes → "
            "geometry_mode (full 3d ou fatia) → motor de geracao (blender ou python puro) → export → "
            "propriedades extra das particulas → cfd opcional → nome do ficheiro → confirmacao."
        )

    def _hint_fluxo_template(self) -> None:
        self.ui.muted(
            "ordem: escolher template (embutido ou salvo) → editar no editor externo → "
            "nome de saida → gravar/compilar → opcional: guardar copia como template salvo ou gerar stl."
        )

    def _hint_fluxo_blender(self) -> None:
        self.ui.muted(
            "ordem: motor (blender ou python) → leito → tampas → tipo/count/diametro → packing_method → "
            "geometry_mode → export → propriedades extra das particulas → "
            "nome .bed → confirmacao (e politica de abrir blender no fim se aplicavel)."
        )

    def show_param_help(self, param_key: str):
        """mostrar ajuda detalhada sobre um parametro"""
        if param_key in self.param_help:
            info = self.param_help[param_key]
            desc, exemplo = self._localized_param_help_texts(param_key, info)
            lbl_d = self._t("help.field.description", "descricao:")
            lines = [f"{lbl_d} {desc}"]
            if "min" in info and "max" in info:
                unit = info.get("unit", "")
                lbl_r = self._t("help.field.range", "range:")
                lines.append(f"{lbl_r} {info['min']}{unit} .. {info['max']}{unit}")
            if exemplo:
                lbl_e = self._t("help.field.example", "exemplo:")
                lines.append(f"{lbl_e} {exemplo}")
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
            self.ui.println()
            self._print_internal_field_aux(review=True)
            self.ui.println()
            if default:
                full_prompt = f"{prompt} [{default}]: "
            else:
                full_prompt = f"{prompt}: "
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
            self.ui.println()
            self._print_internal_field_aux(review=True)
            self.ui.println()
            if default:
                if unit:
                    full_prompt = f"{prompt} [{default} {unit}]: "
                else:
                    full_prompt = f"{prompt} [{default}]: "
            else:
                if unit:
                    full_prompt = f"{prompt} ({unit}): "
                else:
                    full_prompt = f"{prompt}: "

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
    
    def _resolve_menu_default_index(
        self,
        options: List[str],
        menu_default_index: Optional[object],
        param_key: str,
    ) -> Optional[int]:
        """normaliza indice de menu (int) ou valor string legado para get_choice."""
        if menu_default_index is None:
            if param_key:
                return self._default_choice_index(options, param_key, 0)
            return None
        if isinstance(menu_default_index, int):
            if 0 <= menu_default_index < len(options):
                return menu_default_index
            return None
        if isinstance(menu_default_index, str):
            raw = menu_default_index.strip()
            for i, opt in enumerate(options):
                if opt == raw or opt.lower() == raw.lower():
                    return i
            if param_key:
                return self._default_choice_index(options, param_key, 0)
            return None
        try:
            i = int(menu_default_index)
            if 0 <= i < len(options):
                return i
        except (TypeError, ValueError):
            pass
        return None

    def get_choice(
        self,
        prompt: str,
        options: List[str],
        menu_default_index: Optional[object] = None,
        param_key: str = "",
        *,
        with_param_review: bool = True,
    ) -> str:
        """obter escolha do usuario (? ajuda, * revisao quando activo no contexto)."""
        menu_default_index = self._resolve_menu_default_index(
            options, menu_default_index, param_key
        )

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
            menu_default_index,
            help_callback=_help,
            review_callback=(
                self._param_review_and_edit_menu if with_param_review else None
            ),
            cancel_callback=_cancel,
        )

    def get_boolean(
        self,
        prompt: str,
        default: bool = True,
        *,
        allow_empty_default: Optional[bool] = None,
    ) -> bool:
        """obter entrada booleana (sim/nao) do utilizador."""

        def _cancel() -> None:
            raise _WizardCancelled()

        if allow_empty_default is None:
            allow_empty_default = True
        return self.ui.confirm(
            prompt,
            default,
            cancel_callback=_cancel,
            allow_empty_default=allow_empty_default,
        )
    
    def get_list_input(
        self, prompt: str, separator: str = ",", param_key: str = ""
    ) -> List[str]:
        """obter entrada de lista separada por delimitador (? * revisao)"""
        while True:
            self.ui.println()
            self._print_internal_field_aux(review=True)
            self.ui.println()
            value = self.ui.ask_line(
                f"{prompt} (separador '{separator}'): ", default=""
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
            self.print_header("rever parametros", "0 ou c = voltar ao questionario")
            self.ui.breadcrumbs("setup", "revisao")
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
            self.ui.hint("numero para editar  |  0 / enter / c para continuar o fluxo")
            raw = self.ui.ask_line("opcao: ").strip()
            low = raw.lower()
            if not raw or raw == "0" or low in (
                "c",
                "cancel",
                "cancelar",
                "voltar",
                "back",
                "q",
            ):
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
                li["top_type"] = self.get_choice(
                    "tipo da tampa superior", lid_types, None, "lids.top_type"
                )
            elif field == "bottom_type":
                li["bottom_type"] = self.get_choice(
                    "tipo da tampa inferior", lid_types, None, "lids.bottom_type"
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
                pt["kind"] = self.get_choice(
                    "tipo de particula", particle_kinds, None, "particles.kind"
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
                pk["method"] = normalize_packing_mode(
                    self.get_choice("metodo de empacotamento", opts, None, "packing.method")
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
                        "gap entre superficies das particulas",
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
                ex["wall_mode"] = self.get_choice(
                    "modo da parede", wall_modes, None, "export.wall_mode"
                )
            elif field == "fluid_mode":
                ex["fluid_mode"] = self.get_choice(
                    "modo do fluido", fluid_modes, None, "export.fluid_mode"
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
                cf["regime"] = self.get_choice("regime cfd", cfd_regimes, None, "cfd.regime")
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
    
    def _packing_physics_defaults_for_file(self) -> Dict[str, Any]:
        """valores gravados no .bed para packing; nos modos cientificos nao se perguntam ao utilizador."""
        return {
            "gravity": float(self._default_from_loaded("packing.gravity", "-9.81")),
            "substeps": int(float(self._default_from_loaded("packing.substeps", "10"))),
            "iterations": int(float(self._default_from_loaded("packing.iterations", "10"))),
            "damping": float(self._default_from_loaded("packing.damping", "0.1")),
            "rest_velocity": float(self._default_from_loaded("packing.rest_velocity", "0.01")),
            "max_time": float(self._default_from_loaded("packing.max_time", "5.0")),
            "collision_margin": float(
                self._default_from_loaded("packing.collision_margin", "0.001")
            ),
        }

    def _collect_packing_params(self, with_param_help: bool = False) -> Dict[str, Any]:
        # packing_method controla o restante; rigid_body pergunta fisica de simulacao
        # modos cientificos reutilizam defaults silenciosos no texto .bed compativel com o motor
        opts = list(PACKING_MODE_CHOICES)
        ph = (lambda k: k) if with_param_help else (lambda _k: "")
        self.print_section("etapa 4: empacotamento (packing_method)")
        method_raw = self.get_choice(
            "packing_method",
            opts,
            self._default_choice_index(opts, "packing.method", 0),
            "packing.method",
        )
        method = normalize_packing_mode(method_raw)
        if method == "rigid_body":
            pack: Dict[str, Any] = {"method": method}
            pack["gravity"] = float(
                self.get_number_input(
                    "gravidade (rigid body)",
                    self._default_from_loaded("packing.gravity", "-9.81"),
                    "m/s2",
                    True,
                    ph("packing.gravity"),
                )
            )
            pack["substeps"] = int(
                self.get_number_input(
                    "sub-passos de simulacao",
                    self._default_from_loaded("packing.substeps", "10"),
                    "",
                    False,
                    ph("packing.substeps"),
                )
            )
            pack["iterations"] = int(
                self.get_number_input(
                    "iteracoes do solver",
                    self._default_from_loaded("packing.iterations", "10"),
                    "",
                    False,
                    ph("packing.iterations"),
                )
            )
            pack["damping"] = float(
                self.get_number_input(
                    "amortecimento",
                    self._default_from_loaded("packing.damping", "0.1"),
                    "",
                    False,
                    ph("packing.damping"),
                )
            )
            pack["rest_velocity"] = float(
                self.get_number_input(
                    "velocidade de repouso",
                    self._default_from_loaded("packing.rest_velocity", "0.01"),
                    "m/s",
                    False,
                    ph("packing.rest_velocity"),
                )
            )
            pack["max_time"] = float(
                self.get_number_input(
                    "tempo maximo de simulacao",
                    self._default_from_loaded("packing.max_time", "5.0"),
                    "s",
                    False,
                    ph("packing.max_time"),
                )
            )
            pack["collision_margin"] = float(
                self.get_number_input(
                    "margem de colisao",
                    self._default_from_loaded("packing.collision_margin", "0.001"),
                    "m",
                    False,
                    ph("packing.collision_margin"),
                )
            )
            return pack

        pack = {"method": method, **self._packing_physics_defaults_for_file()}
        if method == "spherical_packing":
            pack["gap"] = float(
                    self.get_number_input(
                        "gap minimo entre superficies das particulas (centros usam raio equivalente)",
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
                    "max tentativas de colocacao",
                    self._default_from_loaded("packing.max_placement_attempts", "500000"),
                    "",
                    False,
                    ph("packing.max_placement_attempts"),
                )
            )
            pack["strict_validation"] = self.get_boolean(
                "validacao estrita de colisao (strict_validation)?",
                self._default_bool_from_loaded("packing.strict_validation", True),
            )
        elif method == "hexagonal_3d":
            pack["gap"] = float(
                self.get_number_input(
                    "gap entre centros na grade hexagonal (folga entre superficies; raio equivalente no dominio)",
                    self._default_from_loaded("packing.gap", "0.0001"),
                    "m",
                    False,
                    ph("packing.gap"),
                )
            )
            step_raw = self.get_number_input(
                "passo horizontal step_x (vazio = automatico)",
                self._default_from_loaded("packing.step_x", ""),
                "m",
                False,
                ph("packing.step_x"),
            )
            if step_raw.strip():
                pack["step_x"] = float(step_raw)
            pack["strict_validation"] = self.get_boolean(
                "validacao estrita da grade (strict_validation)?",
                self._default_bool_from_loaded("packing.strict_validation", True),
            )
        elif method == "dem":
            pack["dem"] = self._collect_dem_params_interactive(ph)
        return pack

    def _collect_dem_params_interactive(self, ph) -> Dict[str, Any]:
        """parametros do solver dem (python_engine)."""
        loaded = self._default_from_loaded("packing.dem", {}) or {}
        if not isinstance(loaded, dict):
            loaded = {}

        def _num(key: str, default: str, unit: str = "") -> float:
            return float(
                self.get_number_input(
                    key,
                    str(loaded.get(key, default)),
                    unit,
                    False,
                    ph(f"packing.dem.{key}"),
                )
            )

        return {
            "time_step": _num("time_step", "0.0001", "s"),
            "steps": int(
                self.get_number_input(
                    "passos de simulacao dem",
                    str(loaded.get("steps", "30000")),
                    "",
                    False,
                    ph("packing.dem.steps"),
                )
            ),
            "gravity": _num("gravity", "9.81", "m/s2"),
            "stiffness": _num("stiffness", "5000", ""),
            "damping": _num("damping", "0.2", ""),
            "friction": _num("friction", "0.2", ""),
            "settle_threshold": _num("settle_threshold", "0.001", "m/s"),
            "max_velocity_threshold": _num("max_velocity_threshold", "0.01", "m/s"),
            "seed": int(
                self.get_number_input(
                    "seed dem",
                    str(loaded.get("seed", "42")),
                    "",
                    False,
                    ph("packing.dem.seed"),
                )
            ),
        }

    _EXPORT_FORMAT_CATALOG: List[Tuple[str, str]] = [
        ("stl_binary", "stl binario (impressao 3d / openfoam)"),
        ("obj", "wavefront obj (universal)"),
        ("blend", "blender nativo (.blend)"),
        ("gltf", "gltf (web, varios ficheiros)"),
        ("glb", "glb (web, ficheiro unico)"),
        ("fbx", "fbx (unity / unreal)"),
    ]

    def _pick_export_formats_interactive(self) -> List[str]:
        """lista numerada de formatos; utilizador indica 1,2,5 (como checkboxes na web)."""
        catalog = list(self._EXPORT_FORMAT_CATALOG)
        fed = self._default_from_loaded("export.formats", "stl_binary,obj")
        default_codes: List[str] = []
        if isinstance(fed, str) and fed.strip():
            default_codes = [x.strip() for x in fed.split(",") if x.strip()]
        elif isinstance(fed, list):
            default_codes = [str(x).strip() for x in fed if str(x).strip()]
        if not default_codes:
            default_codes = ["stl_binary", "obj"]
        default_idx = {
            i + 1
            for i, (code, _desc) in enumerate(catalog)
            if code in default_codes
        }
        default_hint = ",".join(str(i) for i in sorted(default_idx)) or "1,2"

        self.ui.muted(
            "indique os numeros dos formatos desejados, separados por virgula "
            f"(ex: {default_hint}). enter vazio usa o padrao destacado."
        )
        self.ui.println()
        opts = [f"{code} — {desc}" for code, desc in catalog]
        rows: List[MenuRow] = []
        for i, opt in enumerate(opts, start=1):
            key = str(i)
            if "—" in opt:
                modo, rest = opt.split("—", 1)
                rows.append((key, modo.strip(), rest.strip()))
            else:
                rows.append((key, opt[:24], opt))
        self.ui.render_main_menu(rows, title="formatos de exportacao")
        self.ui.println()

        while True:
            self._print_internal_field_aux(review=True)
            self.ui.println()
            raw = self.ui.ask_line(
                f"numeros dos formatos [{default_hint}]: ", default=""
            ).strip()
            self._maybe_cancel(raw)
            if raw == "?":
                self.show_param_help("export.formats")
                continue
            if raw == "*":
                self._param_review_and_edit_menu()
                continue
            pick = raw if raw else default_hint
            indices: List[int] = []
            ok_parse = True
            for part in pick.replace(" ", "").split(","):
                if not part:
                    continue
                try:
                    n = int(part)
                except ValueError:
                    ok_parse = False
                    break
                if n < 1 or n > len(catalog):
                    ok_parse = False
                    break
                indices.append(n)
            if not ok_parse or not indices:
                self.ui.warn(
                    f"digite numeros entre 1 e {len(catalog)}, separados por virgula."
                )
                continue
            chosen = []
            seen: set[str] = set()
            for n in indices:
                code = catalog[n - 1][0]
                if code not in seen:
                    seen.add(code)
                    chosen.append(code)
            return chosen

    def _questionnaire_export_section(self) -> None:
        """mesma secao export do questionario completo — reutilizada pelo modo blender."""
        self.print_section("etapa 7: exportacao")
        wall_modes = ["surface", "solid"]
        fluid_modes = ["none", "cavity"]
        self.params.setdefault("export", {})
        e = self.params["export"]
        e["formats"] = self._pick_export_formats_interactive()
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
            None,
            "export.wall_mode",
        )
        e["fluid_mode"] = self.get_choice(
            "modo do fluido",
            fluid_modes,
            None,
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

    def _fill_statistical_2d_params_interactive(self) -> None:
        """reconstrucao 2d por rsa; independente do packing 3d."""
        self.print_section("parametros da reconstrucao 2d estatistica")
        bed = self.params.get("bed") or {}
        d_default = str(bed.get("diameter", "0.05"))
        h_default = str(bed.get("height", "0.1"))
        width = self.get_number_input(
            "largura do dominio 2d", d_default, "m", False, ""
        )
        height = self.get_number_input(
            "altura do dominio 2d", h_default, "m", False, ""
        )
        target = self.get_number_input(
            "porosidade alvo",
            str(self.params.get("particles", {}).get("target_porosity", "0.4")),
            "",
            False,
            "",
        )
        tol = self.get_number_input("tolerancia de porosidade", "0.02", "", False, "")
        max_att = self.get_input("numero maximo de tentativas", "50")
        thickness = self.get_number_input("espessura da geometria fina 3d", "0.002", "m", False, "")
        seed = self.get_input(
            "seed",
            str(self.params.get("particles", {}).get("seed", "42")),
        )
        self.params["statistical_2d"] = {
            "domain_width": float(width),
            "domain_height": float(height),
            "target_porosity": float(target),
            "tolerance": float(tol),
            "max_attempts": int(max_att),
            "slice_thickness": float(thickness),
            "seed": int(seed),
        }

    def _fill_slice_params_interactive(self) -> None:
        """detalhes da lamina; so faz sentido com geometry_mode pseudo_2d_thin_slice."""
        self.print_section("parametros da fatia fina")
        axis = self.get_choice("eixo normal do corte", ["x", "y", "z"], 1)
        thickness = self.get_number_input("espessura da fatia", "0.002", "m", False, "")
        pos = self.get_number_input("posicao central da fatia", "0.0", "m", False, "")
        keep_only = self.get_boolean(
            "manter apenas particulas que intersectam a fatia?", True
        )
        preserve = self.get_boolean(
            "preservar coordenadas originais (nao recentrar na fatia)?", True
        )
        # validacao do corte: gerar tambem o modelo 3d (antes do corte) p/ comparar
        self.ui.hint(
            "validacao: gera o modelo 3D (antes do corte) para comparar com a fatia 2D"
        )
        compare_labels = [
            "3D em arquivo separado (baixar os dois modelos)",
            "2D e 3D juntos, lado a lado (um arquivo)",
            "2D dentro do 3D, na posicao do corte (um arquivo)",
            "todos (separado + lado a lado + sobreposto)",
            "so 2D (nao gerar o 3D)",
        ]
        compare_canon = ["separate", "combined", "overlay", "all", "off"]
        _loaded_cmp = str(
            (self.params.get("slice") or {}).get("compare_mode") or "separate"
        ).strip().lower()
        _cmp_idx = (
            compare_canon.index(_loaded_cmp) if _loaded_cmp in compare_canon else 0
        )
        cmp_label = self.get_choice(
            "saida de validacao do corte (2D vs 3D)",
            compare_labels,
            _cmp_idx,
            "",
        )
        compare_mode = compare_canon[compare_labels.index(cmp_label)]
        self.params["slice"] = {
            "slice_enabled": True,
            "slice_thickness": float(thickness),
            "slice_axis": axis,
            "slice_position": float(pos),
            "keep_only_intersecting_particles": bool(keep_only),
            "preserve_original_packing": bool(preserve),
            "compare_mode": compare_mode,
        }

    def _questionnaire_geometry_mode_section(self) -> None:
        """geometry_mode e independente de packing_method (full 3d vs lamina fina)."""
        self.print_section("etapa 5: geometry_mode")
        opts = [
            "full_3d — volume completo",
            "pseudo_2d_thin_slice — fatia fina (pseudo 2d)",
            "pseudo_2d_statistical — reconstrucao 2d por porosidade",
        ]
        def_idx = 0
        gm = str(self.params.get("geometry_mode") or "").strip()
        if gm == "pseudo_2d_thin_slice":
            def_idx = 1
        elif gm == "pseudo_2d_statistical":
            def_idx = 2
        pick = self.get_choice(
            "como representar a geometria final",
            opts,
            def_idx,
            "",
        )
        if pick.startswith("full"):
            self.params["geometry_mode"] = "full_3d"
            self.params.pop("slice", None)
            self.params.pop("statistical_2d", None)
        elif pick.startswith("pseudo_2d_statistical"):
            self.params["geometry_mode"] = "pseudo_2d_statistical"
            self.params.pop("slice", None)
            self._fill_statistical_2d_params_interactive()
        else:
            self.params["geometry_mode"] = "pseudo_2d_thin_slice"
            self.params.pop("statistical_2d", None)
            self._fill_slice_params_interactive()

    def _questionnaire_generation_backend_section(
        self,
        *,
        geracao_3d_flow: bool = False,
        locked_backend: Optional[str] = None,
    ) -> None:
        """metadado consumido pelo json compilado; nao confunde com packing_method."""
        self.print_section("etapa 6: motor de geracao")
        if locked_backend is not None:
            b = normalize_generation_backend(locked_backend)
            self.params["generation_backend"] = b
            self.ui.muted(
                f"motor fixo neste fluxo: {b} (coerente com a escolha no inicio; "
                "o .json gravara generation_backend)."
            )
            self.ui.println()
            return
        if geracao_3d_flow:
            self.ui.muted(
                "neste menu (geracao 3d) o habitual e escolher blender; enter vazio mantem a "
                "linha destacada (por defeito opcao 1 = blender se o ficheiro nao pedir python puro). "
                "generation_backend e o metadado no .json que diz ao pipeline quem materializa a malha; "
                "python_engine e para gerar stl com o motor em python (sem leito_extracao)."
            )
            self.ui.println()
        opts = [
            "blender — malha via blender",
            "python_engine — malha via motor feito em python",
        ]
        cur = normalize_generation_backend(
            self.params.get("generation_backend")
            or self._default_from_loaded("generation_backend", "blender")
        )
        def_idx = 1 if cur == "python_engine" else 0
        pick = self.get_choice("generation_backend", opts, def_idx, "")
        self.params["generation_backend"] = (
            "python_engine" if "python" in pick.lower() else "blender"
        )

    def _questionnaire_bed_and_lids(self) -> None:
        """leito cilindrico e tampas — primeiro bloco do questionario 3d."""
        self.print_section("etapa 1: geometria do leito")
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
        # modo do interior do leito: rotulos claros -> valor canonico armazenado
        icm_canon = [
            "hollow_boolean_applied",
            "internal_cylinder_visible_no_boolean",
            "solid_internal_cylinder_with_particle_holes",
        ]
        icm_labels = [
            "normal - leito oco, particulas soltas no interior",
            "interior solido + particulas grudadas no cilindro solido",
            "interior solido com furos das particulas (efeito queijo)",
        ]
        self.ui.hint(
            "interior do leito: [1] normal (oco) | "
            "[2] solido com particulas embutidas | "
            "[3] solido furado pelas particulas (queijo)"
        )
        try:
            from bed_internal_modes import (
                normalize_internal_cylinder_mode as _norm_icm,
            )
        except Exception:
            _norm_icm = None
        _loaded_icm = self._flatten_params_for_defaults().get(
            "bed.internal_cylinder_mode"
        )
        if _norm_icm and _loaded_icm:
            _icm_norm = _norm_icm(_loaded_icm)
        elif _loaded_icm:
            _icm_norm = str(_loaded_icm).strip().lower()
        else:
            _icm_norm = icm_canon[0]
        _icm_idx = icm_canon.index(_icm_norm) if _icm_norm in icm_canon else 0
        _icm_label = self.get_choice(
            "modo do interior do leito (o empacotamento continua no anel)",
            icm_labels,
            _icm_idx,
            "bed.internal_cylinder_mode",
        )
        bd["internal_cylinder_mode"] = icm_canon[icm_labels.index(_icm_label)]
        if str(bd.get("internal_cylinder_mode")) != "hollow_boolean_applied":
            print(
                "  nota: empacotamento continua com r_int = diametro/2 - espessura da parede"
            )
        vis_defaults = {
            "internal_cylinder_visible_no_boolean": True,
            "solid_internal_cylinder_with_particle_holes": True,
        }
        show_inner = vis_defaults.get(str(bd.get("internal_cylinder_mode")), False)
        bd.setdefault("visibility", {})
        bd["visibility"]["show_internal_cylinder"] = show_inner
        if str(bd.get("internal_cylinder_mode")) == "solid_internal_cylinder_with_particle_holes":
            bd["visibility"]["show_particles"] = False

        self.print_section("etapa 2: tampas")
        lid_types = ["flat", "hemispherical", "none"]
        self.params.setdefault("lids", {})
        ld = self.params["lids"]
        ld["top_type"] = self.get_choice(
            "tipo da tampa superior",
            lid_types,
            None,
            "lids.top_type",
        )
        ld["bottom_type"] = self.get_choice(
            "tipo da tampa inferior",
            lid_types,
            None,
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

    def _questionnaire_particle_shape_and_count(self) -> None:
        """tipo geometrico, diametro e count — antes do packing."""
        self.print_section("etapa 3: forma e quantidade das particulas")
        particle_kinds = ["sphere", "cube", "cylinder"]
        self.params.setdefault("particles", {})
        pt = self.params["particles"]
        pt["kind"] = self.get_choice(
            "tipo de particula",
            particle_kinds,
            None,
            "particles.kind",
        )
        pt["diameter"] = self.get_number_input(
            "diametro caracteristico das particulas",
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

    def _questionnaire_particles_properties_tail(self, packing_method: str) -> None:
        """porosidade/densidade/massa/seed; atrito e similares so para rigid_body."""
        self.print_section("etapa 8: propriedades adicionais das particulas")
        self.params.setdefault("particles", {})
        pt = self.params["particles"]
        pt["target_porosity"] = float(
            self.get_number_input(
                "porosidade alvo",
                self._default_from_loaded("particles.target_porosity", "0.4"),
                "",
                False,
                "particles.target_porosity",
            )
        )
        pt["density"] = float(
            self.get_number_input(
                "densidade do material",
                self._default_from_loaded("particles.density", "2500.0"),
                "kg/m3",
                True,
                "particles.density",
            )
        )
        pt["mass"] = float(
            self.get_number_input(
                "massa das particulas",
                self._default_from_loaded("particles.mass", "0.0"),
                "g",
                False,
                "particles.mass",
            )
        )
        pm = normalize_packing_mode(str(packing_method or ""))
        if pm in ("rigid_body", "dem"):
            pt["restitution"] = float(
                self.get_number_input(
                    "coeficiente de restituicao",
                    self._default_from_loaded("particles.restitution", "0.3"),
                    "",
                    False,
                    "particles.restitution",
                )
            )
            pt["friction"] = float(
                self.get_number_input(
                    "coeficiente de atrito",
                    self._default_from_loaded("particles.friction", "0.5"),
                    "",
                    False,
                    "particles.friction",
                )
            )
            pt["rolling_friction"] = float(
                self.get_number_input(
                    "atrito de rolamento",
                    self._default_from_loaded("particles.rolling_friction", "0.1"),
                    "",
                    False,
                    "particles.rolling_friction",
                )
            )
            pt["linear_damping"] = float(
                self.get_number_input(
                    "amortecimento linear",
                    self._default_from_loaded("particles.linear_damping", "0.1"),
                    "",
                    False,
                    "particles.linear_damping",
                )
            )
            pt["angular_damping"] = float(
                self.get_number_input(
                    "amortecimento angular",
                    self._default_from_loaded("particles.angular_damping", "0.1"),
                    "",
                    False,
                    "particles.angular_damping",
                )
            )
        else:
            pt["restitution"] = float(
                self._default_from_loaded("particles.restitution", "0.3")
            )
            pt["friction"] = float(self._default_from_loaded("particles.friction", "0.5"))
            pt["rolling_friction"] = float(
                self._default_from_loaded("particles.rolling_friction", "0.1")
            )
            pt["linear_damping"] = float(
                self._default_from_loaded("particles.linear_damping", "0.1")
            )
            pt["angular_damping"] = float(
                self._default_from_loaded("particles.angular_damping", "0.1")
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

    def _fill_params_from_questionnaire(self) -> None:
        """preenche self.params com todas as secoes do questionario (sem nome de arquivo nem salvar)."""
        self._questionnaire_bed_and_lids()
        self._questionnaire_particle_shape_and_count()
        self._questionnaire_geometry_mode_section()
        gm = str(self.params.get("geometry_mode") or "full_3d")
        if gm == "pseudo_2d_statistical":
            self.params["packing"] = {"method": "statistical_reconstruction"}
            self.ui.muted(
                "empacotamento 3d ignorado: modo pseudo_2d_statistical usa reconstrucao rsa 2d"
            )
        else:
            self.params["packing"] = self._collect_packing_params(with_param_help=True)
        self._questionnaire_generation_backend_section()
        self._questionnaire_export_section()
        self._questionnaire_particles_properties_tail(self.params["packing"]["method"])

        self.print_section("parametros cfd (opcional)")
        if self.get_boolean("incluir parametros cfd?", False):
            cfd_regimes = ["laminar", "turbulent_rans"]
            self.params.setdefault("cfd", {})
            cf = self.params["cfd"]
            cf["regime"] = self.get_choice(
                "regime cfd", cfd_regimes, None, "cfd.regime"
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
        self._active_creation_mode = "interactive"
        old = self._cancel_enabled
        self._cancel_enabled = True
        try:
            self.clear_screen()
            self.print_header(
                self._t("menu.start.q.title", "criar basico"),
                self._t("menu.start.q.desc", ""),
            )
            self.ui.breadcrumbs("setup", "criar", "criar-basico")
            self._hint_fluxo_questionario()
            self.ui.println()
            self._maybe_load_existing_bed(caption=self._t("menu.start.q.title", "criar basico"))
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

    def _open_external_bed_editor(self, bed_text: str) -> str:
        """abre ficheiro temporario no editor externo e devolve o texto editado."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bed", delete=False, encoding="utf-8"
        ) as temp_file:
            temp_file.write(bed_text)
            temp_file_path = temp_file.name

        self.ui.println()
        self.ui.muted(f"ficheiro para editar: {temp_file_path}")
        self.ui.println("editores sugeridos:")
        self.ui.muted("notepad (windows) | nano / vim (linux ou mac) | ou continuar sem editar")

        editor_choice = self.get_choice(
            "escolha um editor",
            ["notepad", "nano", "vim", "continuar sem editar"],
            None,
        )

        if editor_choice != "continuar sem editar":
            try:
                subprocess.run([editor_choice, temp_file_path], check=True)
            except subprocess.CalledProcessError:
                self.ui.warn(f"erro ao abrir editor {editor_choice}; continuando sem edicao")
            except FileNotFoundError:
                self.ui.warn(f"editor {editor_choice} nao encontrado; continuando sem edicao")

        with open(temp_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        os.unlink(temp_file_path)
        return content

    def _patch_compiled_json_from_params(self, jpath: Path) -> None:
        if not self.params:
            return
        try:
            patch_compiled_json_packing(jpath, self.params)
            patch_compiled_json_export(jpath, self.params)
            patch_compiled_json_metadata(jpath, self.params)
            patch_compiled_json_slice(jpath, self.params)
            patch_compiled_json_statistical(jpath, self.params)
            patch_compiled_json_bed(jpath, self.params)
        except Exception as exc:
            self.ui.warn(f"aviso ao aplicar metadados no json: {exc}")

    def _maybe_offer_python_stl_after_template(self, jpath: Path) -> None:
        gb = str((self.params or {}).get("generation_backend") or "")
        if normalize_generation_backend(gb) != "python_engine":
            return
        if not self.ui.confirm(
            "gerar stl com o motor python agora?",
            default=False,
            allow_empty_default=False,
        ):
            return
        out_stl = (Path.cwd() / f"{Path(self.output_file).stem}_pure.stl").resolve()
        ok, stl = self.run_pure_python_with_json_path(jpath, out_stl=out_stl)
        if ok and stl and self.ui.confirm(
            "abrir o blender com o stl gerado?",
            default=False,
            allow_empty_default=False,
        ):
            self.open_blender_gui_with_stl(stl)

    def _maybe_offer_save_saved_template(self, bed_content: str, suggested_stem: str) -> None:
        if not self.ui.confirm(
            "guardar copia como template salvo (aparece em carregar templates salvos)?",
            default=False,
            allow_empty_default=False,
        ):
            return
        nome = self.get_input("nome do template salvo", suggested_stem).strip()
        if not nome:
            self.ui.warn("nome vazio; template salvo ignorado.")
            return
        try:
            path = save_saved_template(nome, bed_content)
            self.ui.ok(f"template salvo: {path}")
        except (OSError, ValueError) as exc:
            self.ui.err(f"nao foi possivel guardar template: {exc}")

    def _finalize_template_bed_flow(
        self,
        bed_text: str,
        suggested_output: str,
        *,
        patch_params: bool = True,
    ) -> None:
        """editor → ficheiro de saida → compilar → stl opcional → guardar template opcional."""
        self.ui.println()
        self.ui.muted("edite o modelo no editor; ao fechar, confirme o nome de saida.")
        edited = self._open_external_bed_editor(bed_text)
        self.output_file = self.get_input("nome do arquivo de saida", suggested_output)
        self._normalize_bed_output_path()
        Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(edited)
        self._register_saved_bed()
        self.ui.ok(f"arquivo salvo: {self.output_file}")
        if not self.verify_and_compile():
            return
        jpath = Path(str(Path(self.output_file).resolve()) + ".json")
        if patch_params:
            self._patch_compiled_json_from_params(jpath)
        self._maybe_offer_python_stl_after_template(jpath)
        self._maybe_offer_save_saved_template(edited, Path(self.output_file).stem)

    def template_mode(self, prefer: Optional[str] = None) -> None:
        """modo edicao de template - carregar modelo, editar .bed, gravar e compilar.

        prefer:
          None — menu com embutidos, salvos e editor classico.
          "json" — apenas templates embutidos (dsl/wizard_templates).
          "saved" — apenas templates salvos (local_data/wizard_templates_saved).
          "editor" — editor .bed classico com modelo exemplo.
        """
        self.clear_screen()
        self.print_header("editor de template", "edicao de modelo .bed")
        self.ui.breadcrumbs("setup", "template")
        self._hint_fluxo_template()
        self.ui.println()

        json_names = list_template_names()
        saved_names = list_saved_template_names()
        modo: Optional[str] = None

        if prefer == "editor":
            modo = "editor .bed classico (modelo exemplo)"
        elif prefer == "json":
            if not json_names:
                self.ui.warn("nao ha templates embutidos em dsl/wizard_templates.")
                self.ui.println()
                prefer = "editor"
                modo = "editor .bed classico (modelo exemplo)"
            else:
                modo = "templates embutidos (dsl/wizard_templates)"
        elif prefer == "saved":
            if not saved_names:
                self.ui.warn(
                    f"ainda nao ha templates salvos em {saved_templates_dir()}; "
                    "grave um modelo ao fim do fluxo ou use um embutido."
                )
                self.ui.println()
            else:
                modo = "templates salvos (local_data/wizard_templates_saved)"
        else:
            opcoes: List[str] = []
            if json_names:
                opcoes.append("templates embutidos (dsl/wizard_templates)")
            if saved_names:
                opcoes.append("templates salvos (local_data/wizard_templates_saved)")
            opcoes.append("editor .bed classico (modelo exemplo)")
            modo = self.get_choice("origem do template", opcoes, None)

        if modo and modo.startswith("templates embutidos"):
            self._active_creation_mode = "template_json"
            pick = self.get_choice("template embutido", json_names, None)
            data = load_template(pick)
            normalize_loaded_dict(data)
            self.params = json_to_wizard_params(data)
            bed_text = self.generate_bed_content()
            suggested = f"{pick.replace('default_', 'leito_')}.bed"
            self._finalize_template_bed_flow(bed_text, suggested, patch_params=True)
            return

        if modo and modo.startswith("templates salvos"):
            self._active_creation_mode = "template_saved"
            pick = self.get_choice("template salvo", saved_names, None)
            bed_text = load_saved_template(pick)
            self.params = {}
            suggested = pick if pick.endswith(".bed") else f"{pick}.bed"
            self._finalize_template_bed_flow(bed_text, suggested, patch_params=False)
            return

        self._active_creation_mode = "template"
        bed_text = self.create_default_template()
        self.params = {}
        self._finalize_template_bed_flow(bed_text, "meu_leito.bed", patch_params=False)

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
        self.ui.breadcrumbs("setup", "questionario", "confirmacao")
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
    
    def _register_saved_bed(self) -> None:
        if not self.output_file:
            return
        try:
            from bedflow_bed_registry import register_bed_file
            from bedflow_local_paths import project_root

            p = Path(self.output_file).resolve()
            root = project_root().resolve()
            try:
                rel = str(p.relative_to(root)).replace("\\", "/")
            except ValueError:
                rel = p.name
            register_bed_file(
                rel,
                source="terminal",
                creation_mode=self._active_creation_mode,
                filename=p.name,
            )
        except Exception:
            pass

    def save_bed_file(self):
        """salvar arquivo .bed com conteudo gerado"""
        self._normalize_bed_output_path()
        content = self.generate_bed_content()  # gerar conteudo do arquivo
        
        # escrever arquivo com codificacao utf-8
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self._register_saved_bed()
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
            self._register_saved_bed()
            return True
        except OSError as e:
            self.ui.err(f"falha ao gravar .bed: {e}")
            return False

    def generate_bed_content(self) -> str:
        """gerar conteudo do arquivo .bed a partir dos parametros configurados"""
        lines = ["// arquivo .bed gerado pelo setup"]
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
        icm = bed.get('internal_cylinder_mode')
        if icm:
            lines.append(f'    internal_cylinder_mode = "{icm}";')
        vis = bed.get('visibility')
        if isinstance(vis, dict) and vis:
            lines.append("    visibility {")
            for vk, vv in vis.items():
                if vv is not None:
                    lines.append(f"        {vk} = {str(bool(vv)).lower()};")
            lines.append("    }")
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
        for pk, unit in (
            ('gap', 'm'),
            ('step_x', 'm'),
        ):
            if packing.get(pk) not in (None, ''):
                lines.append(f"    {pk} = {packing[pk]} {unit};")
        for pk in (
            'random_seed',
            'max_placement_attempts',
            'mesh_segmentos',
            'sphere_lat',
            'sphere_lon',
        ):
            if packing.get(pk) not in (None, ''):
                lines.append(f"    {pk} = {packing[pk]};")
        if packing.get('strict_validation') is not None:
            lines.append(f"    strict_validation = {str(bool(packing['strict_validation'])).lower()};")
        if packing.get('use_legacy_drop') is not None:
            lines.append(f"    use_legacy_drop = {str(bool(packing['use_legacy_drop'])).lower()};")
        dem = packing.get('dem')
        if isinstance(dem, dict) and dem:
            lines.append("    dem {")
            for dk, du in (
                ('time_step', 's'),
                ('gravity', 'm/s2'),
                ('settle_threshold', 'm'),
                ('max_velocity_threshold', 'm/s'),
            ):
                if dem.get(dk) not in (None, ''):
                    lines.append(f"        {dk} = {dem[dk]} {du};")
            for dk in ('steps', 'stiffness', 'damping', 'friction', 'restitution', 'seed'):
                if dem.get(dk) not in (None, ''):
                    lines.append(f"        {dk} = {dem[dk]};")
            lines.append("    }")
        lines.append("}")
        lines.append("")

        gm = self.params.get('geometry_mode')
        if gm:
            lines.append("geometry {")
            lines.append(f'    mode = "{gm}";')
            lines.append("}")
            lines.append("")
        gb = self.params.get('generation_backend')
        if gb:
            lines.append("generation {")
            lines.append(f'    backend = "{gb}";')
            lines.append("}")
            lines.append("")
        sl = self.params.get('slice')
        if isinstance(sl, dict) and sl:
            lines.append("slice {")
            if sl.get('slice_enabled') is not None:
                lines.append(f"    enabled = {str(bool(sl['slice_enabled'])).lower()};")
            if sl.get('slice_thickness') not in (None, ''):
                lines.append(f"    thickness = {sl['slice_thickness']} m;")
            if sl.get('slice_axis'):
                lines.append(f'    axis = "{sl["slice_axis"]}";')
            if sl.get('slice_position') not in (None, ''):
                lines.append(f"    position = {sl['slice_position']} m;")
            if sl.get('keep_only_intersecting_particles') is not None:
                lines.append(
                    f"    keep_only_intersecting_particles = {str(bool(sl['keep_only_intersecting_particles'])).lower()};"
                )
            if sl.get('preserve_original_packing') is not None:
                lines.append(
                    f"    preserve_original_packing = {str(bool(sl['preserve_original_packing'])).lower()};"
                )
            lines.append("}")
            lines.append("")
        st = self.params.get('statistical_2d')
        if isinstance(st, dict) and st:
            lines.append("statistical_2d {")
            for sk, su in (
                ('domain_width', 'm'),
                ('domain_height', 'm'),
                ('slice_thickness', 'm'),
            ):
                if st.get(sk) not in (None, ''):
                    lines.append(f"    {sk} = {st[sk]} {su};")
            for sk in ('target_porosity', 'tolerance'):
                if st.get(sk) not in (None, ''):
                    lines.append(f"    {sk} = {st[sk]};")
            for sk in ('max_attempts', 'seed'):
                if st.get(sk) not in (None, ''):
                    lines.append(f"    {sk} = {st[sk]};")
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
    
    def _questionnaire_blender_bed_lids_particles_packing(
        self,
        *,
        geracao_3d_flow: bool = False,
        locked_generation_backend: Optional[str] = None,
    ) -> None:
        """mesmo encadeamento do questionario completo (sem cfd)."""
        self._questionnaire_bed_and_lids()
        self._questionnaire_particle_shape_and_count()
        self._questionnaire_geometry_mode_section()
        gm = str(self.params.get("geometry_mode") or "full_3d")
        if gm == "pseudo_2d_statistical":
            self.params["packing"] = {"method": "statistical_reconstruction"}
            self.ui.muted(
                "empacotamento 3d ignorado: modo pseudo_2d_statistical usa reconstrucao rsa 2d"
            )
        else:
            self.params["packing"] = self._collect_packing_params(with_param_help=True)
        self._questionnaire_generation_backend_section(
            geracao_3d_flow=geracao_3d_flow and locked_generation_backend is None,
            locked_backend=locked_generation_backend,
        )
        self._questionnaire_export_section()
        self._questionnaire_particles_properties_tail(self.params["packing"]["method"])

    def _generation_3d_continue(self, backend: str) -> None:
        """apos escolher motor: carregar opcional, questionario com backend fixo, nome .bed, confirmacao."""
        backend = normalize_generation_backend(backend)
        self._maybe_load_existing_bed(caption="geracao 3d")
        self.params["generation_backend"] = backend
        if not self.skip_questionnaire_after_load:
            self._questionnaire_blender_bed_lids_particles_packing(
                geracao_3d_flow=False,
                locked_generation_backend=backend,
            )
        else:
            self.ui.muted(
                "questionario saltado: o motor escolhido no inicio aplica-se ao ficheiro carregado."
            )
        self.ui.hint("secao cfd omitida neste modo")
        default_bed = (
            "leito_blender.bed" if backend == "blender" else "leito_python.bed"
        )
        _out = default_bed
        if self.output_file:
            _out = Path(self.output_file).name
        self.output_file = self.get_input("nome do arquivo de saida", _out)
        if backend == "blender":
            opt_nunca = "nao abrir o blender apos gerar"
            opt_perg = "perguntar se deseja abrir o blender apos gerar"
            opt_auto = "abrir o blender automaticamente apos gerar"
            escolha = self.get_choice(
                "comportamento apos gerar o modelo",
                [opt_nunca, opt_perg, opt_auto],
                None,
            )
            if escolha == opt_auto:
                policy = "always"
            elif escolha == opt_perg:
                policy = "ask"
            else:
                policy = "never"
            self._confirm_and_generate_blender(open_policy=policy)
        else:
            opt_nunca = "nao abrir o blender apos gerar o stl"
            opt_perg = "perguntar se deseja abrir o blender com o stl"
            opt_auto = "abrir o blender automaticamente com o stl"
            escolha = self.get_choice(
                "comportamento apos gerar o stl (python puro)",
                [opt_nunca, opt_perg, opt_auto],
                None,
            )
            if escolha == opt_auto:
                policy = "always"
            elif escolha == opt_perg:
                policy = "ask"
            else:
                policy = "never"
            self._confirm_and_generate_python(open_policy=policy)

    def generation_3d_mode(self) -> None:
        """unico fluxo 3d sem cfd: primeiro motor (blender ou python), depois questionario e geracao."""
        self._active_creation_mode = "generation_3d"
        try:
            self.clear_screen()
            self.print_header(
                self._t("menu.start.blender.title", "geracao 3d"),
                self._t("menu.start.blender.desc", ""),
            )
            self.ui.breadcrumbs("setup", "geracao-3d")
            self.ui.muted("parametros cfd nao sao pedidos neste modo.")
            self._hint_fluxo_blender()
            self.ui.println()
            motor = self.get_choice(
                "motor para materializar a malha 3d",
                [
                    "blender — leito_extracao em segundo plano (blend/stl conforme export)",
                    "python engine — malha via motor feito em python",
                ],
                0,
                "",
            )
            backend = (
                "python_engine"
                if ("python" in motor.lower() or "puro" in motor.lower())
                else "blender"
            )
            self._generation_3d_continue(backend)
        except _WizardCancelled:
            self.ui.muted("cancelado.")

    def python_generation_mode(self) -> None:
        """atalho: mesmo fluxo que geracao 3d com motor python fixo (sem pergunta blender vs python)."""
        try:
            self.clear_screen()
            self.print_header(
                "geracao 3d (python puro)",
                "sem cfd; motor fixo python; stl via packed bed science; podes abrir o stl no blender no fim",
            )
            self.ui.breadcrumbs("setup", "geracao-3d", "python")
            self.ui.muted("parametros cfd nao sao pedidos neste modo.")
            self._hint_fluxo_blender()
            self.ui.println()
            self._generation_3d_continue("python_engine")
        except _WizardCancelled:
            self.ui.muted("cancelado.")

    def blender_generation_mode(self) -> None:
        """compat: redirecciona para generation_3d_mode (escolha de motor no inicio)."""
        self.generation_3d_mode()

    def _confirm_and_generate_blender(self, open_policy: str) -> None:
        """open_policy: never | ask | always — gera .bed, compila, executa blender."""
        self.clear_screen()
        self.print_header("confirmacao", "geracao 3d")
        self.ui.breadcrumbs("setup", "blender", "confirmar")
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
        if not self.get_boolean(
            "continuar com geracao no blender?",
            True,
            allow_empty_default=False,
        ):
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
        patch_compiled_json_statistical(jpath, self.params)
        patch_compiled_json_bed(jpath, self.params)
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
                "gostaria de abrir o blender com o modelo gerado?",
                False,
                allow_empty_default=False,
            ):
                self.open_blender_gui_with_blend(blend_path)

    def _confirm_and_generate_python(self, open_policy: str) -> None:
        """open_policy: never | ask | always — gera .bed, compila, gera stl em python puro."""
        self.clear_screen()
        self.print_header("confirmacao", "geracao 3d (python puro)")
        self.ui.breadcrumbs("setup", "python", "confirmar")
        fmts = self.params.get("export", {}).get("formats") or []
        fmt_s = ", ".join(str(x) for x in fmts)
        stem = Path(self.output_file).stem if self.output_file else "leito"
        out_stl = (Path.cwd() / f"{stem}_pure.stl").resolve()
        self.ui.println("resumo:")
        self.ui.muted(
            f"  leito: {self.params['bed']['diameter']} m x {self.params['bed']['height']} m"
        )
        self.ui.muted(
            f"  particulas: {self.params['particles']['count']} {self.params['particles']['kind']}"
        )
        self.ui.muted(f"  empacotamento: {self.params['packing']['method']} | export: {fmt_s}")
        self.ui.muted(f"  stl previsto: {out_stl}")
        self.ui.println()
        if open_policy == "always":
            self.ui.hint("apos gerar, o blender abre com o stl (se o executavel existir)")
            self.ui.println()
        if not self.get_boolean(
            "continuar com geracao em python puro (stl)?",
            True,
            allow_empty_default=False,
        ):
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
        patch_compiled_json_statistical(jpath, self.params)
        patch_compiled_json_bed(jpath, self.params)
        self.ui.section("gerando stl em python puro")
        ok, stl_path = self.run_pure_python_with_json_path(jpath, out_stl=out_stl)
        if not ok or not stl_path:
            self.ui.err("falha na geracao python pura (ver mensagens na consola)")
            return
        self.ui.ok(f"stl: {stl_path}")
        if open_policy == "always":
            self.ui.section("concluido")
            self.open_blender_gui_with_stl(stl_path)
            self.ui.muted("blender em segundo plano com o stl importado")
            return
        if open_policy == "ask":
            if self.get_boolean(
                "gostaria de abrir o blender com o stl gerado?",
                False,
                allow_empty_default=False,
            ):
                self.open_blender_gui_with_stl(stl_path)

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
    
    def open_blender_with_file(self, blender_exe: Any, mesh_path: Any) -> None:
        """abrir blender em modo gui: .blend abre a cena; malhas cad importam via script."""
        try:
            p = Path(mesh_path).expanduser().resolve()
        except Exception:
            p = Path(str(mesh_path))
        suf = p.suffix.lower()
        import_script = _BLENDER_SCRIPTS / "open_imported_mesh_gui.py"

        def _emit_launch_summary(title: str, body: str) -> None:
            if rich_available() and getattr(self.ui, "console", None):
                from rich.panel import Panel

                self.ui.console.print(
                    Panel(
                        body,
                        title=title,
                        border_style="rgb(95,25,35)",
                    )
                )
            else:
                self.ui.println(f"\n{title}")
                self.ui.println(body)

        try:
            if suf == ".blend":
                cmd = [str(blender_exe), str(p)]
                _emit_launch_summary(
                    "abrir no blender",
                    f"formato: .blend (cena nativa)\n"
                    f"caminho:\n  {p}\n"
                    f"comando:\n  {' '.join(cmd)}",
                )
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.ui.ok("blender lancado em segundo plano (cena .blend).")
                self.ui.muted("pode fechar este terminal sem fechar o blender.")
                return

            mesh_exts = {".stl", ".obj", ".ply", ".gltf", ".glb"}
            if suf not in mesh_exts:
                self.ui.warn(
                    f"extensao {suf!r} nao tem import automatico via script; "
                    "abra o ficheiro manualmente no blender ou exporte stl/obj."
                )
                cmd = [str(blender_exe), str(p)]
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.ui.muted(f"tentativa legacy: {' '.join(cmd)}")
                return

            if not import_script.is_file():
                self.ui.err(f"script de importacao em falta: {import_script}")
                return

            cmd = [
                str(blender_exe),
                "--python",
                str(import_script),
                "--",
                str(p),
            ]
            _emit_launch_summary(
                "abrir no blender — novo projeto e importacao",
                f"formato detectado: {suf}\n"
                f"fluxo: limpar cena por omissao → importar malha → enquadrar vista\n"
                f"caminho:\n  {p}\n"
                f"script:\n  {import_script}\n"
                f"comando:\n  {blender_exe} --python ... -- <caminho>",
            )
            log_hint = Path(tempfile.gettempdir()) / "bedflow_blender_import.log"
            launch_log = Path(tempfile.gettempdir()) / "bedflow_blender_subprocess.log"
            try:
                with open(launch_log, "ab") as lf:
                    lf.write(
                        f"\n--- launch {p.name} ---\n{' '.join(cmd)}\n".encode(
                            "utf-8", errors="replace"
                        )
                    )
                    subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT)
            except OSError as oe:
                self.ui.warn(f"nao foi possivel abrir registo de subprocesso ({oe}); a lancar sem registo.")
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.ui.ok(
                "blender lancado; abre-se um projeto novo e de seguida importa-se o modelo."
            )
            self.ui.muted(
                f"se o blender fechar ou nao importar, veja o registo:\n  {log_hint}\n"
                f"saida stderr/stdout do processo (se houver):\n  {launch_log}\n"
                "e a versao do blender (3.6+ / 4.x)."
            )
        except Exception as e:
            self.ui.err(f"erro ao lancar blender: {e}")
            self.ui.hint(f"tente manualmente:\n  {blender_exe} {mesh_path}")
    
    def tests_quick_menu(self) -> None:
        # delega no fluxo guiado wizard_quick_tests entrada backend modo execucao pos
        wizard_quick_tests_run(self)

    def show_help_menu(self):
        """mostrar menu de ajuda com informacoes sobre parametros"""
        self.clear_screen()
        self.print_header(
            self._t("help.title", "ajuda"),
            self._t("help.subtitle", "parametros do arquivo .bed"),
        )
        self.ui.breadcrumbs("setup", self._t("help.title", "ajuda"))
        self.ui.hint(self._t("help.top_hint", ""))

        sections = {
            "1": ("bed", self._t("help.sec.bed", "geometria do leito")),
            "2": ("lids", self._t("help.sec.lids", "tampas")),
            "3": ("particles", self._t("help.sec.particles", "particulas")),
            "4": ("packing", self._t("help.sec.packing", "empacotamento")),
            "5": ("export", self._t("help.sec.export", "exportacao")),
            "6": ("cfd", self._t("help.sec.cfd", "simulacao cfd")),
            "7": ("view3d", self._t("help.sec.view3d", "visualizacao 3d (modos e formatos)")),
        }

        entries = [(k, v[1]) for k, v in sections.items()]
        self.ui.render_help_section_menu(entries, back_key="0")
        choice = self.ui.ask_line(self._t("help.prompt", "")).strip()

        if choice.lower() == "h":
            self.ui.hint(global_keys_hint(self.lang))
            self.ui.pause("enter...")
            self.show_help_menu()
            return
        if choice == "0":
            return
        if choice.lower() in ("c", "cancel", "cancelar", "voltar", "q"):
            self.ui.warn(self._t("help.use0", ""))
            self.ui.pause("enter...")
            return
        if choice == "7":
            from wizard_3d_viewer import print_visualization_modes_help

            self.clear_screen()
            self.print_header(
                self._t("help.view3d_title", "ajuda: visualizacao 3d"),
                self._t("help.view3d_subtitle", "modos web, desktop e blender"),
            )
            self.ui.breadcrumbs("setup", self._t("help.title", "ajuda"), "view3d")
            print_visualization_modes_help(self)
            self.ui.pause(self._t("help.pause_continue", ""))
            self.show_help_menu()
            return
        elif choice in sections:
            section_key, section_desc = sections[choice]
            self.clear_screen()
            pfx = self._t("help.detail_prefix", "ajuda:")
            self.print_header(
                f"{pfx} {section_desc}",
                self._t("help.detail_sub", "detalhes dos campos"),
            )
            self.ui.breadcrumbs("setup", self._t("help.title", "ajuda"), section_key)
            
            for param_key, param_info in sorted(self.param_help.items()):
                if param_key.startswith(f"{section_key}."):
                    param_name = param_key.split(".")[1]
                    desc, exemplo = self._localized_param_help_texts(
                        param_key, param_info
                    )
                    lbl_p = self._t("help.field.param", "parametro:")
                    lbl_d = self._t("help.field.description", "descricao:")
                    lines = [
                        f"{lbl_p} {param_name}",
                        f"{lbl_d} {desc}",
                    ]
                    if "min" in param_info and "max" in param_info:
                        unit = param_info.get("unit", "")
                        lbl_r = self._t("help.field.range", "range:")
                        lines.append(
                            f"{lbl_r} {param_info['min']}{unit} .. {param_info['max']}{unit}"
                        )
                    if exemplo:
                        lbl_e = self._t("help.field.example", "exemplo:")
                        lines.append(f"{lbl_e} {exemplo}")
                    self.ui.param_help(lines)
            
            self.ui.pause(self._t("help.pause_continue", ""))
            self.show_help_menu()
        else:
            self.ui.warn(self._t("help.invalid", "opcao invalida"))
            self.ui.pause(self._t("help.pause_continue", ""))
            self.show_help_menu()
    
    def pipeline_completo_mode(self):
        """modo pipeline completo - gera modelo 3d, cria caso cfd e executa simulacao"""
        self._active_creation_mode = "pipeline_completo"
        self.clear_screen()
        self.print_header(
            self._t("menu.start.pipe.title", "pipeline completo"),
            self._t("menu.start.pipe.desc", ""),
        )
        self.ui.breadcrumbs("setup", "pipeline")
        self.ui.println("etapas resumidas:")
        self.ui.muted(
            "1) questionario do leito  2) gerar e compilar .bed  3) blender  "
            "4) caso openfoam  5) simulacao no wsl (longo)"
        )
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
                allow_empty_default=False,
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
        patch_compiled_json_statistical(json_path, self.params)
        patch_compiled_json_bed(json_path, self.params)
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
            # allrun gerado no windows pode ter crlf; wsl acusa /bin/sh^m bad interpreter
            wsl_command = (
                f"cd '{wsl_path}' && sed -i 's/\\r$//' Allrun && "
                f"chmod +x Allrun && ./Allrun"
            )
            
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

        dsl_dir = Path(__file__).parent
        lang = BedWizard._normalize_lang_code(getattr(self, "lang", None))
        doc_path = dsl_dir / "documentacao.html"
        if lang == "en":
            en_path = dsl_dir / "documentacao_en.html"
            if en_path.is_file():
                doc_path = en_path
        if not doc_path.exists():
            self.ui.err(self._t("docs.err_missing", "arquivo de documentacao nao encontrado"))
            self.ui.muted(f"{self._t('docs.err_expected', 'caminho esperado')}: {doc_path}")
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
                self._t("docs.title", "documentacao"),
                self._t("docs.subtitle", ""),
            )
            self.ui.breadcrumbs("setup", self._t("docs.title", "documentacao"))
            if edge_msg:
                self.ui.warn(edge_msg)
                edge_msg = ""
            bloco = paginas[idx]
            is_last = idx >= total - 1
            if is_last:
                ctl = (
                    self._t("docs.ctl_last_standalone", "")
                    if standalone
                    else self._t("docs.ctl_last_menu", "")
                )
            else:
                ctl = self._t("docs.ctl_nav", "")
            panel_title = self._t(
                "docs.page_panel_title",
                "{heading} — pagina {n}/{total}",
            ).format(
                heading=self._t("docs.title", "documentacao"),
                n=idx + 1,
                total=total,
            )
            self.ui.render_documentation_page(
                bloco, idx, total, ctl, panel_title=panel_title
            )
            if is_last:
                fim = (
                    self._t("docs.pause_exit_standalone", "")
                    if standalone
                    else self._t("docs.pause_exit_menu", "")
                )
                self.ui.pause(fim)
                break
            raw = self.ui.ask_line(self._t("docs.action_prompt", ""), default="n").strip().lower()
            if raw in ("q", "c", "cancel", "cancelar", "sair"):
                break
            if raw == "h":
                self.ui.hint(global_keys_hint(self.lang))
                self.ui.pause("enter...")
                continue
            if raw == "?":
                self.ui.muted(self._t("docs.field_help", ""))
                self.ui.pause("enter...")
                continue
            if raw == "p":
                if idx > 0:
                    idx -= 1
                else:
                    edge_msg = self._t("docs.edge_first", "")
                continue
            idx += 1

    def _draw_start_menu(self) -> None:
        """submenu comecar (fluxos operacionais)."""
        self.ui.clear()
        self.ui.header(
            self._t("app.title", "setup de parametrizacao"),
            self._t("app.subtitle", "leitos empacotados — arquivos .bed / antlr / blender / openfoam"),
        )
        self.ui.breadcrumbs("setup", self._t("menu.title.start", "comecar"))
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

    def run_questionnaire_interactive(self) -> None:
        """mesmo fluxo que comecar > criar > criar basico: questionario ate gravar .bed."""
        self.interactive_mode()

    def run_generation_3d(self) -> None:
        """mesmo fluxo que comecar > criar > geracao 3d."""
        self.generation_3d_mode()

    def run_pipeline_completo(self) -> None:
        """mesmo fluxo que comecar > criar > pipeline completo."""
        self.pipeline_completo_mode()

    def run_start_menu(self) -> None:
        """loop do submenu comecar ate o utilizador escolher 0 voltar."""
        while True:
            self._draw_start_menu()
            choice = self.ui.ask_line(self._t("prompt.start.choice", "opcao (0-5): ")).strip()
            low = choice.lower()
            if low == "h":
                self.ui.hint(global_keys_hint(self.lang))
                self.ui.pause("enter...")
                continue
            if choice == "0":
                return
            if not choice:
                self.ui.warn("indique 1 a 5 ou 0 para voltar.")
                self.ui.pause("enter...")
                continue
            try:
                if choice == "1":
                    self.create_flow()
                elif choice == "2":
                    self.templates_editor_menu()
                elif choice == "3":
                    self.tests_quick_menu()
                elif choice == "4":
                    self.visualization_3d_mode()
                elif choice == "5":
                    self.simulacao_cfd_mode()
                else:
                    self.ui.warn("escolha um numero de 0 a 5")
                    self.ui.pause("enter...")
                    continue
            except _WizardCancelled:
                self.ui.muted("cancelado.")
            self.ui.pause("enter para voltar ao submenu comecar...")

    def templates_editor_menu(self) -> None:
        """templates embutidos, salvos e editor .bed classico (sem testes rapidos)."""
        while True:
            self.clear_screen()
            self.print_header(
                "templates e editor",
                "carregar template, editar .bed, gravar e compilar (como na web)",
            )
            self.ui.breadcrumbs("setup", "comecar", "templates-editor")
            self.ui.muted(
                f"templates salvos: {saved_templates_dir()} "
                "(aparecem apos guardar ao fim do fluxo)"
            )
            self.ui.println()
            opcoes = [
                "carregar template embutido (dsl/wizard_templates)",
                "carregar templates salvos (local_data)",
                "editor .bed classico (modelo exemplo)",
            ]
            try:
                fluxo = self.get_choice("fluxo", opcoes, None)
            except _WizardCancelled:
                return
            try:
                if fluxo.startswith("carregar template embutido"):
                    self.template_mode(prefer="json")
                    self.ui.pause("enter para voltar...")
                    continue
                if fluxo.startswith("carregar templates salvos"):
                    self.template_mode(prefer="saved")
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

    def create_flow(self) -> None:
        """submenu criar: criar basico, geracao 3d ou pipeline completo."""
        self.clear_screen()
        self.print_header(
            self._t("menu.start.create.title", "criar"),
            self._t("create.subtitle", ""),
        )
        self.ui.breadcrumbs("setup", "comecar", "criar")
        self.ui.println()
        _em = "\u2014"
        t_q = self._t("menu.start.q.title", "criar basico")
        t_3d = self._t("menu.start.blender.title", "geracao 3d")
        t_pipe = self._t("menu.start.pipe.title", "pipeline completo")
        d_q = self._t("menu.start.q.desc", "")
        d_3d = self._t("menu.start.blender.desc", "")
        d_pipe = self._t("menu.start.pipe.desc", "")
        opt_q = f"{t_q} {_em} {d_q}"
        opt_3d = f"{t_3d} {_em} {d_3d}"
        opt_pipe = f"{t_pipe} {_em} {d_pipe}"
        try:
            pick = self.get_choice(
                self._t("create.prompt", ""),
                [opt_q, opt_3d, opt_pipe],
                None,
                "",
                with_param_review=False,
            )
            if pick == opt_q:
                self.run_questionnaire_interactive()
                return
            if pick == opt_3d:
                self.run_generation_3d()
                return
            if pick == opt_pipe:
                self.run_pipeline_completo()
                return
            self.ui.warn(self._t("help.invalid", "opcao invalida"))
        except _WizardCancelled:
            self.ui.muted("cancelado.")

    def _discover_simulation_cases(self) -> List[Path]:
        """pastas sob local_data/simulations com Allrun ou system/controlDict."""
        root = simulations_dir()
        out: List[Path] = []
        if not root.is_dir():
            return out
        for p in sorted(root.iterdir(), key=lambda x: x.name.lower()):
            if not p.is_dir():
                continue
            if (p / "Allrun").is_file() or (p / "system" / "controlDict").is_file():
                try:
                    out.append(p.resolve())
                except OSError:
                    out.append(p)
        return out

    def _print_simulation_cases_list(self, cases: List[Path]) -> None:
        rows: List[MenuRow] = []
        for i, p in enumerate(cases, start=1):
            try:
                full = str(p.resolve())
            except OSError:
                full = str(p)
            rows.append((str(i), p.name, full))
        title = self._t("cfd.list.title", "casos em local_data/simulations")
        if rich_available() and getattr(self.ui, "_rich", False):
            render_menu_table_rich(self.ui.console, rows, title=title)
        else:
            render_menu_table_plain(rows, title=title)

    def simulacao_cfd_mode(self) -> None:
        """lista casos openfoam guardados e executa run_openfoam_simulation."""
        old = self._cancel_enabled
        self._cancel_enabled = True
        try:
            self.clear_screen()
            self.print_header(
                self._t("menu.start.cfd.title", "simulacao cfd"),
                self._t("menu.start.cfd.desc", ""),
            )
            self.ui.breadcrumbs("setup", "comecar", "simulacao-cfd")
            self.ui.println()
            cases = self._discover_simulation_cases()
            if not cases:
                self.ui.warn(self._t("cfd.warn_none", ""))
                self.ui.pause("enter...")
                return
            self._print_simulation_cases_list(cases)
            self.ui.println()
            self.ui.hint(self._t("cfd.pick_hint", ""))
            while True:
                raw = self.ui.ask_line(self._t("cfd.pick_prompt", "")).strip()
                self._maybe_cancel(raw)
                low = raw.lower()
                if low in ("l", "lista"):
                    self._print_simulation_cases_list(cases)
                    self.ui.println()
                    continue
                if not raw:
                    self.ui.muted("cancelado.")
                    return
                chosen: Optional[Path] = None
                if raw.isdigit():
                    idx = int(raw) - 1
                    if 0 <= idx < len(cases):
                        chosen = cases[idx]
                if chosen is None:
                    try:
                        cand = Path(raw)
                        if not cand.is_absolute():
                            cand = (Path.cwd() / cand).resolve()
                        else:
                            cand = cand.resolve()
                        if cand.is_dir() and (
                            (cand / "Allrun").is_file()
                            or (cand / "system" / "controlDict").is_file()
                        ):
                            chosen = cand
                    except OSError:
                        chosen = None
                if chosen is None:
                    self.ui.warn(self._t("help.invalid", "opcao invalida"))
                    continue
                if not self.get_boolean(
                    self._t("cfd.confirm_run", ""),
                    default=False,
                    allow_empty_default=False,
                ):
                    self.ui.muted("cancelado.")
                    return
                ok = self.run_openfoam_simulation(chosen)
                if ok:
                    self.ui.ok(self._t("cfd.done", ""))
                else:
                    self.ui.err(self._t("cfd.err_failed", "falha na simulacao."))
                self.ui.pause("enter...")
                return
        except _WizardCancelled:
            self.ui.muted("cancelado.")
        finally:
            self._cancel_enabled = old

    def _draw_main_menu(self) -> None:
        """tela inicial estilo navegador (barra + tabela de modos)."""
        self.ui.clear()
        self.ui.header(
            self._t("app.title", "setup de parametrizacao"),
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
        self.lang = BedWizard._normalize_lang_code(self.lang)
        self.clear_screen()
        self.print_header(self._t("lang.header", "idioma"), self._t("lang.subtitle", "trocar idioma do setup"))
        self.ui.breadcrumbs("setup", self._t("lang.header", "idioma"))
        self.ui.println()
        cur = self._t("lang.pt" if self.lang == "pt" else "lang.en", "portugues" if self.lang == "pt" else "ingles")
        self.ui.muted(f"{self._t('lang.current', 'idioma atual')}: {cur}")
        self.ui.println()
        opts = [self._t("lang.pt", "portugues"), self._t("lang.en", "ingles")]
        try:
            pick = self.get_choice(
                self._t("lang.choose", "escolha o idioma"),
                opts,
                None,
                "",
                with_param_review=False,
            )
        except _WizardCancelled:
            self.ui.muted("cancelado.")
            return
        chosen = self._lang_code_from_choice_label(pick)
        if chosen is None:
            try:
                chosen = ("pt", "en")[opts.index(pick)]
            except ValueError:
                chosen = self.lang
        self.lang = BedWizard._normalize_lang_code(chosen)
        self._save_wizard_ui_lang()
        if hasattr(self.ui, "set_ui_lang"):
            self.ui.set_ui_lang(self.lang)
        from graceful_shutdown import set_shutdown_lang

        set_shutdown_lang(self.lang)
        self.ui.ok(self._t("lang.ok", "idioma atualizado"))

    def visualization_3d_mode(self) -> None:
        from wizard_3d_viewer import run_visualization_mode

        run_visualization_mode(self)

    def _web_popen_kwargs_silent(self) -> Dict[str, Any]:
        kw: Dict[str, Any] = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "stdin": subprocess.DEVNULL,
        }
        if sys.platform == "win32":
            kw["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kw["start_new_session"] = True
        return kw

    def _web_popen_kwargs_new_console_win(self) -> Dict[str, Any]:
        return {
            "stdin": subprocess.DEVNULL,
            "creationflags": subprocess.CREATE_NEW_CONSOLE,
        }

    def _web_win_persistent_console_popen(
        self, cmd: List[str], cwd: str
    ) -> subprocess.Popen:
        # abre uma consola nova que permanece aberta mesmo depois de o processo
        # terminar ou falhar (cmd /k), permitindo ler os logs e o erro. espelha
        # o comportamento do terminal no unix (bash -lc "...; read _").
        win_cmd = 'cmd /k "' + subprocess.list2cmdline(cmd) + '"'
        return subprocess.Popen(
            win_cmd,
            cwd=cwd,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )

    def _web_kill_processes_on_port(self, port: int) -> None:
        """best effort: liberta porto (uvicorn/vite orfaos ou sessao antiga)."""
        if sys.platform == "win32":
            ps = (
                f"$c = Get-NetTCPConnection -LocalPort {port} -State Listen -ErrorAction SilentlyContinue; "
                "if ($null -ne $c) { "
                "$c | ForEach-Object { "
                "Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue "
                "} }"
            )
            try:
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps],
                    capture_output=True,
                    timeout=20,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired):
                pass
            return
        try:
            subprocess.run(
                [
                    "sh",
                    "-c",
                    f'for pid in $(lsof -tiTCP:{port} -sTCP:LISTEN 2>/dev/null); do kill -TERM "$pid" 2>/dev/null; done',
                ],
                capture_output=True,
                timeout=12,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
        try:
            subprocess.run(
                [
                    "sh",
                    "-c",
                    f'for pid in $(lsof -tiTCP:{port} -sTCP:LISTEN 2>/dev/null); do kill -KILL "$pid" 2>/dev/null; done',
                ],
                capture_output=True,
                timeout=12,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass

    def _web_kill_process_tree(self, proc: subprocess.Popen) -> None:
        if proc.poll() is not None:
            return
        pid = proc.pid
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            try:
                os.killpg(pid, signal.SIGTERM)
            except (ProcessLookupError, PermissionError, OSError):
                pass
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError, OSError):
                    proc.kill()
        try:
            proc.wait(timeout=5)
        except (subprocess.TimeoutExpired, OSError):
            pass

    def _web_force_stop_backend(self) -> None:
        proc = self._web_backend_proc
        self._web_backend_proc = None
        if proc is not None and proc.poll() is None:
            self._web_kill_process_tree(proc)
        self._web_kill_processes_on_port(8000)

    def _web_force_stop_frontend(self) -> None:
        proc = self._web_frontend_proc
        self._web_frontend_proc = None
        if proc is not None and proc.poll() is None:
            self._web_kill_process_tree(proc)
        self._web_kill_processes_on_port(5173)

    def _web_backend_running(self) -> bool:
        return (
            self._web_backend_proc is not None
            and self._web_backend_proc.poll() is None
        )

    def _web_frontend_running(self) -> bool:
        return (
            self._web_frontend_proc is not None
            and self._web_frontend_proc.poll() is None
        )

    def _web_print_status(self) -> None:
        if self._web_backend_running():
            pid = self._web_backend_proc.pid if self._web_backend_proc else 0
            self.ui.muted(self._t("webapp.status.back.on", "").format(pid=pid))
        else:
            self.ui.muted(self._t("webapp.status.back.off", ""))
        if self._web_frontend_running():
            pid = self._web_frontend_proc.pid if self._web_frontend_proc else 0
            self.ui.muted(self._t("webapp.status.front.on", "").format(pid=pid))
        else:
            self.ui.muted(self._t("webapp.status.front.off", ""))

    def _web_app_menu_rows(self) -> List[Tuple[str, str, str]]:
        specs = [
            ("webapp.opt.both_start.t", "webapp.opt.both_start.d"),
            ("webapp.opt.back_start.t", "webapp.opt.back_start.d"),
            ("webapp.opt.front_start.t", "webapp.opt.front_start.d"),
            ("webapp.opt.back_stop.t", "webapp.opt.back_stop.d"),
            ("webapp.opt.front_stop.t", "webapp.opt.front_stop.d"),
            ("webapp.opt.both_stop.t", "webapp.opt.both_stop.d"),
            ("webapp.opt.back_restart.t", "webapp.opt.back_restart.d"),
            ("webapp.opt.front_restart.t", "webapp.opt.front_restart.d"),
            ("webapp.opt.both_restart.t", "webapp.opt.both_restart.d"),
        ]
        rows: List[Tuple[str, str, str]] = []
        for i, (kt, kd) in enumerate(specs, start=1):
            rows.append((str(i), self._t(kt, ""), self._t(kd, "")))
        rows.append(
            (
                "0",
                self._t("menu.start.back.title", "voltar"),
                self._t("webapp.back_row", ""),
            )
        )
        return rows

    def _draw_web_app_menu(self) -> None:
        self.ui.clear()
        self.ui.header(
            self._t("app.title", ""),
            self._t("app.subtitle", ""),
        )
        self.ui.breadcrumbs("setup", self._t("menu.main.webapp.title", "web"))
        self.ui.println()
        self.ui.muted(self._t("webapp.title", ""))
        self.ui.muted(self._t("webapp.subtitle", ""))
        self.ui.println()
        self._web_print_status()
        self.ui.println()
        self.ui.render_main_menu(
            self._web_app_menu_rows(),
            title=self._t("webapp.actions", "accoes"),
        )

    def _web_unix_terminal_popen(self, cmd: List[str], cwd: str) -> Optional[subprocess.Popen]:
        inner = f"cd {shlex.quote(cwd)} && exec {shlex.join(cmd)}; echo; echo [fim] enter...; read _"
        for exe, argv in (
            ("gnome-terminal", ["gnome-terminal", "--", "bash", "-lc", inner]),
            ("kgx", ["kgx", "--", "bash", "-lc", inner]),
            ("konsole", ["konsole", "-e", "bash", "-lc", inner]),
            ("xfce4-terminal", ["xfce4-terminal", "-e", f"bash -lc {shlex.quote(inner)}"]),
            ("xterm", ["xterm", "-e", "bash", "-lc", inner]),
        ):
            path = shutil.which(argv[0])
            if path:
                argv = [path] + argv[1:]
                try:
                    return subprocess.Popen(
                        argv,
                        cwd=cwd,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True,
                    )
                except OSError:
                    continue
        return None

    def _web_spawn_backend(self) -> Optional[subprocess.Popen]:
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ]
        cwd = str(_REPO_ROOT)
        if sys.platform == "win32":
            try:
                return self._web_win_persistent_console_popen(cmd, cwd)
            except OSError:
                return None
        proc = self._web_unix_terminal_popen(cmd, cwd)
        if proc is not None:
            return proc
        try:
            return subprocess.Popen(cmd, cwd=cwd, **self._web_popen_kwargs_silent())
        except OSError:
            return None

    def _web_spawn_frontend(self) -> Optional[subprocess.Popen]:
        npm = shutil.which("npm")
        if not npm:
            return None
        cmd = [npm, "run", "dev"]
        cwd = str(_REPO_ROOT / "frontend")
        if sys.platform == "win32":
            try:
                return self._web_win_persistent_console_popen(cmd, cwd)
            except OSError:
                return None
        proc = self._web_unix_terminal_popen(cmd, cwd)
        if proc is not None:
            return proc
        try:
            return subprocess.Popen(cmd, cwd=cwd, **self._web_popen_kwargs_silent())
        except OSError:
            return None

    def _web_open_browser_tabs(self, *, backend: bool, frontend: bool) -> None:
        time.sleep(1.0)
        if backend:
            try:
                webbrowser.open("http://127.0.0.1:8000/docs")
            except Exception:
                pass
        if frontend:
            try:
                webbrowser.open("http://127.0.0.1:5173/")
            except Exception:
                pass

    def _web_start_backend(self, *, announce: bool = True, open_browser: bool = False) -> bool:
        self._web_force_stop_backend()
        try:
            self._web_backend_proc = self._web_spawn_backend()
        except OSError as e:
            self._web_backend_proc = None
            self.ui.err(self._t("webapp.err_start_back", "").format(err=e))
            return False
        if self._web_backend_proc is None:
            self.ui.err(self._t("webapp.err_start_back", "").format(err="spawn"))
            return False
        if announce:
            self.ui.ok(self._t("webapp.ok_start_back", ""))
        if open_browser:
            self._web_open_browser_tabs(backend=True, frontend=False)
        return True

    def _web_start_frontend(self, *, announce: bool = True, open_browser: bool = False) -> bool:
        self._web_force_stop_frontend()
        if shutil.which("npm") is None:
            self.ui.err(self._t("webapp.err_no_npm", ""))
            self._web_frontend_proc = None
            return False
        try:
            self._web_frontend_proc = self._web_spawn_frontend()
        except OSError as e:
            self._web_frontend_proc = None
            self.ui.err(self._t("webapp.err_start_front", "").format(err=e))
            return False
        if self._web_frontend_proc is None:
            self.ui.err(self._t("webapp.err_no_npm", ""))
            return False
        if announce:
            self.ui.ok(self._t("webapp.ok_start_front", ""))
        if open_browser:
            self._web_open_browser_tabs(backend=False, frontend=True)
        return True

    def _web_stop_backend(self) -> None:
        self._web_force_stop_backend()
        self.ui.ok(self._t("webapp.ok_stop_back", ""))

    def _web_stop_frontend(self) -> None:
        self._web_force_stop_frontend()
        self.ui.ok(self._t("webapp.ok_stop_front", ""))

    def _web_stop_both(self) -> None:
        self._web_force_stop_backend()
        self._web_force_stop_frontend()
        self.ui.ok(self._t("webapp.ok_stop_both", ""))

    def _web_restart_backend(self) -> bool:
        self._web_force_stop_backend()
        return self._web_start_backend(announce=True, open_browser=False)

    def _web_restart_frontend(self) -> bool:
        self._web_force_stop_frontend()
        return self._web_start_frontend(announce=True, open_browser=False)

    def _web_restart_both(self) -> None:
        self._web_force_stop_backend()
        self._web_force_stop_frontend()
        b = self._web_start_backend(announce=False, open_browser=False)
        f = self._web_start_frontend(announce=False, open_browser=False)
        if b and f:
            self.ui.ok(self._t("webapp.ok_start_both", ""))
            self._web_open_browser_tabs(backend=True, frontend=True)
        elif b:
            self.ui.ok(self._t("webapp.ok_start_back", ""))
            self._web_open_browser_tabs(backend=True, frontend=False)
        elif f:
            self.ui.ok(self._t("webapp.ok_start_front", ""))
            self._web_open_browser_tabs(backend=False, frontend=True)

    def web_app_dev_menu(self) -> None:
        """iniciar ou parar uvicorn + vite em subprocessos desta sessao do wizard."""
        while True:
            self._draw_web_app_menu()
            choice = self.ui.ask_line(self._t("webapp.prompt", "opcao (0-9): ")).strip()
            low = choice.lower()
            if low == "h":
                self.ui.hint(global_keys_hint(self.lang))
                self.ui.pause("enter...")
                continue
            if choice == "0" or low in ("c", "q", "cancel", "cancelar", "voltar", "back"):
                return
            if not choice:
                self.ui.warn(self._t("webapp.warn_invalid", ""))
                self.ui.pause("enter...")
                continue
            if choice == "1":
                b = self._web_start_backend(announce=False, open_browser=False)
                f = self._web_start_frontend(announce=False, open_browser=False)
                if b and f:
                    self.ui.ok(self._t("webapp.ok_start_both", ""))
                    self._web_open_browser_tabs(backend=True, frontend=True)
                elif b:
                    self.ui.ok(self._t("webapp.ok_start_back", ""))
                    self._web_open_browser_tabs(backend=True, frontend=False)
                elif f:
                    self.ui.ok(self._t("webapp.ok_start_front", ""))
                    self._web_open_browser_tabs(backend=False, frontend=True)
            elif choice == "2":
                self._web_start_backend(open_browser=True)
            elif choice == "3":
                self._web_start_frontend(open_browser=True)
            elif choice == "4":
                self._web_stop_backend()
            elif choice == "5":
                self._web_stop_frontend()
            elif choice == "6":
                self._web_stop_both()
            elif choice == "7":
                self._web_restart_backend()
                self._web_open_browser_tabs(backend=True, frontend=False)
            elif choice == "8":
                self._web_restart_frontend()
                self._web_open_browser_tabs(backend=False, frontend=True)
            elif choice == "9":
                self._web_restart_both()
            else:
                self.ui.warn(self._t("webapp.warn_invalid", ""))
            self.ui.pause("enter...")
    
    def run(self):
        """executar wizard"""
        try:
            self._run_main_loop()
        except KeyboardInterrupt:
            from graceful_shutdown import exit_on_user_interrupt

            exit_on_user_interrupt(self.lang)

    def _run_main_loop(self):
        while True:
            self._draw_main_menu()
            choice = self.ui.ask_line(self._t("prompt.main.choice", "opcao (1-5 ou 0): ")).strip()
            low = choice.lower()
            if low == "h":
                self.ui.hint(global_keys_hint(self.lang))
                self.ui.pause("enter...")
                continue
            if not choice:
                self.ui.warn(self._t("main.warn_empty", ""))
                self.ui.pause("enter...")
                continue
            if choice == "0":
                self.ui.muted(self._t("main.bye", ""))
                sys.exit(0)
            if low == "c" or low == "q":
                self.ui.warn(self._t("main.warn_exit_key", ""))
                self.ui.pause("enter...")
                continue

            if choice == "1":
                self.run_start_menu()
                self.ui.pause("enter para voltar ao menu principal...")
            elif choice == "2":
                self.web_app_dev_menu()
                self.ui.pause("enter para voltar ao menu principal...")
            elif choice == "3":
                self.show_help_menu()
            elif choice == "4":
                self.show_documentation()
            elif choice == "5":
                self.language_mode()
                self.ui.pause("enter para voltar ao menu principal...")
            else:
                self.ui.warn("escolha um numero de 1 a 5 ou 0 para sair")
                self.ui.pause("enter para voltar ao menu...")

def main():
    """entrada unifica typer rich comandos e legado argparse via dispatch main"""
    # dsl_dir deve preceder a raiz do repo para "import bed_wizard" resolver
    # para este modulo (dsl/bed_wizard.py) e nao para o atalho da raiz.
    if str(_DSL_DIR) in sys.path:
        sys.path.remove(str(_DSL_DIR))
    sys.path.insert(0, str(_DSL_DIR))
    from graceful_shutdown import install_graceful_shutdown
    from cli.app import dispatch_main

    install_graceful_shutdown("pt")
    try:
        sys.exit(dispatch_main())
    except KeyboardInterrupt:
        from graceful_shutdown import exit_on_user_interrupt

        exit_on_user_interrupt()

# quando executas python bed wizard py diretamente este bloco corre
# quando importas bed wizard como modulo este bloco nao corre
if __name__ == "__main__":
    main()
