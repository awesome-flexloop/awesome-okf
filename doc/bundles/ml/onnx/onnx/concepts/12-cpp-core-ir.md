---
type: concept
title: "C++ 核心 IR"
description: "C++ 层 Graph/Node/Value 类层次、双向循环链表（哨兵节点）、CRTP Attributes、Value::replaceAllUsesWith、Use 结构体、Dimension 三态、initializer_node_、used_names_ O(1) 查重"
sources:
  references: [../references/cpp-ir.md]
  facts: [F-052, F-053, F-054, F-055, F-056, F-057, F-058, F-059]
---

# C++ 核心 IR

## 核心理解

ONNX C++ IR（中间表示）定义在 `onnx/common/ir.h` 中，是 ONNX C++ 内部用于高效操作计算图的数据结构。与 Python 端直接操作 Protobuf message 不同，C++ IR 使用指针连接的对象图（Graph/Node/Value），通过双向循环链表、CRTP 属性模式和哨兵节点等设计实现高效的图遍历和变换。C++ IR 不直接暴露给 Python 用户，但理解它有助于理解 ONNX 内部工作原理，特别是优化器、形状推断和版本转换器的实现。

> **重要**：Python 端没有对应的 Python 版 Graph/Node 类。C++ IR 只在 C++ 编译的模块内部使用（checker、shape_inference、optimizer 等），Python API 始终操作 Protobuf message。

## 机制详解

### 三核心结构体与所有权模型

C++ IR 的核心是三个结构体（F-052）：

```
Graph（计算图，顶级容器）
│
├── 通过 unique_ptr<Node> 拥有所有 Node
├── 通过 unique_ptr<Value> 拥有所有 Value
│
└── Node 和 Value 之间通过原始指针（raw pointer）互相引用
```

```cpp
class Graph {
  std::list<std::unique_ptr<Node>> nodes;  // 实际上是链表管理
  std::vector<std::unique_ptr<Value>> values;
  Node* initializer_node_;  // 持有非输入初始化器的特殊节点
  // ...
};
```

所有权模型：Graph 是所有 Node 和 Value 的唯一所有者。Node 和 Value 之间的引用都是非拥有的原始指针（Node*、Value*），生命周期由 Graph 管理。这种设计避免了循环引用导致的内存泄漏。

### Node：双向循环链表与 CRTP

Node 结构体继承自 `Attributes<Node>`（CRTP 模式），并通过双向循环链表维护图中的顺序（F-053）：

```cpp
struct Node : public Attributes<Node> {  // CRTP
  // 双向循环链表指针
  Node* next_in_graph[2] = {nullptr, nullptr};  // [0]=prev, [1]=next

  // 输入输出
  Value* inputs_[MAX_INPUTS] = {};
  Value* outputs_[MAX_OUTPUTS] = {};
  int numInputs_ = 0;
  int numOutputs_ = 0;

  std::string name_;
  std::string op_type_;
  std::string domain_;
  std::string doc_string_;
  // ...
};
```

#### 哨兵节点模式

链表不使用 nullptr 作为终止标记，而是使用 `output_` 哨兵节点（sentinel node）：

```
遍历链表：

sentinel (output_)
    ↓ next_in_graph[1]
  Node1 ──→ Node2 ──→ Node3 ──→ back to sentinel
    ←──       ←──       ←──
    prev      prev      prev

// 前向遍历
for (Node* n = graph->output()->next_in_graph[kNextDirection];
     n != graph->output();  // 回到哨兵时结束
     n = n->next_in_graph[kNextDirection]) {
  // 处理节点 n
}
```

哨兵模式的优势：
- 不需要 nullptr 检查，简化插入/删除操作
- 空链表时 sentinel 指向自己（prev=next=sentinel）
- 头部/尾部插入只需修改哨兵周围的指针

#### CRTP Attributes

`Attributes<Node>` 是 CRTP（Curiously Recurring Template Pattern）基类，提供类型安全的属性访问：

