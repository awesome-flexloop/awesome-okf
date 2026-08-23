---
type: "concept"
title: "Notebook构造API"
description: "使用new_notebook/new_code_cell/new_markdown_cell/new_raw_cell/new_output等工厂函数程序化构建Notebook"
tags: [construction, factory, new-notebook, new-cell, new-output, programmatic]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: v4-nbbase
    resource: /references/v4-nbbase-source.md
    title: "v4构造API源码"
---

# Notebook构造API

nbformat 提供工厂函数在 v4 版本下程序化构建 Notebook 对象。所有工厂函数位于 `nbformat.v4` 命名空间下。

## 工厂函数总览

| 函数 | 创建对象 | 是否带ID |
|------|---------|---------|
| `new_notebook(**kwargs)` | Notebook根对象 | 否（顶层无ID） |
| `new_code_cell(source="", **kwargs)` | 代码单元 | ✅ 自动生成 |
| `new_markdown_cell(source="", **kwargs)` | Markdown单元 | ✅ 自动生成 |
| `new_raw_cell(source="", **kwargs)` | 原始文本单元 | ✅ 自动生成 |
| `new_output(output_type, data=None, **kwargs)` | 输出对象 | 否（output无ID） |
| `output_from_msg(msg)` | 从kernel消息创建输出 | 否 |

[F-080]

## new_notebook()

```python
def new_notebook(**kwargs):
    nb = NotebookNode(
        nbformat=4,
        nbformat_minor=5,
        metadata=NotebookNode(),
        cells=[],
    )
    nb.update(kwargs)
    validate(nb)
    return nb
```

默认创建一个空Notebook，metadata和cells为空。通过kwargs可以覆盖任何字段：

```python
nb = nbformat.v4.new_notebook(
    metadata=nbformat.from_dict({
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"}
    })
)
```

[F-081]

## 三种Cell类型

### Code Cell（代码单元）

```python
def new_code_cell(source="", **kwargs):
    cell = NotebookNode(
        id=random_cell_id(),           # 8位hex
        cell_type="code",
        metadata=NotebookNode(),
        execution_count=None,
        source=source,
        outputs=[],
    )
    cell.update(kwargs)
    validate(cell, "code_cell")
    return cell
```

code cell 包含 `execution_count`（执行计数，None=未执行）和 `outputs`（输出列表）。

### Markdown Cell（Markdown单元）

```python
def new_markdown_cell(source="", **kwargs):
    cell = NotebookNode(
        id=random_cell_id(),
        cell_type="markdown",
        source=source,
        metadata=NotebookNode(),
    )
    cell.update(kwargs)
    validate(cell, "markdown_cell")
    return cell
```

Markdown cell 无 execution_count 和 outputs，仅包含 source。

### Raw Cell（原始文本单元）

```python
def new_raw_cell(source="", **kwargs):
    cell = NotebookNode(
        id=random_cell_id(),
        cell_type="raw",
        source=source,
        metadata=NotebookNode(),
    )
    cell.update(kwargs)
    validate(cell, "raw_cell")
    return cell
```

Raw cell 用于存放不被解释器处理的原始文本（如nbconvert配置元信息）。

[F-082]

### Cell ID

v4.5+ 的每个cell必须有唯一的 `id` 字段。工厂函数通过 `generate_corpus_id()` 自动生成8位十六进制随机ID：

```python
from nbformat.corpus.words import generate_corpus_id
# generate_corpus_id() = uuid.uuid4().hex[:8]  # 例如 "a1b2c3d4"
```

ID要求8-64个字母/数字/-/_字符，在Notebook范围内唯一。[F-083]

## new_output() — 输出对象

```python
def new_output(output_type, data=None, **kwargs):
```

支持4种输出类型：

### stream（标准流输出）

```python
output = nbformat.v4.new_output(
    "stream",
    name="stdout",       # 或 "stderr"
    text="Hello World\n"
)
```

默认值：`name="stdout"`, `text=""`

### execute_result（执行结果）

