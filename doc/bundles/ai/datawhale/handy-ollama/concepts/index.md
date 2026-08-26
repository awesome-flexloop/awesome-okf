---
okf_version: "0.2"
type: index
title: "handy-ollama 核心概念"
bundle: /datawhale/handy-ollama
---

# 核心概念

本目录包含 handy-ollama 的 5 个核心概念文档，按学习路径排列：从架构安装到模型管理，从 API 接口到生态集成，最终到生产部署实践。

## 入门基础

* [Ollama 架构与安装](ollama-architecture-installation.md) — Ollama 定位与九大特点、自动 GPU/CPU 资源探测、macOS/Windows/Linux/Docker 四平台安装配置、默认端口 11434、serve/run/pull/list 等 CLI 命令体系。

## 模型管理

* [模型管理与 Modelfile](model-management-modelfile.md) — Modelfile 模型打包机制（FROM/SYSTEM/PARAMETER 指令）、GGUF/Safetensors 三种导入方式、ollama create/pull/push/list/ps/rm/cp 全生命周期命令、OLLAMA_MODELS 存储路径配置、CUDA/ROCm GPU 加速。

## API 接口

* [API 与 OpenAI 兼容接口](api-openai-compatibility.md) — REST API 端点（/api/generate、/api/chat、/api/embed）、流式与非流式响应、JSON 结构化输出、多模态 images 参数、tools 工具调用、OpenAI 兼容层（/v1/chat/completions）、Python/Java/JS/C++/Golang 多语言 SDK。

## 生态集成

* [WebUI 与工具集成](webui-tool-integration.md) — FastAPI+WebSocket 自建可视化对话界面、Open WebUI Docker 一行部署、LangChain（Python/JavaScript）Chain 与工具调用、LlamaIndex 查询引擎、Dify 低代码平台接入、Continue AI Copilot 编程助手。

## 生产实践

* [生产部署实践](production-deployment.md) — Docker 容器化部署与网络配置、GPU 调度与多模型并发管理、RAG 检索增强生成（LangChain/LlamaIndex/DeepSeek R1）、Agent ReAct 工具调用、本地隐私保护优势、从单模型到多模型服务的完整应用栈。

```{toctree}
:hidden:
:maxdepth: 7

api-openai-compatibility
model-management-modelfile
ollama-architecture-installation
production-deployment
webui-tool-integration
```
