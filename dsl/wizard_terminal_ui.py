"""
interface do wizard no terminal: layout limpo, tipo barra de endereco + tabela de opcoes.
usa rich se estiver instalado; caso contrario, modo texto simples compativel.
"""

from __future__ import annotations

import os
import textwrap
from typing import Any, Callable, List, Optional, Sequence, Tuple

try:
    from rich import box
    from rich.align import Align
    from rich.console import Console
    from rich.markup import escape
    from rich.panel import Panel
    from rich.prompt import Confirm
    from rich.rule import Rule
    from rich.table import Table
    from rich.text import Text
    from rich.theme import Theme

    _HAS_RICH = True
except ImportError:
    escape = None  # type: ignore
    _HAS_RICH = False

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.key_binding import KeyBindings

    _HAS_PROMPT_TOOLKIT = True
except ImportError:
    PromptSession = None  # type: ignore
    _HAS_PROMPT_TOOLKIT = False

MenuRow = Tuple[str, str, str]


def _menu_resume_two_lines(text: str, line_width: int) -> str:
    """quebra o resumo em exatamente 2 linhas (ascii); ellipsis se nao couber tudo."""
    text = " ".join((text or "").split())
    if not text:
        return "\n "
    w = max(12, int(line_width))
    wrapped = textwrap.wrap(text, width=w, break_long_words=True, break_on_hyphens=False)
    if not wrapped:
        return "\n "
    if len(wrapped) == 1:
        return f"{wrapped[0]}\n "
    first, second = wrapped[0], wrapped[1]
    if len(wrapped) > 2:
        room = max(1, w - 3)
        second = (second[:room] + "...") if len(second) > room else (second + "...")
    return f"{first}\n{second}"


def _wizard_prompt_session() -> Any:
    """sessao prompt_toolkit: historico, tab em atalhos comuns, sugestao do historico."""
    return PromptSession(
        history=InMemoryHistory(),
        completer=WordCompleter(
            ["?", "*", "n", "p", "q", "s", "sim", "nao", "c", "cancel", "cancelar"],
            ignore_case=True,
        ),
        auto_suggest=AutoSuggestFromHistory(),
        enable_history_search=True,
        complete_while_typing=False,
        multiline=False,
    )


def _parse_float_or(value: str, fallback: float) -> float:
    try:
        return float(str(value).strip())
    except Exception:
        return fallback


def _format_number_for_prompt(x: float) -> str:
    # mantem legivel e estavel: sem notacao cientifica "surpresa"
    if abs(x) >= 1e6 or (abs(x) > 0 and abs(x) < 1e-4):
        return f"{x:.6g}"
    s = f"{x:.10f}".rstrip("0").rstrip(".")
    return s if s else "0"


def _clamp(x: float, min_val: Optional[float], max_val: Optional[float]) -> float:
    if min_val is not None and x < min_val:
        return min_val
    if max_val is not None and x > max_val:
        return max_val
    return x


def _number_prompt_key_bindings(
    *,
    step: float,
    big_step: float,
    min_val: Optional[float],
    max_val: Optional[float],
) -> Any:
    kb = KeyBindings()

    def set_buffer(event: Any, new_value: float) -> None:
        v = _clamp(new_value, min_val, max_val)
        buf = event.app.current_buffer
        buf.text = _format_number_for_prompt(v)
        buf.cursor_position = len(buf.text)

    @kb.add("left")
    def _dec(event: Any) -> None:
        cur = _parse_float_or(event.app.current_buffer.text, 0.0)
        set_buffer(event, cur - step)

    @kb.add("right")
    def _inc(event: Any) -> None:
        cur = _parse_float_or(event.app.current_buffer.text, 0.0)
        set_buffer(event, cur + step)

    @kb.add("c-left")
    def _dec_big(event: Any) -> None:
        cur = _parse_float_or(event.app.current_buffer.text, 0.0)
        set_buffer(event, cur - big_step)

    @kb.add("c-right")
    def _inc_big(event: Any) -> None:
        cur = _parse_float_or(event.app.current_buffer.text, 0.0)
        set_buffer(event, cur + big_step)

    @kb.add("home")
    def _to_min(event: Any) -> None:
        if min_val is not None:
            set_buffer(event, min_val)

    @kb.add("end")
    def _to_max(event: Any) -> None:
        if max_val is not None:
            set_buffer(event, max_val)

    return kb


