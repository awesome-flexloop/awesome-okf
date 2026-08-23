---
type: Reference
title: 元包源码参考
description: jupyter-ai 元包的 pyproject.toml、__init__.py 和 AGENTS.md 源码参考
tags: [metapackage, pyproject, entry-points, mcp-tools, source]
sources:
  - id: pyproject
    resource: external/libs/jupyter/jupyter-ai/pyproject.toml
    title: pyproject.toml
  - id: init-py
    resource: external/libs/jupyter/jupyter-ai/jupyter_ai/__init__.py
    title: __init__.py
  - id: agents-md
    resource: external/libs/jupyter/jupyter-ai/AGENTS.md
    title: AGENTS.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# 元包源码参考

本页提供 jupyter-ai 元包核心文件的源码级参考。

## 包元数据

**版本**：3.1.3（定义在 `jupyter_ai/__init__.py` 的 `__version__`）  
**构建系统**：hatchling>=1.4.0  
**Python 要求**：>=3.9  
**许可证**：BSD-3-Clause  

## 核心依赖（pyproject.toml）

| 包名 | 版本范围 | 职责 |
|---|---|---|
| `jupyterlab_chat` | >=0.23.2,<0.24.0 | 聊天 UI 基础组件（React + Python 后端） |
| `jupyter_server_documents` | >=0.3.3,<0.4.0 | 服务端文档处理（YDoc 协作、内核管理） |
| `jupyter_ai_router` | >=0.0.7,<0.1.0 | 消息路由层 |
| `jupyter_ai_persona_manager` | >=0.1.2,<0.2.0 | AI Persona 注册与管理 |
| `jupyter_ai_chat_commands` | >=0.0.4,<0.1.0 | 默认聊天斜杠命令 |
| `jupyter_ai_acp_client` | >=0.2.1,<0.3.0 | Agent Client Protocol 客户端实现 |
| `jupyter_server_mcp` | >=0.2.1,<0.4.0 | Jupyter Server MCP 接口/扩展 |
| `jupyter_ai_tools` | >=0.6.1,<0.7.0 | Notebook 与 Git 工具集 |
| `jupyterlab_notebook_awareness` | >=0.2.0,<0.3.0 | Notebook/单元格 Awareness 追踪 |
| `jupyterlab_commands_toolkit` | >=0.1.6,<0.2.0 | JupyterLab 命令工具包 |

## 可选依赖

| extra 名 | 包含包 | 功能 |
|---|---|---|
| `magics` | jupyter_ai_litellm, jupyter_ai_magic_commands | IPython magic 命令（%ai/%%ai） |
| `jupyternaut` | jupyter_ai_litellm, jupyter_ai_jupyternaut | 默认 AI Persona（基于 LiteLLM） |
| `docs` | sphinx, myst_parser, shibuya 等 | 文档构建依赖 |

## Entry Points

### jupyter_server_mcp.tools

元包注册了默认 MCP 工具集，通过 `DEFAULT_JUPYTER_SERVER_MCP_TOOLS` 列表暴露：

**Notebook 工具集**（jupyter_ai_tools.toolkits.notebook）：

| 工具名 | 功能 |
|---|---|
| `read_notebook` | 读取当前 Notebook |
| `read_notebook_cells` | 读取多个单元格 |
| `read_cell` | 读取单个单元格 |
| `add_cell` | 添加单元格 |
| `insert_cell` | 插入单元格 |
| `delete_cell` | 删除单元格 |
| `edit_cell` | 编辑单元格 |
| `select_cell` | 选中单元格 |
| `get_cell_id_from_index` | 根据索引获取单元格 ID |
| `get_active_notebook` | 获取活动 Notebook |
| `get_active_cell_id` | 获取活动单元格 ID |
| `get_open_documents` | 获取打开的文档列表 |
| `create_notebook` | 创建新 Notebook |

**JupyterLab 工具集**（jupyter_ai_tools.toolkits.jupyterlab）：

| 工具名 | 功能 |
|---|---|
| `open_file` | 打开文件 |
| `run_cell` | 运行单元格 |
| `run_all_cells` | 运行所有单元格 |

## 子模块清单（submodules/manifest.json）

文档聚合子模块注册表，映射 PyPI 包名到 GitHub 仓库：

```json
{
  "jupyter_server_documents": "jupyter-ai-contrib/jupyter-server-documents",
  "jupyter_ai_router": "jupyter-ai-contrib/jupyter-ai-router",
  "jupyter_ai_persona_manager": "jupyter-ai-contrib/jupyter-ai-persona-manager",
  "jupyter_ai_chat_commands": "jupyter-ai-contrib/jupyter-ai-chat-commands",
  "jupyter_ai_acp_client": "jupyter-ai-contrib/jupyter-ai-acp-client",
  "jupyter_server_mcp": "jupyter-ai-contrib/jupyter-server-mcp",
  "jupyter_ai_tools": "jupyter-ai-contrib/jupyter-ai-tools",
  "jupyterlab_notebook_awareness": "jupyter-ai-contrib/jupyterlab-notebook-awareness",
  "jupyterlab_commands_toolkit": "jupyter-ai-contrib/jupyterlab-commands-toolkit",
  "jupyter_ai_litellm": "jupyter-ai-contrib/jupyter-ai-litellm",
  "jupyter_ai_magic_commands": "jupyter-ai-contrib/jupyter-ai-magic-commands",
  "jupyter_ai_jupyternaut": "jupyter-ai-contrib/jupyter-ai-jupyternaut"
}
```

## 相关概念

- [元包架构](../concepts/03-metapackage-architecture.md)
- [MCP 工具与 Notebook 交互](../concepts/07-mcp-tools-and-notebooks.md)
- [Entry Points API](../concepts/09-entry-points-api.md)
