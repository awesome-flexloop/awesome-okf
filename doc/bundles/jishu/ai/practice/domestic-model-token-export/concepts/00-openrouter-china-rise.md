---
okf_version: "0.2"
type: concept
title: OpenRouter 中国模型崛起时间线（2025-2026）
description: OpenRouter 平台中国模型 Token 份额从 <2% 升至 >60% 的事件时间线、排行榜数据、核心数字与中美流量逆转事实。
tags: [openrouter, china-ai, token-market-share, deepseek, minimax, qwen]
---

# OpenRouter 中国模型崛起时间线（2025-2026）

> 截至 2026年6月数据 | 约 1800 字

OpenRouter 是全球最大的 AI 模型路由平台，服务于约 800 万开发者，聚合 400+ 模型，以统一 API 接口提供模型调用。**其流量数据被视为"用钱包投票"的真实市场信号**，而非厂商自宣或基准测试排名。

2025年至2026年，OpenRouter 平台上发生了一场史无前例的份额逆转：美国模型（Google + OpenAI + Anthropic）的 Token 份额从约 **70% 暴跌至约 30%**，而中国模型从不足 **2%** 跃升至超过 **60%**。这不是中国开发者支持国产的结果——OpenRouter 用户主体是全球开发者，大量来自美国、欧洲、印度。

---

## 关键时间节点

| 时间 | 事件 | 来源 |
|------|------|------|
| 2025年6月 | 美国模型占 OpenRouter Token 份额约 **70%** | Bloomberg 引用 OpenRouter + Exponential View 数据 |
| 2025年底 | DeepSeek V3 发布，引发全球开源模型热潮 | DeepSeek 官方博客 |
| 2026年2月初 | 中国模型首次在 OpenRouter 日 Token 量上超越美国模型（仅单日） | OpenRouter 内部数据 |
| 2026年2-3月 | 中国模型持续领先，SEC 介入 DeepSeek 调查 | [Reuters 2026-03-07](https://www.reuters.com/technology/) |
| 2026年3月前两周 | 中国模型在周 Token 量上首次超越美国模型 | CEIBS 分析 |
| 2026年4月24日 | DeepSeek V4 系列发布（V4 Flash / V4 Pro） | DeepSeek 官方博客 |
| 2026年6月 | 中国模型周 Token 约 **18万亿**，美国模型约 **5.5万亿** | OpenRouter 官方 + macgpu.com |
| 2026年7月 | 中国模型占据 OpenRouter Top 5 全部席位，由小米 MiMo-V2.5 领衔 | macgpu.com |
| 2026年8月16日 | Stripe 宣布收购 OpenRouter，>70亿美元 | Bloomberg |

---

## 2026年6月公司层排行榜（周 Token 量）

| 排名 | 公司 | 来源地 | 周 Token 量 | 市占率 |
|------|------|--------|------------|--------|
| 1 | DeepSeek | 🇨🇳 中国 | 5.13T | 17.6% |
| 2 | Anthropic | 🇺🇸 美国 | 4.34T | 14.8% |
| 3 | Google | 🇺🇸 美国 | 3.66T | 12.5% |
| 4 | OpenAI | 🇺🇸 美国 | 2.46T | 8.4% |
| 5 | 小米 (Xiaomi) | 🇨🇳 中国 | 2.42T | 8.3% |
| 6 | MiniMax | 🇨🇳 中国 | 2.37T | 8.1% |
| 7 | 腾讯 (Tencent) | 🇨🇳 中国 | 2.36T | 8.1% |
| 8 | 阿里 Qwen | 🇨🇳 中国 | 1.26T | 4.3% |

**中国厂商（前10名内）合计：约 46%**；含 Moonshot(Kimi) 等全量中国模型：约 **60-63%**。

> **洞察一：这不是爱国消费，是经济学。** 美国、欧洲、印度开发者选择中国模型的原因很直接——价格便宜、性能够用。一位圣地亚哥开发者说："用 Claude 写代码每小时约 10 美元，用 DeepSeek 不到 50 美分。"一位达拉斯开发者分层栈："$500/月 Claude + ChatGPT 处理复杂任务，$200/月 MiniMax + Kimi + MiMo 处理 90% 日常编码。"

---

## 2026年6月模型层排行榜（日均 Token）

| 排名 | 模型 | 厂商 | 日均 Token |
|------|------|------|-----------|
| 1 | DeepSeek V4 Flash | DeepSeek | 619B |
| 2 | Hy3 Preview | 腾讯 | 451B |
| 3 | MiniMax M3 | MiniMax | 447B |
| 4 | MiMo-V2.5 | 小米 | 327B |
| 5 | DeepSeek V4 Pro | DeepSeek | 300B |
| 6 | Claude Opus 4.7 | Anthropic | 263B |
| 7 | Claude Opus 4.8 | Anthropic | ~200B |
| 8 | Claude Sonnet 4.6 | Anthropic | 178B |
| 9 | Gemini 3 Flash Preview | Google | 156B |
| 10 | Kimi K2.6 | Moonshot AI | ~150B |

---

## 用量第一 ≠ 质量第一

| 模型 | Intelligence Index | SWE-bench Pro | 日均 Token |
|------|-------------------|---------------|-----------|
| **Claude Opus 4.8** | **61.4（#1）** | 69.2% | ~200B |
| DeepSeek V4 Flash | — | — | 619B |

- **Claude Opus 4.8**：综合质量指数 61.4，稳居 #1，长上下文和 Agent 任务优势明显。一位工程师 20 个相同任务测试：Opus 4.8 赢了 16 次，GPT-5.5 赢 5 次，Gemini 3.1 Pro 赢 4 次。
- **Claude Fable 5** 曾以 100/100 满分质量得分领跑，但因出口管制于2026年6月中旬全球下架，证明美国质量天花板仍高。

> **结论**：中国模型在"够用且便宜"的区间建立了护城河，但尖端推理能力仍由 Claude 系列领先。两者不是替代关系，而是分层协作——日常任务用中国模型，关键决策用 Claude。

---

## 数据来源

| 数据类型 | 来源 | 可信度 |
|---------|------|--------|
| OpenRouter 流量数据（2026年6月） | macgpu.com（2026-07-01）、officechai.com（2026-06-17）、Superpower Daily（2026-08-27） | 高 |
| 中美份额逆转（70%→30%） | Bloomberg 引用 OpenRouter + Exponential View 数据 | 高 |
| Stripe 收购 OpenRouter | Bloomberg（2026-08-16）、Axios（2026-08-19） | 高 |
| DeepSeek V4 Flash 日均 619B | officechai.com（2026-06-17） | 高 |
| 开发者原话引用 | 博主转述第三方开发者 | 中（无法独立核验） |
