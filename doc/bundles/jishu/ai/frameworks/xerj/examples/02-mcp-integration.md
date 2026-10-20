---
type: Example
title: 把智能体接到 XERJ 上
description: MCP 客户端接入实操——配置块、认证的三层优先级、绝对路径陷阱、token 预算参数，以及无 shell 时的 HTTP 等价路径
tags: [xerj, 示例, mcp, 智能体接入]
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

# 把智能体接到 XERJ 上

XERJ 的 MCP 服务器**就是那个已安装的二进制**——`xerj mcp` 子命令，没有第二个东西要下载或编译。

## 三步接入

```sh
# 1. 起一个节点（MCP 服务器不会自己起节点）
xerj --insecure --data-dir ~/.xerj-data &

# 2. 在项目里注册 MCP + 写 skill
xerj init

# 3.（可选）索引点数据
xerj autoindex ~/my-project
```

`xerj init` 做两件事（F-165）：把 MCP server 注册进 `.mcp.json`；为 Claude Code / Cursor 写一份 10 行 skill。对它编辑的每个文件都留 `.bak` 备份。

## MCP 配置块

```json
{
  "mcpServers": {
    "xerj": {
      "command": "/home/you/.local/bin/xerj",
      "args": ["mcp"],
      "env": { "XERJ_URL": "http://localhost:9200" }
    }
  }
}
```

### 三个必踩的坑

**一、`command` 必须是绝对路径。** 从桌面图标启动的 MCP 宿主不继承你的 shell `PATH`，裸 `"xerj"` 在那里会以没有有用错误的方式失败。用 `command -v xerj` 确认路径。

**二、认证默认开启。** 节点不是 `--insecure` 启动时，有两种处理：

```json
{
  "command": "/home/you/.local/bin/xerj",
  "args": ["mcp"],
  "env": {
    "XERJ_URL": "http://localhost:9200",
    "XERJ_AUTH": "ApiKey <key>"
  }
}
```

`XERJ_AUTH` 的值是**完整的头部值**（`ApiKey <token>`），不是裸 token。密钥在 `<data_dir>/admin.key`。

**三、回环回退会救你一命（也可能让你困惑）。** 对 `localhost` / `127.0.0.1` / `[::1]`，若既没给 `--auth` 也没给 `XERJ_AUTH`，服务器会**自己去读本地 `admin.key`**，并在 stderr 公布它用的是哪个文件（F-065、F-072）：

```
xerj-mcp: no --auth/XERJ_AUTH given; using the admin key at /home/you/.xerj-data/admin.key
```

这个回退**只对回环地址生效**（F-066）——本地可读的密钥发往另一台主机是凭据泄露，不是便利。

> 为什么有这个回退？`xerj init` **有意**不把凭据写进 `.mcp.json`：那份文件是项目作用域、通常会被提交进版本库。没有这层回退，官方的一键设置会对每次工具调用都 401（F-067）。

## 认证优先级

```
--auth  >  XERJ_AUTH  >  （仅回环时）本地 admin.key 发现
```

一个细节：**空的 `XERJ_AUTH` 视为未设置**。已提交进 `.mcp.json` 的空值不应遮蔽发现逻辑并变成一个空的 `Authorization: ` 头。

命令行等价：

```sh
xerj mcp --url http://localhost:9200 --auth "ApiKey <key>"
```

## 工具怎么用

### 一次普通的词法搜索

```json
{
  "tool": "xerj_search",
  "arguments": {
    "index": "ax-code",
    "query": { "match": { "body": "rotate WAL segment" } },
    "max_tokens": 2000
  }
}
```

`xerj_search` 接受标准 ES 查询 DSL 正文（`match`、`match_phrase`、`term`、`terms`、`range`、`bool`、`prefix`、`wildcard`、`exists`、`ids`、`fuzzy`、`query_string`），并支持 `aggs`、`sort`、`from`/`size`、`_source`、`highlight`（F-078 相关）。

### `max_tokens` 是硬预算

五个检索工具（`xerj_search`、`xerj_semantic_search`、`xerj_vector_search`、`xerj_hybrid_search`、`xerj_code_search`）接受 `max_tokens` 并被**强制执行**：响应文本**绝不**超过预算（F-069）。

执行方式：用 XERJ 自己的 `StandardTokenizer`（UAX #29）计数；重叠的 file:line 段落**先去重再计预算**；超预算的命中**降级为定位符**（只有 file:line，没有正文）。

> 多数 MCP 检索工具把 `max_tokens` 当提示词（"尽量别超"），这里它是不变量（"绝不超"）。在上下文预算即成本的宿主里，只有后者有意义。

