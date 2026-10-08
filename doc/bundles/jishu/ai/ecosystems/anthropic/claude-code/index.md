---
okf_version: "0.2"
type: index
title: "Claude Code Wiki"
description: "Anthropic Claude Code 终端AI编码工具中文文档——安装使用、插件体系、13个官方插件索引、命令/Agents/Skills/Hooks扩展机制。"
tags: [claude-code, cli, coding-agent, plugin, terminal, ide]
generated: { by: "process:content-structuring", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
---

# Claude Code Wiki

**Claude Code** 是 Anthropic 推出的**终端 AI 编码工具**（agentic coding tool），基于 Node.js 18+ 运行。它能够理解代码库上下文、执行常规开发任务、解释复杂代码逻辑、自动化 Git 工作流，通过自然语言命令直接在终端中与开发者协作。

Claude Code 提供三种使用模式：终端交互式 CLI、IDE 集成（VS Code 等）、GitHub 中通过 `@claude` 提及使用。

## 快速开始

### 安装

**Mac/Linux（curl 脚本）：**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Mac（Homebrew）：**
```bash
brew install claude-code
```

**Windows（PowerShell 脚本）：**
```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows（WinGet）：**
```powershell
winget install Anthropic.ClaudeCode
```

> 注意：NPM 安装方式已废弃，推荐使用上述官方安装方式。

### 启动使用

```bash
# 进入项目目录
cd your-project

# 启动 Claude Code
claude
```

启动后即可在终端中与 Claude 对话，询问代码、执行重构、生成提交信息等。

## 文档导航

### 📚 概念文档

| 主题 | 说明 |
|------|------|
| [Claude Code 概览](concepts/00-overview.md) | 产品定位、核心能力、安装方式、使用模式、隐私政策 |
| [插件体系](concepts/01-plugin-system.md) | 插件结构、Commands/Agents/Skills/Hooks 四大扩展点详解 |

### 💡 示例文档

| 示例 | 说明 |
|------|------|
| [基本使用示例](examples/basic-usage.md) | 安装、启动、基础对话、任务执行、Git 工作流、插件安装、常用命令速查 |

### 📖 参考文档

| 参考 | 说明 |
|------|------|
| [官方插件索引](references/plugins-index.md) | 13 个官方插件完整清单，按类别分组（开发工作流/安全质量/学习风格/开发工具） |

## 核心能力

| 能力域 | 说明 |
|--------|------|
| 代码库理解 | 自动索引项目结构、理解代码上下文、跨文件引用追踪 |
| 常规任务执行 | 重构代码、修复 bug、编写测试、生成文档等常规开发任务 |
| 复杂代码解释 | 分析并解释晦涩的代码逻辑、架构设计、算法实现 |
| Git 工作流 | 自动生成提交信息、创建 PR、分支管理等 Git 操作自动化 |
| 自然语言命令 | 用自然语言描述需求，Claude Code 自动执行对应的终端操作 |
| 插件扩展 | 通过插件体系扩展 Commands、Agents、Skills、Hooks、MCP servers |

## 更新日志

完整变更记录见 [log.md](log.md)。

```{toctree}
:maxdepth: 3

concepts/index
examples/index
references/index
log
```
