---
type: "concept"
title: "主题系统"
description: "Theme主题加载与继承机制、theme.conf/theme.toml配置、内置13个主题、alabaster默认主题、HTMLTranslator定制、静态资源继承"
tags: [extension, theme, html, styling, alabaster]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: theming-py
    resource: sphinx/theming.py
    title: "Sphinx theme loading"
---

# 主题系统

Sphinx的主题系统控制HTML输出的视觉呈现——布局、配色、字体、导航样式等。主题通过Jinja2模板和CSS样式表定义，支持继承机制，用户可以基于已有主题进行定制。

## 主题目录结构

一个Sphinx主题是一个目录（或Python包），包含以下文件 [F-055]：

```
my_theme/
├── theme.conf          # 主题配置（旧格式）
├── theme.toml          # 主题配置（新格式，Sphinx 7+推荐）
├── my_theme/           # 模板和静态文件目录（必须与主题同名）
│   ├── layout.html     # Jinja2模板
│   ├── page.html       # 页面模板
│   ├── static/         # 静态资源（CSS/JS/图片）
│   │   ├── my_theme.css
│   │   └── my_theme.js
│   └── ...             # 其他模板文件
└── __init__.py         # 作为Python包时需要
```

### theme.toml 配置

新格式使用TOML：

```toml
[theme]
name = "my_theme"
inherit = "basic"          # 继承的父主题
stylesheet = "my_theme.css"  # 主样式表（相对于static/）
pygments_style = "monokai"   # 默认Pygments样式
sidebars = {
  "**" = ["localtoc.html", "sourcelink.html", "searchbox.html"]
}

[options]
# 主题选项（通过html_theme_options配置）
nosidebar = false
body_max_width = "800px"
navigation_with_keys = true
```

### theme.conf 配置（旧格式）

```ini
[theme]
inherit = basic
stylesheet = my_theme.css
pygments_style = sphinx

[options]
nosidebar = false
body_max_width = 800px
```

## 主题继承

主题支持单继承，通过 `inherit` 指定父主题名 [F-056]：

1. 加载主题时，Sphinx递归加载父主题链（如 `furo → basic`）
2. 模板查找从子主题开始，沿继承链向上查找
3. 子主题的同名模板覆盖父主题模板
4. 静态文件同样沿继承链合并，子主题文件优先
5. 主题选项沿继承链合并（子主题默认值覆盖父主题）

所有主题最终继承自内置的 `basic` 主题，它定义了基础HTML结构和必要的CSS/JS。

## 内置主题

Sphinx 内置 13 个主题 [F-057]：

| 主题名 | 继承 | 特点 | 适合场景 |
|--------|------|------|---------|
| **alabaster** | basic | 默认主题，简洁优雅，侧边栏布局 | 默认推荐 |
| **basic** | - | 基础主题，无特殊样式 | 自定义主题的基类 |
| **default** | basic | Sphinx经典样式（旧默认主题） | 传统文档 |
| **classic** | default | 左侧边栏+右侧内容的传统布局 | 老式Python文档 |
| **sphinxdoc** | basic | 仿sphinx-doc.org样式 | 官方风格文档 |
| **scrolls** | basic | 水平滚动式导航 | 交互式文档 |
| **agogo** | basic | 两栏布局，固定侧边栏 | 教程类文档 |
| **nature** | basic | 绿色自然风格 | 快速文档 |
| **pyramid** | basic | 仿Pyramid web框架文档风格 | 框架文档 |
| **haiku** | basic | 无侧边栏，居中单栏 | 简洁文档/单页 |
| **traditional** | basic | 传统LaTeX文档风格 | 学术/技术报告 |
| **nonav** | basic | 无导航栏，纯内容 | 嵌入式文档 |
| **bizstyle** | basic | 商务风格，橙色顶部栏 | 企业文档 |
| **epub** | basic | EPUB电子书专用 | EPUB输出 |

## 第三方流行主题

