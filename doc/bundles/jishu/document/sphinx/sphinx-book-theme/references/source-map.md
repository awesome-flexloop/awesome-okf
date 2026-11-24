---
type: Reference
title: "源码路径映射"
description: "sphinx-book-theme 源码、主题模板、SCSS、测试与文档页的路径索引，按“想改什么/想查什么”组织"
tags: [sphinx, theme, reference, source-map, templates, scss]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-repo
    resource: https://github.com/executablebooks/sphinx-book-theme
    title: sphinx-book-theme GitHub Repository
  - id: sbt-local
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme
    title: 本地源码快照（1.5.0.dev）
---

# 源码路径映射

根路径约定：`<repo>` 指 `external/libs/docs/sphinx-contrib/sphinx-book-theme`。

## Python 模块

| 想查/想改 | 路径 | 关键符号 |
|-----------|------|---------|
| 主题入口、事件注册 | `src/sphinx_book_theme/__init__.py` | `setup`、`add_metadata_to_page`、`hash_html_assets`、`update_navbar_defaults`、`update_general_config`、`update_templates` |
| 版本号 | `src/sphinx_book_theme/__init__.py` | `__version__ = "1.5.0.dev"` |
| `{margin}` 指令 | `src/sphinx_book_theme/directives.py` | `Margin(Sidebar)` |
| 边注节点与 visitor | `src/sphinx_book_theme/nodes.py` | `SideNoteNode`、`visit_SideNoteNode`、`depart_SideNoteNode` |
| 脚注转边注 | `src/sphinx_book_theme/_transforms.py` | `HandleFootnoteTransform` |
| 下载/全屏/仓库信息 | `src/sphinx_book_theme/header_buttons/__init__.py` | `as_bool`、`get_repo_parts`、`get_repo_url`、`prep_header_buttons`、`add_header_buttons`、`update_sourcename`、`update_context_with_repository_info` |
| 源码/编辑/issue 按钮 | `src/sphinx_book_theme/header_buttons/source.py` | `add_source_buttons` |
| Binder/Colab/Thebe 按钮 | `src/sphinx_book_theme/header_buttons/launch.py` | `add_launch_buttons`、`_is_notebook`、`_get_branch` |
| 兼容工具 | `src/sphinx_book_theme/_compat.py` | `findall` |
| 翻译编译 | `src/sphinx_book_theme/_compile_translations.py` | — |

## 主题模板

根路径：`src/sphinx_book_theme/theme/sphinx_book_theme/`。

| 想查/想改 | 路径 | 说明 |
|-----------|------|------|
| 主题声明与默认选项 | `theme.conf` | `inherit`、`sidebars`、`stylesheet`、`[options]` |
| 页面骨架 | `layout.html` | 覆盖 `docs_navbar`、`docs_main`、`docs_body` |
| 正文工具条 | `components/article-header-buttons.html` | 遍历 `header_buttons` |
| 全书目录 | `components/sbt-sidebar-nav.html` | `generate_toctree_html` |
| 页内目录 | `components/page-toc.html` | 右侧栏 |
| 作者/版权/更新 | `components/author.html`、`components/extra-footer.html` | 页脚组件 |
| 主/次侧栏开关 | `components/toggle-primary-sidebar.html`、`components/toggle-secondary-sidebar.html` | 移动端 |
| 内容页脚 | `sections/footer-content.html` | 遍历 `theme_footer_content_items` |
| 按钮宏 | `macros/buttons.html` | `render_link_button`、`render_js_button`、`render_button_group` |
| 静态图片 | `static/images/logo_*.svg` | Binder/JupyterHub/Colab/Deepnote/JupyterLite |
| webpack 宏 | `static/sbt-webpack-macros.html` | 构建期注入 |

## 样式与脚本

