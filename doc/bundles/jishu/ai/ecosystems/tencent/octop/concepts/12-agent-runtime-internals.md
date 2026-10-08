---
type: Concept
title: "Agent 运行时内部：装配、会话模式、模型与工具供给"
description: "AgentManager 核心常量与 harness 装配、ask/plan/craft 三会话模式、providers 模型供给（reasoning/ONNX/presets）、42 条内置工具目录、设置面、安全、记忆瘦身与工作区线程机制。"
tags: [octop, agent, runtime, conversation-mode, providers, onnx, tools, security, memory, workspace]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-206~F-214、F-254~F-271（v1.0.2b5）
  - id: mgr
    resource: /references/agent-manager.md
    title: AgentManager 源码信源
---

# Agent 运行时内部：装配、会话模式、模型与工具供给

[02-agent-runtime.md](02-agent-runtime.md) 已介绍 AgentManager 的角色、Agent CRUD、热重载与 MBTI 人格。本篇只补 v1.0.2 运行时的**内部机制面**：模块级常量如何约束装配、ask/plan/craft 三种会话怎样落到 harness 请求、模型与工具从哪里供给，以及安全、记忆、工作区等子系统如何被组装进单个 `HarnessAgentConfig`。

## 1. AgentManager 核心常量

`src/octop/infra/agents/manager.py` 用四个模块级常量固定运行时的并发、命名与状态边界（F-206）：

```python
_PROVIDER_RELOAD_CONCURRENCY = 6
_MEMORY_NS_PREFIX = "agent_"
_AGENT_STATES_NEEDING_MODEL_RELOAD = frozenset({"failed", "created"})
_HARNESS_AGENT_CONFIG_FIELDS = frozenset(item.name for item in fields(HarnessAgentConfig))
```

| 常量 | 含义 |
|------|------|
| `_PROVIDER_RELOAD_CONCURRENCY = 6` | Provider 变更后批量重建 Agent 的 `asyncio.Semaphore` 上限（F-206） |
| `_MEMORY_NS_PREFIX = "agent_"` | octop-memory 以 `{namespace}_*` 建 SQLite 表，namespace 必须是合法裸 SQL 标识符（F-206） |
| `_AGENT_STATES_NEEDING_MODEL_RELOAD` | `failed`/`created` 状态的 Agent 在 provider 影响分析中一律纳入重建集（F-206） |
| `_HARNESS_AGENT_CONFIG_FIELDS` | 从 harness 包 dataclass 反射出的合法配置字段集合，用于过滤 Octop 侧多余键（F-206） |

记忆 namespace 由单一函数生成，前缀与 Agent id 直接拼接（F-207）：

```python
def _memory_namespace(agent_id: str) -> str:
    return f"agent_{agent_id}"
```

自定义 Agent id 必须匹配 `^[a-zA-Z0-9][a-zA-Z0-9_-]{1,62}[a-zA-Z0-9]$`，且不得使用保留 id `api`、`admin`、`agents`、`experts`（F-208）。`AgentCreateSpec` 是含 22 个字段的 dataclass，`kind` 默认 `"expert"`，合法取值仅 `expert`/`team`，非法值回落 `expert`（F-209、F-210）。

## 2. harness 装配：中间件链八连

`_build_harness_config`（manager.py:2978）把 DB 行、provider、插件与安全策略收敛为一个 `HarnessAgentConfig`。插件中间件链先由全局插件注册表构造，随后追加 8 个 Octop 自有中间件（F-211）：

```python
agent_middleware = [
    TokenQuotaMiddleware(policy_repo=..., usage_repo=...),  # :3123
    ReasoningRequestMiddleware(),                           # :3127
    KnowledgeSearchHintMiddleware(),                        # :3128
    BrowserProfileMiddleware(),                             # :3129
    BinaryReadGuardMiddleware(),                            # :3130
    WorkspaceImageMaterializeMiddleware(workspace=ws),      # :3131
    ThreadArtifactsMiddleware(thread_repo=..., ...),        # :3132
    OctopUiOffloadMiddleware(),                             # :3137
]
```

七个中间件类均继承 `langchain.agents.middleware.AgentMiddleware[Any, Any]`（F-224）。两个装配细节值得注意（F-211）：

