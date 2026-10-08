---
type: reference
scope: chat-langchain
name: agent-entrypoint
version: "0.1.0"
source: https://github.com/langchain-ai/chat-langchain
description: Chat LangChain agent.py 入口参考——define_deep_agent 配置、工具集、中间件管道、模型设置
---

# Agent 入口参考

本文档描述 `agent.py` 中 `define_deep_agent(...)` 的完整配置。

## define_deep_agent 调用

```python
agent = define_deep_agent(
    name="docs_agent",
    model="google_genai:gemini-3.5-flash-lite",
    tools=docs_agent_tools,
    middleware=docs_agent_middleware,
    disable_memory=True,
    metadata=build_docs_agent_trace_metadata(),
)
```

| 参数 | 值 | 说明 |
|---|---|---|
| `name` | `"docs_agent"` | Agent 名称，用于 LangSmith trace 标识 |
| `model` | `"google_genai:gemini-3.5-flash-lite"` | 主模型，字面量硬编码以便 `mda deploy` 推断 provider 包并预检 `GOOGLE_API_KEY` |
| `tools` | `docs_agent_tools` | 4 个工具（见下方） |
| `middleware` | `docs_agent_middleware` | 6 个中间件（见下方） |
| `disable_memory` | `True` | 公共应用尚无跨线程用户记忆，MDA managed memory 关闭 |
| `metadata` | `build_docs_agent_trace_metadata()` | LangSmith root run 元数据（source_type、prompt provenance、agent version） |

## 工具集（docs_agent_tools）

| 工具 | 来源模块 | 功能 |
|---|---|---|
| `search_support_articles` | `src.tools.pylon_tools` | 搜索 Pylon 支持知识库文章 |
| `get_support_article_content` | `src.tools.pylon_tools` | 获取单篇支持文章全文 |
| `fetch_langchain_pricing` | `src.tools.pricing_tools` | 抓取 langchain.com/pricing，1 小时 TTL 缓存 |
| `check_links` | `src.tools.link_check_tools` | 验证 URL，支持 soft-404 检测（docs.langchain.com 等域名） |

MCP 文档工具（LangChain 官方文档搜索）不在此列表中，由 `connectors/mcp.py` 在编译期附加。

## 中间件管道（docs_agent_middleware）

按执行顺序排列：

### 1. IngressGuardsMiddleware

```python
IngressGuardsMiddleware()
```

来自 `src.middleware.ingress_guards_middleware`。在 agent 入口截断超过 `MAX_MESSAGE_CHARS = 50_000` 字符的用户消息，保留非文本 content block。取代旧 `auth.py` 的 `validate_inputs`。

### 2. GuardrailsMiddleware

```python
GuardrailsMiddleware(
    model=GUARDRAILS_MODEL.id,        # "openai:gpt-5.4-nano"
    fallback_model=DEFAULT_MODEL.id,  # "google_genai:gemini-3.5-flash-lite"
    block_off_topic=True,
)
```

来自 `src.middleware.guardrails_middleware`。使用独立模型（GPT-5.4-nano）判定查询是否与 LangChain 相关，阻断离题查询。1% 放行查询采样到 LangSmith 数据集 `Chat-LangChain-Guardrails-Samples`。

### 3. CustomSummarizationMiddleware

```python
CustomSummarizationMiddleware(
    model=DEFAULT_MODEL.id,
    summary_model=summarization_model,
    trigger=("tokens", 130_000),
    keep=("tokens", 30_000),
    summary_prompt=context_summary_prompt,
    trim_tokens_to_summarize=None,
)
```

来自 `src.middleware.summarization_middleware`。当对话 token 数超过 130,000 时触发摘要，保留最近 30,000 token。摘要使用独立的 retry/fallback 模型链（`summarization_model`），摘要失败返回错误字符串但不中断对话。

### 4. tool_retry_middleware

```python
tool_retry_middleware  # ToolRetryMiddleware(max_attempts=3)
```

来自 `src.agent.config`。工具调用失败时最多重试 3 次。

### 5. model_retry_middleware

```python
model_retry_middleware  # ModelRetryMiddleware(max_retries=MAX_RETRIES)
```

来自 `src.agent.config`。`MAX_RETRIES` 默认 2（可通过 `MODEL_MAX_RETRIES` 环境变量调整）。对可重试的 finish reason（如 length）触发 `MalformedResponseError` 并重试。

### 6. model_fallback_middleware

```python
model_fallback_middleware  # ModelFallbackMiddleware("openai:gpt-5.4-nano", "anthropic:claude-haiku-4-5-20251001")
```

来自 `src.agent.config`。主模型（Gemini）不可用时降级链：GPT-5.4-nano → Claude Haiku 4.5。

## Trace 元数据

`build_docs_agent_trace_metadata()`（来自 `src.utils.trace_root_metadata`）返回字典：

- `source_type`: `"Chat-LangChain"`
- prompt provenance 字段（来自 `get_prompt_provenance("docs_agent")`）
- `LANGSMITH_AGENT_VERSION`: 仅当 `LANGCHAIN_REVISION_ID` 或 `LANGSMITH_HOST_REVISION_ID` 环境变量存在时设置

元数据通过 `define_deep_agent(metadata=...)` 在编译期注入，确保落在 LangSmith root run 上（中间件内的 `before_agent` span 无法可靠更新 root run）。

## 相关文档

- Identity 合约参考
- 架构总览
- 事实清单
