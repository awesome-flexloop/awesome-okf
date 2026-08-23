---
type: concept
title: "计算图模型"
description: "GraphProto/NodeProto/Input-Output/Initializer 的拓扑关系、字符串名字连接机制、initializer 与 input 的区别、value_info 的作用、C++ IR 双向链表"
sources:
  references: [../references/onnx-proto.md, ../references/cpp-ir.md]
  facts: [F-005, F-008, F-052, F-053, F-054, F-055, F-057, F-058, F-059]
---

# 计算图模型

## 核心理解

ONNX 计算图是一个**有向无环图（DAG）**，由节点（NodeProto）和值（通过字符串名字标识）构成。节点代表计算操作（算子调用），值代表数据（张量）在节点之间的流动。理解图的连接机制、初始器与输入的区别、以及 Protobuf 表示与 C++ IR 的差异，是正确操作 ONNX 模型的关键。

## 机制详解

### 图的基本结构

GraphProto 包含六类核心元素（F-008）：

```
GraphProto
├── input[]  ──→ ValueInfoProto[]   "图的输入边界"
├── output[] ──→ ValueInfoProto[]   "图的输出边界"
├── node[]   ──→ NodeProto[]        "计算节点"
├── initializer[] ─→ TensorProto[]  "常量权重/参数"
├── sparse_initializer[] → SparseTensorProto[]  "稀疏常量"
└── value_info[] ──→ ValueInfoProto[] "中间值类型信息"
```

### 字符串名字连接机制

ONNX 计算图最独特的设计：**节点之间通过字符串名字连接，而非指针/引用**（F-005）。

```
input: ["X", "W"]     node(MatMul)     output: ["Y"]
                           │
                           │ "Y" 作为下一个节点的 input
                           ↓
input: ["Y", "B"]     node(Add)       output: ["Z"]
                           │
                           ↓
                      output: ["Z"]    (图的输出)
```

规则：
1. 每个 NodeProto 的 `output` 字段**定义**新的名字（字符串）
2. 后续 NodeProto 的 `input` 字段**引用**已定义的名字
3. GraphProto 的 `input` 名字可以被任意节点引用
4. GraphProto 的 `initializer` 名字可以被任意节点引用（作为常量输入）
5. 名字在图范围内必须唯一（checker 验证）

### initializer 与 input 的区别

这是初学者最常混淆的概念：

| | input[] | initializer[] |
|--|---------|---------------|
| **本质** | 图的运行时输入 | 存储在模型内的常量 |
| **类型** | ValueInfoProto（类型描述） | TensorProto（实际数据） |
| **运行时值** | 推理时由调用者提供 | 序列化为模型文件的一部分 |
| **典型用途** | 数据输入（如图像、文本） | 模型权重/偏置/参数 |
| **是否必须有类型** | ✅ 必须有 TypeProto | 可选（建议有 value_info） |

**IR >= 4 的重要变化**（F-057）：
- IR_VERSION 1-3：initializer 中的名字**必须同时**出现在 input 中
- IR_VERSION 4+：initializer 可以不在 input 中声明，这些初始化器是"内部常量"
- 在 C++ IR 中，非输入初始化器通过特殊的 `initializer_node_`（Param 节点）持有

```
IR >= 4 图结构示意：

  graph.input:        ["X"]           ← 运行时输入（数据）
  graph.initializer:  ["W", "B"]      ← 模型权重（常量，不需要在input中声明）

  node1: MatMul(X, W) → Y
  node2: Add(Y, B) → Z
  graph.output:       ["Z"]
```

### value_info 的作用

`value_info` 字段存储**中间值的类型和形状信息**（F-008）：

- 初始创建的模型通常不填充 value_info（不知道中间形状）
- 形状推断（`infer_shapes()`）的结果写入 value_info
- checker 的 full_check 模式依赖 value_info 验证类型一致性
- value_info 不是必须的，但没有它无法进行完整的类型检查

```python
# 形状推断填充 value_info
model = onnx.shape_inference.infer_shapes(model)
# 之后 model.graph.value_info 包含中间值的类型和形状
for vi in model.graph.value_info:
    print(vi.name, vi.type)  # 打印每个中间张量的名字和类型
```

### C++ IR 的高效图表示

在 C++ 层（F-052~F-059），图使用更高效的内存表示：