```cpp
template <typename T>
class Attributes {
  std::unordered_map<std::string, unique_ptr<Attribute>> attributes_;

public:
  // 类型安全的属性访问
  T* self() { return static_cast<T*>(this); }

  float f(const std::string& name) const;
  int64_t i(const std::string& name) const;
  const std::string& s(const std::string& name) const;
  const Tensor* t(const std::string& name) const;
  Graph* g(const std::string& name) const;
  // ... 以及列表版本：fs(), is(), ss(), ts(), gs()

  T& f_(const std::string& name, float value);  // 设置属性，返回 *this 支持链式
  T& i_(const std::string& name, int64_t value);
  // ...
};
```

CRTP 使得属性设置方法返回 `Node&`（而非基类引用），支持链式调用且类型安全。

### Value：边/值与 use-def 链

Value 表示计算图中的边（数据流动），连接生产者节点到消费者节点（F-054, F-059）：

```cpp
struct Value {
  Node* node_;                 // 生产此值的节点（def）
  size_t offset_;              // 在生产节点输出列表中的索引
  size_t unique_;              // 全局唯一ID
  std::string unique_name_;    // 唯一名字
  int32_t elem_type_;          // 元素类型
  std::vector<Dimension> sizes_; // 形状维度
  std::unique_ptr<TypeProto> type_;  // 完整类型信息

  // Use-def 链：使用此值的消费者链表
  Use* uses_head = nullptr;

  // 核心操作：替换所有使用点
  void replaceAllUsesWith(Value* newValue);
  bool hasUses() const;
  Node* node() { return node_; }
};
```

#### Use 结构体与双向链表

每个使用点通过 Use 结构体表示，形成双向链表（F-059）：

```cpp
struct Use {
  Node* user;        // 消费者节点
  size_t offset;     // 在消费者输入中的索引
  Use* next = nullptr;
  Use* prev = nullptr;
};
```

Value 的所有消费者通过 `uses_head` 遍历：

```
Value Y
│
└── uses_head ──→ Use(user=Node2, offset=0) ←→ Use(user=Node3, offset=1)
                      │                              │
                      ↓                              ↓
              Node2.inputs_[0] = Y          Node3.inputs_[1] = Y
```

#### replaceAllUsesWith：图变换核心操作

`replaceAllUsesWith(Value* newValue)` 是图变换（优化、fusion等）中最常用的操作：

```cpp
void Value::replaceAllUsesWith(Value* newValue) {
  // 遍历 uses 链表
  for (Use* u = uses_head; u != nullptr; ) {
    Use* next = u->next;
    // 将用户的输入指针从 this 改为 newValue
    u->user->inputs_[u->offset] = newValue;
    // 从 this 的 uses 链表移除
    // 添加到 newValue 的 uses 链表
    // ...
    u = next;
  }
}
```

典型用途：
- **常量折叠**：将常量输入的节点替换为 Constant 节点
- **算子融合**：将 Conv+BN+Relu 替换为 FusedConv
- **死代码消除**：如果某个 Value 没有 use，可以删除其生产节点

### Dimension 三态

C++ IR 的 Dimension 用两个 bool 标志区分三种状态（F-055）：

```cpp
struct Dimension {
  bool is_unknown = true;
  bool is_int = false;
  int64_t dim = -1;
  std::string param;
};
```

| is_unknown | is_int | 状态 | 字段 |
|-----------|--------|------|------|
| true | - | 未知维度 | dim 和 param 无意义 |
| false | true | 静态维度 | dim = 整数值 |
| false | false | 符号维度 | param = 符号名（如 "batch"） |

### AttributeKind 枚举

12 种属性种类（F-056）：

```cpp
enum class AttributeKind {
  f, fs,    // float / float[]
  i, is,    // int / int[]
  s, ss,    // string / string[]
  t, ts,    // Tensor / Tensor[]
  g, gs,    // Graph / Graph[]（子图！）
  tp, tps   // TypeProto / TypeProto[]
};
```

