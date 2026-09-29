---
type: spec-insights
title: Octop 架构洞察
---

# Octop 架构洞察

> I阶段产出：基于 F-001~F-133 源码事实提炼的架构洞察。

## I-01：Greenfield 延迟绑定——首次启动不打开数据库

**陈述**：OctopServer 在全新 SQLite 安装时故意延迟打开控制面数据库，先以"无 DB"状态启动 HTTP 服务，等 setup wizard 通过 `/setup/database` 选择后端后再调用 `bind_control_plane()` 热绑定。

**证据**：F-035（`start()` 中 `should_defer_control_plane_db` 判断为 True 时仅生成 wizard 密码后返回，services/app_runtime 均为 None）、F-036（`bind_control_plane()` 幂等绑定 DB 并 boot runtime）、F-099（`should_defer_control_plane_db` 仅对无 DB 文件、无 PG 配置、无 `OCTOP_DATABASE_*` 环境变量的全新 SQLite 返回 True）、F-033（`AppRuntime.replace_services` 支持运行时热交换 SharedServices）。

**反常识**：多数自托管应用在启动时即打开数据库并迁移 schema；Octop 反其道而行——HTTP 层先活起来，让用户通过浏览器向导完成数据库选型（SQLite vs PostgreSQL），再热绑定运行时。这意味着 FastAPI 路由必须能处理 `server.services is None` 的"未绑定"状态，setup lockdown 中间件在此期间封锁非 setup 路由。

**行动**：理解 `database_bound` 属性和 setup lockdown 中间件的协作；新增路由时须考虑 services 可能为 None 的窗口期；二次开发若需在启动时访问 DB，应挂在 `_boot_runtime` 之后而非 `start()` 早期。

## I-02：组合根独占——launch.py 是唯一同时接触 infra 与 api 的模块

**陈述**：架构通过严格的依赖方向禁令（dashboard→api→infra→utils）保证领域层不感知传输层，`launch.py` 作为唯一的组合根（composition root）同时导入 `OctopServer` 和 `build_app`，将二者在 uvicorn 进程中装配。

**证据**：F-029（launch.py 同时导入 `infra/server` 和 `api/app`）、F-128（依赖流向内）、F-129（硬禁令：infra 不得导入 api/cli/launch；api 不得导入 cli/launch；cli 不得导入 api）、F-130（只有 launch.py 可同时导入二者）、F-108（`build_app(server)` 接收已启动的 OctopServer 实例而非自己构造）。

**反常识**：许多 FastAPI 项目在 app 工厂内部直接初始化数据库连接和业务服务；Octop 的 `build_app` 只接收一个已构造好的 `OctopServer`，自身不做任何领域初始化。这使得同一 OctopServer 可以被 CLI embedded 模式（`octop acp`、`chats repl`）独立启动，无需经过 HTTP 层。

**行动**：新增领域服务时在 `infra/` 中实现并在 `_boot_runtime` 中装配；新增 HTTP 路由时只做"校验→调用 infra→映射错误"；不要在 router 中 import repos 或构造服务。

## I-03：外部 Harness 三件套委托——Octop 自身不实现 Agent 运行时

**陈述**：Octop 的核心 AI 能力（Agent 执行、IM 网关、记忆、浏览器）全部委托给腾讯内部的外部包 `orcakit-harness-agent`、`harness-gateway`、`harness-memory`、`harness-browser`，Octop 自身只做编排、持久化、多租户和 HTTP/CLI 适配。

**证据**：F-007（核心依赖包含四个 harness 包）、F-052（AgentManager 从 `harness_agent` 导入 HarnessAgent/HarnessAgentConfig/HarnessAgentManager/SecurityPolicy）、F-074（Gateway 从 `harness_gateway` 导入 ChannelManager/ChannelKind/ChannelSubject）、F-056（AgentManager.boot 构造 HarnessAgentManager 并将 agents 注册进去）、F-079（Gateway.boot 构造 harness_gateway ChannelManager）、F-068（MCP 工具通过 `harness_agent.mcp.aload_mcp_tools` 加载）。

