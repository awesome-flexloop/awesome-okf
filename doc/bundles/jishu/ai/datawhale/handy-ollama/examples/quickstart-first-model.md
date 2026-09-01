---
type: example
title: "快速启动第一个本地模型"
bundle: /datawhale/handy-ollama
description: "从安装到首次对话，使用 CLI、curl 和 Python 三种方式调用 Ollama"
sources: https://github.com/datawhalechina/handy-ollama/tree/main/docs/C4
related:
  - /datawhale/handy-ollama/concepts/ollama-architecture-installation
  - /datawhale/handy-ollama/concepts/api-openai-compatibility
  - /datawhale/handy-ollama/references/chapter4-rest-api
tags: [quickstart, cli, curl, python, beginner]
status: stable
---

# 快速启动第一个本地模型

## 目标

5 分钟内完成 Ollama 安装、拉取模型、首次对话，分别通过命令行、HTTP API 和 Python 三种方式调用本地大模型。

## 前置条件

- 一台电脑（Windows/macOS/Linux 均可）
- 至少 8GB 内存（运行 7B 模型）
- 互联网连接（首次下载模型时需要）

## 步骤一：安装 Ollama

访问 [https://ollama.com/download](https://ollama.com/download) 下载对应系统的安装包，或使用 Docker：

```bash
# Docker 方式（跨平台）
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

安装后验证：

```bash
ollama --version
```

## 步骤二：拉取并运行模型

```bash
# 拉取并运行 Llama 3.1 8B 模型（约 4.7GB 下载）
ollama run llama3.1
```

首次运行会自动下载模型。下载完成后自动进入交互模式，直接输入问题即可对话：

```
>>> 你好，请用一句话介绍你自己
你好！我是 Llama 3.1，一个由 Meta 开发的大型语言模型。
```

输入 `/bye` 退出交互模式。

## 步骤三：通过 curl 调用 REST API

保持 Ollama 服务运行（默认端口 11434），新开终端：

### 文本生成（非流式）

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1",
  "prompt": "用一句话解释什么是大语言模型",
  "stream": false
}'
```

返回 JSON 包含 `response` 字段和生成统计信息。

### 对话补全

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.1",
  "messages": [
    {"role": "user", "content": "什么是RAG？"}
  ],
  "stream": false
}'
```

### 通过 OpenAI 兼容接口调用

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

## 步骤四：Python 调用

安装官方 Python 库：

```bash
pip install ollama
```

### 基础对话

```python
import ollama

response = ollama.chat(
    model='llama3.1',
    messages=[
        {'role': 'user', 'content': '用Python写一个快速排序'}
    ]
)
print(response['message']['content'])
```

### 流式输出

```python
import ollama

stream = ollama.chat(
    model='llama3.1',
    messages=[{'role': 'user', 'content': '写一首关于编程的诗'}],
    stream=True
)

for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)
```

### 使用 OpenAI SDK（兼容层）

```python
from openai import OpenAI

client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama'
)

response = client.chat.completions.create(
    model='llama3.1',
    messages=[{'role': 'user', 'content': '你好'}]
)
print(response.choices[0].message.content)
```

## 步骤五：查看模型状态

```bash
# 列出本地已下载的模型
ollama list

# 查看正在运行的模型（显示内存占用和处理器）
ollama ps

# 查看模型详细信息
ollama show llama3.1
```

## 验证结果

成功标志：

1. `ollama run llama3.1` 能进入对话并得到中文回复
2. curl 命令返回包含 `response` 或 `message` 字段的 JSON
3. Python 脚本打印出模型生成的文本
4. `ollama ps` 显示 llama3.1 正在运行

## 常见问题

**Q: 模型下载慢怎么办？**
A: 网络问题，可设置代理或手动下载 GGUF 文件后通过 Modelfile 导入（见下一示例）。

**Q: 内存不够运行 7B 模型？**
A: 使用更小的模型：`ollama run llama3.2:1b`（约 1.3GB）或 `qwen2:0.5b`（约 352MB）。

**Q: 端口 11434 被占用？**
A: 设置 `OLLAMA_HOST=0.0.0.0:11435` 更改端口。

## 延伸阅读

- 了解 Ollama 架构和安装原理 → [Ollama 架构与安装](../concepts/ollama-architecture-installation.md)
- 深入 API 参数和端点 → [API 与 OpenAI 兼容接口](../concepts/api-openai-compatibility.md)
- 自定义模型行为 → [使用 Modelfile 自定义模型](custom-model-modelfile.md)
