---
type: spec
title: "Chat LangChain 事实清单"
---

# Chat LangChain 事实清单

## 项目元信息

F-001: 文件 `pyproject.toml` 第1-10行，项目名称为 `agent`，版本 `0.0.1`，描述为 "LangChain docs agent deployed as a Managed Deep Agent."，作者为 William Fu-Hinthorn，许可证 MIT，要求 Python `>=3.11,<3.15`。

F-002: 文件 `pyproject.toml` 第11-25行，核心依赖包含 `langchain>=1.0.2`、`langgraph>=1.0.0a4`、`langchain-anthropic>=0.1.23`、`langchain-openai>=0.3.0`、`langchain-google-genai>=4.0.0`、`langsmith>=0.8.3`、`managed-deepagents==0.3.0` 等。

F-003: 文件 `README.md` 第9-17行，项目定位为 "A documentation assistant deployed as a Managed Deep Agent"，基于 Managed Deep Agents、LangChain Agents 和 Guardrails 构建，`frontend/` 目录包含 Next.js 前端。

## Agent 入口（agent.py）

F-004: 文件 `agent.py` 第3行，从 `managed_deepagents` 导入 `define_deep_agent`；第53-64行调用 `define_deep_agent(name="docs_agent", model="google_genai:gemini-3.5-flash-lite", tools=docs_agent_tools, middleware=docs_agent_middleware, disable_memory=True, metadata=build_docs_agent_trace_metadata())` 创建全局 `agent` 对象。

F-005: 文件 `agent.py` 第24-29行，`docs_agent_tools` 列表包含四个工具：`search_support_articles`、`get_support_article_content`、`fetch_langchain_pricing`、`check_links`，分别来自 `src.tools.pylon_tools`、`src.tools.pricing_tools`、`src.tools.link_check_tools`。

F-006: 文件 `agent.py` 第31-51行，`docs_agent_middleware` 列表按顺序包含六个中间件：`IngressGuardsMiddleware()`、`GuardrailsMiddleware(model=GUARDRAILS_MODEL.id, fallback_model=DEFAULT_MODEL.id, block_off_topic=True)`、`CustomSummarizationMiddleware(model=DEFAULT_MODEL.id, summary_model=summarization_model, trigger=("tokens", 130_000), keep=("tokens", 30_000), summary_prompt=context_summary_prompt, trim_tokens_to_summarize=None)`、`tool_retry_middleware`、`model_retry_middleware`、`model_fallback_middleware`。

F-007: 文件 `agent.py` 第57行，agent 模型字面量硬编码为 `"google_genai:gemini-3.5-flash-lite"`，注释说明保留字面量以便 `mda deploy` 推断 provider 包并预检 `GOOGLE_API_KEY`；第62行 `disable_memory=True`，注释说明公共应用尚无跨线程用户记忆。

## Identity 合约（identity.py）

F-008: 文件 `identity.py` 第1-15行，模块 docstring 说明该文件由编译器自动发现（`agent.py` 从不导入），取代手写的 `src/api/auth.py`；提供 `validated_token` ingress、多区域 Supabase 支持、`threads: "actor"` 作用域。

F-009: 文件 `identity.py` 第26-31行，`_REGION_ENV` 字典映射四个区域标签到环境变量元组：`"us" -> ("SUPABASE_URL", "SUPABASE_ANON_KEY")`、`"eu" -> ("SUPABASE_EU_URL", "SUPABASE_EU_ANON_KEY")`、`"apac" -> ("SUPABASE_APAC_URL", "SUPABASE_APAC_ANON_KEY")`、`"aws" -> ("SUPABASE_AWS_URL", "SUPABASE_AWS_ANON_KEY")`。

F-010: 文件 `identity.py` 第34-55行，函数 `_providers() -> list[dict]` 遍历 `_REGION_ENV`，对每个配置了 URL 的区域调用 `providers.supabase(url=base.rstrip("/"), introspect=True)`，设置 `provider["id"] = f"supabase-{region}"` 和 introspect headers `{"apikey": "${<key_env>}"}`；最后追加 `providers.guest(ttl="24h", actor_prefix="guest:")` 匿名访客 provider。

F-011: 文件 `identity.py` 第58-62行，`identity = define_identity(ingress={"http": {"mode": "validated_token", "providers": _providers()}}, tenancy="single", scoping={"threads": "actor", "memory": "none", "credentials": "agent"})`。

## 模型配置（src/agent/config.py）

F-012: 文件 `src/agent/config.py` 第28-37行，`@dataclass class ModelConfig` 包含字段 `id: str`、`name: str`、`provider: str`、`api_key_env: str`、`description: str | None = None`。

F-013: 文件 `src/agent/config.py` 第40-65行，`MODELS` 字典注册三个模型：`"claude-haiku-4.5"`（id=`anthropic:claude-haiku-4-5-20251001`）、`"gpt-5.4-nano"`（id=`openai:gpt-5.4-nano`）、`"gemini-3.5-flash-lite"`（id=`google_genai:gemini-3.5-flash-lite`）。

