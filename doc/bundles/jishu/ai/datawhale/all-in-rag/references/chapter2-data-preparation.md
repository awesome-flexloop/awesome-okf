---
type: reference
title: "第二章 数据准备"
bundle: /datawhale/all-in-rag
description: "多格式文档加载（Unstructured）与文本分块策略（Character/Recursive/Semantic Chunking），构建高质量RAG知识库"
source: https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter2/
path: docs/chapter2/
code:
  - code/C2/
tags: [data-loading, unstructured, chunking, character-splitter, semantic-chunker]
status: stable
---

# 第二章 数据准备

## 信源信息

- **章节路径**：`docs/chapter2/`
- **代码路径**：`code/C2/`
- **小节列表**：
  - 第一节 数据加载（`04_data_load.md`）
  - 第二节 文本分块（`05_text_chunking.md`）

## 内容概要

### 第一节 数据加载

- Unstructured 库多格式文档处理（PDF、Word、HTML、Markdown、TXT）
- 文档解析流程：文件读取→格式解析→元素分类→文本清洗→Document 输出
- 不同格式文档的加载注意事项

### 第二节 文本分块

- **Character Splitter**：固定字符数切分，简单高效但可能切断语义
- **Recursive Character Splitter**：递归尝试不同分隔符（段落→换行→句号→空格），LangChain 默认推荐
- **Semantic Chunker**：基于嵌入相似度在语义断点处切分，质量最高但计算成本大
- chunk_size 与 chunk_overlap 参数权衡

## 代码资产

| 文件 | 职责 |
|------|------|
| `code/C2/01_unstructured_example.py` | Unstructured 多格式文档加载 |
| `code/C2/02_character_splitter.py` | 字符分块示例 |
| `code/C2/03_recursive_character_splitter.py` | 递归字符分块示例 |
| `code/C2/04_semantic_chunker.py` | 语义分块示例 |

## 对应概念

- [数据准备与处理](../concepts/data-preparation.md)
