---
type: concept
title: "RAG 与知识检索模式"
description: "检索增强生成（RAG）的 Cookbook 实践模式：基础 RAG 流程、文档切分策略、向量数据库集成（Pinecone）、上下文嵌入优化、知识图谱增强、RAG 质量评估、Wikipedia/Web 数据源集成。"
tags: [rag, retrieval-augmented-generation, embeddings, vector-database, pinecone, knowledge-graph, contextual-embeddings, wikipedia]
generated: { by: "process:content-structuring", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
---

# RAG 与知识检索模式

**RAG（Retrieval-Augmented Generation，检索增强生成）** 是让 Claude 使用你自己的私有知识库回答问题的标准架构。Cookbooks 中提供了从最简单的"Hello RAG"到生产级知识图谱增强 RAG 的完整示例，本文提炼其中的可复用模式。

RAG 解决的核心问题是：**Claude 的训练数据有截止日期，且不知道你的私有文档**——RAG 通过"先检索，再生成"的方式，让 Claude 能基于最新的、私有的、特定领域的知识回答问题。

## RAG 核心概念

### 为什么需要 RAG？

| 方式 | 适用场景 | 局限性 |
|------|---------|--------|
| 直接问 Claude | 常识、通用知识、推理 | 不知道你的私有数据，训练数据有截止日期 |
| 微调（Fine-tuning） | 风格定制、格式模仿 | 成本高、更新难、不适合知识注入 |
| **RAG** | **私有知识库问答、文档问答、最新信息** | **需要搭建检索管线，但效果最好最灵活** |

### RAG 的核心思想

RAG 本质上是"开卷考试"：

```
闭卷考试（无 RAG）：
  学生（Claude）凭记忆答题 → 不知道的就瞎编（幻觉）

开卷考试（有 RAG）：
  1. 学生先翻书（检索）找到相关章节
  2. 然后根据找到的内容答题（生成）
  3. 答案可以溯源到具体页码
```

## 基础 RAG 流程

Cookbook 中所有 RAG 示例都遵循同一个标准两阶段流程：

```
┌─────────────────────────────────────────────────────────────────┐
│                    阶段一：索引（离线，一次性/定期）             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  原始文档 → 文档切分 → 嵌入生成 → 存入向量数据库               │
│              ↓          ↓          ↓                            │
│         Chunking   Embedding   Vector Store                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    阶段二：查询（在线，每次提问）                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  用户问题 → 问题嵌入 → 向量检索 → 相关上下文 → Claude 生成答案  │
│              ↓          ↓          ↓           ↓                │
│         Embedding  Similarity   Top-K    拼接上下文 → 回答     │
│                          Search                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 最小可运行 RAG 示例

这是 Cookbook 风格的"Hello RAG"骨架，不需要外部向量数据库：

```python
from anthropic import Anthropic
import numpy as np
from typing import list

client = Anthropic()

# ============ 阶段一：索引 ============

# 假设我们有一些文档
documents = [
    "Claude 3.5 Sonnet 发布于 2024 年 6 月，上下文窗口 200K tokens。",
    "Prompt Caching 可以缓存系统提示和工具定义，降低成本最多 90%。",
    "Extended Thinking 让 Claude 进行更长的链式思考，适合复杂推理任务。",
    "Tool Use（Function Calling）允许 Claude 调用外部工具和 API。",
]

# 使用 Claude 的嵌入 API（或 Voyage AI，见后文）
def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="claude-3-5-sonnet-20241022",  # 或专门的嵌入模型
        input=text
    )
    return response.embeddings[0].embedding

# 为所有文档生成嵌入（实际项目中存入向量数据库）
doc_embeddings = [get_embedding(doc) for doc in documents]

# ============ 阶段二：查询 ============

def cosine_similarity(a: list[float], b: list[float]) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve(query: str, top_k: int = 2) -> list[str]:
    """检索相关文档"""
    query_emb = get_embedding(query)
    similarities = [cosine_similarity(query_emb, doc_emb) for doc_emb in doc_embeddings]
    # 取最相关的 top_k 个
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return [documents[i] for i in top_indices]

