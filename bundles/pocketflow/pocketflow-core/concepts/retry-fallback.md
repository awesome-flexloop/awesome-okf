---
title: 重试与降级
type: concept
bundle: /pocketflow/pocketflow-core
related:
  - /pocketflow/pocketflow-core/references/node
  - /pocketflow/pocketflow-core/concepts/node-lifecycle
---

# 重试与降级

Node 提供内置的重试（Retry）和降级（Fallback）机制，用于处理 exec 阶段可能出现的瞬时错误。

## 重试机制

通过构造函数的 `max_retries` 参数控制最大尝试次数：

```python
node = MyNode(max_retries=3)  # 最多尝试3次
```

### 重试行为

- `max_retries=1`（默认）：只执行1次，不重试
- `max_retries=N`：最多尝试N次，即初始1次 + (N-1)次重试
- 重试仅发生在 `exec()` 抛出异常时
- prep 和 post **不参与重试**，无论重试多少次都只执行一次

### 重试循环逻辑

```python
for attempt in range(max_retries):
    try:
        return exec(prep_res)  # 成功则返回
    except Exception as e:
        last_exception = e
# 全部失败
if has exec_fallback:
    return exec_fallback(prep_res, last_exception)
else:
    raise last_exception
```

## 降级机制

`exec_fallback(self, prep_res, exc)` 是可选方法，在重试全部失败后提供降级结果：

```python
class APICallNode(Node):
    def exec(self, prep_res):
        response = requests.get("https://api.example.com/data", timeout=5)
        response.raise_for_status()
        return response.json()

    def exec_fallback(self, prep_res, exc):
        # 重试全部失败后，返回缓存数据或默认值
        return {"data": [], "source": "fallback", "error": str(exc)}
```

### 降级关键点

- fallback 接收最后一次异常 `exc`，可以根据异常类型做不同处理
- fallback 的返回值替代 exec_res 传给 post
- post 正常执行，不会感知到 fallback 已被触发
- 如果不定义 exec_fallback，重试耗尽后异常直接向上抛出

## 完整示例

```python
from pocketflow import Node, Flow

class FetchData(Node):
    def __init__(self):
        super().__init__(max_retries=3)  # 最多3次尝试
        self.cache = {"default": [1, 2, 3]}

    def prep(self, shared):
        return shared.get("endpoint", "/api/data")

    def exec(self, endpoint):
        # 模拟可能失败的API调用
        import random
        if random.random() < 0.7:
            raise ConnectionError(f"Failed to fetch {endpoint}")
        return [10, 20, 30]

    def exec_fallback(self, prep_res, exc):
        print(f"All retries failed: {exc}, using cache")
        return self.cache["default"]

    def post(self, shared, prep_res, exec_res):
        shared["data"] = exec_res

fetch = FetchData()
flow = Flow(start=fetch)
shared = {}
flow.run(shared)
print(shared["data"])  # API成功则返回实时数据，失败则返回缓存
```

## AsyncNode 的重试与降级

异步节点使用对应的异步方法：

```python
class AsyncFetchNode(AsyncNode):
    def __init__(self):
        super().__init__(max_retries=3)

    async def exec_async(self, prep_res):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()

    async def exec_fallback_async(self, prep_res, exc):
        return {"data": [], "source": "fallback"}
```

行为与同步版完全一致，只是使用 await 语法。

## 使用建议

1. **幂等操作才重试**：确保 exec 是幂等的，重试不会产生副作用
2. **合理设置 max_retries**：通常 2-3 次足够，过多重试会拖慢流程
3. **fallback 提供有意义的降级**：返回空值、缓存数据或错误标记，而非静默失败
4. **在 post 中可以检测 fallback**：如果需要知道是否走了降级，可以在 exec_fallback 中设置标记到 prep_res 或通过 shared 传递
