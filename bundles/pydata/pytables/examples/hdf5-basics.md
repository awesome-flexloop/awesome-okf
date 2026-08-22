---
type: example
title: PyTables 基础操作
description: 从创建 HDF5 文件、创建 Group/Array/Table、写入数据、追加行、条件查询到压缩设置和读取为 NumPy/pandas 的完整代码示例
tags: [pytables, hdf5, tutorial, example, create, write, query, numpy, pandas]
generated:
  by: reference_agent/trae-glm
  at: 2026-08-22T15:00:00Z
verified:
  by: "process:seven-concepts-v"
  at: 2026-08-22T15:30:00Z
status: stable
stale_after: 2027-12-31
sources:
  - tables/file.py
  - tables/table.py
  - tables/array.py
  - tables/earray.py
  - tables/filters.py
---

# PyTables 基础操作

本示例覆盖 PyTables 的核心操作流程：创建文件、创建分组和节点、写入数据、追加行、条件查询、配置压缩、读取为 NumPy/pandas。

## 前置条件

```python
import numpy as np
import tables as tb
```

确保已安装 PyTables：`pip install tables`

## 1. 创建 HDF5 文件

使用 `tb.open_file()` 创建新文件。`mode='w'` 表示写入模式（已存在则覆盖）。

```python
import os
import numpy as np
import tables as tb

# 清理旧文件（如果存在）
if os.path.exists('tutorial.h5'):
    os.remove('tutorial.h5')

# 创建新 HDF5 文件，设置根级默认压缩过滤器
filters = tb.Filters(complevel=5, complib='blosc2:zstd', shuffle=True, fletcher32=True)
h5file = tb.open_file('tutorial.h5', mode='w', title='PyTables Tutorial', filters=filters)

print(f"文件名: {h5file.filename}")
print(f"打开模式: {h5file.mode}")
print(f"标题: {h5file.title}")
print(f"HDF5 版本: {tb.hdf5_version}")
```

## 2. 创建 Group（分组）

分组类似目录，用于组织节点。

```python
# 在根下创建 detector 分组
detector_group = h5file.create_group('/', 'detector', 'Detector data group')

# 创建嵌套分组（createparents=True 自动创建中间路径）
meta_group = h5file.create_group('/', 'metadata', 'Metadata group')
run_group = h5file.create_group(meta_group, 'runs', 'Run information')

# 使用自然命名访问分组
print(h5file.root.detector)          # /detector (Group) 'Detector data group'
print(h5file.root.metadata.runs)     # /metadata/runs (Group) 'Run information'
```

## 3. 创建 Array（基本数组）

Array 是不分块、不可扩展的数组节点。

```python
# 创建 Array：直接传入 NumPy 数组
calibration = np.array([1.02, 0.98, 1.01, 0.99], dtype=np.float64)
arr_calib = h5file.create_array(
    h5file.root.detector,    # 父分组
    'calibration',           # 节点名
    calibration,             # 数据
    'Calibration constants'  # 标题
)

print(f"Array 路径: {arr_calib._v_pathname}")
print(f"Array 形状: {arr_calib.shape}")
print(f"Array 数据: {arr_calib[:]}")
```

## 4. 创建 EArray（可扩展数组）

EArray 支持沿单一维度追加数据。创建时可扩展维度设为 0。

```python
# 创建可扩展的浮点数数组，形状 (0, 3) 表示沿第0维扩展，每行3个元素
atom = tb.Float32Atom()
waveform = h5file.create_earray(
    detector_group,
    'waveform',
    atom,
    shape=(0, 3),           # 第0维为0表示可扩展
    title='Waveform data (expandable)',
    filters=filters          # 继承根过滤器
)

# 追加数据
waveform.append(np.array([[1.0, 2.0, 3.0]], dtype=np.float32))
waveform.append(np.array([[4.0, 5.0, 6.0], [7.0, 8.0, 9.0]], dtype=np.float32))
print(f"EArray 当前形状: {waveform.shape}")  # (3, 3)
print(f"EArray 全部数据:\n{waveform[:]}")
```

## 5. 创建 CArray（分块压缩数组）

CArray 是固定大小但支持压缩的分块数组。

