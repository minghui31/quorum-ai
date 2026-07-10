"""The Decision Record — Quorum's core primitive.

ChatGPT is for chat; Quorum is for decisions. A deliberation is only worth
what you can audit later, so every run emits a DECISION RECORD: a structured,
versioned JSON artifact carrying the full trail — framing, every agent's
independent opening, the adversarial cross-examination, each ballot with its
confidence, and the verdict with dissent preserved. Think "git for decisions":
the record is the commit, the dissent is the diff that didn't win.

Schema stability contract: RECORD_VERSION bumps on any breaking change to the
shape below. Additive fields do NOT bump the major version.

    {
      "record_version": "1.0",
      "id": "qr_...",                     # derived from content hash — stable, verifiable
      "created_at": "2026-07-06T09:00:00Z",
      "engine":  {"name", "version", "backend", "protocol"},
      "case":    {"title", "body", "council", "language", "context"},   # body is post-redaction
      "council": {"name", "description", "councilors":[{"id","role","emoji","is_skeptic"}]},
      "deliberation": {
        "openings":   [{"councilor_id", "text"}],                        # independent, parallel
        "cross_examination": {"challenger_id", "challenge",
                              "rebuttals":[{"councilor_id","text"}]},
        "ballots":    [{"councilor_id", "stance", "confidence", "reasoning"}]
      },
      "verdict": {"decision", "summary", "vote_tally", "dissent", "action_plan"},
      "disclaimer": "...",                # travels with the record, always
      "integrity": {"algorithm": "sha256", "content_hash": "..."}
    }
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from .schema import Case, Council, Verdict

RECORD_VERSION = "1.0"
_ENGINE_VERSION = "0.1.1"
_PROTOCOL = "brief/openings/cross-exam/vote/verdict v1"


def _canonical(d: dict[str, Any]) -> str:
    return json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build_record(
    case: Case,
    council: Council,
    *,
    body_redacted: str,
    language: str,
    openings: dict[str, str],
    challenger_id: str,
    challenge: str,
    rebuttals: dict[str, str],
    verdict: Verdict,
    backend_name: str,
    created_at: datetime | None = None,
) -> dict[str, Any]:
    """Assemble the full, auditable decision record for one deliberation."""
    created = (created_at or datetime.now(timezone.utc)).isoformat(timespec="seconds")
    record: dict[str, Any] = {
        "record_version": RECORD_VERSION,
        "created_at": created,
        "engine": {
            "name": "quorum-council",
            "version": _ENGINE_VERSION,
            "backend": backend_name,
            "protocol": _PROTOCOL,
        },
        "case": {
            "title": case.title,
            "body": body_redacted,  # PII-redacted framing, as deliberated
            "council": case.council,
            "language": language,
            "context": case.context,
        },
        "council": {
            "name": council.name,
            "description": council.description,
            "councilors": [
                {"id": c.id, "role": c.role, "emoji": c.emoji, "is_skeptic": c.is_skeptic}
                for c in council.councilors
            ],
        },
        "deliberation": {
            "openings": [
                {"councilor_id": cid, "text": text} for cid, text in openings.items()
            ],
            "cross_examination": {
                "challenger_id": challenger_id,
                "challenge": challenge,
                "rebuttals": [
                    {"councilor_id": cid, "text": text} for cid, text in rebuttals.items()
                ],
            },
            "ballots": [
                {
                    "councilor_id": b.councilor_id,
                    "stance": b.stance,
                    "confidence": b.confidence,
                    "reasoning": b.reasoning,
                }
                for b in verdict.ballots
            ],
        },
        "verdict": {
            "decision": verdict.decision,
            "summary": verdict.summary,
            "vote_tally": verdict.vote_tally,
            "dissent": verdict.dissent,
            "action_plan": verdict.action_plan,
        },
        "disclaimer": verdict.disclaimer,
    }
    digest = hashlib.sha256(_canonical(record).encode("utf-8")).hexdigest()
    record["id"] = f"qr_{digest[:16]}"
    record["integrity"] = {"algorithm": "sha256", "content_hash": digest}
    return record


def verify_record(record: dict[str, Any]) -> bool:
    """Re-hash a record (minus id/integrity) and check it hasn't been altered."""
    claimed = record.get("integrity", {}).get("content_hash", "")
    body = {k: v for k, v in record.items() if k not in ("id", "integrity")}
    return hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest() == claimed
