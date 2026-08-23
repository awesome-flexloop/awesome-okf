---
type: concept
scope: open-swe
name: scheduler-reconcile
version: "0.1.0"
source: https://github.com/langchain-ai/open-swe
description: Scheduler 与 Reconcile——cron 扇出图、陈旧运行清理、baby-sit PR CI 监控状态机
---

# Scheduler 与 Reconcile

Scheduler 是 Open SWE 的确定性心跳图：它把 cron 滴答扇出为各类后台任务，包括调度 Agent 运行、陈旧运行清理和 PR CI 监控。Reconcile 则是 durable dispatch 契约的悲观安全网。

## Scheduler 图结构

Scheduler 是一个极简的单节点 LangGraph 图（F-013）：

```python
def get_scheduler(config: RunnableConfig | None = None):
    builder = StateGraph(SchedulerState)
    builder.add_node("launch", _launch)
    builder.add_edge(START, "launch")
    builder.add_edge("launch", END)
    return builder.compile().with_config(config or {})
```

`START -> launch -> END`，没有条件分支、没有循环——所有路由逻辑都在 `_launch` 节点内通过 `task` 字段分派。

### SchedulerState

`SchedulerState` 是 `TypedDict(total=False)`（F-037），字段：

| 字段 | 用途 |
|---|---|
| `schedule_id` | 调度 Agent 运行的 ID |
| `task` | 任务类型（决定路由） |
| `watch_key` | baby-sit watch 的键 |
| `thread_id` | 后台任务监控的目标线程 |
| `agent_thread_id` | 关联的 Agent 线程 |
| `run_id` / `prepare_run_id` | 运行标识 |
| `channel_id` / `thread_ts` | Slack 上下文 |
| `attempt` | 重试次数 |
| `result` | 任务返回结果 |

### 任务路由

`_launch` 根据 `state.task` 或 `configurable.task` 路由（F-038）：

```python
async def _launch(state, config):
    task = state.get("task") or configurable.get("task")
    if task == "reconcile":
        return {"result": await reconcile_stale_runs()}
    if task == "baby_sit":
        key = state.get("watch_key") or configurable.get("watch_key")
        return {"result": {"status": await evaluate_watch(key)}}
    if task == BACKGROUND_TASK_CRON_KIND:
        thread_id = state.get("thread_id") or configurable.get("thread_id")
        return {"result": await monitor_background_tasks(thread_id)}
    if task == "session_cost":
        return {"result": await run_session_cost_refresh(state)}
    # 默认：调度 Agent 运行
    schedule_id = state.get("schedule_id") or configurable.get("schedule_id")
    return {"result": await launch_scheduled_agent_run(schedule_id)}
```

缺失必要键时返回结构化状态（如 `{"status": "missing_watch_key"}`），而非抛异常。

## Reconcile：陈旧运行清理

### 解决的问题

durable dispatch 依赖平台的 completion webhook 终结每次运行。当 webhook 因崩溃、投递丢失而未触发，运行会永远停留在 `pending` 状态，并持有其线程为 `busy`，导致该线程无法接收新运行。`reconcile_stale_runs` 是这个问题的安全网（F-039、F-040）。

### 算法

```python
async def reconcile_stale_runs(*, max_age_seconds: int = 1800) -> dict[str, int]:
    client = langgraph_client()
    now = datetime.now(UTC)
    # 分页遍历 busy 线程
    while True:
        threads = await client.threads.search(metadata=None, status="busy",
                                               limit=100, offset=offset)
        for thread in threads:
            runs = await client.runs.list(thread_id, status="pending")
            stale = [r["run_id"] for r in runs
                     if (now - parse_created_at(r["created_at"])).total_seconds() > max_age_seconds]
            if stale:
                await client.runs.cancel_many(thread_id=thread_id, run_ids=stale,
                                              action="interrupt")
        if len(threads) < 100:
            break
        offset += 100
```

关键设计：

- **只清理 `busy` 线程上的 `pending` run**：不碰正在运行的 run，也不碰空闲线程；
- **`action="interrupt"`**：中断而非删除，保留 checkpoint 以便可能的恢复；
- **per-thread try/except**：一个线程查询失败不中断整个清扫；
- **`created_at` 容错解析**：`_parse_created_at` 处理 datetime 对象、带 Z 的 ISO 字符串、naive 时间（补 UTC），无法解析则跳过并告警；
- **返回计数**：`threads_checked`、`stale_runs`、`cancelled` 用于可观测性。

### 与 completion webhook 的关系

| 机制 | 角色 | 触发 |
|---|---|---|
| completion webhook | 乐观终态 | 每次运行完成/失败时平台主动回调 |
| reconcile sweep | 悲观兜底 | scheduler cron 周期性扫描 busy 线程 |

两者配对：webhook 是常态路径，reconcile 是 webhook 丢失时的兜底。默认 30 分钟阈值意味着即使 webhook 完全丢失，最多 30 分钟（加一个 cron 间隔）后线程会被释放。

## Baby-sit：PR CI 监控

`/baby-sit` 是一个 opt-in 的 PR CI 监控技能，由 `agent/baby_sit.py` 实现。它让 Agent 持续监控一个 PR 的 CI 状态，新失败时恢复原 Agent 线程进行诊断。

