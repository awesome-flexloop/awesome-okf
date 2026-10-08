---
type: Concept
title: "offload 卸载：与记忆沉淀分离的上下文压缩管线"
description: "offload 以 OpenClaw 插件形态实现 backend/collect/local 三模式，用独立的 L1/L1.5/L2/L3/L4 编号管理当前会话的上下文预算，仅在 L4 产出 Skill 时与记忆沉淀管线汇合。"
tags: [tencentdb-agent-memory, concept, offload, context-engineering, compression, mmd, skill]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-core-code
    resource: /references/01-source-code-map.md
    title: TencentDB-Agent-Memory 源码地图
  - id: s-readme-changelog
    resource: /references/02-readme-changelog.md
    title: README 与 CHANGELOG 信源
---

# offload 卸载：与记忆沉淀分离的上下文压缩管线

> **本篇看点**
>
> - 仓库里有两条都用 L1/L2/L3 编号的管线：记忆沉淀与上下文压缩，编号同名、语义不同（洞察二）。
> - offload 管的是「当前会话装得下」：批量上报、任务边界、MMD 节点、token 三级压缩（F-175~F-180）。
> - 三模式 backend / collect / local，可接独立 offload_server 或本地 node-llama-cpp（F-174、F-185、F-186）。
> - 只有 L4 create-skill 的产物回写沉淀管线（F-179）。

## 1. 先辨双管线：同名 L2/L3，不同世界

按洞察二，`MemoryCore/src/core` 与 `MemoryCore/src/offload` 是两个世界，二者刻意分离：

```text
管线 A：记忆沉淀（跨会话持久资产）
  L0 JSONL 原始对话 → L1 原子记忆抽取/去重/双写
  → L2 scene_blocks/*.md 场景 → L3 Persona（F-037~F-040）

管线 B：上下文压缩 offload（当前会话上下文预算）
  L1 批量上报 → L1.5 任务边界判定 → L2 MMD 任务节点
  → L3 token 溢出压缩 → L4 create-skill（F-173~F-184）
  汇合点：L4 产出的 Skill 回写沉淀管线（F-179）
```

沉淀侧 L3 是 Persona，offload 侧 L3 是压缩函数；两侧阈值互不联动，排障须先判断症状属于「记不住」还是「装不下」（洞察二）。

## 2. 入口与三模式

offload 以 OpenClaw 插件形态实现，入口为 `registerOffload`（F-173）；模式分 backend、collect、local 三种（F-174），其中 backend 侧有独立 offload_server、local 侧有本地 LLM 路径（F-185、F-186）。

## 3. L1 → L2 的上报节奏

```text
L1 批量上报（每批 5 条，失败重试 3 次，耗尽写 [L1 degraded]）（F-175）
  → L1.5 任务边界判定（重试 1 次、间隔 3000ms，fail-safe 推 short boundary）（F-176）
  → L2 每 30 条成批、每 5 秒轮询；null 阈值/超时秒数控制收敛（F-177）
  → L1.5 60 秒超时强制 settle（F-177）
  → 产出 .mmd 任务节点，节点 ID 形如 \d{3}-N\d+（F-178）
```

## 4. L1：批量 5、重试 3、降级占位

L1 批量参数 `L1_BATCH_SIZE=5`；失败重试 `MAX_L1_CHUNK_RETRIES=3`；重试耗尽后降级写一条 `[L1 degraded]` 条目而非丢数据（F-175）。

## 5. L1.5：任务边界判定

L1.5 的任务边界判定（l15Judge）有 1 次重试、间隔 3000ms；fail-safe 时推一个 short boundary 保证流程继续（F-176）。

## 6. L2：30 条批量、5 秒轮询与强制 settle

L2 每批 30 条、每 5 秒轮询一次；设有 null 阈值 `l2NullThreshold` 与超时秒数 `l2TimeoutSeconds`；L1.5 在 60 秒超时后被强制 settle（F-177）。L2 产出 MMD，即 `.mmd` 任务节点文件，节点 ID 正则为 `\d{3}-N\d+`（F-178）。

