---
type: Reference
title: sphinx-book-theme 源码路径映射与配置速查
description: 源码文件位置、核心配置项完整列表、指令/角色/事件速查
tags:
- sphinx-book-theme
- reference
- configuration
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- src/sphinx_book_theme/__init__.py
- src/sphinx_book_theme/theme/sphinx_book_theme/theme.conf
- pyproject.toml
---

# sphinx-book-theme 源码参考

## 源码路径映射

| 模块/文件 | 路径 | 职责 |
|-----------|------|------|
| 扩展入口 | `src/sphinx_book_theme/__init__.py` | setup()、事件回调、配置更新、资产哈希 |
| Margin指令 | `src/sphinx_book_theme/directives.py` | `margin` 指令定义 |
| SideNote节点 | `src/sphinx_book_theme/nodes.py` | SideNoteNode 及 HTML visitor |
| 脚注变换 | `src/sphinx_book_theme/_transforms.py` | HandleFootnoteTransform（脚注→边注） |
| 兼容层 | `src/sphinx_book_theme/_compat.py` | findall 兼容函数 |
| 按钮工具 | `src/sphinx_book_theme/header_buttons/__init__.py` | 通用按钮、仓库信息、sourcename处理 |
| 启动按钮 | `src/sphinx_book_theme/header_buttons/launch.py` | Binder/JupyterHub/Colab/Deepnote/JupyterLite/Thebe |
| 源码按钮 | `src/sphinx_book_theme/header_buttons/source.py` | 仓库/查看/编辑/Issue按钮 |
| 主题配置 | `src/sphinx_book_theme/theme/sphinx_book_theme/theme.conf` | 继承关系、默认选项、组件配置 |
| 布局模板 | `src/sphinx_book_theme/theme/sphinx_book_theme/layout.html` | 继承PST layout、添加滚动检测和打印TOC |
| 按钮宏 | `src/sphinx_book_theme/theme/sphinx_book_theme/macros/buttons.html` | link/js/group按钮渲染宏 |
| JS入口 | `src/sphinx_book_theme/assets/scripts/index.js` | 全屏、TOC隐藏、Thebe、打印、侧边栏修复 |
| SCSS入口 | `src/sphinx_book_theme/assets/styles/index.scss` | 样式总入口 |

## 配置项完整速查表

### 基本设置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `repository_url` | str | `""` | 仓库URL（GitHub/GitLab/Bitbucket） |
| `repository_branch` | str | `""` | 仓库分支，空时按钮默认"master"，仓库信息默认"main" |
| `repository_provider` | str | `""` | 强制指定provider，空时自动推断 |
| `path_to_docs` | str | `""` | 文档目录相对于仓库根的路径 |
| `announcement` | str | `""` | 公告栏HTML内容 |
| `use_sidenotes` | bool | `False` | 将脚注转为边注/旁注 |

### 头部按钮

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `use_download_button` | bool | `True` | 显示下载按钮组（源文件/ipynb/PDF） |
| `use_fullscreen_button` | bool | `True` | 显示全屏按钮 |
| `use_repository_button` | bool | `False` | 显示仓库链接按钮 |
| `use_source_button` | bool | `False` | 显示查看源码按钮 |
| `use_edit_page_button` | bool | （继承PST） | 显示建议编辑按钮 |
| `use_issues_button` | bool | `False` | 显示提交Issue按钮 |

### 启动按钮配置（launch_buttons 字典）

| 键 | 类型 | 说明 |
|----|------|------|
| `binderhub_url` | str | BinderHub URL（如 https://mybinder.org） |
| `jupyterhub_url` | str | JupyterHub URL |
| `colab_url` | str | Google Colab URL（如 https://colab.research.google.com） |
| `deepnote_url` | str | Deepnote URL |
| `jupyterlite_url` | str | JupyterLite 部署URL |
| `jupyterlite_ext` | str | JupyterLite文件扩展名（默认使用源文件扩展名） |
| `thebe` | bool | 启用Thebe在线代码执行 |
| `notebook_interface` | str | `"classic"` 或 `"jupyterlab"`，控制Binder/JupyterHub打开界面 |

