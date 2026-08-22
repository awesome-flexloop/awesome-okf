---
type: example
title: "添加自定义 LLM 模型"
description: "通过环境变量配置自定义 LLM 模型，支持 OpenAI/Ark/DeepSeek/Ollama/Qwen/Gemini 六种协议与多模型并存"
tags: [LLM, 模型配置, Ollama, OpenAI, 环境变量]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cs-103
    resource: /references/deployment-infrastructure.md
    title: "LLM 序号后缀配置 6 协议"
  - id: F-cs-090
    resource: /references/deployment-infrastructure.md
    title: "Embedding 5 选项"
---

# 添加自定义 LLM 模型

本指南介绍如何在 Coze Studio 中配置自定义 LLM 模型。系统使用序号后缀（sequential suffix）模式支持多模型并存，可以同时配置多个不同协议的模型。

## 配置模式

每个模型由一组相同序号的环境变量定义，序号从 `0` 开始递增：

```bash
MODEL_PROTOCOL_N=<协议>
MODEL_ID_N=<模型ID>
MODEL_API_KEY_N=<API密钥>
MODEL_NAME_N=<显示名称>
MODEL_BASE_URL_N=<API地址>
```

## 支持的模型协议

| 协议标识 | 提供商 | 需要 API Key | 本地部署 |
|----------|--------|-------------|----------|
| `openai` | OpenAI / OpenAI 兼容 API | ✅ | 取决于服务 |
| `ark` | 火山引擎方舟 | ✅ | ❌ |
| `deepseek` | DeepSeek | ✅ | ❌ |
| `ollama` | Ollama 本地模型 | ❌ | ✅ |
| `qwen` | 阿里通义千问 | ✅ | ❌ |
| `gemini` | Google Gemini | ✅ | ❌ |

## 示例 1：配置 Ollama 本地模型

Ollama 是本地运行大模型的最简单方式。

### 安装并启动 Ollama

```bash
# macOS/Linux 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 拉取模型
ollama pull llama3
ollama pull nomic-embed-text  # 可选：嵌入模型

# 启动 Ollama 服务（默认 http://localhost:11434）
ollama serve
```

### 配置 .env

编辑 `docker/.env` 文件：

```bash
# 模型 0：本地 Ollama Llama3
MODEL_PROTOCOL_0=ollama
MODEL_ID_0=llama3
MODEL_API_KEY_0=
MODEL_NAME_0=Llama3 8B Local
MODEL_BASE_URL_0=http://host.docker.internal:11434/v1

# 嵌入模型（可选）
EMBEDDING_PROTOCOL=ollama
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_API_KEY=
EMBEDDING_BASE_URL=http://host.docker.internal:11434/api
```

> **注意**：在 Docker 容器内访问宿主机服务，需要使用 `host.docker.internal`（Docker Desktop）或宿主机的实际 IP 地址，不能使用 `localhost`。

### 重启服务

```bash
docker compose -f docker/docker-compose.yml restart coze-server
```

## 示例 2：配置 OpenAI 兼容 API

适用于 OpenAI 官方 API 或任何兼容 OpenAI 接口的代理服务。

```bash
# 模型 0：OpenAI GPT-4o
MODEL_PROTOCOL_0=openai
MODEL_ID_0=gpt-4o
MODEL_API_KEY_0=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MODEL_NAME_0=GPT-4o
MODEL_BASE_URL_0=https://api.openai.com/v1

# 模型 1：OpenAI GPT-4o-mini（备选/轻量模型）
MODEL_PROTOCOL_1=openai
MODEL_ID_1=gpt-4o-mini
MODEL_API_KEY_1=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MODEL_NAME_1=GPT-4o Mini
MODEL_BASE_URL_1=https://api.openai.com/v1
```

## 示例 3：配置火山引擎 Ark

```bash
MODEL_PROTOCOL_0=ark
MODEL_ID_0=ep-xxxxxxxxxxxxxxxxxx
MODEL_API_KEY_0=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MODEL_NAME_0=Doubao Pro
MODEL_BASE_URL_0=https://ark.cn-beijing.volces.com/api/v3
```

## 示例 4：多模型混合配置

同时配置本地 Ollama 和云端模型：

```bash
# 模型 0：本地 Ollama（日常开发测试）
MODEL_PROTOCOL_0=ollama
MODEL_ID_0=llama3
MODEL_API_KEY_0=
MODEL_NAME_0=Llama3 (Local)
MODEL_BASE_URL_0=http://host.docker.internal:11434/v1

# 模型 1：DeepSeek（复杂推理）
MODEL_PROTOCOL_1=deepseek
MODEL_ID_1=deepseek-chat
MODEL_API_KEY_1=sk-xxxxxxxxxxxxxxxx
MODEL_NAME_1=DeepSeek Chat
MODEL_BASE_URL_1=https://api.deepseek.com/v1

# 模型 2：OpenAI GPT-4o（高质量任务）
MODEL_PROTOCOL_2=openai
MODEL_ID_2=gpt-4o
MODEL_API_KEY_2=sk-xxxxxxxxxxxxxxxx
MODEL_NAME_2=GPT-4o
MODEL_BASE_URL_2=https://api.openai.com/v1
```

## 嵌入模型配置

知识库的文档向量化需要嵌入模型，支持 5 种后端：

```bash
# 使用 OpenAI 嵌入
EMBEDDING_PROTOCOL=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_KEY=sk-xxxxxxxxxxxxxxxx
EMBEDDING_BASE_URL=https://api.openai.com/v1

# 使用 Ollama 本地嵌入
EMBEDDING_PROTOCOL=ollama
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_API_KEY=
EMBEDDING_BASE_URL=http://host.docker.internal:11434/api

# 使用火山引擎 Ark 嵌入（默认）
EMBEDDING_PROTOCOL=ark
EMBEDDING_MODEL=ep-xxxxxxxxxx
EMBEDDING_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

## 验证配置

重启 `coze-server` 后，在 Web 界面中创建智能体，应能在模型选择下拉框中看到配置的模型名称（如 "Llama3 8B Local"、"GPT-4o" 等）。在 Playground 中发送消息测试模型是否正常响应。

## 相关文档

- [LLM 模型集成](/concepts/05-llm-integration.md)
- [可插拔基础设施](/concepts/04-pluggable-infrastructure.md)
- [Docker 快速入门](/examples/docker-quickstart.md)
- [配置基础设施](/examples/configure-infrastructure.md)
