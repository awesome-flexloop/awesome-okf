---
type: Example
title: "用 v3 API 定制记忆 Prompt：create → set → 对话验证 → 查 SHA-256"
description: "在严格隔离三元组下用 TS SDK 构造客户端、用 curl 裸端点创建并激活自定义记忆 Prompt，再通过 generation-log 对拍哈希。"
tags: [tencentdb-agent-memory, example, memory-prompt, v3-api, typescript-sdk]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-deploy
    resource: /references/04-deploy-install.md
    title: 安装与部署信源
  - id: s-core-api
    resource: /references/03-api-references.md
    title: v3 API 三卷与 OpenAPI 信源
  - id: s-sdk-ts
    resource: /references/05-sdk-ci.md
    title: 官方 SDK 与工程配套信源
---

# 用 v3 API 定制记忆 Prompt

> 本示例基于 commit 8b86874 截面的文档与源码整理，未在真实环境运行验证；命令中的 env/端点均带（F-xxx）溯源，落地前请先实测。

## 1. 前置：v3 严格隔离三元组

1. v3 数据面强制 `team_id` + `agent_id` + `user_id` 三项，缺失返回 422；三项可放在请求体，也可分别由 `x-tdai-team-id`、`x-tdai-agent-id`、`x-tdai-user-id` 请求头提供；`session_id` 可选（F-153）。
2. 鉴权采用 Bearer 令牌加 `x-tdai-service-id` 头（F-156）。
3. MemoryCore 监听 8420（F-022/F-163）。
4. 下例 shell 变量均为本示例自定义占位，不是系统配置项：

```bash
CORE="http://127.0.0.1:8420"
BEARER="sk-mem-..."          # 来自 .admin-key（F-275）
SERVICE_ID="<your-service-id>"
TEAM_ID="<your-team-id>"
AGENT_ID="<your-agent-id>"
USER_ID="<your-user-id>"
```

## 2. TS SDK：只做 import 与构造

TS SDK 包名为 `@tencentdb-agent-memory/memory-sdk-ts-v2`（F-287），顶级导出即 v3 严格 isolation 版本（F-289），构造要求六个参数（F-290）：

```ts
import { MemoryClient } from "@tencentdb-agent-memory/memory-sdk-ts-v2";

const memory = new MemoryClient({
  endpoint: "http://127.0.0.1:8420",
  apiKey: process.env.TDAI_API_KEY!,
  serviceId: process.env.TDAI_SERVICE_ID!,
  teamId: process.env.TDAI_TEAM_ID!,
  agentId: process.env.TDAI_AGENT_ID!,
  userId: process.env.TDAI_USER_ID!,
});
```

SDK 的具体方法名未在事实清单登记，本示例不编造；后续写读操作一律用 curl 调用 F-093 登记的裸端点。方法级用法以随包 `AGENT_GUIDE.typescript.zh-CN.md` 为准（F-291）。

## 3. 创建 Prompt：POST /v3/memory-prompt/create

先把请求体写入文件（字段契约以随仓卷一文档 3.5 Memory-Prompt 章节为准，见 references/03）：

```curl
curl -sS -X POST "$CORE/v3/memory-prompt/create" \
  -H "Authorization: Bearer $BEARER" \
  -H "x-tdai-service-id: $SERVICE_ID" \
  -H "x-tdai-team-id: $TEAM_ID" \
  -H "x-tdai-agent-id: $AGENT_ID" \
  -H "x-tdai-user-id: $USER_ID" \
  -H "Content-Type: application/json" \
  --data-binary @prompt.create.json
```

端点路径属 `/v3/memory-prompt/*` 面（create/get/update/delete/set/log）（F-093）。请求体经 Zod v4 校验，失败返回 400（F-152）。

## 4. 激活 Prompt：POST /v3/memory-prompt/set

