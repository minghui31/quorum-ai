"""Smoke tests — run entirely on the mock backend, no keys needed."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from quorum import Case, deliberate, load_council
from quorum.backends import MockBackend
from quorum.i18n import detect_language
from quorum.privacy import redact


def test_english_deliberation():
    events = []
    v = deliberate(
        Case(title="Offer A vs B?", body="Two offers, which one?", council="careers"),
        backend=MockBackend(),
        on_event=events.append,
    )
    assert v.language == "en"
    assert len(v.ballots) == 5
    assert sum(v.vote_tally.values()) == 5
    assert v.action_plan
    assert "not a guarantee" in v.disclaimer
    assert any(e["type"] == "verdict" for e in events)


def test_chinese_and_visa_disclaimer():
    v = deliberate(
        Case(title="签证怎么办", body="我在考虑 O-1 签证还是 H-1B，该怎么选？", council="careers"),
        backend=MockBackend(),
    )
    assert v.language == "zh"
    assert "不构成任何保证" in v.disclaimer
    assert "移民律师" in v.disclaimer  # visa topics get the extra warning


def test_language_detection():
    assert detect_language("Should I take this job?") == "en"
    assert detect_language("我该接受这份工作吗？") == "zh"


def test_redaction():
    out = redact("Contact me at alice@example.com or +1 (555) 123-4567, passport E12345678.")
    assert "alice@example.com" not in out
    assert "123-4567" not in out
    assert "E12345678" not in out


def test_all_builtin_councils_load():
    for name in ("careers", "dinner", "book_club"):
        c = load_council(name)
        assert c.councilors, name


def test_monte_carlo_ensemble():
    from quorum.montecarlo import simulate

    ens = simulate(
        Case(title="A or B?", body="Two options, council.", council="dinner"),
        load_council("dinner"),
        runs=8,
        backend=MockBackend(),
    )
    assert ens.runs == 8
    assert sum(ens.outcome_dist.values()) == 8
    assert ens.modal_outcome in ("support", "oppose", "conditional", "split")
    assert 0.0 <= ens.flip_rate <= 1.0
    assert len(ens.outcome_dist) >= 2, "salting should decorrelate mock runs"
    assert "not a guarantee" in ens.disclaimer
