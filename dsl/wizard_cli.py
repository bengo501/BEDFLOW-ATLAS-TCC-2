# interface de linha de comandos do bed wizard sem menu interactivo
# fluxo tipico carregar json gerar bed compilar patch json chamar blender
# should_hand_off_to_cli detecta se argv tem flags para nao entrar no menu
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# dsl precisa estar no path para importar wizard json loader e template engine
_DSL = Path(__file__).resolve().parent
_REPO = _DSL.parent
if str(_DSL) not in sys.path:
    sys.path.insert(0, str(_DSL))

from wizard_json_loader import (  # noqa: E402
    export_formats_for_blender,
    json_to_wizard_params,
    load_wizard_json,
    normalize_loaded_dict,
    parse_spec,
    patch_compiled_json_export,
    patch_compiled_json_slice,
    patch_compiled_json_metadata,
    patch_compiled_json_packing,
    resolve_repo_path,
)
from wizard_template_engine import load_template, merge_template  # noqa: E402


def build_arg_parser() -> argparse.ArgumentParser:
    # define todas as flags reconhecidas pelo main do bed wizard
    p = argparse.ArgumentParser(
        description="bed wizard modo cli use sem flags para menu interactivo"
    )
    p.add_argument(
        "--load-json",
        metavar="PATH",
        help="carregar parametros de um ficheiro json e gerar bed compilar",
    )
    p.add_argument(
        "--spec",
        metavar="LABEL@PATH",
        help="exemplo teste hex arroba caminho para o json",
    )
    p.add_argument(
        "--template",
        metavar="NAME",
        help="nome do template em dsl wizard_templates exemplo default spherical",
    )
    p.add_argument(
        "--merge-json",
        metavar="PATH",
        help="fundir este json por cima do template opcional",
    )
    p.add_argument(
        "--output-bed",
        metavar="PATH",
        help="caminho do ficheiro bed de saida padrao label bed no cwd",
    )
    p.add_argument(
        "--run-blender",
        action="store_true",
        help="apos compilar executar blender em background",
    )
    p.add_argument(
        "--open-blender",
        action="store_true",
        help="abrir o blend gerado no blender gui",
    )
    p.add_argument(
        "--no-prompt",
        action="store_true",
        help="nao perguntar se deve abrir o blender open blender vence",
    )
    p.add_argument(
        "--skip-compile",
        action="store_true",
        help="so escrever json final e opcionalmente blender sem bed",
    )
    p.add_argument(
        "--output-json",
        metavar="PATH",
        help="com skip compile gravar json merged aqui padrao cwd cli run json",
    )
    p.add_argument(
        "--pure-python",
        action="store_true",
        help="apos json final usar gerador packed_bed_stl em python puro",
    )
    p.add_argument(
        "--slice",
        action="store_true",
        help="ativar thin slice (pseudo 2d) no json final",
    )
    p.add_argument(
        "--slice-thickness",
        type=float,
        default=0.002,
        help="espessura da fatia (m)",
    )
    p.add_argument(
        "--slice-axis",
        type=str,
        default="y",
        help="eixo normal do corte (x|y|z)",
    )
    p.add_argument(
        "--slice-position",
        type=float,
        default=0.0,
        help="posicao central da fatia (m)",
    )
    p.add_argument(
        "--slice-keep-only",
        action="store_true",
        help="remover particulas fora da fatia (default)",
    )
    p.add_argument(
        "--slice-keep-all",
        action="store_true",
        help="nao remover particulas fora da fatia",
    )
    p.add_argument(
        "--slice-recenter",
        action="store_true",
        help="recentrar particulas no plano do corte (preserve_original_packing=false)",
    )
    return p


