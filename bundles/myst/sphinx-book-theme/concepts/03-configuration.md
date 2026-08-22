---
type: concept
title: 03 - 配置系统详解
description: sphinx-book-theme 的完整配置项说明，包括主题选项、侧边栏组件、导航配置等
tags:
- sphinx-book-theme
- configuration
- html_theme_options
generated: 2026-08-23
status: stable
stale_after: 2027-08-23
sources:
- src/sphinx_book_theme/theme/sphinx_book_theme/theme.conf
- src/sphinx_book_theme/__init__.py
---

# 配置系统详解

sphinx-book-theme 的配置通过 Sphinx 的 `html_theme_options` 字典设置。配置项分为几类：仓库与源码、头部按钮、启动按钮、导航与侧边栏、内容功能、页脚。

## 仓库与源码配置

### repository_url

- **类型**：`str`
- **默认值**：`""`
- **说明**：仓库的完整URL，支持 GitHub、GitLab、Bitbucket。设置后，SBT 自动推断 provider、org、repo 信息注入 `html_context`（F-079-F-085）。

```python
html_theme_options = {
    "repository_url": "https://github.com/executablebooks/sphinx-book-theme",
}
```

### repository_branch

- **类型**：`str`
- **默认值**：`""`（按钮相关默认 "master"，仓库信息默认 "main"）
- **说明**：仓库分支名。空时，仓库URL推断默认 "main"（F-080），但Thebe配置和启动按钮默认 "master"（F-070、F-138）。建议显式设置以避免不一致。

```python
"repository_branch": "main",
```

### repository_provider

- **类型**：`str`
- **默认值**：`""`（自动推断）
- **说明**：强制指定仓库提供商。当使用自定义Git域名（如企业内部GitLab）时需要手动设置。支持的值：`"github"`、`"gitlab"`、`"bitbucket"`。

### path_to_docs

- **类型**：`str`
- **默认值**：`""`
- **说明**：文档目录相对于仓库根的路径。用于构建编辑链接和启动按钮URL。

```python
# 如果文档在仓库的 docs/ 目录下
"path_to_docs": "docs",
```

## 头部按钮配置

### use_download_button

- **类型**：`bool`
- **默认值**：`True`
- **说明**：显示下载按钮组，包括源文件下载、ipynb下载（如有）、PDF打印（F-116-F-120）。

### use_fullscreen_button

- **类型**：`bool`
- **默认值**：`True`
- **说明**：显示全屏切换按钮（F-121-F-122）。

### use_repository_button

- **类型**：`bool`
- **默认值**：`False`
- **说明**：显示仓库链接按钮。需要配置 `repository_url`（F-141）。

### use_source_button

- **类型**：`bool`
- **默认值**：`False`
- **说明**：显示查看当前页面源码的按钮。需要配置 `repository_url`（F-142）。GitHub/GitLab链接到 `/blob/` 页面并添加 `?plain=1` 参数确保显示源码而非渲染。

### use_edit_page_button

- **类型**：`bool`
- **默认值**：（继承 PST，默认 False）
- **说明**：显示在线编辑按钮。需要配置 `repository_url` 和 `path_to_docs`（F-143）。

### use_issues_button

- **类型**：`bool`
- **默认值**：`False`
- **说明**：显示提交Issue按钮，预填页面标题。仅支持 GitHub 和 GitLab（F-144）。Bitbucket 会发出警告。

## 启动按钮配置（launch_buttons）

`launch_buttons` 是一个嵌套字典，配置交互式计算平台的启动按钮（F-123-F-136）。

```python
html_theme_options = {
    "launch_buttons": {
        "binderhub_url": "https://mybinder.org",
        "colab_url": "https://colab.research.google.com",
        "notebook_interface": "jupyterlab",
    },
}
```

### binderhub_url

- **类型**：`str`
- **默认值**：不设置
- **说明**：BinderHub 服务URL。公共实例为 `https://mybinder.org`。支持GitHub/GitLab/通用Git仓库。

### jupyterhub_url

- **类型**：`str`
- **默认值**：不设置
- **说明**：JupyterHub 服务URL，使用 `git-pull` 方式自动拉取仓库。

### colab_url

- **类型**：`str`
- **默认值**：不设置
- **说明**：Google Colab URL，通常为 `https://colab.research.google.com`。仅支持GitHub仓库（F-132）。

### deepnote_url

- **类型**：`str`
- **默认值**：不设置
- **说明**：Deepnote URL。仅支持GitHub仓库（F-133）。

### jupyterlite_url

- **类型**：`str`
- **默认值**：不设置
- **说明**：JupyterLite 部署URL，可用于纯前端笔记本执行（F-134）。

### jupyterlite_ext