```python
# 创建分块数组：形状固定，数据通过 __setitem__ 写入
carr_atom = tb.Int16Atom()
carr = h5file.create_carray(
    detector_group,
    'pedestal',
    carr_atom,
    shape=(100, 16),         # 100行 x 16通道的固定大小
    title='Pedestal values',
    filters=filters
)
# 写入数据
pedestal_data = np.random.randint(-10, 10, size=(100, 16), dtype=np.int16)
carr[:] = pedestal_data
print(f"CArray 形状: {carr.shape}")
print(f"压缩器: {carr.filters.complib}")
```

## 6. 创建 VLArray（变长数组）

VLArray 的每一行可以有不同长度。

```python
vlarr = h5file.create_vlarray(
    detector_group,
    'hits',
    tb.Int32Atom(),
    title='Hit channels per event (variable length)'
)
# 追加变长行
vlarr.append([1, 5, 12])        # 第0行：3个通道
vlarr.append([3, 8])            # 第1行：2个通道
vlarr.append([0, 1, 2, 3, 4])   # 第2行：5个通道
print(f"VLArray 行数: {vlarr.nrows}")
for i in range(vlarr.nrows):
    print(f"  行 {i}: {vlarr[i]}")
```

## 7. 创建 Table（结构化表）

Table 存储异构结构化数据，类似数据库表或 pandas DataFrame。

### 方式一：使用 IsDescription 类定义结构

```python
class Particle(tb.IsDescription):
    """粒子探测记录"""
    event_id = tb.Int32Col(pos=0)          # 事件ID
    energy = tb.Float64Col(pos=1)          # 能量 (keV)
    position = tb.Float32Col(shape=(3,), pos=2)  # 3维位置 (x,y,z)
    detector_name = tb.StringCol(16, pos=3)      # 探测器名称
    is_valid = tb.BoolCol(pos=4)           # 是否有效

# 创建表
table = h5file.create_table(
    h5file.root,
    'particles',
    Particle,
    'Particle detection records',
    expectedrows=10000,     # 预估行数，用于优化chunk大小
    filters=filters
)
print(f"Table 列: {table.cols._v_colnames}")
```

### 方式二：使用字典定义结构

```python
desc = {
    'run_id': tb.Int32Col(),
    'start_time': tb.Float64Col(),
    'duration': tb.Float32Col(),
    'n_events': tb.Int64Col(),
}
run_table = h5file.create_table(run_group, 'summary', desc, 'Run summary table')
```

## 8. 向 Table 追加行

### 逐行追加（使用 Row 对象）

```python
particle = table.row
for i in range(1000):
    particle['event_id'] = i
    particle['energy'] = np.random.exponential(100.0)
    particle['position'] = np.random.randn(3).astype(np.float32)
    particle['detector_name'] = b'DET01' if i % 2 == 0 else b'DET02'
    particle['is_valid'] = (particle['energy'] > 1.0)
    particle.append()     # 将行加入缓冲区

# 向 run_table 追加数据
run = run_table.row
run['run_id'] = 1
run['start_time'] = 0.0
run['duration'] = 3600.0
run['n_events'] = 1000
run.append()

# 刷新缓冲区，写入磁盘
table.flush()
run_table.flush()

print(f"Particles 行数: {table.nrows}")
print(f"Run summary 行数: {run_table.nrows}")
```

### 批量追加（使用 NumPy 结构化数组）

```python
batch_data = np.zeros(500, dtype=table.dtype)
batch_data['event_id'] = np.arange(1000, 1500)
batch_data['energy'] = np.random.exponential(100.0, 500)
batch_data['position'] = np.random.randn(500, 3).astype(np.float32)
batch_data['detector_name'] = [b'DET01'] * 500
batch_data['is_valid'] = True
table.append(batch_data)
table.flush()
print(f"追加后 Particles 行数: {table.nrows}")
```

## 9. 读取 Table 数据

### 读取全部数据为 NumPy 结构化数组

```python
# 全量读取
all_particles = table.read()
print(f"全部数据类型: {all_particles.dtype}")
print(f"前3个事件ID: {all_particles['event_id'][:3]}")
```

### 读取指定列

