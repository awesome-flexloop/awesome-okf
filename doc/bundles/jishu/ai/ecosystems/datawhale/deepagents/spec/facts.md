---
type: spec
title: "Deep Agents 事实采集"
---

# Deep Agents 事实采集

> 来源：https://github.com/datawhalechina/deepagents
> 采集日期：2026-08-23

## 1. 项目定位与原则

- F1. Deep Agents 是一个开源 Agent 框架（agent harness），定位为"开箱即用的有主见的 Agent"，基于 LangChain 和 LangGraph 构建。
- F2. 四大原则：Opinionated（为长周期多步骤工作调优默认值）、Extensible（无需 fork 即可覆盖或替换任何组件）、Model-agnostic（支持任何支持工具调用的 LLM）、Production-ready（基于 LangGraph，支持流式、持久化、检查点）。
- F3. 核心功能包括：子 Agent（sub-agents）、文件系统（filesystem）、上下文管理（context management）、Shell 访问、持久化记忆、人在回路（human-in-the-loop）、技能（skills）、工具（tools/MCP）。
- F4. 存在 JavaScript/TypeScript 版本：deepagents.js。
- F5. 安全模型为"信任 LLM"（trust the LLM）：Agent 可以做其工具允许的任何事，边界应在工具/沙箱层面强制执行。

## 2. Monorepo 结构

- F6. 仓库采用 monorepo 结构，所有包位于 `libs/` 目录下，每个包独立版本化。
- F7. 没有根级 `pyproject.toml`；每个包有自己的 `pyproject.toml`、`Makefile`、`README.md` 和 `uv.lock`。
- F8. 使用 `uv` 管理解释器、虚拟环境和依赖；明确禁止使用 pip、poetry 或 conda。
- F9. 使用 `make` 作为任务运行器，每个包的 Makefile 是命令的唯一来源。
- F10. `libs/Makefile` 提供跨包的 fan-out 目标：`make lint`、`make format`、`make lock`、`make lock-check`、`make lock-bump DEP=<pkg>`、`make bench-all`。
- F11. Python 版本：acp 包要求 3.14（Makefile 中注释），其余包要求 3.12。

## 3. 包清单与职责

- F12. `libs/deepagents/`（PyPI: `deepagents`，当前版本 0.7.8）：核心 SDK，提供 `create_deep_agent()`、中间件（middleware）、后端（backends）、配置文件（profiles）。
- F13. `libs/code/`（PyPI: `deepagents-code`，当前版本 0.1.59）：预构建的终端编码 Agent，通过 `dcode` 命令启动，使用 Textual TUI 框架，支持交互式和 headless 模式。
- F14. `libs/cli/`（PyPI: `deepagents-cli`）：部署 CLI，包含 `init`、`deploy`、`agents`、`mcp-servers` 子命令；注意交互式 REPL 已在 0.1.0 版本拆分到 `deepagents-code`。
- F15. `libs/acp/`（PyPI: `deepagents-acp`，当前版本 0.0.10，Alpha 状态）：Agent Client Protocol 集成，允许在 Zed 等支持 ACP 的编辑器中运行 Deep Agent。
- F16. `libs/evals/`（PyPI: `deepagents-evals`）：端到端行为评估套件，包含 Harbor 集成，用于基准测试 Agent 行为。
- F17. `libs/talon/`（PyPI: `deepagents-talon`，当前版本 0.0.3，Alpha 实验状态）：长运行 Agent 的本地运行时宿主，管理通道适配器、cron 调度器和 Agent 运行时的进程生命周期。
- F18. `libs/partners/`：提供商/沙箱集成包，包含 daytona、modal、quickjs、runloop、vercel 五个子包。

## 4. 三层架构

- F19. Deep Agents 位于三层栈的最顶层：Deep Agents（有主见的框架）→ LangChain（Agent 抽象：model + tools + middleware → agent loop）→ LangGraph（运行时：状态、检查点、流式、中断）。
- F20. `create_deep_agent()` 是组装点，位于 `libs/deepagents/deepagents/graph.py`，它解析模型/配置文件和后端，组装中间件栈，构建默认通用子 Agent，组合系统提示，然后委托给 LangChain 的 `create_agent()`。
- F21. Deep Agents 不引入新的运行时；它通过中间件（middleware）改变 Agent 看到和执行的内容。
- F22. `DeepAgentState` 扩展 LangChain 的 `AgentState`，其 `messages` 字段使用 `DeltaChannel` reducer 以保持检查点线性增长。

## 5. 中间件与后端

