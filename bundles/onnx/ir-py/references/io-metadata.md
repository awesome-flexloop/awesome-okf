---
type: reference
title: "_io.py/_metadata.py/_linked_list.py/_name_authority.py：IO、元数据、链表与命名"
description: "onnx_ir._io 模块模型加载保存、_metadata 模块 MetadataStore、_linked_list 模块 DoublyLinkedSet、_name_authority 模块 NameAuthority 信源登记"
sources:
  - path: "src/onnx_ir/_io.py"
    facts: [F-054, F-055]
  - path: "src/onnx_ir/_metadata.py"
    facts: [F-059]
  - path: "src/onnx_ir/_linked_list.py"
    facts: [F-044, F-045, F-046]
  - path: "src/onnx_ir/_name_authority.py"
    facts: [F-047]
  - path: "src/onnx_ir/_core.py"
    facts: [F-060]
---

# _io.py/_metadata.py/_linked_list.py/_name_authority.py：IO、元数据、链表与命名

## 信源概述

| 信源 | 类型 | 行数 | 职责 |
|------|------|------|------|
| `src/onnx_ir/_io.py` | Python 实现 | ~200行 | 模型 `load()`/`save()`、外部数据卸载与加载 |
| `src/onnx_ir/_metadata.py` | Python 实现 | ~50行 | `MetadataStore` 键值存储与失效标记 |
| `src/onnx_ir/_linked_list.py` | Python 实现 | ~280行 | `_LinkBox` 双向链表节点、`DoublyLinkedSet` 有序集合 |
| `src/onnx_ir/_name_authority.py` | Python 实现 | ~70行 | `NameAuthority` 自动唯一命名 |

## 关键事实登记

### F-054：_io.load() 模型加载

**信源**：`src/onnx_ir/_io.py` L19-L38

```python
def load(path: str | os.PathLike) -> Model:
    # 1. 使用 onnx.load(path, load_external_data=False) 加载 proto
    #    （不让 ONNX 自动加载外部数据，延迟到 IR 层处理）
    # 2. from_proto() 反序列化为 IR Model
    # 3. external_data.set_base_dir(model.graph, os.path.dirname(path))
    #    设置外部数据基础目录
    return model
```

关键点：不让 ONNX C++ 层加载外部数据，而是由 IR 层的 ExternalTensor 通过 mmap 按需加载。

### F-055：_io.save() 模型保存与外部数据

**信源**：`src/onnx_ir/_io.py` L41-L203

`save()` 支持 external_data 模式，参数：
- `external_data: str | None`：外部数据路径
- `size_threshold_bytes: int = 0`：超过阈值的 initializer 转为外部数据
- `max_shard_size_bytes: int = 0`：外部数据分片大小上限
- `max_workers: int | None = None`：并行写入线程数
- `max_in_flight_bytes: int = 0`：内存中in-flight字节上限
- `alignment: int | None = None`：数据对齐

执行流程：
1. 若指定 external_data，调用 `external_data.unload_from_model()` 将 initializer 转为外部数据
2. `to_proto()` 序列化为 ModelProto
3. `onnx.save()` 写入文件
4. **finally 块**中恢复原始 initializer 值，保证 model 对象不变

### F-059：MetadataStore 元数据存储

**信源**：`src/onnx_ir/_metadata.py` L12-L48

`MetadataStore` 继承 `collections.UserDict`，增加失效标记机制：

```python
class MetadataStore(collections.UserDict):
    def __init__(self):
        super().__init__()
        self._invalid_keys: set[str] = set()

    def invalidate(self, key: str) -> None:
        """标记键失效"""
        self._invalid_keys.add(key)

    def is_valid(self, key: str) -> bool:
        """查询键是否有效"""
        return key in self.data and key not in self._invalid_keys

    def __setitem__(self, key, value):
        """写入时自动从invalid_keys移除"""
        self._invalid_keys.discard(key)
        super().__setitem__(key, value)

    def __bool__(self):
        """data非空或有invalid_keys时返回True"""
        return bool(self.data) or bool(self._invalid_keys)
```

### F-044：_LinkBox 双向链表节点容器

**信源**：`src/onnx_ir/_linked_list.py` L13-L65

```python
class _LinkBox:
    __slots__ = ("prev", "next", "value", "owning_list")

    def __init__(self, value=None, owning_list=None):
        self.prev: _LinkBox | None = None
        self.next: _LinkBox | None = None
        self.value = value  # None 表示已擦除/根节点
        self.owning_list = owning_list

    def erase(self) -> None:
        """将自身从链表中摘除，置value为None
        但不破坏prev/next指针以便迭代器安全继续"""
        self.prev.next = self.next
        self.next.prev = self.prev
        self.value = None
        self.owning_list = None
```

关键设计：`erase()` 不修改 prev/next 指针，仅断开邻居指向自己的链接，保证迭代器安全。

### F-045/F-046：DoublyLinkedSet 双向链表有序集合

**信源**：`src/onnx_ir/_linked_list.py` L68-L283

`DoublyLinkedSet` 使用循环双向链表（root 哨兵节点 value=None）：

```python
class DoublyLinkedSet:
    def __init__(self):
        self._root = _LinkBox()  # 哨兵节点，value=None
        self._root.prev = self._root
        self._root.next = self._root
        self._length = 0
        self._value_ids_to_boxes: dict[int, _LinkBox] = {}  # id→box O(1)查找
```

操作复杂度：
| 操作 | 复杂度 | 说明 |
|------|--------|------|
| `append(value)` | O(1) | 尾部插入 |
| `remove(value)` | O(1) | 通过 id 查 box 后摘除 |
| `insert_after(after, value)` | O(1) | 指定位置后插入 |
| `insert_before(before, value)` | O(1) | 指定位置前插入 |
| 索引访问 | O(n) | 顺序遍历（首尾 O(1)） |
| `__contains__` | O(1) | dict 查找 |

迭代器安全保证：
- 迭代中在当前节点**之后**插入的新元素会被遍历到
- 在当前节点**之前**插入的不会
- 当前节点被移动到其他位置时，迭代从原位置的 next 继续
- 插入重复值时先 remove 旧的再插入
- 迭代时遇到 erased box（value=None）自动跳过

### F-047：NameAuthority 命名治理器

**信源**：`src/onnx_ir/_name_authority.py` L10-L72

```python
class NameAuthority:
    def __init__(self):
        self._value_names: set[str] = set()
        self._node_names: set[str] = set()
        self._value_counter = 0
        self._node_counter = 0
```

命名规则：
- 匿名 Value → `val_{counter}` 格式名称
- 匿名 Node → `node_{op_type}_{counter}` 格式名称
- 如果 value/node 已有名称则不改名
- **重要**：名称一旦被跟踪，即使节点/值被移除也不会释放（计数器单调增长）
- 开发者注释明确指出：这可能导致计数器无限增长，但在模型规模范围内完全可接受，释放名称可能导致新旧对象重名引发难以调试的 bug
