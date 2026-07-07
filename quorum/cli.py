"""Quorum CLI.

    quorum demo                    # fun demo, zero keys needed (mock or real)
    quorum deliberate case.yaml    # run any case file
    quorum deliberate case.yaml --backend mock --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from . import deliberate
from .backends import auto_backend, load_env_file
from .i18n import UI
from .schema import Case

try:
    from rich.console import Console
    from rich.panel import Panel

    _console: "Console | None" = Console()
except ImportError:  # graceful degradation — plain stdout
    _console = None


def _print(text: str, style: str = "") -> None:
    if _console:
        _console.print(text, style=style)
    else:
        print(text)


def _render(event: dict, lang_holder: dict) -> None:
    t = event["type"]
    if t == "brief":
        lang_holder["lang"] = event["language"]
        _print(f"\n⚖️  QUORUM · {event['title']}  [backend: {event['backend']}]", "bold")
    elif t == "phase":
        key = {"openings": "phase_openings", "cross_exam": "phase_crossexam",
               "vote": "phase_vote", "verdict": "phase_verdict"}[event["phase"]]
        _print(f"\n━━ {UI[key][lang_holder.get('lang', 'en')]} ━━", "bold cyan")
    elif t == "message":
        _print(f"\n{event['emoji']} {event['role']}:", "bold yellow")
        _print(f"   {event['text']}")
    elif t == "ballot":
        icon = {"support": "✅", "oppose": "❌", "conditional": "🤔"}.get(event["stance"], "❓")
        _print(f" {icon} {event['emoji']} {event['role']} — {event['stance']} ({event['confidence']:.0%}): {event['reasoning']}")
    elif t == "verdict":
        lang = event["language"]
        body = (
            f"[bold]{event['decision']}[/bold]\n\n{event['summary']}\n\n"
            f"[bold]{UI['dissent'][lang]}:[/bold] {event['dissent']}\n\n"
            f"[bold]{UI['action_plan'][lang]}:[/bold]\n"
            + "\n".join(f"  {i}. {s}" for i, s in enumerate(event["action_plan"], 1))
            + f"\n\n[dim]{event['disclaimer']}[/dim]"
        )
        if _console:
            _console.print(Panel(body, title="⚖️ Verdict", border_style="green"))
        else:
            print("\n=== VERDICT ===\n" + body.replace("[bold]", "").replace("[/bold]", "").replace("[dim]", "").replace("[/dim]", ""))


def _load_case(path: str) -> Case:
    d = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return Case(
        title=d["title"],
        body=d.get("case", d.get("body", "")),
        council=d.get("council", "careers"),
        language=d.get("language", "auto"),
        context=d.get("context", {}),
    )


_STANCE_ICON = {"support": "✅", "oppose": "❌", "conditional": "🤔", "split": "⚖️"}


def _simulate(args) -> int:
    from . import load_council
    from .montecarlo import simulate

    case = _load_case(args.case)
    council = load_council(case.council)
    done: list = []

    def render(e: dict) -> None:
        if e["type"] == "run":
            done.append(e)
            icon = _STANCE_ICON.get(e["stance"], "❓")
            _print(f"  council {len(done):>3}/{e['total']} resolved → {icon} {e['stance']}")

    _print(f"\n⚖️  QUORUM ENSEMBLE · {case.title} · {args.runs} councils convening…", "bold")
    try:
        ens = simulate(case, council, runs=args.runs,
                       backend=auto_backend(args.backend),
                       on_event=None if args.json else render)
    except Exception as exc:
        if "401" in str(exc):
            _print("\n❌ Authentication failed (401) — see `quorum demo` help; or use --backend mock.", "bold red")
            return 1
        raise
    if args.json:
        print(json.dumps(ens.to_dict(), ensure_ascii=False, indent=2))
        return 0
    _print("\n━━ Verdict distribution ━━", "bold cyan")
    for stance, n in sorted(ens.outcome_dist.items(), key=lambda kv: -kv[1]):
        bar = "█" * round(30 * n / ens.runs)
        _print(f" {_STANCE_ICON.get(stance, '❓')} {stance:<12} {bar} {n}/{ens.runs} ({n / ens.runs:.0%})")
    _print(f"\n Modal outcome: {ens.modal_outcome}  ·  flip rate {ens.flip_rate:.0%}  ·  avg ballot confidence {ens.avg_confidence:.0%}")
    if ens.recurring_dissent:
        _print(f" Recurring dissent: {ens.recurring_dissent[0]}")
    _print(f"\n{ens.disclaimer}")
    return 0


def main(argv: list[str] | None = None) -> int:
    load_env_file()  # picks up ANTHROPIC_API_KEY etc. from .env — no export needed
    p = argparse.ArgumentParser(prog="quorum", description="A council of AI agents deliberates your decision.")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("deliberate", help="Run a deliberation on a case file")
    d.add_argument("case", help="Path to a case YAML file")
    d.add_argument("--backend", choices=["anthropic", "openai", "camel", "mock"], default=None)
    d.add_argument("--json", action="store_true", help="Print the verdict as JSON")
    d.add_argument("--record", metavar="PATH", default=None,
                   help="Save the full Decision Record (versioned, auditable JSON) to PATH")

    demo = sub.add_parser("demo", help="Run the built-in fun demo (works with zero API keys)")
    demo.add_argument("--backend", choices=["anthropic", "openai", "camel", "mock"], default=None)
    demo.add_argument("--serious", action="store_true", help="Run the serious careers demo instead")
    demo.add_argument("--json", action="store_true")
    demo.add_argument("--record", metavar="PATH", default=None,
                      help="Save the full Decision Record (versioned, auditable JSON) to PATH")

    sim = sub.add_parser("simulate", help="Monte-Carlo: convene N councils, show the verdict distribution")
    sim.add_argument("case", help="Path to a case YAML file")
    sim.add_argument("--runs", type=int, default=10)
    sim.add_argument("--backend", choices=["anthropic", "openai", "camel", "mock"], default=None)
    sim.add_argument("--json", action="store_true")

    ver = sub.add_parser("verify", help="Verify a Decision Record's integrity hash")
    ver.add_argument("record", help="Path to a decision record JSON file")

    args = p.parse_args(argv)

    if args.cmd == "verify":
        from .record import verify_record

        r = json.loads(Path(args.record).read_text(encoding="utf-8"))
        ok = verify_record(r)
        rid, ver_ = r.get("id", "?"), r.get("record_version", "?")
        if ok:
            _print(f"✅ {rid} (record v{ver_}) — integrity verified, record is unaltered.", "bold green")
            return 0
        _print(f"❌ {rid} (record v{ver_}) — HASH MISMATCH: this record was modified after emission.", "bold red")
        return 1

    if args.cmd == "simulate":
        return _simulate(args)

    if args.cmd == "demo":
        examples = Path(__file__).parent.parent / "examples"
        case_path = examples / ("serious_case.yaml" if args.serious else "fun_case.yaml")
        case = _load_case(str(case_path))
    else:
        case = _load_case(args.case)

    lang_holder: dict = {}
    try:
        verdict = deliberate(
            case,
            backend=auto_backend(args.backend),
            on_event=None if args.json else (lambda e: _render(e, lang_holder)),
        )
    except Exception as exc:
        msg = str(exc)
        if "401" in msg:
            _print("\n❌ Authentication failed (401): your API key is missing or invalid.", "bold red")
            _print("   Check it:   echo $ANTHROPIC_API_KEY   (should start with sk-ant-)")
            _print("   Set it:     export ANTHROPIC_API_KEY=sk-ant-...   (no quotes or trailing text)")
            _print("   No key?     quorum demo --backend mock   runs free, instantly.")
            return 1
        if "404" in msg and "model" in msg.lower():
            _print("\n❌ Model not found. Try:   export QUORUM_MODEL=claude-sonnet-5", "bold red")
            return 1
        raise
    if args.json:
        print(json.dumps(verdict.to_dict(), ensure_ascii=False, indent=2))
    if getattr(args, "record", None):
        Path(args.record).write_text(
            json.dumps(verdict.record, ensure_ascii=False, indent=2), encoding="utf-8")
        _print(f"\n📋 Decision record saved → {args.record}  (id: {verdict.record.get('id', '?')})", "bold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