```python
energies = table.read(field='energy')
print(f"能量数组形状: {energies.shape}, 均值: {energies.mean():.2f}")

# 读取多列
subset = table.read(field=['event_id', 'energy', 'is_valid'])
print(f"子集 dtype: {subset.dtype.names}")
```

### 读取行范围

```python
first_10 = table.read(start=0, stop=10)
print(f"前10行: {len(first_10)} 条记录")
```

### 逐行迭代

```python
count = 0
for row in table.iterrows(stop=5):
    print(f"  事件 {row['event_id']}: 能量={row['energy']:.2f}, 探测器={row['detector_name']}")
    count += 1
```

## 10. 条件查询（where）

### where() 迭代器

```python
# 查询能量大于 200 的有效事件
high_energy = []
for row in table.where('(energy > 200) & (is_valid == True)'):
    high_energy.append(row['event_id'])
print(f"高能量有效事件数: {len(high_energy)}")

# 使用 condvars 显式传递变量
threshold = 300.0
very_high = [
    row['event_id']
    for row in table.where('energy > thresh', condvars={'thresh': threshold})
]
print(f"能量 > {threshold} 的事件数: {len(very_high)}")

# 字符串条件（Python 3 需要字节串）
det02_events = [
    row['event_id']
    for row in table.where('detector_name == b"DET02"')
]
print(f"DET02 事件数: {len(det02_events)}")
```

### get_where_list() 获取行号

```python
# 获取满足条件的行索引
valid_indices = table.get_where_list('is_valid == True')
print(f"有效事件索引: 共 {len(valid_indices)} 个，前5个: {valid_indices[:5]}")
```

### read_where() 直接读取数据

```python
# 直接读取满足条件的数据
det02_data = table.read_where('detector_name == b"DET02"')
print(f"DET02 数据量: {len(det02_data)} 条")
```

## 11. 创建索引加速查询

```python
# 为常用查询列创建索引
table.cols.energy.create_index(
    optlevel=9,
    kind='full',      # 完全索引（精确行定位）
    filters=tb.Filters(complevel=1, complib='blosc2')
)
table.cols.detector_name.create_index(kind='medium')

# 验证索引已创建
print(f"energy 列是否有索引: {table.cols.energy.index is not None}")
print(f"索引类型: {table.cols.energy.index.kind}")

# 现在相同的 where 查询会自动使用索引加速
result = table.get_where_list('(energy > 200) & (detector_name == b"DET01")')
print(f"索引加速查询结果数: {len(result)}")
```

## 12. 使用 Cols/Column 访问列数据

```python
# 通过 cols 属性访问列
col_energy = table.cols.energy
print(f"energy 列类型: {col_energy.dtype}")
print(f"energy 列形状: {col_energy.shape}")

# 列切片读取
first_100_energies = table.cols.energy[:100]
print(f"前100个能量值形状: {first_100_energies.shape}")

# 嵌套列访问（如果有嵌套结构）
# pos_x = table.cols.position.x  # 嵌套列示例
```

## 13. 不同压缩配置对比

```python
# 不压缩
none_filters = tb.Filters(complevel=0)

# Zlib 压缩
zlib_filters = tb.Filters(complevel=1, complib='zlib', shuffle=True)

# Blosc2 + BitShuffle（推荐用于浮点数据）
b2_filters = tb.Filters(complevel=5, complib='blosc2:zstd', bitshuffle=True)

# Blosc2 + Fletcher32 校验和
safe_filters = tb.Filters(complevel=3, complib='blosc2', shuffle=True, fletcher32=True)

# 创建使用不同过滤器的数组进行对比
arr_none = h5file.create_earray('/', 'arr_none', tb.Float64Atom(), (0,), filters=none_filters)
arr_zlib = h5file.create_earray('/', 'arr_zlib', tb.Float64Atom(), (0,), filters=zlib_filters)
arr_b2 = h5file.create_earray('/', 'arr_b2', tb.Float64Atom(), (0,), filters=b2_filters)

data = np.random.randn(100000)
arr_none.append(data)
arr_zlib.append(data)
arr_b2.append(data)
h5file.flush()

print(f"不压缩 磁盘大小: {arr_none.size_on_disk / 1024:.1f} KB")
print(f"Zlib    磁盘大小: {arr_zlib.size_on_disk / 1024:.1f} KB")
print(f"Blosc2  磁盘大小: {arr_b2.size_on_disk / 1024:.1f} KB")
```

