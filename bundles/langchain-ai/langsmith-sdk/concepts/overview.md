---
type: concept
title: langsmith-sdk JS 总览
description: 从 Client、RunTree、traceable、evaluation 与 anonymizer 理解 LangSmith JavaScript SDK 的追踪与评测结构。
tags: [langsmith, overview, tracing, evaluation]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
sources:
  - id: source-core
    resource: /references/source-core.md
    title: langsmith-sdk JS 核心源码索引
---

# langsmith-sdk JS 总览

`langsmith` 是 LangSmith 的 JavaScript/TypeScript 客户端库。它既负责把应用执行过程上报为 run，也负责数据集、示例、反馈、实验和评测结果的 API 访问。当前包版本为 `0.9.0`，根入口导出 `Client`、`RunTree` 和主要 schemas 类型；`traceable`、`evaluate`、anonymizer 等能力通过子路径导入。

## 五个核心构件

| 构件 | 入口 | 职责 |
|---|---|---|
| `Client` | `langsmith` / `langsmith/client` | HTTP API、批处理上报、dataset/example/feedback/project 管理 |
| `RunTree` | `langsmith` / `langsmith/run_trees` | 单条 run 的内存模型，维护 `id`、`trace_id`、`dotted_order`、父子关系 |
| `traceable` | `langsmith/traceable` | 高阶函数，自动创建/结束 RunTree，处理 Promise、stream、async iterator |
| `evaluate` | `langsmith/evaluation` | 数据集实验编排：运行 target、执行 evaluator、写入 feedback |
| `createAnonymizer` | `langsmith/anonymizer` | 在客户端递归替换字符串中的敏感值 |

## 追踪链路

一次普通追踪大致经过以下路径：

```text
traceable(fn)
  → 解析当前 RunTree 上下文
  → 创建 RunTree 并 postRun()
  → 执行被包装函数
  → 处理返回值或异常
  → RunTree.end(...)
  → RunTree.patchRun()
  → Client.createRun/updateRun(...)
  → AutoBatchQueue / batchIngestCaller
  → LangSmith API
```

`Client.createRun()` 在启用自动批处理且 run 具有 `trace_id`、`dotted_order` 时不会立即发送请求，而是把 create 操作放入后台队列。`updateRun()` 对根 run 的结束有特殊等待逻辑，短进程或脚本通常需要调用 `await client.awaitPendingTraceBatches()`。

RunTree 与 traceable 的细节分别见 [RunTree 追踪模型](/langchain-ai/langsmith-sdk/concepts/run-tree-tracing.md) 和 [traceable 装饰器](/langchain-ai/langsmith-sdk/concepts/traceable-decorator.md)。

## 评测链路

`evaluate(target, options)` 把数据集示例送入 target，再把 target 产生的 run 交给 evaluator。评测器本身也会被 `traceable` 包装到 `evaluators` 项目中，评测输出通过 `Client.logEvaluationFeedback()` 写成 feedback。

```text
Example
  → target(inputs)
  → prediction Run
  → evaluator.evaluateRun(run, example)
  → EvaluationResult
  → client.logEvaluationFeedback(...)
  → Feedback 挂到实验项目
```

评测接口、`RunEvaluator`、`StringEvaluator` 和 `_ExperimentManager` 的流程见 [评测运行器](/langchain-ai/langsmith-sdk/concepts/evaluation.md)。

## 数据模型主线

`schemas.ts` 中的基础类型贯穿全 SDK：

- `BaseRun` 描述 run 的通用字段：`name`、`run_type`、`inputs`、`outputs`、`parent_run_id`、`trace_id`、`dotted_order`。
- `Run` 扩展 `BaseRun`，表示从 API 读回的 run，增加 `id`、`session_id`、child runs、token stats 等字段。
- `RunCreate` 和 `RunUpdate` 分别对应创建与 PATCH 请求。
- `BaseExample`、`Example`、`Dataset`、`Feedback` 支撑评测与数据集管理。

## 客户端脱敏

`ClientConfig.anonymizer` 接收一个函数，用于处理 run inputs、outputs、metadata 和 error。`anonymizer` 子模块提供 `createAnonymizer()` 与 `createSecretAnonymizer()`：

- `createAnonymizer()` 遍历对象中的字符串节点，接受函数、规则数组或 processor。
- `createSecretAnonymizer()` 预置常见 API key、JWT、PEM 私钥、Authorization header、URL 凭据等规则，默认最大深度为 24。

## 最小使用形态

```ts
import { Client } from "langsmith";
import { traceable } from "langsmith/traceable";

const client = new Client({
  apiKey: process.env.LANGSMITH_API_KEY,
  apiUrl: process.env.LANGSMITH_ENDPOINT,
});

const answer = traceable(async (question: string) => {
  return { answer: `echo: ${question}` };
}, { name: "answer", client });

await answer("What is LangSmith?");
await client.awaitPendingTraceBatches();
```

完整可运行示例见 [快速追踪与评测示例](/langchain-ai/langsmith-sdk/examples/quickstart-trace-and-evaluate.md)。

## 相关概念

- [traceable 装饰器](/langchain-ai/langsmith-sdk/concepts/traceable-decorator.md)
- [RunTree 追踪模型](/langchain-ai/langsmith-sdk/concepts/run-tree-tracing.md)
- [评测运行器](/langchain-ai/langsmith-sdk/concepts/evaluation.md)
- [核心源码参考](/langchain-ai/langsmith-sdk/references/source-core.md)
