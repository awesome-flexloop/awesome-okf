---
title: 异步与并行
type: concept
bundle: /pocketflow/pocketflow-core
related:
  - /pocketflow/pocketflow-core/references/async-node
  - /pocketflow/pocketflow-core/concepts/node-lifecycle
  - /pocketflow/pocketflow-core/concepts/batch-processing
---

# 异步与并行

PocketFlow 的异步体系基于 Python `asyncio`，提供 AsyncNode、AsyncFlow 及并行批量处理能力，适合 I/O 密集型场景（如并发 LLM 调用、API 请求）。

## 异步节点三阶段

AsyncNode 将生命周期方法改为 `async`：

```python
class MyAsyncNode(AsyncNode):
    async def prep_async(self, shared):
        # 异步读取准备
        data = await load_data_async()
        return data

    async def exec_async(self, prep_res):
        # 异步核心执行
        result = await llm_call_async(prep_res)
        return result

    async def post_async(self, shared, prep_res, exec_res):
        # 异步写入
        await save_result_async(exec_res)
        shared["output"] = exec_res
        return "default"
```

运行方式：

```python
# 方式一：异步上下文使用 run_async
result = await node.run_async(shared)

# 方式二：同步上下文使用 run（内部 asyncio.run）
result = node.run(shared)
```

## AsyncFlow：异步流程编排

AsyncFlow 可以混合编排 AsyncNode 和普通 Node：

```python
flow = AsyncFlow(start=async_node1)
async_node1 - "done" >> sync_node
sync_node >> async_node2
```

在 `_orch_async` 中，框架检测节点是否有 `_run_async` 方法：
- AsyncNode → `await node._run_async(shared)`
- 普通 Node → `node._run(shared)`（同步执行）

## 并行批量：AsyncParallelBatchNode

使用 `asyncio.gather` 并行执行所有 item 的 exec_async：

```python
class ParallelFetch(AsyncParallelBatchNode):
    async def prep_async(self, shared):
        return shared["urls"]  # 返回URL列表

    async def exec_async(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()

    async def post_async(self, shared, prep_res, exec_res):
        shared["responses"] = exec_res
```

**关键特性**：
- 所有 URL 同时发起请求，总耗时 ≈ 最慢单个请求时间
- 结果列表顺序与输入 URL 顺序一致
- 任意请求失败，异常立即传播（gather 默认行为）

性能对比测试结果（5个任务，每个0.1s延迟）：
- 串行：~0.5s
- 并行：~0.1s（含开销 < 0.2s）

## AsyncParallelBatchFlow：并行子流程

整个子流程的多个实例并行运行：

```python
class MyParallelBatchFlow(AsyncParallelBatchFlow):
    async def prep_async(self, shared):
        return [{"id": i} for i in range(10)]

# 每个 id 独立运行完整子流程，10个实例并行
```

## 异步类选择决策树

```
需要异步处理？
├─ 否 → 使用 Node / Flow / BatchNode / BatchFlow
└─ 是
    ├─ 单条处理 → AsyncNode
    ├─ 多项处理
    │   ├─ 需要顺序执行 → AsyncBatchNode
    │   └─ 可并行执行 → AsyncParallelBatchNode
    ├─ 多步编排 → AsyncFlow
    └─ 多数据集跑同一流程
        ├─ 串行 → AsyncBatchFlow
        └─ 并行 → AsyncParallelBatchFlow
```

## 注意事项

1. **同步方法仍可用**：AsyncNode 可以定义同步的 prep/exec/post（不推荐），框架会优先调用 async 版本
2. **线程安全**：并行批量时，多个 exec_async 同时运行，避免在 exec_async 中修改 shared（post_async 才是安全写入点）
3. **异常处理**：并行执行时，一个 item 失败会导致整个 gather 失败；如需容错，在 exec_async 内部 try-except
4. **事件循环**：`node.run(shared)` 会创建新的事件循环；在已有异步上下文中使用 `await node.run_async(shared)`
5. **并发控制**：asyncio.gather 无并发限制，如需限制并发数，在 exec_async 中使用 asyncio.Semaphore