def answer_question(question: str) -> str:
    """基于检索到的上下文回答问题"""
    context_docs = retrieve(question)
    context = "\n\n".join(context_docs)
    
    prompt = f"""基于以下参考资料回答用户问题。如果参考资料中没有答案，请说"根据现有资料无法回答"，不要编造。

参考资料：
{context}

用户问题：{question}

回答："""

    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

# 使用
print(answer_question("Prompt Caching 有什么作用？"))
```

这个骨架展示了 RAG 的核心思想，生产环境需要替换为专业的向量数据库。

## 文档切分（Chunking）模式

文档切分是 RAG 效果好坏的**最关键因素**——切分不好，嵌入再好也检索不到正确内容。Cookbook 中展示了多种切分策略：

### 切分策略对比

| 策略 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **固定长度切分** | 通用、快速 | 简单、可预测 | 可能切断句子/段落 |
| **语义切分** | 结构化文档 | 按语义边界切，连贯性好 | 稍复杂 |
| **按结构切分** | Markdown/HTML/代码 | 按标题/段落/函数切 | 需要格式解析 |
| **句子窗口** | 需要精确上下文 | 检索小片段，扩展前后文 | 需要额外处理 |

### Cookbook 推荐的切分实践

```python
def chunk_markdown(markdown_text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Cookbook 风格的 Markdown 感知切分器
    - 优先按标题（# ## ###）切分
    - 其次按段落切分
    - 过大的段落按句子切分
    - chunk 之间有 overlap 防止上下文断裂
    """
    import re
    
    # 按标题切分
    sections = re.split(r'(?=^#{1,3}\s)', markdown_text, flags=re.MULTILINE)
    chunks = []
    current_chunk = ""
    
    for section in sections:
        if len(current_chunk) + len(section) < chunk_size:
            current_chunk += section
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # 如果单个 section 就太大，按段落继续切
            if len(section) > chunk_size:
                paragraphs = section.split("\n\n")
                for para in paragraphs:
                    if len(current_chunk) + len(para) < chunk_size:
                        current_chunk += para + "\n\n"
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = para[-overlap:] + para if overlap else para
            else:
                current_chunk = section[-overlap:] if overlap else section
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks
```

### Chunk 大小选择指南

| 文档类型 | 推荐 chunk 大小 | 说明 |
|---------|----------------|------|
| 短问答/FAQ | 256-512 tokens | 答案通常很集中 |
| 通用文档 | 512-1024 tokens | 平衡粒度和上下文 |
| 长文/书籍章节 | 1024-2048 tokens | 需要更多上下文 |
| 代码文件 | 按函数/类切分 | 语法边界优先于 token 数 |

> 💡 **Cookbook 经验**：chunk 大小没有万能值——一定要在你的数据上测试不同大小的效果。

## 向量数据库集成模式（以 Pinecone 为例）

Cookbook 展示了 Pinecone 等托管向量数据库的集成模式。所有向量数据库的集成都遵循相同的接口模式：

### 通用向量存储接口

```python
from abc import ABC, abstractmethod
from typing import list, dict

class VectorStore(ABC):
    """向量存储抽象接口——不管用 Pinecone/Chroma/Weaviate 都是这个模式"""
    
    @abstractmethod
    def add_documents(self, documents: list[str], embeddings: list[list[float]], metadata: list[dict] = None):
        """添加文档和嵌入"""
        pass
    
    @abstractmethod
    def similarity_search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        """检索最相似的文档，返回文档内容和元数据"""
        pass
```

### Pinecone 集成示例（Cookbook 模式）

```python
from pinecone import Pinecone, ServerlessSpec

class PineconeVectorStore(VectorStore):
    def __init__(self, api_key: str, index_name: str, dimension: int = 1536):
        self.pc = Pinecone(api_key=api_key)
        
        # 如果索引不存在就创建
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        self.index = self.pc.Index(index_name)
    
    def add_documents(self, documents: list[str], embeddings: list[list[float]], metadata: list[dict] = None):
        vectors = []
        for i, (doc, emb) in enumerate(zip(documents, embeddings)):
            meta = metadata[i] if metadata else {}
            meta["text"] = doc  # 把文本存在 metadata 里
            vectors.append((f"doc_{i}", emb, meta))
        
        self.index.upsert(vectors=vectors)
    
    def similarity_search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        return [
            {"text": match.metadata["text"], "score": match.score, "metadata": match.metadata}
            for match in results.matches
        ]
```

### 元数据（Metadata）的重要性

Cookbook 强调：**一定要给 chunk 加元数据**，这能大幅提升 RAG 质量：

```python
metadata = {
    "source": "user_manual.pdf",        # 文档来源
    "page": 42,                         # 页码
    "section": "第3章 安装指南",         # 章节
    "doc_type": "manual",               # 文档类型
    "last_updated": "2024-06-01",       # 更新时间
    "chunk_index": 15,                  # chunk 序号
}
```

元数据可以用来：
- 过滤检索结果（"只搜索用户手册，不搜索销售材料"）
- 溯源（告诉用户答案来自哪个文档哪一页）
- 按时间排序（优先返回最新的内容）

## 上下文嵌入（Contextual Embeddings）优化

Cookbook 中的 `contextual-embeddings` 示例展示了一个显著提升 RAG 准确率的技术：**给每个 chunk 加上它在文档中的上下文**。

### 问题：为什么普通嵌入效果不好？

```
文档内容：
  第3章 安装指南
  ... 前面的内容 ...
  运行以下命令启动服务：     ← 这个 chunk 被单独切出来
  ./start.sh
  ... 后面的内容 ...
```

这个 chunk（"运行以下命令启动服务：./start.sh"）单独看是有歧义的——启动什么服务？在哪个目录？嵌入模型无法准确理解其含义。

### 解决方案：上下文增强

```python
def generate_contextual_chunk(chunk: str, full_document: str, doc_title: str) -> str:
    """用 Claude 为每个 chunk 生成上下文"""
    prompt = f"""文档标题：{doc_title}

以下是文档中的一个片段，但缺少上下文。请为这个片段生成简短的上下文说明（1-2句话），说明它在文档中的位置、讨论的主题、以及任何必要的前置信息。

文档（供参考）：
{full_document[:8000]}...

需要添加上下文的片段：
{chunk}

上下文说明："""

    response = client.messages.create(
        model="claude-3-haiku-20240307",  # 用 Haiku 做这个，便宜快速
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    context = response.content[0].text.strip()
    
    # 返回增强后的 chunk（用于嵌入和检索）
    return f"[上下文：{context}]\n\n{chunk}"
```

这个简单的技巧通常能让 RAG 准确率提升 10-30%，Cookbook 中强烈推荐。

## 知识图谱增强 RAG

Cookbook 中的 `knowledge_graph` 示例展示了用知识图谱补充向量检索的模式——适合实体关系丰富的场景。

### 为什么需要知识图谱？

向量检索擅长语义相似，但不擅长精确的关系查询：
- ❌ "X 公司的 CEO 是谁？" → 向量检索可能找到提到 X 公司和 CEO 的文档，但不保证是正确的人
- ✅ 知识图谱三元组 `(X公司, CEO, 张三)` → 精确回答

### 混合 RAG 架构

```
用户提问
    ↓
┌─────────────────────────────────┐
│    意图路由（Claude 判断）      │
└─────────┬───────────┬───────────┘
          │           │
          ▼           ▼
    ┌──────────┐ ┌──────────┐
    │ 向量检索 │ │ 图谱查询 │  各取所长
    │ (语义)   │ │ (精确)   │
    └─────┬────┘ └────┬─────┘
          │           │
          └─────┬─────┘
                ▼
    ┌─────────────────────────┐
    │  结果融合 + Claude 生成  │
    └─────────────────────────┘
```

Cookbook 中展示了用 Claude 从文档中抽取实体和关系构建知识图谱的流程。

## RAG 质量评估模式

Cookbook 中的自动化评估（Evals）示例也适用于 RAG。评估 RAG 需要三个维度：

### RAG 评估三要素

```
1. 答案相关性（Answer Relevance）
   答案是否回答了用户的问题？
   → 用 Claude 评分 1-5

2. 上下文相关性（Context Relevance）
   检索到的 chunk 是否和问题相关？
   → 有没有检索到不相关的内容（噪声）？

3. 忠实度（Faithfulness / Groundedness）
   答案是否基于检索到的上下文？有没有幻觉？
   → 答案中的每一句话是否都能在检索结果中找到依据？
```

### Cookbook 风格的 RAG 评估器

```python
def evaluate_rag_answer(question: str, context: str, answer: str) -> dict:
    """评估 RAG 答案质量"""
    eval_prompt = f"""请评估以下 RAG 系统的回答质量，从三个维度打分（1-5分）：

用户问题：{question}

检索到的上下文：
{context}

系统回答：{answer}

评分标准：
1. 答案相关性（1-5）：答案是否直接回答了用户问题？
2. 上下文相关性（1-5）：检索到的上下文是否和问题相关？有无无关噪声？
3. 忠实度（1-5）：答案是否完全基于上下文？有没有编造上下文没有的信息？

请以 JSON 格式返回：
{{
  "answer_relevance": 分数,
  "context_relevance": 分数,
  "faithfulness": 分数,
  "issues": "发现的具体问题",
  "suggestions": "改进建议"
}}"""

    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=500,
        messages=[{"role": "user", "content": eval_prompt}]
    )
    return json.loads(response.content[0].text)
```

## Wikipedia / Web 数据源集成

Cookbook 展示了如何将 Wikipedia 和 Web 页面作为 RAG 数据源：

### Wikipedia 集成模式

```python
import wikipedia

def search_wikipedia(query: str, top_k: int = 3) -> list[str]:
    """搜索 Wikipedia 并返回相关内容"""
    # 搜索相关页面
    search_results = wikipedia.search(query, results=top_k)
    docs = []
    for title in search_results:
        try:
            page = wikipedia.page(title, auto_suggest=False)
            # 取页面摘要（避免太长）
            docs.append(f"标题：{page.title}\nURL：{page.url}\n内容：{page.summary}")
        except (wikipedia.DisambiguationError, wikipedia.PageError):
            continue
    return docs
```

### Web 页面读取模式

Cookbook 通常配合 BeautifulSoup 或 Firecrawl 等工具读取网页：

```python
import requests
from bs4 import BeautifulSoup

def fetch_webpage(url: str) -> str:
    """抓取并解析网页正文"""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ClaudeRAG/1.0)"}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 移除无关元素
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()
    
    return soup.get_text(separator="\n", strip=True)
```

这些数据源可以作为 RAG 的"工具"——Claude 在需要最新信息时调用（参见 [工具调用模式](/cookbooks/concepts/01-tool-use-patterns.md)），而不是预先索引所有内容。

## 常见 RAG 问题与解决方案

| 问题 | 症状 | Cookbook 解决方案 |
|------|------|------------------|
| **检索不到正确内容** | 答案总是"资料中没有" | 优化 chunk 大小、尝试语义切分、加元数据过滤、用上下文嵌入 |
| **检索到太多噪声** | 上下文里有很多无关内容 | 减小 top_k、加元数据过滤、用 reranker 重排序 |
| **幻觉** | 答案看起来对但编造内容 | 在提示词中强调"只基于上下文"、加忠实度评估、降低 temperature |
| **答案不完整** | 只回答了部分问题 | 增大 chunk_size、增加 top_k、做父子 chunk 检索 |
| **过时信息** | 用旧内容回答 | 元数据加时间戳、优先检索最近更新的文档、定期重建索引 |

## 相关概念

- [Cookbook 导览](/cookbooks/concepts/00-overview.md) — 回到 Cookbooks 总览
- [工具调用模式](/cookbooks/concepts/01-tool-use-patterns.md) — RAG 检索作为工具被 Agent 调用
- [多模态模式](/cookbooks/concepts/02-multimodal-patterns.md) — PDF/图片文档做 RAG 的前置处理
- [高级技巧 - Prompt Caching](/cookbooks/concepts/04-advanced-techniques.md) — RAG 系统提示缓存降低成本
- [高级技巧 - Evals](/cookbooks/concepts/04-advanced-techniques.md) — RAG 系统的自动化评估框架
- [食谱完整索引](/cookbooks/references/recipe-index.md) — 查找具体 RAG 食谱
