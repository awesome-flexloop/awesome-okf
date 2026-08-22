---
title: Node
type: reference
source: pocketflow/__init__.py
bundle: /pocketflow/pocketflow-core
related:
  - /pocketflow/pocketflow-core/references/base-node
  - /pocketflow/pocketflow-core/references/batch-node
  - /pocketflow/pocketflow-core/concepts/node-lifecycle
---

# Node

`Node` 继承自 [BaseNode](base-node.md)，是同步节点的主要实现类，在 BaseNode 基础上增加了**重试**和**降级（fallback）**机制。

## 构造函数

```python
Node(max_retries: int = 1)
```

- `max_retries`：最大执行尝试次数，默认 1（不重试）。设置为 N 表示最多尝试 N 次。

## 核心方法

Node 继承了 BaseNode 的 `prep`、`exec`、`post` 三个生命周期方法，子类需重写这些方法实现业务逻辑。

### `exec_fallback(prep_res: Any, exc: Exception) -> Any`

**可选的降级方法**。当 `exec` 在 `max_retries` 次尝试后仍然失败（抛出异常），框架会调用此方法。

- 参数：
  - `prep_res` — prep 的返回值
  - `exc` — 最后一次 exec 抛出的异常对象
- 返回：降级结果，传递给 post 作为 `exec_res`

如果不重写此方法，重试耗尽后异常会直接向上抛出。

```python
class MyNode(Node):
    def exec(self, prep_res):
        result = call_api()  # 可能失败
        return result

    def exec_fallback(self, prep_res, exc):
        return {"error": str(exc), "fallback": True}
```

## 内部方法

### `_exec(prep_res: Any) -> Any`

重写自 BaseNode，实现重试循环：

```python
def _exec(self, prep_res):
    for _ in range(self.max_retries):
        try:
            return self.exec(prep_res)
        except Exception as e:
            exc = e
    if hasattr(self, 'exec_fallback'):
        return self.exec_fallback(prep_res, exc)
    raise exc
```

执行逻辑：
1. 最多尝试 `max_retries` 次调用 `exec`
2. 若某次 exec 成功，直接返回结果
3. 若全部失败，检查是否有 `exec_fallback` 方法
4. 有 fallback 则调用它返回降级结果；否则抛出最后一个异常

## 生命周期调用顺序

```
run(shared)
  └─ _run(shared)
       ├─ prep(shared) → prep_res
       ├─ _exec(prep_res)  [含重试循环]
       │    └─ exec(prep_res) → exec_res (成功) 或抛出异常
       │         └─ [重试 max_retries-1 次]
       │              └─ exec_fallback(prep_res, exc) → fallback_res (可选)
       └─ post(shared, prep_res, exec_res_or_fallback_res) → action
```

## 使用示例

```python
from pocketflow import Node, Flow

class ProcessData(Node):
    def prep(self, shared):
        return shared.get("input_data", [])

    def exec(self, items):
        return [x * 2 for x in items]

    def post(self, shared, prep_res, exec_res):
        shared["output"] = exec_res

node = ProcessData(max_retries=3)
shared = {"input_data": [1, 2, 3]}
action = node.run(shared)
# shared["output"] = [2, 4, 6]
```

## 注意事项

- Node 的 `exec` 方法是同步的，不支持 async/await。异步场景使用 [AsyncNode](async-node.md)。
- `max_retries=1` 表示只执行一次，不重试；`max_retries=3` 表示最多尝试 3 次（初始 + 2 次重试）。
- `exec_fallback` 只在重试全部失败后调用，不是每次失败都调用。

## 源码位置

[pocketflow/\_\_init\_\_.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow/pocketflow/__init__.py)
