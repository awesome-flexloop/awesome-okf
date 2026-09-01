---
type: concept
scope: open-swe
name: agent-architecture
version: "0.1.0"
source: https://github.com/langchain-ai/open-swe
description: Open SWE Agent 架构——五个图工厂、每线程无状态 Agent、模型优先级与 middleware 洋葱圈
---

# Agent 架构

## 图工厂模式

Open SWE 的五个图都是**工厂函数**，而非单例 Agent。LangGraph runtime 在每次线程运行时调用对应工厂，工厂解析运行时配置并返回一个全新编译的图。

```python
# agent/server.py:1279
async def get_agent(config: RunnableConfig) -> Pregel:
    configurable = config.get("configurable") or {}
    thread_id = configurable.get("thread_id")
    config["recursion_limit"] = DEFAULT_RECURSION_LIMIT   # 9999

    # 非执行上下文（schema 生成等）返回空 agent
    if thread_id is None or not graph_loaded_for_execution(config):
        return create_deep_agent(system_prompt="", tools=[]).with_config(config)

    # ...解析沙箱、模型、工具、middleware...
    return create_deep_agent(...).with_config(config)
```

`graph_loaded_for_execution(config)`（来自 `agent.runtime.execution`）判断图是否真正被执行加载。在 schema 生成或非执行路径中，工厂返回一个无沙箱、无工具的空 `create_deep_agent`，避免副作用（F-008）。

五个工厂均通过 `traced_graph_factory(...)` 包装为 `traced_*` 导出，接入 LangSmith tracing 项目：agent/chat 用 `AGENT_TRACING_PROJECT`，reviewer/analyzer 用 `REVIEW_TRACING_PROJECT`（F-009 ~ F-012）。

## 无状态 Agent + 有状态沙箱

Agent 对象本身不持有 per-thread 状态。每次运行：

1. 工厂从 `configurable` 读取 `thread_id`；
2. `ensure_sandbox_for_thread(thread_id, ...)` 获取或重连该线程的沙箱；
3. 从线程元数据/team 设置/profile 解析模型与指令；
4. 构造全新的工具列表和 middleware 栈。

可变状态寄居在两处（F-069、F-070）：

- **沙箱**：文件系统、git worktree、安装的依赖。`SANDBOX_BACKENDS` 是进程内 dict，以 `thread_id` 为 key；`sandbox_id` 持久化在线程元数据中跨进程存活。
- **线程元数据**：`sandbox_id`、模型设置、`owner_login`、repo 指令等。

### 沙箱不可达时不替换

`ensure_sandbox_for_thread` 处理三种情况：内存命中 → ping (`echo ok`) 刷新 GitHub proxy；元数据有 id 但无缓存 → 重连；都没有 → 新建。只有第三种真正创建。已存在但不可达的沙箱抛 `SandboxUnreachableError`，**不替换**——替换会得到一个空沙箱，在伪装成恢复的同时销毁未提交工作。主 Agent 在 `PrepareAgentRunMiddleware` 中捕获该异常并通知用户（F-020 周边）。

Reviewer 是唯一例外：`_ensure_reviewer_sandbox_for_thread` 传 `allow_replacement=True`，因为 reviewer 沙箱只含一个 checkout，`prepare_review_repo` 每次运行都重新派生，reviewer 线程一个 PR 一个且寿命长于沙箱（F-028）。

## 模型解析优先级

模型 ID 与 reasoning effort 按以下优先级解析（后者覆盖前者）：

1. **Per-thread 配置**（`configurable.agent_model_id` / `agent_effort`）——webhook/UI 设置，唯一能把线程移出已存设置的因素；
2. **已存线程设置**（thread metadata 中的 `model_id`/`effort`）；
3. **Dashboard profile 覆盖**（按 GitHub login 的 `load_profile`）；
4. **Team 默认模型**（`get_team_default_model_pair("agent")`）。

解析后再经 `gate_fable_model` 门控，并构造 `provider_model_kwargs(...)`（`max_tokens=64000`）。若设置了 `LLM_FALLBACK_MODEL_ID` 或模型自带默认 fallback 且与主模型不同，则追加 `ModelFallbackMiddleware`（F-016、F-019）。

## 工具装配

主 Agent 的 `static_tools` 是一份精心策展的扁平列表（F-017），涵盖网络检索、计划模式、Linear、线程管理、PR/CI、Slack 等。内置 deepagents 工具（`read_file`/`write_file`/`edit_file`/`execute`/`task` 等）由 `create_deep_agent` 自身添加，不重复登记。

工具集按运行模式裁剪：

