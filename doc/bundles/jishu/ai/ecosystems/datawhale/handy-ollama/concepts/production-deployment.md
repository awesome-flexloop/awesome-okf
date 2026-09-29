---
type: concept
title: "生产部署实践"
bundle: /datawhale/handy-ollama
description: "Docker 容器化部署、GPU 调度与多模型管理、RAG 检索增强生成、Agent 工具调用、本地隐私保护与应用栈"
sources: https://github.com/datawhalechina/handy-ollama/tree/main/docs/C7
related:
  - /datawhale/handy-ollama/concepts/model-management-modelfile
  - /datawhale/handy-ollama/concepts/api-openai-compatibility
  - /datawhale/handy-ollama/concepts/webui-tool-integration
  - /datawhale/handy-ollama/references/chapter7-applications
  - /datawhale/handy-ollama/examples/local-rag-application
tags: [production, docker, gpu, rag, agent, privacy, deployment]
status: stable
---

# 生产部署实践

## 核心理解

从"在本地跑一个模型"到"在生产环境提供 AI 服务"，需要解决容器化、资源调度、多模型管理、应用架构和隐私安全等问题。handy-ollama 第7章通过7个应用案例展示了 Ollama 在真实场景中的部署模式，涵盖 RAG 检索增强、Agent 工具调用、低代码平台集成等典型应用。

Ollama 在生产环境中的核心优势是**数据不出本地**——所有模型推理和数据处理都在本地机器或私有服务器完成，天然满足隐私合规要求，这使其在企业内网、医疗、金融等敏感场景中具有独特价值。

## Docker 容器化部署

Docker 是生产环境部署 Ollama 的推荐方式，提供环境隔离、易于扩展和一致的运行体验。

### 基础部署

```bash
# CPU / NVIDIA GPU
docker run -d \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  --restart always \
  ollama/ollama

# AMD GPU
docker run -d \
  --device /dev/kfd --device /dev/dri \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  ollama/ollama:rocm
```

### NVIDIA GPU 透传

```bash
# 需要安装 nvidia-container-toolkit
docker run -d \
  --gpus all \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  ollama/ollama
```

### Docker Compose 编排

生产环境中 Ollama 常与 WebUI、应用服务一起编排：

```yaml
services:
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
    restart: always

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    volumes:
      - open-webui:/app/backend/data
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      - ollama
    restart: always

volumes:
  ollama:
  open-webui:
```

### 网络配置

容器间访问 Ollama 时需注意网络地址：

- **同主机容器访问宿主机 Ollama**：使用 `host.docker.internal`（Docker 20.10+）或 `--add-host` 参数
- **Docker Compose 服务间访问**：使用服务名（如 `http://ollama:11434`）
- **远程访问**：设置 `OLLAMA_HOST=0.0.0.0:11434` 监听所有网络接口

## GPU 调度与多模型管理

### 资源规划

| 模型规模 | 最低内存 | 推荐场景 |
|----------|----------|----------|
| 1B-3B | 2-4GB | 轻量对话、边缘设备 |
| 7B-9B | 8-12GB | 日常对话、代码辅助 |
| 12B-14B | 16-20GB | 高质量生成、RAG |
| 33B-70B | 32GB+ | 复杂推理、Agent |
| 671B (DeepSeek R1) | 400GB+ | 服务器级深度推理 |

### 多模型并发

Ollama 支持同时加载多个模型，通过 `keep_alive` 参数控制模型在内存中的保留时间：

```json
{
  "model": "llama3.1",
  "keep_alive": "30m"
}
```

- 默认 `5m`：请求结束后 5 分钟卸载模型
- 设为 `0`：请求结束立即卸载
- 设为 `-1`：永久保留（需注意内存占用）
- 设为具体时长（如 `30m`、`2h`）：按需调整

### GPU 指定

多 GPU 环境下通过 `CUDA_VISIBLE_DEVICES` 环境变量分配：

```bash
# 指定单张 GPU
CUDA_VISIBLE_DEVICES=GPU-uuid ollama serve

# Linux GPU 选择脚本可灵活配置
```

## RAG 检索增强生成

RAG 是 Ollama 最常见的生产应用模式，解决大模型知识过时和幻觉问题。handy-ollama 提供了三种 RAG 实现路径。

### RAG 基本架构

```
用户提问
    ↓
┌─────────────┐
│  查询改写    │
└──────┬──────┘
       ↓
┌─────────────┐     ┌──────────────┐
│  嵌入模型    │ ←→ │  向量数据库   │
│ (nomic-     │     │  (FAISS等)   │
│  embed-text)│     └──────┬───────┘
└─────────────┘            │
       ↓                  ↓
┌─────────────────────────────┐
│  检索相关文档 Top-K          │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│  Prompt 组装                │
│  系统提示 + 检索上下文 + 问题│
└──────────────┬──────────────┘
               ↓
┌─────────────┐
│  Ollama LLM │ → 生成回答
└─────────────┘
```

