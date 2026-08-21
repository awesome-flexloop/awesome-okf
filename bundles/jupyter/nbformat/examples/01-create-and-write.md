---
type: "example"
title: "创建和写入Notebook"
description: "使用nbformat.v4工厂函数从零构建Notebook，包含Markdown、Code、输出对象，并写入.ipynb文件"
tags: [create, write, factory, new-notebook, new-cell, new-output]
sources:
  - id: v4-nbbase
    resource: /references/v4-nbbase-source.md
    title: "v4构造API"
  - id: init-api
    resource: /references/init-api.md
    title: "包入口公共API"
---

# 创建和写入Notebook

## 示例目标

演示如何从零程序化创建一个完整的Notebook，包含多种cell类型和输出类型，然后写入文件。

## 完整代码

```python
"""
创建一个示例Notebook并写入文件。
包含：Markdown标题、代码单元（无输出）、代码单元（执行结果）、代码单元（流输出）、代码单元（错误输出）。
"""
import nbformat as nbf

# 1. 创建空Notebook（v4.5）
nb = nbf.v4.new_notebook()

# 2. 设置metadata
nb.metadata.kernelspec = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3"
}
nb.metadata.language_info = {"name": "python", "version": "3.10.0"}

# 3. Markdown标题单元
nb.cells.append(nbf.v4.new_markdown_cell(
    source="# 示例Notebook\n\n这是一个用nbformat程序化创建的Notebook。"
))

# 4. 代码单元：导入库（未执行，无输出）
nb.cells.append(nbf.v4.new_code_cell(
    source="import math\nimport random"
))

# 5. 代码单元：计算并添加执行结果
cell = nbf.v4.new_code_cell(source="print(f'π ≈ {math.pi:.4f}')\nmath.pi")
cell.execution_count = 1
cell.outputs.append(nbf.v4.new_output(
    output_type="stream",
    name="stdout",
    text="π ≈ 3.1416\n"
))
cell.outputs.append(nbf.v4.new_output(
    output_type="execute_result",
    data={"text/plain": "3.141592653589793"},
    execution_count=1
))
nb.cells.append(cell)

# 6. 代码单元：带Markdown和HTML富输出
cell = nbf.v4.new_code_cell(source="data = {'name': 'Jupyter', 'version': 4}\ndata")
cell.execution_count = 2
cell.outputs.append(nbf.v4.new_output(
    output_type="execute_result",
    data={
        "text/plain": "{'name': 'Jupyter', 'version': 4}",
        "text/html": "<table><tr><th>name</th><td>Jupyter</td></tr>"
                    "<tr><th>version</th><td>4</td></tr></table>"
    },
    execution_count=2,
    metadata={}
))
nb.cells.append(cell)

# 7. 代码单元：错误输出
cell = nbf.v4.new_code_cell(source="1 / 0")
cell.execution_count = 3
cell.outputs.append(nbf.v4.new_output(
    output_type="error",
    ename="ZeroDivisionError",
    evalue="division by zero",
    traceback=[
        "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
        "\u001b[0;31mZeroDivisionError\u001b[0m: division by zero",
        "",
        "Cell In[3], line 1",
        "\u001b[0;32m----> 1\u001b[0m \u001b[0;31m1\u001b[0m \u001b[0;32m/\u001b[0m \u001b[0;34m0\u001b[0m",
        "",
        "\u001b[0;31mZeroDivisionError\u001b[0m: division by zero"
    ]
))
nb.cells.append(cell)

# 8. Markdown结尾
nb.cells.append(nbf.v4.new_markdown_cell(
    source="---\n\n*以上代码由nbformat自动生成。*"
))

# 9. 写入文件
nbf.write(nb, "example_notebook.ipynb")
print("Notebook已写入 example_notebook.ipynb")
print(f"共 {len(nb.cells)} 个单元")
for i, c in enumerate(nb.cells):
    outputs = len(c.outputs) if c.cell_type == "code" else "-"
    print(f"  [{i}] {c.cell_type:8s} id={c.id[:8]}... outputs={outputs}")
```

## 预期输出

```
Notebook已写入 example_notebook.ipynb
共 7 个单元
  [0] markdown id=a1b2c3d4... outputs=-
  [1] code     id=e5f6g7h8... outputs=0
  [2] code     id=i9j0k1l2... outputs=2
  [3] code     id=m3n4o5p6... outputs=1
  [4] code     id=q7r8s9t0... outputs=1
  [5] markdown id=u1v2w3x4... outputs=-
```

（ID为随机值，每次运行不同）

## 生成的JSON结构概要

写入的 `example_notebook.ipynb` 顶层结构：

```json
{
  "cells": [
    { "cell_type": "markdown", "id": "...", "metadata": {}, "source": "..." },
    { "cell_type": "code", "id": "...", "metadata": {}, "source": "...", "execution_count": null, "outputs": [] },
    { "cell_type": "code", "id": "...", ..., "execution_count": 1, "outputs": [{...}, {...}] },
    ...
  ],
  "metadata": {
    "kernelspec": {...},
    "language_info": {...}
  },
  "nbformat": 4,
  "nbformat_minor": 5
}
```

## 关键要点

- `new_notebook()` 创建空Notebook，`new_code_cell()`/`new_markdown_cell()` 创建单元
- 每个新创建的单元自动通过schema验证
- code cell的 `execution_count` 初始为 `None`（未执行），设置为int表示已执行
- output使用 `new_output()` 创建，需指定 `output_type`
- `nbf.write()` 自动添加末尾换行符
- cell ID由 `generate_corpus_id()` 自动生成（8位hex），也可通过kwargs手动指定

## 相关概念

- [Notebook构造API](../concepts/07-notebook-construction.md)
- [v4格式详解](../concepts/09-v4-format.md)
