---
okf_version: "0.2"
type: Concept
title: "Agent 对话与 Codex 原生：不造轮子的引擎策略"
description: "OpenCreator 如何复用 Codex CLI 作为 Agent 执行引擎——双模式、状态机、版本化、记忆与可扩展 Skills"
tags: [opencreator, codex-cli, agent, dual-mode, versioning, memory, skills]
sources:
  - id: github-repo
    url: "https://github.com/krillinai/OpenCreator"
    title: "OpenCreator README"
  - id: blog
    url: "https://mp.weixin.qq.com/s/oecbF0OUAKYSZfbI6WsKfA"
    title: "1.2万 Star 爆火，来看看这款顶级的一站式 Agent 创作神器"
    account: AI开源无界
---

# Agent 对话与 Codex 原生

## 核心设计：复用 Codex CLI，不自造 Agent 循环

OpenCreator 没有自行实现一个 Agent 循环，而是**直接以 Codex CLI 作为执行引擎**，在其外围加一个稳定的本地 Runtime、可视化工作台与桌面宿主 [F-024](references/facts.md)。它复用了 Codex 的**模型、工具调用、Skills、MCP** 等一整层能力 [F-025](references/facts.md)。

> **术语速览（新人提示）**：**Codex CLI** 是 OpenAI 的开源命令行 Agent 执行器；**Skills** 是用 `SKILL.md` 描述的、可被 Agent 调用的领域能力包（类似"插件"）；**MCP**（Model Context Protocol）是一种把外部工具/数据接给 LLM 的标准协议。三者都可被 OpenCreator 复用，因此你并不需要自己实现它们。

> **价值**：不必再维护第二套执行引擎，专注做「创作领域工作台」。
> **代价**：Agent 能力**绑定 Codex**——模型目录、Skills、MCP 的可获得性都取决于本机 Codex 环境。

## 双模式与统一状态机

| 模式 | 形态 | 说明 |
|------|------|------|
| 内容工作台 | 可视化填参 | 用逗点工具与创作模板，细粒度调字幕/镜头/音频/生成设置 |
| Agent 对话 | 自然语言 | 说清需求，Agent 调工具完成，可组织成项目、后台运行 |

两者共用**同一套状态机**：对话里改字幕颜色 → 工作区同步变；工作区手动调参 → 对话知晓进度 [F-026](references/facts.md)。这避免了"切换工具丢上下文"的心智负担。

## 版本化创作

每次修改生成一个**新版本**，同时保留旧版本的设置与结果；改到第 5 版觉得第 2 版好，可直接切回去 [F-027](references/facts.md)。这一机制贴合创作场景的探索—收敛节奏。

## 记忆与任务

- **记忆三层**：全局 / 项目 / 对话（thread）记忆，带摘要与可复现的 Run 输入快照；"告诉过它的偏好下次还生效" [F-030](references/facts.md)。
- **后台任务**：可后台运行、关闭界面继续执行、跑完发通知 [F-028](references/facts.md)。
- **定时任务**：可设定时调度 [F-029](references/facts.md)。

## 可扩展 Skills

OpenCreator 支持本地 **Codex Skills**（由 `SKILL.md` 定义）。仓库自带视频制作相关的 7 个 Skill [F-049](references/facts.md)：KrillinAI CLI、Subtitle、TTS、Landscape Render、Portrait Render、Cover、Pipeline Plan。也可添加你自己的 Skills 与 MCP。

> ⚠️ 仓库内含 Skill 不等于自动安装；视频工作流 Skill 需要 CLI 与相关服务已配置。

## 模型供给

语言模型的可获得性跟随 **Codex 模型目录** 或你的 **OpenAI 兼容提供商**；图像/视频/语音/转写模型走「Settings → AI Services」配置的服务 [F-031](references/facts.md)[F-032](references/facts.md)。官方语言模型表：GPT、DeepSeek、Qwen（通义千问）、Kimi、GLM（智谱）、Grok、Doubao（豆包）、ERNIE（文心）、Hunyuan（混元）、MiniMax [F-031](references/facts.md)[F-054](references/facts.md)。

> 博文清单遗漏了 Grok，本包补充。

## 相关概念

- [项目身份与定位](00-what-is-opencreator.md)
- [十个创作工具](01-ten-creator-tools.md)
- [安装与快速上手](03-install-quickstart.md)