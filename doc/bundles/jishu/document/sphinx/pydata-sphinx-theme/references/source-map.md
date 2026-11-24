---
type: Reference
title: 源码路径映射
description: pydata-sphinx-theme 核心文件、职责与关键符号索引
tags: [sphinx, theme, pydata, source, reference]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:36:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-repo
    resource: https://github.com/pydata/pydata-sphinx-theme
    title: pydata-sphinx-theme GitHub Repository
---

# 源码路径映射

基准版本：`0.25.0dev0`（`73732a16`）。路径均相对于仓库根。

## Python 模块

| 路径 | 职责 | 关键符号 |
|---|---|---|
| `src/pydata_sphinx_theme/__init__.py` | 入口、配置更新、模板过滤、canonical URL | `setup`、`update_config`、`update_and_remove_templates`、`_fix_canonical_url`、`add_shorten_xform` |
| `src/pydata_sphinx_theme/utils.py` | 选项读取与模板工具 | `get_theme_options_dict`、`config_provided_by_user`、`maybe_warn`、`set_secondary_sidebar_items`、`_update_and_remove_templates` |
| `src/pydata_sphinx_theme/toctree.py` | 导航 HTML 生成 | `add_toctree_functions`、`generate_header_nav_html`、`generate_toctree_html`、`generate_toc_html`、`navbar_align_class`、`add_collapse_checkboxes` |
| `src/pydata_sphinx_theme/edit_this_page.py` | 编辑链接 | `setup_edit_url`、`get_edit_provider_and_url` |
| `src/pydata_sphinx_theme/logo.py` | logo 路径与复制 | `setup_logo_path`、`copy_logo_images` |
| `src/pydata_sphinx_theme/pygments.py` | 双主题高亮 CSS | `get_pygments_stylesheet`、`overwrite_pygments_css` |
| `src/pydata_sphinx_theme/short_link.py` | GitHub/GitLab 链接缩短 | `ShortenLinkTransform`、`parse_url` |
| `src/pydata_sphinx_theme/translator.py` | HTML translator mixin | `BootstrapHTML5TranslatorMixin`、`setup_translators` |

## 主题模板

| 路径 | 职责 |
|---|---|
| `theme/pydata_sphinx_theme/theme.conf` | 继承关系、默认选项、默认侧栏 |
| `theme/pydata_sphinx_theme/layout.html` | 页面骨架、主题初始化脚本、搜索对话框 |
| `theme/pydata_sphinx_theme/search.html` | 搜索页 |
| `theme/pydata_sphinx_theme/sections/` | 9 个页面区段 |
| `theme/pydata_sphinx_theme/components/` | 23 个可插拔组件 |
| `theme/pydata_sphinx_theme/static/styles/theme.css` | 构建产物的占位/样式入口 |

## 前端资源

| 路径 | 职责 |
|---|---|
| `assets/scripts/pydata-sphinx-theme.js` | 主题切换、搜索、版本切换、公告、TOC 同步、抽屉、回到顶部 |
| `assets/scripts/bootstrap.js` | Bootstrap 初始化、tooltip、回到顶部、主题下拉 tooltip |
| `assets/scripts/mixin.js` | `documentReady` |
| `assets/scripts/fontawesome.js` | FontAwesome 初始化 |
| `assets/styles/pydata-sphinx-theme.scss` | SCSS 总入口 |
| `assets/styles/variables/` | 颜色、字体、布局、图标、admonition 变量 |
| `assets/styles/components/` | 组件样式 |
| `assets/styles/sections/` | 区段样式 |
| `assets/styles/extensions/` | ABlog、Bootstrap、copybutton、mermaid、notebook 等扩展适配 |

## 构建与测试

| 路径 | 职责 |
|---|---|
| `pyproject.toml` | 依赖、entry point、sphinx-theme-builder 配置、ruff/pytest 配置 |
| `package.json` | webpack/sass/stylelint/prettier 脚本与前端依赖 |
| `webpack.config.js` | 资源打包规则 |
| `tests/test_build.py` | 多站点构建快照回归 |
| `tests/test_a11y.py` | Playwright + Axe 可访问性扫描 |
| `tests/test_playwright.py` | 交互行为测试 |
| `tests/test_short_url.py` | 链接缩短单测 |
| `tests/sites/` | 测试用 Sphinx 站点配置 |
| `tests/test_build/` | 快照基线 |

## 文档源

| 路径 | 内容 |
|---|---|
| `docs/user_guide/` | 安装、布局、导航、页内目录、搜索、版本、品牌、深色、i18n、静态资源 |
| `docs/community/` | 设计系统、贡献、发布、版本策略、可访问性实践 |
| `docs/examples/` | Kitchen Sink、PyData、Notebook、博客、Gallery |
| `docs/_extension/` | 文档专用指令（gallery、component） |

## 快速定位

- 改默认值：`theme.conf`
- 改页面骨架：`layout.html`
- 改顶部导航：`toctree.py` + `components/navbar-nav.html`
- 改侧栏树：`toctree.py` + `components/sidebar-nav-bs.html`
- 改页内目录：`toctree.py` + `components/page-toc.html`
- 改主题切换：`components/theme-switcher.html` + `pydata-sphinx-theme.js`
- 改搜索：`components/search-*.html` + `pydata-sphinx-theme.js`
- 改高亮：`pygments.py` + `theme.conf`
- 改 logo：`logo.py` + `components/navbar-logo.html`
- 改编辑链接：`edit_this_page.py` + `components/edit-this-page.html`
- 改 HTML 输出：`translator.py` 或新增 `SphinxPostTransform`