- 团队主持人的 `agent_list`/`ask_agent` 由 `PeerAgentMiddleware(team_enabled=True)` 提供，**不**走 `config.tools`（manager.py:3146 注释原文）；
- 最终构造实参含 `middleware=agent_middleware or None`、`tools=merged_tools or None`、`bootstrap_enabled=not team_host`——团队主持人不做 bootstrap。

## 3. ask / plan / craft 三会话模式

会话模式的策略源头（SoT）在 octop-harness，Octop 侧 `conversation_mode.py` 只做宿主叠加。模式解析遵循三级优先级（F-213）：

```
explicit（合法模式串） → thread sticky（线程粘滞） → DEFAULT_CONVERSATION_MODE
```

`resolve_conversation_mode(*, explicit=None, thread_mode=None)` 的 docstring 原文为 `"explicit (if a valid mode string) → thread sticky → craft."`；explicit 非空但不属于 `{"ask", "plan", "craft"}` 时返回导入的 `DEFAULT_CONVERSATION_MODE`（F-213）。

宿主侧对 ask/plan 的收窄由 `stamp_conversation_mode` 完成（F-214）：

```python
HOST_READ_TOOLS: tuple[str, ...] = ("search_knowledge",)

def stamp_conversation_mode(request, mode) -> None:
    configurable[CONFIG_MODE_KEY] = mode
    if mode in ("ask", "plan"):
        configurable[CONFIG_EXTRA_READ_KEY] = list(HOST_READ_TOOLS)
        request["skills"] = []
        request["mcp_servers"] = []
        configurable["skills"] = []
        configurable["mcp_servers"] = []
        configurable.pop("mcp_use_default", None)
    request["configurable"] = configurable
    request["conversation_mode"] = mode
```

即 ask/plan 模式下只额外开放只读的 `search_knowledge`，同时清空技能与 MCP 供给（F-214）。plan 模式的计划文件受白名单约束：`plans/[a-zA-Z0-9][a-zA-Z0-9._-]{0,120}\.md`（F-212）。IM/CLI 中「执行计划/开始干/execute the plan」等 9 个精确词条与 4 条包含词条会被识别为执行待办计划的指令（F-212）。

## 4. providers：模型供给子系统

### 4.1 推理能力归一

`providers/reasoning.py` 把各厂商差异化的推理参数归一为 8 个适配器（F-254）：

```python
REASONING_MODES = frozenset({"auto", "enabled", "disabled"})
REASONING_ADAPTERS = frozenset({
    "status_only", "thinking", "thinking_nested_effort",
    "openai_reasoning_effort", "anthropic_adaptive", "anthropic_budget",
    "dashscope", "openrouter",
})
EFFORT_TYPES = frozenset({"enum", "token_budget"})
```

按 token 计划计费的 8 个模型 id 单独成集（F-254）：`tc-code-latest`、`minimax-m2.5`、`minimax-m2.7`、`glm-5`、`glm-5.1`、`kimi-k2.5`、`deepseek-v4-flash-202605`、`deepseek-v4-pro-202606`。`reasoning_capability(model, *, base_url=None)` 返回 `supported/toggle/default_mode/efforts/default_effort/effort_type/adapter` 七键 dict（F-254）。请求期的覆盖由 `ReasoningRequestMiddleware` 在 `wrap_model_call/awrap_model_call` 两个钩子上落地，配置键为 `octop_reasoning_overrides`，读 `model_fields` 与 `extra_body`（F-226）。

### 4.2 本地 ONNX 嵌入

`onnx_catalog.py` 预置 3 个推荐模型，另在 fastembed 不可导入时展示 9 个扩展条目（F-255）：

| 集合 | 模型 id（逐字） |
|------|----------------|
| `ONNX_PRESET_MODEL_IDS`（3） | `BAAI/bge-small-zh-v1.5`、`jinaai/jina-embeddings-v2-base-zh`、`intfloat/multilingual-e5-large` |
| `_EXTRA_CATALOG_IDS`（9） | bge-small-en-v1.5、bge-base-en-v1.5、bge-large-en-v1.5、jina-embeddings-v2-base-en、jina-embeddings-v2-small-en、all-MiniLM-L6-v2、paraphrase-multilingual-MiniLM-L12-v2、gte-base、gte-large |

