---
okf_version: "0.2"
type: index
title: "handy-ollama：动手学 Ollama 本地大模型部署"
bundle: handy-ollama
description: "Datawhale 开源的 Ollama 系统教程——从四平台安装到 Modelfile 自定义模型，从 REST API 到 OpenAI 兼容层，从 LangChain/LlamaIndex 集成到 WebUI/Dify/RAG/Agent 应用，CPU 也能玩转本地大模型部署"
concepts:
  - /datawhale/handy-ollama/concepts/ollama-architecture-installation
  - /datawhale/handy-ollama/concepts/model-management-modelfile
  - /datawhale/handy-ollama/concepts/api-openai-compatibility
  - /datawhale/handy-ollama/concepts/webui-tool-integration
  - /datawhale/handy-ollama/concepts/production-deployment
references:
  - /datawhale/handy-ollama/references/chapter1-introduction
  - /datawhale/handy-ollama/references/chapter2-installation
  - /datawhale/handy-ollama/references/chapter3-customization
  - /datawhale/handy-ollama/references/chapter4-rest-api
  - /datawhale/handy-ollama/references/chapter5-langchain
  - /datawhale/handy-ollama/references/chapter6-webui
  - /datawhale/handy-ollama/references/chapter7-applications
examples:
  - /datawhale/handy-ollama/examples/quickstart-first-model
  - /datawhale/handy-ollama/examples/custom-model-modelfile
  - /datawhale/handy-ollama/examples/local-rag-application
sources: https://github.com/datawhalechina/handy-ollama
generated:
  by: okf-wiki-bot
  at: "2026-08-23T00:00:00Z"
verified:
  by: process:seven-concepts-v
  at: "2026-08-23T00:00:00Z"
status: stable
stale_after: "2027-08-23"
---

# handy-ollama：动手学 Ollama 本地大模型部署

