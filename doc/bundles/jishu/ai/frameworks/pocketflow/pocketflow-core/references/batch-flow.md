---
title: BatchFlow
type: reference
source: pocketflow/__init__.py
bundle: /pocketflow/pocketflow-core
related:
  - /pocketflow/pocketflow-core/references/flow
  - /pocketflow/pocketflow-core/references/batch-node
  - /pocketflow/pocketflow-core/concepts/batch-processing
---

# BatchFlow

`BatchFlow` 继承自 [Flow](flow.md)，实现**整个子流程的批量执行**。prep 返回一组参数字典，每个参数字典驱动子流程完整执行一次，实现参数化批量处理。

## 核心方法

### `prep(shared: dict) -> list[dict]`

返回参数字典列表。每个字典会通过 `set_params` 注入到子流程的所有节点中，节点通过 `self.params.get(key)` 访问当前参数。

```python
class MyBatchFlow(BatchFlow):
    def prep(self, shared):
        return [{"key": k} for k in shared["input_data"].keys()]
```

## 内部方法

### `_orch(shared: dict, params: dict | None = None) -> None`

重写自 Flow._orch，实现批量执行：

```python
def _orch(self, shared, params=None):
    params_list = self.prep(shared)
    for p in params_list:
        super()._orch(shared, p)
```

执行流程：
1. 调用 `self.prep(shared)` 获取参数列表
2. 对参数列表中的每个参数字典 p，调用 `Flow._orch(shared, p)` 运行一次完整子流程
3. 每次子流程运行时，p 通过 `set_params` 注入到每个节点

## 参数访问

子流程中的节点通过 `self.params` 访问当前批量参数：

```python
class ProcessNode(Node):
    def prep(self, shared):
        key = self.params.get("key")  # 获取当前批次的 key
        data = shared["input_data"][key]
        return data

    def exec(self, data):
        return data * 2

    def post(self, shared, prep_res, exec_res):
        key = self.params.get("key")
        if "results" not in shared:
            shared["results"] = {}
        shared["results"][key] = exec_res
```

## 嵌套 BatchFlow

BatchFlow 可以嵌套，外层 prep 返回 group 参数，内层 prep 根据 group 返回 item 参数：

```python
class InnerBatchFlow(BatchFlow):
    def prep(self, shared):
        group = self.params["group"]
        return [{"item": i, "group": group} for i in range(len(shared["groups"][group]))]

class OuterBatchFlow(BatchFlow):
    def prep(self, shared):
        return [{"group": g} for g in shared["groups"]]
```

## 使用场景

- 对多个独立输入项执行相同的处理流程
- 每个参数集独立运行完整子流程
- 需要在子流程中保持节点间的正常流转（多节点串联/分支）
- 嵌套批量处理（外循环分组、内循环分项目）

## 源码位置

pocketflow/\_\_init\_\_.py
