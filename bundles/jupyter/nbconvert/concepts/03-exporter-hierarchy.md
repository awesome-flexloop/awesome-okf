---
type: "concept"
title: "导出器体系"
description: "Exporter类层次结构、TemplateExporter核心机制、14种内置导出器详解与工厂函数"
tags: [exporter, hierarchy, template-exporter, builtin-exporters, factory]
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
  - id: nbconvert-base
    resource: ../references/nbconvert-base-source.md
    title: "NbConvertBase配置基类源码解析"
---

# 导出器体系

导出器（Exporter）是nbconvert的核心组件，负责执行预处理管道并通过Jinja2模板将Notebook渲染为目标格式。

## 类层次结构

```
NbConvertBase
└── Exporter（预处理管道管理者）
    └── TemplateExporter（Jinja2模板引擎）
        ├── HTMLExporter          → .html
        ├── LatexExporter         → .tex
        │   └── PDFExporter       → .pdf（通过LaTeX编译）
        ├── MarkdownExporter      → .md
        ├── SlidesExporter        → .html（Reveal.js幻灯片）
        ├── PythonExporter        → .py
        ├── ScriptExporter        → 通用脚本
        ├── RSTExporter           → .rst
        ├── ASCIIDocExporter      → .asciidoc
        ├── NotebookExporter      → .ipynb
        ├── WebPDFExporter        → .pdf（通过Playwright）
        ├── QtPDFExporter         → .pdf（通过QtWebEngine）
        └── QtPNGExporter         → .png（通过QtWebEngine）
```

## Exporter 基类

`Exporter` 类管理预处理器管道的执行流程，提供三个输入入口方法。

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `enabled` | Bool | 是否启用此导出器（默认True） |
| `file_extension` | FilenameExtension | 输出文件扩展名（如".html"） |
| `output_mimetype` | str（类属性） | 输出MIME类型 |
| `export_from_notebook` | str | 在Notebook前端显示的名称 |
| `preprocessors` | List | 用户配置的预处理器列表 |
| `default_preprocessors` | List | 默认注册的11个预处理器名称 |
| `optimistic_validation` | Bool | 是否仅在最后验证Notebook（默认False） |

### 三个输入入口

```
from_filename(filename, resources=None)
  → 设置metadata（name/path/modified_date）
  → 打开文件 → from_file()

from_file(file_stream, resources=None)
  → nbformat.read(file_stream, as_version=4)
  → from_notebook_node()

from_notebook_node(nb, resources=None)
  → deepcopy(nb)
  → _init_resources(resources)
  → 设置language
  → _preprocess(nb_copy, resources)  ← 执行预处理管道
  → 返回 (nb_copy, resources)
```

> **注意**：Exporter基类的from_notebook_node返回(NotebookNode, resources)，而TemplateExporter重写后返回(str, resources)（渲染后的字符串）。

### 预处理器注册机制

`register_preprocessor(preprocessor, enabled=False)` 支持四种参数形式：

1. **字符串**：点分模块路径（如"nbconvert.preprocessors.ExecutePreprocessor"），通过`import_item`导入后递归注册
2. **函数/可调用对象**：直接添加到`_preprocessors`列表
3. **HasTraits子类**：实例化时传入`parent=self`以继承配置
4. **普通类**：直接实例化后注册

## TemplateExporter 核心

`TemplateExporter` 是所有实际格式导出器的直接父类，实现了完整的Jinja2模板渲染逻辑。

### 模板查找与加载

模板通过多层级的路径系统查找：

1. `extra_loaders`：用户自定义Jinja2 Loader（最高优先级）
2. `extra_template_basedirs` + `extra_template_paths`：用户自定义模板目录
3. `template_data_paths`：通过`jupyter_path("nbconvert", "templates")`查找
4. Jupyter数据目录中的`nbconvert/templates/`
5. DEV模式下源码目录的`share/jupyter/nbconvert/templates/`
6. `compatibility/`目录（5.x旧版模板兼容）

使用`ExtensionTolerantLoader`包装FileSystemLoader，当查找模板名失败时自动追加`template_extension`（如`.html.j2`）重试。

### 模板继承链解析

`get_template_names()`方法解析conf.json中的`base_template`形成继承链：

```
lab模板查找过程：
  lab/conf.json → base_template: "base"
  base/conf.json → base_template: null
  返回 ["lab", "base"]
```

所有路径的conf.json通过`recursive_update`递归合并，子模板配置覆盖父模板。

### Jinja2 Environment 创建

`_create_environment()`方法：
1. 构建ChoiceLoader链
2. 创建Environment，加载`jinja2.ext.loopcontrols`扩展
3. 注入`uuid4`全局函数
4. 注册default_filters中的40+个过滤器
5. 注册用户自定义filters（覆盖默认）

### 渲染流程

`from_notebook_node()`重写方法：

```python
def from_notebook_node(self, nb, resources=None, **kw):
    nb_copy, resources = super().from_notebook_node(nb, resources, **kw)
    resources["global_content_filter"] = {
        "include_code": not self.exclude_code_cell,
        "include_markdown": not self.exclude_markdown,
        "include_input": not self.exclude_input,
        "include_output": not self.exclude_output,
        # ... 更多过滤选项
    }
    output = self.template.render(nb=nb_copy, resources=resources)
    output = output.lstrip("\r\n")
    return output, resources
```

