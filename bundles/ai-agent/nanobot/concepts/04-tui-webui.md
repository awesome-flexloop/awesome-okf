---
type: concept
title: TUI 与 WebUI 架构
description: TypeScript TUI、React WebUI 与 tui_launcher 的架构概览，以及 gateway 按需启动的协作方式
tags: [nanobot, tui, webui, react, bun, gateway]
sources:
  - resource: "/references/agent-api.md"
    title: "Nanobot SDK 门面 API"
  - resource: "/references/bus-sdk-api.md"
    title: "MessageBus 与 SDK 类型 API"
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# TUI 与 WebUI 架构

nanobot 把终端界面与浏览器界面都做成独立前端，Python 核心只负责拉起它们并提供一个共享的 gateway。本节做架构概览，重点在前后端如何协作，不深入单个前端组件的实现。

## TypeScript TUI（tui/）

`tui/` 是一个基于 Bun 的 TypeScript 原生终端界面（F-051）：

- 包名 `@nanobot/tui`，`version "0.1.0"`，`type "module"`。
- scripts：`start: "bun src/index.ts"`、`build: "bun scripts/build.ts"`、`test: "bun test"`。
- 依赖 `@opentui/core@0.5.3`，开发依赖 `typescript`、`@types/bun`。
- `src/` 下按功能拆分模块：`app.ts`、`protocol.ts`、`host.ts`、`transcript.ts`、`composer-draft.ts`、`tool-renderers.ts`、`diff-viewer.ts`、`session-menu.ts`、`branch-menu.ts`、`command-menu.ts` 等，并配有同名的 `*.test.ts`。

TUI 通过环境变量与 Python 侧传递启动参数，包括 `NANOBOT_TUI_BOOTSTRAP_URL`、`NANOBOT_TUI_API_URL`、`NANOBOT_TUI_MODEL`、`NANOBOT_TUI_MODEL_PRESET`、`NANOBOT_TUI_WORKSPACE`、`NANOBOT_TUI_VERSION`、`NANOBOT_TUI_THEME` 等（F-054）。

## React WebUI（webui/）

`webui/` 是 Vite 构建的 React 18 单页应用（F-052）：

- 包名 `nanobot-webui`，`version "0.1.0"`。
- scripts：`dev: "vite"`、`build: "tsc -p tsconfig.build.json && vite build"`、`test: "vitest run"`。
- 依赖 `react`/`react-dom` 18、`vite` 5、Tailwind、Radix UI、`react-syntax-highlighter`、`streamdown`、`i18next`（多语言，含 `zh-CN`/`zh-TW`）等。
- 源码按 `components/`（settings、thread、workbench、ui）、`hooks/`、`lib/`、`i18n/`、`providers/`、`workers/` 组织，构建产物打进 Python wheel（构建输出 `../nanobot/web/dist`）。

WebUI 通过 gateway 暴露的 WebSocket 多路复用协议与 agent 通信，dev server 会把 `/api`、`/webui`、`/auth` 与 WebSocket 流量代理到 gateway（AGENTS.md 架构说明）。

## tui_launcher：拉起源头与按需 gateway

`nanobot/cli/tui_launcher.py` 负责把 Python CLI 与 TypeScript TUI 桥接起来（F-053）：

- 定义 `TuiUnavailableError(RuntimeError)`、`TuiSessionError(ValueError)` 两类异常，以及 `launch_tui(config, *, config_path, workspace_override, session_id, theme) -> int`。
- `_TUI_DETACH_EXIT_CODE = 90`：TUI 退出码 90 表示"分离并常驻"，`launch_tui` 据此把 gateway lease 标记为 persistent（F-053）。

`_resolve_tui_command()` 依次尝试三种来源（F-055）：`NANOBOT_TUI_BIN` 环境变量覆盖、源码 checkout（要求 Bun，失败则报需装 Bun）、打包的 `tui/bin/<asset>`（`nanobot-tui-{system}-{machine}[.exe]`），最后下载版本匹配、经 sha256 校验的 release 归档。

而 `_ensure_gateway(...)` 通过 `GatewayInstance.resolve` + `GatewayRuntime` + `GatewayClientLease`（kind 为 `"tui"` 或 `"webui"`）启动或复用按需共享的 gateway（F-047、F-053 相关）。

## gateway 协作模型

交互式 WebUI 与 TUI 启动器共享同一个按需 gateway：关闭一个启动器不会停掉别人还在用的 gateway，最后一个启动器退出时才停止它；需要常驻后台时改用 `nanobot gateway --background`（docs/quick-start.md）。

## 相关概念

- [Nanobot 项目概览](/concepts/00-overview.md)
- [CLI 与 SDK](/concepts/03-cli-sdk.md)
- [Nanobot SDK 门面 API](/references/agent-api.md)