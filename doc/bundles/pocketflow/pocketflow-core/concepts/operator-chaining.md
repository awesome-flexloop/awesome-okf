---
title: 运算符重载与DSL
type: concept
bundle: /pocketflow/pocketflow-core
related:
  - /pocketflow/pocketflow-core/references/base-node
  - /pocketflow/pocketflow-core/concepts/flow-orchestration
---

# 运算符重载与DSL

PocketFlow 通过 Python 运算符重载实现了一套声明式的流程定义 DSL（领域特定语言），让图结构的定义直观可读。

## 两个核心运算符

### `>>` — 默认转移（Default Transition）

```python
node_a >> node_b
```

等价于 `node_a.next(node_b, "default")`，表示当 node_a 的 post 返回 None（或未返回值）时，跳转到 node_b。

**链式调用**：`>>` 返回右侧节点，因此可以链式连接：

```python
n1 >> n2 >> n3  # n1→n2→n3 线性管道
```

### `-` + `>>` — 条件转移（Conditional Transition）

```python
node_a - "success" >> node_b
```

单目运算符 `-` 接收一个 action 字符串，创建 `_ConditionalTransition` 过渡对象；然后 `>>` 将该条件分支指向目标节点。等价于 `node_a.next(node_b, "success")`。

**多分支**：同一个节点可以定义多个条件分支：

```python
check - "positive" >> add_pos
check - "negative" >> add_neg
check - "zero" >> handle_zero
```

## _ConditionalTransition 过渡对象

`-` 运算符不直接设置后继，而是返回一个临时对象持有"源节点+action"信息：

```python
class _ConditionalTransition:
    def __init__(self, node, action):
        self.node = node    # 源节点
        self.action = action  # 条件字符串

    def __rshift__(self, target):
        self.node.next(target, self.action)
        return target
```

这使得 `node - "action" >> target` 语法成为可能。`>>` 返回 target 节点，支持链式条件分支后继续串联。

## 与 Flow.start() 配合

Flow 提供 `start()` 方法作为流程定义的起点：

```python
# 方式一：构造函数指定起点
flow = Flow(start=n1)
n1 >> n2 >> n3

# 方式二：start() 方法指定（支持链式）
flow = Flow()
flow.start(n1) >> n2 >> n3

# 方式三：链式 next()
flow = Flow()
flow.start(n1).next(n2).next(n3)
```

## 完整语法示例

```python
from pocketflow import Node, Flow

# 定义节点
class NumberNode(Node):
    def __init__(self, n): super().__init__(); self.n = n
    def prep(self, s): s["current"] = self.n

class CheckNode(Node):
    def post(self, s, p, e):
        return "positive" if s["current"] >= 0 else "negative"

class AddNode(Node):
    def __init__(self, n): super().__init__(); self.n = n
    def prep(self, s): s["current"] += self.n

class SignalNode(Node):
    def post(self, s, p, e): return "done"

# DSL 定义流程
start = NumberNode(10)
check = CheckNode()
add_pos = AddNode(1)
add_neg = AddNode(-1)
end = SignalNode()

flow = Flow()
flow.start(start) >> check
check - "positive" >> add_pos
check - "negative" >> add_neg
add_pos >> check   # 循环
add_neg >> end     # 出口
```

## 运算符优先级

Python 运算符优先级：`-`（单目，优先级高）> `>>`（双目，优先级低）。因此：

```python
check - "positive" >> add_pos
# 等价于：(check - "positive") >> add_pos
# 而不是：check - ("positive" >> add_pos)  ← 错误
```

这保证了语法的正确性。

## 对比 next() 方法

运算符 DSL 直观但只能设置一个后继；`next()` 方法更灵活：

| 操作 | 运算符写法 | 方法写法 |
|------|-----------|---------|
| 默认边 | `a >> b` | `a.next(b)` |
| 条件边 | `a - "act" >> b` | `a.next(b, "act")` |
| 链式默认边 | `a >> b >> c` | `a.next(b).next(c)` |

推荐：简单线性流用 `>>`，条件分支用 `- "action" >>`，复杂动态设置用 `next()`。
