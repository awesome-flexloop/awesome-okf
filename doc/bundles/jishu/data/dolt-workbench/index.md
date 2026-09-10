---
okf_version: "0.2"
type: bundle-index
title: "DoltWorkbench — 现代 SQL 工作台"
description: "DoltWorkbench 知识包：DoltHub 官方开源的现代浏览器 SQL 工作台，支持 MySQL/PostgreSQL/Dolt/Doltgres/SQLite/DoltLite 六数据库类型，基于 Electron + NestJS GraphQL + Next.js 三层架构，内置 Claude AI Agent 模式；含源码事实登记、架构洞察、QueryFactory 工厂模式、DoltLite Revision 缓存机制与实战教程"
tags:
  - dolt-workbench
  - dolt
  - electron
  - nestjs
  - graphql
  - nextjs
  - sql
  - database
  - ai-agent
  - claude
  - doltlite
  - mcp
generated:
  at: "2026-09-09"
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: stable
  noted: "2026-09-09 基于 DoltHub dolt-workbench v0.3.75 (commit 8fb6757) 源码生成，R→I→E→V 四阶段完成，40 条事实登记，5 个概念文档，3 个示例文档"
stale_after: "2027-03-09"
sources:
  - url: "https://github.com/dolthub/dolt-workbench"
    type: official
    title: "dolthub/dolt-workbench — GitHub"
    distance: 1
  - url: "https://github.com/dolthub/dolt-workbench/releases/tag/v0.3.75"
    type: official-release
    title: "DoltWorkbench v0.3.75 Release"
    distance: 1
---

# DoltWorkbench 知识包

## 概述

DoltWorkbench 是 DoltHub 官方推出的现代 SQL 工作台，基于 Electron + NestJS GraphQL Server + Next.js (React) 三层架构构建，支持 MySQL、PostgreSQL、Dolt、Doltgres、SQLite 和 DoltLite 六种数据库类型。

## Bundle 结构

```
dolt-workbench/
├── index.md                 # 本文件（Bundle 根索引）
├── concepts/                # 核心概念文档
│   ├── 00-dolt-workbench-overview.md   # 项目概览
│   ├── 01-architecture.md             # 三层架构设计
│   ├── 02-query-factory-pattern.md    # QueryFactory 工厂模式
│   ├── 03-dolt-lite-revision-cache.md # DoltLite Revision 缓存
│   └── 04-agent-mode.md              # Agent Mode 实现
├── examples/                # 实战教程
│   ├── 00-getting-started.md          # 快速开始
│   ├── 01-connecting-databases.md     # 连接数据库
│   └── 02-using-agent-mode.md         # 使用 Agent Mode
└── references/              # 参考材料
    └── source.md                  # 源码事实登记 (F-001~F-040)
```

## 知识地图

### 概念层（Constituents）

- [00-dolt-workbench-overview](./concepts/00-dolt-workbench-overview.md) — 项目定位、功能特性、支持数据库
- [01-architecture](./concepts/01-architecture.md) — Electron + NestJS + Next.js 三层架构
- [02-query-factory-pattern](./concepts/02-query-factory-pattern.md) — 6 数据库类型的统一查询工厂
- [03-dolt-lite-revision-cache](./concepts/03-dolt-lite-revision-cache.md) — DataSource 缓存与 revision 隔离
- [04-agent-mode](./concepts/04-agent-mode.md) — Claude AI Agent 实现与 MCP 工具

### 示例层（Examples）

- [00-getting-started](./examples/00-getting-started.md) — 安装、配置与首次使用
- [01-connecting-databases](./examples/01-connecting-databases.md) — 6 种数据库连接方式
- [02-using-agent-mode](./examples/02-using-agent-mode.md) — AI 助手使用指南

### 参考层（References）

- [source](./references/source.md) — 40 条源码事实登记（F-001~F-040）

## 关键洞察

1. **三层架构分离**: Electron 主进程管理进程生命周期，NestJS GraphQL Server 提供统一 API，Next.js Renderer 负责 UI 渲染
2. **QueryFactory 多态**: 通过继承链支持 6 种数据库类型，`isDolt` 标记区分 Dolt 系列与非 Dolt 数据库
3. **DoltLite revision 缓存**: 每个 revision 对应独立 DataSource，通过 `file@revision` 语法实现只读隔离
4. **Agent Mode 安全**: 敏感操作（commit/branch/delete）需要用户确认，防止 AI 误操作

## 信源信息

- **信源距离**: ① 官方源码（GitHub 公开仓库）
- **固定版本**: v0.3.75（commit `8fb6757`，2026-08-24）
- **仓库地址**: https://github.com/dolthub/dolt-workbench

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
```
