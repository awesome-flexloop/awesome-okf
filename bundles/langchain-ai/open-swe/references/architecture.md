---
type: reference
scope: open-swe
name: architecture
version: "0.1.0"
source: https://github.com/langchain-ai/open-swe
description: Open SWE 核心模块与图工厂参考——五个 LangGraph 入口、工厂函数、关键常量与中间件清单
---

# 架构参考

本参考登记 Open SWE 的核心模块、图工厂函数、运行时常量与中间件清单，作为概念文档的信源。所有条目均可在源码中定位。

## 图入口（langgraph.json）

`langgraph.json` 注册 5 个 graph 与 1 个 HTTP app（F-005）：

| 名称 | 入口 | 工厂函数 | 用途 |
|---|---|---|---|
| `agent` | `agent.graphs.agent:traced_agent` | `agent.server:get_agent` | 主编码 Agent（F-008、F-009） |
| `reviewer` | `agent.graphs.reviewer:traced_reviewer_agent` | `agent.reviewer:get_reviewer_agent` | 只读 PR 评审（F-010） |
| `analyzer` | `agent.graphs.analyzer:traced_analyzer` | `agent.analyzer:get_analyzer` | 仓库评审风格学习（F-011） |
| `chat` | `agent.graphs.chat:traced_chat_agent` | `agent.chat:get_chat_agent` | "与 PR 对话"只读助手（F-012） |
| `scheduler` | `agent.graphs.scheduler:get_scheduler` | `agent.scheduler:get_scheduler` | cron 任务扇出（F-013） |
| http.app | `agent.webapp:app` | `agent.api.app:create_app` | FastAPI Webhook 与 Dashboard（F-060、F-062） |

`agent/graphs/*.py` 是薄转发层：`agent/graphs/agent.py` 从 `agent.server` 导入 `get_agent`、`traced_agent`（F-006）；`agent/graphs/scheduler.py` 从 `agent.scheduler` 导入 `get_scheduler`（F-007）。

运行时配置：Python 3.12、`langgraph-api` 0.12.6；checkpointer TTL 策略 `delete`，清理间隔 60 分钟，默认 TTL 43200 秒（12 小时）（F-005）。

## 核心工厂函数签名

```python
# agent/server.py:1279
async def get_agent(config: RunnableConfig) -> Pregel

# agent/reviewer.py:1328
async def get_reviewer_agent(config: RunnableConfig) -> Pregel

# agent/analyzer.py:165
async def get_analyzer(config: RunnableConfig) -> Pregel

# agent/chat.py:215
async def get_chat_agent(config: RunnableConfig) -> Pregel

# agent/scheduler.py:57
def get_scheduler(config: RunnableConfig | None = None)
```

每个工厂返回一个经 `create_deep_agent(...)` 构造、`.with_config(config)` 配置的编译图；agent/reviewer/analyzer/chat 均通过 `traced_graph_factory(...)` 包装为 `traced_*` 导出，接入 LangSmith tracing 项目（F-009、F-010、F-011、F-012）。

## 运行时常量

来自 `agent/runtime/constants.py`（F-014）：

| 常量 | 值 | 含义 |
|---|---|---|
| `DEFAULT_LLM_MODEL_ID` | `dashboard.options.DEFAULT_MODEL_ID` | 默认模型 ID |
| `DEFAULT_LLM_MAX_TOKENS` | `64_000` | 单次模型调用最大 token |
| `DEFAULT_RECURSION_LIMIT` | `9_999` | 图递归步数上限 |
| `MODEL_CALL_RECURSION_LIMIT` | `5_000` | 模型调用递归上限（约为前者一半），`exit_behavior="end"` |

各图另有自己的模型调用上限：analyzer `STYLE_ANALYZER_MODEL_CALL_LIMIT = 80`（F-032）、chat `CHAT_MODEL_CALL_LIMIT = 100`（F-046）。

## 主 Agent 工具集

