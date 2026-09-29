---
type: spec
title: "Open SWE 事实清单"
---

# Open SWE 事实清单

> 信源根目录：`d:/spaces/SpecWeave/external/libs/ai/langchain-ai/open-swe/`
> 采集日期：2026-08-23。所有事实均带文件路径与行号，不含推断。

## 项目元信息

F-001: 文件 `pyproject.toml` 第1-7行，项目名称 `open-swe-agent`，版本 `0.1.0`，描述 "Open SWE Agent - Python agent for automating software engineering tasks"，`requires-python = ">=3.11"`，许可证 MIT，构建后端 `hatchling.build`，wheel 包为 `agent`。

F-002: 文件 `pyproject.toml` 第8-35行，核心运行时依赖包含 `deepagents==0.7.6`、`langgraph>=1.2.10`、`langchain>=1.3.9`、`fastapi>=0.141.1`、`uvicorn>=0.52.0`、`langgraph-sdk>=0.4.2`、`langchain-anthropic>=1.5.4`、`langchain-openai>=1.4.1,<2.0.0`、`langchain-fireworks>=1.5.2`、`langchain-google-genai>=4.3.2`、`langchain-mcp-adapters>=0.3.1`、`langchain-daytona>=0.0.8`、`langchain-modal>=0.0.6`、`langchain-runloop>=0.0.7`、`langchain-e2b==0.0.6`、`stagehand>=3.22.0`、`exa-py>=2.16.2`、`websockets>=15.0.1`。

F-003: 文件 `pyproject.toml` 第45-56行，`[tool.uv]` 中 `override-dependencies = ["deepagents==0.7.6", "wcmatch>=11.0"]`，`constraint-dependencies = ["langgraph-api>=0.12.6,<0.13"]`。

F-004: 文件 `pyproject.toml` 第68-82行，ruff 配置 `line-length = 100`、`target-version = "py311"`；pytest 配置 `asyncio_mode = "auto"`、`testpaths = ["tests"]`；basedpyright `pythonVersion = "3.11"`、`typeCheckingMode = "standard"`。

F-005: 文件 `langgraph.json` 第1-26行，`python_version: "3.12"`、`api_version: "0.12.6"`；`graphs` 声明 5 个入口：`agent: "agent.graphs.agent:traced_agent"`、`reviewer: "agent.graphs.reviewer:traced_reviewer_agent"`、`analyzer: "agent.graphs.analyzer:traced_analyzer"`、`chat: "agent.graphs.chat:traced_chat_agent"`、`scheduler: "agent.graphs.scheduler:get_scheduler"`；`http.app: "agent.webapp:app"`；checkpointer TTL 策略 `delete`，`sweep_interval_minutes: 60`，`default_ttl: 43200`。

## Graph 入口与图工厂

F-006: 文件 `agent/graphs/agent.py` 第1-3行，从 `agent.server` 导入 `get_agent`、`traced_agent` 并 `__all__` 导出。

F-007: 文件 `agent/graphs/scheduler.py` 第1-3行，从 `agent.scheduler` 导入 `get_scheduler` 并 `__all__` 导出。

F-008: 文件 `agent/server.py` 第1279行，`async def get_agent(config: RunnableConfig) -> Pregel`，主编码 Agent 图工厂。第1286-1291行，当 `thread_id is None or not graph_loaded_for_execution(config)` 时返回 `create_deep_agent(system_prompt="", tools=[]).with_config(config)`（无沙箱空 agent）。

F-009: 文件 `agent/server.py` 第1706行，模块级 `traced_agent = traced_graph_factory(get_agent, AGENT_TRACING_PROJECT)`。

F-010: 文件 `agent/reviewer.py` 第1328行，`async def get_reviewer_agent(config: RunnableConfig) -> Pregel`；第1449行 `traced_reviewer_agent = traced_graph_factory(get_reviewer_agent, REVIEW_TRACING_PROJECT)`。

