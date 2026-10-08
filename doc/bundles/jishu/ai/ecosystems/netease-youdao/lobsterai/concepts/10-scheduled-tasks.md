---
type: concept
title: "定时任务子系统"
description: "Renderer → Main → OpenClaw Gateway 三层架构、15 秒轮询对账模型、Schedule/Payload 判别联合、投递/会话/唤醒三组正交旋钮，以及四组网关映射函数。"
tags: [lobsterai, scheduled-task, cron, polling, openclaw]
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

# 定时任务子系统

定时任务让 Agent 可以"到点自己干活"：定时播报、周期巡检、定时触发 Agent turn。LobsterAI 的子系统设计文档（`src/scheduledTask/design.md`）明示了两大架构决策：**三层架构**与**15 秒轮询对账**（F-la-057、F-la-058）。

## 一、三层架构与四大理念

```
Renderer（ScheduledTasksView，F-la-041）
    │  scheduledTask:* IPC 通道（F-la-063）
    ▼
Main（src/scheduledTask/，CronJobService）
    │  15 秒轮询对账
    ▼
OpenClaw Gateway（唯一调度事实源）
```

四大设计理念（F-la-058）：

1. **OpenClaw 驱动**：调度语义（cron、周期、单次）委托给 OpenClaw 网关，本地不实现调度器；
2. **策略模式**：调度模型用判别联合建模（见下节），新增调度类型不改既有分支；
3. **来源推断**：任务的来源（手动创建 / IM 触发 / 会话衍生）可推断，支撑 `OriginKind` 分类；
4. **15 秒轮询**：本地以固定周期与网关对账，而非依赖推送。

轮询模型的关键认知：**网关是唯一调度事实源，本地只是其任务状态的镜像视图**。断线重连后对账即可自愈，不存在"本地已触发但网关不知情"的状态不一致。`WakeMode` 的 `next-heartbeat` 取值进一步表明轮询节奏与心跳周期对齐，任务执行被建模为"请求网关安排一次 Agent turn"而非本地直接执行。

## 二、类型模型：两组判别联合

`types.ts` 用 kind 字段判别联合建模两类核心实体（F-la-059、F-la-060）：

**Schedule（调度计划）**：

```ts
// 成员为 ScheduleAt / ScheduleEvery / ScheduleCron，以 kind 字段判别（F-la-059）
type Schedule =
  | { kind: 'at';   at: number }              // 单次定时
  | { kind: 'every'; everyMs: number }        // 固定周期
  | { kind: 'cron'; cron: string; tz?: string } // cron 表达式
```

**ScheduledTaskPayload（任务负载）**：

```ts
// 成员为 AgentTurnPayload / SystemEventPayload（F-la-060）
type ScheduledTaskPayload =
  | { kind: 'agentTurn';  /* …Agent turn 参数 */ }  // 触发一次 Agent 执行
  | { kind: 'systemEvent'; /* …系统事件参数 */ }      // 触发系统级事件
```

判别联合的可扩展性优于枚举拼接：新增一种调度类型只需新增一个联合成员，既有类型分支（渲染表单、映射函数）按 `kind` 分发天然兼容。配套接口还有 `ScheduledTask`、`ScheduledTaskRun`、`ScheduledTaskInput`（F-la-060）。

## 三、三组正交运行旋钮

`constants.ts` 定义的运行枚举彼此正交，可自由组合（F-la-061、F-la-062）：

| 旋钮 | 取值 | 语义 |
|---|---|---|
| `DeliveryMode` | `none` / `announce` / `webhook` | 结果投递方式 |
| `SessionTarget` | `main` / `isolated` | 在目标会话还是隔离会话中执行 |
| `WakeMode` | `now` / `next-heartbeat` | 立即唤醒或对齐下次心跳 |

任务状态 `TaskStatus` 四态：`success` / `error` / `skipped` / `running`（F-la-062）；默认 Agent 为 `DefaultAgentId = 'main'`（F-la-062）。同文件还定义 `ScheduleKind`、`PayloadKind`、`OriginKind`、`BindingKind`、`InternalTaskMarker` 等常量对象——`OriginKind`（legacy / im / cowork / manual）记录任务来源，`BindingKind`（new_session / ui_session / im_session / session_key）声明执行绑定的会话形态。

## 四、CronJobService：轮询对账与映射函数

`CronJobService`（`src/scheduledTask/cronJobService.ts`）的方法面（F-la-064）：

| 方法组 | 成员 |
|---|---|
| 任务 CRUD | `addJob`、`updateJob`、`removeJob`、`listJobs`、`getJob`、`toggleJob`、`runJob` |
| 运行记录 | `listRuns`、`countRuns`、`listAllRuns` |
| 轮询 | `startPolling`、`stopPolling`、`pollOnce`、`notifyGatewayReady` |

**`notifyGatewayReady` 是启动时序的枢纽**：网关就绪后才 `startPolling` 并强制执行一次完整对账（`pollOnce(true)`），避免网关未就绪时的无效轮询。

**四组映射函数**把网关模型规整为本域模型：`mapGatewaySchedule`（网关调度 → `Schedule`）、`mapGatewayTaskState`（网关任务状态 → `TaskStatus` + 投递模式）、`mapGatewayJob`（网关作业 → `ScheduledTask`）、`mapGatewayRun`（网关运行日志 → `ScheduledTaskRun`）（F-la-064）。网关模型演进时，改动收敛在映射函数内，本域类型保持稳定。

## 五、与会话层的双向绑定

`cowork_sessions` 表含 `scheduled_task_id` 列（F-la-016）：定时任务创建的会话反向记录其来源任务，会话侧可回溯"这条会话是哪个定时任务产生的"；任务侧经 `resolveSession` IPC 通道反查绑定会话（F-la-063）。配合 `BindingKind` 的 `im_session` 取值，定时任务的结果可以直接投递到 IM 会话（[/concepts/08-im-gateway.md](08-im-gateway.md)）。

## 六、IPC 通道

`IpcChannel` 常量对象以 `scheduledTask:` 为前缀，键含 `list`、`get`、`create`、`update`、`delete`、`toggle`、`runManually`、`stop`、`listRuns`、`countRuns`、`listAllRuns`、`resolveSession`、`listChannels`、`listChannelConversations`、`statusUpdate`、`runUpdate`、`refresh`（F-la-063）。preload 以 `scheduledTasks` 命名空间暴露这些方法（create/update 走 `invoke`，`onStatusUpdate`/`onRunUpdate` 走 `ipcRenderer.on` 订阅推送），通道常量经 `ScheduledTaskIpc` 别名导入、常量对象单一来源（见 [/concepts/02-ipc-channel-contracts.md](02-ipc-channel-contracts.md)）。

## 设计启示

1. 调度事实源在远端时，用「短周期轮询 + 全量对账 + 映射函数规整」替代本地预调度，换取断线自愈；
2. 调度计划与任务负载都用判别联合建模，kind 字段分发天然支持扩展；
3. 投递/会话/唤醒三组旋钮正交设计，避免组合爆炸的专用枚举；
4. 网关就绪事件（`notifyGatewayReady`）显式驱动对账启动，而不是无条件开机轮询。

## 相关概念

- [/concepts/00-overall-architecture.md](00-overall-architecture.md)
- [/concepts/02-ipc-channel-contracts.md](02-ipc-channel-contracts.md)
- [/concepts/08-im-gateway.md](08-im-gateway.md)
