# Pi Agent Harness — Bundle 知识包

> **类型**：bundle | **分组**：jishu/ai/ai-agent | **生成时间**：2026-09-09

---

## 概述

| 字段 | 值 |
|------|---|
| 标题 | 一起来认识一个超快的Agent：Pi |
| 作者 | 勤劳的树懒（第292篇原创） |
| 发布日期 | 2026年9月3日 |
| 博文 URL | https://mp.weixin.qq.com/s/N63QI5AUc2aIvJFcbv3BLw |
| 信源距离 | 第三方综述（非官方、非厂商自宣） |
| 状态 | stable（P0核验全通过，零勘误） |
| stale_after | 2026-12-31 |

> **说明**：本文为技术综述类博文，介绍 Pi（Agent Harness）的定位、架构、能力、设计理念及与竞品/OpenClaw 的关系，无可复现操作流程，故不设 examples/。

---

## 知识包内容

| 文档 | 类型 | F编号 | 一句话简介 |
|------|------|-------|-----------|
| [00-pi-agent-harness-overview](concepts/00-pi-agent-harness-overview.md) | 概念 | F-001~F-010 | Pi 定位与四层架构（pi-ai/pi-agent-core/pi-coding-agent/pi-tui），三种使用方式 |
| [01-pi-coding-agent-capabilities](concepts/01-pi-coding-agent-capabilities.md) | 概念 | F-011~F-015 | 默认工具集、多模型支持、Skill/Extension/Package 扩展机制、SDK 接入 |
| [02-pi-design-philosophy-and-comparisons](concepts/02-pi-design-philosophy-and-comparisons.md) | 概念 | F-016~F-033 | 为什么快（做减法）、与 Claude Code/Codex/OpenCode/LangGraph 对比、Pi 与 OpenClaw 关系演进 |

---

## 主题关联

| 关联知识包 | 关系 |
|----------|------|
| [pi-cli](../pi-cli/index.md) | pi-cli 束侧重 Pi monorepo 源码级结构（9个包），本文侧重高层定位与竞品综述；两束互补 |
| [openai-codex](../openai-codex/index.md) | Codex 为 Pi 竞品对比参考 |
| [opencode](../opencode/index.md) | OpenCode 为 Pi 竞品对比参考 |

---

## 核验摘要

- P0核验项：4项，全部通过（✅）
- 勘误项：0项
- 核心声明：stable（无 flagged 项）

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
