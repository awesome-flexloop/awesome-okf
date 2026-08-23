---
type: concept
title: "WebUI 与工具集成"
bundle: /datawhale/handy-ollama
description: "FastAPI/WebUI 可视化界面部署、LangChain/LlamaIndex 框架集成、Dify 低代码平台接入、Continue AI Copilot 编程助手"
sources: https://github.com/datawhalechina/handy-ollama/tree/main/docs/C5
related:
  - /datawhale/handy-ollama/concepts/api-openai-compatibility
  - /datawhale/handy-ollama/concepts/production-deployment
  - /datawhale/handy-ollama/concepts/model-management-modelfile
  - /datawhale/handy-ollama/references/chapter5-langchain
  - /datawhale/handy-ollama/references/chapter6-webui
  - /datawhale/handy-ollama/references/chapter7-applications
tags: [webui, fastapi, langchain, llamaindex, dify, copilot, integration]
status: stable
---

# WebUI 与工具集成

## 核心理解

Ollama 作为本地推理运行时，其价值通过广泛的生态集成释放。handy-ollama 教程展示了四个层次的集成方式：**自建界面**（FastAPI+WebSocket 快速搭建可视化对话）、**现成 WebUI**（Open WebUI 一行 Docker 部署）、**应用框架**（LangChain/LlamaIndex 构建 Chain/Agent/RAG）、**平台接入**（Dify 低代码、Continue 编程助手）。

这些集成都建立在 [API 与 OpenAI 兼容接口](api-openai-compatibility.md) 之上——有的调用原生 `/api/chat`，有的通过 OpenAI 兼容层 `/v1/chat/completions` 无缝接入。

## FastAPI 自建可视化界面

handy-ollama 提供了一个完整的 FastAPI + WebSocket 可视化对话应用（`notebook/C6/fastapi_chat_app/`），适合需要自定义界面的场景。

### 架构组成

```
浏览器 (static/index.html)
    ↕ WebSocket
FastAPI 服务 (app.py + websocket_handler.py)
    ↕ HTTP
Ollama 服务 (localhost:11434)
```

### 核心代码结构

```python
# app.py - FastAPI 应用
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # 接收消息 → 调用 Ollama API → 流式返回
```

### 技术要点

- **WebSocket 实时通信**：实现流式逐字输出效果
- **静态前端**：纯 HTML/JS 页面，无需重型前端框架
- **Ollama API 调用**：后端转发请求到 `http://localhost:11434/api/chat`
- **依赖简洁**：`fastapi`、`uvicorn`、`httpx`

```bash
pip install fastapi uvicorn httpx
python app.py
```

## Open WebUI 部署

