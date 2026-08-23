---
type: example
scope: open-swe
name: triggering-agent-run
version: "0.1.0"
source: https://github.com/langchain-ai/open-swe
description: 触发 Agent 运行示例——通过 dispatch_agent_run 持久化分发、reviewer 评审与 reconcile 清理
---

# 触发 Agent 运行与评审循环

本示例演示 Open SWE 的核心运行链路：从外部触发器通过 `dispatch_agent_run` 启动一个持久化运行，到 reviewer 产出 findings，再到 reconcile 安全网清理。示例中的所有 API 调用均来自源码（参见 [架构参考](/langchain-ai/open-swe/references/architecture)）。

## 前置条件

- LangGraph runtime 运行中（`make dev` 启动 `langgraph dev`，服务所有图与 FastAPI app）；
- `LANGGRAPH_URL` 环境变量指向 runtime（默认 `http://localhost:2024`）；
- 已配置 GitHub App 或 OAuth token，沙箱提供商可达（默认 `SANDBOX_TYPE=langsmith`）。

## 1. 通过 dispatch_agent_run 触发主 Agent

`dispatch_agent_run` 是所有外部触发的统一入口。它构造 `RunInput` 并调用 `create_durable_run`，默认使用 `multitask_strategy="interrupt"`：

```python
from agent.dispatch import dispatch_agent_run

configurable = {
    "thread_id": "slack:C12345:1700000000.000000",
    "github_login": "octocat",
    "user_email": "octocat@example.com",
    "source": "slack",
    "slack_thread": {
        "channel_id": "C12345",
        "thread_ts": "1700000000.000000",
        "triggering_user_id": "U9999",
        "triggering_user_name": "Octo Cat",
    },
}

run = await dispatch_agent_run(
    thread_id=configurable["thread_id"],
    content="帮我排查这周 main 分支上的 CI 失败",
    configurable=configurable,
    source="slack",
    assistant_id="agent",
)
print(run["run_id"])
```

`dispatch_agent_run` 内部通过 `_dispatch_input` 构造 sender/channel/system 身份：Slack 来源会解析出 `slack:<user_id>` 的 person 与 `slack:<channel_id>` 的 channel（F-044）。`create_durable_run` 则固定 `stream_mode=V2_RUN_STREAM_MODES`、`stream_subgraphs=True`、`stream_resumable=True`、`durability="sync"`（F-042）。

### 跟进消息中断活跃运行

同一线程上的后续消息默认使用 `multitask_strategy="interrupt"`：当前运行被中断（进度由 sync checkpoint 保留），Agent 带完整历史 + 新消息恢复：

```python
await dispatch_agent_run(
    thread_id=configurable["thread_id"],
    content="重点看 auth 模块",
    configurable=configurable,
    source="slack",
)
```

后台跟进（如 baby-sit CI 失败诊断）改用 `"enqueue"` 排队而不中断：

```python
await dispatch_agent_run(
    thread_id=watch["thread_id"],
    content=failure_prompt,
    configurable=watch["run_config"],
    source="github",
    multitask_strategy="enqueue",
)
```

## 2. 触发 Reviewer 评审 PR

Reviewer 运行同样走 `dispatch_agent_run`，但 `assistant_id="reviewer"`，configurable 携带 PR 坐标：

```python
reviewer_run = await dispatch_agent_run(
    thread_id="reviewer:octocat/hello-world#42",
    content=None,
    configurable={
        "thread_id": "reviewer:octocat/hello-world#42",
        "repo": {"owner": "octocat", "name": "hello-world"},
        "pr_number": 42,
        "base_sha": "abc123",
        "head_sha": "def456",
        "pr_url": "https://github.com/octocat/hello-world/pull/42",
        "source": "github",
    },
    source="github",
    assistant_id="reviewer",
)
```

Reviewer 工厂 `get_reviewer_agent` 会：

1. `_ensure_reviewer_sandbox_for_thread` 获取沙箱（`allow_replacement=True`，F-028）；
2. `prepare_review_repo` clone/fetch 并 checkout PR head；
3. `fetch_pr_diff` + `materialize_review_diff` 物化 diff，计算 `diff_line_set`；
4. `fetch_pr_review_threads` 拉取已有 thread，调用 `reconcile_findings_with_review_threads` 同步状态；
5. 构建 `_build_first_review_context` 上下文，Agent 调用 `fetch_review_diff` → `add_finding` → `list_findings` → `publish_review`。

### 重评审：新 commit 推送后

当 PR 有新 commit，webhook 再次触发 reviewer，configurable 额外携带 `re_review=True` 与 `last_reviewed_sha`：

