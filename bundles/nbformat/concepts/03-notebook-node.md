---
type: "concept"
title: "NotebookNode 与 Struct"
description: "NotebookNode对象模型详解：Struct基类的属性访问、_allownew控制、merge合并，NotebookNode的自动转换与深拷贝优化"
tags: [notebooknode, struct, dict-subclass, attribute-access, deepcopy]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: notebooknode
    resource: /references/notebooknode-source.md
    title: "NotebookNode与Struct源码"
---

# NotebookNode 与 Struct

nbformat 中Notebook的内存表示是一个嵌套的 `NotebookNode` 结构——它是一个支持属性风格访问的dict子类。

## Struct 基类

`Struct(dict)` 是NotebookNode的父类，提供以下核心能力：

### 属性风格访问

Struct 将属性访问（`obj.key`）映射到字典访问（`obj["key"]`）：

```python
from nbformat._struct import Struct

s = Struct(a=10, b=30)
s.a          # 10  → 等价于 s["a"]
s["b"]       # 30
s.c = 40     # 等价于 s["c"] = 40
```

[F-030]

`__getattr__` 捕获 `KeyError` 并转为 `AttributeError`，保证Python属性访问协议一致。

### 类成员保护

Struct 防止覆盖dict的内置方法和类属性：

```python
s = Struct()
s.get = 10   # 抛出 AttributeError: "attr get is a protected member"
```

检查逻辑：如果key在`self.__dict__`或`Struct`类属性中，拒绝设置 [F-031]。

### `_allownew` 键创建控制

```python
s = Struct()
s["a"] = 10           # 正常
s.allow_new_attr(False)
s["a"] = 20           # 正常（已存在的key）
s["b"] = 30           # KeyError: can't create new attribute b
s.allow_new_attr(True)# 恢复允许新键
```

这个机制在NotebookNode中没有默认开启，但可用于在构造Notebook时捕获拼写错误。[F-032]

### merge() 智能合并

`merge()` 比 `update()` 更灵活，支持自定义冲突解决策略：

```python
s = Struct(a=10, b=30)
s2 = Struct(a=20, c=40)

# 默认策略：preserve（保留旧值，等价于 s.update({k:v for k,v in s2.items() if k not in s})）
s.merge(s2)           # s.a=10, s.b=30, s.c=40

# 指定策略
s = Struct(a=10, b=30)
s.merge(s2, {"update": "a", "add": "b"})  # a=20(覆盖), b=70(相加), c=40
```

[F-033]

5种预设冲突策略：

| 策略 | 行为 | lambda |
|------|------|--------|
| `preserve` | 保留旧值（默认） | `lambda old,new: old` |
| `update` | 新值覆盖 | `lambda old,new: new` |
| `add` | 相加（数值/字符串拼接） | `lambda old,new: old+new` |
| `add_flip` | 反向相加 | `lambda old,new: new+old` |
| `add_s` | 字符串空格拼接 | `lambda old,new: old+" "+new` |

### 运算符重载

```python
s1 = Struct(a=10, b=30)
s2 = Struct(a=20, c=40)

s3 = s1 + s2          # 新Struct，等价于s1.copy().merge(s2)
s1 += s2              # 原地merge
s = s1 - Struct(a=0)  # 删除键a
s1 -= Struct(a=0)     # 原地删除
```

[F-034]

## NotebookNode 类

`NotebookNode(Struct)` 是Notebook文档树中所有节点的类型。

### 自动嵌套转换

`__setitem__` 自动将嵌套的普通dict（但非NotebookNode的Mapping）递归包装为NotebookNode：

```python
nb = NotebookNode()
nb["metadata"] = {"kernelspec": {"name": "python3"}}
type(nb.metadata)                    # NotebookNode
type(nb.metadata.kernelspec)         # NotebookNode
```

[F-035]

这意味着从JSON解析后，所有嵌套层级都自动获得属性访问能力。

### from_dict() 递归转换

```python
from nbformat.notebooknode import from_dict

data = {
    "cells": [
        {"cell_type": "code", "source": "print(1)", "metadata": {}}
    ],
    "metadata": {"kernelspec": {"name": "python3"}}
}
nb = from_dict(data)
type(nb)                    # NotebookNode
type(nb.cells[0])           # NotebookNode
type(nb.cells[0].metadata)  # NotebookNode
```

`from_dict()` 递归遍历dict/list/tuple结构，所有dict转为NotebookNode，list/tuple中的元素递归转换，原子类型保持不变 [F-036]。

### 优化的 `__deepcopy__`

标准`copy.deepcopy`对dict子类走`__reduce_ex__`慢路径，Notebook重写了`__deepcopy__`：

1. 创建新的空NotebookNode，注册到memo防止循环引用
2. 原子类型（str/int/float/bool/bytes/None/complex）直接共享引用
3. list类型递归深拷贝元素（list内的普通dict保持为dict，与标准deepcopy行为一致）
4. 其他类型（NotebookNode等）通过`__setitem__`赋值，触发自动转换
5. 最后恢复`__dict__`中的实例状态（`_allownew`等）

[F-037]

Notebook在`validate`/`normalize`/`writes`等操作中频繁深拷贝，此优化显著提升性能。

### update() 方法

遵循 `MutableMapping.update` 协议，支持三种输入：
- Mapping对象（dict/Struct等）
- 带`keys()`方法的对象
- 键值对迭代器

kwargs也会被合并。与dict.update不同，NotebookNode.update通过`__setitem__`赋值，触发嵌套dict自动转换 [F-038]。

## 实践提示

- 访问Notebook内容时，属性风格（`nb.cells[0].source`）和字典风格（`nb["cells"][0]["source"]`）完全等价
- 嵌套dict赋值时不需要手动创建NotebookNode，自动转换
- 深拷贝Notebook使用标准`copy.deepcopy(nb)`，会自动走优化路径
- 检查键是否存在使用 `"key" in nb`，不要用`nb.hasattr("key")`（Struct的hasattr方法不检查dict方法名）

## 相关概念

- [架构总览](02-architecture-overview.md)
- [v4格式详解](09-v4-format.md)
- [Notebook构造API](07-notebook-construction.md)
