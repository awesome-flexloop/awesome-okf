---
okf_version: "0.2"
type: Concept
title: "Octop 是什么：项目身份与定位"
description: "Octop 的定位、官方自述、开源事实、许可、热度（带时点）与它解决的问题（事实层）"
tags: [octop, ai-agent, local-first, self-hosted, project-profile, tencent]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-10T09:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/kskjE8iQ2AxtI_Skqz5fvg"
  - id: github-api
    url: "https://api.github.com/repos/TencentCloud/Octop"
  - id: official-home
    url: "https://tencentcloud.github.io/Octop/"
---

# Octop 是什么：项目身份与定位

> 事实层（What / When / Who / License）。本文只陈述可核验事实，产品理念转述请见 [04 安装与快速上手](04-install-and-run.md) 与官方文档。

## 一句话定位

[Octop](https://github.com/TencentCloud/Octop) 是腾讯云开源的**自托管（self-hosted）多用户、多 Agent AI 助手平台**。官方仓库表述为：

> "A smarter, self-hosted AI assistant — multi-user, multi-agent."（F-031）

它把「单 Agent 聊天框」扩展为一个可长期运行、多专业 Agent 协作、带长期记忆与工具能力、可选多渠道接入的 AI 工作平台（F-001、F-012、F-031）。

## 身份卡片

| 项目 | 值 | 出处 |
|------|-----|------|
| 仓库 | https://github.com/TencentCloud/Octop | F-030 |
| 归属 | GitHub Organization **TencentCloud**（腾讯云官方组织） | F-030 |
| 主语言 | Python（后端）；前端 React + TypeScript + Vite + Ant Design | F-035 |
| 许可 | **MIT License**（官方主页与 GitHub API 均标注） | F-032 |
| 创建时间 | **2026-07-08**（GitHub API）；**2026.07.10** 正式开源 | F-030/F-033 |
| 源码脉络 | 源自 **LightClaw ACE**，面向智能体时代的系统性重构 | F-033 |
| 主页 | 项目页 https://octop.cloud ；官方文档 https://tencentcloud.github.io/Octop/ | F-039 |
| 发布包 | PyPI `octop`（compose 多件套为由 4 个 Harness 组件打包的单一进程） | F-037/F-039 |
| 社区数据 | Star 8292、Fork 1006、Open Issues 697（**2026-10-10 时点**；博文口径 7.9k） | F-029 |

## 热度数据（带时点阅读）

- 博文成文时称「GitHub 上获 7.9k stars」（F-002）。
- 2026-10-10 GitHub API 时点快照：**Star 8292、Fork 1006、Open Issues 697、Watch 58**（F-029）。
- Star 为持续增长的动态数字，引用时必须携带时点；两个数字分别代表各自时点。

## 解决的问题（博文视角）

博文概括 Octop 要解决的问题（F-001 概述，属作者转述）：

1. **AI 助手难以长期陪伴、持续工作**：每次新对话都要重新介绍工作背景、项目进度、使用习惯；
2. **定时任务与工具配置繁琐**：想让 AI 定时整理日报、查询资料、处理文件，需分别配置不同工具；
3. **多人/多 Agent 协同困难**：每人聊天记录、偏好、工作文件不同，如何让多个 AI 助手独立工作又在必要时协作。

Octop 用「多 Agent 专家 + 长期记忆 + RAG 知识库 + 工具调用 + 多用户多渠道」回应这三点，机制细节见 [01 架构](01-architecture-and-harness.md)、[02 多 Agent 与记忆](02-multi-agent-and-memory.md)、[03 工具与渠道](03-tools-and-channels.md)。

## 阅读下一篇

- [01 · 单进程架构与 Harness 组件](01-architecture-and-harness.md)——为什么能单进程自托管，四大组件各管什么
- [02 · 多 Agent 专家与长期记忆](02-multi-agent-and-memory.md)——从单聊天机器人到 AI 专家团队
- [04 · 安装与快速上手](04-install-and-run.md)——两条命令安装、初始化、启动