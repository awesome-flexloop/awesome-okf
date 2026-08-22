---
type: concept
title: "名称管理、元数据存储与废弃 API"
description: "NameAuthority 自动唯一命名策略、MetadataStore 双轨元数据（临时分析 vs 可序列化）、metadata_props 序列化传播、废弃 API 迁移指南（Input→ir.val）、便捷属性构造器工厂函数"
sources:
  references: [../references/io-metadata.md, ../references/core-entities.md]
  facts: [F-047, F-059, F-060, F-061, F-062, F-063]
---

# 名称管理、元数据存储与废弃 API

## 核心理解

onnx-ir 为图实体的命名和元数据管理提供了系统化机制：`NameAuthority` 保证所有节点和值都有唯一名称（匿名实体自动生成），`MetadataStore` 提供带失效标记的键值存储用于临时分析，`metadata_props` 字典用于可序列化到 ONNX proto 的字符串元数据。此外，便捷构造器（`tensor()`/`node()`/`val()`/`Attr*`）提供了比直接调用核心类更友好的 API。

## NameAuthority：名称治理

### 命名策略

`NameAuthority` 为没有显式名称的实体自动生成唯一名称（F-047）：

```python
class NameAuthority:
    _value_names: set[str]     # 已注册的值名称
    _node_names: set[str]      # 已注册的节点名称
    _value_counter: int = 0    # val_0, val_1, val_2, ...
    _node_counter: int = 0     # node_Add_0, node_MatMul_1, ...
```

| 实体类型 | 命名格式 | 示例 |
|----------|---------|------|
| Value（匿名） | `val_{counter}` | `val_0`, `val_1` |
| Node（匿名） | `node_{op_type}_{counter}` | `node_Add_0`, `node_Conv_1` |

### 命名规则

1. **已有名称不覆盖**：如果 value/node 在创建时已有 `name` 属性，NameAuthority 只注册名称到集合中防止重复，不改名
2. **重名检测**：尝试注册已存在的名称会抛出错误
3. **名称永不释放**：即使节点/值被从图中移除，名称仍保留在集合中，计数器单调递增
4. **Value 重命名同步**（F-027）：当 initializer 的 name 被修改时，自动同步更新 const_value.name 和 graph.initializers 字典

### 名称永不释放的设计理由

这是一个刻意选择：在图变换（特别是多 Pass 优化）中，释放名称可能导致：
- 新建对象获得已删除对象的旧名称，造成调试混淆
- 基于名称的外部引用（如其他模块的缓存）指向错误对象
- 序列化/反序列化后名称语义不一致

在模型规模（通常数万节点/值）下，计数器增长完全可接受。

## MetadataStore：临时分析元数据

`MetadataStore` 是一个带失效标记的字典，继承 `collections.UserDict`（F-059）：

```python
class MetadataStore(collections.UserDict):
    def __init__(self):
        super().__init__()
        self._invalid_keys: set[str] = set()
```

### 核心 API

| 方法 | 说明 |
|------|------|
| `invalidate(key)` | 标记键失效（加入 `_invalid_keys`） |
| `is_valid(key)` | 查询键是否有效（在 data 中且不在 invalid_keys 中） |
| `__setitem__(key, value)` | 写入时自动从 invalid_keys 移除该键 |
| `__bool__()` | data 非空**或**有 invalid_keys 时返回 True |

### 失效标记的用途

`invalidate()` 的设计意图是支持图分析 Pass 中的"标记-清除"模式：

```python
# 标记所有可以常量折叠的节点
for node in graph:
    if is_constant_foldable(node):
        node.meta["foldable"] = True
    else:
        node.meta.invalidate("foldable")  # 明确标记不可折叠

# 后续 Pass 检查
for node in graph:
    if node.meta.is_valid("foldable") and node.meta["foldable"]:
        fold_constant(node)
```

失效标记区分了"未设置"和"显式设置为无效"两种状态——单纯的 dict 中 key 不存在无法区分这两种语义。

### meta 不序列化

`meta`（MetadataStore）设计用于**中间分析过程**，在 `to_proto()` 序列化时**不会**被写入 protobuf。每次反序列化都会创建新的空 MetadataStore。

## metadata_props：可序列化元数据

所有 IR 核心实体都有 `metadata_props` 属性（`dict[str, str]`），用于存储需要序列化到 ONNX proto 的字符串元数据（F-060）。

### 哪些实体有 metadata_props？

| 实体 | meta | metadata_props |
|------|------|----------------|
| TensorBase（及所有Tensor子类） | ✅ | ✅ |
| Value | ✅ | ✅ |
| Node | ✅ | ✅ |
| Graph | ✅ | ✅ |
| GraphView | ✅ | ✅ |
| Model | ✅ | ✅ |
| Function | ✅ | ✅ |
| Attr | ✅ | ✅ |

