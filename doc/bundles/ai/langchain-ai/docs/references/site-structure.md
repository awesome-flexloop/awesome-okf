---
type: reference
title: LangChain 文档站结构索引
description: src/ 目录下主要 MDX 文件、子目录与构建管道的结构化索引
tags: [langchain, docs, structure, mdx, mintlify]
sources:
  - id: src-tree
    resource: /langchain-ai/docs/src
    title: src/ 源码目录
  - id: pipeline-tree
    resource: /langchain-ai/docs/pipeline
    title: pipeline/ 构建管道
  - id: scripts-tree
    resource: /langchain-ai/docs/scripts
    title: scripts/ 辅助脚本
generated:
  by: reference_agent/trae-solo
  at: 2026-08-23
status: stable
---

# LangChain 文档站结构索引

本文档索引 `src/` 目录下的主要 MDX 文件和目录，以及 `pipeline/` 和 `scripts/` 的代码结构。所有路径相对于仓库根目录 `d:/spaces/SpecWeave/external/libs/ai/langchain-ai/docs/`。

## 仓库顶层结构

| 路径 | 类型 | 说明 |
|------|------|------|
| `src/` | 目录 | 所有手写文档内容 |
| `pipeline/` | 目录 | Python 构建管道与预处理器 |
| `scripts/` | 目录 | 辅助工具脚本 |
| `build/` | 目录 | Mintlify 构建输出（禁止编辑） |
| `src/docs.json` | 文件 | Mintlify 站点配置与导航（唯一导航真相源） |
| `pyproject.toml` | 文件 | Python 项目配置与依赖 |
| `package.json` | 文件 | npm 依赖（仅 `@langchain/docs-sandbox`） |
| `Makefile` | 文件 | 构建命令入口 |
| `AGENTS.md` / `CLAUDE.md` | 文件 | AI 代理贡献指南（内容同步） |
| `.github/workflows/` | 目录 | CI/CD 工作流 |
| `packages.yml` | 文件 | 包下载量数据源 |

## src/ 根目录文件

| 文件 | 说明 |
|------|------|
| `src/index.mdx` | 首页，自定义布局（`mode: "custom"`），CardGroup 导航 |
| `src/agent-lifecycle.mdx` | Agent 开发生命周期概览 |
| `src/build-overview.mdx` | 构建概览 |
| `src/playground.mdx` | Playground 页面 |
| `src/use-these-docs.mdx` | 文档使用指南 |
| `src/docs.json` | Mintlify 配置与导航 |
| `src/style.css` | 自定义 CSS |
| `src/language-toggle.js` | 语言切换脚本 |
| `src/integration-downloads-table.js` | 集成下载量表格组件 |
| `src/.codespellignore` | codespell 忽略词表 |

## src/ 根目录子目录

| 目录 | 文件数（约） | 说明 |
|------|-------------|------|
| `src/langsmith/` | 474 MDX | LangSmith 商业产品文档（扁平组织） |
| `src/langsmith/fleet/` | 25 MDX | LangSmith Fleet 无代码 Agent 平台文档 |
| `src/langsmith/images/` | 200+ 图片 | LangSmith 文档截图与图示 |
| `src/oss/` | 600+ MDX | 开源框架文档（LangChain/LangGraph/Deep Agents） |
| `src/snippets/` | 1047 MDX | 可复用 MDX 片段 |
| `src/code-samples/` | 404 源文件 | 可执行代码示例（Python/TypeScript/Go） |
| `src/images/` | 100+ 资源 | 品牌 Logo、提供商图标、通用图片 |
| `src/fonts/` | 16 woff2 | TWK Lausanne 字体（7 字重 × 正斜体） |
| `src/.mintlify/skills/` | 3 SKILL.md | Mintlify AI 技能定义 |
| `src/.well-known/` | 1 文件 | security.txt |

## src/langsmith/ 主要页面

LangSmith 文档扁平组织在 `src/langsmith/` 下，按 `docs.json` 中的 7 个标签页逻辑分组：

**Get started 标签页：**
- `index` 对应导航入口，实际页面包括 `admin.mdx`、`auth.mdx`、`billing.mdx`、`cloud.mdx`、`enterprise.mdx`、`faq.mdx` 等。

**Observability 标签页：**
- 核心页面：`tracing` 相关（由 `agent-lifecycle.mdx` 等顶层页面和 langsmith 下的追踪配置页组成）、`alerts.mdx`、`caching.mdx`、`chat-observability.mdx`、`configurable-logs.mdx`、`export-traces.mdx`、`insights.mdx`、`cost-tracking.mdx`、`dashboards.mdx` 等。

