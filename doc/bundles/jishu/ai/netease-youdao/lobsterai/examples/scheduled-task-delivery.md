---
type: example
title: "定时任务配置与投递流程"
description: "创建一个 cron 定时 Agent turn 任务、配置投递/会话/唤醒三组旋钮、经 CronJobService 轮询对账并把结果投递到 IM 会话的完整演练。"
tags: [lobsterai, scheduled-task, cron, delivery, example]
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

# 定时任务配置与投递流程

本演练演示"每天早上 9 点让 Agent 巡检代码仓库，并把结果发到 IM 会话"的完整链路（概念背景见 [/concepts/10-scheduled-tasks.md](../concepts/10-scheduled-tasks.md)、[/concepts/08-im-gateway.md](../concepts/08-im-gateway.md)）。调度语义委托给 OpenClaw 网关，本地经 15 秒轮询对账（F-la-057、F-la-058）。

## 第一步：定义任务输入

任务输入为 `ScheduledTaskInput` 接口（F-la-060），包含调度计划（判别联合 `Schedule`）、负载（判别联合 `ScheduledTaskPayload`）与三组运行旋钮（F-la-059~F-la-061）：

```ts
// 输入骨架：成员与判别值忠实于 src/scheduledTask/types.ts 与 constants.ts
const input: ScheduledTaskInput = {
  name: '每日仓库巡检',
  enabled: true,
  agentId: 'main',                      // DefaultAgentId = 'main'（F-la-062）
  schedule: {
    kind: 'cron',                       // ScheduleCron（F-la-059）
    cron: '0 9 * * *',                  // 每天 09:00
    tz: 'Asia/Shanghai',
  },
  payload: {
    kind: 'agentTurn',                  // AgentTurnPayload（F-la-060）
    prompt: '巡检工作目录的 git 状态与待办事项，输出三段摘要',
  },
  delivery: {
    mode: 'announce',                   // DeliveryMode: none/announce/webhook（F-la-061）
  },
  session: {
    target: 'main',                     // SessionTarget: main/isolated（F-la-061）
  },
  wake: {
    mode: 'next-heartbeat',             // WakeMode: now/next-heartbeat（F-la-061）
  },
};
```

旋钮组合的语义：`announce` 投递 + `main` 会话目标 + `next-heartbeat` 唤醒，即"在主会话中执行，结果主动播报，唤醒对齐心跳节奏"。三组旋钮正交，可自由替换（如 `mode: 'webhook'` 改为回传外部系统）。

## 第二步：创建任务

渲染层经 preload 的 `scheduledTasks` 门面创建（通道常量经 `ScheduledTaskIpc` 导入，`as const` 单一来源，F-la-063）：

```ts
// preload.ts 实际签名：create: (input: any) => ipcRenderer.invoke(ScheduledTaskIpc.Create, input)
const task = await window.scheduledTasks.create(input);
// task: ScheduledTask —— CronJobService.addJob 经 mapGatewayJob 映射后的本域模型（F-la-064）
```

主进程侧 `CronJobService.addJob(input: ScheduledTaskInput)` 把任务登记到网关，返回前经 `mapGatewayJob` 把网关作业规整为 `ScheduledTask`（F-la-064）。

## 第三步：轮询对账与执行

网关是唯一调度事实源；本地 `CronJobService` 以 15 秒轮询镜像其状态（F-la-058、F-la-064）：

```
startPolling() ──► pollOnce() 每 15s ──► 与网关对账任务与运行记录
                        │
notifyGatewayReady() ───┘  网关就绪时强制完整对账一次后才开始轮询
```

每次到点触发后，运行记录经 `mapGatewayRun` 映射为 `ScheduledTaskRun`，状态取 `TaskStatus` 四态之一（`success`/`error`/`skipped`/`running`，F-la-062）。手动补跑一次与停用：

```ts
await window.scheduledTasks.runManually(task.id);   // → ScheduledTaskIpc.RunManually
await window.scheduledTasks.toggle(task.id, false); // → ScheduledTaskIpc.Toggle
```

## 第四步：订阅状态与查询运行历史

```ts
// preload.ts 实际签名（F-la-063 通道键）：
// onStatusUpdate: ipcRenderer.on(ScheduledTaskIpc.StatusUpdate, handler)
const offStatus = window.scheduledTasks.onStatusUpdate((s) => renderStatus(s));
const offRun = window.scheduledTasks.onRunUpdate((r) => appendRun(r));

// 运行历史
const runs = await window.scheduledTasks.listRuns(task.id, 20, 0);
const total = await window.scheduledTasks.countRuns(task.id);
```

## 第五步：投递到 IM 会话

`delivery.mode` 为 `announce` 时，结果经 IM 网关主动推送。任务若绑定 IM 会话（`BindingKind` 的 `im_session` 取值，F-la-062），执行结果直接投递到该会话；渲染层可用 `listChannels` / `listChannelConversations` 选择投递目标（F-la-063）：

```ts
const channels = await window.scheduledTasks.listChannels();
const conversations = await window.scheduledTasks.listChannelConversations('feishu');
```

执行产生的会话经 `cowork_sessions.scheduled_task_id` 列回溯来源任务（F-la-016），反查走 `resolveSession` 通道（F-la-063）。

## 要点回顾

1. 创建只需组装 `ScheduledTaskInput`：判别联合调度 + 判别联合负载 + 三组正交旋钮；
2. 本地不实现调度器，`CronJobService` 15 秒对账网关，断线自愈（F-la-058、F-la-064）；
3. 投递/会话/唤醒旋钮正交组合，同一任务可切换 IM 播报或 webhook 回传；
4. 任务 ↔ 会话双向可追溯：`BindingKind` + `scheduled_task_id` 列 + `resolveSession` 通道。

## 相关概念

- [/concepts/10-scheduled-tasks.md](../concepts/10-scheduled-tasks.md)
- [/concepts/08-im-gateway.md](../concepts/08-im-gateway.md)
- [/concepts/02-ipc-channel-contracts.md](../concepts/02-ipc-channel-contracts.md)