`get_agent` 的 `static_tools`（F-017）按职能分组：

- **网络/检索**：`http_request`、`fetch_url`、`web_search`
- **计划模式**：`approve_plan`、`enter_plan_mode`、`save_plan`
- **指令/技能**：`save_user_instructions`、`save_user_skill`、`delete_user_skill`
- **Linear**：`linear_comment`、`linear_create_issue`、`linear_delete_issue`、`linear_get_issue`、`linear_get_issue_comments`、`linear_list_teams`、`linear_search_issues`、`linear_update_issue`
- **线程管理**：`list_threads`、`get_thread`、`manage_thread`、`schedule_thread_wakeup`
- **PR/CI**：`open_pull_request`、`request_pr_review`、`manage_baby_sit`、`recreate_sandbox`
- **Slack**：`slack_add_reaction`、`slack_move_thread`、`slack_read_thread_messages`、`slack_start_new_thread`、`slack_thread_reply`
- **其他**：`background_execute`、`background_task`、`notify_automation_channel`、`read_user_settings`、`report_platform_issue`，条件性 `output_iframe`、`create_sandbox_file_download_url`

Desktop 本地运行时工具集缩减为 `[http_request, fetch_url, web_search]`（F-018）；`stop_summary_mode` 时缩减为 `[slack_read_thread_messages, slack_thread_reply]`（F-018）。内置 deepagents 工具（`read_file`/`write_file`/`edit_file`/`delete`/`ls`/`glob`/`grep`/`execute`/`task` 等）由 `create_deep_agent` 自身添加。

## Reviewer 工具集与 Finding 模型

Reviewer 工具（F-024）：`add_finding`、`update_finding`、`list_findings`、`publish_review`、`fetch_review_diff`、`reply_to_finding_thread`、`resolve_finding_thread`、`fetch_url`、`http_request`、`web_search`。无 commit/push/开 PR 工具。

`Finding` TypedDict（`agent/review/findings.py:100`，F-066）核心字段：

```python
class Finding(TypedDict):
    id: str
    severity: Severity          # critical/high/medium/low
    confidence: Confidence
    category: str
    title: str
    file: str
    start_line: int | None
    end_line: int | None
    side: DiffSide
    in_diff: bool               # 是否锚定在 PR diff 内
    description: str
    suggestion: str | None
    status: FindingStatus       # open/resolved/dismissed
    first_seen_sha: str
    last_confirmed_sha: str
    fingerprint: str
    github_review_id: int | None
    github_review_thread_id: str | None
    github_thread_resolved: bool
    last_human_reply_at: str | None
    last_human_reply_author: str | None
    last_human_reply_body: str | None
    interactions: list[FindingInteraction]
    # ... 其余 github_review_comment_ids 等多值字段
```

`REVIEW_FINDING_CAP = 6`（F-023）。Finding 存储操作：`new_finding`、`append_finding`、`update_finding_fields`、`list_findings`、`replace_findings`、`mutate_findings`、`append_finding_interaction`（F-067）。

## Scheduler 任务路由

`SchedulerState` 字段（F-037）：`schedule_id`、`task`、`watch_key`、`thread_id`、`agent_thread_id`、`run_id`、`prepare_run_id`、`channel_id`、`thread_ts`、`attempt`、`result`。

`_launch` 节点按 `task` 路由（F-038）：

| task 值 | 调用 |
|---|---|
| `"reconcile"` | `reconcile_stale_runs()` |
| `"baby_sit"` | `evaluate_watch(watch_key)` |
| `BACKGROUND_TASK_CRON_KIND` | `monitor_background_tasks(thread_id)` |
| `"session_cost"` | `run_session_cost_refresh(state)` |
| 其他（含 schedule_id） | `launch_scheduled_agent_run(schedule_id)` |

图结构为 `START -> launch -> END` 单节点线性图（F-013）。

## Dispatch 契约

`agent/dispatch.py` 关键函数（F-041 ~ F-045）：