### 内容过滤选项

TemplateExporter提供了一系列布尔trait用于控制输出内容：

| Trait | 默认 | 效果 |
|-------|------|------|
| `exclude_code_cell` | False | 排除所有code cell |
| `exclude_markdown` | False | 排除markdown cell |
| `exclude_raw` | False | 排除raw cell |
| `exclude_input` | False | 排除代码输入部分 |
| `exclude_output` | False | 排除代码输出部分 |
| `exclude_input_prompt` | False | 排除输入提示符（`In [1]:`） |
| `exclude_output_prompt` | False | 排除输出提示符（`Out[1]:`） |
| `exclude_output_stdin` | True | 排除stdin流输出 |
| `exclude_unknown` | False | 排除未知类型cell |

### conf.json预处理器配置

TemplateExporter重写`_init_preprocessors()`，额外从conf.json加载预处理器配置：

```json
{
  "preprocessors": {
    "01-tagrremove": {"type": "nbconvert.preprocessors.TagRemovePreprocessor"},
    "02-clearmeta": null
  }
}
```

- 数字前缀保证处理顺序（类似`/etc/rc.d/`风格）
- 值为`null`表示禁用该预处理器
- `type`字段指定预处理器类

## 内置导出器详解

### HTMLExporter

- **输出格式**：HTML（`.html`）
- **MIME类型**：`text/html`
- **默认模板**：`lab`（JupyterLab风格）
- **功能**：生成包含CSS样式的自包含HTML文件，支持代码高亮、数学公式（MathJax）、Widget嵌入
- **模板选项**：`lab`（默认）、`classic`（经典Notebook风格）、`basic`（最小HTML）

### LatexExporter / PDFExporter

- **LatexExporter**：输出LaTeX（`.tex`）文件
- **PDFExporter**：继承LatexExporter，通过LaTeX编译器（xelatex）生成PDF
- **MIME类型**：`text/latex` / `application/pdf`
- **依赖**：需要安装TeX发行版

### MarkdownExporter

- **输出格式**：Markdown（`.md`）
- **MIME类型**：`text/markdown`
- **功能**：将Notebook转换为Markdown，图片输出到`{notebook_name}_files/`目录
- **模板**：`markdown`

### SlidesExporter

- **输出格式**：HTML幻灯片（`.slides.html`）
- **MIME类型**：`text/html`
- **框架**：Reveal.js
- **功能**：基于cell的slideshow metadata（slide类型：slide/subslide/fragment/skip/notes）生成演示文稿
- **模板**：`reveal`

### PythonExporter / ScriptExporter

- **PythonExporter**：输出Python脚本（`.py`），仅保留code cell，用`# In[1]:`分隔
- **ScriptExporter**：通用脚本导出器，根据notebook metadata中的language_info选择语言模板
- **模板**：`python` / `script`

### RSTExporter / ASCIIDocExporter

- **RSTExporter**：输出reStructuredText（`.rst`），适用于Sphinx文档
- **ASCIIDocExporter**：输出AsciiDoc（`.asciidoc`）格式
- **依赖**：需要pandoc进行Markdown到目标格式的转换

### NotebookExporter

- **输出格式**：Notebook（`.ipynb`）
- **功能**：输入和输出都是.ipynb格式，主要用于预处理后重新保存Notebook（如执行完代码后保存）
- **不使用Jinja2模板**

### WebPDFExporter

- **输出格式**：PDF（`.pdf`）
- **渲染引擎**：Playwright无头浏览器
- **流程**：先渲染为HTML，再通过Chromium打印为PDF
- **可选依赖**：`pip install nbconvert[webpdf] && playwright install`

### QtPDFExporter / QtPNGExporter

- **输出格式**：PDF/PNG
- **渲染引擎**：QtWebEngine（PyQt）
- **可选依赖**：`pip install nbconvert[qtpng]`或`nbconvert[qtpdf]`

## 工厂函数

### export(exporter, nb, \**kw)

一站式导出函数，自动处理输入类型分发：

```python
from nbconvert.exporters import HTMLExporter, export

# 从NotebookNode导出
nb = nbformat.read("notebook.ipynb", as_version=4)
output, resources = export(HTMLExporter, nb)

# 从文件路径导出
output, resources = export(HTMLExporter, "notebook.ipynb", config=my_config)
```

### get_exporter(name, config=None)

按名称或导入路径获取导出器类：

```python
from nbconvert.exporters import get_exporter

HTMLExporter = get_exporter("html")
MyExporter = get_exporter("mypackage.exporters.MyExporter")
```

查找顺序：entry points → 完整导入路径 → 抛出ExporterNameError。

### get_export_names(config=None)

返回当前可用的导出器名称列表（仅enabled的）：

```python
from nbconvert.exporters import get_export_names
print(get_export_names())
# ['asciidoc', 'custom', 'html', 'latex', 'markdown', 'notebook',
#  'pdf', 'python', 'qtpdf', 'qtpng', 'rst', 'script', 'slides', 'webpdf']
```

## 相关概念

- [架构总览](02-architecture-overview.md)
- [预处理器系统](04-preprocessor-system.md)
- [模板系统](05-template-system.md)
- [CLI与配置](08-cli-and-configuration.md)