```python
output = nbformat.v4.new_output(
    "execute_result",
    data={"text/plain": "2", "text/html": "<b>2</b>"},
    execution_count=1,
    metadata={}
)
```

默认值：`execution_count=None`, `data={}`, `metadata={}`

### display_data（显示数据）

```python
output = nbformat.v4.new_output(
    "display_data",
    data={"image/png": "base64data...", "text/plain": "<Figure>"},
    metadata={"image/png": {"width": 640, "height": 480}}
)
```

默认值：`data={}`, `metadata={}`

### error（错误输出）

```python
output = nbformat.v4.new_output(
    "error",
    ename="ValueError",
    evalue="invalid literal for int()",
    traceback=["Traceback (most recent call last):", ...]
)
```

默认值：`ename="NotImplementedError"`, `evalue=""`, `traceback=[]`

[F-084]

### data 参数快捷方式

传入 `data` 参数时直接赋值给 `output.data`，等价于在kwargs中指定 `data=data`。

### 验证

每个新创建的output都会通过 `validate(output, output_type)` 验证schema合规性。

## output_from_msg() — 从Kernel消息创建

```python
def output_from_msg(msg):
```

从Jupyter Kernel IOPub通道消息创建输出NotebookNode，支持4种消息类型：
- `execute_result` → execute_result输出
- `stream` → stream输出
- `display_data` → display_data输出
- `error` → error输出

消息中的transient数据会被过滤掉（`display_id`保留在transient字段中）。[F-085]

## 完整示例：构建带输出的Notebook

```python
import nbformat as nbf

nb = nbf.v4.new_notebook()

# Markdown标题
nb.cells.append(nbf.v4.new_markdown_cell("# 计算圆周率"))

# 代码单元：无输出（未执行）
nb.cells.append(nbf.v4.new_code_cell("import math\nprint(math.pi)"))

# 代码单元：带执行结果
cell = nbf.v4.new_code_cell("1 + 1")
cell.execution_count = 1
cell.outputs.append(nbf.v4.new_output(
    "execute_result",
    data={"text/plain": "2"},
    execution_count=1,
))
nb.cells.append(cell)

# 代码单元：带stream输出
cell = nbf.v4.new_code_cell("print('hello')")
cell.execution_count = 2
cell.outputs.append(nbf.v4.new_output(
    "stream", name="stdout", text="hello\n"
))
nb.cells.append(cell)

# 代码单元：带错误
cell = nbf.v4.new_code_cell("1/0")
cell.execution_count = 3
cell.outputs.append(nbf.v4.new_output(
    "error",
    ename="ZeroDivisionError",
    evalue="division by zero",
    traceback=[
        "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
        "\u001b[0;31mZeroDivisionError\u001b[0m: division by zero"
    ]
))
nb.cells.append(cell)

# 写入文件
nbf.write(nb, "example.ipynb")
```

[F-086]

## kwargs覆盖机制

所有工厂函数的最后一步都是 `cell.update(kwargs)` + `validate()`，这意味着：
1. 可以通过kwargs覆盖任何默认值（包括id、cell_type等）
2. kwargs会在validate之前应用，所以必须满足schema要求
3. validate保证最终结果符合规范

```python
# 自定义cell ID
cell = nbf.v4.new_code_cell("x=1", id="my-custom-id")

# 添加metadata
cell = nbf.v4.new_code_cell(
    "x=1",
    metadata=nbf.NotebookNode({"tags": ["hide-input"]})
)
```

[F-087]

## 注意事项

- 工厂函数创建的对象自动验证，不需要手动调用validate
- `random_cell_id()` 每次调用生成不同ID，但可能重复（概率极低，8位hex=40亿空间）
- `new_output()` 的默认值不包含data（stream和error除外），必须手动提供
- v1/v2/v3版本也有各自的工厂函数（v1.nbbase、v2.nbbase、v3.nbbase），但建议使用v4

## 相关概念

- [NotebookNode与Struct](03-notebook-node.md)
- [v4格式详解](09-v4-format.md)
- [验证体系](06-validation.md)
