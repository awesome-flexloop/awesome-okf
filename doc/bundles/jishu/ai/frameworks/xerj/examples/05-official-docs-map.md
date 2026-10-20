---
type: Example
title: 官方文档地图与选型
description: xerj.org/docs/ 46 页的导航地图——每一页由本束哪篇文档承接、13 个官方 recipe 与 5 个 playbook 的选型表、Corpus Hub 的两条通道，以及四处文档漂移的复核方法
tags: [xerj, 示例, 文档地图, recipe, playbook, 选型]
generated: { by: source-code-to-okf-wiki/E, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-docs-facts
    resource: /references/facts-docs.md
    title: 官方文档站事实清单
  - id: xerj-docs-source
    resource: /references/docs-source.md
    title: 官方文档站信源登记
---

# 官方文档地图与选型

`https://xerj.org/docs/` 是 XERJ 的官方手册，共 **46 页**（版本 v1.0.0-rc.97）。本示例给出三件事：**每一页由本束哪篇文档承接**、**10 个 recipe 与 5 个 playbook 怎么选**、以及**遇到文档与代码不一致时怎么复核**。

## 文档站的组织方式

站点的导航把 46 页分成六组加三个专区：

```
START        快速上手 · 安装 · 从 ES 迁移
REFERENCE    CLI · 配置 TOML · 环境变量 · 原生 REST · ES 兼容 API
DATA MODEL   查询类型 · 聚合 · 分析器 · 向量与 kNN
ENGINE       摄取管线 · 存储与 WAL · 压缩 · 集群 · 指标 · 认证与 TLS
OPERATIONS   生产运行 · 备份恢复 · 升级 · 排障
PLAYBOOKS    SIEM · 日志分析 · 向量·RAG · 全文检索 · 可观测性
RECIPES      10 个任务导向配方
CORPUS HUB   注册表与贡献
FOR AI       面向智能体的总览 · 快速上手 · 端点契约
```

每页底部都有一行 `Source → engine/crates/...`——**那是查证入口，不是装饰**。

## 页面 → 本束文档对照

| 站点页面 | 本束承接文档 |
|---|---|
| `index.html` | [00 整体架构](/concepts/00-overview.md) |
| `quickstart.html` / `install.html` | [01 安装与快速上手](/concepts/01-getting-started.md) |
| `migration-from-es.html` | [04 从 ES 迁移的评估路径](/examples/04-migration-from-elasticsearch.md) · [07 ES 兼容与基准](/concepts/07-es-compat-and-benchmarks.md) |
| `cli.html` / `config.html` / `env.html` | [12 配置与环境变量](/concepts/12-config-and-environment.md) |
| `api-native.html` | [12 配置与环境变量](/concepts/12-config-and-environment.md) |
| `api-es-compat.html` | [04 检索路径与响应裁剪](/concepts/04-search-query-path.md) · [07](/concepts/07-es-compat-and-benchmarks.md) |
| `queries.html` / `aggregations.html` | [09 查询类型与聚合](/concepts/09-query-types-and-aggregations.md) |
| `analyzers.html` / `ingest.html` | [10 分析器与摄取管线](/concepts/10-analyzers-and-ingest.md) |
| `vectors.html` | [05 向量、嵌入与混合检索](/concepts/05-vector-and-hybrid.md) |
| `storage.html` / `compression.html` / `clustering.html` | [11 存储、压缩与集群现状](/concepts/11-storage-compression-clustering.md) |
| `metrics.html` / `security.html` / `operations.html` / `backup-restore.html` / `upgrades.html` / `troubleshooting.html` | [12](/concepts/12-config-and-environment.md) · [13 生产运维与排障](/concepts/13-operations-and-troubleshooting.md) |
| `playbooks/*` · `recipes/*` | 本文 || `corpus-hub.html` | [08 参考编码与语料库](/concepts/08-reference-coding.md) |
| `agents/*` | [03 MCP 智能体接口](/concepts/03-mcp-agent-surface.md) · [06 智能体记忆与第二大脑](/concepts/06-agent-memory-and-brain.md) |

## 13 个官方 Recipe 的选型表

官方配方是**任务导向**的，每个都经过端到端验证并附带可运行示例。站点索引的编号有跳号（12 是 flagship，13 是运维），下表按用途重排：

| # | 配方 | 什么时候用 | 关键事实 |
|---|---|---|---|
| flagship | **零配置索引** `xerj autoindex` | 手里有一堆敌意混合格式文件（JSONL、方言 CSV、SQLite、PDF、DOCX、日志、SQL dump、gzip——**13 个嗅探家族**） | 1,995 文件 / 518 MB 语料上 **80/81** 项 ground-truth 通过；2,018,398 条记录存活、耗时 **38.1 s**；`kill -9` 后恢复到完全相同的计数（F-349） |
| 01 | **语义搜索 & RAG** | 按意义检索，`semantic_text` 在摄入时自动嵌入，不需要独立向量库 | — |
| 02 | **智能体长期记忆** | `/_memory` API：存、语义 + 关键词召回、元数据过滤、遗忘、按智能体隔离 | — |
| 03 | **长文档段落检索** | 文档很长，需要以**任一段落**参与竞争（best-passage，max-sim 评分） | **98% top-3 vs 汇总式 32%**（F-350） |
| 04 | **向量搜索 kNN** | `dense_vector` 上的最近邻 | 未过滤 HNSW，过滤走精确扫描 |
| 05 | **向量量化** | 把 `dense_vector` 字段 opt-in 到 `scalar8`（接受 ES 的 `int8_hnsw`） | **recall@10 = 0.998**（F-351）。**精度，不是内存**（见 [05](/concepts/05-vector-and-hybrid.md)） |
| 06 | **混合搜索** | 关键词 + 向量在一次查询里——结果不是 BM25 单独能找到的，也不是 kNN 单独能找到的 | — |
| 07 | **日志分析** | 从原始日志到仪表盘：错误率、p95 延迟、Top 服务 | — |
| 08 | **异常检测** | `_ml` 的统计型检测器，标记指标与日志里的尖峰 | — |
| 09 | **持续异常数据流** | 定时重算索引并把异常记录存下来供轮询 | — |
| 10 | **从 ES 迁移** | 把现有 ES 客户端指向 XERJ | 同线协议，换 URL |
| 11 | **索引 PDF/Word/网页文件夹** | 递归走 PDF/DOCX/HTML/MD/TXT，抽取 + 分块 + 自动嵌入 | **21/22 vs 公平 grep 基线的 14/22**，决定性差距在 `binary_only`（**6/7 vs 0/7**）——grep 读不了 PDF/DOCX（F-352） |
| 13 | **完全离线运行** | 空气隔离部署：在一台联网机器上预置 release、校验和与可选的三文件神经模型包 | 覆盖词法默认、本地神经资产、代理/ONNX 边界、回环/认证姿态、WAL overlay 与 Console 的系统字体回退 |

### 选型建议

| 你的目标 | 走哪条 |
|---|---|
| 让一个文件夹可被智能体检索 | flagship（`autoindex`），然后 `autoindex map` |
| 按意义检索自己的文档 | 01（先决定 `--embed-mode`，因为它在摄入时绑定） |
| 让智能体跨会话记事 | 02（`/_memory`） |
| 文档很长、答案在某一段里 | 03（passage retrieval） |
| 已有嵌入向量，要近邻 | 04 |
| 想少一点召回损失换打分精度 | 05（注意：**不是**省内存） |
| 关键词与语义都要 | 06（`hybrid`，`fusion: rrf`） |
| 日志 / 指标 / trace | 07 · 08 · 09 · Playbook 02 · Playbook 05 |
| 替换 ES | 10 + [04 从 ES 迁移的评估路径](/examples/04-migration-from-elasticsearch.md) |
| 合规环境无外网 | 13 |

## 5 个 Playbook

Playbook 是**顶级 ES 用例的完整配方**：一份 schema、一条摄取命令、一个查询，以及把它可视化的仪表盘（F-353）：

| Playbook | 覆盖 | 值得注意的查询 |
|---|---|---|
| **01 SIEM** | 认证日志、防火墙丢弃、进程执行、DNS 查询 | 5 个检测：Top 源 IP；异常父进程（`parent=wininit.exe` + `terms` 进程名）；**DNS 隧道候选**（正则 `[a-zA-Z0-9]{30,}\..*`）；横向移动（`terms` 动作 + `cardinality` 去重主机数）；`date_histogram` 尖峰检测（F-354） |
| **02 日志分析** | Nginx、JSON、syslog、OTLP 高速摄取 | p95 延迟用 `terms` + `percentiles` 嵌套；保留策略需自己删索引（`[logs] retention_days` 未接线） |
| **03 向量 · RAG** | 一台机器上索引向量、混合检索 | `hybrid` 是**查询子句**，要放在 `query` 内部，且 `queries` 每一项把自己的子句包在 `query` 里（`linear` 融合时的可选 `weight` 放在旁边）（F-357） |
| **04 全文检索** | 倒排 + BM25 + 分析器 + 高亮 + 查询期加权 | `multi_match` 字段加权 `"fields": ["title^3", "body"]`；`match_phrase` 带 `slop`；`bool` 的 must + filter；terms + date_histogram 双层聚合（F-356） |
| **05 可观测性** | 指标 + trace + 日志一体 | 三个独立索引；OTLP 直入**无需 collector**；用 `trace_id` 关联日志（F-355） |

> SIEM 与日志分析两个 Playbook 的仪表盘在 playground 里（`ANOMALY → DETECT`、`LOGS → OVERVIEW`）。

## Corpus Hub：两条通道

官方文档站新增的 [Corpus Hub](https://hub.xerj.org) 页面把「参考语料」做成了**公开注册表**：每个语料固定到确切 commit、经人工许可证审查，记录包还带校验和与签名（F-342）。

| 通道 | 形态 | 是什么 | 适合 |
|---|---|---|---|
| **Lane A** | `tools/xerj-code/hub/<name>.json`（清单） | **别人的源码**在固定 commit 上 | 参考编码（「三个引擎分别怎么实现合并策略？」） |
| **Lane B** | `tools/packs/<name>/recipe.toml`（配方） | **从多源蒸馏出的结构化记录** | 整理好的数据集（如首个 `rust-vulns` 包：1,950 条 Rust 漏洞公告，跨 osv.dev 与 RustSec 做身份合并，每日重建并签名） |

**判断你的内容属于哪条**：是「别人能克隆的文件」→ Lane A；是「从若干来源蒸馏出的记录」→ Lane B。

### 许可证三档

每份源都带一个人工审查块，三种判定之一（F-343）：

| 判定 | 许可证 | 含义 |
|---|---|---|
| `adapt-with-attribution` | Apache-2.0 · MIT · BSD | 改写时引 `file:line`；许可证内复制没问题 |
| `approach-only` | AGPL · SSPL · Elastic · BUSL · GPL | **读设计，自己写代码，绝不粘贴** |
| `mixed` | 逐文件分档 | 在 note 里指明边界 |

> 文档记录了项目自己的一个教训（F-344）：许可证检测器**曾把 Elasticsearch 报成 Apache-2.0**——因为 AGPL 文本里含有 "an \"Apache License 2.0\" compatible license" 这一句。**检测器的假阳性，正是受限代码被粘进 Apache-2.0 项目的路径。**

### 贡献流程

```sh
git clone -b corpus-hub https://github.com/xerj-org/xerj && cd xerj
# 写 tools/xerj-code/hub/<your-name>.json 或 tools/packs/<name>/recipe.toml
python3 tools/xerj-code/hub/validate_hub.py     # 本地校验（仅标准库）
git checkout -b corpus/<your-name>
git add tools/xerj-code/hub/<your-name>.json
git commit -m "corpus: add <your-name> (<domain>)"
git push -u origin corpus/<your-name>
```

**必须从 `corpus-hub` 分支切出**（不是 main），这样 CI 工作流会随 PR 一起进来（F-345）。CI 除同一份校验器外还跑两条注册表守卫（F-346）：

- 注册表路径下**不得有超过 5 MB 的文件**（构建出的包与密钥材料不得入库）；
- `tools/packs/keys/` 下**不得有私钥材料**。

构建出的包**从不入库**——维护者从配方构建，把签名的包挂到 GitHub Release，清单链接它；git 里的注册表只存配方与清单（F-347）。

### 两个「适不适合」的问题

都是实测式的，不是感觉（F-348）：

1. **能否说清领域？** 补完这句话："an agent working on ___ would query this for ___." 语料是**按领域**建的，不是按语言或知名度——一个什么都有的语料，检索起来就像没有查询的搜索引擎。
2. **内容是否未被模型记住？** 检索的实测收益在小众、私有、内部、训练截止后的材料上；在模型已知的热门公共库上，检索是开销。

---

## 复核方法：遇到文档与代码不一致怎么办

文档站首页立的规则是（F-208）：

> If the docs and the code disagree, **the code is right**. File a bug; we'll reconcile the docs.

这条规则是**可执行**的，因为文档的每个数字都能机械复核。本轮复核的结果——**四处不一致**：

| # | 不一致点 | 文档说法 | 代码事实 | 处置 |
|---|---|---|---|---|
| 1 | 查询类型数量 | 站点导航写 "32 variants"；同页正文列 50 | `SUPPORTED_QUERY_TYPES` = **50** | 以代码与正文为准（F-209、F-212） |
| 2 | 配置文件默认路径 | CLI 页写 `--config` 默认 `./xerj.toml` | `main.rs:699` 只查 `--config` → `XERJ_CONFIG`，**无 `./xerj.toml` 回退** | 以代码与配置页为准（F-256、F-257） |
| 3 | 一致性用例总数 | 迁移页写 1,371/1,374（2026-09-20）；README 徽章写 1,366/1,369 | 两者都是**发布说明**而非代码事实；门禁不变量是「0 失败」 | 两者都记录，说明差异来自快照时点（F-319、F-320） |
| 4 | explain 端点路径 | 原生 API 页写 `POST /v1/indices/:name/_explain`；迁移页写 `/v1/explain-plan` | 两者都未在 `xerj-api/src/router.rs` 中以该字面路径出现 | 记录冲突，不替上游裁决（F-335、F-336） |

**复核成本极低**——上面四处全部是「数一个常量 / 跑一个 grep / 比一张表」级别的操作，合计不到十分钟。养成这个习惯后，官方文档就从「信源」变成了「线索」。

### 复核清单

| 要核的 | 怎么核 |
|---|---|
| 一个数字 | 在 `engine/crates/` 里找对应常量或数组，**脚本计数**而不是目测 |
| 一个端点路径 | `grep` `xerj-api/src/router.rs` 与 `native.rs` / `es_compat.rs` |
| 一个配置键 | 查 `xerj-common/src/config.rs` 的结构体字段；**注意「accepted but not wired」** |
| 一个查询/聚合类型 | 数 `SUPPORTED_QUERY_TYPES` / `SUPPORTED_AGG_TYPES` |
| 一个默认值 | 查 `engine/xerj.default.toml` 与 `config.rs` 的 `Default` 实现 |

## 相关概念

- [05 官方文档地图与选型](/examples/05-official-docs-map.md)：本文
- [12 配置与环境变量](/concepts/12-config-and-environment.md)：未接线键的完整清单
- [08 参考编码与语料库](/concepts/08-reference-coding.md)：语料闭环与许可证纪律
- [Examples 索引](index.md)：全部示例
