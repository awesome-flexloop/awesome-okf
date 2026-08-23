---
okf_version: "0.2"
type: reference
title: "第五章 Ollama 在 LangChain 中的使用"
bundle: /datawhale/handy-ollama
sources:
  - https://github.com/datawhalechina/handy-ollama/blob/main/docs/C5/
tags: [chapter5, langchain, python, javascript, chain, tools, rag]
status: stable
---

# 第五章 Ollama 在 LangChain 中的使用

## 信源定位

- **源码路径**：`docs/C5/`（2 节）+ `notebook/C5/`（Python notebook + JavaScript 代码）
- **在线阅读**：[第五章](https://datawhalechina.github.io/handy-ollama/#/C5/)
- **内容性质**：框架集成，LangChain 双语言对接 Ollama

## 章节结构

| 节 | 文件 | 核心内容 |
|----|------|----------|
| 5.1 | `1. Ollama 在 LangChain 中的使用 - Python 集成.md` | langchain-ollama 包、ChatOllama、ChatPromptTemplate、LCEL 管道链、多模态、工具调用、JSON 输出、RAG 检索链 |
| 5.2 | `2. Ollama 在 LangChain 中的使用 - JavaScript 集成.md` | LangChain.js、@langchain/ollama、base_chat、advanced_prompt、base_tool、base_multimodal、advanced_json |

## 关键事实

- Python 集成包：`langchain-ollama`、`langchain`、`langchain-community`
- JavaScript 集成包：`@langchain/ollama`、`langchain`
- ChatOllama 初始化：`ChatOllama(model="llama3.1", temperature=0.7)`
- 使用 LCEL 管道操作符 `|` 组合 prompt 和 model：`chain = prompt | model`
- 支持多模态（Pillow 图像处理 + llava 模型）
- 支持工具调用（bind_tools）
- RAG 集成：OllamaEmbeddings + FAISS 向量库
- Conda 环境配置：`conda create -n handlm python=3.10`

## 代码资产

- `notebook/C5/ollama_langchain_python.ipynb`：Python 完整集成 notebook
- `notebook/C5/ollama_langchain_javascript/`：
  - `base_chat.js`：基础对话
  - `advanced_pormpt.js`：高级提示词
  - `base_tool.js`：工具调用
  - `base_multimodal.js`：多模态
  - `advanced_json.js`：JSON 结构化输出
- `notebook/C5/requirements.txt`：Python 依赖清单

## 关联概念

- [WebUI 与工具集成](../concepts/webui-tool-integration.md) — LangChain 集成的概念整理
- [API 与 OpenAI 兼容接口](../concepts/api-openai-compatibility.md) — LangChain 底层调用的 API 基础
- [搭建本地 RAG 应用](../examples/local-rag-application.md) — LangChain RAG 实战
