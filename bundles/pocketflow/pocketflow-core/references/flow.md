---
title: Flow
type: reference
source: pocketflow/__init__.py
bundle: /pocketflow/pocketflow-core
related:
  - /pocketflow/pocketflow-core/references/base-node
  - /pocketflow/pocketflow-core/references/node
  - /pocketflow/pocketflow-core/concepts/flow-orchestration
  - /pocketflow/pocketflow-core/concepts/operator-chaining
---

# Flow

`Flow` 继承自 [Node](node.md)，是 PocketFlow 的核心编排器。它将多个节点连接成有向图，按节点的 post 返回值（action）驱动流转，支持线性管道、条件分支、循环、嵌套子流程。

## 构造函数

```python
Flow(start: BaseNode | None = None)
```

- `start`：可选的起始节点。也可以在构造后通过 `start()` 方法设置。

## 核心方法

### `start(start_node: BaseNode) -> Flow`

设置流程的起始节点，返回 self 支持链式调用。

```python
flow = Flow()
flow.start(node_a) >> node_b >> node_c
# 或
flow.start(node_a).next(node_b).next(node_c)
```

### `run(shared: dict) -> str | None`

运行流程，公开入口方法。返回最后一个执行节点的 post 返回值。

- 参数：`shared` — 全局共享存储字典，所有节点通过它传递数据
- 返回：最后一个节点 post 的返回值（action 字符串或 None）；若流程因找不到后继而终止，返回最后一个 action

### `get_next_node(curr: BaseNode, action: Any) -> BaseNode | None`

根据当前节点和 action 查找下一个节点。查找顺序：
1. 精确匹配 action：`curr.successors.get(action)`
2. 字符串化匹配：`curr.successors.get(str(action))`
3. 默认分支：`curr.successors.get("default")`
4. 都找不到：发出 UserWarning，返回 None

## 内部方法

### `_orch(shared: dict, params: dict | None = None) -> str | None`

核心编排方法，驱动节点流转循环：

```python
def _orch(self, shared, params=None):
    curr = copy.copy(self.start_node)
    p = params or {**self.params}
    last_action = None
    while curr:
        curr.set_params(p)
        last_action = curr._run(shared)
        curr = copy.copy(self.get_next_node(curr, last_action))
    return last_action
```

关键特性：
- 使用 `copy.copy()` 对每个节点做浅拷贝，防止多次运行间的状态污染
- params 合并：外部传入的 params 优先于 Flow 自身的 params
- 循环条件：curr 不为 None（即找到了后继节点）
- 终止条件：get_next_node 返回 None（找不到匹配 action 的后继且无 default）

## 连接节点的两种方式

### 方式一：运算符重载（推荐）

```python
flow = Flow(start=n1)
n1 >> n2                    # 默认边
n2 - "positive" >> n3       # 条件边
n2 - "negative" >> n4       # 条件边
```

### 方式二：next() 方法链式调用

```python
flow = Flow()
flow.start(n1).next(n2).next(n3)           # 链式默认边
n2.next(n3, "positive").next(n4, "negative") # next 指定 action
```

## 流程模式

### 线性管道

```python
n1 >> n2 >> n3
flow = Flow(start=n1)
flow.run(shared)
```

### 条件分支

```python
check - "positive" >> add_pos
check - "negative" >> add_neg
```

### 循环（自环）

```python
check - "positive" >> subtract3
subtract3 >> check  # 回到 check，形成循环
check - "negative" >> end_node  # 退出条件
```

### 嵌套子流程

```python
inner_flow = Flow(start=inner_start)
inner_start >> inner_end
outer_flow = Flow(start=inner_flow)
inner_flow - "inner_done" >> next_node  # 内层 Flow 返回的 action 可作为外层分支条件
```

## 注意事项

- Flow 继承自 Node，因此 Flow 本身也可以作为一个节点嵌入另一个 Flow 中。
- 节点间数据传递通过 `shared` 字典完成，不依赖节点间直接传参。
- 每个节点执行前会 `set_params(p)`，BatchFlow 等子类通过 params 传递批量参数。
- `copy.copy()` 浅拷贝意味着节点实例属性会被复制，但可变对象（如列表、字典）的引用仍指向同一对象。

## 源码位置

[pocketflow/\_\_init\_\_.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow/pocketflow/__init__.py)
