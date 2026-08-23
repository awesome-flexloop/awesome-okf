---
type: Example
title: "创建自定义 Agent：从 CLI 到 API"
description: "通过 CLI 和 HTTP API 创建和配置自定义 Agent，包括 MBTI 人格、系统提示词、技能包、MCP 连接器、工作区目录和生命周期管理。"
tags: [octop, agent, custom, mbti, mcp, lifecycle]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: agent
    resource: /concepts/02-agent-runtime.md
    title: Agent 运行时
  - id: db
    resource: /concepts/04-db-di.md
    title: 数据库层与 DI
---

# 创建自定义 Agent

本示例演示如何通过 CLI 和 HTTP API 创建、配置和管理自定义 Agent。

## Agent 核心概念

每个 Agent 在 Octop 中对应：
- **DB 行**：`agents` 表中的一条记录（agent_id、name、config_json 等）
- **工作区目录**：`~/.octop/agents/<agent_id>/`（Agent 文件、SOUL.md、技能等）
- **HarnessAgent 实例**：运行时由 harness-agent 管理，执行实际 AI 逻辑
- **通道绑定**：可选绑定飞书/钉钉/Discord 等 IM 通道

## 通过 CLI 创建 Agent

### 创建基本 Agent

```bash
octop agent create \
  --name "代码助手" \
  --description "帮助编写和审查代码" \
  --mbti INTJ \
  --default-model openai/gpt-4o
```

`agent create` 命令使用 Embedded 传输层（进程内启动 OctopServer），执行流程：

1. 校验 Agent name 在用户范围内唯一
2. 自动生成 ULID 作为 agent_id（或使用 `--agent-id` 指定）
3. MBTI 人格写入 `config["persona"] = "INTJ"`
4. 初始化工作区目录 `~/.octop/agents/<agent_id>/`
5. 写入 DB
6. 启动 Agent 到 harness 运行时

### 指定自定义 Agent ID

```bash
octop agent create --name "代码助手" --agent-id code-assistant
```

自定义 ID 必须匹配正则 `^[a-zA-Z0-9][a-zA-Z0-9_-]{1,62}[a-zA-Z0-9]$`（3-64 字符），且不能是保留 ID（`api`、`admin`、`agents`、`experts`）。

### 从专家模板创建

```bash
# 列出可用专家模板
octop agent experts

# 从模板创建
octop agent from-expert --template code-reviewer --name "代码审查员"
```

专家模板从 bundled library（`infra/agents/experts/library/`）和用户市场目录加载。

### Agent 生命周期管理

```bash
# 列出所有 Agent
octop agent list

# 启动 Agent
octop agent start <agent-id>

# 停止 Agent（持久化 last_state=stopped，重启后不自动启动）
octop agent stop <agent-id>

# 重新加载 Agent（配置变更后）
octop agent reload <agent-id>

# 固定默认 Agent（写入 cli_state.json）
octop agent use <agent-id>

# 删除 Agent（同时删除工作区目录）
octop agent delete <agent-id>
```

## 通过 HTTP API 创建 Agent

### 创建 Agent

```bash
curl -X POST http://127.0.0.1:8088/api/agents \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "代码助手",
    "description": "帮助编写和审查代码",
    "persona_mbti": "INTJ",
    "default_model": "openai/gpt-4o",
    "system_prompt": "你是一个资深代码审查专家...",
    "is_shared": false
  }'
```

### 更新 Agent 配置

```bash
curl -X PUT http://127.0.0.1:8088/api/agents/<agent-id> \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "system_prompt": "更新后的系统提示词...",
    "default_model": "anthropic/claude-3-5-sonnet"
  }'
```

更新后 AgentManager 调度后台热重载，无需重启服务器。

### 启动/停止

```bash
# 启动
curl -X POST http://127.0.0.1:8088/api/agents/<agent-id>/start \
  -H "Authorization: Bearer <jwt-token>"

# 停止
curl -X POST http://127.0.0.1:8088/api/agents/<agent-id>/stop \
  -H "Authorization: Bearer <jwt-token>"
```

## 配置 Agent 能力

### MBTI 人格

Octop 支持 16 种 MBTI 人格类型，影响 Agent 的沟通风格：

