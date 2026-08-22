---
type: concept
title: "内部 Graph API 设计：make_node / set_dtype / get_shape"
description: "tf2onnx 内部图表示的 API 设计：Node 类对 ONNX NodeProto 的封装、Graph 类的索引体系与图操作方法（make_node/make_const/set_dtype/get_shape/set_body_graph_as_attr）、子图管理与大模型外部存储"
sources:
  references: [../references/graph-rewriter.md]
  facts: [F-022, F-023, F-024, F-025, F-026]
  insights: [I-003]
---

# 内部 Graph API 设计：make_node / set_dtype / get_shape

## 核心理解

tf2onnx 的内部图表示不是从零设计的自定义 IR，而是在 ONNX Protobuf 之上构建的 Node/Graph 包装类。这些包装类提供了丰富的图操作 API（创建节点、替换输入、遍历消费者、传播形状和类型），使得图变换操作（重写、映射、优化）便捷且安全。理解 Graph API 是编写自定义重写器、自定义算子处理器和自定义优化器的前提。

**设计哲学**：目标即 IR——ONNX Protobuf 本身就是中间表示，Node/Graph 只是提供操作便利性。

## Node 类：ONNX NodeProto 的包装

Node 类是 ONNX `NodeProto` 的 Python 包装器，每个 Node 实例对应图中的一个算子节点。

```python
class Node(object):
    def __init__(self, node, graph=None):
        self._node = node       # 底层 ONNX NodeProto（onnx.NodeProto）
        self._input = list(node.input)   # 输入张量名列表（可修改）
        self._output = list(node.output)  # 输出张量名列表（可修改）
        self._attr = {}          # 属性字典（从 proto 提取，修改后同步回）
        self.graph = graph       # 所属 Graph 引用
        self.skip_conversion = False  # 是否已被重写器/映射器处理
```

### 属性操作 API

| 方法 | 说明 |
|------|------|
| `get_attr(name, default=None)` | 获取属性值，返回 Python 原生类型 |
| `set_attr(name, value)` | 设置属性值（自动转换为 ONNX AttrProto） |
| `get_attr_int(name, default=0)` | 获取整数属性 |
| `get_attr_str(name, default="")` | 获取字符串属性 |
| `get_attr_float(name, default=0.0)` | 获取浮点数属性 |
| `get_attr_list(name, default=None)` | 获取列表属性 |

### 输入操作 API

| 方法 | 说明 |
|------|------|
| `replace_input(idx, new_input_name)` | 替换第 idx 个输入为新张量名 |
| `replace_all_inputs(old_name, new_name)` | 将所有等于 old_name 的输入替换为 new_name |
| `insert_input(idx, input_name)` | 在位置 idx 插入输入 |
| `remove_input(idx)` | 删除第 idx 个输入 |

### 类型判断 API

| 方法 | 说明 |
|------|------|
| `is_const()` | 是否为常量节点（type == "Const"） |
| `is_graph_input()` | 是否为图输入（Placeholder） |
| `is_while()` | 是否为 Loop/While 算子 |
| `is_if()` | 是否为 If 算子 |
| `type` 属性 | 获取/设置节点算子类型名 |
| `name` 属性 | 获取/设置节点名称 |

### 示例：在处理函数中修改节点

```python
@tf_op("RealDiv", onnx_op="Div")
class RealDiv:
    @classmethod
    def version_6(cls, ctx, node, **kwargs):
        # node.type 已经被改为 "Div"（由 onnx_op kwarg 处理）
        # RealDiv 在 opset 6+ 直接映射为 Div（支持广播），无需额外操作
        pass
```

## Graph 类：图操作门面

Graph 类是整个图操作的核心入口，维护多个索引以加速图遍历和修改。

### 核心数据结构

```python
class Graph(object):
    def __init__(self, nodes, outputs, op_name_counts, dtypes, shapes, ...):
        # 三大索引
        self._nodes_by_name = {}          # Dict[str, Node]
        self._output_to_node_name = {}    # Dict[str, str]  (张量名 → 产出节点名)
        self._output_to_consumers = {}    # Dict[str, List[Node]] (张量名 → 消费者列表)
        
        # 形状与类型
        self.shapes = shapes or {}        # Dict[str, List[int]] (张量名 → 形状)
        self._dtypes = dtypes or {}       # Dict[str, int] (张量名 → ONNX dtype 整数)
        
        # 子图管理
        self.contained_graphs = {}        # Dict[str, Graph] (子图名 → 子图)
        
        # 配置
        self._opset = opset_version
        self._target = target
        self._name_counter = {}           # 节点名计数器（避免重名）
```