F-011: 文件 `agent/analyzer.py` 第165行，`async def get_analyzer(config: RunnableConfig) -> Pregel`；第212行 `traced_analyzer = traced_graph_factory(get_analyzer, REVIEW_TRACING_PROJECT)`。

F-012: 文件 `agent/chat.py` 第215行，`async def get_chat_agent(config: RunnableConfig) -> Pregel`；第266行 `traced_chat_agent = traced_graph_factory(get_chat_agent, AGENT_TRACING_PROJECT)`。

F-013: 文件 `agent/scheduler.py` 第57-62行，`def get_scheduler(config: RunnableConfig | None = None)`：构建 `StateGraph(SchedulerState)`，添加节点 `launch`，边 `START -> launch -> END`，`compile().with_config(config or {})`。

## 运行时常量

F-014: 文件 `agent/runtime/constants.py` 第1-6行，`DEFAULT_LLM_MODEL_ID` 来自 `agent.dashboard.options.DEFAULT_MODEL_ID`；`DEFAULT_LLM_MAX_TOKENS = 64_000`；`DEFAULT_RECURSION_LIMIT = 9_999`；`MODEL_CALL_RECURSION_LIMIT = 5_000`。

F-015: 文件 `agent/runtime/__init__.py` 第1-23行，从 `.constants` 导出 4 个常量，从 `.execution` 导出 `graph_loaded_for_execution`，从 `.sandbox` 导出 `configure_git_identity`、`ensure_sandbox_for_thread`、`get_cached_sandbox_backend`。

## 主 Agent（server.py）

F-016: 文件 `agent/server.py` 第1632-1703行，`get_agent` 返回 `create_deep_agent(model=main_model, system_prompt="", tools=static_tools, subagents=[_general_purpose_subagent(...), *([_browser_subagent(...)] if browser_tools else [])], skills=skill_sources, backend=agent_backend, middleware=[...])`。

F-017: 文件 `agent/server.py` 第1531-1569行，`static_tools` 列表包含 `http_request`、`fetch_url`、`web_search`、`approve_plan`、`background_execute`、`background_task`、`enter_plan_mode`、`save_plan`、`save_user_instructions`、`save_user_skill`、`delete_user_skill`、`linear_comment`、`linear_create_issue`、`linear_delete_issue`、`linear_get_issue`、`linear_get_issue_comments`、`linear_list_teams`、`linear_search_issues`、`linear_update_issue`、`list_threads`、`get_thread`、`manage_thread`、`manage_baby_sit`、`notify_automation_channel`、`open_pull_request`、`read_user_settings`、`request_pr_review`、`recreate_sandbox`、`report_platform_issue`、`schedule_thread_wakeup`、`slack_add_reaction`、`slack_move_thread`、`slack_read_thread_messages`、`slack_start_new_thread`、`slack_thread_reply`，以及 admin 线程时追加 `ADMIN_TOOLS`。

F-018: 文件 `agent/server.py` 第1570-1573行，`local_run` 时 `static_tools = [http_request, fetch_url, web_search]`；`stop_summary_mode` 时 `static_tools = [slack_read_thread_messages, slack_thread_reply]`。

F-019: 文件 `agent/server.py` 第1648-1701行，主 Agent middleware 列表（按序）：`PrepareAgentRunMiddleware(...)`、可选 `DynamicToolMiddleware`、`SanitizeToolInputsMiddleware()`、`ModelCallLimitMiddleware(run_limit=MODEL_CALL_RECURSION_LIMIT, exit_behavior="end")`、`ToolErrorMiddleware()`、可选 `ExcludeToolsMiddleware(excluded=STOP_SUMMARY_EXCLUDED_TOOLS)`（stop_summary 时）、`SubdirAgentsReadMiddleware()`、`ToolRetryMiddleware(max_retries=2, tools=["task"], retry_on=task_retry_on, on_failure=task_on_failure, initial_delay=1.0, max_delay=10.0)`、可选 `PullRequestCreationGuardMiddleware()`（非 local_run 时）、`WorkflowPushGuardMiddleware()`、`refresh_github_proxy_before_model`、可选 `check_message_queue_before_model`（非 stop_summary 时）、`TimeoutWrapupMiddleware()`、`DynamicContextMiddleware()`、`notify_step_limit_reached`、可选 `ModelFallbackMiddleware`、可选 `PlanModeMiddleware`、`SanitizeFireworksMessagesMiddleware()`、`SanitizeOpenAIResponsesMiddleware()`、`SanitizeThinkingBlocksMiddleware()`、`ModelCallTimeoutMiddleware()`（最内层）。

