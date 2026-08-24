---
type: Concept
title: AI Persona 系统
description: AI Persona 的概念、BasePersona 抽象类、内置 Persona、@提及规则和自定义 Persona 开发
tags: [persona, agent, base-persona, acp, jupyternaut, extension, entry-points]
sources:
  - id: user-guide
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/index.md
    title: users/index.md
  - id: personas-group
    resource: external/libs/jupyter/jupyter-ai/docs/source/developers/entry_points_api/personas_group.md
    title: personas_group.md
  - id: contributors
    resource: external/libs/jupyter/jupyter-ai/docs/source/contributors/index.md
    title: contributors/index.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# AI Persona 系统

AI Persona 是 Jupyter AI 中 Agent 的集成抽象层。理解 Persona 系统是理解 Jupyter AI 如何同时支持多种 AI Agent 的关键。

## Persona 的概念

Persona 是聊天中的"AI 角色"，类似于其他聊天应用中的"Bot"。**Persona 不是模型本身，而是 Agent 或模型的集成点**。

这一区分很重要：
- Persona 负责**接收消息并产生回复**
- Persona 可以直接调用模型（如 Jupyternaut 通过 LiteLLM）
- Persona 也可以将消息转发给外部 Agent（如 Claude Code 通过 ACP）
- 同一个 Agent 可以通过不同的 Persona 呈现不同的配置（不同模型、不同系统提示）

## 组件角色

Jupyter AI 会话中的各组件角色：[^user-guide]

| 组件 | 角色 |
|---|---|
| 聊天面板 | 收集消息、附件和权限决策，显示流式回复 |
| AI Persona | 接收消息并产生回复，是 Agent 的集成点 |
| ACP 集成 | 通过 Agent Client Protocol 连接外部 Agent |
| Jupyter MCP 服务器 | 暴露 Notebook 和 JupyterLab 操作作为 MCP 工具 |
| 自定义 MCP 服务器 | 通过 mcp_settings.json 添加额外工具源 |

## 内置 Persona

### Jupyternaut（默认）

Jupyternaut 是 Jupyter AI 提供的默认 Persona：

- **类型**：直接模型调用 Persona（非 ACP）
- **模型支持**：通过 LiteLLM 支持 1000+ 模型（OpenAI、Bedrock、Ollama、vLLM、OpenRouter 等）
- **安装**：`pip install 'jupyter-ai[jupyternaut]'` 或 `pip install jupyter-ai-jupyternaut`
- **多模型切换**：同一 Persona 内可切换不同模型
- **记忆管理**：默认内存记忆，可选 SQLite 持久化（`[persistence]` extra）
- **工具访问**：默认访问所有 Jupyter MCP 工具

### Claude Code Persona

通过 `jupyter-ai-claude-code` 包提供，是 ACP Persona 的参考实现：
- 通过 ACP 协议连接 Claude Code CLI
- 支持模型选择、属性配置、推理力度调整
- 显示 Token 使用量和成本

### 其他 ACP Persona

安装对应的 Agent CLI 和 ACP 适配器后，自动可用：
- Codex（通过 @zed-industries/codex-acp）
- GitHub Copilot
- Goose
- Kilo
- Kiro
- Mistral Vibe
- OpenCode

## Persona 交互规则

### @提及机制

当聊天中有多个 Persona 或多个用户时，Persona 的回复规则如下：

| 场景 | 回复行为 |
|---|---|
| 1 用户 + 1 Persona | 该 Persona 总是自动回复 |
| 1 用户 + >1 Persona | 最后被 @提及 的 Persona 自动回复 |
| >1 用户 + ≥1 Persona | Persona 不自动回复，必须 @提及 |

**@多 Persona**：可以在一条消息中 @多个 Persona，每个被 @的 Persona 都会回复，方便比较不同 AI 的表现。

### Persona 选择器

聊天输入工具栏中有 Persona 选择菜单：
- 列出所有可用的 Persona
- 每个 Persona 初始化后显示模型选择器、权限模式、推理力度等设置
- 未登录的 Persona 显示登录提示

### 模型选择器

Persona 初始化完成后（通常首次回复后），会出现模型选择菜单：
- 显示该 Persona 支持的模型列表
- 允许在同一聊天中切换模型
- ACP Persona 可显示模型属性（如 Claude 的 thinking mode、effort level）
- 显示 Token 计数和成本信息（ACP Agent 支持）

## 自定义 Persona 开发

### BasePersona 基类

自定义 Persona 必须继承 `jupyter_ai_persona_manager:BasePersona`，并实现两个抽象成员：

#### `process_message()` 方法

```python
@abstractmethod
async def process_message(self, message: Message) -> None:
```

Persona 的主入口，处理每条新消息。`message.body` 包含消息文本内容。

#### `defaults` 属性

```python
@property
@abstractmethod
def defaults(self) -> PersonaDefaults:
```

返回 Persona 的默认配置（名称、头像、描述、系统提示）。

### PersonaDefaults 模型

```python
class PersonaDefaults(BaseModel):
    name: str           # 显示名称，如 "Jupyternaut"
    description: str    # 描述文本
    avatar_path: str    # 头像 URL 路径（相对于 Jupyter Server 域名）
    system_prompt: str  # 系统提示词
```

### 内置响应方法

BasePersona 提供两个方法用于发送回复：

| 方法 | 说明 |
|---|---|
| `send_message(body: str)` | 立即发送完整消息 |
| `stream_message(stream: AsyncIterator[str])` | 流式发送，接受 async iterator |

`stream_message()` 可直接传入 LangChain 模型的 `astream()` 输出。

### 注册 Entry Point

自定义 Persona 通过 Python entry points 注册：

```toml
[project.entry-points."jupyter_ai.personas"]
my_persona = "my_package.persona:MyPersona"
```

安装包并重启 JupyterLab 后，Persona 自动出现在选择器中。

### 最小实现

```python
from jupyter_ai_persona_manager import BasePersona
from jupyter_ai_persona_manager.api import PersonaDefaults
from jupyterlab_chat.models import Message, NewMessage

class DebugPersona(BasePersona):
    @property
    def defaults(self):
        return PersonaDefaults(
            name="DebugPersona",
            avatar_path="/api/ai/static/jupyternaut.svg",
            description="A debug persona.",
            system_prompt="You are a helpful assistant."
        )

    async def process_message(self, message: Message):
        self.send_message(NewMessage(body=f"Received: {message.body}", sender=self.id))
```

完整的 API 参考见 [Persona API 参考](../references/persona-api.md)。

## 相关概念

- [ACP 与 MCP 双协议](04-protocols-acp-mcp.md)
- [聊天界面](02-chat-interface.md)
- [Entry Points API](09-entry-points-api.md)
- [MCP 工具与 Notebook 交互](07-mcp-tools-and-notebooks.md)
- [Persona API 参考](../references/persona-api.md)
- [自定义 Persona 示例](../examples/custom-persona.md)

[^user-guide]: users/index.md
