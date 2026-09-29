---
okf_version: "0.2"
type: concept
title: Skills 技术机制与核心概念
description: Agent Skills 的工作原理、动态工具注入机制、跨平台多模型支持（F-016 至 F-021）
tags: [agent-skills, skills-sdk, mechanism, cross-platform]
generated:
  by: agnes-2.5-flash
  at: "2026-09-09T15:22:00+08:00"
sources:
  - id: blog-article
    url: https://mp.weixin.qq.com/s/7ox6ioOtGI2TNyFs4UpL4Q
  - id: github-mattpocock-skills
    url: https://github.com/mattpocock/skills
  - id: skills-sh
    url: https://www.skills.sh/
---

# Skills 技术机制与核心概念

## 什么是 Skills

Skills 是嵌入 AI 系统提示中的**工具（Tools）和上下文（Context）包**（F-018）。它们不是独立的运行时，而是告诉 AI "某一类活怎么干"的说明文档。

**关键特征**：
- **轻量**：单个 Skill 通常是一个 Markdown 文件
- **可组合**：多个 Skill 可同时加载，互不干扰
- **按需触发**：通过 `/skill-name` 命令激活，非持续占用上下文

## 核心机制：动态工具注入

> F-019：Skills 的核心机制是**动态工具注入**——根据用户请求，按需将特定工具/函数添加到 AI 的上下文中。

这与传统"全量注入所有工具"的方式不同：

```
传统方式：系统提示包含所有可能用到的工具（臃肿、慢）
Skills 方式：只在需要时注入当前任务相关的工具（精简、快）
```

**实际效果**：
- 减少上下文浪费，降低 API 调用成本
- 提高 AI 响应准确率（工具描述更聚焦）
- 支持复杂工作流的分步执行

## 安装与使用

### 安装命令（F-016）

```bash
npx skills@latest add <owner/repo>
```

示例：安装 Matt Pocock 的 skills 项目：

```bash
npx skills@latest add mattpocock/skills
```

### 平台支持（F-017）

skills 被设计为**跨平台兼容**，可被以下主流 AI 编程工具使用：

| 工具 | 支持状态 | 来源 |
|------|---------|------|
| Claude Code | ✅ | F-017 |
| Cursor | ✅ | F-017 |
| Trae | ✅ | F-017 |
| VS Code（Cline/Continue 等） | ✅ | F-017 |

### 多模型支持（F-021）

Skills 不绑定单一模型，支持多种 LLM 后端：

| 模型提供商 | 支持状态 |
|-----------|---------|
| Anthropic Claude | ✅ F-021 |
| OpenAI GPT 系列 | ✅ F-021 |
| Google Gemini | ✅ F-021 |

## 跨平台运行（F-020）

Skills SDK 保证在以下操作系统上正常运行：

- **Windows** ✅
- **Linux** ✅
- **macOS** ✅

## Skills 格式规范

每个 Skill 是一个 Markdown 文件，包含：

1. **触发词**：如 `/deploy`、`/review`
2. **系统提示注入**：告诉 AI 当前任务的上下文
3. **工具定义**：可选，定义具体的工具函数
4. **执行逻辑**：可选，描述步骤顺序

> 注意：具体格式规范以 [Skills SDK 官方文档](https://www.skills.sh/) 为准，本 bundle 仅基于博文内容描述。

## 主题关联

- [00-intro](./00-intro.md)：项目概述与背景
- [02-ecosystem](./02-ecosystem.md)：生态格局与竞争分析