- F23. 中间件栈顺序：基础脚手架中间件（规划、文件系统、子 Agent 委派、摘要、请求清理）→ 调用者中间件 → 配置文件和尾部中间件（提供商特定行为、工具排除、提示缓存、记忆注入、人工审批）。
- F24. 核心中间件模块位于 `libs/deepagents/deepagents/middleware/`，包括 subagents.py、filesystem.py、skills.py、memory.py、permissions.py、summarization.py 等。
- F25. 后端位于 `libs/deepagents/deepagents/backends/`，决定文件、记忆和 Shell 执行的位置；公共导出包括 state、filesystem、store、composite、local-shell、LangSmith-sandbox、ContextHub 变体。
- F26. 配置文件（profiles）位于 `libs/deepagents/deepagents/profiles/`，分为 provider profiles（nvidia、openai、openrouter）和 harness profiles（anthropic haiku/opus/sonnet、nvidia nemotron、openai codex），通过 entry-point groups 插件化注册。

## 6. Deep Agents Code（dcode）

- F27. `deepagents-code` 采用客户端/服务器双进程架构：终端客户端（Textual TUI）负责呈现和输入，Agent 服务器运行编码 Agent 图，两者通过流式协议通信。
- F28. 安装方式：`curl -LsSf https://langch.in/dcode | bash`，支持通过 `DEEPAGENTS_CODE_EXTRAS` 环境变量选择额外提供商。
- F29. 功能特性：交互式 TUI、会话恢复、Web 搜索、远程沙箱（LangSmith、AgentCore、Daytona、Modal、Runloop 等）、持久化记忆、自定义技能（slash commands）、Headless 模式（`-x`）、人在回路审批。
- F30. `deepagents-code` 在 `pyproject.toml` 中精确钉住 `deepagents==0.7.8` 版本；CI 检查在发布时验证 pin 不过期。
- F31. 斜杠命令定义在 `command_registry.py` 的 `COMMANDS` 元组中，每个命令声明名称、描述、bypass_tier、可选 hidden_keywords 和 aliases。
- F32. 模型提供商通过可选依赖支持，配置在 `model_config.py` 的 `PROVIDER_API_KEY_ENV`、`PROVIDER_BASE_URL_ENV`、`RETRY_PARAM_BY_PROVIDER` 中。
- F33. 启动性能要求：不得在模块级别或参数解析路径导入重型包（deepagents、LangChain、LangGraph），延迟导入到实际需要时。
- F34. 安全模型：默认信任运行目录，人在回路审批门控模型请求的工具调用，但项目工件在审批提示前已被读取；不可信仓库应使用远程沙箱。

## 7. 部署 CLI（deepagents-cli）

- F35. CLI 包含四个子命令组：`init`（脚手架新项目）、`deploy`（部署为托管 Agent）、`agents`（列出/获取/删除工作区 Agent）、`mcp-servers`（注册/列出/更新/删除 MCP 服务器，支持 OAuth 连接）。
- F36. 项目布局：`agent.json`（名称、描述、后端、运行时模型、权限）、`AGENTS.md`（系统提示）、`tools.json`（工具定义）、`skills/<name>/SKILL.md`、`subagents/<name>/`。
- F37. 新 Agent 默认使用 `state` 后端；可通过 `agent.json` 的 `backend.type` 设置为 `sandbox` 并配置 `sandbox_config`。
- F38. 需要 LangSmith API 密钥访问 Managed Deep Agents 私有预览。

## 8. ACP 协议集成

- F39. ACP（Agent Client Protocol）允许在支持 ACP 的文本编辑器（如 Zed）中运行 Python Deep Agent。
- F40. 核心类 `AgentServerACP` 位于 `libs/acp/deepagents_acp/server.py`，包装编译后的 Agent 图。
- F41. 支持会话持久化：当 Agent 使用持久化 LangGraph checkpointer 时，`AgentServerACP(agent, load_sessions=True)` 可实现 ACP `session/load` 能力。
- F42. 支持动态模型切换：通过 Session Config Options 在会话中切换 LLM 模型而不丢失对话历史。
- F43. `dcode --acp` 可将预构建的编码 Agent 作为 ACP 服务器暴露，无需自定义 Agent 代码。
- F44. 依赖 `agent-client-protocol>=0.10.1` 和 `python-dotenv`。

## 9. 评估套件（deepagents-evals）

- F45. 规范入口点是 `deepagents-evals` 控制台脚本，子命令包括：run、trials、aggregate、radar、catalog、model-groups、list。
- F46. 评估运行真实 LLM，捕获完整轨迹（工具调用、文件变更、最终响应），从正确性和效率评分。
- F47. 指标包括：correctness、solve_rate、step_ratio、tool_call_ratio、median_duration_s，以及按类别（memory、tool_use、file_operations 等）的分数。
- F48. 退出码：0=成功，1=评估失败，2=配置错误，3=无可用报告。
- F49. 必须启用 LangSmith tracing（`LANGSMITH_TRACING=true`）才能运行评估。
- F50. Harbor 集成用于运行沙箱基准测试，如 Terminal Bench 2.0；包含 drbench 和 contextbench 适配器。
- F51. 支持 `--retry-failed` 从先前试验中仅重跑失败项。

