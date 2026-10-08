---
type: Reference
title: "CodeBuddy IDE 官网信源"
description: "CodeBuddy IDE 产品官网（codebuddy.cn/ide）的事实登记，记录产品定位、全流程开发链路、平台支持与部署集成。"
tags: [codebuddy, ide, reference, official-site]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-02-23
sources:
  - id: ide-official
    resource: https://www.codebuddy.cn/ide/
    title: CodeBuddy IDE 产品官网
---

# CodeBuddy IDE 官网信源

本文件登记 CodeBuddy IDE 产品官网（https://www.codebuddy.cn/ide/）的公开事实，对应事实编号 F-001 ~ F-008。

## 信源元信息

| 项目 | 内容 |
|------|------|
| 信源 ID | ide-official |
| URL | https://www.codebuddy.cn/ide/ |
| 类型 | 产品官网 |
| 抓取日期 | 2026-08-23 |
| 对应事实 | F-001 ~ F-008 |

## 产品定位

CodeBuddy IDE 定位为"全球首款 AI 驱动的集成产品、设计与开发全栈高级工程师"（F-001），官网标语为 "Where Design Meets Dev in Real-Time"（F-002）。其核心主张是将产品、设计、研发三个角色的工作流整合到同一个 AI 驱动的桌面环境中。

## 全流程开发链路

IDE 以自然语言为输入，驱动完整开发链路（F-003）：

```
自然语言 → PRD → 设计原型 → 前后端代码 → 部署
```

关键能力包括：

- **后端一键部署**：集成腾讯云 CloudBase 与 Supabase 后端（F-004）。
- **Figma 设计稿转代码**：支持 Figma 设计稿一键转代码（F-005）。
- **预置组件库**：内置组件库，并支持通过自然语言修改组件（F-006）。

## 平台支持

| 平台 | 版本要求 |
|------|----------|
| macOS | 11.0+（Apple/Intel 双架构） |
| Windows | 10+ x64 |
| Linux | .deb（ARM64/x86_64） |

以上平台支持信息见 F-007。

## 技术架构

IDE 基于 VSCode 架构构建，因此天然支持插件市场与远程 SSH 开发（F-008）。这一架构选择意味着 CodeBuddy IDE 可视为深度集成了产设研 AI 能力的 VSCode 衍生发行版，兼容 VSCode 生态。

## 事实索引

| 事实 ID | 内容摘要 |
|---------|----------|
| F-001 | 全球首款 AI 驱动的集成产品、设计与开发全栈高级工程师 |
| F-002 | 标语 "Where Design Meets Dev in Real-Time" |
| F-003 | 自然语言驱动全流程：自然语言→PRD→设计原型→前后端代码→部署 |
| F-004 | 集成腾讯云 CloudBase/Supabase 后端一键部署 |
| F-005 | Figma 设计稿一键转代码 |
| F-006 | 预置组件库 + 自然语言修改 |
| F-007 | 平台：macOS 11.0+、Windows 10+ x64、Linux .deb ARM64/x86_64 |
| F-008 | 基于 VSCode 架构，支持插件市场、远程 SSH 开发 |

## 相关概念

- [产品矩阵总览](../concepts/00-product-matrix.md) — CodeBuddy 三态一体产品矩阵
- [CodeBuddy IDE](../concepts/01-ide.md) — IDE 产设研一体能力详解
- [CLI](../concepts/02-cli.md) — 终端原生 AI 编程工具
- [IDE 工作流示例](../examples/ide-workflow.md) — 从自然语言到部署的实战流程
