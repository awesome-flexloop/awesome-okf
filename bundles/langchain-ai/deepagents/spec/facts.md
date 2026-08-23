---
type: spec
scope: deepagents
name: facts
version: "0.7.8"
source: https://github.com/langchain-ai/deepagents
description: deepagents 源码事实验证清单——从核心 SDK、ACP、CLI 及 lca-deepagents 变体中提取的编号事实
---

# deepagents 事实清单

## 项目元信息

F-001: 文件 `libs/deepagents/pyproject.toml` 第2-5行，项目名称为 `deepagents`，版本 `0.7.8`，描述为 "Production-ready, extensible agent harness with a built-in filesystem and context management, sub-agent delegation, skills, and long-term memory."，许可证 MIT，要求 Python `>=3.11,<4.0`。

F-002: 文件 `libs/deepagents/pyproject.toml` 第22-30行，核心依赖包括 `langchain>=1.3.16,<2.0.0`、`langchain-core>=1.6.0,<2.0.0`、`langchain-anthropic>=1.6.1,<2.0.0`、`langchain-google-genai>=4.3.4,<5.0.0`、`langsmith>=0.11.1`、`packaging>=23.2`、`wcmatch>=11.0`。可选依赖组包括 `aws`、`quickjs`、`video`。

F-003: 文件 `libs/deepagents/deepagents/_version.py` 第21行，`__version__ = "0.7.8"`，通过 release-please 注解 `# x-release-please-version` 与 pyproject.toml 保持同步。

F-004: 文件 `README.md` 第24-31行，Deep Agents 定位为 "batteries-included agent harness"，四大原则：Opinionated（长周期多步任务的默认调优）、Extensible（无需 fork 即可覆盖或替换任何组件）、Model-agnostic（支持任何支持 tool calling 的 LLM）、Production-ready（基于 LangGraph，支持流式、持久化、检查点）。

## 公共 API（deepagents/__init__.py）

F-005: 文件 `libs/deepagents/deepagents/__init__.py` 第4-7行，从 `deepagents.graph` 导入 `DeepAgentState` 和 `create_deep_agent`。

F-006: 文件 `libs/deepagents/deepagents/__init__.py` 第8-16行，导入的中间件类包括：`AsyncSubAgent`、`AsyncSubAgentMiddleware`、`CompiledSubAgent`、`FilesystemMiddleware`、`FilesystemPermission`、`FsToolName`、`MemoryMiddleware`、`RubricMiddleware`、`SubAgent`、`SubAgentMiddleware`。

F-007: 文件 `libs/deepagents/deepagents/__init__.py` 第17-26行，导入的 profile 类包括：`GeneralPurposeSubagentProfile`、`HarnessProfile`、`HarnessProfileConfig`、`register_harness_profile`、`ProviderProfile`、`register_provider_profile`。

F-008: 文件 `libs/deepagents/deepagents/__init__.py` 第28-48行，`__all__` 列表共17个公开符号，包含上述所有类和函数及 `__version__`。

## 核心图组装（graph.py）

F-009: 文件 `libs/deepagents/deepagents/graph.py` 第70-73行，`DeepAgentState` 继承自 `AgentState`，其 `messages` 字段使用 `Annotated[list[AnyMessage], DeltaChannel(_messages_delta_reducer, snapshot_frequency=50)]`，将检查点增长从 O(N²) 降至 O(N)。

F-010: 文件 `libs/deepagents/deepagents/graph.py` 第140-148行，`_build_default_model()` 返回 `ChatAnthropic(model_name="claude-sonnet-4-6")`。`get_default_model()` 自 0.5.3 起标记 `@deprecated`，将在 1.0.0 移除。

F-011: 文件 `libs/deepagents/deepagents/graph.py` 第238-253行，`_REQUIRED_MIDDLEWARE` 元组包含两个不可排除的脚手架中间件：`FilesystemMiddleware` 和 `SubAgentMiddleware`。通过 `HarnessProfile.excluded_middleware` 排除它们会引发 `ValueError`。

F-012: 文件 `libs/deepagents/deepagents/graph.py` 第268-288行，`create_deep_agent()` 函数签名包含参数：`model`、`tools`、`system_prompt`、`middleware`、`subagents`、`skills`、`memory`、`permissions`、`backend`、`interrupt_on`、`response_format`、`state_schema`、`context_schema`、`checkpointer`、`store`、`debug`、`name`、`cache`。返回类型为 `CompiledStateGraph`。