_WIZARD_THEME = Theme(
    {
        "wizard.chrome": "bold white on rgb(95,25,35)",
        "wizard.path": "dim italic",
        "wizard.path_seg": "bold rgb(240,212,168)",
        "wizard.accent": "bold rgb(240,212,168)",
        "wizard.section": "bold rgb(240,212,168)",
        "wizard.muted": "dim",
        "wizard.hint": "italic dim",
        "wizard.warn": "yellow",
        "wizard.err": "bold red",
        "wizard.ok": "green",
        "wizard.label": "bold",
    }
)


class PlainWizardUi:
    """fallback sem rich — mantem o wizard utilizavel."""

    def __init__(self) -> None:
        self._rich = False
        self._pt_session: Optional[Any] = None

    def clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def header(self, title: str, subtitle: str = "") -> None:
        print("=" * 62)
        print(f"  {title}")
        print("=" * 62)
        if subtitle:
            print(f"  {subtitle}")
        print()

    def section(self, title: str) -> None:
        print(f"\n--- {title} ---")

    def breadcrumbs(self, *parts: str) -> None:
        if not parts:
            return
        print("  " + " > ".join(parts))
        print()

    def println(self, *args, **kwargs) -> None:
        print(*args, **kwargs)

    def muted(self, msg: str) -> None:
        print(f"  {msg}")

    def hint(self, msg: str) -> None:
        print(f"  {msg}")

    def warn(self, msg: str) -> None:
        print(f"  aviso: {msg}")

    def err(self, msg: str) -> None:
        print(f"  erro: {msg}")

    def ok(self, msg: str) -> None:
        print(f"  {msg}")

    def param_help(self, lines: Sequence[str]) -> None:
        for line in lines:
            print(f"  {line}")
        print()

    def pause(self, msg: str = "pressione enter para continuar...") -> None:
        input(f"\n{msg}")

    def ask_line(self, prompt: str, default: str = "") -> str:
        if _HAS_PROMPT_TOOLKIT:
            if self._pt_session is None:
                self._pt_session = _wizard_prompt_session()
            try:
                return str(self._pt_session.prompt(prompt, default=default)).rstrip()
            except Exception:
                pass
        return input(prompt)

    def ask_number(
        self,
        prompt: str,
        default: str = "",
        *,
        step: float = 1.0,
        big_step: Optional[float] = None,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ) -> str:
        if _HAS_PROMPT_TOOLKIT:
            if self._pt_session is None:
                self._pt_session = _wizard_prompt_session()
            start = _parse_float_or(default, min_val if min_val is not None else 0.0)
            start = _clamp(start, min_val, max_val)
            if big_step is None:
                big_step = step * 10.0
            try:
                kb = _number_prompt_key_bindings(
                    step=step,
                    big_step=big_step,
                    min_val=min_val,
                    max_val=max_val,
                )
                return str(
                    self._pt_session.prompt(
                        prompt,
                        default=_format_number_for_prompt(start),
                        key_bindings=kb,
                    )
                ).rstrip()
            except Exception:
                pass
        return self.ask_line(prompt, default=default)

    def pick_from_list(
        self,
        caption: str,
        options: List[str],
        default_index: int = 0,
        help_callback: Optional[Callable[[], None]] = None,
        review_callback: Optional[Callable[[], None]] = None,
        cancel_callback: Optional[Callable[[], None]] = None,
    ) -> str:
        while True:
            print(f"\n{caption}")
            for i, option in enumerate(options):
                print(f"  {i + 1}. {option}")
            if help_callback or review_callback:
                print("  (? ajuda  * rever parametros)")
            if cancel_callback:
                print("  (c cancelar e voltar ao menu inicial)")
            try:
                raw = self.ask_line(
                    f"\nescolha (1-{len(options)}): ",
                    default=str(default_index + 1),
                ).strip()
                if cancel_callback and raw.lower() in ("c", "cancel", "cancelar", "voltar", "back"):
                    cancel_callback()
                    continue
                if raw == "?" and help_callback:
                    help_callback()
                    continue
                if raw == "*" and review_callback:
                    review_callback()
                    continue
                if not raw:
                    return options[default_index]
                idx = int(raw) - 1
                if 0 <= idx < len(options):
                    return options[idx]
                print(f"  aviso: escolha entre 1 e {len(options)}!")
            except ValueError:
                print("  aviso: digite um numero valido!")

    def confirm(
        self,
        message: str,
        default: bool = True,
        cancel_callback: Optional[Callable[[], None]] = None,
    ) -> bool:
        default_str = "sim" if default else "nao"
        while True:
            value = input(f"{message} (s/n) [{default_str}]: ").strip()
            if cancel_callback and value.lower() in ("c", "cancel", "cancelar", "voltar", "back"):
                cancel_callback()
                continue
            if not value:
                return default
            value = value.lower()
            if value in ("s", "sim", "y", "yes"):
                return True
            if value in ("n", "nao", "no"):
                return False
            print("  aviso: digite 's' para sim ou 'n' para nao!")

    def render_main_menu(self, rows: Sequence[MenuRow], title: str = "opcoes") -> None:
        print()
        print(f"  {title}")
        print("  " + "-" * 56)
        for key, titulo, desc in rows:
            desc2 = _menu_resume_two_lines(desc, 52)
            print(f"  [{key}]  {titulo}")
            for ln in desc2.splitlines():
                print(f"       {ln}")
            print()

    def render_help_section_menu(self, entries: Sequence[Tuple[str, str]], back_key: str = "0") -> None:
        print("secoes de ajuda:")
        for key, label in entries:
            print(f"  {key}. {label}")
        print(f"  {back_key}. voltar ao menu principal")
        print()

    def render_documentation_page(
        self,
        body: str,
        page_index: int,
        total_pages: int,
        control_hint: str,
    ) -> None:
        print()
        print(f"  --- documentacao  pagina {page_index + 1}/{total_pages} ---")
        print()
        for ln in body.splitlines():
            print(f"  {ln}")
        print()
        print(f"  {control_hint}")
        print()


