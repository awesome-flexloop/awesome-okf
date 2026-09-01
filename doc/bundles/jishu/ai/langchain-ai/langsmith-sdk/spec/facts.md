# langsmith-sdk JS 事实清单

## 项目与公共导出

F-001: `js/package.json` 第2-4行记录包名为 `langsmith`，版本为 `0.9.0`，描述为 `Client library to connect to the LangSmith Observability and Evaluation Platform.`。

F-002: `js/package.json` 第139-141行的 repository 字段指向 `https://github.com/langchain-ai/langsmith-sdk.git`。

F-003: `js/package.json` 第245-362行声明子路径导出：`.`、`./client`、`./run_trees`、`./traceable`、`./evaluation`、`./schemas`、`./anonymizer` 等分别映射到 ESM 与 CJS 入口。

F-004: `js/src/index.ts` 第1-5行从 `./client.js` 导出 `Client`、`ClientConfig`、`LangSmithTracingClientInterface`。

F-005: `js/src/index.ts` 第7-15行从 `./schemas.js` 导出类型 `Dataset`、`Example`、`TracerSession`、`Run`、`Feedback`、`FeedbackConfigSchema`、`RetrieverOutput`。

F-006: `js/src/index.ts` 第17行导出 `RunTree`、`RunTreeConfig`、`WriteReplica`；第57行导出常量 `__version__ = "0.9.0"`；第60行导出 `LS_MESSAGE_VIEW_EXCLUDE = "ls_message_view_exclude"`。

F-007: `js/src/index.ts` 没有导出 `traceable`、`evaluate`、`createAnonymizer`；这些入口分别由 `./traceable`、`./evaluation`、`./anonymizer` 子路径导出。

## schemas.ts

F-008: `js/src/schemas.ts` 第44行定义 `KVMap = Record<string, any>`；第46-53行定义 `RunType`，包含 `llm`、`chain`、`tool`、`retriever`、`embedding`、`prompt`、`parser`。

F-009: `js/src/schemas.ts` 第54-56行定义 `ScoreType = number | boolean | null`、`ValueType = number | boolean | string | object | null`、`DataType = "kv" | "llm" | "chat"`。

F-010: `js/src/schemas.ts` 第58-64行定义 `BaseExample`，字段包含 `dataset_id`、`inputs`、`outputs`、`metadata`、`source_run_id`。

F-011: `js/src/schemas.ts` 第77-80行定义 `Attachments = Record<string, [string, AttachmentData] | AttachmentDescription>`。

F-012: `js/src/schemas.ts` 第86-151行定义 `BaseRun`，字段包含 `id?`、`name`、`start_time?`、`run_type`、`end_time?`、`extra?`、`error?`、`serialized?`、`events?`、`inputs`、`outputs?`、`reference_example_id?`、`parent_run_id?`、`tags?`、`trace_id?`、`dotted_order?`、`attachments?`。

F-013: `js/src/schemas.ts` 第166-214行定义 `Run extends BaseRun`，增加 `id: string`、`session_id?`、`child_run_ids?`、`child_runs?`、`feedback_stats?`、`app_path?`、`status?`、`prompt_tokens?`、`completion_tokens?`、`total_tokens?` 等字段。

F-014: `js/src/schemas.ts` 第216-220行定义 `RunCreate extends BaseRun`，增加 `revision_id?`、`child_runs?: this[]`、`session_name?`。

F-015: `js/src/schemas.ts` 第222-243行定义 `RunUpdate`，其中 `id?`、`name?`、`run_type?`、`inputs?`、`outputs?`、`trace_id?`、`dotted_order?` 等字段均为可选。

## Client

F-016: `js/src/client.ts` 第161-241行定义 `ClientConfig`，包含 `apiUrl?`、`apiKey?`、`callerOptions?`、`timeout_ms?`、`webUrl?`、`anonymizer?`、`hideInputs?`、`hideOutputs?`、`hideMetadata?`、`omitTracedRuntimeInfo?`、`autoBatchTracing?`、`batchSizeBytesLimit?`、`batchSizeLimit?`、`maxIngestMemoryBytes?`、`blockOnRootRunFinalization?`、`traceBatchConcurrency?`、`fetchOptions?`、`manualFlushMode?`、`tracingSamplingRate?`、`debug?`、`workspaceId?`、`fetchImplementation?`、`disablePromptCache?`、`tracingMode?`、`headers?`。

