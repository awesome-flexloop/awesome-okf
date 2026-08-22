---
type: concept
title: "核心实体：Model/Graph/Node/Value"
description: "IR 的核心实体关系模型——Value 作为图连接中心的一等公民、Node 的受控变异 API、Graph 的双向链表存储与拓扑排序、Model 的 opset 委托、Function 的 Graph 委托模式"
sources:
  references: [../references/core-entities.md]
  facts: [F-025, F-026, F-027, F-028, F-030, F-031, F-032, F-034, F-035, F-036, F-037, F-038, F-039, F-040, F-041, F-042]
---

# 核心实体：Model/Graph/Node/Value

## 核心理解

onnx-ir 的图结构以 **Value** 为连接中心，形成 Model → Graph → Node → Value 的层次关系。Value 维护 producer（0或1个生产节点）和 uses（消费者集合）双向引用，是 SSA（静态单赋值）风格的数据流边。Node 的 inputs/outputs 采用受控变异 API（不可直接赋值），Graph 使用双向链表存储节点以支持遍历中安全增删。

## 实体关系模型

```
┌─────────────────────────────────────────────────────────────┐
│                          Model                               │
│  ir_version / producer_name / domain / model_version         │
│  opset_imports ──────────委托──→ graph.opset_imports         │
│  _functions: dict[(domain,name,overload), Function]           │
│  graphs() → yield 主图 + 所有子图                             │
└──────────────────────────┬──────────────────────────────────┘
                           │ graph
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                          Graph                               │
│  继承 Sequence[Node]                                          │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ _nodes: DoublyLinkedSet[Node]  ← 双向链表，O(1)增删    ││
│  │ inputs:  GraphInputs  (MutableSequence[Value])          ││
│  │ outputs: GraphOutputs (MutableSequence[Value])          ││
│  │ initializers: GraphInitializers (dict-like, name→Value) ││
│  │ _name_authority: NameAuthority                          ││
│  └─────────────────────────────────────────────────────────┘│
│  append/extend/remove/insert_after/insert_before             │
│  sort() → Kahn算法+堆稳定拓扑排序                             │
│  clone() → 深拷贝                                            │
│  subgraphs()/all_nodes() → 递归遍历                           │
└───────┬──────────┬──────────┬──────────┬─────────────────────┘
        │ nodes    │ inputs   │ outputs  │ initializers
        ▼          ▼          ▼          ▼
   ┌─────────┐ ┌───────┐ ┌───────┐ ┌──────────────────────┐
   │  Node   │ │ Value │ │ Value │ │ Value(const_value=   │
   │ (多个)  │ │(图输入)│ │(图输出)│ │  TensorProtocol)     │
   └────┬────┘ └───────┘ └───┬───┘ └──────────────────────┘
        │                    │
        │ inputs/outputs     │ _is_graph_input/_is_graph_output
        ▼                    ▼
   ┌─────────────────────────────────────────────────────┐
   │                       Value                           │
   │  producer: Node | None   ← 0或1个生产节点              │
   │  uses: dict[Usage, None] ← 有序集合，支持同一节点多次引用│
   │  _is_graph_input / _is_graph_output / _is_initializer │
   │  type: TypeProtocol | None                            │
   │  shape: Shape | None                                  │
   │  replace_all_uses_with(replacement) → SSA替换         │
   └─────────────────────────────────────────────────────┘
```

## Value：图连接中心

Value 是 IR 中最重要的实体，统一表示图输入、图输出、节点输出、初始化值（F-025）。

### Producer-Uses 双向引用

每个 Value 有：
- **0 或 1 个 producer**：生产该值的 Node。无 producer 时，该值必须是图输入或 Initializer
- **N 个 uses**：消费该值的节点集合，使用 `dict[Usage, None]`（有序字典）存储以支持同一值在同一节点被多次引用（如 `Add(x, x)` 中 x 出现两次）

```python
# Value 的角色标记（F-026）
value._is_graph_input    # 只能由 Graph._GraphIO 设置
value._is_graph_output   # 只能由 Graph._GraphIO 设置
value._is_initializer    # 只能由 Graph.GraphInitializers 设置

# 公开查询
value.is_graph_input()
value.is_graph_output()
value.is_initializer()
```

### 受控重命名（F-027）

`Value.name` setter 包含重命名逻辑：如果是 initializer，先检查新名称不冲突，再同步更新 `const_value.name`、弹出 graph.initializers 旧条目并插入新条目；禁止将 initializer 名称设为 None。

### SSA 风格值替换（F-028）

```python
value.replace_all_uses_with(replacement, replace_graph_outputs=False)
```

遍历所有 uses，调用每个 consumer 的 `replace_input_with()`。当值是图输出且 `replace_graph_outputs=False` 时抛出 ValueError，防止意外替换图输出。

### 算术运算符重载（F-029）

`Value` 继承 `WithArithmeticMethods` mixin，通过类级别 `_magic_handler`（ClassVar）实现算术运算符（`+`, `-`, `*`, `/`, 负号及反向版本）。框架作者可通过 `set_value_magic_handler()` 注入自定义 handler 实现算子录制（详见 [06-tape-transform.md](06-tape-transform.md)）。

## Node：算子节点

### 初始化行为（F-030）

Node 初始化时：
1. `domain` 为 `"ai.onnx"` 时归一化为 `""`（空串表示标准 ONNX 域）
2. `inputs` 存储为不可变 tuple
3. `outputs` 在初始化时创建（默认1个输出），每个输出的 `_producer` 设为 self、`_index` 设为对应序号
4. `attributes` 包装为 `_graph_containers.Attributes`
5. 初始化后自动将自身注册为所有 input values 的 usage

### 受控变异（F-031）

