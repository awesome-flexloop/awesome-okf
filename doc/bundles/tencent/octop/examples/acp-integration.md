---
type: Example
title: "ACP 集成：Zed 入站与 Runner 出站"
description: "配置 Octop 作为 ACP 服务器接入 Zed 编辑器，以及配置出站 acp_runner 工具让 Octop Agent 委托 OpenCode/CodeBuddy/Claude Code/Codex 执行编码任务。"
tags: [octop, acp, zed, opencode, codebuddy, claude-code, codex, ide]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: acp
    resource: /concepts/05-acp-protocol.md
    title: ACP 双向集成
  - id: cli
    resource: /concepts/06-cli-commands.md
    title: CLI 命令体系
---

# ACP 集成：Zed 入站与 Runner 出站

本示例演示 ACP（Agent Client Protocol）的两个集成方向：将 Octop 作为 ACP 服务器接入 Zed，以及配置出站 runner 让 Octop Agent 委托外部编码工具。

## 前提条件

1. Octop 已安装并初始化（`pip install octop && octop init`）
2. 至少有一个已配置 Provider 并成功启动的 Agent
3. 出站集成需要在运行 `octop run` 的机器上安装外部 CLI

## 入站：Zed 驱动 Octop Agent

### 步骤 1：确认 Agent 可正常工作

```bash
# 列出 Agent
octop agent list

# 如果没有 Agent，创建一个
octop agent create --name "coding-agent" --default-model openai/gpt-4o

# 固定为默认 Agent（可选）
octop agent use coding-agent
```

### 步骤 2：验证 ACP 服务器

```bash
# 手动测试 ACP stdio 服务器
octop acp --agent coding-agent
```

此命令启动独立 OctopServer（不需要 `octop run` 运行），在 stdin/stdout 上使用 JSON-RPC 通信。按 `Ctrl+C` 退出。

调试模式：

```bash
octop acp --agent coding-agent --debug
```

`--debug` 将日志输出到 stderr，不干扰 stdio JSON-RPC。

### 步骤 3：配置 Zed

编辑 Zed 设置文件：

- **Linux/macOS**：`~/.config/zed/settings.json`
- **Windows**：`%APPDATA%\Zed\settings.json`

```json
{
  "agent_servers": {
    "Octop": {
      "command": "octop",
      "args": ["acp", "--agent", "coding-agent"],
      "env": {}
    }
  }
}
```

如果从开发检出目录运行（使用 uv）：

```json
{
  "agent_servers": {
    "Octop": {
      "command": "uv",
      "args": ["run", "octop", "acp", "--agent", "coding-agent"],
      "env": {}
    }
  }
}
```

如果需要自定义 `OCTOP_HOME`：

```json
{
  "agent_servers": {
    "Octop": {
      "command": "octop",
      "args": ["acp", "--agent", "coding-agent"],
      "env": {
        "OCTOP_HOME": "/data/octop"
      }
    }
  }
}
```

### 步骤 4：在 Zed 中使用

1. 打开 Zed
2. 创建 Agent 线程（Agent Panel → New Thread）
3. 选择 "Octop" 作为 Agent 服务器
4. 像使用内置 Agent 一样对话

会话映射到 Octop 的 `thread_id`，Agent 工作区保持在 `~/.octop/agents/<agent_id>/`。Zed 中打开的项目目录作为 cwd 传递给 Agent。

### 入站故障排查

| 问题 | 排查 |
|------|------|
| `octop acp` 立即退出 | 检查 Agent 是否存在且已配置 Provider/模型；`octop agent list` |
| Zed 显示 "Agent server not found" | 确认 `octop` 在 Zed 的 PATH 中；使用绝对路径或 uv |
| Agent 无响应 | `octop acp --agent <id> --debug` 查看 stderr 日志 |
| 权限错误 | 确认 `~/.octop/` 目录权限正确 |

## 出站：配置 acp_runner 委托

### 步骤 1：安装外部 Runner CLI

在运行 `octop run` 的机器上安装至少一个 runner：

```bash
# OpenCode
npm install -g opencode
# 或参考 https://opencode.ai 安装

# CodeBuddy（腾讯内部）
npm install -g @tencent/codebuddy
codebuddy auth status

# Claude Code（通过 npx，无需全局安装）
# npx -y @zed-industries/claude-agent-acp

# Codex（通过 npx，无需全局安装）
# npx -y @zed-industries/codex-acp
```

验证 CLI 在 PATH 中：

```bash
which opencode
which codebuddy
# npx 类 runner 不需要 which
```

如果服务器进程的 PATH 与 shell 不同（如 systemd 服务），在 runner 配置中使用绝对路径。

### 步骤 2：启动 Octop 服务

```bash
octop run
```

### 步骤 3：在 Dashboard 中配置 Runner

