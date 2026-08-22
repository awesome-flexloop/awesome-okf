---
type: Reference
title: MCP 配置与工具参考
description: MCP 服务器配置格式（mcp_settings.json）、默认工具清单、权限系统参考
tags: [mcp, tools, configuration, permission, notebook]
sources:
  - id: user-guide
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/index.md
    title: users/index.md
  - id: init-py
    resource: external/libs/jupyter/jupyter-ai/jupyter_ai/__init__.py
    title: __init__.py
  - id: getting-started
    resource: external/libs/jupyter/jupyter-ai/docs/source/getting-started.md
    title: getting-started.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# MCP 配置与工具参考

本页提供 MCP（Model Context Protocol）服务器配置格式和默认工具集的完整参考。

## .jupyter/mcp_settings.json 配置

自定义 MCP 服务器通过工作区根目录的 `.jupyter/mcp_settings.json` 文件配置。Jupyter AI 启动时读取此文件，将配置的服务器自动提供给所有 ACP Agent。

### 顶层结构

```json
{
  "mcp_servers": [ ... ]
}
```

### Stdio 服务器配置

本地子进程方式运行的 MCP 服务器：

```json
{
  "mcp_servers": [
    {
      "name": "My Custom Tools",
      "command": "npx",
      "args": ["-y", "@my-org/my-mcp-server"],
      "env": [
        {"name": "API_KEY", "value": "sk-abc123"}
      ]
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | MCP 服务器的人类可读名称 |
| `command` | string | 是 | 服务器可执行文件路径 |
| `args` | string[] | 是 | 命令行参数列表 |
| `env` | object[] | 否 | 环境变量，每项含 `name` 和 `value` 字段 |

### HTTP 服务器配置

远程 HTTP MCP 服务器：

```json
{
  "mcp_servers": [
    {
      "type": "http",
      "name": "Remote Tools",
      "url": "https://my-mcp-server.example.com/mcp",
      "headers": [
        {"name": "Authorization", "value": "Bearer my-token"}
      ]
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `type` | `"http"` | 是 | HTTP 类型必须显式声明 |
| `name` | string | 是 | MCP 服务器的人类可读名称 |
| `url` | string | 是 | MCP 服务器 URL |
| `headers` | object[] | 否 | HTTP 请求头，每项含 `name` 和 `value` 字段 |

### 完整配置示例

```json
{
  "mcp_servers": [
    {
      "name": "Filesystem Tools",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    },
    {
      "name": "GitHub Tools",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": [
        {"name": "GITHUB_PERSONAL_ACCESS_TOKEN", "value": "ghp_xxx"}
      ]
    },
    {
      "type": "http",
      "name": "Company Internal Tools",
      "url": "https://internal-mcp.corp.example.com/mcp",
      "headers": [
        {"name": "Authorization", "value": "Bearer my-token"}
      ]
    }
  ]
}
```

配置修改后需重启 JupyterLab 生效。

## 默认 MCP 工具清单

Jupyter AI 通过 `jupyter_server_mcp` 默认注册 16 个工具，分两个工具集。

### Notebook 工具集

`jupyter_ai_tools.toolkits.notebook` 提供 13 个 Notebook 操作工具：

| 工具名 | 功能 |
|---|---|
| `read_notebook` | 读取当前活动 Notebook 的完整内容 |
| `read_notebook_cells` | 批量读取指定单元格 |
| `read_cell` | 读取单个单元格内容 |
| `add_cell` | 在 Notebook 末尾添加单元格 |
| `insert_cell` | 在指定位置插入单元格 |
| `delete_cell` | 删除指定单元格 |
| `edit_cell` | 编辑（替换）单元格内容 |
| `select_cell` | 选中指定单元格 |
| `get_cell_id_from_index` | 根据索引获取单元格 ID |
| `get_active_notebook` | 获取当前活动 Notebook 信息 |
| `get_active_cell_id` | 获取当前活动单元格 ID |
| `get_open_documents` | 获取所有打开的文档列表 |
| `create_notebook` | 创建新的空 Notebook |

### JupyterLab 工具集

`jupyter_ai_tools.toolkits.jupyterlab` 提供 3 个 JupyterLab 操作工具：

| 工具名 | 功能 |
|---|---|
| `open_file` | 在 JupyterLab 中打开指定文件 |
| `run_cell` | 运行指定单元格（通过内核执行） |
| `run_all_cells` | 运行 Notebook 中所有单元格 |

## 权限系统

Agent 调用工具时遵循权限护栏机制：

- **默认行为**：Agent 在写入文件、执行命令或调用 MCP 工具前**必须请求用户批准**
- **权限控制**：通过输入工具栏的控制按钮切换权限模式
- **工具调用审批 UI**：弹出对话框显示工具名称和参数，用户选择允许/拒绝

## 协议角色

Jupyter AI 在单一会话中可同时扮演多个协议角色：

| 角色 | 协议 | 说明 |
|---|---|---|
| ACP Client | ACP | 连接外部 ACP Agent 到聊天界面 |
| MCP Server | MCP | Jupyter Server 暴露 Notebook 工具给 Agent |
| MCP Client 配置提供者 | MCP | 读取 mcp_settings.json 并传递给 Agent |

## 相关概念

- [MCP 工具与 Notebook 交互](/concepts/07-mcp-tools-and-notebooks.md)
- [ACP 与 MCP 双协议](/concepts/04-protocols-acp-mcp.md)
- [自定义 MCP 服务器](/concepts/08-custom-mcp-servers.md)
- [自定义 MCP 服务器示例](/examples/custom-mcp-server.md)
