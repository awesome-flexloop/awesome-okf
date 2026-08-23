---
type: concept
scope: langchain-google
name: overview
version: "0.1.0"
source: https://github.com/langchain-ai/langchain-google
description: langchain-google 总览——Monorepo 结构、三包职责、双后端抽象与 SDK 迁移现状
---

# langchain-google 总览

## 什么是 langchain-google

`langchain-google` 是 LangChain 官方维护的 Google AI 服务集成 monorepo，将 Google 的 Gemini 模型、Vertex AI 平台、Google Cloud 服务（BigQuery、GCS、Drive、Gmail、Calendar 等）接入 LangChain 生态。它包含三个独立版本化、独立发布的 Python 包：

| 包名 | 版本 | 职责 | 底层 SDK |
|---|---|---|---|
| `langchain-google-genai` | 4.3.5 | Gemini 聊天/嵌入/LLM，双后端（Gemini API + Vertex AI） | `google-genai` |
| `langchain-google-vertexai` | 3.2.4 | Vertex AI 全功能集成（含 Model Garden、Vector Search、Vision、Evaluators） | `google-cloud-aiplatform` + `vertexai`（向 google-genai 迁移中） |
| `langchain-google-community` | — | Google Workspace 与 Cloud 工具集（Gmail/Calendar/Sheets/Drive/BigQuery 等） | 各 Google Cloud 客户端库 |

- **源码**：<https://github.com/langchain-ai/langchain-google>
- **Python 要求**：≥ 3.10
- **构建系统**：hatchling + uv

## 解决的问题

Google 的 AI 服务存在两个面向不同场景的入口：

1. **Gemini Developer API**：公网服务，API key 鉴权，适合个人开发者和快速原型。
2. **Vertex AI**：GCP 企业平台，支持 ADC/服务凭证/API key，提供区域端点、VPC-SC、数据驻留、Model Garden 第三方模型等企业能力。

传统集成往往为两者提供独立的类（如 `ChatGoogleGenerativeAI` 与 `ChatVertexAI`），导致代码在开发/生产环境间切换时需要改导入和类名。langchain-google 通过**双后端统一抽象**解决了这一问题。

## 核心机制：双后端自动检测

`langchain-google-genai` 4.0.0 的 `ChatGoogleGenerativeAI` 和 `GoogleGenerativeAIEmbeddings` 在同一个类中支持两个后端。后端选择由 `_determine_backend()` 自动完成，优先级为：

```
vertexai 参数（显式 True/False）
    ↓ 未设置
GOOGLE_GENAI_USE_VERTEXAI 环境变量
    ↓ 未设置
credentials 参数存在 → Vertex AI
    ↓
project 参数存在 → Vertex AI
    ↓
默认 Gemini Developer API
```

一旦后端确定，`_initialize_client` validator 创建统一的 `google.genai.Client` 实例，后续所有调用（`client.models.generate_content`、`client.models.embed_content`）都不感知后端差异。详见 [聊天模型](/langchain-ai/langchain-google/concepts/chat-models)。

## 三包关系与演进方向

```
┌─────────────────────────────────────────────────┐
│          langchain-google-genai (新)            │
│  ChatGoogleGenerativeAI / GoogleGenerativeAI    │
│  GoogleGenerativeAIEmbeddings                   │
│  ← 统一 google-genai SDK，双后端，主推方向       │
└──────────────────┬──────────────────────────────┘
                   │ 弃用迁移
                   ▼
┌─────────────────────────────────────────────────┐
│       langchain-google-vertexai (旧/全功能)     │
│  ChatVertexAI [deprecated]                      │
│  VertexAIEmbeddings [deprecated→内部已用genai]   │
│  + Model Garden (Mistral/Llama/Anthropic)       │
│  + Vector Search / Vision / Evaluators          │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│       langchain-google-community (工具集)       │
│  Gmail / Calendar / Sheets / Drive / Tasks      │
│  BigQuery / Document AI / Vision / Speech       │
│  Vertex AI Search / Model Armor / Geocoding     │
└─────────────────────────────────────────────────┘
```

关键现状：

- `ChatVertexAI`、`VertexAI`、`VertexAIEmbeddings` 已标记 `@deprecated(since="3.2.0", removal="4.0.0")`，推荐迁移到 genai 包。
- 但 `VertexAIEmbeddings` **内部已改用 `genai.Client(vertexai=True)`**，是迁移的"支点"——先让旧类跑在新 SDK 上验证，再引导用户换类。
- vertexai 包仍承载 genai 包未覆盖的能力：Model Garden 第三方模型（Mistral/Llama/Anthropic）、Vector Search、Imagen 视觉模型、Evaluators。

