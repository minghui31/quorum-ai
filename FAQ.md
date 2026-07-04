# FAQ

**Is this just [Perplexity Model Council / multi-LLM voting]?**
No — those diversify *models* (same question to GPT+Claude+Gemini, merge
answers). Quorum diversifies *incentives*: one model, five stakeholder personas
whose jobs make them see different risks, forced through an adversarial
protocol (independent openings → designated-skeptic cross-examination →
confidence ballots → dissent-preserving verdict). See "Not another multi-model
council" in the README.

**Do I need an API key?**
No — `quorum demo` runs in deterministic mock mode instantly. Real deliberation
needs any one key: Anthropic (best), or any OpenAI-compatible endpoint
(OpenAI, DeepSeek, Qwen, local vLLM/ollama).

**How much does a real deliberation cost?**
One council ≈ a dozen LLM calls with short prompts — typically a few cents on a
mid-tier model. Ensembles multiply that by `--runs` (capped by
`QUORUM_MAX_RUNS`, default 50).

**Why did all five councilors agree?**
Sometimes the case is genuinely one-sided — but check the Skeptic's ballot
confidence. If consensus bothers you, run `quorum simulate` and look at the
flip rate: a 0% flip rate across 20 councils is signal, not groupthink.

**Can I trust the verdict for a real visa/legal/financial decision?**
No. Every verdict says so. Quorum is structured perspective-taking —
illustrative guidance that helps you *think*, not a prediction or professional
advice. Visa outputs always point to licensed immigration attorneys, by design.

**Why AGPL?**
So the engine stays open: anyone serving Quorum (or a modified version) over a
network must publish their source. Commercial licenses for companies that
can't do AGPL: open an issue.

**Can it speak my language?**
It answers in the language of your case. EN and 简体中文 are first-class
(disclaimers, UI, verdicts); other languages generally work via the underlying
model but aren't officially wired yet — PRs welcome (`quorum/i18n.py`).

**What's my CV/case data used for?**
Nothing. Processed in memory, never stored, never trained on, no telemetry.
PII (emails/phones/IDs) is regex-redacted before any LLM call (`quorum/privacy.py`).

**Does it work with CAMEL-AI?**
Yes — `pip install "quorum-ai[camel]"` runs councilors on CAMEL ChatAgents;
Quorum's engine owns the protocol, CAMEL owns the agent plumbing.
