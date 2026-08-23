---
type: spec
title: sphinx-book-theme 源码事实采集
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
sources:
- src/sphinx_book_theme/__init__.py
- src/sphinx_book_theme/directives.py
- src/sphinx_book_theme/nodes.py
- src/sphinx_book_theme/_transforms.py
- src/sphinx_book_theme/_compat.py
- src/sphinx_book_theme/header_buttons/__init__.py
- src/sphinx_book_theme/header_buttons/launch.py
- src/sphinx_book_theme/header_buttons/source.py
- src/sphinx_book_theme/theme/sphinx_book_theme/theme.conf
- src/sphinx_book_theme/theme/sphinx_book_theme/layout.html
- "src/sphinx_book_theme/theme/sphinx_book_theme/components/*.html"
- src/sphinx_book_theme/theme/sphinx_book_theme/macros/buttons.html
- src/sphinx_book_theme/assets/scripts/index.js
- src/sphinx_book_theme/assets/styles/ (SCSS files)
- pyproject.toml
description: sphinx-book-theme 源码事实清单
tags:
- sphinx-book-theme
- spec
- facts
stale_after: '2027-08-23'
---

# sphinx-book-theme 源码事实采集（零推断）

## 项目元数据

- F-001: 项目名称 sphinx-book-theme，版本号 1.5.0.dev（`__init__.py:27`）
- F-002: 项目描述 "A clean book theme for scientific explanations and documentation with Sphinx"（`pyproject.toml:36`）
- F-003: 构建系统使用 sphinx-theme-builder >= 0.2.0a7，build-backend 为 "sphinx_theme_builder"（`pyproject.toml:2-3`）
- F-004: 构建配置指定 Node.js 版本为 20.9.0，theme-name 为 "sphinx_book_theme"，额外编译静态资源包含 "locales/"（`pyproject.toml:5-10`）
- F-005: 要求 Python >= 3.11（`pyproject.toml:40`）
- F-006: 核心依赖：sphinx>=8.2, pydata-sphinx-theme==0.20.0（`pyproject.toml:41-44`）
- F-007: 开发状态分类为 "Development Status :: 4 - Beta"（`pyproject.toml:53`）
- F-008: 许可证为 BSD License（`pyproject.toml:57`）
- F-009: 入口点注册为 sphinx.html_themes: sphinx_book_theme = "sphinx_book_theme"（`pyproject.toml:97-98`）
- F-010: 项目维护者为 Executable Books Team（`pyproject.toml:48-49`）
- F-011: 文档地址 https://sphinx-book-theme.readthedocs.io/，仓库地址 https://github.com/executablebooks/sphinx-book-theme（`pyproject.toml:100-102`）

## 主题配置（theme.conf）

