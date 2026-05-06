# aplicacao typer principal bedwizard comandos e callback modo interativo
from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path
from typing import Optional

import typer

from cli.generate_driver import build_generate_argv, run_generate
from cli.render_common import print_equivalent_command, render_error, render_info

app = typer.Typer(
    name="bedwizard",
    help="cli bedwizard leitos empacotados modo interativo e comandos diretos",
    rich_markup_mode="rich",
    add_completion=True,
)

_LEGACY_FLAGS = frozenset(
    {
        "--load-json",
        "--spec",
        "--template",
        "--merge-json",
        "--output-bed",
        "--run-blender",
        "--open-blender",
        "--no-prompt",
        "--skip-compile",
        "--output-json",
        "--pure-python",
        "--slice",
        "--slice-thickness",
        "--slice-axis",
        "--slice-position",
        "--slice-keep-only",
        "--slice-keep-all",
        "--slice-recenter",
    }
)


class BackendChoice(str, Enum):
    pure_python = "pure_python"
    blender = "blender"


class PackingChoice(str, Enum):
    spherical_packing = "spherical_packing"
    hexagonal_3d = "hexagonal_3d"
    rigid_body = "rigid_body"


def _run_interactive_menu() -> None:
    from bed_wizard import BedWizard

    BedWizard().run()


def _print_cli_flags_help() -> None:
    """mostra --help do typer e exemplos de flags sem encerrar o interpretador."""
    argv_bak = sys.argv[:]
    prog = argv_bak[0] if argv_bak else "bed_wizard.py"
    try:
        sys.argv = [prog, "--help"]
        try:
            app()
        except SystemExit as se:
            if se.code not in (0, None):
                raise
    finally:
        sys.argv = argv_bak
    typer.echo()
    typer.secho("modo legado (mesmas flags que antes)", fg=typer.colors.CYAN)
    typer.echo(f'  {prog} --load-json params.json --output-bed saida.bed')
    typer.echo(f'  {prog} --template default --merge-json extra.json --output-bed out.bed')
    typer.echo()
    typer.secho("subcomandos typer (recomendado)", fg=typer.colors.CYAN)
    typer.echo(f"  {prog} generate --help")
    typer.echo(f"  {prog} test -i caso.bed --backend pure_python")
    typer.echo(f"  {prog} compile modelo.bed")
    typer.echo()


def _choose_startup_mode() -> bool:
    """sem argumentos pergunta interativo vs linha de comandos. retorna false se so mostrou ajuda."""
    typer.echo()
    typer.echo(" bed wizard — como pretende usar?")
    typer.echo("  [1] menu interativo (passo a passo no terminal)")
    typer.echo("  [2] linha de comandos (subcomandos e flags — ver ajuda e exemplos)")
    typer.echo()
    choice = typer.prompt("opcao (1 ou 2)", default="1").strip().lower()
    if choice in ("2", "cli", "flags", "f", "linha", "comandos"):
        _print_cli_flags_help()
        return False
    _run_interactive_menu()
    return True


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        if not _choose_startup_mode():
            raise typer.Exit(0)


@app.command("interactive")
def cmd_interactive() -> None:
    """abre o menu numerado completo do wizard"""
    _run_interactive_menu()


@app.command("wizard")
def cmd_wizard() -> None:
    """alias do menu interativo"""
    _run_interactive_menu()


