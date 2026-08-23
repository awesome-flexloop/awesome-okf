---
type: concept
title: "双向链表图结构：DoublyLinkedSet 迭代安全与 NameAuthority 命名"
description: "Graph 节点存储采用 DoublyLinkedSet 循环双向链表而非 Python list，实现遍历中 O(1) 安全增删；NameAuthority 为匿名节点/值自动生成唯一名称，采用单调计数器永不释放的设计"
sources:
  references: [../references/io-metadata.md, ../references/core-entities.md]
  facts: [F-044, F-045, F-046, F-047, F-034, F-035, F-037]
---

# 双向链表图结构：DoublyLinkedSet 迭代安全与 NameAuthority 命名

## 核心理解

Python list 是最直觉的图节点存储选择，但在图 Pass 中迭代 list 时执行 `remove`/`insert` 会导致索引错位或元素遗漏。onnx-ir 采用 `DoublyLinkedSet`（循环双向链表 + id→box O(1) 索引）存储图节点，解决迭代中变异安全问题；配合 `NameAuthority` 自动命名治理器，保证所有节点和值都有唯一名称。

## 为什么不用 Python list？

在图优化 Pass 中，常见模式是遍历节点列表同时执行增删：

```python
# 如果用 list，这是不安全的！
for node in list(graph):
    if can_fuse(node):
        fused = fuse(node, next_node)
        graph.remove(node)       # 索引错位！
        graph.remove(next_node)
        graph.insert_before(node, fused)  # 可能跳过节点！
```

Python list 的 `remove`/`insert` 是 O(n) 操作，且迭代中修改列表会导致未定义行为（跳过元素或重复访问）。

## _LinkBox：双向链表节点容器

`_LinkBox` 是链表的内部节点容器（F-044）：

```python
class _LinkBox:
    __slots__ = ("prev", "next", "value", "owning_list")
    prev: _LinkBox | None       # 前驱box
    next: _LinkBox | None       # 后继box
    value: Any                  # 实际存储对象（None = 已擦除/根哨兵）
    owning_list: DoublyLinkedSet | None
```

### erase() 的关键设计

```python
def erase(self) -> None:
    self.prev.next = self.next    # 前驱跳过自己
    self.next.prev = self.prev    # 后继跳过自己
    self.value = None             # 标记已擦除
    self.owning_list = None
    # 注意：不修改 self.prev / self.next 指针！
```

**关键**：`erase()` 不修改自身的 prev/next 指针，仅断开邻居指向自己的链接。这保证了正在遍历到该 box 的迭代器仍可通过 `self.next` 找到下一个元素。

## DoublyLinkedSet：循环双向链表有序集合

`DoublyLinkedSet` 使用循环双向链表（root 哨兵节点 value=None）+ id→box 字典（F-045）：

```
┌──────┐     ┌──────┐     ┌──────┐     ┌──────┐
│ root │◄───►│ BoxA │◄───►│ BoxB │◄───►│ BoxC │◄──┐
│(None)│     │(Node)│     │(Node)│     │(Node)│   │
└──┬───┘     └──────┘     └──────┘     └──────┘   │
   └──────────────────────────────────────────────┘
               （循环双向链表）

_value_ids_to_boxes: {id(A): BoxA, id(B): BoxB, id(C): BoxC}
```

### 操作复杂度

| 操作 | 复杂度 | 实现方式 |
|------|--------|----------|
| `append(value)` | O(1) | root.prev 后插入新box |
| `remove(value)` | O(1) | id 查找box → erase() |
| `insert_after(existing, value)` | O(1) | id 查找box → 在其后插入 |
| `insert_before(existing, value)` | O(1) | id 查找box → 在其前插入 |
| `__contains__(value)` | O(1) | id 查找dict |
| `__len__` | O(1) | 维护 _length 字段 |
| 索引访问 `[i]` | O(n) | 顺序遍历（首尾 O(1)） |

索引访问是 O(n)，但图遍历几乎都是顺序迭代而非随机索引，这是正确的权衡。

### 重复值处理

插入重复值时，先 remove 旧的再插入新位置。这意味着一个对象同一时刻只能在链表中出现一次（集合语义）。

### 迭代器安全保证（F-046）

迭代器行为规则：
1. **当前节点之后插入的新元素会被遍历到**：因为迭代器沿 next 前进，新节点被正确链接到链表中
2. **当前节点之前插入的不会被遍历到**：因为迭代器已经走过了那个位置
3. **当前节点被移动到其他位置时**，迭代从原位置的 next 继续（不跳转到新位置）
4. **迭代时遇到 erased box（value=None）自动跳过**

