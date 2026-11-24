---
type: Concept
title: 内部实现与扩展点
description: Translator mixin、链接缩短 transform、canonical URL 修正、i18n 与自定义扩展的正确接入方式
tags: [sphinx, theme, pydata, internals, translator, transform, i18n]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:20:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
---

# 内部实现与扩展点

本文面向需要写扩展、改模板或排查构建异常的读者。所有结论都对应 `src/pydata_sphinx_theme/` 下的模块。

## 1. HTML Translator mixin

`translator.py` 不替换 Sphinx 的 translator，而是动态构造一个“mixin + 原 translator”的子类：

```python
translator = types.new_class(
    "BootstrapHTML5Translator",
    (BootstrapHTML5TranslatorMixin, default_translator_class),
    {},
)
app.set_translator(app.builder.name, translator, override=True)
```

mixin 做三件事：

1. `__init__` 中设 `self.settings.table_style = "table"`，去掉 docutils 默认的 `docutils`/`align-default` 类。
2. `starttag` 为 `role="heading"` 的标签补 `aria-level="2"`。
3. `visit_table` / `depart_table` 把表格包进 `<div class="pst-scrollable-table-container">`，`autosummary` 表格额外加 `autosummary` 类。

扩展点：

- 若你注册了自己的 translator，主题会把 mixin 叠加到**每一个**已注册 translator 上；因此不要在 `setup_translators` 之前假设 translator 还是原类。
- 非 HTML builder（gettext、linkcheck 等）不做任何处理。

## 2. 链接缩短 transform

`short_link.ShortenLinkTransform` 是 `SphinxPostTransform`：

- `default_priority = 400`
- `formats = ("html",)`
- 只处理“显示文本与 `refuri` 完全相同”的链接，用户自定义过文案的链接不动。

GitHub 规则：

| 原 URL | 显示 |
|---|---|
| `https://github.com` | `github` |
| `https://github.com/org` | `org` |
| `https://github.com/org/repo` | `org/repo` |
| `https://github.com/org/repo/issues/12` | `org/repo#12` |
| `https://github.com/org/repo/pull/12` | `org/repo#12` |
| `https://github.com/orgs/org/projects/3` | `org/projects#3` |

GitLab 规则类似，issue 用 `#`，merge request 用 `!`；其他路径保留 `group/subgroup/repo`。

开关：

```python
html_theme_options = {"shorten_urls": False}
```

注册时机是 `builder-inited`，且仅当 builder 有 `theme` 属性。

## 3. canonical URL 修正

`_fix_canonical_url` 处理 Sphinx 的已知问题：`dirhtml` builder 生成的 canonical URL 以 `.html` 结尾。

逻辑：

```python
if (not html_baseurl or not isinstance(builder, DirectoryHTMLBuilder)
        or not pageurl or not pageurl.endswith(".html")):
    return
pageurl = html_baseurl + builder.get_target_uri(pagename)
```

扩展含义：若你自定义 `pageurl`，要放在该回调之后，或自行处理 `dirhtml` 的目录式 URI。

## 4. i18n

主题自带 `locale/`，包含 10 种语言：`ca`、`cs`、`de`、`en`、`es`、`fr`、`it`、`ja`、`ru`、`zh`。

`setup()` 中：

```python
app.add_message_catalog("sphinx", here / "locale")
```

因此模板里的 `_("Back to top")`、`_("Site navigation")` 等会随文档 `language` 切换。

两类字符串要区分：

1. **内置字符串**：写死在模板里，由主题的 `.po` 翻译；新增语言需向主题提交翻译。
2. **可配置字符串**：`search_bar_text`、`icon_links_label`、`icon_links[].name`、`external_links[].name` 等。要让它们可翻译，需在自己的文档项目中建立 message catalog：

```python
# conf.py
import os.path
from sphinx.locale import get_translation

catalog = "messages"
_ = get_translation(catalog)

html_theme_options = {
    "search_bar_text": _("Search the docs..."),
    "icon_links": [{"name": _("GitHub"), "url": "...", "icon": "fa-brands fa-github"}],
}

def setup(app):
    app.add_message_catalog(catalog, os.path.join(os.path.dirname(__file__), "locale"))
```

然后 `pybabel extract/init/compile`。

## 5. 自定义扩展的正确接入点

| 需求 | 推荐钩子 | 注意 |
|---|---|---|
| 修改主题选项默认值 | `builder-inited`（晚于主题的 `update_config`） | 改 `app.builder.theme_options` |
| 给每页注入变量 | `html-page-context` | 不要改 `app.config` |
| 只给某些页加 CSS/JS | `html-page-context` + `app.add_css_file` | 资源只作用于当前页 |
| 修改最终 HTML 树 | `SphinxPostTransform` | 指定 `formats = ("html",)` |
| 构建结束后处理文件 | `build-finished` | 检查 `exception is None` |
| 新增模板组件 | 放入 `templates_path`，在区段配置中引用 | 空渲染会被移除 |

### 5.1 一个最小扩展

```python
# myext.py
def setup(app):
    app.add_config_value("my_banner_text", "", "html")

    def inject(app, pagename, templatename, context, doctree):
        context["my_banner_text"] = app.config.my_banner_text

    app.connect("html-page-context", inject)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
```

```python
extensions = ["myext"]
my_banner_text = "Internal docs"
```

`_templates/my-banner.html`：

```html+jinja
{% if my_banner_text %}
<div class="my-banner">{{ my_banner_text }}</div>
{% endif %}
```

```python
html_theme_options = {"announcement": "my-banner"}
```

## 6. 模板上下文中的常用变量

| 变量 | 来源 | 用途 |
|---|---|---|
| `theme_*` | `theme.conf` + `html_theme_options` | 所有主题配置 |
| `theme_logo.image_relative` | `logo.setup_logo_path` | light/dark logo 路径 |
| `secondary_sidebar_items` | `utils.set_secondary_sidebar_items` | 右侧栏模板列表 |
| `generate_header_nav_html()` | `toctree.add_toctree_functions` | 顶部导航 HTML |
| `generate_toctree_html()` | 同上 | 侧栏树 HTML |
| `generate_toc_html()` | 同上 | 页内 TOC HTML |
| `navbar_align_class()` | 同上 | 对齐类 |
| `get_edit_provider_and_url()` | `edit_this_page` | 编辑链接 |
| `theme_version` | `update_and_remove_templates` | 主题版本 |
| `DOCUMENTATION_OPTIONS` | 主题注入 | 前端读取的配置 |

## 7. 不要做的事

1. 不要 `from pydata_sphinx_theme import ...` 依赖内部函数作为稳定 API；优先复制必要逻辑或通过模板覆盖。
2. 不要在 `build-finished` 之外重写 `pygments.css`，否则会被主题覆盖。
3. 不要覆盖 `layout.html` 的 `<html>` 标签而丢掉 `data-content_root`，否则即时搜索链接会错。
4. 不要把自定义组件放在 `_static`，它不会进入 Jinja 搜索路径。
5. 不要在 `setup()` 里假设 `app.builder` 已存在；`builder-inited` 之前它可能为 `None`。

## 相关概念

- [架构总览](02-architecture-overview.md)
- [布局与模板区段](03-layout-and-sections.md)
- [可访问性、性能与 FAQ](10-accessibility-performance-faq.md)
- [自定义组件示例](../examples/05-custom-components.md)
- [Sphinx 扩展开发](../../sphinx/concepts/15-extension-development.md)