### 三大索引详解

**为什么需要三个索引？** 图变换中最常见的操作是：
1. 通过节点名找到节点（_nodes_by_name）
2. 知道一个张量，找到产出它的节点（_output_to_node_name）——反向追踪
3. 知道一个张量，找到所有消费它的节点（_output_to_consumers）——正向传播

以"将张量 A 替换为张量 B"为例，需要：
- 找到所有以 A 为输入的节点（通过 _output_to_consumers[A]）
- 在这些节点中将 A 替换为 B
- 更新 _output_to_consumers

没有第三个索引（消费者列表），每次替换都需要遍历全图。

### 节点创建 API

| 方法 | 说明 |
|------|------|
| `make_node(op_type, inputs, attr=None, name=None, ...)` | 创建新节点并添加到图中，返回 Node |
| `make_const(name, np_array, ...)` | 创建常量节点，从 numpy 数组生成 |
| `remove_node(node)` | 删除节点（从图中移除） |
| `copy_node(node, new_name=None)` | 复制节点 |

**make_node 示例**：

```python
# 在两个节点之间插入一个 Transpose
def insert_transpose(g, node, input_idx, perm):
    # 获取原始输入张量名
    original_input = node.input[input_idx]
    # 创建唯一名称
    transpose_name = g.get_unique_name(original_input + "_transpose")
    transpose_output = transpose_name + ":0"
    # 创建 Transpose 节点
    transpose_node = g.make_node(
        "Transpose",
        inputs=[original_input],
        outputs=[transpose_output],
        name=transpose_name,
        perm=perm
    )
    # 替换原节点的输入
    node.replace_input(input_idx, transpose_output)
    # 设置形状和类型
    g.set_shape(transpose_output, g.get_shape(original_input))
    g.set_dtype(transpose_output, g.get_dtype(original_input))
    return transpose_node
```

### 形状与类型 API

| 方法 | 说明 |
|------|------|
| `get_shape(tensor_name)` | 获取张量形状（List[int] 或 None） |
| `set_shape(tensor_name, shape)` | 设置张量形状 |
| `get_dtype(tensor_name)` | 获取张量数据类型（ONNX dtype 整数，如 onnx.TensorProto.FLOAT） |
| `set_dtype(tensor_name, dtype)` | 设置张量数据类型 |
| `set_shape_dtype(tensor_name, shape, dtype)` | 同时设置形状和类型 |

**形状传播**：在图变换中，新创建的节点必须正确设置输出形状和类型，否则后续优化器可能出错。

### 子图管理 API

| 方法 | 说明 |
|------|------|
| `set_body_graph_as_attr(node, attr_name, subgraph)` | 将子图设置为节点的属性（用于 If/Loop/Scan） |
| `get_body_graphs(node)` | 获取节点的所有子图 |

**子图处理**：If/Loop/Scan 等控制流算子包含 body 子图（then_branch/else_branch/loop_body），这些子图是独立的 Graph 对象，存储在 `contained_graphs` 字典中。重写器和映射器需要递归处理子图。

### 图输出管理

| 方法 | 说明 |
|------|------|
| `outputs` 属性 | 获取/设置图输出节点列表 |
| `reset_outputs()` | 在构造时为输出添加 Identity 保护 |

**Identity 保护机制**（F-024）：Graph 构造时自动为每个输出添加 Identity 节点，防止转换过程中输出节点被重命名或删除导致输出名称变化。

```python
# 构造时执行的保护逻辑
for output in self.outputs:
    identity_name = self.get_unique_name(output + "_identity")
    identity_output = identity_name + ":0"
    identity_node = self.make_node(
        "Identity",
        inputs=[output],
        outputs=[identity_output],
        name=identity_name
    )
    # 将图输出改为 Identity 的输出
    # 原始输出节点可以被安全修改/删除
```

### 模型输出 API

| 方法 | 说明 |
|------|------|
| `make_model(doc_string="", producer_name="tf2onnx", ...)` | 构建最终的 ONNX ModelProto |
| `serialize_to_string()` | 序列化为 protobuf 二进制 |
| `topological_sort(nodes)` | 拓扑排序 |

