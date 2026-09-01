---
type: "concept"
title: "自定义模板"
description: "创建自定义Jinja2模板、conf.json配置、模板继承链、目录结构设计"
tags: [custom-template, jinja2, template-inheritance, conf-json, skeleton]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: template-exporter
    resource: ../references/template-exporter-source.md
    title: "TemplateExporter源码解析"
  - id: factory
    resource: ../references/factory-source.md
    title: "导出器工厂函数源码解析"
---

# 自定义模板

自定义模板是定制nbconvert输出外观和结构最常用的方式。模板基于Jinja2引擎，通过目录结构和`conf.json`配置文件组织，支持模板继承。

## 模板目录结构

一个完整的模板目录结构如下：

```
my_template/
├── conf.json          # 模板配置文件（必需）
├── index.py.j2        # 主模板文件（扩展名匹配导出器template_extension）
├── base.py.j2         # 可选：基础骨架模板
├── skeleton/          # 可选：骨架片段目录
│   ├── header.py.j2
│   ├── footer.py.j2
│   ├── code-cell.py.j2
│   ├── markdown-cell.py.j2
│   └── ...
├── static/            # 可选：静态资源（CSS/JS/图片等）
│   ├── style.css
│   └── main.js
└── resources/         # 可选：模板配置资源
    └── ...
```

模板名称即为目录名称。

## conf.json 配置详解

`conf.json`是模板的元数据文件，控制模板的继承关系和行为。

### 基本配置

```json
{
  "base_template": "base",
  "mimetypes": {
    "text/x-python": true
  }
}
```

### 完整配置选项

```json
{
  "base_template": "lab",
  "mimetypes": {
    "text/html": true
  },
  "preprocessors": [
    "nbconvert.preprocessors.coalesce_streams.CoalesceStreamsPreprocessor"
  ],
  "filters": {
    "my_filter": "mypackage.filters.my_filter_function"
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `base_template` | string | 父模板名称，形成继承链 |
| `mimetypes` | object | 支持的MIME类型，键为MIME类型，值为true |
| `preprocessors` | array | 模板默认启用的预处理器（点路径字符串） |
| `filters` | object | 模板注册的过滤器，键为过滤器名，值为点路径字符串 |

### 模板继承链

nbconvert的内置模板形成继承链：

```
base
├── skeleton (通过skeleton/目录提供片段)
├── lab
│   ├── lab/
│   └── classic（继承自lab）
├── classic
├── reveal（slides格式）
├── markdown
├── rst
├── asciidoc
├── python
└── article（LaTeX）
```

自定义模板可以选择任意内置模板作为`base_template`：
- `base`：最基础，提供cell级骨架
- `skeleton`：提供通用文档骨架片段
- `lab`：Jupyter Lab风格HTML
- `classic`：经典Jupyter Notebook风格HTML

## Jinja2模板语法基础

nbconvert模板使用Jinja2语法，但有nbconvert特有的变量和模式。

### 可用变量

| 变量 | 类型 | 说明 |
|------|------|------|
| `nb` | NotebookNode | 完整Notebook对象（经过预处理） |
| `resources` | dict | 资源字典，包含metadata/outputs等 |
| `resources.global_content_filter` | dict | 全局内容过滤开关 |

### 模板中可用的全局函数

| 函数 | 说明 |
|------|------|
| `add_prompts(text, in_prompt, out_prompt)` | 添加输入/输出提示符 |
| `ansi2html(text)` | ANSI转HTML颜色 |
| `ansi2latex(text)` | ANSI转LaTeX颜色 |
| `filter_data_type(data, metadata)` | 按优先级选择输出MIME类型 |
| `get_lines(text, start, end)` | 获取文本的行范围 |
| `highlight2html(source, metadata)` | HTML代码高亮 |
| `highlight2latex(source, metadata)` | LaTeX代码高亮 |
| `markdown2html(source)` | Markdown转HTML |
| `markdown2latex(source)` | Markdown转LaTeX |
| `markdown2rst(source)` | Markdown转RST |
| `markdown2asciidoc(source)` | Markdown转AsciiDoc |
| `clean_html(html)` | 清洗HTML |
| `escape_latex(text)` | 转义LaTeX特殊字符 |
| `strip_files_prefix(text)` | 移除files/前缀 |
| `posix_path(path)` | 转换为POSIX路径 |
| `prevent_list_blocks(text)` | 防止列表嵌套问题 |
| `indent(text, n)` | 缩进文本 |
| `json_dumps(obj)` | JSON序列化 |

### cell级骨架（block模式）

使用`block`模式按cell类型分块处理：

```jinja2
{%- extends 'base.j2' -%}

{% block header %}
<!DOCTYPE html>
<html>
<head>
  <title>{{ resources.metadata.name }}</title>
  <link rel="stylesheet" href="static/style.css">
</head>
<body>
{% endblock header %}

{% block body %}
<div class="notebook">
  {{ super() }}