1. 打开 `http://127.0.0.1:8088`
2. 进入侧边栏 **ACP** 页面（`/acp`）
3. 确认内置 runner 卡片：
   - `opencode`：command=`opencode`, args=`["acp"]`
   - `codebuddy`：command=`codebuddy`, args=`["--acp"]`
   - `claude_code`：command=`npx`, args=`["-y", "@zed-industries/claude-agent-acp"]`
   - `codex`：command=`npx`, args=`["-y", "@zed-industries/codex-acp"]`
4. 启用需要的 runner（toggle on）
5. 可选：添加自定义 runner（**Add runner**）

Runner 配置是 **per-user** 的（存储在 `settings` 表 key `acp_runners:user:{id}`），该用户的所有 Agent 共享。

### 步骤 4：为 Agent 启用 acp_runner 工具

1. 在 Dashboard 顶部栏切换到目标 Agent
2. 进入 Agent 设置
3. 开启 **Enable acp_runner tool**

或通过 API：

```bash
curl -X PUT http://127.0.0.1:8088/api/agents/<agent-id>/acp/tool \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"tool_enabled": true}'
```

此设置是 **per-agent** 的（存储在 `config_json.acp.tool_enabled`）。

### 步骤 5：在聊天中使用

在 Agent 聊天中直接请求：

```text
请用 acp_runner：action=start, runner=opencode, message=在当前 workspace 中找 README.md 并总结其内容。
```

或自然语言让 Agent 自动决定委托：

```text
帮我用 OpenCode 在项目里找所有 TODO 注释并生成报告。
```

### acp_runner 工具 Action 参考

| Action | 用途 | 参数 |
|--------|------|------|
| `list` | 列出已启用 runner 和会话状态 | — |
| `start` | 创建新会话 | `runner`, `message`, `cwd`（可选） |
| `message` | 向已有会话发送消息 | `session_id`, `message` |
| `respond` | 响应权限请求 | `session_id`, `option_id` |
| `status` | 查询会话状态 | `session_id` |
| `close` | 结束会话 | `session_id` |

### 权限处理

外部 Agent（如 Claude Code）在执行敏感操作时会发出 `[permission_required]` 事件：

1. 权限提示出现在 Octop 聊天中
2. 用户选择允许/拒绝选项
3. Octop 自动调用 `action=respond` 传入选项 ID
4. 也可以明确指示 Agent："选择允许"

### 自定义 Runner 示例

添加一个使用绝对路径的自定义 runner：

```json
{
  "id": "my-opencode",
  "enabled": true,
  "command": "/usr/local/bin/opencode",
  "args": ["acp"],
  "env": {
    "ANTHROPIC_API_KEY": "sk-..."
  },
  "trusted": true,
  "tool_parse_mode": "update_detail",
  "stdio_buffer_limit_bytes": 52428800
}
```

通过 API 添加：

```bash
curl -X PUT http://127.0.0.1:8088/api/acp/my-opencode \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "command": "/usr/local/bin/opencode",
    "args": ["acp"],
    "env": {},
    "trusted": true,
    "tool_parse_mode": "update_detail",
    "stdio_buffer_limit_bytes": 52428800
  }'
```

添加自定义 runner 后需要**重启 `octop run`**（ACP 服务缓存是进程级的）。

### 出站故障排查

| 问题 | 排查 |
|------|------|
| Runner 列出但启动报 "Unknown runner" | 重启 `octop run`（自定义 runner 需要重启生效） |
| 外部 runner 无文本返回 | 检查 CLI 认证/配额（如 `codebuddy auth status`） |
| `command not found` | 在 runner 配置中使用绝对路径；systemd 服务的 PATH 可能不同 |
| 某些 Agent 看不到 runner | 打开 `/acp` 页面触发一次 legacy 迁移；或 `GET /api/acp` |
| stdio buffer 溢出 | 增大 `stdio_buffer_limit_bytes`（默认 50MB） |
| `acp_runner` 工具未出现 | 确认 Agent 已开启 tool_enabled；全局 runner 变更后 Agent 会自动重载 |

## 双向集成架构

```
┌──────────────┐  stdio JSON-RPC   ┌──────────────┐
│     Zed      │ ◄──────────────► │  octop acp   │  (入站)
│  (IDE/ACP    │                   │  (独立进程)   │
│   client)    │                   │              │
└──────────────┘                   └──────┬───────┘
                                          │ HarnessAgent
                                          ▼
┌──────────────┐  acp_runner tool  ┌──────────────┐
│  Octop Agent │ ────────────────► │  OpenCode    │  (出站)
│ (octop run   │  stdio JSON-RPC   │  CodeBuddy   │
│  进程内)      │ ◄──────────────── │  Claude Code │
│              │                   │  Codex       │
└──────────────┘                   └──────────────┘
```

入站和出站可以同时使用：Zed 通过入站 ACP 驱动 Octop Agent，而该 Agent 又可以通过出站 `acp_runner` 委托给其他编码工具。

## 相关概念

- [/concepts/05-acp-protocol.md](/concepts/05-acp-protocol.md)
- [/concepts/06-cli-commands.md](/concepts/06-cli-commands.md)
- [/concepts/02-agent-runtime.md](/concepts/02-agent-runtime.md)