## 14. 节点遍历

```python
# 遍历根下所有直接子节点
print("根节点直接子节点:")
for node in h5file.iter_nodes('/'):
    print(f"  {node._v_pathname} ({type(node).__name__})")

# 递归遍历所有叶子节点
print("\n所有叶子节点:")
for leaf in h5file.walk_nodes('/', classname='Leaf'):
    print(f"  {leaf._v_pathname} (shape={leaf.shape})")
```

## 15. 读取为 pandas DataFrame

```python
import pandas as pd

# Table 数据直接转为 DataFrame
df = pd.DataFrame.from_records(table.read())
print(f"DataFrame 形状: {df.shape}")
print(df.head())
# 注意：字节串列（如 detector_name）在 pandas 中可能需要.decode()

# 也可以使用 pandas 内置的 HDFStore
# df.to_hdf('pandas_test.h5', key='particles', mode='w')
# df2 = pd.read_hdf('pandas_test.h5', key='particles')
```

## 16. 关闭文件

```python
# 查看文件信息
print(f"\n文件操作统计:")
print(f"  文件大小: {os.path.getsize('tutorial.h5') / 1024:.1f} KB")

# 关闭文件
h5file.close()

# 验证关闭后无法访问
try:
    _ = h5file.root
except tb.ClosedFileError:
    print("文件已正确关闭")
```

## 17. 只读模式重新打开

```python
# 只读模式打开
h5file = tb.open_file('tutorial.h5', mode='r')
print(f"只读打开: {h5file.filename}")

# 读取之前创建的表
t = h5file.root.particles
print(f"Particles 行数: {t.nrows}")
print(f"平均能量: {t.cols.energy[:].mean():.2f}")

h5file.close()

# 清理
os.remove('tutorial.h5')
```

## 常用 API 速查表

| 操作 | 代码 |
|------|------|
| 创建/打开文件 | `tb.open_file(filename, mode)` |
| 创建分组 | `h5file.create_group(where, name, title)` |
| 创建 Array | `h5file.create_array(where, name, obj, title)` |
| 创建 CArray | `h5file.create_carray(where, name, atom, shape, title, filters)` |
| 创建 EArray | `h5file.create_earray(where, name, atom, shape, title, filters)` |
| 创建 VLArray | `h5file.create_vlarray(where, name, atom, title, filters)` |
| 创建 Table | `h5file.create_table(where, name, description, title, expectedrows, filters)` |
| EArray 追加 | `earray.append(data)` |
| Table 逐行追加 | `row = table.row; row['col']=val; row.append(); table.flush()` |
| Table 批量追加 | `table.append(recarray)` |
| 读取数据 | `node[:]` 或 `node.read(start, stop, step)` |
| 条件查询 | `table.where(condition)` |
| 获取条件行号 | `table.get_where_list(condition)` |
| 条件读取 | `table.read_where(condition)` |
| 创建列索引 | `table.cols.colname.create_index(optlevel, kind)` |
| 遍历节点 | `h5file.iter_nodes(where)` / `h5file.walk_nodes(where)` |
| 获取节点 | `h5file.get_node(path)` 或自然命名 `h5file.root.a.b` |
| 刷新缓冲区 | `table.flush()` / `h5file.flush()` |
| 关闭文件 | `h5file.close()` |

## 异常处理

```python
try:
    h5file = tb.open_file('nonexistent.h5', mode='r')
except (IOError, tb.HDF5ExtError) as e:
    print(f"无法打开文件: {e}")

try:
    node = h5file.get_node('/nonexistent')
except tb.NoSuchNodeError:
    print("节点不存在")

try:
    h5file_w = tb.open_file('readonly.h5', mode='r')
    h5file_w.create_array('/', 'test', [1,2,3])
except tb.FileModeError:
    print("只读模式下无法写入")
```

## 相关概念

- [PyTables 简介](../concepts/00-introduction.md)
- [节点层次体系](../concepts/01-node-hierarchy.md)
- [Table 与 Atom](../concepts/02-table-atom.md)
- [压缩与索引](../concepts/03-compression-indexing.md)
- [文件初始化参考](../references/file-init.md)
