"""The Quorum council protocol.

Five phases, designed against groupthink:
  1. BRIEF     — the case is framed neutrally.
  2. OPENINGS  — councilors take positions INDEPENDENTLY (no cross-talk yet).
  3. CROSS-EXAM— the Skeptic attacks the strongest consensus; others rebut.
  4. VOTE      — structured JSON ballots: stance + confidence + reasoning.
  5. VERDICT   — the Chair synthesizes; dissent is preserved, never averaged away.

Every verdict carries a legal disclaimer. See quorum/i18n.py.
"""
from __future__ import annotations

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from .backends import Backend, auto_backend
from .i18n import DISCLAIMER, VISA_EXTRA, detect_language, lang_instruction
from .privacy import redact
from .schema import Ballot, Case, Council, Verdict

Event = dict
EventHandler = Callable[[Event], None]

_VISA_HINT = re.compile(r"visa|签证|immigration|移民|h-?1b|o-?1|绿卡|green card", re.I)


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}


class Deliberation:
    def __init__(
        self,
        council: Council,
        backend: Backend | None = None,
        on_event: EventHandler | None = None,
        max_workers: int = 5,
    ):
        self.council = council
        self.backend = backend or auto_backend()
        self.on_event = on_event or (lambda e: None)
        self.max_workers = max_workers

    # -- helpers --------------------------------------------------------------

    def _emit(self, **event) -> None:
        self.on_event(event)

    def _system(self, persona: str, lang: str) -> str:
        return (
            f"{persona}\n\nYou sit on the council '{self.council.name}': "
            f"{self.council.description}\nBe concrete and honest; no flattery. "
            "Plain text only — no markdown, no headers, no bullet lists. "
            "Argue the single strongest position YOUR role's incentives dictate; "
            "if you suspect the other councilors will say the same thing, sharpen "
            "the angle only your role can see instead of repeating the consensus. "
            "Never state statistics as fact — you have no live data. If a number "
            "matters, say 'roughly' or 'reportedly' and tell the user to verify "
            "the current figure. "
            f"Hard limit: 120 words. {lang_instruction(lang)}"
        )

    # -- protocol phases --------------------------------------------------------

    def run(self, case: Case) -> Verdict:
        # Cost guard: cap council size so a deliberation stays cheap by default.
        cap = int(os.environ.get("QUORUM_MAX_COUNCILORS", "7"))
        self.council.councilors = self.council.councilors[:cap]
        lang = case.language if case.language in ("en", "zh") else detect_language(case.body)
        body = redact(case.body)
        brief = f"CASE: {case.title}\n\n{body}"
        if case.context:
            brief += f"\n\nADDITIONAL CONTEXT:\n{json.dumps(case.context, ensure_ascii=False)}"
        self._emit(type="brief", title=case.title, language=lang, backend=self.backend.name)

        # Phase 2 — independent openings (parallel; no shared context).
        self._emit(type="phase", phase="openings")

        def opening(c):
            text = self.backend.chat(
                self._system(c.persona, lang),
                f"{brief}\n\nGive your OPENING position on this case from your role's perspective.",
            )
            self._emit(type="message", phase="openings", councilor=c.id, role=c.role, emoji=c.emoji, text=text)
            return c.id, text

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            openings = dict(pool.map(opening, self.council.councilors))

        # Phase 3 — cross-examination: skeptic challenges, others rebut.
        self._emit(type="phase", phase="cross_exam")
        skeptic = next((c for c in self.council.councilors if c.is_skeptic), self.council.councilors[-1])
        transcript = "\n\n".join(f"[{cid}]: {t}" for cid, t in openings.items())
        challenge = self.backend.chat(
            self._system(skeptic.persona, lang),
            f"{brief}\n\nOPENING POSITIONS:\n{transcript}\n\n[CHALLENGE] Attack the strongest "
            "point of consensus above. What is everyone conveniently ignoring?",
        )
        self._emit(type="message", phase="cross_exam", councilor=skeptic.id, role=skeptic.role, emoji=skeptic.emoji, text=challenge)

        rebuttals = {}
        for c in self.council.councilors:
            if c.id == skeptic.id:
                continue
            reb = self.backend.chat(
                self._system(c.persona, lang),
                f"{brief}\n\nYour opening: {openings[c.id]}\n\nThe skeptic's challenge: {challenge}\n\n"
                "[REBUT] Respond briefly: concede, counter, or revise your position.",
            )
            rebuttals[c.id] = reb
            self._emit(type="message", phase="cross_exam", councilor=c.id, role=c.role, emoji=c.emoji, text=reb)

        # Phase 4 — structured vote.
        self._emit(type="phase", phase="vote")
        ballots: list[Ballot] = []
        for c in self.council.councilors:
            raw = self.backend.chat(
                self._system(c.persona, lang),
                f"{brief}\n\nFull deliberation so far:\n{transcript}\n\nChallenge: {challenge}\n\n"
                '[BALLOT] Cast your vote as JSON only: {"stance": "support|oppose|conditional", '
                '"confidence": 0.0-1.0, "reasoning": "one sentence"}',
            )
            d = _extract_json(raw)
            ballot = Ballot(
                councilor_id=c.id,
                stance=str(d.get("stance", "conditional")).lower(),
                confidence=float(d.get("confidence", 0.5)),
                reasoning=str(d.get("reasoning", raw))[:500],
            )
            ballots.append(ballot)
            self._emit(type="ballot", councilor=c.id, role=c.role, emoji=c.emoji, **ballot.__dict__)

        tally: dict[str, int] = {}
        for b in ballots:
            tally[b.stance] = tally.get(b.stance, 0) + 1

        # Phase 5 — synthesis by the Chair; dissent preserved.
        self._emit(type="phase", phase="verdict")
        ballots_txt = "\n".join(f"[{b.councilor_id}] {b.stance} ({b.confidence}): {b.reasoning}" for b in ballots)
        raw = self.backend.chat(
            self._system(self.council.chair_persona, lang),
            f"{brief}\n\nOPENINGS:\n{transcript}\n\nCHALLENGE:\n{challenge}\n\nBALLOTS:\n{ballots_txt}\n\n"
            "[SYNTHESIZE] Produce the council's verdict as JSON only: "
            '{"decision": "...", "summary": "...", "dissent": "the strongest minority view, verbatim spirit", '
            '"action_plan": ["3-5 concrete next steps"]}',
        )
        d = _extract_json(raw)
        disclaimer = DISCLAIMER[lang]
        if _VISA_HINT.search(case.title + " " + body):
            disclaimer += "\n" + VISA_EXTRA[lang]

        verdict = Verdict(
            decision=d.get("decision", ""),
            summary=d.get("summary", raw),
            vote_tally=tally,
            dissent=d.get("dissent", ""),
            action_plan=list(d.get("action_plan", [])),
            ballots=ballots,
            disclaimer=disclaimer,
            language=lang,
        )
        self._emit(type="verdict", **verdict.to_dict())
        return verdict