[Open WebUI](https://github.com/open-webui/open-webui)（原 ollama-webui-lite）是功能最完善的 Ollama 可视化界面，支持多用户、模型管理、对话历史等。

### 方式一：Node.js 源码部署

```bash
# 安装 Node.js
git clone https://github.com/ollama-webui/ollama-webui-lite.git
cd ollama-webui-lite
npm ci
npm run dev
# 访问 http://localhost:3000/
```

### 方式二：Docker 部署（推荐）

```bash
docker run -d \
  -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

关键参数说明：

| 参数 | 作用 |
|------|------|
| `-p 3000:8080` | 将容器 8080 端口映射到主机 3000 |
| `--add-host=host.docker.internal:host-gateway` | 让容器能访问宿主机的 Ollama 服务 |
| `-v open-webui:/app/backend/data` | 持久化用户数据和对话历史 |
| `--restart always` | 开机自启 |

部署后访问 `http://localhost:3000/`，注册账号即可使用，自动发现本地 Ollama 模型。

## LangChain 集成

LangChain 是构建 LLM 应用的主流框架，Ollama 通过 `langchain-ollama` 包提供原生集成。

### Python 集成

```bash
pip install langchain-ollama langchain langchain-community faiss-cpu Pillow
```

#### 基础对话链

```python
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

model = ChatOllama(model="llama3.1", temperature=0.7)

template = """你是一个乐于助人的AI，擅长回答各种问题。
问题：{question}"""
prompt = ChatPromptTemplate.from_template(template)

chain = prompt | model
response = chain.invoke({"question": "你比GPT4厉害吗？"})
```

LangChain 使用管道操作符 `|` 组合 prompt 和 model，形成 LCEL（LangChain Expression Language）链。

#### 多模态

```python
from langchain_ollama import ChatOllama
from PIL import Image
import base64

model = ChatOllama(model="llava")
# 传入图片进行视觉问答
```

#### 工具调用

```python
model_with_tools = model.bind_tools([get_weather, search_web])
```

#### RAG 检索链

```python
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever()
```

### JavaScript 集成

LangChain.js 提供对等能力，包含 base_chat、advanced_prompt、base_tool、base_multimodal、advanced_json 等示例：

```javascript
import { ChatOllama } from "@langchain/ollama";
import { ChatPromptTemplate } from "@langchain/core/prompts";

const model = new ChatOllama({ model: "llama3.1" });
const prompt = ChatPromptTemplate.fromTemplate("问题：{question}");
const chain = prompt.pipe(model);
```

## LlamaIndex 集成

LlamaIndex 专注于数据索引和检索，在 RAG 场景中与 Ollama 结合紧密：

```python
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

llm = Ollama(model="llama3.1", request_timeout=120.0)
embed_model = OllamaEmbedding(model_name="nomic-embed-text")
```

LlamaIndex 的查询引擎支持多种 agent 模式：

| 模式 | 说明 |
|------|------|
| `best`（默认） | 自动选择 react 或 openai agent |
| `react` | ReAct 推理-行动循环 |
| `openai` | OpenAI 风格 function calling agent |

## Dify 低代码平台接入

Dify 是开源的 LLM 应用开发平台，原生支持 Ollama 作为模型供应商。

### 接入配置

在 Dify 的 `设置 > 模型供应商 > Ollama` 中填入：

| 字段 | 值 |
|------|-----|
| 模型名称 | `llama3.1` |
| 基础 URL | `http://<ollama-ip>:11434`（Docker 部署 Dify 时需填局域网 IP 或宿主机 IP，如 `http://172.17.0.1:11434`） |
| 模型类型 | `对话`（LLM）或 `Embedding`（嵌入模型） |
| 上下文长度 | `4096` |
| 最大 token | `4096` |
| Vision | 多模态模型（如 llava）勾选 |

### Docker 网络注意事项

Dify 和 Ollama 都在 Docker 中运行时，`localhost` 指向容器自身而非宿主机。解决方案：

- Dify Docker 部署：使用局域网 IP（`http://192.168.x.x:11434`）或 Docker 宿主机 IP（`http://172.17.0.1:11434`）
- Linux/macOS 查找 IP：`ip addr show` 或 `ifconfig`
- Windows 查找 IP：`ipconfig`
- Ollama 需暴露网络访问（设置 `OLLAMA_HOST=0.0.0.0`）

### 模型类型

Dify 支持同时接入 Ollama 的 LLM（对话/生成）和 Embedding（文本嵌入）模型，分别用于对话应用和 RAG 知识库。

## Continue AI Copilot 编程助手

[Continue](https://continue.dev) 是开源的 AI 编程助手插件，支持 VS Code 和 JetBrains IDE，可接入 Ollama 本地模型实现代码补全、对话、重构等：

- 支持本地模型（LM Studio/Ollama）及任何 OpenAI 兼容接口
- 支持多种模型提供商：OpenRouter、Anthropic、OpenAI、Google Gemini 等
- 在 IDE 中直接与本地模型对话，代码不出本机

配置方式：在 Continue 设置中将 provider 设为 `ollama`，model 设为已拉取的模型名（如 `deepseek-r1:1.5b` 或 `codellama`）。

## 集成模式总结

| 集成方式 | 适用场景 | 技术栈 | 复杂度 |
|----------|----------|--------|--------|
| FastAPI 自建 | 需要完全自定义界面 | Python + WebSocket | 中 |
| Open WebUI | 开箱即用的聊天界面 | Docker | 低 |
| LangChain | 构建复杂 LLM 应用/Chain/Agent | Python/JavaScript | 中高 |
| LlamaIndex | 数据密集型 RAG 应用 | Python | 中高 |
| Dify | 低代码 AI 应用平台 | Docker + Web | 低 |
| Continue | IDE 内编程助手 | VS Code/JetBrains | 低 |

## 交叉阅读

- 所有集成的技术基础是 REST API 和 OpenAI 兼容层，详见 [API 与 OpenAI 兼容接口](api-openai-compatibility.md)
- RAG/Agent 应用的生产化部署详见 [生产部署实践](production-deployment.md)
- LangChain RAG 的完整实战详见 [搭建本地 RAG 应用](../examples/local-rag-application.md)