**Evaluation 标签页：**
- `evaluation.mdx`、`evaluation-concepts.mdx`、`evaluation-types.mdx`、`evaluation-quickstart.mdx`、`evaluators.mdx`、`datasets` 相关页面、`annotation-queues.mdx`、`chat-evaluation.mdx` 等。

**Prompt engineering 标签页：**
- `create-a-prompt.mdx`、`prompts` 相关教程页面。

**Agent deployment 标签页：**
- `deployment.mdx`、`deployment-quickstart.mdx`、`agent-server.mdx`、`agent-server-overview.mdx`、`agent-server-scale.mdx`、`custom-apps.mdx`、`custom-middleware.mdx`、`custom-routes.mdx`、`engine.mdx`、`engine-overview.mdx` 等。

**Platform setup 标签页：**
- `hybrid.mdx`、`byoc.mdx`、`aws-self-hosted.mdx`、`gcp-self-hosted.mdx`、`azure-self-hosted.mdx`、`kubernetes.mdx`、`govern.mdx`、`encryption.mdx`、`audit-logs.mdx` 等。

**Reference 标签页：**
- `api-ref-control-plane.mdx`、`changelog.mdx`、`agent-server-openapi.json` 等。

## src/langsmith/fleet/ 文件列表

| 文件 | 说明 |
|------|------|
| `index.mdx` | Fleet 首页 |
| `quickstart.mdx` | 快速入门 |
| `essentials.mdx` | 核心概念 |
| `agent-identity.mdx` | Agent 身份 |
| `auth-format.mdx` | 认证格式 |
| `channels.mdx` | 渠道 |
| `code.mdx` | 代码 |
| `skills.mdx` | 技能 |
| `tools.mdx` | 工具 |
| `webhooks.mdx` | Webhooks |
| `schedules.mdx` | 调度 |
| `templates.mdx` | 模板 |
| `slack-app.mdx` | Slack 应用 |
| `teams-app.mdx` | Teams 应用 |
| `salesforce.mdx` | Salesforce 集成 |
| `mcp-framework.mdx` | MCP 框架 |
| `remote-mcp-servers.mdx` | 远程 MCP 服务器 |
| `computer-use.mdx` | 计算机使用 |
| `arcade.mdx` | Arcade 集成 |
| `comparison.mdx` | 对比 |
| `manage-agent-settings.mdx` | 管理 Agent 设置 |
| `access-and-oversight.mdx` | 访问与监督 |
| `workspace-admin.mdx` | 工作区管理 |
| `self-hosted-link.mdx` | 自托管链接 |
| `changelog.mdx` | 更新日志 |

## src/oss/ 目录结构

### src/oss/langchain/（32 个 MDX）

LangChain 框架核心文档：

| 文件 | 说明 |
|------|------|
| `overview.mdx` | 概述 |
| `install.mdx` | 安装 |
| `quickstart.mdx` | 快速入门 |
| `philosophy.mdx` | 设计哲学 |
| `agents.mdx` | Agent 概念 |
| `tools.mdx` | 工具 |
| `models.mdx` | 模型 |
| `messages.mdx` | 消息 |
| `mcp.mdx` | MCP 集成 |
| `streaming.mdx` | 流式传输 |
| `structured-output.mdx` | 结构化输出 |
| `retrieval.mdx` | 检索 |
| `knowledge-base.mdx` | 知识库 |
| `short-term-memory.mdx` | 短期记忆 |
| `long-term-memory.mdx` | 长期记忆 |
| `context-engineering.mdx` | 上下文工程 |
| `guardrails.mdx` | 护栏 |
| `human-in-the-loop.mdx` | 人机交互 |
| `deploy.mdx` | 部署 |
| `observability.mdx` | 可观测性 |
| `runtime.mdx` | 运行时 |
| `event-streaming.mdx` | 事件流 |
| `studio.mdx` | LangGraph Studio |
| `ui.mdx` | UI 组件 |
| `voice-agent.mdx` | 语音 Agent |
| `sql-agent.mdx` | SQL Agent |
| `deep-agent-from-scratch.mdx` | 从零构建 Deep Agent |
| `component-architecture.mdx` | 组件架构 |
| `academy.mdx` | LangChain Academy |
| `get-help.mdx` | 获取帮助 |
| `changelog-py.mdx` | Python 更新日志 |
| `changelog-js.mdx` | JS 更新日志 |

