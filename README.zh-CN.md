<div align="center">

# ⚖️ Quorum

**一个 AI 议事会，公开审议你最难的决定——并展示全部过程。**

*五个立场、职责、疑虑各不相同的智能体公开辩论你的问题：
各方陈述 → 交叉质询 → 真实投票 → 保留异议的最终裁定。*

[![License: AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-blue)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Built on CAMEL-AI](https://img.shields.io/badge/built%20on-CAMEL--AI-orange)](https://github.com/camel-ai/camel)

[English](README.md) · **简体中文**

<!-- 🎬 demo.gif — 议事会现场辩论 -->

</div>

---

## 为什么是"议事会"？

问一个 AI，你得到一个自信的答案。问一个**议事会**，你得到重大决定应有的东西：
互相竞争的视角、专门攻击共识的"唱反调者"、带置信度的结构化投票，以及
**保留异议而不是把它平均掉**的最终裁定。共识不等于验证——五个智能体
瞬间达成一致是警报，不是结论。Quorum 就建立在这个理念上。

## 不是又一个"多模型合议"

"把同一个问题发给几个 AI 再汇总答案"已经有人做了。Quorum 押注的是另一件事：
**立场的多样性 > 权重的多样性。** 招聘官、用人经理和签证分析员意见相左，
不是因为他们是不同的模型，而是因为他们的*职责*让他们看到不同的风险。
Quorum 把这一点变成结构：利益相关者人设（而非模型集成）、各方独立并行陈述
（互相看不到答案，杜绝锚定）、专职唱反调者攻击一切共识、带置信度的选票、
保留异议的裁定——以及 20 行 YAML 就能定义你自己的议事会。

## 快速开始（无需任何 API Key）

```bash
git clone https://github.com/minghui31/quorum-ai && cd quorum-ai
pip install -e ".[cli]"
quorum demo            # 🍜 晚餐议事会开庭（mock 模式——即开即用，免费）
quorum demo --serious  # 🛂 职业议事会审议一个真实的职业/签证决定
```

加一个 Key 让它来真的（任选其一）：

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # 效果最好
# 或任何 OpenAI 兼容 API（OpenAI、DeepSeek、通义千问、本地 vLLM）：
export OPENAI_API_KEY=... OPENAI_BASE_URL=https://api.deepseek.com/v1 QUORUM_MODEL=deepseek-chat
quorum deliberate examples/serious_case.zh.yaml
```

**网页版**（围观辩论直播 + 下载可分享的"裁定卡"）：

```bash
cp .env.example .env   # 填一个 key，留空则用 mock 模式
docker compose up      # → http://localhost:8000
```

中文输入 → 中文审议 → 中文裁定。语言自动识别。

## 工作原理

```
     案件（任何语言——议事会用你的语言回答）
        │
  ① 案情 ──► ② 各方陈述 ──► ③ 交叉质询 ──► ④ 投票 ──► ⑤ 裁定
             独立并行，      唱反调者        JSON 选票    多数意见
             杜绝从众        攻击共识        + 置信度     + 保留异议
                                                        + 行动计划
```

智能体运行在 [CAMEL-AI](https://github.com/camel-ai/camel) 之上
（`pip install "quorum-ai[camel]"`），另有 Anthropic / OpenAI 兼容后端，
以及零 Key 的 **mock 模式**，克隆即可运行。

## 议事会就是一个 YAML 文件

内置议事会：`careers`（旗舰：招聘官🎯 / 用人经理🧑‍💼 / 签证分析员🛂 /
职业导师🌱 / 唱反调者🔥）、`dinner`（今晚吃什么）、`book_club`
（文学议事会——试试《红楼梦》结局案）。20 行 YAML 就能写一个你自己的。

## 作为库 / API 调用

```python
from quorum import Case, deliberate
v = deliberate(Case(title="接 A 还是 B？", body="...", council="careers"))
print(v.decision, v.vote_tally, v.dissent, v.action_plan)
```

## 重要声明（请务必阅读）

- **仅供参考，不构成任何保证。** 裁定是 AI 生成的视角，不是对真实结果的预测。
  签证/移民相关输出附加额外警示，并始终建议咨询持牌律师。本项目不构成法律、
  移民或财务建议。
- **隐私：** 案件/简历文本仅在内存中处理——不存储、不用于训练、无遥测。
  文本发送给任何 LLM 后端之前会先经过 `redact()` 脱敏（邮箱/电话/证件号）。
- **成本护栏：** 议事会人数默认封顶（`QUORUM_MAX_COUNCILORS=7`），流程固定
  五个阶段，一次审议花不了多少钱。

## 已知局限

- 议事会的水平取决于人设与底层模型；它可能自信地犯错。
- 出于成本考虑只有一轮交叉质询——这是审议，不是马拉松式国会辩论。
- Mock 模式是预制内容：它演示的是*协议*，不是真实推理。

## 许可证

[AGPL-3.0](LICENSE) © 2026 Minghui Shi