F-013: 文件 `libs/deepagents/deepagents/graph.py` 第291-296行，默认内置工具包括：`ls`、`read_file`、`write_file`、`edit_file`、`glob`、`grep`（文件操作）、`execute`（shell 命令）、`task`（调用子代理）。

F-014: 文件 `libs/deepagents/deepagents/graph.py` 第362-391行，主代理中间件栈顺序：
- 基础栈：`SkillsMiddleware`（如有 skills）→ `FilesystemMiddleware` → `SubAgentMiddleware`（如有内联子代理）→ `SummarizationMiddleware` → `PatchToolCallsMiddleware` → `AsyncSubAgentMiddleware`（如有异步子代理）
- 用户中间件插入点
- 尾部栈：Harness profile `extra_middleware` → `_ToolExclusionMiddleware` → PromptCaching 中间件 → `MemoryMiddleware`（如有 memory）→ `HumanInTheLoopMiddleware`（如有 interrupt_on）

F-015: 文件 `libs/deepagents/deepagents/graph.py` 第627行，默认 backend 为 `StateBackend()`。

F-016: 文件 `libs/deepagents/deepagents/graph.py` 第935-943行，最终通过 `.with_config()` 设置 `recursion_limit: 9999` 和 metadata（`ls_integration: "deepagents"`、`lc_versions`、`lc_agent_name`）。

## 子代理系统（middleware/subagents.py）

F-017: 文件 `libs/deepagents/deepagents/middleware/subagents.py` 第36-164行，`SubAgent` 是 `TypedDict`，必填字段为 `name`、`description`、`system_prompt`，可选字段包括 `tools`、`model`、`middleware`、`interrupt_on`、`skills`、`permissions`、`response_format`。

F-018: 文件 `libs/deepagents/deepagents/middleware/subagents.py` 第167-244行，`CompiledSubAgent` 是 `TypedDict`，必填字段为 `name`、`description`、`runnable`（类型 `Runnable`），支持传入预编译的 `create_agent()` 或自定义 LangGraph 图。

F-019: 文件 `libs/deepagents/deepagents/middleware/subagents.py` 第301-306行，`GENERAL_PURPOSE_SUBAGENT` 常量定义了名为 `"general-purpose"` 的默认子代理，其描述为 "General-purpose agent for researching complex questions..."，系统提示为 `DEFAULT_SUBAGENT_PROMPT`。

F-020: 文件 `libs/deepagents/deepagents/middleware/subagents.py` 第252-269行，`_EXCLUDED_STATE_KEYS` 集合包含 `"messages"`、`"todos"`、`"structured_response"`，这些状态键在传递给子代理和从子代理返回时被排除。中间件私有状态字段也被排除。

F-021: 文件 `libs/deepagents/deepagents/middleware/subagents.py` 第272-282行，`TaskToolSchema` 是 `task` 工具的 Pydantic 输入模型，包含 `description`（详细任务描述）和 `subagent_type`（子代理类型名）两个字段。

F-022: 文件 `libs/deepagents/deepagents/middleware/subagents.py` 第474-512行，`_return_command_with_state_update()` 从子代理结果中提取响应：优先使用 `structured_response`（通过 `model_dump_json()` 或 `json.dumps()` 序列化），否则回溯最后一条非空 `AIMessage` 文本。结果通过 `Command(update=...)` 返回给父代理。

F-023: 文件 `libs/deepagents/deepagents/middleware/subagents.py` 第608-742行，`SubAgentMiddleware` 类继承 `AgentMiddleware`，构造函数接收 `backend`、`subagents`、`system_prompt`、`task_description`、`private_state_keys`、`state_schema`。它通过 `wrap_model_call`/`awrap_model_call` 在每次模型调用前注入子代理使用说明。

## 异步子代理（middleware/async_subagents.py）

F-024: 文件 `libs/deepagents/deepagents/middleware/async_subagents.py` 第34-77行，`AsyncSubAgent` 是 `TypedDict`，必填字段为 `name`、`description`、`graph_id`，可选字段为 `url` 和 `headers`。通过 LangGraph SDK 连接远程 Agent Protocol 服务器。

F-025: 文件 `libs/deepagents/deepagents/middleware/async_subagents.py` 第80-119行，`AsyncTask` 是持久化在代理状态中的异步任务跟踪结构，字段包括 `task_id`、`agent_name`、`thread_id`、`run_id`、`status`、`created_at`、`last_checked_at`、`last_updated_at`。

