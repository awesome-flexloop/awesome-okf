---
type: "concept"
title: "自定义导出器"
description: "继承TemplateExporter创建自定义导出器、注册entry points、配置自定义模板和过滤器"
tags: [custom-exporter, plugin, entry-points, extension]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: exporter-base
    resource: ../references/exporter-base-source.md
    title: "Exporter基类源码解析"
  - id: template-exporter
    resource: ../references/template-exporter-source.md
    title: "TemplateExporter源码解析"
  - id: factory
    resource: ../references/factory-source.md
    title: "导出器工厂函数源码解析"
---

# 自定义导出器

nbconvert支持通过继承和注册机制创建自定义导出器，扩展支持新的输出格式或定制已有格式的行为。

## 自定义导出器的三种方式

### 方式1：配置定制（最简单）

通过配置文件修改已有导出器的行为，无需编写新类：

```python
# my_config.py
c = get_config()

# 使用自定义模板
c.HTMLExporter.template_name = "my_template"
c.HTMLExporter.extra_template_basedirs = ["./templates"]

# 注册自定义过滤器
def upper_filter(text):
    return str(text).upper()
c.HTMLExporter.filters = {"upper": upper_filter}

# 配置预处理器
c.HTMLExporter.exclude_input = True
```

```bash
jupyter nbconvert --config my_config.py --to html notebook.ipynb
```

### 方式2：继承TemplateExporter（推荐）

创建新的导出器类，适用于需要新输出格式或深度定制的场景。

```python
from nbconvert.exporters import TemplateExporter

class DocxExporter(TemplateExporter):
    """自定义DOCX导出器示例"""
    
    # 输出文件扩展名
    file_extension = ".docx"
    
    # MIME类型
    output_mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    # 导出格式名称（在Notebook前端显示）
    export_from_notebook = "DOCX"
    
    # 默认使用的模板名称
    template_name = "docx"
    
    # 可以覆盖默认过滤器
    def default_filters(self):
        # 先获取父类的过滤器
        filters = dict(super().default_filters())
        # 添加或覆盖过滤器
        filters["my_custom_filter"] = my_filter_func
        return filters.items()
    
    # 可以覆盖预处理方法添加自定义逻辑
    def from_notebook_node(self, nb, resources=None, **kw):
        # 在调用父方法前的自定义处理
        output, resources = super().from_notebook_node(nb, resources, **kw)
        # 在渲染后的后处理
        return output, resources
```

### 方式3：继承Exporter基类（完全自定义）

当不需要Jinja2模板引擎时（如二进制格式输出），可以直接继承Exporter基类：

```python
from nbconvert.exporters import Exporter

class BinaryExporter(Exporter):
    """二进制格式导出示例"""
    
    file_extension = ".bin"
    output_mimetype = "application/octet-stream"
    
    def from_notebook_node(self, nb, resources=None, **kw):
        # 调用父类执行预处理
        nb_copy, resources = super().from_notebook_node(nb, resources, **kw)
        
        # 自定义渲染逻辑（不使用Jinja2）
        output = self._convert_to_binary(nb_copy, resources)
        return output, resources
    
    def _convert_to_binary(self, nb, resources):
        # 自定义二进制转换逻辑
        return b"binary data"
```

## 注册自定义导出器

### 方式1：Python API直接使用

```python
from nbconvert.exporters import export
output, resources = export(DocxExporter, "notebook.ipynb")
```

### 方式2：通过entry points注册（插件方式）

在第三方包的`pyproject.toml`中注册：

```toml
[project.entry-points."nbconvert.exporters"]
docx = "mypackage.exporters:DocxExporter"
```

安装后，导出器自动可用：

```bash
jupyter nbconvert --to docx notebook.ipynb
```

Python API中也能发现：

```python
from nbconvert.exporters import get_export_names, get_exporter
print("docx" in get_export_names())  # True
DocxExporter = get_exporter("docx")
```

### 方式3：配置文件中注册

```python
# jupyter_nbconvert_config.py
from mypackage.exporters import DocxExporter

c = get_config()
c.NbConvertApp.exporter_class = DocxExporter
```

## 自定义导出器模板

创建与导出器配套的模板目录：

```
mypackage/
├── exporters/
│   ├── __init__.py
│   └── docx.py          # DocxExporter类
└── templates/
    └── docx/
        ├── conf.json
        └── index.docx.j2
```

**conf.json：**
```json
{
  "base_template": "base",
  "mimetypes": {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": true
  }
}
```

**模板文件中设置template_data_paths：**
```python
from jupyter_core.paths import jupyter_path
import os

class DocxExporter(TemplateExporter):
    file_extension = ".docx"
    output_mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    template_name = "docx"
    
    @default("template_data_paths")
    def _template_data_paths(self):
        paths = super()._template_data_paths()
        # 添加包内模板路径
        pkg_templates = os.path.join(os.path.dirname(__file__), "..", "templates")
        paths.insert(0, pkg_templates)
        return paths
```

## 添加自定义预处理器和过滤器

```python
from nbconvert.exporters import TemplateExporter
from nbconvert.preprocessors import Preprocessor

class CodeCountPreprocessor(Preprocessor):
    """统计代码行数的预处理器"""
    enabled = True  # 默认启用
    
    def preprocess(self, nb, resources):
        code_lines = 0
        for cell in nb.cells:
            if cell.cell_type == "code":
                code_lines += len(cell.source.splitlines())
        resources["code_line_count"] = code_lines
        return nb, resources

class MyFormatExporter(TemplateExporter):
    file_extension = ".myfmt"
    
    def _init_preprocessors(self):
        super()._init_preprocessors()
        self.register_preprocessor(CodeCountPreprocessor, enabled=True)
    
    def default_filters(self):
        filters = dict(super().default_filters())
        filters["line_count_label"] = lambda n: f"共{n}行代码"
        return filters.items()
```

模板中使用：
```jinja2
{{ resources.code_line_count | line_count_label }}
```

## ExporterDisabledError与enabled属性

导出器可以通过`enabled=False`被禁用：

```python
class MyExporter(TemplateExporter):
    enabled = False  # 默认禁用，需要配置启用
```

```python
# 启用被禁用的导出器
c = Config()
c.MyExporter.enabled = True
```

## 相关概念

- [导出器体系](03-exporter-hierarchy.md)
- [预处理器系统](04-preprocessor-system.md)
- [自定义预处理器](10-custom-preprocessor.md)
- [自定义模板](11-custom-template.md)