</div>
{% endblock body %}

{% block footer %}
</body>
</html>
{% endblock footer %}

{% block codecell %}
<div class="code-cell">
  {{ super() }}
</div>
{% endblock codecell %}
```

### 手动遍历cell模式

```jinja2
{%- extends 'base.j2' -%}

{% block body %}
<article>
  {% for cell in nb.cells %}
    {% if cell.cell_type == 'markdown' %}
      <section class="markdown-cell">
        {{ cell.source | markdown2html | clean_html }}
      </section>
    {% elif cell.cell_type == 'code' %}
      <section class="code-cell">
        <pre class="input">{{ cell.source | highlight2html(metadata=nb.metadata) }}</pre>
        {% for output in cell.outputs %}
          {% if output.output_type == 'stream' %}
            <pre class="output stream">{{ output.text | ansi2html }}</pre>
          {% elif output.output_type in ('execute_result', 'display_data') %}
            <div class="output data">
              {{ output.data['text/html'] | safe if output.data.get('text/html') else output.data['text/plain'] }}
            </div>
          {% elif output.output_type == 'error' %}
            <pre class="output error">{{ output.traceback | join('\n') | ansi2html }}</pre>
          {% endif %}
        {% endfor %}
      </section>
    {% elif cell.cell_type == 'raw' %}
      <section class="raw-cell">{{ cell.source }}</section>
    {% endif %}
  {% endfor %}
</article>
{% endblock body %}
```

## 创建自定义HTML模板示例

### 步骤1：创建模板目录

```bash
mkdir -p ./my_templates/blog
mkdir -p ./my_templates/blog/static
```

### 步骤2：创建conf.json

```json
{
  "base_template": "lab",
  "mimetypes": {
    "text/html": true
  }
}
```

### 步骤3：创建主模板index.html.j2

```jinja2
{%- extends 'lab/index.html.j2' -%}

{% block header %}
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ resources.metadata.name }}</title>
  <style>
    body { max-width: 800px; margin: 0 auto; padding: 20px; font-family: sans-serif; }
    .code-cell { background: #f5f5f5; padding: 10px; border-radius: 4px; margin: 10px 0; }
    .markdown-cell img { max-width: 100%; }
  </style>
</head>
<body>
{% endblock header %}

{% block footer %}
<footer>
  <p>Generated by nbconvert</p>
</footer>
</body>
</html>
{% endblock footer %}
```

### 步骤4：使用自定义模板

```bash
# 命令行使用
jupyter nbconvert --to html --template blog \
  --TemplateExporter.extra_template_basedirs=./my_templates \
  notebook.ipynb
```

```python
# Python API使用
from nbconvert.exporters import HTMLExporter
exporter = HTMLExporter(
    template_name="blog",
    extra_template_basedirs=["./my_templates"]
)
output, resources = exporter.from_filename("notebook.ipynb")
```

## 使用skeleton片段复用模板

在模板目录下创建`skeleton/`子目录，Jinja2加载器会自动将其作为命名空间，可通过`include`引用：

```
my_template/
├── conf.json
├── index.html.j2
└── skeleton/
    ├── header.html.j2
    ├── toc.html.j2
    └── footer.html.j2
```

**index.html.j2中引用：**
```jinja2
{% include 'skeleton/header.html.j2' %}

{% block body %}{{ super() }}{% endblock body %}

{% include 'skeleton/footer.html.j2' %}
```

## 注册模板为包（插件方式）

在第三方Python包中注册模板，使其全局可用：

1. 将模板目录放在包内：
```
mypackage/
├── __init__.py
└── templates/
    └── my_template/
        ├── conf.json
        └── index.html.j2
```

2. 在`pyproject.toml`中注册：
```toml
[project.entry-points."nbconvert.exporters"]
my_template = "mypackage:MyTemplateExporter"
```

3. 导出器指定模板路径：
```python
from nbconvert.exporters import HTMLExporter
import os

class MyTemplateExporter(HTMLExporter):
    template_name = "my_template"
    export_from_notebook = "My Template"
    
    @default("template_data_paths")
    def _template_data_paths(self):
        paths = super()._template_data_paths()
        pkg_templates = os.path.join(os.path.dirname(__file__), "templates")
        paths.insert(0, pkg_templates)
        return paths
```

## 模板调试技巧

### 查看模板变量

```jinja2
{# 在模板中打印所有可用变量 #}
<pre>{{ nb | json_dumps(indent=2) }}</pre>
```

### 查看资源字典

```jinja2
<pre>{{ resources | json_dumps(indent=2) }}</pre>
```

### 查看所有可用过滤器

模板中无法直接列出过滤器列表，但可通过导出器的`environment.filters`属性在Python中检查：

```python
exporter = HTMLExporter()
print(sorted(exporter.environment.filters.keys()))
```

## 相关概念

- [模板系统](05-template-system.md)
- [过滤器系统](06-filters-system.md)
- [自定义导出器](09-custom-exporter.md)