三个预置模型的兜底体积分别为 0.09/0.32/1.2 GB（F-255）。下载侧 `onnx_download.py` 的策略是「Race COS, Hugging Face, and hf-mirror」三路竞速：官方站 `https://huggingface.co`、镜像 `https://hf-mirror.com`、腾讯云 COS `https://octop-1258344699.cos.ap-guangzhou.myqcloud.com`（前缀 `models/embedding`、清单名 `files.json`、revision 字面 `cos-mirror`），探测超时 4 秒（F-257）。

本地服务由 `onnx_service.py` 管理：settings 键 `onnx_local_service`，pip 依赖 spec 为 `fastembed>=0.4` 与 `huggingface_hub>=0.20`，运行时 pip 安装需环境变量 `OCTOP_ALLOW_RUNTIME_PIP` 取值 `{1,true,yes,on}`；下载状态机 `OnnxDownloadStatus` 五态 `idle/downloading/loading/done/failed`；模块级单例 `DOWNLOAD_MANAGER = OnnxDownloadManager()`（F-256）。

### 4.3 provider 登记、预设与 codex OAuth

`ProviderStore` 的 `KIND_TO_PROTOCOL` 映射 5 键：openai/anthropic 同名，ollama/azure/gemini 均归化为 `"openai"` 协议（F-258）。模型引用形态为 `f"{provider_name}/{model_id}"`（F-258）。

`load_provider_presets()` 从包资源 `octop_harness.providers/provider_template.json` 加载模板，并补两个内置预置（F-259）：

- 缺 `openai-codex` 时插入：base_url `https://chatgpt.com/backend-api/codex`、protocol `openai`、auth_method `codex_oauth`，含 `gpt-5.4`/`gpt-5.4-mini`/`gpt-5.5` 三个模型；
- 缺 `onnx` 时在 ollama 之后插入，模型项 `enabled=False, "embedding": True, "task": "embedding"`。

`sync_providers_to_harness(harness_manager, providers, *, shared_factory=None)` 以差量方式对 harness factory 执行 add/remove provider（F-259）。

## 5. 工具供给：42 条内置目录

`settings/tool_catalog.py` 的 `BUILTIN_TOOL_CATALOG` 是一个 42 条 `BuiltinToolEntry(name, category)` 的元组，专供工具设置对话框与禁用策略使用（不含 MCP 工具）（F-260）：

| category | 数量 | 代表工具 |
|----------|---:|----------|
| filesystem | 7 | ls、read_file、write_file、edit_file、glob、grep、execute |
| orchestration | 2 | write_todos、task |
| web | 8 | web_fetch、browser_use、desktop_screenshot、5 个搜索工具 |
| misc | 5 | current_time、send_file_to_user、read/write_env_file、acp_runner |
| cron | 6 | cronjob_list/get/create/update/delete/run_now |
| mobile | 6 | mobile_screenshot/tap/swipe/launch_app/ui_dump/handoff_to_user |
| media / memory / teams | 各 2 | generate_image/video；memory_search/get；agent_list/ask_agent |
| interaction / knowledge | 各 1 | ask_user_question；search_knowledge |

六个关键工具 `ls/read_file/glob/grep/write_todos/task` 组成 `CRITICAL_TOOLS`，即使出现在 `tools_disabled` 中也会被 `normalize_tools_disabled` 剔除（排序去重后减去关键集）（F-260）。`acp_runner` 条目默认不可用，需读 `acp.tool_enabled` 才放行（F-260）。

## 6. 设置面：运行时限额、profile、ACP、媒体与 Langfuse

| 设置模块 | 关键事实 |
|----------|----------|
| runtime_limits | `AGENT_RUNTIME_CONFIG_KEYS` 5 键：max_iters/max_input_length/temperature/top_p/max_tokens；默认输入上限 128_000 token；temperature 区间 [0.0, 2.0]、top_p [0.0, 1.0]（F-261） |
| profile | `PROFILE_CONFIG_KEYS` 9 键：expert_id/icon_name/icon_url/color/skill_package_ids/published_expert_id/welcome_message/knowledge_base_ids/mcp_servers；expert_id 提升为列键 `template_name`（F-262） |
| acp | settings 前缀 `acp_runners:user:`；内置 3 个 runner（kimi_code/cursor_cli/pi，命令分别为 `kimi acp`、`agent acp`、`npx -y pi-acp`，均 trusted）；隐藏 runner `qwen_code`（F-263） |
| media_generation | 厂商 Literal `volcengine/dashscope/minimax`，最多 8 个 provider；默认火山引擎，默认图模型 `doubao-seedream-5-0-lite-260128`、视频模型 `doubao-seedance-2-0-mini-260615`；预置 3 家共 11 图 11 视频模型（F-263） |
| langfuse | settings 键 `observability_langfuse_enabled/public_key/host` + secret 键 `langfuse_secret_key`；校验 URL `{base}/api/public/projects`，urlopen 超时 15 秒（F-263） |