F-017: `js/src/client.ts` 第1015行声明 `export class Client implements LangSmithTracingClientInterface`。

F-018: `js/src/client.ts` 第1016-1108行列出 Client 的私有字段，包括 `apiKey`、`apiUrl`、`webUrl`、`workspaceId`、`caller`、`batchIngestCaller`、`timeout_ms`、`hideInputs`、`hideOutputs`、`hideMetadata`、`anonymizer`、`tracingSampleRate`、`autoBatchTracing`、`autoBatchQueue`、`batchSizeBytesLimit`、`batchSizeLimit`、`fetchOptions`、`manualFlushMode`、`_tracingMode`、`_promptCache` 等。

F-019: `js/src/client.ts` 第1370-1456行的构造函数读取 `Client.getDefaultClientConfig()`；设置 `timeout_ms` 默认值 `90_000`，`caller` 的 `maxRetries` 为 4，`batchIngestCaller` 的 `maxRetries` 为 4、`maxConcurrency` 为 `traceBatchConcurrency`、`maxQueueSizeBytes` 为 `maxIngestMemoryBytes ?? DEFAULT_MAX_SIZE_BYTES`。

F-020: `js/src/client.ts` 第1429-1435行将 `hideInputs`、`hideOutputs`、`hideMetadata` 的回退值设为 `config.anonymizer`；同时单独保存 `this.anonymizer = config.anonymizer`。

F-021: `js/src/client.ts` 第1445-1454行把 `config.fetchOptions.headers` 归一化后存入 `_fetchOptionsHeaders`，其余 `fetchOptions` 存入 `fetchOptions`；`config.headers` 经 `assertValidHeaders` 校验后存入 `_customHeaders`。

F-022: `js/src/client.ts` 第2487-2494行的 `flush()` 调用 `_getBatchSizeLimitBytes()`、`_getBatchSizeLimit()`，随后调用 `drainAutoBatchQueue(...)`。

F-023: `js/src/client.ts` 第2508-2566行定义 `createRun(run, options?)`；当采样过滤器返回空数组时直接返回；在 `autoBatchTracing`、`trace_id`、`dotted_order` 都存在时调用 `processRunOperation({ action: "create", ... })`，否则向 `${apiUrl}/runs` 发送 POST。

F-024: `js/src/client.ts` 第2572-2660行定义 `batchIngestRuns({ runCreates?, runUpdates? }, options?)`；方法会预处理 create/update，将同 id 的 create 与 update 合并，并构造 `{ post, patch }` 批量体。

F-025: `js/src/client.ts` 第2662-2699行的 `_postBatchIngestRuns` 向 `${apiUrl}/runs/batch` 发送 POST，请求头包含合并后的 SDK headers、`Content-Type: application/json`、`Accept: application/json`。

F-026: `js/src/client.ts` 第2705行定义 `multipartIngestRuns(...)`，用于多部分批量上传路径。

F-027: `js/src/client.ts` 第3099-3193行定义 `updateRun(runId, run, options?)`；方法首先 `assertUuid(runId)`，分别处理 `inputs`、`outputs`、`error`、`extra.metadata`、`events`；在自动批处理条件满足时将 `{ action: "update", item: data }` 加入队列，否则向 `${apiUrl}/runs/${runId}` 发送 PATCH。

F-028: `js/src/client.ts` 第3136-3152行在根 run 结束、`blockOnRootRunFinalization` 为 true 且非 manual flush 模式时，`updateRun` 会 `await processRunOperation(...)`。

F-029: `js/src/client.ts` 第3196-3207行标记 `readRun(runId, { loadChildRuns }?)` 为 deprecated，并转调 `_readRun`；第3403-3410行标记 `listRuns(props)` 为 deprecated，并转调 `_listRuns`。

F-030: `js/src/client.ts` 第4177行定义 `createProject(...)`；第4379行定义 `getDatasetUrl(...)`；第4550行定义 `createDataset(...)`；第4718行定义异步生成器 `listDatasets(...)`；第4889行定义 `createExample(...)`；第5106行定义异步生成器 `listExamples(...)`；第5497行定义重载 `createFeedback(...)`。

F-031: `js/src/client.ts` 第5822-5834行的 `_selectEvalResults` 将单个 `EvaluationResult`、`EvaluationResult[]` 或 `EvaluationResults` 归一为 `EvaluationResult[]`。

