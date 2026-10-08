---
title: 流程编排
type: concept
bundle: /pocketflow/pocketflow-core
related:
  - /pocketflow/pocketflow-core/references/flow
  - /pocketflow/pocketflow-core/concepts/operator-chaining
  - /pocketflow/pocketflow-core/concepts/node-lifecycle
---

# 流程编排

Flow 是 PocketFlow 的编排引擎，将节点组织成有向图，通过节点 post 返回的 action 驱动流转。

## 编排核心循环

Flow._orch 的核心是一个 while 循环：

```python
curr = copy.copy(self.start_node)
while curr:
    curr.set_params(p)              # 注入参数
    last_action = curr._run(shared) # 执行节点（prep→exec→post）
    curr = copy.copy(self.get_next_node(curr, last_action))  # 找下一个节点
return last_action
```

循环终止条件：`get_next_node` 返回 None（找不到匹配 action 的后继节点）。

## 流转规则

节点执行完后，Flow 根据 post 返回的 action 查找后继：

1. 精确匹配：`successors.get(action)`
2. 字符串化匹配：`successors.get(str(action))`
3. 默认分支：`successors.get("default")`
4. 都找不到 → 发出 UserWarning，流程结束

```
post返回值          查找的key         匹配的连接方式
─────────────────────────────────────────────────
None              "default"          node_a >> node_b
"success"         "success"          node_a - "success" >> node_b
"error"           "error"            node_a - "error" >> node_c
任意字符串          该字符串            对应的条件边
```

## 四种基本流程模式

### 1. 线性管道（Sequential Pipeline）

所有节点走 default 边，post 返回 None。

```python
n1 >> n2 >> n3
flow = Flow(start=n1)
flow.run(shared)
```

执行顺序：n1 → n2 → n3，线性执行。

### 2. 条件分支（Conditional Branching）

一个节点根据 post 返回不同 action，走不同分支。

```python
check - "positive" >> add_pos
check - "negative" >> add_neg
```

执行路径：check 返回 "positive" → add_pos；返回 "negative" → add_neg。

### 3. 循环（Loop / Cycle）

后继节点指回前面的节点，形成环，直到满足退出条件。

```python
check - "continue" >> process
process >> check           # 回到 check 形成循环
check - "done" >> end_node # 退出条件
```

执行顺序：check → process → check → process → ... → check → end_node

### 4. 嵌套子流程（Nested Flow）

Flow 本身继承自 Node，因此可以作为节点嵌入另一个 Flow。

```python
inner_flow = Flow(start=ia)
ia >> ib  # 内层流程

outer_flow = Flow(start=inner_flow)
inner_flow - "done" >> oc  # 内层 Flow 的返回值作为外层的分支条件
```

内层 Flow 执行完毕后，其最后一个节点的 post 返回值作为 action 传递给外层 Flow，用于外层分支。

## 节点状态隔离

Flow 对每个节点执行 `copy.copy()` 浅拷贝，这意味着：

- 节点实例属性（如 `self.number`、`self.chunk_size`）在每次执行时是独立的副本
- 但共享的可变对象（如类属性、外部传入的列表/字典引用）仍指向同一对象
- 同一节点在循环中不会累积状态（因为每次都是新的副本）

## 参数传递

Flow 在执行每个节点前调用 `curr.set_params(p)`，将参数注入节点：

- 普通 Flow：`params` 参数或 `self.params` 作为参数集
- BatchFlow：prep 返回的每个参数字典独立注入一次
- 嵌套 Flow：外层 Flow 的 params 会传递给内层 Flow 的节点

节点内通过 `self.params.get("key")` 访问参数。

## shared 存储

`shared` 是贯穿整个 Flow 生命周期的字典，是节点间通信的唯一渠道：

- 任意节点都可以读写 shared
- prep 从 shared 读取前序节点的输出
- post 将当前节点的结果写入 shared
- Flow 结束后，调用者从 shared 中获取最终结果

```python
shared = {}
flow.run(shared)
print(shared["result"])  # 获取最终结果
```
