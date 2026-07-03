"""LLM backends.

Priority when auto-selecting:
1. CAMEL-AI ChatAgent (if camel-ai installed) — the agent substrate Quorum glues.
2. Anthropic API (ANTHROPIC_API_KEY) — default for polished deliberations.
3. Any OpenAI-compatible API (OPENAI_API_KEY [+ OPENAI_BASE_URL]) — incl. DeepSeek/Qwen.
4. MockBackend — deterministic, zero-key; lets anyone run the demo instantly.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Protocol


class Backend(Protocol):
    name: str

    def chat(self, system: str, user: str) -> str: ...


class AnthropicBackend:
    name = "anthropic"

    def __init__(self, model: str | None = None):
        self.model = model or os.environ.get("QUORUM_MODEL", "claude-sonnet-5")
        self.key = os.environ["ANTHROPIC_API_KEY"]

    def chat(self, system: str, user: str) -> str:
        import httpx

        r = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": 1024,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["content"][0]["text"]


class OpenAICompatBackend:
    name = "openai-compatible"

    def __init__(self, model: str | None = None):
        self.model = model or os.environ.get("QUORUM_MODEL", "gpt-4o-mini")
        self.key = os.environ["OPENAI_API_KEY"]
        self.base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

    def chat(self, system: str, user: str) -> str:
        import httpx

        r = httpx.post(
            f"{self.base}/chat/completions",
            headers={"Authorization": f"Bearer {self.key}"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


class CamelBackend:
    """Glue to CAMEL-AI (https://github.com/camel-ai/camel).

    Uses a fresh ChatAgent per call; Quorum's engine owns the conversation
    structure, CAMEL owns the agent/model plumbing.
    """

    name = "camel"

    def __init__(self, model=None):
        from camel.agents import ChatAgent  # noqa: F401

        self._ChatAgent = ChatAgent
        self._model = model  # a camel model instance or None for its default

    def chat(self, system: str, user: str) -> str:
        agent = (
            self._ChatAgent(system_message=system, model=self._model)
            if self._model is not None
            else self._ChatAgent(system_message=system)
        )
        resp = agent.step(user)
        return resp.msgs[0].content


# --- Mock -------------------------------------------------------------------

_MOCK_OPENINGS = {
    "en": [
        "From where I sit, the case is stronger than the applicant thinks — but timing is everything.",
        "I see real substance here, though one gap worries me and I'd want it closed first.",
        "The fundamentals check out; the risk is concentrated in a single dependency.",
        "My advice: commit, but stage it. The all-at-once version of this plan is fragile.",
    ],
    "zh": [
        "在我看来，这个案子比当事人自己以为的更有底气——但时机是关键。",
        "我看到了实质性的东西，不过有一个短板让我担心，我希望先补上它。",
        "基本面是成立的；风险集中在单一依赖上。",
        "我的建议：可以做，但要分阶段。一步到位的版本太脆弱。",
    ],
}

_MOCK_CHALLENGE = {
    "en": "Devil's advocate: everyone is assuming the best-case timeline. What happens if the single most likely thing goes wrong first?",
    "zh": "唱个反调：大家都在假设最顺利的时间线。如果最可能出错的那件事先发生了呢？",
}

_MOCK_REBUTTAL = {
    "en": "Fair challenge — but a staged approach absorbs exactly that failure mode, which is why I stand by my position.",
    "zh": "质疑有道理——但分阶段推进恰好能吸收这种失败模式，所以我坚持我的判断。",
}


class MockBackend:
    """Deterministic, zero-key backend so `git clone && quorum demo` always works."""

    name = "mock"

    def _pick(self, options: list[str], seed: str) -> str:
        h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
        return options[h % len(options)]

    def chat(self, system: str, user: str) -> str:
        lang = "zh" if "简体中文" in system or "简体中文" in user else "en"
        if "[BALLOT]" in user:
            h = int(hashlib.sha256((system + user).encode()).hexdigest(), 16)
            stance = ["support", "conditional", "support", "oppose"][h % 4]
            reasons = {
                "en": "Weighing upside against the identified risks, this is my honest read.",
                "zh": "权衡上行空间与已识别的风险，这是我的真实判断。",
            }
            return json.dumps(
                {"stance": stance, "confidence": round(0.55 + (h % 40) / 100, 2), "reasoning": reasons[lang]},
                ensure_ascii=False,
            )
        if "[SYNTHESIZE]" in user:
            v = {
                "en": {
                    "decision": "Proceed — in stages, with the flagged gap closed first.",
                    "summary": "The council leans support: the fundamentals hold, but the majority conditions its support on de-risking the single point of failure identified in cross-examination.",
                    "dissent": "One councilor holds that the timeline is too optimistic and would wait one cycle before committing.",
                    "action_plan": [
                        "Close the single biggest gap identified by the council within 30 days.",
                        "Split the plan into two stages with a clear go/no-go checkpoint.",
                        "Line up one credible fallback option before stage two.",
                    ],
                },
                "zh": {
                    "decision": "可以推进——分阶段进行，先补上被指出的短板。",
                    "summary": "议事会倾向支持：基本面成立，但多数意见以化解交叉质询中指出的单点风险为支持前提。",
                    "dissent": "一位议员认为时间线过于乐观，主张再观望一个周期。",
                    "action_plan": [
                        "30 天内补上议事会指出的最大短板。",
                        "把计划拆成两个阶段，设一个明确的去留决策点。",
                        "在第二阶段前准备一个可信的备选方案。",
                    ],
                },
            }
            return json.dumps(v[lang], ensure_ascii=False)
        if "[CHALLENGE]" in user:
            return _MOCK_CHALLENGE[lang]
        if "[REBUT]" in user:
            return _MOCK_REBUTTAL[lang]
        return self._pick(_MOCK_OPENINGS[lang], system + user)


def auto_backend(prefer: str | None = None) -> Backend:
    prefer = prefer or os.environ.get("QUORUM_BACKEND")
    if prefer == "mock":
        return MockBackend()
    if prefer == "anthropic" or (prefer is None and os.environ.get("ANTHROPIC_API_KEY")):
        return AnthropicBackend()
    if prefer == "openai" or (prefer is None and os.environ.get("OPENAI_API_KEY")):
        return OpenAICompatBackend()
    if prefer == "camel":
        return CamelBackend()
    if prefer is None:
        try:
            return CamelBackend()
        except Exception:
            pass
    return MockBackend()
