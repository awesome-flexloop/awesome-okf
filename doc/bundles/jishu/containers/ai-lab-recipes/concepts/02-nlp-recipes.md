---
type: Concept
title: NLP配方概览
description: natural_language_processing 目录下的各类NLP应用：Chatbot、RAG、Agent、Codegen、Function Calling、Summarizer
tags: [NLP, Chatbot, RAG, Agent, 代码生成, 函数调用]
generated: { by: "trae-ai", at: "2026-08-26T08:09:00Z" }
verified: { by: "process:source-code-to-okf-wiki", at: "2026-08-26T08:09:00Z" }
status: stable
stale_after: 2027-08-26
sources:
  - id: S-001
    resource: /references/readme-source.md
    title: 项目根目录 README.md
---

# NLP配方概览

自然语言处理（NLP）是 ai-lab-recipes 中最丰富的配方类别，位于 `recipes/natural_language_processing/` 目录下，覆盖了从基础聊天到智能体、RAG 等多种常见 LLM 应用场景。

## 配方列表

| 配方 | 目录 | 技术栈 | 核心能力 | 多语言版本 |
|------|------|--------|---------|-----------|
| Chatbot | `chatbot/` | Python + LangChain + Streamlit | 基础对话交互 | Python/Java Quarkus/Node.js/Llama-Stack/Pydantic-AI |
| RAG | `rag/` | Python + LangChain + ChromaDB/Milvus | 检索增强生成 | Python/Node.js |
| Graph RAG | `graph-rag/` | Python + 图数据库 | 知识图谱增强RAG | Python |
| Agents | `agents/` | Python + ReAct | 智能体推理 | Python |
| Codegen | `codegen/` | Python + Streamlit | 代码生成 | Python（含VS Code集成） |
| Function Calling | `function_calling/` | Python/Node.js | 工具函数调用 | Python/Node.js |
| Summarizer | `summarizer/` | Python | 文本摘要 | Python |

## Chatbot（聊天机器人）

Chatbot 是最基础的配方，提供 LLM 对话交互界面。

**架构特点**：
- 默认使用 Python + LangChain + Streamlit 技术栈
- 通过 OpenAI 兼容 API 连接 llamacpp_python 模型服务器
- 支持多轮对话上下文
- 提供 Web UI（http://localhost:8501）

**多语言变体**：
- `chatbot/`：标准 Python 版本
- `chatbot-java-quarkus/`：Java Quarkus 后端版本
- `chatbot-nodejs/`：Node.js + Next.js 全栈版本
- `chatbot-llama-stack/`：基于 Llama Stack 的版本
- `chatbot-pydantic-ai/`：使用 Pydantic AI 框架的版本

**典型部署**：支持 Quadlet/Kubernetes YAML、Bootc 可启动容器、Ansible 自动化部署。

## RAG（检索增强生成）

RAG 配方在 Chatbot 基础上增加了文档检索能力，使 LLM 能够基于私有文档回答问题。

**架构特点**：
- 三组件架构：模型服务器 + 向量数据库 + AI应用
- 支持两种向量数据库：ChromaDB（轻量）、Milvus（生产级）
- 需要两个模型：LLM（生成回答）+ Embedding 模型（向量化文档，如 BAAI/bge-base-en-v1.5）
- 支持文档上传和向量库管理
- 提供 `manage_vectordb.py` 工具管理向量数据库

**数据流**：
1. 用户上传文档（PDF/TXT）
2. Embedding 模型将文档转换为向量
3. 向量存储在 ChromaDB/Milvus 中
4. 用户提问时，检索相关文档片段
5. LLM 基于检索到的上下文生成回答

**多语言变体**：
- `rag/`：Python 版本
- `rag-nodejs/`：Node.js + Next.js 版本

## Agents（智能体）

Agents 配方实现了 ReAct（Reasoning + Acting）模式的智能体。

**架构特点**：
- 基于 ReAct 框架：思考→行动→观察循环
- 支持工具调用和推理链
- 可扩展自定义工具

**核心文件**：`app/react-agent-app.py`

## Codegen（代码生成）

Codegen 配方专注于代码生成场景，提供代码生成和辅助编程能力。

**特点**：
- 专门优化的代码生成 UI
- 提供 VS Code 扩展集成指南（`llms-vscode-integration.md`）
- 支持多种编程语言代码生成

## Function Calling（函数调用）

Function Calling 配方展示 LLM 的工具调用能力。

**多语言变体**：
- `function_calling/`：Python 版本（天气工具示例）
- `function-calling-nodejs/`：Node.js 版本

## Summarizer（摘要）

Summarizer 配方提供长文本摘要能力。

## NLP 应用通用模式

所有 NLP 配方共享以下设计模式：

### 目录结构规范

每个 NLP 应用目录包含：
```
<recipe-name>/
├── app/                     # 应用代码
│   ├── Containerfile        # 应用容器构建文件
│   ├── *.py                 # 应用主程序
│   └── requirements.txt     # Python依赖
├── quadlet/                 # Podman Quadlet systemd配置
│   ├── <name>.image
│   ├── <name>.kube
│   └── <name>.yaml          # Kubernetes YAML
├── bootc/                   # Bootable Containers配置
│   ├── Containerfile
│   └── README.md
├── provision/               # Ansible自动化部署
│   ├── playbook.yml
│   └── requirements.yml
├── Makefile                 # 构建脚本
├── ai-lab.yaml              # AI Lab扩展元数据
└── README.md                # 使用说明
```

### Makefile 标准目标

所有配方通过统一的 Makefile 提供标准化操作：

```bash
make build          # 构建应用镜像
make run            # 运行应用容器
make quadlet        # 生成Quadlet/Kubernetes YAML
make bootc          # 构建可启动容器镜像
```

### 环境变量配置

应用通过环境变量连接模型服务器：
- `MODEL_ENDPOINT`：模型服务器 API 地址（如 http://10.88.0.1:8001）
- `VECTORDB_HOST`：向量数据库地址（RAG场景）
- `VECTORDB_PORT`：向量数据库端口
- `VECTORDB_VENDOR`：向量数据库类型（chroma/milvus）

## 相关概念

- [配方架构概览](00-introduction.md)：理解双容器整体架构
- [模型服务器选型](01-model-servers.md)：了解支撑这些NLP应用的模型服务器
- [部署方式](03-deployment.md)：学习Quadlet、Bootc、Ansible等部署方式