F-032: `js/src/client.ts` 第5836-5879行的 `_logEvaluationFeedback` 遍历评估结果，将 `targetRunId` 或被评估 run 的 id 作为反馈 run id，并调用 `createFeedback(runId_, res.key, { score, value, comment, correction, sourceInfo, sourceRunId, feedbackConfig, feedbackSourceType: "model", sessionId, startTime })`。

F-033: `js/src/client.ts` 第5881-5938行定义公共重载 `logEvaluationFeedback(...)`，支持对象参数形式 `{ evaluatorResponse, run, projectId, sourceInfo? }` 与旧版位置参数形式。

F-034: `js/src/client.ts` 第7979-8014行的 `awaitPendingTraceBatches()` 在 `manualFlushMode` 下输出警告并返回；否则等待 1ms、等待 `_pendingDrains`、等待 `autoBatchQueue.items` 与 `batchIngestCaller.queue.onIdle()`；OTEL 模式下还会调用 span processor 的 `forceFlush()`。

## RunTree

F-035: `js/src/run_trees.ts` 第67-80行定义 `convertToDottedOrderFormat(epoch, runId, executionOrder = 1)`，返回 `{ dottedOrder, microsecondPrecisionDatestring }`，其中 `dottedOrder` 由微秒时间串和 `runId` 拼接。

F-036: `js/src/run_trees.ts` 第82-112行定义 `RunTreeConfig`，字段包含 `name`、`run_type?`、`id?`、`project_name?`、`parent_run?`、`parent_run_id?`、`child_runs?`、`start_time?`、`end_time?`、`extra?`、`metadata?`、`tags?`、`error?`、`serialized?`、`inputs?`、`outputs?`、`reference_example_id?`、`client?`、`tracingEnabled?`、`on_end?`、`execution_order?`、`child_execution_order?`、`trace_id?`、`dotted_order?`、`attachments?`、`replicas?`、`distributedParentId?`。

F-037: `js/src/run_trees.ts` 第160-177行定义 `WriteReplica`，字段包含 `apiUrl?`、`apiKey?`、`workspaceId?`、`projectName?`、`primary?`、`updates?`、`fromEnv?`、`reroot?`、`client?`。

F-038: `js/src/run_trees.ts` 第274-321行声明 `RunTree implements BaseRun`，公开字段包括 `id`、`name`、`run_type`、`project_name`、`parent_run?`、`parent_run_id?`、`child_runs`、`start_time`、`end_time?`、`extra`、`tags?`、`error?`、`serialized`、`inputs`、`outputs?`、`reference_example_id?`、`client`、`events?`、`trace_id`、`dotted_order`、`tracingEnabled?`、`execution_order`、`child_execution_order`、`attachments?`、`replicas?`、`distributedParentId?`。

F-039: `js/src/run_trees.ts` 第323-381行的构造函数在传入 RunTree 时进行浅拷贝；否则合并默认配置，合并 `metadata` 与 `extra.metadata`，选择 `config.client ?? RunTree.getSharedClient()`；无 `id` 时用 `uuid7FromTime(...)` 生成，无 `trace_id` 时继承 `parent_run.trace_id ?? this.id`，无 `dotted_order` 时由 `convertToDottedOrderFormat(...)` 生成并拼接父节点的 `dotted_order`。

F-040: `js/src/run_trees.ts` 第397-411行的 `getDefaultConfig()` 返回默认 `run_type: "chain"`、`project_name: getDefaultProjectName()`、`child_runs: []`、`start_time: Date.now()`、`serialized: {}`、`inputs: {}`、`extra: {}`。

F-041: `js/src/run_trees.ts` 第414-419行的静态方法 `getSharedClient()` 在 `sharedClient` 为空时创建 `new Client()`。

F-042: `js/src/run_trees.ts` 第421-504行定义 `createChild(config)`；子节点 `execution_order` 与 `child_execution_order` 为父节点 `child_execution_order + 1`，继承父节点的 `project_name`、client、`tracingEnabled` 与去除 `reroot` 的 replicas，合并父节点 metadata，并在最后 `this.child_runs.push(child)`。

F-043: `js/src/run_trees.ts` 第508-522行定义 `end(outputs?, error?, endTime = Date.now(), metadata?)`；该方法只在字段尚未设置时写入 `outputs`、`error`、`end_time`，并合并传入 metadata。

