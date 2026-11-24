---
type: spec
title: "pydata-sphinx-theme 源码事实清单"
---

# pydata-sphinx-theme 源码事实清单

> R 阶段采集的零推测事实，每条均可通过源码路径或配置文件复核。采集基准：仓库 `73732a16`（`__version__ = "0.25.0dev0"`）。

## 项目元数据与依赖

- F-001: `src/pydata_sphinx_theme/__init__.py` 定义 `__version__ = "0.25.0dev0"`。
- F-002: `pyproject.toml` 要求 `requires-python = ">=3.11"`。
- F-003: 运行时依赖为 `sphinx>=8.2,<10`、`beautifulsoup4`、`docutils!=0.17.0`、`Babel`、`pygments>=2.7`、`accessible-pygments`、`jinja2`、`requests`。
- F-004: 构建后端为 `sphinx_theme_builder`（`sphinx-theme-builder>=0.3.2`），配置 `node-version = "24.22.2"`、`theme-name = "pydata_sphinx_theme"`。
- F-005: `[project.entry-points."sphinx.html_themes"]` 注册 `pydata_sphinx_theme = "pydata_sphinx_theme"`。
- F-006: `package.json` 依赖 Bootstrap `^5.2.2`、`@popperjs/core`、`compare-versions`、FontAwesome 7（`@fortawesome/fontawesome-free ^7.2.0`）。
- F-007: 前端构建使用 webpack 5 + sass + css-loader/style-loader，`npm run build` 执行 `webpack --mode=production`。
- F-008: `[tool.sphinx-theme-builder].additional-compiled-static-assets` 列出 `webpack-macros.html`、`vendor/`、`scripts/bootstrap.js`、`scripts/fontawesome.js`、`locale/`。

## 入口与事件接线

- F-009: `setup(app)` 通过 `app.add_html_theme("pydata_sphinx_theme", theme_path)` 注册主题，`theme_path = <package>/theme/pydata_sphinx_theme`。
- F-010: `setup(app)` 连接 3 个 `builder-inited` 回调：`add_shorten_xform`、`translator.setup_translators`、`update_config`。
- F-011: `setup(app)` 连接 6 个 `html-page-context` 回调：`_fix_canonical_url`、`edit_this_page.setup_edit_url`、`toctree.add_toctree_functions`、`update_and_remove_templates`、`logo.setup_logo_path`、`utils.set_secondary_sidebar_items`。
- F-012: `setup(app)` 连接 2 个 `build-finished` 回调：`pygments.overwrite_pygments_css`、`logo.copy_logo_images`。
- F-013: `setup(app)` 调用 `app.add_message_catalog("sphinx", here / "locale")`，并把主题的 `components` 目录追加到 `app.config.templates_path`。
- F-014: `setup(app)` 返回 `{"parallel_read_safe": True, "parallel_write_safe": True}`。

## 配置更新（update_config）

- F-015: `update_config` 优先操作 `app.builder.theme_options`（通过 `utils.get_theme_options_dict`），因为 `builder-inited` 之后修改 `app.config.html_theme_options` 不会影响页面 Jinja 上下文。
- F-016: 兼容废弃键：`pygment_light_style` / `pygment_dark_style` 会被改写为 `pygments_light_style` / `pygments_dark_style` 并发出告警。
- F-017: `icon_links` 不是列表时抛出 `ExtensionError`。
- F-018: `disable_search=True` 且用户未显式设置 `navbar_persistent` 时，将其设为 `[]`。
- F-019: 用户未配置 `html_permalinks_icon` 时，主题默认设为 `"#"`。
- F-020: `switcher` 为字典且 `check_switcher` 为真时，读取并校验版本 JSON：缺 `url` 或 `version` 键会告警，非法 JSON 会报错；支持 http(s) URL 与相对 `srcdir` 的本地路径。
- F-021: `analytics.plausible_analytics_domain` + `plausible_analytics_url` 会注册 defer 脚本；`analytics.google_analytics_id` 会注入 consent 默认拒绝的 gtag 脚本。
- F-022: 扩展列表含 `ablog` 且用户未配置 `fontawesome_included` 时，自动将其设为 `True`。
- F-023: `github_url`、`gitlab_url`、`bitbucket_url`、`twitter_url` 四个快捷配置会被转换为 `icon_links` 条目并插入列表头部。
- F-024: `theme_logo_link` 会写入 `logo["link"]`；`logo` 不是字典时抛 `ValueError`。