- F-012: 主题继承自 pydata_sphinx_theme（`theme.conf:2` inherit = pydata_sphinx_theme）
- F-013: Pygments 代码高亮样式为 tango（`theme.conf:3`）
- F-014: 默认侧边栏组件顺序：navbar-logo.html, icon-links.html, search-button-field.html, sbt-sidebar-nav.html（`theme.conf:4`）
- F-015: 主样式表路径 styles/sphinx-book-theme.css（`theme.conf:5`）
- F-016: 公告栏 announcement 默认空（`theme.conf:9`）
- F-017: 次级侧边栏默认组件 secondary_sidebar_items = page-toc.html（`theme.conf:12`）
- F-018: 目录标题 toc_title 默认 "Contents"（`theme.conf:13`）
- F-019: 文章头部左侧组件 article_header_start = toggle-primary-sidebar.html（`theme.conf:16`）
- F-020: 文章头部右侧组件 article_header_end = article-header-buttons.html（`theme.conf:17`）
- F-021: 下载按钮 use_download_button 默认 True（`theme.conf:18`）
- F-022: 全屏按钮 use_fullscreen_button 默认 True（`theme.conf:19`）
- F-023: 问题按钮 use_issues_button 默认 False（`theme.conf:20`）
- F-024: 源码按钮 use_source_button 默认 False（`theme.conf:21`）
- F-025: 仓库按钮 use_repository_button 默认 False（`theme.conf:22`）
- F-026: use_edit_page_button 继承自 pydata-sphinx-theme（`theme.conf:23` 注释说明）
- F-027: 文档路径 path_to_docs 默认空（`theme.conf:26`）
- F-028: 仓库URL repository_url 默认空（`theme.conf:27`）
- F-029: 仓库分支 repository_branch 默认空（`theme.conf:28`）
- F-030: 仓库提供商 repository_provider 默认空（`theme.conf:29`）
- F-031: 启动按钮配置 launch_buttons 默认空字典 {}（`theme.conf:30`）
- F-032: 导航栏各位置（navbar_start/center/end/persistent）默认清空（`theme.conf:34-37`），覆盖 PST 默认值
- F-033: 首页是否在目录中 home_page_in_toc 默认 False（`theme.conf:40`）
- F-034: 导航栏显示深度 show_navbar_depth 默认 1（`theme.conf:41`）
- F-035: 导航栏最大深度 max_navbar_depth 默认 4（`theme.conf:42`）
- F-036: 导航栏折叠 collapse_navbar 默认 False（`theme.conf:43`）
- F-037: 额外页脚 extra_footer 默认空（`theme.conf:46`）
- F-038: 页脚内容项 footer_content_items = author.html, copyright.html, last-updated.html, extra-footer.html（`theme.conf:47`）
- F-039: 页脚首尾位置 footer_start/footer_end 默认清空（`theme.conf:50-51`），覆盖 PST 默认值
- F-040: 边注功能 use_sidenotes 默认 False（`theme.conf:54`）
- F-041: 已弃用配置项 expand_toc_sections 默认空列表（`theme.conf:57`）

## 扩展入口（setup 函数）

- F-042: `get_html_theme_path()` 返回 Path 对象，指向 theme/sphinx_book_theme/ 目录（`__init__.py:35-39`）
- F-043: `setup(app)` 注册主题路径 app.add_html_theme("sphinx_book_theme", theme_dir)（`__init__.py:212-213`）
- F-044: setup 中添加 JS 文件 scripts/sphinx-book-theme.js（`__init__.py:214`）
- F-045: 翻译目录位于 static/locales，消息目录名 MESSAGE_CATALOG_NAME = "booktheme"（`__init__.py:32,217-218`）
- F-046: setup 连接的 builder-inited 事件回调：update_mode_thebe_config、check_deprecation_keys、update_sourcename、update_context_with_repository_info（`__init__.py:221-224`）
- F-047: setup 连接的 html-page-context 事件回调：add_metadata_to_page、hash_html_assets、update_templates（默认优先级）（`__init__.py:225-227`）
- F-048: setup 中调用 update_general_config(app, app.config) 立即设置配置（`__init__.py:233`）
- F-049: setup 同时连接 config-inited 事件到 update_general_config（`__init__.py:237`），原因是主题在使用前立即初始化而扩展先初始化
- F-050: SideNoteNode 通过 SideNoteNode.add_node(app) 注册（`__init__.py:240`）
- F-051: 头部按钮事件顺序：prep_header_buttons（默认优先级）→ add_launch_buttons（priority=501）→ add_source_buttons（priority=501）→ add_header_buttons（priority=501）（`__init__.py:243-247`）
- F-052: 注册自定义指令 "margin" → Margin 类（`__init__.py:250`）
- F-053: 注册 Post-Transform：HandleFootnoteTransform（`__init__.py:253`）
- F-054: setup 返回 parallel_read_safe=True, parallel_write_safe=True（`__init__.py:255-257`）

## 事件处理函数

### add_metadata_to_page

- F-055: `add_metadata_to_page` 处理 root_doc/master_doc 兼容（Sphinx 4.x 重命名）（`__init__.py:45-48`）
- F-056: 设置 context["root_title"] 为根文档标题文本（`__init__.py:48`）
- F-057: 设置 context["pagetitle"] 为当前页标题文本（`__init__.py:51-53`）
- F-058: 生成页面描述：遍历 doctree 中的 section，拼接文本取前160字符（`__init__.py:56-61`）
- F-059: 若 app.config.author != "unknown"，设置 context["author"]（`__init__.py:64-65`）
- F-060: 将翻译函数 translation 注入 context["translate"]（`__init__.py:68-69`）
- F-061: 若用户未设置 search_bar_text，默认设置为 translation("Search") + "..."（`__init__.py:72-74`）

