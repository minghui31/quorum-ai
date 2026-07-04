# Contributing to Quorum

Thanks for wanting to make the council bigger. Three ways in, easiest first:

## 1. Add a council (no Python needed — this is the fun one)

Councils are single YAML files in `quorum/councils/`. Copy `dinner.yaml`, invent
five stakeholders with genuinely *conflicting incentives*, and open a PR. Ideas
we'd merge tomorrow: relocation council, grad-school council, pricing council,
"should I text them back" council, 春节回家 council.

Rules for a good council:
- Every councilor argues from a **role's interests**, not a personality quirk
- Exactly one councilor has `is_skeptic: true` — their job is attacking consensus
- Personas stay kind to people, harsh to plans
- Nothing that produces medical, legal, or financial *directives* — perspectives only

## 2. Report real deliberations

Ran a case and got a verdict that was brilliant, unhinged, or wrong? Open an
issue with the (redacted) case + transcript. Real transcripts drive persona
tuning better than any unit test.

## 3. Code

- `pip install -e ".[cli]" && python -m pytest tests/` (mock mode, no keys needed)
- Keep the protocol lean: 5 phases, cost-capped. PRs adding rounds/agents need a
  cost story.
- **Never weaken the disclaimers.** Verdict disclaimer text and the visa-warning
  logic in `quorum/i18n.py` / `engine.py` are load-bearing; PRs touching them
  need a very good reason.

## Contributor License Agreement

By submitting a PR you agree to the terms in [CLA.md](CLA.md) — in short: your
contribution is yours, you license it to the project, and you're okay with the
project offering commercial licenses alongside AGPL. One-time, painless.

## Conduct

Be the mentor persona, not the skeptic, to humans. 中英文 issues both welcome.