def _resolve_data_from_args(
    args: argparse.Namespace,
) -> Tuple[Dict[str, Any], str, Path]:
    # tres entradas mutuamente excluidas no uso real validadas em run_cli
    # template carrega base json e opcionalmente merge com outro json
    # spec usa parse spec com arroba
    # load json e caminho directo
    # normalize_loaded_dict garante packing mode no topo
    label = "cli_run"
    source: Optional[Path] = None

    if args.template:
        base = load_template(args.template)
        if args.merge_json:
            over = load_wizard_json(resolve_repo_path(args.merge_json))
            data = merge_template(base, over)
        else:
            data = base
        label = args.template.strip().replace(".json", "").replace("/", "_")
    elif args.spec:
        label, path = parse_spec(args.spec)
        data = load_wizard_json(path)
        source = path
    elif args.load_json:
        path = resolve_repo_path(args.load_json)
        data = load_wizard_json(path)
        label = path.stem
        source = path
    else:
        raise SystemExit("interno sem fonte de dados")

    normalize_loaded_dict(data)
    return data, label, source or Path(".")


def _cli_json_for_disk(data: Dict[str, Any], wizard_params: Dict[str, Any]) -> Dict[str, Any]:
    # alinha bed e metadados com o que o wizard usa para compilacao e pure python
    # este helper e usado apenas quando o user passa --skip-compile
    # nesse caso o pipeline nao gera o arquivo bed e nem passa pelo antlr
    # entao precisamos gravar um json final que o gerador pure python consiga ler
    out = deepcopy(data)
    out["bed"] = dict(wizard_params.get("bed") or {})
    if wizard_params.get("generation_backend") is not None:
        out["generation_backend"] = wizard_params["generation_backend"]
    if wizard_params.get("packing_mode") is not None:
        out["packing_mode"] = wizard_params["packing_mode"]
    return out


def _wants_pure_python(args: argparse.Namespace, wizard_params: Dict[str, Any]) -> bool:
    if args.pure_python:
        return True
    return str(wizard_params.get("generation_backend") or "") == "pure_python"


