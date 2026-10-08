---
type: Reference
title: "CodeBuddy IDE 文档介绍信源"
description: "CodeBuddy IDE 官方文档介绍页（docs/ide/Introduction）的事实登记，记录三种形态、四阶段流程、内置生态与插件兼容矩阵。"
tags: [codebuddy, ide, docs, reference, introduction]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-02-23
sources:
  - id: docs-intro
    resource: https://www.codebuddy.cn/docs/ide/Introduction
    title: CodeBuddy IDE 文档介绍
---

# CodeBuddy IDE 文档介绍信源

本文件登记 CodeBuddy IDE 官方文档介绍页（https://www.codebuddy.cn/docs/ide/Introduction）的公开事实，对应事实编号 F-009 ~ F-025。

## 信源元信息

| 项目 | 内容 |
|------|------|
| 信源 ID | docs-intro |
| URL | https://www.codebuddy.cn/docs/ide/Introduction |
| 类型 | 官方文档 |
| 抓取日期 | 2026-08-23 |
| 对应事实 | F-009 ~ F-025 |

## 三种产品形态

CodeBuddy 提供三种产品形态（F-009）：

| 形态 | 定位 |
|------|------|
| IDE | 产设研一体的独立桌面端 |
| 插件 | 即插即用，嵌入主流 IDE |
| CLI/Code | 终端命令行工具 |

## 四阶段开发流程

文档将开发流程划分为四个阶段（F-010 ~ F-013）：

### 产品阶段

- 需求分析
- PRD 生成（F-010）

### 设计阶段

- 原型设计
- 草图转高保真
- 组件库（F-011）

### 研发阶段

- Figma 转码
- 智能补全
- 单测生成
- 代码审查（@workspace#Codebase）（F-012）

### 部署阶段

- 沙箱部署
- 公开链接发布（F-013）

## 内置生态

| 类别 | 生态服务 | 事实 ID |
|------|----------|---------|
| 后端（BaaS） | Supabase、腾讯 CloudBase | F-014 |
| 部署 | CloudStudio、EdgeOne Pages | F-015 |
| 组件库 | TDesign、MUI、Shadcn | F-016 |
| 多模型 | 混元、DeepSeek | F-017 |

## 高级功能

文档列出的高级功能（F-018）：

- Plan 模式
- Subagents
- Skills
- Hooks
- MCP
- 模型配置
- 检查点
- 记忆
- 规则
- 智能提交

## 插件兼容矩阵

| 宿主 IDE | 兼容版本 | 事实 ID |
|----------|----------|---------|
| VS Code | 1.82+ | F-019 |
| IntelliJ IDEA / PyCharm 等 JetBrains IDE | 2022.2+ | F-020 |
| Android Studio | Flamingo | F-021 |
| 微信开发者工具 | 1.06+ | F-022 |
| Xcode | 14.0+ | F-023 |
| Visual Studio | 2022 | F-024 |

## CLI 安装

文档给出的 CLI 安装命令（F-025）：

```bash
npm install -g @tencent-ai/codebuddy-code
```

要求 Node.js 18.0+。

## 事实索引

| 事实 ID | 内容摘要 |
|---------|----------|
| F-009 | 三种形态：IDE、插件、CLI/Code |
| F-010 | 产品阶段：需求分析/PRD |
| F-011 | 设计阶段：原型/草图转高保真/组件库 |
| F-012 | 研发阶段：Figma转码/智能补全/单测生成/代码审查 |
| F-013 | 部署阶段：沙箱/公开链接 |
| F-014 | 后端生态：Supabase + 腾讯 CloudBase |
| F-015 | 部署生态：CloudStudio/EdgeOne Pages |
| F-016 | 组件库：TDesign/MUI/Shadcn |
| F-017 | 多模型：混元/DeepSeek |
| F-018 | 高级功能清单（Plan/Subagents/Skills/Hooks/MCP 等） |
| F-019 ~ F-024 | 插件兼容六大宿主 IDE 版本 |
| F-025 | CLI 安装命令与 Node.js 18.0+ 要求 |

## 相关概念

- [CodeBuddy IDE](../concepts/01-ide.md) — 四阶段流程与内置生态详解
- [CLI](../concepts/02-cli.md) — 终端工具能力与跨形态共享特性
- [产品矩阵总览](../concepts/00-product-matrix.md) — 三种形态的定位与关系
- [CLI 快速入门](../examples/quick-start-cli.md) — CLI 安装与初始化实战