### 语义搜索——先确认嵌入模式

```json
{
  "tool": "xerj_semantic_search",
  "arguments": {
    "index": "ax-docs",
    "query": { "semantic": { "field": "body", "query": "how do I rotate keys", "k": 10 } }
  }
}
```

> **工具名写着 semantic，但默认嵌入器是词法**（F-113、F-115）。节点不是以 `--embed-mode neural` 启动时，这个查询等于「词/子词重叠 + BM25」。**在向用户承诺「按意义搜」之前，先确认嵌入模式。**

### 向量搜索

```json
{
  "tool": "xerj_vector_search",
  "arguments": {
    "index": "ax-docs",
    "query": {
      "knn": {
        "field": "embedding",
        "query_vector": [/* 你自己算的向量 */],
        "k": 10,
        "num_candidates": 100
      }
    }
  }
}
```

查询向量要**自己带**。未过滤且文档数 ≥ 1,024 时走 HNSW + 精确重打分；过滤形态走精确扫描（F-123、F-125）。

### 混合

```json
{
  "tool": "xerj_hybrid_search",
  "arguments": {
    "index": "ax-docs",
    "query": {
      "hybrid": {
        "queries": [
          { "query": { "match": { "body": "rotate keys" } }, "weight": 1.0 },
          { "query": { "semantic": { "field": "body", "query": "how do I rotate keys", "k": 10 } }, "weight": 1.0 }
        ],
        "fusion": "rrf"
      }
    }
  }
}
```

`fusion` 只有 `rrf`（默认）与 `linear`（F-094）。`"learned"` 会被引擎以 400 明确拒绝。

### 看数据里有什么

```json
{ "tool": "xerj_map", "arguments": { "index": "ax-orders" } }
```

返回 autoindex 目录里的按索引字段图，按字节上限裁剪，其余逐字返回。

### 记一笔

```json
{
  "tool": "xerj_memory_store",
  "arguments": {
    "namespace": "project-notes",
    "text": "用户偏好暗色主题",
    "metadata": { "topic": "ui" }
  }
}
```

### 规划一个查询

```json
{
  "tool": "xerj_plan",
  "arguments": { "index": "ax-orders", "prompt": "2026 年金额超过 100 的订单" }
}
```

返回 `{query, plan[], confidence, indices[]}`。**确定性规则引擎，不是 LLM**；无法落地的短语返回 422 并指名该短语（F-131）。

## 没有 shell 的智能体：纯 HTTP 路径

除 `autoindex`（**CLI 独有**，没有 HTTP 等价物，F-166）外，所有核心能力都有 HTTP 端点：

```sh
curl -s localhost:9200/ax-*/_search -H 'content-type: application/json' \
  -d '{"query":{"match":{"body":"BuiltinPager"}}}'

curl -s localhost:9200/_memory/project-notes/_recall \
  -H 'content-type: application/json' \
  -d '{"query":"什么 UI 主题","semantic":true,"k":5}'

curl -s localhost:9200/_ask -H 'content-type: application/json' \
  -d '{"index":"ax-orders","prompt":"2026 年金额超过 100 的订单"}'
```

这正是「薄代理」设计的收益：MCP 能做的，curl 都能做（F-060、F-061）。

## 故障速查

| 症状 | 原因 | 处理 |
|---|---|---|
| `command not found`（MCP 宿主里） | `command` 用了裸名 | 写绝对路径 |
| 每次工具调用 401 | 节点开认证但没传凭据 | 加 `XERJ_AUTH`，或依赖回环回退 |
| `XERJ_AUTH` 用了裸 token | 该变量要完整头部值 | 改成 `ApiKey <token>` |
| stdout 出现非 JSON-RPC 文本 | 有人在 stdout 打印了东西 | 诊断必须走 stderr |
| 语义搜索结果像关键词匹配 | 默认嵌入器是词法 | 节点以 `--embed-mode neural` 启动并**重新索引** |
| 混合查询 400 | 有索引没映射 `semantic_text` | 查 mapping，把语义臂只指向有能力的索引 |

## 相关概念

- [03 MCP 智能体接口](/concepts/03-mcp-agent-surface.md)：17 工具全表与工具描述里的诚实声明
- [05 向量、嵌入与混合检索](/concepts/05-vector-and-hybrid.md)：嵌入模式与扫描路径
- [06 智能体记忆与第二大脑](/concepts/06-agent-memory-and-brain.md)：记忆与 brain 工具
- [01 安装与快速上手](/concepts/01-getting-started.md)：节点启动与认证
- [Examples 索引](index.md)：全部示例
