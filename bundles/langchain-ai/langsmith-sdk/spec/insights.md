# langsmith-sdk JS 架构洞察

## I-001：RunTree 用 UUID7 与 dotted_order 同时表达父子关系和执行顺序

- **陈述**：一条 trace 不是只靠 `parent_run_id` 还原，还同时携带 `trace_id` 与 `dotted_order`。RunTree 在构造时生成基于开始时间的 UUID7，并把时间串和 run id 拼成 dotted order；子节点把父节点的 `dotted_order` 作为前缀。
- **证据**：F-035、F-038、F-039、F-042、F-044；`RunTree` 字段包含 `trace_id`、`dotted_order`、`execution_order`、`child_execution_order`；`_convertToCreate` 会把这些字段写入 `RunCreate`。
- **反常识**：树结构并不足以表达异步、并发、重试、流式输出中的顺序。SDK 没有在结束时重新排序，而是在创建每个 span 时就把时间和 UUID 编入可排序字符串。
- **行动**：阅读和排查 trace 时，应同时看 `trace_id`、`parent_run_id`、`dotted_order`；集成自定义执行器时要保留 ALS 上下文或显式传入 RunTree，否则顺序串会断开。

## I-002：traceable 的核心是“上下文解析 + 返回值包装”，不是装饰器语法

- **陈述**：`traceable` 是高阶函数。它先从显式 `RunTree`、`ROOT`、LangChain runnable config 或 ALS 中解析当前上下文，再包装函数返回值；普通 Promise、ReadableStream、AsyncIterable、generator 都有不同分支。
- **证据**：F-048-F-063；参数类型允许 `[RunTree, ...Inputs]` 与 `[RunnableConfigLike, ...Inputs]`；函数内部识别 RunnableConfigLike、RunTree、ALS store；流和迭代器路径会添加 `new_token` 事件并在结束时处理 outputs。
- **反常识**：`traceable` 不是简单地在函数前后各发一次 HTTP 请求。它会在调用前 `postRun()`，并把最终 patch 推迟到 Promise resolve、stream done、iterator return 或错误发生之后。
- **行动**：封装 LLM/工具/Agent 时优先使用 `processInputs`、`processOutputs`、`aggregator`、`extractAttachments` 等配置点；排查“输出没上报”时应检查返回值是否为未被识别的异步迭代对象。

## I-003：Client 将 tracing API 设计成异步批处理管道，把可靠性放在请求路径之外

- **陈述**：Client 同时维护普通 caller、batch ingest caller、AutoBatchQueue、pending drain 集合和失败 trace 落盘目录。`createRun` 与 `updateRun` 在具备 `trace_id`、`dotted_order` 且启用自动批处理时进入队列，而不是立即发送。
- **证据**：F-019、F-023、F-024、F-027、F-028、F-034；构造函数设置两个 `AsyncCaller`、最大队列内存和重试；`updateRun` 在根 run 结束且 `blockOnRootRunFinalization` 为 true 时可等待批处理；`awaitPendingTraceBatches()` 会等待队列与 caller idle。
- **反常识**：示例脚本“看起来执行完了”不等于 trace 已经到达服务端。批处理是后台 Promise，评测或短进程需要显式等待。
- **行动**：在脚本、测试、Serverless、评测任务结束前调用 `await client.awaitPendingTraceBatches()`；高吞吐场景再考虑 `manualFlushMode` 与 `flush()`；不要依赖同步函数返回来判断上报成功。

## I-004：evaluate 复用 traceable 与 feedback API，形成“预测 run → evaluator run → feedback”的流水线

- **陈述**：`evaluate` 不是独立评测系统，而是把 target 函数包装成 traceable 生成预测 run，把 evaluator 也包装成 traceable 生成 evaluator run，再通过 `logEvaluationFeedback` 把 evaluator 输出写成模型反馈。
- **证据**：F-069-F-091；`DynamicRunEvaluator.evaluateRun` 使用 `traceable(..., { project_name: "evaluators", name: "evaluator" })`；`_forward` 对 target 做同样包装；`_runEvaluators` 调用 `client.logEvaluationFeedback(...)`；`_evaluate` 最后等待 pending trace batches。
- **反常识**：评测器本身也是被观测对象。它会产生 project_name 为 `evaluators` 的 run，并通过 `sourceRunId`、`targetRunId` 把评估 run 和被评估 run 连接起来。
- **行动**：编写 evaluator 时只需要返回稳定的 `key` 和 `score/value/comment`；如果需要追踪 evaluator 内部细节，可依赖同一套 traceable/RunTree 机制，而不是另建日志系统。

## 知识地图

```text
入口
├── Client ........................... HTTP、批处理、feedback、dataset/project API
├── RunTree .......................... run 数据模型、id/trace_id/dotted_order、post/patch
├── traceable ........................ 上下文解析、Promise/Stream/Generator 包装
├── evaluation ....................... target 运行、evaluator 包装、summary feedback
└── anonymizer ....................... 输入/输出/metadata 字符串级脱敏
```

推荐阅读顺序：

1. [SDK 总览](/langchain-ai/langsmith-sdk/concepts/overview.md)
2. [traceable 装饰器](/langchain-ai/langsmith-sdk/concepts/traceable-decorator.md)
3. [RunTree 追踪模型](/langchain-ai/langsmith-sdk/concepts/run-tree-tracing.md)
4. [评测运行器](/langchain-ai/langsmith-sdk/concepts/evaluation.md)
5. [快速示例](/langchain-ai/langsmith-sdk/examples/quickstart-trace-and-evaluate.md)

## 文档覆盖矩阵

| 文档 | 覆盖事实 |
|---|---|
| [overview](/langchain-ai/langsmith-sdk/concepts/overview.md) | F-001-F-034, F-093-F-100 |
| [traceable-decorator](/langchain-ai/langsmith-sdk/concepts/traceable-decorator.md) | F-048-F-068, F-093-F-100 |
| [run-tree-tracing](/langchain-ai/langsmith-sdk/concepts/run-tree-tracing.md) | F-008-F-015, F-035-F-047 |
| [evaluation](/langchain-ai/langsmith-sdk/concepts/evaluation.md) | F-069-F-092 |
| [quickstart-trace-and-evaluate](/langchain-ai/langsmith-sdk/examples/quickstart-trace-and-evaluate.md) | F-003-F-007, F-016-F-034, F-048-F-091 |