**make_model 流程**（F-025）：
1. 调用 `make_graph()` 将所有节点序列化为 GraphProto
2. 设置 producer_name/version
3. 添加 opset_imports（主 domain + ML domain + extra_opset）
4. 根据 opset 设置 IR 版本（opset ≥ 15 → IR 8，否则 IR 7 等）
5. （可选）调用 ONNX optimizer
6. 返回 ModelProto

## ExternalTensorStorage：大模型外部存储

对于超过 2GB 的大模型，protobuf 有大小限制。tf2onnx 提供 `ExternalTensorStorage` 类支持外部张量存储：

```python
class ExternalTensorStorage(object):
    def __init__(self):
        self._data = {}  # 张量名 → raw_data bytes
        self._threshold = 1024  # 元素数阈值
        self._file_counter = 0
    
    def add_tensor(self, name, array):
        """将大张量添加到外部存储"""
        if array.size > self._threshold:
            filename = f"tensor_{self._file_counter}.bin"
            self._data[name] = (filename, array.tobytes())
            self._file_counter += 1
            return True
        return False
```

超过 1024 元素的常量张量被提取到外部 `.bin` 文件，原张量设置 `data_location = EXTERNAL` 并通过 `external_data` 字段引用文件名。使用时通过 `large_model=True` 启用：

```python
model_proto, ext_storage = tf2onnx.convert.from_saved_model(
    "saved_model_dir",
    large_model=True  # 启用外部张量存储
)
# 保存时需要同时保存外部文件
onnx.save_model(model_proto, "model.onnx")
```

## 图操作的常见模式

### 模式一：单节点修改

```python
# 修改节点属性
node.set_attr("perm", [0, 3, 1, 2])  # NHWC -> NCHW
# 节点类型重命名
node.type = "BatchNormalization"
```

### 模式二：插入节点

```python
# 在 node 的第 idx 个输入前插入 Cast
cast_output = g.get_unique_name(node.input[idx] + "_cast") + ":0"
g.make_node("Cast", inputs=[node.input[idx]], outputs=[cast_output],
            to=onnx.TensorProto.FLOAT)
node.replace_input(idx, cast_output)
g.set_dtype(cast_output, onnx.TensorProto.FLOAT)
```

### 模式三：子图替换（重写器）

```python
# 将一个子图（多个节点）替换为单个 ONNX 算子
for match in matcher.match_ops(ops):
    old_nodes = [match.get_op(name) for name in [...]]
    new_node = g.make_node("OnnxOp", inputs=[...], outputs=[...])
    for old in old_nodes:
        g.replace_all_inputs(old.output[0], new_node.output[0])
        old.skip_conversion = True
```

### 模式四：拓扑排序

```python
# 图修改后必须拓扑排序，确保节点按依赖顺序排列
g.topological_sort(g.get_nodes())
```

## update_proto：内存状态同步回 Protobuf

Node 和 Graph 的修改都在 Python 对象层面进行，最终需要同步回 ONNX protobuf：

```python
def update_proto(self):
    """将 Graph 内部状态（Node 的修改）同步回 ONNX protobuf"""
    nodes_proto = []
    for node in self._nodes:
        # 同步输入输出列表
        node._node.input[:] = node._input
        node._node.output[:] = node._output
        # 同步属性
        for key, value in node._attr.items():
            # 将 Python 值转为 ONNX AttrProto
            node._node.attribute[key].CopyFrom(make_attribute(key, value))
        nodes_proto.append(node._node)
    return nodes_proto
```

`make_model` 调用 `update_proto` 获取最终的 NodeProto 列表。

## 关联概念

- [tf2onnx 整体架构](00-overall-architecture.md) — 理解 Graph 对象如何在三阶段流水线中传递
- [转换流水线详解](01-conversion-pipeline.md) — 理解 Graph 创建时机和各阶段对图的修改
- [装饰器驱动的版本化算子注册表](02-versioned-opset-registry.md) — 理解 version_N 方法中 ctx/Node 参数的 API
- [图重写与模式匹配](03-graph-rewriting.md) — 理解重写器中如何使用 Graph API 进行子图替换
- [ONNX 图优化器](05-optimizers.md) — 理解优化器如何在 Graph 对象上执行图变换
- [数据布局、类型系统与 Target 适配](06-data-layout-types.md) — 理解 set_dtype/set_shape 在布局转换中的作用