- **Desktop 本地运行**（`source == "desktop"`）：仅 `[http_request, fetch_url, web_search]`（F-018）；
- **Stop-summary 模式**：仅 `[slack_read_thread_messages, slack_thread_reply]`；
- **Slack 禁用**时从静态列表中移除 Slack 工具；
- **Admin 线程**追加 `ADMIN_TOOLS`；
- **集成工具**（Corridor/Observability/Currents/Notion/Browser）通过 `DynamicToolMiddleware` 动态注入，不污染静态列表（F-019）。

## Middleware 洋葱圈

主 Agent 的 middleware 按严格顺序装配，外层包裹内层（F-019）：

```
PrepareAgentRunMiddleware        # 最外层：沙箱/模型/prompt 准备
  DynamicToolMiddleware          # （可选）集成工具注入
    SanitizeToolInputsMiddleware
      ModelCallLimitMiddleware   # run_limit=5000, exit_behavior="end"
        ToolErrorMiddleware
          ExcludeToolsMiddleware # （可选，stop_summary）
            SubdirAgentsReadMiddleware
              ToolRetryMiddleware # max_retries=2, tools=["task"]
                PullRequestCreationGuardMiddleware  # （非 local）
                  WorkflowPushGuardMiddleware
                    refresh_github_proxy_before_model
                      check_message_queue_before_model
                        TimeoutWrapupMiddleware
                          DynamicContextMiddleware
                            notify_step_limit_reached
                              ModelFallbackMiddleware  # （可选）
                                PlanModeMiddleware      # （可选）
                                  SanitizeFireworksMessagesMiddleware
                                    SanitizeOpenAIResponsesMiddleware
                                      SanitizeThinkingBlocksMiddleware
                                        ModelCallTimeoutMiddleware  # 最内层
```

### 顺序为何重要

- **`ModelCallTimeoutMiddleware` 在最内层**：其截止时间覆盖 provider 调用本身，超时向外升级到 `ModelFallbackMiddleware` 触发降级模型。
- **`check_message_queue_before_model`** 在 model 调用前拉取中途到达的 Linear/Slack 消息并注入为用户消息——这是"Agent 工作时给它发消息也能响应"的机制。
- **`refresh_github_proxy_before_model`** 在每次模型调用前刷新 GitHub proxy token。
- **`ToolRetryMiddleware`** 仅对子 Agent `task` 工具重试 2 次；子 Agent 编译为独立图，父 middleware **不**包裹其 model 调用，因此每个 SubAgent spec 自带 `ModelCallTimeoutMiddleware`（F-026、F-049）。

### "每轮必须调工具"不变量

系统提示 `OPEN_SWE_SHARED_BASE` 末尾强制要求 "You must ALWAYS call a tool in EVERY SINGLE TURN"（F-064）。配合 after-model hook 逻辑（`ensure_no_empty_msg` / `check_message_queue_before_model` 之后），当模型发出无 tool call 的消息时，重新注入合成的 `no_op`/`confirming_completion` tool call，防止运行在任务中途提前终止。

## Backend 与 Skills 路由

`agent_backend = CompositeBackend(default=backend, routes=skill_routes)` 把默认沙箱与只读 skills 路由组合（F-021）：

- `BUNDLED_SKILLS_ROUTE`：包内自带技能，只读 `FilesystemBackend(virtual_mode=True)`；
- `ORGANIZATION_SKILLS_ROUTE`：组织级技能，`StoreBackend`（云端运行时）；
- `USER_SKILLS_ROUTE`：按 `profile_login` 的用户技能，`StoreBackend` 或 desktop 下的 `StateBackend`；
- Desktop 运行时额外通过 `desktop_artifact_routes` 把 `large_tool_results`/`conversation_history` 路由到临时目录，避免 scratch 文件污染用户仓库（F-059）。

Skills 通过虚拟文件 `/skills/` 提供，由 `CompositeBackend` 路由，**永不写入沙箱**。

## 子 Agent

主 Agent 装配两类子 Agent（F-016）：

- **通用子 Agent**（`_general_purpose_subagent`）：继承主模型与工具（去掉 `background_execute`/`background_task`），可委派任务；
- **浏览器子 Agent**（`_browser_subagent`）：仅在加载了 browser 工具时存在。

Reviewer 有自己的 `reviewer` 子 Agent，最多委派一次评审轮次，给它不重叠的文件列表，只返回候选缺陷，由父级校验后记录 finding（F-026）。Chat agent 覆盖默认通用子 Agent，用 `FilesystemMiddleware(tools=["read_file","ls","glob","grep"])` 保持只读（F-049）。

## 相关概念

- 总览 — Open SWE 是什么
- Dispatch-Review 循环 — durable dispatch 与 findings 模型
- Scheduler 与 Reconcile — cron 扇出与安全网
- 架构参考 — 完整函数与常量清单
