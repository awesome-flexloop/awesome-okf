---
title: 批量处理
type: concept
bundle: /pocketflow/pocketflow-core
related:
  - /pocketflow/pocketflow-core/references/batch-node
  - /pocketflow/pocketflow-core/references/batch-flow
  - /pocketflow/pocketflow-core/concepts/node-lifecycle
---

# 批量处理

PocketFlow 提供两种批量处理机制：**BatchNode**（单节点内批量）和 **BatchFlow**（子流程级批量），分别对应 MapReduce 中的 Map 步骤和参数化流程执行。

## BatchNode：单节点批量

BatchNode 在单个节点内对一组 items 逐个执行 exec，适合简单的数据转换场景。

```
prep(shared) → [item1, item2, item3, ...]
                ├─ exec(item1) → res1
                ├─ exec(item2) → res2
                └─ exec(item3) → res3
post(shared, prep_res, [res1, res2, res3, ...])
```

### 典型用法：MapReduce

```python
class MapChunks(BatchNode):
    """Map阶段：将大数组分块求和"""
    def prep(self, shared):
        arr = shared["array"]
        chunk_size = 10
        return [arr[i:i+chunk_size] for i in range(0, len(arr), chunk_size)]

    def exec(self, chunk):
        return sum(chunk)

    def post(self, shared, prep_res, exec_res):
        shared["chunk_sums"] = exec_res

class ReduceNode(Node):
    """Reduce阶段：汇总结果"""
    def prep(self, shared):
        return shared["chunk_sums"]

    def exec(self, chunk_sums):
        return sum(chunk_sums)

    def post(self, shared, prep_res, exec_res):
        shared["total"] = exec_res

map_node >> reduce_node
flow = Flow(start=map_node)
flow.run({"array": list(range(100))})
# shared["total"] = 4950
```

## BatchFlow：子流程级批量

BatchFlow 对整个子流程执行多次，每次使用不同的参数集。适合需要多个步骤协作的批量处理。

```
prep(shared) → [params1, params2, params3, ...]
              ├─ Flow._orch(shared, params1)  → 子流程完整执行一次
              ├─ Flow._orch(shared, params2)  → 子流程完整执行一次
              └─ Flow._orch(shared, params3)  → 子流程完整执行一次
```

### 典型用法：多Key处理

```python
class ProcessKeyBatchFlow(BatchFlow):
    def prep(self, shared):
        return [{"key": k} for k in shared["data"].keys()]

class FetchNode(Node):
    def prep(self, shared):
        key = self.params.get("key")
        return shared["data"][key]

    def exec(self, value):
        return value * 2

    def post(self, shared, prep_res, exec_res):
        key = self.params.get("key")
        if "results" not in shared:
            shared["results"] = {}
        shared["results"][key] = exec_res

fetch = FetchNode()
batch_flow = ProcessKeyBatchFlow(start=fetch)
batch_flow.run({"data": {"a": 1, "b": 2, "c": 3}})
# shared["results"] = {"a": 2, "b": 4, "c": 6}
```

### 多参数传递

BatchFlow 的 prep 可以返回包含多个键的参数字典：

```python
class MultiParamBatchFlow(BatchFlow):
    def prep(self, shared):
        return [
            {"key": k, "multiplier": i + 1}
            for i, k in enumerate(shared["data"].keys())
        ]

class ProcessNode(Node):
    def exec(self, prep_res):
        key = self.params.get("key")
        mult = self.params.get("multiplier", 1)
        return shared["data"][key] * mult
```

## 嵌套批量

BatchFlow 可以嵌套，实现分层批量处理：

```python
class InnerBatchFlow(BatchFlow):
    """内层：处理一个group内的所有items"""
    def prep(self, shared):
        group = self.params["group"]
        return [{"item": i, "group": group} for i in range(len(shared["groups"][group]))]

class OuterBatchFlow(BatchFlow):
    """外层：遍历所有groups"""
    def prep(self, shared):
        return [{"group": g} for g in shared["groups"]]
```

## BatchNode vs BatchFlow 选择指南

| 场景 | 选择 |
|------|------|
| 单步数据转换（每项处理逻辑相同） | BatchNode |
| MapReduce 的 Map 阶段 | BatchNode |
| 多项需要经过相同的多步处理流程 | BatchFlow |
| 每项处理需要条件分支/循环 | BatchFlow |
| 分层批量（分组+分组内项） | 嵌套 BatchFlow |
| 需要并行执行 | AsyncParallelBatchFlow |

## 与异步结合

异步版本提供并行批量能力：
- `AsyncBatchNode`：串行异步批量
- `AsyncParallelBatchNode`：并行异步批量（asyncio.gather）
- `AsyncBatchFlow`：串行异步批量流程
- `AsyncParallelBatchFlow`：并行异步批量流程
