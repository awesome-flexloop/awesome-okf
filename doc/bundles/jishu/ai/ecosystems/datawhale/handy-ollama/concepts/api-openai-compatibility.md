---
type: concept
title: "API 与 OpenAI 兼容接口"
bundle: /datawhale/handy-ollama
description: "Ollama REST API 端点（generate/chat/embed）、流式响应、JSON 模式、多模态、工具调用、OpenAI 兼容层及多语言 SDK"
sources: https://github.com/datawhalechina/handy-ollama/tree/main/docs/C4
related:
  - /datawhale/handy-ollama/concepts/ollama-architecture-installation
  - /datawhale/handy-ollama/concepts/model-management-modelfile
  - /datawhale/handy-ollama/concepts/webui-tool-integration
  - /datawhale/handy-ollama/references/chapter4-rest-api
  - /datawhale/handy-ollama/examples/quickstart-first-model
tags: [api, rest, openai-compatibility, streaming, sdk, tools]
status: stable
---

# API 与 OpenAI 兼容接口

## 核心理解

Ollama 启动后在本地 `http://localhost:11434` 提供 REST API 服务，这是所有应用集成的基础。API 设计包含两个层次：**原生 API**（`/api/generate`、`/api/chat`、`/api/embed` 等）提供 Ollama 特有功能，**OpenAI 兼容层**（`/v1/chat/completions`、`/v1/embeddings`）让现有 OpenAI 生态工具零成本切换到本地模型。

这一双层 API 设计是 Ollama 生态枢纽地位的技术基础——应用既可以使用原生 API 的流式控制、模型管理等高级功能，也可以通过 OpenAI 兼容接口无缝接入 LangChain、Dify、Continue 等现有工具链。

## API 端点总览

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/generate` | POST | 回答补全（文本生成） |
| `/api/chat` | POST | 对话补全（多轮对话） |
| `/api/embed` | POST | 生成嵌入向量 |
| `/api/create` | POST | 从 Modelfile 创建模型 |
| `/api/copy` | POST | 复制模型 |
| `/api/delete` | DELETE | 删除模型 |
| `/api/pull` | POST | 拉取模型 |
| `/api/push` | POST | 推送模型 |
| `/api/ps` | GET | 列出运行中模型 |
| `/api/tags` | GET | 列出本地模型 |
| `/api/show` | POST | 显示模型信息 |
| `/v1/chat/completions` | POST | OpenAI 兼容对话接口 |
| `/v1/embeddings` | POST | OpenAI 兼容嵌入接口 |

## 回答补全：/api/generate

最基础的文本生成端点，流式返回逐 token 响应。

### 请求参数

```json
{
  "model": "llama3.1",
  "prompt": "为什么草是绿的？",
  "system": "你是一个植物学家",
  "template": "...",
  "context": [1, 2, 3],
  "stream": true,
  "raw": false,
  "format": "json",
  "images": ["base64..."],
  "options": {
    "temperature": 0.7,
    "seed": 1001,
    "top_p": 0.9
  },
  "keep_alive": "5m"
}
```

| 参数 | 说明 |
|------|------|
| `model` | （必需）模型名称 |
| `prompt` | 生成提示 |
| `system` | 系统消息 |
| `context` | 上一轮请求返回的上下文，用于保持对话记忆 |
| `stream` | `false` 时返回单个完整响应而非流式 |
| `format` | 设为 `json` 强制 JSON 格式输出 |
| `images` | base64 编码图像列表（多模态模型如 llava） |
| `options` | 模型参数（temperature、seed 等） |
| `keep_alive` | 请求后模型在内存中保留时间（默认 5m） |

### 流式响应

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1",
  "prompt": "为什么草是绿的？"
}'
```

返回 JSON 对象流，每个对象包含一个 token 片段：

```json
{"model":"llama3.1","response":"植物","done":false}
{"model":"llama3.1","response":"叶子","done":false}
```

最终响应包含统计信息：`total_duration`、`load_duration`、`prompt_eval_count`、`eval_count`、`eval_duration`（可计算 token/s 速度）。

