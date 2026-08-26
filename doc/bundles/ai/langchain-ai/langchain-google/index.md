---
type: bundle
okf_version: "0.2"
scope: langchain-google
name: langchain-google
version: "0.1.0"
source: https://github.com/langchain-ai/langchain-google
description: LangChain 官方 Google AI 集成 monorepo——langchain-google-genai 4.3.5 基于 google-genai SDK 统一 Gemini Developer API 与 Vertex AI 双后端，提供 ChatGoogleGenerativeAI/GoogleGenerativeAIEmbeddings；langchain-google-vertexai 3.2.4 提供 Model Garden/Vector Search/Vision/Evaluators 等 Vertex AI 全功能；langchain-google-community 提供 Gmail/Calendar/BigQuery/Drive 等 Google Cloud 工具集
---

# langchain-google

**langchain-google** 是 LangChain 官方维护的 Google AI 服务集成 monorepo，将 Google Gemini 模型、Vertex AI 平台和 Google Cloud 服务接入 LangChain 生态。它包含三个独立版本化的 Python 包，覆盖从模型调用到企业级云服务工具的完整场景。

- **源码**：<https://github.com/langchain-ai/langchain-google>
- **语言**：Python ≥ 3.10
- **构建**：hatchling + uv
- **核心依赖**：langchain-core、google-genai、google-cloud-aiplatform

## 三个包

| 包 | 版本 | 底层 SDK | 核心能力 |
|---|---|---|---|
| `langchain-google-genai` | 4.3.5 | `google-genai` | Gemini 聊天/嵌入/LLM，**Gemini API + Vertex AI 双后端统一** |
| `langchain-google-vertexai` | 3.2.4 | `google-cloud-aiplatform`（向 google-genai 迁移中） | Vertex AI 全功能：Model Garden 第三方模型、Vector Search、Imagen、Evaluators |
| `langchain-google-community` | — | 各 Google Cloud 客户端 | Gmail/Calendar/Sheets/Tasks/Drive/BigQuery/Document AI/Vision/Search/Model Armor 工具集 |

## 核心特性

- **双后端统一抽象**：`ChatGoogleGenerativeAI` 和 `GoogleGenerativeAIEmbeddings` 通过 `vertexai` 参数/环境变量/凭证自动检测后端，同一套 API 在 Gemini Developer API（API key）和 Vertex AI（ADC/服务凭证）间切换，无需改代码。后端选择优先级：显式 `vertexai` → `GOOGLE_GENAI_USE_VERTEXAI` → `credentials` 存在 → `project` 存在 → 默认 Gemini API。
- **统一 google-genai SDK**：自 4.0.0 起基于 `google-genai`（`from google import genai`），替代旧的 `google-generativeai`/`google-ai-generativelanguage`，支持 Gemini 模型的所有新能力（思考预算、代码执行、Google Search/Maps 接地、视频生成等）。
- **LangChain 协议适配**：将 Google 异常按 HTTP 状态码映射到 `langchain_core.exceptions.Model*Error` 体系（401 认证/403 权限/404 模型/429 限流/5xx 服务端），上下文溢出特殊映射为 `ContextOverflowError` 以支持中间件回退；流式错误在生成器消费点分类。
- **工具调用与结构化输出**：`bind_tools` 支持 Pydantic/Callable/BaseTool/dict/原生 GoogleTool，`tool_choice` 支持 auto/any/none/指定函数；`with_structured_output` 默认使用原生 JSON schema（`json_schema` 方法），流式输出完整 Pydantic 对象。
- **模型 Profile 数据驱动**：通过 `ModelProfileRegistry` 和 `profile_augmentations.toml` 注册模型能力元数据，由 `langchain-profiles` CLI 生成，新增模型支持往往只需刷新数据。
- **Vertex AI 企业能力**：Model Garden MaaS（Llama/Mistral/Anthropic）、Vector Search（含 Datastore/GCS 文档存储）、Imagen 视觉模型（字幕/编辑/生成/视觉问答）、Vertex Evaluators（成对/单串评估）。
- **Google Cloud 工具生态**：community 包提供 Google Workspace 工具集（Gmail/Calendar/Sheets/Tasks）、BigQuery 向量存储、Document AI 解析、Cloud Vision、Speech-to-Text、Text-to-Speech、Translate、Vertex AI Search、Model Armor 净化中间件等。