| 想查/想改 | 路径 |
|-----------|------|
| SCSS 入口 | `src/sphinx_book_theme/assets/styles/index.scss` |
| 变量与 mixin | `assets/styles/abstracts/_variables.scss`、`_mixins.scss` |
| 基础排版/打印 | `assets/styles/base/_base.scss`、`_print.scss`、`_typography.scss` |
| 组件样式 | `assets/styles/components/_back-to-top.scss`、`_icon-links.scss`、`_logo.scss`、`_search.scss` |
| 内容样式 | `assets/styles/content/_admonitions.scss`、`_code.scss`、`_images.scss`、`_margin.scss`、`_notebooks.scss`、`_quotes.scss` |
| 扩展样式 | `assets/styles/extensions/_myst-nb.scss`、`_sphinx-design.scss`、`_sphinx-tabs.scss`、`_sphinx-togglebutton.scss`、`_thebe.scss`、`_comments.scss` |
| 分区样式 | `assets/styles/sections/_announcement.scss`、`_article.scss`、`_footer-*.scss`、`_header-*.scss`、`_sidebar-*.scss` |
| JS 入口 | `assets/scripts/index.js` |
| 翻译源 | `assets/translations/` |
| 编译产物 | `theme/sphinx_book_theme/static/`（不入 git） |

## 构建与配置

| 想查/想改 | 路径 | 关键内容 |
|-----------|------|---------|
| 构建后端/依赖/entry point | `pyproject.toml` | `sphinx-theme-builder`、`pydata-sphinx-theme==0.23.0`、`sphinx>=8.2`、`requires-python>=3.11` |
| webpack 配置 | `webpack.config.js` | SCSS/JS 打包 |
| 前端依赖 | `package.json` | Node 工具链 |
| 测试配置 | `pyproject.toml` 的 `[tool.pytest.ini_options]` | warning 过滤、testpaths |
| tox 环境 | `tox.ini` | `compile` 等 |
| CI | `.github/workflows/tests.yml`、`publish.yml` | 测试与发布 |

## 测试

| 想查/想改 | 路径 |
|-----------|------|
| 构建测试 | `tests/test_build.py` |
| 翻译测试 | `tests/test_locale_convert.py` |
| fixture | `tests/conftest.py` |
| 最小站点 | `tests/sites/base/`、`tests/sites/notitle/`、`tests/sites/parallel-build/`、`tests/sites/base/titles/` |
| HTML 回归快照 | `tests/test_build/*.html` |
| 按钮快照 | `tests/test_build/header__launch-buttons--*.html`、`header__repo-buttons--*.html` |

## 文档页映射

| 文档主题 | 源文件 |
|----------|--------|
| 首页 | `docs/index.md` |
| 快速开始 | `docs/tutorials/get-started.md` |
| 内容块/边注 | `docs/content/content-blocks.md` |
| Notebook | `docs/content/notebooks.md` |
| 在线启动 | `docs/content/launch.md` |
| 页面分区 | `docs/sections/index.md`、`header.md`、`sidebar-primary.md`、`sidebar-secondary.md`、`footer.md`、`footer-content.md`、`announcements.md` |
| 组件 | `docs/components/logo.md`、`icon-links.md`、`source-files.md`、`download.md`、`custom-css.md` |
| 参考元素 | `docs/reference/special-theme-elements.md`、`extensions.md`、`notebooks.md`、`thebe.md`、`blog.md`、`comments.md`、`api-numpy.md` |
| 贡献指南 | `docs/contributing/index.md`、`architecture.md`、`setup.md`、`style.md`、`subthemes.md`、`tests.md`、`translate.md`、`versions.md` |
| 变更日志 | `CHANGELOG.md`、`docs/changelog.md` |

## 按问题定位

| 现象 | 先看 |
|------|------|
| 页面没有页眉 | `layout.html` 的 `docs_navbar` block；`theme_navbar_*` 是否为空 |
| 左侧目录不展开 | `theme.conf` 的 `show_navbar_depth`；`sbt-sidebar-nav.html` |
| 页眉按钮不出现 | `header_buttons/*.py`；对应 `use_*` 开关；是否有 `repository_url` |
| 边注位置错 | `_transforms.py` 的嵌套复制逻辑；`_margin.scss` |
| 样式没更新 | `hash_html_assets`；是否重新 `stb compile`；浏览器缓存 |
| 子主题没样式 | `theme.conf` 的 `stylesheet` 是否包含父主题 CSS |
| 翻译不生效 | `add_message_catalog`；`static/locales` 是否编译 |
| 测试快照大面积失败 | 模板/按钮结构是否变化；不要盲目 `--force-regen` |

## 相关概念

- [主题骨架与构建链](../concepts/02-theme-architecture.md)
- [页眉按钮机制](../concepts/05-header-buttons.md)
- [主题选项速查](theme-options-reference.md)
