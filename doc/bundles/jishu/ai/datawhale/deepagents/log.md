# 知识包构建日志

## 2026-08-23 — 初始构建

### R 阶段（调研）
- 探索项目根目录与 `libs/` 子目录结构，确认七个包：deepagents、code、cli、acp、evals、talon、partners。
- 阅读根 `AGENTS.md`、`README.md`、`libs/README.md`、`libs/ARCHITECTURE.md`、`libs/DEVELOPMENT.md`、`libs/Makefile`。
- 阅读各模块 README：acp、cli、code、evals、talon、deepagents。
- 阅读 code 模块的 `AGENTS.md` 和 `ARCHITECTURE.md`、evals 模块的 `AGENTS.md`。
- 检查 OpenWiki 生成文档（index.md、architecture/overview.md、quickstart.md）。
- 检查 `.mcp.json`、`ACTION.md`、各包 `pyproject.toml` 关键元数据。
- 在 `spec/facts.md` 中记录 81 条编号事实，覆盖 14 个主题域。

### I 阶段（洞察）
- 提炼 5 个核心洞察到 `spec/insights.md`：
  1. 三层栈架构——"框架而非运行时"的定位哲学
  2. Monorepo 的独立版本化与清晰模块边界
  3. Code 模块的客户端/服务器分离与 Textual TUI 工程
  4. ACP 协议——将 Agent 嵌入编辑器的标准化桥接
  5. 评估驱动的工程文化与 Harbor 沙箱基准

### E 阶段（工程化）
- 创建 `index.md`（含完整 frontmatter：title/type/bundle/description/concepts/references/examples）。
- 创建 `log.md`。
- 创建 7 个概念文档：monorepo架构、核心SDK与三层架构、ACP协议集成、CLI部署工具、Code终端编码Agent、Evals评估套件、Talon运行时宿主。
- 创建 6 个示例文档。
- 创建 13 个引用文档，登记各模块 README 和 AGENTS.md。
- 全部使用中文，交叉链接以 `/datawhale/deepagents/` 开头。

### V 阶段（验证）
通过 Grep/Glob 对源码进行交叉验证，所有引用均确认存在：

- **关键符号**：`create_deep_agent`（graph.py）、`AgentServerACP`（server.py）、`DeepAgentState`（graph.py）、`AgentSessionContext`（server.py）、`SlashCommand`（command_registry.py:38）、`ChatInput`（chat_input.py:2067）、`Spinner`（tui/widgets/loading.py）、`_escape_markdown`/`_markdown_table`（app.py）
- **核心文件**：`graph.py`、`server.py`、`cli.py`、`command_registry.py`、`model_config.py`、`config.py`
- **目录结构**：middleware/（18 个 .py 文件含 subagents/filesystem/skills/memory/permissions/summarization）、backends/（11 个 .py 文件含 state/filesystem/store/composite/local_shell/sandbox/langsmith/context_hub）、profiles/（provider/ 和 harness/ 两个子目录）、talon 的 host.py/runtime.py/config.py/channels/cron/
- **CLI 子命令**：init（commands.py:49）、deploy（commands.py:223）、agents（commands.py:524）、mcp-servers（commands.py:583）
- **环境变量**：`DEEPAGENTS_EVALS_MODEL`（cli.py:76）、`DEEPAGENTS_TALON_WHATSAPP_ENABLED`、`DEEPAGENTS_TALON_TELEGRAM_ENABLED`、`DEEPAGENTS_TALON_INTERRUPT_ON_TOOLS`、`DEEPAGENTS_CODE_DEBUG`
- **版本号**：deepagents==0.7.8（code pyproject.toml:30）、deepagents-code 0.1.59（:7）、deepagents-acp 0.0.10（:7）、deepagents-talon 0.0.3（:7）
- **Partner 包**：daytona、modal、quickjs、runloop、vercel 五个 pyproject.toml 均存在
- **Cron 事件**：cron.tick/cron.dispatch/cron.failure/cron.success 在 scheduler.py 中确认
- **evals CLI**：cli.py 包含子命令解析器，run_trials.py:55 引用 DEEPAGENTS_EVALS_MODEL

### C 阶段（收尾）
- 最终目录结构：30 个文件（1 个 index.md、1 个 log.md、7 个概念文档、6 个示例文档、13 个引用文档、2 个 spec 文档）。
- frontmatter 格式校验：index.md 含 title/type:index/bundle/description/concepts/references/examples/sources；concept 文件含 title/type:concept/bundle/related/sources；交叉链接均以 /datawhale/deepagents/ 开头。
- 全部文档使用中文撰写，sources 标注 https://github.com/datawhalechina/deepagents。
