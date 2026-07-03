<div align="center">

# ⚖️ Quorum

**A council of AI agents deliberates your hardest decision — and shows its work.**

*Five agents with different jobs, incentives, and doubts argue your case in the open:
opening positions → cross-examination → a real vote → a verdict with dissent preserved.*

[![License: AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-blue)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Built on CAMEL-AI](https://img.shields.io/badge/built%20on-CAMEL--AI-orange)](https://github.com/camel-ai/camel)

**English** · [简体中文](README.zh-CN.md)

<!-- 🎬 demo.gif goes here — the council arguing live -->

</div>

---

## Why a council?

Ask one AI and you get one confident answer. Ask a **council** and you get what real
decisions deserve: competing perspectives, a designated skeptic attacking the consensus,
a structured vote with confidence levels, and a verdict that **preserves the dissent
instead of averaging it away**. Consensus is not verification — when five agents agree
instantly, that's a red flag, not a conclusion. Quorum is built around that idea.

## Not another multi-model council

"Ask several AIs and merge the answers" already exists — products send one question
to GPT + Claude + Gemini and synthesize. Quorum is built on a different bet:
**diversity of *incentives* beats diversity of *weights*.** A recruiter, a hiring
manager, and a visa officer don't disagree because they're different models — they
disagree because their *jobs* make them see different risks. Quorum makes that
structural:

- **Stakeholder personas, not model ensembles** — each councilor argues its role's interests
- **Independent parallel openings** — no one sees anyone else's answer first (no anchoring)
- **A designated Skeptic** whose only job is attacking whatever consensus forms
- **Ballots with confidence, verdicts with dissent** — the minority view survives synthesis
- **Councils are YAML** — define your own five stakeholders in 20 lines

## Quickstart (zero API keys needed)

```bash
git clone https://github.com/minghui31/quorum-ai && cd quorum-ai
pip install -e ".[cli]"
quorum demo            # 🍜 the dinner council convenes (mock mode — instant, free)
quorum demo --serious  # 🛂 the careers council debates a real career/visa decision
```

Add a key to make it real (any one of these):

```bash
export ANTHROPIC_API_KEY=sk-ant-...        # best quality
# or any OpenAI-compatible API (OpenAI, DeepSeek, Qwen, local vLLM):
export OPENAI_API_KEY=... OPENAI_BASE_URL=https://api.deepseek.com/v1 QUORUM_MODEL=deepseek-chat
quorum deliberate examples/offer_case.yaml
```

**Web demo** (watch them argue live + download a shareable verdict card):

```bash
cp .env.example .env   # add a key, or leave empty for mock mode
docker compose up      # → http://localhost:8000
```

## How it works

```
     CASE (any language — the council answers in yours)
        │
  ① BRIEF ──► ② OPENINGS ──► ③ CROSS-EXAM ──► ④ VOTE ──► ⑤ VERDICT
              independent,     the Skeptic      JSON        majority view
              parallel — no    attacks the      ballots +   + dissent kept
              groupthink       consensus        confidence  + action plan
```

Agents run on [CAMEL-AI](https://github.com/camel-ai/camel)'s agent substrate
(`pip install "quorum-ai[camel]"`), with direct Anthropic / OpenAI-compatible
backends and a deterministic **mock mode** so the repo runs anywhere, instantly.

## Councils are just YAML

```yaml
name: careers
councilors:
  - id: recruiter      # 🎯 market signal
  - id: hiring_manager # 🧑‍💼 would I spend a headcount on you?
  - id: visa_officer   # 🛂 evidence, timelines, risk (illustrative only)
  - id: mentor         # 🌱 the 10-year view
  - id: skeptic        # 🔥 designated devil's advocate
```

Built-ins: `careers` (flagship), `dinner` (fun), `book_club` (deliberates the great
unresolved questions of fiction — try the 《红楼梦》 ending). Write your own council
in 20 lines and drop it in `quorum/councils/`.

## Use it as a library / API

```python
from quorum import Case, deliberate
v = deliberate(Case(title="Offer A vs B?", body="...", council="careers"))
print(v.decision, v.vote_tally, v.dissent, v.action_plan)
```

```bash
pip install "quorum-ai[server]" && uvicorn quorum.server:app
# POST /deliberate · GET /deliberate/stream (SSE) · GET /councils · GET /stats
```

## Guardrails (read this)

- **Illustrative guidance, not a guarantee.** Verdicts are AI-generated perspectives,
  not predictions. Visa/immigration outputs carry an extra warning and always point
  to licensed attorneys. This is not legal, immigration, or financial advice.
- **Privacy:** case/CV text is processed in memory only — never stored, never used for
  training, no telemetry. A `redact()` pass strips emails/phones/ID numbers before
  anything reaches an LLM backend.
- **Cost guard:** council size is capped by default (`QUORUM_MAX_COUNCILORS=7`) and the
  protocol is a fixed 5 phases, so a deliberation stays cheap.

## Limitations (honest ones)

- The council is only as good as its personas and its LLM; it can be confidently wrong.
- One cross-examination round by design (cost) — it's a deliberation, not a senate.
- Mock mode is canned: it demos the *protocol*, not real reasoning.

## Roadmap

Persona marketplace · multi-round debate mode · citation/source hooks per councilor ·
council-of-councils · more built-in councils (relocation, grad school, pricing).

## Contributing

PRs welcome — new councils (YAML only!) are the easiest first contribution.
Keep verdict disclaimers intact; that's non-negotiable.

## License

[AGPL-3.0](LICENSE) © 2026 Minghui Shi
