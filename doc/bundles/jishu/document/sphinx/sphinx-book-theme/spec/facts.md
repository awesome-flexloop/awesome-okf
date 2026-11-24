---
type: spec
title: "sphinx-book-theme 源码事实清单"
---

# sphinx-book-theme 源码事实清单

> R 阶段采集的零推测事实。每条均可通过仓库路径或官方文档验证。事实陈述不使用因果解释。

## 项目元数据

- F-001: `src/sphinx_book_theme/__init__.py` 中 `__version__ = "1.5.0.dev"`。
- F-002: `pyproject.toml` 中 `requires-python = ">=3.11"`。
- F-003: 依赖 `sphinx>=8.2`。
- F-004: 依赖 `pydata-sphinx-theme==0.23.0`（精确版本）。
- F-005: 构建后端为 `sphinx_theme_builder`，要求 `sphinx-theme-builder >= 0.2.0a7`。
- F-006: `[tool.sphinx-theme-builder]` 中 `node-version = "20.9.0"`、`theme-name = "sphinx_book_theme"`。
- F-007: entry point 为 `[project.entry-points."sphinx.html_themes"]`，键值 `sphinx_book_theme = "sphinx_book_theme"`。
- F-008: 许可证为 BSD-3-Clause（classifier 与 LICENSE）。
- F-009: 项目描述为 "A clean book theme for scientific explanations and documentation with Sphinx"。
- F-010: README 含 "Maintenance Mode" 提示，声明接受缺陷修复、不保证新功能开发。
- F-011: CHANGELOG 顶部正式版本为 `v1.4.0 -- 2026-07-19`。
- F-012: CHANGELOG 中 `v1.4.0` 条目写明升级 pydata-sphinx-theme 0.20 与 Sphinx >=8.2。
- F-013: CHANGELOG 中 `v1.2.0 -- 2026-03-09` 条目写明支持 Sphinx 9 / Python 3.14，最低 Sphinx 7 / Python 3.11。
- F-014: `docs/conf.py` 中 `html_theme = "sphinx_book_theme"`。
- F-015: `docs/conf.py` 使用 `myst_nb`、`sphinx_thebe`、`sphinx_design`、`sphinx_togglebutton`、`sphinx_tabs`、`sphinx_copybutton`、`sphinxcontrib.bibtex` 等扩展。
- F-016: `docs/conf.py` 设置 `nb_execution_mode = "cache"`。
- F-017: `docs/conf.py` 的 `html_theme_options` 包含 `path_to_docs="docs"`、`repository_url`、`repository_branch="main"`、`use_edit_page_button=True`、`use_source_button=True`、`use_issues_button=True`、`use_download_button=True`、`use_sidenotes=True`、`show_toc_level=2`。
- F-018: `docs/conf.py` 的 `html_sidebars` 为 `reference/blog/*` 配置了 ABlog 侧栏组件列表。

## 主题注册与 setup

