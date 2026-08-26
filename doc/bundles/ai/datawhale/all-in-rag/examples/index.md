# 实战示例

本目录包含 All-in-RAG 教程中的核心代码实践示例，聚焦于第八、九章的完整项目实战，覆盖从基础 RAG 到 Graph RAG 的技术跃迁。

## 项目实战

* [基础RAG食谱问答系统](c8-basic-rag.md) — 第八章 `code/C8/`：基于 FAISS + LangChain + Kimi 的食谱 RAG 系统，涵盖数据准备、父子文档分块、混合检索、元数据过滤、查询路由、流式生成全链路。对应概念：[项目实战](../concepts/project-practice.md)、[数据准备与处理](../concepts/data-preparation.md)、[检索进阶技术](../concepts/retrieval-advanced.md)。
* [Graph RAG食谱问答系统](c9-graph-rag.md) — 第九章 `code/C9/`：基于 Neo4j 知识图谱 + Milvus 向量库的双引擎图 RAG 系统，支持智能查询路由、多跳推理、子图提取与自适应生成。对应概念：[项目实战](../concepts/project-practice.md)、[检索进阶技术](../concepts/retrieval-advanced.md)、[索引构建](../concepts/index-construction.md)。

## 章节代码索引

除上述综合实战外，各章节还提供独立代码示例，位于源码 `code/` 目录：

| 章节 | 目录 | 主要内容 |
|------|------|---------|
| 第一章 | `code/C1/` | LangChain/LlamaIndex RAG 快速上手 |
| 第二章 | `code/C2/` | Unstructured 数据加载、三种分块策略 |
| 第三章 | `code/C3/` | BGE 嵌入、FAISS/Milvus、多模态检索、句子窗口/递归检索 |
| 第四章 | `code/C4/` | 混合检索、Text2SQL、查询路由、重排优化 |
| 第五章 | `code/C5/` | Pydantic 结构化输出、Function Calling |
| 第六章 | `code/C6/` | LlamaIndex 评估示例 |
| 第八章 | `code/C8/` | 基础 RAG 食谱问答系统（详见上文） |
| 第九章 | `code/C9/` | Graph RAG 优化系统（详见上文） |

```{toctree}
:hidden:
:maxdepth: 7

c8-basic-rag
c9-graph-rag
```
