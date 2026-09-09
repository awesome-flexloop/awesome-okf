---
type: concept
title: "IPC 通道契约体系"
description: "preload 按命名空间分组的 30+ IPC 通道、cowork:stream 流式推送事件族、IM 平台参数化通道模式，以及 as const 常量对象契约规范。"
tags: [lobsterai, electron, ipc, preload, contract, streaming]
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

# IPC 通道契约体系

在 [/concepts/00-overall-architecture.md](00-overall-architecture.md) 所述的分工下，渲染进程与主进程唯一的通信手段是 IPC。LobsterAI 的 IPC 设计有三个值得学习的特征：**命名空间分组**、**`as const` 常量对象契约**、**流式推送事件族**。

## 一、preload：白名单式 API 门面

`src/main/preload.ts` 以 `ipcRenderer.invoke`（请求/响应）与 `ipcRenderer.on`（订阅推送）暴露全部 IPC 通道，按命名空间分组为 30+ 组（F-la-037）：

| 命名空间 | 代表通道 | 职责 |
|---|---|---|
| `skills:*` | `skills:list`、`skills:download` | 技能管理（见 [/concepts/09-skill-system.md](09-skill-system.md)） |
| `kits:*` | `kits:install`、`kits:listInstalled` | 套件市场安装 |
| `enterprise:*` | `enterprise:getConfig` | 企业配置 |
| `api:fetch` / `api:stream` / `api:stream:cancel` | — | 主进程代发的网络请求与流 |
| `window-*` / `window:*` | `window-minimize`、`window:isMaximized` | 无边框窗口控制 |
| `store:*` | `store:get`、`store:set`、`store:remove` | 键值配置 |
| `cowork:session:*` | `cowork:session:start`、`cowork:session:fork` | 会话生命周期 |
| `cowork:config:*` / `cowork:memory:*` / `cowork:dreaming:*` | `cowork:config:get` 等 | 配置、记忆与"梦境" |
| `cowork:stream:*` | 9 个推送事件（见下节） | Agent 流式输出 |
| `dialog:*` / `artifact:*` / `app:*` | `dialog:selectFile` 等 | 系统对话框与制品 |
| `plugins:*` | `plugins:install`、`plugins:sync` | OpenClaw 插件管理 |
| `log:*` | `log:getPath`、`log:exportZip` | 日志 |
| `im:*` | `im:gateway:start`、`im:status:get` | IM 网关（见 [/concepts/08-im-gateway.md](08-im-gateway.md)） |
| `media:*` / `feishu:install:*` / `dingtalk:install:*` | — | 媒体与 IM 安装流程 |
| `github-copilot:*` / `openai-codex-oauth:*` / `xai-oauth:*` | 设备码/轮询/登出 | OAuth 接入 |
| `network:status-change` | — | 网络状态推送 |

preload 门面与 [/concepts/01-main-window-security.md](01-main-window-security.md) 的安全基线互为表里：`nodeIntegration: false` + `contextIsolation: true` 保证渲染层只能通过 preload 暴露的对象访问 IPC，无法自行 `require('electron')`。

## 二、cowork:stream 流式推送事件族

Agent 的流式输出不是一次性响应，而是 9 个推送事件（F-la-038）：

| 事件 | 含义 |
|---|---|
| `cowork:stream:message` | 新消息到达 |
| `cowork:stream:messageUpdate` | 消息内容增量更新（流式 token） |
| `cowork:stream:sessionStatus` | 会话状态变化 |
| `cowork:stream:contextUsage` | 上下文用量上报 |
| `cowork:stream:contextMaintenance` | 上下文维护（压缩等） |
| `cowork:stream:permission` | 权限请求（需用户审批） |
| `cowork:stream:permissionDismiss` | 权限请求撤销 |
| `cowork:stream:complete` | turn 完成 |
| `cowork:stream:error` | 错误 |

设计要点：**消息创建与消息更新分离**（`message` / `messageUpdate`）——渲染层可先占位再增量渲染，避免长 turn 期间整段重绘；权限请求独立成对事件（`permission`/`permissionDismiss`），与数据面事件解耦。

## 三、IM 平台参数化通道模式

IM 实例管理通道按平台参数化（F-la-039）：

```
im:{platform}:instance:add
im:{platform}:instance:delete
im:{platform}:instance:config:set
```

`{platform}` 覆盖 telegram、discord、feishu、dingtalk、wecom、weixin、nim、qq、email 九个平台；另有平台无关的配对审批通道 `im:pairing:list` / `im:pairing:approve` / `im:pairing:reject`。把平台作为通道参数而非通道名的一部分（如 `im:telegram:instance:add`），使九平台共享同一处理器签名，新增平台时无需改动渲染层调用代码。

OAuth 与安装流程通道同样成组设计（F-la-040）：`github-copilot:request-device-code`/`poll-for-token`/`cancel-polling`/`sign-out`/`refresh-token`/`token-updated`，`openai-codex-oauth:start`/`cancel`/`logout`/`status`，`xai-oauth:start`/`cancel`/`logout`/`status`/`device-code`，以及 `feishu:install:qrcode`/`poll`/`verify` 与 `dingtalk:install:qrcode`/`poll`/`verify`——每个第三方接入都是"启动 → 轮询 → 确认/取消 → 登出 → 状态"的完整生命周期通道组。

## 四、as const 常量对象契约

项目 AGENTS.md 规定 IPC 通道必须使用 `as const` 常量对象声明（F-la-008），源码中有两个典范：

**`CoworkIpcChannel`**（`src/shared/cowork/constants.ts`，F-la-055）：

```ts
export const CoworkIpcChannel = {
  CancelMediaTask: 'cowork:media:cancel',
  ForkSession: 'cowork:session:fork',
  SubmitBtw: 'cowork:session:submitBtw',
  AbortBtw: 'cowork:session:abortBtw',
  SubmitSteer: 'cowork:session:submitSteer',
  GoalCommand: 'cowork:session:goalCommand',
  StreamBtwResult: 'cowork:stream:btwResult',
  MemoryReadRaw: 'cowork:memory:readRaw',
  // ...
} as const;
```

**`IpcChannel`**（`src/scheduledTask/constants.ts`，F-la-063）：以 `scheduledTask:` 为前缀，键含 `list`、`get`、`create`、`update`、`delete`、`toggle`、`runManually`、`stop`、`listRuns`、`countRuns`、`listAllRuns`、`resolveSession`、`listChannels`、`listChannelConversations`、`statusUpdate`、`runUpdate`、`refresh`。

常量对象 + `as const` 的双重收益：主进程注册 `ipcMain.handle(channel, ...)` 与 preload 调用 `ipcRenderer.invoke(channel, ...)` 引用同一键，**字符串通道名只书写一次**，杜绝手写字符串散落各处导致的拼写漂移；同时键名（PascalCase 语义键）与值（kebab 通道名）分离，重构通道名时类型系统全量跟进。

## 设计启示

1. 通道命名采用 `域:子域:动作` 三段式（`cowork:session:fork`），词法上自带分组；
2. 请求/响应用 `invoke`，服务端主动推送用 `on`，两者在同一命名空间内并存但事件以过去分词/名词区分（`statusUpdate` vs `get`）；
3. 平台类通道优先参数化（`im:{platform}:*`），生命周期类通道按"启动-轮询-取消-登出-状态"五件套成组设计。

## 相关概念

- [/concepts/00-overall-architecture.md](00-overall-architecture.md)
- [/concepts/05-human-collab-protocols.md](05-human-collab-protocols.md)
- [/concepts/10-scheduled-tasks.md](10-scheduled-tasks.md)
