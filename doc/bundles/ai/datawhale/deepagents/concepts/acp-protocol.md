---
title: ACP 协议集成
type: concept
bundle: /datawhale/deepagents
related:
  - /datawhale/deepagents/concepts/core-sdk
  - /datawhale/deepagents/concepts/code-module
  - /datawhale/deepagents/concepts/monorepo-architecture
sources:
  - https://github.com/datawhalechina/deepagents/blob/main/libs/acp/README.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/acp/deepagents_acp/server.py
  - https://github.com/datawhalechina/deepagents/blob/main/libs/acp/pyproject.toml
  - https://agentclientprotocol.com/overview/introduction
---

# ACP 协议集成

ACP（Agent Client Protocol）集成包（`deepagents-acp`，位于 `libs/acp/`）允许在支持 ACP 协议的文本编辑器（如 [Zed](https://zed.dev/)）中运行 Python Deep Agent。它将编译后的 LangGraph 图适配为 ACP 服务器，通过 stdio 与编辑器通信。

> 包状态：Alpha（版本 0.0.10），要求 Python 3.14。

## 核心组件

### AgentServerACP

核心类 `AgentServerACP` 位于 `libs/acp/deepagents_acp/server.py`，包装一个编译后的 Deep Agent 图，处理 ACP 协议事件：

- 消息收发
- 工具进度和差异展示
- Todo 列表同步
- 支持的人在回路（HITL）流程

### 会话持久化

当 Agent 使用持久化 LangGraph checkpointer 时，`AgentServerACP` 可通告并实现 ACP 的 `session/load` 能力：

```python
server = AgentServerACP(agent, load_sessions=True)
```

加载时，适配器恢复 LangGraph 线程，验证原始工作目录，并通过 `session/update` 向客户端回放对话。checkpointer 必须在 Agent 进程重启后保持可用；内存 checkpointer 仅适用于测试。

### 动态模型切换

ACP 适配器支持通过 Session Config Options 在会话中动态切换 LLM 模型，无需丢失对话历史。通过 Agent 工厂模式实现：

```python
def build_agent(context: AgentSessionContext):
    model = context.model
    return create_deep_agent(model=model, checkpointer=checkpointer)

server = AgentServerACP(agent=build_agent, models=models)
```

`models` 参数声明可用模型列表，每项包含 `value`（`provider:model-name` 格式）和 `name`（显示名称）。

## 两种使用模式

### 模式一：自定义 Deep Agent

适用于需要自定义工具或 Agent 架构的场景：

```python
from deepagents_acp.server import AgentServerACP

agent = create_deep_agent(
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
    checkpointer=MemorySaver(),
)
server = AgentServerACP(agent)
await run_agent(server)
```

### 模式二：dcode --acp

适用于不需要自定义 Agent 的场景。`deepagents-code` 可直接将完整的预构建编码 Agent（文件系统工具、Shell、MCP 支持、子 Agent）作为 ACP 服务器暴露：

```bash
uv tool install -U deepagents-code --with deepagents-acp
dcode --acp
```

在 Zed 中配置：

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

## Zed 编辑器配置

对于自定义 Agent，需要在 Zed 的 `settings.json` 中配置 Agent 服务器，指向启动脚本：

```json
{
  "agent_servers": {
    "DeepAgents": {
      "type": "custom",
      "command": "/absolute/path/to/run_demo_agent.sh"
    }
  }
}
```

## 依赖

```toml
dependencies = [
    "deepagents",
    "agent-client-protocol>=0.10.1",
    "python-dotenv>=1.2.2",
]
```

## Toad 启动器

ACP 也支持通过 [Toad](https://github.com/agent-client-protocol/toad) 启动器运行：

```bash
uv tool install -U batrachian-toad --python 3.14
toad acp "python path/to/your_server.py" .
```

## 设计意义

ACP 集成代表了 Deep Agents 从终端向**编辑器原生体验**扩展的方向。它定义了一个与传输无关的 Agent 接口标准——Agent 不再绑定到特定 UI，而是作为协议端点被任何兼容客户端消费。这与 [Talon运行时宿主](/ai/datawhale/deepagents/concepts/talon-runtime) 的消息平台通道形成互补：ACP 面向开发者工具场景，Talon 面向消息平台场景。

## 与其他概念的关系

- [核心SDK与三层架构](/ai/datawhale/deepagents/concepts/core-sdk) 提供被包装的 Agent 图。
- [Code终端编码Agent](/ai/datawhale/deepagents/concepts/code-module) 可通过 `--acp` 标志直接暴露为 ACP 服务器。
- [Monorepo 架构](/ai/datawhale/deepagents/concepts/monorepo-architecture) 描述了 acp 包在仓库中的位置。
