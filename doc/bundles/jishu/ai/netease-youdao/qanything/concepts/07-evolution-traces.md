---
type: concept
title: 演进痕迹——死代码、失效导入与版本错位
description: 以 faiss/milvus 死模块、集合名日期戳与 compose 镜像版本错位为线索，还原 QAnything 从单机 FAISS 到服务化 Milvus 的架构演进，并建立"模块可达性验证"的源码阅读方法论。
tags: [qanything, legacy-code, dead-code, version-drift, architecture]
generated: { by: okf-wiki/0.2, at: 2026-09-09 }
verified: { by: "process:seven-concepts-v", at: "2026-09-09" }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: QAnything 源码事实清单（F-qa-001~060）
  - id: insights
    resource: /references/insights.md
    title: QAnything 架构洞察与知识地图
---

# 演进痕迹——死代码、失效导入与版本错位

活跃演进的开源仓库里，代码的"存在"不等于"可达"。QAnything 的源码中保留了一批被新架构绕过的遗留模块与相互矛盾的版本号，它们既是历史演进的化石，也是阅读源码时最容易踩的陷阱。本文以这些痕迹为线索还原架构演进轨迹，并给出可迁移的"可达性验证"方法论。

## 死代码实证：两个失效的数据库连接器

`connector/database/faiss/faiss_client.py` 与 `connector/database/milvus/milvus_client.py` 两个模块存在**失效导入**：前者导入 `FAISS_LOCATION`、`FAISS_CACHE_SIZE`，后者导入 `MILVUS_HOST_ONLINE`、`CHUNK_SIZE`——这四个名称均不存在于 `model_config.py`，模块一运行即 ImportError；且 Grep 全仓验证无任何其他文件 import 这两个模块（F-qa-027）。

这条事实的价值不在bug本身，而在它揭示的演进轨迹：

- **faiss_client 的存在**说明项目早期（或某条支线）采用单机 FAISS 做向量存储——FAISS 是进程内嵌的本地向量索引库；
- **milvus_client 的弃用**说明服务化 Milvus 的接入路径发生过迁移：RAG 主链路现在实际使用的是 `core/retriever/vectorstore.py`（`VectorStoreMilvusClient`/`SelfMilvus`）与 `core/retriever/elasticsearchstore.py`（`StoreElasticSearchClient`）（F-qa-013、F-qa-015）；
- 新链路绕开了 `connector/database/` 下的旧连接器，旧模块成为无人引用的死代码，且因配置常量被删除/改名而根本无法加载。

## 命名中的时间戳

集合名与索引名带有日期戳：`MILVUS_COLLECTION_NAME='qanything_collection_240625'`、`ES_INDEX_NAME='qanything_es_index_240625'`（F-qa-023），说明这两处存储结构定型于 2024-06-25 前后的某次发布。存储名一旦上线即不敢轻易更换（涉及全量数据迁移），于是日期戳成为"某次架构定型"的永久印记。

## 版本错位的三重口径

仓库同时存在三套互不一致的版本号（F-qa-058、F-qa-053）：

| 口径 | 版本 | 证据 |
|---|---|---|
| git 最近 tag | v2.0.0 | 事实清单基线 |
| docker-compose 主镜像 | `xixihahaliu01/qanything-{linux,mac,win}:v1.5.1` | F-qa-058 |
| 前端 package 版本 | 2.0.4 | F-qa-053 |

语义化版本里 v2.0.0 应晚于 v1.5.1，但 compose 镜像、前端版本、git tag 三者各说各话，说明版本号并非单一来源驱动。**部署时不能假定"git checkout 最新 = 运行最新"**——直接使用仓库自带 compose 的镜像 tag，跑起来的可能是与源码基线不一致的旧镜像。另外三平台 compose 的基础设施版本组合是固定的（ES 8.13.2、etcd v3.5.5、Milvus v2.4.8、MySQL 8.4，F-qa-057、F-qa-060），升级任一组件都需自行验证兼容性。

## 方法论：源码阅读先做"可达性验证"

本案例可提炼出一条可迁移的源码阅读纪律——**区分"存在"与"可达"**：

1. 对疑似遗留的模块，先查它的导入名在配置/依赖中是否仍然存在（本例中四个失效名称即一票否决）；
2. 再查全仓反向引用：无任何文件 import 的模块不参与真实架构；
3. 最后以主链路入口（本例为 `LocalDocQA.init_cfg()`，F-qa-001）为锚点，只沿着真实实例化路径阅读。

对二次开发者，这一验证应固化为自动化步骤：对疑似死代码执行 import 测试或反向引用检索，避免基于死代码做出错误的设计决策。阅读 QAnything 源码时可直接跳过 `connector/database/` 下这两个遗留模块，从 `core/retriever/` 入手。

## 行动清单

- 以本仓库为改造对象时，将 0.28/0.5/0.9/300 等硬编码阈值提取为配置项（见 [/concepts/02-rag-pipeline.md](/concepts/02-rag-pipeline.md)）；
- 自行部署时不要直接使用仓库自带 compose 的镜像 tag，核对镜像内容与 git 基线的一致性（F-qa-058）；
- 存储 schema 命名（集合名/索引名）一旦携带业务流量即成为事实标准，初期命名应预留演进空间（F-qa-023）；
- 引用本项目版本号时须注明口径（git tag / 镜像 tag / 前端版本），三者不可混用。

## 相关概念

- [02 LocalDocQA 问答编排链与硬编码阈值](/concepts/02-rag-pipeline.md)
- [04 Milvus 分区多租户与三存储分层](/concepts/04-storage-multitenancy.md)
- [信源登记与基线说明](/references/sources.md)
