# Roadmap

Quorum's bet: **AI chat is a commodity; auditable decisions are infrastructure.**
The unit we're building around is the [Decision Record](docs/DECISION_RECORD.md)
— a versioned, verifiable artifact of every deliberation. Git for decisions.

## Now (v0.1)

- ✅ 5-phase anti-groupthink council protocol (independent openings → cross-exam → confidence ballots → dissent-preserving verdict)
- ✅ Decision Record v1.0: stable schema, integrity hashes, `quorum verify`
- ✅ Monte-Carlo ensembles: run N councils, measure the split instead of trusting one answer
- ✅ Councils as YAML · bilingual EN/中文 · CLI, REST/SSE, web demo · Docker one-command

## Next

- **Playground as the demo surface** — paste a decision, watch the council argue, share the record. Web-first: the audience for decision tooling lives in browsers, APIs, and docs — not app stores.
- **Records where work happens** — GitHub Action (councils review architecture decisions, record committed beside your ADRs), Slack `/quorum`, exports to Notion/Linear. Community integrations welcome — the schema is stable and documented.
- **Domain packs** — councils tuned for recurring professional decisions (hiring loops, procurement, investment memos). Always advisory, always human-ratified.
- **Record signing** — prove who emitted a record, not just that it's unaltered.
- **More built-in councils** — relocation, grad school, pricing. (YAML-only PRs are the easiest first contribution.)

## The open-core promise

The engine — protocol, schema, CLI, server — is **AGPL and stays free forever**.
If a hosted offering ever exists (managed deliberations, team archives of
records, governance tooling), it will be built *on top of* the open engine,
never carved out of it. Contributions are covered by a [CLA](CLA.md) to keep
licensing clean for everyone.

## Non-goals

- A native mobile app.
- Replacing professionals. Records document input to human decisions —
  verdicts ship with disclaimers, and visa/legal/financial topics always point
  to licensed humans.
- Consensus theater. If the council splits 3-2, you'll see the 2.
