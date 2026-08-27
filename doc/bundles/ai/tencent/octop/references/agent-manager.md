---
type: Reference
title: "AgentManager：Agent 生命周期与 Harness 委托"
description: "AgentManager 类的源码信源登记，涵盖 CRUD、生命周期、运行时访问、热重载、MCP 工具缓存、Provider/Security/Langfuse 等 settings stores。"
tags: [octop, agent, harness-agent, lifecycle, hot-reload, mcp]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-051~F-072
---

# AgentManager：Agent 生命周期与 Harness 委托

本信源登记 `src/octop/infra/agents/manager.py` 的全部可验证事实。

## 类定义与依赖

```python
from harness_agent import HarnessAgent, HarnessAgentConfig, HarnessAgentManager
from harness_agent.security.models import SecurityPolicy

class AgentManager:
    def __init__(
        self, *,
        repos: RepoBundle,
        paths: PathLayout,
        config: OctopConfig | None = None,
        expert_catalog: ExpertCatalog | None = None,
        plugin_manager: PluginManager | None = None,
    ) -> None: ...
```

AgentManager 是进程级单例，拥有 harness `HarnessAgentManager` 和所有 `HarnessAgent` 实例（F-051、F-052）。

## 持有的 Settings Stores

| Store | 类型 | 用途 |
|-------|------|------|
| `_langfuse` | `LangfuseSettingsStore` | Langfuse 追踪配置 |
| `_security` | `SecuritySettingsStore` | 安全策略 |
| `_acp_settings` | `ACPSettingsStore` | ACP runner 配置 |
| `_tool_guard_rules` | `ToolGuardRulesStore` | 工具审批规则 |
| `_providers` | `ProviderStore` | LLM Provider 管理 |
| `_connector_svc` | `ConnectorService` | 连接器/MCP 服务 |

来源：F-053。

## AgentCreateSpec

创建 Agent 的输入规格（F-054），字段包括：
`name`、`agent_id`（可选，自定义 ID）、`user_id`、`description`、`persona_mbti`、`default_model`、`system_prompt`、`icon`、`template_name`、`is_shared`、`icon_name`、`icon_url`、`color`、`skill_package_ids`、`published_expert_id`、`welcome_message`、`runtime_config`、`config`。

### Agent ID 校验

- 正则：`^[a-zA-Z0-9][a-zA-Z0-9_-]{1,62}[a-zA-Z0-9]$`（3-64 字符）
- 保留 ID：`{"api", "admin", "agents", "experts"}`
- 未指定时通过 `new_short_id()`（ULID）生成，最多重试 16 次

来源：F-055。

## 生命周期方法

### boot()

```
seed tool_guard_rules
→ providers.build_harness_configs()
→ HarnessAgentManager(providers, langfuse, team_processor)
→ set_security_policy()
→ agent_repo.list_all(include_disabled=False)
→ for row (跳过 last_state=="stopped"): _start_agent(row)
```

来源：F-056。

### shutdown()

获取 `asyncio.Lock` 后调用 `harness_manager.close()`（F-057）。

### create(spec, defer_bootstrap=False)

完整流程（F-058）：
1. 校验 agent name 可用
2. 若指定 agent_id，校验格式和唯一性；否则生成 ULID
3. 合并 runtime_config 到 config
4. 若有 persona_mbti，写入 `config["persona"] = mbti.upper()`
5. `seed_workspace_dir_on_create` 初始化工作区
6. 强制 `system_files_path` 为内部默认值（不可用户配置）
7. extract/strip profile config
8. 写入 DB（`agent_repo.create`）
9. 可选 set_shared
10. 可选 seed expert template
11. `defer_bootstrap=True`：异步 task bootstrap；否则同步 `_start_agent(row, init_workspace=True)`
12. 写审计日志 `agent.create`

### update(agent_id, **kwargs)

