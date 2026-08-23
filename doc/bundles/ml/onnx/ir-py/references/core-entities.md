---
type: reference
title: "_core.py 核心实体：Model/Graph/Node/Value/Tensor 系列"
description: "onnx_ir._core 模块核心实体类源码信源登记——Tensor 张量体系、Value/Node/Graph/Model/Function 图结构、Attr 属性、Type 类型系统"
sources:
  - path: "src/onnx_ir/_core.py"
    facts: [F-002, F-003, F-009, F-011, F-012, F-013, F-014, F-015, F-016, F-017, F-018, F-019, F-020, F-021, F-023, F-024, F-025, F-026, F-027, F-028, F-029, F-030, F-031, F-032, F-033, F-034, F-035, F-036, F-037, F-038, F-039, F-040, F-041, F-042, F-043, F-060, F-061, F-062]
---

# _core.py 核心实体：Model/Graph/Node/Value/Tensor 系列

## 信源概述

| 信源 | 类型 | 行数 | 职责 |
|------|------|------|------|
| `src/onnx_ir/_core.py` | Python 实现 | ~5300行 | IR 核心实体定义：Tensor 张量体系、SymbolicDim/Shape 形状系统、Value/Node/Graph/Model/Function 图结构、Attr 属性、TypeProtocol 类型层次、WithArithmeticMethods 算术混入、MetadataStore 元数据、便捷构造器 |

`_core.py` 是 ir-py 最大、最核心的模块，约 5300 行，涵盖从张量数据表示到完整计算图模型的全部 IR 实体。文件开头明确声明 protobuf-free 原则：

```python
# _core.py L6-L9
# NOTE: The classes defined in this file should NOT contain any methods like
# to_onnx/from_protobuf. Those should go to serde.py to keep the IR free of
# protobuf dependencies.
```

开发者注释还禁止导入 `pathlib`（因性能原因），要求使用 `os.path`（F-003）。

## 关键事实登记

### F-011/F-012：TensorBase 抽象基类

**信源**：`src/onnx_ir/_core.py` L122-L274

`TensorBase` 是所有张量类的抽象基类，继承 `abc.ABC`、`TensorProtocol`、`PrettyPrintable`，使用 `__slots__` 定义四个字段：

```python
class TensorBase(abc.ABC, TensorProtocol, PrettyPrintable):
    __slots__ = ("_doc_string", "_metadata", "_metadata_props", "_name")
```

公共属性和方法：
- `name` / `doc_string`：名称和文档字符串
- `size`：元素数（`math.prod(shape.numpy())`）
- `nbytes`：字节数（`math.ceil(dtype.itemsize * size)` 处理4位/2位类型）
- `metadata_props`：可序列化元数据（`dict[str, str]`）
- `meta`：临时分析用 `MetadataStore`（不序列化）
- `tofile()` / `display()`：导出和显示方法

### F-013/F-014：Tensor 内存张量（零拷贝）

**信源**：`src/onnx_ir/_core.py` L435-L555

`Tensor` 是不可变具体张量，包装原始数据（numpy/DLPack兼容对象），零拷贝构造：

```python
class Tensor(TensorBase):
    def __init__(self, array: ArrayCompatible, dtype: DataType | None = None, ...):
        # 不做任何数据复制，仅存储引用
        # numpy scalar 自动转为 ndarray
        # 非 numpy 原生 dtype 通过 ml_dtypes 做 view
```

实现 `__array__` 和 `__dlpack__`/`__dlpack_device__` 协议，支持 numpy 和 DLPack 零拷贝互操作。

### F-016/F-017/F-018：ExternalTensor 内存映射张量

**信源**：`src/onnx_ir/_core.py` L616-L1019

`ExternalTensor` 通过 `mmap.mmap` 实现内存映射外部张量数据，包含三层安全检查：
1. 字符串路径遍历防护（`..` 检测）
2. 符号链接 `realpath` 检查
3. 硬链接检测（`nlink > 1` 拒绝）

```python
class ExternalTensor(TensorBase):
    def __init__(self, location: str, dtype: DataType, shape: Shape,
                 offset: int = 0, length: int | None = None, ...):
        # location/offset/length/dtype/shape 不可变
        # base_dir 可变（setter），path = os.path.join(base_dir, location)
```