[handy-ollama](https://github.com/datawhalechina/handy-ollama) 是 Datawhale 开源的系统性 Ollama 教程，于 2025.11.06 被 Ollama 官方仓库收录为唯一 Tutorial。教程定位"从零开始实现 CPU 玩转大模型部署"，覆盖从四平台安装、Modelfile 自定义模型、REST API 与 OpenAI 兼容接口，到 LangChain/LlamaIndex 集成、WebUI/Dify 可视化部署、RAG/Agent 应用的完整链路，让没有 GPU 的学习者也能在个人 PC 上部署和运行大模型。

## 知识地图

```
🚀 入门部署（第1-2章）
  ├── Ollama 介绍 → 开源 LLM 服务工具、自动资源探测、Modelfile 打包
  └── 四平台安装 → macOS / Windows / Linux / Docker 统一体验
        ↓
⚙️ 自定义配置（第3章）
  ├── 自定义导入模型 → GGUF / Safetensors / 模型直接导入 / 自定义 Prompt
  ├── 自定义模型存储位置 → OLLAMA_MODELS 环境变量、跨平台路径迁移
  └── 自定义 GPU 运行 → CUDA / ROCm 加速、多 GPU 指定
        ↓
🔌 API 与生态（第4-5章）
  ├── REST API → /api/generate、/api/chat、/api/embed、流式/JSON/多模态
  ├── 多语言 SDK → Python / Java / JavaScript / C++ / Golang
  └── LangChain 集成 → Python / JavaScript、Chain、工具调用、RAG
        ↓
🌐 界面与应用（第6-7章）
  ├── 可视化界面 → FastAPI+WebSocket / Open WebUI (Docker)
  ├── 平台集成 → Dify 低代码、Continue AI Copilot
  └── 应用案例 → LangChain/LlamaIndex RAG、Agent、DeepSeek R1 RAG
```

## 核心概念（concepts/）

* [Ollama 架构与安装](concepts/ollama-architecture-installation.md) — Ollama 定位与核心特性、自动 GPU/CPU 资源探测、四平台（macOS/Windows/Linux/Docker）安装配置、默认端口 11434、常用 CLI 命令体系。
* [模型管理与 Modelfile](concepts/model-management-modelfile.md) — Modelfile 模型打包机制（FROM/SYSTEM/PARAMETER 指令）、GGUF/Safetensors 导入、ollama create/pull/list/ps/rm 命令、OLLAMA_MODELS 存储路径、GPU 加速配置。
* [API 与 OpenAI 兼容接口](concepts/api-openai-compatibility.md) — REST API 端点（/api/generate、/api/chat、/api/embed）、流式/非流式响应、JSON 模式、多模态 images 参数、工具调用 tools、OpenAI 兼容层（/v1/chat/completions）、多语言 SDK。
* [WebUI 与工具集成](concepts/webui-tool-integration.md) — FastAPI+WebSocket 自建可视化界面、Open WebUI Docker 部署、LangChain（Python/JS）集成、LlamaIndex 集成、Dify 低代码平台接入、Continue AI Copilot 编程助手。
* [生产部署实践](concepts/production-deployment.md) — Docker 容器化部署、GPU 调度与多模型管理、RAG 检索增强生成（LangChain/LlamaIndex/DeepSeek R1）、Agent 工具调用、本地隐私保护、从单模型到多模型服务的应用栈。

## 实战示例（examples/）

* [快速启动第一个本地模型](examples/quickstart-first-model.md) — 从安装 Ollama 到 `ollama run llama3.1` 完成首次对话，含 CLI 交互、REST API 调用和 Python 调用三种方式。
* [使用 Modelfile 自定义模型](examples/custom-model-modelfile.md) — 从 GGUF 文件创建自定义模型，配置 SYSTEM 提示词和 PARAMETER 参数，构建专属角色模型。
* [搭建本地 RAG 应用](examples/local-rag-application.md) — 使用 LangChain + Ollama + FAISS 构建本地文档问答 RAG 应用，含文档加载、分块、嵌入、检索和生成全链路。

## 信源登记（references/）

* [第一章 Ollama 介绍](references/chapter1-introduction.md) — Ollama 定义、九大特点、支持模型列表、常用命令。
* [第二章 Ollama 安装与配置](references/chapter2-installation.md) — macOS/Windows/Linux/Docker 四平台安装与配置。
* [第三章 自定义使用 Ollama](references/chapter3-customization.md) — 自定义导入模型、模型存储位置、GPU 运行配置。
* [第四章 Ollama REST API](references/chapter4-rest-api.md) — API 使用指南、Python/Java/JavaScript/C++/Golang 多语言调用。
* [第五章 Ollama 在 LangChain 中的使用](references/chapter5-langchain.md) — Python/JavaScript 双语言 LangChain 集成。
* [第六章 Ollama 可视化界面部署](references/chapter6-webui.md) — FastAPI 部署、WebUI (Open WebUI) 部署。
* [第七章 应用案例](references/chapter7-applications.md) — AI Copilot、Dify 接入、LangChain/LlamaIndex RAG/Agent、DeepSeek R1 RAG。

## 深度洞察

本知识包的设计决策与核心洞察详见 [spec/insights.md](spec/insights.md)，包括：

1. **本地大模型部署的极简路径**——自动资源探测+GGUF量化+四平台统一，将 GPU 专属的 LLM 部署民主化到 CPU 消费级硬件
2. **OpenAI 兼容层的生态枢纽价值**——Ollama 的护城河不是推理性能，而是作为本地 AI 基础设施让现有工具链即插即用
3. **从单模型到多模型服务的应用栈跃迁**——Modelfile 抽象实现模型即代码，6级能力递进构成完整本地 AI 应用运行时

## 目录结构

```
handy-ollama/
├── spec/
│   ├── facts.md              # 章节结构与关键事实清单（25+ 事实）
│   └── insights.md           # 3 个核心设计洞察
├── concepts/                 # 5 个核心概念
│   ├── index.md
│   ├── ollama-architecture-installation.md
│   ├── model-management-modelfile.md
│   ├── api-openai-compatibility.md
│   ├── webui-tool-integration.md
│   └── production-deployment.md
├── examples/                 # 3 个实战示例
│   ├── index.md
│   ├── quickstart-first-model.md
│   ├── custom-model-modelfile.md
│   └── local-rag-application.md
├── references/               # 7 章信源登记
│   ├── index.md
│   └── chapter1-7 ... .md
├── index.md                  # 本文件
└── log.md                    # 更新日志
```

---

> **源码位置**：`external/libs/ai/datawhalechina/handy-ollama/`
>
> **在线阅读**：https://datawhalechina.github.io/handy-ollama/
>
> **官方收录**：2025.11.06 被 Ollama 官方仓库收录为唯一 Tutorial
>
> **开源协议**：CC BY-NC-SA 4.0
>
> **生成时间**：2026-08-23 | **维护者**：OKF Wiki Bot

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
