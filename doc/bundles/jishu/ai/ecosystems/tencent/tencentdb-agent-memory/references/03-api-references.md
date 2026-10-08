---
type: Reference
title: "v3 API 三卷与 OpenAPI 信源"
description: "MemoryCore/MemoryKnowledge/MemoryProxy 随仓 v3 接口文档的结构登记：公共约定（信封/鉴权/分页/错误码）、端点分组计数、MCP 工具面与 openapi.yaml。"
tags: [tencentdb-agent-memory, reference, api, v3, openapi, mcp]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-core-api
    resource: MemoryCore/v3-api-memorycore-doc.md
    title: v3 接口文档 · 卷一 MemoryCore
  - id: s-know-doc
    resource: MemoryKnowledge/v3-api-memoryknowledge-doc.md、openapi.yaml
    title: v3 接口文档 · 卷二 MemoryKnowledge + OpenAPI
  - id: s-proxy-doc
    resource: MemoryProxy/v3-api-memoryproxy-doc.md
    title: MemoryProxy v3 管理接口文档
---

# v3 API 三卷信源

## 信源元信息

| 项目 | 内容 |
|------|------|
| 文件 | MemoryCore/v3-api-memorycore-doc.md、MemoryKnowledge/v3-api-memoryknowledge-doc.md、MemoryProxy/v3-api-memoryproxy-doc.md、MemoryKnowledge/openapi.yaml |
| 采集日期 | 2026-10-04（commit 8b86874） |
| 对应事实 | F-093、F-128、F-151~F-163、F-193~F-216、F-221~F-234 |

## 卷一 MemoryCore：公共约定

- 服务端口 8420（F-163）；统一响应信封 `{code, message, request_id, data}`（F-151）。
- 鉴权分层：Bearer + `x-tdai-service-id`；v3 数据面强制 team_id/agent_id/user_id 三元组（F-153/F-156）。
- 文档含统一分页约定、数据面错误码语义与三类错误 message 格式章节。
- 附录登记 v1/v2 废弃接口（/capture、/recall、/search/* 为兼容面，F-056）。

## 卷一：端点目录（按文档章节计数）

| 章节 | 端点数 | 代表端点 |
|------|--------|---------|
| 3.1 L0–L3 数据面 | 18 | conversation 5（add/query/search/delete/count）、atomic 5（update/query/search/delete/count）、scenario 5（ls/read/write/rm/count）、core 3（read/write/count） |
| 3.2 Skill | 17 | 与 skill-handlers.ts:1155-1171 路由表一一对应（F-145） |
| 3.3 Knowledge 代理 | 5 | create/get/update/delete/list |
| 3.4 Chat-Memory | 1 | /v3/chat-memory/clear |
| 3.5 Memory-Prompt | 7 | create/get/update/delete/set/setting/list/log |
| 3.6 Generation-Log | 2 | list/get（F-093） |
| 3.7 Meta 元数据 | 55 | User 5、User-Key 5、Team 5、Team-Member 4、Agent 6、Task 6、Task-Agent 3、Participation-Log 2、Asset 7、Agent-Fixed-Asset 4、ACL 4、Auth 1（/v3/meta/auth/verify）、Instance-Quota & Config 3 |
| 3.8 Internal Meta | 2 | init-admin、list-by-instance（F-160） |
| 3.9 Instance Destroy | 1 | /v3/instance/destroy |

数据面 18 与路由层 V3_ALLOWED_SUBPATHS 集合实际成员一致（v2-router.ts:153-172：conversation5/atomic5/scenario5/core3，逐条计数 18；F-154）。注意 v2-router.ts:520 源码注释自述「数据面 14 条」系过期注释，与集合实际内容不符，复核以集合成员为准，勿引用 14 这个数字。

## 卷二 MemoryKnowledge：公共约定

- 除 `GET /v3/auto-sync/status` 与 `GET /health` 外其余接口全部 POST；健康检查返回裸 JSON `{status, timestamp}`；Swagger UI 在 /docs、spec 在 /openapi.json。
- 鉴权用 service key（x-tdai-service-id）；例外：`POST /v3/internal/llm-binding/list` 不要求该头（供 Panel 启动缓存，Bearer 仍需）。
- 资源状态枚举 pending/processing/ready/failed（wiki 另有 draft）（F-197）。

## 卷二：端点目录

| 章节 | 数量 | 要点 |
|------|------|------|
| Wiki | 16 | create/list/get/update-meta/delete/ingest、raw 4（ls/read/write/rm）、page 4（ls/read/write/rm）、graph、search |
| Code-Graph | 14 | create/list/get/update-meta/sync/delete + 8 个 id-only 查询工具（search/explore/callers/callees/impact/node/status/files，kind 枚举含 function/method/class/interface/type/variable/route/component） |
| Tools 自发现 | 2 | /v3/tools/list、/v3/tools/call（F-128 同类机制） |
| Internal LLM-Binding | 3 | set/status/list，status/list 不回明文 key（F-209） |
| Auto-Sync | 2 | POST trigger + GET status（F-201） |

MCP 面另暴露 12 个只读工具（8 code + 4 wiki），管理操作不进 MCP（F-202）。openapi.yaml 随仓提供，可直接驱动客户端生成。

## MemoryProxy 管理接口（6 个）

| 端点 | 方法 | 用途 |
|------|------|------|
| /v3/instance/proxy-destroy | POST | 实例销毁（F-029） |
| /v3/admin/rate-limits | GET/PUT/DELETE | 频控规则管理（F-229/F-230） |
| /v3/session/refresh-cache | POST | 刷新会话缓存 |
| /v3/session/force-archive-skill | POST | 强制归档会话技能 |

代理业务路由：/health、/whoami、/direct/*、/skill-bridge/*、/memory-bridge/*（白名单 6 个只读子路径，F-221/F-222）；对话面为 /v1/chat/completions 与 /v1/messages（F-219）。

## 引用纪律

- 端点数量以随仓文档章节计数为准，并已与源码路由表交叉核对（skill 17 两处一致；数据面 18 两处一致）。
- v1/v2 兼容接口不在三卷正文，引用 /capture、/recall 时须标注「兼容面」。