### 导航栏配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `home_page_in_toc` | bool | `False` | 首页链接显示在侧边栏顶部 |
| `show_navbar_depth` | int | `1` | 侧边栏默认展开深度 |
| `max_navbar_depth` | int | `4` | 侧边栏最大深度 |
| `collapse_navbar` | bool | `False` | 是否折叠侧边栏子项 |

### 侧边栏组件

| 位置 | 默认组件 |
|------|---------|
| `sidebars`（主侧边栏） | navbar-logo.html, icon-links.html, search-button-field.html, sbt-sidebar-nav.html |
| `secondary_sidebar_items` | page-toc.html |
| `article_header_start` | toggle-primary-sidebar.html |
| `article_header_end` | article-header-buttons.html |
| `footer_content_items` | author.html, copyright.html, last-updated.html, extra-footer.html |

### 目录配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `toc_title` | str | `"Contents"` | 目录标题文字 |

### 页脚

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `extra_footer` | str | `""` | 额外页脚HTML |

## 指令与节点

| 名称 | 类型 | 说明 |
|------|------|------|
| `margin` | directive | 右侧边距内容，继承自 docutils Sidebar |
| `SideNoteNode` | node | 边注/旁注节点，生成label+checkbox纯CSS交互结构 |

## Post-Transform

| 名称 | 优先级 | 格式 | 说明 |
|------|--------|------|------|
| `HandleFootnoteTransform` | 1 | html | 将footnote转为sidenote/marginnote |

## 事件钩子

| 事件 | 回调 | 优先级 | 说明 |
|------|------|--------|------|
| `builder-inited` | update_mode_thebe_config | 默认 | Thebe配置更新 |
| `builder-inited` | check_deprecation_keys | 默认 | 弃用键检查 |
| `builder-inited` | update_sourcename | 默认 | html_sourcelink_suffix处理 |
| `builder-inited` | update_context_with_repository_info | 默认 | 仓库信息注入html_context |
| `config-inited` | update_general_config | 默认 | templates_path配置（双重调用） |
| `html-page-context` | add_metadata_to_page | 默认 | 页面元数据注入 |
| `html-page-context` | hash_html_assets | 默认 | 静态资源哈希缓存清除 |
| `html-page-context` | update_templates | 默认 | 模板名称处理 |
| `html-page-context` | prep_header_buttons | 默认 | 初始化header_buttons列表 |
| `html-page-context` | add_launch_buttons | 501 | 添加启动按钮组 |
| `html-page-context` | add_source_buttons | 501 | 添加源码按钮组 |
| `html-page-context` | add_header_buttons | 501 | 添加下载/全屏按钮 |

## 按钮字典格式

### link 按钮

```python
{
    "type": "link",
    "url": "...",
    "text": "...",        # 按钮文字（单按钮时可留空只显示图标）
    "icon": "fas fa-xxx", # Font Awesome 类名 或 图片路径
    "tooltip": "...",     # 提示文字（自动翻译）
    "label": "...",       # CSS类名 btn-{label}
}
```

### javascript 按钮

```python
{
    "type": "javascript",
    "javascript": "functionName()",
    "text": "...",
    "icon": "fas fa-xxx",
    "tooltip": "...",
    "label": "...",
}
```

### group 按钮（下拉菜单）

```python
{
    "type": "group",
    "tooltip": "...",
    "icon": "fas fa-xxx",
    "buttons": [...],  # 子按钮列表
    "label": "...",
}
```

## 边注语法

### MyST（Markdown）

```markdown
标准旁注（带编号）：
这是正文[^1]

[^1]: 这是旁注内容，显示在右侧边距

无边注编号：
这是正文[^2]

[^2]: {-} 这是边注内容，不显示编号
```

### reStructuredText

```rst
标准旁注（带编号）：
这是正文[#note1]_

.. [#note1] 这是旁注内容

无边注编号：
这是正文[#note2]_

.. [#note2] {-} 这是边注内容
```
