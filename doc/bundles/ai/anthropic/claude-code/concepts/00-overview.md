---
type: concept
title: "Claude Code 概览"
tags: [claude-code, overview, installation, getting-started]
---

# Claude Code 概览

Claude Code 是 Anthropic 推出的**终端 AI 编码工具**（agentic coding tool），基于 Node.js 18+ 运行。它直接在终端环境中工作，能够理解代码库上下文、执行终端命令、读写文件，并通过自然语言交互辅助开发者完成各类编码任务。

## 产品定位

Claude Code 不是一个简单的代码补全工具，而是一个**具备执行能力的 AI 代理**（AI Agent）。它可以：

- 直接访问你的本地文件系统
- 执行终端命令（需用户确认）
- 理解整个代码库的结构和上下文
- 自主规划并完成多步骤开发任务
- 与 Git 等版本控制系统深度集成

## 核心能力

### 代码库理解

Claude Code 启动后会自动索引当前项目的文件结构，建立代码上下文理解：

- 识别项目的编程语言、框架、构建工具
- 理解跨文件的函数调用、类继承、模块依赖关系
- 读取配置文件、文档、测试用例等辅助信息
- 基于代码库上下文回答问题，而非孤立地看单个文件

### 常规任务执行

可以直接通过自然语言委派各类开发任务：

- 「重构这个函数，提取重复逻辑为独立方法」
- 「为这个模块编写单元测试」
- 「修复这个类型错误」
- 「更新依赖版本并解决兼容性问题」
- 「根据 README 生成 API 文档」

Claude Code 会自主制定执行计划，逐步完成任务，并在关键操作前请求确认。

### 复杂代码解释

对于接手陌生代码库或理解复杂逻辑非常有用：

- 「解释这个模块的整体架构」
- 「这段正则表达式在做什么？」
- 「追踪这个请求从入口到响应的完整调用链」
- 「这个算法的时间复杂度是多少？有没有优化空间？」

### Git 工作流自动化

与 Git 深度集成，简化版本控制操作：

- 自动分析变更并生成符合 Conventional Commits 规范的提交信息
- 一键完成 add → commit → push → PR 创建全流程
- 清理已合并分支、查看工作区状态
- 代码审查辅助

### 自然语言命令

无需记忆复杂的 CLI 语法，用自然语言描述需求即可：

- 「运行测试并报告失败用例」
- 「启动开发服务器」
- 「查找所有包含 TODO 注释的文件」
- 「对比这两个分支的差异并总结」

## 安装方式

### 环境要求

- **Node.js**：18.0 或更高版本
- **操作系统**：macOS、Linux、Windows（支持 PowerShell 和 WinGet）

> ⚠️ **注意**：NPM 全局安装方式（`npm install -g @anthropic-ai/claude-code`）已废弃，请使用以下官方推荐的安装方式。

### Mac/Linux（curl 脚本）

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

### Mac（Homebrew）

```bash
brew install claude-code
```

### Windows（PowerShell 脚本）

```powershell
# 以管理员权限运行 PowerShell
irm https://claude.ai/install.ps1 | iex
```

### Windows（WinGet）

```powershell
winget install Anthropic.ClaudeCode
```

### 验证安装

安装完成后，验证安装是否成功：

```bash
claude --version
```

## 快速开始

```bash
# 1. 进入你的项目目录
cd your-project-directory

# 2. 启动 Claude Code
claude
```

首次启动会要求你登录 Anthropic 账号进行认证。认证完成后即可在终端中与 Claude 对话。

## 使用模式

Claude Code 支持三种主要使用方式：

### 1. 终端交互式 CLI（默认）

最常用的方式，直接在终端中启动交互式会话：

```bash
claude
```

进入 REPL 环境后，可以直接输入自然语言指令，Claude Code 会在终端中响应并执行操作。

### 2. IDE 集成

支持与 VS Code 等主流 IDE 集成，在编辑器中直接调用 Claude Code 的能力，保持开发流程不中断。

### 3. GitHub @claude

在 GitHub 的 Issue、PR、Discussion 中通过 `@claude` 提及，可以让 Claude Code 参与代码审查、回答问题、执行 PR 检查等。

## 数据收集与隐私

Claude Code 的数据处理遵循 Anthropic 的隐私政策：

- **代码上下文**：为了理解项目，Claude Code 会将相关代码片段发送到 Anthropic 服务器
- **用户对话**：对话内容会被处理以生成响应
- **可选数据收集**：默认情况下 Anthropic 可能收集使用数据用于改进服务，可以在设置中选择退出
- **企业版**：提供数据不驻留、零数据保留等企业级隐私选项

建议在处理敏感代码前 review Anthropic 的最新隐私政策和企业版选项。

## 与其他 Anthropic 产品的关系

| 产品 | 定位 | 关系 |
|------|------|------|
| **Claude Code** | 终端编码代理工具 | 终端原生，具备文件/命令执行能力 |
| **Claude API** | REST API 服务 | Claude Code 底层调用 Claude 模型（如 Sonnet、Opus） |
| **Claude Python SDK** | API 客户端库 | 用于在 Python 代码中调用 Claude API，是编程接口而非终端工具 |
| **Claude.ai 网页版** | Web 聊天界面 | 通用对话，不具备本地代码库访问和终端执行能力 |

简单来说：Claude Code 是面向开发者的终端工具，它在底层使用 Claude API 的模型能力，但针对编码场景做了专门优化，增加了文件系统访问、命令执行、代码库索引等代理能力。

## 相关资源

- [插件体系](/claude-code/concepts/01-plugin-system.md) — 了解如何通过插件扩展 Claude Code
- [基本使用示例](/claude-code/examples/basic-usage.md) — 安装后的常用操作示例
- [官方插件索引](/claude-code/references/plugins-index.md) — 13 个官方插件完整清单
