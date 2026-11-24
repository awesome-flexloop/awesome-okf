---
type: Concept
title: "定制、子主题与主题开发：从换颜色到发布新主题"
description: "自定义 CSS 的稳定钩子、Jinja 模板覆盖、基于 sphinx_book_theme 的子主题打包、翻译扩展、测试与发布流程，以及常见定制边界"
tags: [sphinx, theme, customization, subtheme, css, jinja2, testing]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-custom-css
    resource: https://sphinx-book-theme.readthedocs.io/en/latest/components/custom-css.html
    title: Add your own CSS rules
  - id: sbt-subthemes
    resource: https://sphinx-book-theme.readthedocs.io/en/latest/contributing/subthemes.html
    title: Sub-themes
  - id: sbt-tests
    resource: https://sphinx-book-theme.readthedocs.io/en/latest/contributing/tests.html
    title: Testing
---

# 定制、子主题与主题开发：从换颜色到发布新主题

## 定制阶梯

按侵入性从低到高选择：

| 层级 | 手段 | 适合 | 风险 |
|------|------|------|------|
| 1 | `html_theme_options` | 开关、文案、布局深度 | 最低 |
| 2 | 自定义 CSS | 配色、字体、间距、局部样式 | 低 |
| 3 | 模板覆盖 | 改页面结构、增删区块 | 中 |
| 4 | 子主题 | 复用本书主题并形成品牌主题 | 中高 |
| 5 | Fork 主题 | 改核心逻辑 | 最高，需跟进上游 |

优先停在前两层。多数"想要不一样"的需求不需要动模板。

## 自定义 CSS

### 最小接入

```python
html_static_path = ["_static"]
html_css_files = ["custom.css"]
```

```css
/* _static/custom.css */
h1, h2 {
    color: #003b71;
}

/* 用主题的稳定钩子，而不是深层选择器 */
.btn-download-buttons {
    border-radius: 0;
}
```

### 稳定钩子

| 前缀/类 | 来源 | 稳定性 |
|---------|------|--------|
| `btn-<label>` | 页眉按钮的 `label` 字段 | 高，测试依赖 |
| `sbt-*` | 本书主题自有元素（如 `sbt-scroll-pixel-helper`、`sbt-sidebar-nav`） | 高 |
| `bd-*` | 父主题的 Bootstrap 布局类 | 中，随父主题升级变化 |
| `margin` / `full-width` / `margin-caption` | 内容语义类 | 高 |
| `cell` / `cell_input` / `cell_output` | MyST-NB 生成 | 中，随 myst-nb 变化 |

### CSS 变量

父主题大量使用 CSS 自定义属性。优先改变量，而不是覆盖具体规则：

```css
:root {
    --pst-color-primary: #0b5fff;
    --pst-color-link: #0b5fff;
    --pst-font-family-base: "Source Han Sans SC", system-ui, sans-serif;
}
```

变量名以父主题当前版本为准（本书主题锁定 `0.23.0`）。

### 避免的做法

- 不要用 `!important` 大军压制样式；先找对应变量。
- 不要依赖 `div > div > p` 这类结构选择器；HTML 随版本变化。
- 不要在自定义 CSS 里重写整页布局；布局用模板覆盖更可控。
- 不要隐藏焦点轮廓；可访问性会退化。

## 模板覆盖

Sphinx 的模板查找顺序由 `templates_path` 决定，用户目录优先于主题目录。

### 覆盖整个分区

```text
_templates/
└── sections/
    └── header.html
```

放同名文件即可替换页眉分区。这是文档中明确给出的"整体覆盖 header"方式。

### 覆盖小组件

```text
_templates/
└── components/
    └── page-toc.html
```

可用于改变右侧目录结构。覆盖前先读原模板，保留必要的 Jinja 变量与 class，否则 JS 与测试会失效。

### 追加而非替换

更安全的方式是用 `navbar_end` / `footer_end` 指向自己的小模板：

```python
templates_path = ["_templates"]
html_theme_options = {
    "navbar_end": ["my-github-star.html"],
}
```

```html
<!-- _templates/my-github-star.html -->
<a class="btn btn-sm" href="https://github.com/org/repo" target="_blank" rel="noopener">
  <i class="fab fa-github"></i>
</a>
```

## 子主题

当你要把"本书主题 + 品牌样式 + 少量模板改动"打包复用，做一个子主题。

### 目录

```text
my-book-theme/
├── pyproject.toml
└── src/my_book_theme/
    ├── __init__.py
    └── theme/my_book_theme/
        ├── theme.conf
        └── static/
            └── my-book-theme.css
```

### theme.conf

```ini
[theme]
inherit = sphinx_book_theme
stylesheet = my-book-theme.css

[options]
# 可在这里声明子主题自己的默认值
brand_color = #0b5fff
```

### setup 与 entry point

```python
# src/my_book_theme/__init__.py
from pathlib import Path

__version__ = "0.1.0"


def get_html_theme_path():
    return Path(__file__).parent / "theme" / "my_book_theme"


def setup(app):
    app.add_html_theme("my_book_theme", str(get_html_theme_path()))
    return {"parallel_read_safe": True, "parallel_write_safe": True}
```

```toml
[project.entry-points]
"sphinx.html_themes" = { my_book_theme = "my_book_theme" }
```

用户配置：

```python
html_theme = "my_book_theme"
```

### 子主题的 CSS 陷阱

本书主题的 `hash_html_assets` 只在 `html_theme == "sphinx_book_theme"` 时追加 `sphinx-book-theme.css`：

```python
if app.config.html_theme == "sphinx_book_theme":
    assets.append("styles/sphinx-book-theme.css")
```