- F-019: `get_html_theme_path()` 返回 `Path(__file__).parent / "theme" / "sphinx_book_theme"`。
- F-020: `setup(app)` 调用 `app.add_html_theme("sphinx_book_theme", theme_dir)`。
- F-021: `setup(app)` 调用 `app.add_js_file("scripts/sphinx-book-theme.js")`。
- F-022: `setup(app)` 调用 `app.add_message_catalog("booktheme", locale_dir)`，locale 目录为 `theme_dir/static/locales`。
- F-023: `setup(app)` 连接 `builder-inited` 到 `update_navbar_defaults`，优先级 400。
- F-024: `setup(app)` 连接 `builder-inited` 到 `update_mode_thebe_config`、`check_deprecation_keys`、`update_sourcename`、`update_context_with_repository_info`。
- F-025: `setup(app)` 连接 `html-page-context` 到 `add_metadata_to_page`、`hash_html_assets`、`update_templates`。
- F-026: `setup(app)` 在 `setup` 内直接调用一次 `update_general_config(app, app.config)`，并再连接到 `config-inited`。
- F-027: `setup(app)` 调用 `SideNoteNode.add_node(app)`。
- F-028: `setup(app)` 连接 `html-page-context` 到 `prep_header_buttons`。
- F-029: `setup(app)` 连接 `html-page-context` 到 `add_launch_buttons`、`add_source_buttons`、`add_header_buttons`，三者优先级均为 501。
- F-030: `setup(app)` 调用 `app.add_directive("margin", Margin)`。
- F-031: `setup(app)` 调用 `app.add_post_transform(HandleFootnoteTransform)`。
- F-032: `setup(app)` 返回 `{"parallel_read_safe": True, "parallel_write_safe": True}`。
- F-033: `update_navbar_defaults` 对 `theme_options` 执行 `setdefault("navbar_persistent", [])`。
- F-034: `update_general_config` 把 `theme_dir/components` 追加到 `config.templates_path`。
- F-035: `update_templates` 处理的模板分区列表为 `["theme_footer_content_items"]`。
- F-036: `update_templates` 把逗号分隔字符串拆成列表，并给无后缀项补 `.html`。
- F-037: `add_metadata_to_page` 在 `context` 中设置 `root_doc`、`root_title`、`pagetitle`、`page_description`、`author`、`translate`。
- F-038: `add_metadata_to_page` 在用户未配置 `search_bar_text` 时设置 `context["theme_search_bar_text"] = translation("Search") + "..."`。
- F-039: `update_sourcename` 在用户未显式配置 `html_sourcelink_suffix` 时，将其设为 `""`。
- F-040: `hash_html_assets` 的资产列表为 `["scripts/sphinx-book-theme.js"]`。
- F-041: `hash_html_assets` 仅在 `app.config.html_theme == "sphinx_book_theme"` 时追加 `"styles/sphinx-book-theme.css"`。
- F-042: `_gen_hash` 使用 `hashlib.sha1(path.read_bytes()).hexdigest()`。
- F-043: `check_deprecation_keys` 的废弃键列表为 `["single_page"]`，warning 类型为 `"sphinxbooktheme"`。

## theme.conf

- F-044: `[theme]` 段 `inherit = pydata_sphinx_theme`。
- F-045: `pygments_style = tango`。
- F-046: `sidebars = navbar-logo.html, icon-links.html, search-button-field.html, sbt-sidebar-nav.html`。
- F-047: `stylesheet = styles/sphinx-book-theme.css`。
- F-048: `announcement` 默认为空。
- F-049: `secondary_sidebar_items = page-toc.html`。
- F-050: `toc_title = Contents`。
- F-051: `article_header_start = toggle-primary-sidebar.html`。
- F-052: `article_header_end = article-header-buttons.html`。
- F-053: `use_download_button = True`、`use_fullscreen_button = True`。
- F-054: `use_issues_button = False`、`use_source_button = False`、`use_repository_button = False`。
- F-055: `path_to_docs`、`repository_url`、`repository_branch`、`repository_provider` 默认均为空。
- F-056: `launch_buttons = {}`。
- F-057: `navbar_start`、`navbar_center`、`navbar_end`、`navbar_persistent` 默认均为空。
- F-058: `home_page_in_toc = False`。
- F-059: `show_navbar_depth = 1`、`max_navbar_depth = 4`。
- F-060: `collapse_navbar = False`。
- F-061: `extra_footer` 默认为空。
- F-062: `footer_content_items = author.html, copyright.html, last-updated.html, extra-footer.html`。
- F-063: `footer_start`、`footer_end` 默认均为空。
- F-064: `use_sidenotes = False`。
- F-065: `expand_toc_sections = []`，注释标记为 DEPRECATE。

## 模板

- F-066: `layout.html` 首行为 `{% extends "pydata_sphinx_theme/layout.html" %}`。
- F-067: `layout.html` 的 `docs_navbar` block 仅在任一 `theme_navbar_*` 非空时调用 `super()`。
- F-068: `layout.html` 的 `docs_main` block 插入 `<div class="sbt-scroll-pixel-helper"></div>`。
- F-069: `layout.html` 的 `docs_body` block 插入 `id="jb-print-docs-body"` 的打印目录容器。
- F-070: 主题 `components/` 目录包含 `article-header-buttons.html`、`author.html`、`extra-footer.html`、`page-toc.html`、`sbt-sidebar-nav.html`、`toggle-primary-sidebar.html`、`toggle-secondary-sidebar.html`。
- F-071: 主题 `sections/` 目录包含 `footer-content.html`。
- F-072: 主题 `macros/` 目录包含 `buttons.html`。
- F-073: `macros/buttons.html` 定义 `render_link_button`、`render_js_button`、`render_button_group` 三个宏。
- F-074: `macros/buttons.html` 定义 `render_funcs` 映射：`group`、`javascript`、`link`。
- F-075: `sbt-sidebar-nav.html` 调用 `generate_toctree_html`，参数含 `startdepth=0`、`kind="sidebar"`、`maxdepth=theme_max_navbar_depth|int`、`collapse=theme_collapse_navbar|tobool`、`includehidden=True`、`titles_only=True`、`show_nav_level=theme_show_navbar_depth|int`。
- F-076: `sbt-sidebar-nav.html` 在 `theme_home_page_in_toc == True` 时插入根文档链接。
- F-077: `article-header-buttons.html` 遍历 `header_buttons`，按 `button.get("type")` 选择宏，并 include `theme-switcher.html`、`search-button.html`、`toggle-secondary-sidebar.html`。
- F-078: `sections/footer-content.html` 遍历 `theme_footer_content_items`，每项 include 到 `.footer-item`。
- F-079: `theme/sphinx_book_theme/static/.gitignore` 列出 `styles`、`scripts`、`locales`。

