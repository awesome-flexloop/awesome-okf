---
type: example
title: "搭建本地 RAG 应用"
bundle: /datawhale/handy-ollama
description: "使用 LangChain + Ollama + FAISS 构建本地文档问答应用，涵盖文档加载、分块、嵌入、检索和生成全链路"
sources: https://github.com/datawhalechina/handy-ollama/tree/main/notebook/C7
related:
  - /datawhale/handy-ollama/concepts/production-deployment
  - /datawhale/handy-ollama/concepts/webui-tool-integration
  - /datawhale/handy-ollama/concepts/api-openai-compatibility
  - /datawhale/handy-ollama/references/chapter7-applications
tags: [rag, langchain, faiss, embeddings, document-qa, retrieval]
status: stable
---

# 搭建本地 RAG 应用

## 目标

使用 LangChain + Ollama + FAISS 构建一个完全本地运行的文档问答 RAG（检索增强生成）应用。所有数据处理都在本地完成，无需调用云端 API，保护数据隐私。

## 前置条件

- 已安装 Ollama 并拉取以下模型：
  ```bash
  ollama pull llama3.1
  ollama pull nomic-embed-text
  ```
- Python 3.10+ 环境
- 一份待问答的文本文档（如 `data.txt`）

## RAG 架构原理

```
文档 → 加载 → 分块 → 嵌入 → 向量库
                                ↓
用户问题 → 嵌入 → 向量检索(Top-K) → Prompt组装 → LLM生成 → 回答
```

RAG 的核心思想：先从文档中检索与问题相关的片段，将这些片段作为上下文提供给 LLM，让 LLM 基于检索到的内容回答，而非依赖模型参数中的知识。

## 步骤一：安装依赖

```bash
pip install langchain langchain-ollama langchain-community faiss-cpu
```

依赖说明：

| 包 | 作用 |
|----|------|
| `langchain` | LLM 应用框架核心 |
| `langchain-ollama` | Ollama 的 LangChain 集成（LLM + Embedding） |
| `langchain-community` | 社区集成（文档加载器、向量库等） |
| `faiss-cpu` | Facebook 开源向量相似度搜索库 |

## 步骤二：完整代码实现

创建 `local_rag.py`：

```python
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


def create_rag_chain(doc_path: str = "data.txt"):
    # 1. 加载文档
    loader = TextLoader(doc_path, encoding="utf-8")
    documents = loader.load()

    # 2. 文本分块
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""]
    )
    splits = text_splitter.split_documents(documents)
    print(f"文档已分为 {len(splits)} 个文本块")

    # 3. 创建嵌入和向量库
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = FAISS.from_documents(splits, embeddings)
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    # 4. 初始化 LLM
    llm = ChatOllama(
        model="llama3.1",
        temperature=0.1,
        num_ctx=4096
    )

    # 5. 定义 Prompt 模板
    prompt = ChatPromptTemplate.from_template("""
你是一个文档问答助手。请根据以下检索到的文档内容回答用户的问题。
如果文档内容中没有相关信息，请明确说明"根据现有文档无法回答该问题"，不要编造答案。

检索到的文档内容：
{context}

用户问题：{question}

请给出准确、简洁的回答：
""")

    # 6. 构建 RAG 链（LCEL 语法）
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever


def main():
    rag_chain, retriever = create_rag_chain("data.txt")

    # 交互式问答
    print("本地 RAG 文档问答系统已启动（输入 'quit' 退出）")
    print("-" * 50)

    while True:
        question = input("\n请输入问题：").strip()
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue

        # 可选：查看检索到的文档片段
        # retrieved_docs = retriever.invoke(question)
        # for i, doc in enumerate(retrieved_docs):
        #     print(f"\n[检索片段 {i+1}] {doc.page_content[:100]}...")

        print("\n正在检索并生成回答...")
        response = rag_chain.invoke(question)
        print(f"\n回答：{response}")


if __name__ == "__main__":
    main()
```

## 步骤三：准备测试文档

