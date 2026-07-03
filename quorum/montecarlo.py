"""Monte-Carlo deliberation: convene N independent councils, report the
verdict *distribution* instead of a single verdict.

One council tells you an answer. Fifty councils tell you how contested the
answer is — the modal outcome, the flip rate, and which dissent keeps
recurring. For real decisions, the shape of disagreement IS the information.

Cost guard: each run ≈ a dozen LLM calls. Default runs=10, hard cap via
QUORUM_MAX_RUNS (default 50). Mock mode simulates the full ensemble for free.
"""
from __future__ import annotations

import os
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from typing import Callable

from .backends import Backend, auto_backend
from .engine import Deliberation
from .schema import Case, Council, Verdict


class _SaltedBackend:
    """Wraps a backend, salting prompts per-run so ensemble runs decorrelate
    (mock mode becomes non-degenerate; real models get mild prompt diversity)."""

    def __init__(self, inner: Backend, salt: int):
        self._inner = inner
        self._salt = salt
        self.name = inner.name

    def chat(self, system: str, user: str) -> str:
        return self._inner.chat(system, f"{user}\n[ensemble run {self._salt}]")


@dataclass
class Ensemble:
    runs: int
    outcome_dist: dict[str, int]          # modal ballot stance per run → count
    modal_outcome: str
    flip_rate: float                      # share of runs disagreeing with the mode
    avg_confidence: float                 # mean ballot confidence across all runs
    recurring_dissent: list[str]          # dissent lines from non-modal runs (sample)
    sample_verdict: dict                  # one representative modal-run verdict
    disclaimer: str
    language: str
    verdicts: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _run_stance(v: Verdict) -> str:
    if not v.vote_tally:
        return "split"
    top = max(v.vote_tally.values())
    winners = [s for s, n in v.vote_tally.items() if n == top]
    return winners[0] if len(winners) == 1 else "split"


def simulate(
    case: Case,
    council: Council,
    runs: int = 10,
    backend: Backend | None = None,
    max_workers: int = 4,
    on_event: Callable[[dict], None] | None = None,
    keep_verdicts: bool = False,
) -> Ensemble:
    runs = min(runs, int(os.environ.get("QUORUM_MAX_RUNS", "50")))
    base = backend or auto_backend()
    emit = on_event or (lambda e: None)

    def one(i: int) -> Verdict:
        import copy

        d = Deliberation(copy.deepcopy(council), backend=_SaltedBackend(base, i))
        v = d.run(case)
        emit({"type": "run", "index": i, "stance": _run_stance(v), "total": runs})
        return v

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        verdicts = list(pool.map(one, range(runs)))

    stances = [_run_stance(v) for v in verdicts]
    dist = dict(Counter(stances))
    modal = max(dist, key=lambda s: dist[s])
    flips = sum(1 for s in stances if s != modal)
    confidences = [b.confidence for v in verdicts for b in v.ballots]
    dissents = [v.dissent for v, s in zip(verdicts, stances) if s != modal and v.dissent]
    sample = next(v for v, s in zip(verdicts, stances) if s == modal)

    ensemble = Ensemble(
        runs=runs,
        outcome_dist=dist,
        modal_outcome=modal,
        flip_rate=round(flips / runs, 3),
        avg_confidence=round(sum(confidences) / max(len(confidences), 1), 3),
        recurring_dissent=dissents[:3],
        sample_verdict=sample.to_dict(),
        disclaimer=sample.disclaimer,
        language=sample.language,
        verdicts=[v.to_dict() for v in verdicts] if keep_verdicts else [],
    )
    emit({"type": "ensemble", **{k: v for k, v in ensemble.to_dict().items() if k != "verdicts"}})
    return ensemble
