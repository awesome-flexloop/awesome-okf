---
type: concept
title: "全景与分层架构"
description: "LobsterAI 的总体定位、Cowork（产品/会话层）与 OpenClaw（唯一 Agent 运行时/网关）的职责切分，以及主进程、渲染进程、共享协议层、定时任务四区布局总览。"
tags: [lobsterai, electron, architecture, openclaw, overview]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:vendor-grep", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: LobsterAI 源码事实清单（R 阶段，基线 2026.9.4）
  - id: insights
    resource: /references/insights.md
    title: LobsterAI 架构洞察（I 阶段，基线 2026.9.4）
---

# 全景与分层架构

LobsterAI 是网易有道开源的桌面端 AI Agent 应用：package.json 中 `name` 为 `lobsterai`，版本 `2026.9.4`（F-la-001），技术栈为 Electron 40 + React 18（F-la-003），依赖 better-sqlite3、`@modelcontextprotocol/sdk`、`@reduxjs/toolkit`、有道智云 NIM SDK（`nim-web-sdk-ng`）与 zod（F-la-004）。

阅读本束其余概念文档前，建议先建立两条主线：**「产品层与运行时如何分工」**与**「代码在四区如何分布」**。

## 一、Cowork 与 OpenClaw：产品层与运行时的职责切分

项目内 AGENTS.md 明确声明了架构分工（F-la-008）：

- **Cowork 是产品/会话层**：负责窗口、视图、会话管理、人机交互协议等"产品形态"的一切。
- **OpenClaw 是唯一 Agent 运行时/网关**：所有 Agent 执行能力（LLM 调用、工具使用、技能执行、定时任务触发）都委托给 OpenClaw，应用本身不内嵌第二套运行时。README 声明其依赖 openclaw v2026.6.1 与 dsh 0.1.1-rc.1（F-la-009）。

这一分工决定了 LobsterAI 的代码组织方式：本仓库代码几乎全部是"围绕唯一运行时的产品壳"——会话的创建、渲染、打断、纠偏、记忆、定时触发都是本地代码，而真正消耗 token 的 Agent turn 一律经网关下发。

## 二、四区布局总览

```
┌────────────────────────────────────────────────────────────┐
│ 渲染进程 src/renderer/                                      │
│   App.tsx 顶层视图路由：CoworkView / KitsView /              │
│   LibraryView / ScheduledTasksView / Settings /            │
│   SkillsAndConnectorsView（F-la-041）                       │
│   store/slices/：13 个 Redux slice（21 个 .ts，F-la-042）  │
├────────────────────────────────────────────────────────────┤
│ 共享协议层 src/shared/cowork/                               │
│   btw.ts / goal.ts / rail.ts / steer.ts / constants.ts      │
│   —— 人机协作四类协议的类型契约（F-la-043~F-la-056）          │
├────────────────────────────────────────────────────────────┤
│ 主进程 src/main/ —— Agent 运行时中枢                         │
│   main.ts（主窗口，约 1.3 万行，F-la-010~F-la-014）          │
│   sqliteStore / coworkStore / agentManager（本地状态，F-la-015~023）│
│   im/（九平台 IM 网关，F-la-025~F-la-028）                  │
│   mcp/ + libs/mcpBridgeServer（MCP 运行时，F-la-029~F-la-032）│
│   skills/skillManager（技能系统，F-la-033）                  │
│   skins/（皮肤扩展面，20 个 .ts，F-la-035）                  │
│   preload.ts（IPC 通道契约，F-la-037~F-la-040）             │
├────────────────────────────────────────────────────────────┤
│ 定时任务 src/scheduledTask/                                 │
│   Renderer → Main → OpenClaw Gateway 三层架构（F-la-057）    │
└────────────────────────────────────────────────────────────┘
```

### 主进程即运行时中枢

主流 Electron 应用把主进程当作"窗口管理器"，重型逻辑放在独立后端服务中；LobsterAI 反其道而行——三类通常驻留服务端的子系统全部实现在主进程内（详见 [/concepts/08-im-gateway.md](08-im-gateway.md)、[/concepts/07-mcp-integration-runtime.md](07-mcp-integration-runtime.md)、[/concepts/09-skill-system.md](09-skill-system.md)）：