创建 `data.txt`，放入一些专属内容（如项目文档、个人笔记等），例如：

```text
handy-ollama 是 Datawhale 开源的动手学 Ollama 教程，于2025年11月6日被 Ollama 官方仓库收录。
教程共7章，覆盖 Ollama 介绍、安装配置、自定义使用、REST API、LangChain集成、可视化界面和应用案例。
Ollama 默认 API 端口为 11434，支持的模型包括 Llama3.1、DeepSeek-R1、Qwen2、Gemma2 等。
运行7B模型至少需要8GB内存，运行13B模型至少需要16GB内存。
Modelfile 是 Ollama 的模型打包格式，类似 Dockerfile，通过 FROM 指令指定模型来源。
```

## 步骤四：运行应用

```bash
python local_rag.py
```

交互示例：

```
本地 RAG 文档问答系统已启动（输入 'quit' 退出）
--------------------------------------------------
文档已分为 3 个文本块

请输入问题：handy-ollama 是什么时候被官方收录的？

正在检索并生成回答...

回答：handy-ollama 于2025年11月6日被 Ollama 官方仓库收录。

请输入问题：Ollama 默认端口是多少？

正在检索并生成回答...

回答：Ollama 默认 API 端口为 11434。
```

## 关键参数调优

### 分块参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `chunk_size` | 300-1000 | 文本块大小（字符数），需匹配模型上下文窗口 |
| `chunk_overlap` | 50-200 | 块间重叠，避免语义被截断 |
| `separators` | 按段落/句子 | 中文优先按 `\n\n`、`。`、`！` 分割 |

### 检索参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `k` | 3-5 | 检索返回的相关片段数量 |
| `search_type` | `similarity` | `similarity`（相似度）或 `mmr`（最大边际相关性，去冗余） |

### LLM 参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `temperature` | 0.0-0.2 | RAG 场景低温度保证事实准确性 |
| `num_ctx` | 4096+ | 上下文窗口需容纳 system prompt + 检索片段 + 问题 |

## 扩展：支持 PDF 文档

安装 PDF 加载器：

```bash
pip install pypdf
```

修改文档加载部分：

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("document.pdf")
documents = loader.load()
```

## 扩展：持久化向量库

避免每次重新嵌入文档，将 FAISS 索引保存到本地：

```python
# 首次创建后保存
vectorstore.save_local("faiss_index")

# 后续加载
from langchain_ollama import OllamaEmbeddings
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = FAISS.load_local("faiss_index", embeddings)
```

## 验证结果

成功标志：

1. 文档成功分块并创建 FAISS 索引（无报错）
2. 针对文档内容的提问能得到基于文档的准确回答
3. 文档中没有的信息，模型会说明"无法回答"而非编造
4. 整个过程无需互联网连接（模型已下载到本地）

## 常见问题

**Q: 检索不到相关内容？**
A: 调整 `chunk_size`（过小会丢失上下文，过大引入噪声）和 `k` 值；检查嵌入模型是否正确下载。

**Q: 回答出现幻觉？**
A: 降低 `temperature` 到 0.0-0.1；在 Prompt 中明确要求"仅基于文档内容回答"；增加检索片段数量 `k`。

**Q: 中文分块效果差？**
A: 使用中文友好的分隔符顺序 `["\n\n", "\n", "。", "！", "？", ""]`；或尝试中文语义分块器。

**Q: 内存不足？**
A: 使用更小的 LLM（如 `llama3.2:1b`）和嵌入模型；减小 `chunk_size` 和 `k`。

## 延伸阅读

- RAG 架构原理和生产部署 → [生产部署实践](../concepts/production-deployment.md)
- API 端点和嵌入接口详情 → [API 与 OpenAI 兼容接口](../concepts/api-openai-compatibility.md)
- LangChain 集成和工具调用 → [WebUI 与工具集成](../concepts/webui-tool-integration.md)
- LlamaIndex RAG 和 Agent 实现方式 → 参考 [第七章应用案例](../references/chapter7-applications.md)