```python
EVENT_STREAMING_V2_CONFIG_KEY = "__event_streaming_v2"
V2_RUN_STREAM_MODES = ("values", "updates", "messages", "custom", "tasks", "checkpoints")

def prepare_run_config(config, metadata) -> RunConfig
async def create_durable_run(
    thread_id, assistant_id, *, input, source,
    config=None, metadata=None, client=None,
    multitask_strategy="interrupt",   # 跟进消息中断活跃运行
    durability="sync",                # 每步前 checkpoint
    if_not_exists="create",
    stream_resumable=True,            # 事件流可重放
    after_seconds=None,
) -> Run
async def dispatch_agent_run(
    thread_id, content, configurable, *, source,
    input=None, context=None, people=None, channels=None, systems=None,
    assistant_id="agent", metadata=None, client=None,
    multitask_strategy="interrupt",
) -> Run
```

## Baby-sit 常量与状态机

`agent/baby_sit.py` 常量（F-050）：

| 常量 | 值 |
|---|---|
| `WATCH_SCHEDULE` | `"*/10 * * * *"`（每 10 分钟） |
| `MAX_RETRIES_PER_HEAD` | `3` |
| `MAX_DISPATCH_KEYS` | `30` |
| `MAX_DELIVERY_IDS` | `50` |
| `MAX_ALERT_KEYS` | `30` |
| `MAX_EVALUATION_ERRORS` | `3` |
| `CHECK_SET_SETTLE_MINUTES` | `10` |
| `WATCH_LOCK_TTL_MINUTES` | `5` |

`evaluate_watch` 返回状态字符串（F-055）：`"busy"`、`"missing"`、`"stopped"`、`"merged"`、`"closed"`、`"pending"`、`"settling"`、`"dispatched"`、`"duplicate"`、`"error"`。

## FastAPI 装配

`agent/api/app.py:create_app()`（F-062）按序挂载 router：

1. `dashboard_router`
2. `plan_router`
3. `workflow_approval_router`
4. `linear_webhook_router`
5. `slack_webhook_router`
6. `health_router`
7. `github_webhook_router`

CORS 来源由 `DASHBOARD_ALLOWED_ORIGINS` 逗号分隔解析；包含 `"*"` 时抛 RuntimeError（因 `allow_credentials=True`）。`lifespan` 在启动时校验沙箱与本地 LLM 配置，关闭时 `close_cached_models()`（F-061）。

## 模块路径速查

| 模块 | 职责 |
|---|---|
| `agent/server.py` | 主 Agent 图工厂、沙箱生命周期、模型解析、middleware 栈 |
| `agent/reviewer.py` | PR 评审图工厂、reviewer prompt、diff/finding 上下文构建 |
| `agent/analyzer.py` | 评审风格学习图、bootstrap/continual 两种模式 |
| `agent/chat.py` | 无沙箱只读 PR 对话图 |
| `agent/scheduler.py` | cron 扇出图 |
| `agent/dispatch.py` | 持久化运行分发单一契约 |
| `agent/reconcile.py` | 陈旧 pending 运行清理安全网 |
| `agent/baby_sit.py` | PR CI 监控 watches |
| `agent/prompt.py` | 系统提示构造 |
| `agent/desktop.py` | 本地桌面后端 |
| `agent/webapp.py` / `agent/api/app.py` | FastAPI 装配 |
| `agent/review/findings.py` | Finding 数据模型与存储 |
| `agent/review/reconcile.py` | Finding 与 GitHub thread 同步 |
| `agent/middleware/` | 全部中间件实现 |
| `agent/tools/` | 全部自定义工具 |
| `agent/dashboard/` | Dashboard API、OAuth、管理端点 |
| `agent/webhooks/` | GitHub/Linear/Slack webhook 路由 |
| `agent/integrations/` | 沙箱提供商（langsmith/modal/daytona/runloop/e2b/local）与 MCP 集成 |
