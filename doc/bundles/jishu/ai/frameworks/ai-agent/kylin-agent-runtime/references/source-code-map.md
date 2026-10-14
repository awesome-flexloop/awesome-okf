---
type: Reference
title: Kylin Agent Runtime 源码信源索引
description: openkylin/agent-runtime 固定快照元数据（commit ee0c170）、关键源文件到事实编号 F-001~F-150 的映射与数量统计口径。
tags: [kylin-agent-runtime, source, reference]
generated: { by: "process:seven-concepts-e/trae-cn", at: 2026-10-14T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-14T00:00:00+08:00 }
status: stable
stale_after: 2027-10-14
sources:
  - id: repo
    resource: https://gitee.com/openkylin/agent-runtime.git
    title: openKylin agent-runtime 仓库
---

# Kylin Agent Runtime 源码信源索引

## 快照元数据（可复现基线）

| 项 | 值 |
|---|---|
| 远程仓库 | https://gitee.com/openkylin/agent-runtime.git |
| 固定 commit | `ee0c1709199b37ebccdc69b545f266e52e5ed6c9` |
| 分支/时间 | master，2026-10-13 16:39 +0800 |
| 最近 tag 血缘 | `git describe` = `V0.9.4-52-gee0c170`（V0.9.4 之后 52 个提交；HEAD 无精确 release tag，故固定 commit hash 而非浮动分支） |
| 打包版本 | pyproject.toml name=`kylin-agent-runtime`、version=`1.0.1` |
| 运行要求 | Python >= 3.11，MIT License，authors: Nous Research |
| 组件版本 | CLI 包 `__version__` 0.9.4（2026.7.24）；acp_registry/agent.json 0.9.3；skills/kylin-cua 0.9.8 |
| 快照日期 | 2026-10-14 |

复验方式：`git fetch <url>` 后 `git checkout ee0c1709199b37ebccdc69b545f266e52e5ed6c9`，本束全部 `文件:行号` 证据均对应该快照。

## 关键源文件 → 事实编号映射

### 项目元数据与入口

| 文件 | 说明 | 事实 ID |
|---|---|---|
| `pyproject.toml` | 包元数据、钉版依赖、extras、console_scripts、py-modules、packages.find | F-001 ~ F-009 |
| `README.zh-CN.md` | 中文自述、安装、运行命令、网关 systemd 服务 | F-010 ~ F-012 |
| `AGENTS.md` | 开发指南：项目结构、文件依赖链、AIAgent 说明 | F-013、F-018 |
| `docs/features.zh-CN.md` | 功能清单：9 种运行形态、能力分组 | F-017 |
| `acp_registry/agent.json` | ACP 代理注册清单（id/name/version/uvx） | F-015 |
| `skills/kylin-cua/version` | kylin-cua 技能版本 0.9.8 | F-016 |
| `Dockerfile`、`docker-compose.yml`、`docker/`、`nix/`、`setup-kylin-agent-runtime.sh` | 容器/Nix/安装脚本资产 | F-019、F-020 |

### Agent 核心（根模块 + agent/ 包）

| 文件 | 说明 | 事实 ID |
|---|---|---|
| `run_agent.py` | AIAgent 类（转发壳）、chat/run_conversation/main | F-021 ~ F-023 |
| `agent/agent_init.py` | init_agent 真实初始化逻辑 | F-024 |
| `agent/conversation_loop.py` | 模块级 run_conversation 对话环 | F-025 |
| `agent/system_prompt.py`、`agent/prompt_builder.py` | 系统提示词三段构建、平台提示、上下文文件加载 | F-026 ~ F-029 |
| `agent/iteration_budget.py` | 父子代理迭代预算 | F-030 |
| `agent/tool_executor.py` | 工具并发/串行执行、中断处理 | F-031 |
| `agent/tool_guardrails.py` | 幂等/变更工具分类、失败护栏控制器 | F-032、F-033 |
| `agent/error_classifier.py`、`retry_utils.py`、`stream_diag.py` | 18 类故障转移、退避、流式诊断 | F-034、F-035 |
| `agent/think_scrubber.py`、`message_sanitization.py` | 思维链清洗、消息消毒 | F-036、F-150 |
| `agent/completion_review.py`、`background_review.py` | 完成度自审、后台复盘 | F-037、F-038 |
| `agent/delegation_router.py`、`task_recovery.py`、`trajectory.py` | 委派路由、任务恢复策略、轨迹落盘 | F-039 ~ F-041 |
| `agent/file_safety.py`、`redact.py`、`shell_hooks.py`、`session_detail_logger.py` | 写保护、密钥脱敏、Shell 钩子、明细日志 | F-042 ~ F-045 |