## 7. 安全三件套

- **policy_store**：settings 键 `security_policy`；默认策略在 `SecurityPolicy.defaults()` 上覆盖 `hitl.enabled = False`、`tool_guard = {"enabled": True, "mode": "warn"}`（F-265）。
- **tool_guard_rules**：规则展示路径 `~/.octop/security/tool_guard/{rules_file.name}`；`ensure_seeded` 在文件缺失时写入 bundled YAML；保存前先 `validate_rules_yaml`，返回 `(规则数, [])`（F-265）。
- **hitl_session**：模式 Literal `ask/allow_all/allow_tools`，审批工具固定 `ask_user_question`，工具数上限 64、工具名上限 128；策略经 `HitlSessionPolicyStore` 写到 thread 行的 composer 上。该模块**没有定义任何 TTL/过期常量**——HITL 策略随线程持久化，直到被显式改写（F-264，源码目录 grep TTL/expire 无命中）。

## 8. 记忆后端与 slim 三件套

记忆后端由配置形态四选一决定（F-266）：省略/null；`{"type":"sqlite","db_path":...}`（默认落到宿主系统目录下 `memory.sqlite`）；`{"type":"postgres","dsn":...}`；`{"type":"postgres","use_control_plane_dsn": true}`（控制面为 PG 时省略配置也会回落同 DSN）。打开记忆时 namespace 固定为 `f"agent_{agent_id}"`（F-266）。

记忆瘦身由三个文件协作（F-267）：

```python
# slim_control.py —— 进程内本地控制端点
ENDPOINT = "memory-slim-control.json"
asyncio.start_server(self._handle, "127.0.0.1", 0, limit=8192)
# token = secrets.token_hex(32)，比较用 hmac.compare_digest；落盘键 port/token/pid
```

`slim_control` 提供 `list`/`slim` 两个 operation，轮询间隔 0.25 秒；`slim.py` 的 `MemorySlimCoordinator` 只接受 `SqliteMemoryBackend` + `CompactSqliteSaver`，PG 后端直接走报错分支（F-267）。`launch.py` 在服务前后对该控制端点做 start/close（F-162）。

## 9. 工作区与线程：execute_env、artifact、fork、context_breakdown

- **workspace/dir**：系统目录常量 `.octop`，scoped 目录 `workspaces`，Agent 私有路径形态 `/.octop/workspaces/{agent_id}`；技能发现根为工作区下 `.octop/skills` 与 `skills` 两条（F-268）。
- **execute_env**：可执行后端 kind 仅 `local_shell`/`docker`；注入 4 个环境变量 `OCTOP_AGENT_ID/OCTOP_AUTH_DIR/OCTOP_HOME/OCTOP_SKILLS_DIR`；local_shell 分支默认 `inherit_env=True`，composite 后端递归注入（F-269）。
- **threads/artifact**：6 个产物工具基（write_file/edit_file/send_file/send_file_to_user/desktop_screenshot/mobile_screenshot）配 6 个路径键；路径必须锚定 outbound/inbound/generated，拒绝 `/_builtin_skills/` 与纯数字 basename（F-270）。
- **threads/fork**：分叉历史上限 `_FORK_HISTORY_LIMIT = 100_000`；无可分叉的 assistant 消息时抛 `NOT_FOUND "no assistant message to fork from"`（F-271）。
- **context_breakdown**：7 段兜底分段键 `system_prompt/tool_definitions/rules/skills/mcp/subagent_definitions/conversation`，优先从 `octop_harness.context_usage` 导入；空结果上限回落 128_000（F-271）。

## 相关概念

- [/concepts/02-agent-runtime.md](02-agent-runtime.md)——AgentManager 全貌与 CRUD/热重载
- [/concepts/13-plugin-system.md](13-plugin-system.md)——插件与技能包双扩展体系
- [/concepts/16-history-trajectory.md](16-history-trajectory.md)——运行时轨迹如何被记录
