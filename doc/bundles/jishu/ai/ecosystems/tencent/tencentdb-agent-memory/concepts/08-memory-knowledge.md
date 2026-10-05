---
type: Concept
title: "MemoryKnowledge 知识引擎：双 bin、异步构建状态机与 12 个只读 MCP 工具"
description: "MemoryKnowledge 在 8421 端口以 Hono 提供 Wiki/CodeGraph 的异步构建、每库独立 index.db、12 个只读 MCP 工具与 proxy/byo 两种 LLM 绑定模式。"
tags: [tencentdb-agent-memory, concept, memoryknowledge, wiki, codegraph, mcp, state-machine]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-core-code
    resource: /references/01-source-code-map.md
    title: TencentDB-Agent-Memory 源码地图
  - id: s-core-api
    resource: /references/03-api-references.md
    title: v3 API 三卷信源
  - id: s-know-doc
    resource: /references/03-api-references.md
    title: MemoryKnowledge v3 API 与 OpenAPI
---

# MemoryKnowledge 知识引擎：双 bin、异步构建状态机与 12 个只读 MCP 工具

> **本篇看点**
>
> - 两个 bin：knowledge-server 与 knowledge-mcp；默认 8421、`./data/knowledge.db`、LLM 默认经 proxy/openai（F-191、F-192）。
> - Wiki/CodeGraph 走 pending→processing→ready/failed 异步状态机，消费端必须等 ready（F-197、F-199）。
> - MCP 只暴露 12 个只读工具，管理操作不进 MCP（F-202）。
> - 每个 Wiki 独立 index.db，含 FTS 虚表、页面元数据、图谱边与来源四表（F-204）。

## 1. 双 bin 与默认配置

package.json 声明两个 bin：knowledge-server（bin/server.mjs）与 knowledge-mcp（bin/mcp.mjs）（F-191）。config 默认端口 8421，SQLite DB 路径为 `./data/knowledge.db`，LLM 默认经 proxy/openai（F-192）。

## 2. Hono 路由面与只读白名单

server.ts 基于 Hono，在 `/v3` 下挂载七组路由并暴露 OpenAPI 与文档；只读白名单免 service key（F-193）：

| 挂载点 / 路径 | 用途（F-193） |
|---|---|
| wiki | Wiki 管理 |
| code-graph | 代码图谱管理 |
| tools | 工具 |
| internal | 内部端点 |
| llm-binding | LLM 绑定 |
| auto-sync | 自动同步 |
| analytics | 分析 |
| `/openapi.json`、`/docs` | OpenAPI 与文档 |

## 3. 存储：WAL 与 5 张表

SQLite 经 better-sqlite3 以 WAL 模式加 busy timeout 打开（F-194）。DDL 共 5 张表（F-195）：`knowledge_code_graph`、`knowledge_wiki`、`knowledge_wiki_audit`、`knowledge_code_graph_audit`、`llm_binding`。

主要字段（F-196）：

| 表 | 字段（F-196） |
|---|---|
| code_graph | code_graph_id、repo_url、branch、status、internal_status、sync_error、stats_json |
| wiki | wiki_id、source_type、source_url、status、internal_status、page_count、service_url、summary |
| llm_binding | mode、proxy_base_url、api_key、base_url、enabled |

## 4. 状态枚举、幂等键与构建状态机

状态枚举 `SyncStatus = pending | processing | ready | failed`；WikiStatus 额外含 draft。codegraph 创建默认 pending，wiki 创建默认 draft（F-197）。两组幂等键分别为：codegraph 按 (service_id, team_id, repo_url, branch) 查重，wiki 按 (service_id, team_id, name) 查重（F-198）。

```text
构建状态机
  pending → processing → ready
                       ↘ failed
  busy / not_found 有独立返回
  全程：写审计表 → 通过 TMC callback 回调（F-199）
```

## 5. auto-sync：三变量、只扫 ready、FIFO