### Watch 数据模型

`BabySitWatch` TypedDict（F-051）持久化在 LangGraph store 的 `["baby_sit_watches"]` namespace，键由 `watch_key(owner, repo, pr_number)` 生成，格式为 `"{owner}/{repo}#{pr_number}"`（owner/repo 小写化，F-052）。

核心字段：`active`、`thread_id`（原 Agent 线程）、`head_sha`、`retry_count`、`settled_check_key`/`settled_check_at`（去重抖动）、`dispatch_keys`（已派发失败指纹，上限 30）、`delivery_ids`（上限 50）、`alert_keys`（上限 30）、`evaluation_errors`（连续错误计数，上限 3）、`cron_id`。

### 双触发机制

Baby-sit 由两条路径触发，互为补充：

1. **签名 GitHub CI webhook**（`handle_ci_webhook`，F-056）：CI 事件到达时立即评估活跃 watch，低延迟；
2. **每 10 分钟 cron**（`WATCH_SCHEDULE = "*/10 * * * *"`，F-050）：确定性兜底，不调用模型即可检查未变化状态。

### 分布式锁

`_watch_lock` 用 LangGraph 线程作为锁（F-053）：lock thread id 为 `uuid5(NAMESPACE_URL, f"open-swe:baby-sit-lock:{key}")`，通过 `threads.create(if_exists="raise", ttl=5 minutes)` 获取。`ConflictError` 表示另一评估正在进行，返回 `"busy"`。finally 块删除锁线程。这保证同一 watch 不会被 webhook 和 cron 并发评估。

### evaluate_watch 状态机

`evaluate_watch(key, token=None)` 是入口，获取锁后委托给 `_evaluate_watch`（F-054、F-055）。状态机返回值：

```
获取 watch
  ├─ 不存在 → "missing"
  ├─ 非 active → stop_watch → "stopped"
  ├─ token 不可用 → 记录错误
  ├─ PR 不存在 → 记录错误
  ├─ PR 已关闭 → "merged" / "closed"（finish_watch）
  ├─ head_sha 变化 → 重置 retry_count/settled/dispatch_keys
  ▼
拉取 check_runs + commit_statuses
  ├─ 任一不可用 → 记录错误
  ├─ state == "pending" → 清空 settled，返回 "pending"
  ├─ state == "success"
  │     ├─ check_set 未 settled（10 分钟稳定期）→ "settling"
  │     └─ 已 settled → finish_watch（完成通知）
  ├─ state == "blocked" → finish_watch（需人工 triage）
  ├─ retry_count >= 3 → finish_watch（flaky 重跑上限）
  ├─ 失败指纹已派发 → "duplicate"
  └─ 新失败 → dispatch_agent_run(multitask_strategy="enqueue")
              → "dispatched"
```

关键行为：

- **head SHA 变化重置重试计数**：新 push 视为新机会，`retry_count` 归零；
- **check set 稳定期**：`CHECK_SET_SETTLE_MINUTES = 10`，成功状态需持续 10 分钟才认定完成，避免 CI 抖动误报；
- **失败指纹去重**：`_failure_key(head_sha, retry_count)` 加入 `dispatch_keys`（保留最近 30 个），同一失败不重复派发；
- **flaky 重跑上限**：`MAX_RETRIES_PER_HEAD = 3`，同一 head 失败重跑 3 次后停止，避免无限循环；
- **`multitask_strategy="enqueue"`**：CI 失败诊断作为后台跟进排队，不中断 Agent 当前可能正在进行的工作（与默认 `"interrupt"` 不同）；
- **终态直接通知源频道**：成功/blocked/超限等终态通过 `_finish_watch` 直接发布到原 Slack 线程，不恢复 Agent。

### 与主 Agent 的关系

Baby-sit 不自己诊断失败——它检测到新失败后，通过 `dispatch_agent_run` 恢复**原 Agent 线程**（`watch["thread_id"]`），把失败信息作为用户消息 enqueue。原 Agent 拥有完整的沙箱和上下文，可以拉日志、重跑、修复。这使得 baby-sit 是一个轻量监控层，智能仍在主 Agent。

## 后台任务与 Session Cost

除 reconcile 和 baby_sit 外，scheduler 还处理：

- **`BACKGROUND_TASK_CRON_KIND`**：调用 `monitor_background_tasks(thread_id)` 监控 `background_execute` 启动的长运行命令；
- **`"session_cost"`**：调用 `run_session_cost_refresh(state)` 刷新会话成本统计；
- **默认（schedule_id）**：调用 `launch_scheduled_agent_run(schedule_id)` 启动用户配置的定时 Agent 运行。

这些任务共享同一个 scheduler 图和 cron 基础设施，但各自有独立的业务逻辑模块。

## 相关概念

- [Dispatch-Review 循环](/langchain-ai/open-swe/concepts/dispatch-review-cycle) — durable dispatch 契约与 completion webhook
- [Agent 架构](/langchain-ai/open-swe/concepts/agent-architecture) — 图工厂与 middleware
- [总览](/langchain-ai/open-swe/concepts/overview)
- [架构参考](/langchain-ai/open-swe/references/architecture) — scheduler 与 baby-sit 常量