### JSON 模式

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1",
  "prompt": "为什么草是绿的？以JSON格式输出答案",
  "format": "json",
  "stream": false
}'
```

> **注意**：需在 prompt 中指示模型以 JSON 格式响应，否则可能生成大量空格。

### 可复现输出

设置 `options.seed` 为固定值可获得可复现的生成结果。

## 对话补全：/api/chat

专为多轮对话设计，支持消息角色和工具调用。

### 请求结构

```json
{
  "model": "llama3.1",
  "messages": [
    {"role": "system", "content": "你是一个有用的助手"},
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！有什么可以帮你？"},
    {"role": "user", "content": "今天天气怎么样？"}
  ],
  "tools": [...],
  "stream": false,
  "options": {"temperature": 0.7}
}
```

### 消息角色

| 角色 | 说明 |
|------|------|
| `system` | 系统指令，设定助手行为 |
| `user` | 用户消息 |
| `assistant` | 助手回复（用于多轮上下文） |
| `tool` | 工具返回结果 |

### 工具调用（Tool Calling）

Ollama 支持 Llama 3.1 等模型的工具调用。当 `stream` 设为 `false` 时，模型可在响应中返回 `tool_calls`：

```json
{
  "model": "llama3.1",
  "messages": [{"role": "user", "content": "北京现在多少度？"}],
  "tools": [{
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "获取指定城市的天气",
      "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"]
      }
    }
  }],
  "stream": false
}
```

模型返回 `tool_calls` 后，应用执行对应函数，将结果以 `role: "tool"` 消息发回，模型据此生成最终回答。这是 Agent 应用的基础。

## 嵌入生成：/api/embed

```bash
curl http://localhost:11434/api/embed -d '{
  "model": "nomic-embed-text",
  "input": "要嵌入的文本"
}'
```

嵌入模型（如 `nomic-embed-text`、`mxbai-embed-large`）生成向量表示，用于 RAG 检索、语义搜索等场景。

## 多模态支持

向 `/api/generate` 或 `/api/chat` 传入 base64 编码的 `images` 列表，即可使用 llava、llama3.2-vision 等多模态模型：

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llava",
  "prompt": "描述这张图片",
  "stream": false,
  "images": ["iVBORw0KGgoAAAANSUhEUgAA..."]
}'
```

## OpenAI 兼容层

Ollama 提供与 OpenAI API 兼容的端点，这意味着任何使用 OpenAI SDK 或 OpenAI 格式 API 的应用都可以直接指向本地 Ollama：

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # 任意字符串，Ollama 不验证
)

response = client.chat.completions.create(
    model="llama3.1",
    messages=[{"role": "user", "content": "你好"}]
)
```

兼容的端点包括：

| OpenAI 端点 | Ollama 对应 | 用途 |
|-------------|-------------|------|
| `POST /v1/chat/completions` | `/api/chat` | 对话补全 |
| `POST /v1/completions` | `/api/generate` | 文本补全 |
| `POST /v1/embeddings` | `/api/embed` | 嵌入向量 |
| `GET /v1/models` | `/api/tags` | 模型列表 |

> 参考：https://ollama.com/blog/openai-compatibility

这一兼容层的生态价值巨大：LangChain、LlamaIndex、Dify、Continue、Open WebUI 等工具原生支持 OpenAI API，只需修改 `base_url` 即可切换到本地 Ollama，无需任何代码改动。

## 多语言 SDK

### Python

```python
import ollama

response = ollama.chat(model='llama3.1', messages=[
    {'role': 'user', 'content': '你好'}
])
print(response['message']['content'])

# 流式响应
stream = ollama.chat(model='llama3.1', messages=[...], stream=True)
for chunk in stream:
    print(chunk['message']['content'], end='')
```

也可直接使用 `requests` 库调用 REST API。

### Java

使用 OkHttp 发送 HTTP 请求，或通过 Spring AI 集成 Ollama。Spring AI 提供 `OllamaChatModel` 等高级抽象。

### JavaScript / Node.js

```javascript
const ollama = require('ollama');

const response = await ollama.chat({
  model: 'llama3.1',
  messages: [{ role: 'user', content: '你好' }]
});
```

### C++

使用 libcurl 或 cpr 库发送 HTTP 请求，解析 JSON 响应（如 nlohmann/json）。

### Golang

使用 `ollama-go` 客户端库，支持 chat、generate、streaming、structured output 等。

## 模型管理 API

除推理外，API 还支持完整的模型生命周期管理：

```bash
# 拉取模型（流式显示进度）
curl http://localhost:11434/api/pull -d '{"name": "llama3.1"}'

# 列出本地模型
curl http://localhost:11434/api/tags

# 列出运行中模型
curl http://localhost:11434/api/ps

# 删除模型
curl -X DELETE http://localhost:11434/api/delete -d '{"name": "mymodel"}'
```

## 交叉阅读

- Ollama 服务架构和默认端口详见 [Ollama 架构与安装](ollama-architecture-installation.md)
- Modelfile 与模型创建 API 的关系详见 [模型管理与 Modelfile](model-management-modelfile.md)
- LangChain/LlamaIndex 等框架通过 API 集成详见 [WebUI 与工具集成](webui-tool-integration.md)
- 使用 Python 调用 API 的完整示例详见 [快速启动第一个本地模型](../examples/quickstart-first-model.md)
