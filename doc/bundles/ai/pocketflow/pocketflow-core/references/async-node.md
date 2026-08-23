---
title: AsyncNode 与异步类族
type: reference
source: pocketflow/__init__.py
bundle: /pocketflow/pocketflow-core
related:
  - /pocketflow/pocketflow-core/references/node
  - /pocketflow/pocketflow-core/concepts/async-parallel
---

# AsyncNode 与异步类族

PocketFlow 提供完整的异步节点和流程体系，类名以 `Async` 为前缀，使用 `async/await` 语法，支持 I/O 密集型任务的高效执行。

## AsyncNode

`AsyncNode` 继承自 [Node](node.md)，将生命周期方法改为异步版本。

### 异步核心方法

| 同步方法 | 异步方法 | 说明 |
|---------|---------|------|
| `prep(shared)` | `prep_async(shared)` | 异步前处理 |
| `exec(prep_res)` | `exec_async(prep_res)` | 异步核心执行 |
| `post(shared, prep_res, exec_res)` | `post_async(shared, prep_res, exec_res)` | 异步后处理 |
| `exec_fallback(prep_res, exc)` | `exec_fallback_async(prep_res, exc)` | 异步降级 |

### 方法签名

```python
class AsyncNode(Node):
    async def prep_async(self, shared): ...
    async def exec_async(self, prep_res): ...
    async def post_async(self, shared, prep_res, exec_res): ...
    async def exec_fallback_async(self, prep_res, exc): ...
```

### 运行方式

```python
# 异步方式
result = await node.run_async(shared)

# 同步方式（内部使用 asyncio.run）
result = node.run(shared)
```

### 重试机制

`_exec_async` 实现异步重试循环，逻辑与 Node._exec 相同但使用 await：

```python
async def _exec_async(self, prep_res):
    for _ in range(self.max_retries):
        try:
            return await self.exec_async(prep_res)
        except Exception as e:
            exc = e
    if hasattr(self, 'exec_fallback_async'):
        return await self.exec_fallback_async(prep_res, exc)
    raise exc
```

## AsyncBatchNode

继承自 `AsyncNode`，异步串行批量处理。`_exec_async` 依次 await 每个 item 的 `exec_async`：

```python
async def _exec_async(self, items):
    results = []
    for item in items:
        results.append(await self.exec_async(item))
    return results
```

适用于批量项之间有顺序依赖或需要控制并发数的场景。

## AsyncParallelBatchNode

继承自 `AsyncNode`，**异步并行批量处理**。`_exec_async` 使用 `asyncio.gather` 并行执行所有 item：

```python
async def _exec_async(self, items):
    tasks = [self.exec_async(item) for item in items]
    return await asyncio.gather(*tasks)
```

关键特性：
- 所有 item 的 exec_async 同时启动
- 结果列表顺序与输入顺序一致
- 总耗时约等于单个最慢 item 的耗时
- 任意 item 抛出异常时，gather 会立即传播该异常（除非使用 return_exceptions）

## AsyncFlow

继承自 `AsyncNode`，异步版本的 [Flow](flow.md)。`_orch_async` 使用 await 驱动节点流转：

```python
async def _orch_async(self, shared, params=None):
    curr = copy.copy(self.start_node)
    p = params or {**self.params}
    last_action = None
    while curr:
        curr.set_params(p)
        if hasattr(curr, '_run_async'):
            last_action = await curr._run_async(shared)
        else:
            last_action = curr._run(shared)
        curr = copy.copy(self.get_next_node(curr, last_action))
    return last_action
```

AsyncFlow 可以混合编排 AsyncNode 和普通 Node：异步节点调用 `_run_async`，同步节点调用 `_run`。

## AsyncBatchFlow

继承自 `AsyncFlow`，异步串行批量流程。`prep_async` 返回参数列表，依次 await 每个子流程。

## AsyncParallelBatchFlow

继承自 `AsyncFlow`，异步并行批量流程。使用 `asyncio.gather` 并行运行多个子流程实例，每个实例使用不同的 params。

## 异步类族速查表

| 类名 | 继承 | 批量方式 | 并行度 | 典型场景 |
|------|------|---------|-------|---------|
| AsyncNode | Node | 单条 | - | 单次异步 I/O 操作 |
| AsyncBatchNode | AsyncNode | 串行批量 | 1 | 顺序处理多项 |
| AsyncParallelBatchNode | AsyncNode | 并行批量 | N | 并发 API 调用 |
| AsyncFlow | AsyncNode | 单流程 | - | 多步异步编排 |
| AsyncBatchFlow | AsyncFlow | 串行批量流程 | 1 | 多数据集串行跑同一流程 |
| AsyncParallelBatchFlow | AsyncFlow | 并行批量流程 | N | 多数据集并发跑同一流程 |

## 源码位置

[pocketflow/\_\_init\_\_.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow/pocketflow/__init__.py)
