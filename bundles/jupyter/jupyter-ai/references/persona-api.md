---
type: Reference
title: Persona API 参考
description: BasePersona 抽象类、PersonaDefaults 数据模型、process_message 方法签名及 Persona 开发 API
tags: [persona, api, base-persona, entry-points, extension]
sources:
  - id: personas-group
    resource: external/libs/jupyter/jupyter-ai/docs/source/developers/entry_points_api/personas_group.md
    title: personas_group.md
  - id: providing-entry-points
    resource: external/libs/jupyter/jupyter-ai/docs/source/developers/entry_points_api/providing_entry_points.md
    title: providing_entry_points.md
  - id: contributors
    resource: external/libs/jupyter/jupyter-ai/docs/source/contributors/index.md
    title: contributors/index.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# Persona API 参考

本页提供 AI Persona 开发的 API 参考。Persona 是 Agent 的集成抽象层，所有 AI 交互通过 Persona 进行。

## BasePersona 抽象类

所有自定义 Persona 必须继承 `jupyter_ai_persona_manager:BasePersona`，并实现两个抽象成员。

### 必须实现的抽象方法

#### `process_message()`

```python
@abstractmethod
async def process_message(self, message: Message) -> None:
```

Persona 的**主入口方法**，处理每条新消息。

| 参数 | 类型 | 说明 |
|---|---|---|
| `message` | `Message` | 用户发送的新消息对象 |

`Message` 对象来自 `jupyterlab_chat.models:Message`，主要属性：
- `message.body: str` — 消息内容文本

#### `defaults` 属性

```python
@property
@abstractmethod
def defaults(self) -> PersonaDefaults:
```

返回 Persona 的默认配置。

### PersonaDefaults 数据模型

```python
class PersonaDefaults(BaseModel):
    name: str           # Persona 显示名称，如 "Jupyternaut"
    description: str    # 描述文本（当前保留未使用）
    avatar_path: str    # 头像 URL 路径，相对于 Jupyter Server 域名
    system_prompt: str  # 系统提示词（当前保留未使用）
```

### 内置响应方法

BasePersona 提供两个内置方法用于发送回复：

| 方法 | 签名 | 说明 |
|---|---|---|
| `send_message` | `send_message(body: str)` | 立即发送完整消息 |
| `stream_message` | `stream_message(stream: AsyncIterator[str])` | 流式发送消息，接受 async iterator 逐块输出 |

`stream_message()` 可直接传入 LangChain 模型的 `astream()` 输出。

## Entry Point 注册

自定义 Persona 通过 Python entry points 注册到 `jupyter_ai.personas` 组。

### pyproject.toml 配置

```toml
[project.entry-points."jupyter_ai.personas"]
my_persona = "my_package.persona:MyPersona"
```

格式：`<唯一名称> = "<模块路径>:<类名>"`

### 注册步骤

1. 在包的 `pyproject.toml` 中添加 entry point
2. 将包安装到 Jupyter AI 所在的 Python 环境
3. 重启 JupyterLab（entry points 仅在服务启动时读取）

## 内置 Persona 参考

| Persona | 包 | 类型 | 说明 |
|---|---|---|---|
| Jupyternaut | `jupyter_ai_jupyternaut` | 直接模型调用 | 默认 Persona，通过 LiteLLM 支持 1000+ 模型 |
| Claude Code | `jupyter_ai_claude_code` | ACP 包装 | 通过 ACP 协议连接 Claude Code CLI |

## 消息流

```
用户发送消息
    │
    ▼
Chat Panel（收集消息/附件/权限决策）
    │
    ▼
Router（路由到选中的 Persona）
    │
    ├── ACP Persona ──→ ACP Client ──→ 外部 Agent（Claude/Codex/...）
    │                      │
    │                      ▼
    │                  MCP 工具调用（需权限审批）
    │
    └── 直接模型 Persona ──→ LiteLLM/Provider ──→ LLM API
                           │
                           ▼
                       MCP 工具调用（需权限审批）
    │
    ▼
流式回复 ──→ Chat Panel（显示）
```

## 最小实现示例

```python
from jupyter_ai_persona_manager import BasePersona
from jupyter_ai_persona_manager.api import PersonaDefaults
from jupyterlab_chat.models import Message, NewMessage

class DebugPersona(BasePersona):
    """一个简单的调试 Persona，总是回复 Hello!"""

    @property
    def defaults(self):
        return PersonaDefaults(
            name="DebugPersona",
            avatar_path="/api/ai/static/jupyternaut.svg",
            description="A mock persona for debugging.",
            system_prompt="You are a helpful assistant."
        )

    async def process_message(self, message: Message):
        self.send_message(NewMessage(body="Hello!", sender=self.id))
```

## 相关概念

- [AI Persona 系统](../concepts/05-ai-personas.md)
- [ACP 与 MCP 双协议](../concepts/04-protocols-acp-mcp.md)
- [Entry Points API](../concepts/09-entry-points-api.md)
- [自定义 Persona 示例](../examples/custom-persona.md)