1. **多平台 IM 网关**：`IMGatewayManager` 统一管理 telegram、discord、feishu、dingtalk、wecom、weixin、nim、qq、email 九个平台的实例（F-la-028），使本地 Agent 能被各 IM 平台触达。
2. **MCP 工具运行时**：`McpStore` + `McpRuntime` + `McpBridgeServer` 负责 MCP 服务器配置、启动解析与三类桥接工具（AskUser、媒体生成、浏览器工具）的请求/响应（F-la-029~F-la-032）。
3. **技能系统**：`SkillManager` 管理 29 个内置 SKILL.md 的同步、下载、升级与自动路由（F-la-033、F-la-065）。

子系统之间以 EventEmitter 事件流而非 HTTP/RPC 连接，换来同进程直读 SQLite 的零拷贝与部署零依赖，代价是主进程单点复杂度（main.ts 中 `new BrowserWindow` 出现在约第 13470 行，F-la-010）。

### 渲染进程只做展示与交互

渲染进程不直接触碰任何运行时子系统。`App.tsx` 顶层路由包含六大视图（F-la-041），状态由 13 个 Redux slice 管理（`src/renderer/store/slices/` 共 21 个 `.ts`，含 8 个并置测试，F-la-042，如 `coworkSlice.ts`、`agentSlice.ts`、`artifactSlice.ts`）。渲染层与主进程之间以 30+ 命名空间的 IPC 通道契约通信，通道规范见 [/concepts/02-ipc-channel-contracts.md](02-ipc-channel-contracts.md)。

### 共享层：协议先于界面

`src/shared/cowork/` 把「打断提问（btw）、持续目标（goal）、会话轨道索引（rail）、流内纠偏（steer）」四种人机协作语义建模为独立的类型模块——状态枚举、限长常量、请求/响应接口全部在共享层声明（F-la-043~F-la-052），再由 `CoworkIpcChannel` 常量对象映射为 IPC 通道（F-la-055）。协作语义因此不随 UI 重构漂移，同一套协议可被 GUI、IM Bot、定时任务等多种入口复用，详见 [/concepts/05-human-collab-protocols.md](05-human-collab-protocols.md)。

### 定时任务：独立子目录的三层架构

定时任务在 `src/scheduledTask/` 中自成体系，采用 Renderer → Main → OpenClaw Gateway 三层架构（F-la-057），以 15 秒轮询与网关对账任务状态（F-la-058），详见 [/concepts/10-scheduled-tasks.md](10-scheduled-tasks.md)。

## 三、扩展面与工程化

- **OpenClaw 插件**：package.json 的 `openclaw.plugins` 列出 10 个插件（dingtalk-connector、qqbot、discord、wecom-openclaw-plugin、clawemail-email 等），其中 moltbot-popo 与 openclaw-nim-channel 标记 `"optional": true`（F-la-006）。
- **皮肤系统**：`src/main/skins/` 共 20 个 `.ts` 文件，含 12 个实现文件与 8 个并置测试文件（F-la-035、F-la-074）。
- **测试工程**：vitest 双 include（`src/**/*.test.ts` 与 `tests/**/*.test.ts`）、node 环境、20 秒超时；`tests/` 目录共 38 个测试文件，含 sqlite-backup 与 openclaw-extensions 两个子目录（F-la-070、F-la-072、F-la-073）。

## 阅读路线

| 顺序 | 文档 | 主题 |
|---|---|---|
| 01 | [/concepts/01-main-window-security.md](01-main-window-security.md) | 主窗口模型与安全基线 |
| 02 | [/concepts/02-ipc-channel-contracts.md](02-ipc-channel-contracts.md) | IPC 通道契约体系 |
| 03 | [/concepts/03-sqlite-local-storage.md](03-sqlite-local-storage.md) | SQLite 本地优先存储层 |
| 05 | [/concepts/05-human-collab-protocols.md](05-human-collab-protocols.md) | 人机协作四类协议 |
| 07 | [/concepts/07-mcp-integration-runtime.md](07-mcp-integration-runtime.md) | MCP 集成与桥接运行时 |
| 09 | [/concepts/09-skill-system.md](09-skill-system.md) | 技能系统与注册机制 |
| 10 | [/concepts/10-scheduled-tasks.md](10-scheduled-tasks.md) | 定时任务子系统 |
