---
type: example
title: 快速追踪与评测示例
description: 使用 Client、traceable、createSecretAnonymizer 与 evaluate 构造最小可运行的 LangSmith JS SDK 示例。
tags: [langsmith, quickstart, traceable, evaluate]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
sources:
  - id: source-core
    resource: /references/source-core.md
    title: langsmith-sdk JS 核心源码索引
---

# 快速追踪与评测示例

本示例演示四个常见动作：创建带密钥脱敏的 `Client`、用 `traceable` 包装业务函数、在嵌套调用中读取当前 RunTree、用 `evaluate()` 对内存示例运行简单 evaluator。

## 1. 安装与导入

```ts
import { Client } from "langsmith";
import { traceable, getCurrentRunTree } from "langsmith/traceable";
import { evaluate } from "langsmith/evaluation";
import { createSecretAnonymizer } from "langsmith/anonymizer";
```

包导出映射由 `package.json` 的 `exports` 字段声明：根入口导出 `Client`，追踪、评测和脱敏能力分别从 `langsmith/traceable`、`langsmith/evaluation`、`langsmith/anonymizer` 导入。

## 2. 创建 Client

```ts
const client = new Client({
  apiKey: process.env.LANGSMITH_API_KEY,
  apiUrl: process.env.LANGSMITH_ENDPOINT,
  anonymizer: createSecretAnonymizer(),
  autoBatchTracing: true,
});
```

`createSecretAnonymizer()` 返回的函数会在 inputs、outputs、metadata 和 error 上报前递归处理字符串节点。默认规则会把常见 API key、JWT、PEM 私钥、Authorization header、Bearer token 和 URL 中的密码替换为 `[SECRET_DETECTED]`。

## 3. 包装业务函数

```ts
const normalize = traceable(
  async (text: string) => {
    return text.trim().toLowerCase();
  },
  { name: "normalize", client, run_type: "tool" },
);

const answer = traceable(
  async (question: string) => {
    const currentRun = getCurrentRunTree();
    currentRun.metadata = { questionLength: question.length };

    const normalized = await normalize(question);
    return {
      answer: `echo: ${normalized}`,
    };
  },
  { name: "answer", client, run_type: "chain" },
);

await answer("  Hello LangSmith  ");
await client.awaitPendingTraceBatches();
```

执行 `answer()` 时，SDK 会：

1. 创建名为 `answer` 的根 RunTree。
2. 调用 `normalize()` 时从 ALS 读取父 RunTree 并创建子 run。
3. 在函数返回后 patch outputs。
4. 把 create/update 操作交给 Client 的自动批处理队列。

最后一行 `await client.awaitPendingTraceBatches()` 用于短进程脚本。没有这一行，Node.js 可能在后台批处理请求发出前退出。

## 4. 使用 processInputs 与 processOutputs

```ts
const tracedSummarize = traceable(
  async (input: { text: string }) => {
    return { summary: input.text.slice(0, 20) };
  },
  {
    name: "summarize",
    client,
    processInputs: (input) => ({ textLength: input.text.length }),
    processOutputs: (output) => ({ summaryLength: output.summary.length }),
  },
);
```

`processInputs` 接收归一后的输入对象，`processOutputs` 接收归一后的返回值。配置要求不要 mutate 原始对象。

## 5. 运行内存数据集评测

`data` 支持 `Example[]`。以下示例使用内存数组，字段结构对应 `BaseExample`：

```ts
const results = await evaluate(
  async (input: { question: string }) => {
    return answer(input.question);
  },
  {
    client,
    experimentPrefix: "traceable-echo",
    data: [
      {
        dataset_id: "00000000-0000-7000-8000-000000000001",
        inputs: { question: "Hello" },
        outputs: { answer: "echo: hello" },
      },
      {
        dataset_id: "00000000-0000-7000-8000-000000000001",
        inputs: { question: "LangSmith" },
        outputs: { answer: "echo: langsmith" },
      },
    ],
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
    maxConcurrency: 1,
  },
);

console.log(results.length);
```

`evaluate()` 会为 target 创建预测 run，为 evaluator 创建 `project_name: "evaluators"` 的 run，并把每个 `EvaluationResult` 转成 feedback。`results.length` 对应该次实验处理的行数。

## 6. 使用 StringEvaluator

```ts
import { StringEvaluator } from "langsmith/evaluation";

const exactMatch = new StringEvaluator({
  evaluationName: "string_exact_match",
  inputKey: "question",
  predictionKey: "answer",
  answerKey: "answer",
  gradingFunction: async ({ input, prediction, answer }) => {
    return {
      score: prediction === answer,
      comment: `input=${input}`,
    };
  },
});
```

`StringEvaluator` 从 `run.inputs[inputKey]`、`run.outputs[predictionKey]` 和 `example.outputs[answerKey]` 取值。它实现了 `RunEvaluator` 接口，因此可以直接放入 `evaluators` 数组。

## 验证点

- 如果 trace 没有出现在 UI 中，先确认脚本末尾调用了 `await client.awaitPendingTraceBatches()`。
- 如果嵌套函数没有形成子 run，检查它是否经过同一个 `traceable` 包装函数调用，以及运行时是否支持 AsyncLocalStorage。
- 如果 evaluator 没有分数，检查返回对象是否包含 `key`。
- 如果敏感数据仍出现在 payload 中，确认自定义 anonymizer 被传入 `new Client({ anonymizer })`，并且该字段是字符串节点。

## 相关概念

- [SDK 总览](/ai/langchain-ai/langsmith-sdk/concepts/overview.md)
- [traceable 装饰器](/ai/langchain-ai/langsmith-sdk/concepts/traceable-decorator.md)
- [RunTree 追踪模型](/ai/langchain-ai/langsmith-sdk/concepts/run-tree-tracing.md)
- [评测运行器](/ai/langchain-ai/langsmith-sdk/concepts/evaluation.md)
