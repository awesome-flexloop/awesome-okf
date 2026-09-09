---
type: concept
title: "MCP 集成与桥接运行时"
description: "MCP 服务器 CRUD 与存储、launch resolution（来源指纹/npx 判定）、McpRuntime 运行时职责，以及 AskUser/媒体生成/浏览器工具三类桥接工具协议。"
tags: [lobsterai, mcp, modelcontextprotocol, bridge, askuser]
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

# MCP 集成与桥接运行时

LobsterAI 通过 `@modelcontextprotocol/sdk`（F-la-004）接入 Model Context Protocol（MCP），把外部工具服务器纳入 Agent 的工具面。整套集成由**存储层（McpStore）→ 解析层（mcpLaunchResolution）→ 运行时（McpRuntime + McpBridgeServer）**三级构成，全部驻留主进程（[/concepts/00-overall-architecture.md](00-overall-architecture.md)）。

## 一、McpStore：服务器配置 CRUD

`McpStore`（`src/main/mcp/mcpStore.ts`）提供 MCP 服务器的完整 CRUD（F-la-029）：

- 服务器管理：`listServers`、`getServer`、`createServer`、`updateServer`、`deleteServer`、`setEnabled`、`getEnabledServers`；
- launch resolution 读写（与解析层配合）；
- 配套接口 `McpServerRecord`（持久化形态）与 `McpServerFormData`（表单提交形态），存储记录与表单数据分离，使 UI 层演进不影响存储 schema。

数据落库在 `mcp_servers` 与 `mcp_launch_resolutions` 两张表（F-la-016，见 [/concepts/03-sqlite-local-storage.md](03-sqlite-local-storage.md)）。

## 二、mcpLaunchResolution：启动解析

MCP 服务器"如何被启动"需要解析与缓存，`mcpLaunchResolution.ts` 导出（F-la-030）：

- 常量对象 `McpLaunchResolverKind` 与 `McpLaunchResolutionStatus`；
- 接口 `McpLaunchResolution`；
- 工具函数：
  - `createMcpLaunchSourceFingerprint(server)`——由服务器配置生成**来源指纹**，配置变化即指纹变化，是缓存失效的判定依据；
  - `normalizeMcpCommand(command?)`——启动命令规范化；
  - `isNpxMcpServer(server)`——判定服务器是否经 npx 启动。

教学要点：launch resolution 把"服务器配置 → 可执行启动方式"的解析结果显式持久化（独立表），并以来源指纹关联缓存——配置没变就复用解析结果，变了则重解析。这是"昂贵解析结果缓存"的标准三件套：**解析记录 + 指纹 + 状态枚举**。

## 三、McpRuntime：运行时中枢

`McpRuntime`（`src/main/mcp/mcpRuntime.ts`）的方法面揭示其职责（F-la-031）：

| 方法 | 职责域 |
|---|---|
| `getStore` / `getLaunchResolverManager` | 依赖访问 |
| `ensureLaunchResolution` / `refreshResolvedServersCache` / `getResolvedServersCache` | 解析缓存的确保与刷新 |
| `startAskUserServer` / `askUserInternal` / `resolveAskUser` / `getAskUserCallbackUrl` | AskUser 桥接服务器的生命周期 |
| `setMediaGenerationHandler` / `setBrowserToolHandler` | 注册媒体生成与浏览器工具处理器 |
| `getBridgeSecret` | 桥接通信的密钥 |
| `broadcastServersChanged` | 服务器变更事件广播 |

配套 `McpRuntimeDeps` 接口以依赖注入方式组装。两类桥接处理器（媒体生成、浏览器工具）以 setter 注入而非构造注入，允许在运行时就绪后再挂载——与主进程的初始化顺序解耦。

## 四、McpBridgeServer：三类桥接工具协议

`mcpBridgeServer.ts` 导出 `McpBridgeServer` 类与三组请求/响应类型（F-la-032）：

| 请求类型 | 响应类型 | 桥接方向 |
|---|---|---|
| `AskUserRequest` | `AskUserResponse` | Agent → 用户（提问并等待回答） |
| `MediaGenerationRequest` | `MediaGenerationResponse` | Agent → 媒体生成服务 |
| `BrowserToolRequest` | `BrowserToolResponse` | Agent → 内嵌浏览器工具 |

桥接的本质：Agent 运行时（OpenClaw）发出的工具调用经桥接服务器转译为应用内能力。AskUser 是最典型的一类——Agent 执行中需要向用户提问，请求经桥接抵达渲染层，以 `cowork:stream:permission` 事件呈现（见 [/concepts/02-ipc-channel-contracts.md](02-ipc-channel-contracts.md)），回答后经 `resolveAskUser` 回送。其会话无关性由共享层常量保证：`SESSION_AGNOSTIC_PERMISSION_SESSION_ID = '__askuser__'` 与 `ASK_USER_QUESTION_TOOL_NAME = 'AskUserQuestion'`（F-la-053，见 [/concepts/05-human-collab-protocols.md](05-human-collab-protocols.md)）。

## 设计启示

1. 集成外部协议时分三层：**配置存储 / 解析缓存 / 运行时桥接**，每层单一职责、依赖向下；
2. 昂贵解析用「来源指纹 + 状态枚举 + 独立表」三件套管理缓存失效；
3. 桥接工具按"请求/响应类型对"显式建模，新增一类桥接即新增一对类型 + 一个 setter 注入点，不动既有协议。

## 相关概念

- [/concepts/02-ipc-channel-contracts.md](02-ipc-channel-contracts.md)
- [/concepts/03-sqlite-local-storage.md](03-sqlite-local-storage.md)
- [/concepts/05-human-collab-protocols.md](05-human-collab-protocols.md)
