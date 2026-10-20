---
type: Example
title: 从 Elasticsearch 迁移的评估路径
description: 迁移评估实操——用 autoindex 作为低成本对照实验、兼容面与不兼容面清单、滚动替换的顺序、以及必须自己承担的运维工作
tags: [xerj, 示例, 迁移, elasticsearch, 评估]
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

# 从 Elasticsearch 迁移的评估路径

本示例给出一条**低成本、高信息量**的评估路径。它不假设你要迁移，只假设你想知道自己该不该考虑迁移。

## 第 0 步：先分开两个问题

XERJ 同时是**摄取客户端**与**检索引擎**。它们可以分开评估：

| 问题 | 怎么测 | 成本 |
|---|---|---|
| XERJ 的检索引擎比 ES 准/快吗？ | 拿自己的语料与查询集对拍 | 中 |
| XERJ 的摄取能力比「人写 Logstash 管线」省事吗？ | 跑一次 autoindex 对照实验 | 低 |

> **反常识**：`autoindex` 是纯 ES 兼容 HTTP 客户端，**不链接 `xerj-engine`**（F-027）。所以你**可以把它指向一台真实的 Elasticsearch**——这是一个成本极低、信息量极高的对照实验：同一份摄取代码，两个后端，谁的结果更可用？

## 第 1 步：三个零成本的对照实验

### 实验 A：把 autoindex 指向真实 ES

```sh
# 同一个客户端，指向真实 ES（注意 auth 与 ES 一致）
xerj autoindex ~/my-corpus --url https://es.internal:9200 --api-key "$ES_KEY" --prefix probe
```

你会得到：每个文件被识别成什么类型、抽出哪些字段、落到哪些数据集。这份「数据地图」是 ES 侧**没有**的能力——你可以拿它去评估自己的管线，而不是只评估引擎。

### 实验 B：同一份查询，两边各跑一次

```sh
# ES
curl -s "$ES_URL/probe-*/_search" -H 'content-type: application/json' \
  -d '{"query":{"match":{"body":"rotate WAL segment"}},"size":5}' | jq '.hits.total'

# XERJ
curl -s "http://localhost:9200/probe-*/_search" -H 'content-type: application/json' \
  -d '{"query":{"match":{"body":"rotate WAL segment"}},"size":5}' | jq '.hits.total'
```

**注意响应大小**——这往往比结果本身更能说明问题。XERJ 的默认响应是完整文档，源码类语料下很可能是几百 KB（F-087）；加上 `"fields":["_passage"]` 后是几十 KB（34 倍缩减，F-087）。ES 也有 `_doc`/stored fields 机制，但默认值不同——**比较时要把裁剪做进两边**，否则比的是默认配置的差异，不是引擎的差异。

### 实验 C：把「智能体的真实问题」变成查询集

拿一个智能体在你们代码库上会问的 20 个问题，写成查询，两个引擎各跑一遍，人工判定 top-3 是否包含正确段落。

这比跑 ES 官方 YAML 套件更有信息量：套件测的是**语法兼容**，你的查询集测的是**实际有用**。

## 第 2 步：兼容面清单

XERJ 实现 ES REST API 的这些部分（F-152）：

```
indices · documents · bulk · search · aggregations · mappings
kNN · scroll · reindex · _cat 端点
```

Kibana 与官方客户端库可直接连接。一致性套件当前通过 **1366/1369** 个用例，分布在 15 个套件目录、221 个用例文件（F-149、F-150）。

### 一个必须知道的语义边界

**scroll 是有界的前置快照，不是逐 segment 游标**（F-153）：

> 精确总数超出快照窗口的查询被**拒绝为 400**，而不是静默截断。

如果你的导出工具依赖 scroll 扫全量，需要改成 `search_after`。这是迁移中最容易「看起来跑通了但结果少了」的地方——ES 会静默给你一个截断的快照，XERJ 会拒绝。这个差异是**对你有利的**。

## 第 3 步：性能与失败面

对拍记分卡（对照 live ES 8.13.4，F-154）：

| 维度 | 值 |
|---|---|
| 胜 / 平 / 负 | 55 / 26 / 4 |
| 摄入吞吐 | 1.72× |
| 磁盘占用 | 1.61× 更小 |

完整矩阵上还有 3 个 N/A（F-156）。

**四处失败全部是同一格：高写入速率下运行的读 p99**（F-155）。上游把它写成了完整发现文档 `demo/playbooks/MIXED_READ_UNDER_WRITE_FINDING_2026-07-08.md`，而不是略去。

