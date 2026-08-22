---
type: "concept"
title: "过滤器系统"
description: "nbconvert的Jinja2过滤器体系：40+内置过滤器分类详解、自定义过滤器注册方法"
tags: [filters, jinja2, markdown, highlight, ansi, custom-filter]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: filters
    resource: ../references/filters-source.md
    title: "过滤器模块源码解析"
  - id: template-exporter
    resource: ../references/template-exporter-source.md
    title: "TemplateExporter源码解析"
---

# 过滤器系统

过滤器（Filter）是nbconvert模板系统中的核心数据处理单元。它们是注册在Jinja2 Environment中的Python函数/可调用对象，模板中通过`{{ variable | filter_name }}`语法调用，用于将原始Notebook数据转换为目标格式所需的表示形式。

## 过滤器注册机制

### 默认过滤器

TemplateExporter的模块级`default_filters`字典注册了40+个内置过滤器，在`_create_environment()`中通过`_register_filter()`方法逐一注册到Jinja2 Environment中。

### 用户自定义过滤器

通过配置添加或覆盖过滤器：

```python
from traitlets.config import Config
from nbconvert.exporters import HTMLExporter

def shout(text):
    """将文本转为大写"""
    return str(text).upper()

c = Config()
c.TemplateExporter.filters = {"shout": shout}
exporter = HTMLExporter(config=c)
```

模板中即可使用：`{{ cell.source | shout }}`

### 过滤器注册支持的类型

`_register_filter()`方法支持四种过滤器形式：
1. **字符串**：点分模块路径，通过`import_item`导入后递归注册
2. **函数**：直接添加到`environment.filters`
3. **HasTraits类**：实例化（传入`parent=self`）后注册
4. **普通类**：实例化后注册（类的实例必须是可调用的，即实现`__call__`）

## 内置过滤器分类

### Markdown转换过滤器

负责将Markdown cell的source转换为目标格式。

| 过滤器 | 签名 | 功能 | 后端 |
|--------|------|------|------|
| `markdown2html` | `(source) → str` | Markdown→HTML | mistune（默认）/pandoc |
| `markdown2latex` | `(source) → str` | Markdown→LaTeX | pandoc |
| `markdown2rst` | `(source) → str` | Markdown→RST | pandoc |
| `markdown2asciidoc` | `(source) → str` | Markdown→AsciiDoc | pandoc |
| `markdown2html_mistune` | `(source) → str` | Markdown→HTML | mistune（直接调用） |
| `markdown2html_pandoc` | `(source) → str` | Markdown→HTML | pandoc（直接调用） |

**注意**：`markdown2html`默认使用mistune（纯Python Markdown解析器），无需pandoc依赖；LaTeX/RST/AsciiDoc转换需要pandoc。

### 代码高亮过滤器

基于pygments实现语法高亮。

| 过滤器 | 功能 |
|--------|------|
| `Highlight2HTML` | 将代码高亮为HTML（带CSS类的`<span>`标签） |
| `Highlight2Latex` | 将代码高亮为LaTeX（使用fancyvrb/color包） |

使用方式（类过滤器，实例可调用）：
```jinja2
{{ cell.source | highlight2html(metadata=nb.metadata) }}
```

支持从cell/Notebook metadata中获取语言信息（`language_info.name`）。

### ANSI转义序列过滤器

处理终端输出中的ANSI颜色代码。

| 过滤器 | 功能 |
|--------|------|
| `ansi2html` | 将ANSI颜色代码转换为HTML `<span style="color:...">` 标签 |
| `ansi2latex` | 将ANSI颜色代码转换为LaTeX `\textcolor{}` 命令 |
| `strip_ansi` | 剥离所有ANSI转义序列，返回纯文本 |

典型用法（处理stream输出）：
```jinja2
<pre>{{ output.text | ansi2html }}</pre>
```

### HTML处理过滤器

| 过滤器 | 功能 |
|--------|------|
| `clean_html` | 基于bleach清洗HTML，移除危险标签/属性（XSS防护） |
| `html2text` | 将HTML转换为纯文本 |
| `escape_html` | HTML转义（`html.escape`） |
| `escape_html_keep_quotes` | HTML转义但保留引号 |
| `escape_html_script` | HTML转义（斜杠转义，用于`<script>`标签内） |