### hash_html_assets

- F-062: `_gen_hash(path)` 使用 hashlib.sha1 计算文件内容哈希，使用 @lru_cache 缓存（`__init__.py:77-79`）
- F-063: `hash_assets_for_files` 为 CSS/JS 资源添加 ?digest={hash} 参数以实现缓存清除（`__init__.py:82-118`）
- F-064: hash_assets_for_files 根据文件后缀判断资源类型：.css → css_files，否则 → script_files（`__init__.py:95`）
- F-065: hash_html_assets 默认哈希 scripts/sphinx-book-theme.js（`__init__.py:126`）
- F-066: 仅当 html_theme == "sphinx_book_theme" 时才哈希 CSS 文件 styles/sphinx-book-theme.css，避免影响子主题（`__init__.py:130-131`）

### update_mode_thebe_config

- F-067: `update_mode_thebe_config` 检查 launch_buttons.thebe 为 True 时的配置（`__init__.py:135-166`）
- F-068: 若启用 thebe 但未添加 sphinx_thebe 扩展，发出警告（`__init__.py:141-145`）
- F-069: thebe_config 中若未设置 repository_url，自动从主题配置填充（`__init__.py:157-158`）
- F-070: thebe_config 中若未设置 repository_branch，自动填充（默认为 "master"，非 "main"）（`__init__.py:159-164`）

### check_deprecation_keys

- F-071: `check_deprecation_keys` 检查已弃用配置键，目前仅 "single_page"（`__init__.py:169-179`）
- F-072: 默认日志类型 DEFAULT_LOG_TYPE = "sphinxbooktheme"（`__init__.py:31`）

### update_general_config

- F-073: `update_general_config` 将 theme/sphinx_book_theme/components 目录添加到 templates_path（`__init__.py:182-185`）

### update_templates

- F-074: `update_templates` 处理 theme_footer_content_items 模板名称分割（`__init__.py:188-207`）
- F-075: 支持逗号分隔的模板名称字符串自动拆分（`__init__.py:199-202`）
- F-076: 自动为无后缀模板名添加 ".html" 后缀（`__init__.py:205-207`）

### update_sourcename

- F-077: `update_sourcename` 将 html_sourcelink_suffix 默认设为空字符串，覆盖 Sphinx 默认的 .txt（`header_buttons/__init__.py:125-133`）
- F-078: 判断条件为用户未手动配置 html_sourcelink_suffix（使用 config_provided_by_user 检测）（`header_buttons/__init__.py:132`）

### update_context_with_repository_info

- F-079: `update_context_with_repository_info` 从 repository_url 配置推断 provider 信息并注入 html_context（`header_buttons/__init__.py:136-190`）
- F-080: 默认分支为 "main"（`header_buttons/__init__.py:156`），注意与 thebe_config 的默认分支 "master" 不同
- F-081: 通过 rsplit("/", 2) 从 URL 解析 provider_url/org/repo（`header_buttons/__init__.py:159`）
- F-082: 支持的 provider 列表：bitbucket、github、gitlab（`header_buttons/__init__.py:162-166`）
- F-083: provider 自动推断通过检查 provider_url 是否包含默认域名实现（`header_buttons/__init__.py:169-173`）
- F-084: 无法识别 provider 时抛出 SphinxError（`header_buttons/__init__.py:176-180`）
- F-085: 注入 html_context 的键格式为 {provider}_user、{provider}_repo、{provider}_version、{provider}_url 及 doc_path（`header_buttons/__init__.py:183-189`）

## 工具函数

- F-086: `as_bool(var)` 函数将字符串 "true"/"false" 转为布尔值，布尔值直接返回，None/其他返回 False（`header_buttons/__init__.py:15-27`）
- F-087: `get_repo_parts(context)` 遍历 ["github", "bitbucket", "gitlab"]，从 context 中提取 provider_url、source_user、source_repo、provider（`header_buttons/__init__.py:30-37`）
- F-088: `get_repo_url(context)` 调用 get_repo_parts，拼接 repo_url = f"{provider_url}/{user}/{repo}"（`header_buttons/__init__.py:40-44`）
- F-089: `findall(node, *args, **kwargs)` 兼容函数：优先使用 node.findall（docutils v0.18+），回退到 node.traverse（`_compat.py:5-8`）

