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

## Day 3-4 CLOSED — 2026-07-04 evening
- L&E Clinic intake submitted (free startup legal; screening interview ~1-2 wks).
- LICENSE fixed on GitHub via browser: now true AGPL-3.0 (commit 6390deb).
- HOSTED DEMO LIVE: https://quorum-brkj.onrender.com (Render Blueprint from
  render.yaml, free tier, mock mode until ANTHROPIC_API_KEY set in dashboard).
- Live E2E verified in production: 红楼梦 case, zh auto-detect, SSE stream, all
  5 phases, split vote 3-1-1 w/ dissent, disclaimers, card buttons, waitlist+consent.
- Remaining to make hosted demo REAL: user pastes ANTHROPIC_API_KEY in Render
  Environment + sets Anthropic console spend cap. Auto-deploy: connect GitHub
  in Render later (currently public-repo mode = manual sync).

## Day 5 — asset production
- 60s launch video v1 (EN) PRODUCED via Higgsfield explainer pipeline:
  6 isometric-flat-vector scenes (gemini_omni) + Sterling narration (seed_audio)
  + subtitles, assembled server-side. 2 failed blocks re-rendered successfully.
- Platform promo cards built (assets/promo_cards.html): YouTube 1280x720,
  小红书 1080x1440, X 1200x675 — per image-CTR research.
- Launch kit v2: master posting schedule (8:30am CDT = HN window + 小红书 golden
  hour simultaneously), X link-in-reply rule, Show HN survival tactics.
- Anthropic credits: $19.93 prepaid, auto-reload OFF (= hard spend cap ✅).
- BLOCKED on user: git push (4 commits), ANTHROPIC_API_KEY into Render env
  (→ real-inference GIF + promo screenshots + live ballot verification).
- TODO: 中文 video version; GIF; social-preview upload; README GIF embed (D6).

## Day 5 close-out — live verification round
- 中文 60s video produced (same scenes, Hana narration, zh subtitles).
- Live real-Claude runs verified: personas exceptional (Nutritionist caught a
  counting detail; 红楼梦 council cites 脂批/判词/清代出版环境 — 小红书 gold).
- Bug #1 fixed: thinking blocks crashed verdict synthesis (robust text-block extraction).
- Bug #2 fixed: unescaped inner quotes in zh JSON broke ballot/verdict parsing →
  field-level regex fallbacks + prompt rule (use 「」 inside strings) + test.
- Both bugs caught BEFORE launch by production verification. Worth everything.

## Day 5 CLOSED / Day 6 started — 2026-07-05 early
- Demo GIF recorded against LIVE real-Claude deliberation (careers council,
  startup-vs-safe-job case): 17 frames, openings → cross-exam → vote → verdict.
  Bonus: the run itself verified the parser fix in production (verdict card
  rendered perfectly, conditional×5, dissent + 5-step plan intact).
- The recorded deliberation was launch-gold: council unanimously converged,
  then the Skeptic surfaced the blind spot (IP/moonlighting clauses in the
  sponsored offer) — exactly the anti-groupthink pitch, on camera.
- Promo cards exported pixel-exact via in-page html2canvas: YouTube 1280×720,
  小红书 1080×1440, X 1200×675, GitHub social preview 1280×640.
  (First social-preview capture came out 857px/broken — viewport clipping;
  fixed with windowWidth + block layout, all re-verified visually.)
- README (EN+zh): GIF embedded + "Try it live" link.
- User TODO: move quorum-demo.gif + 4 PNGs from Downloads → quorum/assets/,
  upload social preview PNG in GitHub Settings, then commit+push. ✅ all done same night.

## Virality detail pass — 2026-07-04 late (deployed live, commit bd4aa9d)
- Web demo had ZERO og/twitter meta → added full set (og:image = social preview
  PNG, verified 200 image/png live). Links now unfurl as cards on X/Discord/WeChat.
- Demo→star loop was broken (no repo link in UI) → ★ GitHub header button +
  post-verdict ⭐ star CTA (EN/zh) at the moment of peak delight.
- Favicon (⚖️ svg data-URI). pyproject: [project.urls], 12 keywords, classifiers.
- GitHub repo: website field + 12 topics were EMPTY → filled via extension.
- Social preview uploaded to GitHub Settings via extension (file_upload).
- Push hiccup: 8.25MiB pack hit http.postBuffer default → fixed w/ 157286400.
- Account plan: user creating HN/Reddit/X/小红书/掘金/PyPI accounts now (aging
  matters most for Reddit karma filters; HN + 小红书 nearly age-blind).

## Ensemble mode SHIPPED to web demo — 2026-07-06 late night
- /simulate/stream (SSE): live distribution bars fill as councils vote;
  majority verdict shown above bars; flip rate + avg confidence + recurring
  dissent + share text (EN/zh). Panel header shows council count.
- Cost engineering (all measured, not guessed): user's 5-council Sonnet run
  = $0.38 → ensembles now run on Haiku (QUORUM_ENSEMBLE_MODEL) ≈ $0.07/click;
  default selector ×3; server cap QUORUM_WEB_MAX_RUNS=5; single-council
  flagship stays premium. $38 budget ≈ 400-900 ensemble clicks.
