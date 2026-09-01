---
type: Concept
title: 04 - 头部按钮系统
description: 头部按钮的三阶段注入机制、下载按钮组、启动按钮组、源码按钮组的构建逻辑和自定义方法
tags:
- sphinx-book-theme
- header-buttons
- launch-buttons
- source-buttons
- download-buttons
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- src/sphinx_book_theme/header_buttons/__init__.py
- src/sphinx_book_theme/header_buttons/launch.py
- src/sphinx_book_theme/header_buttons/source.py
- src/sphinx_book_theme/theme/sphinx_book_theme/macros/buttons.html
- src/sphinx_book_theme/theme/sphinx_book_theme/components/article-header-buttons.html
---

# 头部按钮系统

头部按钮是 sphinx-book-theme 的核心交互功能，集中显示在每篇文章右上角。按钮系统采用事件驱动的三阶段注入机制，支持三种按钮类型（链接、JavaScript、下拉组），通过 Jinja2 宏系统渲染。

## 三阶段注入流水线

按钮的构建遵循严格的事件优先级顺序（F-051）：

```
html-page-context 事件
    │
    ├─ 优先级默认: prep_header_buttons
    │   └─ 初始化 context["header_buttons"] = []
    │
    ├─ 优先级501: add_launch_buttons
    │   └─ 构建启动按钮组（Binder/JupyterHub/Colab等）
    │
    ├─ 优先级501: add_source_buttons
    │   └─ 构建源码按钮组（仓库/查看/编辑/Issue）
    │
    └─ 优先级501: add_header_buttons
        └─ 构建下载按钮组和全屏按钮
```

> priority=501 确保在 PST 设置完 edit URL 函数之后运行，这样源码按钮才能正确获取编辑链接（F-051注释）。

### 为什么需要 prep 阶段？

`prep_header_buttons` 只做一件事：初始化空列表。这保证后续所有按钮回调都能向同一个列表追加元素，而不会覆盖其他按钮。如果跳过 prep 阶段，第一个访问 `context["header_buttons"]` 的回调会遇到 KeyError。

## 按钮类型与渲染

按钮由 `macros/buttons.html` 中的三个宏渲染（F-153-F-157）：

### link 按钮

渲染为 `<a target="_blank">` 链接，用于跳转外部URL。

```python
{
    "type": "link",
    "url": "https://example.com",
    "text": "按钮文字",
    "icon": "fas fa-external-link-alt",  # Font Awesome 类名 或 图片路径
    "tooltip": "提示文字（自动翻译）",
    "label": "my-button",  # CSS类: btn-my-button
}
```

图标渲染逻辑：如果 `icon` 以 `"fa"` 开头，使用 `<i class="{{icon}}">`（Font Awesome）；否则使用 `<img src="{{pathto(icon, 1)}}">`（图片文件，如平台logo）（F-153）。

### javascript 按钮

渲染为 `<button onclick="...">`，执行JavaScript代码。

```python
{
    "type": "javascript",
    "javascript": "toggleFullScreen()",
    "text": "",  # 单按钮可留空只显示图标
    "icon": "fas fa-expand",
    "tooltip": "全屏模式",
    "label": "fullscreen-button",
}
```

### group 按钮（下拉菜单）

渲染为 Bootstrap 5 下拉菜单（dropdown），包含多个子按钮。

```python
{
    "type": "group",
    "tooltip": "下载此页面",
    "icon": "fas fa-download",
    "label": "download-buttons",
    "buttons": [
        {"type": "link", "url": "...", "text": ".ipynb", ...},
        {"type": "link", "url": "...", "text": ".md", ...},
        {"type": "javascript", "javascript": "window.print()", "text": ".pdf", ...},
    ],
}
```

子按钮自动添加 `dropdown-item` 类，tooltip 位置设为左侧（`tooltip_placement="left"`）（F-156）。

## 下载按钮组

下载按钮组由 `add_header_buttons` 构建（F-062-F-109），包含以下子按钮：

| 按钮 | 条件 | 行为 |
|------|------|------|
| .ipynb 下载 | `context["ipynb_source"]` 存在（MD笔记本转换） | 下载Jupyter Notebook文件 |
| 源文件下载 | 存在 `page_source_suffix` | 下载原始源文件（.md/.rst等） |
| PDF打印 | 始终添加 | 调用 `window.print()` 触发浏览器打印 |

```python
# 禁用下载按钮
html_theme_options = {
    "use_download_button": False,
}
```

> **注意**：`html_sourcelink_suffix` 默认为空字符串（F-077-F-078），这是为了显示文件的原始扩展名（.md/.rst/.ipynb），而非Sphinx默认的 .txt。

## 全屏按钮

全屏按钮由 `add_header_buttons` 构建（F-112-F-122），调用 `toggleFullScreen()` JavaScript函数。该函数兼容标准 Fullscreen API 和 webkit 前缀（Safari）（F-029-F-050）。

```python
# 禁用全屏按钮
html_theme_options = {
    "use_fullscreen_button": False,
}
```

## 启动按钮组

启动按钮组由 `add_launch_buttons` 构建（F-123-F-136），仅在以下条件全部满足时显示：
1. 配置了 `launch_buttons` 且非空
2. 当前页面是笔记本页面（`_is_notebook` 判断：metadata含kernelspec或后缀为.ipynb）（F-252-F-262）
3. 至少配置了一个启动提供者