F-026: 文件 `libs/deepagents/deepagents/middleware/async_subagents.py` 第1-9行模块文档，异步子代理使用 LangGraph SDK 在远程 Agent Protocol 服务器上启动后台运行，立即返回 task ID，允许主代理监控进度和发送更新。兼容 LangGraph Platform（托管）和自托管服务器。

## 文件系统中间件（middleware/filesystem.py）

F-027: 文件 `libs/deepagents/deepagents/middleware/filesystem.py` 第1行，模块提供文件系统工具中间件。第38行导入 `CompositeBackend`、`FilesystemBackend`、`LocalShellBackend`、`StateBackend`。第40-60行从 `backends.protocol` 导入 `BackendProtocol`、`SandboxBackendProtocol` 及结果类型（`ReadResult`、`WriteResult`、`EditResult`、`GlobResult`、`GrepResult`、`LsResult`、`ExecuteResponse` 等）。

F-028: 文件 `libs/deepagents/deepagents/middleware/filesystem.py` 第120行，`FilesystemOperation = Literal["read", "write"]` 定义文件系统操作类型。

F-029: 文件 `libs/deepagents/deepagents/graph.py` 第454-478行，`permissions` 参数接受 `FilesystemPermission` 规则列表，规则按声明顺序求值，首匹配优先。`mode` 可为 `"allow"`（默认）、`"deny"`、`"interrupt"`（通过 `HumanInTheLoopMiddleware` 暂停等待人工审批）。子代理除非指定自己的 `permissions`，否则继承父代理规则。

## 上下文管理（middleware/summarization.py）

F-030: 文件 `libs/deepagents/deepagents/middleware/summarization.py` 第1-17行模块文档，提供两个中间件类：`SummarizationMiddleware`（token 使用量超过阈值时自动压缩对话）和 `SummarizationToolMiddleware`（暴露 `compact_conversation` 工具供按需触发）。

F-031: 文件 `libs/deepagents/deepagents/middleware/summarization.py` 第44-51行，卸载的消息以 Markdown 格式存储在 `/conversation_history/{session_id}.md`，Base64 媒体单独写入 `<artifacts_root>/conversation_history/media/` 并通过路径引用。

F-032: 文件 `libs/deepagents/deepagents/middleware/summarization.py` 第113-117行，`DEEPAGENTS_DEFAULT_SUMMARY_PROMPT` 在 LangChain 的 `DEFAULT_SUMMARY_PROMPT` 基础上插入媒体引用说明 addendum，位于 `<messages>` 标记之前。

## 内存与技能（middleware/memory.py, middleware/skills.py）

F-033: 文件 `libs/deepagents/deepagents/middleware/memory.py` 第1-5行，`MemoryMiddleware` 实现 AGENTS.md 规范（https://agents.md/），从可配置源加载内存/上下文并注入系统提示。与 skills（按需工作流）不同，memory 始终加载。

F-034: 文件 `libs/deepagents/deepagents/middleware/memory.py` 第37-39行，多个 memory 源按顺序加载并拼接，后出现的源在组合提示中位于后面。HTML 注释（`<!-- ... -->`）在注入前被剥离。

F-035: 文件 `libs/deepagents/deepagents/middleware/skills.py` 第1-14行，`SkillsMiddleware` 实现 Anthropic 的 agent skills 模式（渐进式披露），从后端存储的可配置源加载技能。源按顺序加载，同名技能后加载者覆盖前者（last one wins），支持 base → user → project → team 分层。

F-036: 文件 `libs/deepagents/deepagents/middleware/skills.py` 第22-44行，每个技能是一个包含 `SKILL.md` 文件的目录，SKILL.md 使用 YAML frontmatter，字段包括 `name`（最大64字符，小写字母数字和连字符）、`description`（最大1024字符）、`path`，可选 `license`、`compatibility`、`metadata`、`allowed_tools`。

## 后端系统（backends/）

F-037: 文件 `libs/deepagents/deepagents/backends/__init__.py` 第1-23行，公开后端类包括：`CompositeBackend`、`ContextHubBackend`、`FilesystemBackend`、`LangSmithSandbox`、`LocalShellBackend`、`StateBackend`、`StoreBackend`，以及协议 `BackendProtocol` 和常量 `DEFAULT_EXECUTE_TIMEOUT`、`NamespaceFactory`。