### LaTeX处理过滤器

| 过滤器 | 功能 |
|--------|------|
| `escape_latex` | 转义LaTeX特殊字符（`_`, `^`, `\`, `{`, `}`, `&`, `%`, `$`, `#`等） |
| `citation2latex` | 将HTML引用标签转换为LaTeX引用命令 |
| `strip_dollars` | 移除LaTeX数学模式的`$`分隔符 |

### 文本处理过滤器

| 过滤器 | 签名 | 功能 |
|--------|------|------|
| `indent` | `(text, n=4, predicate=None)` | 缩进文本n个空格 |
| `get_lines` | `(text, start=0, end=None)` | 获取文本的行范围 |
| `wrap_text` | `(text, width=80)` | 按宽度自动换行 |
| `comment_lines` | `(text, prefix='# ')` | 给每行添加注释前缀 |
| `strip_trailing_newline` | `(text)` | 移除尾部换行符 |
| `add_prompts` | `(text, prompt='In []:', cont='...')` | 添加输入/输出提示符 |
| `add_anchor` | `(text)` | 添加HTML锚点链接 |
| `prevent_list_blocks` | `(text)` | 防止Markdown列表块嵌套问题 |
| `ascii_only` | `(s)` | 移除非ASCII字符 |
| `ipython2python` | `(text)` | 将IPython语法转为纯Python（注释掉magic命令） |
| `posix_path` | `(path)` | 转换为POSIX路径格式（反斜杠转正斜杠） |
| `path2url` | `(path)` | 文件路径转URL路径 |
| `strip_files_prefix` | `(text)` | 移除`files/`前缀 |
| `text_base64` | `(text)` | 文本base64编码 |
| `json_dumps` | `json.dumps` | JSON序列化（标准库函数） |

### 数据类型与元数据过滤器

| 过滤器 | 功能 |
|--------|------|
| `DataTypeFilter` | 按`display_data_priority`顺序选择display_data输出的第一个可用MIME类型 |
| `get_metadata` | 从output.metadata中安全提取指定key的值（返回default或None） |
| `convert_pandoc` | 调用pandoc进行通用格式转换 |
| `ConvertExplicitlyRelativePaths` | 转换pandoc输出中的相对路径 |

## 过滤器使用模式

### 管道链式调用

```jinja2
{{ cell.source | strip_ansi | indent(4) | highlight2html(metadata=nb.metadata) }}
```

### 条件使用

```jinja2
{% if cell.source %}
  {{ cell.source | markdown2html | clean_html }}
{% endif %}
```

### DataTypeFilter的工作原理

`DataTypeFilter`是处理display_data/execute_result输出的关键过滤器：

1. 接收output对象（包含多个MIME类型数据）
2. 按`display_data_priority`列表顺序遍历MIME类型
3. 返回第一个在output.data中存在的MIME类型的数据
4. 对返回数据应用相应的渲染（HTML直接safe，图片处理为`<img>`标签等）

默认优先级顺序：
```python
["text/html", "application/pdf", "text/latex", "image/svg+xml",
 "image/png", "image/jpeg", "text/markdown", "text/plain"]
```

## 自定义过滤器

### 函数过滤器

```python
def reverse_text(text):
    """反转文本"""
    return str(text)[::-1]

from nbconvert.exporters import HTMLExporter
exporter = HTMLExporter()
exporter.register_filter("reverse", reverse_text)
```

### 类过滤器（可配置）

```python
from traitlets import Int
from nbconvert.utils.base import NbConvertBase

class TruncateFilter(NbConvertBase):
    """可配置的截断过滤器"""
    max_length = Int(100).tag(config=True)
    
    def __call__(self, text):
        text = str(text)
        if len(text) > self.max_length:
            return text[:self.max_length] + "..."
        return text

from traitlets.config import Config
c = Config()
c.TruncateFilter.max_length = 200
exporter = HTMLExporter(config=c)
exporter.register_filter("truncate", TruncateFilter)
```

### 在conf.json中声明过滤器

通过模板的conf.json也可以注册预处理器，但过滤器目前主要通过Python API或配置注册。

## 相关概念

- [模板系统](05-template-system.md)
- [导出器体系](03-exporter-hierarchy.md)