支持的启动平台：

### Binder

```python
"launch_buttons": {
    "binderhub_url": "https://mybinder.org",
    "notebook_interface": "jupyterlab",  # 或 "classic"
}
```

URL构建规则（F-128-F-139）：
- GitHub: `{binderhub_url}/v2/gh/{org}/{repo}/{branch}?urlpath=lab/tree/{path}`
- GitLab: `{binderhub_url}/v2/gl/{org}%2F{repo}/{branch}?urlpath=...`（注意 %2F 编码）
- 其他Git: `{binderhub_url}/v2/git/{quoted_url}/{branch}?urlpath=...`

### JupyterHub

```python
"launch_buttons": {
    "jupyterhub_url": "https://your-jupyterhub.edu",
}
```

URL格式：`{jupyterhub_url}/hub/user-redirect/git-pull?repo={repo_url}&urlpath=tree/{repo}/{path}&branch={branch}`（F-150-F-158）

### Google Colab

```python
"launch_buttons": {
    "colab_url": "https://colab.research.google.com",
}
```

URL格式：`{colab_url}/github/{org}/{repo}/blob/{branch}/{path}`（F-168-F-181）
**仅支持 GitHub**，其他provider会发出警告。

### Deepnote

```python
"launch_buttons": {
    "deepnote_url": "https://deepnote.com",
}
```

URL格式：`{deepnote_url}/launch?url=https%3A%2F%2Fgithub.com%2F{org}%2F{repo}%2Fblob%2F{branch}%2F{path}`（F-183-F-197）
**仅支持 GitHub**。

### JupyterLite

```python
"launch_buttons": {
    "jupyterlite_url": "https://your-jupyterlite.com",
    "jupyterlite_ext": ".ipynb",  # 可选
}
```

URL格式：`{jupyterlite_url}?path={path}`（F-199-F-211）

### Thebe（在线代码执行）

```python
"launch_buttons": {
    "thebe": True,
}
```

需要同时安装 `sphinx-thebe` 扩展。点击按钮调用 `initThebeSBT()`，在 h1 标题后插入 thebe-launch-button 并初始化 Thebe（F-214-F-225、F-143-F-156）。配置的 repository_url 和 repository_branch 会自动注入 thebe_config（F-157-F-166）。

### MD文件笔记本转换

当源文件是 .md 但通过 MyST-NB 执行生成了 .ipynb 时，SBT 自动从 `jupyter_execute/` 目录复制 .ipynb 到 `_sources/` 目录，并设置 `context["ipynb_source"]` 使 ipynb 下载按钮可用（F-067-F-082）。

## 源码按钮组

源码按钮组由 `add_source_buttons` 构建（F-014-F-121），支持四种按钮：

| 按钮 | 配置项 | 链接目标 |
|------|--------|---------|
| 仓库主页 | `use_repository_button` | 仓库根URL |
| 查看源码 | `use_source_button` | `/blob/` 页面（加 ?plain=1） |
| 建议编辑 | `use_edit_page_button` | `/edit/` 页面 |
| 提交Issue | `use_issues_button` | 新建Issue页面（预填标题） |

按钮的URL构建依赖 PST 的 `context["get_edit_provider_and_url"]()` 函数（F-052），这也是为什么启动按钮和源码按钮的 priority 设为 501——要等 PST 先设置好这个函数。

### 单按钮 vs 下拉组

- 启用多个源码按钮时：渲染为下拉组（type="group"），显示仓库图标
- 仅启用一个源码按钮时：清空text字段，只显示图标按钮（F-118-F-121）

```python
html_theme_options = {
    "repository_url": "https://github.com/org/repo",
    "repository_branch": "main",
    "path_to_docs": "docs",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
}
```

## 文章头部按钮容器

`article-header-buttons.html` 负责渲染所有按钮（F-150-F-152）：

```html
<div class="article-header-buttons">
{% for button in header_buttons %}
    {{ render_funcs``[button.type](**button_opts.md)`` }}
{% endfor %}
{% include "theme-switcher.html" %}
{% include "search-button.html" %}
{% include "toggle-secondary-sidebar.html" %}
</div>
```

除了动态构建的 header_buttons，容器还固定包含三个PST组件：主题切换器、搜索按钮、次级侧边栏切换。

## 添加自定义按钮

要添加自定义头部按钮，连接 `html-page-context` 事件，向 `context["header_buttons"]` 追加按钮字典：

```python
def add_my_button(app, pagename, templatename, context, doctree):
    # 确保 header_buttons 已初始化
    if "header_buttons" not in context:
        context["header_buttons"] = []

    context["header_buttons"].append({
        "type": "link",
        "url": "https://example.com/my-page",
        "text": "My Link",
        "icon": "fas fa-star",
        "tooltip": "My custom button",
        "label": "my-custom-button",
    })

def setup(app):
    app.connect("html-page-context", add_my_button, priority=502)
```

> 使用 priority >= 502 确保在内置按钮之后添加。

## 相关概念

- [主题架构与PST继承](02-theme-architecture.md)
- [配置系统详解](03-configuration.md)
- [交互功能（全屏/TOC隐藏/Thebe）](06-interactive-features.md)
- [源码路径映射与配置速查](../references/sbt-source.md)
- [交互式计算书籍配置示例](../examples/interactive-book.md)
