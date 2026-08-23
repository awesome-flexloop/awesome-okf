---
type: concept
title: "数据准备与处理"
bundle: /datawhale/all-in-rag
description: "RAG 数据加载（Unstructured 多格式文档处理）与文本分块策略（Character/Recursive/Semantic Chunking），构建高质量知识库的基础"
sources: https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter2/
related:
  - /datawhale/all-in-rag/concepts/rag-overview
  - /datawhale/all-in-rag/concepts/index-construction
  - /datawhale/all-in-rag/concepts/project-practice
tags: [data-loading, chunking, unstructured, markdown, pdf, semantic-chunker]
status: stable
---

# 数据准备与处理

## 核心理解

数据准备是 RAG 链路的第一环，直接决定检索质量的上限。无论嵌入模型和检索算法多么强大，"垃圾进、垃圾出"——低质量的文档加载和不合理的文本分块都会导致检索结果充满噪声或丢失关键上下文。第二章覆盖两个核心环节：**数据加载**（将多种格式文档解析为纯文本）和**文本分块**（将长文档切分为适合检索的片段）。

## 数据加载

### Unstructured 库

项目使用 `unstructured` 库处理多格式文档加载，支持：

- **PDF 文档**：提取文本内容，保留段落结构
- **Word 文档**：解析 .doc/.docx 格式
- **HTML 网页**：去除标签，提取正文
- **Markdown**：解析结构化文档
- **纯文本**：直接读取

加载过程通常包括：文件读取 → 格式解析 → 元素分类（标题、段落、表格等）→ 文本清洗 → 输出统一 Document 对象。

### 实战项目中的数据特点

第八章"尝尝咸淡"项目基于 HowToCook 菜谱数据集，约 300 多个 Markdown 文件。这些菜谱有两个关键特点：

1. **结构高度规整**：每个文件严格按统一格式组织（食材、步骤等小标题）
2. **内容篇幅较短**：单个菜谱约 700 字

这种结构化数据非常适合 RAG——可以通过元数据提取（菜品名、分类、难度）实现精准的元数据过滤检索。

## 文本分块策略

第二章介绍三种分块策略，从简单到智能递进：

### 1. Character Splitter（字符分块）

最基础的分块方式，按固定字符数（chunk_size）切分，可设置重叠长度（chunk_overlap）避免语义断裂。

- 优点：简单高效
- 缺点：可能在句子或段落中间切断，破坏语义完整性

### 2. Recursive Character Splitter（递归字符分块）

LangChain 默认推荐的分块器，按优先级尝试不同分隔符（段落→换行→句号→空格→字符），尽量在自然语义边界切分。

- 优点：在保持块大小均匀的同时，尊重语义边界
- 缺点：仍基于规则，无法理解深层语义

### 3. Semantic Chunker（语义分块）

基于嵌入模型计算句子间的语义相似度，在语义变化最大的"断点"处切分，确保每个块内语义连贯。

- 优点：分块质量最高，块内语义一致性好
- 缺点：计算成本高，需要额外嵌入计算

## 分块策略选择

| 策略 | 适用场景 | 计算成本 | 语义保持 |
|------|---------|---------|---------|
| Character Splitter | 格式统一、段落清晰的短文档 | 低 | 低 |
| Recursive Character Splitter | 通用场景，LangChain 默认推荐 | 低 | 中 |
| Semantic Chunker | 语义复杂、对检索精度要求高 | 高 | 高 |

关键参数 `chunk_size` 和 `chunk_overlap` 的权衡：块太大会引入噪声、稀释语义；块太小会丢失上下文。通常 200-1000 token 为常见范围，overlap 设为 chunk_size 的 10%-20%。

## 父子文档分块

第八章实战采用了**父子文档分块**策略：

- **子块（Child Chunk）**：较小的文本块用于精准向量检索
- **父文档（Parent Document）**：检索到子块后，返回其所属的完整菜谱文档给 LLM

这种设计兼顾了检索精度（小块语义聚焦）和生成质量（完整文档上下文充足），是生产级 RAG 的常用模式。

## 代码实践

第二章代码位于 `code/C2/`：
- `01_unstructured_example.py`——多格式文档加载示例
- `02_character_splitter.py`——字符分块
- `03_recursive_character_splitter.py`——递归字符分块
- `04_semantic_chunker.py`——语义分块

## 延伸阅读

- [RAG 概述与架构](rag-overview.md)——数据准备在 RAG 链路中的位置
- [索引构建](index-construction.md)——分块后的向量化与存储
- [项目实战](project-practice.md)——父子文档分块的工程实现