### src/oss/langgraph/（34 个 MDX + 子目录）

LangGraph 框架核心文档：

| 文件 | 说明 |
|------|------|
| `overview.mdx` | 概述 |
| `install.mdx` | 安装 |
| `quickstart.mdx` | 快速入门 |
| `graph-api.mdx` | Graph API |
| `functional-api.mdx` | 函数式 API |
| `use-graph-api.mdx` | 使用 Graph API |
| `use-functional-api.mdx` | 使用函数式 API |
| `choosing-apis.mdx` | API 选择指南 |
| `pregel.mdx` | Pregel 模型 |
| `workflows-agents.mdx` | 工作流与 Agent |
| `add-memory.mdx` | 添加记忆 |
| `persistence.mdx` | 持久化 |
| `checkpointers.mdx` | 检查点 |
| `stores.mdx` | 存储 |
| `interrupts.mdx` | 中断 |
| `use-subgraphs.mdx` | 子图 |
| `use-time-travel.mdx` | 时间旅行 |
| `streaming.mdx` | 流式传输 |
| `event-streaming.mdx` | 事件流 |
| `fault-tolerance.mdx` | 容错 |
| `test.mdx` | 测试 |
| `deploy.mdx` | 部署 |
| `local-server.mdx` | 本地服务器 |
| `studio.mdx` | Studio |
| `observability.mdx` | 可观测性 |
| `agentic-rag.mdx` | Agentic RAG |
| `sql-agent.mdx` | SQL Agent |
| `application-structure.mdx` | 应用结构 |
| `case-studies.mdx` | 案例研究 |
| `thinking-in-langgraph.mdx` | LangGraph 思维模式 |
| `ui.mdx` | UI |
| `backward-compatibility.mdx` | 向后兼容 |
| `changelog-py.mdx` | Python 更新日志 |
| `changelog-js.mdx` | JS 更新日志 |

子目录：
- `errors/`：6 个错误码文档（`GRAPH_RECURSION_LIMIT.mdx`、`INVALID_CHAT_HISTORY.mdx`、`INVALID_CONCURRENT_GRAPH_UPDATE.mdx`、`INVALID_GRAPH_NODE_RETURN_VALUE.mdx`、`MISSING_CHECKPOINTER.mdx`、`MULTIPLE_SUBGRAPHS.mdx`）
- `frontend/`：前端文档（`overview.md`、`custom-stream-channels.mdx`、`graph-execution.mdx`）

### src/oss/deepagents/（36 个顶层 MDX + 3 个子目录）

Deep Agents 框架文档，顶层文件包括：`overview.mdx`、`quickstart.mdx`、`customization.mdx`、`models.mdx`、`comparison.mdx`、`tools.mdx`、`subagents.mdx`、`dynamic-subagents.mdx`、`async-subagents.mdx`、`skills.mdx`、`memory.mdx`、`retrieval.mdx`、`context-engineering.mdx`、`profiles.mdx`、`backends.mdx`、`permissions.mdx`、`sandboxes.mdx`、`interpreters.mdx`、`multimodal.mdx`、`event-streaming.mdx`、`streaming.mdx`、`human-in-the-loop.mdx`、`rubric.mdx`、`fault-tolerance.mdx`、`going-to-production.mdx`、`mcp.mdx`、`acp.mdx`、`a2a.mdx`、`rag.mdx`、`deep-research.mdx`、`data-analysis.mdx`、`content-builder.mdx`、`openwiki.mdx`、`code-link.mdx`、`changelog-py.mdx`、`changelog-js.mdx`。

子目录：
- `code/`（16 个 MDX）：`dcode` CLI 文档——`overview.mdx`、`quickstart.mdx`、`configuration.mdx`、`config-file.mdx`、`credentials.mdx`、`providers.mdx`、`plugins.mdx`、`hooks.mdx`、`mcp-tools.mdx`、`subagents.mdx`、`memory-and-skills.mdx`、`goals-and-rubrics.mdx`、`approval-modes.mdx`、`remote-sandboxes.mdx`、`cli-reference.mdx`、`changelog.mdx`
- `frontend/`（4 个 MDX）：`overview.mdx`、`sandbox.mdx`、`subagent-streaming.mdx`、`todo-list.mdx`
- `cli/`：仅含 `.gitkeep`（占位）

### src/oss/python/integrations/（21 个组件子目录）

