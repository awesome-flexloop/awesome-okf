---
type: concept
title: "张量体系：五种 Tensor 与零拷贝/延迟/mmap 设计"
description: "TensorBase 抽象基类定义统一协议，派生出 Tensor(内存)/ExternalTensor(mmap)/StringTensor(字符串)/LazyTensor(延迟)/PackedTensor(亚字节打包) 五种实现，外加 serde 层的 TensorProtoTensor(protobuf零拷贝)，支持 numpy/DLPack 互操作"
sources:
  references: [../references/core-entities.md, ../references/tape-serde.md, ../references/enums-types.md]
  facts: [F-011, F-012, F-013, F-014, F-015, F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-009]
---

# 张量体系：五种 Tensor 与零拷贝/延迟/mmap 设计

## 核心理解

onnx-ir 不将"张量"等同于 numpy 数组，而是通过 `TensorBase` 抽象基类定义统一的 `TensorProtocol` 协议，派生出**五种**具体张量实现，外加序列化层的 `TensorProtoTensor`。所有实现统一支持 numpy 互操作（`__array__`/`numpy()`）和 DLPack 互操作（StringTensor 除外），使用场景通过类型选择而非配置参数区分。

## 张量类层次

```
TensorBase(ABC, TensorProtocol, PrettyPrintable)  ← __slots__: 4个字段
├── Tensor                → 内存 numpy 数组（零拷贝包装）
├── ExternalTensor        → mmap 内存映射外部数据
├── StringTensor          → 字符串张量（bytes 序列）
├── LazyTensor            → 延迟求值（thunk callable）
└── PackedTensor          → 2位/4位亚字节打包格式

serde.py:
└── TensorProtoTensor     → 零拷贝包装 onnx.TensorProto
```

## TensorBase 公共协议

所有张量类型继承自 `TensorBase`，共享以下属性和方法（F-011/F-012）：

| 成员 | 类型 | 说明 |
|------|------|------|
| `name` | str | 张量名称 |
| `doc_string` | str | 文档字符串 |
| `dtype` | DataType | 数据类型（抽象属性，子类实现） |
| `shape` | Shape | 形状（抽象属性，子类实现） |
| `size` | int | 元素总数（`math.prod(shape.numpy())`） |
| `nbytes` | int | 字节数（亚字节类型用 `math.ceil(dtype.itemsize * size)`） |
| `metadata_props` | dict[str,str] | 可序列化元数据 |
| `meta` | MetadataStore | 临时分析元数据（不序列化） |
| `numpy()` | np.ndarray | 转为 numpy 数组（抽象方法） |
| `tobytes()` | bytes | 序列化为小端字节序 |
| `tofile()` | None | 写入文件 |
| `display()` | None | 格式化显示 |

`__slots__` 定义四个字段：`_doc_string`, `_metadata`, `_metadata_props`, `_name`。

## Tensor：内存张量（零拷贝）

`Tensor` 是不可变的具体张量，包装原始数据（F-013/F-014）。

**核心设计：零拷贝构造**

```python
class Tensor(TensorBase):
    def __init__(self, array: ArrayCompatible, dtype: DataType | None = None, ...):
        # 1. 不做任何数据复制，仅存储引用
        # 2. numpy scalar 自动转为 ndarray
        # 3. 非 numpy 原生 dtype 通过 _maybe_view_np_array_with_ml_dtypes()
        #    用 ml_dtypes 做 view（不复制）
```

**numpy/DLPack 互操作**：
- `__array__()`：允许 `np.array(tensor)` 直接获取 numpy 视图
- `__dlpack__()`/`__dlpack_device__()`：支持 DLPack 零拷贝跨框架共享

**字节序列化**（F-015）：`tobytes()` 将张量序列化为小端字节序，通过 `_create_np_array_for_byte_representation()` 处理：
- 4位类型：`pack_4bitx2`（两个4位值打包进1字节）
- 2位类型：`pack_2bitx4`（四个2位值打包进1字节）
- 自动处理大端→小端转换

## ExternalTensor：mmap 外存张量

`ExternalTensor` 通过 `mmap.mmap` 实现内存映射外部张量数据，专为大模型设计（F-016/F-017/F-018）。

**三层安全防护**（F-016）：

```python
class ExternalTensor(TensorBase):
    def _load(self):
        # 1. 路径遍历防护：拒绝包含 ".." 的路径
        # 2. 符号链接检查：os.path.realpath 检测，防止符号链接绕过
        # 3. 硬链接检测：os.stat().st_nlink > 1 时拒绝
        #    （防止通过硬链接绕过路径遍历防护）
        ...
        self._mmap = mmap.mmap(fd, length, offset=offset)
```

