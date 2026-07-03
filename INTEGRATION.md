# Integrating Quorum into your app

Quorum is designed to be embedded: your app owns the users and the data, Quorum
owns the deliberation. Integration is one REST call — no shared database, no SDK
lock-in. (This is how [Summit](https://summitapp.io) uses it as its flagship AI
feature.)

## The contract

```
POST /deliberate
{
  "title":   "Should I take this offer?",
  "body":    "<the user's situation, any language>",
  "council": "careers",
  "language": "auto",              // auto | en | zh
  "context": { ... }               // host-app data, see below
}
→ 200 { decision, summary, vote_tally, dissent, action_plan, ballots, disclaimer, language }
```

For a live in-app experience, use the SSE stream instead and render events as
they arrive (`phase`, `message`, `ballot`, `verdict`):

```
GET /deliberate/stream?title=...&body=...&council=careers
```

## Injecting your data (`context`)

Anything you put in `context` is shown to every councilor as ADDITIONAL CONTEXT.
This is how a host app makes verdicts *grounded* instead of generic. Example —
a career app injecting real visa-sponsorship data:

```json
{
  "context": {
    "sponsor_data": [
      {"company": "Acme Corp",  "h1b_filings_3yr": 412, "approval_rate": 0.94, "sponsors_new_grads": true},
      {"company": "Beta Inc",   "h1b_filings_3yr": 3,   "approval_rate": 0.67, "sponsors_new_grads": false}
    ],
    "note": "Figures from public LCA disclosures; illustrative, not adjudicative."
  }
}
```

The visa-analyst councilor will reason from these numbers instead of vibes.
Keep payloads small (a few KB): every councilor reads them on every phase.

## Rules for host apps

1. **Don't strip the disclaimer.** Every verdict ships with one; surface it in
   your UI. If your users are making immigration or legal decisions, keep the
   attorney pointer visible. This is a hard requirement of the AGPL-licensed
   deployment, not a suggestion.
2. **Privacy flows through you.** Quorum stores nothing, but *you* see the case
   text. Get consent before sending user CVs, and call `quorum.privacy.redact()`
   (or replicate it) client-side if you want PII stripped before transit.
3. **Rate-limit your own endpoint.** A deliberation ≈ a dozen LLM calls. Put
   your auth in front of Quorum; don't expose `/deliberate` raw to the internet
   unless you enjoy paying for strangers' dinner-council sessions.
4. **Stay decoupled.** Pin a Quorum version, talk REST only. You should be able
   to swap in a newer Quorum by restarting a container.