| 主题 | 安装 | 特点 |
|------|------|------|
| **Furo** | `pip install furo` | 现代化三栏布局，暗色模式支持，响应式设计 |
| **Read the Docs** | `pip install sphinx-rtd-theme` | 仿Read the Docs风格，广泛使用 |
| **PyData Sphinx Theme** | `pip install pydata-sphinx-theme` | Bootstrap风格，适合数据科学项目 |
| **sphinx-book-theme** | `pip install sphinx-book-theme` | Jupyter Book风格 |
| **Material** | `pip install sphinx-immaterial` | Google Material Design风格 |
| **Piccolo** | `pip install piccolo-theme` | 简洁快速，暗色主题 |

## 使用主题

### 基本配置

```python
# conf.py
html_theme = 'furo'
html_theme_path = []  # 自定义主题搜索路径

html_theme_options = {
    'navigation_depth': 3,
    'collapse_navigation': False,
    'announcement': 'This is beta documentation',
}

html_static_path = ['_static']
html_css_files = ['custom.css']  # 额外自定义CSS
```

### 自定义CSS覆盖

在 `_static/custom.css` 中覆盖主题样式：

```css
/* custom.css */
:root {
    --color-brand-primary: #2c3e50;
    --color-brand-content: #3498db;
}
```

### 模板覆盖

在 `templates_path`（如 `_templates/`）中创建与主题同名的模板文件即可覆盖：

```
_templates/
└── layout.html    # 覆盖主题的layout.html
```

使用Jinja2的 `{% extends %}` 扩展而非完全替换：

```jinja2
{# _templates/layout.html #}
{% extends "!layout.html" %}

{% block extrahead %}
    {{ super() }}
    <link rel="icon" href="{{ pathto('_static/favicon.ico', 1) }}">
{% endblock %}

{% block footer %}
    {{ super() }}
    <script src="{{ pathto('_static/custom.js', 1) }}"></script>
{% endblock %}
```

注意 `!` 前缀表示"从父模板继承"而非当前目录。

## HTMLTranslator 定制

主题不仅可以通过CSS定制外观，还可以通过自定义Translator类来修改HTML结构 [F-058]：

```python
class MyThemeTranslator(HTML5Translator):
    def visit_paragraph(self, node):
        # 自定义段落渲染
        self.body.append('<p class="custom-paragraph">')

    def depart_paragraph(self, node):
        self.body.append('</p>')
```

主题可以通过 `set_translator()` 方法注册自定义Translator：

```python
def setup(app):
    app.set_translator('html', MyThemeTranslator, override=True)
    return {'version': '1.0', 'parallel_read_safe': True}
```

## 主题侧边栏配置

`html_sidebars` 配置项控制每个页面显示哪些侧边栏组件：

```python
html_sidebars = {
    '**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html'],
    'index': ['localtoc.html', 'searchbox.html'],  # 首页不同
}
```

内置侧边栏模板：

| 模板 | 内容 |
|------|------|
| `globaltoc.html` | 全局目录树 |
| `localtoc.html` | 当前页面的本地目录 |
| `relations.html` | 上一页/下一页导航 |
| `sourcelink.html` | 源文件链接 |
| `searchbox.html` | 搜索框 |
| `customsidebar.html` | 用户自定义 |

## 设计洞察

1. **Jinja2继承链**：主题系统充分利用Jinja2的模板继承机制，通过配置文件声明inherit关系实现主题层级。子主题只需要覆盖需要修改的模板块（block），而不是复制整个模板。

2. **静态文件合并策略**：静态文件沿继承链从子主题到父主题依次搜索，最先找到的文件生效。这允许子主题精确覆盖特定CSS/JS文件而无需复制全部资源。

3. **主题选项机制**：通过theme.toml/conf中的`[options]`定义可配置项，用户通过`html_theme_options`设置值，模板中通过`theme_<option_name>`访问。这种模式使得主题用户不需要编写代码就能定制外观。

4. **Translator级定制**：对于更深层的定制（修改HTML标签结构），主题可以通过自定义Translator类来实现，这比CSS更强大但也更复杂。

5. **basic作为最小基础**：basic主题提供了最小可用的HTML结构（doctype、head、body、基本CSS类），所有其他主题都基于它构建，确保了即使在简单主题下文档也能正常显示。

## 相关概念

- [HTML 构建器详解](11-html-builder.md)
- [扩展开发详解](15-extension-development.md)
- [Sphinx 简介](00-introduction.md)