F-020: 文件 `agent/server.py` 第995行，`class PrepareAgentRunMiddleware(BasePrepareRunMiddleware)`；构造函数参数含 `thread_id`、`config`、`profile_login`、`repo_instructions`、`model_id`、`effort`、`title_model`、`source`、`user_email`、`linear_project_id`、`linear_issue_number`、`draft_prs`、`plan_mode`、`corridor_enabled`、`admin_environments`。

F-021: 文件 `agent/server.py` 第1591-1615行，`agent_backend = CompositeBackend(default=backend, routes=skill_routes)`；`skill_routes` 含 `BUNDLED_SKILLS_ROUTE`（只读 `FilesystemBackend(root_dir=BUNDLED_SKILLS_DIR, virtual_mode=True)`），云端运行时还含 `ORGANIZATION_SKILLS_ROUTE`（`StoreBackend`）和按 `profile_login` 的 `USER_SKILLS_ROUTE`；desktop 运行时含 `USER_SKILLS_ROUTE`（`StateBackend`）和 `desktop_artifact_routes`。

F-022: 文件 `agent/server.py` 第500行，`async def ensure_sandbox_for_thread(...)` 定义于 server.py；第626行 `async def recreate_sandbox_for_thread(...)`。

## Reviewer（reviewer.py）

F-023: 文件 `agent/reviewer.py` 第55行，`REVIEW_FINDING_CAP` 从 `.review.findings` 导入；`agent/review/findings.py` 第55行 `REVIEW_FINDING_CAP = 6`。

F-024: 文件 `agent/reviewer.py` 第98-109行，reviewer 工具集从 `.tools` 导入：`add_finding`、`fetch_review_diff`、`fetch_url`、`http_request`、`list_findings`、`publish_review`、`reply_to_finding_thread`、`resolve_finding_thread`、`update_finding`、`web_search`。

F-025: 文件 `agent/reviewer.py` 第129-334行，`REVIEWER_PROMPT_TEMPLATE` 字符串，占位符含 `{working_dir}`、`{repo_owner}`、`{repo_name}`、`{pr_number}`、`{review_finding_cap}`、`{historical_review_guidance}`、`{repo_checkout_note}`；模板规定 diff-anchor 纪律、严重级别 rubric（critical/high/medium/low）、9 步 review workflow、publish 前检查清单。

F-026: 文件 `agent/reviewer.py` 第353-368行，`def _reviewer_subagent(model: BaseChatModel) -> SubAgent`，返回 `name="reviewer"` 的 SubAgent 字典，`middleware=[SanitizeOpenAIResponsesMiddleware(), ModelCallTimeoutMiddleware()]`，描述为 "Reviews one explicit, disjoint file partition..."。

F-027: 文件 `agent/reviewer.py` 第928-930行，`class PrepareReviewerRunState(PrepareRunState)`，含 `NotRequired[str] diff_text` 与 `NotRequired[dict[str, dict[str, set[int]]] | None] diff_line_set`。

F-028: 文件 `agent/reviewer.py` 第933-971行，`async def _ensure_reviewer_sandbox_for_thread(thread_id, configurable)`，调用 `ensure_sandbox_for_thread(..., allow_replacement=True)`，注释说明 reviewer 沙箱仅含 checkout、`prepare_review_repo` 每次重新派生。

F-029: 文件 `agent/reviewer.py` 第974行，`class PrepareReviewerRunMiddleware(BasePrepareRunMiddleware)`，`state_schema = PrepareReviewerRunState`。