自动同步由 `KNOWLEDGE_AUTO_SYNC_ENABLED`、`SCAN_INTERVAL_MIN`、`MAX_CONCURRENT` 三个环境变量控制；仅扫描 status=ready 的 codegraph，用 inFlight 去重并按 FIFO 调度（F-200）。两个端点为 `GET /auto-sync/status` 与 `POST /auto-sync/trigger`（F-201）。

## 6. 12 个 MCP 只读工具

MCP 暴露 12 个只读工具，管理操作不进 MCP（F-202）：

| 侧 | 工具（F-202） |
|---|---|
| code（8 个） | code_search、code_explore、code_callers、code_callees、code_impact、code_node、code_status、code_files |
| wiki（4 个） | wiki_search、wiki_read、wiki_list、wiki_graph |

MCP 服务端在 `mcp/server.ts`，HTTP 客户端在 `mcp/http-client.ts`（F-203）。

## 7. Wiki 索引库 index.db

每个 Wiki 有独立 SQLite 索引库 index.db，含四张表：`wiki_fts`（BM25 虚表）、`page_meta`、`graph_edge`、`source`（F-204）。索引写用独立连接，读用 LRU 连接池（F-205）。wikilink 正则为 `/\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]/g`；仅取 visible 页面，滤除 hidden、自环与不可解析目标，(source,target) 去重后写入 graph_edge（F-206）。

## 8. ingest-v2：14 个模块

Wiki ingest-v2 流水线含 14 个模块：chunker、cascade、prompts、llm、overview、merge、frontmatter、slug、safe-path、template、index-builder、log-writer、file-protocol、index（F-207）。

## 9. llm-binding：proxy / byo

llm-binding 模式为 proxy | byo；proxy 模式生成 `/proxy/{service_id}/v1` 形态的 URL（F-208）。三个 internal 端点为 `POST /v3/internal/llm-binding/set|status|list`，需带 x-tdai-service-id；status 与 list 不返回明文 key，只回 `has_api_key` 布尔（F-209）。

## 10. 代码引擎、遥测与中间件

- 代码引擎 `engines/code/` 含 bridge.ts、index.ts、normalize.ts；source-fetcher 含 git-fetcher 与注册表（F-210）。
- 遥测点击穿至 ClickHouse：clickhouse-telemetry、analytics-routes、telemetry（F-211）。
- 响应信封与错误处理中间件在 `middleware/response-envelope.ts`、`error-handler.ts`（F-212）。

## 11. 容器、入口与部署环境

- Dockerfile 设 `PORT=8421`、`EXPOSE 8421`，healthcheck 调用 `/health`，ENTRYPOINT 为 docker-entrypoint.sh（F-213）。
- entrypoint 要求 `--public-url`；LLM routing 支持 proxy/custom；映射 `KNOWLEDGE_PUBLIC_BASE_URL`、`LLM_API_KEY`、`LLM_BASE_URL`（F-214）。
- 部署侧 `KNOWLEDGE_PUBLIC_BASE_URL` 默认 `http://host.docker.internal:8424/v3`；`KNOWLEDGE_SERVICE_KEY` 留空自动生成 `ks-svc-*`（F-215）。
- `v3-api-memoryknowledge-doc.md` 与 `openapi.yaml` 随仓提供；仓库还含 drizzle.config.ts 与 docker-compose.yml（F-216）。

## 12. 设计解读：只读工具面 + 异步状态机

按洞察六的解读，Wiki/CodeGraph 不是灌进提示词的知识库，而是「随用随取的工具」：MCP 侧只有只读工具（F-202），构建必须走完状态机到 ready 才可查（F-199），自动同步只扫 ready 且 inFlight 去重以防重建风暴（F-200），每库独立 index.db 与可见性过滤保证工具只看见 visible 页面（F-204、F-206）。API key 只回布尔不回明文（F-209），则与只读白名单（F-193）一起构成工具面的最小暴露面。

## 延伸阅读

- [07 offload 卸载与上下文压缩](07-offload-context.md)
- [09 MemoryProxy LLM 代理](09-memory-proxy.md)
- [实战 04：Wiki/CodeGraph 导入与工具调用](../examples/04-wiki-codegraph-ingest.md)
