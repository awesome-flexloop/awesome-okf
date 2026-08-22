---
type: "concept"
title: "模板系统"
description: "nbconvert基于Jinja2的模板系统：目录结构、conf.json配置、模板继承链、内置模板与自定义模板"
tags: [template, jinja2, conf.json, template-inheritance, custom-template]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: template-exporter
    resource: ../references/template-exporter-source.md
    title: "TemplateExporter源码解析"
  - id: filters
    resource: ../references/filters-source.md
    title: "过滤器模块源码解析"
---

# 模板系统

模板系统是nbconvert的核心——所有格式输出都通过Jinja2模板渲染生成。nbconvert采用**目录式模板**设计，每个模板是一个包含`conf.json`配置文件和`.j2`模板文件的目录，支持通过`base_template`形成继承链。

## 模板目录结构

```
share/jupyter/nbconvert/templates/
├── base/                  ← 基础模板（所有模板的根）
│   ├── conf.json
│   ├── null.j2
│   ├── display_priority.j2
│   ├── celltags.j2
│   ├── cell_id_anchor.j2
│   ├── jupyter_widgets.html.j2
│   └── mathjax.html.j2
├── lab/                   ← JupyterLab风格模板
│   ├── conf.json
│   ├── index.html.j2      ← 主模板
│   ├── base.html.j2       ← 继承base
│   ├── conf.json
│   └── mermaidjs.html.j2  ← Mermaid图表支持
├── classic/               ← 经典Jupyter风格
│   ├── conf.json
│   ├── index.html.j2
│   └── base.html.j2
├── latex/                 ← LaTeX模板
│   ├── conf.json
│   ├── index.tex.j2
│   ├── base.tex.j2
│   ├── document_contents.tex.j2
│   ├── display_priority.j2
│   ├── null.j2
│   ├── report.tex.j2
│   └── style_*.tex.j2     ← 多种样式文件
├── markdown/              ← Markdown模板
│   ├── conf.json
│   └── index.md.j2
├── python/                ← Python脚本模板
│   ├── conf.json
│   └── index.py.j2
├── reveal/                ← Reveal.js幻灯片模板
│   ├── conf.json
│   ├── index.html.j2
│   ├── base.html.j2
│   ├── cellslidedata.j2
│   └── static/
│       └── custom_reveal.css
├── rst/                   ← reStructuredText模板
│   ├── conf.json
│   └── index.rst.j2
├── asciidoc/              ← AsciiDoc模板
│   ├── conf.json
│   └── index.asciidoc.j2
├── script/                ← 通用脚本模板
│   ├── conf.json
│   └── script.j2
├── webpdf/                ← WebPDF模板
│   ├── conf.json
│   └── index.pdf.j2
├── basic/                 ← 基础HTML模板
│   ├── conf.json
│   └── index.html.j2
└── compatibility/         ← 5.x旧版模板兼容
    ├── display_priority.tpl
    └── full.tpl
```

## conf.json 配置文件

每个模板目录下的`conf.json`是模板的配置文件，控制模板的行为和继承关系。

### 核心配置项

