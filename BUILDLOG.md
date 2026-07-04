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

## Day 2 (early) — 2026-07-04, overnight block
- README repositioned (EN+zh): new "Not another multi-model council" section —
  incentives > weights, vs Perplexity Model Council / council-app crowd.
- CamelBackend hardened against current camel-ai API (ChatAgent/.step verified
  from upstream README); ModelFactory usage documented.
- Day-3 prep: INTEGRATION.md (REST contract, sponsor-data context example,
  host-app rules: keep disclaimers, consent, rate-limit, stay decoupled).
- Day-4 prep: render.yaml + fly.toml + DEPLOY.md incl. launch-day traffic notes.
- Launch kit v1 drafted (private, o1/38_Quorum_Launch_Kit.md): Show HN title+maker
  comment, X thread, Reddit angles, 小红书/掘金/知乎, CAMEL "Built with" PR plan,
  investor DM template, star/upvote ethics rules, asset checklist.
- First real-API run done (Jul 3 night): personas distinct, skeptic sharp; tuned
  (no markdown, hard word cap, anti-pile-on instruction).
- Monte-Carlo deliberation shipped: quorum/montecarlo.py (ensemble of N
  independent councils → outcome distribution, flip rate, recurring dissent),
  CLI `quorum simulate --runs N` with distribution bars, POST /simulate,
  salted-backend decorrelation, QUORUM_MAX_RUNS cost cap, test added.
  README (EN+zh): "Convene one council — or fifty" section.

## Day 2 check-in — 2026-07-04
- Done since Day 1: README repositioning (incentives > ensembles), CAMEL glue hardened,
  persona tuning from first real run, Monte-Carlo deliberation (`quorum simulate`),
  verdict card v2 (share loop), INTEGRATION.md + deploy configs (D3/D4 prep pulled forward).
- ⚠️ LICENSE still plain GPL-3.0 — the GitHub "Update LICENSE" edit did NOT insert
  Affero text ("GNU GENERAL PUBLIC LICENSE", not "GNU AFFERO..."). README claims AGPL;
  mismatch is a credibility bug. Fix + push.
- ⚠️ 2 commits unpushed (Monte-Carlo, verdict card v2) — origin is stale.
- ⚠️ Still owed: vote+verdict paste from a real `quorum demo --serious` (ballot-parse check).
- Legal check: disclaimers/attorney pointers intact (i18n.py, careers.yaml), redact()
  wired into engine, no case/CV persistence found. ✅
- GitHub: 0 stars (seeding is D7–9; organic only).

## Day 3 block — resumed after rest day
- Release hygiene shipped: CONTRIBUTING.md (councils-as-YAML contribution funnel),
  CLA.md (draft, counsel review pre-1.0), FAQ.md (incl. the Model Council
  differentiation answer), RELEASING.md (PyPI steps + pre-launch checklist +
  good-first-issues list).
- Summit integration: examples/summit_client.example.jsx — React hook + panel
  (SSE live view, verdict render w/ mandatory disclaimer) + backend proxy sketch
  (auth, rate-limit, server-side sponsor-data injection).
- 小红书 launch essay drafted (private, o1/41) — story-first per research.
