---
type: Concept
title: "Agent 运行时：AgentManager、HarnessAgent 与专家库"
description: "AgentManager 进程级单例、HarnessAgent 委托、Agent CRUD 与生命周期、Provider/Security/Langfuse 设置、MBTI 16 种人格、专家库与子代理目录。"
tags: [octop, agent, harness-agent, mbti, experts, provider, lifecycle]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/agent-manager.md
    title: AgentManager 源码信源
---

# Agent 运行时：AgentManager 与 HarnessAgent

Octop 的 Agent 运行时由 `AgentManager` 编排，但实际的 AI 执行逻辑委托给外部包 `orcakit-harness-agent` 中的 `HarnessAgent` / `HarnessAgentManager`（I-03）。

## AgentManager 的角色

`AgentManager` 是进程级单例（F-051），负责：

1. **持有 harness 运行时**：`HarnessAgentManager` 实例管理所有 live `HarnessAgent`
2. **DB ↔ 运行时同步**：Agent 行的 CRUD 操作同步更新 harness 运行时
3. **配置组装**：从 DB 行、Provider、安全策略、MCP 连接器等组装 `HarnessAgentConfig`
4. **热重载**：Provider/模型/安全规则变更时有界并行重建 Agent
5. **Settings stores**：管理 Langfuse、Security、ACP、ToolGuard、Provider 配置

```python
class AgentManager:
    def __init__(self, *, repos, paths, config=None,
                 expert_catalog=None, plugin_manager=None):
        self._harness_manager: HarnessAgentManager | None = None
        self._langfuse = LangfuseSettingsStore(...)
        self._security = SecuritySettingsStore(...)
        self._acp_settings = ACPSettingsStore(...)
        self._tool_guard_rules = ToolGuardRulesStore(paths=paths)
        self._providers = ProviderStore(provider_repo=...)
        self._connector_svc = ConnectorService(...)
```

## 启动流程

`boot()` 方法（F-056）：

```
1. tool_guard_rules.ensure_seeded()
2. providers.build_harness_configs() → provider 配置列表
3. HarnessAgentManager(providers, langfuse, team_processor)
4. harness_manager.set_security_policy(security.harness_policy())
5. agent_repo.list_all(include_disabled=False)
6. for row in rows:
     if row.last_state == "stopped": skip
     await _start_agent(row)
```

启动时跳过 `last_state="stopped"` 的 Agent，使其保持停止状态直到用户显式启动。

## Agent CRUD

### 创建 Agent

`create(spec: AgentCreateSpec, *, defer_bootstrap=False)`（F-058）：

1. 校验 Agent name 在用户范围内唯一
2. Agent ID：自定义（需匹配 `^[a-zA-Z0-9][a-zA-Z0-9_-]{1,62}[a-zA-Z0-9]$`）或自动生成 ULID
3. 合并 runtime_config 到 config
4. MBTI 人格写入 `config["persona"] = mbti.upper()`
5. 初始化工作区目录（`seed_workspace_dir_on_create`）
6. `system_files_path` 强制为内部默认值（不可用户配置）
7. 提取 profile 字段（template_name、color、skill_package_ids 等）
8. 写入 DB
9. 可选设置 shared、seed expert template
10. `defer_bootstrap=True`：异步 task 启动；否则同步启动
11. 写审计日志

### 更新 Agent

`update(agent_id, **kwargs)`（F-059）：
- 分离 `AGENT_RUNTIME_CONFIG_KEYS` 合并到 config_json
- 保留 `system_files_path`（用户不可修改）
- 提取 profile 字段提升到列
- 更新 DB 后调度 `_schedule_reload(agent_id)` 后台热重载

### 删除 Agent

`delete(agent_id)`（F-060）：
1. 从 harness 运行时移除
2. 删除工作区目录（`shutil.rmtree`）
3. 删除 DB 行
4. 写审计日志

## 运行时访问

| 方法 | 用途 | 异常 |
|------|------|------|
| `get_agent(agent_id)` | 获取 live `HarnessAgent` | AGENT_NOT_FOUND / AGENT_FAILED / AGENT_NOT_RUNNING |
| `stream(agent_id, request)` | 流式对话 | 同上 |
| `call(agent_id, request)` | 一次性调用 | 同上 |
| `resume_hitl(agent_id, thread_id, decisions)` | 恢复 HITL 中断 | 同上 |
| `cancel_stream(agent_id, thread_id)` | 取消正在进行的流 | — |