def run_cli(wizard: Any, argv: Optional[list[str]] = None) -> int:
    # wizard e instancia BedWizard ja criada para reutilizar generate bed verify compile blender
    # argv omitido usa padrao do argparse
    # codigo zero sucesso codigo um falha compilacao ou blender codigo dois falta fonte
    args = build_arg_parser().parse_args(argv)
    if not (args.load_json or args.spec or args.template):
        print("erro use load json spec ou template")
        return 2
    data, label, _ = _resolve_data_from_args(args)

    wizard.params = json_to_wizard_params(data)

    # flags de thin slice (pseudo 2d)
    if args.slice:
        axis = str(args.slice_axis or "y").strip().lower()
        if axis not in ("x", "y", "z"):
            axis = "y"
        keep_only = True
        if args.slice_keep_all:
            keep_only = False
        preserve = not bool(args.slice_recenter)
        wizard.params["slice"] = {
            "slice_enabled": True,
            "slice_thickness": float(args.slice_thickness),
            "slice_axis": axis,
            "slice_position": float(args.slice_position),
            "keep_only_intersecting_particles": bool(keep_only),
            "preserve_original_packing": bool(preserve),
        }

    if args.output_bed:
        out_bed = resolve_repo_path(args.output_bed)
    else:
        out_bed = (Path.cwd() / f"{label}.bed").resolve()

    wizard.output_file = str(out_bed)

    if args.skip_compile:
        # modo skip compile significa
        # 1 o sistema grava um json final no disco
        # 2 se generation_backend indicar pure python
        #    a geometria stl e gerada direto pelo modulo pure generation
        # 3 se nao indicar ou se o user pedir blender usamos o fluxo do blender
        out_json = (
            resolve_repo_path(args.output_json)
            if args.output_json
            else (Path.cwd() / "cli_run.json").resolve()
        )
        disk = _cli_json_for_disk(data, wizard.params)
        if wizard.params.get("slice"):
            disk["slice"] = wizard.params["slice"]
        with out_json.open("w", encoding="utf-8") as f:
            json.dump(disk, f, indent=2, ensure_ascii=False)
        wizard.output_file = str(out_bed)
        print(f"json gravado: {out_json}")
        want_pure = _wants_pure_python(args, wizard.params)
        if want_pure:
            ok, stl = wizard.run_pure_python_with_json_path(out_json)
            if not ok:
                return 1
            if stl and (
                args.open_blender
                or (
                    not args.no_prompt
                    and wizard.get_boolean(
                        "gostaria de abrir o blender com o stl gerado?", False
                    )
                )
            ):
                wizard.open_blender_gui_with_stl(stl)
        elif args.run_blender:
            fmt = export_formats_for_blender(wizard.params.get("export") or {})
            ok, blend, _bl_out = wizard.run_blender_with_json_path(
                out_json,
                open_after=args.open_blender,
                formats=fmt,
            )
            if not ok:
                return 1
            if (
                not args.no_prompt
                and not args.open_blender
                and blend
                and wizard.get_boolean("gostaria de abrir o blender com o modelo gerado?", False)
            ):
                wizard.open_blender_gui_with_blend(blend)
        return 0

    content = wizard.generate_bed_content()
    out_bed.parent.mkdir(parents=True, exist_ok=True)
    with open(wizard.output_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"gravado: {wizard.output_file}")

    if not wizard.verify_and_compile():
        print("falha na compilacao")
        return 1

    json_path = Path(str(Path(wizard.output_file).resolve()) + ".json")
    patch_compiled_json_packing(json_path, wizard.params)
    patch_compiled_json_export(json_path, wizard.params)
    patch_compiled_json_metadata(json_path, wizard.params)
    patch_compiled_json_slice(json_path, wizard.params)

    want_pure = _wants_pure_python(args, wizard.params)
    want_blender = args.run_blender or args.open_blender
    # aqui o cli decide o que fazer com o json compilado
    # se want_pure for true
    # chamamos o gerador stl sem blender
    # depois opcionalmente abrimos o blender com o arquivo stl
    # se want_blender for true
    # chamamos o blender para gerar os formatos configurados

    if want_pure:
        ok, stl = wizard.run_pure_python_with_json_path(json_path)
        if not ok:
            return 1
        if stl and (
            args.open_blender
            or (
                not args.no_prompt
                and wizard.get_boolean("gostaria de abrir o blender com o stl gerado?", False)
            )
        ):
            wizard.open_blender_gui_with_stl(stl)

    if want_blender:
        fmt = export_formats_for_blender(wizard.params.get("export") or {})
        ok, blend, _bl_out = wizard.run_blender_with_json_path(
            json_path,
            open_after=args.open_blender,
            formats=fmt,
        )
        if not ok:
            return 1
        if (
            not args.no_prompt
            and not args.open_blender
            and blend
            and wizard.get_boolean("gostaria de abrir o blender com o modelo gerado?", False)
        ):
            wizard.open_blender_gui_with_blend(blend)
    elif not want_pure:
        if not args.no_prompt and wizard.get_boolean(
            "executar blender agora para gerar o modelo 3d?", False
        ):
            fmt = export_formats_for_blender(wizard.params.get("export") or {})
            ok, blend, _bl_out = wizard.run_blender_with_json_path(
                json_path, open_after=False, formats=fmt
            )
            if ok and blend and wizard.get_boolean(
                "gostaria de abrir o blender com o modelo gerado?", False
            ):
                wizard.open_blender_gui_with_blend(blend)
        elif not args.no_prompt and wizard.get_boolean(
            "gerar stl em python puro agora (sem blender)?", False
        ):
            ok, stl = wizard.run_pure_python_with_json_path(json_path)
            if ok and stl and wizard.get_boolean(
                "gostaria de abrir o blender com o stl gerado?", False
            ):
                wizard.open_blender_gui_with_stl(stl)

    return 0


def should_hand_off_to_cli(argv: Optional[list[str]] = None) -> bool:
    # qualquer token que comece com dois hifens activa modo cli
    # h isolado tambem para mostrar help do argparse
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        return False
    return any(a.startswith("--") or a in ("-h",) for a in argv)
