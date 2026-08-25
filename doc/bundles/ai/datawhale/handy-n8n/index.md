---
okf_version: "0.2"
type: index
title: "handy-n8n：n8n 工作流自动化从入门到精通"
bundle: handy-n8n
description: "Datawhale 开源的 n8n 系统学习教程——从工具定位与多场景部署，到节点编排与代码扩展，再到 AI/RAG/MCP 集成与自定义节点开发，覆盖工作流自动化全链路"
concepts:
  - /datawhale/handy-n8n/concepts/getting-started
  - /datawhale/handy-n8n/concepts/workflow-design
  - /datawhale/handy-n8n/concepts/data-processing
  - /datawhale/handy-n8n/concepts/ai-api-integration
  - /datawhale/handy-n8n/concepts/advanced-practice
references:
  - /datawhale/handy-n8n/references/c01-introduction
  - /datawhale/handy-n8n/references/c02-installation
  - /datawhale/handy-n8n/references/c03-basic-concepts
  - /datawhale/handy-n8n/references/c04-advanced-usage
  - /datawhale/handy-n8n/references/c05-community-nodes
  - /datawhale/handy-n8n/references/c06-case-studies
examples:
  - /datawhale/handy-n8n/examples/github-trending-digest
  - /datawhale/handy-n8n/examples/github-issue-notify
  - /datawhale/handy-n8n/examples/rag-knowledge-chat
  - /datawhale/handy-n8n/examples/custom-amap-node
sources: https://github.com/datawhalechina/handy-n8n
generated:
  by: okf-wiki-bot
  at: "2026-08-23T00:00:00Z"
verified:
  by: process:seven-concepts-v
  at: "2026-08-23T00:00:00Z"
status: stable
stale_after: "2027-08-23"
---

# handy-n8n：n8n 工作流自动化从入门到精通