## 主题配置（theme.conf）

- F-025: `[theme]` 段 `inherit = basic`，`stylesheet = styles/pydata-sphinx-theme.css`，`pygments_style = tango`，`sidebars = sidebar-collapse, sidebar-nav-bs`。
- F-026: `[options]` 共约 50 个键，含 31 个通用/功能选项、17 个模板放置选项、2 个废弃别名。
- F-027: 默认 `navbar_start = navbar-logo`，`navbar_center = navbar-nav`，`navbar_end = theme-switcher, navbar-icon-links`，`navbar_persistent = search-button-field`。
- F-028: 默认 `article_header_start = breadcrumbs`；`primary_sidebar_end = sidebar-ethical-ads`；`secondary_sidebar_items = page-toc, edit-this-page, sourcelink`。
- F-029: 默认 `footer_start = copyright, sphinx-version`，`footer_center` 为空，`footer_end = theme-version`。
- F-030: 默认 `show_nav_level = 1`、`navigation_depth = 4`、`show_toc_level = 1`、`header_links_before_dropdown = 5`、`header_dropdown_text = More`。
- F-031: 默认 `pygments_light_style = a11y-high-contrast-light`、`pygments_dark_style = a11y-high-contrast-dark`，来自 `accessible-pygments`。
- F-032: 默认 `shorten_urls = True`、`back_to_top_button = True`、`search_as_you_type = False`、`surface_warnings = True`、`check_switcher = True`、`sticky_banners = False`。

## 布局与模板

- F-033: `theme/pydata_sphinx_theme/layout.html` 继承 `basic/layout.html`，重定义 `<html>` 标签并输出 `data-content_root` 与可选 `data-theme`。
- F-034: `layout.html` 在 `<head>` 内联脚本中从 `localStorage` 读取 `mode` / `theme`，避免主题闪烁；并用 `<noscript>` 隐藏 `.pst-js-only`。
- F-035: `layout.html` 定义搜索对话框 `<dialog id="pst-search-dialog">`，`disable_search` 为真时整块不渲染。
- F-036: `layout.html` 由 `sections/` 下 9 个片段组成：`announcement`、`header`、`header-article`、`sidebar-primary`、`sidebar-secondary`、`footer-article`、`footer-content`、`footer`、`article`。
- F-037: `components/` 目录含 23 个可插拔组件模板，包括 `breadcrumbs`、`navbar-logo`、`navbar-nav`、`navbar-icon-links`、`page-toc`、`edit-this-page`、`sourcelink`、`version-switcher`、`theme-switcher`、`search-button-field`、`search-field`、`sidebar-nav-bs`、`sidebar-collapse`、`indices`、`prev-next`、`last-updated` 等。
- F-038: `sections/header.html` 渲染 `navbar_start` / `navbar_center` / `navbar_end` / `navbar_persistent` 四区，并在窄屏渲染主/次侧栏的汉堡按钮。

## 模板过滤与资产注入

- F-039: `update_and_remove_templates` 处理的模板区段包括 `theme_navbar_start`、`theme_navbar_center`、`theme_navbar_persistent`、`theme_navbar_end`、`theme_article_header_start`、`theme_article_header_end`、`theme_article_footer_items`、`theme_content_footer_items`、`theme_footer_start`、`theme_footer_center`、`theme_footer_end`、`theme_primary_sidebar_end`、`sidebars`。
- F-040: 模板名不带后缀时自动补 `.html`；渲染结果为空白的模板会被剔除，`templates_skip_empty_check` 中的模板跳过该检查。
- F-041: 主题 CSS 同时出现在 `theme.conf` 与 `webpack-macros.html`，代码会从 `context["css_files"]` 中删除重复的 `_static/styles/pydata-sphinx-theme.css`。
- F-042: `theme_favicons` 中每个图标会通过 `app.add_css_file` 注册，`rel`、`sizes`、`type` 可由配置覆盖。
- F-043: 每页向 `DOCUMENTATION_OPTIONS` 注入 `pagename`、`theme_version`；存在 `switcher` 时再注入 `theme_switcher_json_url`、`theme_switcher_version_match`、`show_version_warning_banner`。
- F-044: `search_as_you_type` 在 `pagename == "search"` 时强制为 `false`，避免与 `searchtools.js` 争用 `#search-results`。