## 7. L3：token 溢出三级压缩

L3 是 token 溢出压缩，实现于 `llm-input-l3.ts`，含三级策略：`compressByScoreCascade`、`aggressiveCompressUntilBelowThreshold`、`emergencyCompress`，并有保底常量 `EMERGENCY_MIN_MESSAGES_TO_KEEP`（F-180）。token 计数使用 tiktoken 的 o200k_base 编码，分布在 l3-token-counter、fast-token-estimate、context-token-tracker 三处（F-181）。

```text
L3 压缩级联
  compressByScoreCascade（按分压缩）
  → aggressiveCompressUntilBelowThreshold（压到阈值以下）
  → emergencyCompress（紧急压缩，保留 EMERGENCY_MIN_MESSAGES_TO_KEEP）（F-180）
```

## 8. L4：create-skill

L4 对应 create-skill 斜杠命令，生成 SKILL.md，是压缩管线与 Skill 沉淀的汇合点（F-179）。

## 9. 会话过滤与工具调用触发

- 内部会话用正则 `/memory-.*-session-\d+/` 识别；HEARTBEAT 心跳消息被过滤，不计入卸载（F-182）。
- `after_tool_call` hook 攒工具调用 pair，`forceTriggerThreshold` 默认为 4（F-183）。
- LLM 输出侧卸载由 `hooks/llm-output.ts` 处理（F-187）。

## 10. 配套文件与独立服务

offload 配套文件（F-184）：

| 文件 | 事实出处（F-184） |
|---|---|
| backend-client.ts | offload 配套文件之一 |
| reclaimer.ts | offload 配套文件之一 |
| session-registry.ts | offload 配套文件之一 |
| state-manager.ts | offload 配套文件之一 |
| mmd-injector.ts | offload 配套文件之一 |
| storage.ts | offload 配套文件之一 |
| opik-tracer.ts | offload 配套文件之一 |

独立 `offload_server/` 提供五个模块（F-185）：

| 模块 | 事实出处（F-185） |
|---|---|
| ingest-handler | offload_server 模块 |
| mmd-handler | offload_server 模块 |
| router | offload_server 模块 |
| schemas | offload_server 模块 |
| session-utils | offload_server 模块 |

客户端为 `offload-client/context-engine.ts`（F-185）。本地 LLM 路径在 `offload/local-llm/`（index.ts、llm-caller.ts），对应 peer 依赖 node-llama-cpp（F-186）。

## 11. 安装脚本与随仓文档

- 插件安装脚本为 `install-openclaw-plugin.sh` 与 `install-hermes-plugin.sh`（F-188）。
- openclaw-plugin 架构文档位于 `openclaw-plugin/docs/architecture.md`（F-189）。
- MemoryCore 根目录的 `SKILL.md`、`SKILL-MIGRATION.md`、`SKILL-DIAGNOSTIC-EXPORT.md` 是随仓 Skill 的使用、迁移与诊断文档（F-190）。

## 12. 设计解读：把「记得住」与「装得下」拆成两个工程问题

offload 的全部参数都服务于当前会话的连续性：批大小与轮询控制上报节奏（F-175、F-177），边界判定失败推 short boundary（F-176），压缩有保底消息数（F-180），心跳与内部会话被显式排除（F-182）。它与沉淀管线仅在 Skill 产物处汇合（F-179），意味着上下文工程可以激进压缩与丢弃，而跨会话记忆不被在线压缩决策污染。

## 延伸阅读

- [06 网关与隔离契约](06-gateway-isolation.md)
- [08 MemoryKnowledge 知识引擎](08-memory-knowledge.md)
- [实战 02：Claude Code 经 Proxy 零插件接入](../examples/02-claude-code-proxy.md)