F-014: 文件 `src/agent/config.py` 第68-75行，`DEFAULT_MODEL = MODELS["gemini-3.5-flash-lite"]`，`GUARDRAILS_MODEL = MODELS["gpt-5.4-nano"]`，`FALLBACK_MODELS = [MODELS["gpt-5.4-nano"], MODELS["claude-haiku-4.5"]]`。

F-015: 文件 `src/agent/config.py` 第98行，`MAX_RETRIES = int(os.getenv("MODEL_MAX_RETRIES", "2"))`；第135-138行，创建 `model_retry_middleware = ModelRetryMiddleware(max_retries=MAX_RETRIES)`、`tool_retry_middleware = ToolRetryMiddleware(max_attempts=3)`、`model_fallback_middleware = ModelFallbackMiddleware(*[m.id for m in FALLBACK_MODELS])`。

## 中间件

F-016: 文件 `src/middleware/ingress_guards_middleware.py` 第23行，`MAX_MESSAGE_CHARS = 50_000`；第26-42行，类 `IngressGuardsMiddleware(AgentMiddleware)` 的 `before_agent` 方法从后向前查找最新 human 消息，超过 50,000 字符则截断并返回更新后的 messages。

F-017: 文件 `src/middleware/guardrails_middleware.py` 第30-33行，`GUARDRAILS_DATASET_NAME = "Chat-LangChain-Guardrails-Samples"`、`ALLOWED_SAMPLE_RATE = 0.01`（1% 放行查询采样到数据集）、`GUARDRAILS_MAX_RETRIES = 2`、`GUARDRAILS_TIMEOUT_SECONDS = 10`。

F-018: 文件 `src/middleware/summarization_middleware.py` 第11-37行，类 `CustomSummarizationMiddleware(SummarizationMiddleware)` 接收 `summary_model: Runnable`，`_create_summary` 方法调用 `self.summary_model.invoke(...)` 生成摘要，异常时返回 `"Error generating summary: {e!s}"`。

## 工具

F-019: 文件 `src/tools/link_check_tools.py` 第14-17行，`DEFAULT_TIMEOUT = 10.0`、`MAX_REDIRECTS = 5`、`USER_AGENT = "LangChain-LinkChecker/1.0"`、`CONTENT_CHECK_BYTES = 8192`；第20-25行，`SOFT_404_DOMAINS` 集合包含 `docs.langchain.com`、`python.langchain.com`、`js.langchain.com`、`support.langchain.com`。

F-020: 文件 `src/tools/pricing_tools.py` 第13-14行，`PRICING_URL = "https://www.langchain.com/pricing"`、`TIMEOUT = 15.0`、`USER_AGENT = "LangChain-SupportAgent/1.0"`；第21行 `_CACHE_TTL_SECONDS = 3600`（1 小时进程内 TTL 缓存）。

F-021: 文件 `src/tools/pylon_tools.py` 第19行，`PYLON_API_BASE_URL = "https://api.usepylon.com"`；第22-35行，`_get_kb_id()` 和 `_get_api_key()` 分别从环境变量 `PYLON_KB_ID` 和 `PYLON_API_KEY` 读取，缺失时抛出 `ValueError`。

## 连接器

F-022: 文件 `connectors/mcp.py` 第5-13行，`connector = define_mcp_servers(prefix_tool_name_with_server_name=False, mcp_servers={"langchain-docs": {"transport": "http", "url": "https://docs.langchain.com/mcp"}})`，声明托管 MCP 文档连接器。

F-023: 文件 `connectors/langsmith.py` 第20-53行，`connector = langsmith.connector(...)` 声明两个浏览器可见能力：`langsmith:chat-feedback`（actions: create/update/delete，one_per_actor=True，max_comment_chars=2000）和 `langsmith:trace-viewer`（actions: read/share，include 含 token/cost/timing 字段）。

## Trace 元数据

F-024: 文件 `src/utils/trace_root_metadata.py` 第14行，`_PROVENANCE_GRAPH_ID = "docs_agent"`；第17-31行，函数 `build_docs_agent_trace_metadata(*, graph_id="docs_agent") -> dict[str, str]` 返回包含 `source_type: "Chat-LangChain"` 和 prompt provenance 的字典，若环境变量 `LANGCHAIN_REVISION_ID` 或 `LANGSMITH_HOST_REVISION_ID` 存在则附加 `LANGSMITH_AGENT_VERSION`。

## 环境变量

F-025: 文件 `.env.example` 第6-9行，支持四家 LLM provider 的 API key：`ANTHROPIC_API_KEY`、`OPENAI_API_KEY`、`GOOGLE_API_KEY`、`BASETEN_API_KEY`；第14-15行 Pylon 配置 `PYLON_API_KEY`、`PYLON_KB_ID`；第20-22行 LangSmith 配置 `LANGCHAIN_TRACING_V2=true`、`LANGSMITH_API_KEY`、`LANGSMITH_PROJECT=docs-agent`。

F-026: 文件 `.env.example` 第50-57行，identity.py 使用的四组 Supabase 环境变量（无 `NEXT_PUBLIC_` 前缀）：`SUPABASE_URL/ANON_KEY`、`SUPABASE_EU_*`、`SUPABASE_APAC_*`、`SUPABASE_AWS_*`；第62行 `MDA_GUEST_SIGNING_KEY` 供托管 guest provider 签发/验证 HS256 guest token。
