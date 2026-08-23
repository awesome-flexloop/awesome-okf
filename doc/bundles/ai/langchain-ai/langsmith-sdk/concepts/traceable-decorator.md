---
type: concept
title: traceable 自动追踪装饰器
description: traceable 如何解析 RunTree 上下文、归一输入输出、包装 Promise/Stream/AsyncIterable 并挂载追踪元数据。
tags: [langsmith, traceable, async-context, streaming]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-23T00:00:00+08:00" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-23T00:00:00+08:00" }
status: stable
stale_after: 2027-08-23
sources:
  - id: source-core
    resource: /references/source-core.md
    title: langsmith-sdk JS 核心源码索引
---

# traceable 自动追踪装饰器

`traceable()` 是一个高阶函数。它接收普通函数和 `TraceableConfig`，返回带 `langsmith:traceable` 属性的 `TraceableFunction`。返回函数执行时会自动创建 RunTree、上报 run start、等待返回值完成、再上报 outputs 或 error。

## 配置结构

`TraceableConfig<Func>` 以 `RunTreeConfig` 为基础，但去掉了 `inputs` 和 `outputs`，并增加追踪钩子：

| 配置 | 作用 |
|---|---|
| `name` | run 名称；未传时使用函数名，匿名函数为 `<lambda>` |
| `run_type` | run 类型，默认来自 RunTree 的 `chain` |
| `client` | 指定 `Client`，否则使用 RunTree shared client |
| `project_name` | LangSmith 项目名 |
| `tags`、`metadata` | 标签和元数据 |
| `processInputs` | 上报前转换输入 |
| `processOutputs` | 上报前转换输出 |
| `aggregator` | 聚合 stream/iterator chunks |
| `extractAttachments` | 从参数中提取附件 |
| `getInvocationParams` | 提取模型名、temperature 等调用参数 |
| `on_start`、`on_end` | run 开始/结束回调 |
| `argsConfigPath` | 从函数参数中提取运行时配置 |
| `tracer` | OTEL tracer |

输入输出类型有统一归一规则：无参数记录为空对象；单个对象直接记录；单个非对象包装为 `{ input: value }`；多个参数包装为 `{ args: [...] }`；非对象返回值包装为 `{ outputs: value }`。

## 上下文解析顺序

包装函数的第一个参数可以参与上下文选择：

1. 如果第一个参数类似 LangChain 的 `RunnableConfigLike`，则通过 `RunTree.fromRunnableConfig(...)` 接入 LangChain 上下文。
2. 如果第一个参数是带 `callbackManager` 的旧式 RunTree，则直接使用该 run tree。
3. 如果第一个参数是 `ROOT`，则创建新的根 RunTree。
4. 如果第一个参数是普通 RunTree，则调用 `firstArg.createChild(ensuredConfig)` 创建子 run。
5. 否则读取 ALS 中的当前 RunTree；存在父 RunTree 时创建子节点，不存在时创建新的根节点。
6. 如果父上下文显式关闭 tracing，且子配置没有覆盖，则把 `tracingEnabled: false` 传播给子 run。

上下文本体由 `AsyncLocalStorageProviderSingleton` 管理。浏览器或不支持 ALS 的环境会回退到 mock 实现，mock 的 `getStore()` 返回 `undefined`，`run()` 只直接执行回调。

## 生命周期

```text
调用 traceable function
  │
  ├─ 提取 runtime config
  ├─ 序列化可序列化参数
  ├─ 解析 currentContext / rawInputs
  ├─ 调用 on_start(currentRunTree)
  ├─ currentRunTree.postRun()
  ├─ 执行 wrappedFunc(...rawInputs)
  ├─ Promise resolve / stream done / iterator return / error
  ├─ currentRunTree.end(...)
  ├─ handleRunOutputs(...)
  └─ currentRunTree.patchRun()
```

`postRun()` 在函数体执行前启动。对于普通 Promise，SDK 会在 `then` 中处理 outputs；对于同步抛出的错误，会把错误转为 rejected Promise 并进入错误分支。

## Promise 与流式返回值

返回值处理分多条路径：

- 普通 Promise：在 resolve 后处理 outputs，在 reject 时调用 `currentRunTree.end(undefined, String(error))`。
- `ReadableStream`：包装 stream，逐个 chunk 透传；当 run 类型为 `llm` 时添加 `new_token` 事件；流结束后聚合 chunks 并 patch outputs。
- `AsyncIterable`：包装异步迭代器，保留 cancel/return 清理逻辑，异常或取消时写入 error。
- 同步 iterator/generator：收集所有 iterator result，聚合 outputs，再返回原始迭代结果。
- 对象上的 `__finalTracedIteratorKey`：只包装该字段指向的异步可迭代对象，其他字段原样返回。

为了同时保留“对象方法”和“Promise 方法”，SDK 在对象返回值外创建 Proxy：访问 `then`、`catch`、`finally` 时委托给内部 `tracedPromise`，访问其他字段时走原始对象。

## 运行时配置与显式上下文

`argsConfigPath` 支持两种写法：

- `[index]`：把最后一个或指定位置的对象参数作为 runtime config 并移除。
- `[index, "path"]`：从对象参数中取出某个字段作为 runtime config，剩余对象继续传给原函数。

也可以直接把 RunTree 作为第一个参数传入：

```ts
import { RunTree } from "langsmith";
import { traceable } from "langsmith/traceable";

const child = traceable(async (value: string) => value.toUpperCase(), {
  name: "child",
});

const parent = new RunTree({ name: "parent" });
await child(parent, "hello");
await parent.patchRun();
```

`ROOT` 用于强制开启新的根 trace，`withRunTree(runTree, fn)` 用于在回调中临时设置 ALS 上下文，`getCurrentRunTree()` 用于在 traceable 函数内部读取当前 run。

## 与 Client 的关系

`traceable` 本身不直接发送 HTTP 请求。它通过 `RunTree.postRun()` 和 `RunTree.patchRun()` 间接调用 `Client.createRun()`、`Client.updateRun()`。因此：

- 设置 `client` 可以把某个 trace 发到不同 endpoint 或项目。
- `processInputs`、`processOutputs` 与 client 侧 anonymizer 都会影响最终 payload。
- 函数返回后应等待 `client.awaitPendingTraceBatches()`，否则短进程可能在后台批处理发送前退出。

## 相关概念

- [SDK 总览](/ai/langchain-ai/langsmith-sdk/concepts/overview.md)
- [RunTree 追踪模型](/ai/langchain-ai/langsmith-sdk/concepts/run-tree-tracing.md)
- [评测运行器](/ai/langchain-ai/langsmith-sdk/concepts/evaluation.md)
- [快速追踪与评测示例](/ai/langchain-ai/langsmith-sdk/examples/quickstart-trace-and-evaluate.md)
