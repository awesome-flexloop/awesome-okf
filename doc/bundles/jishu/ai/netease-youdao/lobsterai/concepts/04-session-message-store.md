---
type: concept
title: "会话与消息数据管理"
description: "CoworkStore 四组 40+ 方法的数据访问模式、会话 fork（含 worktree 模式）元数据、分页与搜索策略，以及连续性胶囊的用途。"
tags: [lobsterai, cowork, session, message, store, fork, pagination]
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

# 会话与消息数据管理

在 [/concepts/03-sqlite-local-storage.md](03-sqlite-local-storage.md) 的表结构之上，`CoworkStore`（`src/main/coworkStore.ts`）封装了全部会话与消息的数据访问。其方法规模达 40+，但按职责可归为四组（F-la-019~F-la-022），分组本身就是一份"会话产品需要哪些数据能力"的清单。

## 一、四组方法

### 会话方法（F-la-019）

`createSession`、`getSession`、`forkSession`（含私有辅助 `getSessionForkMetadata`）、`updateSession`、`deleteSession`、`deleteSessions`、`listSessions`、`searchSessions`、`countSessions`、`countSearchSessions`、`setSessionPinned`、`resetRunningSessions`、`listSessionIdsByAgent`。

要点：增删改查之外有三个产品级能力——**分页计数成对出现**（`listSessions`/`countSessions`、`searchSessions`/`countSearchSessions`，UI 分页器需要总数）；**批量删除独立成方法**（`deleteSessions`）；**恢复运行态**（`resetRunningSessions`，应用重启后把残留的"运行中"会话重置，避免假死状态）。

### 消息方法（F-la-020）

`addMessage`、`insertMessageBeforeId`、`deleteMessage`、`replaceConversationMessages`、`replaceSessionMessages`、`updateMessage`、`getPagedSessionMessages`、`getSessionSearchMessagePage`、`getRecentConversationMessages`、`getAllConversationMessages`、`getSessionMessageRailIndex`、`getMessageTimestamp`。

要点：`insertMessageBeforeId` 支持在任意消息前插入（配合消息编辑/重跑场景）；`replaceConversationMessages` 与 `replaceSessionMessages` 两条"整段替换"路径分别面向会话视图与持久化视图；`getSessionMessageRailIndex` 返回消息轨道索引（配合 rail 协议，见 [/concepts/05-human-collab-protocols.md](05-human-collab-protocols.md)）。

### 配置与记忆方法（F-la-021）

`getConfig`、`setConfig`、`listUserMemories`、`createUserMemory`、`updateUserMemory`、`deleteUserMemory`、`getMemoryStats`、`autoDeleteNonPersonalMemories`、`markMemorySourcesInactiveBySession`、`markOrphanImplicitMemoriesStale`。

要点：记忆不仅有 CRUD，还有三条**生命周期治理**方法——按会话失效来源、孤儿隐式记忆标记过期、非个人记忆自动删除。记忆不是"只进不出"的堆叠，而是有来源追踪与过期机制的受管数据。

### 其他方法（F-la-022）

`listRecentCwds`（默认 limit 8）、`listRecentSessionCwds`、`listSessionCwds`、`getAppLanguage`（返回 `'zh' | 'en'`）、`conversationSearch`、`recentChats`、`getContinuityCapsule`、`upsertContinuityCapsule`、`deleteContinuityCapsules`、`countSessionMessages`。

## 二、会话 fork 与 CoworkForkMode

`forkSession` 配合私有辅助 `getSessionForkMetadata` 读取 fork 元数据（F-la-019）；fork 模式由共享层类型 `CoworkForkMode` 定义，取值为 `none`、`conversation`、`worktree` 三种（F-la-056），与 `cowork_sessions` 表的 `fork_mode`、`fork_workspace_path`、`fork_git_branch`、`fork_git_base_ref` 四列对应（F-la-016）：

| 模式 | 语义 |
|---|---|
| `none` | 非 fork 会话（默认值） |
| `conversation` | 仅分叉对话上下文，共享工作目录 |
| `worktree` | 分叉对话并创建 git worktree（`fork_git_branch`、`fork_git_base_ref` 记录分支与基点） |

教学要点：fork 是"从某条消息另起支线"的产品能力，其元数据不落关联表而是直接列在会话表上（单库内聚的简化，见 [/concepts/03-sqlite-local-storage.md](03-sqlite-local-storage.md)），模式判别用共享层类型常量而非魔法字符串。

## 三、分页与搜索策略

共享层 `constants.ts` 统一声明分页常量（F-la-054）：

| 常量 | 值 | 用途 |
|---|---|---|
| `COWORK_SESSION_PAGE_SIZE` | 50 | 会话列表分页 |
| `COWORK_MESSAGE_PAGE_SIZE` | 30 | 消息历史分页 |
| `COWORK_SEARCH_MESSAGE_PAGE_SIZE` | 200 | 搜索返回上限 |

常量集中声明在共享层而非各调用点，避免魔法数字随实现漂移——渲染层与主进程读取同一份分页约定。

## 四、连续性胶囊

`getContinuityCapsule` / `upsertContinuityCapsule` / `deleteContinuityCapsules` 操作 `cowork_session_capsules` 表（F-la-016、F-la-022）。胶囊是会话的"续接摘要"载体：当会话上下文需要压缩或跨会话延续时，关键状态被固化为胶囊，下次接续时不必重放全量消息。它与 btw 协议的 16k 字符上下文上限、消息轨道索引共同构成 LobsterAI 的上下文治理体系。

## 设计启示

1. 数据访问层按"会话 / 消息 / 配置记忆 / 其他"四组划分，新增能力时先归组再落方法，避免 40+ 方法平铺；
2. 分页方法必须携带计数配对，否则 UI 分页器将被迫做低效的全量统计；
3. fork 这类跨表语义优先用"主表加列 + 共享层判别类型"实现，而非独立关联表。

## 相关概念

- [/concepts/03-sqlite-local-storage.md](03-sqlite-local-storage.md)
- [/concepts/05-human-collab-protocols.md](05-human-collab-protocols.md)
- [/concepts/06-agent-preset-system.md](06-agent-preset-system.md)