F-030: 文件 `agent/reviewer.py` 第552-594行，`def _build_first_review_context(...) -> str` 生成首次评审上下文；第597-643行 `def _build_re_review_context(...)` 生成重评审上下文（含 `last_reviewed_sha`、`existing_findings_block`）；第646-694行 `def _build_finding_reply_context(...)` 生成 finding 回复上下文。

F-031: 文件 `agent/reviewer.py` 第727-734行，`def _escape_for_data_block(text: str) -> str`，用正则 `_CLOSING_TAG_RE` 将包装标签的闭合标签重写为惰性 `</name_>` 形式，防止 PR 作者控制文本逃逸 XML 数据块。

## Analyzer（analyzer.py）

F-032: 文件 `agent/analyzer.py` 第66行，`STYLE_ANALYZER_MODEL_CALL_LIMIT = 80`。

F-033: 文件 `agent/analyzer.py` 第70-90行，`STYLE_ANALYZER_PROMPT` 字符串，占位符 `{repo_owner}`、`{repo_name}`、`{working_dir}`、`{mode}`、`{skill_path}`、`{reviewer_themes}`；指示 agent 读取 `skill_path` 指向的 SKILL.md 并通过 `save_review_style_prompt` 持久化。

F-034: 文件 `agent/analyzer.py` 第119行，`class PrepareAnalyzerRunMiddleware(BasePrepareRunMiddleware)`；第137行 `_prepare` 方法从 configurable 读取 `review_style_full_name`、`review_style_samples_text`、`analyzer_mode`（默认 `"bootstrap"`）、`review_style_github_token`。

F-035: 文件 `agent/analyzer.py` 第176-177行，`backend = CompositeBackend(default=default_backend, routes={SKILLS_ROUTE: StateBackend()})`。

F-036: 文件 `agent/analyzer.py` 第188-209行，`create_deep_agent(model=..., system_prompt="", tools=[save_review_style_prompt, read_finding_outcomes], backend=backend, skills=[SKILLS_ROUTE], middleware=[PrepareAnalyzerRunMiddleware(...), SanitizeToolInputsMiddleware(), ModelCallLimitMiddleware(run_limit=STYLE_ANALYZER_MODEL_CALL_LIMIT, exit_behavior="end"), ToolErrorMiddleware(), TimeoutWrapupMiddleware(), DynamicContextMiddleware(), SanitizeOpenAIResponsesMiddleware()])`。

## Scheduler（scheduler.py）

F-037: 文件 `agent/scheduler.py` 第19-30行，`class SchedulerState(TypedDict, total=False)`，字段：`schedule_id`、`task`、`watch_key`、`thread_id`、`agent_thread_id`、`run_id`、`prepare_run_id`、`channel_id`、`thread_ts`、`attempt`、`result`。

F-038: 文件 `agent/scheduler.py` 第33-54行，`async def _launch(state: SchedulerState, config: RunnableConfig) -> dict[str, Any]`：`task == "reconcile"` 时调用 `reconcile_stale_runs()`；`task == "baby_sit"` 时调用 `evaluate_watch(key)`；`task == BACKGROUND_TASK_CRON_KIND` 时调用 `monitor_background_tasks(thread_id)`；`task == "session_cost"` 时调用 `run_session_cost_refresh(state)`；否则调用 `launch_scheduled_agent_run(schedule_id)`。

## Reconcile（reconcile.py）

F-039: 文件 `agent/reconcile.py` 第18行，`_SEARCH_PAGE_SIZE = 100`。

F-040: 文件 `agent/reconcile.py` 第37行，`async def reconcile_stale_runs(*, max_age_seconds: int = 1800) -> dict[str, int]`；分页搜索 `status="busy"` 线程，列出其 `status="pending"` runs，取消 `created_at` 超过 `max_age_seconds` 的 run，调用 `client.runs.cancel_many(thread_id=..., run_ids=..., action="interrupt")`；返回 `{"threads_checked", "stale_runs", "cancelled"}`。

