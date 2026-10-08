---
type: Concept
title: "ACP 双向集成：入站服务器与出站 Runner"
description: "ACP（Agent Client Protocol）双向集成：Octop 作为入站 ACP stdio 服务器被外部 IDE 驱动，通过 acp_runner 工具出站委托 OpenCode/CodeBuddy/Claude Code/Codex 执行编码任务。"
tags: [octop, acp, agent-client-protocol, runner, opencode, codebuddy, claude-code, codex]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: acp
    resource: /references/cli-api.md
    title: CLI 与 HTTP API 信源（ACP 部分）
  - id: docs
    resource: /spec/facts.md
    title: F-121~F-127 ACP 事实
---

# ACP 双向集成

Octop 集成了 [ACP（Agent Client Protocol）](https://agentclientprotocol.com/)，支持两个方向的互操作。两者均使用 **stdio JSON-RPC** 传输，Octop 不暴露 HTTP ACP 端点（F-127）。

## 双向架构

| 方向 | ACP 服务器 | ACP 客户端 | 典型用途 |
|------|-----------|-----------|---------|
| **入站（Inbound）** | Octop（`octop acp`） | Zed、OpenCode 等外部 IDE | 外部 IDE 驱动 Octop Agent 执行编码 |
| **出站（Outbound）** | OpenCode、CodeBuddy、Claude Code、Codex | Octop（`acp_runner` 工具） | Octop Agent 将编码任务委托给外部 CLI |

来源：F-121。

## 入站：Octop 作为 ACP 服务器

### CLI 命令

```bash
octop acp --agent main
octop acp --agent main --debug
```

选项（F-125）：
- `--agent ID`：要暴露的 Agent（默认 CLI `default_agent` 或第一个 Agent）
- `--debug`：将日志输出到 stderr

### 工作原理

`octop acp` 启动一个**独立的** `OctopServer`（读取 `~/.octop`），引导指定 Agent，然后在 stdin/stdout 上讲 ACP 协议（F-125）。它**不需要** `octop run` 正在运行——这是一个独立进程。

会话映射到 LangGraph 的 `thread_id`；Agent 工作区保持在 `~/.octop/agents/<agent_id>/`（F-125）。

### Zed 集成示例

`~/.config/zed/settings.json`：

```json
{
  "agent_servers": {
    "Octop": {
      "command": "octop",
      "args": ["acp", "--agent", "main"],
      "env": {}
    }
  }
}
```

从开发检出目录运行：

```json
{
  "agent_servers": {
    "Octop": {
      "command": "uv",
      "args": ["run", "octop", "acp", "--agent", "main"],
      "env": {}
    }
  }
}
```

在 Zed 中创建 Agent 线程即可像使用内置 Agent 一样与 Octop Agent 对话。

### 默认 Agent 固定

```bash
octop user login --username you
octop agent use main   # 写入 ~/.octop/cli_state.json
# 或直接：
octop --agent main acp
```

## 出站：acp_runner 工具

Octop Agent 可以通过 `acp_runner` 工具将编码任务委托给外部 ACP runner（如 OpenCode、CodeBuddy）。

### 配置作用域

| 设置 | 作用域 | 存储位置 |
|------|--------|---------|
| Runner 卡片（command、args、enabled 等） | **Per user**（所有 Agent 共享） | `settings` 表 key `acp_runners:user:{id}` |
| **Enable acp_runner tool** 开关 | **Per agent** | Agent `config_json.acp.tool_enabled` |

来源：F-123。

Legacy per-agent `config_json.acp.runners` 在首次加载时自动迁移到 user-global store。

### 四个内置 Runner

| ID | Command | Args |
|----|---------|------|
| `opencode` | `opencode` | `["acp"]` |
| `codebuddy` | `codebuddy` | `["--acp"]` |
| `claude_code` | `npx` | `["-y", "@zed-industries/claude-agent-acp"]` |
| `codex` | `npx` | `["-y", "@zed-industries/codex-acp"]` |

来源：F-122。

内置 runner 不可删除；自定义 runner 可通过 Dashboard 的 **Add runner** 按钮添加。

### Runner 对象结构

```json
{
  "enabled": true,
  "command": "opencode",
  "args": ["acp"],
  "env": {},
  "trusted": true,
  "tool_parse_mode": "update_detail",
  "stdio_buffer_limit_bytes": 52428800
}
```

- `command`：可执行文件路径或 PATH 中的命令名
- `args`：命令参数
- `env`：额外环境变量
- `trusted`：是否信任该 runner
- `tool_parse_mode`：工具调用解析模式
- `stdio_buffer_limit_bytes`：stdio 缓冲区上限（50MB）

### acp_runner 工具 Action

```
action=list     → 列出已启用的 runner 和会话状态
action=start    → 新会话：runner + message（+ 可选 cwd）
action=message  → 继续会话
action=respond  → 响应 [permission_required]，传入精确选项 ID
action=status   → 会话状态（开放/等待权限）
action=close    → 结束会话
```

来源：F-124。

### 典型使用流程

1. 在 Dashboard `/acp` 页面配置并启用至少一个 runner
2. 在顶部栏切换 Agent，开启 **Enable acp_runner tool**
3. 在聊天中要求 Agent 使用 `acp_runner`，或让其在适当时自动委托

示例用户消息：

```text
请用 acp_runner：action=start, runner=opencode, message=在 workspace 里找 README 并总结。
```

外部 Agent 的权限提示会出现在聊天中；用户可以选择选项或指示 Agent 调用 `action=respond` 传入选项 ID。

### 热重载

- 修改全局 runners 后，Octop 自动重新加载所有 Agent
- 仅修改 `tool_enabled` 时只重新加载该 Agent

## HTTP API

### 全局 Runner（当前用户）

| Method | Path | 说明 |
|--------|------|------|
| `GET` | `/api/acp` | 获取所有 runner |
| `PUT` | `/api/acp` | 批量更新 runners |
| `GET` | `/api/acp/{runner_name}` | 获取单个 runner |
| `PUT` | `/api/acp/{runner_name}` | 更新单个 runner |
| `DELETE` | `/api/acp/{runner_name}` | 删除自定义 runner（内置不可删） |

### Per-Agent 工具开关

| Method | Path | 说明 |
|--------|------|------|
| `GET` | `/api/agents/{agent_id}/acp` | 获取全局 runners + agent tool_enabled |
| `PUT` | `/api/agents/{agent_id}/acp` | 更新 tool_enabled（runners 可选） |
| `PUT` | `/api/agents/{agent_id}/acp/tool` | 仅更新 tool_enabled |

来源：F-126。

## 前置条件

- **harness-agent `[acp]` extra**：拉取 `agent-client-protocol` 包（已包含在 Octop wheel 对 harness-agent 的依赖中）
- **出站**：在运行 `octop run` 的机器上安装外部 CLI（`opencode`、`codebuddy` 等），确保在 PATH 中（或在 runner 配置中设置绝对路径）
- **入站**：Agent 必须能成功启动（已配置 Provider + 模型）

## 故障排查

| 症状 | 可能原因 |
|------|---------|
| 某些 Agent 看不到 runner | 升级到 user-global runners；打开 `/acp` 页面或 `GET /api/acp` 触发迁移 |
| `acp_runner` 列出 runner 但启动报 "Unknown runner" | 添加自定义 runner 后重启 `octop run`（ACP 服务缓存是进程级的） |
| 外部 runner 无文本返回 | 检查 CLI 认证/配额（如 `codebuddy auth status`） |
| `octop acp` 立即失败 | Agent 未运行或 `--agent` 无效；先在 Dashboard 创建/启动 Agent |
| Command not found | 如果服务器进程的 PATH 与 shell 不同，在 runner `command` 中使用绝对路径 |

## 安全考量

- 出站 runner 在 Octop 服务器主机上执行外部进程，应仅启用受信任的 runner
- `trusted` 字段控制 runner 的权限级别
- 入站 ACP 服务器不做额外认证——任何能访问该进程 stdio 的用户都可以驱动 Agent
- `stdio_buffer_limit_bytes` 防止恶意/异常 runner 耗尽内存

## 相关概念

- [/concepts/02-agent-runtime.md](02-agent-runtime.md)
- [/concepts/06-cli-commands.md](06-cli-commands.md)
- [/examples/acp-integration.md](../examples/acp-integration.md)
