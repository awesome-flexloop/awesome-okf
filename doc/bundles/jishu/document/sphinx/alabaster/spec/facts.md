---
type: spec
title: "Alabaster 源码事实清单"
---

# Alabaster 源码事实清单

> R 阶段采集的零推测事实，每个事实可通过源码路径验证。

## 项目元数据

- F-001: 版本号 `__version__ = "1.0.0"`，`__version_info__ = (1, 0, 0)`
- F-002: `pyproject.toml` 要求 `requires-python = ">=3.10"`
- F-003: `setup(app)` 中调用 `app.require_sphinx("6.2")`，要求 Sphinx >= 6.2
- F-004: 构建系统使用 `flit_core>=3.7`，build-backend 为 `flit_core.buildapi`
- F-005: 通过 entry point `[project.entry-points."sphinx.html_themes"]` 注册，键为 `alabaster = "alabaster"`
- F-006: 许可证为 BSD-3-Clause

## 核心 Python 模块（alabaster/__init__.py）

- F-007: `get_path()` 函数返回主题包所在目录的绝对路径（`os.path.abspath(os.path.dirname(os.path.dirname(__file__)))`）
- F-008: `update_context(app, pagename, templatename, context, doctree)` 函数向模板上下文注入 `alabaster_version` 和 `alabaster_version_info`
- F-009: `update_context()` 读取 `app.config.html_theme_options["show_powered_by"]`，转换为 `context["show_sphinx"]` 布尔值（支持字符串 "true"/"false" 和整数值）
- F-010: `setup(app)` 中 `theme_path = os.path.abspath(os.path.dirname(__file__))`
- F-011: `setup(app)` 调用 `app.add_html_theme("alabaster", theme_path)` 注册主题
- F-012: `setup(app)` 调用 `app.connect("html-page-context", update_context)` 连接事件
- F-013: `setup(app)` 返回字典 `{"version": __version__, "parallel_read_safe": True, "parallel_write_safe": True}`

## Pygments 样式（alabaster/support.py）

- F-014: 定义 `class Alabaster(Style)` 继承自 `pygments.style.Style`
- F-015: `background_color = "#f8f8f8"`，`default_style = ""`
- F-016: `styles` 字典定义了完整的 Pygments token 颜色映射（Comment、Keyword、Name、String、Number、Operator、Generic 等）
- F-017: Comment 样式为 `italic #8f5902`，Keyword 为 `bold #004461`，String 为 `#4e9a06`，Number 为 `#990000`
- F-018: Name.Exception 为 `bold #cc0000`，Name.Builtin 为 `#004461`，Generic.Deleted 为 `#a40000`，Generic.Inserted 为 `#00A000`

## 主题配置（alabaster/theme.conf）

- F-019: `[theme]` 段 `inherit = basic`，继承 Sphinx 内置 basic 主题
- F-020: `stylesheet = basic.css, alabaster.css`，加载两个样式表
- F-021: `sidebars = about.html, searchfield.html, navigation.html, relations.html, donate.html`
- F-022: `pygments_style = alabaster.support.Alabaster`，指向自定义 Pygments 样式类
- F-023: `[options]` 段定义了 50+ 个配置项，包含布局、颜色、字体、服务链接等类别

### 布局选项

- F-024: `page_width = 940px`，`sidebar_width = 220px`，`body_min_width = inherit`
- F-025: `fixed_sidebar = false`（默认关闭固定侧边栏）
- F-026: `sidebar_collapse = true`，`sidebar_includehidden = true`
- F-027: `show_powered_by = true`，`show_relbars = false`，`show_related = false`

### 服务链接选项

- F-028: `github_button = true`，`github_count = true`，`github_type = watch`，`github_banner = false`
- F-029: `github_user = ""`，`github_repo = ""`（默认为空）
- F-030: `travis_button = false`，`codecov_button = false`，`analytics_id = ""`
- F-031: `donate_url = ""`，`opencollective = ""`，`tidelift_url = ""`
- F-032: `badge_branch = master`

### 颜色体系

