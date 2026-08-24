---
type: bundle
okf_version: "0.2"
scope: chat-langchain
name: chat-langchain
version: "0.1.0"
source: https://github.com/langchain-ai/chat-langchain
description: Chat LangChain——LangChain 官方文档助手，部署为 Managed Deep Agent，基于 LangChain Agents + Guardrails + 多区域 Supabase 身份认证，含 Next.js 前端
---

# Chat LangChain

**Chat LangChain** 是 LangChain 官方的文档助手，部署为 **Managed Deep Agent（MDA）**。它帮助用户回答关于 LangChain、LangGraph 和 LangSmith 的问题，通过托管 MCP 连接器搜索官方文档，通过 Pylon 知识库查找已知问题，并在回复前验证链接有效性。项目同时包含一个 Next.js 前端作为公共聊天 UI。

- **版本**：0.0.1（pyproject.toml）
- **许可证**：MIT
- **Python 要求**：>=3.11, <3.15
- **核心依赖**：LangChain ≥1.0.2、LangGraph ≥1.0.0a4、managed-deepagents ==0.3.0、LangSmith ≥0.8.3
- **前端**：Next.js（`frontend/` 目录）

## 核心特性

- **托管 MCP 文档搜索**：通过 `connectors/mcp.py` 连接 `docs.langchain.com/mcp`，运行时附加官方文档搜索工具。
- **Pylon 支持知识库**：搜索和获取已知问题与解决方案。
- **Guardrails 内容过滤**：使用独立模型（GPT-5.4-nano）判定查询是否偏离 LangChain 主题，阻断离题请求。
- **多区域 Supabase 身份认证**：支持 US/EU/APAC/AWS 四个区域，通过 token introspection 兼容 legacy HS256 token；匿名访客通过 MDA 托管 guest token。
- **模型弹性**：主模型 Gemini 3.5 Flash Lite，降级链 GPT-5.4-nano → Claude Haiku 4.5，配合重试中间件。
- **链接验证**：在回复中包含 URL 前验证有效性，检测 soft-404 页面。
- **LangSmith 可观测性**：全链路 trace，反馈和 trace 查看通过托管连接器代理，API key 不暴露到浏览器。

## 架构概览

Chat LangChain 后端由两个 MDA 编译器自动发现的顶层文件定义：

- **`agent.py`**：声明 agent 的模型、工具、中间件和 trace 元数据（行为能力）。
- **`identity.py`**：声明 HTTP ingress 的 token 验证模式、身份 provider 和线程隔离策略（访问控制）。

两者互不导入，由 MDA 编译器在构建 bundle 时各自发现并组合。

详见 [架构总览](/ai/langchain-ai/chat-langchain/concepts/overview)。

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/langchain-ai/chat-langchain.git
cd chat-langchain

# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API keys

# 本地启动后端
uv run mda dev .

# 本地启动前端（另一个终端）
cd frontend
npm ci
npm run dev:local
```

部署到 Managed Deep Agents：

```bash
mda deploy .
```

## 文档导航

### 核心概念

- [总览](/ai/langchain-ai/chat-langchain/concepts/overview) — 双入口架构、agent.py 与 identity.py 的角色分工、中间件管道

### 技术参考

- [Agent 入口参考](/ai/langchain-ai/chat-langchain/references/agent-entrypoint) — define_deep_agent 配置、工具集、六层中间件、模型弹性
- [Identity 合约参考](/ai/langchain-ai/chat-langchain/references/identity-contract) — 多区域 Supabase introspection、guest provider、actor scoping

### 事实与洞察

- [事实清单](/ai/langchain-ai/chat-langchain/spec/facts) — 26 条源码事实验证（含文件路径行号）
- [深度洞察](/ai/langchain-ai/chat-langchain/spec/insights) — 双文件合约机制、中间件分层防御与模型弹性策略

## 目录结构

```
chat-langchain/
├── spec/
│   ├── facts.md           # 源码事实验证清单
│   └── insights.md        # 设计决策与深度洞察
├── concepts/              # 核心概念（1 篇）
│   ├── overview.md
│   └── index.md
├── references/            # 技术参考（2 篇）
│   ├── agent-entrypoint.md
│   ├── identity-contract.md
│   └── index.md
├── log.md                 # 变更日志
└── index.md               # 本文件
```

```{toctree}
:hidden:

concepts/index
references/index
spec/facts
spec/insights
log
```
