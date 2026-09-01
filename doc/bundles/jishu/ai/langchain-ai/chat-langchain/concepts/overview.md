---
type: concept
scope: chat-langchain
name: overview
version: "0.1.0"
source: https://github.com/langchain-ai/chat-langchain
description: Chat LangChain 总览——Managed Deep Agent 文档助手的架构、agent.py 与 identity.py 的角色分工
---

# Chat LangChain 总览

## 什么是 Chat LangChain

Chat LangChain 是 LangChain 官方的文档助手，部署为 **Managed Deep Agent（MDA）**。它帮助用户回答关于 LangChain、LangGraph 和 LangSmith 的问题，通过托管 MCP 连接器搜索官方文档，通过 Pylon 知识库查找已知问题，并在回复前验证链接有效性。

- **项目名称**：agent（pyproject.toml）
- **版本**：0.0.1
- **许可证**：MIT
- **Python 要求**：>=3.11, <3.15
- **核心框架**：LangChain ≥1.0.2、LangGraph ≥1.0.0a4、managed-deepagents ==0.3.0
- **前端**：Next.js（`frontend/` 目录）

## 核心架构：双入口文件

Chat LangChain 的后端由两个 MDA 编译器自动发现的顶层文件定义，二者**互不导入**：

### agent.py — Agent 定义入口

`agent.py` 是 Managed Deep Agent 的主入口，负责声明 agent 的**行为能力**：

```python
agent = define_deep_agent(
    name="docs_agent",
    model="google_genai:gemini-3.5-flash-lite",
    tools=docs_agent_tools,          # 4 个工具
    middleware=docs_agent_middleware, # 6 个中间件
    disable_memory=True,
    metadata=build_docs_agent_trace_metadata(),
)
```

它组装了：

- **工具集**（`docs_agent_tools`）：Pylon 支持文章搜索与内容获取、LangChain 定价查询、链接验证。
- **中间件管道**（`docs_agent_middleware`）：输入截断 → Guardrails → 上下文摘要 → 工具重试 → 模型重试 → 模型降级。
- **模型**：硬编码为 `google_genai:gemini-3.5-flash-lite`，字面量保留以便 `mda deploy` 推断 provider。
- **Trace 元数据**：通过 `build_docs_agent_trace_metadata()` 注入 LangSmith root run。

MCP 文档工具不在 `agent.py` 中声明，而是在 `connectors/mcp.py` 中由 MDA runtime 在编译期附加。

详见 Agent 入口参考。

### identity.py — 身份合约入口

`identity.py` 定义 agent 的**访问控制与租户隔离**，由 MDA 编译器自动发现，取代了旧版手写的 `src/api/auth.py`：

```python
identity = define_identity(
    ingress={"http": {"mode": "validated_token", "providers": _providers()}},
    tenancy="single",
    scoping={"threads": "actor", "memory": "none", "credentials": "agent"},
)
```

它配置了：

- **Ingress 模式**：`validated_token`——浏览器自带 Supabase access token（或 MDA 签发的 guest token），MDA runtime 负责验证。
- **多区域 Supabase**：US/EU/APAC/AWS 四个区域，每个区域一个 `providers.supabase(introspect=True)` provider，通过 `/auth/v1/user` introspection 验证（兼容 legacy HS256 token）。
- **匿名访客**：`providers.guest(ttl="24h", actor_prefix="guest:")` 替代前端的 guest token 签发路由。
- **线程隔离**：`threads: "actor"`——线程按用户 email 或 guest actor id 隔离，替代旧的 `@auth.on.threads` owner 标记。

详见 Identity 合约参考。

## 中间件管道

请求经过六层中间件处理：

| 顺序 | 中间件 | 职责 |
|---|---|---|
| 1 | `IngressGuardsMiddleware` | 截断超过 50,000 字符的用户输入 |
| 2 | `GuardrailsMiddleware` | LLM 判定查询是否与 LangChain 相关，阻断离题查询 |
| 3 | `CustomSummarizationMiddleware` | token 超 130k 时触发摘要，保留 30k 上下文 |
| 4 | `tool_retry_middleware` | 工具调用失败重试（最多 3 次） |
| 5 | `model_retry_middleware` | 模型响应异常重试（最多 2 次） |
| 6 | `model_fallback_middleware` | 主模型降级到 GPT-5.4-nano → Claude Haiku 4.5 |

## 工具与连接器

| 组件 | 来源 | 功能 |
|---|---|---|
| `search_support_articles` | `src/tools/pylon_tools.py` | 搜索 Pylon 支持知识库 |
| `get_support_article_content` | `src/tools/pylon_tools.py` | 获取单篇支持文章内容 |
| `fetch_langchain_pricing` | `src/tools/pricing_tools.py` | 抓取 langchain.com/pricing（1h TTL 缓存） |
| `check_links` | `src/tools/link_check_tools.py` | 验证 URL 有效性，检测 soft-404 |
| LangChain Docs MCP | `connectors/mcp.py` | 托管 MCP 连接器，附加 docs.langchain.com 搜索工具 |
| LangSmith Connector | `connectors/langsmith.py` | 浏览器代理反馈和 trace 查看，API key 不暴露到前端 |

## 文档导航

### 核心概念

- 总览 — 本页：架构、agent.py 与 identity.py 的角色

### 技术参考

- Agent 入口参考 — agent.py 的工具、中间件、模型配置
- Identity 合约参考 — identity.py 的多区域 Supabase、guest provider、scoping 配置

### 事实与洞察

- 事实清单 — 26 条源码事实验证
- 深度洞察 — 双文件合约机制与中间件分层防御策略

## 目录结构

```
chat-langchain/
├── agent.py                    # Agent 定义入口
├── identity.py                 # Identity 合约入口
├── connectors/
│   ├── mcp.py                  # 托管 MCP 文档连接器
│   └── langsmith.py            # LangSmith 反馈/trace 连接器
├── src/
│   ├── agent/config.py         # 模型注册与中间件配置
│   ├── middleware/             # Guardrails、摘要、重试等中间件
│   ├── tools/                  # Pylon、定价、链接检查工具
│   ├── prompts/                # 提示词
│   └── utils/                  # Trace 元数据、prompt provenance
├── frontend/                   # Next.js 前端
└── pyproject.toml
```
