---
title: libs/cli/README.md
type: reference
bundle: /datawhale/deepagents
source_path: libs/cli/README.md
source_url: https://github.com/datawhalechina/deepagents/blob/main/libs/cli/README.md
---

# libs/cli/README.md 引用

Deep Agents CLI 部署工具的使用文档。

## 核心内容

- **定位**：部署 CLI，仅包含 init/deploy/agents/mcp-servers 子命令（交互式 REPL 已拆分到 deepagents-code）
- **安装**：`uv tool install deepagents-cli`，需要 LANGSMITH_API_KEY
- **使用流程**：`deepagents init` 脚手架 → `deepagents mcp-servers add` 注册 MCP 服务器 → 编辑 tools.json → `deepagents deploy` 部署
- **项目布局**：agent.json（配置）、AGENTS.md（系统提示）、tools.json（工具）、skills/、subagents/
- **后端配置**：默认 state 后端，可配置 sandbox 后端（scope: thread/agent，policy_ids，TTL）
- **agents 命令**：list、get、delete
- **mcp-servers 命令**：list、add、get、tools、update、delete、connect（OAuth）
- **标识符解析**：get/update/delete/connect 接受 id、精确名称或 URL

## 相关概念

- [CLI部署工具链](/ai/datawhale/deepagents/concepts/cli-toolchain)
