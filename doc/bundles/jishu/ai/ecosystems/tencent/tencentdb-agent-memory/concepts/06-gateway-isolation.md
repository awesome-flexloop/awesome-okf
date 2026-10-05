---
type: Concept
title: "网关与隔离契约：统一信封、v3 三元组与受控子路径"
description: "MemoryCore 网关以统一响应信封、Zod v4 校验、team/agent/user 强制三元组与 18 个受控子路径，把多租户隔离写进 API 契约。"
tags: [tencentdb-agent-memory, concept, gateway, isolation, v3-api, memorycore, multi-tenant]
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
---

# 网关与隔离契约：统一信封、v3 三元组与受控子路径

> **本篇看点**
>
> - 所有响应走 `{code, message, request_id, data}` 信封，请求体经 Zod v4 校验，失败即 400（F-151、F-152）。
> - v3 强制 team_id + agent_id + user_id 三元组，缺失返回 422，可走三组请求头（F-153）。
> - v3 记忆面只开放 18 个受控子路径，按 5+5+5+3 分组（F-154）。
> - 鉴权用 Bearer + `x-tdai-service-id`，并区分 standalone/service 两种部署模式（F-155、F-156）。

## 1. 统一响应信封与 400 校验

v2-router 的统一响应信封为 `{code, message, request_id, data}`（F-151）。请求体使用 Zod v4 的 safeParse 校验，校验失败返回 400（F-152）。

## 2. v3 强制三元组与请求头

v3 接口的 `collectV3Missing` 强制要求 team_id + agent_id + user_id 三项，缺失任一即返回 422；三项既可以放在 body，也可由 `x-tdai-team-id`、`x-tdai-agent-id`、`x-tdai-user-id` 三组请求头提供；session_id 为可选项（F-153）。

```text
请求进入 → 收集 team_id / agent_id / user_id
  来源：body 或 x-tdai-team-id / x-tdai-agent-id / x-tdai-user-id
  缺失：422
  session_id：可选（F-153）
```

## 3. 18 个受控子路径（5+5+5+3）

`V3_ALLOWED_SUBPATHS` 共 18 个子路径，按四组前缀分配（F-154）：

| 前缀组 | 子路径数 |
|---|---|
| conversation | 5 |
| atomic | 5 |
| scenario | 5 |
| core | 3 |

## 4. 部署模式与鉴权

部署模式 `deployMode` 取值 standalone / service；文件存储模式 `FILE_STORE_MODE` 在 service 模式为 cos、standalone 模式为 local（F-155）。鉴权采用 Bearer 令牌加 `x-tdai-service-id` 头；`/health` 与 CORS 预检豁免鉴权，CORS 使用白名单（F-156）。`/v3/skill/*` 路径在鉴权豁免判断中被单独列出处理（F-157）。

```text
请求生命周期
  CORS 预检 / /health → 豁免（F-156）
  其他请求 → Bearer + x-tdai-service-id 鉴权（F-156）
         → Zod v4 safeParse 校验 body，失败 400（F-152）
         → v3 收集三元组，缺失 422（F-153）
         → 子路径必须命中 18 个白名单（F-154）
         → 响应统一信封 {code, message, request_id, data}（F-151）
```

## 5. per-instance 路由与 v3 API 总面

server.ts 同时承载 `/v2` 记忆接口与 `/v3/skill/conversation/add` 的 per-instance 路由（F-158）。v3 API 总面包含六组路由（F-159）：

| API 面 |
|---|
| `/v3/skill/*` |
| `/v3/meta/*` |
| `/v3/knowledge/*` |
| `/v3/memory-prompt/*` |
| `/v3/memory-generation-log/*` |
| `/v3/tools/*` |

元数据面两个关键端点（F-160）：

| 端点 | 用途（F-160） |
|---|---|
| `/v3/meta/auth/verify` | 鉴权校验，部署脚本启动自检调用 |
| `/v3/internal/meta/user/init-admin` | 初始化管理员，由部署脚本调用 |

v2 与 v3 在同一进程共存：server.ts 同时承载 `/v2` 记忆接口与 `/v3/skill/conversation/add` 的 per-instance 路由（F-158）。

## 6. 其他 handler 与监听配置

- `knowledge-handlers.ts` 代理 Core 对 Knowledge 的调用；`analytics/index.ts` 提供 ClickHouse 查询接口（F-161）。
- `error-handler.ts` 统一错误处理（F-162）。
- 网关配置文件 `tdai-gateway.yaml` 声明监听 8420（F-163）。

## 7. 容器形态：8420、tini 与 healthcheck

Dockerfile 运行时基础镜像为 node:22-slim，`EXPOSE 8420`，定义 healthcheck，ENTRYPOINT 为 tini，CMD 启动 gateway（F-164）。生产部署要求 STORE_MODE 等环境变量经容器注入，配置文件只读挂载（F-165）。

## 8. 关键环境变量

| 变量 / 事项 | 口径 |
|---|---|
| 管理员用户名 | 默认 admin（F-166） |
| 管理员 key | 随机生成 `sk-mem-*` key，写入 `${MEMORY_CORE_ADMIN_KEY_FILE}`，经 init-admin 与 auth/verify 双接口校验（F-166） |
| `MEMORY_CORE_GATEWAY_API_KEY` | 留空等于关闭 Bearer 鉴权，用于本地零配置（F-167） |
| `MEMORY_CORE_STORE_MODE` | sqlite（默认）/ mongodb（试验，需 Mongo 7.0+ mongot，不静默降级）（F-168） |
| `MEMORY_CORE_METADATA_BACKEND` | auto / sqlite（F-168） |
| `MEMORY_PROMPT_MODE` | code（默认）/ chat（F-169） |
| `MEMORY_LLM_*` | core/hub 内部使用的 LLM 配置，含 `MEMORY_LLM_PROTOCOL=openai|anthropic`（F-170） |
| `PROXY_UPSTREAM_*` | 代理上游 LLM 配置，与 `MEMORY_LLM_*` 分离（F-170） |

## 9. 文档与验证脚本

v3 接口权威文档为随仓的 `v3-api-memorycore-doc.md`（F-171）。观测与端到端脚本包括 `e2e-memory-prompt-vdb-cos.ts`、`start-e2e-gateway.ts` 以及 `bench-l0-mongo/` 性能基准等 7 个文件（F-172）。

## 10. 设计解读：隔离写进契约与存储格式

按洞察五的解读，v3 三元组不是查询时临时拼装的过滤条件，而是 API 契约的一部分：缺失即 422（F-153），受控子路径只有 18 个（F-154），配合 Bearer 与 service-id 的实例维度（F-156），隔离从入口处就无法被绕过。standalone 与 service 两种模式共享同一套契约，仅文件存储模式与后端选择随部署形态切换（F-155），本地零配置（API key 留空）与多实例 service 模式因此可以复用同一网关代码（F-146、F-167）。

## 延伸阅读

- [05 Skill 记忆](05-skill-memory.md)
- [07 offload 卸载与上下文压缩](07-offload-context.md)
- [实战 01：一键启动与验证](../examples/01-quickstart.md)
