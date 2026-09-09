---
type: concept
title: "安装与快速上手：包元数据、三种调用路径与模型清单"
description: "BCEmbedding 的包元数据与依赖约束、pip/源码两种安装方式、封装类/原生 transformers/sentence-transformers 三种调用路径，以及 bce-embedding-base_v1 与 bce-reranker-base_v1 模型清单。"
tags: [bcembedding, embedding, reranker, installation, quickstart, rag]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:facts-md", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: BCEmbedding 源码事实清单（F-bc 系列）
  - id: insights
    resource: /references/insights.md
    title: BCEmbedding 架构洞察与知识地图
---

# 安装与快速上手

BCEmbedding 是网易有道开源的双语与跨语种嵌入库，为 RAG（检索增强生成）场景提供 `EmbeddingModel`（语义向量生成）与 `RerankerModel`（相关性打分与重排序）两个核心模型类（F-bc-004）。本库是有道 RAG 产品（如 QAnything）的嵌入底座，主攻中英文双语及跨语种检索。

## 包元数据与依赖约束

`setup.py` 声明包名 `BCEmbedding`、版本 `0.1.5`、许可证 `apache-2.0`、作者 `Netease Youdao, Inc.`（F-bc-001）。安装依赖共 4 项（F-bc-002）：

| 依赖 | 约束 |
|---|---|
| `torch` | `>=1.6.0` |
| `transformers` | `>=4.35.0,<4.37.0`（上界锁死在 4.36 系列） |
| `datasets` | 无版本约束 |
| `sentence-transformers` | 无版本约束 |

两点需要注意：

1. **无 `python_requires` 声明**（F-bc-003）：源码中不存在权威的 Python 版本约束，唯一旁证是 README 安装示例使用 `conda create --name bce python=3.10`，即官方以 Python 3.10 为基准环境。
2. **transformers 上界锁定**：`>=4.35.0,<4.37.0` 意味着与新版 transformers（≥4.37）不保证兼容，在已有较新 transformers 的环境中安装需先评估冲突。

## 安装方式

README 提供两种方式（F-bc-030）：

```bash
# 方式一：从 PyPI 安装固定版本
pip install BCEmbedding==0.1.5

# 方式二：源码目录可编辑安装
git clone git@github.com:netease-youdao/BCEmbedding.git
cd BCEmbedding
pip install -v -e .
```

## 模型清单

README 模型清单共 2 个模型，权重均发布于 HuggingFace `maidalun1020` 组织（F-bc-027）：

| 模型名 | 类型 | 语言 | 参数量 |
|---|---|---|---|
| `bce-embedding-base_v1` | `EmbeddingModel` | 中、英 | 279M |
| `bce-reranker-base_v1` | `RerankerModel` | 中、英、日、韩 | 279M |

两者即构造器的默认 `model_name_or_path` 取值（F-bc-005、F-bc-013），不传参数即可加载默认模型。README 另声明两点使用语义（F-bc-028）：`RerankerModel` 支持长 passage 重排序（"more than 512 tokens, less than 32k tokens"，实现机制见 [/concepts/02-reranker-model.md](/concepts/02-reranker-model.md)）；`EmbeddingModel` 则 "does not need specific instructions"，即自家嵌入模型不需要查询指令前缀——这一声明与指令字典的设计动机密切相关（见 [/concepts/03-query-instruction.md](/concepts/03-query-instruction.md)）。

## 三种调用路径

README Quick Start 给出三条等价调用路径（F-bc-029），按抽象层级从低到高排列：

### 路径一：`BCEmbedding` 封装类（官方推荐）

顶层包 `BCEmbedding/__init__.py` 执行 `from .models import *`，而 `models/__init__.py` 以 `__all__` 导出 `EmbeddingModel` 与 `RerankerModel`（F-bc-004），因此可以直接：

```python
from BCEmbedding import EmbeddingModel, RerankerModel

model = EmbeddingModel(model_name_or_path="maidalun1020/bce-embedding-base_v1")
embeddings = model.encode(['sentence_0', 'sentence_1'])
```

### 路径二：原生 `transformers`

直接用 `AutoModel` / `AutoModelForSequenceClassification` 加载权重，自行实现 cls pooling 与 L2 归一化（F-bc-029）。此路径适合需要定制前向逻辑的场景，但 pooling 与归一化的组合必须忠实复刻封装类行为（`outputs.last_hidden_state[:, 0]` 取 CLS 向量后按行归一化，F-bc-011），否则向量语义会与官方封装不一致。

### 路径三：`sentence-transformers`

用 `SentenceTransformer`（对应 EmbeddingModel）与 `CrossEncoder`（对应 RerankerModel）调用（F-bc-029），适合已在 sentence-transformers 生态中工作的项目。

## 顶层导入约定

```python
from BCEmbedding import EmbeddingModel   # OK：经 __all__ 导出
from BCEmbedding import RerankerModel    # OK
```

框架集成层（LangChain / LlamaIndex）则是另一套路：`BCERerank` 封装类在 `BCEmbedding/tools/` 下按框架分目录提供，详见 [/concepts/04-framework-integrations.md](/concepts/04-framework-integrations.md)。

## 注意事项

- transformers 版本上界 `<4.37.0` 是硬性约束来源（F-bc-002），升级依赖前应先跑通 `encode`/`compute_score` 冒烟测试。
- 官方集成示例锁定的框架版本较旧（LangChain `0.1.0`、LlamaIndex `0.9.42.post2`，F-bc-031），复制官方教程代码时需注意与当前框架版本的兼容性。
- README 中的 MTEB/RAG 榜单数字属厂商自宣数据，本知识包未将其纳入事实清单，引用时应另行核验。

## 相关概念

- [/concepts/01-embedding-model.md](/concepts/01-embedding-model.md) — EmbeddingModel 构造参数与 encode 数据流详解
- [/concepts/02-reranker-model.md](/concepts/02-reranker-model.md) — RerankerModel 打分与重排序接口详解
- [/concepts/03-query-instruction.md](/concepts/03-query-instruction.md) — 指令字典与跨语种检索