## 导航与目录树（toctree.py）

- F-045: `LinkInfo` 数据类含 `is_current`、`is_current_page`、`href`、`title`、`is_external` 五个字段；`is_current` 标记当前章节，`is_current_page` 仅标记当前页。
- F-046: 顶部导航链接来自 `root_doc` 的 toctree 条目，外加 `theme_external_links`；标题缺失时依次回退到文档标题、`Index`、`Python Module Index`、`Search`。
- F-047: `generate_header_nav_html` 的折叠逻辑：若链接数 ≤ `n+1` 则全部显示；否则前 `n` 个显示，其余进入 `More` 下拉。
- F-048: `generate_toctree_html(kind="sidebar", startdepth=1)` 从当前顶层祖先页面生成侧栏子树，而不是从全站根节点生成。
- F-049: 侧栏 HTML 会为顶层 `<ul>` 添加 `nav bd-sidenav`，为有子节点的 `<li>` 添加 `has-children`，并插入 `<details>/<summary>` 折叠控件。
- F-050: `show_nav_level=0` 时，`p.caption` 与紧随其后的 `<ul>` 被包进 `li.toctree-l0`，实现按 caption 折叠整段。
- F-051: 侧栏 toctree 缓存仅在 `kind == "sidebar"`、`collapse=False`、`startdepth==0` 或存在祖先、且页面 URI 不以 `/` 结尾时启用；键为 `(祖先, 输出目录, show_nav_level, 排序后的 kwargs)`。
- F-052: 缓存命中时通过 `_move_current_markers` 把 `current/active` 类、`aria-current`、`<details open>` 从旧页条目迁移到当前页条目。
- F-053: `generate_toc_html` 为页内 TOC 添加 `toc-hN`、`nav`、`section-nav`、`flex-column`、`toc-entry`、`nav-link` 类；只有一个 `h1` 且无 `h2` 时返回空 TOC。
- F-054: `navbar_align_class` 支持 `content`（`col-lg-3`/`col-lg-9`/`me-auto`）、`left`、`right`，其他值抛 `ValueError`。

## 页内 TOC 与次级侧栏

- F-055: `utils.set_secondary_sidebar_items` 支持列表或 `{页面模式: 模板列表}` 字典；字典按 `sphinx.util.matching.patmatch` 匹配，支持 `*`、`?`、`[` 通配。
- F-056: 同一页面匹配两个通配模式时发出警告，并采用最后一个匹配项。
- F-057: 页面元数据含 `html_theme.sidebar_secondary.remove` 时，`layout.html` 不渲染次级侧栏。
- F-058: `edit_this_page.setup_edit_url` 支持 GitHub、GitLab、Bitbucket 与自定义 `edit_page_url_template`；自定义模板必须包含 `file_name`。
- F-059: 编辑链接由 `pagename` + `page_source_suffix`、`doc_path` 与 provider 版本分支拼接；预置 provider 的链接文案为 “Edit on GitHub/GitLab/Bitbucket”。

## 品牌、样式与暗色模式

- F-060: `logo.setup_logo_path` 为 `logo.image_light` / `logo.image_dark` 计算 `image_relative`；URL 原样使用，本地文件经 `pathto("_static/<name>")`。
- F-061: 未提供某模式 logo 时回退到 `html_logo`；两者都没有则不写该键。
- F-062: `logo.copy_logo_images` 在 `build-finished` 把本地 logo 复制到 `_static`；目标已存在则跳过；路径缺失告警；路径以 `_t` 结尾时抛 `ExtensionError`（防止模板注入）。
- F-063: `pygments.get_pygments_stylesheet` 生成两份规则，前缀分别为 `html[data-theme="light"] .highlight` 与 `html[data-theme="dark"] .highlight`。
- F-064: `overwrite_pygments_css` 在 `build-finished` 覆盖 `_static/pygments.css`，回退样式为 `tango`（light）与 `monokai`（dark）；样式名不存在时告警并回退。
- F-065: 主题 CSS 变量包括 `--pst-color-primary`、`--pst-color-secondary`、`--pst-color-accent`、`--pst-color-success/info/warning/danger`、`--pst-color-background/on-background/surface/on-surface/target`。
- F-066: 主题在 `html[data-theme="light"]` 与 `html[data-theme="dark"]` 上定义颜色，因此自定义需用 `html[data-theme]` 选择器而非 `:root`。
- F-067: 字体变量包括 `--pst-font-family-base`、`--pst-font-family-display`、`--pst-font-family-heading`、`--pst-font-family-monospace`，以及对应的 `*-system` 回退变量。
- F-068: 仅内置 FontAwesome 7 Free 字体；正文与标题默认使用系统字体；v0.24.0 起 FontAwesome `<i>` 不再被转换为 `<svg>`（自定义图标仍是 `<svg>`）。

