---
type: Reference
title: XERJ 官方文档站信源登记
description: 第二轮信源登记——xerj.org/docs/ 在线文档站 46 页与本地落地快照 landing/docs 的对应关系、版本锚点、页面清单与采信规则
tags: [xerj, 信源登记, 官方文档, 文档站]
generated: { by: source-code-to-okf-wiki/R, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-docs-site
    resource: https://xerj.org/docs/
    title: XERJ 官方文档站（v1.0.0-rc.97）
  - id: xerj-docs-snapshot
    resource: /references/docs-source.md
    title: 本轮采集所依据的文档站落地快照
---

# XERJ 官方文档站信源登记

## 双源对应关系

XERJ 的文档站不是独立维护的站点仓库——它由**同一个仓库的 `landing/docs/` 目录**直接部署（Cloudflare Pages 以 `landing/` 为发布根，提交即上线，无构建步骤）。

| 项 | 值 |
|---|---|
| 在线文档站 | `https://xerj.org/docs/` |
| 落地快照 | `external/dao/search/xerj/landing/docs/`（工作区内相对路径） |
| 快照提交 | `51ff219276d7e55d9d85b4938e8b94f235f9d099`（与第一轮同一快照） |
| 站点版本标识 | 页脚与侧栏均为 `XERJ.AI · V1.0.0-RC.97 · 2026-08-11` |
| 引擎版本 | `engine/Cargo.toml` 的 `[workspace.package] version = "1.0.0-rc.97"` |
| 页面总数 | **46** 个 HTML 页面（脚本计数） |

**版本锚点一致性已核对**：在线站页脚版本、快照页脚版本、引擎 `Cargo.toml` 的 workspace 版本三者一致，均为 `1.0.0-rc.97`；`git describe` 的 `v1.0.0-rc.97-38-g51ff2192` 表明快照位于该 rc 之后 38 个提交，与「站点由 main 分支部署」一致。

> **本轮采信规则**：以**本地落地快照**为事实来源（路径稳定、内容固定在 commit 上），以**在线站点**为呈现面对照。二者版本一致，因此不存在「文档站比快照新」的问题；文中凡引用官方文档的表述，均已回到快照文件逐字核对。

## 页面清单（46 页，按站点导航分组）

| 分组 | 页面 | 页数 |
|---|---|---:|
| 首页 | `index.html` | 1 |
| START | `quickstart.html`、`install.html`、`migration-from-es.html` | 3 |
| REFERENCE | `cli.html`、`config.html`、`env.html`、`api-native.html`、`api-es-compat.html` | 5 |
| DATA MODEL | `queries.html`、`aggregations.html`、`analyzers.html`、`vectors.html` | 4 |
| ENGINE | `ingest.html`、`storage.html`、`compression.html`、`clustering.html`、`metrics.html`、`security.html` | 6 |
| OPERATIONS | `operations.html`、`backup-restore.html`、`upgrades.html`、`troubleshooting.html` | 4 |
| PLAYBOOKS | `playbooks/{siem,log-analytics,vector-search,full-text,observability}.html` | 5 |
| RECIPES | `recipes/*.html` | 13 |
| CORPUS HUB | `corpus-hub.html` | 1 |
| FOR AI | `agents/{index,quickstart,endpoints}.html` + `agents/schemas/*.json` | 3 + 4 |

## 文档站自述的权威规则

文档站首页把它的方法论写在了最显眼的位置（F-208）：

> **Read the source.**
> Every key, every flag, every default in these docs comes out of the Rust crates under `engine/crates/`. If the docs and the code disagree, **the code is right**. File a bug; we'll reconcile the docs.

这条规则正是本轮交叉验证的依据：文档站的每个数字、每个键、每个端点，都回到 `engine/crates/` 复核。**复核结果记录在 [facts-docs.md](facts-docs.md)，发现的不一致集中列在 [insights-docs.md](insights-docs.md)。**

## 与第一轮信源的关系

| 轮次 | 信源 | 覆盖 | 事实编号 |
|---|---|---|---|
| 第一轮 | 仓库 README / AGENTS.md / ARCHITECTURE.md / WHY_XERJ.md / llms.txt / 源码 / `tools/xerj-code/` | 定位、架构、autoindex、MCP、检索、向量、记忆、基准、参考编码 | F-001～F-206 |
| **第二轮（本文件）** | **官方文档站 46 页** | **参考层（CLI/配置/环境/API）、数据模型层（查询/聚合/分析器/向量）、引擎层（摄取/存储/压缩/集群/指标/安全）、运维层（生产/备份/升级/排障）、Playbook、Recipe、Corpus Hub** | **F-207～F-338** |

两轮信源在代码上重叠、在**叙事层级**上互补：第一轮从源码与上游自述出发，第二轮从**运维者与使用者的手册**出发。同一个事实在两轮中被独立记录——例如「默认嵌入是词法」在第一轮是 `local.rs` 的代码事实，在第二轮是配置页与 `vectors.html` 的文档事实；两处一致时互为印证，不一致时以代码为准。

## 页面级索引

| 页面 | 本知识包由哪篇文档承接 |
|---|---|
| `index.html` | [00 整体架构](/concepts/00-overview.md)（定位与导航哲学） |
| `quickstart.html` | [01 安装与快速上手](/concepts/01-getting-started.md) |
| `install.html` | [01 安装与快速上手](/concepts/01-getting-started.md) |
| `migration-from-es.html` | [04 从 Elasticsearch 迁移的评估路径](/examples/04-migration-from-elasticsearch.md) + [07 ES 兼容与基准诚实性](/concepts/07-es-compat-and-benchmarks.md) |
| `cli.html` | [12 配置与环境变量](/concepts/12-config-and-environment.md) |
| `config.html` | [12 配置与环境变量](/concepts/12-config-and-environment.md) |
| `env.html` | [12 配置与环境变量](/concepts/12-config-and-environment.md) |
| `api-native.html` | [12 配置与环境变量](/concepts/12-config-and-environment.md)（原生表面清单） |
| `api-es-compat.html` | [04 检索路径与响应裁剪](/concepts/04-search-query-path.md) + [07](/concepts/07-es-compat-and-benchmarks.md) |
| `queries.html` | [09 查询类型与聚合](/concepts/09-query-types-and-aggregations.md) |
| `aggregations.html` | [09 查询类型与聚合](/concepts/09-query-types-and-aggregations.md) |
| `analyzers.html` | [10 分析器与摄取管线](/concepts/10-analyzers-and-ingest.md) |
| `vectors.html` | [05 向量、嵌入与混合检索](/concepts/05-vector-and-hybrid.md) |
| `ingest.html` | [10 分析器与摄取管线](/concepts/10-analyzers-and-ingest.md) |
| `storage.html` | [11 存储、压缩与集群现状](/concepts/11-storage-compression-clustering.md) |
| `compression.html` | [11 存储、压缩与集群现状](/concepts/11-storage-compression-clustering.md) |
| `clustering.html` | [11 存储、压缩与集群现状](/concepts/11-storage-compression-clustering.md) |
| `metrics.html` | [13 生产运维与排障](/concepts/13-operations-and-troubleshooting.md) |
| `security.html` | [12 配置与环境变量](/concepts/12-config-and-environment.md) |
| `operations.html` | [13 生产运维与排障](/concepts/13-operations-and-troubleshooting.md) |
| `backup-restore.html` | [13 生产运维与排障](/concepts/13-operations-and-troubleshooting.md) |
| `upgrades.html` | [13 生产运维与排障](/concepts/13-operations-and-troubleshooting.md) |
| `troubleshooting.html` | [13 生产运维与排障](/concepts/13-operations-and-troubleshooting.md) |
| `playbooks/*.html` | [05 官方文档地图与选型](/examples/05-official-docs-map.md) |
| `recipes/*.html` | [05 官方文档地图与选型](/examples/05-official-docs-map.md) |
| `corpus-hub.html` | [08 参考编码与语料库](/concepts/08-reference-coding.md) |
| `agents/*.html` | [03 MCP 智能体接口](/concepts/03-mcp-agent-surface.md) + [06 智能体记忆与第二大脑](/concepts/06-agent-memory-and-brain.md) |

## 相关参考

- [第二轮事实清单](facts-docs.md)：F-207～F-338
- [第二轮洞察](insights-docs.md)：洞察 7～12
- [第一轮信源登记](source.md)：源码快照与计数口径
- [References 索引](index.md)：本目录汇总