F-044: `js/src/run_trees.ts` 第524-574行的 `_convertToCreate(run, runtimeEnv, excludeChildRuns = true)` 返回 `RunCreate & { id: string }`，字段包含 `session_name: run.project_name`、`parent_run_id: run.parent_run?.id ?? run.parent_run_id`、`trace_id`、`dotted_order`、`tags`、`attachments`、`events`。

F-045: `js/src/run_trees.ts` 第805-862行定义 `postRun(excludeChildRuns = true)`；有 replicas 时为每个 replica 调用 `_remapForProject(...)` 并通过目标 client 的 `createRun(...)` 发送，否则调用 `_convertToCreate(...)` 后 `this.client.createRun(runCreate)`；最后清空 `this.child_runs`。

F-046: `js/src/run_trees.ts` 第876-964行定义 `patchRun(options?)`；默认 `excludeInputs` 来自 `getExcludeInputsOnPatch()`；有 replicas 时对每个 replica 构造 `RunUpdate` 并调用目标 client 的 `updateRun(...)`，否则构造本 run 的 `RunUpdate` 并调用 `this.client.updateRun(this.id, runUpdate)`；最后清空 `this.child_runs`。

F-047: `js/src/run_trees.ts` 第966-968行 `toJSON()` 返回 `this._convertToCreate(this, undefined, false)`；第974行定义 `addEvent(event: RunEvent | string): void`；第1122行定义类型守卫 `isRunTree(x?)`。

## traceable

F-048: `js/src/traceable.ts` 第611-625行定义 `ProcessInputs<Args>` 与 `ProcessOutputs<ReturnValue>`：零参数为 `Record<string, never>`，单对象参数保留为对象，单非对象参数包装为 `{ input: Input }`，多参数包装为 `{ args: Args }`；返回值为非对象时包装为 `{ outputs: ReturnValue }`。

F-049: `js/src/traceable.ts` 第628-698行定义 `TraceableConfig<Func>`，它是 `Partial<Omit<RunTreeConfig, "inputs" | "outputs">>`，并增加 `aggregator?`、`argsConfigPath?`、`tracer?`、`on_start?`、`__finalTracedIteratorKey?`、`__deferredSerializableArgOptions?`、`extractAttachments?`、`getInvocationParams?`、`processInputs?`、`processOutputs?`。

F-050: `js/src/traceable.ts` 第715-718行定义 `traceable<Func>(wrappedFunc: Func, config?: TraceableConfig<Func>)`。

F-051: `js/src/traceable.ts` 第736-738行的包装函数参数类型为 `Parameters<Func> | [RunTree, ...Parameters<Func>] | [RunnableConfigLike, ...Parameters<Func>]`。

F-052: `js/src/traceable.ts` 第742-760行处理 `argsConfigPath`：当配置指定参数位置且无 path 时会从参数中弹出 runtime config；指定 path 时会从对象参数中提取该字段作为 runtime config 并写回剩余对象。

F-053: `js/src/traceable.ts` 第824-862行按顺序识别第一参数：`RunnableConfigLike` 走 `RunTree.fromRunnableConfig(...)`；带 `callbackManager` 的 RunTree 直接作为上下文；`ROOT` 或普通 RunTree 分别创建新根或调用 `firstArg.createChild(ensuredConfig)`；然后调用 `getTracingRunTree(...)`。

F-054: `js/src/traceable.ts` 第866-903行在 ALS 中存在父 RunTree 时，向父节点的 `_LC_CHILD_RUN_END_PROMISES_KEY` 推入 `runEndedPromise`，调用 `prevRunFromStore.createChild(ensuredConfig)`，并通过 `getTracingRunTree(...)` 得到当前 run。

F-055: `js/src/traceable.ts` 第910-925行在父上下文不是 RunTree 但带有 `tracingEnabled` 时，将该设置传播给子配置。

F-056: `js/src/traceable.ts` 第947-950行在非 deferred inputs 情况下调用 `currentRunTree?.postRun()` 启动 run 创建。

F-057: `js/src/traceable.ts` 第964-1021行的 `tapReadableStreamForTracing` 包装 `ReadableStream`，在每个 chunk 到达时，当 `currentRunTree.run_type === "llm"` 添加 `{ name: "new_token", kwargs: { token: result.value } }` 事件，并在流结束时调用 `handleRunOutputs(...)`。