```json
{
  "base_template": "base",
  "mimetypes": {
    "text/html": true
  },
  "preprocessors": {
    "01-tagrremove": {"type": "nbconvert.preprocessors.TagRemovePreprocessor"}
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `base_template` | string | 父模板名称，形成继承链；为null表示根模板 |
| `mimetypes` | dict | 支持的MIME类型，key为MIME类型，value为bool |
| `preprocessors` | dict | 需要启用的预处理器，数字前缀控制顺序 |

### 配置合并机制

模板继承链上的conf.json通过`recursive_update`递归合并：
- 子模板配置覆盖父模板
- 字典类型递归合并
- 值为`null`表示删除该键
- preprocessors按数字前缀排序

## 模板继承链

以`lab`模板为例，继承链解析过程：

```
get_template_names("lab")
│
├─ 查找 lab/conf.json
│   ├─ base_template: "base"
│   └─ 加入模板名列表: ["lab"]
│
├─ 查找 base/conf.json
│   ├─ base_template: null（终止）
│   └─ 加入模板名列表: ["lab", "base"]
│
└─ 返回 ["lab", "base"]
```

模板路径按照继承链顺序添加到Jinja2搜索路径中，子模板可以通过Jinja2的`{% extends %}`继承父模板。

### base 模板（根模板）

`base`模板是所有模板的根，提供：
- `null.j2`：空输出块
- `display_priority.j2`：按display_data_priority选择输出格式
- `celltags.j2`：cell标签处理逻辑
- `cell_id_anchor.j2`：cell锚点生成
- 通用的Widget和MathJax支持

## Jinja2 模板编写

### 模板中的变量

模板渲染时可访问两个顶级变量：

| 变量 | 类型 | 说明 |
|------|------|------|
| `nb` | NotebookNode | 当前Notebook对象 |
| `resources` | dict | 资源字典（metadata、output_extension、global_content_filter等） |

### 常用模板结构

```jinja2
{%- extends 'base.html.j2' -%}