**反常识**：名为"AI assistant"的 Octop 并不包含模型调用、工具执行、对话图编排等核心 AI 逻辑——这些在 harness-agent（基于 LangGraph）中。Octop 的代码量集中在多用户管理、CRUD、IM 通道注册、配置持久化、setup wizard、TLS/备份等"平台外壳"。这使得 Octop 可以独立于 AI 运行时演进，但也意味着脱离 harness 包 Octop 无法独立运行。

**行动**：文档中只描述 Octop 如何调用 harness 包的公共 API，不虚构其内部实现；调试 AI 行为需查看 harness-agent 源码；升级 harness 包版本时关注 `HarnessAgentConfig` 字段变化（F-080 的 `_HARNESS_AGENT_CONFIG_FIELDS` 反射机制即为此设计）。

## I-04：CLI 延迟加载 + 三层传输——20 个子命令零启动成本

**陈述**：CLI 使用 `_LazyCLI`  click.Group 在调用时才 import 命令模块，且每个子命令根据需求选择 Offline（直读本地 SQLite）、Embedded（进程内启动 OctopServer）或 External（直接 OS 调用）三种传输层之一，避免无谓的服务器启动。

**证据**：F-114（_LazyCLI.get_command 通过 importlib 按需导入）、F-116（20 个命令在 COMMANDS 字典中注册为模块路径元组）、F-120（三层传输定义）、F-117（UTF-8 stdio 强制处理 Windows GBK 兼容）、F-125（`octop acp` 启动独立 OctopServer 而不依赖 `octop run`）。

**反常识**：典型 Click 应用在根 group 加载时导入所有子命令模块，即使执行 `octop version` 也要加载整个依赖树；Octop 的 lazy registry 使 `--help` 和 version 几乎瞬时返回。更关键的是三层传输设计——`octop agent list` 直接读 SQLite 文件，`octop chats send` 在进程内启动完整 OctopServer，`octop models ollama-pull` 直接调用本地 Ollama HTTP——同一 CLI 工具根据操作语义选择最经济的执行路径。

**行动**：新增 CLI 命令时在 registry.py 注册元组而非直接 import；根据命令是否需要运行时选择 transport 层；Offline 命令不得构造 OctopServer；Embedded 命令须确保正确 shutdown。

## I-05：单进程多 Agent + 有界并行热重载

**陈述**：Octop 采用单进程 asyncio 模型承载所有用户和 Agent，AgentManager 在进程内维护所有 HarnessAgent 实例；配置变更（provider/model/tool guard）触发有界并行热重载（并发上限 6），无需重启进程。

**证据**：F-037（_boot_runtime 在单个 asyncio 事件循环中构造所有运行时单例）、F-066（`_PROVIDER_RELOAD_CONCURRENCY = 6`，`on_provider_changed` 使用 asyncio.Semaphore 并行 reload）、F-057/F-060（Agent 启停均在进程内通过 harness_manager 完成）、F-067（三种热重载粒度：单 agent、全部 agent、仅 harness 侧重建）、F-083（Cron 投递在同一进程内通过 agent_manager.stream 执行）。

**反常识**：多用户 AI 平台常采用每用户/每 Agent 独立进程或容器隔离；Octop 选择单进程多租户——所有 Agent 共享同一个 asyncio 事件循环和 HarnessAgentManager。这降低了部署复杂度（无需编排器），但要求 Agent 间通过 harness 的安全策略（SecurityPolicy）和工具审批（guardrails）隔离，而非 OS 级隔离。热重载的有界并行设计避免了 provider 变更时同时重建数十个 Agent 导致的资源尖峰。

**行动**：不在 async 路径中做阻塞 I/O（F-131 禁止 blocking I/O）；理解 `asyncio.Lock` 在 AgentManager 中的保护范围；新增全局配置变更时通过 `on_provider_changed` 模式计算影响集合并有界重载，而非全量重启。
