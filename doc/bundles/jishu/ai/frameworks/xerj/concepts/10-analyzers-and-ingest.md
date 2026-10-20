---
type: Concept
title: 分析器与摄取管线
description: XERJ 的四个内置分析器与选择规则、四条进程内摄取路径（turbo-ingest/logs/syslog/otlp）、以及端到端背压的两种形态
tags: [xerj, 分析器, 摄取, pipeline, 背压]
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

# 分析器与摄取管线

## 分析器：源码注册 11 个，官方文档只写了 4 个

分析器把原始文本变成 token 流。**每个文本字段在索引创建时恰好选定一个分析器**。

> ⚠️ **先说清一件必须以代码为准的事**：官方文档 `analyzers.html` 列出 4 个内置分析器（`standard`、`whitespace`、`simple`、`english`），但源码 `xerj-fts/src/analyzer.rs` 的 `register_defaults()` 实际注册 **11** 个（F-218）。**`simple` 在整个 `engine/` 树中零次出现**——它不可用；而源码的 `keyword`、`lowercase`、`stemmer`、`cjk`、`thai`、`icu_folding`、`ecommerce`、`code` 八个分析器**未被文档提及**。

### 真实的 11 个（以注册处注释为准，F-219）

| 分析器 | 管线 | 适用 |
|---|---|---|
| `standard` | Unicode 词切分 + 小写化，**无停用词、无词干** | 默认选择。**刻意与 ES 的 `standard` 逐语义一致** |
| `english` | **旧的** `standard` 管线：unicode 切分 + 小写化 + 英文停用词 + Snowball 词干 | 对齐 ES 的 `english`；需要 "running"/"runs" 匹配时用 |
| `whitespace` | 只按空白切分，无归一化 | 多词标识符、代码，需要精确 token 匹配 |
| `keyword` | 整个输入作为**单个 token** | 整值匹配（ID、枚举值） |
| `lowercase` | whitespace 分词 + 小写化 | 常见 ES 分析器 |
| `stemmer` | standard + Snowball 词干，**无停用词** | 想要词干但不想丢 "GET" 这类词 |
| `cjk` | CJK / 日 / 韩 **bigram** 分词器 | 中文、日文、韩文 |
| `thai` | 泰文**词边界**分词器 | 泰文（无空格分词） |
| `icu_folding` | **NFKC 归一化**过滤 + standard 分词器 | 全半角/兼容字符归一 |
| `ecommerce` | standard 分词 + 精选同义词表（**双向扩展**）+ Snowball 词干 | 电商商品标题 |
| `code` | 面向代码的管线 | 代码检索 |

### 三个值得记住的细节

**一、`standard` 为什么不含停用词与词干。** 源码注册处的注释给出了完整理由（F-358）：

> `standard` —— 逐语义匹配 ES：Unicode 词切分 + 小写化，**无停用词、无词干**。此前的管线含英文停用词（会丢掉 "GET"）与 Snowball 词干（会过度匹配 "static"/"statics"）——两者都造成与 Elasticsearch 默认 `standard` 的语义偏离。想要旧行为的索引可以在映射里显式命名为 `english`。

> **反常识**：官方文档说 `standard` 含英文停用词表——**恰好相反**。这是「为对齐上游而做的改动」没同步到文档的典型。

**二、`english` 不是「standard + 词干」，而是「旧的 standard」。** 文档写 "standard + Porter2 词干 + 更大的停用词表"（F-358）；源码说它是旧 `standard` 管线，且词干实现是 `rust_stemmers` 的 **Snowball**（`Algorithm::English`），不是文档所称的 Porter2。

**三、`ecommerce` 的同义词扩展是双向的。** 源码注释举例：搜 "sneakers" 也会匹配含 "trainers" 或 "shoes" 的文档——因为同义词表把两侧都映射到同一概念。词表在源码中约 77 条字面量。

### 选择规则（一个字段无自有分析器时）

> 没有自有分析器的文本字段，使用**索引声明的 `analysis.analyzer.default`**；索引未声明则用 `standard`（F-220）。

```json
{
  "fields": {
    "message": { "type": "text", "analyzer": "english" },
    "raw":     { "type": "text", "analyzer": "whitespace" }
  }
}
```

> **多语言与代码的实践建议**：中文语料用 `cjk`（bigram），泰语用 `thai`，全半角混排用 `icu_folding`，代码用 `code`——这四个在官方文档里**都不存在**，只能从源码发现。

### 一个必须知道的「没接线」

节点侧 `[fts] default_analyzer` 被接受但**未接线**——改离默认值只会在启动时打一条警告，行为不变（F-221、F-260）。要改默认分析器，**在创建索引时的 mapping 里按字段或按索引声明**。

