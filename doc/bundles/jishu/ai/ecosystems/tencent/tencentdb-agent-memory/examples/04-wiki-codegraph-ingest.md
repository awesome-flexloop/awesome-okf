---
type: Example
title: "CodeGraph 与 Wiki 摄取：从创建、轮询 ready 到 MCP 只读查询"
description: "把公开 HTTPS 仓库与 Wiki 文档导入 MemoryKnowledge，按 pending→processing→ready/failed 状态机轮询，再用 12 个 MCP 只读工具查询，并配置自动同步。"
tags: [tencentdb-agent-memory, example, codegraph, wiki, knowledge, mcp]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-deploy
    resource: /references/04-deploy-install.md
    title: 安装与部署信源
  - id: s-know-doc
    resource: /references/03-api-references.md
    title: v3 API 三卷与 OpenAPI 信源
---

# CodeGraph 与 Wiki 摄取到可查

> 本示例基于 commit 8b86874 截面的文档与源码整理，未在真实环境运行验证；命令中的 env/端点均带（F-xxx）溯源，落地前请先实测。

## 1. 前置条件与约束

1. CodeGraph 当前仅支持公开 HTTPS 仓库，私库或非 HTTPS 地址不在支持范围（F-049）。
2. Wiki/CodeGraph 均为异步构建，创建后必须等待 `ready` 才能查询，不能假设导入即可搜（F-049/F-199）。
3. Knowledge 宿主默认端口 8424（容器内监听 8421），部署侧默认基址 `http://host.docker.internal:8424/v3`（F-023/F-272/F-215）。
4. 鉴权使用 service key（请求头 `x-tdai-service-id`）；只读白名单免 service key，Bearer 仍需（F-193）。`KNOWLEDGE_SERVICE_KEY` 留空时自动生成 `ks-svc-*`（F-276）。
5. 构建依赖 LLM 通路：llm-binding 模式为 `proxy` 或 `byo`，proxy 模式生成 `/proxy/{service_id}/v1` 形态 URL；通过 `POST /v3/internal/llm-binding/set|status|list` 配置，status/list 不返回明文 key、只回 `has_api_key` 布尔（F-208/F-209）。

## 2. 创建 CodeGraph：POST /v3/code-graph/create

```bash
# 本块均为示例自定义 shell 变量，不是系统配置项
KNOW="http://127.0.0.1:8424/v3"
BEARER="<bearer-token>"
SERVICE_KEY="<ks-svc-* 或 .env 中配置的值>"   # F-276
SERVICE_ID="<your-service-id>"
TEAM_ID="<your-team-id>"
```

```curl
curl -sS -X POST "$KNOW/code-graph/create" \
  -H "Authorization: Bearer $BEARER" \
  -H "x-tdai-service-id: $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": "'"$SERVICE_ID"'",
    "team_id": "'"$TEAM_ID"'",
    "repo_url": "https://github.com/<owner>/<repo>.git",
    "branch": "main"
  }'
```

幂等键为 `(service_id, team_id, repo_url, branch)`：同一四元组重复提交不会重建（F-198）。记录字段含 `repo_url`、`branch`、`status`、`internal_status`、`sync_error`、`stats_json`（F-196）。创建后默认状态为 `pending`（F-197）。

## 3. 轮询构建状态

状态机为 `pending → processing → ready/failed`（F-197/F-199）。轮询手段用 MCP 只读工具 `code_status`（工具清单见第 5 节，F-202）；HTTP 侧 Code-Graph 查询分组（list/get 等）见 references/03 卷二目录。

| 轮询返回 | 含义（依据） | 处理 |
|----------|---------------|------|
| `pending` / `processing` | 排队或构建中（F-197） | 继续等待轮询，勿发起查询（F-049） |
| `ready` | 构建完成（F-197/F-199） | 可进入第 5 节查询 |
| `failed` | 构建失败（F-197） | 读记录中的 `sync_error` 排障（F-196）；全程有审计与 TMC callback（F-199） |
| busy 独立返回 | 已有构建在飞（F-199） | 不要重复触发，等待当前构建结束 |
| not_found 独立返回 | 资源不存在（F-199） | 核对四元组与 service-id 后重新 create |

## 4. Wiki：create（默认 draft）→ ingest

