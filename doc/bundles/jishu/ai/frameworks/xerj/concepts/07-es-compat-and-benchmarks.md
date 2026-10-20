---
type: Concept
title: ES 兼容与基准诚实性
description: XERJ 的 Elasticsearch 8.x 线协议兼容面、零失败一致性门禁、对拍 ES 8.13.4 的记分卡与四处败因、基准方法学，以及能力边界与未实现清单
tags: [xerj, elasticsearch, 兼容性, 基准, 诚实性]
generated: { by: source-code-to-okf-wiki/E, at: 2026-10-20T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-10-20T00:00:00Z }
status: stable
stale_after: 2027-04-20
sources:
  - id: xerj-facts
    resource: /references/facts.md
    title: XERJ 事实清单
  - id: xerj-insights
    resource: /references/insights.md
    title: 架构洞察与知识地图
---

# ES 兼容与基准诚实性

本篇讲两件事：**兼容到什么程度**（决定迁移成本），以及**它在哪里会输**（决定能不能押注）。后者在上游文档里写得比前者更详细，这不是偶然。

## 兼容面

XERJ 实现 Elasticsearch REST API 的这些部分（F-152）：

indices · documents · bulk · search · aggregations · mappings · kNN · scroll · reindex · `_cat` 端点。

Kibana 与官方客户端库可直接连接。迁移在多数场景下就是「改一个 URL」。

一致性命中的机制是 `es-yaml-runner` harness：拿 ES 8.13 的 REST-API-spec YAML 套件打真实服务器。套件目录 **15 个**、用例文件 **221** 个（F-150）：

```
aggregations  bulk  ccr  cluster  delete_by_query  indices  ingest
ml  reindex  scroll  search  security  smoke  update_by_query  vectors
```

当前通过 **1366/1369** 个用例（F-149）。

### 门禁语义

**硬门禁是零失败**（F-151）：通过与跳过的总数会随上游套件演进而变化，因此**判定应基于失败数，而不是某个固定总数**。

> 这是一条容易被忽略的工程纪律：把「1366/1369」写成门禁阈值，等于把门禁绑在一个会漂移的数字上；上游新增一个用例就红。正确做法是把「0 失败」作为不变量，把总数作为报告项。

### 一个必须知道的语义边界

**scroll 是有界的前置快照，不是逐 segment 游标**（F-153）：

> 一个精确总数超出快照窗口的查询被**拒绝为 400**，而不是被静默截断。

任意大小的结果集请用 `search_after`。这条设计是刻意的——静默截断会让人以为拿到了全量数据。

## 记分卡

最新闭环对拍（对照 **live Elasticsearch 8.13.4**）的得分（F-154）：

| 维度 | 值 |
|---|---|
| 胜 / 平 / 负 | **55 / 26 / 4** |
| 摄入吞吐 | 1.72× |
| 磁盘占用 | 1.61× 更小 |

`docs/WHY_XERJ.md` 补充了完整矩阵上的第三态：**3 个 N/A**（F-156）。

### 四处失败是同一格

四处失败全部是同一个缺口：**高写入速率下运行的读 p99**（F-155）。上游没有把它略去，而是写成了完整发现文档 `demo/playbooks/MIXED_READ_UNDER_WRITE_FINDING_2026-07-08.md`。

读懂这件事很重要：如果你的负载是「批量写入 + 读多写少」，XERJ 在写入侧更快、占盘更小；如果你的负载是「持续高速写入 + 读延迟敏感」，那 p99 正是你付代价的地方。

### 基准方法学

上游把方法学写成了政策（F-157）：

- **闭环**：写入的数据参与后续查询；
- **关缓存**；
- **语料相同**；
- **带正确性校验**——「更快但算错」计为**失败**，不算赢；
- 发布前经**独立对抗复测**；
- 复测把数字推向**不利于 XERJ** 的一侧时，公开数字**当天更正**。

XERJ 侧头条指标的一键复现脚本在 `scripts/bench/`：摄入 docs/s、size:0 延迟、kNN 召回、重排阶段契约（F-158）。上游对未复现的数字的态度是：「对你无法复现的任何数字保持怀疑，包括我们的。」

> **可迁移的方法论**：「更快但算错算输」这一条，把基准从营销材料变成了工程约束。它与「4 处失败被完整写出」是同一套政策的两面。

## 兼容带来的与没带来的

`docs/WHY_XERJ.md` 用两张表区分（F-008、F-010）：

**买到的**：零成本采用。一致性门禁要求零失败，所以既有 ES 客户端库、仪表板与习惯原样可用。迁移就是「改 URL」。

**没买到的**：使命。仍然存在的兼容缺口被公开追踪（`demo/playbooks/` 里的 stub 审计与兼容文档），且在 ES 语义确实更好的地方 XERJ 向它收敛——但**路线图由智能体工作流驱动，不是由追逐功能清单对标驱动**。

