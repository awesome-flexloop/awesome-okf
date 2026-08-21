---
type: "concept"
title: "5分钟快速上手"
description: "安装nbformat、创建Notebook、读写文件、验证Notebook的快速入门指南"
tags: [getting-started, quickstart, basic-usage]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: init-api
    resource: /references/init-api.md
    title: "包入口公共API"
  - id: v4-nbbase
    resource: /references/v4-nbbase-source.md
    title: "v4构造API"
---

# 5分钟快速上手

## 安装

```bash
pip install nbformat
```

## 读取Notebook文件

```python
import nbformat

# 从文件读取（自动检测版本，默认转换为v4）
nb = nbformat.read("my_notebook.ipynb", as_version=4)

# 读取时不转换版本
nb = nbformat.read("old_notebook.ipynb", as_version=nbformat.NO_CONVERT)

# 从JSON字符串读取
nb = nbformat.reads(json_string, as_version=4)
```

`read()` 同时支持文件路径字符串和文件对象，内部自动判断 [F-010]。

## 创建Notebook

```python
import nbformat

# 创建空Notebook
nb = nbformat.v4.new_notebook()

# 添加Markdown单元
nb.cells.append(nbformat.v4.new_markdown_cell("# Hello World"))

# 添加代码单元
nb.cells.append(nbformat.v4.new_code_cell("print('Hello, Jupyter!')"))

# 添加带输出的代码单元
cell = nbformat.v4.new_code_cell("1+1")
cell.outputs.append(nbformat.v4.new_output(
    "execute_result",
    data={"text/plain": "2"},
    execution_count=1,
))
cell.execution_count = 1
nb.cells.append(cell)
```

## 写入Notebook文件

```python
# 写入文件（保持当前版本）
nbformat.write(nb, "output.ipynb")

# 写入时指定版本（自动转换）
nbformat.write(nb, "output_v3.ipynb", version=3)

# 序列化为JSON字符串
json_str = nbformat.writes(nb)
```

写入时确保文件末尾有换行符 [F-011]。

## 验证Notebook

```python
from nbformat import validate, ValidationError

try:
    validate(nb)
    print("Notebook is valid!")
except ValidationError as e:
    print(f"Validation error: {e}")

# 仅检查是否有效（返回bool，不抛异常）
from nbformat.validator import isvalid
if isvalid(nb):
    print("Valid")
```

`read()`/`reads()`/`write()`/`writes()` 在内部自动调用 `validate()`，验证失败仅记录错误日志，不抛出异常（除非通过 `capture_validation_error` 参数捕获）[F-012]。

## 版本转换

```python
from nbformat import convert

# 将任意版本的Notebook转换为v4
nb_v4 = convert(nb, 4)

# 降级为v3
nb_v3 = convert(nb_v4, 3)
```

版本转换是逐步递归的：v3→v4通过 `v4.upgrade()`，v4→v3通过 `v4.downgrade()`，跨版本（如v2→v4）会递归经过v3 [F-013]。

## 捕获验证错误

```python
errors = {}
nb = nbformat.read("notebook.ipynb", as_version=4, capture_validation_error=errors)
if "ValidationError" in errors:
    print(f"Found validation error: {errors['ValidationError']}")
```

## 签名Notebook（信任）

```python
from nbformat.sign import NotebookNotary

with NotebookNotary() as notary:
    notary.sign(nb)           # 标记为可信
    trusted = notary.check_signature(nb)  # 检查是否可信
    notary.unsign(nb)         # 取消信任
```

## 相关概念

- [nbformat简介](00-introduction.md)
- [架构总览](02-architecture-overview.md)
- [NotebookNode与Struct](03-notebook-node.md)