```curl
curl -sS -X POST "$CORE/v3/memory-prompt/set" \
  -H "Authorization: Bearer $BEARER" \
  -H "x-tdai-service-id: $SERVICE_ID" \
  -H "x-tdai-team-id: $TEAM_ID" \
  -H "x-tdai-agent-id: $AGENT_ID" \
  -H "x-tdai-user-id: $USER_ID" \
  -H "Content-Type: application/json" \
  --data-binary @prompt.set.json
```

解析优先级为 agent → team → instance → 内置默认（F-088）：要验证 agent 级是否生效，需确认同级没有更高优先级的 Prompt 覆盖。

## 5. 对话验证

经 proxy 发起一轮正常对话，让记忆抽取链路消费新 Prompt（注入侧见 F-225）。验证时注意三层输出协议不可通过自定义 Prompt 修改（F-091）：

| 层 | 固定输出协议 |
|----|--------------|
| L1 | JSON（F-091） |
| L2 | Scene Markdown（F-091） |
| L3 | Persona + Doctrine（F-091） |

自定义策略文本经 composer 注入 `<CUSTOM_MEMORY_STRATEGY>` 占位符，并由 `<SYSTEM_CUSTOM_STRATEGY_GUARD>` 守卫约束（F-090）。

## 6. 查生成日志：generation-log 的 list/get

调用裸路径 `/v3/memory-generation-log/list` 与 `/v3/memory-generation-log/get`（F-093）；HTTP 方法与参数以随仓卷一文档 3.6 章节为准：

```bash
curl -sS "$CORE/v3/memory-generation-log/list" \
  -H "Authorization: Bearer $BEARER" \
  -H "x-tdai-service-id: $SERVICE_ID" \
  -H "x-tdai-team-id: $TEAM_ID" \
  -H "x-tdai-agent-id: $AGENT_ID" \
  -H "x-tdai-user-id: $USER_ID"
```

日志记录 Prompt ID、版本、来源与 SHA-256，**不存储 prompt 正文**（F-092）。审计做法是用 SHA-256 与现存 Prompt 对拍，而不是从日志还原正文（F-092）。

## 7. 限制与红线

1. 每个 instance 最多 500 条 Prompt，单条 ≤ 10000 Unicode 字符；版本递增而 `memory_prompt_id` 保持不变（F-089）。
2. L1 JSON / L2 Scene Markdown / L3 Persona+Doctrine 的输出协议不可改（F-091）。
3. 只能改策略文本与措辞，占位符与 GUARD 必须保留（F-090）。

## 8. 失败处置

| 现象 | 依据 | 处置 |
|------|------|------|
| 返回 422 | 三元组缺失（F-153） | 补齐 body 字段或三个 `x-tdai-*` 头 |
| 返回 400 | 请求体未通过 Zod 校验（F-152） | 按卷一 3.5 契约修正 JSON 后重试 |
| 返回 401/403 | Bearer 或 service-id 问题（F-156） | 核对 admin key 与 service-id |
| 修改后行为无变化 | 解析优先级 agent→team→instance→内置（F-088） | 用 set 激活目标层级，并检查更高优先级是否覆盖 |
| Prompt 被拒绝/不生效 | 触碰固定输出协议（F-091） | 只调整策略文本，保留 JSON/MD/Persona 协议骨架 |
| 超长写入失败 | 单条 ≤10000 Unicode、每 instance ≤500 条（F-089） | 拆条或精简；同一策略用版本递增而非新建 id |
| 日志里找不到正文 | 日志只记 SHA-256（F-092） | 用哈希对拍，不要尝试从日志还原 |

## 相关概念

- [L2 场景、L3 Persona 与自定义 Prompt](../concepts/03-l2-scene-l3-persona.md)
- [网关、隔离与 API 契约](../concepts/06-gateway-isolation.md)
- [SDK 与工程配套](../concepts/12-sdk-engineering.md)
- 信源：[v3 API 三卷与 OpenAPI 信源](../references/03-api-references.md)、[官方 SDK 与工程配套信源](../references/05-sdk-ci.md)