```python
await dispatch_agent_run(
    thread_id="reviewer:octocat/hello-world#42",
    content=None,
    configurable={
        **base_configurable,
        "re_review": True,
        "last_reviewed_sha": "def456",
        "head_sha": "ghi789",
    },
    source="github",
    assistant_id="reviewer",
)
```

此时上下文由 `_build_re_review_context` 构建，Agent 对每个开放 finding 决定 `update_finding(status="resolved", note="...")` 或新增 finding（F-030）。

## 3. Scheduler 周期任务

Scheduler 图由 cron 触发，`task` 字段决定执行什么。例如触发 reconcile 清理：

```python
from agent.scheduler import get_scheduler

scheduler = get_scheduler({})
result = await scheduler.ainvoke(
    {"task": "reconcile"},
    config={"configurable": {"prepare_run_id": "reconcile-001"}},
)
print(result)  # {"result": {"threads_checked": N, "stale_runs": M, "cancelled": K}}
```

`_launch` 节点识别 `task == "reconcile"` 并调用 `reconcile_stale_runs(max_age_seconds=1800)`，取消 busy 线程上超过 30 分钟的 pending run（F-038、F-040）。

触发 baby-sit 评估：

```python
result = await scheduler.ainvoke(
    {"task": "baby_sit", "watch_key": "octocat/hello-world#42"},
    config={"configurable": {}},
)
print(result["result"]["status"])  # pending/success/dispatched/duplicate/...
```

## 4. Baby-sit 管理 Watch

通过 `manage_baby_sit` 工具（暴露给主 Agent）或直接调用模块函数启动 watch：

```python
from agent.baby_sit import start_watch, watch_key, evaluate_watch
from agent.utils.slack import GitHubPrRef

pr_ref = GitHubPrRef(
    owner="octocat",
    repo="hello-world",
    number=42,
    url="https://github.com/octocat/hello-world/pull/42",
)
watch = await start_watch(
    pr_ref=pr_ref,
    head_sha="def456",
    head_ref="feature/login",
    installation_id=None,
    thread_id="slack:C12345:1700000000.000000",
    run_config={
        "source": "slack",
        "slack_thread": {"channel_id": "C12345", "thread_ts": "1700000000.000000"},
        "thread_id": "slack:C12345:1700000000.000000",
    },
    source_context={"slack_thread": {"channel_id": "C12345"}},
)

key = watch_key(pr_ref.owner, pr_ref.repo, pr_ref.number)
status = await evaluate_watch(key)
```

`start_watch` 持久化 `BabySitWatch` 到 store 并注册每 10 分钟 cron（`WATCH_SCHEDULE = "*/10 * * * *"`）。CI webhook 到达时 `handle_ci_webhook` 立即评估；cron 提供确定性兜底。新失败时，`_evaluate_watch` 以 `multitask_strategy="enqueue"` 把失败提示派发到原 Agent 线程（F-055）。

## 5. 配置 completion webhook

为让运行结束后自动回复源频道，部署时设置绝对 https URL 与 secret：

```bash
export COMPLETION_WEBHOOK_URL="https://open-swe.example.com/webhooks/run-complete"
export RUN_COMPLETE_WEBHOOK_SECRET="some-long-random-secret"
```

`_resolve_completion_webhook_url` 会校验 URL 非相对、非 loopback，然后以 `?token=<secret>` 附加到 `create_durable_run` 的 `webhook` 参数（F-045）。若 secret 未设置或 URL 为 localhost，则不附加 webhook 且记录告警——完成回复变为 best-effort，但不会破坏运行创建。

## 验证要点

- 运行创建后可在 LangGraph dashboard 看到 thread 状态为 `busy`，事件流含 `tools`/`lifecycle`/子 Agent 命名空间；
- reviewer 的 `add_finding` 对 diff 外行返回 `success: false, in_diff: false`；
- 若 completion webhook 未配置，手动停止一个运行或等待 `reconcile_stale_runs` 清扫（默认 30 分钟阈值）；
- `publish_review` 返回的 `review_id` 为数字且 `skipped_empty_re_review`/`dry_run` 均未置位时，才表示评审真正发布到 GitHub。

## 相关概念

- [Dispatch-Review 循环](/langchain-ai/open-swe/concepts/dispatch-review-cycle) — durable dispatch 与 findings 模型
- [Scheduler 与 Reconcile](/langchain-ai/open-swe/concepts/scheduler-reconcile) — cron 扇出与 baby-sit 状态机
- [Agent 架构](/langchain-ai/open-swe/concepts/agent-architecture) — 图工厂与 middleware
