---
type: concept
title: 评测运行器
description: evaluate 如何通过 _ExperimentManager 运行 target、包装 evaluator、记录 EvaluationResult，并把结果写成 LangSmith feedback。
tags: [langsmith, evaluation, experiment, feedback]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
sources:
  - id: source-core
    resource: /references/source-core.md
    title: langsmith-sdk JS 核心源码索引
---

# 评测运行器

`langsmith/evaluation` 子路径导出 `evaluate()`、`EvaluateOptions`、`RunEvaluator`、`StringEvaluator` 等类型和类。评测模块不是独立的执行引擎；它复用 `traceable` 创建预测 run，再把 evaluator 的返回值转换成 feedback。

## 数据与目标函数

`evaluate(target, options)` 的 `data` 可以是：

- 数据集名称字符串
- `Example[]`
- `AsyncIterable<Example>`

标准 target 可以是函数，也可以是带 `invoke(input, config?)` 方法的对象：

```ts
type StandardTargetT =
  | ((input, config?) => Promise<output>)
  | ((input, config?) => output)
  | { invoke: (input, config?) => output }
  | { invoke: (input, config?) => Promise<output> };
```

当 target 为数组时，`evaluate()` 会进入比较评估路径并转调 `evaluateComparative()`。普通评估路径则创建 `_ExperimentManager`。

## 评估结果结构

每个行级 evaluator 返回以下形态之一：

- 单个 `EvaluationResult`
- `EvaluationResult[]`
- `EvaluationResults`，即 `{ results: EvaluationResult[] }`

`EvaluationResult` 的核心字段包括：

| 字段 | 说明 |
|---|---|
| `key` | feedback 名称 |
| `score` | 数值或布尔分数 |
| `value` | 分类或字符串值 |
| `comment` | 评语 |
| `correction` | 修正记录 |
| `evaluatorInfo` | 写入 feedback source info 的 evaluator 元信息 |
| `sourceRunId` | evaluator run 的 id |
| `targetRunId` | 被评估 run 的 id；缺省时指向根 run |
| `feedbackConfig` | feedback key 的配置 |

## evaluator 适配

`RunEvaluator` 接口要求实现 `evaluateRun(run, example?, options?)`。普通函数可用 `runEvaluator(func)` 包装为 `DynamicRunEvaluator`。

`DynamicRunEvaluator` 做了两件事：

1. 把内部传入的 `{ langSmithRunAndExample: { run, example } }` 解包。
2. 调用用户函数时传入增强对象：`{ ...run, run, example, inputs, outputs, referenceOutputs, attachments }`。

在 `evaluateRun()` 内，用户函数还会被 `traceable(..., { project_name: "evaluators", name: "evaluator" })` 包装。因此 evaluator 自身也产生一条可观测 run，并通过 `sourceRunId` 与被评估 run 关联。

## StringEvaluator

`StringEvaluator` 是面向字符串输入输出的内置 `RunEvaluator`。构造参数包括：

- `evaluationName?`
- `inputKey?`，默认 `input`
- `predictionKey?`，默认 `output`
- `answerKey?`，默认 `output`
- `gradingFunction`

执行时它从 `run.inputs[inputKey]` 读取输入，从 `run.outputs[predictionKey]` 读取预测，从 `example.outputs[answerKey]` 读取参考答案，然后调用 grading function。`run.outputs` 不存在时会抛出错误；grading function 返回缺少 key 时，使用 `evaluationName` 作为结果 key。

## _ExperimentManager 流水线

`_evaluate()` 的核心编排如下：

```text
new _ExperimentManager(...)
  → start()
  → withPredictions(target)
  → withEvaluators(evaluators)
  → withSummaryEvaluators(summaryEvaluators)
  → new ExperimentResults(manager)
  → results.processData(manager)
  → client.awaitPendingTraceBatches()
```

每个 `withX` 方法返回新的 `_ExperimentManager`，并通过 `atee()` 把异步生成器分流：

- `withPredictions()` 产生预测 run 和 result rows。
- `withEvaluators()` 解析 evaluator，执行评分，并把评估结果附加到 rows。
- `withSummaryEvaluators()` 在全部 run 完成后运行聚合评估器。

这种设计让预测、评分和结果消费可以通过异步生成器串联，而不是一次性把所有 run 放入内存。

## 并发控制

`EvaluateOptions` 提供三层并发参数：

- `maxConcurrency`：target 和 evaluator 的共享默认并发。
- `targetConcurrency`：预测阶段并发。
- `evaluationConcurrency`：evaluator 阶段并发。

当同时设置 `targetConcurrency` 和 `evaluationConcurrency` 时，runner 使用两个独立队列；否则使用共享队列。源码中 `maxConcurrency: 0` 注释为顺序执行，实际 PQueue 的 concurrency 为 `maxConcurrency === 0 ? 1 : maxConcurrency`。

## Feedback 写入

`_runEvaluators()` 为每条预测 run 调用 evaluator，随后调用：

```ts
client.logEvaluationFeedback({
  evaluatorResponse,
  run,
  projectId: this._getExperiment().id,
});
```

`Client._logEvaluationFeedback()` 将结果归一为数组，并对每个结果调用 `createFeedback(runId, key, ...)`。其中 run id 优先使用 `EvaluationResult.targetRunId`，否则使用被评估 run 的 id；`feedbackSourceType` 固定为 `"model"`。

Summary evaluator 在聚合所有 runs 后执行，并通过 `client.createFeedback(null, key, { projectId, ... })` 把聚合分数写到实验项目上。

## 典型 evaluator 写法

```ts
import { evaluate } from "langsmith/evaluation";

await evaluate(
  async (input: { question: string }) => {
    return { answer: `echo: ${input.question}` };
  },
  {
    data: "my-dataset",
    evaluators: [
      async ({ run, example }) => {
        const predicted = String(run.outputs?.answer ?? "");
        const expected = String(example?.outputs?.answer ?? "");
        return {
          key: "exact_match",
          score: predicted === expected,
        };
      },
    ],
    experimentPrefix: "echo-test",
  },
);
```

评测完成后，`evaluate()` 会等待 pending trace batches，确保预测 run、evaluator run 和 feedback 都已进入发送队列。

## 相关概念

- [SDK 总览](overview.md)
- [traceable 装饰器](traceable-decorator.md)
- [RunTree 追踪模型](run-tree-tracing.md)
- [快速追踪与评测示例](../examples/quickstart-trace-and-evaluate.md)