Node 的 inputs/outputs **不可直接赋值**（setter 抛出 AttributeError），必须通过受控 API 修改：

```python
# 修改输入
node.resize_inputs(new_size)           # 调整输入数量
node.replace_input_with(index, value)  # 替换指定位置的输入

# 修改输出
node.resize_outputs(new_size)          # 调整输出数量
# 缩小时被移除的输出不能有 uses，否则报错
```

这种设计防止了直接修改 tuple 导致的图结构不一致。

### 节点关系查询（F-032）

- `predecessors()`：去重的前驱节点（按 dict 有序去重）
- `successors()`：去重的后继节点
- `prepend(nodes)` / `append(nodes)`：委托给 graph 的 `insert_before`/`insert_after`
- `op_identifier()`：返回 `(domain, op_type, overload)` 三元组

### 多设备与分片（F-033）

Node 支持多设备配置：
- `device_configurations`：存储 `NodeDeviceConfiguration` 元组
- `shard(value, configuration, axis, num_shards, ...)`：记录张量分片信息
- `sharding_of(value)`：按对象身份匹配返回分片规格
- `set_pipeline_stage(configuration, stage)`：设置流水线阶段

## Graph：计算图

### 存储结构（F-034）

Graph 继承 `Sequence[Node]`，核心存储：
- `_nodes: DoublyLinkedSet[Node]`：双向链表有序集合，支持安全迭代中变异
- `inputs: GraphInputs`（MutableSequence[Value]）
- `outputs: GraphOutputs`（MutableSequence[Value]）
- `initializers: GraphInitializers`（dict-like，name→Value 映射）
- `_name_authority: NameAuthority`：管理自动命名

### 构造流程（F-035）

```
1. 注册 inputs 的名称到 NameAuthority
2. 注册 initializers 的名称到 NameAuthority
3. self.extend(nodes) 添加节点：
   a. 每个节点设置 graph 引用
   b. 节点自动命名（匿名节点→node_{op_type}_{counter}）
   c. 节点输出值自动命名（匿名值→val_{counter}）
```

### 变异操作

| 方法 | 说明 |
|------|------|
| `append(node)` | 尾部追加节点 |
| `extend(nodes)` | 批量追加 |
| `remove(nodes, safe=False)` | 删除节点，safe 模式事务性检查 |
| `insert_after(after, node)` | 在指定节点后插入 |
| `insert_before(before, node)` | 在指定节点前插入 |
| `sort()` | Kahn 算法+堆稳定拓扑排序 |
| `clone()` | 深拷贝 |
| `subgraphs()` | 递归 yield 所有子图（Graph 属性中的图） |
| `all_nodes()` | 递归 yield 所有节点（含子图中的） |

### 安全删除（F-037）

`remove(safe=True)` 执行三项检查，**先全部检查再执行删除**（事务性保证）：
1. 被移除节点的输出不被其他保留节点使用
2. 被移除节点的输出不是图输出
3. 断开所有 input 引用（`replace_input_with(i, None)`）

### 拓扑排序（F-036）

`sort()` 使用稳定拓扑排序算法（参考 MedallionTopologicalSort）：
1. 将子图中的所有节点视为包含子图属性节点的前驱
2. 用优先队列（heapq）按负原始索引排序以获得稳定顺序
3. 排序后对每个子图分别 reversed 后 extend 回 graph

### GraphView 只读视图（F-038）

`GraphView` 是只读视图：
- inputs/outputs 存储为 tuple（不可变）
- nodes 存储为 tuple（不可变）
- initializers 为 dict（可反映底层变异）
- 不拥有节点，但反映底层 Graph 的变异
- 可序列化为 ONNX，可用于创建 Model（创建时拓扑固定、不复制）

## Model：模型顶层

Model 包含（F-039）：
- `graph: Graph`：主计算图
- `ir_version`、`producer_name`、`producer_version`、`domain`、`model_version`、`doc_string`
- `_functions: dict[(domain,name,overload), Function]`：函数定义
- `device_configurations` 元组
- `opset_imports`：委托给 `graph.opset_imports`
- `graphs()`：yield 主图和所有子图（递归）

## Function：函数定义

Function 采用 **Graph 委托模式**（F-040）：
- 内部包装一个 `Graph` 对象（`_graph`）
- 通过委托模式暴露图操作方法：`inputs`/`outputs`/`__getitem__`/`__len__`/`__iter__`/`append`/`extend`/`remove`/`insert_after`/`insert_before`/`sort`/`subgraphs`/`all_nodes`/`clone`
- 额外有 `attributes`（函数参数定义，支持 RefAttr 引用属性）
- `identifier()` 返回 `(domain, name, overload)` 三元组

## Attr：属性统一表示

Attr 统一表示普通属性和引用属性（F-041）：
- `ref_attr_name` 非 None 时为 RefAttr（引用属性，在 Function 中使用）
- 构造时强制类型转换：INT/FLOAT→Python int/float，列表类型→tuple
- 类型安全 getter：`as_float`/`as_int`/`as_string`/`as_tensor`/`as_graph`/`as_floats`/`as_ints`/`as_strings`/`as_tensors`/`as_graphs`

## TypeProtocol 类型层次（F-042/F-043）

```
TypeProtocol（接口）
├── _TensorTypeBase
│   ├── TensorType（dtype: DataType, shape: Shape | None）
│   └── SparseTensorType（elem_type: TensorType）
└── _RecursiveTypeBase（持有 elem_type）
    ├── SequenceType（elem_type: TypeProtocol）
    └── OptionalType（elem_type: TypeProtocol）
```

`TypeAndShape` 是 dataclass，包含 `type: TypeProtocol | None` 和 `shape: Shape | None`，用于构造 TypeProto 属性值。