F-058: `js/src/traceable.ts` 第1023-1074行的异步迭代器包装逻辑在 chunk 到达时为 llm run 添加 `new_token` 事件，发生错误时 `end(undefined, String(e))`，取消或未完成时 `end(undefined, "Cancelled")`，最后调用 `handleRunOutputs(...)`。

F-059: `js/src/traceable.ts` 第1108-1142行在返回值是 `AsyncIterable` 或对象内 `__finalTracedIteratorKey` 指向 `AsyncIterable` 时，使用 `AsyncLocalStorage.snapshot()` 并包装异步迭代器。

F-060: `js/src/traceable.ts` 第1168-1201行对 generator 返回 iterator-like 的情况收集所有 chunks，调用 `handleRunOutputs(...)` 后返回保留原始 done/value 行为的生成器。

F-061: `js/src/traceable.ts` 第1236-1243行返回 `new Proxy(returnValue, ...)`，当访问 Promise 方法时将其绑定到内部 `tracedPromise`，其他属性走原始对象。

F-062: `js/src/traceable.ts` 第1256-1260行在返回函数上定义属性 `langsmith:traceable`，属性值为 `runTreeConfig`，并将函数断言为 `TraceableFunction<Func>`。

F-063: `js/src/traceable.ts` 第1263-1268行从 `./singletons/traceable.js` 重新导出 `getCurrentRunTree`、`isTraceableFunction`、`withRunTree`、`ROOT`；第1270行重新导出类型 `RunTreeLike`、`TraceableFunction`。

## singletons/traceable

F-064: `js/src/singletons/traceable.ts` 第4-11行定义 `AsyncLocalStorageInterface`，包含 `getStore()` 与 `run(context, fn)`；第13-21行定义 `MockAsyncLocalStorage`，其 `getStore()` 返回 `undefined`，`run()` 直接执行回调。

F-065: `js/src/singletons/traceable.ts` 第23行定义 `TRACING_ALS_KEY = Symbol.for("ls:tracing_async_local_storage")`；第27-40行定义 `AsyncLocalStorageProvider`，从 `globalThis[TRACING_ALS_KEY]` 读取实例，不存在时返回 mock；第42-43行导出单例 `AsyncLocalStorageProviderSingleton`。

F-066: `js/src/singletons/traceable.ts` 第59-68行定义 `getCurrentRunTree(permitAbsentRunTree = false)`；未允许缺失且 store 为 undefined 时抛出 `Could not get the current run tree...` 错误。

F-067: `js/src/singletons/traceable.ts` 第71-82行定义 `withRunTree<Fn>(runTree, fn)`，返回 Promise，并在 ALS 的 `run(runTree, ...)` 中执行 `fn()`。

F-068: `js/src/singletons/traceable.ts` 第84行导出 `ROOT = Symbol.for("langsmith:traceable:root")`；第86-91行定义 `isTraceableFunction(x)`，当 `typeof x === "function"` 且 `"langsmith:traceable" in x` 时返回 true。

## evaluation

F-069: `js/src/evaluation/evaluator.ts` 第15-24行定义 `Category`；第29-72行定义 `EvaluationResult`，字段包含 `key`、`score?`、`value?`、`comment?`、`correction?`、`evaluatorInfo?`、`sourceRunId?`、`targetRunId?`、`feedbackConfig?`；第78-83行定义 `EvaluationResults = { results: Array<EvaluationResult> }`。

F-070: `js/src/evaluation/evaluator.ts` 第85-91行定义接口 `RunEvaluator`，包含 `evaluateRun(run, example?, options?): Promise<EvaluationResult | EvaluationResults>`。

F-071: `js/src/evaluation/evaluator.ts` 第93-123行定义 `RunEvaluatorLike`，支持旧版 `(run, example?)` 形式与对象参数 `{ run, example, inputs, outputs, referenceOutputs }` 形式，可同步或异步返回单个结果、结果数组或批量结果。

F-072: `js/src/evaluation/evaluator.ts` 第128-271行定义 `DynamicRunEvaluator<Func> implements RunEvaluator`；构造函数将传入 evaluator 包装为读取 `input.langSmithRunAndExample` 的函数，并向原函数传入 `{ ...run, run, example, inputs: example?.inputs, outputs: run?.outputs, referenceOutputs: example?.outputs, attachments: example?.attachments }`。

