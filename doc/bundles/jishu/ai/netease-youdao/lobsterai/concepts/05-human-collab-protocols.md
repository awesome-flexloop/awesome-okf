---
type: concept
title: "人机协作四类协议"
description: "btw（打断提问）/ goal（持续目标）/ rail（轨道索引）/ steer（流内纠偏）四类协作协议的状态枚举、限长常量、多模态请求负载与 AskUser 权限通道设计。"
tags: [lobsterai, cowork, btw, goal, rail, steer, protocol]
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

# 人机协作四类协议

常见 Agent 产品把「追问、中断、纠偏」实现为前端局部状态加一次性消息，协作语义随 UI 重构而漂移。LobsterAI 的做法是**协议先于界面**：四类协作动词被打断提问（btw）、持续目标（goal）、会话轨道索引（rail）、流内纠偏（steer）——各自建模为 `src/shared/cowork/` 下的独立类型模块，含状态枚举、限长常量、请求/响应接口，再由 `CoworkIpcChannel` 映射为 IPC 通道（F-la-043~F-la-055）。同一套协议因此可被 GUI、IM Bot、定时任务等多种入口复用。

## 一、btw：打断提问协议（`btw.ts`）

"Agent 正在干活，用户突然想插一句不相关的话"——btw（by the way）协议承载这种旁路提问。

**状态枚举** `CoworkBtwStatus`：`pending`、`answered`、`failed`、`stopped` 四态（F-la-043）。

**限长常量**（F-la-044，全部与状态枚举同文件声明）：

| 常量 | 值 | 用途 |
|---|---|---|
| `COWORK_BTW_CONTEXT_MAX_CHARS` | 16_000 | btw 可携带的上下文上限 |
| `COWORK_BTW_EVENT_QUESTION_MAX_CHARS` | 120_000 | 提问事件体上限 |
| `COWORK_BTW_RESULT_MAX_CHARS` | 120_000 | 回答结果体上限 |
| `COWORK_BTW_IDENTIFIER_MAX_CHARS` | 512 | 标识符上限 |
| `COWORK_BTW_THREAD_ENTRY_LIMIT` | 50 | 线程条目数上限 |
| `COWORK_BTW_THREAD_CONTENT_MAX_CHARS` | 500_000 | 线程内容总上限 |
| `COWORK_BTW_EPHEMERAL_THREAD_LIMIT` | 12 | 临时线程上限 |

**双命令别名**：`parseCoworkBtwCommand` 以正则 `/^\/(?:btw|side)(?=\s|$)/i` 同时匹配 `/btw` 与 `/side` 命令（F-la-046）。别名不是冗余——IM 场景下手机端输入 `/btw` 比找按钮自然，协议设计时即已考虑非 GUI 入口。

**接口与运行 ID**：`CoworkBtwEntry`、`CoworkBtwThread`、`CoworkBtwSubmitRequest`/`CoworkBtwSubmitResponse`、`CoworkBtwAbortRequest`/`CoworkBtwAbortResponse`（F-la-045）；`createCoworkRunId` 生成 `btw-${Date.now()}-${rand}` 格式的运行 ID（F-la-046）。btw 是**可中止**的——旁路提问不应阻塞主 turn 的取消权。

## 二、goal：持续目标协议（`goal.ts`）

"给 Agent 一个长期目标，让它多轮持续推进并汇报进度"——goal 协议把目标建模为可度量、可暂停、可封顶的实体。

- **状态枚举** `CoworkGoalStatus`：`active`、`paused`、`blocked`、`usage_limited`、`budget_limited`、`complete` 六态（F-la-047）。其中 `usage_limited` 与 `budget_limited` 分开——用量受限（外部配额）与预算受限（用户自设上限）是两种不同的停滞原因。
- **接口**：`CoworkGoal` 含 `id`、`objective`、`status`、`tokensUsed`、`tokenBudget`、`continuationTurns` 等字段（F-la-048），token 用量与预算字段使目标进度可量化。
- **工具函数**：`normalizeCoworkGoal` 做外部状态的规范化校验（畸形状态返回 `null`）；`formatCoworkGoalTokenCount` 以 k/m 缩写格式化 token 数（F-la-048）。