{% block header %}
{# 自定义头部内容 #}
{% endblock header %}

{% block body %}
{% for cell in nb.cells %}
  {% if cell.cell_type == 'markdown' %}
    {{ cell.source | markdown2html }}
  {% elif cell.cell_type == 'code' %}
    {% block code_cell %}
      <div class="cell code_cell">
        {% if not resources.global_content_filter.include_input %}
          {# 跳过输入 #}
        {% else %}
          <div class="input">{{ cell.source | highlight2html(nb.metadata) }}</div>
        {% endif %}
        
        {% for output in cell.outputs %}
          {% if output.output_type == 'stream' %}
            <pre>{{ output.text | ansi2html }}</pre>
          {% elif output.output_type in ('execute_result', 'display_data') %}
            {{ output | filter_data_type | safe }}
          {% elif output.output_type == 'error' %}
            <pre class="error">{{ output.traceback | join('\n') | ansi2html }}</pre>
          {% endif %}
        {% endfor %}
      </div>
    {% endblock code_cell %}
  {% endif %}
{% endfor %}
{% endblock body %}
```

### 内置Jinja2过滤器

模板中可使用40+个内置过滤器，主要分类：

**Markdown转换：**
- `{{ source | markdown2html }}` — Markdown→HTML
- `{{ source | markdown2latex }}` — Markdown→LaTeX
- `{{ source | markdown2rst }}` — Markdown→RST

**代码高亮：**
- `{{ source | highlight2html(metadata) }}` — 代码→HTML高亮
- `{{ source | highlight2latex(metadata) }}` — 代码→LaTeX高亮

**ANSI处理：**
- `{{ text | ansi2html }}` — ANSI颜色→HTML
- `{{ text | ansi2latex }}` — ANSI颜色→LaTeX
- `{{ text | strip_ansi }}` — 剥离ANSI转义

**文本处理：**
- `{{ text | indent(n=4) }}` — 缩进文本
- `{{ text | wrap_text(width=80) }}` — 自动换行
- `{{ text | strip_trailing_newline }}` — 移除尾部换行
- `{{ text | comment_lines(prefix='# ') }}` — 注释每行

**HTML/LaTeX：**
- `{{ text | clean_html }}` — HTML清洗（XSS防护）
- `{{ text | escape_latex }}` — LaTeX特殊字符转义
- `{{ text | escape_html }}` — HTML转义

**工具函数：**
- `{{ cell | get_metadata('key', 'default') }}` — 安全获取metadata
- `{{ path | path2url }}` — 路径转URL
- `{{ text | add_prompts(prompt, cont) }}` — 添加输入/输出提示
- `{{ output | filter_data_type }}` — 按display_data_priority选择输出格式

全局函数：
- `uuid4()` — 生成UUID（用于唯一锚点）

### resources.global_content_filter

控制内容显示的布尔标志字典：

| 键 | 含义 |
|----|------|
| `include_code` | 是否包含code cell |
| `include_markdown` | 是否包含markdown cell |
| `include_raw` | 是否包含raw cell |
| `include_unknown` | 是否包含未知类型cell |
| `include_input` | 是否包含代码输入 |
| `include_output` | 是否包含代码输出 |
| `include_input_prompt` | 是否包含输入提示（`In [1]:`） |
| `include_output_prompt` | 是否包含输出提示（`Out[1]:`） |
| `include_output_stdin` | 是否包含stdin流 |
| `no_prompt` | 是否同时隐藏输入输出提示 |

## 内置模板详解

### lab（默认HTML模板）

- **输出格式**：HTML
- **MIME类型**：`text/html`
- **风格**：JupyterLab样式
- **特性**：支持Mermaid图表、MathJax、Jupyter Widgets
- **对应CLI**：`jupyter nbconvert --to html --template lab`（默认）

### classic（经典HTML模板）

- **输出格式**：HTML
- **风格**：经典Jupyter Notebook样式
- **对应CLI**：`jupyter nbconvert --to html --template classic`

### basic（基础HTML模板）

- **输出格式**：HTML
- **风格**：最小HTML框架，无自定义样式
- **用途**：自定义模板的基础或需要嵌入其他页面时

### reveal（Reveal.js幻灯片）

- **输出格式**：HTML
- **框架**：Reveal.js
- **用法**：在cell metadata中设置`slideshow.slide_type`为`slide`/`subslide`/`fragment`/`skip`/`notes`
- **对应CLI**：`jupyter nbconvert --to slides`

### latex（LaTeX模板）

- **输出格式**：.tex
- **MIME类型**：`text/latex`
- **特性**：支持多种文档样式（`style_ipython`、`style_jupyter`、`style_python`、`style_bw_ipython`、`style_bw_python`）
- **支持report/article文档类**
- **对应CLI**：`jupyter nbconvert --to latex`

### markdown（Markdown模板）

- **输出格式**：.md
- **特性**：代码块使用fenced code格式，图片提取到`{name}_files/`目录
- **对应CLI**：`jupyter nbconvert --to markdown`

### python/script（脚本模板）

- **python**：输出.py文件，code cell用`# In[1]:`注释分隔
- **script**：通用脚本，根据metadata.language_info选择模板
- **对应CLI**：`jupyter nbconvert --to python` / `--to script`

## 自定义模板

### 步骤1：创建模板目录

```
my_template/
├── conf.json
└── index.html.j2
```

### 步骤2：编写conf.json

```json
{
  "base_template": "lab",
  "mimetypes": {
    "text/html": true
  }
}
```

### 步骤3：编写模板文件

```jinja2
{%- extends 'lab/index.html.j2' -%}

{% block header %}
{{ super() }}
<style>
  /* 自定义CSS */
  .cell { margin: 20px 0; padding: 10px; border-left: 3px solid #007bff; }
</style>
{% endblock header %}
```

### 步骤4：使用自定义模板

```bash
# 通过--template指定模板目录
jupyter nbconvert --to html --template ./my_template notebook.ipynb

# 或通过extra_template_basedirs指定模板搜索路径
jupyter nbconvert --to html --template my_template --TemplateExporter.extra_template_basedirs="['./templates']" notebook.ipynb
```

Python API：

```python
from nbconvert.exporters import HTMLExporter

exporter = HTMLExporter(
    template_name="my_template",
    extra_template_basedirs=["./templates"]
)
output, resources = exporter.from_filename("notebook.ipynb")
```

## 相关概念

- [导出器体系](03-exporter-hierarchy.md)
- [过滤器系统](06-filters-system.md)
- [自定义模板](11-custom-template.md)