@app.command("test")
def cmd_test(
    input_path: Optional[Path] = typer.Option(
        None,
        "--input",
        "-i",
        help="caminho para json ou ficheiro bed",
        path_type=Path,
    ),
    backend: Optional[BackendChoice] = typer.Option(
        None,
        "--backend",
        "-b",
        help="pure_python ou blender padrao vem do json",
    ),
    mode: Optional[PackingChoice] = typer.Option(
        None,
        "--mode",
        "-m",
        help="spherical_packing hexagonal_3d ou rigid_body",
    ),
    quick: bool = typer.Option(
        True,
        "--quick/--full",
        help="rapida so modelo ou completa bed compilar patch",
    ),
    open_blender: bool = typer.Option(
        False,
        "--open-blender",
        help="abrir blender apos sucesso",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-I",
        help="fluxo guiado com menus em vez de flags",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="mostrar resumo tecnico e preview ascii antes de executar",
    ),
    show_equivalent: bool = typer.Option(
        True,
        "--show-equivalent/--no-show-equivalent",
        help="mostrar comando equivalente ao fim",
    ),
    slice_enabled: bool = typer.Option(
        False,
        "--slice/--no-slice",
        help="ativar thin slice (pseudo 2d) no json de trabalho",
    ),
    slice_thickness: float = typer.Option(
        0.002,
        "--slice-thickness",
        help="espessura da fatia (m)",
    ),
    slice_axis: str = typer.Option(
        "y",
        "--slice-axis",
        help="eixo normal do corte (x|y|z)",
    ),
    slice_position: float = typer.Option(
        0.0,
        "--slice-position",
        help="posicao central da fatia (m) no eixo do corte",
    ),
    keep_only_intersecting_particles: bool = typer.Option(
        True,
        "--slice-keep-only/--slice-keep-all",
        help="remover particulas fora da fatia",
    ),
    preserve_original_packing: bool = typer.Option(
        True,
        "--slice-preserve/--slice-recenter",
        help="preservar coordenadas originais (senao recentra no plano)",
    ),
) -> None:
    """testes rapidos com json ou bed backend pure ou blender e preview rich"""
    from bed_wizard import BedWizard
    from wizard_quick_tests import (
        execute_quick_test_noninteractive,
        format_equivalent_test_command,
        run as run_quick_interactive,
    )

    if interactive:
        run_quick_interactive(BedWizard())
        raise typer.Exit(0)
    if input_path is None:
        typer.secho("erro use --input path.json ou path.bed ou flag --interactive", fg=typer.colors.RED)
        raise typer.Exit(2)
    p = input_path.resolve()
    if not p.is_file():
        typer.secho(f"erro ficheiro inexistente {p}", fg=typer.colors.RED)
        raise typer.Exit(2)

    w = BedWizard()
    bstr = backend.value if backend else None
    mstr = mode.value if mode else None
    code, bf, pf = execute_quick_test_noninteractive(
        w,
        input_path=p,
        backend=bstr,
        packing=mstr,
        quick=quick,
        open_blender=open_blender,
        verbose=verbose,
        slice_cfg=(
            {
                "slice_enabled": True,
                "slice_thickness": float(slice_thickness),
                "slice_axis": str(slice_axis).strip().lower(),
                "slice_position": float(slice_position),
                "keep_only_intersecting_particles": bool(keep_only_intersecting_particles),
                "preserve_original_packing": bool(preserve_original_packing),
            }
            if slice_enabled
            else None
        ),
    )
    if code == 0 and show_equivalent:
        print_equivalent_command(
            format_equivalent_test_command(
                input_path=p,
                backend=bf,
                packing=pf,
                quick=quick,
                open_blender=open_blender,
            )
        )
    raise typer.Exit(code)