Python 集成按组件类型组织，每个组件目录含 `index.mdx` 和各提供商页面：

| 组件目录 | 说明 | 代表文件 |
|---------|------|---------|
| `chat/` | 聊天模型 | `openai.mdx`、`anthropic.mdx`、`google_vertex_ai.mdx`、`bedrock.mdx`、`TEMPLATE.mdx` |
| `embeddings/` | 嵌入模型 | `openai.mdx`、`cohere.mdx`、`huggingfacehub.mdx`、`voyageai.mdx` |
| `vectorstores/` | 向量存储 | `pgvector.mdx`、`chroma.mdx`、`pinecone.mdx`、`redis.mdx`、`qdrant.mdx`、`weaviate.mdx` |
| `tools/` | 工具 | `tavily_search.mdx`、`mcp_toolbox.mdx`、`google_search.mdx`、`sql.mdx` |
| `retrievers/` | 检索器 | `bedrock.mdx`、`cohere.mdx`、`pinecone_reranker.mdx`、`TEMPLATE.mdx` |
| `document_loaders/` | 文档加载器 | `google_drive.mdx`、`azure_blob_storage.mdx`、`unstructured_file.mdx` |
| `document_transformers/` | 文档转换器 | `cross_encoder_reranker.mdx`、`voyageai-reranker.mdx` |
| `llms/` | 传统 LLM | `openai.mdx`、`anthropic.mdx`、`huggingface_pipelines.mdx` |
| `middleware/` | 中间件 | `anthropic.mdx`、`aws.mdx`、`openai.mdx`、`TEMPLATE.mdx` |
| `providers/` | 提供商总览 | `overview.mdx`、`all_providers.mdx`、`openai.mdx`、`anthropic.mdx` |
| `stores/` | 键值存储 | `in_memory.mdx`、`file_system.mdx`、`astradb.mdx` |
| `sandboxes/` | 沙箱 | `langsmith.mdx`、`daytona.mdx`、`modal.mdx`、`aws.mdx` |
| `graphs/` | 图数据库 | `neo4j_cypher.mdx`、`amazon_neptune_open_cypher.mdx` |
| `caches/` | 缓存 | `redis_llm_caching.mdx` |
| `callbacks/` | 回调 | `google_bigquery.mdx`、`agentsystems_notary.mdx` |
| `agents/` | Agent | `sap_hana_sparql_qa_agent.mdx` |
| `chains/` | 链 | `sap_hana_sparql_qa_chain.mdx` |
| `chat_message_histories/` | 聊天历史 | `cockroachdb.mdx` |
| `checkpointers/` | 检查点 | `index.mdx` |
| `long-term-memory/` | 长期记忆 | `index.mdx` |
| `splitters/` | 分割器 | `markdown_header_metadata_splitter.mdx`、`recursive_json_splitter.mdx` |

### src/oss/javascript/integrations/（17 个组件子目录）

TypeScript/JavaScript 集成，结构与 Python 对应，组件目录包括：`chat/`、`embeddings/`、`vectorstores/`、`tools/`、`retrievers/`、`document_loaders/`、`document_transformers/`、`document_compressors/`、`llms/`、`llm_caching/`、`middleware/`、`providers/`、`stores/`、`sandboxes/`、`graphs/`、`agents/`、`chains/`。

### src/oss/ 其他子目录

| 目录 | 文件 | 说明 |
|------|------|------|
| `concepts/` | 4 MDX | `context.mdx`、`memory.mdx`、`products.mdx`、`providers-and-models.mdx` |
| `contributing/` | 8 MDX | `overview.mdx`、`documentation.mdx`、`code.mdx`、`implement-langchain.mdx`、`integrations-langchain.mdx`、`publish-langchain.mdx`、`standard-tests-langchain.mdx`、`comarketing.mdx` |
| `reference/` | 9 MDX | `overview.mdx`、`langchain-python.mdx`、`langchain-javascript.mdx`、`langgraph-python.mdx`、`langgraph-javascript.mdx`、`deepagents-python.mdx`、`deepagents-javascript.mdx`、`integrations-python.mdx`、`integrations-javascript.mdx`（均链接到 reference.langchain.com） |
| `integrations/` | 共享 | `backends/`、`providers/`、`splitters/` 等共享集成内容 |
| `images/` | 200+ | OSS 文档专用图片和视频 |
| `python/migrate/` | 3 MDX | 迁移指南：`langchain-v1.mdx`、`langgraph-v1.mdx`、`langgraph-supervisor.mdx` |
| `python/releases/` | 3 MDX | 发行说明：`changelog.mdx`、`langchain-v1.mdx`、`langgraph-v1.mdx` |
| `javascript/migrate/` | 2 MDX | 迁移指南：`langchain-v1.mdx`、`langgraph-v1.mdx` |
| `javascript/releases/` | 3 MDX | 发行说明：`changelog.mdx`、`langchain-v1.mdx`、`langgraph-v1.mdx` |

