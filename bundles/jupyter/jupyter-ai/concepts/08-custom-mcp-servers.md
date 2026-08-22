---
type: Concept
title: 自定义 MCP 服务器
description: 如何通过 mcp_settings.json 配置自定义 MCP 服务器，支持 stdio 和 HTTP 两种类型，以及环境变量配置
tags: [mcp, custom-server, stdio, http, configuration, extensions, tools]
sources:
  - id: mcp-config
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/mcp_config.md
    title: mcp_config.md
  - id: user-guide
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/index.md
    title: users/index.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# 自定义 MCP 服务器

除了内置的 Notebook 和 JupyterLab 工具，Jupyter AI 允许你通过配置文件添加自定义 MCP（Model Context Protocol）服务器。配置的工具对所有 ACP Agent 和直接模型 Persona 自动可用。

## 配置文件位置

自定义 MCP 服务器在 Jupyter 配置目录下的 `mcp_settings.json` 中配置：

| 操作系统 | 配置文件路径 |
|---|---|
| macOS/Linux | `~/.jupyter/mcp_settings.json` |
| Windows | `%USERPROFILE%\.jupyter\mcp_settings.json` |

> 如果配置文件不存在，需要手动创建。配置后需**重启 JupyterLab** 使更改生效。

## 配置格式

`mcp_settings.json` 包含一个 `mcp_servers` 数组，每个元素是一个 MCP 服务器配置对象：

```json
{
  "mcp_servers": [
    { ... 服务器配置 ... }
  ]
}
```

Jupyter AI 支持两种类型的 MCP 服务器：**stdio** 和 **HTTP**。

## Stdio 服务器

Stdio 服务器通过子进程运行，通过标准输入/输出与 Jupyter 通信。适用于本地工具和 CLI 工具。

```json
{
  "mcp_servers": [
    {
      "name": "Filesystem Tools",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/workspace"],
      "env": []
    }
  ]
}
```

| 字段 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `name` | string | ✅ | MCP 服务器的人类可读名称 |
| `command` | string | ✅ | 可执行文件路径或命令名 |
| `args` | string[] | ✅ | 命令行参数数组 |
| `env` | object[] | ❌ | 环境变量数组，每项含 `name` 和 `value` 字段 |

### 带环境变量的示例：GitHub MCP 服务器

```json
{
  "mcp_servers": [
    {
      "name": "GitHub Tools",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": [
        {"name": "GITHUB_PERSONAL_ACCESS_TOKEN", "value": "ghp_your_token_here"}
      ]
    }
  ]
}
```

## HTTP 服务器

HTTP 服务器通过 URL 连接到远程运行的 MCP 服务。适用于企业内部工具服务、远程 API 等。HTTP 服务器需要显式声明 `"type": "http"`。

```json
{
  "mcp_servers": [
    {
      "type": "http",
      "name": "Remote Tools",
      "url": "https://my-mcp-server.example.com/mcp",
      "headers": [
        {"name": "Authorization", "value": "Bearer your-token"}
      ]
    }
  ]
}
```

| 字段 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `type` | `"http"` | ✅ | HTTP 类型必须显式声明为 `"http"` |
| `name` | string | ✅ | MCP 服务器的人类可读名称 |
| `url` | string | ✅ | MCP 服务器的 HTTP URL |
| `headers` | object[] | ❌ | HTTP 请求头数组，每项含 `name` 和 `value` 字段 |

## 完整配置示例

```json
{
  "mcp_servers": [
    {
      "name": "Filesystem Tools",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"],
      "env": []
    },
    {
      "name": "GitHub Tools",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": [
        {"name": "GITHUB_PERSONAL_ACCESS_TOKEN", "value": "ghp_xxxxxxxxxxxxxxxx"}
      ]
    },
    {
      "type": "http",
      "name": "Company Internal Tools",
      "url": "https://internal-mcp.corp.example.com/mcp",
      "headers": [
        {"name": "Authorization", "value": "Bearer eyJhbGciOi..."}
      ]
    }
  ]
}
```

## 工作原理

1. Jupyter AI 启动时读取 `mcp_settings.json`
2. 对于每个配置的 stdio 服务器，启动子进程
3. 对于每个 HTTP 服务器，建立 HTTP 连接
4. 所有配置的 MCP 服务器与内置 Jupyter MCP 服务器一起注册
5. Persona/Agent 启动时，将所有可用 MCP 工具的信息传递给 Agent
6. Agent 可以像使用内置工具一样使用自定义 MCP 工具
7. 所有 MCP 工具调用（自定义和内置）都经过相同的权限审批流程

## 常用 MCP 服务器参考

以下是一些社区常用的 MCP 服务器：

| 服务器 | 用途 | 启动命令 |
|---|---|---|
| `@modelcontextprotocol/server-filesystem` | 文件系统读写 | `npx -y @modelcontextprotocol/server-filesystem <path>` |
| `@modelcontextprotocol/server-github` | GitHub 操作（Issues/PR/代码） | `npx -y @modelcontextprotocol/server-github`（需 `GITHUB_PERSONAL_ACCESS_TOKEN`） |
| `@modelcontextprotocol/server-brave-search` | 网络搜索 | `npx -y @modelcontextprotocol/server-brave-search`（需 Brave API key） |
| `@modelcontextprotocol/server-postgres` | PostgreSQL 数据库操作 | `npx -y @modelcontextprotocol/server-postgres <connection-string>` |

> 注意：第三方 MCP 服务器的安全性和可靠性由其作者负责，建议使用前审查工具代码和权限范围。

## Entry Points 方式注册（开发者）

除了 JSON 配置文件，Python 包还可以通过 entry points 注册 MCP 工具，详见 [Entry Points API](/concepts/09-entry-points-api.md) 和 [工具注册 API 参考](/references/entry-points-reference.md#工具注册-jupyter_server_mcp-tools)。

## 故障排查

### 自定义工具不可见
- 检查 `mcp_settings.json` 是否在正确的 Jupyter 配置目录（`~/.jupyter/`）
- 检查 JSON 格式是否正确（可用 JSON 验证器检查）
- 确认使用 `mcp_servers` 数组格式（不是 `servers` 对象）
- 确认 JupyterLab 已重启
- 检查命令路径是否正确（stdio 服务器需要 command 在 PATH 中）

### Stdio 服务器启动失败
- 确保 `command` 指向的可执行文件存在且可执行
- 在终端中手动运行 command + args 测试是否正常
- 检查必要的环境变量是否在 `env` 数组中正确设置

## 相关概念

- [ACP 与 MCP 双协议](/concepts/04-protocols-acp-mcp.md)
- [MCP 工具与 Notebook 交互](/concepts/07-mcp-tools-and-notebooks.md)
- [配置系统](/concepts/11-configuration-system.md)
- [Entry Points API](/concepts/09-entry-points-api.md)
- [MCP 配置参考](/references/mcp-config-reference.md)
- [配置自定义 MCP 服务器示例](/examples/custom-mcp-server.md)
