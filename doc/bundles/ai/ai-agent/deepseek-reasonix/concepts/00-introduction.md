---
type: Concept
title: Reasonix 简介
description: DeepSeek 开源的 Go 语言 AI 编码 Agent，支持 ACP 协议、桌面应用、Bot 网关，单二进制部署
tags: [deepseek-reasonix, introduction, overview, go, acp, desktop, bot]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-23T00:00:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-23T00:00:00Z
status: stable
stale_after: 2027-08-23
sources:
  - id: SRC-001
    resource: /references/source.md
    title: DeepSeek-Reasonix 源码信源索引
---

## Reasonix 是什么

Reasonix 是 DeepSeek 开源的 AI 编码 Agent，使用 Go 语言编写，以单个静态二进制文件分发。项目定位为 "a coding agent you can leave running"——一个可以长时间自主运行、仍可读取和撤销操作的编码代理。

项目采用 MIT 协议，Go module 名为 `reasonix`，要求 Go 1.25+，toolchain 固定为 go1.26.6。（F-001, F-006）

## 四种接入方式

同一个本地 Reasonix 引擎支持四种前端接入：

1. **Terminal（CLI/TUI）**——通过 npm 或 Homebrew 安装原生二进制，使用 Bubble Tea TUI 框架交互
2. **Desktop App**——基于 Wails v2 的桌面应用，支持 macOS/Windows/Linux
3. **Browser**——HTTP/SSE 服务模式
4. **Editor over ACP**——通过 Agent Client Protocol 接入 VS Code 等编辑器

四种前端共享同一个 `control.Controller` 和 `boot.BuildRuntime` 组装路径。（F-007, F-089）

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  CLI/TUI    │  │  Desktop    │  │  Browser    │  │  ACP Editor │
│  (bubbletea)│  │  (Wails)    │  │  (HTTP/SSE) │  │  (JSON-RPC) │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │                │
       └────────────────┴────────────────┴────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │ control.Controller│
                    │ (boot.BuildRuntime)│
                    └─────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
        ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
        │   Agent   │  │   Tools   │  │ Provider  │
        │ (run loop)│  │ (registry)│  │ (model)   │
        └───────────┘  └───────────┘  └───────────┘
```

## 核心特性

- **配置驱动**：Provider、Agent、工具、插件均在 `reasonix.toml` 中声明，无硬编码模型
- **多模型组合**：DeepSeek 作为预设，任何 OpenAI 兼容端点都是配置项；可选 executor + planner 双模型
- **插件扩展**：MCP 服务器贡献工具/prompt/resource；Extension Protocol v1 sidecar 可拦截运行时事件
- **缓存感知上下文维护**：启动时注入稳定环境摘要，过期工具输出在摘要压缩前裁剪
- **零摩擦分发**：`CGO_ENABLED=0` 单二进制，一条命令交叉编译到 6 个目标

（F-002, F-003, F-004）

## 技术栈

| 层面 | 技术 |
|------|------|
| 语言 | Go 1.25 |
| TUI | charm.land/bubbletea/v2 + lipgloss |
| 桌面 | Wails v2 + React/TypeScript |
| 数据库 | modernc.org/sqlite（纯 Go） |
| Shell | mvdan.cc/sh/v3 |
| 飞书 | github.com/larksuite/oapi-sdk-go/v3 |
| QQ | golang.org/x/net/websocket |
| 代码解析 | tree-sitter（JavaScript/Python/Rust/TypeScript） |

（F-002）

## 相关概念

- [项目架构](/concepts/01-project-architecture.md)——整体包结构和启动流程
- [Agent 运行循环](/concepts/02-agent-run-loop.md)——核心执行引擎
- [ACP 协议](/concepts/03-acp-protocol.md)——编辑器集成协议
- [Bot 网关](/concepts/04-bot-gateway.md)——多平台 IM 接入
