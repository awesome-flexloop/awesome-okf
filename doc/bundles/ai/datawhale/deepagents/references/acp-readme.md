---
title: libs/acp/README.md
type: reference
bundle: /datawhale/deepagents
source_path: libs/acp/README.md
source_url: https://github.com/datawhalechina/deepagents/blob/main/libs/acp/README.md
---

# libs/acp/README.md 引用

Deep Agents ACP 集成的使用指南。

## 核心内容

- **定位**：Agent Client Protocol 连接器，在 Zed 等支持 ACP 的编辑器中运行 Python Deep Agent
- **快速开始**：克隆仓库、`uv sync --group examples`、配置 `.env`（ANTHROPIC_API_KEY、可选 LangSmith tracing）、在 Zed settings.json 中配置 agent_servers
- **自定义 Agent**：`uv add deepagents-acp`，使用 `AgentServerACP(agent)` 包装，`run_agent(server)` 启动
- **会话持久化**：`AgentServerACP(agent, load_sessions=True)`，需要持久化 checkpointer
- **dcode --acp**：`uv tool install -U deepagents-code --with deepagents-acp`，Zed 配置 command 为 `dcode` args 为 `["--acp"]`
- **模型切换**：通过 Agent 工厂和 models 列表支持会话中动态切换模型
- **Toad 启动器**：`uv tool install -U batrachian-toad --python 3.14`，`toad acp "python server.py" .`

## 相关概念

- [ACP协议集成](/ai/datawhale/deepagents/concepts/acp-protocol)
