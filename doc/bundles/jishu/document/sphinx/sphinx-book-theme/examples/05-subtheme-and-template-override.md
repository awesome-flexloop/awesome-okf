---
type: Example
title: "子主题与模板覆盖"
description: "从零创建一个继承 sphinx_book_theme 的品牌子主题：包结构、entry point、theme.conf、模板覆盖、CSS 叠加、安装与验收"
tags: [sphinx, theme, example, subtheme, packaging, jinja2]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-subthemes
    resource: https://sphinx-book-theme.readthedocs.io/en/latest/contributing/subthemes.html
    title: Sub-themes
  - id: sbt-theme-conf
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme/src/sphinx_book_theme/theme/sphinx_book_theme/theme.conf
    title: theme.conf
---

# 子主题与模板覆盖

目标：做一个 `my_book_theme`，它继承 `sphinx_book_theme`，只改品牌色、页眉按钮和页脚，不复制整个主题。

## 1. 包结构

```text
my-book-theme/
├── pyproject.toml
└── src/
    └── my_book_theme/
        ├── __init__.py
        └── theme/
            └── my_book_theme/
                ├── theme.conf
                ├── layout.html
                └── static/
                    └── styles/
                        └── my-book-theme.css
```

## 2. pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-book-theme"
version = "0.1.0"
description = "A branded sub-theme of sphinx-book-theme"
requires-python = ">=3.11"
dependencies = [
  "sphinx>=8.2",
  "sphinx-book-theme>=1.4",
]

[project.entry-points]
"sphinx.html_themes" = { my_book_theme = "my_book_theme" }

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
my_book_theme = [
  "theme/my_book_theme/*.conf",
  "theme/my_book_theme/*.html",
  "theme/my_book_theme/static/styles/*",
]
```

## 3. __init__.py

```python
"""Branded sub-theme of sphinx-book-theme."""

from pathlib import Path

__version__ = "0.1.0"


def get_html_theme_path() -> Path:
    return Path(__file__).parent / "theme" / "my_book_theme"


def setup(app):
    app.add_html_theme("my_book_theme", str(get_html_theme_path()))
    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
```

## 4. theme.conf

```ini
[theme]
inherit = sphinx_book_theme
stylesheet = styles/my-book-theme.css

[options]
announcement = Welcome to My Book.
toc_title = On this page
show_toc_level = 2
```

要点：

- `inherit = sphinx_book_theme` 继承模板、选项与静态目录。
- `stylesheet` 只声明子主题自己的 CSS；子主题 CSS 在首行 `@import "sphinx-book-theme.css";` 引入父主题样式。官方 sub-themes 指南推荐这种“先 import 再覆盖”的方式。
- 子主题的 `static/styles/` 与父主题的 `static/styles/` 在输出中同属 `_static/styles/`，因此相对 `@import` 能解析。
- 子主题可以覆盖任意 `theme.conf` 默认值。

## 5. 模板覆盖：页眉

`theme/my_book_theme/layout.html`：

```jinja
{% extends "sphinx_book_theme/layout.html" %}

{# 在页眉右侧加一个品牌链接 #}
{% block docs_navbar %}
{{ super() }}
{% if theme_navbar_end %}
<div class="my-brand-strip">
  <a href="https://example.org">Example Org</a>
</div>
{% endif %}
{% endblock docs_navbar %}
```

更常见的做法是不改 `layout.html`，而是用 `navbar_end` 指向一个小模板：

```ini
[options]
navbar_end = my-brand-link.html
```

```html
<!-- theme/my_book_theme/my-brand-link.html -->
<a class="btn btn-sm my-brand-link" href="https://example.org">
  Example Org
</a>
```

> 模板文件放在主题目录根部即可被 Sphinx 找到；也可以放在 `components/` 下并在配置中写相对路径。

## 6. 模板覆盖：页脚

```ini
[options]
footer_content_items = my-footer.html
```

```html
<!-- theme/my_book_theme/my-footer.html -->
<div class="my-footer">
  <span>© 2026 Example Org</span>
  <span>Built with Sphinx Book Theme</span>
</div>
```

## 7. 品牌 CSS

`theme/my_book_theme/static/styles/my-book-theme.css`：

```css
@import "sphinx-book-theme.css";

:root {
    --pst-color-primary: #0b5fff;
    --pst-color-link: #0b5fff;
}

.my-brand-strip {
    padding: 0.25rem 1rem;
    background: #0b5fff;
    color: #fff;
}

.my-brand-strip a {
    color: #fff;
    text-decoration: none;
}

.my-footer {
    display: flex;
    gap: 1rem;
    justify-content: space-between;
    font-size: 0.85rem;
    color: #4a5568;
}
```

## 8. 安装与启用

```bash
pip install -e /path/to/my-book-theme
```

```python
# 项目的 conf.py
html_theme = "my_book_theme"
```

验证 entry point：

```bash
python -c "from importlib.metadata import entry_points; print([e for e in entry_points(group='sphinx.html_themes')])"
```

## 9. 验收清单

| 检查 | 预期 |
|------|------|
| `html_theme = "my_book_theme"` | 构建无 `ThemeError` |
| 页面样式 | 本书主题布局仍在，品牌色生效 |
| 页眉 | 出现品牌链接 |
| 页脚 | 出现自定义页脚 |
| 下载/全屏按钮 | 仍可用（继承自本书主题） |
| 移动端 | 品牌链接不遮挡正文 |
| 构建日志 | 无缺失静态文件 warning |

## 10. 资产哈希的注意点

本书主题的 `hash_html_assets` 只在 `html_theme == "sphinx_book_theme"` 时给 `sphinx-book-theme.css` 追加 digest。使用子主题时：

- 父主题 CSS 仍会随主题静态目录复制并在输出 `_static/styles/` 中可用；
- 但不会自动追加缓存哈希；
- 需要缓存失效时，可复用本书主题的 `hash_assets_for_files(assets, theme_static, context, app)`，在 `html-page-context` 中给子主题 CSS 追加 digest；
- 或在自己的构建流程里给 CSS 文件名加版本，或配置服务器缓存策略。

## 11. 版本与升级策略

| 策略 | 做法 | 适用 |
|------|------|------|
| 锁定 | `sphinx-book-theme==1.4.0` | 稳定交付 |
| 小版本浮动 | `sphinx-book-theme~=1.4` | 接收缺陷修复 |
| 跟随主线 | `sphinx-book-theme>=1.4` | 愿意处理模板变化 |

升级后至少检查：

- `theme.conf` 选项是否被重命名/废弃；
- 覆盖的模板 block 是否仍存在；
- 页眉按钮的 class/label 是否变化；
- 回归测试快照是否大面积变动。

## 12. 什么时候不该做子主题

- 只改颜色：用项目级 `custom.css` 就够。
- 只加一个按钮：用 `navbar_end` + 小模板。
- 只想改文案：用 `html_theme_options`。
- 需要改核心按钮逻辑：Fork 本书主题，而不是在子主题里 monkey patch。

子主题的价值在**复用**：多个项目共享同一套品牌与模板时，才值得维护一个包。

## 相关概念

- [定制、子主题与主题开发](../concepts/08-customization-and-development.md)
- [主题骨架与构建链](../concepts/02-theme-architecture.md)
- [页面分区与导航](../concepts/03-layout-and-navigation.md)
