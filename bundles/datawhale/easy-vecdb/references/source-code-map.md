---
title: 源码结构映射
type: reference
bundle: /datawhale/easy-vecdb
description: easy-vecdb 项目 src/ 目录下的代码项目结构、核心模块与文件职责说明
sources:
  - https://github.com/datawhalechina/easy-vecdb/tree/main/src
tags:
  - reference
  - source-code
---

# 源码结构映射

本文件登记 easy-vecdb 项目 `src/` 目录下的代码项目结构，供深入实践时参考。

## 目录总览

```
src/
├── ANN_alorithms/        # ANN 算法 Jupyter Notebook 实战
├── Cre_milvus/           # Milvus 综合工程项目（教程主项目）
├── HDBSCAN/              # 数据聚类可视化
├── Meta_chunking/        # Meta-Chunking 论文代码 demo
├── faissSear/            # Faiss 搜索 Web 应用
├── graph_rag/            # 基于 Neo4j 的图 RAG 系统
└── README.md             # 实践项目说明与数据集构建指南
```

## ANN 算法 Notebook（src/ANN_alorithms/）

| 文件 | 说明 |
|------|------|
| `Annoy算法.ipynb` | Annoy 随机投影树算法的代码实现与可视化 |
| `HNSW算法.ipynb` | HNSW 分层小世界图算法的代码实现与可视化 |
| `IVF算法.ipynb` | IVF 倒排文件索引算法的代码实现与可视化 |
| `LSH算法.ipynb` | LSH 局部敏感哈希算法的代码实现与可视化 |
| `PQ算法.ipynb` | PQ 乘积量化算法的代码实现与可视化 |

## Cre_milvus 综合工程项目（src/Cre_milvus/）

这是 Milvus 部分的主项目，包含完整的数据处理、索引构建、搜索、监控和测试体系。

### 核心文件

| 文件 | 职责 |
|------|------|
| `backend_api.py` | 后端 API 服务 |
| `frontend.py` | 前端界面 |
| `config.yaml` | 配置文件 |
| `config_loader.py` | 配置加载器 |
| `simple_milvus.py` | Milvus 简化封装 |
| `simple_startup.py` | 简化启动脚本 |
| `start_simple.py` | 启动入口 |
| `requirements.txt` | Python 依赖 |

### 子模块

| 目录 | 说明 |
|------|------|
| `ColBuilder/` | 集合构建工具，含 `visualization.py` 可视化 |
| `IndexParamBuilder/` | 索引参数构建：`indexparam.py`、`searchparam.py` |
| `Search/` | 搜索模块：ES 搜索、聚类、嵌入、Milvus/Redis 服务、搜索优化、关键词提取 |
| `System/` | 系统模块：重试、集群工具、评估、初始化、监控、启动 |
| `dataBuilder/` | 数据构建：多种格式文件处理工具（csv/md/txt/pdf/img）、分块策略（含 Meta-Chunking） |
| `milvusBuilder/` | Milvus 构建：连接管理、快速插入、懒加载、持久化连接 |
| `multimodal/` | 多模态：CLIP 编码器 |
| `reorder/` | 重排序：聚类重排 |
| `testing/` | 测试：Locust 性能测试、性能监控 |
| `utils/` | 工具：错误处理 |

### dataBuilder/chunking/ 分块策略

| 文件 | 说明 |
|------|------|
| `chunk_strategies.py` | 分块策略基类与实现 |
| `meta_chunking.py` | Meta-Chunking 算法实现 |
| `perplexity_chunking.py` | Perplexity 分块 |
| `api_client.py` | LLM API 客户端 |
| `error_handler.py` | 错误处理 |
| `models.py` | 数据模型 |

## HDBSCAN 聚类可视化（src/HDBSCAN/）

| 文件 | 说明 |
|------|------|
| `pipeline_hdbscan_umap.py` | HDBSCAN 聚类 + UMAP 降维可视化流水线 |
| `requirements.txt` | 依赖 |
| `news_data_dedup.csv` | 示例数据（新闻去重数据） |

## Meta-Chunking（src/Meta_chunking/）

| 文件 | 说明 |
|------|------|
| `app.py` | 应用入口 |
| `chunk_rag.py` | 分块 RAG 实现 |
| `perplexity_chunking.py` | Perplexity 分块算法 |
| `README.md` | 项目说明 |
| `data/examples.json` | 示例数据 |

## Faiss 搜索应用（src/faissSear/）

| 文件 | 说明 |
|------|------|
| `app.py` | Flask Web 应用，提供 Faiss 检索 API |
| `requirements.txt` | 依赖 |
| `template/index.html` | 前端页面 |

## 图 RAG（src/graph_rag/）

基于 Neo4j 的图 RAG 系统，支持 Annoy、Faiss、Milvus 三种向量库。

| 路径 | 说明 |
|------|------|
| `docker-compose.yml` | Neo4j + 依赖服务编排 |
| `milvus_dockercompose.yml` | Milvus 服务编排 |
| `rag_code/config.py` | 配置文件 |
| `rag_code/main.py` | 主程序 |
| `rag_code/env.example` | 环境变量示例 |
| `rag_code/rag_modules/` | RAG 核心模块 |
| `rag_code/annoy_index/` | Annoy 索引存储 |
| `rag_code/faiss_index/` | Faiss 索引存储 |
| `data/cypher/` | Neo4j 导入数据（nodes.csv、relationships.csv、cypher 脚本） |

## 数据集构建指南要点

src/README.md 中记录的工程实践要点：

1. **数据清洗**：去除 HTML 标签、特殊符号、乱码等噪声
2. **数据去重**：合并相似内容，避免冗余
3. **标准化**：统一文本格式、日期、单位、大小写
4. **安全合规**：敏感信息过滤、偏见检测、权限控制
5. **分块策略**：语义切分、动态块大小、重叠分块
6. **模型适配**：领域微调、多模态支持、轻量化部署
7. **索引优化**：分层索引（HNSW 用于高频、IVF-PQ 用于长尾）、元数据过滤、分布式部署