## Margin 指令

- F-090: Margin 类继承自 docutils.parsers.rst.directives.body.Sidebar（`directives.py:1,4`）
- F-091: Margin 指令 optional_arguments = 1，required_arguments = 0（`directives.py:7-8`）
- F-092: Margin.run() 若无参数则设置 self.arguments = [""]（`directives.py:12-13`）
- F-093: Margin.run() 调用 super().run() 后，为节点添加 "margin" CSS 类（`directives.py:14-15`）
- F-094: 若无标题参数（self.arguments 为空列表设置为 [""]），移除第一个子节点（title 节点）（`directives.py:18-19`）

## SideNoteNode 节点

- F-095: SideNoteNode 继承自 docutils.nodes.Element（`nodes.py:6`）
- F-096: SideNoteNode.__init__ 调用 super().__init__("", **attributes)，rawsource 为空字符串（`nodes.py:10-11`）
- F-097: SideNoteNode.add_node(app) 注册 HTML visitor：html=(visit_SideNoteNode, depart_SideNoteNode)，override=True（`nodes.py:13-16`）
- F-098: visit_SideNoteNode 根据 tagid 中是否包含 "marginnote" 选择输出 class：marginnote-label 或 margin-toggle（`nodes.py:19-27`）
- F-099: visit_SideNoteNode 中 sidenote 类型（tagid 含 "sidenote"）额外输出 <span> 开始标签（`nodes.py:26-27`）
- F-100: depart_SideNoteNode 中 sidenote 类型输出 </span>，所有类型输出 </label> 和隐藏的 <input type='checkbox'> 元素（`nodes.py:30-37`）
- F-101: checkbox 元素的 id/name 属性与 label 的 for 属性一致，实现 CSS 纯交互（点击切换）（`nodes.py:35-36`）

## HandleFootnoteTransform

- F-102: HandleFootnoteTransform 继承自 SphinxPostTransform（`_transforms.py:10`）
- F-103: default_priority = 1，formats = ("html",)（`_transforms.py:13-14`）
- F-104: run() 首先检查 theme_options.get("use_sidenotes", False)，若为 False 则直接返回 None（`_transforms.py:17-19`）
- F-105: 遍历所有 footnote_reference 节点，匹配对应的 footnote 节点（通过 backrefs[0] == ids[0]）（`_transforms.py:23-32`）
- F-106: footnote 节点的第二个子节点（children[1]）为内容文本（`_transforms.py:35`）
- F-107: 若脚注内容以 "{-}" 开头，则创建 marginnote（无边注编号），移除 "{-}" 标记，CSS 类为 "marginnote"（`_transforms.py:42-51`）
- F-108: 普通脚注创建 sidenote（保留编号），生成 superscript 标签，CSS 类为 "sidenote"（`_transforms.py:52-61`）
- F-109: marginnote 的 tagid 格式为 "marginnote-role-{label}"，sidenote 的 tagid 格式为 "sidenote-role-{label}"（`_transforms.py:51,60`）
- F-110: 嵌套场景处理：若引用位于 admonition 等容器内，复制内容节点并插入到容器之前，原位置保留副本并添加 "d-n"（display:none）CSS 类（`_transforms.py:67-81`）
- F-111: 嵌套检测循环：向上遍历父节点直到遇到 section 或 document 节点（`_transforms.py:70-72`）
- F-112: 若父节点是 paragraph 或 footnote，则继续向上查找；否则执行 replace_self 操作（`_transforms.py:74-77`）
- F-113: 最后从原父节点移除 footnote 节点（`_transforms.py:85-86`）

## 头部按钮系统（prep/add_header_buttons）