提供 `invalidate()` 标记数据损坏、`release()` 关闭 mmap。`tofile()` 优先使用 Linux `os.copy_file_range` 内核态拷贝。

### F-019：StringTensor 字符串张量

**信源**：`src/onnx_ir/_core.py` L1022-L1110

`StringTensor` 专门处理字符串张量：
- `dtype` 固定为 `DataType.STRING`
- 不支持 `tobytes()` 和 DLPack
- 通过 `string_data()` 返回 `Sequence[bytes]`
- `nbytes` 对所有字符串长度求和

### F-020：LazyTensor 延迟求值张量

**信源**：`src/onnx_ir/_core.py` L1113-L1230

`LazyTensor` 接受一个返回 `TensorProtocol` 的 callable（thunk）：
- `cache` 参数控制是否缓存结果（默认 False 即每次重新求值）
- 访问 `__array__`/`__dlpack__`/`numpy()`/`tobytes()` 时触发 `_evaluate()`

### F-021：PackedTensor 亚字节打包张量

**信源**：`src/onnx_ir/_core.py` L1233-L1383

`PackedTensor`（v0.1.2新增）存储2位/4位类型的打包格式数据：
- `dtype` 必须是 INT2/UINT2/INT4/UINT4/FLOAT4E2M1
- `numpy_packed()` 返回打包的 uint8 数组
- `numpy()` 返回解包后的数组

### F-023/F-024：SymbolicDim 与 Shape

**信源**：`src/onnx_ir/_core.py` L1386-L2023

`SymbolicDim` 是不可变符号维度，内部存储 `_value`（str/None）和懒初始化的 `_expr_cache`（sympy.Expr），支持算术运算（`+`, `-`, `*`, `//`, `/`, `%`, `neg`, `ceil`, `floor`, `trunc`）。

`Shape` 支持冻结（`freeze()`）后不可修改，提供：
- `rank()` / `numpy()`（要求全静态维度）
- `is_static(dim?)` / `is_dynamic(dim?)` / `is_unknown_dim(dim)`
- `evaluate(bindings)` 用具体值替换符号
- `simplify()` / `free_symbols()`
- 维度合并规则：int优先于SymbolicDim，有名字的SymbolicDim优先于None，同名字保留当前值

### F-025-F-029：Value 图连接中心

**信源**：`src/onnx_ir/_core.py` L2879-L3402, L3460-L3473

`Value` 统一表示图/函数/节点的输入输出：
- 每个 Value 有 0 或 1 个 producer Node；无 producer 时必须是图输入或 Initializer
- 使用 `dict[Usage, None]`（有序字典）存储 uses 集合，支持同一值在同一节点被多次引用
- 三个布尔标记 `_is_graph_input`/`_is_graph_output`/`_is_initializer`，只能由 Graph 类设置
- `name` setter 包含重命名逻辑：同步更新 `const_value.name` 和 graph.initializers 字典
- `replace_all_uses_with(replacement, replace_graph_outputs=False)` 实现 SSA 风格引用替换
- 继承 `WithArithmeticMethods` mixin，通过类级 `_magic_handler` 支持算术运算符重载

```python
# F-061: Input() 自 v0.1.9 起 deprecated
def Input(name=None, shape=None, type=None, doc_string=None):
    """Deprecated. Use ir.val(...) instead."""
    warnings.warn(...)
    return Value(name=name, shape=shape, type=type, doc_string=doc_string)
```

### F-030-F-033：Node 算子节点

**信源**：`src/onnx_ir/_core.py` L2063-L2768

`Node` 初始化行为：
- `domain` 为 `"ai.onnx"` 时归一化为 `""`
- `inputs` 存储为不可变 tuple，不可直接赋值，必须通过 `resize_inputs()` + `replace_input_with()` 修改
- `outputs` 在初始化时创建（默认1个输出），每个输出的 `_producer` 设为 self，`_index` 设为对应序号
- 初始化后自动将自身注册为所有 input values 的 usage
- `outputs` 同样不可直接赋值，通过 `resize_outputs()` 修改

关键方法：
- `predecessors()` / `successors()`：去重的前驱/后继节点
- `prepend(nodes)` / `append(nodes)`：委托给 graph 的 insert_before/insert_after
- `op_identifier()`：返回 `(domain, op_type, overload)` 三元组
- 多设备配置：`device_configurations`、`shard()`、`sharding_of()`、`set_pipeline_stage()`