## Dispatch（dispatch.py）

F-041: 文件 `agent/dispatch.py` 第58行，`EVENT_STREAMING_V2_CONFIG_KEY = "__event_streaming_v2"`；第61-68行 `V2_RUN_STREAM_MODES: tuple[str, ...] = ("values", "updates", "messages", "custom", "tasks", "checkpoints")`。

F-042: 文件 `agent/dispatch.py` 第233-275行，`async def create_durable_run(thread_id, assistant_id, *, input, source, config=None, metadata=None, client=None, multitask_strategy="interrupt", durability="sync", if_not_exists="create", stream_resumable=True, after_seconds=None) -> Run`；设置 `stream_mode=list(V2_RUN_STREAM_MODES)`、`stream_subgraphs=True`、`stream_resumable=True`，条件附加 `webhook=COMPLETION_WEBHOOK_URL`。

F-043: 文件 `agent/dispatch.py` 第214-230行，`def prepare_run_config(config, metadata) -> RunConfig`：注入 `configurable.prepare_run_id = str(uuid.uuid4())` 与 `configurable[EVENT_STREAMING_V2_CONFIG_KEY] = True`，并将 `prepare_run_id` 写入 metadata。

F-044: 文件 `agent/dispatch.py` 第278-327行，`async def dispatch_agent_run(thread_id, content, configurable, *, source, input=None, context=None, people=None, channels=None, systems=None, assistant_id="agent", metadata=None, client=None, multitask_strategy="interrupt") -> Run`；当 `input is None` 时通过 `_dispatch_input` 或 `build_run_input` 构造输入，再调用 `create_durable_run`。

F-045: 文件 `agent/dispatch.py` 第165-201行，`COMPLETION_WEBHOOK_URL` 由环境变量 `COMPLETION_WEBHOOK_URL`（默认 `/webhooks/run-complete`）与 `RUN_COMPLETE_WEBHOOK_SECRET` 经 `_resolve_completion_webhook_url` 解析；当 secret 未设置或 URL 为相对/loopback 时返回 `None`。

## Chat（chat.py）

F-046: 文件 `agent/chat.py` 第77行，`CHAT_MODEL_CALL_LIMIT = 100`；第82行 `_EXCLUDED_TOOLS = frozenset({"execute", "write_file", "edit_file", "delete"})`。

F-047: 文件 `agent/chat.py` 第105-131行，`CHAT_PROMPT` 字符串：声明 "You have NO sandbox"，上下文以虚拟文件 `/pr/overview.md`、`/pr/diff.patch`、`/pr/findings.md` 加载；工具含 `read_repo_file(path, ref)`、`search_repo_code(query)`、`list_review_findings(status_filter)`、`web_search`、`fetch_url`。

F-048: 文件 `agent/chat.py` 第62-68行，chat 工具集：`fetch_url`、`list_review_findings`、`read_repo_file`、`search_repo_code`、`web_search`。

F-049: 文件 `agent/chat.py` 第85-102行，`def _chat_general_purpose_subagent() -> SubAgent`，覆盖 deepagents 默认通用子代理，middleware 含 `FilesystemMiddleware(tools=["read_file", "ls", "glob", "grep"])`、`SanitizeOpenAIResponsesMiddleware()`、`ModelCallTimeoutMiddleware()`。

## Baby-sit（baby_sit.py）

F-050: 文件 `agent/baby_sit.py` 第31-40行，`WATCH_NAMESPACE = ["baby_sit_watches"]`、`WATCH_CRON_KIND = "baby_sit_watch"`、`WATCH_SCHEDULE = "*/10 * * * *"`、`MAX_RETRIES_PER_HEAD = 3`、`MAX_DISPATCH_KEYS = 30`、`MAX_DELIVERY_IDS = 50`、`MAX_ALERT_KEYS = 30`、`MAX_EVALUATION_ERRORS = 3`、`CHECK_SET_SETTLE_MINUTES = 10`、`WATCH_LOCK_TTL_MINUTES = 5`。

