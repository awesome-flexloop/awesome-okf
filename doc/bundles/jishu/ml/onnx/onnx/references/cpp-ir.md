---
type: reference
title: "common/ir.h：C++ IR 核心类"
description: "C++ IR 中 Graph/Node/Value/Dimension/AttributeKind/Use/Initializer 核心类定义，双向链表哨兵模式、CRTP Attributes、used_names_ 哈希表、subgraph_bearing_nodes_"
sources:
  - path: "external/libs/models/onnx/onnx/onnx/common/ir.h"
    facts: [F-052, F-053, F-054, F-055, F-056, F-057, F-058, F-059]
---

# common/ir.h：C++ IR 核心类

## 信源概述

| 信源 | 类型 | 行数 | 职责 |
|------|------|------|------|
| `onnx/common/ir.h` | C++ 头文件 | ~1100行 | C++ 中间表示（IR）核心类：Graph/Node/Value/Dimension/Use/Attributes |

## 关键事实登记

### F-052：三核心结构体与所有权模型

**信源**：`onnx/common/ir.h` L43-L55；L952-L953

C++ IR 基于三个核心结构体：
- **Graph**：计算图，拥有所有 Node 和 Value 的所有权（通过 `unique_ptr<Node>` 和 `unique_ptr<Value>`）
- **Node**：计算节点
- **Value**：值/边，连接节点的输出到输入

所有内部引用均使用原始指针（Node*、Value*），Graph 通过 unique_ptr 管理生命周期。

```
Graph (owns Nodes and Values via unique_ptr)
├── Node* nodes (raw pointers, referenced from unique_ptr storage)
│   ├── Value* inputs[]  ──→ Value (owned by Graph)
│   └── Value* outputs[] ──→ Value (owned by Graph)
└── Value* values (raw pointers)
    ├── Node* node_ (producer)
    └── Use* uses_head (linked list of consumers)
```

### F-053：Node 的双向循环链表与 CRTP Attributes

**信源**：`onnx/common/ir.h` L438-L468

```cpp
struct Node : public Attributes<Node> {  // CRTP 模式
  Node* next_in_graph[2];  // [0]=prev, [1]=next，双向链表
  Value* inputs_[MAX_INPUTS];
  Value* outputs_[MAX_OUTPUTS];
  int numInputs_;
  int numOutputs_;
  std::string name_;
  std::string op_type_;
  std::string domain_;
  std::string doc_string_;
  // ...
};
```

- Node 继承自 `Attributes<Node>`（CRTP，Curiously Recurring Template Pattern），提供类型安全的属性访问
- `next_in_graph[2]` 维护图中的双向循环链表，`output_` 节点作为哨兵节点（sentinel），链表不使用 nullptr 终止
- 节点通过链表顺序确定拓扑序

### F-054：Value 结构体与 replaceAllUsesWith

**信源**：`onnx/common/ir.h` L307-L436

```cpp
struct Value {
  Node* node_;           // 生产此值的节点指针
  size_t offset_;        // 在生产节点输出列表中的索引
  size_t unique_;        // 唯一ID
  int32_t elem_type_;    // 元素类型
  std::vector<Dimension> sizes_;  // 形状维度
  std::unique_ptr<TypeProto> type_;  // 完整类型信息
  std::string unique_name_;
  Use* uses_head;        // 使用此值的消费者链表头

  void replaceAllUsesWith(Value* newValue);
  bool hasUses() const;
  Node* node() const;
  // ...
};
```

`replaceAllUsesWith()` 遍历 uses 链表，将所有使用此值的节点输入重定向到新值，是图变换的核心操作。

### F-055：Dimension 三态表示

**信源**：`onnx/common/ir.h` L70-L79

```cpp
struct Dimension {
  bool is_unknown;
  bool is_int;
  int64_t dim;
  std::string param;
};
```

维度表示三种状态：
1. **未知维度**：`is_unknown=true`
2. **整数值维度**：`is_int=true, dim=具体值`
3. **符号参数维度**：`is_int=false, is_unknown=false, param="符号名"`（如 "batch_size"）

### F-056：AttributeKind 枚举

**信源**：`onnx/common/ir.h` L81-L96

```cpp
enum class AttributeKind {
  f, fs,    // float / float[]
  i, is,    // int / int[]
  s, ss,    // string / string[]
  t, ts,    // Tensor / Tensor[]
  g, gs,    // Graph / Graph[]
  tp, tps   // TypeProto / TypeProto[]
};
```

12 种属性种类，对应单值/列表的 float/int/string/tensor/graph/type_proto。CRTP Attributes 模板类提供 `f()`/`i()`/`s()`/`t()`/`g()` 等类型安全访问方法。

### F-057：initializer_node_ 与 addInitializerAndCreateValue

**信源**：`onnx/common/ir.h` L962-L965；L1078-L1097

```cpp
Node* initializer_node_;  // 独立的 Param 节点，持有不在图输入中的初始化器
```

- IR >= 4 支持初始化器不要求必须在 graph.input 中声明
- `initializer_node_` 是一个特殊的 Param 节点，所有非输入初始化器对应的 Value 作为其输出
- `addInitializerAndCreateValue()` 方法同时添加 Tensor 和对应的 Value，并将 Value 注册到 initializer_node_ 的输出

### F-058：used_names_ 哈希表与 subgraph_bearing_nodes_

**信源**：`onnx/common/ir.h` L983-L1005

```cpp
std::unordered_map<std::string, int> used_names_;
std::unordered_set<Node*> subgraph_bearing_nodes_;
```

- `used_names_`：哈希表，映射名字→引用计数，实现 O(1) 的名字唯一性检查和名字生成
- `subgraph_bearing_nodes_`：集合，跟踪包含子图属性（attribute 类型为 GRAPH 或 GRAPHS）的节点，避免遍历所有节点即可快速找到需要特殊处理的节点

### F-059：Use 结构体

**信源**：`onnx/common/ir.h` L291-L295

```cpp
struct Use {
  Node* user;    // 消费者节点指针
  size_t offset; // 在消费者输入列表中的索引
  Use* next;     // 链表下一个
  Use* prev;     // 链表上一个
};
```

Use 表示 Value 的一个使用点，通过双向链表链接（`next`/`prev`），构成同一 Value 的所有消费者链表。Value 的 `uses_head` 指向链表头。

## 内存布局图

```
Graph:
  nodes_: [Node] ←→ [Node] ←→ [Node] ←→ [sentinel=output_]
            │          │          │
            ↓          ↓          ↓
    outputs_: [V1,V2]  [V3]    [V4,V5,V6]
               ││       │        │││
               ││       ↓        │││
               ││    uses: V3←Node2.input[0]
               ││                │││
               │└──→ uses: V1←Node2.input[1]
               └───→ uses: V2←Node3.input[0]

Node (Attributes<Node> via CRTP):
  ┌─────────────────────────────┐
  │ Attributes<Node> base       │ ← 属性存储: f/i/s/t/g + CRTP访问器
  │ next_in_graph[2]            │ ← 双向循环链表指针
  │ inputs_[] / outputs_[]      │ ← Value* 数组
  │ op_type_ / name_ / domain_  │
  └─────────────────────────────┘

Value:
  node_ → Node* (producer)
  offset_ → index in producer outputs
  uses_head → Use ←→ Use ←→ Use (doubly-linked list of consumers)
```