F-038: 文件 `libs/deepagents/deepagents/backends/protocol.py` 第1-6行，`BackendProtocol` 定义所有后端实现必须遵循的可插拔存储后端接口。后端可将文件存储在不同位置（state、filesystem、database 等）并提供统一文件操作接口。

F-039: 文件 `libs/deepagents/deepagents/backends/protocol.py` 第20-28行，`DEFAULT_GREP_TIMEOUT = 15` 秒，`ASYNC_GREP_TIMEOUT = (2 * DEFAULT_GREP_TIMEOUT) + 5 = 35` 秒。

F-040: 文件 `libs/deepagents/deepagents/backends/protocol.py` 第30-53行，`FileOperationError` 字面量类型包含四种标准化错误码：`file_not_found`、`permission_denied`、`is_directory`、`invalid_path`。

F-041: 文件 `libs/deepagents/deepagents/graph.py` 第298-299行，`execute` 工具仅当后端实现 `SandboxBackendProtocol` 时可用；非沙箱后端的 `execute` 工具返回错误消息。

## Harness Profiles（profiles/）

F-042: 文件 `libs/deepagents/deepagents/profiles/harness/harness_profiles.py` 第1-18行，Harness profiles 声明 `create_deep_agent` 应为给定提供者或模型规格塑造的运行时行为，调整提示组装、工具可见性、中间件和默认子代理行为。与 `ProviderProfile`（控制模型构造阶段）正交。

F-043: 文件 `libs/deepagents/deepagents/profiles/harness/harness_profiles.py` 第82-98行，`GeneralPurposeSubagentProfile` 是冻结 dataclass，包含 `enabled` 字段（三态：`None` 继承/默认开启、`True` 强制包含、`False` 禁用）。

F-044: 文件 `libs/deepagents/deepagents/graph.py` 第605行，`_profile = _harness_profile_for_model(model, _model_spec)` 根据模型自动解析适用的 harness profile。内置 profile 文件包括 Anthropic Sonnet/Opus/Haiku、NVIDIA Nemotron、OpenAI Codex 等。

## ACP 集成（libs/acp/）

F-045: 文件 `libs/acp/README.md` 第1-3行，`deepagents-acp` 是 Agent Client Protocol (ACP) 连接器，允许在支持 ACP 的文本编辑器（如 Zed）中运行 Python Deep Agent。

F-046: 文件 `libs/acp/deepagents_acp/server.py` 第164-216行，`AgentServerACP` 类继承自 `ACPAgent`，构造函数接收 `agent`（`CompiledStateGraph` 或工厂函数）、`modes`、`models`（模型列表，每项含 `value`、`name`、可选 `description`）、`load_sessions`（是否支持持久化 `session/load`）。

F-047: 文件 `libs/acp/deepagents_acp/server.py` 第57-59行，导入 `create_deep_agent`、`CompositeBackend`、`FilesystemBackend`、`StateBackend` 及 `MemorySaver`。

F-048: 文件 `libs/acp/deepagents_acp/server.py` 第95-97行，ACP 元数据键包括 `_ACP_MODE_METADATA_KEY = "acp_mode"`、`_ACP_MODEL_METADATA_KEY = "acp_model"`、`_ACP_SESSION_METADATA_KEY = "acp_session"`。

F-049: 文件 `libs/acp/README.md` 第113-125行，`AgentServerACP(agent, load_sessions=True)` 可通告并实现 ACP 的 `session/load` 能力，要求代理使用持久化 LangGraph checkpointer。加载时适配器恢复 LangGraph 线程、验证原始工作目录、通过 `session/update` 回放对话。

## CLI 部署工具（libs/cli/）

F-050: 文件 `libs/cli/README.md` 第8-14行，`deepagents-cli` 包含部署子命令 `init`、`deploy`、`agents`、`mcp-servers`。交互式 REPL 已迁移至 `deepagents-code`（`dcode`）。

F-051: 文件 `libs/cli/README.md` 第78-87行，CLI 项目布局：`agent.json`（名称、描述、后端、运行时模型、权限）、`AGENTS.md`（系统提示）、`tools.json`（可选工具）、`skills/<name>/SKILL.md`（可选技能）、`subagents/<name>/`（可选子代理定义）。

F-052: 文件 `libs/cli/README.md` 第59-64行，新代理默认使用 `state` 后端。可选配置 `sandbox` 后端，`sandbox_config.scope` 可为 `thread` 或 `agent`，CLI 不在本地创建或运行沙箱。

## GitHub Action（ACTION.md）

