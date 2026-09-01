---
type: Example
title: "配置自定义 MCP 服务器"
description: "添加和配置 MCP (Model Context Protocol) 服务器，扩展 AI 的工具能力"
tags: [jupyterlite-ai, mcp, model-context-protocol, custom-tools, integration]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-04-21T00:00:00+08:00" }
status: stable
stale_after: 2026-10-21
sources:
  - id: source
    resource: /references/source-code.md
    title: 源码结构与核心文件索引
  - id: plugin
    resource: /references/plugin-architecture.md
    title: 插件架构参考
---

# 配置自定义 MCP 服务器

MCP (Model Context Protocol) 是一种开放协议，允许你将外部工具和数据源接入 AI 助手。本指南介绍如何在 JupyterLite AI 中配置自定义 MCP 服务器。

## MCP 概述

MCP 服务器可以为 AI 提供额外的工具，例如：
- 数据库查询工具
- 文件系统操作工具
- API 集成工具
- 自定义业务逻辑工具

JupyterLite AI 内置了一个 MCP 管理器，支持动态添加/移除 MCP 服务器并自动将其工具注册到 AI 工具循环中。

## 配置方式

### 通过设置面板配置

1. 打开 AI Chat 设置面板（齿轮图标）
2. 找到 **MCP Servers** 配置区域
3. 添加 MCP 服务器配置

MCP 服务器配置格式：

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"],
      "env": {}
    }
  }
}
```

### 通过 Settings Editor 配置

1. 菜单栏 → Settings → Settings Editor
2. 找到 JupyterLite AI 设置
3. 在 `mcpServers` 字段中添加配置

## MCP 服务器配置参数

每个 MCP 服务器配置支持以下字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `command` | string | ✅ | 启动 MCP 服务器的命令 |
| `args` | string[] | ❌ | 命令行参数列表 |
| `env` | object | ❌ | 环境变量键值对 |
| `url` | string | ❌ | SSE/HTTP 传输的 URL（替代 command） |

### 两种传输方式

1. **Stdio 传输**（本地进程）：
   ```json
   {
     "command": "npx",
     "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
   }
   ```

2. **SSE/HTTP 传输**（远程服务）：
   ```json
   {
     "url": "http://localhost:3000/sse"
   }
   ```

> ⚠️ JupyterLite 浏览器环境中，stdio 模式受限（无法启动本地进程），建议使用 SSE/HTTP 模式。

## 常用 MCP 服务器示例

### 1. 文件系统访问

允许 AI 读取和操作指定目录的文件：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/notebooks"]
    }
  }
}
```

### 2. GitHub 集成

允许 AI 操作 GitHub 仓库：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

### 3. PostgreSQL 数据库

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost:5432/mydb"]
    }
  }
}
```

### 4. 自定义 MCP 服务器（Python）

如果你有自己开发的 MCP 服务器：

```json
{
  "mcpServers": {
    "my-custom-tools": {
      "command": "python",
      "args": ["-m", "my_mcp_server"],
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

## MCP 服务器生命周期

1. **添加配置** → MCP 管理器检测到新配置
2. **启动连接** → 建立与 MCP 服务器的通信（stdio 进程或 SSE 连接）
3. **工具发现** → 自动获取 MCP 服务器提供的工具列表
4. **工具注册** → 将 MCP 工具注入 AI 的 ToolLoop
5. **使用工具** → AI 可在对话中调用 MCP 工具
6. **断开/移除** → 配置移除或重启时断开连接

## 工具审批

MCP 工具的审批策略取决于工具的元数据：
- 如果 MCP 工具声明为破坏性操作（`destructive: true`），执行前需要用户审批
- 否则 AI 可以自动调用

## 故障排查

### 常见问题

**Q: MCP 服务器连接失败**
- 检查 command/args 是否正确
- 确保命令对应的包已安装（如 `npx` 会自动下载，但需网络连接）
- 查看浏览器控制台/终端日志中的错误信息

**Q: JupyterLite 中无法启动 stdio MCP 服务器**
- 浏览器环境无法启动本地进程，请使用 SSE/HTTP 模式的 MCP 服务器
- 将 MCP 服务器部署为远程 HTTP 服务，通过 `url` 字段连接

**Q: MCP 工具未出现在可用工具中**
- 检查 MCP 服务器是否成功启动
- 等待几秒钟让工具发现完成
- 尝试重启 AI 内核（重新打开聊天面板或刷新页面）

**Q: MCP 工具调用报错**
- 确认 MCP 服务器本身正常运行（可独立测试）
- 检查环境变量和认证信息是否正确配置
