---
type: Concept
title: Notebook 文件格式（.ipynb）
description: .ipynb 文件的 JSON 结构、nbformat 版本、NotebookNode 数据模型、单元格类型、元数据、信任签名机制
tags: [jupyter, ipynb, nbformat, notebook-format, json, notebooknode]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T10:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jupyter-metasource
    resource: /references/jupyter-metasource.md
---

# Notebook 文件格式（.ipynb）

Jupyter Notebook 使用 `.ipynb` 文件扩展名存储，这是一种基于 JSON 的结构化文档格式。`.ipynb` 的名称来源于 "IPython Notebook"，保留了历史痕迹（尽管现在支持众多语言）。Notebook 文件格式由 [nbformat](https://nbformat.readthedocs.io) 包定义和处理。

## 文件顶层结构

一个 `.ipynb` 文件是标准的 JSON 文档，顶层包含以下字段：

```json
{
  "cells": [],
  "metadata": {},
  "nbformat": 4,
  "nbformat_minor": 5
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `cells` | Array | Notebook 中的单元格列表，按顺序排列 |
| `metadata` | Object | 整个 Notebook 的元数据（内核信息、作者、扩展配置等） |
| `nbformat` | Integer | 主版本号（当前为 4） |
| `nbformat_minor` | Integer | 次版本号（当前为 5） |

### 版本历史

| nbformat 版本 | 说明 |
|--------------|------|
| v1-v3 | 早期版本，已不推荐使用 |
| v4 | 当前标准版本（2015年起），所有现代 Jupyter 应用使用 |

## 单元格（Cells）

单元格是 Notebook 的基本构建块，有四种类型：

### 1. Markdown 单元格

用于叙述性文本、标题、公式、图片等：

```json
{
  "cell_type": "markdown",
  "metadata": {},
  "source": ["# 标题\n", "这是**Markdown**文本，支持 $\\LaTeX$ 公式。"]
}
```

- `source` 字段是字符串数组，每个元素是一行文本（以换行符结尾），也可以是单个字符串
- 支持标准 Markdown 语法，包括标题、列表、链接、图片、表格
- 支持 LaTeX 数学公式（`$...$` 行内，`$$...$$` 块级）
- 支持 HTML 嵌入

### 2. Code 单元格

包含可执行代码和执行结果：

```json
{
  "cell_type": "code",
  "execution_count": 1,
  "metadata": {},
  "outputs": [],
  "source": ["import numpy as np\n", "x = np.array([1, 2, 3])\n", "x.mean()"]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `source` | Array/String | 代码内容，按行分割或单字符串 |
| `execution_count` | Integer/null | 执行计数器（Kernel 中递增），未执行为 `null` |
| `outputs` | Array | 输出列表，可以包含多种类型 |
| `metadata` | Object | 单元格元数据（标签、折叠状态等） |

### 3. Raw 单元格

原始单元格，内容不经过任何处理直接传递：

```json
{
  "cell_type": "raw",
  "metadata": {},
  "source": ["Raw content, passed through unchanged."]
}
```

Raw 单元格在 nbconvert 转换时按原样输出（如转换为 LaTeX 时作为原始 LaTeX）。

### 输出（Outputs）

Code 单元格的 `outputs` 数组可以包含以下输出类型：

#### Stream 输出（stdout/stderr）

```json
{
  "output_type": "stream",
  "name": "stdout",
  "text": ["Hello, World!\n"]
}
```

- `name`: `"stdout"` 或 `"stderr"`
- `text`: 输出文本内容

#### Display Data（富媒体显示）

```json
{
  "output_type": "display_data",
  "data": {
    "text/plain": ["<Figure size 640x480 with 1 Axes>"],
    "text/html": ["<b>Hello</b>"],
    "image/png": "iVBORw0KGgo..."
  },
  "metadata": {}
}
```

- `data` 是一个 MIME 类型到内容的映射
- 前端选择最合适的 MIME 类型渲染（浏览器优先 HTML/PNG，终端选 text/plain）
- 图片数据使用 base64 编码
- 常见 MIME 类型：
  - `text/plain`：纯文本回退
  - `text/html`：HTML 渲染
  - `text/markdown`：Markdown 渲染
  - `image/png`、`image/jpeg`、`image/svg+xml`：图片
  - `application/json`：JSON 数据
  - `application/vnd.jupyter.widget-view+json`：ipywidgets
  - `text/latex`：LaTeX 公式

#### Execute Result（执行结果）

```json
{
  "output_type": "execute_result",
  "execution_count": 1,
  "data": {
    "text/plain": ["2.0"]
  },
  "metadata": {}
}
```

类似 display_data，但额外包含 `execution_count`，表示单元格的最后一个表达式求值结果（即 REPL 中自动打印的值）。

#### Error 输出

```json
{
  "output_type": "error",
  "ename": "ValueError",
  "evalue": "invalid literal for int()",
  "traceback": [
    "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
    "\u001b[0;31mValueError\u001b[0m: invalid literal for int()"
  ]
}
```

- `ename`：异常类名
- `evalue`：异常消息
- `traceback`：格式化的堆栈跟踪（包含 ANSI 颜色转义序列）

## 元数据（Metadata）

### Notebook 级元数据

```json
{
  "metadata": {
    "kernelspec": {
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    },
    "language_info": {
      "name": "python",
      "version": "3.13.0",
      "mimetype": "text/x-python",
      "file_extension": ".py"
    },
    "authors": [{"name": "Author Name"}]
  }
}
```

- `kernelspec`：关联的内核信息，决定打开 Notebook 时启动哪个 Kernel
- `language_info`：语言版本和语法高亮信息
- 扩展可以添加自定义元数据字段

### 单元格级元数据

```json
{
  "cell_type": "code",
  "metadata": {
    "tags": ["parameters", "hide-input"],
    "collapsed": false,
    "scrolled": false
  }
}
```

常见的单元格元数据：
- `tags`：标签数组，用于 papermill 参数化、nbconvert 条件显示等
- `collapsed`：是否折叠输出
- `scrolled`：输出是否滚动显示

## 使用 nbformat 编程操作 Notebook

nbformat 包提供了读写和操作 Notebook 文件的 Python API：

```python
import nbformat

# 读取 Notebook
nb = nbformat.read('notebook.ipynb', as_version=4)

# 访问单元格
for cell in nb.cells:
    if cell.cell_type == 'code':
        print(f"Code cell (exec_count={cell.execution_count}):")
        print(cell.source[:50])
    elif cell.cell_type == 'markdown':
        print(f"Markdown: {cell.source[:50]}")

# 创建新单元格
new_cell = nbformat.v4.new_code_cell(source="print('hello')")
nb.cells.append(new_cell)

# 写入 Notebook
nbformat.write(nb, 'output.ipynb')
```

### NotebookNode 对象

nbformat 将 Notebook 加载为 `NotebookNode` 对象，它是一个类似字典的对象，支持属性访问：

```python
# 属性访问
print(nb.nbformat)           # 4
print(nb.cells[0].cell_type) # 'markdown'

# 字典访问也可以
print(nb['nbformat'])
```

### Notebook 验证

nbformat 包含验证器，可以检查 Notebook 是否符合格式规范：

```python
from nbformat import validate, ValidationError

try:
    validate(nb)
    print("Notebook is valid")
except ValidationError as e:
    print(f"Validation error: {e}")
```

## 信任签名机制

Jupyter 实现了 Notebook 信任（Trust）机制，防止恶意 HTML/JavaScript 在用户打开 Notebook 时自动执行：

- **不受信任的 Notebook**：打开时，所有 JavaScript 和潜在危险的 HTML 输出被清理（sanitize）
- **受信任的 Notebook**：所有输出正常渲染

信任签名基于 Notebook 内容的 HMAC 签名，存储在用户配置目录中：

1. 用户执行 Notebook 的所有单元格后，Notebook 被标记为受信任
2. 签名基于单元格内容计算，内容修改后签名失效
3. 签名存储在 `~/.local/share/jupyter/nbsignatures.db`（SQLite 数据库）

```python
from nbformat import sign

# 检查 Notebook 是否受信任
notary = sign.NotebookNotary()
print(notary.check_signature(nb))  # True/False

# 标记为受信任
notary.sign(nb)
```

## nbconvert 转换流程

Notebook 转换为其他格式（HTML/PDF/Markdown等）由 nbconvert 完成：

```mermaid
graph LR
    NB["Notebook (.ipynb)"] --> Read["nbformat.read<br/>(加载NotebookNode)"]
    Read --> Preprocess["Preprocessors<br/>(执行/提取/清理)"]
    Preprocess --> Export["Exporter<br/>(模板渲染)"]
    Export --> Post["Postprocessors<br/>(后处理)"]
    Post --> Output["输出文件"]
    
    style NB fill:#e3f2fd
    style Read fill:#fff3e0
    style Preprocess fill:#f3e5f5
    style Export fill:#e8f5e9
    style Post fill:#fce4ec
    style Output fill:#fafafa
```

1. **读取**：nbformat.read 加载为 NotebookNode
2. **预处理**：如 ExecutePreprocessor 运行代码、TagRemovePreprocessor 移除标记的单元格
3. **导出**：使用 Jinja2 模板将 Notebook 渲染为目标格式（HTML/LaTeX/Markdown/RST/PDF）
4. **后处理**：如 PDF 后处理调用 LaTeX 编译

```bash
# 命令行转换
jupyter nbconvert --to html notebook.ipynb
jupyter nbconvert --to pdf notebook.ipynb
jupyter nbconvert --to markdown notebook.ipynb
jupyter nbconvert --to script notebook.ipynb  # 导出为 .py 脚本
```

## 最小 Notebook 示例

以下是一个完整的最小 `.ipynb` 文件：

```json
{
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": ["# 我的第一个Notebook\n", "这是一个简单的演示。"]
    },
    {
      "cell_type": "code",
      "execution_count": 1,
      "metadata": {},
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": ["Hello, Jupyter!\n"]
        }
      ],
      "source": ["print('Hello, Jupyter!')"]
    }
  ],
  "metadata": {
    "kernelspec": {
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 5
}
```

## 相关概念

- [什么是计算笔记本与 Jupyter 核心架构](01-what-is-jupyter.md) — Notebook 在架构中的角色
- [Kernel 架构](06-kernel-architecture.md) — 代码如何在 Kernel 中执行
- [客户端-服务器架构详解](08-client-server.md) — Notebook 文件如何在 Server 中处理
- [nbformat 官方文档](https://nbformat.readthedocs.io) — nbformat 包详细 API 参考
