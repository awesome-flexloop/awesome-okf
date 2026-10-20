---
type: Example
title: 从一个文件夹到可查询索引
description: 端到端实操——启动节点、估计与决策门、autoindex 索引一个混合语料、用 autoindex map 摸清数据、再用 _passage 做低成本查询
tags: [xerj, 示例, autoindex, 端到端]
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

# 从一个文件夹到可查询索引

本示例走完 XERJ 的旗舰回路：`autoindex` → `autoindex map` → 查询。**这个回路才是产品**，线协议只是入口。

## 场景

假设有一个混杂语料：

```
~/my-project/
├── src/                  # Rust 与 Python 源码
├── docs/                 # Markdown 文档
├── data/                 # CSV、JSONL 日志
├── contracts/            # PDF、.docx
└── .gitignore
```

## 第 0 步：起节点，且别让它索引自己

```sh
# 数据目录放在将被索引的树之外
xerj --insecure --data-dir ~/.xerj-data &
```

`data/` 不在内置忽略列表里，把 `--data-dir` 放在 `~/my-project` 里，节点会把自己的 WAL 与 segment 一起索引进去（F-057）。

## 第 1 步：先估，不要先跑

```sh
xerj autoindex ~/my-project --dry-run
```

`--dry-run` 走完遍历、嗅探与采样，**一个字节都不写**（F-056）。它会打印作业规模行，例如：

```
autoindex: 1995 files (518 MB) under /home/you/my-project
```

因为索引可能要占别人的笔记本几分钟而对方看不到你的工具输出，正确的做法是**给一个区间，不是一个自信的单值**。

## 第 2 步：如果很大，先问

当估算上界超过 `--max-minutes`（默认 10）且没有批准时，autoindex **在写入任何东西之前**停下，输出 JSON 决策请求并以退出码 **4** 结束（F-044、F-048）：

```sh
xerj autoindex ~/my-project --approve proceed
xerj autoindex ~/my-project --approve fast      # 索引，但 --no-semantic --no-graph
xerj autoindex ~/my-project --approve cancel
```

回答时用 `--approve`，**不要重试**。也可以说「停掉是安全的」——续跑日志加幂等 `_id` 意味着中断的运行能恢复且永不重复。

> 决策请求里的 `fast` 选项**不会**声称一个加速倍数：它说明自己改变了什么范围（去掉服务端嵌入与客户端边检测），并承认倍数未测。这是唯一诚实的写法。

## 第 3 步：真正索引

```sh
xerj autoindex ~/my-project
```

你会看到两个进度行：

```
xerj-bar [######################--] 93.4% | index | 8082/8083 items | eta 7s
xerj-progress phase=index basis=bytes pct=93.4 items=8082/8083 eta_s=7.2 …
```

- `xerj-bar` 是**给人看的**，转述给用户时逐字展示，最多每 15 秒一条；
- `xerj-progress` 是**给机器看的**，按 `--progress-interval`（默认 5 秒）节奏输出，解析它。

一个重要细节：在 `--no-graph` 路径上，阶段序列是
`walk, hash, scan, prepare, snapshot, index, finalize-catalog, finalize-refresh, finalize-verify`。
因此一行仍显示 `scan 100%` 意味着**还在扫描**，绝不是已经在索引（F-042）。

结束时看终行：

```
done in 158.1s, 593 datasets, 83103 records live, 790 junk records
```

以及摘要行：

```
indexed: 83103 documents live; this run submitted 83103 source records from 25329 files
```

若语料已存在且本次没有新内容，摘要行会追加 `(already indexed; nothing new to send)`（F-052）。

## 第 4 步：摸清数据

```sh
xerj autoindex map
xerj autoindex map --json      # 机器可读
```

它给你一份**简报**：每个数据集的计数、每字段的类型与**真实示例值**、可开箱即用的查询，以及引擎记录下来的坑。也可以直接查目录索引：

```sh
curl -s localhost:9200/autoindex-catalog/_search | jq '.hits.hits[]._source'
```

MCP 侧的对应物是 `xerj_map` 工具（见 [03](/concepts/03-mcp-agent-surface.md)）。

> **为什么要看 map**：它给出的**真实字段名**是避免 400 的关键。XERJ 在 `ax-*` 索引上对未映射字段的严格模式会 400 并报出可检索字段（F-092）——但更好的做法是**先看 map 再写查询**。

## 第 5 步：查询（带裁剪）

```sh
# 全量（不推荐用于源码语料）
curl "localhost:9200/ax-*/_search?q=checkout+error"

# 推荐：只要匹配片段 + 投影 _source
curl -s localhost:9200/ax-code/_search \
  -H 'content-type: application/json' \
  -d '{
    "fields": ["_passage"],
    "_source": ["title", "ax_path"],
    "query": { "match": { "body": "rotate WAL segment" } },
    "size": 5
  }'
```

为什么这么写：默认 `_search` 返回**完整文档**，源码类语料下 5 个命中就是 416,630 字节；加上 `_passage` 并投影 `_source` 后是 12,122 字节——**34 倍**缩减（F-087）。

`_passage` 是 opt-in 的，不出现在任何 `_mapping` 里；如果你忘了加，响应会在 `_xerj.hints` 里**直接给你改好的请求**（F-089）。

## 第 6 步：结构化查询与聚合

```sh
curl localhost:9200/ax-orders/_search -H 'content-type: application/json' -d '{
  "query": { "range": { "total": { "gte": 100 } } },
  "aggs":  { "by_status": { "terms": { "field": "status" } } }
}'
```

`size:0` 的聚合走**列式快速路径**（F-081）——这正是智能体最常问的问题类型（计数、基数、直方图、百分位）。

## 第 7 步：把产出交回智能体

```sh
xerj init          # 注册 .mcp.json + 写 10 行 skill
```

之后智能体就能用 `xerj_search` / `xerj_map` / `xerj_code_search` 等工具直接查这个索引。

## 复盘清单

| 现象 | 原因 | 处理 |
|---|---|---|
| 退出码 3 | 完成但含 junk——**这是成功** | 读 `reason` 与 `datasets_refused`/`files_refused` |
| 退出码 4 | 需要决策 | `--approve proceed\|fast\|cancel`，不要重试 |
| 退出码 1 + `the server kept rejecting` | 节点 600 秒持续背压 | 重跑同一命令续跑 |
| 查询 400 报字段名 | `ax-*` 索引的严格未知字段模式 | 查 `autoindex map` 拿真实字段名 |
| 查询 400 报 `fusion learned` | 未实现的融合方式 | 改 `rrf` 或 `linear` |
| 响应巨大 | 没裁剪 | 加 `fields: ["_passage"]` + 投影 `_source` |
| `semantic` 查询 400 | 索引没把字段映射为 `semantic_text` | 查 mapping；混合查询会让整个请求失败 |

## 相关概念

- [02 autoindex 零配置流水线](/concepts/02-autoindex-pipeline.md)：每一步的机制细节
- [04 检索路径与响应裁剪](/concepts/04-search-query-path.md)：`_passage`、`_xerj.hints`、严格字段
- [01 安装与快速上手](/concepts/01-getting-started.md)：节点启动与认证
- [Examples 索引](index.md)：全部示例