- F-114: prep_header_buttons 在 context 中初始化空列表 header_buttons = []（`header_buttons/__init__.py:47-49`）
- F-115: add_header_buttons 添加下载按钮组和全屏按钮（`header_buttons/__init__.py:52-122`）
- F-116: 下载按钮组仅当 use_download_button=True 且存在 page_source_suffix 时添加（`header_buttons/__init__.py:62`）
- F-117: 下载按钮组包含：ipynb 下载（若存在 ipynb_source）、源文件下载（.sourcename 后缀）、PDF 打印（window.print()）（`header_buttons/__init__.py:66-98`）
- F-118: ipynb_source 来自 context，由 add_launch_buttons 中 MD 笔记本转换时设置（`header_buttons/__init__.py:66-76; launch.py:67-82`）
- F-119: PDF 按钮使用 javascript 类型，执行 window.print()（`header_buttons/__init__.py:89-98`）
- F-120: 下载按钮组 type="group"，tooltip 为 "Download this page"，icon 为 "fas fa-download"（`header_buttons/__init__.py:101-109`）
- F-121: 全屏按钮仅当 use_fullscreen_button=True 时添加（`header_buttons/__init__.py:112`）
- F-122: 全屏按钮 type="javascript"，调用 toggleFullScreen()，icon 为 "fas fa-expand"，classes 为 "pst-navbar-icon"（`header_buttons/__init__.py:113-122`）

## 启动按钮（launch.py）

- F-123: add_launch_buttons 函数签名接受 app, pagename, templatename, context, doctree（`launch.py:22-28`）
- F-124: 跳过条件：无 launch_buttons 配置、非笔记本页面、未配置任何启动提供者（binderhub_url/jupyterhub_url/thebe/colab_url/jupyterlite_url）（`launch.py:47-61`）
- F-125: _is_notebook 判断逻辑：metadata 中存在 kernelspec 或 page_source_suffix 包含 "ipynb"（`launch.py:252-262`）
- F-126: MD 文件笔记本处理：从 jupyter_execute 目录复制 .ipynb 文件到 _sources 目录，设置 context["ipynb_source"]（`launch.py:67-82`）
- F-127: notebook_interface 支持 "classic"（tree 路径前缀）和 "jupyterlab"（lab/tree 路径前缀），默认 "classic"（`launch.py:94-102`）
- F-128: 若非 .ipynb 文件但同名 .ipynb 存在，自动切换 extension 为 .ipynb（`launch.py:106-107`）
- F-129: Binder URL 构建：标准 GitHub/GitLab 使用 v2/gh/{org}/{repo}/{branch} 或 v2/gl/{org}%2F{repo}/{branch} 格式，其他 provider 使用 v2/git/{quote(repo_url)}/{branch}（`launch.py:128-138`）
- F-130: Binder URL 添加 urlpath 参数：{ui_pre}/{path_rel_repo}（`launch.py:139`）
- F-131: JupyterHub URL 使用 /hub/user-redirect/git-pull?repo=...&urlpath=...&branch=...（`launch.py:150-158`）
- F-132: Colab 仅支持 GitHub provider，URL 格式：{colab_url}/github/{org}/{repo}/blob/{branch}/{path_rel_repo}（`launch.py:168-181`）
- F-133: Deepnote 仅支持 GitHub provider，URL 格式：{deepnote_url}/launch?url=https%3A%2F%2Fgithub.com%2F{org}%2F{repo}%2Fblob%2F{branch}%2F{path_rel_repo}（`launch.py:183-197`）
- F-134: JupyterLite URL 格式：{jupyterlite_url}?path={jl_rel_repo}，支持 jupyterlite_ext 配置扩展名（`launch.py:199-211`）
- F-135: Thebe 按钮 type="javascript"，调用 initThebeSBT()，设置 context["use_thebe"] = True（`launch.py:214-225`）
- F-136: 所有启动按钮封装在 type="group" 中，tooltip 为 "Launch interactive content"，icon 为 "fas fa-rocket"（`launch.py:228-236`）
- F-137: 各平台图标路径：Binder→_static/images/logo_binder.svg, JupyterHub→_static/images/logo_jupyterhub.svg, Colab→_static/images/logo_colab.png, Deepnote→_static/images/logo_deepnote.svg, JupyterLite→_static/images/logo_jupyterlite.svg（`launch.py:145,163,178,194,208`）
- F-138: _get_branch 默认分支为 "master"（`launch.py:265-268`）

## 源码按钮（source.py）