- F-033: 全局灰度：`gray_1 = #444`，`gray_2 = #EEE`，`gray_3 = #AAA`
- F-034: 粉色系：`pink_1 = #FCC`，`pink_2 = #FAA`，`pink_3 = #D52C2C`
- F-035: 主色：`base_bg = #fff`，`base_text = #000`，`body_text = #3E4349`，`link = #004B6B`，`link_hover = #6D4100`
- F-036: 侧边栏色：`sidebar_text = #555`，`sidebar_list = #000`，`narrow_sidebar_bg = #333`，`narrow_sidebar_fg = #FFF`
- F-037: 代码色：`code_bg = #ecf0f3`，`code_text = #222`，`code_highlight = #FFC`，`highlight_bg = #FAF3E8`
- F-038: 提示框色：`note_border = #CCC`，`seealso_border = #CCC`，`tip_border = #CCC`，`footnote_bg = #FDFDFD`

### 字体选项

- F-039: `font_size = 17px`，`code_font_size = 0.9em`
- F-040: `font_family = Georgia, serif`
- F-041: `code_font_family = 'Consolas', 'Menlo', 'DejaVu Sans Mono', 'Bitstream Vera Sans Mono', monospace`
- F-042: `caption_font_size = inherit`，`caption_font_family = inherit`，`head_font_family` 为空（继承默认）

## Jinja2 模板

### layout.html（主布局模板）

- F-043: `{%- extends "basic/layout.html" %}` 继承 basic 主题布局
- F-044: `extrahead` 块中加载 `custom.css` 并处理 `touch_icon` 和 `canonical_url`
- F-045: 定义 `rellink_markup()` 宏生成上下页导航（prev/next）
- F-046: 通过 `{%- set theme_show_relbar_top = theme_show_relbar_top or theme_show_relbars %}` 处理 show_relbars 开关
- F-047: 覆盖 `relbar1` 和 `relbar2` 为空块（移除默认顶部/底部导航栏）
- F-048: `content` 块根据 `fixed_sidebar` 选择布局：固定侧边栏模式自定义布局，否则调用 `{{ super() }}`
- F-049: `footer` 块包含版权信息、Powered by Sphinx & Alabaster、Page source 链接、GitHub banner、Google Analytics 脚本

### about.html（Logo 与项目信息）

- F-050: 处理 `logo` 配置：有 logo 时显示 `<img>`，否则显示文本标题
- F-051: `logo_name` 配置支持三态：`true` 显示项目名，`false` 不显示，其他字符串显示自定义文本
- F-052: `description` 配置显示项目简介（blurb）
- F-053: GitHub 按钮通过 iframe 嵌入 `ghbtns.com`，支持 `github_type`（watch/star/fork）和 `github_count`
- F-054: Travis-CI 按钮和 CodeCov 按钮通过 `badge_branch` 配置分支

### navigation.html（目录导航）

- F-055: 使用 `{{ toctree(includehidden=theme_sidebar_includehidden, collapse=theme_sidebar_collapse) }}` 生成目录树
- F-056: `extra_nav_links` 配置项支持在主导航下方添加自定义外部链接（字典格式）

### relations.html（相关页面导航）

- F-057: 生成面包屑式层级导航，显示父级文档链和上下页链接
- F-058: 通过 `parents` 变量迭代生成嵌套 `<ul>` 结构

### donate.html（捐赠与支持）

- F-059: 支持三种捐赠渠道：`donate_url`（通用捐赠徽章）、`opencollective`（Open Collective）、`tidelift_url`（Tidelift 商业支持）
- F-060: `opencollective_button_color` 配置 Open Collective 按钮颜色

## 文档与背景

- F-061: Alabaster 最初基于 Kenneth Reitz 的 krTheme（Requests 项目使用的主题），后者基于 Armin Ronacher 的 Flask 主题
- F-062: 从 Sphinx 1.3 开始成为 Sphinx 安装时的依赖并被设为默认主题
- F-063: 官方文档站点为 https://alabaster.readthedocs.io/
- F-064: 支持通过 `_static/custom.css` 进行自定义 CSS 覆盖（0.7.8 版本新增）
- F-065: `canonical_url` 选项已废弃，推荐使用 Sphinx 内置 `html_baseurl`
- F-066: `show_powered_by` 选项在 0.17.14 版本废弃，推荐使用 `html_show_sphinx`
- F-067: `gittip_user`/`gratipay_user` 选项已废弃（对应服务已关闭）