```
迭代过程中 remove(B)：
  迭代器当前指向 BoxB
  BoxB.erase()：prev.next=next, next.prev=prev, value=None

  ┌──────┐     ┌──────┐     ┌──────┐     ┌──────┐
  │ root │◄───►│ BoxA │◄──┐ │ BoxB │  ┌─►│ BoxC │◄──┐
  │(None)│     │(Node)│  │ │(None)│  │ │(Node)│   │
  └──┬───┘     └──────┘  └─┴──────┴──┘ └──────┘   │
     └─────────────────────────────────────────────┘
  迭代器从 BoxB.next → BoxC，继续正常遍历！
```

## Graph 如何使用 DoublyLinkedSet（F-034/F-035）

Graph 的节点存储和操作：

```python
class Graph(Sequence[Node]):
    _nodes: DoublyLinkedSet[Node]
    _name_authority: NameAuthority
    inputs: GraphInputs      # MutableSequence[Value]
    outputs: GraphOutputs    # MutableSequence[Value]
    initializers: GraphInitializers  # dict-like, name→Value
```

### 构造流程

```
1. 注册 inputs 的名称到 NameAuthority
2. 注册 initializers 的名称到 NameAuthority
3. self.extend(nodes)：
   a. 每个节点设置 self._graph 引用
   b. 匿名节点自动命名（node_{op_type}_{counter}）
   c. 节点输出值自动命名（val_{counter}）
   d. _nodes.append(node)
```

### 变异方法委托

| Graph 方法 | 底层操作 |
|------------|----------|
| `append(node)` | 设置 graph 引用 + 自动命名 + `_nodes.append()` |
| `extend(nodes)` | 逐个 append |
| `remove(nodes, safe)` | 安全检查 + `_nodes.remove()` |
| `insert_after(after, node)` | 设置 graph 引用 + 自动命名 + `_nodes.insert_after()` |
| `insert_before(before, node)` | 设置 graph 引用 + 自动命名 + `_nodes.insert_before()` |

### 安全删除（F-037）

`remove(safe=True)` 是事务性操作：
1. **检查阶段**：验证所有待删除节点的输出不被保留节点使用、不是图输出
2. **执行阶段**：断开引用、从链表摘除、清理 NameAuthority
3. 如果检查阶段任何一项失败，图不被修改（原子性保证）

## NameAuthority：自动唯一命名

`NameAuthority` 为匿名节点和值自动生成唯一名称（F-047）：

```python
class NameAuthority:
    _value_names: set[str]     # 已使用的值名称集合
    _node_names: set[str]      # 已使用的节点名称集合
    _value_counter: int        # 值名称计数器
    _node_counter: int         # 节点名称计数器
```

### 命名规则

| 对象类型 | 匿名命名格式 | 示例 |
|----------|-------------|------|
| Value | `val_{counter}` | `val_0`, `val_1`, `val_2` |
| Node | `node_{op_type}_{counter}` | `node_Add_0`, `node_MatMul_1` |

- 如果对象已有名称（`name is not None`），则不改名
- 已有名称会被注册到集合中防止重复
- 尝试注册重复名称会抛出错误

### 反直觉设计：名称永不释放

开发者注释明确指出：名称一旦被跟踪，即使节点/值被移除也不会释放，计数器单调增长。

**为什么这样设计？** 释放名称可能导致新旧对象重名。在图变换（optimization pass）中，如果删除节点A后新建节点B恰好获得A的名称，可能导致：
- 序列化后 proto 中出现同名但语义不同的对象
- 调试时难以区分"删除前的val_3"和"新建的val_3"
- 基于名称的缓存或分析结果错误

在模型规模范围内（通常数万个节点/值），计数器增长完全可接受。

## Graph 容器包装

Graph 的 inputs/outputs/initializers 不是直接暴露 list/dict，而是包装为专用容器类：

| 容器 | 行为 | 职责 |
|------|------|------|
| `GraphInputs` (MutableSequence) | 输入值列表 | 添加/移除时同步设置/清除 `_is_graph_input` 标记、注册/注销 NameAuthority |
| `GraphOutputs` (MutableSequence) | 输出值列表 | 添加/移除时同步设置/清除 `_is_graph_output` 标记 |
| `GraphInitializers` (dict-like) | name→Value 映射 | 设置值时标记 `_is_initializer`、设置 `const_value`；删除时清除标记；重命名时同步更新 |

这些容器保证了 Value 角色标记的一致性——`_is_graph_input`/`_is_graph_output`/`_is_initializer` 三个布尔标记只能由对应容器设置，外部无法直接修改。
