---
type: example
title: "图遍历与变换"
description: "遍历 ONNX IR 计算图的各种方式——顺序迭代、前驱/后继查询、子图递归、安全删除节点、值替换（replace_all_uses_with）、常量折叠 Pass 示例"
sources:
  concepts: [../concepts/01-core-entities.md, ../concepts/04-doubly-linked-graph.md, ../concepts/02-tensor-protocol.md]
  references: [../references/core-entities.md, ../references/io-metadata.md]
---

# 图遍历与变换

## 目标

掌握 onnx-ir 图遍历的各种模式：顺序迭代节点、查询前驱后继、递归遍历子图、安全增删节点、值替换（SSA 风格的 use-def 链操作），以及实现一个简单的常量折叠 Pass。

## 前置知识

- [核心实体 Model/Graph/Node/Value](../concepts/01-core-entities.md)：Value 的 producer/uses 关系、Node 的前驱后继
- [双向链表图结构](../concepts/04-doubly-linked-graph.md)：DoublyLinkedSet 迭代安全、安全删除

## 遍历模式

### 1. 顺序迭代所有节点（推荐方式）

```python
import onnx_ir as ir
from onnx_ir._io import load

# 加载模型
model = load("model.onnx")
graph = model.graph

# ✅ 推荐：直接 for-in 遍历（双向链表安全迭代器）
for node in graph:
    print(f"{node.op_identifier()}: {[v.name for v in node.inputs]} → "
          f"{[v.name for v in node.outputs]}")
```

**为什么不能用索引遍历？**

```python
# ❌ 不推荐：索引访问是 O(n)，整体 O(n²)
for i in range(len(graph)):
    node = graph[i]  # O(n) 每次！
    ...
```

DoublyLinkedSet 的索引访问是 O(n)，因为需要从链表头/尾顺序遍历。直接 for-in 使用迭代器是 O(n) 整体，且支持遍历中安全增删。

### 2. 查询前驱和后继节点

```python
for node in graph:
    # 前驱节点（使用当前节点输入值的节点）
    preds = node.predecessors()
    # successors 中去重（通过 dict 保持顺序）
    print(f"Node {node.op_identifier()}:")
    print(f"  predecessors: {[n.op_type for n in preds]}")
    print(f"  successors: {[n.op_type for n in node.successors()]}")
```

### 3. 遍历图输入、输出和初始化值

```python
# 图输入
for value in graph.inputs:
    print(f"Input: {value.name}, shape={value.shape}, dtype={value.type}")

# 图输出
for value in graph.outputs:
    print(f"Output: {value.name}")

# 初始化值（常量权重）
for name, value in graph.initializers.items():
    tensor = value.const_value
    print(f"Initializer: {name}, shape={tensor.shape}, dtype={tensor.dtype}")
```

### 4. 递归遍历所有子图

```python
# Graph.subgraphs() 递归 yield 所有子图（If/Loop 等算子的子图）
for subgraph in graph.subgraphs():
    print(f"Subgraph with {len(subgraph)} nodes")

# Graph.all_nodes() 递归 yield 所有节点（含子图中的节点）
for node in graph.all_nodes():
    print(f"Node: {node.op_type}")
```

### 5. 递归遍历 Model 中所有图

```python
for g in model.graphs():
    print(f"Graph with {len(g)} nodes, inputs={[v.name for v in g.inputs]}")
```

## 图变换操作

### 1. 在指定位置插入节点

```python
# 找到目标节点
target_node = None
for node in graph:
    if node.op_type == "Relu":
        target_node = node
        break

# 在 target_node 之后插入新节点
new_value = ir.val(name="new_out")
new_node = ir.Node(
    "MyCustomOp",
    inputs=[target_node.outputs[0]],
    outputs=[new_value],
)
graph.insert_after(target_node, new_node)

# 在 target_node 之前插入
before_node = ir.Node(
    "AnotherOp",
    inputs=[target_node.inputs[0]],
    outputs=[ir.val(name="before_out")],
)
graph.insert_before(target_node, before_node)
```

### 2. 安全删除节点

```python
# 删除单个 Relu 节点（安全模式）
nodes_to_remove = [n for n in graph if n.op_type == "Dropout"]

# safe=True（默认）：检查被删除节点的输出是否被其他节点使用
try:
    graph.remove(nodes_to_remove, safe=True)
    print(f"Removed {len(nodes_to_remove)} Dropout nodes")
except ValueError as e:
    print(f"Cannot safely remove: {e}")
```

**safe=True 做了什么？**

1. 检查被移除节点的输出不被其他保留节点使用
2. 检查被移除节点的输出不是图输出
3. 断开所有 input 引用（`replace_input_with(i, None)`）
4. 如果任何检查失败，图不被修改（事务性保证）

```python
# 如果你确定引用关系，可以使用 safe=False（不推荐，需自己保证一致性）
graph.remove(nodes_to_remove, safe=False)
```

### 3. 值替换（replace_all_uses_with）

这是 SSA 风格的值替换，类似于 LLVM 的 `replaceAllUsesWith`：

```python
# 将所有使用 old_value 的地方替换为 new_value
old_value = some_node.outputs[0]
new_value = another_node.outputs[0]

old_value.replace_all_uses_with(new_value)
# 之后所有 consumer 节点引用 old_value 的位置都指向 new_value
```

如果 old_value 是图输出且不希望替换图输出：