- **类型**：`str`
- **默认值**：使用源文件扩展名
- **说明**：JupyterLite 打开文件的扩展名（F-200）。

### thebe

- **类型**：`bool`
- **默认值**：`False`
- **说明**：启用 Thebe 在线代码执行。需要安装 `sphinx-thebe` 扩展并添加到 extensions 列表（F-067-F-068）。点击按钮在页面中直接运行代码块。

### notebook_interface

- **类型**：`str`
- **默认值**：`"classic"`
- **说明**：Binder/JupyterHub 打开的界面类型（F-094-F-102）。可选值：
  - `"classic"`：经典 Notebook 界面（路径前缀 `tree/`）
  - `"jupyterlab"`：JupyterLab 界面（路径前缀 `lab/tree/`）

## 导航与侧边栏配置

### home_page_in_toc

- **类型**：`bool`
- **默认值**：`False`
- **说明**：在主侧边栏顶部添加首页链接（F-159）。设为 True 时，侧边栏最顶部显示根文档标题链接。

### show_navbar_depth

- **类型**：`int`
- **默认值**：`1`
- **说明**：侧边栏导航默认展开的层级深度（F-160 中 `show_nav_level` 参数）。

### max_navbar_depth

- **类型**：`int`
- **默认值**：`4`
- **说明**：侧边栏导航的最大嵌套深度（F-160 中 `maxdepth` 参数）。

### collapse_navbar

- **类型**：`bool`
- **默认值**：`False`
- **说明**：是否折叠侧边栏的子导航项（F-160 中 `collapse` 参数）。设为 True 时，只展开当前页面的父级路径。

## 内容功能配置

### use_sidenotes

- **类型**：`bool`
- **默认值**：`False`
- **说明**：将脚注转换为边注/旁注（F-104）。启用后，标准脚注自动显示在右侧边距。在脚注内容前添加 `{-} ` 前缀创建无边注编号的边注。

```python
"use_sidenotes": True,
```

MyST 语法：
```markdown
正文内容[^1]

[^1]: 这是带编号的旁注（sidenote）

正文内容[^2]

[^2]: {-} 这是无边距编号的边注（marginnote）
```

### announcement

- **类型**：`str`
- **默认值**：`""`
- **说明**：页面顶部公告栏的 HTML 内容。

```python
"announcement": "<p>⚠️ 本文档正在建设中！</p>",
```

## 页脚配置

### extra_footer

- **类型**：`str`
- **默认值**：`""`
- **说明**：页脚区域的自定义 HTML 内容。

### footer_content_items

- **类型**：逗号分隔的模板名列表
- **默认值**：`"author.html, copyright.html, last-updated.html, extra-footer.html"`
- **说明**：页脚内容区域显示的组件（F-038、F-074-F-076）。

## 目录配置

### toc_title

- **类型**：`str`
- **默认值**：`"Contents"`
- **说明**：右侧页内目录（次级侧边栏）的标题文字（F-018）。

## 侧边栏组件位置

SBT 预设了各区域的组件，也可以通过 PST 的配置项自定义：

```python
html_theme_options = {
    # 主侧边栏组件
    "secondary_sidebar_items": ["page-toc.html"],

    # 文章头部
    "article_header_start": ["toggle-primary-sidebar.html"],
    "article_header_end": ["article-header-buttons.html"],
}
```

可用的 SBT 自定义组件：
- `article-header-buttons.html`：文章头部按钮容器（下载/启动/源码按钮）
- `sbt-sidebar-nav.html`：SBT 定制侧边栏导航（支持深度和折叠配置）
- `page-toc.html`：页内目录
- `toggle-primary-sidebar.html`：主侧边栏切换按钮
- `toggle-secondary-sidebar.html`：次级侧边栏切换按钮
- `author.html`：作者信息
- `extra-footer.html`：额外页脚

## 继承自 PST 的常用配置

由于 SBT 继承自 PST，以下 PST 配置项同样可用：

| 配置项 | 说明 |
|--------|------|
| `logo` | Logo配置（`image_light`/`image_dark`/`text`） |
| `icon_links` | 导航栏图标链接列表 |
| `show_toc_level` | 页内目录显示层级 |
| `navigation_depth` | 左侧导航深度（PST层面） |
| `pygments_light_style` | 亮色模式代码高亮样式 |
| `pygments_dark_style` | 暗色模式代码高亮样式 |

## 相关概念

- [主题概述](/concepts/00-introduction.md)
- [主题架构与PST继承](/concepts/02-theme-architecture.md)
- [头部按钮系统](/concepts/04-header-buttons.md)
- [Margin指令与边注旁注](/concepts/05-margin-sidenotes.md)
- [源码路径映射与配置速查](/references/sbt-source.md)
