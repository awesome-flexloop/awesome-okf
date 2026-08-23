---
type: Concept
title: MCP 配置格式
description: 在 TRAE IDE 中通过 Settings → MCP → Add 路径配置 MCP 服务器，JSON 配置包含 mcpServers 顶层结构，每个服务器需指定 command、args 和 env 字段。
tags: [trae-mcp, trae, mcp, configuration, json-config, setup]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/mcp-source.md
    title: "Trae MCP 源码信源"
---

# MCP 配置格式

本文档介绍在 TRAE IDE 中配置 MCP 服务器的 JSON 格式和操作流程。

## 添加 MCP 的入口路径

在 TRAE 中添加 MCP 服务器的操作路径为：

```
Settings → MCP → Add → Manually Add
```

## JSON 配置结构

MCP 配置为 JSON 格式，顶层结构如下：

```json
{
  "mcpServers": {
    "your-mcp-name": {
      "command": "启动命令",
      "args": ["参数1", "参数2"],
      "env": {
        "环境变量名": "环境变量值"
      }
    }
  }
}
```

### 顶层结构

- `mcpServers`：顶层对象，key 为 MCP 服务器的名称（自定义），value 为该服务器的配置。

### 单服务器配置字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `command` | string | 是 | 启动 MCP 服务器进程的命令，如 `node`、`npx`、`python` |
| `args` | string[] | 是 | 传递给 command 的参数数组 |
| `env` | object | 否 | 启动进程时的环境变量键值对，用于传入 API Key 等敏感信息 |

## 配置示例

### 示例 1：本地构建的 MCP 服务器

```json
{
  "mcpServers": {
    "your-mcp-name": {
      "command": "node",
      "args": ["/absolute/path/to/build/index.js"],
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

此配置通过 `node` 命令启动本地构建好的 MCP 服务器入口文件 `index.js`，并通过 `env` 传入 `API_KEY` 环境变量。

### 示例 2：通过 npx 启动 npm 包形式的 MCP（CloudBase MCP）

```json
{
  "mcpServers": {
    "cloudbase-mcp": {
      "command": "npx",
      "args": ["-y", "@cloudbase/cloudbase-mcp@latest"],
      "env": {}
    }
  }
}
```

此配置通过 `npx -y` 自动下载并运行最新版本的 CloudBase MCP 包。`-y` 参数表示自动确认安装。首次使用时，服务器会打开浏览器进行登录和环境选择。

## 使用方式

配置完成后：

1. 保存配置
2. 返回 TRAE 聊天界面
3. 使用 **Builder with MCP** 或自定义 agent
4. 即可在对话中调用新添加的 MCP 工具

## Transport 选择策略

`command` 和 `args` 的选择取决于 MCP 服务器的分发形式：

| 分发形式 | command | args 示例 | 说明 |
|---------|---------|----------|------|
| npm 全局包 | `npx` | `["-y", "package-name@latest"]` | 最简单，无需预安装 |
| 本地 Node.js 项目 | `node` | `["/absolute/path/to/build/index.js"]` | 需要先构建，路径必须为绝对路径 |
| Python 包 | `python` / `uvx` | `["-m", "package_name"]` | 取决于具体包的入口方式 |
| 独立可执行文件 | 可执行文件路径 | `[]` | 如编译好的 Go/Rust 二进制文件 |

## 相关链接

- [MCP 三层模型](/concepts/01-mcp-architecture.md)
- [CloudBase MCP](/concepts/03-cloudbase-mcp.md)
- [MCP 开发入门](/concepts/05-mcp-development.md)
- [配置 MCP 服务器示例](/examples/configure-mcp.md)
- [CloudBase MCP 使用示例](/examples/use-cloudbase-mcp.md)