[handy-n8n](https://github.com/datawhalechina/handy-n8n) 是 Datawhale 开源的 n8n 系统学习教程，以"理论 + 实操"为核心，带你从入门到精通 n8n 工作流自动化。全书 6 章，从 n8n 工具定位与多场景部署出发，系统讲解节点编排、数据处理、代码扩展、AI/RAG/MCP 集成，最终通过自定义节点开发和实战案例将知识转化为生产力。

## 知识地图

```
🚀 入门篇（第1-2章）
  ├── C01 n8n 初识 → 定义、特点、应用场景、与 dify/coze 对比定位
  └── C02 安装与配置 → SaaS / 本地 Docker / 云主机 Compose / HF Space 四种部署
        ↓
🧩 基础篇（第3章）
  ├── 平台介绍 → 界面、工作流导入、数据结构（json/binary 对象数组）
  ├── 触发器节点 → Manual / Schedule / Webhook / Chat
  ├── 核心节点 → 数据处理（Edit Fields/Split Out）、控制流（If/Merge/Loop）、HTTP
  └── 代码能力 → Expressions 表达式、Code 节点（JS/Python）、内置变量与外部库
        ↓
🔬 进阶篇（第4-5章）
  ├── 子工作流与错误处理 → Execute Workflow、Error Trigger、容错通知
  ├── AI 集成 → 集群节点、Memory、RAG、Tools、MCP
  └── 社区节点与自定义开发 → npm 社区节点、TypeScript 声明式/程序式节点开发
        ↓
🎯 实战篇（第6章）
  └── GitHub Trending 每日推送 / GitHub Issue 飞书通知
```

## 核心概念（concepts/）

* [n8n 入门与核心概念](concepts/getting-started.md) — n8n 定义与特点（nodemation）、与 dify/coze 的定位对比、四种部署方式（SaaS/本地 Docker/云主机 Compose/HF Space）、平台界面与数据结构。对应 C01-C02 及 C03 平台介绍。
* [工作流设计](concepts/workflow-design.md) — 触发器节点（Manual/Schedule/Webhook/Chat）、核心节点（Edit Fields/Split Out/If/Merge/Loop/HTTP Request）、工作流导入与执行、节点连接与分支控制。对应 C03。
* [数据处理与转换](concepts/data-processing.md) — n8n 数据结构（对象数组 json/binary）、Expressions 表达式（`{{ }}` 模板）、Code 节点（JavaScript/Python 双模式、内置变量、外部库引入）、数据拆分与合并。对应 C03。
* [AI 与 API 集成](concepts/ai-api-integration.md) — 集群节点（Chain/Agent）、Memory 记忆、RAG 向量检索、Tools 工具调用、MCP 协议（Client/Server 双向）、HTTP Request 节点作为通用 API 连接器。对应 C04。
* [高级实战](concepts/advanced-practice.md) — 子工作流模块化、Error Trigger 错误处理、社区节点安装、TypeScript 自定义节点开发（声明式/程序式、INodeType/ICredentialType）、GitHub 实战案例。对应 C04-C06。

## 实战示例（examples/）

* [GitHub Trending 每日推送](examples/github-trending-digest.md) — C06 案例：Schedule Trigger 定时获取 GitHub Trending，邮件发送日报。
* [GitHub Issue 飞书通知](examples/github-issue-notify.md) — C06 案例：Webhook 监听 GitHub Issue 事件，飞书机器人实时通知。
* [RAG 知识库对话](examples/rag-knowledge-chat.md) — C04 实践：Form Trigger 文件上传 → Embedding → Vector Store，Chat Trigger + Agent 检索问答。
* [自定义高德地图天气节点](examples/custom-amap-node.md) — C05 实践：TypeScript 声明式节点开发全流程，含鉴权类、routing 配置、npm link 本地调试。

## 信源登记（references/）

* [C01 n8n 初识](references/c01-introduction.md) — n8n 简介、应用场景、节点分类、与 dify/coze 对比。
* [C02 n8n 安装与配置](references/c02-installation.md) — 官方 SaaS、本地 PC Docker、云主机 Docker Compose、HuggingFace Space 四种部署方式。
* [C03 n8n 基本概念](references/c03-basic-concepts.md) — 平台介绍、触发器节点、核心节点、代码节点（表达式与 Code）。
* [C04 n8n 高阶用法](references/c04-advanced-usage.md) — 子工作流、错误处理、集群节点、Memory、RAG、Tools、MCP。
* [C05 n8n 社区节点与节点开发](references/c05-community-nodes.md) — 社区节点安装、自定义节点开发（高德地图天气示例）。
* [C06 n8n 案例分享](references/c06-case-studies.md) — GitHub Trending 推送、GitHub Issue 通知两个实战案例。

## 深度洞察

本知识包的设计决策与核心洞察详见 [spec/insights.md](spec/insights.md)，包括：

1. **渐进式学习曲线**——从工具定位对比到多场景部署选择，再到节点编排与代码扩展，每一步都有明确的能力递进
2. **低代码平台的"逃生舱"设计**——表达式→Code 节点→自定义节点的三层代码能力递进，在无代码体验与可编程扩展性之间取得平衡
3. **AI 作为工作流节点而非全部**——从 Chain 到 Agent 到 MCP 的 AI 集成路径，n8n 将 AI 能力嵌入更广泛的自动化编排中

## 目录结构

```
handy-n8n/
├── spec/
│   ├── facts.md              # 章节结构与工作流资产事实清单
│   └── insights.md           # 3 个核心设计洞察
├── concepts/                 # 5 个核心概念
│   ├── index.md
│   ├── getting-started.md
│   ├── workflow-design.md
│   ├── data-processing.md
│   ├── ai-api-integration.md
│   └── advanced-practice.md
├── examples/                 # 4 个实战示例
│   ├── index.md
│   ├── github-trending-digest.md
│   ├── github-issue-notify.md
│   ├── rag-knowledge-chat.md
│   └── custom-amap-node.md
├── references/               # 6 章信源登记
│   ├── index.md
│   └── c01-c06 ... .md
├── index.md                  # 本文件
└── log.md                    # 更新日志
```

---

> **源码位置**：`external/libs/ai/datawhalechina/handy-n8n/`
>
> **在线阅读**：https://datawhalechina.github.io/handy-n8n/
>
> **n8n 官网**：https://n8n.io/
>
> **开源协议**：CC BY-NC-SA 4.0
>
> **生成时间**：2026-08-23 | **维护者**：OKF Wiki Bot

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
