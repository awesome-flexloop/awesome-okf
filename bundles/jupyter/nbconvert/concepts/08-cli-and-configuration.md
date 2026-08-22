---
type: "concept"
title: "CLI与配置系统"
description: "jupyter nbconvert命令行工具详解、traitlets配置系统、配置文件编写方法"
tags: [cli, command-line, configuration, traitlets, config-file]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: nbconvertapp
    resource: "../../../../../../external/libs/jupyter/nbconvert/nbconvert/nbconvertapp.py"
    title: "nbconvertapp.py"
  - id: pyproject
    resource: "../../../../../../external/libs/jupyter/nbconvert/pyproject.toml"
    title: "pyproject.toml"
---

# CLI与配置系统

nbconvert基于Jupyter的`traitlets`配置框架，提供了统一的命令行接口和多层次的配置机制。

## CLI 命令详解

### 基本命令格式

```bash
jupyter nbconvert [options] <notebook_files...>
```

支持批量转换多个Notebook文件，支持glob模式。

### 输出格式选项（--to）

```bash
jupyter nbconvert --to <format> notebook.ipynb
```

可用格式（`--to`参数值）：

| 格式值 | 输出 | 说明 |
|--------|------|------|
| `html` | .html | HTML网页（默认模板lab） |
| `latex` | .tex | LaTeX文档 |
| `pdf` | .pdf | PDF（通过LaTeX） |
| `webpdf` | .pdf | PDF（通过Playwright浏览器） |
| `markdown` | .md | Markdown文档 |
| `rst` | .rst | reStructuredText |
| `asciidoc` | .asciidoc | AsciiDoc |
| `slides` | .slides.html | Reveal.js幻灯片 |
| `python` | .py | Python脚本 |
| `script` | 按语言 | 可执行脚本 |
| `notebook` | .ipynb | Notebook（预处理后） |
| `qtpdf` | .pdf | PDF（通过QtWebEngine） |
| `qtpng` | .png | PNG截图（通过QtWebEngine） |
| `custom` | 自定义 | 自定义模板导出 |

### 主要选项别名（aliases）

| CLI选项 | 配置路径 | 说明 |
|---------|---------|------|
| `--to <format>` | `NbConvertApp.export_format` | 输出格式 |
| `--template <name>` | `TemplateExporter.template_name` | 模板名称 |
| `--template-file <file>` | `TemplateExporter.template_file` | 模板文件路径 |
| `--theme <name>` | `HTMLExporter.theme` | 代码高亮主题 |
| `--writer <class>` | `NbConvertApp.writer_class` | Writer类 |
| `--post <class>` | `NbConvertApp.postprocessor_class` | PostProcessor类 |
| `--output <name>` | `NbConvertApp.output_base` | 输出文件名 |
| `--output-dir <dir>` | `FilesWriter.build_directory` | 输出目录 |
| `--reveal-prefix <url>` | `SlidesExporter.reveal_url_prefix` | Reveal.js URL前缀 |
| `--nbformat <ver>` | `NotebookExporter.nbformat_version` | Notebook格式版本 |
| `--config <file>` | - | 配置文件路径 |
| `--sanitize-html` | `HTMLExporter.sanitize_html` | HTML清洗 |

### 标志选项（flags）

| Flag | 设置的配置 | 说明 |
|------|-----------|------|
| `--execute` | `ExecutePreprocessor.enabled=True` | 转换前执行Notebook |
| `--allow-errors` | `ExecutePreprocessor.allow_errors=True` | 执行出错时继续 |
| `--stdin` | `NbConvertApp.from_stdin=True` | 从标准输入读取 |
| `--stdout` | `NbConvertApp.writer_class="StdoutWriter"` | 输出到stdout |
| `--inplace` | 输出到原文件（notebook格式） | 原地修改 |
| `--clear-output` | 启用ClearOutputPreprocessor | 清空输出并原地保存 |
| `--coalesce-streams` | 启用CoalesceStreamsPreprocessor | 合并流输出并原地保存 |
| `--no-prompt` | 排除输入/输出提示符 | 隐藏`In []:`/`Out[]:` |
| `--no-input` | 排除代码输入和输出提示 | 生成无代码报告 |
| `--allow-chromium-download` | 允许下载Chromium | WebPDF导出 |
| `--debug` | 设置日志级别为DEBUG | 调试模式 |

### 常用命令示例

```bash
# 基本转换
jupyter nbconvert --to html notebook.ipynb

# 执行并转换
jupyter nbconvert --execute --to html notebook.ipynb

# 指定输出目录和文件名
jupyter nbconvert --to html --output-dir ./docs --output report notebook.ipynb

# 使用lab模板
jupyter nbconvert --to html --template lab notebook.ipynb

# 无代码报告
jupyter nbconvert --to html --no-input notebook.ipynb

# 幻灯片并预览
jupyter nbconvert --to slides --post serve notebook.ipynb

# 清空输出（原地保存）
jupyter nbconvert --clear-output notebook.ipynb

# 从stdin读取并输出到stdout
cat notebook.ipynb | jupyter nbconvert --stdin --stdout --to markdown

# 批量转换
jupyter nbconvert --to html *.ipynb

# Markdown输出到stdout
jupyter nbconvert --to markdown --stdout notebook.ipynb
```

