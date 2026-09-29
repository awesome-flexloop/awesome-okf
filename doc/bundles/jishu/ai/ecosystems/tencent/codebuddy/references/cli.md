---
type: Reference
title: "CodeBuddy CLI 官网信源"
description: "CodeBuddy CLI 产品官网（codebuddy.cn/cli）的事实登记，记录终端原生 AI 编程工具的安装、代码感知、MCP、分层记忆与 Sub-agents 能力。"
tags: [codebuddy, cli, reference, official-site, terminal]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-02-23
sources:
  - id: cli-official
    resource: https://www.codebuddy.cn/cli/
    title: CodeBuddy CLI 产品官网
---

# CodeBuddy CLI 官网信源

本文件登记 CodeBuddy CLI 产品官网（https://www.codebuddy.cn/cli/）的公开事实，对应事实编号 F-026 ~ F-038。

## 信源元信息

| 项目 | 内容 |
|------|------|
| 信源 ID | cli-official |
| URL | https://www.codebuddy.cn/cli/ |
| 类型 | 产品官网 |
| 抓取日期 | 2026-08-23 |
| 对应事实 | F-026 ~ F-038 |

## 产品定位

CodeBuddy CLI 定位为终端原生 AI 编程工具，具备全仓百万级代码感知能力（F-026）。它面向偏好终端工作流的开发者，提供深度编码、全代码库分析与语义搜索能力。

## 安装与环境要求

```bash
npm install -g @tencent-ai/codebuddy-code
```

环境要求（F-027）：

- Node.js 22+
- Git

> 注：IDE 文档页给出的 Node.js 要求为 18.0+（F-025），CLI 官网要求为 22+（F-027），以 CLI 官网为 CLI 使用的权威要求。

## 核心特性

### 终端深度编码与代码智能

- 终端深度编码（F-028）
- 高级代码智能：全代码库分析 + 语义搜索（F-029）
- 全仓百万级代码感知（F-026）

### 项目手册初始化

- `/init` 命令生成 CODEBUDDY.md 项目手册（F-030）

### 多模态输入

- 支持图片与截图输入，通过 Ctrl+V 粘贴（F-031）

### MCP 协议

- 同时具备 MCP 客户端与服务器能力（F-032）

### 长期记忆（分层）

CodeBuddy.md 记忆分三层（F-033）：

| 层级 | 作用范围 |
|------|----------|
| 项目级 | 当前项目 |
| 用户级 | 当前用户所有项目 |
| 企业级 | 企业统一规则 |

### Sub-agents

- 独立上下文
- 专属提示词
- 独立工具权限（F-034）

### 自定义

- 分层配置
- CLI 参数覆盖（F-035）

## 跨平台与语言支持

- 平台：macOS / Linux / Windows（F-036）
- 编程语言：50+（F-036）

## 故障排查

`/doctor` 命令用于环境与配置故障排查（F-037）。

## 计费

CLI 使用按 Token 消耗计费（F-038）。

## 事实索引

| 事实 ID | 内容摘要 |
|---------|----------|
| F-026 | 终端原生 AI 编程工具，全仓百万级代码感知 |
| F-027 | 安装命令、Node.js 22+、Git 要求 |
| F-028 | 终端深度编码 |
| F-029 | 全代码库分析 + 语义搜索 |
| F-030 | /init 生成 CODEBUDDY.md |
| F-031 | 图片/截图支持（Ctrl+V） |
| F-032 | MCP 客户端/服务器 |
| F-033 | 长期记忆分层：项目/用户/企业级 |
| F-034 | Sub-agents 独立上下文/提示词/工具权限 |
| F-035 | 分层配置 + CLI 参数 |
| F-036 | 跨平台，50+ 编程语言 |
| F-037 | /doctor 故障排查 |
| F-038 | 按 Token 消耗计费 |

## 相关概念

- [CLI](../concepts/02-cli.md) — CLI 架构与分层记忆详解
- [产品矩阵总览](../concepts/00-product-matrix.md) — CLI 在三态一体中的定位
- [CLI 快速入门](../examples/quick-start-cli.md) — 安装、初始化与常用命令实战
- [CodeBuddy IDE](../concepts/01-ide.md) — CLI 与 IDE 共享的高级能力
