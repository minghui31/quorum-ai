"""Quorum — a council of AI agents that deliberate your hardest decisions."""
from __future__ import annotations

from pathlib import Path

import yaml

from .backends import auto_backend
from .engine import Deliberation
from .schema import Case, Council, Verdict

__version__ = "0.1.0"
__all__ = ["Case", "Council", "Verdict", "Deliberation", "deliberate", "load_council"]

_COUNCILS_DIR = Path(__file__).parent / "councils"


def load_council(name_or_path: str) -> Council:
    p = Path(name_or_path)
    if not p.exists():
        p = _COUNCILS_DIR / f"{name_or_path}.yaml"
    if not p.exists():
        available = ", ".join(sorted(f.stem for f in _COUNCILS_DIR.glob("*.yaml")))
        raise FileNotFoundError(f"No council '{name_or_path}'. Built-in councils: {available}")
    return Council.from_dict(yaml.safe_load(p.read_text(encoding="utf-8")))


def deliberate(case: Case, backend=None, on_event=None) -> Verdict:
    """One-call API: quorum.deliberate(Case(title=..., body=..., council='careers'))."""
    council = load_council(case.council)
    return Deliberation(council, backend=backend or auto_backend(), on_event=on_event).run(case)
