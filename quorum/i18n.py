"""Language detection and bilingual boilerplate (EN / 简体中文)."""
from __future__ import annotations

DISCLAIMER = {
    "en": (
        "⚖️ Illustrative guidance, not a guarantee. Quorum's verdicts are "
        "AI-generated perspectives based on patterns, not predictions of real "
        "outcomes, and are not legal, immigration, or financial advice. For "
        "visa or legal decisions, consult a licensed attorney."
    ),
    "zh": (
        "⚖️ 仅供参考，不构成任何保证。Quorum 的结论是基于模式的 AI 视角，"
        "并非对真实结果的预测，也不构成法律、移民或财务建议。"
        "涉及签证或法律决定，请咨询持牌律师。"
    ),
}

VISA_EXTRA = {
    "en": "🛂 Visa-related content is informational only — real immigration decisions require a licensed immigration attorney.",
    "zh": "🛂 签证相关内容仅供参考——真实的移民决定请务必咨询持牌移民律师。",
}

UI = {
    "phase_openings": {"en": "Opening positions", "zh": "各方陈述"},
    "phase_crossexam": {"en": "Cross-examination", "zh": "交叉质询"},
    "phase_vote": {"en": "The vote", "zh": "投票"},
    "phase_verdict": {"en": "Verdict", "zh": "最终裁定"},
    "action_plan": {"en": "Action plan", "zh": "行动计划"},
    "dissent": {"en": "Dissenting view", "zh": "异议观点"},
}


def detect_language(text: str) -> str:
    """Return 'zh' if the text is predominantly CJK, else 'en'."""
    if not text:
        return "en"
    cjk = sum(1 for ch in text if "一" <= ch <= "鿿")
    return "zh" if cjk / max(len(text), 1) > 0.15 else "en"


def lang_instruction(lang: str) -> str:
    return (
        "Respond in Simplified Chinese (简体中文)."
        if lang == "zh"
        else "Respond in English."
    )