```python
try:
    old_value.replace_all_uses_with(new_value, replace_graph_outputs=False)
except ValueError:
    # old_value 是图输出，不能替换（除非设置 replace_graph_outputs=True）
    pass
```

### 4. 修改节点输入

```python
node = graph[0]  # 第一个节点

# 替换指定位置的输入
node.replace_input_with(0, new_input_value)

# 调整输入数量
node.resize_inputs(3)  # 增加到3个输入
node.replace_input_with(2, third_input)
node.resize_inputs(1)  # 减少到1个输入（多余的输入被断开）
```

注意：`node.inputs` 是不可变 tuple，不能直接赋值！

### 5. 修改节点输出

```python
# 调整输出数量
node.resize_outputs(2)  # 增加到2个输出
node.resize_outputs(1)  # 减少到1个输出
# 注意：缩小时被移除的输出不能有 uses，否则报错
```

## 实战：简单的常量折叠 Pass

以下示例实现一个简单的常量折叠 Pass：将输入都是 initializer 的算子替换为常量输出。

```python
import numpy as np
import onnx_ir as ir
from onnx_ir._io import load, save

def is_constant_value(value: ir.Value) -> bool:
    """检查值是否是编译期常量（initializer 或 Constant 节点输出）"""
    return value.is_initializer() or (
        value.producer is not None
        and value.producer.op_type == "Constant"
    )

def evaluate_constant_node(node: ir.Node) -> np.ndarray | None:
    """对常量输入的简单算子求值（仅演示少数算子）"""
    inputs = []
    for inp in node.inputs:
        if inp.is_initializer():
            inputs.append(inp.const_value.numpy())
        elif inp.producer and inp.producer.op_type == "Constant":
            # Constant 节点的 value 属性包含张量
            value_attr = inp.producer.attributes.get("value", None)
            if value_attr is not None:
                inputs.append(value_attr.as_tensor().numpy())
            else:
                return None
        else:
            return None

    try:
        if node.op_type == "Add":
            return inputs[0] + inputs[1]
        elif node.op_type == "Mul":
            return inputs[0] * inputs[1]
        elif node.op_type == "Relu":
            return np.maximum(inputs[0], 0)
        elif node.op_type == "Shape":
            return np.array(inputs[0].shape.numpy(), dtype=np.int64)
        # ... 更多算子
    except Exception:
        return None
    return None

def constant_fold_pass(graph: ir.Graph) -> int:
    """常量折叠 Pass，返回折叠的节点数量"""
    folded = 0
    changed = True

    while changed:
        changed = False
        # 注意：在遍历中收集要修改的节点，不要在迭代中直接增删
        nodes_to_remove = []
        replacements = {}  # old_value -> new_const_value

        for node in graph:
            # 检查所有输入是否是常量
            if not all(is_constant_value(inp) for inp in node.inputs):
                continue

            # 尝试求值
            result = evaluate_constant_node(node)
            if result is None:
                continue

            # 创建常量 initializer
            const_tensor = ir.tensor(
                result.astype(np.float32) if result.dtype.kind == 'f'
                else result,
                name=f"folded_{node.outputs[0].name}",
            )
            const_value = ir.Value(
                name=const_tensor.name,
                const_value=const_tensor,
            )
            # 注意：将 initializer 加入 graph 需要通过 graph.initializers

            replacements[node.outputs[0]] = const_value
            nodes_to_remove.append(node)
            folded += 1
            changed = True

        # 应用替换（在迭代之外）
        for old_val, new_val in replacements.items():
            # 添加新常量到 initializers
            graph.initializers[new_val.name] = new_val
            # 替换所有使用
            old_val.replace_all_uses_with(new_val)

        # 删除折叠掉的节点（安全模式）
        if nodes_to_remove:
            graph.remove(nodes_to_remove, safe=True)

    return folded

# 使用
model = load("model.onnx")
count = constant_fold_pass(model.graph)
print(f"Folded {count} constant nodes")
save(model, "model_folded.onnx")
```

## 遍历中安全变异的最佳实践

```
┌──────────────────────────────────────────────────────────┐
│              图 Pass 的标准模式                           │
│                                                          │
│  1. for node in graph:  （安全迭代器）                    │
│     ├─ 分析节点，收集信息到 meta 或局部变量               │
│     └─ 收集待修改的节点/值到列表（不直接修改）             │
│                                                          │
│  2. 遍历结束后：                                          │
│     ├─ value.replace_all_uses_with(new_val)              │
│     ├─ graph.append/insert_after/insert_before           │
│     └─ graph.remove(nodes, safe=True)                    │
│                                                          │
│  3. graph.sort() （如需拓扑排序）                        │
└──────────────────────────────────────────────────────────┘
```

### 关键要点

1. **直接 for-in 遍历**：`for node in graph` 使用双向链表安全迭代器，支持遍历中增删
2. **避免索引遍历**：`for i in range(len(graph))` 是 O(n²)，且迭代中修改不安全
3. **收集-应用模式**：在迭代中收集要修改的节点，迭代结束后统一应用修改
4. **优先使用 replace_all_uses_with**：不要手动遍历每个 consumer 修改引用
5. **默认 safe=True 删除**：除非你完全确定引用关系，否则使用安全删除
6. **利用 meta 存储分析结果**：Pass 间通过 `node.meta["key"]` 传递信息，自动失效标记可用于"标记-清除"模式
7. **递归遍历用 all_nodes/subgraphs**：不要自己写递归，使用 Graph 提供的方法
