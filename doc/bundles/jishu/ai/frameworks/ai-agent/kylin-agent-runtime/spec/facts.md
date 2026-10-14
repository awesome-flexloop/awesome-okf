---
type: reference
title: Kylin Agent Runtime 事实清单（R 阶段）
description: 对 openkylin/agent-runtime 快照 ee0c170 的分层源码事实采集，编号 F-001 起，每条附 文件:行 证据；数量事实集中于 Q 节并附计数口径。
tags: [kylin-agent-runtime, facts, source-analysis]
generated: { by: "process:seven-concepts-r/trae-cn", at: 2026-10-14T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v/trae-cn", at: 2026-10-14T00:00:00+08:00 }
status: stable
stale_after: 2027-10-14
sources:
  - id: source-code
    resource: /references/source-code-map.md
    title: Kylin Agent Runtime 源码信源
  - id: community-sig
    resource: /references/community-sig.md
    title: openKylin AISubsystem SIG 信源
---

# Kylin Agent Runtime 事实清单（R 阶段）

> 快照：`https://gitee.com/openkylin/agent-runtime.git`，commit `ee0c1709199b37ebccdc69b545f266e52e5ed6c9`（2026-10-13，master），`git describe` = `V0.9.4-52-gee0c170`。
> 纪律：每条事实可凭 `文件:行号` 在该快照复验；事实段只陈述代码中存在什么，推断归入 [insights.md](insights.md)。行号按 ripgrep/Read（以 `\n` 分行）口径。

## 0. 快照与项目元数据

- F-001：`pyproject.toml` 声明 name = "kylin-agent-runtime"、version = "1.0.1"、requires-python = ">=3.11"、license = {text = "MIT"}、authors = [{name = "Nous Research"}]。证据：pyproject.toml:6-12
- F-002：构建后端为 setuptools（`[build-system] requires=["setuptools>=61.0"]`，backend `setuptools.build_meta`）。证据：pyproject.toml:1-3
- F-003：核心 dependencies 全部精确钉版（==），含 openai==2.24.0、httpx[socks]==0.28.1、pydantic==2.13.4、croniter==6.0.0、numpy==2.4.6 等；注释记录 2026-05-12 Mini Shai-Hulud 蠕虫事件后收紧钉版策略。证据：pyproject.toml:13-70
- F-004：optional-dependencies 含 anthropic、mcp、acp（agent-client-protocol==0.9.0）、bedrock、web（fastapi==0.133.1 + uvicorn）、dingtalk、feishu、google、voice、computer-use 等；`[all]` 只收不可懒安装的 extra，注释列出 2026-05-12 起改为懒安装的后端清单。证据：pyproject.toml:72-210
- F-005：console_scripts 有 4 个入口：`kylin-agent-runtime = kylin_agent_runtime_cli.main:main`、`hermes`（同目标，向后兼容别名）、`hermes-agent = run_agent:main`、`hermes-acp = acp_adapter.entry:main`。证据：pyproject.toml:212-217
- F-006：`[tool.setuptools] py-modules` 列出 14 个顶层单文件模块：run_agent、model_tools、toolsets、batch_runner、trajectory_compressor、toolset_distributions、cli、kylin_agent_runtime_bootstrap/constants/state/time/logging、utils。证据：pyproject.toml:219-220
- F-007：packages.find.include 含 agent、tools、kylin_agent_runtime_cli、gateway、tui_gateway、cron、acp_adapter、plugins、providers 及各自 `.*`。证据：pyproject.toml:231-232
- F-008：package-data 打包 `kylin_agent_runtime_cli` 的 web_dist/tui_dist 与 install 脚本、gateway/assets、plugins 的 dashboard manifest 与 dist。证据：pyproject.toml:222-229
- F-009：pytest 配置 testpaths=["tests"]，addopts 含 `-n auto --timeout=30 --timeout-method=signal`，marker `integration` 与 `real_concurrent_gate`。证据：pyproject.toml:234-249
- F-010：中文 README 首句陈述"Kylin Agent Runtime 是基于 Hermes 改进的自进化智能体运行时"；安装路径 `git clone https://gitee.com/openkylin/agent-runtime.git`，Python 3.11，`uv pip install -e ".[all]"`。证据：README.zh-CN.md:1-18
- F-011：README 给出运行命令 `kylin-agent-runtime setup`、`kylin-agent-runtime`、`--tui`、`-z "..."`、`dashboard`（Web 控制台默认端口 9119）。证据：README.zh-CN.md:26-48
- F-012：README 给出网关 systemd 用户服务名 `kylin-agent-runtime-gateway.service` 及 start/stop/restart/status/enable/disable/journalctl 命令集。证据：README.zh-CN.md:50-71
- F-013：仓内 AGENTS.md 标题为 "Hermes Agent - Development Guide"；结构注释称 run_agent.py 为 AIAgent 核心对话环（约 12k LOC）、cli.py 为 HermesCLI 交互编排器（约 11k LOC）。证据：AGENTS.md:1-3,27-31
- F-014：CLI 包自身版本 `__version__ = "0.9.4"`、`__release_date__ = "2026.7.24"`。证据：kylin_agent_runtime_cli/__init__.py:17-18
- F-015：acp_registry/agent.json 字段：id="kylin-agent"、name="KylinAgent"、version="0.9.3"，distribution.uvx.package="kylin-agent-runtime[acp]==0.9.3"，args=["hermes-acp"]，license=MIT，authors=["Nous Research"]。证据：acp_registry/agent.json
- F-016：skills/kylin-cua/version 文件内容为单行 `0.9.8`。证据：skills/kylin-cua/version
- F-017：docs/features.zh-CN.md 标题为 "Hermes Agent 功能清单"，列出 9 种运行形态（经典 CLI `hermes`、Ink TUI、gateway、OpenAI 兼容 API server、Web Dashboard、ACP `hermes-acp`、Cron、Batch Runner、库式 AIAgent API）。证据：docs/features.zh-CN.md:19-30
- F-018：用户配置目录为 `~/.kylin-agent-runtime/`（config.yaml 配置、.env 仅放密钥、logs/ 三类日志）；代码内仍大量出现 hermes 命名（如 HERMES_* 环境变量、hermes_home）。证据：AGENTS.md:68-71；agent/file_safety.py:19-111
- F-019：Docker 资产：根 Dockerfile、docker-compose.yml、docker/entrypoint.sh 与 docker/SOUL.md。证据：Dockerfile、docker-compose.yml、docker/entrypoint.sh、docker/SOUL.md（目录清单）
- F-020：另有 Nix 打包资产（nix/ 下 11 个 .nix：packages/devShell/hermes-agent/nixosModules/overlays 等）、Homebrew packaging/homebrew/README.md、安装脚本 setup-kylin-agent-runtime.sh 与 scripts/install.{sh,ps1,cmd}。证据：nix/、packaging/homebrew/、scripts/（目录清单）

## 1. AIAgent 核心与对话循环

- F-021：`class AIAgent` 定义于 run_agent.py:326；`__init__`（run_agent.py:349-416）是转发壳，docstring 明示 "Forwarder — see agent.agent_init.init_agent"，函数体内 `from agent.agent_init import init_agent` 并转发全部参数。证据：run_agent.py:326-445
- F-022：AIAgent.__init__ 关键默认值：max_iterations=90（注释：tool-calling iterations，与子代理共享）、tool_delay=1.0、prompt_profile="full"、checkpoint_max_snapshots=20、checkpoint_max_total_size_mb=500、checkpoint_max_file_size_mb=10；形参含平台/会话身份组（platform/user_id/chat_id/thread_id/gateway_session_key）、9 类 callback、credential_pool、fallback_model、iteration_budget、parent_session_id。证据：run_agent.py:349-416
- F-023：`def run_conversation(self, user_message, system_message=None, conversation_history=None, task_id=None)` 在 run_agent.py:3996；`def chat(self, message, stream_callback=None) -> str` 在 run_agent.py:4019；`def main()` 在 run_agent.py:4046。证据：run_agent.py:3996-4046
- F-024：真正初始化逻辑在 `init_agent(agent, ...)`，形参从 agent/agent_init.py:74 延续到 133 行之后，含 enabled/disabled_toolsets、reasoning_config、request_overrides、prefill_messages、session_db、parent_session_id、iteration_budget 等。证据：agent/agent_init.py:74-133
- F-025：模块级对话函数 `run_conversation(agent, user_message, system_message=None, conversation_history=None, task_id=None, stream_callback=None, persist_user_message=None) -> Dict[str,Any]` 定义于 agent/conversation_loop.py:372-380；内部调用 `auxiliary_client.set_runtime_main(agent.provider, agent.model)` 与 `kylin_agent_runtime_logging.set_session_context(agent.session_id)`。证据：agent/conversation_loop.py:372-426
- F-026：系统提示词构建：`build_system_prompt_parts(agent, system_message=None) -> Dict[str,str]` 返回 stable/context/volatile 三键（agent/system_prompt.py:164-181）；`build_system_prompt(...)` 在 413、`invalidate_system_prompt` 433、`format_tools_for_system_message` 444。证据：agent/system_prompt.py:164-444
- F-027：提示词片段常量含 DEFAULT_AGENT_IDENTITY、KYLIN_AGENT_HELP_GUIDANCE、CHINA_WEB_ACCESS_GUIDANCE、MEMORY_GUIDANCE、SKILLS_GUIDANCE、KANBAN_GUIDANCE、TOOL_USE_ENFORCEMENT_GUIDANCE。证据：agent/prompt_builder.py:137-279
- F-028：`TOOL_USE_ENFORCEMENT_MODELS = ("gpt","codex","gemini","gemma","grok","glm","qwen","deepseek")`（8 项）；PLATFORM_HINTS 字典 19 个键（whatsapp/telegram/discord/slack/signal/email/cron/cli/sms/bluebubbles/mattermost/matrix/feishu/weixin/wecom/qqbot/yuanbao/api_server/webui）。证据：agent/prompt_builder.py:296,440-626
- F-029：上下文文件加载 `build_context_files_prompt(cwd=None, skip_soul=False)`，优先级注释：.kylin-agent-runtime.md/HERMES.md → AGENTS.md → CLAUDE.md → .cursorrules；常量 CONTEXT_FILE_MAX_CHARS=20_000、截断 head 0.7/tail 0.2。证据：agent/prompt_builder.py:855-857,1455-1579
- F-030：迭代预算 `class IterationBudget`：`__init__(max_total)`、consume()/refund()、used/remaining，threading.Lock 保护；模块 docstring 记录父代理上限取 max_iterations（默认 90）、子代理取 delegation.max_iterations（默认 50）。证据：agent/iteration_budget.py:4-59
- F-031：工具并发/串行执行：`execute_tool_calls_concurrent(agent, assistant_message, messages, effective_task_id, api_call_count=0)`（agent/tool_executor.py:355）、`execute_tool_calls_sequential(...)`（:819）；中断时为每个 tool call 追加 "Tool execution cancelled"。证据：agent/tool_executor.py:355-373,819
- F-032：工具护栏常量：IDEMPOTENT_TOOL_NAMES frozenset 16 项（read_file/search_files/web_search/web_extract/memory/browser_* 等）、MUTATING_TOOL_NAMES frozenset 15 项（terminal/execute_code/write_file/patch/todo/skill_manage/browser_写操作/send_message/cronjob/delegate_task/process）。证据：agent/tool_guardrails.py:20-59
- F-033：`@dataclass(frozen=True) ToolCallGuardrailConfig` 阈值：exact_failure_warn_after=2、exact_failure_block_after=5、same_tool_failure_warn_after=3、same_tool_failure_halt_after=8、no_progress_warn_after=2、no_progress_block_after=5；`class ToolCallGuardrailController` 提供 before_call/after_call/reset_for_turn。证据：agent/tool_guardrails.py:62-379
- F-034：错误分类 `class FailoverReason(enum.Enum)` 18 个成员（auth/billing/rate_limit/overloaded/server_error/timeout/context_overflow/model_not_found/...）；`classify_api_error(...) -> ClassifiedError` 在 agent/error_classifier.py:345。证据：agent/error_classifier.py:24-61,345-353
- F-035：退避重试 `jittered_backoff(attempt, base_delay=5.0, max_delay=120.0, jitter_ratio=0.5)`；流式诊断 STREAM_DIAG_HEADERS 10 个响应头，stream_diag_init/capture/log_stream_retry 一组函数。证据：agent/retry_utils.py:19-25；agent/stream_diag.py:27-214
- F-036：思维链清洗 `class StreamingThinkScrubber`，开放标签名集合 ("think","thinking","reasoning","thought","REASONING_SCRATCHPAD")，feed()/flush()。证据：agent/think_scrubber.py:61-204
- F-037：完成度自审：`class CompletionReviewer`（review(agent, request, messages, candidate, todo) -> ReviewResult）、ReviewSettings 默认 enabled=True/max_attempts=2/max_reviews=8、decision 集合 {completed,continue,await_user,await_approval,blocked}。证据：agent/completion_review.py:115-360
- F-038：后台复盘 `spawn_background_review_thread(agent, messages_snapshot, review_memory=False, review_skills=False)` 返回 (target, prompt)；写记忆元数据构造 `build_memory_write_metadata(...)`。证据：agent/background_review.py:294-301,548-573
- F-039：委派路由 `decide_delegation_hint(user_message, valid_tool_names, prompt_profile="full", config=None) -> DelegationRouterDecision`；打分规则 explicit_delegation +4、implementation +3、parallel/multi_angle +2 等；config 默认 enabled=True 但 router_enabled=False、mainline_branch_enabled=False。证据：agent/delegation_router.py:80-212
- F-040：任务恢复：`recovery_policy_for_tool(tool_name, args=None)` 返回 {resume_children, safe_retry, verify_effects, confirm_before_retry}（delegate_task→resume_children）；`task_checkpoint_context(db, task_run_id, ...)` 上下文管理器。证据：agent/task_recovery.py:48-137
- F-041：轨迹保存 `save_trajectory(trajectory, model, completed, filename=None)` 默认写 trajectory_samples.jsonl / failed_trajectories.jsonl（JSONL 追加）。证据：agent/trajectory.py:30-53
- F-042：安全：`build_write_denied_paths(home)` 16 个精确路径（.ssh 密钥/.env/shell rc/.netrc 等）、`build_write_denied_prefixes(home)` 9 个目录前缀；is_write_denied/get_safe_write_root（env HERMES_WRITE_SAFE_ROOT）。证据：agent/file_safety.py:19-111
- F-043：脱敏 redact：_PREFIX_PATTERNS 36 条密钥正则（sk-/ghp_/xox/AIza/AKIA/hf_ 等）、_SENSITIVE_QUERY_PARAMS 16 项、RedactingFormatter 日志格式化器；开关 env HERMES_REDACT_SECRETS 默认 true。证据：agent/redact.py:19-107,312-459
- F-044：Shell 钩子 `register_from_config(cfg, accept_hooks=False) -> List[ShellHookSpec]`；事件名来自 `kylin_agent_runtime_cli.plugins.VALID_HOOKS`，allowlist 文件 shell-hooks-allowlist.json，DEFAULT_TIMEOUT_SECONDS=60。证据：agent/shell_hooks.py:83-85,149-320,546-844
- F-045：会话明细日志 session_detail_context/subscribe_session_details/write_session_detail（best-effort 逐次 flush），日志路径函数 session_detail_log_path/session_usage_log_path。证据：agent/session_detail_logger.py:31-228

## 2. 工具体系

- F-046：工具注册单例 `registry = ToolRegistry()` 在 tools/registry.py:544；`ToolRegistry.register(...)` 参数含 name/toolset/schema/handler/check_fn/requires_env/is_async/description/emoji/max_result_size_chars/dynamic_schema_overrides/override。证据：tools/registry.py:151-248
- F-047：发现函数 `discover_builtin_tools(tools_dir=None)` 在 tools/registry.py:57：glob 扫描 tools/ 根 *.py，排除 __init__.py/registry.py/mcp_tool.py，先用 AST（_module_registers_tools/_is_registry_register_call）静态判定模块顶层含 `registry.register(` 再 importlib 导入自注册。证据：tools/registry.py:29-57
- F-048：ToolEntry 用 __slots__ 列出 name/toolset/schema/handler/check_fn/requires_env/is_async/description/emoji/max_result_size_chars/dynamic_schema_overrides；辅助 tool_error/tool_result 在 563/577。证据：tools/registry.py:77-577
- F-049：model_tools.py 第 32 行 `from tools.registry import discover_builtin_tools, registry`，第 180 行模块级调用 discover_builtin_tools()；函数 get_tool_definitions(293)/coerce_tool_args(597)/handle_function_call(793)/get_all_tool_names(963)/get_toolset_for_tool(968)；常量 REMOVED_TOOL_NAMES=frozenset({"session_search"})。证据：model_tools.py:32,180,241,293-968
- F-050：toolsets.py 的 `_HERMES_CORE_TOOLS` 是 CLI 与全部消息平台共享的核心工具名列表（web_search/web_extract、terminal/process、read_file/write_file/patch/search_files、vision_analyze/image_generate、skills_list/skill_view/skill_manage、12 个 browser_*、text_to_speech、todo、memory、clarify、execute_code/delegate_task、cronjob、send_message、4 个 ha_*、9 个 kanban_*、computer_use）。证据：toolsets.py:31-73
- F-051：TOOLSETS 字典定义 31 个顶层工具集键（web/search/x_search/vision/video/image_gen/video_gen/computer_use/terminal/moa/skills/browser/cronjob/messaging/file/tts/todo/memory/clarify/code_execution/delegation/homeassistant/kanban/discord/discord_admin/yuanbao/feishu_doc/feishu_drive/spotify/debugging/safe），支持工具集间组合引用。证据：toolsets.py:78-311
- F-052：toolset_distributions.py 定义 DISTRIBUTIONS 字典（:29）与 get_distribution/list_distributions/sample_toolsets_from_distribution/validate_distribution/print_distribution_info。证据：toolset_distributions.py:29-304
- F-053：文件工具一次注册 4 个（read_file/write_file/patch/search_files，tools/file_tools.py:1170-1173）；浏览器 browser_tool.py 内 10 个 register 调用（3715-3789）；kanban 9 个（kanban_tools.py:1218-1290）。证据：tools/file_tools.py:1170-1173；tools/browser_tool.py:3715-3789；tools/kanban_tools.py:1218-1290
- F-054：大型工具文件：terminal_tool.py register 在 2471；delegate_tool.py 在 3933（子代理审批回调 74/88/101）；code_execution_tool.py 在 1902（checkpoint 钩子、_scrub_child_env）；cronjob_tools.py 在 788；mcp_tool.py 两个 register（3105、3142）。证据：tools/ 对应文件行号
- F-055：computer_use 是 shim + 子包两层：tools/computer_use_tool.py:19-32 注册名 computer_use 并转发到 tools/computer_use/；子包含抽象基类 ComputerUseBackend（backend.py:71）、数据类 UIElement/CaptureResult/ActionResult、CuaDriverBackend（cua_backend.py:319）、handle_computer_use/get_computer_use_schema（tool.py:208, schema.py:189）。证据：tools/computer_use_tool.py:19-32；tools/computer_use/{backend,cua_backend,tool,schema}.py
- F-056：终端环境后端基类 `BaseEnvironment(ABC)`（tools/environments/base.py:293），ProcessHandle Protocol（:192），常量 DEFAULT_PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"（:31）；由 terminal_tool._create_environment 按 TERMINAL_ENV 选择。证据：tools/environments/base.py:31-293
- F-057：8 个可经 TERMINAL_ENV 选择的叶子终端后端：LocalEnvironment(BaseEnvironment, local.py:429)、DockerEnvironment(docker.py:274)、SSHEnvironment(ssh.py:36)、ModalEnvironment(BaseEnvironment, modal.py:164)、ManagedModalEnvironment(BaseModalExecutionEnvironment, managed_modal.py:36)、DaytonaEnvironment(daytona.py:30)、SingularityEnvironment(singularity.py:156)、VercelSandboxEnvironment(vercel_sandbox.py:235)；中间基类 BaseModalExecutionEnvironment(BaseEnvironment, modal_utils.py:58) 是 BaseEnvironment 的第 8 个直接子类、仅 ManagedModal 继承它；FileSyncManager（file_sync.py:107）。继承树类共 9 个、叶子可选后端 8 个。证据：tools/environments/ 各文件类定义行
- F-058：审批与澄清：approval.py 的 _fire_approval_hook（:36）；clarify_tool.py register 在 131（clarify_tool:23、check_clarify_requirements:78），网关侧 clarify_gateway.py 的 _ClarifyEntry/wait_for_response（:48-103）；checkpoint_manager 校验 _validate_commit_hash/_validate_file_path（:155-171）。证据：tools/{approval,clarify_tool,clarify_gateway,checkpoint_manager}.py
- F-059：凭证/环境注入工具 register_credential_file（credential_files.py:56）、register_env_passthrough（env_passthrough.py:70，_is_hermes_provider_credential:48）；BudgetConfig（budget_config.py:23）。证据：tools/credential_files.py:37-56；tools/env_passthrough.py:48-70；tools/budget_config.py:23
- F-060：其余注册工具：memory_tool 1（:129）、skills_tool 2（1525/1560）、skill_manager 1（915）、todo 1（393）、tts 1（2360）、vision 2（1050/1413）、image_generation 1（1089）、video_generation 1（551）、web_tools 2（1540/1550）、x_search 1（517）、mixture_of_agents 1（533）、process_registry 1（1538）、send_message 1（2016）、homeassistant 4（479-506）、feishu_doc 1/feishu_drive 4、yuanbao 5（501-690）、discord 2（943/952）。证据：tools/ 各文件 register 行

## 3. 模型与 Provider

- F-061：传输抽象 `class ProviderTransport(ABC)` 成员：属性 api_mode、convert_messages、convert_tools、build_kwargs、normalize_response -> NormalizedResponse；默认 validate_response→True、extract_cache_stats→None、map_finish_reason 原样返回。证据：agent/transports/base.py:16-89
- F-062：传输类型 @dataclass ToolCall（id/name/arguments/provider_data，兼容 type/function/call_id 等属性）、Usage、NormalizedResponse（content/tool_calls/finish_reason/reasoning/usage/provider_data）；build_tool_call/map_finish_reason 工厂。证据：agent/transports/types.py:19-162
- F-063：传输注册表 `_REGISTRY`、register_transport/get_transport（未命中再 discover）、_discover_transports 依次 try-import anthropic/codex/chat_completions/bedrock。证据：agent/transports/__init__.py:17-68
- F-064：注册的传输类 4 个（行号统一为模块尾 register_transport 调用行）：AnthropicTransport→"anthropic_messages"（anthropic.py:179，类定义 :13）、BedrockTransport→"bedrock_converse"（bedrock.py:154，类 :15）、ResponsesApiTransport→"codex_responses"（codex.py:289，类 :14）、ChatCompletionsTransport→"chat_completions"（chat_completions.py:660，类 :102）。证据：agent/transports/*.py 的 register_transport 调用行
- F-065：Codex app server 三件套：CodexAppServerClient（codex_app_server.py:52）、CodexAppServerSession（codex_app_server_session.py:154）、CodexEventProjector（codex_event_projector.py:69）；另有 hermes_tools_mcp_server.main（hermes_tools_mcp_server.py:197）。证据：agent/transports/
- F-066：中央 provider 路由 `resolve_provider_client(provider, model=None, async_mode=False, raw_codex=False, explicit_base_url=None, explicit_api_key=None, api_mode=None, main_runtime=None, is_vision=False) -> Tuple[Optional,Optional]`；docstring 列 provider 取值 openrouter/nous/openai-codex/zai/kimi-coding/minimax/minimax-cn/custom/auto。证据：agent/auxiliary_client.py:3069-3092
- F-067：通用 LLM 调用 call_llm/async_call_llm（auxiliary_client.py:4578/5001）、extract_content_or_reasoning（:4945）；辅助客户端 Codex/Anthropic AuxiliaryClient 同步+异步四件套（:908-1091）；set_runtime_main/clear_runtime_main（:1679/1692）。证据：agent/auxiliary_client.py:908-5001
- F-068：Anthropic 适配：build_anthropic_client（anthropic_adapter.py:640）、OAuth 一族 read_claude_code_credentials/refresh_anthropic_oauth_pure/resolve_anthropic_token/run_hermes_oauth_login_pure（:853-1302）；第三方端点判定 _is_kimi_family_endpoint/_is_deepseek_anthropic_endpoint/_is_minimax_anthropic_endpoint/_is_azure_anthropic_endpoint（:365-512）。证据：agent/anthropic_adapter.py:365-2004
- F-069：Bedrock 适配：_get_bedrock_runtime_client、resolve_bedrock_region、has_aws_credentials、convert_tools_to_converse、normalize_converse_response、discover_bedrock_models、classify_bedrock_error。证据：agent/bedrock_adapter.py:74-1276
- F-070：Gemini 原生适配：probe_gemini_tier 返回 "free"/"paid"/"unknown"（gemini_native_adapter.py:47）、build_gemini_request（:388）、translate_gemini_response（:474）、GeminiNativeClient（:805）。证据：agent/gemini_native_adapter.py:37-940
- F-071：Copilot/Gemini OAuth/Code Assist：CopilotACPClient（copilot_acp_client.py:334）、google_code_assist 的 load_code_assist/onboard_user/retrieve_user_quota/ProjectIdRequiredError。证据：agent/copilot_acp_client.py:334-359；agent/google_code_assist.py:69-392
- F-072：凭证池：`class CredentialPool`（credential_pool.py:389）方法 current/select/mark_exhausted_and_rotate/acquire_lease/release_lease/try_refresh_current/load_pool；4 策略 FILL_FIRST/ROUND_ROBIN/RANDOM/LEAST_USED；PooledCredential dataclass 含 auth_type/expires_at/runtime_api_key 等。证据：agent/credential_pool.py:52-1933
- F-073：凭证来源注册表 credential_sources：register/find_removal_step + 10 个内置移除函数（env/claude_code/hermes_pkce/nous_device_code/minimax_oauth/xai_oauth_loopback_pkce/codex_device_code/qwen_cli/copilot_gh/custom_config）。证据：agent/credential_sources.py:112-383
- F-074：模型元数据：fetch_model_metadata（model_metadata.py:611）、get_model_context_length（:1429）、本地探测 is_local_endpoint/detect_local_server_type/query_ollama_num_ctx、token 估算 estimate_tokens_rough 一族。证据：agent/model_metadata.py:414-1806
- F-075：models.dev 集成：MODELS_DEV_URL="https://models.dev/api.json"，@dataclass ModelInfo/ProviderInfo，PROVIDER_TO_MODELS_DEV 35 条映射，get_model_capabilities/list_agentic_models。证据：agent/models_dev.py:34-693
- F-076：定价与限流：CostResult/PricingEntry/estimate_usage_cost（usage_pricing.py:70-857）；RateLimitState 四桶（requests/tokens × min/hour）与 parse_rate_limit_headers（rate_limit_tracker.py:57-226）；Nous 限流 record_nous_rate_limit/nous_rate_limit_remaining（nous_rate_guard.py:71-192）。证据：agent/usage_pricing.py；agent/rate_limit_tracker.py；agent/nous_rate_guard.py
- F-077：图像路由 decide_image_input_mode 返回 "native"/"text"（image_routing.py:99）；LM Studio reasoning effort 六值 {none,minimal,low,medium,high,xhigh}（lmstudio_reasoning.py:17）；Moonshot/Gemini 工具 schema 清洗器（moonshot_schema.py、gemini_schema.py）；Anthropic 缓存断点 apply_anthropic_cache_control（prompt_caching.py:49，策略 "system_and_3"，最多 4 断点）。证据：agent/image_routing.py:46-230；agent/lmstudio_reasoning.py:17-48；agent/prompt_caching.py:41-77
- F-078：账户额度：fetch_account_usage 聚合 codex/anthropic/openrouter 三抓取器，AccountUsageSnapshot/render_account_usage_lines。证据：agent/account_usage.py:19-308
- F-079：插件化 LLM 网关 `class PluginLlm`（complete/complete_structured/acomplete/acomplete_structured）与数据类 PluginLlmCompleteResult/PluginLlmUsage（含 cost_usd）、PluginLlmTrustError。证据：agent/plugin_llm.py:78-823
- F-080：providers/ 包：ProviderProfile 配置类（providers/base.py:39）、register_provider/get_provider_profile/list_providers/_discover_providers（providers/__init__.py:53-140，扫描 plugins/model-providers/ 与 $HERMES_HOME/plugins/model-providers/，同名用户覆盖）。证据：providers/base.py:21-39；providers/__init__.py:53-140

## 4. 记忆、上下文与用户画像

- F-081：`class ContextEngine(ABC)`：抽象 update_from_response/should_compress/compress；类属性 threshold_percent=0.75、protect_first_n=3、protect_last_n=6；带默认钩子 on_session_start/on_session_end/get_tool_schemas/handle_tool_call/update_model。证据：agent/context_engine.py:32-211
- F-082：`class ContextCompressor(ContextEngine)`：构造参数 threshold_percent=0.50/protect_last_n=20/summary_target_ratio=0.20 等；构造体内赋值 self.threshold_percent=0.80 与 threshold_tokens=int(context_length*0.8)；compress(messages, current_tokens=None, focus_topic=None, force=False) 在 1487。证据：agent/context_compressor.py:453-1487
- F-083：上下文引用（@ 语法）：REFERENCE_PATTERN 支持 @diff/@staged/@file/@folder/@git/@url:<value>（可带 :行号）；parse_context_references/preprocess_context_references（同步+async）；_ensure_reference_path_allowed 路径白名单。证据：agent/context_references.py:16-342
- F-084：记忆编排 `class MemoryManager`（memory_manager.py:244）：add_provider、build_system_prompt、prefetch_all/queue_prefetch_all/sync_all、get_all_tool_schemas、handle_tool_call、on_session_switch/on_pre_compress/on_memory_write/on_delegation/shutdown_all。证据：agent/memory_manager.py:227-592
- F-085：`class MemoryProvider(ABC)`：抽象 name/is_available/initialize/get_tool_schemas；可选钩子 on_turn_start/on_session_switch/on_pre_compress/on_delegation/save_config/on_memory_write（action 取值 add/replace/remove，target 取 memory/user）。证据：agent/memory_provider.py:42-279
- F-086：`class InsightsEngine`：generate(days=30, source=None) 聚合 _get_sessions/_get_tool_usage/_get_skill_usage/_get_message_stats，输出 format_terminal/format_gateway。证据：agent/insights.py:93-866
- F-087：技能策展 curator：run_curator_review(on_summary, synchronous, dry_run)（curator.py:1369）、maybe_run_curator(idle_for_seconds)（:1763）、should_run_now/apply_automatic_transitions（:199-256）、状态 load_state/save_state/set_paused；备份 snapshot_skills/rollback/list_backups（curator_backup.py:209-680）。证据：agent/curator.py:82-1763；agent/curator_backup.py:159-680
- F-088：技能运行时：skill_bundles.scan_bundles/get_skill_bundles/build_bundle_invocation_message（skill_bundles.py:168-407）；skill_commands.scan_skill_commands/build_skill_invocation_message（skill_commands.py:263-475）；skill_preprocessing.preprocess_skill_content（模板变量替换+inline shell，skill_preprocessing.py:123）；skill_utils.parse_frontmatter/skill_matches_platform/get_all_skills_dirs/discover_all_skill_config_vars。证据：agent/skill_bundles.py:168-407；agent/skill_commands.py:160-475；agent/skill_preprocessing.py:23-123；agent/skill_utils.py:34-507
- F-089：用户画像子系统（agent/user_profile/）：Pydantic 模型 UserProfile/ProfileEntry（confidence、source: onboarding|explicit|inferred、lifecycle: static|dynamic|boundary）/ProfileUpdate/ExtractionBatch（上限 50）；FIELDS 81 个 + LEGACY_FIELDS 29 个字段定义；policy.apply_updates 要求推断 confidence>=0.70 且 boundary 仅接受 explicit。证据：agent/user_profile/models.py:17-95；agent/user_profile/schema.py:38-621；agent/user_profile/policy.py:13-106
- F-090：画像存储 EncryptedFileProfileStore（Fernet 加密，文件名 <hmac-sha256>.profile.enc，O_EXCL/0600 写密钥，hmac.compare_digest 校验）；EnvironmentKeyProvider 读 KYLIN_PROFILE_KEY；抽取器 OpenAICompatibleProfileExtractor.from_environment 读 KYLIN_PROFILE_LLM_* env；onboarding 固定 3 问（称呼/年龄/职业）。证据：agent/user_profile/storage.py:13-100；agent/user_profile/extractors.py:389-468；agent/user_profile/onboarding.py:13-67
- F-091：画像运行时 RuntimeUserProfile（profile_prompt/observe）、initialize_user_profile/build_user_profile_prompt；匿名 ID pseudonymous_user_id 用 HMAC-SHA256 加 "v1_" 前缀。证据：agent/user_profile_runtime.py:28-234；agent/user_profile/identity.py:11-32
- F-092：embeddings/ 目录含 metadata.json 与 vectors.npy 两个文件。证据：embeddings/（目录清单）
- F-093：子目录提示 SubdirectoryHintTracker（check_tool_call，加载目录内提示文件）；标题生成 generate_title/auto_title_session（title_generation 辅助任务，max_tokens=500，截 80 字符）。证据：agent/subdirectory_hints.py:48-171；agent/title_generator.py:29-133

## 5. 技能、插件与外部供给注册

- F-094：CLI 侧插件管理器 `class PluginManager`（discover_and_load/_load_plugin/_load_directory_module/_load_entrypoint_module），entry-points 组名 "hermes_agent.plugins"；get_bundled_plugins_dir 默认指向仓内 plugins/（env HERMES_BUNDLED_PLUGINS 覆盖）；模块级 discover_plugins/invoke_hook。证据：kylin_agent_runtime_cli/plugins.py:55-1404
- F-095：VALID_HOOKS 集合 17 个钩子：pre/post_tool_call、transform_terminal_output/tool_result/llm_output、pre/post_llm_call、pre/post_api_request、on_session_start/end/finalize/reset、subagent_stop、pre_gateway_dispatch、pre_approval_request/post_approval_response。证据：kylin_agent_runtime_cli/plugins.py:128-168
- F-096：插件目录 17 个：agent-eval-recorder、browser、context_engine、disk-cleanup、example-dashboard、google_meet、hermes-achievements、image_gen、kanban、memory、model-providers、observability、platforms、spotify、teams_pipeline、video_gen、web；plugins/__init__.py 全文仅 1 行注释。证据：plugins/__init__.py:1；plugins/ 目录清单
- F-097：记忆后端插件 8 个目录：byterover、hindsight、holographic、honcho、mem0、openviking、retaindb、supermemory；Web 搜索后端插件 8 个：brave_free、ddgs、exa、firecrawl、parallel、searxng、tavily、xai（各含 plugin.yaml/provider.py/__init__.py）。证据：plugins/memory/、plugins/web/（目录清单）
- F-098：技能树 skills/ 根存在 4 个状态文件 .bundled_manifest、.curator_state、.usage.json、.usage.json.lock；技能分类含 creative/p5js、dogfood、email/himalaya、github（6 个技能）、kylin-cua、mcp/native-mcp、media/songsee、research/arxiv、yuanbao、ukui-direct-control、autonomous-ai-agents、productivity、software-development 等。证据：skills/ 目录清单
- F-099：optional-skills/ 顶层 17 个分类目录（autonomous-ai-agents/blockchain/communication/creative/devops/dogfood/email/finance/health/mcp/migration/mlops/productivity/research/security/software-development/web-development），顶层 DESCRIPTION.md。证据：optional-skills/DESCRIPTION.md 及目录清单
- F-100：四类能力 Provider ABC + registry：BrowserProvider（create_session/close_session/emergency_cleanup）、WebSearchProvider（search/extract/crawl + supports_* 能力位）、ImageGenProvider（generate，默认 landscape）、VideoGenProvider（generate + capabilities：modalities/max_duration=10 等）；各 registry register_provider/list_providers/get_provider/get_active_*_provider 从 config 读 cloud_provider/search_backend/image_gen.provider/video_gen.provider。证据：agent/{browser_provider,browser_registry,web_search_provider,web_search_registry,image_gen_provider,image_gen_registry,video_gen_provider,video_gen_registry}.py
- F-101：浏览器实现资产：tools/browser_camofox.py（is_camofox_mode/get_camofox_url）、browser_cdp_tool.py（_resolve_cdp_endpoint）、browser_supervisor.py（PendingDialog/DialogRecord）。证据：tools/browser_*.py

## 6. 消息网关 Gateway

- F-102：网关主类 `class GatewayRunner`：__init__(config: Optional[GatewayConfig]=None)（run.py:1424）、async start()（:3595）、async stop(restart, detached_restart, service_restart)（:5564）、request_restart(detached, via_service)（:3501）；无 run 方法。证据：gateway/run.py:1401-5564
- F-103：装配字段：self.adapters: Dict[Platform, BasePlatformAdapter]、session_store=SessionStore、delivery_router=DeliveryRouter、_agent_cache OrderedDict、_failed_platforms；适配器工厂 _create_adapter(platform, config) 先查 platform_registry 再走 if/elif 链。证据：gateway/run.py:1424-1520,5899-6117
- F-104：模块级 start_gateway(config, replace, verbosity)（run.py:17793）、main() argparse 接 --config/-c、--verbose/-v（:18216）、__main__ 守卫（:18248）。证据：gateway/run.py:17793-18248
- F-105：会话模型：@dataclass SessionSource（platform/chat_id/chat_name/chat_type/user_id/thread_id/...，to_dict/from_dict）、SessionContext（source/connected_platforms/home_channels/shared_multi_user_session/session_key/session_id）、SessionEntry（含 input/output/cache token、estimated_cost_usd、was_auto_reset、suspended、resume_pending 等字段）。证据：gateway/session.py:70-491
- F-106：`class SessionStore`（session.py:668）持有 _entries 与 SQLite SessionDB（失败回退 JSONL）；build_session_key（:600）、is_shared_multi_user_session（:578）。证据：gateway/session.py:578-691
- F-107：会话模型切换 SessionModelController（session_models.py:96，__call__(agent) 按 revision 切换）；11 个会话 ContextVar + 3 个 cron 投递变量（session_context.py:51-70），get_session_env 未设置回退 os.environ。证据：gateway/session_models.py:96-101；gateway/session_context.py:45-154
- F-108：`class Platform(Enum)` 22 个内置成员：LOCAL + telegram/discord/whatsapp/slack/signal/mattermost/matrix/homeassistant/email/sms/dingtalk/api_server/webhook/msgraph_webhook/feishu/wecom/wecom_callback/weixin/bluebubbles/qqbot/yuanbao；_missing_ 支持插件名动态造成员，_scan_bundled_plugin_platforms 扫描插件平台。证据：gateway/config.py:100-176
- F-109：配置 dataclass 群 PlatformConfig/StreamingConfig/GatewayConfig/HomeChannel/SessionResetPolicy；load_gateway_config() -> GatewayConfig（config.py:682），含 _validate_gateway_config/_apply_env_overrides。证据：gateway/config.py:203-1289
- F-110：平台注册表 PlatformRegistry：@dataclass PlatformEntry（name/label/adapter_factory/check_fn/validate_config/is_connected/required_env/source="plugin"）、register/get/all_entries/plugin_entries/create_adapter；模块单例 platform_registry；无装饰器，内置平台不注册（快照内无内置注册调用方）。证据：gateway/platform_registry.py:38-260
- F-111：适配器基类 `class BasePlatformAdapter(ABC)`（platforms/base.py:1290），4 个抽象方法：async connect()、async disconnect()、async send(chat_id, content, reply_to, metadata) -> SendResult、async get_chat_info(chat_id)；配套 MessageEvent/SendResult/MessageType/ProcessingOutcome。证据：gateway/platforms/base.py:919-3661
- F-112：20 个一对一平台适配器文件与类：TelegramAdapter(telegram.py:320)、DiscordAdapter(:533)、WhatsAppAdapter(:218)、SlackAdapter(:289)、SignalAdapter(:174)、MattermostAdapter(:71)、MatrixAdapter(:317)、HomeAssistantAdapter(:51)、EmailAdapter(:245)、SmsAdapter(:56)、DingTalkAdapter(:146)、APIServerAdapter(api_server.py:1091)、WebhookAdapter(:98)、MSGraphWebhookAdapter(:44)、FeishuAdapter(feishu.py:1407)、WeComAdapter(:142)、WecomCallbackAdapter(:55)、WeixinAdapter(weixin.py:1176)、BlueBubblesAdapter(:100)、YuanbaoAdapter(yuanbao.py:4499)。证据：gateway/platforms/ 各文件
- F-113：QQ 平台在子包：QQAdapter(BasePlatformAdapter) 位于 platforms/qqbot/adapter.py:155（check_qq_requirements:140、QQCloseError:78），由 _create_adapter 导入；platforms/__init__.py 用 PEP 562 __getattr__ 惰性再导出 QQAdapter/YuanbaoAdapter。证据：gateway/platforms/qqbot/adapter.py:78-155；gateway/platforms/__init__.py:34
- F-114：helpers.py 三个共享类 MessageDeduplicator(:27)/TextBatchAggregator(:81)/ThreadParticipationTracker(:201)；另有 10 个辅助文件（feishu_comment*、wecom_crypto.WXBizMsgCrypt、yuanbao_proto/sticker/media、signal_rate_limit、telegram_network、kylin_chat_approval.ChatApprovals、_http_client_limits）。证据：gateway/platforms/{helpers,feishu_comment,wecom_crypto,yuanbao_*,signal_rate_limit,telegram_network,kylin_chat_approval,_http_client_limits}.py
- F-115：投递 DeliveryRouter（deliver/_deliver_to_platform，MAX_PLATFORM_OUTPUT=4000）；配对 PairingStore（is_approved/list_approved/revoke，CODE_TTL_SECONDS/RATE_LIMIT_SECONDS/MAX_FAILED_ATTEMPTS）；频道目录 build_channel_directory/resolve_channel_name。证据：gateway/delivery.py:21-226；gateway/pairing.py:39-138；gateway/channel_directory.py:19-314
- F-116：网关运维：HookRegistry.discover_and_load（hooks.py:64，HOOKS_DIR）；status 运行锁/PID 函数 acquire_gateway_runtime_lock/write_pid_file/is_gateway_running；restart 常量 GATEWAY_SERVICE_RESTART_EXIT_CODE=75；memory_monitor RSS 监控线程（默认 300s）；shutdown_forensics 关停取证；stream_consumer "先发后编辑"流式；runtime_footer 默认字段 (model,context_pct,cwd)；slash_access 斜杠命令授权。证据：gateway/{hooks,status,restart,memory_monitor,shutdown_forensics,stream_consumer,runtime_footer,slash_access}.py
- F-117：镜像 mirror_to_session/_append_to_sqlite；WhatsApp 标识归一化 normalize_whatsapp_identifier/canonical_whatsapp_identifier；贴图缓存 sticker_cache 一族。证据：gateway/{mirror,whatsapp_identity,sticker_cache}.py

## 7. 协议：ACP / MCP / LSP

- F-118：ACP 服务器代理 `class HermesACPAgent(acp.Agent)`（acp_adapter/server.py:445），__init__(session_manager=None)（:516）、on_connect(:523)、async initialize(:821)、async authenticate(:855)、_register_session_mcp_servers(:750)；模块注释明示 stdio-only。证据：acp_adapter/server.py:38-855
- F-119：ACP 入口 entry.main(argv=None)（entry.py:212）调 acp.run_agent(agent, use_unstable_protocol=True)，_parse_args 支持 --version/--check/--setup/--setup-browser。证据：acp_adapter/entry.py:111-212
- F-120：ACP 会话 SessionState(:170)/SessionManager(:186)、任务 cwd 登记 _register_task_cwd/_clear_task_cwd；auth.detect_provider/has_provider/build_auth_methods；permissions.make_approval_callback；edit_approval 的 EditProposal/maybe_require_edit_approval；events 四个回调工厂（tool_progress/thinking/step/message）。证据：acp_adapter/{session,auth,permissions,edit_approval,events,tools}.py
- F-121：MCP 服务器 mcp_serve.py 基于 mcp.server.fastmcp.FastMCP，create_mcp_server(event_bridge=None)（:450），@mcp.tool() 装饰器 10 处（行 471/528/561/618/670/699/733/769/823/839），EventBridge 轮询 SessionDB（:204），run_mcp_server(verbose=False)（:866），无顶层 main()。证据：mcp_serve.py:51-866
- F-122：transports/hermes_tools_mcp_server.py 提供 _build_server/main（把 Hermes 工具暴露为 MCP）。证据：agent/transports/hermes_tools_mcp_server.py:108-197
- F-123：LSP 子系统：进程级单例 get_service()/shutdown_service()（agent/lsp/__init__.py:45-106）；LSPClient（JSON-RPC Content-Length 分帧，start/shutdown/open_file/save_file/wait_for_diagnostics）；LSPService.create_from_config/get_diagnostics_sync；SERVERS 列表 26 个 ServerDef（pyright/typescript/gopls/rust_analyzer/clangd/bash/yaml/lua/...）；LANGUAGE_BY_EXT 69 条扩展名映射；安装 try_install 支持 npm/go/pip 三策略；CLI 子命令 status/list/install/install-all/restart/which。证据：agent/lsp/{protocol,client,manager,servers,install,workspace,cli}.py
- F-124：LSP 诊断配套 range_shift（编辑后行号漂移）、reporter（MAX_TOTAL_CHARS=4000）、eventlog 11 个 log_* 函数。证据：agent/lsp/{range_shift,reporter,eventlog}.py

## 8. Cron 调度

- F-125：cron/ 为函数式调度（无 Scheduler 类）：run_job(job)（scheduler.py:1232）、_run_job_impl（:1239）、tick(verbose=True, adapters=None, loop=None)（:1885）、投递 _resolve_delivery_targets/_deliver_result、prompt 组装 _build_job_prompt 与注入扫描 _scan_assembled_cron_prompt；异常 CronPromptInjectionBlocked。证据：cron/scheduler.py:48-1885
- F-126：作业为 dict 记录：create_job 字段含 prompt/schedule/name/repeat/deliver/origin/skill/skills/model/provider/base_url/script/context_from/enabled_toolsets/workdir/profile/no_agent；parse_schedule/compute_next_run/load_jobs/save_jobs/list_jobs/pause_job；异常 AmbiguousJobReference。证据：cron/jobs.py:99-786
- F-127：desktop_sessions.reconcile_desktop_job_sessions(jobs, db: SessionDB|None) -> int。证据：cron/desktop_sessions.py:15
- F-128：cron/ 包含 4 个 Python 文件：__init__.py、scheduler.py、jobs.py、desktop_sessions.py（无独立 Scheduler 类，函数式调度）。证据：cron/ 目录清单（Q-001）

## 9. 状态存储 SessionDB

- F-129：`class SessionDB` 在 kylin_agent_runtime_state.py:381；`class MemoryDB(SessionDB)` 在 :4050。证据：kylin_agent_runtime_state.py:381,4050
- F-130：9 张普通表：schema_version/sessions/projects/project_roots/messages/state_meta/task_runs/task_subruns/task_checkpoints；后加迁移表 telegram_dm_topic_mode/telegram_dm_topic_bindings。证据：kylin_agent_runtime_state.py:187-3453
- F-131：2 张 FTS5 虚表：messages_fts（USING fts5(content)，三触发器拼接 content+tool_name+tool_calls）、messages_fts_trigram（tokenize='trigram'，注释支撑 CJK 子串检索）。证据：kylin_agent_runtime_state.py:326-358
- F-132：关键方法 create_session(838)/save_project(875)/get_session(1162)/get_session_title(1274)/list_sessions_rich(1392)/append_message(1663)/add_task_checkpoint(2084)/search_messages(2878)/search_sessions(3178)。证据：kylin_agent_runtime_state.py:838-3178

## 10. CLI / TUI / Web Dashboard

- F-133：交互 CLI 类 `class HermesCLI`（cli.py:2609）、ChatConsole（:2380）、_SkinAwareAnsi（:1581），main()（:14235），run()（:11875）。证据：cli.py:1581-14235
- F-134：新 CLI 包入口 main()（kylin_agent_runtime_cli/main.py:10547，文件 13434 行）；build_top_level_parser/_parser.py:82，add_subparsers(dest="command")（_parser.py:229），args.func(args) 分发（main.py:13427），无 command 默认 cmd_chat。证据：kylin_agent_runtime_cli/main.py:10405-13434；kylin_agent_runtime_cli/_parser.py:82-229
- F-135：_BUILTIN_SUBCOMMANDS 冻结集合 48 条；顶层子命令含 chat/model/fallback/migrate/gateway/proxy/setup/postinstall/whatsapp/slack/login/logout/auth/status/cron/webhook/kanban/hooks/doctor/dump/debug/backup/checkpoints/import/config/pairing/skills/bundles/plugins/curator/memory/tools/computer-use/mcp/sessions/insights/claw/version/update/uninstall/acp/profile/completion/dashboard/logs/help；lsp 与 send 经 register_subparser 外挂；无独立 tui 子命令（顶层 --tui/--tui-dev flag 触发）。证据：kylin_agent_runtime_cli/main.py:10405-13200；_parser.py:215-226
- F-136：gateway 二级命令 run/start/stop/restart/status/install/uninstall/list/setup/migrate-legacy（main.py:10704 区段）；GatewayRuntimeSnapshot/ProfileGatewayProcess 与 SIGUSR1 优雅重启（gateway.py:50-205）。证据：kylin_agent_runtime_cli/main.py:10704；kylin_agent_runtime_cli/gateway.py:50-205
- F-137：setup wizard run_setup_wizard(args)（setup.py:3131），含 prompt_choice/prompt_yes_no/prompt_checklist/setup_model_provider。证据：kylin_agent_runtime_cli/setup.py:235-3131
- F-138：dashboard FastAPI：app=FastAPI(title="Hermes Agent", version=__version__)（web_server.py:79），start_server(host="127.0.0.1", port=9119, open_browser=True, allow_public=False)（:4513），uvicorn.run（:4582），mount_spa(app) 挂 web/ 构建产物；cmd_dashboard 启动前构建 web/。证据：kylin_agent_runtime_cli/web_server.py:79-4582；main.py:10282-10318
- F-139：TUI 启动 cmd_chat→_launch_tui（main.py:1433/1259）：子进程跑 ui-tui 的 dist/entry.js（dev 模式 tsx src/entry.tsx），wheel 内探测 tui_dist/entry.js（该目录源码快照不存在）。证据：kylin_agent_runtime_cli/main.py:1102-1107,1259,1567
- F-140：tui_gateway/ 为 TUI 的 Python JSON-RPC 2.0 后端：server.handle_request/dispatch/run（server.py:464-510）、事件帧 {"jsonrpc":"2.0","method":"event"}、entry.main、StdioTransport/TeeTransport/WSTransport/WsPublisherTransport、_SlashWorker 驻留斜杠命令子进程。证据：tui_gateway/{server,entry,transport,ws,event_publisher,slash_worker}.py
- F-141：web/ 前端 package.json name="web"，React 19.2 + Vite + Tailwind v4 + @xterm/xterm 6.0（4 addon）+ @nous-research/ui 0.14 + lucide-react/motion/gsap/@react-three/fiber；build=tsc -b && vite build。证据：web/package.json
- F-142：ui-tui package.json name="hermes-tui"、version 0.0.1、private；以 file:./packages/hermes-ink 本地依赖组织（packages 下仅 hermes-ink 1 个包），ink ^6.8 + React 19 + nanostores，esbuild 打包；start=tsx src/entry.tsx。证据：ui-tui/package.json
- F-143：皮肤引擎 skin_engine：SkinConfig、list_skins/load_skin/get_active_skin/set_active_skin/init_skin_from_config；dashboard 主题键 dashboard.theme 默认 default。证据：kylin_agent_runtime_cli/skin_engine.py:130-790；web_server.py:4007
- F-144：工具配置 tools_config：CONFIGURABLE_TOOLSETS、_DEFAULT_OFF_TOOLSETS、TOOL_CATEGORIES、TOOLSET_ENV_REQUIREMENTS、install_cua_driver；cron CLI 经 _cron_api 与调度器通信（cron_list/create/edit/tick/status）。证据：kylin_agent_runtime_cli/tools_config.py:54-556；kylin_agent_runtime_cli/cron.py:35-285

## 11. 国际化与其他横切

- F-145：i18n：SUPPORTED_LANGUAGES 16 语言码（en/zh/zh-hant/ja/de/es/fr/tr/uk/af/ko/it/ga/pt/ru/hu），DEFAULT_LANGUAGE="en"，get_language/t(key,lang,...)/reset_language_cache；locales/ 16 个 YAML 对应。证据：agent/i18n.py:42-208；locales/ 目录清单
- F-146：进程引导 process_bootstrap：_OpenAIProxy/_get_proxy_for_base_url/_install_safe_stdio；用户目录 get_user_directories 按 sys.platform 分支。证据：agent/process_bootstrap.py:48-145；agent/user_directories.py:103-114
- F-147：常量/引导/时间/日志四个 kylin_agent_runtime_* 根模块：constants.get_hermes_home/display_hermes_home（profile 感知路径）；logging.setup_logging（agent.log/errors.log/gateway.log）；time 模块 82 行；bootstrap 104 行。证据：kylin_agent_runtime_constants.py；kylin_agent_runtime_logging.py；kylin_agent_runtime_time.py；kylin_agent_runtime_bootstrap.py
- F-148：display 工具：LocalEditSnapshot/get_tool_emoji/build_tool_preview/capture_local_edit_snapshot/extract_edit_diff/KawaiiSpinner/get_cute_tool_message；markdown_tables.realign_markdown_tables；async_utils.safe_schedule_threadsafe。证据：agent/{display,markdown_tables,async_utils}.py
- F-149：批处理/评测资产：batch_runner.py（1278 行）、agent_eval_runner.py（470 行）、mini_swe_runner.py（701 行）、trajectory_compressor.py（1465 行）；evals/agent_behavior/README.md；tests/ 含 acp/agent/cli/cron/gateway/tools/run_agent 等测试包。证据：根目录文件与 tests/ 目录清单
- F-150：消息/工具结果清洗 message_sanitization.__all__ 11 项（代理对修复/非 ASCII 处理/图片剥离等）。证据：agent/message_sanitization.py:432-444

## Q. 数量事实（计数口径与复核记录）

> 纪律：每个数量附 R 阶段计数命令、口径（含/不含什么、原始匹配 vs 去重名）；V 阶段以独立手段复核（见 tasks.md TR-8.2）。

- Q-001：Python 文件数（口径：`Get-ChildItem -Recurse -File -Filter *.py`，含 __init__.py，不含 .git/embeddings 产物）：agent/ 120（=根 86 + transports 11 + lsp 11 + user_profile 12）、plugins/ 118、tools/ 93（=根 76 + environments 12 + computer_use 5）、kylin_agent_runtime_cli/ 94（=顶层 87 + proxy 7）、gateway/ 64、tests/ 1199、optional-skills/ 48、skills/ 33、scripts/ 14、acp_adapter/ 10、tui_gateway/ 8、cron/ 4、providers/ 2、website/ 3、根目录散文件 18。
- Q-002：gateway/platforms 直接子文件 *.py（排除 __init__.py）= 32 = 20 个一对一适配器 + base.py + helpers.py + 10 个辅助文件；Platform 枚举内置成员 22 个（LOCAL + 21 外部平台），另有 qqbot 适配器在 qqbot/ 子包（枚举含 QQBOT），即适配器实现共 21 个。
- Q-003：TOOLSETS 字典顶层键 31 个（正则 `^    "[a-z_]+":\s*\{` 实测 31 行）；_HERMES_CORE_TOOLS 列表为单条共享事实（F-050），其成员数 V 阶段如文档引用再计数。
- Q-004：注册传输类 4 个（Select-String `^register_transport\(` = 4）；LSP ServerDef 26 个（区间正则）；LANGUAGE_BY_EXT 69 条；CLI _BUILTIN_SUBCOMMANDS 48 条；VALID_HOOKS 17 个；MCP @mcp.tool() 10 处；FailoverReason 18 成员；PLATFORM_HINTS 19 键；SUPPORTED_LANGUAGES/locales 16。
- Q-005：插件目录 17 个；记忆后端 8 个；Web 搜索后端 8 个；skills/ 顶层目录条目 25 个（含隐藏 .curator_backups）、递归目录 179 个、SKILL.md 77 个；optional-skills 顶层分类 17 个。
- Q-006：SessionDB 表：9 张普通表 + 2 张 Telegram 迁移表 + 2 张 FTS5 虚表。
- Q-007：版本号多处：pyproject 1.0.1（打包版本）、git describe V0.9.4-52（最近上游 tag 血缘）、CLI 包 __version__ 0.9.4（2026.7.24）、agent.json 0.9.3、skills/kylin-cua/version 0.9.8。
- Q-008：根脚本行数（`Get-Content | Measure-Object -Line`，该口径对 lone-CR 混合换行偏少）：cli.py 13108、run_agent.py 3810、kylin_agent_runtime_state.py 3692、trajectory_compressor.py 1465、batch_runner.py 1278、model_tools.py 849、toolsets.py 771、mcp_serve.py 745、mini_swe_runner.py 701、agent_eval_runner.py 470。gateway/run.py ripgrep 口径至少 18249 行而 Measure-Object 口径 16612（混合换行差，行号引用一律用 ripgrep 口径）。
- Q-009：终端环境叶子后端 8 个（TERMINAL_ENV 可选）：Local/Docker/SSH/Modal/ManagedModal/Daytona/Singularity/VercelSandbox；类继承树共 9 个类——另有中间基类 BaseModalExecutionEnvironment(BaseEnvironment)，仅 ManagedModal 继承它，ModalEnvironment 直接继承 BaseEnvironment（V 阶段 Python 复核口径，见 E-008）。
- Q-010：用户画像 FIELDS 81 + LEGACY_FIELDS 29 = 110 个 FieldDefinition；PROVIDER_TO_MODELS_DEV 35 条；IDEMPOTENT_TOOL_NAMES 16 / MUTATING_TOOL_NAMES 15；redact 密钥正则 36 条。

## 勘误与审计留痕

- E-001（2026-10-14 R 阶段）：终端后端数量，初版口头盘点写"7 个具体后端"，按 environments/ 文件枚举实为 8 个类（含 managed_modal 与 vercel_sandbox）；以 Q-009 枚举为准，文档采用"8 个后端实现"。
- E-002：Specify 阶段预盘 platforms"32 个平台文件"与 R 阶段一致（32 个文件），但需区分"32 个 .py 文件"与"21 个平台适配器实现 / 22 个枚举成员"；文档按此区分表述。
- E-003：多处 hermes/kylin 双命名并存（portal_tags 代码返回 product=kylin-agent 而 docstring 示例写 hermes-agent；FastAPI title="Hermes Agent"；ui-tui 包名 hermes-tui；HERMES_* 环境变量）——属事实，00-overview 血缘章节如实陈述，不做对错判断。
- E-004：ContextCompressor 入参 threshold_percent=0.50 被函数体 0.80 无条件覆盖（context_compressor.py:512 vs :533）——代码事实，洞察阶段作为技术债线索。
- E-005：疑点（未验证不结论）：agent/ 根 86 个 py 中 12 个文件未深采（agent_runtime_helpers/azure_identity_adapter/chat_completion_helpers/codex_runtime/codex_responses_adapter/conversation_compression/gemini_cloudcode_adapter/google_oauth/mainline_orchestration/manual_compression_feedback/tool_dispatch_helpers/tool_result_classification）；巨型文件仅采顶层符号；纯静态分析未执行运行时验证。
- E-006：快照残留文件 gateway/platforms/api_server.py.before-kylin-approvals（非 .py，不入口径）；kylin_agent_runtime_cli/web_dist 与 tui_dist 在源码快照不存在（仅 wheel 打包路径）。
- E-008（2026-10-14 V 独立复核）：终端环境继承关系修正——R 卡 F-057 误述 ModalEnvironment 共享 BaseModalExecutionEnvironment；实测 ModalEnvironment(modal.py:164) 直接继承 BaseEnvironment，BaseModalExecutionEnvironment(modal_utils.py:58) 仅被 ManagedModalEnvironment 继承。叶子可选后端 8 个结论不变，类继承树共 9 个类（含中间基类）；04 篇与 F-057/Q-009 已同步。
- E-007（2026-10-14 V 前核对）：三处符号行号采集偏差（符号真实存在，快照零漂移）：probe_gemini_tier 61→47（gemini_native_adapter.py:47）、CopilotACPClient 321→334（copilot_acp_client.py:334，321 为同文件 _ACPChatCompletions 区段）、apply_anthropic_cache_control 41→49（prompt_caching.py:49）。F-070/F-071/F-077 与 concepts/05 已同步修正。