**可变性与生命周期**（F-017）：
- `location`/`offset`/`length`/`dtype`/`shape`：不可变（初始化后不可修改）
- `base_dir`：可变（setter），`path = os.path.join(base_dir, location)`
- `invalidate()`：标记数据损坏/删除，后续访问报错
- `release()`：关闭 mmap 并释放引用

**高效文件拷贝**（F-018）：`tofile()` 优先使用 Linux `os.copy_file_range` 内核态拷贝（零用户态 buffer），回退到 1MiB 分块用户态拷贝，支持对端文件对象的 `fileno/flush/tell/seek` 检测。

**4位/2位类型处理**：对亚字节类型，先以 uint8 读入再 unpack。

## StringTensor：字符串张量

`StringTensor` 专门处理字符串数据（F-019）：

| 特性 | 值 |
|------|-----|
| `dtype` | 固定为 `DataType.STRING` |
| `tobytes()` | 不支持（抛异常） |
| DLPack | 不支持 |
| 数据访问 | `string_data() → Sequence[bytes]` |
| `nbytes` | 所有字符串长度之和 |

## LazyTensor：延迟求值张量

`LazyTensor` 接受一个返回 `TensorProtocol` 的 callable（thunk），实现真正的图构建期延迟求值（F-020）：

```python
class LazyTensor(TensorBase):
    def __init__(self, thunk: Callable[[], TensorProtocol], cache: bool = False):
        self._thunk = thunk
        self._cache = cache
        self._cached: TensorProtocol | None = None

    def _evaluate(self):
        if self._cache and self._cached is not None:
            return self._cached
        result = self._thunk()
        if self._cache:
            self._cached = result
        return result
```

- `cache=False`（默认）：每次访问重新求值
- `cache=True`：首次访问后缓存结果
- 触发求值的方法：`__array__`/`__dlpack__`/`numpy()`/`tobytes()`/`nbytes`

## PackedTensor：亚字节打包张量

`PackedTensor`（v0.1.2新增）原生存储2位/4位类型的打包格式数据（F-021）：

```python
class PackedTensor(TensorBase):
    # dtype 必须是 INT2/UINT2/INT4/UINT4/FLOAT4E2M1
    def numpy_packed(self) -> np.ndarray:
        """返回打包的 uint8 数组（存储格式）"""
    def numpy(self) -> np.ndarray:
        """返回解包后的数组（使用格式）"""
```

这避免了亚字节类型存储时50%-75%的空间浪费。

## TensorProtoTensor：Protobuf 零拷贝包装

定义在 `serde.py` 中（F-022），直接包装 `onnx.TensorProto`，不立即转为 numpy 数组：

**改进于 onnx.numpy_helper.to_array**：
1. 优先使用 `raw_data` 字段配合 `np.frombuffer` **零拷贝**
2. 按不同 data field 分别处理：int32_data/int64_data/float_data/double_data/uint64_data/string_data
3. 自动处理 bfloat16/float8/int4/int2 等类型的 view 转换

## 非 numpy 原生类型支持

27种 DataType 中，以下11种不被 numpy 原生支持，通过 `ml_dtypes` 包提供（F-009）：

```python
_NON_NUMPY_NATIVE_TYPES = frozenset({
    DataType.BFLOAT16,
    DataType.FLOAT8E4M3FN, DataType.FLOAT8E4M3FNUZ,
    DataType.FLOAT8E5M2,  DataType.FLOAT8E5M2FNUZ,
    DataType.FLOAT8E8M0,
    DataType.INT4, DataType.UINT4, DataType.FLOAT4E2M1,
    DataType.INT2, DataType.UINT2,
})
```

## 设计权衡：为什么不是一个统一的 Tensor 类？

直觉上张量应该有一个统一的构造函数或工厂方法，按参数决定存储方式。但不同存储策略的生命周期管理差异极大：

| 张量类型 | 生命周期特点 |
|----------|-------------|
| Tensor | 持有 numpy 引用，简单值语义 |
| ExternalTensor | mmap 文件描述符/invalidate/release，三层安全检查 |
| StringTensor | bytes 序列，无 DLPack，nbytes 特殊计算 |
| LazyTensor | thunk 闭包/cache 策略，访问触发求值 |
| PackedTensor | packed/unpacked 双视图，亚字节类型专用 |
| TensorProtoTensor | proto 内存生命周期，零拷贝 frombuffer |

统一到一个类会导致大量条件分支和状态膨胀。分类型设计让每个类职责单一，Protocol 统一对外接口。
