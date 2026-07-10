# The Decision Record — spec v1.0

> ChatGPT is for chat. Quorum is for decisions — and a decision is only worth
> what you can audit later.

Every Quorum deliberation emits a **decision record**: a versioned, structured
JSON artifact of the full deliberation. Think **git for decisions** — the
record is the commit; the dissent is the diff that didn't win.

This document is the stability contract for anyone building on the format.

## Getting a record

| Surface | How |
|---|---|
| CLI | `quorum deliberate case.yaml --record decision.json` |
| Python | `v = deliberate(case); v.record` |
| REST | `POST /deliberate` → `verdict.record` (additive field) |
| SSE | final stream event: `event: record` |
| Web demo | ⬇️ Decision record (JSON) button under the verdict |

## Shape (informative)

```jsonc
{
  "record_version": "1.0",          // stability contract — see Versioning
  "id": "qr_285de7c4ad3eb773",      // content-derived, stable, verifiable
  "created_at": "2026-07-06T09:00:00+00:00",
  "engine":  { "name": "quorum-council", "version": "0.1.0", "backend": "anthropic",
               "protocol": "brief/openings/cross-exam/vote/verdict v1" },
  "case":    { "title": "...", "body": "...(post-redaction)...",
               "council": "careers", "language": "en", "context": {} },
  "council": { "name": "careers", "description": "...",
               "councilors": [{ "id": "recruiter", "role": "Tech Recruiter",
                                "emoji": "🎯", "is_skeptic": false }, ...] },
  "deliberation": {
    "openings": [{ "councilor_id": "recruiter", "text": "..." }, ...],   // independent, parallel
    "cross_examination": { "challenger_id": "skeptic", "challenge": "...",
                           "rebuttals": [{ "councilor_id": "...", "text": "..." }, ...] },
    "ballots": [{ "councilor_id": "recruiter", "stance": "conditional",
                  "confidence": 0.72, "reasoning": "..." }, ...]
  },
  "verdict": { "decision": "...", "summary": "...",
               "vote_tally": { "conditional": 5 },
               "dissent": "...(the strongest minority view, preserved)...",
               "action_plan": ["...", "..."] },
  "disclaimer": "...",              // always present; travels with the record
  "integrity": { "algorithm": "sha256", "content_hash": "..." }
}
```

The normative schema is [`schemas/decision-record-1.0.schema.json`](../schemas/decision-record-1.0.schema.json)
(JSON Schema 2020-12). A committed example lives at
[`examples/decision_record.example.json`](../examples/decision_record.example.json).

## Versioning contract

- `record_version` follows `MAJOR.MINOR`.
- **Additive** changes (new optional fields) bump MINOR only. Consumers MUST
  ignore fields they don't recognize.
- **Breaking** changes (removing/renaming/retyping a field) bump MAJOR and a
  new schema file is published alongside the old one. `1.x` records will
  remain parseable by their published schema forever.

## Integrity

`integrity.content_hash` = SHA-256 of the canonical JSON (UTF-8, sorted keys,
compact separators) of the record **minus** `id` and `integrity`. `id` is
`"qr_" + content_hash[:16]`.

Verify a record:

```bash
quorum verify decision.json
```

```python
from quorum.record import verify_record
verify_record(record)   # → bool
```

Note: the hash proves the record wasn't altered after emission. It does not
prove *who* emitted it — signing is a candidate `1.x` addition.

## Privacy

`case.body` is stored **after** Quorum's PII redaction pass (emails, phone
numbers, ID-like strings). Records are emitted to the caller only; the engine
persists nothing.

## What records are for

Records are designed to accumulate: commit them next to ADRs, attach them to
tickets, archive them for governance. A deliberation you can re-read, verify,
and diff is the difference between "the AI said so" and a decision process you
can defend — to your team, your board, or your auditor. Always human-ratified:
records document input to a human decision, they are not the decision itself.
