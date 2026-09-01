---
type: concept
title: Table 与 Atom
description: PyTables 的 Table 结构化表类、Cols/Column 列访问机制、Atom 类型描述符系统、行追加/读取/修改与 where() 条件查询
tags: [pytables, table, atom, column, col, row, query, where, dtype, structured-array]
generated:
  by: reference_agent/trae-glm
  at: 2026-08-22T15:00:00Z
verified:
  by: "process:seven-concepts-v"
  at: 2026-08-22T15:30:00Z
status: stable
stale_after: 2027-12-31
sources:
  - tables/table.py
  - tables/atom.py
  - tables/description.py
  - tables/conditions.py
---

# Table 与 Atom

Table 是 PyTables 中用于存储**异构结构化数据**的叶子节点类型，类似关系数据库表或 pandas DataFrame，但数据持久化在 HDF5 文件中。Atom 是描述数据元素类型的描述符系统，为数组和表的列提供类型信息。

## Table 类

`Table` 定义在 table.py:383，继承自 `tableextension.Table`（Cython 扩展层）和 `Leaf`。

### 表结构描述（Description）

创建 Table 时必须提供**表结构描述**，支持以下形式：

1. **IsDescription 子类**：通过继承 `IsDescription` 类，在类体中声明 `Col` 实例作为列定义
2. **字典**：键为列名，值为 Col 实例或类型字符串
3. **Description 实例**：复用已有表的 description 属性
4. **NumPy dtype**：结构化 NumPy dtype
5. **NumPy 结构化数组实例**：使用其 dtype 作为描述，并可直接注入数据

### IsDescription 声明方式

```python
import tables as tb

class Event(tb.IsDescription):
    """粒子事件记录"""
    event_id = tb.Int32Col(pos=0)       # 32位整数，位置0
    energy = tb.Float64Col(pos=1)       # 64位浮点，位置1
    detector = tb.StringCol(16, pos=2)  # 16字节字符串，位置2
    timestamp = tb.Time64Col(pos=3)     # 时间类型，位置3
```

`pos` 参数控制列在表中的位置，未指定位置的列按字母顺序排列在已定位列之后。列支持嵌套：嵌套列使用另一个 `IsDescription` 子类作为值。

### Col 列类型

`Col` 类（description.py:41）继承自 `Atom`，用于声明非嵌套列。主要类型：

| Col 类型 | 对应 Atom | 说明 |
|----------|----------|------|
| `Int8Col`/`Int16Col`/`Int32Col`/`Int64Col` | Int 系列 | 有符号整数 |
| `UInt8Col`/`UInt16Col`/`UInt32Col`/`UInt64Col` | UInt 系列 | 无符号整数 |
| `Float32Col`/`Float64Col` | Float 系列 | 浮点数 |
| `Complex64Col`/`Complex128Col` | Complex 系列 | 复数 |
| `BoolCol` | BoolAtom | 布尔值 |
| `StringCol(itemsize)` | StringAtom | 定长字节串 |
| `Time32Col`/`Time64Col` | Time 系列 | 时间戳 |
| `EnumCol(enum, ...)` | EnumAtom | 枚举类型 |

所有 Col 构造函数支持 `shape`（列形状，默认 `()` 为标量）、`dflt`（默认值）、`pos`（位置）、`attrs`（属性元数据）参数。

### Table 核心属性

| 属性 | 说明 |
|------|------|
| `nrows` | 当前行数 |
| `shape` | 表形状，始终为 `(nrows,)` |
| `rowsize` | 单行字节大小 |
| `dtype` | 对应的 NumPy 结构化 dtype |
| `description` | Description 实例，描述表结构 |
| `cols` | Cols 列访问器 |
| `row` | Row 行写入器实例 |
| `colpathnames` | 所有列的路径名列表（含嵌套列） |
| `coldflts` | 各列默认值字典 |
| `autoindex` | 是否自动维护索引（可读写） |
| `size_in_memory` | 全部加载到内存的字节数 |

## Cols 与 Column：列访问

### Cols 容器

`Cols` 类（table.py:3250）是列的容器，通过 `table.cols` 访问：