- 分离 `AGENT_RUNTIME_CONFIG_KEYS` 合并到 config_json
- preserve `system_files_path`（用户不可修改内部布局控制）
- extract profile 字段提升到列
- 名称变更时校验可用性
- `agent_repo.update_config` → `_schedule_reload(agent_id)`

来源：F-059。

### delete(agent_id)

从 harness 移除 → 删除 workspace 目录（shutil.rmtree）→ 删除 DB 行 → 审计日志（F-060）。

### start / stop

- `start(agent_id)`：加载 agent 到 harness 运行时
- `stop(agent_id)`：从 harness 卸载，持久化 `last_state="stopped"`

来源：F-061。

## 运行时访问

| 方法 | 返回 | 异常 |
|------|------|------|
| `get_agent(agent_id)` | `HarnessAgent` | AGENT_NOT_FOUND / AGENT_FAILED / AGENT_NOT_RUNNING |
| `get_row(agent_id)` | `AgentRow \| None` | — |
| `stream(agent_id, request)` | `AsyncIterator` | 同上 |
| `call(agent_id, request)` | `dict` | 同上 |
| `resume_hitl(agent_id, thread_id, decisions)` | `AsyncIterator` | 同上 |
| `cancel_stream(agent_id, thread_id)` | `None` | — |

来源：F-062、F-063、F-064。

### Thread Model 覆盖

`get_thread_model` / `set_thread_model` / `clear_thread_model` 支持 per-thread 模型切换（F-065）。

### Checkpoint 删除

`delete_thread_checkpoint(agent_id, thread_id) -> bool`：最佳努力删除 LangGraph checkpointer 中的真实对话数据。Octop 的 `thread_registry` 仅追踪 UI 元数据，真实消息在 checkpointer 中（F-072）。

## 热重载

### 三种粒度

| 方法 | 范围 |
|------|------|
| `reload(agent_id)` | 重建单个 agent 的 harness 运行时 |
| `reload_all()` | 有界并行（并发上限 6）重建所有 enabled agents |
| `reload_harness_agents()` | 仅重建 harness 侧（不从 DB 重读 Octop config） |

来源：F-067。

### on_provider_changed

```
providers.build_harness_configs()
→ sync_providers_to_harness()
→ _provider_reload_impact_ids(provider_name, active_model_changed)
→ _reload_agents(impact_ids)  # Semaphore(6) 有界并行
```

影响集合计算逻辑（F-066）：
- 无参数时：所有 enabled agents
- 指定 provider_name：引用该 provider 的 agents + failed/created 状态的 agents
- active_model_changed=True：使用 auto default model 的 agents 也受影响

## MCP 工具缓存

```python
_mcp_tool_cache: dict[tuple[int, str, str], list[Any]]
# key = (user_id, server_name, fingerprint)
```

- 通过 `harness_agent.mcp.aload_mcp_tools` 加载
- `wrap_tools_for_shared_use` 包装以支持跨 agent 共享
- 每 user/server 有 asyncio.Lock 防止并发重复加载
- fingerprint 变更时自动清理旧缓存

来源：F-068。

### prepare_chat_mcp

`prepare_chat_mcp(agent_id, names, *, connector_user_id=None) -> list[str]`：
确保请求的 MCP servers 已配置且工具已加载，返回加载失败的 server 名列表（F-069）。

## 工作区解析

`resolve_workspace_dir(agent_id, *, persist_if_missing=True) -> Path`：
- 优先使用 config 中的 `workspace_dir`
- 回退到 `~/.octop/agents/<agent_id>/`
- 可将 agent 面向的 `/.octop/workspaces/…` 映射到 scoped root_dir

来源：F-071。

## 控制面重绑定

`replace_persistence(repos, config)` 在控制面 DB 热交换后重建所有 settings stores（langfuse/security/acp_settings/providers/connector_svc）（F-070）。

## 相关概念

- [/concepts/02-agent-runtime.md](../concepts/02-agent-runtime.md)
- [/concepts/05-acp-protocol.md](../concepts/05-acp-protocol.md)
- [/concepts/04-db-di.md](../concepts/04-db-di.md)