F-051: 文件 `agent/baby_sit.py` 第67-89行，`class BabySitWatch(TypedDict)` 字段含 `key`、`active`、`thread_id`、`owner`、`repo`、`pr_number`、`pr_url`、`head_sha`、`head_ref`、`installation_id`、`run_config`、`source_context`、`retry_count`、`settled_check_key`、`settled_check_at`、`dispatch_keys`、`delivery_ids`、`alert_keys`、`evaluation_errors`、`cron_id`、`created_at`、`updated_at`。

F-052: 文件 `agent/baby_sit.py` 第96-97行，`def watch_key(owner, repo, pr_number) -> str` 返回 `f"{owner.strip().lower()}/{repo.strip().lower()}#{pr_number}"`。

F-053: 文件 `agent/baby_sit.py` 第43-64行，`@asynccontextmanager async def _watch_lock(key)`：用 `uuid5(NAMESPACE_URL, f"open-swe:baby-sit-lock:{key}")` 作为 lock thread id，`threads.create(if_exists="raise", ttl=WATCH_LOCK_TTL_MINUTES)` 获取锁，`ConflictError` 时 yield False，finally 删除。

F-054: 文件 `agent/baby_sit.py` 第470-474行，`async def evaluate_watch(key, *, token=None) -> str`：`async with _watch_lock(key) as acquired`，未获取返回 `"busy"`，否则调用 `_evaluate_watch`。

F-055: 文件 `agent/baby_sit.py` 第477-584行，`_evaluate_watch` 状态机返回值：watch 不存在返回 `"missing"`；非 active 返回 `"stopped"`；PR 关闭返回 `"merged"`/`"closed"`；CI 状态 `pending` 返回 `"pending"`；`success` 返回 `"settling"` 或完成消息；`blocked` 返回 triage 消息；超过 `MAX_RETRIES_PER_HEAD` 返回停止消息；失败指纹已存在返回 `"duplicate"`；否则 `dispatch_agent_run(..., multitask_strategy="enqueue")` 后返回 `"dispatched"`。

F-056: 文件 `agent/baby_sit.py` 第190行 `async def start_watch(...)`、第249行 `async def stop_watch(key) -> bool`、第587行 `async def handle_ci_webhook(payload, event_type, *, delivery_id=None) -> dict[str, int]`。

## Desktop（desktop.py）

F-057: 文件 `agent/desktop.py` 第15-16行，`def is_desktop_run(configurable) -> bool` 返回 `configurable.get("source") == "desktop"`。

F-058: 文件 `agent/desktop.py` 第39-44行，`def create_desktop_backend(configurable) -> LocalShellBackend`：返回 `LocalShellBackend(root_dir=resolve_desktop_project(configurable), virtual_mode=True, env={...})`，env 仅透传 `HOME`、`LANG`、`LC_ALL`、`PATH`、`SHELL`、`TMPDIR`。

F-059: 文件 `agent/desktop.py` 第54-72行，`async def desktop_artifact_routes(thread_id) -> dict[str, FilesystemBackend]`：为 `large_tool_results` 与 `conversation_history` 在 artifacts 根目录下创建子目录并返回 `FilesystemBackend(root_dir=..., virtual_mode=True)` 路由。

## Webapp / API（webapp.py, api/app.py）

F-060: 文件 `agent/webapp.py` 第1-5行，`from .api.app import app`，`__all__ = ["app"]`（兼容入口）。

F-061: 文件 `agent/api/app.py` 第21行，模块加载时调用 `pin_single_event_loop()`；第24-35行 `lifespan` 异步上下文管理器，启动时 `validate_sandbox_startup_config()`、`validate_local_dev_llm_config()`，关闭时 `await close_cached_models()`。

