---
type: concept
title: "n8n 入门与核心概念"
bundle: /datawhale/handy-n8n
description: "n8n 定义与特点、与 dify/coze 的定位对比、四种部署方式、平台界面与数据结构"
sources: https://github.com/datawhalechina/handy-n8n/blob/main/c01/README.md
related:
  - /datawhale/handy-n8n/concepts/workflow-design
  - /datawhale/handy-n8n/references/c01-introduction
  - /datawhale/handy-n8n/references/c02-installation
tags: [n8n, automation, deployment, basics]
status: stable
---

# n8n 入门与核心概念

## 核心理解

n8n（nodemation，node + automation，读作 n-eight-n）是一个开源的、基于节点的工作流自动化工具。其名称本身就揭示了本质——**节点（node）+ 自动化（automation）**，通过可视化的节点连接来编排数据流和任务执行。

n8n 的四大核心特点：

1. **模块化**：将复杂任务分解为可管理的小块，每个节点代表一个操作或服务连接
2. **可视化**：通过直观的拖放界面构建工作流，流程一目了然
3. **可扩展性**：支持数百种集成，允许创建自定义节点
4. **数据流**：数据在节点之间流动，每个节点处理或转换数据，直至完成整个工作流

## 工具定位：n8n vs dify vs coze

n8n 并非 AI 原生平台，而是以**工作流自动化**为核心，AI 是其节点生态的一部分。三者定位差异：

| 维度 | n8n | dify | coze |
|------|-----|------|------|
| 核心定位 | 通用工作流自动化 | AI 驱动的自动化与智能应用 | 低代码 AI 应用开发 |
| AI 能力 | 通过节点集成 AI | 原生支持 RAG、多模态 | 内置多种 AI 组件 |
| 部署灵活性 | 本地/云端/Docker，数据可控 | 以云端为主，本地部署有限 | 仅云端，无开源版本 |
| 扩展方式 | 自定义节点开发（TypeScript） | 插件扩展 | 自定义组件 |
| 适合场景 | 复杂自动化、多系统集成、数据主权要求高 | 构建智能问答/RAG 应用 | 快速搭建中小型 AI 应用 |

**关键认知**：n8n 的优势在于"海外主流平台对接 + 灵活编排 + 部署可控"，适合需要将 AI 能力嵌入更广泛业务自动化流程的场景。

## 四种部署方式

n8n 提供从开箱即用到底层可控的部署光谱：

### 官方 SaaS
- 14 天免费试用，基础版 $20/月
- 开箱即用，无需运维
- 适合快速体验和小规模使用

### 本地 PC 部署（Docker）
```bash
docker volume create n8n_data
docker run -d --name n8n -p 5678:5678 \
  -e GENERIC_TIMEZONE="Asia/Shanghai" \
  -e TZ="Asia/Shanghai" \
  -v n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```
- 快速上手，默认 SQLite 存储
- 限制：网络环境影响集成、回调功能受限、定时任务需保持开机

### 云主机部署（Docker Compose）
- 使用官方 `n8n-hosting` 仓库的 `withPostgresAndWorker` 配置
- 包含 n8n + PostgreSQL + Redis + Worker 四个服务
- 队列模式（Queue Mode）：Redis 作消息队列，可水平扩展 Worker
- Caddy 反向代理自动管理 SSL 证书
- 需要域名和基本运维能力

### HuggingFace Space 部署
- 免费 CPU Basic（2vCPU/16GB/50GB）
- 使用 Supabase 作为外部数据库（Space 休眠后数据不丢失）
- Duplicate Space 模板，配置环境变量即可
- 适合无服务器资源的学习者

## 平台界面与数据结构

### 工作流管理
- 工作流不会自动保存，需手动点击 Save 或快捷键
- 支持两种导入方式：复制 JSON 粘贴 / Import from URL
- 右上角 Inactive/Active 开关控制工作流是否激活（定时/Webhook 触发器需激活）

### 数据结构
n8n 节点间使用**对象数组**传递数据：

```json
[
  {
    "json": {
      "apple": "beets",
      "carrot": { "dill": 1 }
    },
    "binary": {
      "apple-picture": {
        "data": "....",
        "mimeType": "image/png",
        "fileExtension": "png",
        "fileName": "example.png"
      }
    }
  }
]
```

- `json` 字段：文本数据
- `binary` 字段：二进制数据（图片、文件等），Base64 编码
- 每个数组项类似数据库表中的一行
- n8n **自动对数组逐项处理**，大部分场景不需要显式循环

## 节点分类

n8n 官方节点主要分类：
- **AI**：Agent、LLM、向量数据库、记忆体等
- **Communication**：邮件、Slack 等通讯工具
- **Data & Storage**：Google Sheets、数据库、对象存储
- **Development**：代码块、Webhook、HTTP、GitHub
- **HITL**：Human-in-the-loop，人机交互节点

## 在 handy-n8n 中的位置

C01 建立工具认知（什么是 n8n、与竞品的差异），C02 解决"如何用上 n8n"（四种部署方式），C03 平台介绍部分解决"如何操作 n8n"（界面、数据结构）。这三部分共同构成入门基础，后续章节在此基础上展开节点编排和高级功能。

## 延伸阅读

- [工作流设计](workflow-design.md)——触发器与核心节点的编排方法
- [数据处理与转换](data-processing.md)——深入理解 n8n 数据结构和代码能力
- [C01 n8n 初识](../references/c01-introduction.md)——完整信源
- [C02 n8n 安装与配置](../references/c02-installation.md)——部署详解
