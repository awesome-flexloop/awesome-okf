---
type: reference
title: BCEmbedding 信源登记表
tags: [embedding, reranker, rag, netease-youdao, source-registry]
status: stable
sources:
  - id: bcembedding-vendor
    resource: vendor/netease-youdao/BCEmbedding/
    title: netease-youdao/BCEmbedding（SpecWeave vendor 子模块，只读）
---

# BCEmbedding 信源登记表

## 上游仓库

| 项目 | 值 |
|---|---|
| 上游仓库 URL | `git@github.com:netease-youdao/BCEmbedding.git` |
| 固定基线 commit | `1aa07ea64f94523965c8672e93da47c3faf4d2cd` |
| 本地引用位置 | `vendor/netease-youdao/BCEmbedding/`（git submodule，只读） |
| 许可证 | Apache-2.0（setup.py 声明 `apache-2.0`，F-bc-001） |
| 采集版本 | 0.1.5（F-bc-001、F-bc-030） |

> 信源路径稳定性：本 bundle 全部事实与文档引用仅指向 `vendor/` 下的 stable 位置，不引用任何临时目录或 `file:///` 绝对路径。基线 commit 为不可变引用点，重跑 R 阶段时以该 hash 复核。

## 关键信源文件清单

以下为 facts.md（F-bc 系列）中引用到的主要源码/文档文件，按模块分组（相对 vendor 仓库根）：

| 分组 | 文件路径 | 支撑事实编号 |
|---|---|---|
| 包元数据 | `setup.py` | F-bc-001~003 |
| 项目说明 | `README.md` | F-bc-003、027~031 |
| 顶层包 | `BCEmbedding/__init__.py`、`BCEmbedding/models/__init__.py` | F-bc-004 |
| Embedding 模型 | `BCEmbedding/models/embedding.py` | F-bc-005~012 |
| Reranker 模型 | `BCEmbedding/models/reranker.py` | F-bc-013~020 |
| 模型工具函数 | `BCEmbedding/models/utils.py` | F-bc-021~023 |
| 日志工具 | `BCEmbedding/utils/logger.py` | F-bc-024 |
| 指令字典 | `BCEmbedding/utils/query_instructions.py` | F-bc-025、026 |
| 评测模块 | `BCEmbedding/evaluation/c_mteb/__init__.py`、`BCEmbedding/evaluation/c_mteb/Retrieval.py`、`BCEmbedding/evaluation/c_mteb/Reranking.py`、`BCEmbedding/evaluation/c_mteb/yd_dres_model.py` | F-bc-032~037 |
| 框架集成 | `BCEmbedding/tools/langchain/bce_rerank.py`、`BCEmbedding/tools/llama_index/bce_rerank.py` | F-bc-038~040 |

## 使用说明

- E/V 阶段生成与验证文档时，API 真实性以本表文件为准逐一 Grep 核验。
- `BCEmbedding/evaluation/` 下的 `eval_mteb`、`eval_rag` 等入口脚本仅登记存在，未逐行采集（详见 facts.md「存疑与说明」）。
