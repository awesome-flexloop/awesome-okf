---
okf_version: "0.2"
type: index
title: "handy-ollama 信源登记"
bundle: /datawhale/handy-ollama
sources: https://github.com/datawhalechina/handy-ollama
---

# 信源登记簿

本目录登记 handy-ollama 知识束所有内容据以派生的源码文档信源。所有概念文档和示例文档的 `sources` 字段均指向对应的 GitHub 源码章节。信源基于 handy-ollama 仓库 `docs/` 目录下的 7 章 Markdown 文档，与 `docs/_sidebar.md` 章节导航完全一致。

## 章节目录

* [第一章 Ollama 介绍](chapter1-introduction.md) — `docs/C1/1. Ollama 介绍.md`：Ollama 定义与九大特点、支持模型列表（DeepSeek-R1/Llama3.x/Gemma2/Qwen2 等）、常用 CLI 命令（serve/run/pull/create/list/ps/rm）。
* [第二章 Ollama 安装与配置](chapter2-installation.md) — `docs/C2/`：macOS/Windows/Linux/Docker 四平台安装与配置，含 Docker 镜像拉取、端口映射、GPU 支持。
* [第三章 自定义使用 Ollama](chapter3-customization.md) — `docs/C3/`：自定义导入模型（GGUF/Safetensors/模型直接导入/自定义 Prompt）、自定义模型存储位置（OLLAMA_MODELS）、自定义 GPU 运行（CUDA/ROCm）。
* [第四章 Ollama REST API](chapter4-rest-api.md) — `docs/C4/`：API 使用指南（generate/chat/embed 端点）、Python/Java/JavaScript/C++/Golang 多语言调用示例。
* [第五章 Ollama 在 LangChain 中的使用](chapter5-langchain.md) — `docs/C5/`：Python 集成（langchain-ollama、ChatPromptTemplate、多模态、工具调用、RAG）、JavaScript 集成。
* [第六章 Ollama 可视化界面部署](chapter6-webui.md) — `docs/C6/`：FastAPI+WebSocket 自建可视化对话界面、Open WebUI（Node.js/Docker 两种部署方式）。
* [第七章 应用案例](chapter7-applications.md) — `docs/C7/`：AI Copilot 编程助手、Dify 接入本地模型、LangChain/LlamaIndex RAG、LangChain/LlamaIndex Agent、DeepSeek R1+RAG 七个实战案例。

```{toctree}
:hidden:

chapter1-introduction
chapter2-installation
chapter3-customization
chapter4-rest-api
chapter5-langchain
chapter6-webui
chapter7-applications
```
