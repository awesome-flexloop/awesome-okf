---
okf_version: "0.2"
type: Concept
title: "OpenCreator 是什么：项目身份与定位"
description: "OpenCreator（原名 KrillinAI）的定位、归属、许可、热度与双模式工作方式"
tags: [opencreator, what-is, local-first, apache-2.0, codex-cli]
sources:
  - id: github-api
    url: "https://api.github.com/repos/krillinai/OpenCreator"
    title: "GitHub API 仓库元数据"
  - id: blog
    url: "https://mp.weixin.qq.com/s/oecbF0OUAKYSZfbI6WsKfA"
    title: "1.2万 Star 爆火，来看看这款顶级的一站式 Agent 创作神器"
    account: AI开源无界
---

# OpenCreator 是什么

## 一句话定义

[OpenCreator](https://github.com/krillinai/OpenCreator) 是一个**面向创作者（尤其是自媒体/视频创作者个人与小团队）的本地优先 AI 工作台**：把视频翻译、视频下载、图片/视频生成、文章写作、小红书笔记、短视频脚本、火柴人动画、智能配音等创作日常所需的能力汇聚到一个应用，跑在自己的电脑上，以 **Codex CLI 作为 Agent 执行引擎**组织创作流程。官方 README 自述：*"The open-source AI workspace & Skills for creators"*。

## 身份与归属

- **仓库**：`krillinai/OpenCreator`（官方 org 为个人/团队 `krillinai`）。
- **原名前身**：**KrillinAI**（官方 README 明确「OpenCreator was formerly known as KrillinAI」），原为专注视频翻译配音的工具 [F-004](references/facts.md)。
- **创建时间**：**2024-12-17**（GitHub API）[F-005](references/facts.md)。
- **许可**：**Apache-2.0**（官方；博文未提及，本包补充）[F-046](references/facts.md)。
- **技术栈**：**TypeScript** monorepo（pnpm workspace）[F-045](references/facts.md)。
- **官方项目主页**：https://www.open-creator.ai/en/ [F-047](references/facts.md)。

## 热度（带时点）

| 指标 | 数值（2026-10-10 快照） | 博文口径 |
|------|------------------------|---------|
| Star | 12,671 | 「1.2 万」[F-001](references/facts.md)[F-048](references/facts.md) |
| Fork | 1,306 | 约 1.2k |
| Open Issues | 29 | — |
| 当日排名 | Trendshift 单日 #1 | — [F-055](references/facts.md) |

> ⚠️ 动态数字以官方 API 快照为准，引用须带时点；博文「1.2 万」为成文口径，本包采用官方现值。

## 定位：本地优先，与网页单功能工具做差异化

OpenCreator 的核心定位是**不造轮子的本地 Agent 创作平台**：

- **本地优先**：默认跑在自己机器上，素材与成品不经过第三方服务器；模型密钥由用户自行配置 [F-006](references/facts.md)[F-007](references/facts.md)。
- **不开箱即用的云服务**：与同类网页服务（素材和成品都过别人服务器）形成对比。
- **面向个人与小团队**：设计带「Ready-to-Use Desktop App」与本地 Runtime 自启，降低上手门槛 [F-035](references/facts.md)。

## 两种连接的工作方式

OpenCreator 提供两条互补路径 [F-023](references/facts.md)：

1. **内容工作台（可视化）**：打开工具填参数点生成，用可复用的创作模板快速出成品。
2. **Agent 对话**：以自然语言描述需求，Agent 自行调用工具完成（如「把这个视频翻译成英语，字幕换成黄色，顺便出个竖屏版」）。

两种方式共用**同一套状态机**——对话里改字幕颜色，工作区界面同步变；工作区手动调参，对话也知道进度 [F-026](references/facts.md)。每次修改生成一个新版本，旧版本设置和结果保留，可随时切回 [F-027](references/facts.md)。

## 采用提示与已知边界

- **优点**：多模态创作闭环、本地可控、Agent 编排开箱即用、上手快（桌面版自带 Codex，免装 Node）。
- **边界**：① Agent 能力绑定 Codex CLI（复用其引擎的代价，见 [02 概念](02-agent-and-codex-native.md)）；② 模型服务额度自备，是**自己的配额**，单 Agent 任务可能消耗较大 token，建议先小任务试水（社区估算、非官方数字）[F-040](references/facts.md)；③ 我未在本机实测，具体命令与端口以官方文档为准。

## 相关概念

- [十个创作工具一览](01-ten-creator-tools.md)
- [Agent 与 Codex 原生架构](02-agent-and-codex-native.md)