- 支持自然命名访问列：`table.cols.event_id`
- 嵌套列返回子 Cols 实例：`table.cols.nested.subfield`
- 支持切片读写：`table.cols.energy[0:100]`
- 提供 `_f_col(colname)` 方法按名称获取列

| 属性 | 说明 |
|------|------|
| `_v_colnames` | 直接子列名称列表 |
| `_v_colpathnames` | 所有列路径名列表（含嵌套） |
| `_v_desc` | 关联的 Description 实例 |

### Column 列对象

`Column` 类（table.py:3519）代表单个非嵌套列的访问器：

| 属性/方法 | 说明 |
|-----------|------|
| `name` | 列名称 |
| `pathname` | 列完整路径名 |
| `dtype` | 列的 NumPy dtype |
| `type` | PyTables 类型字符串 |
| `shape` | 列形状 `(nrows,) + col_shape` |
| `table` | 所属 Table 实例 |
| `index` | 关联的 Index 实例（未索引返回 None） |
| `attrs` | 列属性集合 |
| `create_index(...)` | 为该列创建索引 |
| `reindex()` | 重新索引该列 |
| `__getitem__/__setitem__` | 通过切片读写列数据 |

### 列数据访问示例

```python
# 读取整个列
energies = table.cols.energy[:]

# 读取部分行
first_100 = table.cols.energy[0:100]

# 按条件通过列索引加速查询（需要先创建索引）
table.cols.energy.create_index()
```

## 行追加：Row 对象

`table.row` 属性返回 `tableextension.Row` 实例，用于逐行追加数据：

```python
row = table.row
for i in range(1000):
    row['event_id'] = i
    row['energy'] = random_energy()
    row['detector'] = b'DET01'
    row['timestamp'] = time.time()
    row.append()           # 将当前行加入缓冲区
table.flush()              # 刷新缓冲区写入磁盘
```

Row 对象的关键点：
- 通过 `__setitem__` 设置字段值（字段名或索引）
- `append()` 将当前行缓冲追加到表
- 数据先写入 I/O 缓冲区，`table.flush()` 时真正写入 HDF5
- 也支持通过 `table.append(rows)` 一次性追加 NumPy 结构化数组或记录列表

### Table.append() 批量追加

```python
def append(self, rows: list | np.ndarray) -> None:
```

接受 NumPy 结构化数组或记录字典列表，批量追加多行。效率高于逐行 append。

## 数据读取

### Table.read() 全量/范围读取

```python
def read(self, start=None, stop=None, step=None, field=None, ...):
```

读取指定行范围的数据，返回 NumPy 结构化数组。

| 参数 | 说明 |
|------|------|
| `start`, `stop`, `step` | 行切片参数 |
| `field` | 只读指定列（列名字符串或列名列表） |

### Table.iterrows() 行迭代

```python
def iterrows(self, start=None, stop=None, step=None, ...):
```

逐行迭代，每行返回一个 Row 记录对象，可通过 `row['colname']` 访问字段。适合内存无法容纳全表时的流式处理。

### Table.read_coordinates() 坐标读取

```python
def read_coordinates(self, coords, field=None):
```

按行号数组读取指定行。

### Table.read_sorted() 排序读取

```python
def read_sorted(self, sortby, checkCSI=False, ...):
```

按指定列排序后读取数据，利用索引加速。

## 条件查询

### where() 条件迭代

```python
def where(
    self,
    condition: str,
    condvars: dict | None = None,
    start=None,
    stop=None,
    step=None,
) -> Iterator[tableextension.Row]:
```

`where()` 是最常用的查询方法，返回满足条件的行迭代器。

**condition 参数**：字符串表达式，支持 NumPy/Numexpr 语法的比较与逻辑运算：
- 比较：`<`, `<=`, `==`, `!=`, `>=`, `>`
- 逻辑：`&`（与）、`|`（或）、`~`（非），注意位运算符优先级，需加括号
- 列名直接作为变量使用
- 字符串字面量在 Python 3 中需要使用字节串（如 `b"DET01"`）

```python
# 查询能量大于 100 且探测器为 DET01 的事件
results = [row['event_id'] for row in table.where(
    '(energy > 100) & (detector == b"DET01")'
)]
```

