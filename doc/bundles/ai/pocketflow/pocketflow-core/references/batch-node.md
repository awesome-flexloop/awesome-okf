---
title: BatchNode
type: reference
source: pocketflow/__init__.py
bundle: /pocketflow/pocketflow-core
related:
  - /pocketflow/pocketflow-core/references/node
  - /pocketflow/pocketflow-core/concepts/batch-processing
---

# BatchNode

`BatchNode` 继承自 [Node](node.md)，实现**单节点内的批量处理**（Map 模式）。`prep` 返回待处理项列表，框架自动对每项调用 `exec`，结果收集为列表传给 `post`。

## 核心方法

BatchNode 继承 Node 的 `prep`、`post`、`exec_fallback`，仅重写 `_exec` 方法。

### `exec(item: Any) -> Any`

处理单个项。与 Node.exec 签名相同，但语义不同：
- Node.exec 接收 prep 返回的完整结果
- BatchNode.exec 每次只接收 prep 返回列表中的一个元素

### `prep(shared: dict) -> Iterable[Any]`

返回一个可迭代对象（通常是列表），每个元素作为一次 exec 调用的输入。

### `post(shared: dict, prep_res: Iterable, exec_res: list[Any]) -> str | None`

`exec_res` 是所有 item 的 exec 结果组成的列表（顺序与 prep 返回的列表一致）。

## 内部方法

### `_exec(items: Iterable) -> list[Any]`

```python
def _exec(self, items):
    results = []
    for item in items:
        results.append(self.exec(item))
    return results
```

遍历 items，对每个元素调用 self.exec(item)，收集结果为列表。

## 使用模式

BatchNode 实现 Map 步骤（分治中的"分"），通常配合一个普通 Node 做 Reduce 步骤（"合"）：

```python
class MapChunks(BatchNode):
    def prep(self, shared):
        # 将大数组分成小块
        array = shared["input_array"]
        return [array[i:i+10] for i in range(0, len(array), 10)]

    def exec(self, chunk):
        return sum(chunk)  # 每个块求和

    def post(self, shared, prep_res, exec_res):
        shared["chunk_sums"] = exec_res

class ReduceResults(Node):
    def prep(self, shared):
        return shared["chunk_sums"]

    def exec(self, chunk_sums):
        return sum(chunk_sums)  # 汇总所有块的和

    def post(self, shared, prep_res, exec_res):
        shared["total"] = exec_res

map_node >> reduce_node
flow = Flow(start=map_node)
```

## 与 BatchFlow 的区别

| 特性 | BatchNode | BatchFlow |
|------|-----------|-----------|
| 批量范围 | 单个节点内 | 整个子流程内 |
| 执行内容 | 多次调用 exec | 多次运行完整子流程 |
| 参数传递 | prep 返回列表，exec 逐个处理 | prep 返回 params 列表，每个 params 驱动子流程 |
| 节点间状态 | 同一个节点实例，exec 间通过循环 | 每次子流程独立运行，通过 shared 通信 |

## 源码位置

pocketflow/\_\_init\_\_.py