F-073: `js/src/evaluation/evaluator.ts` 第212-270行的 `evaluateRun` 生成 `sourceRunId = uuidv7()`，构造 metadata `{ targetRunId: run.id, experiment?: run.session_id }`，用 `traceable(this.func, { project_name: "evaluators", name: "evaluator", on_end, ...options })` 包装评估函数，调用后将数组结果归一为 `{ results }`，将缺少 key 的对象补充为函数名或返回带 key 的结果。

F-074: `js/src/evaluation/evaluator.ts` 第273-275行导出 `runEvaluator(func): RunEvaluator`，函数体返回 `new DynamicRunEvaluator(func)`。

F-075: `js/src/evaluation/string_evaluator.ts` 第4-26行定义 `GradingFunctionResult`、`GradingFunctionParams`、`StringEvaluatorParams`；grading 函数接收 `{ input, prediction, answer? }`。

F-076: `js/src/evaluation/string_evaluator.ts` 第28-68行定义 `StringEvaluator implements RunEvaluator`；默认 `inputKey = "input"`、`predictionKey = "output"`、`answerKey = "output"`；`evaluateRun` 在 `run.outputs` 为空时抛出错误，从 `run.inputs[this.inputKey]`、`run.outputs[this.predictionKey]`、`example?.outputs?.[this.answerKey]` 取值，调用 grading function 后返回 `{ key, score, value, comment, correction }`。

F-077: `js/src/evaluation/_runner.ts` 第36-49行定义标准 target 类型：接收 `(input, config?)` 的函数或带 `invoke(input, config?)` 的对象；比较评估 target 类型为字符串数组或 `ExperimentResults` Promise/对象数组。

F-078: `js/src/evaluation/_runner.ts` 第52行定义 `DataT = string | AsyncIterable<Example> | Example[]`。

F-079: `js/src/evaluation/_runner.ts` 第68-84行定义 `SummaryEvaluatorT`；第102-121行定义 `EvaluatorT`，其中新形式接收 `{ run, example, inputs, outputs, referenceOutputs?, attachments? }`。

F-080: `js/src/evaluation/_runner.ts` 第184-217行定义 `EvaluateOptions`，包含 `targetConcurrency?`、`evaluationConcurrency?`、`evaluators?`、`summaryEvaluators?`、`data`、`includeAttachments?`，并继承 `metadata?`、`experimentPrefix?`、`description?`、`maxConcurrency?`、`client?`、`numRepetitions?`。

F-081: `js/src/evaluation/_runner.ts` 第237-253行定义 `evaluate` 的比较评估重载、标准评估重载和实现签名；实现函数返回 `_evaluate(target, options)`。

F-082: `js/src/evaluation/_runner.ts` 第255-259行定义 `ExperimentResultRow`，包含 `run: Run`、`example: Example`、`evaluationResults: EvaluationResults`。

F-083: `js/src/evaluation/_runner.ts` 第288-434行定义 `_ExperimentManager`；构造函数在未传 experiment 时使用 `randomName()` 生成名称，传字符串时追加 `-` 与 uuid 前 8 位，传对象时要求对象有 `name`；metadata 中在缺少 `revision_id` 时填入 `getLangSmithEnvVarsMetadata().revision_id`；client 缺省为 `new Client()`。

F-084: `js/src/evaluation/_runner.ts` 第526-546行的 `start()` 调用 `getExamples()`、`_getProject(firstExample)`、`_printExperimentStart()`，并返回新的 `_ExperimentManager`。

F-085: `js/src/evaluation/_runner.ts` 第548-584行的 `withPredictions(target, options?)` 调用 `_predict(target, options)`，用 `atee` 分流结果，并返回带 `resultRows` 与 `runs` 异步生成器的新 manager。

F-086: `js/src/evaluation/_runner.ts` 第586-621行的 `withEvaluators(evaluators, options?)` 调用 `_resolveEvaluators(evaluators)` 与 `_score(...)`，用 `atee(..., 3)` 分流为结果行、runs 与评估结果。

F-087: `js/src/evaluation/_runner.ts` 第623-643行的 `withSummaryEvaluators(summaryEvaluators)` 调用 `_applySummaryEvaluators(...)` 并返回带 `summaryResults` 的新 manager。

