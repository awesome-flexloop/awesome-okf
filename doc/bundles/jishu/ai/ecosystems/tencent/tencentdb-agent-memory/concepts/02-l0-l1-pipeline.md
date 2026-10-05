---
type: Concept
title: "L0/L1 管线：抽取、去重、双写与 fail-open 降级"
description: "MemoryCore 的包依赖与 bin、L1 抽取默认参数、topK=5 去重与四决策、JSONL 主存向量双写、隔离过滤、状态后端与三个后台服务。"
tags: [tencentdb-agent-memory, concept, pipeline, l0, l1, dedup, fail-open]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: s-core-code
    resource: /references/01-source-code-map.md
    title: TencentDB-Agent-Memory 源码地图
  - id: s-readme
    resource: /references/02-readme-changelog.md
    title: README 与 CHANGELOG 信源
---

# L0/L1 管线：抽取、去重、双写与 fail-open 降级

> **本篇看点**：L0/L1 是「记下来优先于记得好」的一条管线：L1 抽取默认每 10 条消息一轮、每会话上限 10 条记忆（F-061），去重用 topK=5 召回候选并让 LLM 做 store/skip/update/merge 四决策（F-062~F-064）；写入以 JSONL 为主存、向量为副写，嵌入与向量失败均不阻塞主存（F-065）。召回超时只返回 error 结果、hook 层不抛错（F-068）。这一「能力降级但不中断」的模式被 spec/insights.md 洞察三概括为 **fail-open（降级优先）**：无 LLM、无 embedding、检索不健康时全链路仍可运转（F-063~F-068）。

## 包形态：依赖与 bin

MemoryCore 包名为 `@tencentdb-agent-memory/memory-tencentdb-v2`，版本 `1.0.2-beta.1`（F-057）。主要依赖如下（F-058）：

| 类别 | 包 |
|---|---|
| LLM/SDK | ai@^6、@ai-sdk/openai（F-058） |
| 向量/分词 | sqlite-vec@0.1.7-alpha.2、@node-rs/jieba（F-058） |
| 存储/后端 | mongodb@^6.21（F-058） |
| 校验/工具 | zod@4、undici@8、js-tiktoken（F-058） |

optionalDependencies 含 @clickhouse/client、cos-nodejs-sdk-v5、ioredis、kafkajs、opik；peerDependencies 含 node-llama-cpp（本地 LLM）与 openclaw>=2026.3.7（F-059）。bin 声明四个命令：migrate-sqlite-to-tcvdb、export-tencent-vdb、read-local-memory、seed-v2（F-060）。

## L1 抽取默认参数：10 / 5 / 10

| 参数 | 默认值 | 含义 |
|---|---|---|
| maxMessagesPerExtraction | 10 | 单次抽取最多消费的消息数（F-061） |
| maxBackgroundMessages | 5 | 背景消息上限（F-061） |
| enableDedup | true | 默认开启去重（F-061） |
| maxMemoriesPerSession | 10 | 每会话记忆条数上限（F-061） |

上述默认值定义在 l1-extractor.ts（F-061）。L1 抽取 prompt 位于 core/prompts/l1-extraction.ts，去重 prompt 位于 l1-dedup.ts，场景抽取 prompt 位于 scene-extraction.ts（F-069）。

## 去重：topK=5、混合候选与四决策

去重召回参数 conflictRecallTopK=5，即对每条候选记忆取 5 条最相似的既有记忆做冲突判断（F-062）。候选召回走 hybrid/FTS/vector + RRF 融合；当检索能力缺失时，降级为全量保存（F-063）。去重 LLM 判定超时或失败时同样降级为全量 store；判定结果固定为四个决策值（F-064）：

```text
候选记忆 ── hybrid/FTS/vector + RRF 融合召回（topK=5）
          │
          ├─ 检索能力缺失 ───────────────→ 全量保存（F-063）
          ├─ LLM 判定超时 / 失败 ─────────→ 全量 store（F-064）
          └─ LLM 四选一：
               store  ：新增记忆
               skip   ：丢弃
               update ：更新既有记忆
               merge  ：合并既有记忆（F-064）
```

## 写入：JSONL 主存 + 向量双写

L1 写入采用 JSONL 主存 + 向量双写，降级次序明确（F-065）：

```text
1. JSONL 主存写入        —— 不可降级，必须成功
2. 嵌入（embedding）失败 —— 仅写 metadata / FTS，丢向量（F-065）
3. 向量写入失败          —— 不阻塞 JSONL 主存（F-065）
```

