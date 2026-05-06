# extrai texto legivel de documentacao html para mostrar no terminal
from __future__ import annotations

import re
from html import unescape
from pathlib import Path


def html_file_to_plain(path: Path) -> str:
    if not path.is_file():
        return ""
    raw = path.read_text(encoding="utf-8", errors="replace")
    return html_to_plain(raw)


def html_to_plain(html: str) -> str:
    html = re.sub(r"(?is)<script[^>]*>.*?</script>", "", html)
    html = re.sub(r"(?is)<style[^>]*>.*?</style>", "", html)
    html = re.sub(r"(?is)<nav[^>]*>.*?</nav>", "", html)
    html = re.sub(r"(?i)<\s*br\s*/?>", "\n", html)
    for tag in ("h1", "h2", "h3", "h4", "p", "li", "tr", "section", "header", "footer", "main"):
        html = re.sub(fr"(?i)</{tag}>", "\n", html)
    html = re.sub(r"<[^>]+>", "", html)
    text = unescape(html)
    lines: list[str] = []
    for ln in text.splitlines():
        s = " ".join(ln.split())
        if s:
            lines.append(s)
        elif lines and lines[-1] != "":
            lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines).strip()


def paginate_plain(text: str, lines_per_page: int = 36) -> list[str]:
    if not text.strip():
        return ["(documento vazio ou sem texto extraivel)"]
    lines = text.splitlines()
    pages: list[str] = []
    i = 0
    while i < len(lines):
        chunk = lines[i : i + lines_per_page]
        pages.append("\n".join(chunk))
        i += lines_per_page
    return pages