@app.command("generate")
def cmd_generate(
    json_path: Optional[Path] = typer.Option(
        None,
        "--json",
        "-j",
        help="carregar parametros deste json",
        path_type=Path,
    ),
    spec: Optional[str] = typer.Option(None, "--spec", help="formato etiqueta@caminho"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="nome template em wizard_templates"),
    merge_json: Optional[Path] = typer.Option(None, "--merge-json", path_type=Path),
    output_bed: Optional[Path] = typer.Option(None, "--output-bed", path_type=Path),
    output_json: Optional[Path] = typer.Option(None, "--output-json", path_type=Path),
    skip_compile: bool = typer.Option(False, "--skip-compile"),
    pure_python: bool = typer.Option(False, "--pure-python"),
    run_blender: bool = typer.Option(False, "--run-blender"),
    open_blender: bool = typer.Option(False, "--open-blender"),
    no_prompt: bool = typer.Option(True, "--no-prompt/--prompt", help="sem perguntas no fim"),
    dry_run: bool = typer.Option(False, "--dry-run", help="so mostrar o que faria"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    slice_enabled: bool = typer.Option(
        False,
        "--slice/--no-slice",
        help="ativar thin slice (pseudo 2d) no json final",
    ),
    slice_thickness: float = typer.Option(0.002, "--slice-thickness", help="espessura da fatia (m)"),
    slice_axis: str = typer.Option("y", "--slice-axis", help="eixo normal do corte (x|y|z)"),
    slice_position: float = typer.Option(0.0, "--slice-position", help="posicao central da fatia (m)"),
    keep_only_intersecting_particles: bool = typer.Option(
        True,
        "--slice-keep-only/--slice-keep-all",
        help="remover particulas fora da fatia",
    ),
    preserve_original_packing: bool = typer.Option(
        True,
        "--slice-preserve/--slice-recenter",
        help="preservar coordenadas originais (senao recentra no plano)",
    ),
) -> None:
    """gerar bed compilar e opcionalmente stl pure ou cena blender"""
    if dry_run:
        render_info(
            "dry-run",
            "geraria bed e json a partir das flags sem gravar use sem dry-run para executar",
        )
        raise typer.Exit(0)
    if sum(x is not None for x in (json_path, spec, template)) != 1:
        typer.secho("erro escolha exactamente um entre --json --spec --template", fg=typer.colors.RED)
        raise typer.Exit(2)
    from bed_wizard import BedWizard

    argv = build_generate_argv(
        load_json=json_path,
        spec=spec,
        template=template,
        merge_json=merge_json,
        output_bed=output_bed,
        output_json=output_json,
        run_blender=run_blender,
        open_blender=open_blender,
        no_prompt=no_prompt,
        skip_compile=skip_compile,
        pure_python=pure_python,
        slice_enabled=slice_enabled,
        slice_thickness=float(slice_thickness),
        slice_axis=str(slice_axis).strip().lower(),
        slice_position=float(slice_position),
        slice_keep_only=bool(keep_only_intersecting_particles),
        slice_preserve=bool(preserve_original_packing),
    )
    if verbose:
        render_info("argv interno", " ".join(argv))
    code = run_generate(BedWizard(), argv)
    raise typer.Exit(code)


@app.command("compile")
def cmd_compile(
    bed: Path = typer.Argument(..., exists=True, help="ficheiro bed a compilar", path_type=Path),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """compilar um bed existente e gerar json ao lado"""
    from bed_wizard import BedWizard

    w = BedWizard()
    w.output_file = str(bed.resolve())
    if verbose:
        typer.echo(f"compilar {bed}")
    if not w.verify_and_compile():
        render_error("compilacao", str(bed))
        raise typer.Exit(1)
    typer.secho(f"ok json {Path(str(bed.resolve()) + '.json')}", fg=typer.colors.GREEN)
    raise typer.Exit(0)


@app.command("blender")
def cmd_blender(
    params: Path = typer.Option(
        ...,
        "--params",
        "-p",
        help="ficheiro json de parametros",
        path_type=Path,
        exists=True,
    ),
    open_after: bool = typer.Option(False, "--open-blender", help="abrir gui apos gerar"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """executar leito_extracao com json e formatos do proprio json"""
    from bed_wizard import BedWizard
    from wizard_json_loader import export_formats_for_blender, load_wizard_json

    w = BedWizard()
    data = load_wizard_json(params.resolve())
    fmt = export_formats_for_blender((data.get("export") or {}))
    if verbose:
        typer.echo(f"formatos {fmt}")
    ok, blend, out = w.run_blender_with_json_path(
        params.resolve(), open_after=open_after, formats=fmt
    )
    if not ok:
        raise typer.Exit(1)
    if verbose and out:
        typer.echo(out[-2000:])
    raise typer.Exit(0)


@app.command("pipeline")
def cmd_pipeline(
    interactive_only: bool = typer.Option(
        True,
        "--interactive/--no-interactive",
        help="pipeline completo requer fluxo guiado",
    ),
) -> None:
    """pipeline modelo openfoam e simulacao use modo guiado"""
    from bed_wizard import BedWizard

    if not interactive_only:
        typer.secho("erro pipeline completo so suportado no modo interativo por agora", fg=typer.colors.YELLOW)
        raise typer.Exit(2)
    w = BedWizard()
    w.pipeline_completo_mode()


@app.command("docs")
def cmd_docs() -> None:
    """mostrar documentacao no terminal (texto extraido do html)"""
    from bed_wizard import BedWizard

    BedWizard().show_documentation(standalone=True)


@app.command("help-sections")
def cmd_help_sections() -> None:
    """menu de ajuda por seccao bed particles packing"""
    from bed_wizard import BedWizard

    BedWizard().show_help_menu()


@app.command("templates")
def cmd_templates(
    interactive: bool = typer.Option(
        True,
        "--interactive/--list",
        help="modo guiado ou apenas listar nomes",
    ),
) -> None:
    """templates json listar ou editor guiado"""
    from bed_wizard import BedWizard
    from wizard_template_engine import list_template_names

    if not interactive:
        for n in list_template_names():
            typer.echo(n)
        raise typer.Exit(0)
    w = BedWizard()
    w.template_mode()


def dispatch_main() -> int:
    argv = sys.argv[1:]
    if not argv:
        _choose_startup_mode()
        return 0
    if any(a in _LEGACY_FLAGS for a in argv):
        from bed_wizard import BedWizard
        from wizard_cli import run_cli

        return run_cli(BedWizard(), argv)
    try:
        app()
    except SystemExit as e:
        c = e.code
        if c is None:
            return 0
        if isinstance(c, int):
            return c
        return 1
    return 0