F-053: 文件 `ACTION.md` 第1-3行，根目录 `action.yml` 在 GitHub Actions 中非交互式运行 `dcode`。常用输入包括 `prompt`、`model`（`provider:model` 格式）、`*_api_key`、`shell_allow_list`、`max_turns`、`task_timeout`、`quiet`、`json`。

F-054: 文件 `ACTION.md` 第54-59行，持久化内存默认通过 `actions/cache` 启用。可用 `enable_memory: "false"` 禁用，`memory_scope` 可为 `pr`、`branch`、`repo`，`agent_name` 区分多个动作身份。

## lca-deepagents 变体

F-055: 文件 `lca-deepagents/python/pyproject.toml` 第9-11行，项目名 `lca-deepagents-python`，版本 `0.1.0`，要求 Python `>=3.11,<3.15`。第14行固定依赖 `deepagents==0.7.0`。

F-056: 文件 `lca-deepagents/python/pyproject.toml` 第13-33行，依赖包括 `deepagents==0.7.0`、`langgraph>=1.0.0,<2.0`、`langchain>=1.0.0,<2.0`、`langchain-anthropic`、`langchain-openai`、`langgraph-cli[inmem]>=0.4.0`、`deepagents-code`、`langchain-quickjs`、`langchain-mcp-adapters`、`tavily-python`、`matplotlib`、`questionary` 等。

F-057: 文件 `lca-deepagents/README.md` 第1-6行，lca-deepagents 是 LangChain Academy 课程 "Foundation: Introduction to Deep Agents" 的课程材料仓库，包含 `python/`（Python 实现）、`typescript/`（TypeScript 实现，即将推出）、`agent-chat-ui/`（langchain-ai/agent-chat-ui 的 fork，为第5.5课 "The Sales Assistant (Advanced)" 增加功能）。

F-058: 文件 `lca-deepagents/python/README.md` 第7行，截至 2026年8月5日，课程运行在 `deepagents==0.7.0`。课程分为5个模块（m1-m5），涵盖基础代理、工具与沙箱、技能与内存、子代理委派、综合项目。

F-059: 文件 `lca-deepagents/python/m5/sales_assistant/agent.py` 第43-58行，Sales Assistant 示例使用 `FilesystemBackend(root_dir=str(HERE), virtual_mode=True)`，配置了 `subagents`、`skills=["/skills"]`、`memory=["/AGENTS.md"]`、`backend`、`middleware=[CodeInterpreterMiddleware()]`，通过 `MultiServerMCPClient` 连接邮件 MCP 服务器。

F-060: 文件 `lca-deepagents/python/m5/sales_assistant/subagents.py` 第1-22行模块文档，定义了四个专业子代理：`chinook-analyst`（拥有数据库，新客户写入需人工审批）、`inbox-manager`（拥有邮件 MCP 工具，保存草稿需人工审批）、`quote-reviewer`（检查报价单算术和一致性）、`genre-researcher`（为新闻稿研究音乐流派，仅在 Tavily 配置时存在）。

F-061: 文件 `lca-deepagents/python/m5/sales_assistant/subagents.py` 第17-21行，关键安全设计：将受审批控制的工具（`mail_create_draft`、`add_customer`）仅放在有审批门控的专业子代理上，而不放在主代理上，因为通用子代理继承主代理工具，可能绕过审批。

## 架构文档（libs/ARCHITECTURE.md）

F-062: 文件 `libs/ARCHITECTURE.md` 第16-20行，三层架构：Deep Agents（opinionated harness：默认值、中间件、后端、profiles）→ LangChain（代理抽象：model + tools + middleware → agent loop）→ LangGraph（运行时：state、checkpoints、streaming、interrupts）。

F-063: 文件 `libs/ARCHITECTURE.md` 第38-46行，`create_deep_agent()` 构造六步：(1) 解析请求的聊天模型和适用的 provider/harness profile；(2) 解析文件系统、技能、内存和 execute 行为使用的后端；(3) 组装主代理中间件栈；(4) 构建默认通用子代理和调用者提供的子代理；(5) 组合系统提示；(6) 调用 LangChain 的 `create_agent(...)` 生成可运行代理图。

F-064: 文件 `libs/ARCHITECTURE.md` 第89-100行，状态分两部分：LangGraph 提供图状态和检查点（保留对话状态、消息历史、interrupt、可恢复性）；Deep Agents 后端提供文件系统和内存持久化（默认 state backend 为线程作用域，store-backed 或 filesystem-backed 路由可使文件跨线程持久化）。
