---
title: CLI 部署 Agent 项目
type: example
bundle: /datawhale/deepagents
sources:
  - https://github.com/datawhalechina/deepagents/blob/main/libs/cli/README.md
---

# CLI 部署 Agent 项目

使用 `deepagents-cli` 脚手架新项目、注册 MCP 服务器并部署为托管 Agent。

## 安装

```bash
uv tool install deepagents-cli
export LANGSMITH_API_KEY="..."
```

## 部署流程

### 1. 脚手架新项目

```bash
deepagents init my-agent
cd my-agent
```

生成结构：
- `agent.json` — Agent 配置
- `AGENTS.md` — 系统提示
- `tools.json` — 工具定义（初始为空）
- `skills/` — 示例技能
- `subagents/` — 示例子 Agent

### 2. 注册 MCP 服务器

```bash
deepagents mcp-servers add \
  --url https://tools.langchain.com \
  --header X-Api-Key=$LANGSMITH_API_KEY \
  --name Fleet
```

### 3. 配置工具

编辑 `tools.json`，引用已注册 MCP 服务器的工具：

```json
{
  "name": "read_url_content",
  "mcp_server_url": "https://tools.langchain.com",
  "mcp_server_name": "Fleet",
  "display_name": "read_url_content"
}
```

### 4. 部署

```bash
deepagents deploy
```

## Agent 管理命令

```bash
deepagents agents list
deepagents agents get <agent_id>
deepagents agents delete <agent_id>
```

## MCP 服务器管理

```bash
deepagents mcp-servers list
deepagents mcp-servers tools <id|name|url>
deepagents mcp-servers update <id|name|url>
deepagents mcp-servers delete <id|name|url>
deepagents mcp-servers connect <id|name|url>
```

## 沙箱后端配置

在 `agent.json` 中配置沙箱后端：

```json
{
  "backend": {
    "type": "sandbox",
    "sandbox_config": {
      "scope": "thread",
      "policy_ids": ["policy-id"]
    }
  }
}
```

## 相关概念

- [CLI部署工具链](/datawhale/deepagents/concepts/cli-toolchain)