- F-139: add_source_buttons 管理四种仓库相关按钮：use_repository_button、use_source_button、use_edit_page_button、use_issues_button（`source.py:23-28`）
- F-140: 四种按钮值均通过 as_bool() 转换（`source.py:29-30`）
- F-141: use_repository_button：链接到仓库首页，icon 使用 fab fa-{provider}（`source.py:36-48`）
- F-142: use_source_button：调用 context["get_edit_provider_and_url"]() 获取 edit_url，将 /edit/ 替换为 /blob/ 并添加 ?plain=1（GitHub/GitLab），Bitbucket 移除 ?mode=edit（`source.py:50-71`）
- F-143: use_edit_page_button：直接使用 edit_url（`source.py:73-85`）
- F-144: use_issues_button：仅支持 GitHub/GitLab，预填 issue 标题为 "Issue on page /{pagename}.html"（`source.py:87-105`）
- F-145: 多按钮时使用 type="group" 下拉菜单，单按钮时清空 text 只显示图标（`source.py:108-121`）

## HTML 模板

### layout.html

- F-146: layout.html 继承 pydata_sphinx_theme/layout.html（`layout.html:1`）
- F-147: 重写 docs_main 块：在 super() 前添加 <div class="sbt-scroll-pixel-helper"></div> 用于滚动检测（`layout.html:4-8`）
- F-148: 重写 docs_body 块：添加打印专用目录区域 #jb-print-docs-body（`layout.html:11-30`）
- F-149: 打印目录区域包含 .onlyprint 类的 h1 和 page-toc 导航（`layout.html:13-28`）

### article-header-buttons.html

- F-150: article-header-buttons.html 从 macros/buttons.html 导入 render_funcs（`article-header-buttons.html:1`）
- F-151: 遍历 header_buttons 列表，按 button.type 分发到对应渲染宏（`article-header-buttons.html:4-8`）
- F-152: 额外包含 theme-switcher.html、search-button.html、toggle-secondary-sidebar.html（`article-header-buttons.html:12-14`）

### macros/buttons.html

- F-153: render_inner_html 宏渲染图标和文本：fa 图标使用 <i> 标签，其他图标使用 <img> 标签（`buttons.html:2-14`）
- F-154: render_link_button 宏渲染 <a target="_blank"> 链接按钮，支持 tooltip、data-bs-toggle、data-bs-placement（`buttons.html:17-25`）
- F-155: render_js_button 宏渲染 <button onclick="..."> JavaScript 按钮（`buttons.html:28-36`）
- F-156: render_button_group 宏渲染 Bootstrap 5 下拉菜单（dropdown），子按钮使用 dropdown-item 类（`buttons.html:39-55`）
- F-157: render_funcs 字典映射 "group"→render_button_group、"javascript"→render_js_button、"link"→render_link_button（`buttons.html:57-61`）

### sbt-sidebar-nav.html

- F-158: sbt-sidebar-nav.html 渲染主导航侧边栏，使用 <nav class="bd-links bd-docs-nav">（`sbt-sidebar-nav.html:1`）
- F-159: 若 theme_home_page_in_toc == True，在顶部添加首页链接（`sbt-sidebar-nav.html:3-12`）
- F-160: 使用 generate_toctree_html() 生成目录树，参数：startdepth=0, kind="sidebar", maxdepth=theme_max_navbar_depth, collapse=theme_collapse_navbar, includehidden=True, titles_only=True, show_nav_level=theme_show_navbar_depth（`sbt-sidebar-nav.html:15-22`）

### 其他组件模板

- F-161: toggle-primary-sidebar.html 渲染主侧边栏切换按钮
- F-162: toggle-secondary-sidebar.html 渲染次级侧边栏切换按钮
- F-163: page-toc.html 渲染页面内目录
- F-164: author.html 渲染作者信息
- F-165: extra-footer.html 渲染额外页脚
- F-166: footer-content.html 渲染页脚内容区域（sections/ 目录）
- F-167: sbt-webpack-macros.html 为 webpack 宏模板（static/ 目录）

## JavaScript 功能（index.js）

- F-168: sbRunWhenDOMLoaded(cb) 函数：DOM 就绪后执行回调，兼容 addEventListener 和 attachEvent（`index.js:10-20`）
- F-169: toggleFullScreen() 函数：切换全屏模式，兼容 webkit 前缀（Safari）（`index.js:29-50`）
- F-170: initTocHide() 使用 IntersectionObserver 实现两个功能（`index.js:66-138`）：
  - 当 margin/sidenote 内容进入视口时隐藏次级侧边栏（TOC）
  - 通过 sbt-scroll-pixel-helper 检测滚动，添加/移除 body.scrolled 类
