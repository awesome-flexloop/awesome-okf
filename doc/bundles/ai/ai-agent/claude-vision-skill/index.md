---
okf_version: "0.2"
type: bundle
title: "claude-vision-skill——给纯文本模型装上眼睛的 Claude Code Skill"
description: "开源工具教程：claude-vision-skill 通过视觉模型中转转录，让 DeepSeek V4 Pro 等纯文本模型在 Claude Code 中获得识图能力。含安装配置、三场景实战、架构原理、Skill自动触发机制。35条事实，6项P0核验全部✅，含3项时效性补充（DeepSeek官方视觉模型已上线）。"
author: OKF Wiki Bot
date: 2026-08-29
source: "https://mp.weixin.qq.com/s/3AZbLPVwg45PrQSuvcJDHQ"
article_author: "macrozheng"
article_date: "2026-08-21"
repo: "https://github.com/asuojun/claude-vision-skill"
status: verified
stale_after: "2026-11-29"
tags: ["Claude Code", "Agent Skill", "视觉模型", "DeepSeek", "qwen-vl-max", "阿里云百炼", "MCP替代方案", "开源工具"]
---

# claude-vision-skill

> **来源**：微信公众号"macrozheng"（mall/mall-swarm 作者），2026-08-21 发布
> **原文**：[《DeepSeek V4 Pro 也能看图了！》](https://mp.weixin.qq.com/s/3AZbLPVwg45PrQSuvcJDHQ)
> **开源仓库**：https://github.com/asuojun/claude-vision-skill
> **P0核验**：6项声明全部 ✅ 通过（详见 [verification.md](references/verification.md)）

> **⏰ 时效性提示**：博文发布当天（2026-08-21），DeepSeek 官方上线了首个多模态模型 `deepseek-v4-flash-vision-exp`（基于 V4-Flash，实验性）。用户现在多了"直连 DeepSeek 视觉模型"的选项；但 V4 Pro 截至 2026-08-29 仍无视觉 API，本 Skill 的中转方案对 V4 Pro 依然有效。

## 项目一句话

给 Claude Code 接入的**纯文本模型**（如 DeepSeek V4 Pro）借一双眼睛：图片先发给视觉模型（如阿里云百炼 qwen-vl-max）转录成文字描述，再交回文本模型推理——配置一次，全局可用。

## 核心机制

```mermaid
graph LR
    U[用户发图片] --> S[claude-vision-skill<br/>SKILL.md自动触发]
    S --> V[vision.js]
    V --> B[图片→base64]
    B --> Q[视觉模型API<br/>qwen-vl-max]
    Q -->|文字描述| D[DeepSeek V4 Pro<br/>继续推理]
```

## 知识结构

```
claude-vision-skill/
├── index.md
├── concepts/
│   ├── index.md
│   ├── 00-problem-vision-gap.md       ← 问题：纯文本模型的视觉鸿沟
│   ├── 01-transcription-architecture.md ← 方案：视觉转录架构
│   └── 02-skill-mechanism.md          ← Claude Code Skill 自动触发机制
├── examples/
│   ├── index.md
│   ├── 00-install-and-config.md       ← 安装配置完整步骤（含避坑）
│   └── 01-usage-scenarios.md          ← 三场景实战+回退逻辑
├── references/
│   ├── index.md
│   ├── article-source.md              ← F-001~F-035 事实登记
│   └── verification.md                ← P0核验报告
└── log.md
```

## 分层导航

### 概念层（3篇）

1. [纯文本模型的视觉鸿沟](concepts/00-problem-vision-gap.md) — [Unsupported Image] 现象、DeepSeek模型视觉支持现状
2. [视觉转录架构](concepts/01-transcription-architecture.md) — 中转原理、链路、成本与模型选型
3. [Skill 自动触发机制](concepts/02-skill-mechanism.md) — SKILL.md frontmatter、model-invoked 机制

### 实战层（2篇）

1. [安装配置完整步骤](examples/00-install-and-config.md) — clone、路径替换、.env、dotenv避坑
2. [三场景实战](examples/01-usage-scenarios.md) — 本地/URL/剪贴板、自动触发、回退逻辑

### 信源层（2篇）

- [事实登记](references/article-source.md) — F-001~F-035
- [核验报告](references/verification.md) — 6项P0全✅ + 3项时效性补充

## 信任与生命周期

- **事实基数**：35条（F-001~F-035）
- **P0核验**：6✅ 0⚠️ 0❌
- **时效性补充**：3项（DeepSeek官方视觉模型、README安装方式差异、omni模型成本）
- **status**: verified
- **stale_after**: 2026-11-29（视觉模型生态变化快，3个月后复核）

## 已知边界

1. 仓库 SKILL.md 硬编码了他人机器路径 `/Users/wwu/.codex/skills/...`（3处），安装时必须替换为本机绝对路径
2. 仓库 README 主推"项目根目录放 vision.js + 合并 CLAUDE.md"方式，博文采用 `~/.claude/skills/` 全局安装方式，两者都可行
3. **dotenv 静默失败陷阱**：不装 dotenv 不报错但 .env 完全不生效，Key 退回默认值 sk-xxx
4. DeepSeek 官方视觉模型 deepseek-v4-flash-vision-exp 已于 2026-08-21 上线，新用户可先评估直连方案
5. qwen3.5-omni-plus 为全模态模型，看图成本约 qwen-vl-max 的 4 倍（7元 vs 1.6元/百万token输入）
6. 百炼免费额度为每模型100万Token、开通后180天内有效

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
