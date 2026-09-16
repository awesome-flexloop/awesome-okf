---
okf_version: "0.2"
type: bundle
title: "免费大模型接入实战（2026-09）：Agnes·dots3·AMD 三平台零成本接入手册"
description: "微信博文经 OKF v0.2 七阶段工作流转化：Agnes AI、小红书 dots3-note-prev、AMD Radeon Cloud Token Factory 的注册拿 Key、OpenAI 兼容接入 WorkBuddy/Trae、图像/视频 API 实操，含 31 项声明官方核验与勘误"
tags: [免费大模型, Agnes-AI, dots3, AMD-Radeon, OpenAI兼容, WorkBuddy, Trae, 文生视频, 模型选型, 博文转化]
generated: { by: "process:blog-article-to-okf-wiki:R/I/E/V", at: "2026-09-16T22:05:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-16T22:05:00+08:00" }
status: flagged
stale_after: 2026-11-30
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/qnQqCivPiuRfJIVMM-zTNQ
    title: "《我用3个免费模型，把WorkBuddy的成本砍到了零》（技术宅SuperLaos/老商，2026-09-10）"
  - id: agnes-wiki
    resource: https://wiki.agnes-ai.cn/zh-Hans/docs/overview
    title: Agnes AI 官方文档中心（国内站）
  - id: dots-docs
    resource: https://dots.ai/platform/docs
    title: dots3-note Preview 官方 API 文档
  - id: amd-panel
    resource: https://developer.amd.com.cn/radeon/modelapis
    title: AMD Radeon Cloud Public Free Model APIs
  - id: openrouter-dots
    resource: https://www.openrouter.ai/dots-studio/dots-3-note-preview:free
    title: dots-3-note-preview OpenRouter 模型页（2026-09-30 下线）
---

# 免费大模型接入实战（2026-09）

> **⚠️ 状态：`flagged`（2026-09-16 核验）**
>
> 三平台"当前仍可免费接入"的总论成立，但博文（2026-09-10）三处主推内容已变化，阅读与实操前必读：
>
> 1. **AMD 免费名单发布后第 6 天即变更**：DeepSeek-V4-Flash-Vision-Exp 已下架、MiniCPM5-1B 被 9 月 7 日开源的 MiniCPM5-2B 取代，另新增 Qwen3.8-27B、MinerU2.5-Pro——演练以 [09-16 在册 5 款](examples/02-amd-walkthrough.md) 为准。
> 2. **dots3 的 OpenRouter/AtlasCloud 免费通道 2026-09-30 关闭**；Trae 直连 dots.ai 有认证头障碍（401），绕行通道有时效。
> 3. **博文 §6 全局价格表 13 行中 6 行有硬错**（DeepSeek 上下文、豆包三项、Kimi 价格、ERNIE 型号、GLM 价格边界、Trae 内置名单），[概念 02](concepts/02-selection-matrix.md) 已给勘误版。
>
> 完整核验过程见 [P0 权威核验报告](references/verification.md)。本束在 `stale_after`（2026-11-30）前安排复核。

## 这束知识包解决什么问题

想零成本把大模型接进 WorkBuddy、Trae Work 等 OpenAI 兼容客户端（开发者/运营/数据分析师向）。博文《免费大模型接入全攻略（2026-09 实战版）》给出 Agnes AI、小红书 dots3、AMD Radeon Cloud 三个平台的完整接入路径；本知识包在其基础上完成**官方源核验与勘误**，所有域名、模型名、参数、价格均可溯源至 F-001 ~ F-089 编号事实。

## 内容导航

| 层 | 文档 | 内容 |
|---|---|---|
| 概念 | [00 免费模型平台全景](concepts/00-free-model-landscape.md) | 三平台是谁、免费什么、注册门槛、关键时点时间线（What/When/Who） |
| 概念 | [01 平台机制深潜](concepts/01-platform-deep-dive.md) | 认证头矩阵、多协议网关、Thinking 开关、图像档位/异步视频两步、积分制、限流与安全 |
| 概念 | [02 选型矩阵与免费档全景](concepts/02-selection-matrix.md) | 三平台横评、§6 价格表勘误版、场景决策树、组合策略 |
| 演练 | [00 Agnes AI 全流程](examples/00-agnes-walkthrough.md) | 注册拿 Key → WorkBuddy 配置 → 对话/生图/生视频 curl → Agnes Code 边界 |
| 演练 | [01 dots3 接入](examples/01-dots3-walkthrough.md) | `api-key` 头特例、WorkBuddy 直连、Trae 401 障碍与 Bearer 绕行 |
| 演练 | [02 AMD Radeon Cloud](examples/02-amd-walkthrough.md) | 领 Key、核验日 5 款模型、VLM 喂图、积分解读与稳定性设置 |
| 信源 | [博文事实清单](references/article-source.md) | F-001~F-089 双份事实登记（博文 61 条 + 核验 28 条） |
| 信源 | [P0 核验报告](references/verification.md) | 31 项关键声明、勘误四张清单、时效失效记录、flagged 裁决 |
| 日志 | [变更日志](log.md) | 生成过程、并行会话合并记录、质量门 |

## 已知边界（读者使用前提）

1. **时效**：免费额度、限流、截止日按周变动；本束现行状态截至 2026-09-16，接入前以各平台控制台当日显示为准（F-004）。
2. **单源项**：Agnes Code 的"Linux 桌面版不与 CLI 混用"、精确系统版本号、8 个内置技能 slug 仅博文单源，官方未文档化（F-068）；AMD"$1/天额度缩水"判为传言（F-077）；"200 万 token 耗 5%"为作者个人实测、不可复算（F-077）。
3. **观点分层**：选型口诀与组合策略为博文作者观点（F-046/F-060），经核验修正后保留；事实与观点在正文中分别标注。
4. **数据红线**：医药、患者、未公开经营数据不传第三方云模型，改走本地（Ollama / MiniCPM5）（F-004/F-032）。
5. **非生产承诺**：dots3 为预览版、AMD 全站 BETA/experimental，二者官方定位均为开发测试（F-038/F-077）。

## 主题关联

- [free-llm-api-roundup](../free-llm-api-roundup/index.md)：40 家免费 API 平台**广度目录**（2026-06 时点，亦为 flagged）——先查它发现平台，再用本束完成深度接入。
- [agnes-ai/agnes-ai-models](../agnes-ai/agnes-ai-models/index.md)：Agnes 2.5/2.1 代际系统教程——本束补充 3.0-flash 与 image/video-2.5-flash 新代际、9 月网关现状。

```{toctree}
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