## 三、rail：会话轨道索引协议（`rail.ts`）

长会话的消息列表需要一条"轨道"支持快速定位——rail 协议定义消息索引项：

- `CoworkMessageRailIndexItem`：字段 `messageId`、`type: 'user' | 'assistant'`、`sequence`、`messageOffset`、`timestamp`、`preview`、`contentLen`（F-la-049）；
- `COWORK_RAIL_PREVIEW_MAX_LENGTH = 50`：预览文本最大 50 字符；
- `stripCoworkRailPreviewMarkdown` 与 `getCoworkRailPreview`：预览生成前先剥离 Markdown，保证轨道索引的轻量与可读（F-la-049）。

`CoworkStore.getSessionMessageRailIndex`（见 [/concepts/04-session-message-store.md](04-session-message-store.md)）是 rail 协议在数据层的落点。

## 四、steer：流内纠偏协议（`steer.ts`）

"Agent 正在输出，用户想立即改方向"——steer 协议在不取消 turn 的前提下注入纠偏指令。

- **状态枚举** `CoworkSteerStatus`：`pending`、`accepted`、`rejected` 三态（F-la-050）；
- **拒绝原因枚举** `CoworkSteerRejectReason` 共 7 个取值（F-la-051）：

| 取值 | 含义 |
|---|---|
| `no_active_turn` | 无活动 turn，无可纠偏对象 |
| `not_streaming` | 当前不在流式输出中 |
| `context_maintenance` | 正处于上下文维护窗口 |
| `runtime_unsupported` | 运行时（OpenClaw）不支持纠偏 |
| `runtime_rejected` | 运行时拒绝了纠偏请求 |
| `empty_input` | 纠偏输入为空 |
| `unknown` | 未知原因 |

把拒绝原因做成显式枚举而非错误字符串，渲染层可以针对每种原因给出差异化提示。

- **请求负载**：`CoworkSteerRequest` 字段 `sessionId`、`text`、`clientSteerId`（F-la-052）；`CoworkPendingSteer` 可携带 `attachments`、`imageAttachments`、`selectedTextSnippets`、`browserAnnotations`、`kitIds` 等多模态附件；`CoworkQueuedMediaSelection` 的 `mode` 取值为 `'auto' | 'image' | 'video' | 'none'`（F-la-052）。纠偏不是纯文本——用户可能圈选一段代码、附一张截图、引用浏览器标注后说"按这个改"。

## 五、AskUser 权限通道（`constants.ts`）

共享层常量还承载权限审批的基础设施（F-la-053）：

- `SESSION_AGNOSTIC_PERMISSION_SESSION_ID = '__askuser__'`：权限请求的会话无关占位 ID，AskUser 工具不隶属于任何具体会话；
- `ASK_USER_QUESTION_TOOL_NAME = 'AskUserQuestion'`：Agent 向用户提问的工具名，其请求/响应经 `McpBridgeServer` 桥接（见 [/concepts/07-mcp-integration-runtime.md](07-mcp-integration-runtime.md)），并在流事件层以 `cowork:stream:permission` / `permissionDismiss` 事件对推送（见 [/concepts/02-ipc-channel-contracts.md](02-ipc-channel-contracts.md)）。

## 设计启示

1. 为每个协作动词写独立的共享层类型模块：**状态枚举 + 限长常量 + 请求/响应接口 + IPC 通道键**，四件套缺一不可；
2. 限长常量与状态枚举同文件声明，防止"魔法数字"随实现漂移；
3. 拒绝原因、停滞原因建模为显式枚举，为差异化 UI 提示留好扩展点；
4. 命令协议预留文本别名（`/btw`/`/side`），是面向 IM 入口的低成本兼容性设计。

## 相关概念

- [/concepts/02-ipc-channel-contracts.md](02-ipc-channel-contracts.md)
- [/concepts/04-session-message-store.md](04-session-message-store.md)
- [/concepts/07-mcp-integration-runtime.md](07-mcp-integration-runtime.md)