换句话说：**兼容性是门票，不是作品**。

## 能力边界与未实现清单

上游把「没做什么」与「做到什么程度」同等对待地写下来。几个对评估决策影响最大的：

### 告警：部分可用

真实可用的**只有一个** watch 形态（F-169）：`PUT /_watcher/watch/<id>`，配 `trigger.schedule.interval`（≥ 1 秒）、**单个**索引的 `input.search`、`condition.xerj_decide`（问题、正标签、`p_min`、`k`）与 `index_alert` 动作。后台评估器先用 watch 自己的查询预筛（keyset 分页，100 条/页），再把渲染出的问题送进真实的 `/_decide`，胜出且非弃权、且概率 ≥ `p_min` 时写入 `.xerj_alert_fires`。

其余形态（cron 调度、transform、其他动作类型、多索引输入）返回 **501** 并指名不评估什么。

诚实边界（F-170）：**重启不恢复 watch**；单次 decide 预算 1000。

### 用户摄入插件：未实现

转换管线只有内置原生代码，**树里没有 wasmtime 后端**（F-171）。

### 语料包：记录包真实、预索引包未构建

- **记录包（record pack）自 v1.0.0-rc.78 起真实存在**（F-172）：`xerj corpus build` 把声明式配方变成带校验和的可移植记录包（`format_version` 未知则拒绝，每条记录带许可证与出处）；`corpus add --from <pack>` 校验每个文件的 SHA-256，`--verify-sig` 校验 SHA256SUMS 上的 ed25519 分离签名；首个包 `rust-vulns` 每日重建、签名并作为带日期的 GitHub Release 发布。
- **尚未构建的是「预索引」那一半**（F-173）：可挂载的已建索引包仍不存在。

### 服务端堆增长

服务端**按已索引文档数保留堆**：三个 per-segment 缓存（`stored_value_cache`、`dv_cache`、`id_pos_cache`）在合并回收其 segment 之前无上限（F-100）。观测数据点：一次 lexical 模式节点在大规模多仓库代码语料中途常驻 **20.2 GB**（F-101）。

客户端侧的 RSS  runaway 已修复（#1002：10 万文档摄入后的常驻从约 677 MB 降到约 108 MB；1 GB 邮箱在 16 GiB 上限下可完成），但**服务端**这一侧的告诫仍在。

### 外部连接清单

节点可以打开的出站连接只有四类（F-099）：

| 连接 | 默认 | 携带文档文本 |
|---|---|---|
| 一次性神经模型下载（HuggingFace Hub） | 关闭 | 否 |
| 集群 Raft（到你自己的对等节点） | 关闭 | 否 |
| 嵌入代理（`--embed-mode proxy` / `default_endpoint`） | 关闭 | **是** |
| WAL tap（`PUT /_xerj/wal_tap`） | 关闭 | **是** |

外加一个搜索期的 `rerank`（见 [05](/concepts/05-vector-and-hybrid.md)）。默认节点只联系自己人。

## 兼容性缺口怎么查

| 想知道 | 去哪 |
|---|---|
| 具体哪个 ES 接口不兼容 | `demo/playbooks/` 里的 stub 审计与兼容文档 |
| 一致性套件怎么跑 | `cargo run --release -p es-yaml-runner -- --dir tests/es-compat-yaml/yaml` |
| 基准怎么复现 | `scripts/bench/`；对拍方法学在 `demo/playbooks/` |
| 真实使用反馈 | `user-feedback/` 目录下的现场报告 |

## 评估清单

1. **先跑旗舰回路**（`autoindex` → `autoindex map` → 查询），而不是先测 DSL——那是产品面。
2. **读 `llms.txt` 的 Caveats 再下结论**——那些条目是承载性的，且保持更新。
3. **按自己的负载形状看记分卡**：如果你是「持续写 + 读延迟敏感」，那 4 处失败正是你的场景。
4. **用 `scripts/bench/` 复现头条数字**，不要直接采信。
5. **对照真正的竞争者**：对「让一个文件夹可被智能体检索」这个用例，竞争对手是「一个会写摄取管线的人」，不是 Elasticsearch 的查询 DSL。

## 相关概念

- [00 整体架构](/concepts/00-overview.md)：兼容面在整体中的位置
- [04 检索路径与响应裁剪](/concepts/04-search-query-path.md)：scroll 与 `search_after` 的边界
- [05 向量、嵌入与混合检索](/concepts/05-vector-and-hybrid.md)：kNN 召回的诚实表述、`rerank` 外呼边界
- [02 autoindex 零配置流水线](/concepts/02-autoindex-pipeline.md)：规模化边界
- 事实来源：[事实清单](/references/facts.md)