`get_agent` 的错误映射逻辑（F-062）：
- 无 DB 行 → `AGENT_NOT_FOUND`
- DB 行状态为 failed/error → `AGENT_FAILED`
- 其他（未加载到 harness）→ `AGENT_NOT_RUNNING`

### Thread Model 覆盖

每个对话线程可以临时切换模型（F-065）：
- `get_thread_model(agent_id, thread_id)`
- `set_thread_model(agent_id, thread_id, model)`
- `clear_thread_model(agent_id, thread_id)`

### Checkpoint 删除

`delete_thread_checkpoint(agent_id, thread_id)` 删除 LangGraph checkpointer 中的真实对话数据。Octop 的 `thread_registry` 仅追踪 UI 元数据（标题、置顶、最后活跃时间），真实消息内容在 checkpointer 中（F-072）。

## 热重载机制

### 三种粒度

| 方法 | 范围 | 用途 |
|------|------|------|
| `reload(agent_id)` | 单个 Agent | 插件安装后 |
| `reload_all()` | 所有 enabled Agents | 批量变更 |
| `reload_harness_agents()` | 仅 harness 侧重建 | tool guard 规则变更（不从 DB 重读 Octop config） |

来源：F-067。

### Provider 变更影响分析

`on_provider_changed(*, provider_name=None, active_model_changed=False)`（F-066）：

```
1. sync_providers_to_harness()  # 同步 provider 到 harness factory
2. _provider_reload_impact_ids(provider_name, active_model_changed)
3. _reload_agents(impact_ids)   # Semaphore(6) 有界并行
```

影响集合计算：
- **无参数**（备份恢复/OAuth/未知）：所有 enabled agents
- **指定 provider**：引用该 provider 的 agents + failed/created 状态 agents
- **active_model_changed**：使用 auto default model 的 agents 也加入影响集

有界并行通过 `asyncio.Semaphore(6)` 实现（`_PROVIDER_RELOAD_CONCURRENCY = 6`），防止同时重建数十个 Agent 导致资源尖峰。

## MCP 工具缓存

AgentManager 维护用户级 MCP 工具缓存（F-068）：

```python
_mcp_tool_cache: dict[tuple[int, str, str], list[Any]]
# key = (user_id, server_name, fingerprint)
```

- 通过 `harness_agent.mcp.aload_mcp_tools` 加载
- 按 MCP spec 的 fingerprint 缓存，配置变更时自动失效
- 工具被 `wrap_tools_for_shared_use` 包装，支持跨 Agent 共享
- 每 user/server 有 asyncio.Lock 防止并发重复加载

`prepare_chat_mcp(agent_id, names)` 在聊天前确保 MCP 工具已加载，返回加载失败的 server 名列表（F-069）。

## MBTI 人格系统

Agent 支持 16 种 MBTI 人格类型，通过 `persona_mbti` 字段指定，创建时写入 `config["persona"]`（F-058）。Dashboard 提供 `/api` 下的 MBTI 路由用于人格选择和展示。MBTI 值在存储时统一转为大写。

## 专家库与子代理

### ExpertCatalog

- 从 bundled library（`infra/agents/experts/library/`）和用户市场目录（`~/.octop/expert_market/`）加载专家模板
- `default_library_root()` 返回内置库路径
- 创建 Agent 时可通过 `template_name` 从专家模板初始化

### SubagentCatalog

- 从 `infra/agents/subagents/library/` 加载子代理包
- `default_package_root()` 返回内置包路径
- 支持 divisions 分组（`divisions.json`）

### PluginManager

- 从 `~/.octop/plugins/` 加载第三方插件
- `load_installed(install_deps=True)` 在启动时安装插件依赖
- 插件工具名经过清洗以避免冲突

## 安全与审批

- **SecurityPolicy**：通过 `SecuritySettingsStore` 生成 harness 安全策略，在 `boot()` 时设置到 `HarnessAgentManager`
- **ToolGuardRules**：从 `~/.octop/security/tool_guard/dangerous_shell_commands.yaml` 加载危险命令规则
- **HITL（Human-in-the-loop）**：`resume_hitl` 支持暂停等待用户审批后继续执行
- **工具审批 guardrails**：harness-agent 在执行敏感工具前触发中断

## 相关概念

- [/concepts/00-architecture.md](/concepts/00-architecture.md)
- [/concepts/05-acp-protocol.md](/concepts/05-acp-protocol.md)
- [/concepts/04-db-di.md](/concepts/04-db-di.md)
