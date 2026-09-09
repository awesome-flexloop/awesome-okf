---
type: example
title: "通过 IPC 通道查询会话消息"
description: "渲染层经 cowork:session:* 通道分页拉取会话列表与消息历史、订阅 cowork:stream:* 流式事件、以 CoworkStore 方法面理解主进程侧数据出口的完整演练。"
tags: [lobsterai, ipc, session, message, pagination, example]
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

# 通过 IPC 通道查询会话消息

本演练演示渲染进程（受 `contextIsolation` 约束，无 Node 能力）如何经 preload 门面读取会话与消息（概念背景见 [/concepts/02-ipc-channel-contracts.md](../concepts/02-ipc-channel-contracts.md)、[/concepts/04-session-message-store.md](../concepts/04-session-message-store.md)）。所有通道名均忠实于 preload.ts 实际暴露（F-la-037）。

## 第一步：分页拉取会话列表

会话列表默认分页 50（`COWORK_SESSION_PAGE_SIZE = 50`，F-la-054），主进程侧由 `CoworkStore.listSessions` / `countSessions` 承载（F-la-019）：

```ts
// preload 门面（F-la-037），invoke 走 ipcRenderer.invoke
const page = await window.cowork.listSessions({ offset: 0, limit: 50 });
const total = await window.cowork.countSessions();
// 通道：cowork:session:list / cowork:session:* 系列（F-la-037）
```

配套操作：置顶 `cowork:session:pin`、重命名 `cowork:session:rename`、删除 `cowork:session:delete` 与批量删除 `cowork:session:deleteBatch`（F-la-037）。

## 第二步：拉取单条会话的消息历史

消息历史默认分页 30（`COWORK_MESSAGE_PAGE_SIZE = 30`，F-la-054），对应主进程 `CoworkStore.getPagedSessionMessages`（F-la-020）：

```ts
// preload.ts 实际签名：getMessages: (options) => ipcRenderer.invoke('cowork:session:getMessages', options)
const messages = await window.cowork.getMessages({
  sessionId,
  offset: 0,
  limit: 30,
});
```

向上翻页时递增 `offset` 即可；数据层方法 `getRecentConversationMessages` / `getAllConversationMessages` 提供"近期"与"全量"两种读取面（F-la-020）。

## 第三步：搜索消息

跨会话搜索的返回上限为 200（`COWORK_SEARCH_MESSAGE_PAGE_SIZE = 200`，F-la-054），主进程侧由 `CoworkStore.conversationSearch` / `getSessionSearchMessagePage` 承载（F-la-020、F-la-022）。

## 第四步：订阅流式更新

查询给出的是快照；turn 进行中的增量经 `cowork:stream:*` 推送事件族到达（F-la-038）：

```ts
// preload 门面：ipcRenderer.on('cowork:stream:message', handler) 等（F-la-037、F-la-038）
const unsubscribe = window.coworkStream.onMessage((msg) => appendMessage(msg));
window.coworkStream.onMessageUpdate((update) => patchMessage(update));
window.coworkStream.onComplete(() => unsubscribe());
```

教学要点：**快照 + 增量订阅**是本地优先架构的查询范式——数据全在本机 SQLite（F-la-004、F-la-016），快照查询走 `invoke` 一次性返回，运行态变化走事件推送，两者以消息 ID 关联，渲染层 Redux slice（F-la-042）负责归并。

## 第五步：fork 一条会话（进阶）

从当前会话分叉支线，走 `CoworkIpcChannel.ForkSession = 'cowork:session:fork'` 通道（F-la-055）：

```ts
await window.cowork.forkSession({
  sessionId,
  mode: 'conversation',   // CoworkForkMode: 'none' | 'conversation' | 'worktree'（F-la-056）
});
```

fork 元数据（`fork_mode`、`fork_workspace_path`、`fork_git_branch`、`fork_git_base_ref`）落 `cowork_sessions` 表（F-la-016），读取侧由 `CoworkStore.forkSession` 与私有辅助 `getSessionForkMetadata` 承载（F-la-019）。

## 要点回顾

1. 查询面全部经 preload `invoke`，渲染层无直接数据库访问；
2. 分页常量（50/30/200）在共享层集中声明（F-la-054），客户端与服务端读同一份约定；
3. 快照查询与流式订阅分工明确，消息 ID 是两者的关联键；
4. fork 这类结构性操作也有对应的常量通道键（`CoworkIpcChannel`），无手写字符串（F-la-055）。

## 相关概念

- [/concepts/02-ipc-channel-contracts.md](../concepts/02-ipc-channel-contracts.md)
- [/concepts/04-session-message-store.md](../concepts/04-session-message-store.md)