> 这正是洞察 7 的一个最小实例：一个看起来是全局开关的键，实际是无效的。查证判据见 [12 配置与环境变量](/concepts/12-config-and-environment.md)。

### `english` 与 turbo 路径

文档提到 `english` 的词干化可以由 `[indexing] turbo_fast_analyzer = true` 关闭以换摄入速度（F-219）——但同一个键也被标注为**未接线**（F-260），且 turbo 路径会忽略它、字段保留各自的分析器。**因此这条「关闭」路径在当前构建里不生效**。

## 摄取管线：四条路径，进程内解析

XERJ 的解析器**在写入器内进程内运行**：一次 fsync、一次网络跳转，**没有 Logstash 层**（F-222）。四条路径覆盖多数真实负载：

### 1. `turbo-ingest` —— NDJSON 批量（快路径）

文档以 NDJSON 到达，**跨核并行分词**，成批进入 memtable。

```sh
curl -sX POST http://localhost:8080/v1/indices/logs/turbo-ingest \
  -H 'Content-Type: application/x-ndjson' \
  --data-binary @nginx.jsonl
```

三个 `[indexing]` 键对应这条路径：`turbo_batch_size`（每批文档数，默认 1000，范围 500～5000）、`turbo_parallel`（Rayon 线程上的并行分词）、`turbo_fast_analyzer`（跳过词干化与停用词）——**三者在本构建中都被接受但未接线**（F-260）：turbo 请求按一个批次索引，turbo 摄入不再预分词（没有可并行之物），turbo 路径忽略快速分析器开关。

> 换句话说，**turbo 模式的三个旋钮当前都是装饰**。真实存在的差别是 turbo 走的是批量 NDJSON 路径而非逐文档。

### 2. `logs` —— 自动识别时间戳

发送原始日志行——Apache combined、Nginx access、ISO-8601 结构化。摄取路径**检测格式、把时间戳归一化到秒、存下结构化字段**，无需正则配置。

```sh
curl -sX POST http://localhost:8080/v1/indices/logs/logs \
  -H 'Content-Type: text/plain' \
  --data-binary @access.log
```

### 3. `syslog` —— RFC-5424

接受原始 syslog 帧，解析信封、抽取结构化字段、索引 message。

```sh
curl -sX POST http://localhost:8080/v1/indices/syslog/syslog \
  -H 'Content-Type: text/plain' \
  --data-binary @messages
```

### 4. `otlp` —— OpenTelemetry

OTLP HTTP protobuf，**前面不需要 collector**。接受 logs、metrics、traces；**trace 落成连通图而非扁平文档**（F-223）。

```sh
curl -sX POST http://localhost:8080/v1/indices/traces/otlp \
  -H 'Content-Type: application/x-protobuf' \
  --data-binary @spans.pb
```

> 「trace 落成连通图」是这四条路径里最有意思的一条：可观测性负载里 trace 天然是一棵树/一张图，把它存成扁平文档会丢掉 span 之间的父子关系。XERJ 保留了这个结构。

## 背压：端到端的两种形态

背压不是「等到 OOM 再拒」，而是两种主动形态（F-224）：

| 触发 | 表现 |
|---|---|
| memtable 接近 `flush_size_mb` | **写入器开始阻塞**，而不是 OOM |
| WAL 滚动快于 segment flush | `turbo-ingest` 返回 **429** 并带 `Retry-After` 头 |

429 这一条与 autoindex 客户端的语义是同一套（见 [02 autoindex 零配置流水线](/concepts/02-autoindex-pipeline.md)）：429 是节点内存断路器短时卸荷，客户端应降低并发、退避后**只重发被拒条目**并继续，而不是当作失败中止。

## 四条路径的选型

| 数据形态 | 用哪条 | 理由 |
|---|---|---|
| 已经结构化的 NDJSON | `turbo-ingest` | 无需再解析，最快 |
| 原始 Web/代理访问日志 | `logs` | 自动识别时间戳与格式，零配置 |
| 网络设备 syslog | `syslog` | RFC-5424 信封解析 |
| OpenTelemetry 导出 | `otlp` | 无 collector，trace 保留图结构 |
| 混合格式文件夹 | `xerj autoindex` | 见 [02](/concepts/02-autoindex-pipeline.md) |

## 相关概念

- [02 autoindex 零配置流水线](/concepts/02-autoindex-pipeline.md)：文件夹摄取与 429 背压语义
- [10 分析器与摄取管线](/concepts/10-analyzers-and-ingest.md)：本文
- [12 配置与环境变量](/concepts/12-config-and-environment.md)：未接线键的完整清单
- [13 生产运维与排障](/concepts/13-operations-and-troubleshooting.md)：摄入吞吐下降的排障路径
- 事实来源：[第二轮事实清单](/references/facts-docs.md)
