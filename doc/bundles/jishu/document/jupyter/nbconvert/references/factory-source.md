---
type: "Reference"
title: "导出器工厂函数源码解析"
description: "nbconvert.exporters.base模块：export、get_exporter、get_export_names工厂函数源码解析"
tags: [factory, export, entry-points, plugin, source-code]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: base-py
    resource: "../../../../../../external/libs/jupyter/nbconvert/nbconvert/exporters/base.py"
    title: "exporters/base.py"
  - id: pyproject
    resource: "../../../../../../external/libs/jupyter/nbconvert/pyproject.toml"
    title: "pyproject.toml"
---

# 导出器工厂函数源码解析

> 源码路径：`nbconvert/exporters/base.py`

## 模块概述

本模块提供nbconvert的三个顶层工厂函数：`export()`、`get_exporter()`、`get_export_names()`，实现了导出器的动态发现、实例化和一站式导出功能。

## 异常类

### ExporterNameError

```python
class ExporterNameError(NameError):
    """An exporter name error."""
```

- 继承自`NameError`
- 当请求的导出器名称不存在时抛出
- 错误消息会提示可用的导出器名称列表

### ExporterDisabledError

```python
class ExporterDisabledError(ValueError):
    """An exporter disabled error."""
```

- 继承自`ValueError`
- 当导出器存在但被配置禁用时抛出

## export函数

```python
def export(exporter, nb, **kw):
```

**参数：**
- `exporter`：Exporter类或实例
- `nb`：NotebookNode对象、文件路径字符串、或文件流对象
- `**kw`：额外参数（config、resources等传递给Exporter构造函数）

**返回：** `(output, resources)`元组

**执行流程：**

```
export(exporter, nb, **kw)
│
├─ 参数校验
│   ├─ exporter is None → TypeError
│   ├─ exporter不是Exporter子类/实例 → TypeError
│   └─ nb is None → TypeError
│
├─ 创建/使用exporter实例
│   ├─ resources = kw.pop("resources", None)
│   └─ exporter_instance = exporter if isinstance(exporter, Exporter) else exporter(**kw)
│
└─ 根据nb类型分发
    ├─ NotebookNode实例 → exporter_instance.from_notebook_node(nb, resources)
    ├─ str类型 → exporter_instance.from_filename(nb, resources)
    └─ 其他（文件流）→ exporter_instance.from_file(nb, resources)
```

**使用示例：**

```python
import nbformat
from nbconvert.exporters import HTMLExporter, export

# 方式1：传入类
nb = nbformat.read("notebook.ipynb", as_version=4)
output, resources = export(HTMLExporter, nb)

# 方式2：传入实例（自定义配置）
from traitlets.config import Config
c = Config()
c.HTMLExporter.exclude_input = True
exporter = HTMLExporter(config=c)
output, resources = export(exporter, "notebook.ipynb")
```

## get_exporter函数

```python
def get_exporter(name, config=None):
```

**参数：**
- `name`：导出器名称（如"html"、"latex"）或完整导入路径（如"mypackage.MyExporter"）
- `config`：可选的traitlets Config对象

**返回：** Exporter类（注意：不是实例）

**查找流程：**

1. **别名处理**：`"ipynb"` → `"notebook"`
2. **Entry Points查找**：
   - 使用`importlib.metadata.entry_points(group="nbconvert.exporters")`
   - 匹配name或name.lower()
   - 加载并检查enabled属性
3. **完整导入路径查找**：
   - 如果name包含"."，尝试`import_item(name)`
   - 同样检查enabled属性
4. **未找到**：抛出`ExporterNameError`，消息中包含所有可用导出器名

**内置Entry Points注册**（pyproject.toml）：

```toml
[project.entry-points."nbconvert.exporters"]
custom = "nbconvert.exporters:TemplateExporter"
html = "nbconvert.exporters:HTMLExporter"
slides = "nbconvert.exporters:SlidesExporter"
latex = "nbconvert.exporters:LatexExporter"
pdf = "nbconvert.exporters:PDFExporter"
qtpdf = "nbconvert.exporters:QtPDFExporter"
qtpng = "nbconvert.exporters:QtPNGExporter"
webpdf = "nbconvert.exporters:WebPDFExporter"
markdown = "nbconvert.exporters:MarkdownExporter"
python = "nbconvert.exporters:PythonExporter"
rst = "nbconvert.exporters:RSTExporter"
notebook = "nbconvert.exporters:NotebookExporter"
asciidoc = "nbconvert.exporters:ASCIIDocExporter"
script = "nbconvert.exporters:ScriptExporter"
```

## get_export_names函数

```python
def get_export_names(config=None):
```

**返回：** 当前可用的导出器名称列表（已排序，且仅包含enabled的导出器）

**特殊环境变量：**
- `NBCONVERT_DISABLE_CONFIG_EXPORTERS`：设置后跳过配置检查，直接返回所有entry points名称

**执行流程：**

1. 从entry points获取所有导出器名称并排序
2. 如果禁用了配置导出器，直接返回
3. 对每个导出器名称，调用`get_exporter(name)(config=config)`实例化
4. 检查`e.enabled`，收集启用的导出器名称
5. 捕获`ExporterDisabledError`和`ValueError`（跳过不可用的）

## 插件扩展机制

第三方包可以通过entry points注册自定义导出器：

```toml
# pyproject.toml
[project.entry-points."nbconvert.exporters"]
myformat = "mypackage.exporters:MyFormatExporter"
```

安装后，`jupyter nbconvert --to myformat notebook.ipynb`即可使用。