### 工具体系

| 文件 | 说明 | 事实 ID |
|---|---|---|
| `tools/registry.py` | ToolRegistry 单例、AST 预判 + discover_builtin_tools | F-046 ~ F-048 |
| `model_tools.py`、`toolsets.py`、`toolset_distributions.py` | 工具发现触发、工具定义/分发、_HERMES_CORE_TOOLS、31 工具集 | F-049 ~ F-052 |
| `tools/file_tools.py`、`browser_tool.py`、`kanban_tools.py`、`terminal_tool.py`、`delegate_tool.py`、`code_execution_tool.py`、`cronjob_tools.py`、`mcp_tool.py` | 各工具群 register 行位 | F-053、F-054、F-060 |
| `tools/computer_use_tool.py` + `tools/computer_use/` | computer_use shim 与 CUA 后端子包 | F-055 |
| `tools/environments/` | BaseEnvironment + 8 个终端环境实现 | F-056、F-057、Q-009 |
| `tools/{approval,clarify_tool,clarify_gateway,checkpoint_manager,credential_files,env_passthrough,budget_config}.py` | 审批/澄清/检查点/凭证注入 | F-058、F-059 |

### 模型与 Provider

| 文件 | 说明 | 事实 ID |
|---|---|---|
| `agent/transports/` | ProviderTransport ABC、4 个注册传输、Codex app server、Hermes MCP server | F-061 ~ F-065、F-122 |
| `agent/auxiliary_client.py` | resolve_provider_client 中央路由、call_llm、运行时主绑定 | F-066、F-067 |
| `agent/anthropic_adapter.py`、`bedrock_adapter.py`、`gemini_native_adapter.py`、`copilot_acp_client.py`、`google_code_assist.py` | 各厂商适配/OAuth | F-068 ~ F-071 |
| `agent/credential_pool.py`、`credential_sources.py` | 凭证池四策略/轮换、十类凭证来源 | F-072、F-073 |
| `agent/model_metadata.py`、`models_dev.py`、`usage_pricing.py`、`rate_limit_tracker.py`、`nous_rate_guard.py` | 上下文长度、models.dev、定价、限流 | F-074 ~ F-076 |
| `agent/{image_routing,lmstudio_reasoning,moonshot_schema,gemini_schema,prompt_caching,account_usage,plugin_llm}.py` | 图像路由、推理参数、schema 清洗、缓存、额度、插件 LLM | F-077 ~ F-079 |
| `providers/` | ProviderProfile 与 provider 注册表（两处扫描） | F-080 |

### 记忆、上下文、画像、技能、插件

| 文件/目录 | 说明 | 事实 ID |
|---|---|---|
| `agent/context_engine.py`、`context_compressor.py`、`context_references.py` | 压缩引擎 ABC/实现、@引用展开 | F-081 ~ F-083 |
| `agent/memory_manager.py`、`memory_provider.py`、`insights.py` | 记忆编排、MemoryProvider ABC、洞察统计 | F-084 ~ F-086 |
| `agent/curator.py`、`curator_backup.py` | 技能策展与备份回滚 | F-087 |
| `agent/skill_bundles.py`、`skill_commands.py`、`skill_preprocessing.py`、`skill_utils.py` | 技能运行时四件套 | F-088 |
| `agent/user_profile/`、`agent/user_profile_runtime.py` | 画像模型/策略/加密存储/抽取/onboarding/运行时 | F-089 ~ F-091 |
| `embeddings/`、`agent/subdirectory_hints.py`、`title_generator.py` | 嵌入产物、目录提示、标题生成 | F-092、F-093 |
| `kylin_agent_runtime_cli/plugins.py` | PluginManager、VALID_HOOKS 17 钩、entry-points 组 | F-094、F-095 |
| `plugins/` | 17 插件目录、8 记忆后端、8 搜索后端 | F-096、F-097 |
| `skills/`、`optional-skills/` | 内置技能树（4 状态文件/77 SKILL.md）与可选技能 17 类 | F-098、F-099 |
| `agent/*_provider.py`、`*_registry.py`、`tools/browser_*.py` | 四类能力 Provider ABC/注册、浏览器资产 | F-100、F-101 |