在 ONNX proto 中，metadata_props 序列化为 `repeated StringStringEntryProto` 字段（键值对列表）。

### 双轨元数据的选择

```
                    元数据选择决策树
                         │
         ┌───────────────┴───────────────┐
         │ 这个数据需要随模型保存吗？       │
         └───────────┬───────────────────┘
                     │
              是 ────┴──── 否
              │             │
    ┌─────────┴──────┐  ┌──┴────────────┐
    │ metadata_props │  │ meta          │
    │ (dict[str,str])│  │ (MetadataStore)│
    │                │  │                │
    │ • 字符串键值对  │  │ • 任意Python   │
    │ • 序列化为proto │  │   对象         │
    │ • 跨反序列化持久│  │ • 支持失效标记  │
    │ • 所有实体都有  │  │ • 不序列化     │
    └────────────────┘  │ • 所有实体都有  │
                         └───────────────┘
```

典型用途：
- `metadata_props`：模型作者、版本标签、编译器标记（如 `"optimization_level": "3"`）
- `meta`：Pass 分析结果、中间计算缓存、遍历标记、调试信息

## Input() 废弃 API（F-061）

`Input()` 函数自 v0.1.9 起标记为 deprecated：

```python
def Input(name=None, shape=None, type=None, doc_string=None):
    """Deprecated. Use ir.val(...) instead."""
    warnings.warn(
        "Input() is deprecated, use ir.val(...) instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return Value(name=name, shape=shape, type=type, doc_string=doc_string)
```

迁移路径：`Input(name="x", shape=shape, dtype=dtype)` → `ir.val(name="x", shape=shape, dtype=dtype)`

`ir.val()` 是从 `_convenience._constructors` 导入的顶层便捷构造器（F-063），提供比直接调用 `Value()` 更友好的 API。

## 便捷属性构造器（F-062）

一系列工厂函数统一创建 `Attr` 实例，无需手动指定 `AttributeType`：

| 工厂函数 | 属性类型 | 等价 Attr 构造 |
|----------|---------|---------------|
| `AttrFloat32(v)` | FLOAT | `Attr("name", atype=FLOAT, value=float(v))` |
| `AttrInt64(v)` | INT | `Attr("name", atype=INT, value=int(v))` |
| `AttrString(v)` | STRING | `Attr("name", atype=STRING, value=str(v))` |
| `AttrTensor(v)` | TENSOR | `Attr("name", atype=TENSOR, value=v)` |
| `AttrGraph(v)` | GRAPH | `Attr("name", atype=GRAPH, value=v)` |
| `AttrFloat32s(*v)` | FLOATS | `Attr("name", atype=FLOATS, value=tuple(float(x) for x in v))` |
| `AttrInt64s(*v)` | INTS | `Attr("name", atype=INTS, value=tuple(int(x) for x in v))` |
| `AttrStrings(*v)` | STRINGS | `Attr("name", atype=STRINGS, value=tuple(str(x) for x in v))` |
| `AttrTensors(*v)` | TENSORS | `Attr("name", atype=TENSORS, value=tuple(v))` |
| `AttrGraphs(*v)` | GRAPHS | `Attr("name", atype=GRAPHS, value=tuple(v))` |
| `AttrSparseTensor(v)` | SPARSE_TENSOR | 稀疏张量属性 |
| `AttrSparseTensors(*v)` | SPARSE_TENSORS | 稀疏张量列表属性 |
| `AttrTypeProto(v)` | TYPE_PROTO | 类型引用属性 |
| `AttrTypeProtos(*v)` | TYPE_PROTOS | 类型引用列表属性 |
| `RefAttr(name, ref_attr_name, type)` | 引用属性 | `Attr(name, ref_attr_name=..., type=...)` |

### 构造时的强制类型转换

Attr 构造时执行以下强制类型转换（F-041）：
- INT/FLOAT → Python 原生 int/float（而非 numpy.int64/numpy.float32）
- INTS/FLOATS/STRINGS/TENSORS/GRAPHS/TYPE_PROTOS → tuple（而非 list，保证不可变）
- 类型不匹配的 getter 调用（如 `as_float()` 在 INT 属性上）抛出 TypeError

## 顶层便捷构造器（F-063）

从 `_convenience._constructors` 导入三个顶层函数：

| 函数 | 用途 |
|------|------|
| `ir.tensor(...)` | 创建 Tensor（比直接调用 Tensor() 更友好） |
| `ir.node(...)` | 创建 Node（比直接调用 Node() 更友好） |
| `ir.val(...)` | 创建 Value（替代废弃的 Input()） |

这些便捷构造器处理默认参数、类型推断等，推荐优先使用而非直接实例化核心类。