### jupyter-dejavu

除了`jupyter nbconvert`，还提供`jupyter dejavu`命令（`dejavu_main`入口点），这是一个重复执行nbconvert的工具，用于在文件变化时自动重新转换。

## 配置系统

nbconvert基于traitlets框架，支持多层次配置。

### 配置加载顺序

1. **命令行参数**（最高优先级）
2. **用户配置文件**（`~/.jupyter/jupyter_nbconvert_config.py`）
3. **环境变量**（`JUPYTER_CONFIG_DIR`等）
4. **默认值**（最低优先级）

### 配置文件格式

配置文件是Python文件（`.py`），使用`c = get_config()`获取配置对象，通过类名属性设置：

```python
# jupyter_nbconvert_config.py
c = get_config()

# 导出格式
c.NbConvertApp.export_format = "html"

# 模板设置
c.TemplateExporter.template_name = "lab"
c.TemplateExporter.exclude_input = True
c.TemplateExporter.exclude_input_prompt = True

# HTML导出器设置
c.HTMLExporter.theme = "light"

# 执行预处理器设置
c.ExecutePreprocessor.enabled = True
c.ExecutePreprocessor.timeout = 600
c.ExecutePreprocessor.kernel_name = "python3"

# 输出设置
c.FilesWriter.build_directory = "./output"

# 标签移除预处理器
c.TagRemovePreprocessor.remove_cell_tags = ("remove_cell",)
c.TagRemovePreprocessor.remove_input_tags = ("remove_input",)
```

### 使用配置文件

```bash
# 指定配置文件
jupyter nbconvert --config my_config.py notebook.ipynb

# 使用默认配置文件位置
# 将配置文件放在 ~/.jupyter/jupyter_nbconvert_config.py
jupyter nbconvert --to html notebook.ipynb
```

### Python API配置

在Python代码中使用`Config`对象：

```python
from traitlets.config import Config
from nbconvert.exporters import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor

# 创建配置
c = Config()

# 设置导出器选项
c.HTMLExporter.exclude_input = False
c.HTMLExporter.exclude_output_prompt = True
c.HTMLExporter.template_name = "lab"

# 设置预处理器
c.ExecutePreprocessor.timeout = 300
c.ExecutePreprocessor.kernel_name = "python3"
c.ExecutePreprocessor.allow_errors = False

# 创建导出器
exporter = HTMLExporter(config=c)

# 也可以注册额外预处理器
ep = ExecutePreprocessor(config=c)
exporter.register_preprocessor(ep, enabled=True)
```

### 类名引用规则

配置中使用的类名与Python模块路径对应：

| 配置类名 | 对应模块 |
|---------|---------|
| `NbConvertApp` | nbconvert.nbconvertapp |
| `TemplateExporter` | nbconvert.exporters.templateexporter |
| `HTMLExporter` | nbconvert.exporters.html |
| `LatexExporter` | nbconvert.exporters.latex |
| `MarkdownExporter` | nbconvert.exporters.markdown |
| `SlidesExporter` | nbconvert.exporters.slides |
| `ExecutePreprocessor` | nbconvert.preprocessors.execute |
| `TagRemovePreprocessor` | nbconvert.preprocessors.tagremove |
| `ClearOutputPreprocessor` | nbconvert.preprocessors.clearoutput |
| `FilesWriter` | nbconvert.writers.files |
| `StdoutWriter` | nbconvert.writers.stdout |
| `ServePostProcessor` | nbconvert.postprocessors.serve |
| `NbConvertBase` | nbconvert.utils.base（全局配置） |

### 常用配置项

#### 内容过滤

```python
c.TemplateExporter.exclude_code_cell = False
c.TemplateExporter.exclude_markdown = False
c.TemplateExporter.exclude_raw = False
c.TemplateExporter.exclude_input = False
c.TemplateExporter.exclude_output = False
c.TemplateExporter.exclude_input_prompt = False
c.TemplateExporter.exclude_output_prompt = False
c.TemplateExporter.exclude_output_stdin = True
c.TemplateExporter.exclude_unknown = False
```

#### 显示数据优先级

```python
c.NbConvertBase.display_data_priority = [
    "text/html",
    "image/svg+xml",
    "image/png",
    "image/jpeg",
    "text/markdown",
    "text/latex",
    "text/plain",
]
```

#### 自定义过滤器

```python
def my_filter(text):
    return text.upper()

c.TemplateExporter.filters = {"my_filter": my_filter}
```

#### 模板路径

```python
c.TemplateExporter.extra_template_basedirs = ["./my_templates"]
c.TemplateExporter.extra_template_paths = ["./shared_templates"]
```

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [导出器体系](03-exporter-hierarchy.md)
- [模板系统](05-template-system.md)
- [自定义导出器](09-custom-exporter.md)
