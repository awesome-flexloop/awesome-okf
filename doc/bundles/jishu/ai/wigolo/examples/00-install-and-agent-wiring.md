---
okf_version: "0.2"
type: Example
title: "安装 wigolo 并接入 AI 编程 Agent"
description: "Node ≥20 前置检查、init 初始化（1.5GB 下载）、9 类 Agent 一键接线、doctor 体检、verify 冒烟与干净卸载的可照做流程"
tags: [wigolo, install, claude-code, cursor, mcp, doctor]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-09-16T21:10:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/IXBNcf2zJI6Bja7gVGOy9w
  - id: official-readme
    url: https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/README.md
  - id: official-installation
    url: https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/docs/installation.md
  - id: official-cli
    url: https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/docs/cli.md
---

# 示例 00：安装 wigolo 并接入 AI 编程 Agent

> 可复现流程。命令以官方 README / installation.md / cli.md 为准（F-038/F-039/F-054），博文命令（F-015~F-018）经逐字核验。

## 前置条件

- **Node.js ≥ 20**（F-015/F-038）。检查：

```bash
node --version    # 需要 v20 以上；官方支持 macOS / Linux / Windows
```

- 约 **1.5 GB 可用磁盘**：初始化会下载浏览器引擎与本地模型（F-016/F-038）。
- 不需要预先注册任何账号、不需要 API Key（核心功能）。

## 第一步：初始化并接入 Agent

博文给出的单 Agent 接法（F-016）：

```bash
npx wigolo init --agents=claude-code
```

官方支持一次接入多个客户端（逗号分隔，F-038）：

```bash
npx wigolo init --agents=claude-code,cursor
```

`--agents` 的 9 个官方目标（F-039，博文列出其中 7 个，另有 OpenCode 与 Antigravity）：

| id | 客户端 | id | 客户端 |
|----|--------|----|--------|
| `claude-code` | Claude Code | `vscode` | VS Code |
| `cursor` | Cursor | `windsurf` | Windsurf |
| `codex` | Codex | `zed` | Zed |
| `gemini-cli` | Gemini CLI | `opencode` | OpenCode |
| `antigravity` | Antigravity | | |

init 会写入各客户端的 MCP 配置（支持时附带使用说明），下载浏览器引擎与端侧模型，逐组件输出报告；某个组件下载失败不会让整体安装失败，报告会指出具体修复方法（F-038）。

**可选开关**：
- `--no-warmup`：延迟到首次使用再下载模型/引擎；
- `--interactive`（纯文本问答）/ `--wizard`（终端 TUI）；
- 只想准备引擎、暂不接线：裸 `npx wigolo init`。

其他 MCP 客户端（如 Cline）不在 `--agents` 列表，手工登记 stdio 配置即可（F-039）：

```json
{
  "mcpServers": {
    "wigolo": { "command": "npx", "args": ["-y", "wigolo"] }
  }
}
```

## 第二步：体检

```bash
npx wigolo doctor
```

逐项检查数据目录可写性、浏览器引擎、抓取分层、端侧模型、LLM provider 状态、搜索后端、各引擎健康度、缓存统计等；博文所说"显示全绿即就绪"即此步（F-018）。发现已知故障可加 `--fix` 自动修复（F-054）。

需要真实联网验证端到端能力时：

```bash
npx wigolo verify     # 真实网络调用的冒烟检查，全过 exit 0
```

## 第三步：在 Agent 中使用

打开 Claude Code（或已接线的客户端），直接提一个需要实时信息的问题，例如博文示例（F-018）：

> 帮我搜一下 React 19 的最新特性

Agent 会经 MCP 调用 wigolo 搜索，并在回答中带来源引用（citation_id，见 [概念 01](../concepts/01-ten-tools-and-evidence-model.md)）。

## 干净卸载

```bash
npx wigolo uninstall            # 移除 MCP 配置、instructions、skills、slash command
```

注意：卸载命令**刻意保留 `~/.wigolo`**（缓存/模型/密钥）。要连数据一起删除（F-054）：

```bash
rm -rf ~/.wigolo               # macOS/Linux；Windows 手动删除 %USERPROFILE%\.wigolo
```

## 排障速查

| 现象 | 处理 |
|------|------|
| init 下载某个组件失败 | init 不整体失败，按报告提示修复后跑 `npx wigolo warmup` 重下（F-038/F-054） |
| doctor 报 LLM provider 未配置 | 不影响搜索/抓取等 6 个免 Key 工具；需要成稿功能再按 [示例 02](02-rest-docker-and-llm.md) 配置 |
| Agent 中调用无反应 | 确认客户端 MCP 配置已写入；用 `npx wigolo status` 查看连接的 Agent（F-054） |

## 下一步

- [示例 01：CLI 搜索与缓存技巧](01-cli-search-and-cache.md)
- [示例 02：REST API、Docker 与 LLM 配置](02-rest-docker-and-llm.md)
