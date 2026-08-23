---
type: Example
title: "使用内置工具"
description: "让 AI 使用命令执行、浏览器获取、Web搜索等内置工具完成复杂任务"
tags: [jupyterlite-ai, tools, execute-command, browser-fetch, web-search, approval]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-04-21T00:00:00+08:00" }
status: stable
stale_after: 2026-10-21
sources:
  - id: source
    resource: /references/source-code.md
    title: 源码结构与核心文件索引
  - id: tools
    resource: /references/built-in-tools.md
    title: 内置 AI 工具参考
---

# 使用内置工具

JupyterLite AI 内置了多种工具，AI 可以自主决定何时调用这些工具来完成任务。本指南介绍各内置工具的用途和使用方式。

## 工具审批机制

出于安全考虑，某些工具在执行前需要用户批准：

- **需要审批（destructive）**：`execute_command` — 执行系统命令可能影响文件和环境
- **无需审批**：`browser_fetch`、`web_search`、`web_fetch`、`discover_commands`、Notebook 操作工具

当 AI 调用需要审批的工具时，聊天面板会显示确认对话框：
- ✅ **Approve**：批准执行
- ❌ **Deny**：拒绝执行
- 🔄 **Approve always**：始终自动批准（本次会话内）

## 可用内置工具

### 1. discover_commands — 发现可用命令

**无需审批**

AI 使用此工具发现 JupyterLab 中可用的命令列表，了解可以执行什么操作。

**触发方式**：自然提问即可
```
JupyterLab 里有哪些可用的命令？
```

### 2. execute_command — 执行命令

**需要审批**

执行 JupyterLab 命令系统中的任意命令，如新建单元格、运行单元格、打开文件等。

**触发示例**：
```
帮我在当前 Notebook 中插入一个新的代码单元格
```
```
运行当前所有单元格
```
```
打开一个新的 Launcher
```

**审批提示示例**：
> AI 请求执行命令：`notebook:insert-cell-below`
> 参数：`{}`
> [Approve] [Deny] [Approve always]

### 3. browser_fetch — 获取浏览器内容

**无需审批**

在浏览器环境中获取指定 URL 的内容，用于阅读文档、查看网页等。这是 JupyterLite 环境中的网络请求工具。

**触发示例**：
```
帮我看看 https://jupyterlite.readthedocs.io 的首页内容
```
```
读取这个文件的内容：https://raw.githubusercontent.com/.../example.py
```

> 💡 此工具在浏览器中运行，受浏览器 CORS 策略限制。

### 4. web_search / web_fetch — Web搜索与获取（提供商原生工具）

**无需审批**

OpenAI 和 Anthropic 提供商原生支持的网络工具：
- `web_search`：搜索网络获取最新信息
- `web_fetch`：获取指定 URL 内容

**触发示例**：
```
搜索一下 Python 3.13 有什么新特性
```
```
帮我查一下最新的 pandas 版本和更新内容
```

> ⚠️ 这两个工具仅在使用 OpenAI 或 Anthropic 提供商时可用。Google 和 Mistral 提供商不提供内置 web 工具。

## 工具使用最佳实践

### 明确表达意图

直接告诉 AI 你想要什么结果，而不是指定具体工具：

| ❌ 不推荐 | ✅ 推荐 |
|----------|---------|
| "帮我调用 execute_command 运行所有单元格" | "帮我运行这个 Notebook 里的所有代码" |
| "用 browser_fetch 获取这个 URL" | "帮我看看这个网页的内容：https://..." |

AI 会自动选择合适的工具组合来完成任务。

### 利用工具链组合

AI 可以串联多个工具完成复杂任务：

```
1. 搜索 NumPy 最新文档 → web_search
2. 获取文档页面内容 → web_fetch/browser_fetch
3. 发现可用命令 → discover_commands
4. 在 Notebook 中插入示例代码 → execute_command
```

**示例提问**：
```
帮我搜索 NumPy 的最新线性代数函数，然后在 Notebook 里写一个使用示例并运行它
```

### 安全使用 execute_command

对于命令执行工具：

1. **首次使用建议逐条审批**，了解 AI 调用了哪些命令
2. 熟悉后可使用 **Approve always** 提高效率
3. 执行前注意查看命令参数，避免误操作

## 工具使用限制

| 工具 | JupyterLab 环境 | JupyterLite 环境 | 说明 |
|------|----------------|-----------------|------|
| execute_command | ✅ 完全支持 | ⚠️ 有限支持 | JupyterLite 中部分命令不可用 |
| browser_fetch | ✅ 支持 | ✅ 完全支持 | 浏览器环境原生支持 |
| web_search | ✅ OpenAI/Anthropic | ✅ OpenAI/Anthropic | 需要提供商支持 |
| web_fetch | ✅ OpenAI/Anthropic | ✅ OpenAI/Anthropic | 需要提供商支持 |
| MCP工具 | ✅ 支持 | ✅ 支持 | 需配置 MCP 服务器 |

## 实战练习

**练习1：让 AI 帮你查找文档并写入 Notebook**
```
搜索一下 Python dataclasses 的用法，然后在我的 Notebook 里插入一个使用 dataclass 的完整示例代码
```

**练习2：让 AI 帮你操作 Notebook**
```
帮我在当前单元格下面插入一个 Markdown 单元格，标题是"数据分析结果"
```

**练习3：让 AI 获取网络内容并分析**
```
请帮我获取 https://raw.githubusercontent.com/jupyterlite/ai/main/README.md 的内容并总结核心功能
```
