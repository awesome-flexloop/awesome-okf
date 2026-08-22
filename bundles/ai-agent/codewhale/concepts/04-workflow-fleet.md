---
type: concept
title: Workflow 与 Fleet（Workflow & Fleet）
description: CodeWhale 用声明式 IR 与沙箱 QuickJS VM 双层实现编排，通过 Agent Fleet 落盘管理可重试、可恢复的多 worker 运行
tags: [codewhale, workflow, fleet, subagents]
sources:
  - resource: "/references/crates-overview.md"
    title: "Crates 全景概览"
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# Workflow 与 Fleet

CodeWhale 的编排能力由「声明式 IR + 命令式 JS VM」双轨构成，并叠加一个落地到磁盘的 Agent Fleet 控制面。

## 双轨架构

- **`crates/workflow`（静态 IR）**：16 个子模块（见 [F-073]），承载 gates（`GateSpec`/`GateOutcome`/`stopship_gate_pipeline`，见 [F-074]）、fleet 精确/快照/预检、replay、review_repair（`ReviewRepairLoop`/`RouteReceipt`）、role_resolve（`FleetRoleMap`/`ResolvedWorkflowAgent`）。`WorkflowConfig` 含 `goal`、`max_concurrent`、`phases`（见 [F-076]）。
- **`crates/workflow-js`（命令式 VM）**：沙箱 QuickJS（rquickjs）运行时，脚本在一个 async 函数内用 `task()`、`parallel()`、`pipeline()` 派发子代理，用 `log()`/`phase()` 上报进度，通过 `budget` 全局读 token 池。`Date.now()`、`Math.random()` 直接抛错，以保证轨迹可重放（见 [F-077] 上下文）。

## 容量常量

容量上限被写死为常量（见 [F-075][F-078]）：

| 常量 | 值 | 位置 |
|---|---|---|
| `DEFAULT_FLEET_WORKFLOW_MAX_AGENTS` | 1000 | `workflow` |
| `DEFAULT_FLEET_WORKFLOW_MAX_DEPTH` | 5 | `workflow` |
| `WORKFLOW_LIFETIME_CAP` | 1000 | `workflow-js` |
| `WORKFLOW_MAX_CONCURRENT` | 16 | `workflow-js` |

## Agent Fleet

Fleet 是本地优先的「多 worker 持久化控制面」。一个 fleet worker 本质是 fleet 启动并持久追踪的 `/codewhale exec` 无头运行。状态存于 `.codewhale/fleet.jsonl`，日志分别在 `.codewhale/fleet/` 与 `.codewhale/fleet-host/`（见 [F-092]）。

CLI 动词（见 [F-091]）：

```text
init / run tasks.json --max-workers 4 / status / inspect <worker-id>
logs <worker-id> / artifacts <worker-id> / interrupt <worker-id>
restart <worker-id> / resume <run-id> / stop --all
```

`resume <run-id>` 是重启恢复动词：重放 ledger、协调失联 worker 的租约、幂等且不启动新工作。

## 子代理角色

`agent` 工具以 `type` 字段选择 Fleet 姿态，角色含 `worker`（可写）、`scout`（只读）、`planner`（只出策略）、`reviewer`（只读+评分）（见 [F-093]）。子代理默认继承父的完整工具面，仅在深度预算耗尽时过滤掉 `agent`（默认深度 3，见 [F-081]）。

## 相关概念

- [总览](/concepts/00-overview.md)
- [Agent 主循环](/concepts/01-agent-loop.md)
- [Crates 全景概览](/references/crates-overview.md)