## 页眉按钮

- F-080: `header_buttons/__init__.py` 定义 `as_bool(var)`：字符串按小写比较 `"true"`，布尔原样返回，其他返回 `False`。
- F-081: `get_repo_parts(context)` 依次检查 `github`、`bitbucket`、`gitlab` 三组 `<provider>_url`、`<provider>_user`、`<provider>_repo` 上下文变量。
- F-082: `update_context_with_repository_info` 使用 `repo_url.strip("/").rsplit("/", 2)` 拆分 `provider_url`、`org`、`repo`。
- F-083: 未显式给定 provider 时，按 URL 是否含 `bitbucket.org`、`github.com`、`gitlab.com` 推断。
- F-084: provider 推断失败时抛出 `SphinxError`，消息含 "Provider not recognized"。
- F-085: `repository_branch` 为空时，`update_context_with_repository_info` 使用 `"main"`。
- F-086: `add_header_buttons` 在 `use_download_button` 为真且存在源文件后缀时，生成下载组。
- F-087: 下载组可包含 `.ipynb`（当 `context["ipynb_source"]` 存在）、源文件后缀、`.pdf` 三项。
- F-088: `.pdf` 按钮的 `javascript` 为 `window.print()`。
- F-089: 全屏按钮的 `javascript` 为 `toggleFullScreen()`。
- F-090: `add_source_buttons` 处理 `use_issues_button`、`use_source_button`、`use_edit_page_button`、`use_repository_button` 四个开关。
- F-091: GitHub/GitLab 的源码 URL 由编辑 URL 的 `/edit/` 替换为 `/blob/` 并追加 `?plain=1`。
- F-092: Bitbucket 的源码 URL 去掉 `?mode=edit`。
- F-093: issue 按钮仅对 GitHub 与 GitLab 生成；其他 provider 记录 warning。
- F-094: 单个仓库按钮时，`text` 被清空，只显示图标；多个按钮时合并为 `group`。
- F-095: `add_launch_buttons` 在 `launch_buttons` 为空、页面非 Notebook、或未配置任何服务时直接返回。
- F-096: `_is_notebook` 在页面 metadata 含 `kernelspec` 或 `page_source_suffix` 含 `ipynb` 时返回 `True`。
- F-097: 当页面源文件为 `.md` 或 `.md.txt` 且是 Notebook 时，`add_launch_buttons` 把 `jupyter_execute/<pagename>.ipynb` 复制到 `_sources/<pagename>.ipynb`。
- F-098: `notebook_interface_prefixes` 为 `{"classic": "tree", "jupyterlab": "lab/tree"}`。
- F-099: `notebook_interface` 不在上述键中时抛出 `ValueError`。
- F-100: Binder GitHub URL 模式为 `<binderhub>/v2/gh/<org>/<repo>/<branch>?urlpath=<ui_pre>/<path_rel_repo>`。
- F-101: Binder GitLab URL 模式使用 `%2F` 连接 org 与 repo。
- F-102: 非 `https://github.com` / `https://gitlab.com` 的仓库使用 `<binderhub>/v2/git/<quote(repo_url)>/<branch>`。
- F-103: Colab 仅在 provider 为 GitHub 时生成，URL 为 `<colab_url>/github/<org>/<repo>/blob/<branch>/<path_rel_repo>`。
- F-104: Deepnote 仅在 provider 为 GitHub 时生成，URL 含 `launch?url=https%3A%2F%2Fgithub.com...`。
- F-105: JupyterLite URL 为 `<jupyterlite_url>?path=<book_relpath><pagename><jl_ext>`。
- F-106: Thebe 按钮的 `javascript` 为 `initThebeSBT()`，并设置 `context["use_thebe"] = True`。
- F-107: `launch_buttons["thebe"]` 为真但未启用 `sphinx_thebe` 时，`update_mode_thebe_config` 记录 warning 并返回。
- F-108: `update_mode_thebe_config` 在 `thebe_config` 缺少 `repository_url` / `repository_branch` 时，从主题选项补入；分支回退为 `"master"`。
- F-109: `_get_branch` 在 `repository_branch` 为空时返回 `"master"`。
- F-110: 按钮的 `label` 会生成 `btn-<label>` class。

