---
type: spec
scope: open-swe
name: insights
version: "0.1.0"
source: https://github.com/langchain-ai/open-swe
description: Open SWE 深度洞察——从源码中提炼的多图编排、durable dispatch、review-reconcile 循环与 LangGraph 中间件架构
---

# Open SWE 深度洞察

## 洞察 1：五个 LangGraph 图工厂，每线程无状态 Agent + 有状态沙箱

**陈述**：Open SWE 不是"一个 Agent"，而是由 `langgraph.json` 注册的五个独立图（agent / reviewer / analyzer / chat / scheduler）组成的多 Agent 系统。每个图都是一个工厂函数（`get_agent` / `get_reviewer_agent` / `get_analyzer` / `get_chat_agent` / `get_scheduler`），在每次线程运行时被调用，构造一个全新的 `create_deep_agent(...)` 实例。Agent 自身无状态——所有 per-thread 状态寄居在线程元数据 + 隔离沙箱中。

**证据**：
- `langgraph.json` 声明 5 个 graphs 入口（F-005）。
- `get_agent` 在 `thread_id is None or not graph_loaded_for_execution(config)` 时返回空 `create_deep_agent(system_prompt="", tools=[])`，说明图工厂可在非执行上下文（如 schema 生成）中被无副作用调用（F-008）。
- 主 Agent 工厂 `get_agent` 每次运行解析 GitHub token、get-or-create 沙箱、解析 team/profile/per-thread 模型与 effort、构造全新工具列表和 middleware 栈（F-016、F-019、F-020）。
- `SANDBOX_BACKENDS` 是进程内 dict，以 `thread_id` 为 key；`sandbox_id` 持久化在线程元数据中跨进程存活（F-069、F-070）。

**反常识**：直觉上"Agent 状态"应存于 Agent 对象或 LangGraph state 中，但 Open SWE 把可变工作状态全部下放到沙箱（文件系统、git worktree）和线程元数据，图工厂每次返回全新实例。这使得图工厂是纯装配逻辑、可安全重入，也解释了为什么沙箱生命周期（ping/reconnect/create，且不可达时拒绝替换）是整个系统最微妙的部分——替换沙箱等于清空 Agent 的"记忆"。

**行动**：理解 Open SWE 时，应沿"图工厂 → 沙箱生命周期 → 线程元数据"三条线追踪，而非在 Agent 对象内找状态字段。新增图时在 `langgraph.json` 注册入口并提供 `get_*` 工厂；新增 per-thread 状态时优先考虑沙箱文件或线程 metadata，而非图实例属性。

## 洞察 2：Durable Dispatch 单一契约 + reconcile 安全网构成闭环

**陈述**：所有 Slack/Linear/GitHub/dashboard 触发都汇聚到 `dispatch_agent_run` → `create_durable_run` 这一个持久化分发契约。它默认 `multitask_strategy="interrupt"`（跟进消息中断活跃运行并带完整历史恢复）、`durability="sync"`（每步前 checkpoint）、`stream_resumable=True`（事件流可重放），并通过 completion webhook 让每次运行都有终态信号。`reconcile_stale_runs` 作为安全网，定期取消卡在 `pending` 超过 30 分钟的运行，释放 busy 线程。

**证据**：
- `create_durable_run` 默认参数 `multitask_strategy="interrupt"`、`durability="sync"`、`stream_resumable=True`，固定 `stream_mode=V2_RUN_STREAM_MODES`、`stream_subgraphs=True`（F-042）。
- `prepare_run_config` 为每次运行注入唯一 `prepare_run_id`（uuid）和 `__event_streaming_v2` 标记（F-043）。
- `COMPLETION_WEBHOOK_URL` 仅在 secret 已设置且 URL 为绝对非 loopback 时附加，相对/localhost URL 会降级为 None 并告警，避免平台 422 毒化每次 `runs.create`（F-045）。
- `reconcile_stale_runs(max_age_seconds=1800)` 分页遍历 `status="busy"` 线程，对其上 `status="pending"` 且超龄的 run 执行 `cancel_many(action="interrupt")`（F-039、F-040）。
- scheduler 图的 `_launch` 节点把 `"reconcile"` 任务路由到 `reconcile_stale_runs()`，说明 reconcile 本身也是由 cron 调度的图运行（F-038）。

**反常识**：分发层看似只是"调一下 SDK"，但 Open SWE 把它提升为一等契约——v2 流式标记、webhook 终态、interrupt 策略缺一不可，否则 dashboard 看不到外部触发的运行（无 stop 按钮、无子 Agent 卡片）。reconcile 不是异常路径，而是与 completion webhook 配对的常态安全网：webhook 是"乐观终态"，reconcile 是"悲观兜底"。

**行动**：新增触发入口时必须走 `dispatch_agent_run`，不要直接 `client.runs.create`。部署时必须把 `COMPLETION_WEBHOOK_URL` 设为绝对 https URL 并配置 secret，否则终态回复静默失效；scheduler cron 必须持续运行以驱动 reconcile。

## 洞察 3：Reviewer 的 findings 单一演进模型 + diff-anchor 纪律 + GitHub thread 双向协调

**陈述**：Reviewer 图围绕一个"单一、持续演进的 findings 列表"模型运作：首次评审用 `add_finding` 记录候选，重评审对已有 finding 做 `update_finding(status="resolved")` 或新增，作者回复用 `resolve_finding_thread(status="dismissed")`。每个 finding 必须锚定到 PR diff 内的具体变更行（`add_finding` 拒绝 in-diff 外的发现）。`reconcile_findings_with_review_threads` 在每次评审前把本地 findings 与 GitHub 上的实际 review thread 状态双向同步（发布身份、最新人工回复、线程 resolved 状态）。

