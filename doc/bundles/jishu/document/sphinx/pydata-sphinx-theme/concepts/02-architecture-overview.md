---
type: Concept
title: 架构总览
description: 包结构、setup() 事件管线、模板继承链与前端构建管线
tags: [sphinx, theme, pydata, architecture, events]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T02:55:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
---

# 架构总览

## 1. 包结构

```text
src/pydata_sphinx_theme/
├── __init__.py            # setup()、update_config()、模板过滤、canonical URL 修正
├── utils.py               # 主题选项读取、模板空渲染过滤、次级侧栏选择
├── toctree.py             # 顶部导航、侧栏 toctree、页内 TOC 的 HTML 生成
├── edit_this_page.py      # "Edit this page" URL 构造
├── logo.py                # light/dark logo 路径计算与复制
├── pygments.py            # 双主题 pygments.css 生成
├── short_link.py          # GitHub/GitLab 链接缩短后处理
├── translator.py          # Bootstrap 化 HTML translator mixin
├── theme/pydata_sphinx_theme/
│   ├── theme.conf         # 继承关系、默认选项、默认侧栏
│   ├── layout.html        # 页面骨架
│   ├── search.html        # 搜索页
│   ├── sections/          # 9 个页面区段
│   ├── components/        # 23 个可插拔组件
│   └── static/            # 构建产物（主题 CSS 等）
├── assets/
│   ├── scripts/           # 主题 JS、Bootstrap 包装、FontAwesome 包装
│   └── styles/            # SCSS：变量、组件、区段、扩展适配
└── locale/                # 10 种语言的 gettext 目录
```

`pyproject.toml` 通过 `sphinx.html_themes` entry point 让 Sphinx 发现主题；`sphinx-theme-builder` 负责在安装/构建时编译 SCSS 与 JS。

## 2. setup() 的事件管线

`setup(app)` 只做四件事：注册主题、连接事件、注册翻译目录、把 `components/` 加入模板搜索路径。

```text
builder-inited
├── add_shorten_xform        # 按 shorten_urls 决定是否注册链接缩短 transform
├── translator.setup_translators  # 为 HTML builders 注入 Bootstrap translator mixin
└── update_config            # 迁移废弃键、校验 switcher、注入 analytics、整理 icon_links/logo

html-page-context（每个页面）
├── _fix_canonical_url       # 修正 dirhtml 的 canonical URL
├── edit_this_page.setup_edit_url   # 注入 get_edit_provider_and_url()
├── toctree.add_toctree_functions   # 注入 generate_*_html / navbar_align_class
├── update_and_remove_templates     # 过滤空模板、去重 CSS、注入 DOCUMENTATION_OPTIONS
├── logo.setup_logo_path            # 计算 logo 的相对路径
└── utils.set_secondary_sidebar_items  # 解析按页次级侧栏配置

build-finished
├── pygments.overwrite_pygments_css  # 重写 _static/pygments.css
└── logo.copy_logo_images            # 复制 light/dark logo 到 _static
```

这条管线解释了三个常见现象：

1. **为什么改 `html_theme_options` 有时不生效**：`builder-inited` 之后应修改 `app.builder.theme_options`，而不是 `app.config.html_theme_options`。
2. **为什么某些模板"消失"**：`update_and_remove_templates` 会剔除渲染为空的模板。
3. **为什么构建后 `pygments.css` 与源码里的不一样**：它在 `build-finished` 被双主题版本覆盖。

## 3. 模板继承链

```text
basic/layout.html（Sphinx 内置）
└── pydata_sphinx_theme/layout.html
    ├── sections/announcement.html
    ├── sections/header.html
    │   ├── components/navbar-logo.html
    │   ├── components/navbar-nav.html
    │   ├── components/navbar-icon-links.html
    │   ├── components/search-button-field.html
    │   └── components/theme-switcher.html
    ├── sections/header-article.html
    │   └── components/breadcrumbs.html
    ├── sections/sidebar-primary.html
    │   ├── components/sidebar-collapse.html
    │   └── components/sidebar-nav-bs.html
    ├── sections/sidebar-secondary.html
    │   ├── components/page-toc.html
    │   ├── components/edit-this-page.html
    │   └── components/sourcelink.html
    ├── sections/footer-article.html
    ├── sections/footer-content.html
    └── sections/footer.html
```

`layout.html` 主要重写 `css`、`extrahead`、`body_tag`、`content`、`footer` 等块。它还把 `<html>` 的 `data-content_root` 与 `data-theme` 写好，使前端脚本无需猜测站点根路径。

## 4. 构建期与运行期的分工

| 阶段 | 负责 | 产物 |
|---|---|---|
| 构建期（Python） | 配置迁移、导航树解析、模板选择、HTML 改写、CSS/JS 资源注入 | 带 `pst-` 类名的 HTML、`_static/pygments.css`、复制后的 logo |
| 构建期（Node） | SCSS → CSS、JS 打包、vendor 资源 | `pydata-sphinx-theme.css`、`bootstrap.js`、`fontawesome.js` |
| 运行期（浏览器） | 主题切换、搜索弹窗、搜索即输、版本切换、公告、TOC 高亮、抽屉 | DOM 状态与 `localStorage` |

## 5. 配置数据的流向

```text
conf.py: html_theme_options
        │
        ▼
Sphinx 复制到 app.builder.theme_options
        │
        ▼
update_config() 迁移/补全/校验
        │
        ▼
Jinja 上下文中的 theme_* 变量
        │
        ├── sections/*.html 决定渲染哪些组件
        └── components/*.html 读取具体值
```

`utils.get_theme_options_dict(app)` 优先返回 `app.builder.theme_options`，只有 builder 尚未建立时才回退到 `app.config.html_theme_options`。这是写自定义扩展时必须遵守的顺序。

## 6. 关键设计约束

1. **不要在 `html-page-context` 里修改 `app.config`**：此时页面上下文已生成，改配置不会反映到当前页。
2. **不要假设所有 builder 都有主题**：`add_shorten_xform` 会检查 `hasattr(app.builder, "theme")`，`setup_translators` 会检查 `format == "html"`；自定义代码应同样防御。
3. **不要绕过 `pathto` 拼静态资源路径**：主题用 `pathto(..., resource=True)` 处理 `dirhtml` 与相对深度。
4. **并行安全是声明，不是自动保证**：主题返回 `parallel_read_safe` / `parallel_write_safe`，自定义回调若写共享状态需自行加锁或改为幂等。

## 相关概念

- [布局与模板区段](03-layout-and-sections.md)
- [内部实现与扩展点](09-internals-and-extension-points.md)
- [主题配置项](06-theme-options.md)
- [Sphinx 事件系统](../../sphinx/concepts/05-event-system.md)