> **行动**：按自己的负载形状对号入座。「批量写入 + 读多写少」是 XERJ 的优势区；「持续高速写入 + 读延迟敏感」正是那 4 处失败所在——那是你要付代价的地方。

基准方法学是闭环、关缓存、语料相同、带正确性校验（**更快但算错算输**），发布前经独立对抗复测（F-157）。XERJ 侧的头条指标有一键复现脚本在 `scripts/bench/`（F-158）。**用你的语料重跑，别直接采信别人的数字。**

## 第 4 步：兼容买到了什么、没买到什么

上游的表述很清楚（F-008、F-010）：

**买到**：零成本采用。迁移就是「改 URL」。

**没买到**：使命。仍然存在的兼容缺口被公开追踪（`demo/playbooks/` 里的 stub 审计与兼容文档），路线图由智能体工作流驱动，不是追逐功能清单对标。

## 第 5 步：迁移中要自己承担的事

| 项 | 说明 |
|---|---|
| 认证 | 默认开启，`admin.key` 在 `<data_dir>/admin.key`；`--insecure` 只适合单机开发（F-159、F-160、F-161） |
| 服务端堆 | 三个 per-segment 缓存在合并回收其 segment 之前无上限（F-100）；一次观测到 20.2 GB 常驻（F-101）。一次索引一个语料，盯 RSS，语料之间重启节点 |
| 集群 | `xerj-cluster` 的 Raft 只管集群元数据，数据面是单机 LSM 风格结构（F-017） |
| 告警 | 只有一个 watch 形态真实可用，其余返回 501；重启不恢复 watch（F-169、F-170） |
| 用户摄入插件 | 未实现，转换管线只有内置原生代码（F-171） |
| 滚动升级 | 快照/恢复只支持**子集**，见 `docs/SNAPSHOT_AND_RESTORE.md` |
| 语料包 | 记录包（record pack）真实可用，带 SHA-256 与可选 ed25519 签名校验（F-172）；**预索引包尚不存在**（F-173） |

## 第 6 步：XERJ 独有的那一层

如果迁移只是「换个更快的 ES」，那 XERJ 的差异化价值就浪费了。它真正多出来的是三件 ES 没有的东西（F-011）：

| 能力 | 端点/命令 | 替代物 |
|---|---|---|
| 零设计入库 | `xerj autoindex <folder>` | 人写映射 + Logstash/Beats 管线 |
| 面向智能体的定位 | `xerj autoindex map` + `autoindex-catalog` | 只有 `_cat/indices` |
| 跨会话连续性 | `/_memory/{ns}`、`/_graph/{brain}` | 自己搭 |

第三件尤其值得注意：智能体记忆不是一个「附加功能」，而是让智能体从一次性问答变成**有连续性的协作者**的东西。在 ES 上做同样的事，需要额外一套向量库 + 嵌入服务 + 记忆存储。

## 一个务实的推荐路径

不要做「一次性切换」。建议：

1. **并行期**：新查询走 XERJ，老查询留在 ES。两者用同一份摄取代码（autoindex 双写）。
2. **观测期**：比较响应大小、p99、召回质量，以及**智能体 token 消耗**。
3. **收敛期**：把 ES 侧真正不可替代的能力（如果有）单独保留，其余迁走。
4. **留后门**：`search_after` 替代 scroll；`autoindex --prefix` 分语料命名空间；`_xerj.hints` 的严格字段模式先不开。

## 评估清单

- [ ] 跑过旗舰回路（`autoindex` → `map` → 查询），而不只是线协议测试
- [ ] 读过 `llms.txt` 的 Caveats
- [ ] 用自己的查询集对比过召回，而不只看套件通过率
- [ ] 按自己的负载形状看过那 4 处失败
- [ ] 用 `scripts/bench/` 复现过关键数字
- [ ] 算过服务端堆的增长（尤其多语料连续索引）
- [ ] 确认了 `scroll` → `search_after` 的改造范围
- [ ] 确认了智能体记忆这类「ES 没有的东西」是否真的需要

## 相关概念

- [07 ES 兼容与基准诚实性](/concepts/07-es-compat-and-benchmarks.md)：兼容面、记分卡、能力边界
- [02 autoindex 零配置流水线](/concepts/02-autoindex-pipeline.md)：摄取侧的完整机制
- [06 智能体记忆与第二大脑](/concepts/06-agent-memory-and-brain.md)：ES 没有的那一层
- [01 安装与快速上手](/concepts/01-getting-started.md)：认证与信任边界
- [Examples 索引](index.md)：全部示例
