---
type: "concept"
title: "5分钟快速上手"
description: "nbconvert CLI和Python API的基本用法：命令行转换、Python编程转换、常用选项"
tags: [getting-started, cli, python-api, basic-usage]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: factory
    resource: ../references/factory-source.md
    title: "导出器工厂函数源码解析"
  - id: exporter-base
    resource: ../references/exporter-base-source.md
    title: "Exporter基类源码解析"
  - id: writer
    resource: ../references/writer-source.md
    title: "Writer写入器源码解析"
---

# 5分钟快速上手

## CLI 基本用法

nbconvert 的命令行基本格式为：

```bash
jupyter nbconvert --to <format> <notebook.ipynb> [options]
```

### 转换为 HTML

```bash
jupyter nbconvert --to html mynotebook.ipynb
```

生成 `mynotebook.html` 文件，可直接在浏览器中打开。

### 转换为 Markdown

```bash
jupyter nbconvert --to markdown mynotebook.ipynb
```

生成 `mynotebook.md` 文件，图片将提取到 `mynotebook_files/` 目录。

### 转换为 PDF

```bash
# LaTeX方式（需要安装TeX）
jupyter nbconvert --to pdf mynotebook.ipynb

# WebPDF方式（需要playwright）
jupyter nbconvert --to webpdf mynotebook.ipynb
```

### 转换为幻灯片（Reveal.js）

```bash
jupyter nbconvert --to slides mynotebook.ipynb
```

生成 HTML 幻灯片，使用 Reveal.js 框架。

### 转换为可执行脚本

```bash
# Python脚本
jupyter nbconvert --to python mynotebook.ipynb

# 通用脚本（保留cell类型标记）
jupyter nbconvert --to script mynotebook.ipynb
```

### 列出可用导出格式

```bash
jupyter nbconvert --help
# 或查看--to选项的说明
```

## 常用 CLI 选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `--to <format>` | 指定输出格式 | `--to html` |
| `--output <name>` | 指定输出文件名（不含扩展名） | `--output report` |
| `--output-dir <dir>` | 指定输出目录 | `--output-dir ./output` |
| `--template <name>` | 指定模板 | `--template lab` |
| `--template-file <file>` | 指定模板文件 | `--template-file mytemplate.html.j2` |
| `--no-input` | 排除代码输入 | `--no-input` |
| `--no-prompt` | 排除输入/输出提示 | `--no-prompt` |
| `--execute` | 转换前执行Notebook | `--execute` |
| `--stdout` | 输出到标准输出而非文件 | `--stdout` |
| `--post <processor>` | 指定后处理器 | `--post serve` |
| `--config <file.py>` | 指定配置文件 | `--config myconfig.py` |

### 执行并转换

```bash
# 先执行所有code cell，再转换为HTML
jupyter nbconvert --execute --to html mynotebook.ipynb
```

### 使用模板

```bash
# 使用lab模板（JupyterLab风格）
jupyter nbconvert --to html --template lab mynotebook.ipynb

# 使用classic模板（经典Jupyter风格）
jupyter nbconvert --to html --template classic mynotebook.ipynb
```

### 排除代码单元

```bash
# 仅输出Markdown和结果，不含代码
jupyter nbconvert --to html --no-input mynotebook.ipynb

# 排除输入和输出提示
jupyter nbconvert --to html --no-prompt mynotebook.ipynb
```

### 启动预览服务器

```bash
# 转换为HTML后启动HTTP服务器在浏览器中预览
jupyter nbconvert --to html --post serve mynotebook.ipynb
```

## Python API 基本用法

### 使用 export 函数（最简单）

```python
import nbformat
from nbconvert.exporters import HTMLExporter, export

# 方式1：从文件转换
output, resources = export(HTMLExporter, "mynotebook.ipynb")

# 方式2：从NotebookNode对象转换
nb = nbformat.read("mynotebook.ipynb", as_version=4)
output, resources = export(HTMLExporter, nb)

# output是渲染后的HTML字符串
print(output[:500])
```

### 使用 Exporter 实例

```python
from nbconvert.exporters import HTMLExporter

exporter = HTMLExporter()
# 从文件转换
output, resources = exporter.from_filename("mynotebook.ipynb")
# 从NotebookNode转换
nb = nbformat.read("mynotebook.ipynb", as_version=4)
output, resources = exporter.from_notebook_node(nb)
```

### 使用 Writer 写入文件

```python
from nbconvert.exporters import HTMLExporter
from nbconvert.writers import FilesWriter

exporter = HTMLExporter()
output, resources = exporter.from_filename("mynotebook.ipynb")

writer = FilesWriter(build_directory="output/")
writer.write(output, resources, notebook_name="mynotebook")
```

### 使用配置自定义行为

```python
from traitlets.config import Config
from nbconvert.exporters import HTMLExporter

# 创建配置
c = Config()
c.HTMLExporter.exclude_input = True          # 排除代码输入
c.HTMLExporter.exclude_input_prompt = True   # 排除输入提示
c.HTMLExporter.template_name = "lab"         # 使用lab模板

exporter = HTMLExporter(config=c)
output, resources = exporter.from_filename("mynotebook.ipynb")
```

### 执行 Notebook

```python
from nbconvert.exporters import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor

exporter = HTMLExporter()
# 启用ExecutePreprocessor
ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
exporter.register_preprocessor(ep, enabled=True)

output, resources = exporter.from_filename("mynotebook.ipynb")
```

## 动态发现导出器

```python
from nbconvert.exporters import get_export_names, get_exporter

# 获取所有可用的导出器名称
print(get_export_names())
# ['asciidoc', 'custom', 'html', 'latex', 'markdown', 'notebook',
#  'pdf', 'python', 'qtpdf', 'qtpng', 'rst', 'script', 'slides', 'webpdf']

# 按名称获取导出器类
HTMLExporter = get_exporter("html")
```

## 下一步

- 了解nbconvert的核心架构：[架构总览](02-architecture-overview.md)
- 深入导出器体系：[导出器体系](03-exporter-hierarchy.md)