- F-171: TOC 隐藏触发的选择器类：marginnote, sidenote, margin, margin-caption, full-width, sidebar, popout（`index.js:110-118`）
- F-172: 选择器同时支持三种命名变体：.{cls}、.tag_{cls}、.{cls_with_underscores}、.tag_{cls_with_underscores}（`index.js:120-129`）
- F-173: TOC 隐藏的 rootMargin 为 "0px 0px -33% 0px"（元素顶部进入屏幕上2/3时触发）（`index.js:106`）
- F-174: initThebeSBT() 函数：在 h1 后插入 thebe-launch-button，调用 sphinx-thebe 提供的 initThebe()（`index.js:143-156`）
- F-175: addNoPrint() 函数：为头部、侧边栏、页脚等导航元素添加 noprint 类（`index.js:162-176`）
- F-176: addBlurToButtons() 函数：点击按钮后自动 blur() 以消除 tooltip 残留（`index.js:188-210`）
- F-177: fixSidebarToggle() 函数：在宽屏（>=992px）上阻止侧边栏切换按钮打开 dialog modal，改为切换 pst-sidebar-hidden 类（`index.js:217-242`）
- F-178: fixSidebarToggle 使用 capture phase（addEventListener 第三个参数 true）在 PST 处理之前拦截事件（`index.js:239`）
- F-179: 全局暴露的函数：window.initThebeSBT、window.toggleFullScreen（`index.js:181-182`）
- F-180: DOM 就绪时初始化：initTocHide、addNoPrint、addBlurToButtons、fixSidebarToggle（`index.js:247-250`）

## CSS/SCSS 样式架构

- F-181: 样式入口文件 assets/styles/index.scss，通过 JS import 引入（`index.js:3`）
- F-182: SCSS 目录结构：abstracts/（_mixins.scss, _variables.scss）、base/（_base.scss, _print.scss, _typography.scss）、components/（_back-to-top.scss, _icon-links.scss, _logo.scss, _search.scss）、content/（_admonitions.scss, _code.scss, _images.scss, _margin.scss, _notebooks.scss, _quotes.scss）、extensions/（_comments.scss, _myst-nb.scss, _sphinx-design.scss, _sphinx-tabs.scss, _sphinx-togglebutton.scss, _thebe.scss）、sections/（_announcement.scss, _article-container.scss, _article.scss, _footer-article.scss, _footer-content.scss, _header-article.scss, _header-primary.scss, _sidebar-primary.scss, _sidebar-secondary.scss）
- F-183: extensions/ 目录包含对第三方扩展的样式适配：myst-nb、sphinx-design、sphinx-tabs、sphinx-togglebutton、thebe、comments
- F-184: content/_margin.scss 处理边注/旁注样式
- F-185: base/_print.scss 处理打印样式

## 国际化与翻译

- F-186: 翻译 JSON 文件位于 assets/translations/jsons/ 目录
- F-187: 翻译键列表（从文件名提取）："By the", "By", "Contents", "Copyright", "Download notebook file", "Download source file", "Download this page", "Edit this page", "Fullscreen mode", "Last updated on", "Launch", "Open an issue", "Print to PDF", "Source repository", "Sphinx Book Theme", "Theme by the", "Toggle navigation", "next page", "open issue", "previous page", "repository", "suggest edit"
- F-188: 翻译函数通过 get_translation(MESSAGE_CATALOG_NAME) 获取（`__init__.py:68; header_buttons/__init__.py:12`）
- F-189: 按钮宏中所有文本通过 translate() 函数翻译（`buttons.html:9,13,20,31`）

## 静态资源

- F-190: 平台图标位于 static/images/：logo_binder.svg, logo_colab.png, logo_deepnote.svg, logo_jupyterhub.svg, logo_jupyterlite.svg
- F-191: CSS 输出路径 styles/sphinx-book-theme.css（通过 webpack 编译 SCSS）
- F-192: JS 输出路径 scripts/sphinx-book-theme.js（通过 webpack 编译 index.js 及其依赖）