## 10. Talon 运行时宿主

- F52. Talon 是实验性的本地运行时宿主，在单个事件循环中管理通道适配器、cron 调度器和 Agent 运行时的进程生命周期。
- F53. 包含：宿主进程（优雅关闭、每会话序列化、`/stop` 取消）、通用通道协议、WhatsApp 适配器（通过本地 Node bridge）、持久化 cron 调度器、MCP 工具加载、可选 LangSmith tracing。
- F54. 状态存储在 `~/.deepagents/<assistant_id>/`，目录权限 0700，cron 文件权限 0600。
- F55. WhatsApp 通道使用本地 Node bridge，仅通过 loopback 通信；支持 `self`/`allowlist`/`open` 三种暴露模式，`open` 模式需要显式确认。
- F56. Telegram 通道使用 Bot API 长轮询，支持 allowlist 用户/聊天 ID。
- F57. 支持入站语音转录（可选），默认使用 NVIDIA Parakeet 模型通过 Transformers，也支持 OpenAI SDK 转录路径。
- F58. MCP 配置查找顺序：`DEEPAGENTS_TALON_MCP_CONFIG` → `MCP_CONFIG` → `~/.deepagents/.mcp.json`。
- F59. 支持 Fleet zip 导入：`deepagents-talon import-fleet <fleet-export.zip>`。
- F60. Cron 作业持久化在 `cron/jobs.json`，通过 `talon_event` JSON 日志记录生命周期事件（cron.tick、cron.dispatch、cron.success 等）。
- F61. Talon 明确为单操作者设计，不提供多租户隔离、沙箱执行隔离或生产级 HITL 策略执行。

## 11. Partners 集成

- F62. `langchain-daytona`：Daytona 沙箱集成。
- F63. `langchain-modal`：Modal 沙箱集成。
- F64. `langchain-quickjs`：QuickJS 中间件，支持 PTC（prompt-tool-call）、REPL、快照、子 Agent，是唯一有基准测试的 partner 包。
- F65. `langchain-runloop`：Runloop 提供商和沙箱集成。
- F66. `langchain-vercel-sandbox`：Vercel 沙箱集成。

## 12. 开发规范与 CI/CD

- F67. PR 标题遵循 Conventional Commits 格式，必须包含 scope；允许的类型和 scope 定义在 `.github/workflows/pr_lint.yml`。
- F68. 分支命名：`<github-username>/<scope>/<short-description>`。
- F69. 测试分两类：`tests/unit_tests/`（无网络）和 `tests/integration_tests/`（允许网络）；使用 `asyncio_mode = "auto"`，不需要 `@pytest.mark.asyncio`。
- F70. 所有包将 pytest 警告视为错误（`"error"` 在 filterwarnings 首位）。
- F71. pre-commit 钩子运行格式化、lint、锁文件检查和 Conventional Commit 消息验证。
- F72. 三个包有基准测试：deepagents、code、partners/quickjs；使用 `bench`（walltime）和 `bench-memory`（heap）Make 目标，结果上传到 CodSpeed。
- F73. 发布使用 release-please，支持版本分支、changelog 覆盖和多组件 fan-out。
- F74. GitHub Actions 必须固定到完整长度的 commit SHA，标签引用会被拒绝。

## 13. OpenWiki 与文档

- F75. 仓库包含生成的 `openwiki/` 证据索引，由 GitHub Actions 工作流 `openwiki-update.yml` 定期刷新。
- F76. OpenWiki 包含：quickstart.md、architecture/overview.md、workflows/（deep-agents-code.md、evaluation-and-release.md）、engineering/operations-and-testing.md。
- F77. OpenWiki 工作流安装 `openwiki@0.3.3`，在 Node.js 26 下运行，使用专用的 `openwiki` GitHub 环境。
- F78. `.mcp.json` 配置了两个 MCP 服务器：docs-langchain 和 reference-langchain，用于开发时查阅文档。
- F79. 根 `action.yml` 定义了 GitHub Action，以非交互方式运行 `dcode`，支持 prompt、model、API keys、shell_allow_list、max_turns 等输入。

## 14. 示例生态

- F80. `examples/` 目录包含多种模式：deep_research（多步网络研究）、content-builder-agent（内容构建）、text-to-sql-agent（自然语言转 SQL）、nvidia_deep_agent（NVIDIA Nemotron 研究 Agent）、async-subagent-server（异步子 Agent 服务器）、ralph_mode（自主循环）、llm-wiki（LLM 知识库）、talon（Docker Compose 拓扑）等。
- F81. 每个示例使用 `uv` 管理依赖，包含 `pyproject.toml` 和 `uv.lock`，钉住 deepagents 版本范围。