### LangChain RAG

```python
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

# 1. 加载和分块文档
loader = TextLoader("data.txt")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
splits = splitter.split_documents(docs)

# 2. 创建向量索引
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = FAISS.from_documents(splits, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 3. 构建 RAG 链
llm = ChatOllama(model="llama3.1")
# chain = retriever | prompt | llm | output_parser
```

### LlamaIndex RAG

LlamaIndex 提供更高级的数据索引抽象：

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=OllamaEmbedding(model_name="nomic-embed-text")
)
query_engine = index.as_query_engine(
    llm=Ollama(model="llama3.1", request_timeout=120)
)
response = query_engine.query("你的问题")
```

### DeepSeek R1 + RAG

DeepSeek R1 是深度推理模型，与 Ollama 结合可实现带思维链的 RAG 应用：

```bash
ollama pull deepseek-r1:1.5b  # 轻量版
ollama pull deepseek-r1       # 完整版（需大内存）
```

DeepSeek R1 会先输出 `<think>...</think>` 思维链过程，再给出最终答案，适合复杂推理问答场景。教程中包含基于 PDF 文档的 DeepSeek R1 RAG 完整实现。

## Agent 工具调用

Agent 让 LLM 能够调用外部工具完成任务，是从"问答"到"行动"的关键跃迁。

### LangChain Agent

```python
from langchain_ollama import ChatOllama
from langchain_core.tools import tool

@tool
def search_web(query: str) -> str:
    """搜索网络获取信息"""
    return web_search(query)

@tool
def calculate(expression: str) -> str:
    """执行数学计算"""
    return str(eval(expression))

llm = ChatOllama(model="llama3.1")
llm_with_tools = llm.bind_tools([search_web, calculate])
```

Agent 通过 ReAct（Reasoning + Acting）循环：思考→选择工具→执行→观察结果→继续思考→最终回答。

### LlamaIndex Agent

LlamaIndex 的 Agent 支持 react 和 openai 两种模式，可将查询引擎、函数等注册为工具。

## 应用案例矩阵

handy-ollama 第7章的7个案例覆盖了不同应用场景：

| 案例 | 类型 | 核心技术 | 适用场景 |
|------|------|----------|----------|
| AI Copilot 编程助手 | IDE 集成 | Continue + VS Code/JetBrains | 代码补全、重构、问答 |
| Dify 接入本地模型 | 低代码平台 | Dify + Ollama Docker | 快速搭建 AI 应用 |
| LangChain RAG | 检索增强 | LangChain + FAISS + Ollama | 文档问答、知识库 |
| LlamaIndex RAG | 检索增强 | LlamaIndex + Ollama | 数据密集型 RAG |
| LangChain Agent | 智能体 | LangChain + tools + Ollama | 工具调用、任务自动化 |
| LlamaIndex Agent | 智能体 | LlamaIndex Agent + Ollama | 数据查询代理 |
| DeepSeek R1 RAG | 推理增强 | DeepSeek R1 + PDF RAG | 复杂推理问答 |

## 本地隐私保护

Ollama 在生产环境中的独特优势：

1. **数据不出本地**：所有文档、对话、嵌入都在本地机器处理，不上传第三方
2. **离线可用**：模型下载后无需互联网连接即可运行
3. **合规友好**：满足医疗、金融、政务等数据不出域的合规要求
4. **成本可控**：无 API 调用费用，适合高频使用场景
5. **可定制性**：通过 Modelfile 定制模型行为，微调后本地部署

## 从单模型到应用栈的能力递进

```
Level 1  ollama run llama3.1              命令行单模型对话
Level 2  Modelfile + ollama create        自定义模型配置
Level 3  REST API /v1/chat/completions    服务化 API 接口
Level 4  LangChain/LlamaIndex Chain       框架化应用编排
Level 5  WebUI/Dify/FastAPI               多用户可视化界面
Level 6  Docker+GPU+RAG+Agent             生产级 AI 服务
```

每个 Level 都建立在前一个的基础上，Ollama 贯穿全栈作为推理底座。

## 交叉阅读

- 模型存储和 GPU 环境变量配置详见 [模型管理与 Modelfile](model-management-modelfile.md)
- API 端点和 OpenAI 兼容层是所有应用的通信基础，详见 [API 与 OpenAI 兼容接口](api-openai-compatibility.md)
- WebUI、LangChain、Dify 等集成方式详见 [WebUI 与工具集成](webui-tool-integration.md)
- RAG 应用的完整可运行代码详见 [搭建本地 RAG 应用](../examples/local-rag-application.md)