## src/snippets/ 片段目录

| 子目录 | 说明 |
|--------|------|
| `snippets/code-samples/` | 代码示例片段（约 600+ 文件），按 `<topic>-<variant>-<lang>.mdx` 命名 |
| `snippets/langsmith/` | LangSmith 专用片段（含 `smithdb-migration/` 子目录） |
| `snippets/oss/` | OSS 文档片段，含下载量表格、Studio 片段、部署片段等 |
| `snippets/` 根目录 | 通用片段（如 `chat-model-tabs.mdx`、`vectorstore-tabs-py.mdx`、`trace-with-openai.mdx`） |

## src/code-samples/ 可执行示例

| 子目录/文件 | 说明 |
|------------|------|
| `code-samples/langchain/` | LangChain 示例（`rag.py`、`rag.ts`、`sql-agent.py`、`sql-agent.ts`） |
| `code-samples/deepagents/` | Deep Agents 示例（`tools.py`、`tools.ts`、`skills.py`、`streaming.py` 等） |
| `code-samples/conftest.py` | pytest 配置 |
| `code-samples/package.json` | npm 依赖 |
| `code-samples/go.mod` / `go.sum` | Go 模块 |
| `code-samples/profile.yaml` | 示例配置 |

## pipeline/ 构建管道结构

```
pipeline/
├── __init__.py
├── __main__.py              # python -m pipeline 入口
├── cli.py                   # CLI 入口（docs dev/build/mv/migrate）
├── commands/
│   ├── build.py             # build 命令实现
│   └── dev.py               # dev 命令实现
├── core/
│   ├── builder.py           # DocumentationBuilder 核心构建器
│   └── watcher.py           # 文件监听器
├── preprocessors/
│   ├── __init__.py
│   ├── link_map.py          # @[ClassName] API 引用链接映射
│   └── utm_links.py         # UTM 参数注入
└── tools/
    ├── notebook/convert.py  # Jupyter notebook 转 Markdown
    ├── docusaurus_parser.py # Docusaurus 格式迁移
    ├── parser.py            # MkDocs → Mintlify 解析器
    ├── links.py             # 链接处理与文件移动更新
    ├── highlights.py        # 代码高亮处理
    ├── lexer.py             # 词法分析
    └── partner_pkg_table.py # 合作伙伴包表格生成
```

## scripts/ 辅助脚本

| 脚本 | 说明 |
|------|------|
| `extract_code_snippets.py` | 从 code-samples 提取 Bluehawk 标签片段 |
| `generate_code_snippet_mdx.py` | 将提取结果转为 MDX |
| `test_code_samples.py` | 执行代码示例验证 |
| `check_cross_refs.py` | 验证 @[ref] 引用完整性 |
| `check_import_mappings.py` | 检查导入映射一致性 |
| `check_llms_urls.py` | 验证 llms.txt URL |
| `check_pr_imports.py` | PR 导入规范检查 |
| `filter_mint_broken_links.py` | 过滤 mint broken-links 误报 |
| `update_mdx.py` | 批量 MDX 更新 |
| `assemble_changelog.py` | 组装 changelog |
| `audit_changelog_coverage.py` | changelog 覆盖率审计 |
| `packages_yml_get_downloads.py` | 获取包下载量数据 |
| `sync_deepagents_signatures.py` | 同步 Deep Agents 签名 |
| `process_langsmith_openapi.py` | 处理 LangSmith OpenAPI |
| `convert_pip_to_codegroup.py` | pip 命令转 CodeGroup |
| `gh_artifact_download.py` | GitHub artifact 下载 |

## 交叉引用

- 事实采集：[spec/facts.md](/ai/langchain-ai/docs/spec/facts.md)
- 架构洞察：[spec/insights.md](/ai/langchain-ai/docs/spec/insights.md)
- 外部站点：[docs.langchain.com](https://docs.langchain.com)
- API 参考：[reference.langchain.com](https://reference.langchain.com)
