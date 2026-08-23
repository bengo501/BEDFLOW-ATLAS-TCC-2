#!/usr/bin/env python3
"""
atalho na raiz do repositorio: executa o wizard terminal em dsl/bed_wizard.py.

uso (a partir da pasta bedflow-atlas):
  python bed_wizard.py

equivalente:
  python dsl/bed_wizard.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_DSL = Path(__file__).resolve().parent / "dsl"
_MAIN = _DSL / "bed_wizard.py"

if not _MAIN.is_file():
    print(f"erro: ficheiro nao encontrado: {_MAIN}", file=sys.stderr)
    sys.exit(1)

if str(_DSL) not in sys.path:
    sys.path.insert(0, str(_DSL))

import bed_wizard as _bw  # noqa: E402

if __name__ == "__main__":
    _bw.main()
