---
title: BaseNode
type: reference
source: pocketflow/__init__.py
bundle: /pocketflow/pocketflow-core
---

# BaseNode

`BaseNode` 是 PocketFlow 所有节点类型的抽象基类，定义了节点的核心数据结构（params、successors）、生命周期方法（prep/exec/post）和流连接运算符（>>、-）。

## 构造函数

```python
BaseNode()
```

初始化两个空字典：
- `self.params = {}` — 节点参数存储，由 Flow 编排时通过 `set_params` 注入
- `self.successors = {}` — 后继节点映射，key 为 action 字符串（"default" 为默认分支），value 为目标节点对象

## 核心方法

### `set_params(params: dict) -> None`

将参数字典合并到节点的 params 中。Flow 在编排每个节点前调用此方法，将当前迭代的参数注入节点。

```python
node.set_params({"key": "value", "batch_id": 0})
```

### `next(node: BaseNode, action: str = "default") -> BaseNode`

设置后继节点，返回被连接的 node 对象以支持链式调用。

```python
node_a.next(node_b)           # 默认分支：node_a 的 post 返回 None 时跳转
node_a.next(node_c, "error")  # 条件分支：node_a 的 post 返回 "error" 时跳转
```

### `prep(shared: dict) -> Any`

**前处理步骤**。在 exec 之前执行，通常用于从 shared 存储中读取数据、做准备工作。返回值作为 exec 的输入参数 `prep_res`。

- 参数：`shared` — 全局共享存储字典，贯穿整个 Flow 生命周期
- 返回：任意值，传递给 exec

默认实现：`pass`（返回 None）。

### `exec(prep_res: Any) -> Any`

**核心执行步骤**。实现节点的主要业务逻辑。

- 参数：`prep_res` — prep 方法的返回值
- 返回：任意值，传递给 post 作为 `exec_res`

默认实现：`pass`（返回 None）。

### `post(shared: dict, prep_res: Any, exec_res: Any) -> str | None`

**后处理步骤**。在 exec 之后执行，通常用于将结果写入 shared 存储、决定下一个 action 分支。

- 参数：
  - `shared` — 全局共享存储字典（可修改）
  - `prep_res` — prep 的返回值
  - `exec_res` — exec 的返回值
- 返回：字符串表示走对应 action 条件分支；返回 None 走 default 分支；返回的字符串也作为 Flow 的最终返回值（如果是最后一个节点）

默认实现：`pass`（返回 None）。

### `run(shared: dict) -> str | None`

公开同步运行入口。执行 prep → _exec → post 完整生命周期，返回 post 的结果。

```python
result = node.run(shared_storage)
```

## 运算符重载

### `__rshift__(other: BaseNode) -> BaseNode`

`>>` 运算符：设置默认后继节点，等价于 `self.next(other, "default")`。

```python
node_a >> node_b  # node_a 的 post 返回 None 时跳转到 node_b
```

### `__sub__(action: str) -> _ConditionalTransition`

`-` 运算符：创建条件过渡对象，用于后续 `>>` 指定条件分支。

```python
node_a - "success" >> node_b  # node_a 的 post 返回 "success" 时跳转到 node_b
node_a - "fail" >> node_c     # node_a 的 post 返回 "fail" 时跳转到 node_c
```

## 内部方法

### `_exec(prep_res: Any) -> Any`

内部执行方法，BaseNode 中直接调用 `self.exec(prep_res)`。子类（如 Node）可重写此方法添加重试、批处理等逻辑。

### `_run(shared: dict) -> str | None`

内部运行方法，执行 `prep → _exec → post` 三步调用链，返回 post 的结果。

## 子类继承关系

```
BaseNode
├── Node              # 同步节点（带重试）
│   ├── BatchNode     # 同步批量节点
│   └── Flow          # 同步流程
│       └── BatchFlow # 同步批量流程
└── AsyncNode         # 异步节点（带重试）
    ├── AsyncBatchNode           # 异步串行批量
    ├── AsyncParallelBatchNode   # 异步并行批量
    └── AsyncFlow                # 异步流程
        ├── AsyncBatchFlow           # 异步串行批量流程
        └── AsyncParallelBatchFlow   # 异步并行批量流程
```

## 源码位置

pocketflow/\_\_init\_\_.py
