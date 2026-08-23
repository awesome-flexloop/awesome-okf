---
okf_version: "0.2"
type: index
title: "handy-ollama 实战示例"
bundle: /datawhale/handy-ollama
---

# 实战示例

本目录包含 handy-ollama 的 3 个实战示例，从快速上手到自定义模型再到 RAG 应用，覆盖 Ollama 的核心使用场景。

## 示例列表

* [快速启动第一个本地模型](quickstart-first-model.md) — 从安装 Ollama 到 `ollama run llama3.1` 完成首次对话，包含 CLI 交互、curl REST API 调用和 Python 客户端调用三种方式，5 分钟跑通本地大模型。

* [使用 Modelfile 自定义模型](custom-model-modelfile.md) — 从 GGUF 文件创建自定义模型，配置 SYSTEM 提示词设定角色、PARAMETER 调优推理参数，通过 `ollama create` 构建专属模型并运行。

* [搭建本地 RAG 应用](local-rag-application.md) — 使用 LangChain + Ollama + FAISS 构建本地文档问答 RAG 应用，涵盖文档加载、文本分块、Ollama Embedding、向量检索、Prompt 组装和 LLM 生成全链路。
