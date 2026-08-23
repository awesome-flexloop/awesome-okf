---
title: 核心资源分类
type: concept
bundle: /datawhale/Agent-Learning-Hub
description: Agent Learning Hub 将精选资源分为官方指南、项目地图、Skills/协议、现代系统、遗留框架、论文、GitHub 仓库、博客、Claude Code 学习路径九大分类，每类附推荐理由。
related:
  - /datawhale/Agent-Learning-Hub/concepts/agent-learning-roadmap
  - /datawhale/Agent-Learning-Hub/references/source-repo
sources:
  - id: github-repo
    resource: /references/source-repo.md
    title: Agent-Learning-Hub GitHub 仓库
---

# 核心资源分类

Agent Learning Hub 的 Curated Resources 板块不是简单的链接列表，而是按**学习目的和资源类型**分层组织的导航系统。每个资源都附有"为什么值得读"的说明，帮助学习者判断优先级。

## 资源分类总览

### 1. 官方指南与博客（Official Guides And Blogs）

15 条来自 Anthropic、OpenAI、Google 的官方文档和工程博客，是最权威的一手资料：

- **Anthropic**：Building effective agents（Agent 设计入门必读）、Claude Code 系列（Overview/Subagents/Hooks/GitHub Actions/Advanced Patterns）、Tool Use、Computer Use
- **OpenAI**：A practical guide to building agents、New tools for building agents、Agents SDK
- **Google**：Gemini Function Calling、Code Execution、Agent Development Kit（ADK）
- **协议**：Model Context Protocol（MCP）

### 2. 项目地图（Project Map）

开源项目不按 star 数排列，而是按学习目的分 7 层：

| 层级 | 学什么 | 代表项目 |
|------|--------|---------|
| Build From Scratch | agent loop、tool registry、session、context compaction | learn-claude-code、claw0、hello-agents |
| Personal / Always-On Agents | 长运行、skills、记忆、消息入口、权限 | OpenClaw、Hermes Agent、CyberClaw |
| Coding Agents | 真实代码库编辑、shell、测试、sandbox、PR 工作流 | Claude Code、Codex、OpenCode、OpenHands、SWE-agent、pi |
| Agent Harness / SuperAgent Runtime | 长任务执行、sandbox、memory、skills、subagents、trace | DeerFlow、LangGraph |
| Deep Research / RAG Agents | 搜索、抓取、检索、rerank、引用、报告生成 | GPT Researcher、Open Deep Research、LlamaIndex |
| Tutorial Encyclopedias | ReAct、Plan-and-Execute、Multi-Agent、production patterns | GenAI_Agents、hello-agents、smolagents、agents-towards-production |
| Browser / Multimodal Agents | 浏览器/桌面操作、视觉理解、动作空间、失败恢复 | browser-use、UI-TARS-desktop |

### 3. Skills、协议与工具

聚焦现代 agent 能力打包和互操作的 5 个关键概念：

- **Skills**：把流程知识、脚本、模板和验收标准打包成可复用能力（Claude Code Skills、OpenClaw Skills）
- **MCP**（Model Context Protocol）：让 agent 标准化连接外部工具和数据源
- **A2A**（Agent2Agent Protocol）：不同 agent 之间的发现、通信和协作
- **ACP**（Agent Client Protocol）：编辑器/终端/IDE/宿主应用与 agent 之间的统一接口
- **Skill Quality**：评估 skills 是否真正提升成功率（SWE-Skills-Bench、SkillOpt）

### 4. 现代 Agent 系统（Modern Agent Systems）

13 个值得深入研究的系统，每个都标注了独特学习价值。包括 Claude Code（coding agent 产品形态）、learn-claude-code（从零复刻 harness）、claw0（从零构建 gateway）、hello-agents（中文教程）、OpenClaw（本地优先个人 agent）、Hermes Agent（自托管成长型 agent）、CyberClaw（透明审计架构）、DeerFlow（字节 SuperAgent harness）、smolagents（CodeAgent 范式）、LangGraph（状态图编排）、Qwen-Agent（国产生态）、Pydantic AI（类型安全）、pi（TypeScript toolkit）。

### 5. 遗留或可选框架（Legacy Or Optional Frameworks）

明确标注不建议作为学习主线的项目：

- **CrewAI**：可了解 role/task/crew 抽象，但已被更强的 coding agent/harness 形态覆盖
- **AutoGen**：多 agent 对话框架经典项目，适合了解历史和论文
- **LangChain Agents**：生态仍重要，建议重点转向 LangGraph 和具体工程模式

### 6. 论文（Papers）

17 篇按主题覆盖 agent 基础范式到前沿研究：

- **基础范式**：ReAct（reasoning+acting）、Toolformer（工具调用学习）、Reflexion（自我改进）
- **记忆与规划**：Generative Agents（记忆/反思/规划）、Voyager（长期学习）
- **多 Agent**：AutoGen
- **评测基准**：AgentBench、WebArena、SWE-bench、GAIA、OSWorld、τ-bench
- **工程分析**：SWE-agent（agent-computer interface）、Dive into Claude Code、AI Harness Engineering、Configuring Agentic AI Coding Tools、Your Agent Their Asset（安全风险）

### 7. GitHub 仓库

23 个精选仓库，与项目地图互补但更侧重可直接 clone 学习的代码库。额外收录了 Aider（终端 pair programming）、goose（Block 出品可扩展 agent）、microsoft/ai-agents-for-beginners（系统化入门课程）等。

### 8. 深度博客（Thoughtful Blogs）

- **Lilian Weng: LLM Powered Autonomous Agents**——经典长文，系统整理 agent 架构、记忆、规划和工具使用
- **Simon Willison: AI/LLM writing**——务实的 LLM 工程观察
- **LangChain Blog**——LangGraph、LangSmith、agent 工程实践
- **Google Developers Blog: ADK**——Google ADK 官方发布文章

### 9. Claude Code 学习路径

Claude Code 被单独列为研究对象，推荐按"官方文档→复刻项目→架构解析→工程对照"的顺序学习，包含官方工作流教程、learn-claude-code 复刻项目、中文源码解析、Dive into Claude Code 论文等 7 个资源。

## 资源筛选原则

项目欢迎的贡献类型反映了资源筛选标准：

- 优先官方文档和官方工程博客
- 高质量论文和 benchmark
- 有可运行代码的开源仓库
- 有原创见解的严肃技术博客
- 帮助练习特定技能的小项目

明确拒绝搬运的平台帖子、无实质内容的课程广告、私有/付费材料、绕过平台规则的抓取内容。

## 相关概念

- [Agent 学习路线图](./agent-learning-roadmap.md)——这些资源如何嵌入 9 阶段学习路径和 11 级项目阶梯
- [信源登记](../references/source-repo.md)——项目 GitHub 仓库与文件结构说明