```curl
curl -sS -X POST "$KNOW/wiki/create" \
  -H "Authorization: Bearer $BEARER" \
  -H "x-tdai-service-id: $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": "'"$SERVICE_ID"'",
    "team_id": "'"$TEAM_ID"'",
    "name": "<wiki-name>"
  }'
```

Wiki 幂等键为 `(service_id, team_id, name)`（F-198）；Wiki 状态在 pending/processing/ready/failed 之外额外含 `draft`，创建后默认 `draft`（F-197）。随后触发摄取（`ingest` 为卷二 Wiki 分组 16 个端点之一，见 references/03）：

```curl
curl -sS -X POST "$KNOW/wiki/ingest" \
  -H "Authorization: Bearer $BEARER" \
  -H "x-tdai-service-id: $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @wiki.ingest.json
```

`wiki.ingest.json` 的字段契约以随仓卷二文档与 `openapi.yaml` 为准（F-216）。摄取同样按状态机走到 `ready`；每个 Wiki 有独立 SQLite 索引库（含 BM25 虚表与 wikilink 图谱边）（F-204/F-206）。

## 5. 查询：MCP 的 12 个只读工具

构建 `ready` 后，经 knowledge-mcp（bin 见 F-191）调用只读工具；管理操作不暴露给 MCP（F-202）。

| 分组 | 工具名 |
|------|--------|
| Code（8 个） | `code_search`、`code_explore`、`code_callers`、`code_callees`、`code_impact`、`code_node`、`code_status`、`code_files` |
| Wiki（4 个） | `wiki_search`、`wiki_read`、`wiki_list`、`wiki_graph` |

工具调用参数未在事实清单登记，本示例不列参数名；参数契约以 `openapi.yaml` 与 `/docs`（Swagger UI）为准（F-216）。服务端在 `/v3` 下挂载 wiki、code-graph、tools、internal、llm-binding、auto-sync、analytics 路由，并暴露 `/openapi.json`（F-193）。

## 6. 自动同步 auto-sync

自动同步由三个环境变量控制（F-200）：

| 环境变量 | 作用（F-200） |
|----------|----------------|
| `KNOWLEDGE_AUTO_SYNC_ENABLED` | 开关 |
| `SCAN_INTERVAL_MIN` | 扫描间隔（分钟） |
| `MAX_CONCURRENT` | 最大并发 |

调度器仅扫描 `status=ready` 的 CodeGraph，inFlight 去重、FIFO 排队（F-200）。手动触发与查状态（F-201）：

```curl
curl -sS -X POST "$KNOW/auto-sync/trigger" \
  -H "Authorization: Bearer $BEARER" \
  -H "x-tdai-service-id: $SERVICE_KEY"
```

```curl
curl -sS "$KNOW/auto-sync/status" \
  -H "Authorization: Bearer $BEARER" \
  -H "x-tdai-service-id: $SERVICE_KEY"
```

## 7. 失败处置

| 现象 | 依据 | 处置 |
|------|------|------|
| create 被拒：仓库地址不合法 | 仅支持公开 HTTPS 仓库（F-049） | 换公开 HTTPS 地址；私库无入口 |
| 重复 create 返回同一资源 | 四元组幂等（F-198） | 属预期；直接轮询既有资源 |
| 长时间停在 processing | 异步构建需等 ready（F-049/F-199） | 继续轮询；busy 表示已有构建在飞（F-199） |
| status=failed | F-197/F-199 | 读 `sync_error`（F-196），修好后重新触发 |
| 查询返回 not_found | 资源不存在（F-199） | 核对 `(service_id, team_id, repo_url, branch)` |
| ready 前查询无结果 | 未 ready 不可查（F-049） | 等状态机完成后再调用 MCP 工具 |
| 构建报 LLM 相关错误 | llm-binding 未配置（F-208/F-209） | 用 `/v3/internal/llm-binding/set` 配 proxy/byo，再查 status |
| MCP 调不到创建/删除类操作 | 管理操作不暴露给 MCP（F-202） | 改走 `/v3` HTTP 端点并带 service key |

## 相关概念

- [MemoryKnowledge：知识引擎](../concepts/08-memory-knowledge.md)
- [Skill 记忆资产](../concepts/05-skill-memory.md)
- 信源：[v3 API 三卷与 OpenAPI 信源](../references/03-api-references.md)、[安装与部署信源](../references/04-deploy-install.md)