| 维度 | 类型 |
|------|------|
| 态度 | E（外向）/ I（内向） |
| 信息 | S（感觉）/ N（直觉） |
| 决策 | T（思考）/ F（情感） |
| 生活方式 | J（判断）/ P（感知） |

MBTI 值通过 `persona_mbti` 字段指定，存储时转为大写，写入 `config_json.persona`。

### 系统提示词

`system_prompt` 字段定义 Agent 的基础行为指令，存储在 DB 列中并同步到 harness 配置。

### 技能包

Agent 可以关联技能包（skill packages）：

```bash
# 列出 Agent 技能
octop skills list --agent <agent-id>

# 启用技能
octop skills enable --agent <agent-id> <skill-slug>

# 禁用技能
octop skills disable --agent <agent-id> <skill-slug>
```

技能包 ID 列表存储在 `skill_package_ids` 列（JSON 数组），创建时通过 `--skill-package-ids` 指定。

### MCP 连接器

Agent 通过 ConnectorService 连接 MCP 服务器（如 GitHub、数据库、文件系统等）。连接器配置是 per-user 的，共享 Agent（user_id IS NULL）在聊天时使用当前用户的连接器。

API 管理连接器：

```bash
# 列出连接器
curl http://127.0.0.1:8088/api/connectors \
  -H "Authorization: Bearer <jwt-token>"

# 创建连接器
curl -X POST http://127.0.0.1:8088/api/connectors \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "mcp",
    "display_name": "GitHub",
    "config": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"] }
  }'
```

MCP 工具在聊天时按需加载，通过用户级缓存（key 为 `(user_id, server_name, fingerprint)`）在多个 Agent 间共享。

### ACP Runner 委托

可以为 Agent 启用 `acp_runner` 工具，使其能够委托编码任务给外部 CLI：

```bash
curl -X PUT http://127.0.0.1:8088/api/agents/<agent-id>/acp/tool \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"tool_enabled": true}'
```

全局 runner 配置（per-user）通过 `/api/acp` 管理。详见 [/concepts/05-acp-protocol.md](/concepts/05-acp-protocol.md)。

## 工作区目录

每个 Agent 有独立的工作区目录：

```
~/.octop/agents/<agent_id>/
├── .octop/                    # 系统文件（内部，不可用户配置）
│   ├── sessions/              # 会话 SQLite
│   ├── skills/                # 技能系统树
│   └── auth/                  # 认证令牌
├── SOUL.md                    # Agent 灵魂/人格文件
├── inbound/                   # 聊天附件上传目录
└── skills/                    # Agent 级技能
```

- `system_files_path` 是内部布局控制，强制为 `.octop/`，用户不可修改
- 工作区内容文件的读写必须通过 `HarnessAgent.workspace`（BackendWorkspace），不直接使用 `Path.read_text/write_text`
- 支持 Docker 沙箱和远程存储后端（S3/COS），通过 `config.backend` 配置

## 共享 Agent

设置 `is_shared: true` 使 Agent 对所有用户可见：

```bash
curl -X PUT http://127.0.0.1:8088/api/agents/<agent-id> \
  -H "Authorization: Bearer <jwt-token>" \
  -d '{"is_shared": true}'
```

共享 Agent 的 `user_id` 为 NULL，连接器在聊天时使用当前请求用户的凭证。

## 安全与审批

- **JWT 认证**：所有 API 需要 Bearer token，token TTL 默认 86400 秒（可配置）
- **argon2 密码哈希**：用户密码使用 argon2-cffi 哈希
- **登录锁定**：连续失败 5 次（可配置）锁定 900 秒
- **工具审批 guardrails**：危险 shell 命令规则在 `~/.octop/security/tool_guard/dangerous_shell_commands.yaml`
- **SecurityPolicy**：通过 SecuritySettingsStore 生成 harness 安全策略
- **HITL**：敏感工具执行前触发中断，等待用户审批后通过 `resume_hitl` 继续

## 相关概念

- [/concepts/02-agent-runtime.md](/concepts/02-agent-runtime.md)
- [/concepts/05-acp-protocol.md](/concepts/05-acp-protocol.md)
- [/concepts/03-gateway-channels.md](/concepts/03-gateway-channels.md)