F-088: `js/src/evaluation/_runner.ts` 第777-824行的 `_runEvaluators` 为每个 evaluator 构造 `{ reference_example_id, project_name: "evaluators", metadata: { example_version }, client, tracingEnabled: true }`，调用 `evaluator.evaluateRun(run, example, options)`，然后通过 `client.logEvaluationFeedback(...)` 将结果写入项目反馈。

F-089: `js/src/evaluation/_runner.ts` 第833-859行的 `_score` 在未提供 queue 时创建 `PQueue`，注释写明 `maxConcurrency: 0 means sequential execution`，但实际 queue 的 concurrency 为 `maxConcurrency === 0 ? 1 : maxConcurrency`。

F-090: `js/src/evaluation/_runner.ts` 第1047-1145行的 `_evaluate` 在 target 为数组时转调 `evaluateComparative(...)`；否则创建或解析 experiment，构造 `_ExperimentManager` 并依次调用 `start()`、`withPredictions(...)`、`withEvaluators(...)`、`withSummaryEvaluators(...)`，最后创建 `ExperimentResults`、调用 `processData(manager)`，并 `await client.awaitPendingTraceBatches()`。

F-091: `js/src/evaluation/_runner.ts` 第1147-1226行的 `_forward` 为 target 设置 `reference_example_id: example.id`、`project_name: experimentName`、metadata 中的 `example_version`、client 与 `tracingEnabled: true`；若 target 已是 traceable 函数则直接使用，若对象有 `invoke` 则包装 `fn.invoke(...)`，否则用 `traceable(fn, defaultOptions)` 包装。

F-092: `js/src/evaluation/index.ts` 第1-17行导出 `RunEvaluator`、`EvaluationResult`、`StringEvaluator`、`GradingFunctionParams`、`GradingFunctionResult`、`evaluate`、`EvaluateOptions`、`TargetT`、`DataT`、`SummaryEvaluatorT`、`EvaluatorT`、`ExperimentResultRow`、`evaluateComparative`。

## anonymizer

F-093: `js/src/anonymizer/index.ts` 第1-4行导出接口 `StringNode`，包含 `value: string` 与 `path: string`。

F-094: `js/src/anonymizer/index.ts` 第15-66行的 `extractStringNodes(data, options)` 使用队列遍历数据；默认 `maxDepth` 为 10；字符串节点记录 `value`、`path`、`parent`、`key` 与递增 `_id`；数组路径形如 `${path}[${i}]`，对象路径形如 `${path}.${k}`。

F-095: `js/src/anonymizer/index.ts` 第68-70行的 `deepClone<T>(data): T` 实现为 `JSON.parse(JSON.stringify(data))`。

F-096: `js/src/anonymizer/index.ts` 第72-80行导出 `StringNodeProcessor` 与 `StringNodeRule`；规则包含可选 `type?: "pattern"`、`pattern: RegExp | string`、`replace?: string`。

F-097: `js/src/anonymizer/index.ts` 第82-85行导出 `ReplacerType = ((value, path?) => string) | StringNodeRule[] | StringNodeProcessor`。

F-098: `js/src/anonymizer/index.ts` 第87-174行导出 `createAnonymizer(replacer, options?)`；返回的函数先深拷贝输入，提取字符串节点，将函数、规则数组或 processor 归一为 `StringNodeProcessor`，调用 `maskNodes(nodes)` 后按 `_id` 或 path 回写变更；根路径为空字符串时直接替换整个值。

F-099: `js/src/anonymizer/index.ts` 第180行导出 `SECRET_PLACEHOLDER = "[SECRET_DETECTED]"`；第199-299行导出 `DEFAULT_SECRET_RULES: StringNodeRule[]`，包含 Anthropic、OpenAI、LangSmith、GitHub、GitLab、AWS、Google、Slack、Stripe、npm、PyPI、SendGrid、JWT、PEM 私钥、结构化 key/value、Authorization header、Bearer token、URL 凭据等规则。

F-100: `js/src/anonymizer/index.ts` 第319-325行导出 `createSecretAnonymizer(options?)`；它将 `options?.extraRules ?? []` 追加到 `DEFAULT_SECRET_RULES`，并以 `{ maxDepth: options?.maxDepth ?? 24 }` 调用 `createAnonymizer(rules, ...)`。
