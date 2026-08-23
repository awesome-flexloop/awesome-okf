---
okf_version: "0.2"
type: reference
title: "第七章 应用案例"
bundle: /datawhale/handy-ollama
sources:
  - https://github.com/datawhalechina/handy-ollama/blob/main/docs/C7/
tags: [chapter7, applications, copilot, dify, rag, agent, deepseek, langchain, llamaindex]
status: stable
---

# 第七章 应用案例

## 信源定位

- **源码路径**：`docs/C7/`（7 节）+ `notebook/C7/`（5 个应用案例代码）
- **在线阅读**：[第七章](https://datawhalechina.github.io/handy-ollama/#/C7/)
- **内容性质**：实战应用，7 个从编程助手到 RAG/Agent 的完整案例

## 章节结构

| 节 | 文件 | 核心内容 | 代码资产 |
|----|------|----------|----------|
| 7.1 | `1. 搭建本地的 AI Copilot 编程助手.md` | Continue 插件接入 Ollama，VS Code/JetBrains 本地代码补全与对话 | - |
| 7.2 | `2. Dify 接入 Ollama 部署的本地模型.md` | Dify 模型供应商配置、LLM/Embedding 接入、Docker 网络问题排查 | - |
| 7.3 | `3. 使用 LangChain 搭建本地 RAG 应用.md` | 文档加载、分块、向量检索、Ollama LLM 生成 | `notebook/C7/LangChain_RAG/` |
| 7.4 | `4. 使用 LlamaIndex 搭建本地 RAG 应用.md` | LlamaIndex 查询引擎、react/openai agent 模式、数据索引 | `notebook/C7/LlamaIndex_RAG/`（含 app.py + data/dw.txt） |
| 7.5 | `5. 使用 LangChain 实现本地 Agent.md` | ReAct 推理-行动循环、工具注册、本地 Agent | `notebook/C7/LangChain_Agent/` |
| 7.6 | `6. 使用 LlamaIndex 实现本地 Agent.md` | LlamaIndex Agent、工具调用、查询引擎工具 | `notebook/C7/LlamaIndex_Agent/` |
| 7.7 | `7. 使用 DeepSeek R1 和 Ollama 实现本地 RAG 应用.md` | DeepSeek R1 推理模型、PDF 解析、RAG 结合思维链 | `notebook/C7/DeepSeek_R1_RAG/`（含 DeepSeek_R1.pdf + app.py） |

## 关键事实

### AI Copilot 编程助手

- Continue 是开源 AI 编程助手，支持 VS Code 和 JetBrains IDE
- 支持本地模型（LM Studio/Ollama）及任何 OpenAI 兼容接口
- 支持多种提供商：OpenRouter/Anthropic/OpenAI/Google Gemini/AWS Bedrock/Azure 等

### Dify 接入

- Dify 中路径：`设置 > 模型供应商 > Ollama`
- 基础 URL：`http://<ollama-endpoint>:11434`
- Docker 部署 Dify 时不能用 localhost（指向容器自身），需用局域网 IP（`http://192.168.x.x:11434`）或宿主机 IP（`http://172.17.0.1:11434`）
- 支持同时接入 LLM（对话类型）和 Embedding（文本嵌入类型）模型
- Ollama 需暴露网络访问（设置 OLLAMA_HOST=0.0.0.0）

### RAG 应用

- LangChain RAG：文档加载器 → TextSplitter 分块 → OllamaEmbeddings → FAISS 向量库 → 检索 → Prompt → ChatOllama
- LlamaIndex RAG：SimpleDirectoryReader → VectorStoreIndex → OllamaEmbedding → query_engine → Ollama LLM
- LlamaIndex 查询引擎支持 `best`（默认）、`react`、`openai` 三种 agent 模式
- DeepSeek R1 模型输出含 `<think>...</think>` 思维链过程，适合复杂推理

### Agent 应用

- LangChain Agent：通过 `@tool` 装饰器注册工具，`bind_tools` 绑定到 LLM，ReAct 循环
- LlamaIndex Agent：将查询引擎和函数注册为工具，Agent 自主选择工具完成任务

### DeepSeek R1

- 轻量版：`ollama pull deepseek-r1:1.5b`
- 完整版：`ollama pull deepseek-r1`（671B，需 404GB）
- DeepSeek R1 是深度推理模型，先输出思维链再给出答案

## 代码资产汇总

- `notebook/C7/DeepSeek_R1_RAG/`：DeepSeek R1 RAG 完整应用（含 PDF 和 app.py）
- `notebook/C7/LangChain_Agent/`：LangChain Agent notebook
- `notebook/C7/LangChain_RAG/`：LangChain RAG notebook
- `notebook/C7/LlamaIndex_Agent/`：LlamaIndex Agent notebook
- `notebook/C7/LlamaIndex_RAG/`：LlamaIndex RAG 应用（app.py + 数据文件）

## 关联概念

- [生产部署实践](../concepts/production-deployment.md) — RAG/Agent 架构和生产配置
- [WebUI 与工具集成](../concepts/webui-tool-integration.md) — Dify、Continue 等平台集成方式
- [搭建本地 RAG 应用](../examples/local-rag-application.md) — LangChain RAG 完整可运行示例