class RichWizardUi:
    """terminal com paineis, tabelas e prompts alinhados ao estilo web (chrome + conteudo)."""

    def __init__(self) -> None:
        self._rich = True
        self._pt_session: Optional[Any] = None
        # soft_wrap evita quebrar layout em caminhos longos
        self.console = Console(theme=_WIZARD_THEME, highlight=False, soft_wrap=True)

    def clear(self) -> None:
        self.console.clear()

    def header(self, title: str, subtitle: str = "") -> None:
        chrome = Text()
        chrome.append(" bedflow atlas ", style="wizard.chrome")
        chrome.append(" ", style="")
        chrome.append("wizard://", style="wizard.path")
        seg = title.strip().lower().replace(" ", "-")[:48]
        chrome.append(seg if seg else "inicio", style="wizard.path_seg")
        bar = Panel(
            Align.left(chrome),
            box=box.HEAVY,
            border_style="rgb(95,25,35)",
            padding=(0, 1),
        )
        self.console.print(bar)
        if subtitle:
            self.console.print(Text(subtitle, style="wizard.muted"), end="\n\n")
        else:
            self.console.print()

    def section(self, title: str) -> None:
        self.console.print()
        self.console.print(Rule(Text(title.lower(), style="wizard.section"), style="rgb(95,25,35)"))

    def breadcrumbs(self, *parts: str) -> None:
        if not parts:
            return
        t = Text()
        t.append("wizard://", style="wizard.path")
        for i, p in enumerate(parts):
            if i:
                t.append(" / ", style="wizard.muted")
            t.append(p.lower(), style="wizard.path_seg")
        self.console.print(Align.left(t))
        self.console.print()

    def println(self, *args, **kwargs) -> None:
        self.console.print(*args, **kwargs)

    def muted(self, msg: str) -> None:
        self.console.print(Text(msg, style="wizard.muted"))

    def hint(self, msg: str) -> None:
        self.console.print(Text(msg, style="wizard.hint"))

    def warn(self, msg: str) -> None:
        self.console.print(Text(f"aviso: {msg}", style="wizard.warn"))

    def err(self, msg: str) -> None:
        self.console.print(Text(f"erro: {msg}", style="wizard.err"))

    def ok(self, msg: str) -> None:
        self.console.print(Text(msg, style="wizard.ok"))

    def param_help(self, lines: Sequence[str]) -> None:
        body = "\n".join(lines)
        self.console.print(
            Panel(
                body,
                title="ajuda",
                title_align="left",
                border_style="dim",
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )

    def pause(self, msg: str = "pressione enter para continuar...") -> None:
        self.console.input(f"\n[wizard.muted]{msg}[/] ")

    def ask_line(self, prompt: str, default: str = "") -> str:
        plain = escape(prompt) if escape else prompt
        if _HAS_PROMPT_TOOLKIT:
            if self._pt_session is None:
                self._pt_session = _wizard_prompt_session()
            try:
                return str(self._pt_session.prompt(plain, default=default)).rstrip()
            except Exception:
                pass
        return self.console.input(plain)

    def ask_number(
        self,
        prompt: str,
        default: str = "",
        *,
        step: float = 1.0,
        big_step: Optional[float] = None,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ) -> str:
        plain = escape(prompt) if escape else prompt
        if _HAS_PROMPT_TOOLKIT:
            if self._pt_session is None:
                self._pt_session = _wizard_prompt_session()
            start = _parse_float_or(default, min_val if min_val is not None else 0.0)
            start = _clamp(start, min_val, max_val)
            if big_step is None:
                big_step = step * 10.0
            try:
                kb = _number_prompt_key_bindings(
                    step=step,
                    big_step=big_step,
                    min_val=min_val,
                    max_val=max_val,
                )
                return str(
                    self._pt_session.prompt(
                        plain,
                        default=_format_number_for_prompt(start),
                        key_bindings=kb,
                    )
                ).rstrip()
            except Exception:
                pass
        return self.ask_line(prompt, default=default)

    def pick_from_list(
        self,
        caption: str,
        options: List[str],
        default_index: int = 0,
        help_callback: Optional[Callable[[], None]] = None,
        review_callback: Optional[Callable[[], None]] = None,
        cancel_callback: Optional[Callable[[], None]] = None,
    ) -> str:
        self.console.print()
        self.console.print(Text(caption, style="wizard.label"))
        table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="wizard.section", border_style="dim")
        table.add_column("#", justify="right", style="wizard.muted", width=4)
        table.add_column("opcao", style="")
        for i, opt in enumerate(options):
            table.add_row(str(i + 1), opt)
        self.console.print(table)
        if help_callback or review_callback:
            self.console.print(Text("? ajuda   * rever parametros", style="wizard.hint"))
        if cancel_callback:
            self.console.print(Text("c cancelar e voltar ao menu inicial", style="wizard.hint"))
        self.console.print()
        while True:
            raw = self.ask_line(
                f"numero (1-{len(options)}, enter={default_index + 1}): ",
                default=str(default_index + 1),
            ).strip()
            if cancel_callback and raw.lower() in ("c", "cancel", "cancelar", "voltar", "back"):
                cancel_callback()
                continue
            if raw == "?" and help_callback:
                help_callback()
                continue
            if raw == "*" and review_callback:
                review_callback()
                continue
            try:
                if not raw:
                    n = default_index + 1
                else:
                    n = int(raw)
                idx = int(n) - 1
                if 0 <= idx < len(options):
                    return options[idx]
                self.warn(f"escolha entre 1 e {len(options)}!")
            except (ValueError, TypeError):
                self.warn("digite um numero valido!")

    def confirm(
        self,
        message: str,
        default: bool = True,
        cancel_callback: Optional[Callable[[], None]] = None,
    ) -> bool:
        default_str = "sim" if default else "nao"
        while True:
            raw = self.console.input(f"{message} (s/n) [{default_str}]: ").strip()
            if cancel_callback and raw.lower() in ("c", "cancel", "cancelar", "voltar", "back"):
                cancel_callback()
                continue
            if not raw:
                return default
            v = raw.lower()
            if v in ("s", "sim", "y", "yes"):
                return True
            if v in ("n", "nao", "no"):
                return False
            self.warn("digite 's' para sim ou 'n' para nao!")

    def render_main_menu(self, rows: Sequence[MenuRow], title: str = "opcoes") -> None:
        self.console.print()
        table = Table(
            box=box.ROUNDED,
            show_header=True,
            show_lines=True,
            header_style="bold rgb(240,212,168)",
            border_style="rgb(95,25,35)",
            expand=True,
            pad_edge=True,
            title=title,
            title_style="wizard.muted",
        )
        table.add_column(
            "#",
            justify="center",
            style="wizard.accent",
            width=4,
            no_wrap=True,
        )
        # modo numa so linha evita celulas multilinha que partem o alinhamento da tabela
        table.add_column(
            "modo",
            style="bold default",
            min_width=24,
            max_width=36,
            no_wrap=True,
            overflow="ellipsis",
        )
        # separador visual entre "modo" e "resumo"
        table.add_column(
            "",
            justify="center",
            style="wizard.muted",
            width=1,
            no_wrap=True,
        )
        table.add_column(
            "resumo",
            style="wizard.muted",
            ratio=1,
            no_wrap=False,
            overflow="fold",
        )
        term_w = int(getattr(self.console, "width", None) or 80)
        # largura aproximada da celula resumo: terminal menos colunas fixas e bordas
        resume_w = max(16, term_w - 52)
        for key, titulo, desc in rows:
            desc_cell = _menu_resume_two_lines(desc, resume_w)
            table.add_row(key, titulo, "|", desc_cell)
        self.console.print(table)
        self.console.print()

    def render_help_section_menu(self, entries: Sequence[Tuple[str, str]], back_key: str = "0") -> None:
        table = Table(box=box.SIMPLE, show_header=False, border_style="dim")
        table.add_column("atalho", style="wizard.accent", width=6)
        table.add_column("secao", style="")
        for key, label in entries:
            table.add_row(key, label)
        table.add_row(back_key, "voltar ao menu principal")
        self.console.print(table)
        self.console.print()

    def render_documentation_page(
        self,
        body: str,
        page_index: int,
        total_pages: int,
        control_hint: str,
    ) -> None:
        title = f"documentacao — pagina {page_index + 1}/{total_pages}"
        self.console.print(
            Panel(
                body,
                title=title,
                title_align="left",
                border_style="dim",
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )
        self.console.print(Text(control_hint, style="wizard.hint"))


def make_terminal_ui():
    if _HAS_RICH:
        return RichWizardUi()
    return PlainWizardUi()


def rich_available() -> bool:
    return _HAS_RICH


def prompt_toolkit_available() -> bool:
    return _HAS_PROMPT_TOOLKIT