即派生索引（向量、FTS）全部允许缺席，原始事实先落盘，索引可事后重建（F-065）。

## fail-open：降级优先的写入与召回美学

本篇管线在多个关键路径上选择「能力降级但不中断」，即 spec/insights.md 洞察三所称的 fail-open 模式（F-063、F-064、F-065、F-068）：

- 去重 LLM 不可用 → 全量 store，跳过 skip/update/merge 精修（F-064）。
- 混合检索任一路不可用 → RRF 天然允许单路缺席；整体检索能力缺失则全量保存（F-063）。
- embedding/向量失败 → 只丢向量，不丢原文（F-065）。
- 召回超时 → 返回 RecallResult.error，hook 层不向上抛错（F-068）。

其设计取舍是：检索变差是质量问题，记忆漏记是永久数据丢失，因此「记下来」永远优先（F-065）。运维代价是降级期去重失效带来数据膨胀，必须消费 error/不健康标记，不能只看请求成功率（F-063、F-068）。

## L0 记录器：隔离字段与延迟嵌入

L0 记录器实现于 l0-recorder.ts；L0 表/文件包含 team_id、user_id、agent_id、session_key、session_id、task_id 六个隔离字段（F-066）。hooks/auto-capture.ts 在捕获时写 L0 记录并打 checkpoint；L0 向量为可选项，当 supportsDeferredEmbedding 可用时在后台做延迟嵌入（F-067）。

## 召回 hook：超时不抛错

hooks/auto-recall.ts 的召回用 Promise.race 做超时控制：超时返回 RecallResult.error，hook 层不向上抛错，避免记忆子系统拖垮主对话链路（F-068）。召回支持 keyword、embedding、hybrid 三种模式（F-068）。L1 reader 实现于 record/l1-reader.ts，负责读取与隔离过滤（F-070）。

## IsolationFilter 六字段

隔离过滤结构 IsolationFilter 含六个字段（F-071）：

| 字段 | 对应隔离维度 |
|---|---|
| teamId | 团队（F-071） |
| userId | 用户（F-071） |
| agentId | Agent（F-071） |
| sessionId | 会话（F-071） |
| taskId | 任务（F-071） |
| sessionKey | 会话键（F-071） |

六字段与 L0 落库的隔离列一一对应，使多租户隔离在读取与写入两侧保持同一口径（F-066、F-071）。

## 状态后端与定时器

local-backend.ts 维护 sessionStates、buffers、timers、taskQueue、pendingTasks、locks 等内存结构（F-072）。消息到达后的冲刷策略为：capture 达到阈值即入队，否则由定时器冲刷；timer-member 映射覆盖 L1、L2、L3、flush 四类成员（F-073）。

## 三个后台服务

| 服务 | 职责 |
|---|---|
| pipeline-worker | 管线后台执行（F-074） |
| timer-scanner | 定时扫描并触发冲刷（F-074） |
| worker-permit-pool | worker 许可池，控并发（F-074） |

三个后台服务均位于 services/ 目录（F-074）。

## 存储抽象、工具与适配层

- 存储抽象层为 storage/adapter.ts 配 factory.ts；本地实现 local-backend.ts，Mongo 实现 mongo-fs-backend.ts（F-075）。
- 内部工具层含 memory-search.ts 与 read-cos.ts 两个工具（F-076）。
- 报告层支持 console、file、noop、obs、otlp 多种 backend，由 report/factory.ts 选择（F-077）。
- API 追踪子系统 api-trace 含策略、脱敏、stdout、OTel 上下文传播与 traced-proxy（F-078）。
- 适配层：OpenClaw 适配位于 adapters/openclaw/（index.ts、llm-runner.ts），standalone 适配位于 adapters/standalone/index.ts（F-079）。
- 运维工具：内存清理与备份位于 utils/memory-cleaner.ts、utils/backup.ts、utils/checkpoint.ts（F-080）。

## 延伸阅读

- 上一篇：[01-four-layer-memory.md](01-four-layer-memory.md)——四层模型与四类资产
- 下一篇：[03-l2-scene-l3-persona.md](03-l2-scene-l3-persona.md)——L2 场景、L3 Persona 与自定义 Prompt
- 存储细节：[04-storage-retrieval.md](04-storage-retrieval.md)——三后端、RRF 与 BM25
- 信源：[源码地图](../references/01-source-code-map.md)、[README 与 CHANGELOG](../references/02-readme-changelog.md)
