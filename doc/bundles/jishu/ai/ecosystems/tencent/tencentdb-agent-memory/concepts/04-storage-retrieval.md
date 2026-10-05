---
type: Concept
title: "存储后端与混合检索：sqlite/TCVDB/Mongo 三选一与 RRF/BM25"
description: "后端选择决策树、TCVDB 占位索引与 sparse BM25、SQLite 表结构与隔离列、RRF_K=60 融合公式、BM25 TS 化与不健康降级、配额费率及元数据/数据面分库。"
tags: [tencentdb-agent-memory, concept, storage, retrieval, sqlite, tcvdb, rrf, bm25]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-core-code
    resource: /references/01-source-code-map.md
    title: TencentDB-Agent-Memory 源码地图
  - id: s-readme
    resource: /references/02-readme-changelog.md
    title: README 与 CHANGELOG 信源
  - id: s-core-api
    resource: /references/03-api-references.md
    title: MemoryCore v3 API 文档摘要
  - id: s-deploy
    resource: /references/04-deploy-install.md
    title: 部署形态与安装指南
---

# 存储后端与混合检索：sqlite/TCVDB/Mongo 三选一与 RRF/BM25

> **本篇看点**：存储后端按「mongoConfig → service/tcvdb 配置 → sqlite 默认」的决策树选择（F-107）。SQLite 侧主表、vec0 虚表、FTS5 全文表都直接带六列隔离字段，库文件名为 vectors.db（F-111~F-113）；TCVDB 侧索引优先 DISK_FLAT 再回退 HNSW，无 embedding 时建 dim=1 占位索引、用 sparse vector 承载 BM25（F-109/F-110）。混合检索用 RRF（RRF_K=60）后融合 BM25 与向量，BM25 已从 Python sidecar 改为 TS 实现，服务不可达时返回空向量并标记不健康（F-114~F-116）。这些「能力缺失仍可运转」的设计与 L0/L1 管线同属 spec/insights.md 洞察三概括的 fail-open 模式（F-110、F-116）。

## 配额：DEFAULT_RATES 与模型倍率

credit-calculator.ts 定义 DEFAULT_RATES（input/cache/output 三费率）与 DEFAULT_MODEL_MULTIPLIERS（模型倍率）（F-094）。quota-manager.ts 实现配额管理，网关侧配额策略在 quota-credit-policy.ts（F-095）。即 token 消耗先按输入/缓存/输出三类费率计费，再乘模型倍率（F-094）。

## 元数据面 / 数据面分库

| 面 | 库命名 | 实现位置 |
|---|---|---|
| 元数据面（auth/instance/pagination 等） | `tdai_metadata_<instance>` | metadata/：router、store（sqlite-adapter、db-name、factory、interface）、utils（crypto、id-generator、user-key）（F-097、F-098） |
| 数据面（记忆本体） | `tdai_memory` | metadata/store/db-name.ts 与部署文档（F-098） |

分库使多实例（instance）各自拥有独立元数据库，而数据面命名保持统一（F-097、F-098）。

## 后端选择决策树

后端选择逻辑集中在 store/factory.ts 与 store/store-pool.ts，core/backend-selection/ 另有独立决策模块（F-107、F-126）：

```text
存在 mongoConfig？                         → mongodb
否；service/tcvdb 模式且存在 VDB 配置？      → tcvdb
以上均否                                    → sqlite（默认）（F-107）
```

存储后端类型与适配器接口定义在 store/types.ts、store/adapter.ts、store/index.ts，抽象核心接口在 core/abstractions/types.ts（F-125、F-127）。

## TCVDB 后端：连接、索引与占位向量

- 连接需 url、apiKey、database 三项参数（F-108）。
- 向量索引优先 DISK_FLAT，回退 HNSW；HNSW 带 M/efConstruction 参数（F-109）。
- 无 embedding 能力时建 dim=1 占位向量索引，sparse vector 承载 BM25（F-110）。

dim=1 占位是典型 fail-open：即使没有配置 embedding，表结构与写入链路依然成立，稀疏检索照常工作（F-110）。

## SQLite 后端：表、虚表与 vectors.db

- 实现于 store/sqlite/memory-store.ts，主表包括 l1_records、l0_conversations，隔离字段 team_id/user_id/agent_id/session_key/session_id/task_id 直接落列（F-111）。
- 向量表 l1_vec、l0_vec 使用 sqlite-vec 的 vec0 虚表、cosine 距离；FTS5 全文表同样包含隔离字段（F-112）。
- SQLite 数据库文件名为 vectors.db；初始化 DDL 脚本为 scripts/db/sqlite-init.sql（F-113、F-123）。