## 前端行为（JavaScript）

- F-069: `setTheme(mode)` 接受 `auto|light|dark`，写入 `document.documentElement.dataset.mode/theme` 与 `localStorage`；`auto` 监听 `prefers-color-scheme`。
- F-070: 搜索快捷键为 Windows/Linux 的 `Ctrl+K` 与 macOS 的 `Cmd+K`；Escape 关闭搜索框。
- F-071: `search_as_you_type` 使用 Sphinx 的 `Search.performSearch`，300 ms 防抖，并把结果注入 `#search-results`；通过 `data-content_root` 修正相对链接。
- F-072: 版本切换器从 `switcher.json` 读取条目；点击时先 `HEAD` 请求目标页，存在则跳转，404/CORS 失败则回退到目标版首页。
- F-073: 版本警告横幅要求 JSON 中恰好一个 `preferred: true`；关闭后写入 `localStorage.pst_banner_pref`，14 天内不再显示。
- F-074: `announcement` 以 `http` 开头时异步 fetch 远程 HTML；空文件视为移除；关闭状态写入 `pst_announcement_banner_pref`，保留 14 天。
- F-075: 次级侧栏 TOC 使用 `IntersectionObserver` 同步滚动高亮；点击目录后 1 秒内禁用观察器，避免高亮跳动。
- F-076: 窄屏下主/次侧栏被整体搬入 `<dialog>`，关闭时再搬回；`ResizeObserver` 在跨越断点时自动关闭抽屉。
- F-077: 可横向滚动的 `pre`、notebook 输出、表格容器等会被动态设置 `tabIndex=0`，使其可键盘聚焦。

## 翻译与 HTML 转换

- F-078: `translator.BootstrapHTML5TranslatorMixin` 为 `role="heading"` 的标签补 `aria-level="2"`，并设置 `table_style = "table"`。
- F-079: 表格被包进 `<div class="pst-scrollable-table-container">`，`autosummary` 表格额外获得 `autosummary` 类。
- F-080: `setup_translators` 仅对 `app.builder.format == "html"` 生效；对默认 translator 或注册表中的每个 translator 动态构造 `BootstrapHTML5Translator`。
- F-081: `short_link.ShortenLinkTransform` 是 `SphinxPostTransform`，`default_priority = 400`，`formats = ("html",)`，仅处理显示文本与 URL 完全相同的链接。
- F-082: GitHub 链接缩短规则：机构/仓库保留 `org/repo`，`issues`/`pull`/`discussions` 追加 `#编号`，`orgs/<org>/projects/<id>` 变为 `<org>/projects#<id>`；GitLab 的 issue 用 `#`、merge request 用 `!`。
- F-083: `_fix_canonical_url` 修正 `dirhtml` builder 下 Sphinx 生成 `.html` 结尾 canonical URL 的问题。
- F-084: `locale/` 提供 10 种语言目录：`ca`、`cs`、`de`、`en`、`es`、`fr`、`it`、`ja`、`ru`、`zh`，并含 `sphinx.pot` 模板。

## 质量保障

- F-085: `tests/test_build.py` 用 `pytest-regressions` 对 `tests/sites/` 多套配置的构建产物做快照比对。
- F-086: `tests/test_a11y.py` 用 Playwright + Axe-core 扫描 Kitchen Sink 页面，检查可访问性违规。
- F-087: `tests/test_playwright.py` 覆盖交互行为（主题切换、搜索、侧栏、版本切换等）；`tests/test_short_url.py` 覆盖链接缩短。
- F-088: 文档声明自动化可访问性测试最多只能发现约 30–40% 的问题，不能替代人工测试。
