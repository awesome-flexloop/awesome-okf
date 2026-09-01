---
type: concept
scope: deepagents
name: acp-protocol
version: "0.7.8"
source: https://github.com/langchain-ai/deepagents
description: Deep Agents ACP 协议集成概念——Agent Client Protocol 如何桥接 Deep Agent 与代码编辑器
---

# ACP 协议

## 什么是 ACP

[Agent Client Protocol (ACP)](https://agentclientprotocol.com/overview/introduction) 是一个开放协议，定义了 AI 代理与客户端（如代码编辑器）之间的通信标准。它类似于 LSP（Language Server Protocol）之于语言服务器——标准化代理如何与编辑器交互。

Deep Agents 通过 `deepagents-acp` 包实现 ACP 服务端，使任何 Deep Agent 可以在支持 ACP 的编辑器（如 [Zed](https://zed.dev/)）中运行。

## 架构定位

```
┌──────────────┐     ACP/stdio      ┌──────────────────┐
│  Zed Editor  │ ◄────────────────► │ AgentServerACP   │
│  (ACP Client)│                    │  (ACP Server)    │
└──────────────┘                    └────────┬─────────┘
                                             │ invoke()
                                             ▼
                                    ┌──────────────────┐
                                    │ CompiledStateGraph│
                                    │ (Deep Agent)      │
                                    └──────────────────┘
```

`AgentServerACP` 是协议适配器，将 ACP 消息翻译为 LangGraph 图调用，将图的流式输出翻译回 ACP 消息。

## AgentServerACP

`AgentServerACP` 继承自 `acp.Agent`，是连接 Deep Agents 与 ACP 的桥梁。

### 两种构造模式

**静态代理模式**：直接传入编译好的 `CompiledStateGraph`：

```python
agent = create_deep_agent(...)
server = AgentServerACP(agent)
```

此模式下 `modes` 和 `models` 参数必须为 `None`。

**工厂模式**：传入接收 `AgentSessionContext` 的工厂函数：

```python
def build_agent(context: AgentSessionContext):
    return create_deep_agent(model=context.model, ...)

server = AgentServerACP(build_agent, models=models, modes=modes)
```

工厂模式支持运行时模型切换和模式切换。

### 会话管理

`AgentServerACP` 为每个 ACP 会话维护独立状态：

| 状态 | 用途 |
|---|---|
| `_agent_session_id` | 当前代理会话 ID |
| `_session_models` | 每会话当前选中的模型 |
| `_session_modes` | 每会话当前模式 |
| `_session_cwds` | 每会话工作目录 |
| `_session_plans` | 每会话计划列表（AgentPlanUpdate） |
| `_session_mcp_servers` | 每会话 MCP 服务器配置 |
| `_allowed_command_types` | 每会话允许的 shell 命令类型 |

### 模型切换

ACP 适配器通过 Session Config Options 支持动态模型切换。模型列表通过 `models` 参数传入：

```python
models = [
    {"value": "anthropic:claude-opus-4-6", "name": "Claude Opus 4"},
    {"value": "anthropic:claude-sonnet-4", "name": "Claude Sonnet 4"},
    {"value": "openai:gpt-4-turbo", "name": "GPT-4 Turbo"},
]
```

用户可在编辑器中切换模型而不丢失对话历史。切换时工厂函数以新模型重新创建代理实例。

### 会话持久化

`load_sessions=True` 启用 ACP 的 `session/load` 能力：

- 要求代理使用跨进程重启持久的 LangGraph checkpointer
- 加载时恢复 LangGraph 线程状态
- 验证原始工作目录是否匹配
- 通过 `session/update` 向客户端回放对话历史
- 内存 checkpointer（`MemorySaver`）适合测试但不提供重启持久化

### 流式输出

ACP 服务器将 LangGraph 的流式事件转换为 ACP 消息类型：

- `AgentMessageChunk`：代理文本输出块
- `ToolCallStart` / `ToolCallUpdate`：工具调用生命周期
- `AgentPlanUpdate`：计划更新
- `update_agent_message`：更新代理消息
- `start_edit_tool_call` / `tool_diff_content`：文件编辑差异展示

支持的内容块类型包括：文本（`text_block`）、图片（`image_block`）、音频（`audio_block`）、嵌入式资源（`EmbeddedResourceContentBlock`）、资源内容块。

### MCP 服务器集成

ACP 服务器支持在会话级别配置 MCP 服务器，类型别名为：

```python
McpServer = HttpMcpServer | SseMcpServer | McpServerStdio
```

支持三种传输方式：HTTP、SSE、stdio。

### 安全机制

ACP 适配器包含多层安全控制：

1. **危险模式检测**：`contains_dangerous_patterns()` 检测 shell 命令中的危险模式
2. **命令允许列表**：`_allowed_command_types` 跟踪每会话允许的命令类型，可配置允许/拒绝特定命令
3. **权限选项**：通过 ACP 的 `PermissionOption` 实现用户审批

## dcode --acp

`deepagents-code` 包的终端编码代理 `dcode` 可通过 `--acp` 标志直接作为 ACP 服务器运行，无需编写自定义代理代码：

```bash
uv tool install -U deepagents-code --with deepagents-acp
dcode --acp --model anthropic:claude-sonnet-4-5
```

这提供了完整的编码代理体验：文件系统工具、shell、MCP 支持、子代理，比使用基础 `create_deep_agent()` 构建的代理功能更丰富。

Zed 配置：

```json
{
  "agent_servers": {
    "Deep Agents Code": {
      "type": "custom",
      "command": "dcode",
      "args": ["--acp", "--model", "anthropic:claude-sonnet-4-5"]
    }
  }
}
```

## ACP 与其他接口的对比

| 接口 | 用途 | 传输 |
|---|---|---|
| ACP (`deepagents-acp`) | 编辑器内代理交互 | stdio |
| CLI (`deepagents-cli`) | 部署管理（init/deploy/agents/mcp-servers） | HTTP API |
| GitHub Action (`action.yml`) | CI 中非交互式运行 `dcode` | 进程 |
| LangGraph SDK | 异步远程子代理 | HTTP/ASGI |

## 相关概念

- 总览 — Deep Agents 整体架构
- 规划与子代理 — ACP 工厂模式与子代理
- ACP 协议参考 — AgentServerACP API 详情