## SDK 迁移现状

仓库正处于从旧 SDK 到 `google-genai` 的渐进式迁移中：

- **genai 包**：已完成切换，完全基于 `google-genai`。
- **vertexai 包**：`ChatVertexAI`/`VertexAI`/`VertexAIEmbeddings`/`create_structured_runnable` 已标记 `@deprecated(since="3.2.0", removal="4.0.0")`，推荐迁移到 genai 包对应类。但 `VertexAIEmbeddings` 内部已改用 `genai.Client(vertexai=True)`——先让旧类跑在新 SDK 上验证，再引导用户迁移。
- **未迁移能力**：Model Garden、Vector Search、Vision、Evaluators 仍仅在 vertexai 包中。

## 快速开始

```bash
pip install langchain-google-genai
```

```python
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Gemini Developer API（设置 GOOGLE_API_KEY 环境变量）
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")
print(llm.invoke("解释什么是 RAG").content)

# Vertex AI 后端（同一套 API，通过参数/环境变量切换）
# llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", project="my-project", vertexai=True)

# 嵌入
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
vector = embeddings.embed_query("什么是向量数据库？")
```

详见 [基础使用示例](/ai/langchain-ai/langchain-google/examples/basic-usage)。

## 文档导航

### 核心概念

- [总览](/ai/langchain-ai/langchain-google/concepts/overview) — Monorepo 三包职责、双后端自动检测、SDK 迁移现状与鉴权方式
- [聊天模型架构](/ai/langchain-ai/langchain-google/concepts/chat-models) — ChatGoogleGenerativeAI 客户端初始化、消息转换、生成流程、工具调用、结构化输出、错误分类
- [嵌入模型与 Vertex AI](/ai/langchain-ai/langchain-google/concepts/embeddings-vertex) — GoogleGenerativeAIEmbeddings 双后端、批处理、task_type、VertexAIEmbeddings 弃用与 Vector Search

### API 参考

- [API 参考](/ai/langchain-ai/langchain-google/references/api) — ChatGoogleGenerativeAI/GoogleGenerativeAIEmbeddings 完整签名、VertexAI 弃用类、Model Garden/Vector Search/Vision、环境变量速查

### 使用示例

- [基础使用](/ai/langchain-ai/langchain-google/examples/basic-usage) — 聊天/流式/Vertex AI 切换/工具调用/结构化输出/嵌入/安全设置/思考预算/错误处理/LCEL

### 源码事实与洞察

- [事实清单](/ai/langchain-ai/langchain-google/spec/facts) — 85 条带文件行号的源码事实
- [架构洞察](/ai/langchain-ai/langchain-google/spec/insights) — 双后端统一抽象、SDK 代际迁移策略、错误分类与流式异常处理

## 目录结构

```
langchain-google/
├── index.md                    # 本文件
├── log.md                      # 变更日志
├── spec/
│   ├── facts.md                # 源码事实验证清单（85 条）
│   └── insights.md             # 3 个架构洞察
├── concepts/                   # 核心概念（3 篇）
│   ├── overview.md
│   ├── chat-models.md
│   ├── embeddings-vertex.md
│   └── index.md
├── references/                 # API 参考（1 篇）
│   ├── api.md
│   └── index.md
└── examples/                   # 使用示例（1 篇）
    ├── basic-usage.md
    └── index.md
```

## 相关项目

| 项目 | 路径 | 关系 |
|---|---|---|
| langchain | [/langchain-ai/langchain/](/ai/langchain-ai/langchain/) | LangChain 核心框架，langchain-google 实现其 ChatModel/Embeddings/Tool 接口 |
| langgraph | [/langchain-ai/langgraph/](/ai/langchain-ai/langgraph/) | LangChain 编排框架，可与 ChatGoogleGenerativeAI 组合构建 Agent |

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