**证据**：
- `Finding` TypedDict 含 `in_diff: bool`、`start_line/end_line`、`side: DiffSide`、`fingerprint`、`status: FindingStatus` 及全套 `github_review_*` 字段（F-066）。
- `REVIEW_FINDING_CAP = 6`，reviewer prompt 明确 "Out-of-diff findings are disabled. `add_finding` rejects any finding whose `start_line..end_line` is not part of the PR diff"（F-023、F-025）。
- 三种上下文构建函数分别处理首次评审、新 commit 的重评审、作者对 finding 的回复，对应 finding 的三种生命周期事件（F-030）。
- `PrepareReviewerRunState` 额外携带 `diff_text` 与 `diff_line_set`，在 runnable config 中传递，使 `add_finding` 能在创建时即校验 diff 归属（F-027、F-029）。
- `reconcile_findings_with_review_threads` 通过 by_thread_id/by_comment_id/by_marker_id 三套索引匹配 finding 与 GitHub thread，同步 publication identity、latest human reply、thread status，有更新才 `replace_findings`（F-068）。
- reviewer 沙箱以 `allow_replacement=True` 创建——它只含一个 checkout，`prepare_review_repo` 每次重新派生，不可达时可安全替换（F-028）。

**反常识**：代码评审通常被建模为"每次产出一份评审报告"，但 Open SWE 把它建模为"一组有状态 finding 对象随 PR 演进而演进"。这使得重评审和作者回复成为对同一批对象的状态转换，而非重新生成全文。diff-anchor 纪律把"可申报的缺陷"严格约束在本次 diff 行内——即使能证明未变更调用点存在回归，也不能申报，这是对 LLM "扩散式推测"的强约束。

**行动**：扩展 reviewer 时，新工具应操作 finding 对象（add/update/resolve）而非生成自由文本；新增 finding 字段需同步 `Finding` TypedDict、`new_finding`、`replace_findings` 与 reconcile 同步逻辑。评审规则变更应写入 prompt 的 "bar" 与 "Do NOT file" 段落，并保持 diff-anchor 校验在工具层强制执行。

## 洞察 4：基于 LangGraph + Deep Agents 的洋葱圈中间件与沙箱后端组合

**陈述**：Open SWE 在 `deepagents.create_deep_agent` 之上，通过有序 middleware 栈（洋葱圈模型）横切注入横切关注点：工具输入消毒、模型调用限额、工具错误兜底、消息队列注入、空消息补刀、步数通知、沙箱熔断、模型降级、计划模式、思维块消毒、调用超时。后端用 `CompositeBackend` 把默认沙箱与只读 skills 路由（bundled/organization/user）组合。模型解析有四级优先级（per-thread > stored thread settings > profile override > team default），并支持 fallback 模型。

**证据**：
- 主 Agent middleware 列表按严格顺序装配，`ModelCallTimeoutMiddleware` 位于最内层以覆盖 provider 调用本身，超时向外升级到 `ModelFallbackMiddleware`（F-019）。
- `ensure_no_empty_msg`（对应 `check_message_queue_before_model` 之后的 after-model hook 逻辑）在模型发出无 tool call 的消息时重新注入合成 tool call，配合系统提示 "You must ALWAYS call a tool in EVERY SINGLE TURN" 防止运行提前终止（F-064、F-019）。
- `ToolRetryMiddleware(max_retries=2, tools=["task"], ...)` 仅对子 Agent `task` 工具做重试；子 Agent 编译为独立图，父 middleware 不包裹其 model 调用，因此子 Agent 携带自己的 `ModelCallTimeoutMiddleware`（F-019、F-026、F-049）。
- `CompositeBackend(default=backend, routes=skill_routes)` 把 `/skills/` 等虚拟路径路由到 `FilesystemBackend`/`StoreBackend`/`StateBackend`，skills 永远不写入沙箱（F-021、F-035）。
- 模型优先级链在 `get_agent` 中依次应用 team default → profile override → stored thread settings → per-thread configurable，后者是唯一能把线程移出 stored 设置的因素（F-016 周边逻辑）。
- Reviewer 使用精简 middleware 栈（SanitizeToolInputs/ModelCallLimit/ToolError/SanitizeThinkingBlocks 等），Chat agent 无沙箱且 `_EXCLUDED_TOOLS` 剥离写工具（F-024 周边、F-046、F-049）。

**反常识**：中间件顺序不是实现细节而是正确性条件——`ModelCallTimeoutMiddleware` 必须在最内层才能让超时触发外层 fallback；`refresh_github_proxy_before_model` 必须在 model 调用前；`check_message_queue_before_model` 注入的中途消息必须在 `ToolErrorMiddleware` 之后、model 之前。这种顺序敏感性意味着 middleware 列表不能随意重排，也不能用"集合"语义。此外，"Agent 必须每轮调工具"不是建议而是由 `ensure_no_empty_msg` 强制执行的运行时不变量。

**行动**：新增 middleware 时放入 `agent/middleware/`，从 `__init__.py` 导出，并在 `get_agent` 的 `middleware=[...]` 列表中按语义位置插入——包裹范围越广（如错误兜底）越靠外，越接近 provider 调用（如超时、消息消毒）越靠内。新集成工具通过 `DynamicToolMiddleware` 注入而非加入静态 `static_tools`，避免污染所有运行。
