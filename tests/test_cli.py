"""CLI output mode tests (mock backend, no API keys required)."""
from __future__ import annotations

import json

from quorum.cli import main


def test_deliberate_json_output_unchanged(tmp_path, capsys):
    case_file = tmp_path / "case.yaml"
    case_file.write_text(
        """
title: Offer A vs B?
case: Two offers, which one?
council: careers
language: en
""".strip()
        + "\n",
        encoding="utf-8",
    )

    code = main(["deliberate", str(case_file), "--backend", "mock", "--json"])
    assert code == 0

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["decision"]
    assert payload["vote_tally"]
    assert payload["disclaimer"]


def test_deliberate_markdown_output(tmp_path, capsys):
    case_file = tmp_path / "case.yaml"
    case_file.write_text(
        """
title: Offer A vs B?
case: Two offers, which one?
council: careers
language: en
""".strip()
        + "\n",
        encoding="utf-8",
    )

    code = main(["deliberate", str(case_file), "--backend", "mock", "--output", "markdown"])
    assert code == 0

    out = capsys.readouterr().out.strip()
    assert out.startswith("# ")
    assert "## Vote Tally" in out
    assert "| Stance | Count |" in out
    assert "## Dissent" in out
    assert "\n> " in out
    assert "## Action Plan" in out
    assert "\n1. " in out
    assert "\n---\n" in out
    assert out.splitlines()[-1]


def test_demo_markdown_output(capsys):
    code = main(["demo", "--backend", "mock", "--output", "markdown"])
    assert code == 0

    out = capsys.readouterr().out.strip()
    assert out.startswith("# ")
    assert "## Vote Tally" in out
    assert "## Dissent" in out
    assert "## Action Plan" in out
    assert "\n---\n" in out
