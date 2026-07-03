"""Core data types for Quorum deliberations."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Councilor:
    id: str
    role: str
    persona: str
    emoji: str = "🤖"
    is_skeptic: bool = False


@dataclass
class Council:
    name: str
    description: str
    councilors: list[Councilor]
    chair_persona: str = (
        "You are the impartial Chair of the council. You synthesize the "
        "deliberation faithfully, preserving dissent rather than erasing it."
    )

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Council":
        return cls(
            name=d["name"],
            description=d.get("description", ""),
            councilors=[Councilor(**c) for c in d["councilors"]],
            chair_persona=d.get("chair_persona", cls.chair_persona),
        )


@dataclass
class Case:
    title: str
    body: str
    council: str = "careers"
    language: str = "auto"  # auto | en | zh
    context: dict[str, Any] = field(default_factory=dict)  # e.g. sponsor data


@dataclass
class Ballot:
    councilor_id: str
    stance: str  # support | oppose | conditional
    confidence: float
    reasoning: str


@dataclass
class Verdict:
    decision: str
    summary: str
    vote_tally: dict[str, int]
    dissent: str
    action_plan: list[str]
    ballots: list[Ballot]
    disclaimer: str
    language: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
