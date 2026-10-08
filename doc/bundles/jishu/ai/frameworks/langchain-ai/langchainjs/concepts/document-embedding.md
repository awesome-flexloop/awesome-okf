---
type: concept
scope: langchainjs
name: document-embedding
version: "0.1.0"
source: https://github.com/langchain-ai/langchainjs
description: LangChain.js Document 与 Embedding——文档数据模型、向量化抽象与 RAG 基础组件
---

# Document 与 Embedding

## RAG 的基础构件

检索增强生成（Retrieval-Augmented Generation, RAG）是 LLM 应用的核心模式之一。RAG 流水线通常包含三个阶段：

1. **文档加载与切分**：将原始数据转为 `Document` 对象并切分为适当大小的块
2. **向量化**：使用 `Embeddings` 模型将文本块转为向量
3. **存储与检索**：将向量存入 `VectorStore`，查询时检索最相关的文档块

本文档覆盖 LangChain.js 中前两个阶段的核心抽象：`Document` 和 `Embeddings`。

## Document

**源码位置**：`documents/document.ts:38`

`Document` 是 LangChain.js 中表示文本文档的标准数据结构：

```typescript
class Document<Metadata extends Record<string, any> = Record<string, any>> {
  pageContent: string;
  metadata: Metadata;
  id?: string;

  constructor(fields: DocumentInput<Metadata>);
}
```

### 三个字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `pageContent` | `string` | 文档的文本内容。构造时调用 `.toString()`，未提供时为空字符串 |
| `metadata` | `Metadata` | 任意元数据对象，默认 `{}`。常用于存储来源、页码、URL、时间戳等 |
| `id` | `string?` | 可选标识符，建议为 UUID 但不强制。未来可能成为必填字段 |

### 设计特点

- **极简结构**：只有文本内容 + 元数据，不包含向量、评分等检索相关字段
- **泛型 Metadata**：通过泛型参数约束元数据形状，提供类型安全
- **可选 ID**：当前为可选，注释说明"在足够多的向量存储实现采用后，未来可能成为必填"（document.ts:48-50）

### 创建文档

```typescript
import { Document } from "@langchain/core/documents";

const doc = new Document({
  pageContent: "LangChain 是一个 LLM 应用框架。",
  metadata: { source: "维基百科", page: 1, url: "https://..." },
  id: "doc-001",
});
```

文档加载器（document loaders）和文本切分器（text splitters）产出和消费 Document 对象。`@langchain/core` 定义了 `BaseDocumentLoader` 抽象，`@langchain/textsplitters` 包提供文本切分能力。

### Document 接口

`DocumentInterface`（document.ts:18-33）定义了文档的公共契约，`DocumentInput`（document.ts:1-16）是构造输入类型。两者都包含 `pageContent`、`metadata?`、`id?`，但 DocumentInterface 的 `metadata` 为必填（默认 `{}`）。

## Embeddings

**源码位置**：`embeddings.ts:32`

`Embeddings` 是文本向量化模型的抽象基类：

```typescript
abstract class Embeddings<TOutput = number[]>
  implements EmbeddingsInterface<TOutput> {
  caller: AsyncCaller;

  abstract embedDocuments(documents: string[]): Promise<TOutput[]>;
  abstract embedQuery(document: string): Promise<TOutput>;
}
```

### 两个核心方法

| 方法 | 输入 | 输出 | 用途 |
|---|---|---|---|
| `embedDocuments` | `string[]` | `Promise<TOutput[]>` | 批量嵌入文档（用于索引），通常调用批量 API 以提高效率 |
| `embedQuery` | `string` | `Promise<TOutput>` | 嵌入单个查询（用于检索），可能使用不同的编码前缀 |

区分这两个方法的原因是：某些嵌入模型（如旧版 BGE 系列）对查询和文档使用不同的指令前缀，检索效果更好。

### AsyncCaller

`Embeddings` 构造函数创建 `AsyncCaller` 实例（`embeddings.ts:42`），提供：
- **并发控制**：通过 `maxConcurrency` 限制并发请求数
- **重试逻辑**：失败时自动重试（指数退避）
- **超时控制**：通过 `timeout` 限制单次请求时长

具体嵌入实现应通过 `this.caller.call(fn)` 发起 API 请求以获得这些能力。

### 泛型 TOutput

`TOutput` 默认为 `number[]`，但允许嵌入模型返回其他类型的向量表示（如稀疏向量、二进制向量等）。`EmbeddingsInterface`（embeddings.ts:9-26）定义了公共接口契约。

### 嵌入模型实现

具体的嵌入模型由集成包提供，例如：

```typescript
// @langchain/openai
import { OpenAIEmbeddings } from "@langchain/openai";

const embeddings = new OpenAIEmbeddings({
  model: "text-embedding-3-small",
});

// 嵌入文档（批量）
const vectors = await embeddings.embedDocuments([
  "LangChain 是一个框架",
  "LangChain 支持 Agent",
]);

// 嵌入查询（单个）
const queryVector = await embeddings.embedQuery("什么是 LangChain？");
```

## 与其他核心抽象的关系

```
Document ──→ Embeddings.embedDocuments ──→ number[] ──→ VectorStore
                                                          │
Query ──→ Embeddings.embedQuery ──→ number[] ──→ similaritySearch
                                                          │
                                                    Document[]
```

### VectorStore（向量存储）

向量存储的抽象定义在检索器模块中。`VectorStore` 继承 `Runnable`，核心方法包括：

- `addDocuments(documents: Document[])`：添加文档
- `similaritySearch(query: string, k?: number)`：相似性搜索，返回 Document[]
- `similaritySearchVectorWithScore(query, k)`：返回带相似度分数的结果
- `asRetriever()`：转换为 Retriever

因为 VectorStore 是 Runnable，它可以直接 `pipe` 到 LLM 链中，构成完整的 RAG 管道：

```typescript
const chain = RunnableSequence.from([
  (input) => input.question,
  vectorStore.asRetriever(),
  (docs) => formatDocs(docs),
  prompt,
  model,
  parser,
]);
```

### Document Transformers

`documents/transformers.ts` 提供文档变换的抽象基类，用于文档清洗、元数据提取等操作。文本切分器是其最常见的实现。

## RAG 流水线示例

```typescript
import { Document } from "@langchain/core/documents";
import { OpenAIEmbeddings } from "@langchain/openai";
import { MemoryVectorStore } from "@langchain/core/vectorstores";
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

// 1. 创建文档
const rawDocs = [
  new Document({
    pageContent: "LangChain 是一个用于构建 LLM 应用的 TypeScript 框架...",
    metadata: { source: "docs" },
  }),
];

// 2. 切分文档
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 1000,
  chunkOverlap: 200,
});
const splitDocs = await splitter.splitDocuments(rawDocs);

// 3. 嵌入并存入向量存储
const embeddings = new OpenAIEmbeddings();
const vectorStore = await MemoryVectorStore.fromDocuments(
  splitDocs,
  embeddings
);

// 4. 检索
const results = await vectorStore.similaritySearch("LangChain 是什么？", 2);
```

## 相关文档

- 总览
- Runnable 接口 — VectorStore 也是 Runnable
- 消息系统 — Document 内容进入 Prompt 后的消息表示