隔离字段进入 FTS5 与 vec0 虚表，意味着全文检索与向量检索都无法绕过租户维度（F-112）。

## RRF 融合：RRF_K=60

RRF 融合参数 RRF_K=60，实现于 store/search-utils.ts（F-114）：

```text
对每条候选记忆 d，跨通道 c 求和：

  score(d) = Σ_c  1 / (k + rank_c(d) + 1)     其中 k = 60

通道：BM25（稀疏） + 向量（稠密）（F-114）
```

按排名而非原始得分融合，使 BM25 与向量两路量纲不可比也能相加，且任一路缺席时公式依然成立（F-114）。

## BM25：TS 实现、不健康降级与 jieba 分词

- bm25-local.ts 以 `@tencentdb-agent-memory/tcvdb-text` 的 TS 实现替代 Python sidecar（F-115）。
- bm25-client.ts 在 BM25 服务不可达时返回空向量并标记不健康，而非让请求失败（F-116）。
- 分词使用 @node-rs/jieba，封装于 store/tokenize.ts（F-117）。
- embedding 封装于 store/embedding.ts（F-118）。

BM25 服务不健康时召回退化为仅向量/仅元数据，监控必须消费「不健康」标记而不能只看 HTTP 成功率（F-116）。该降级与 TCVDB 的 dim=1 占位索引同属洞察三的 fail-open 美学，写入侧（JSONL 主存优先）的同类设计见 [02-l0-l1-pipeline.md](02-l0-l1-pipeline.md)（F-110、F-115、F-116）。

## 其余存储模块（F-119~F-130）

| 模块 | 职责 |
|---|---|
| store/profile-row-store.ts | profile 行级存取（F-119） |
| store/list-page.ts | 列表分页抽象（F-120） |
| store/tcvdb/skill-store.ts、store/sqlite/skill-store.ts | TCVDB / SQLite 两套 Skill 存储（F-121） |
| scripts/db/mongodb-init.js | MongoDB 初始化脚本，要求 Mongo 7.0+ mongot，配 docker-compose.local-mongo.yaml（F-122） |
| scripts/db/sqlite-init.sql | SQLite 初始化 DDL（F-123） |
| tdai-gateway.yaml / tdai-gateway.standalone.yaml / tdai-gateway.local-mongo.yaml | 默认 / standalone / 本地 Mongo 三套网关配置（F-124） |
| core/backend-selection/（index.ts、types.ts） | 后端决策集中模块（F-126） |
| `/v3/tools/list`、`/v3/tools/call` | 工具调用 API 面（F-128） |
| core/tools/read-cos.ts | 从 COS 读取资源的内部工具（F-129） |
| bin/export-tencent-vdb.mjs、bin/migrate-sqlite-to-tcvdb.mjs | 导出 / 迁移工具（F-130） |

store/types.ts、store/adapter.ts、store/index.ts 共同定义后端类型与适配器接口（F-125）；core/abstractions/types.ts 定义核心抽象接口（F-127）。

## 相邻装配模块（同范围内背景）

- instance-config-provider.ts 提供每实例配置，tdai-core.ts 为核心装配入口（F-096）。
- seed 子系统含 input.ts、seed-runtime.ts、types.ts，对应 bin seed-v2；CLI 入口为 src/cli/index.ts（F-100、F-101）。
- 网关 LLM 解析在 llm-resolver.ts，支持 openai|anthropic 协议；chat-memory-handlers.ts 承载 `/capture`、`/recall` 兼容面，knowledge-handlers.ts 代理知识调用（F-102、F-104）。
- 环境配置工具有 env.ts、env-config.ts，部署模式常量在 gateway/metadata-env.ts；网关 generated/ 由 kubb.config.ts 生成（F-103、F-105）。
- 根 index.ts 与 openclaw.plugin.json 声明包入口与 OpenClaw 插件元数据，postinstall 对 openclaw 打 patch，兼容 pluginApi>=2026.3.13（F-106）。

## 延伸阅读

- 上一篇：[03-l2-scene-l3-persona.md](03-l2-scene-l3-persona.md)——场景、Persona 与自定义 Prompt
- 管线篇：[02-l0-l1-pipeline.md](02-l0-l1-pipeline.md)——fail-open 在写入侧的表现
- 模型篇：[01-four-layer-memory.md](01-four-layer-memory.md)
- 信源：[API 摘要](../references/03-api-references.md)、[部署安装](../references/04-deploy-install.md)、[源码地图](../references/01-source-code-map.md)