```
Graph (unique_ptr 所有权)
│
├── 双向循环链表 (next_in_graph[2])
│   │
│   sentinel ── Node(1) ── Node(2) ── Node(3) ── sentinel
│   (output_)   ↑                          │
│   │           └──────────────────────────┘
│   │
├── Node 结构（继承 CRTP Attributes<Node>）
│   ├── inputs_[]: Value*    ──→ 输入值指针
│   ├── outputs_[]: Value*   ──→ 输出值指针（拥有所有权）
│   └── 属性通过 Attributes<Node> CRTP 访问
│
├── Value 结构（边/值）
│   ├── node_: Node*         ──→ 生产节点
│   ├── offset_: size_t      ──→ 在生产节点输出中的索引
│   ├── uses_head: Use*      ──→ 消费者双向链表头
│   ├── sizes_: Dimension[]  ──→ 形状
│   └── replaceAllUsesWith() ──→ 替换所有使用点（图变换核心）
│
└── Use 结构（使用点）
    ├── user: Node*          ──→ 消费者节点
    ├── offset: size_t       ──→ 在消费者输入中的索引
    ├── next/prev: Use*      ──→ 双向链表指针
    └── 通过 Value.uses_head 遍历同一值的所有消费者
```

**哨兵节点（Sentinel）**：双向循环链表使用 `output_` 作为哨兵节点，链表中没有 nullptr 指针。遍历方式：

```cpp
for (Node* n = graph->output()->next_in_graph[1];  // 第一个节点
     n != graph->output();                         // 回到哨兵结束
     n = n->next_in_graph[1]) {
  // 处理节点 n
}
```

**used_names_ O(1) 查重**：Graph 维护 `unordered_map<string, int> used_names_` 哈希表，实现 O(1) 时间复杂度的名字唯一性检查和自动命名（F-058）。

**subgraph_bearing_nodes_**：跟踪包含 GRAPH/GRAPHS 属性的节点（如 If、Loop、Scan），避免遍历所有节点找子图（F-058）。

### Dimension 三态

C++ IR 的 Dimension 结构体（F-055）用两个 bool 标志区分三种状态：

| is_unknown | is_int | 含义 |
|-----------|--------|------|
| true | - | 未知维度 |
| false | true | 整数维度（dim 字段有值） |
| false | false | 符号参数维度（param 字段有值） |

这比 protobuf oneof 更适合 C++ 的可变状态场景。

## 图遍历示例

Python 端遍历计算图（操作 Protobuf message）：

```python
import onnx

model = onnx.load("model.onnx")
graph = model.graph

# 1. 遍历所有节点
for node in graph.node:
    print(f"Op: {node.op_type}, Name: {node.name}")
    print(f"  Inputs: {list(node.input)}")
    print(f"  Outputs: {list(node.output)}")

# 2. 构建名字→初始器映射
initializer_map = {init.name: init for init in graph.initializer}

# 3. 构建名字→ValueInfo映射
value_info_map = {vi.name: vi for vi in graph.value_info}
input_map = {vi.name: vi for vi in graph.input}
output_map = {vi.name: vi for vi in graph.output}

# 4. 查找某个输出值的类型信息
def get_value_info(name):
    for vi_map in [input_map, output_map, value_info_map]:
        if name in vi_map:
            return vi_map[name]
    # 在initializer中查找
    if name in initializer_map:
        return initializer_map[name]
    return None
```

## 关键洞察/反常识

1. **字符串连接而非指针**：Protobuf 层面节点之间通过字符串名字连接，这使得序列化极其简单（不需要处理引用），但图变换时需要手动维护名字一致性。C++ IR 层使用指针，但只在内部使用。
2. **initializer ≠ input**：IR >= 4 后，权重参数不需要（也不应该）放在 graph.input 中。graph.input 只用于运行时需要外部提供的输入。
3. **value_info 不是自动填充的**：加载模型后，中间值的类型信息通常不在 value_info 中。必须调用 `infer_shapes()` 才能获得中间值形状。
4. **C++ IR 不直接暴露给 Python**：Python 端操作的始终是 Protobuf message 对象。C++ 的 Graph/Node/Value 类只在 C++ 编译的扩展模块内部使用，Python 无法直接访问。
5. **空字符串输入是合法的**：NodeProto 的 input 中可以有空字符串 `""`，表示该位置的输入是可选的（未连接）。这对应 OpSchema 中的 Optional 形参。

## 关联概念

- [Protobuf IR：核心 Message 结构](01-protobuf-ir.md) — GraphProto/NodeProto 的完整字段定义
- [张量类型系统](02-tensor-type-system.md) — ValueInfoProto 和 TensorProto 的类型表示
- [C++ 核心 IR](12-cpp-core-ir.md) — C++ 层 Graph/Node/Value 的深入分析
- [形状推断实现](06-shape-inference.md) — value_info 如何通过形状推断填充
- [图遍历与变换实战](../examples/graph-transformation.md) — 实际操作图结构的代码示例