### initializer_node_：非输入初始化器

IR >= 4 支持初始化器不在 graph.input 中声明（F-057）。这些"内部常量"在 C++ IR 中通过特殊的 Param 节点持有：

```cpp
class Graph {
  Node* initializer_node_;  // 特殊 Param 节点
  // ...
};
```

`addInitializerAndCreateValue()` 方法：
1. 创建 Tensor（初始器数据）
2. 创建对应的 Value
3. 将 Value 注册为 initializer_node_ 的输出
4. initializer_node_ 不出现在图节点列表中，但持有这些 Value 的所有权

### used_names_ 与 subgraph_bearing_nodes_

两个高效查找的辅助数据结构（F-058）：

```cpp
class Graph {
  // 名字 → 引用计数，O(1) 查重和自动命名
  std::unordered_map<std::string, int> used_names_;

  // 包含子图属性的节点集合，避免遍历所有节点
  std::unordered_set<Node*> subgraph_bearing_nodes_;
};
```

**used_names_**：
- 每次创建新名字时递增引用计数
- 自动生成唯一名字（如 "conv1" → "conv1_1" → "conv1_2"）
- O(1) 时间复杂度检查名字是否存在

**subgraph_bearing_nodes_**：
- 当节点的属性包含 GRAPH 或 GRAPHS 类型时，加入此集合
- 需要递归处理子图时（如形状推断、图变换），直接遍历此集合，无需遍历所有节点
- 这是一个性能优化：大多数节点不包含子图

## C++ IR vs Protobuf IR 对比

| 特性 | C++ IR (Graph/Node/Value) | Protobuf IR (GraphProto/NodeProto) |
|------|--------------------------|-----------------------------------|
| 连接方式 | 指针（Node*、Value*） | 字符串名字引用 |
| 遍历方式 | 双向循环链表 | repeated 字段顺序遍历 |
| 所有权 | unique_ptr + 原始指针 | proto 消息嵌套 |
| 属性访问 | CRTP 类型安全访问 | AttributeProto oneof 字段 |
| 图变换 | replaceAllUsesWith O(n) | 手动修改字符串名字 |
| 子图处理 | subgraph_bearing_nodes_ 索引 | 遍历所有 attribute 检查 |
| 使用场景 | C++ 内部（checker/optimizer/converter） | Python API / 跨语言交换 |
| 转换方式 | ir_pb_converter 双向转换 | 标准序列化/反序列化 |

## 关键洞察/反常识

1. **Python 端没有 Node/Graph 类**：Python 中 `model.graph.node[0]` 是 NodeProto（protobuf message），不是 C++ 的 Node 对象。Python 端的图操作本质上是操作嵌套的 protobuf 消息，效率不如 C++ IR。
2. **哨兵节点使得链表操作无分支**：双向循环链表配合哨兵节点，插入/删除操作不需要 if(nullptr) 检查，减少分支预测失败。
3. **CRTP 避免虚函数开销**：Attributes<Node> 使用 CRTP 而非虚函数实现类型安全的多态访问，零运行时开销。
4. **use-def 链是图优化的基础**：Value 的 uses 链表使得 replaceAllUsesWith、死代码消除、常量折叠等操作可以在 O(n) 时间完成，这是优化器性能的关键。
5. **initializer_node_ 是"隐形"节点**：它不出现在 graph.node 列表中，也不参与计算，只是用于持有非输入初始器的 Value 所有权。

## 关联概念

- [计算图模型](03-computation-graph.md) — Protobuf 层面的图结构，对比理解 C++ IR
- [算子定义与注册机制 OpSchema](05-operator-schema.md) — C++ checker/shape_inference 如何使用 OpSchema
- [形状推断实现](06-shape-inference.md) — 形状推断如何使用 C++ IR 遍历图
- [图遍历与变换实战](../examples/graph-transformation.md) — Python 端（Protobuf层面）的图操作对比
