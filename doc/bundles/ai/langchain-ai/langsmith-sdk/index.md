---
type: bundle
okf_version: "0.2"
scope: langsmith-sdk
name: langsmith-sdk
version: "0.9.0"
source: https://github.com/langchain-ai/langsmith-sdk
description: LangSmith JavaScript/TypeScript SDK 源码学习包，覆盖 Client 上报、RunTree 追踪模型、traceable 高阶函数、evaluate 评测流水线与客户端脱敏。
---

# langsmith-sdk JS

**langsmith-sdk** 是 LangSmith 的 JavaScript/TypeScript 客户端库。它把 LLM 应用执行过程建模为 `RunTree`，通过 `traceable` 自动串联嵌套调用，由 `Client` 批量上报到 LangSmith API，并通过 `evaluate` 在数据集上运行预测与评测器。

- **包名**：`langsmith`
- **版本**：0.9.0
- **源码仓库**：https://github.com/langchain-ai/langsmith-sdk
- **重点模块**：`client.ts`、`run_trees.ts`、`traceable.ts`、`evaluation/`、`anonymizer/`

## 核心能力

- **自动追踪**：`traceable()` 包装普通函数、Promise、ReadableStream、AsyncIterable 和 generator，自动创建和结束 run。
- **树形执行模型**：`RunTree` 使用 UUID7、`trace_id` 与 `dotted_order` 同时表达 trace 根、父子关系和执行顺序。
- **批量上报**：`Client.createRun()` 与 `Client.updateRun()` 进入 AutoBatchQueue 和 batch caller，结束时可通过 `awaitPendingTraceBatches()` 等待。
- **评测流水线**：`evaluate()` 复用 traceable 生成预测 run 和 evaluator run，再将 `EvaluationResult` 写成 feedback。
- **客户端脱敏**：`createSecretAnonymizer()` 预置常见密钥规则，可传入 `ClientConfig.anonymizer`。

## 文档导航

### 核心概念

- [SDK 总览](/ai/langchain-ai/langsmith-sdk/concepts/overview.md) — 五个核心构件、追踪链路、评测链路与数据模型
- [traceable 自动追踪装饰器](/ai/langchain-ai/langsmith-sdk/concepts/traceable-decorator.md) — 上下文解析、流包装、Promise Proxy 与配置钩子
- [RunTree 追踪模型](/ai/langchain-ai/langsmith-sdk/concepts/run-tree-tracing.md) — `trace_id`、`dotted_order`、`createChild`、`postRun`、`patchRun`
- [评测运行器](/ai/langchain-ai/langsmith-sdk/concepts/evaluation.md) — `evaluate`、`_ExperimentManager`、`RunEvaluator`、`StringEvaluator`

### 使用示例

- [快速追踪与评测示例](/ai/langchain-ai/langsmith-sdk/examples/quickstart-trace-and-evaluate.md) — Client、traceable、anonymizer、evaluate、StringEvaluator 的最小组合

### 参考资料

- [核心源码索引](/ai/langchain-ai/langsmith-sdk/references/source-core.md) — 核心源码文件、公共导入路径与数据流

### 工作稿

- [事实清单](/ai/langchain-ai/langsmith-sdk/spec/facts.md) — 100 条带源码路径和行号的编号事实
- [架构洞察](/ai/langchain-ai/langsmith-sdk/spec/insights.md) — 4 个架构洞察与知识地图
- [变更日志](/ai/langchain-ai/langsmith-sdk/log.md) — bundle 生成记录

## 快速开始

```ts
import { Client } from "langsmith";
import { traceable } from "langsmith/traceable";

const client = new Client();

const answer = traceable(async (question: string) => {
  return { answer: `echo: ${question}` };
}, { name: "answer", client });

await answer("What is LangSmith?");
await client.awaitPendingTraceBatches();
```

## 目录结构

```text
langsmith-sdk/
├── concepts/              # 核心概念（4 篇）
├── examples/              # 使用示例（1 篇）
├── references/            # 源码参考（1 篇）
├── spec/
│   ├── facts.md           # 源码事实验证清单
│   └── insights.md        # 架构洞察
├── index.md               # 本文件
└── log.md                 # 生成日志
```

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
