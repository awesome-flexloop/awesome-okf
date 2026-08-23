---
type: reference
title: langsmith-sdk JS 核心源码索引
description: 按 Client、RunTree、traceable、evaluation、anonymizer 梳理核心源码文件与可验证事实编号。
tags: [langsmith, tracing, sdk, source-map]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
sources:
  - id: source-core
    resource: /references/source-core.md
    title: langsmith-sdk JS 核心源码索引
---

# langsmith-sdk JS 核心源码索引

本参考页登记本次 OKF bundle 使用的源码范围。事实清单见 [/spec/facts.md](/langchain-ai/langsmith-sdk/spec/facts.md)，架构洞察见 [/spec/insights.md](/langchain-ai/langsmith-sdk/spec/insights.md)。

## 源码位置

| 模块 | 文件 | 覆盖内容 |
|---|---|---|
| 包元数据 | `js/package.json` | 包名、版本、子路径导出 |
| 根入口 | `js/src/index.ts` | `Client`、`RunTree`、schemas 类型、错误类型、缓存 API 导出 |
| HTTP 客户端 | `js/src/client.ts` | `Client`、`ClientConfig`、run 上报、批处理、feedback、dataset/project API |
| Run 树 | `js/src/run_trees.ts` | `RunTree`、`RunTreeConfig`、`WriteReplica`、`convertToDottedOrderFormat` |
| 自动追踪 | `js/src/traceable.ts` | `traceable`、`TraceableConfig`、输入输出归一、流与迭代器包装 |
| 上下文单例 | `js/src/singletons/traceable.ts` | ALS provider、`getCurrentRunTree`、`withRunTree`、`ROOT` |
| 数据结构 | `js/src/schemas.ts` | `Run`、`RunCreate`、`RunUpdate`、`Example`、`Dataset`、`Feedback` |
| 评测入口 | `js/src/evaluation/_runner.ts` | `evaluate`、`_ExperimentManager`、并发队列、summary evaluator |
| 评测器接口 | `js/src/evaluation/evaluator.ts` | `EvaluationResult`、`RunEvaluator`、`DynamicRunEvaluator`、`runEvaluator` |
| 字符串评测器 | `js/src/evaluation/string_evaluator.ts` | `StringEvaluator`、`GradingFunctionParams` |
| 脱敏器 | `js/src/anonymizer/index.ts` | `createAnonymizer`、`DEFAULT_SECRET_RULES`、`createSecretAnonymizer` |

## 公共入口映射

| 导入路径 | 导出内容 | 事实 |
|---|---|---|
| `langsmith` | `Client`、`RunTree`、schemas 类型、错误类型、prompt cache 工具 | F-004-F-006 |
| `langsmith/client` | `Client` 相关入口 | F-003 |
| `langsmith/run_trees` | `RunTree`、`RunTreeConfig`、`WriteReplica` | F-003、F-035-F-047 |
| `langsmith/traceable` | `traceable`、`getCurrentRunTree`、`withRunTree`、`ROOT` | F-048-F-068 |
| `langsmith/evaluation` | `evaluate`、`EvaluateOptions`、`RunEvaluator`、`StringEvaluator` | F-069-F-092 |
| `langsmith/schemas` | run、example、dataset、feedback 等类型 | F-008-F-015 |
| `langsmith/anonymizer` | `createAnonymizer`、`createSecretAnonymizer`、规则类型 | F-093-F-100 |

## 核心数据流

```text
traceable(fn)
  │
  ├─ 解析 RunTree / ROOT / RunnableConfigLike / ALS
  ├─ currentRunTree.postRun()
  ├─ 执行 fn，包装 Promise / Stream / AsyncIterable
  └─ handleRunOutputs(...)
        │
        └─ RunTree.patchRun()
              │
              └─ Client.updateRun(...)
                    │
                    ├─ AutoBatchQueue
                    ├─ batchIngestCaller
                    └─ PATCH /runs/:id

evaluate(target, { data, evaluators })
  │
  ├─ _ExperimentManager.start()
  ├─ traceable(target) 生成预测 run
  ├─ RunEvaluator.evaluateRun(...) 生成 evaluator run
  └─ Client.logEvaluationFeedback(...)
```

## 关键版本与边界

- 当前事实基于 `langsmith@0.9.0`（F-001、F-006）。
- `readRun()` 与 `listRuns()` 在源码中带有 deprecated JSDoc，并转调内部方法（F-029）。
- 根入口没有导出 `traceable` 与 `evaluate`，需要使用子路径导入（F-007）。

## 相关概念

- [SDK 总览](/langchain-ai/langsmith-sdk/concepts/overview.md)
- [traceable 装饰器](/langchain-ai/langsmith-sdk/concepts/traceable-decorator.md)
- [RunTree 追踪模型](/langchain-ai/langsmith-sdk/concepts/run-tree-tracing.md)
- [评测运行器](/langchain-ai/langsmith-sdk/concepts/evaluation.md)
