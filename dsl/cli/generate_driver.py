# ponte entre opcoes typer do comando generate e o motor existente wizard cli run cli
# nao gera geometria so monta lista argv compativel com o parser antigo
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from wizard_cli import run_cli


def build_generate_argv(
    *,
    load_json: Optional[Path] = None,
    spec: Optional[str] = None,
    template: Optional[str] = None,
    merge_json: Optional[Path] = None,
    output_bed: Optional[Path] = None,
    output_json: Optional[Path] = None,
    run_blender: bool = False,
    open_blender: bool = False,
    no_prompt: bool = True,
    skip_compile: bool = False,
    pure_python: bool = False,
    slice_enabled: bool = False,
    slice_thickness: float = 0.002,
    slice_axis: str = "y",
    slice_position: float = 0.0,
    slice_keep_only: bool = True,
    slice_preserve: bool = True,
) -> List[str]:
    # argv e a lista de strings que simula sys argv depois do nome do programa
    argv: List[str] = []
    # template tem prioridade sobre spec e sobre load json
    if template:
        argv.extend(["--template", template])
        if merge_json is not None:
            argv.extend(["--merge-json", str(merge_json)])
    elif spec:
        argv.extend(["--spec", spec])
    elif load_json:
        argv.extend(["--load-json", str(load_json)])
    else:
        raise ValueError("precisa de --json --spec ou --template")
    if output_bed:
        argv.extend(["--output-bed", str(output_bed)])
    if output_json:
        argv.extend(["--output-json", str(output_json)])
    if skip_compile:
        argv.append("--skip-compile")
    if run_blender:
        argv.append("--run-blender")
    if open_blender:
        argv.append("--open-blender")
    if no_prompt:
        argv.append("--no-prompt")
    if pure_python:
        argv.append("--pure-python")
    if slice_enabled:
        argv.append("--slice")
        argv.extend(["--slice-thickness", str(slice_thickness)])
        argv.extend(["--slice-axis", str(slice_axis)])
        argv.extend(["--slice-position", str(slice_position)])
        if not slice_keep_only:
            argv.append("--slice-keep-all")
        if not slice_preserve:
            argv.append("--slice-recenter")
    return argv


def run_generate(wizard: object, argv: List[str]) -> int:
    # wizard e a instancia bed wizard ja configurada
    # argv vem de build generate argv
    # retorno inteiro e codigo de saida convencional zero sucesso
    return run_cli(wizard, argv)