## 边注与 margin

- F-111: `HandleFootnoteTransform.default_priority = 1`，`formats = ("html",)`。
- F-112: `HandleFootnoteTransform.run` 在 `use_sidenotes` 为 `False` 时直接返回 `None`。
- F-113: 变换通过 `foot_node.attributes["backrefs"][0] == ref_node.attributes["ids"][0]` 匹配脚注与引用。
- F-114: 脚注 `children[0]` 为编号标签，`children[1].children` 为内容。
- F-115: 内容以 `{-}` 开头时加 `marginnote` class，并移除 `{-}`。
- F-116: 非 margin note 时生成 `superscript` 编号，并加 `sidenote` class。
- F-117: 节点 `names` 分别为 `marginnote-role-<label>` 与 `sidenote-role-<label>`。
- F-118: 嵌套在非 `paragraph`/`footnote` 容器中的引用，会把内容段落插到容器之前，并在原引用处放入带 `d-n` class 的副本。
- F-119: 变换结束时从父节点移除原 `footnote`。
- F-120: `SideNoteNode` 的 HTML visitor 输出 `<label for='...' class='margin-toggle ...'>` 与 `<input type='checkbox' ... class='margin-toggle'>`。
- F-121: `Margin` 继承 `docutils.parsers.rst.directives.body.Sidebar`。
- F-122: `Margin.optional_arguments = 1`，`required_arguments = 0`。
- F-123: `Margin.run` 给首个节点的 `classes` 追加 `"margin"`。
- F-124: `Margin.run` 在无参数时把 `self.arguments` 设为 `[""]`；随后的 `if not self.arguments` 分支位于该赋值之后，条件为假。

## 样式、脚本与翻译

- F-125: SCSS 源文件按 `abstracts`、`base`、`components`、`content`、`extensions`、`sections` 分层。
- F-126: `content/_margin.scss`、`content/_notebooks.scss`、`extensions/_myst-nb.scss`、`extensions/_thebe.scss` 分别存在。
- F-127: `assets/scripts/index.js` 导入 `../styles/index.scss`。
- F-128: `index.js` 定义 `toggleFullScreen`，包含 `webkitRequestFullscreen` / `webkitExitFullscreen` 分支。
- F-129: `assets/translations/jsons/` 下有 22 个 JSON 文件。
- F-130: 翻译词条包含 `Search`、`Download this page`、`Download notebook file`、`Download source file`、`Fullscreen mode`、`Launch`、`Open an issue`、`Print to PDF`、`Source repository`、`Suggest edit` 等。

## 测试

- F-131: 测试依赖包含 `pytest`、`beautifulsoup4`、`pytest-regressions`、`myst-nb`、`sphinx_thebe`。
- F-132: `tests/sites/` 下存在 `base`、`notitle`、`parallel-build` 站点，`base` 下还有 `titles`。
- F-133: `tests/test_build/` 下存在 `build__header-article.html`、`build__pagetoc--*.html`、`build__sidebar-primary__nav.html` 等快照。
- F-134: 按钮快照文件包括 `header__launch-buttons--github.html`、`header__launch-buttons--gitlab.html`、`header__repo-buttons--all-on.html` 等。
- F-135: `pyproject.toml` 的 pytest 配置将 `DeprecationWarning` 等设为 `error`，并列出多条 ignore。

## 文档

