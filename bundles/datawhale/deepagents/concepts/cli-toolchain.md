---
title: CLI 部署工具链
type: concept
bundle: /datawhale/deepagents
related:
  - /datawhale/deepagents/concepts/monorepo-architecture
  - /datawhale/deepagents/concepts/code-module
  - /datawhale/deepagents/concepts/core-sdk
sources:
  - https://github.com/datawhalechina/deepagents/blob/main/libs/cli/README.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/cli/DEVELOPMENT.md
  - https://github.com/datawhalechina/deepagents/blob/main/libs/cli/deepagents_cli/main.py
---

# CLI 部署工具链

`deepagents-cli`（位于 `libs/cli/`）是 Deep Agents 的**部署命令行工具**，用于将 Agent 项目脚手架化并部署到 LangSmith Managed Deep Agents 平台。

> 重要：自 `deepagents-cli==0.1.0` 起，交互式 REPL 已拆分到独立的 [`deepagents-code`](/datawhale/deepagents/concepts/code-module) 包（`dcode`）。CLI 包现在仅包含部署子命令。

## 安装与前置条件

```bash
uv tool install deepagents-cli
```

需要 LangSmith API 密钥（访问 Managed Deep Agents 私有预览），通过环境变量、仓库 `.env` 或 `~/.deepagents/.env` 提供：

```bash
export LANGSMITH_API_KEY="..."
```

## 子命令

CLI 包含四个子命令组：

### init — 脚手架新项目

```bash
deepagents init my-agent
```

生成以下项目结构：

```text
my-agent/
  agent.json              # 名称、描述、后端、运行时模型、权限
  AGENTS.md               # 系统提示
  tools.json              # Agent 可调用的工具（可选）
  skills/<name>/SKILL.md  # frontmatter 标记的技能（可选）
  subagents/<name>/       # 委派的子 Agent 定义（可选）
```

`tools.json` 初始为空，因为每个工具必须引用已在工作区注册的 MCP 服务器。

### deploy — 部署托管 Agent

```bash
cd my-agent && deepagents deploy
```

将项目 upsert 为 `/v1/deepagents/*` 上的托管 Agent。

新 Agent 默认使用 `state` 后端。可通过 `agent.json` 配置沙箱后端：

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

`scope` 可选 `thread` 或 `agent`。CLI 不在本地创建或运行沙箱，沙箱生命周期由 Managed Deep Agents 平台处理。

### agents — Agent 管理

```bash
deepagents agents list                  # 列出工作区 Agent
deepagents agents get <agent_id>        # 显示单个 Agent
deepagents agents delete <agent_id>     # 删除 Agent
```

### mcp-servers — MCP 服务器管理

```bash
deepagents mcp-servers list                  # 列出工作区 MCP 服务器
deepagents mcp-servers add --url URL          # 注册服务器
deepagents mcp-servers get <id|name|url>      # 显示服务器
deepagents mcp-servers tools <id|name|url>    # 列出服务器工具
deepagents mcp-servers update <id|name|url>   # 更新 URL 或 headers
deepagents mcp-servers delete <id|name|url>   # 移除服务器
deepagents mcp-servers connect <id|name|url>  # 为服务器启动 OAuth
```

`get`、`update`、`delete`、`connect` 接受 MCP 服务器的 id、精确名称或 URL（URL 匹配忽略大小写和尾部斜杠）。

## CLI 源码结构

```text
libs/cli/deepagents_cli/
  __init__.py
  __main__.py
  main.py              # CLI 入口
  config.py            # 配置处理
  model_config.py      # 模型配置
  deploy/
    __init__.py
    commands.py        # deploy 子命令实现
    api_client.py      # LangSmith API 客户端
    project.py         # 项目脚手架
    payload.py         # 部署载荷构建
    state.py           # 状态管理
    mcp_resolver.py    # MCP 服务器解析
```

## 部署流程概要

1. `deepagents init` 创建项目骨架
2. `deepagents mcp-servers add` 注册工具所需的 MCP 服务器
3. 编辑 `tools.json` 引用已注册的 MCP 服务器工具
4. 编辑 `AGENTS.md` 编写系统提示
5. （可选）添加 `skills/` 和 `subagents/`
6. `deepagents deploy` 部署到托管平台

## 与其他概念的关系

- [Code终端编码Agent](/datawhale/deepagents/concepts/code-module) 是从 CLI 拆分出的交互式产品，两者是独立包。
- [核心SDK与三层架构](/datawhale/deepagents/concepts/core-sdk) 是 CLI 部署的 Agent 的底层运行时。
- [Monorepo 架构](/datawhale/deepagents/concepts/monorepo-architecture) 描述了 cli 包在仓库中的位置。