### F-034-F-038：Graph 与 GraphView

**信源**：`src/onnx_ir/_core.py` L3512-L4240

`Graph` 继承 `Sequence[Node]`：
- 节点存储在 `_linked_list.DoublyLinkedSet[Node]`（双向链表有序集合），支持安全迭代中变异
- inputs/outputs 包装为 `_graph_containers.GraphInputs/GraphOutputs`（MutableSequence）
- initializers 包装为 `_graph_containers.GraphInitializers`（dict-like）
- `_name_authority` 管理自动命名

构造流程：先注册 inputs 和 initializers 的名称到 NameAuthority，再通过 `self.extend(nodes)` 添加节点。

变异方法：`append`/`extend`/`remove`/`insert_after`/`insert_before`、`sort()`（Kahn 算法+堆稳定拓扑排序）、`clone()` 深拷贝、`subgraphs()`/`all_nodes()` 递归遍历。

`remove(safe=True)` 安全模式三项检查：
1. 被移除节点的输出不被其他保留节点使用
2. 被移除节点的输出不是图输出
3. 断开所有 input 引用

`GraphView` 是只读视图，inputs/outputs 存储为 tuple，nodes 存储为 tuple，initializers 为 dict，反映底层变异但不可修改。

### F-039：Model 模型

**信源**：`src/onnx_ir/_core.py` L4243-L4375

`Model` 包含：
- `graph`（Graph）
- `ir_version`、`producer_name`、`producer_version`、`domain`、`model_version`、`doc_string`
- `_functions`：以 `(domain, name, overload)` 为 key 的 dict
- `device_configurations` 元组
- `opset_imports` 委托给 `graph.opset_imports`
- `graphs()` 方法 yield 主图和所有子图

### F-040：Function 函数定义

**信源**：`src/onnx_ir/_core.py` L4553-L4865

`Function` 内部包装一个 `Graph` 对象（`_graph`），通过委托模式暴露图操作方法（`inputs`/`outputs`/`append`/`extend`/`remove`/`sort`/`clone` 等）。额外有 `attributes`（函数参数定义，支持 RefAttr）和 `identifier()` 返回 `(domain, name, overload)`。

### F-041/F-062：Attr 属性与便捷构造器

**信源**：`src/onnx_ir/_core.py` L4868-L5290

`Attr` 统一表示普通属性和引用属性（`ref_attr_name` 非 None 时为 RefAttr）：
- 构造时对 INT/FLOAT 强制转为 Python int/float（而非 numpy 类型）
- 对 INTS/FLOATS/STRINGS/TENSORS/GRAPHS/TYPE_PROTOS 强制转为 tuple
- 提供类型安全 getter：`as_float`/`as_int`/`as_string`/`as_tensor`/`as_graph`/`as_floats`/`as_ints`/`as_strings`/`as_tensors`/`as_graphs`

便捷属性构造器（工厂函数）：`AttrFloat32`、`AttrInt64`、`AttrString`、`AttrTensor`、`AttrGraph`、`AttrFloat32s`、`AttrInt64s`、`AttrStrings`、`AttrTensors`、`AttrGraphs`、`AttrSparseTensor`、`AttrSparseTensors`、`AttrTypeProto`、`AttrTypeProtos`、`RefAttr()`。

### F-042/F-043：TypeProtocol 类型层次

**信源**：`src/onnx_ir/_core.py` L2784-L2876, L5258-L5266

类型系统类层次：
- `TypeProtocol`：所有类型的协议接口
- `_TensorTypeBase` → `TensorType`、`SparseTensorType`
- `_RecursiveTypeBase` → `SequenceType`、`OptionalType`（递归类型持有 `elem_type`）
- `TypeAndShape`（dataclass）：包含 `type: TypeProtocol | None` 和 `shape: Shape | None`

### F-060：双轨元数据

**信源**：`src/onnx_ir/_core.py` L184-L203, L2508-L2527, L3016-L3335, L4017-L4037, L4191-L4207, L4311-L4331, L4685-L4700, L4946-L4954

所有 IR 核心实体（TensorBase/Value/Node/Graph/GraphView/Model/Function/Attr）都有两个元数据接口：
- `meta`（MetadataStore）：用于中间分析，不序列化
- `metadata_props`（dict[str,str]）：序列化到 ONNX proto