- F-136: `docs/` 按 Diataxis 框架组织，含 `tutorials/`、`content/`、`sections/`、`components/`、`reference/`、`contributing/`。
- F-137: `docs/index.md` 的 toctree 列出 `tutorials/get-started`、`content/index`、`sections/index`、`components/index`、`reference`、`contributing/index`、`changelog`。
- F-138: `docs/reference/extensions.md` 覆盖 `sphinxcontrib-bibtex`、`ABlog`、`sphinx-togglebutton`、`sphinx-tabs`、`sphinxcontrib.youtube`、`sphinx-design`。
- F-139: `docs/contributing/style.md` 声明设计原则：极简视觉、单书用例、Tufte 元素。
- F-140: `docs/contributing/style.md` 声明 SCSS 用 `stb compile` 或 `tox -e compile` 编译，编译产物不入 git。

## 补充事实（旧包合并回补）

> 下列事实由原 `myst/sphinx-book-theme` 知识包合并回补（2026-11-24），编号自 F-141 顺延；与上文去重后保留旧包独有的逐文件／逐函数粒度事实。

### 项目元数据（补）

- F-141: `pyproject.toml` 配置 `additional-compiled-static-assets = ["locales/"]`，即翻译目录在构建时编译。
- F-142: `pyproject.toml` 的 classifier 含 `Development Status :: 4 - Beta`。
- F-143: 项目维护者为 Executable Books Team。
- F-144: 文档地址为 `https://sphinx-book-theme.readthedocs.io/`；仓库地址为 `https://github.com/executablebooks/sphinx-book-theme`。

### 主题配置与事件处理（补）

- F-145: `theme.conf` 注释说明 `use_edit_page_button` 继承自 pydata-sphinx-theme。
- F-146: `add_metadata_to_page` 处理 `root_doc`/`master_doc` 兼容（Sphinx 4.x 重命名）。
- F-147: `page_description` 由遍历 doctree 中的 section、拼接文本并截取前 160 字符生成。
- F-148: `_gen_hash(path)` 以 `hashlib.sha1` 计算文件哈希，并加 `@lru_cache(maxsize=None)` 缓存。
- F-149: `hash_assets_for_files` 为资源追加 `?digest={hash}` 参数实现缓存清除；按扩展名分类：`.css → css_files`，否则 → `script_files`。
- F-150: `DEFAULT_LOG_TYPE = "sphinxbooktheme"`。
- F-151: `update_sourcename` 以 `config_provided_by_user` 判定用户是否已显式配置 `html_sourcelink_suffix`。
- F-152: `_compat.py` 提供 `findall(node, *args, **kwargs)`：优先 `node.findall`（docutils v0.18+），回退 `node.traverse`。

### 上下文注入与按钮常量（补）

- F-153: `update_context_with_repository_info` 向 `html_context` 注入 `{provider}_user`、`{provider}_repo`、`{provider}_version`、`{provider}_url` 与 `doc_path`。
- F-154: `get_repo_url(context)` 调用 `get_repo_parts`，拼接 `f"{provider_url}/{user}/{repo}"`。
- F-155: 下载按钮组 `type="group"`、`tooltip="Download this page"`、`icon="fas fa-download"`。
- F-156: 全屏按钮 `type="javascript"`、调用 `toggleFullScreen()`、`icon="fas fa-expand"`、`classes="pst-navbar-icon"`。
- F-157: 启动按钮组 `type="group"`、`tooltip="Launch interactive content"`、`icon="fas fa-rocket"`。
- F-158: 平台图标路径：Binder `_static/images/logo_binder.svg`、JupyterHub `logo_jupyterhub.svg`、Colab `logo_colab.png`、Deepnote `logo_deepnote.svg`、JupyterLite `logo_jupyterlite.svg`。
- F-159: JupyterHub 启动 URL 为 `/hub/user-redirect/git-pull?repo=...&urlpath=...&branch=...`。
- F-160: `notebook_interface` 支持 `"classic"`（路径前缀 `tree`）与 `"jupyterlab"`（`lab/tree`），默认 `"classic"`。
- F-161: 页面源文件非 `.ipynb` 但同目录存在同名 `.ipynb` 时，自动把 extension 切换为 `.ipynb`。
- F-162: `use_repository_button` 以 `fab fa-{provider}` 作为图标。
- F-163: issue 按钮预填标题为 `"Issue on page /{pagename}.html"`。

### 模板（补）