F-062: 文件 `agent/api/app.py` 第38-64行，`def create_app() -> FastAPI`：CORS 来源从 `DASHBOARD_ALLOWED_ORIGINS` 解析，禁止 `"*"`（`allow_credentials=True` 时抛 RuntimeError）；include_router 顺序：`dashboard_router`、`plan_router`、`workflow_approval_router`、`linear_webhook_router`、`slack_webhook_router`、`health_router`、`github_webhook_router`。第67行 `app = create_app()`。

## Prompt（prompt.py）

F-063: 文件 `agent/prompt.py` 第17行，`DEFAULT_PROMPT_PATH = os.environ.get("DEFAULT_PROMPT_PATH")`；第20-47行 `_load_default_prompt()` 从该路径或包资源 `agent.resources/default_prompt.md` 读取，将 `{`/`}` 转义为 `{{`/`}}`，包装在 "### Custom Instructions" 段落下。

F-064: 文件 `agent/prompt.py` 第53-113行，`OPEN_SWE_SHARED_BASE` 字符串：声明 "You are **Open SWE**, an open-source agent built on LangGraph and Deep Agents"，含 Concise Style、Structured Model Input（`<system-instructions>`/`<dynamic-context>`/`<input-message>`）、Core Behavior、Working in the Sandbox、Working with Code、Communication 段落；末尾强制 "You must ALWAYS call a tool in EVERY SINGLE TURN"。

F-065: 文件 `agent/prompt.py` 第123行，`def render_open_swe_shared_base(*, sandbox_file_downloads: bool) -> str`；第536行 `def construct_system_prompt(working_dir, dashboard_base_url="", linear_project_id="", linear_issue_number="", default_repo=None, plan_mode=False, plan_url=None, repo_custom_instructions=None, corridor_enabled=False, environment_name=None, environment_instructions=None, admin_environments=False, source="dashboard", slack_context=False, sandbox_file_downloads=False) -> str`。

## Review Findings（review/findings.py, review/reconcile.py）

F-066: 文件 `agent/review/findings.py` 第100-141行，`class Finding(TypedDict)` 核心字段：`id: str`、`severity: Severity`、`confidence: Confidence`、`category: str`、`title: str`、`file: str`、`start_line: int | None`、`end_line: int | None`、`side: DiffSide`、`in_diff: bool`、`description: str`、`suggestion: str | None`、`status: FindingStatus`、`first_seen_sha: str`、`last_confirmed_sha: str`、`fingerprint: str`，以及多个 `github_review_*` 字段与 `last_human_reply_*`、`interactions: list[FindingInteraction]`。

F-067: 文件 `agent/review/findings.py` 第208行 `def new_finding(...)`、第377行 `async def list_findings(thread_id) -> list[Finding]`、第392行 `async def replace_findings(thread_id, findings)`、第438行 `async def mutate_findings(...)`、第476行 `async def append_finding(thread_id, finding) -> AppendFindingResult`、第497行 `async def update_finding_fields(...)`、第541行 `async def append_finding_interaction(...)`。

F-068: 文件 `agent/review/reconcile.py` 第253-281行，`async def reconcile_findings_with_review_threads(reviewer_thread_id: str, review_threads: list[ReviewThread]) -> list[Finding]`：读取 `list_findings`，用 `_index_review_threads` 建立 by_thread_id/by_comment_id/by_marker_id 索引，对每个 finding 调用 `_find_review_threads_for_finding`、`_sync_publication_identity`、`_sync_latest_human_reply`、`_sync_thread_status`，有更新则 `replace_findings`。

## Sandbox 状态（utils/sandbox_state.py）

F-069: 文件 `agent/utils/sandbox_state.py` 第32行，`class SandboxUnreachableError(RuntimeError)`；第53行 `class SandboxBackendProxy(BaseSandbox)`；第320行 `SANDBOX_BACKENDS: dict[str, SandboxBackendProxy] = {}`。

F-070: 文件 `agent/utils/sandbox_state.py` 第347行 `def get_or_create_sandbox_backend_proxy(...)`、第402行 `async def get_sandbox_backend(thread_id) -> SandboxBackendProxy`、第323行 `def unwrap_sandbox_backend(...)`。