- Counter hardened: persisted to disk + QUORUM_COUNT_FLOOR env (set to 15 via
  dashboard; deploys had been resetting social proof to 0).
- zh auto-detect (navigator.language) → Chinese browsers land on 中文 UI.
- Waitlist copy now teases "100-council deep reports on hosted version"
  (demand capture; NO pricing shown — monetization is post-OPT only, §10 of
  launch kit has the full ladder: $4.99/20, $19.99/100-report, margin-first).
- no-cache header on index (stale-page bug during rapid deploys).

## Day 3 check-in — 2026-07-05 (calendar Day 3; progress ≈ playbook Day 6)
- Since last check-in: demo GIF (live real-Claude run) in README, promo cards ×4
  exported, virality pass (og/twitter tags, star CTAs, favicon, topics, social
  preview) — all pushed; GitHub verified current at bd4aa9d (README GIF + Try-it-live
  + custom og:image all live; earlier "5 commits" page was CDN cache).
- Closed: AGPL LICENSE ✅ (Affero text verified), git push ✅, Render real-key runs ✅
  (ballot/verdict parse verified in prod — the owed --serious verification is
  effectively done via live runs + parser tests).
- ⚠️ Stars: 0 (0 forks/watchers). Seeding window (D7–9) can start EARLY since build
  is ahead: genuine outreach only (personal network, CAMEL community, "Built with"
  PR). Never purchased/fake stars.
- 🎯 Today: (1) start organic star/outreach runway + CAMEL "Built with" PR;
  (2) PyPI release per RELEASING.md so `pip install quorum-ai` works before launch;
  (3) finalize launch posts from kit v2 + pick launch day (Tue Jul 7–Thu Jul 9
  window is now feasible ahead of the Jul 13 deadline — decide).
- Legal: disclaimers + attorney pointers intact (i18n.py, careers.yaml), redact()
  wired pre-LLM, no case/CV persistence. ✅ CLA still needs counsel review pre-1.0.

## Day 4 check-in — 2026-07-06 (calendar Day 4; progress ≈ playbook D7)
- Since last check-in: ENSEMBLE MODE shipped to web demo (7 commits, pushed):
  /simulate/stream SSE + live distribution bars, flip rate, recurring dissent,
  majority verdict, share text (EN/zh); Haiku ensembles ≈ $0.07/click (measured),
  QUORUM_WEB_MAX_RUNS=5 server cap; counter persisted + QUORUM_COUNT_FLOOR;
  zh browser auto-detect; waitlist teases 100-council deep reports (no pricing).
- ⚠️ 1 commit unpushed (d727652 buildlog) — push with today's work.
- ⚠️ Not started: PyPI publish + v0.1.0 tag; CAMEL "Built with" PR; founder
  cheat sheet + hostile-commenter drill; platform bios / Reddit karma warm-up.
- 🎯 Today: (1) PyPI release + v0.1.0 tag per RELEASING.md (`pip install
  quorum-ai` must work before any outreach); (2) founder cheat sheet EN+zh +
  drill ×1 (biggest launch risk is the human, not the repo); (3) start organic
  runway: CAMEL "Built with" PR + Discord showcase + daily Reddit warm-up.
- GitHub: 0 stars / 0 forks / 0 watchers. Launch Tue Jul 14 8:30am CDT locked.
- Legal: disclaimers + attorney pointers intact (i18n.py ×4, web UI), redact()
  wired pre-LLM (engine.py:123), no case/CV persistence (server docstring
  confirms in-memory only). ✅ CLA counsel review still owed pre-1.0.

## Day 5 check-in — 2026-07-07 (calendar Day 5; progress ≈ playbook D8)
- Since last check-in: DECISION RECORD v1.0 shipped (76a3fee) — versioned auditable
  JSON of every deliberation w/ sha256 integrity, emitted by engine/CLI(--record)/
  API/SSE/web download, tests + README EN/zh; format layer (f12ee75) — JSON Schema,
  spec doc, committed example, `quorum verify` command, public ROADMAP (open-core).
  All pushed; origin current at f12ee75. "ChatGPT is for chat, Quorum is for
  decisions" positioning now has its artifact.
- ⚠️ Slipped (2nd day): PyPI publish + v0.1.0 tag; founder cheat sheet + hostile-
  commenter drill; CAMEL "Built with" PR / Discord showcase; Reddit karma warm-up.
  Build is ahead — the human-and-distribution track is now the critical path.
- 🎯 Today (launch T-7): (1) PyPI release + v0.1.0 tag per RELEASING.md — blocks
  all outreach copy (`pip install quorum-ai` must work); (2) founder cheat sheet
  EN+zh + drill ×1 — biggest launch risk is the human, not the repo; (3) CAMEL
  "Built with" PR + Discord showcase + first Reddit warm-up posts (organic only).
- GitHub: 0 stars / 0 forks / 0 watchers. Launch Tue Jul 14 8:30am CDT (T-7).
- Legal: disclaimers + attorney pointers intact (i18n.py, README Guardrails verified
  live on GitHub), redact() wired pre-LLM (engine.py:123), in-memory only, no CV
  storage/training. ✅ CLA counsel review still owed pre-1.0 — L&E Clinic screening
  pending (~1-2 wks from Jul 4; may land near launch, chase if silent by Jul 10).