**索引加速**：若条件中的列已创建索引，`where()` 自动使用索引缩小搜索范围，性能显著提升。将最严格的索引条件放在最左侧可获得最佳性能。

**condvars 参数**：显式指定变量映射，避免依赖命名空间查找：
```python
table.where('energy > min_e', condvars={'min_e': 100})
```

### get_where_list() 获取行索引

```python
def get_where_list(self, condition, condvars=None, ...) -> np.ndarray:
```

返回满足条件的所有行号（int64 数组），不读取实际数据。适合先确定行号再批量读取。

### read_where() 条件读取

```python
def read_where(self, condition, condvars=None, field=None, ...) -> np.ndarray:
```

直接返回满足条件的行数据数组，等价于 `table.read_coordinates(table.get_where_list(...))`。

### append_where() 条件追加

```python
def append_where(self, table, condition, condvars=None, ...):
```

将满足条件的行追加到另一个表。

## Atom 类型描述符

`Atom` 类（atom.py:187）是数组元素的类型描述符，定义存储在 CArray/EArray/VLArray 中元素的类型、大小和形状。

### Atom 的 kind（类型族）

| kind | 类型类 | 说明 | 支持的 itemsize（字节） |
|------|--------|------|----------------------|
| `bool` | BoolAtom | 布尔 | 1 |
| `int` | IntAtom/Int8/16/32/64Atom | 有符号整数 | 1,2,4,8 |
| `uint` | UIntAtom/UInt8/16/32/64Atom | 无符号整数 | 1,2,4,8 |
| `float` | FloatAtom/Float32/64Atom | 浮点数 | 4,8 |
| `complex` | ComplexAtom/Complex64/128Atom | 复数 | 8,16 |
| `string` | StringAtom | 定长字节串 | 自定义 |
| `time` | Time32Atom/Time64Atom | 时间戳 | 4,8 |
| `enum` | EnumAtom | 枚举类型 | 基础类型决定 |
| `vlstring` | VLStringAtom | 变长字节串（VLArray） | 可变 |
| `vlunicode` | VLUnicodeAtom | 变长 Unicode 串 | 可变 |
| `object` | ObjectAtom | Python 对象（pickle 序列化） | 可变 |

### Atom 工厂方法

不直接使用构造函数，推荐通过工厂方法创建：

| 工厂方法 | 说明 |
|----------|------|
| `Atom.from_sctype(sctype, shape=(), dflt=None)` | 从 NumPy 标量类型创建 |
| `Atom.from_dtype(dtype, dflt=None)` | 从 NumPy dtype 创建 |
| `Atom.from_kind(kind, itemsize, shape=(), dflt=None)` | 从类型族名称和大小创建 |

### Atom 核心属性

| 属性 | 说明 |
|------|------|
| `kind` | 类型族字符串（如 'int'、'float'） |
| `itemsize` | 单个元素字节大小 |
| `shape` | 原子形状（标量为 `()`） |
| `dtype` | 对应的 NumPy dtype |
| `nbytes` | 单个原子字节数（itemsize * shape 元素数） |
| `default` | 默认值 |

### split_type() 工具函数

```python
def split_type(type_: str) -> tuple[str, int | None]:
```

将 PyTables 类型字符串拆分为（kind, itemsize）元组：
- `split_type('int32')` → `('int', 4)`
- `split_type('string')` → `('string', None)`
- `split_type('float64')` → `('float', 8)`

## 条件编译：conditions.py

`conditions.compile_condition()` 将字符串条件表达式编译为可重用的 `CompiledCondition` 对象，包含：
- `index_variables`：可用于索引的变量集合
- `index_expressions`：索引表达式列表（变量、操作符、范围）
- `string_expression`：传给 Numexpr 的表达式字符串

Table 的 `where()` 和 `get_where_list()` 内部使用此编译结果进行索引优化。

## 相关概念

- [节点层次体系](01-node-hierarchy.md)
- [压缩与索引](03-compression-indexing.md)
- [PyTables 简介](00-introduction.md)
- [基础操作示例](../examples/hdf5-basics.md)