因此子主题必须：

- 在 `theme.conf` 里用 `stylesheet` 声明自己的 CSS（建议放在 `static/styles/`）；
- 在自己 CSS 的首行写 `@import "sphinx-book-theme.css";` 引入父主题样式，再写覆盖规则；
- 不要假设父主题 CSS 会被自动链接；父主题的静态文件会复制到输出，但 `<link>` 只来自 `stylesheet` 声明。

官方 sub-themes 指南推荐“先 import 再覆盖”，并把子主题 CSS 放在 `STATIC_PATH/styles/`，与父主题 CSS 在输出中同属 `_static/styles/`。

若需要缓存失效，可复用 `hash_assets_for_files`（其中 `get_html_theme_path()` 指子主题自己的路径函数）：

```python
from sphinx_book_theme import hash_assets_for_files

def hash_my_assets(app, pagename, templatename, context, doctree):
    hash_assets_for_files(
        ["styles/my-book-theme.css"],
        get_html_theme_path() / "static",
        context,
        app,
    )

def setup(app):
    app.add_html_theme("my_book_theme", str(get_html_theme_path()))
    app.connect("html-page-context", hash_my_assets)
```

### 子主题的模板继承

子主题可以继续 `{% extends "sphinx_book_theme/layout.html" %}`，只覆盖需要的 block。继承链变成：

```text
pydata_sphinx_theme/layout.html
  ← sphinx_book_theme/layout.html
    ← my_book_theme/layout.html
```

## 扩展主题配置

如果子主题需要新的配置项，用 Sphinx 配置而不是硬编码：

```python
def setup(app):
    app.add_html_theme("my_book_theme", str(get_html_theme_path()))
    app.add_config_value("my_brand_name", "My Book", "html")
```

模板中通过 `{{ my_brand_name }}` 读取。注意 `add_config_value` 的重建类型：`"html"` 表示改变后需要重建 HTML。

## 翻译

主题文案走 message catalog：

- 本书主题：catalog 名 `booktheme`，源文案在 `assets/translations/`。
- 子主题：注册自己的 catalog，避免与父主题冲突。

```python
def setup(app):
    app.add_message_catalog("mytheme", str(Path(__file__).parent / "locales"))
```

模板中用 `{{ translate("Download this page") }}`，不要硬编码中文或英文。

## 测试

本书主题的测试栈：

```bash
pip install -e ".[test]"
pytest
```

| 工具 | 用途 |
|------|------|
| `pytest` | 驱动最小站点构建 |
| `beautifulsoup4` | 解析 HTML、断言按钮/导航结构 |
| `pytest-regressions` | 对比 `tests/test_build/*.html` 快照 |
| `tests/sites/` | base、notitle、parallel-build、titles 等最小站点 |

修改模板后的正确流程：

1. 跑 `pytest`，看哪些快照失败。
2. 打开失败 diff，确认变化是**预期内**的。
3. 只对确认过的文件执行 `--force-regen`。
4. 再跑一次全量测试。

不要因为"快照太多"就整体重生成；那会把真正的回归一起吞掉。

## 构建与发布

| 步骤 | 命令/机制 |
|------|----------|
| 编译资产 | `stb compile` 或 `tox -e compile` |
| 运行测试 | `pytest` |
| 构建分发包 | `python -m build`（后端为 sphinx-theme-builder） |
| 版本号 | 来自 `src/.../__init__.py` 的 `__version__`（动态版本） |
| 前端工具链 | Node `20.9.0`，webpack |
| CI | GitHub Actions：tests、publish、lighthouse |

发布前检查：

- `__version__` 是否更新；
- CHANGELOG 是否记录；
- 编译产物是否最新（`static/` 不入库，但发布包需要）；
- 测试快照是否与模板一致；
- 父主题版本锁定是否仍合理。

## 调试技巧

### 看实际模板上下文

```python
def setup(app):
    @app.connect("html-page-context")
    def _dump(app, pagename, templatename, context, doctree):
        if pagename == "index":
            print(sorted(context.keys()))
```

### 看主题选项

```python
from pydata_sphinx_theme.utils import get_theme_options_dict
print(get_theme_options_dict(app))
```

### 定位某个 class 的来源

1. 在 `src/sphinx_book_theme/theme/` 搜模板；
2. 在 `src/sphinx_book_theme/assets/styles/` 搜 SCSS；
3. 找不到就去父主题源码搜（`ARCHITECTURE.md` 的建议）；
4. 仍找不到，检查是否是 MyST-NB 或第三方扩展生成。

### 清理缓存

```bash
sphinx-build -E -a -b html docs _build/html
```

## 定制边界

| 想做 | 推荐做法 | 不推荐 |
|------|---------|--------|
| 换主色 | CSS 变量 | Fork 主题 |
| 换字体 | CSS 变量 + `html_css_files` | 改 SCSS 源文件 |
| 加页眉按钮 | `navbar_end` + 小模板 | 覆盖整个 header |
| 改侧栏顺序 | `html_sidebars` | 改 `sbt-sidebar-nav.html` |
| 改页脚 | `footer_content_items` + 模板 | 改 `sections/footer-content.html` |
| 品牌化整套主题 | 子主题 | 在每个项目复制 CSS |
| 改核心按钮逻辑 | Fork + 跟进上游 | 在子主题 monkey patch |

## 相关概念

- [主题骨架与构建链](02-theme-architecture.md)
- [页面分区与导航](03-layout-and-navigation.md)
- [子主题与模板覆盖](../examples/05-subtheme-and-template-override.md)
