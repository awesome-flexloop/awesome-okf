---
type: Concept
title: Entry Points API
description: Jupyter AI 的 entry points 插件机制，包括 Persona 注册、MCP 工具注册、聊天命令注册的 API 和示例
tags: [entry-points, plugin, extension, persona, tools, chat-commands, developer-api]
sources:
  - id: entry-points
    resource: external/libs/jupyter/jupyter-ai/docs/source/developers/entry_points_api/index.md
    title: entry_points_api/index.md
  - id: personas-group
    resource: external/libs/jupyter/jupyter-ai/docs/source/developers/entry_points_api/personas_group.md
    title: personas_group.md
  - id: tools-group
    resource: external/libs/jupyter/jupyter-ai/docs/source/developers/entry_points_api/tools_group.md
    title: tools_group.md
  - id: ep-ref
    resource: external/libs/jupyter/jupyter-ai/docs/source/developers/reference/entry_points.md
    title: entry_points.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# Entry Points API

Jupyter AI 使用 Python entry points 作为插件注册机制。第三方开发者可以通过在 `pyproject.toml` 中声明 entry points，向 Jupyter AI 注册自定义 Persona、MCP 工具和聊天命令，无需修改 Jupyter AI 核心代码。

## Entry Points 概览

Jupyter AI 定义了 4 个 entry point group：

| Entry Point Group | 注册对象 | 必需包 |
|---|---|---|
| `jupyter_ai.personas` | 自定义 AI Persona | `jupyter_ai_persona_manager` |
| `jupyter_server_mcp.tools` | MCP 工具包 | `jupyter_server_mcp` |
| `jupyter_ai.chat_commands` | 斜杠命令处理函数 | `jupyter_ai_chat_commands` |
| `jupyterlab_chat.awareness` | Awareness 面板插件 | `jupyterlab_chat` |

## 注册 AI Persona

### 1. 创建 Persona 类

继承 `BasePersona`，实现 `process_message()` 方法和 `defaults` 属性：

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
            description="A debug persona that echoes user input.",
            system_prompt="You are a helpful assistant."
        )

    async def process_message(self, message: Message):
        """处理用户消息，返回回复"""
        # 发送回复
        self.send_message(
            NewMessage(body=f"Echo: {message.body}", sender=self.id)
        )
```

### 2. 声明 Entry Point

在 `pyproject.toml` 中注册：

```toml
[project.entry-points."jupyter_ai.personas"]
debug_persona = "my_persona:DebugPersona"
```

### 3. 流式回复

使用 `stream_message()` 发送流式回复：

```python
async def process_message(self, message: Message):
    # 假设有一个 async iterator 生成文本块
    async def text_stream():
        for chunk in ["Hello", ", ", "world!"]:
            yield chunk

    await self.stream_message(text_stream())
```

可以直接传入 LangChain/LLM 的 `astream()` 输出。

详细 API 见 [Persona API 参考](../references/persona-api.md)。

## 注册 MCP 工具

MCP 工具通过 `jupyter_server_mcp.tools` entry point 注册，支持三种返回类型。

### 类型 1：字符串列表（默认 MCP 工具路径）

```python
# my_package/tools.py
MY_TOOLS = [
    "my_package.toolkits.data:query_database",
    "my_package.toolkits.data:list_tables",
]
```

```toml
[project.entry-points."jupyter_server_mcp.tools"]
my_tools = "my_package.tools:MY_TOOLS"
```

### 类型 2：Tool 对象（MCP 兼容）

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-tools")

@mcp.tool()
def query_database(sql: str) -> str:
    """Execute SQL query and return results."""
    # ...
    return results
```

```toml
[project.entry-points."jupyter_server_mcp.tools"]
my_tools = "my_package.tools:mcp"
```

### 类型 3：MCP Server URL（远程服务器）

```python
MY_SERVER = "https://my-mcp-server.example.com/mcp"
```

```toml
[project.entry-points."jupyter_server_mcp.tools"]
remote_tools = "my_package.config:MY_SERVER"
```

### Jupyter AI 默认工具注册

Jupyter AI 自身通过相同机制注册默认工具：

```toml
[project.entry-points."jupyter_server_mcp.tools"]
jupyter_ai = "jupyter_ai:DEFAULT_JUPYTER_SERVER_MCP_TOOLS"
```

## 注册聊天命令

聊天斜杠命令（如 `/clear`、`/help`）通过 `jupyter_ai.chat_commands` entry point 注册。

```python
from jupyter_ai_chat_commands import ChatCommand, CommandContext

async def my_command(ctx: CommandContext, args: str):
    """处理 /mycommand 命令"""
    await ctx.reply(f"Received args: {args}")

my_chat_command = ChatCommand(
    name="mycommand",
    description="我的自定义命令",
    handler=my_command,
)
```

```toml
[project.entry-points."jupyter_ai.chat_commands"]
my_command = "my_package.commands:my_chat_command"
```

默认聊天命令由 `jupyter_ai_chat_commands` 包提供。

## 完整的 Entry Point 参考

| Group | 对象类型 | 注册值类型 | 说明 |
|---|---|---|---|
| `jupyter_ai.personas` | Persona 类 | `BasePersona` 子类 | 每个 entry point 是一个 Persona 类 |
| `jupyter_server_mcp.tools` | 工具集合 | `List[str]` / `FastMCP` / `str` (URL) | 每个 entry point 是一组工具或 MCP 服务器 |
| `jupyter_ai.chat_commands` | 聊天命令 | `ChatCommand` 实例 | 每个 entry point 是一个斜杠命令 |
| `jupyterlab_chat.awareness` | Awareness 面板 | Awareness 提供者 | 在聊天侧栏显示活动信息 |

## 开发流程

1. 选择需要扩展的功能点（Persona/工具/命令）
2. 创建 Python 包，依赖对应子包
3. 实现功能类/函数
4. 在 pyproject.toml 中声明 entry points
5. 安装包（`pip install -e .` 开发模式）
6. 重启 JupyterLab，插件自动加载

## 相关概念

- [AI Persona 系统](05-ai-personas.md)
- [MCP 工具与 Notebook 交互](07-mcp-tools-and-notebooks.md)
- [自定义 MCP 服务器](08-custom-mcp-servers.md)
- [Persona API 参考](../references/persona-api.md)
- [Entry Points 参考](../references/entry-points-reference.md)
- [配置参考](../references/config-reference.md)
- [自定义 Persona 示例](../examples/custom-persona.md)
