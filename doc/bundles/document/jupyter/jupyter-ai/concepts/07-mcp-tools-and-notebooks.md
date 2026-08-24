---
type: Concept
title: MCP 工具与 Notebook 交互
description: Jupyter AI 内置的 MCP 工具集、Notebook 操作工具、JupyterLab 操作工具以及工具调用的权限机制
tags: [mcp, tools, notebook, cell, kernel, execution, permissions]
sources:
  - id: user-guide
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/index.md
    title: users/index.md
  - id: tools-group
    resource: external/libs/jupyter/jupyter-ai/docs/source/developers/entry_points_api/tools_group.md
    title: tools_group.md
  - id: init-py
    resource: external/libs/jupyter/jupyter-ai/jupyter_ai/__init__.py
    title: jupyter_ai/__init__.py
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# MCP 工具与 Notebook 交互

MCP 工具是 AI Persona 与 Jupyter 环境交互的核心机制。Jupyter AI 通过 `jupyter_ai_tools` 包提供了一整套内置工具，覆盖 Notebook 读写编辑、单元格执行、文件操作、JupyterLab 命令等能力。

## 内置工具集概览

Jupyter AI 默认注册了 16 个 MCP 工具（来自 `DEFAULT_JUPYTER_SERVER_MCP_TOOLS`），分为两个工具包：

### Notebook 工具包（13个）

这些工具让 AI Persona 可以读取、创建、编辑、选择 Jupyter Notebook 单元格：

| 工具 | 功能 |
|---|---|
| `read_notebook` | 读取当前活动 Notebook 的完整内容 |
| `read_notebook_cells` | 批量读取指定单元格 |
| `read_cell` | 读取单个单元格内容 |
| `add_cell` | 在 Notebook 末尾添加新单元格 |
| `insert_cell` | 在指定位置插入单元格 |
| `delete_cell` | 删除指定单元格 |
| `edit_cell` | 编辑（替换）单元格内容 |
| `select_cell` | 选中指定单元格 |
| `get_cell_id_from_index` | 根据索引获取单元格 ID |
| `get_active_notebook` | 获取当前活动 Notebook 信息 |
| `get_active_cell_id` | 获取当前活动单元格 ID |
| `get_open_documents` | 获取所有打开的文档列表 |
| `create_notebook` | 创建新的空 Notebook |

### JupyterLab 工具包（3个）

这些工具让 AI Persona 可以操作 JupyterLab 界面和执行代码：

| 工具 | 功能 |
|---|---|
| `open_file` | 在 JupyterLab 中打开指定文件 |
| `run_cell` | 运行指定单元格（通过内核执行代码） |
| `run_all_cells` | 运行 Notebook 中所有单元格 |

## 工具注册机制

内置工具通过 Python entry point `jupyter_server_mcp.tools` 注册：[^tools-group]

```toml
[project.entry-points."jupyter_server_mcp.tools"]
jupyter_ai = "jupyter_ai:DEFAULT_JUPYTER_SERVER_MCP_TOOLS"
```

`DEFAULT_JUPYTER_SERVER_MCP_TOOLS` 是 `jupyter_ai/__init__.py` 中定义的字符串列表：

```python
DEFAULT_JUPYTER_SERVER_MCP_TOOLS = [
    # Notebook 工具
    "jupyter_ai_tools.toolkits.notebook:read_notebook",
    "jupyter_ai_tools.toolkits.notebook:add_cell",
    # ... 16 个工具路径
]
```

### 自定义工具包注册

第三方包可以通过相同的 entry point 注册自定义工具：

```toml
[project.entry-points."jupyter_server_mcp.tools"]
my_tools = "my_package.tools:MY_TOOLS"
```

其中 `MY_TOOLS` 是可被调用的对象，支持三种类型：
1. **字符串列表**：每个字符串是 Python 可调用对象的点分路径
2. **Tool 对象**：兼容 MCP Tool 协议的对象
3. **MCP Server URL 字符串**：以 `http://` 或 `https://` 开头的远程 MCP Server 地址

## 工具调用流程

```
用户消息 → AI Persona/Agent
              │
              ├── 1. 分析消息，决定需要什么操作
              │
              ├── 2. 调用 MCP 工具（如 run_cell）
              │       │
              │       ▼
              ├── 3. 权限审批对话框弹出
              │       │
              │       ▼
              ├── 4. 用户批准/拒绝
              │       │
              │       ▼
              ├── 5. 工具执行（如内核运行代码）
              │       │
              │       ▼
              └── 6. 结果返回给 Agent，继续生成回复
```

## 权限护栏

### 默认安全策略

Jupyter AI 默认启用安全护栏：**Agent 在写入文件、运行命令或使用 MCP 工具前必须请求权限**。这防止 AI 误操作修改用户数据或执行危险命令。

### 权限模式

权限模式可通过输入工具栏的控制按钮调整：
- **审批模式（默认）**：每次工具调用都弹出审批对话框
- **自动批准模式**：在当前会话中自动批准某类工具（需手动启用）
- **拒绝模式**：拒绝所有工具调用

### 权限选项

审批对话框提供以下选项：
- **允许一次**：仅本次允许该工具调用
- **始终允许**：本次聊天会话中始终允许该工具
- **拒绝**：拒绝本次调用

### Agent 自身的权限控制

部分外部 ACP Agent（如 Claude Code、Codex）有自己的权限/工具模式设置，在模型选择器中可以调整。这些设置独立于 Jupyter AI 的权限护栏。

## Notebook 交互示例

AI Persona 典型的 Notebook 操作序列：

**场景：帮我修复第3个单元格的错误**

1. `get_active_notebook()` → 获取当前活动 Notebook 信息
2. `read_notebook()` → 读取整个 Notebook 内容
3. `get_cell_id_from_index(2)` → 获取第3个单元格的 ID（0-indexed）
4. `read_cell(cell_id)` → 读取该单元格内容
5. 分析代码和错误
6. `edit_cell(cell_id, new_code)` → 编辑修复代码
7. `select_cell(cell_id)` → 选中修复后的单元格
8. `run_cell()` → 运行当前选中的单元格（JupyterLab 工具）
9. 返回结果给用户

## 相关概念

- [ACP 与 MCP 双协议](04-protocols-acp-mcp.md)
- [自定义 MCP 服务器](08-custom-mcp-servers.md)
- [AI Persona 系统](05-ai-personas.md)
- [Entry Points API](09-entry-points-api.md)
- [MCP 配置与工具参考](../references/mcp-config-reference.md)
- [Entry Points 参考](../references/entry-points-reference.md)

[^tools-group]: tools_group.md