### 网关、协议、调度、存储

| 文件/目录 | 说明 | 事实 ID |
|---|---|---|
| `gateway/run.py` | GatewayRunner、start/stop、适配器工厂、main | F-102 ~ F-104 |
| `gateway/session.py`、`session_models.py`、`session_context.py` | 会话数据模型/存储/上下文变量 | F-105 ~ F-107 |
| `gateway/config.py`、`platform_registry.py`、`platforms/base.py` | Platform 枚举 22、插件注册表、适配器 ABC | F-108 ~ F-111 |
| `gateway/platforms/` | 20 个文件适配器 + qqbot 子包 + 10 辅助文件 | F-112 ~ F-114、Q-002 |
| `gateway/{delivery,pairing,channel_directory,hooks,status,restart,memory_monitor,shutdown_forensics,stream_consumer,runtime_footer,slash_access,mirror,whatsapp_identity,sticker_cache}.py` | 投递/配对/运维套件 | F-115 ~ F-117 |
| `acp_adapter/`、`acp_registry/` | ACP stdio 服务器/会话/审批/事件 | F-118 ~ F-120 |
| `mcp_serve.py` | FastMCP 服务器（10 个 @mcp.tool） | F-121 |
| `agent/lsp/` | LSP 单例/客户端/服务/26 ServerDef/安装/CLI | F-123、F-124 |
| `cron/` | 函数式调度 run_job/tick、作业 dict 模型 | F-125 ~ F-127（F-128 为目录事实） |
| `kylin_agent_runtime_state.py` | SessionDB/MemoryDB、9+2 表、2 FTS5、检索方法 | F-129 ~ F-132 |

### CLI / TUI / Web / 横切

| 文件/目录 | 说明 | 事实 ID |
|---|---|---|
| `cli.py` | HermesCLI/ChatConsole 遗产交互 CLI | F-133 |
| `kylin_agent_runtime_cli/` | 新 CLI 包：main 分发、48 子命令、setup、gateway、plugins、tools_config、cron、skin | F-134 ~ F-137、F-143、F-144 |
| `kylin_agent_runtime_cli/web_server.py`、`web/` | FastAPI dashboard（9119）+ React 19 前端 | F-138、F-141 |
| `kylin_agent_runtime_cli/main.py` TUI 分发、`tui_gateway/`、`ui-tui/` | Ink TUI 启动链与 JSON-RPC 后端 | F-139、F-140、F-142 |
| `agent/i18n.py`、`locales/` | 16 语言 | F-145 |
| `agent/process_bootstrap.py`、`user_directories.py`、`kylin_agent_runtime_{constants,logging,time,bootstrap}.py`、`display.py`、`markdown_tables.py`、`async_utils.py` | 进程引导/路径/日志/显示横切 | F-146 ~ F-148 |
| `batch_runner.py`、`agent_eval_runner.py`、`mini_swe_runner.py`、`trajectory_compressor.py`、`tests/`、`evals/` | 批处理/评测/测试资产 | F-149 |

## 事实统计

- 编号事实：150 条（F-001 ~ F-150；F-128 为 cron/ 目录事实，编号连续无缺）。
- 数量卡：10 条（Q-001 ~ Q-010），每条附计数命令与口径；勘误/审计 8 条（E-001 ~ E-008），见 [facts.md](../spec/facts.md)。
- 行号口径：统一以 ripgrep/Read 按 `\n` 分行（gateway/run.py 存在 lone-CR 混合换行，PowerShell `Measure-Object -Line` 口径偏少，已在 Q-008 记录）。
