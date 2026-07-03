# Quorum build log

## Day 1 — 2026-07-03
- Decisions locked: glue **CAMEL-AI** (role-play native, biggest Chinese dev community,
  OASIS lineage); name **quorum-ai** (brand "Quorum"; plain `quorum` collides with the
  ConsenSys Ethereum client); backends = Anthropic default + any OpenAI-compatible +
  zero-key mock; license **AGPL-3.0**.
- Built the full skeleton in one session:
  - `quorum/engine.py` — 5-phase council protocol (brief → independent parallel
    openings → skeptic cross-exam + rebuttals → JSON ballots w/ confidence →
    chair synthesis with dissent preserved). Anti-groupthink by construction.
  - `quorum/backends.py` — CAMEL / Anthropic / OpenAI-compat / deterministic mock.
  - 3 councils (careers ★flagship, dinner, book_club) + 5 example cases (EN + 中文,
    incl. 《红楼梦》 ending for the MiroFish-style cultural share).
  - CLI with live rendering; FastAPI server with SSE stream, /stats counter, /waitlist.
  - `web/index.html` — bilingual live demo + canvas-rendered 1200×630 verdict card (the viral unit).
  - Docker one-command start, .env.example, cost caps, PII redaction, disclaimers (EN/zh)
    stamped on every verdict, extra visa warning auto-added.
- Legal-risk items baked in from §6 of the playbook (illustrative-only labels, no CV
  storage/training, attorney pointers).

## TODO (Days 2–10, per playbook §3)
- D2: real-LLM quality pass on personas + prompts; CAMEL integration test.
- D3: Summit wiring (sponsor DB into `case.context`) — keep decoupled via REST.
- D4: hosted deploy (Netlify/Fly) + waitlist live.
- D5: record demo GIF (fun) + 60s video (serious, bilingual subtitles).
- D6: README polish w/ real GIF + badges; CONTRIBUTING.
- D7–9: seed 50–100 stars, pre-write Show HN / Reddit / 掘金 / 小红书 posts.
- D10: coordinated launch (Tue–Thu, US Pacific morning).