## 鉴权方式

| 后端 | 鉴权方式 | 关键配置 |
|---|---|---|
| Gemini Developer API | API key | `api_key` 参数或 `GOOGLE_API_KEY`/`GEMINI_API_KEY` 环境变量 |
| Vertex AI | ADC（推荐） | `gcloud auth application-default login`，自动发现凭证 |
| Vertex AI | 服务账号 | `credentials` 参数传入 `google.oauth2.service_account.Credentials` |
| Vertex AI | API key | `vertexai=True` + `project` + API key（通过环境变量传给 SDK） |

`google.auth` 库的查找顺序：`GOOGLE_APPLICATION_CREDENTIALS` 环境变量 → 系统级凭证。详见 [嵌入模型与 Vertex AI](/langchain-ai/langchain-google/concepts/embeddings-vertex)。

## 架构概览

```
libs/
├── genai/langchain_google_genai/
│   ├── __init__.py          # 公共导出
│   ├── _common.py           # _BaseGoogleGenerativeAI, 后端检测, 鉴权
│   ├── chat_models.py       # ChatGoogleGenerativeAI (~4000行)
│   ├── embeddings.py        # GoogleGenerativeAIEmbeddings
│   ├── llms.py              # GoogleGenerativeAI (文本补全)
│   ├── _function_utils.py   # 工具/函数调用转换
│   ├── _image_utils.py      # 图片字节加载
│   ├── _enums.py            # HarmCategory/BlockThreshold/Modality
│   └── data/_profiles.py    # 模型能力 profile
├── vertexai/langchain_google_vertexai/
│   ├── __init__.py
│   ├── _base.py             # _VertexAIBase, _VertexAICommon
│   ├── chat_models.py       # ChatVertexAI (gapic/proto 路径)
│   ├── embeddings.py        # VertexAIEmbeddings (已迁 genai)
│   ├── model_garden.py      # VertexAIModelGarden
│   ├── model_garden_maas/   # Llama/Mistral MaaS
│   ├── _anthropic_*.py      # Anthropic 适配
│   ├── vectorstores/        # Vector Search 集成
│   ├── vision_models.py     # Imagen 视觉模型
│   └── evaluators/          # Vertex 评估器
└── community/langchain_google_community/
    ├── gmail/ calendar/ sheets/ tasks/ drive/
    ├── bigquery.py  docai.py  vision.py
    ├── search.py  places_api.py  geocoding.py
    ├── vertex_ai_search.py  vertex_rank.py
    └── model_armor/         # 提示/响应净化中间件
```

## 快速开始

```bash
pip install langchain-google-genai
```

```python
from langchain_google_genai import ChatGoogleGenerativeAI

# Gemini Developer API（设置 GOOGLE_API_KEY 环境变量）
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")
llm.invoke("解释什么是 RAG")
```

```python
# Vertex AI 后端（自动检测 project/credentials）
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    project="my-gcp-project",
    vertexai=True,
)
```

更多用法见 [基础使用示例](/langchain-ai/langchain-google/examples/basic-usage)。

## 已知限制与注意事项

1. **禁用重试用 `max_retries=1`**，不是 0——Google SDK 将 0 解释为"使用默认值"（5 次）。
2. **429 重试延迟**：SDK 内置重试忽略服务器返回的 `retry_delay`，用固定指数退避（上游 issue #1875）。
3. **嵌入仅文本**：`GoogleGenerativeAIEmbeddings` 的 LangChain 接口仅接受文本；多模态嵌入需直接用 google-genai SDK。
4. **批大小限制**：嵌入每批最多 100 条文本、20000 token。
5. **Gemini 3.0+ temperature**：未显式设置时自动置 None，避免无限循环和推理性能问题。

## 进一步阅读

- [聊天模型架构](/langchain-ai/langchain-google/concepts/chat-models) — ChatGoogleGenerativeAI 内部流程、工具调用、结构化输出、错误分类
- [嵌入模型与 Vertex AI](/langchain-ai/langchain-google/concepts/embeddings-vertex) — GoogleGenerativeAIEmbeddings、VertexAIEmbeddings、批处理、task_type
- [API 参考](/langchain-ai/langchain-google/references/api) — 核心类与方法签名
- [基础使用示例](/langchain-ai/langchain-google/examples/basic-usage) — 聊天、嵌入、工具调用、Vertex AI 配置