- F-164: `macros/buttons.html` 的 `render_inner_html` 宏：fa 图标用 `<i>`，其他图标用 `<img>`。
- F-165: `sbt-webpack-macros.html` 为 webpack 宏模板（位于 `static/`）。
- F-166: `layout.html` 的 `#jb-print-docs-body` 打印目录区域含 `.onlyprint` 类 h1 与 `page-toc` 导航。

### 边注节点（补）

- F-167: `visit_SideNoteNode` 中 sidenote 类型额外输出 `<span>` 开始标签；`depart_SideNoteNode` 输出 `</span>`、`</label>` 与隐藏 `<input type='checkbox'>`。
- F-168: checkbox 的 `id`/`name` 与 label 的 `for` 一致，构成纯 CSS 点击切换。
- F-169: 嵌套检测循环向上遍历父节点直到 `section` 或 `document`；父节点为 `paragraph`/`footnote` 时继续上溯，否则执行 `replace_self`。

### JavaScript index.js（补）

- F-170: `sbRunWhenDOMLoaded(cb)`：DOM 就绪后执行回调，兼容 `addEventListener` 与 `attachEvent`。
- F-171: `initTocHide()` 以 `IntersectionObserver` 实现：margin/sidenote 进入视口时隐藏次级侧边栏；经 `sbt-scroll-pixel-helper` 检测滚动切换 `body.scrolled`。
- F-172: TOC 隐藏触发选择器类：`marginnote, sidenote, margin, margin-caption, full-width, sidebar, popout`。
- F-173: 上述选择器同时匹配四种命名变体：`.{cls}`、`.tag_{cls}`、`.{cls_with_underscores}`、`.tag_{cls_with_underscores}`。
- F-174: `initTocHide` 的 `rootMargin = "0px 0px -33% 0px"`。
- F-175: `initThebeSBT()` 在 h1 后插入 `thebe-launch-button`，调用 sphinx-thebe 的 `initThebe()`。
- F-176: `addNoPrint()` 为头部、侧边栏、页脚等导航元素添加 `noprint` 类。
- F-177: `addBlurToButtons()` 在点击按钮后 `blur()` 以消除 tooltip 残留。
- F-178: `fixSidebarToggle()` 在宽屏（≥992px）阻止切换按钮打开 dialog modal，改为切换 `pst-sidebar-hidden` 类。
- F-179: `fixSidebarToggle` 以 capture phase（`addEventListener` 第三参 `true`）在 PST 处理之前拦截事件。
- F-180: 全局暴露 `window.initThebeSBT`、`window.toggleFullScreen`。
- F-181: DOM 就绪时初始化 `initTocHide`、`addNoPrint`、`addBlurToButtons`、`fixSidebarToggle`。

### SCSS 与翻译（补）

- F-182: SCSS 目录逐文件枚举：`abstracts/`（`_mixins.scss`、`_variables.scss`）；`base/`（`_base.scss`、`_print.scss`、`_typography.scss`）；`components/`（`_back-to-top.scss`、`_icon-links.scss`、`_logo.scss`、`_search.scss`）；`content/`（`_admonitions.scss`、`_code.scss`、`_images.scss`、`_margin.scss`、`_notebooks.scss`、`_quotes.scss`）；`extensions/`（`_comments.scss`、`_myst-nb.scss`、`_sphinx-design.scss`、`_sphinx-tabs.scss`、`_sphinx-togglebutton.scss`、`_thebe.scss`）；`sections/`（`_announcement.scss`、`_article-container.scss`、`_article.scss`、`_footer-article.scss`、`_footer-content.scss`、`_header-article.scss`、`_header-primary.scss`、`_sidebar-primary.scss`、`_sidebar-secondary.scss`）。
- F-183: 翻译键全表（22 项）：`By the`、`By`、`Contents`、`Copyright`、`Download notebook file`、`Download source file`、`Download this page`、`Edit this page`、`Fullscreen mode`、`Last updated on`、`Launch`、`Open an issue`、`Print to PDF`、`Source repository`、`Sphinx Book Theme`、`Theme by the`、`Toggle navigation`、`next page`、`open issue`、`previous page`、`repository`、`suggest edit`。
- F-184: 翻译函数由 `get_translation(MESSAGE_CATALOG_NAME)` 获取；`buttons.html` 中文本经 `translate()` 处理。
- F-185: 静态资源输出：CSS `styles/sphinx-book-theme.css` 与 JS `scripts/sphinx-book-theme.js` 均由 webpack 编译（SCSS / `index.js` 及依赖）产出。
