---
type: Concept
title: "页眉按钮机制：从配置到一组 URL"
description: "sphinx-book-theme 如何在 html-page-context 阶段生成 header_buttons 数据、Jinja 宏如何渲染、下载/源码/仓库/issue/启动按钮各自的 URL 规则与限制"
tags: [sphinx, theme, header-buttons, jinja2, binder, colab, thebe]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-buttons
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme/src/sphinx_book_theme/header_buttons/__init__.py
    title: header_buttons/__init__.py
  - id: sbt-source
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme/src/sphinx_book_theme/header_buttons/source.py
    title: header_buttons/source.py
  - id: sbt-launch
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme/src/sphinx_book_theme/header_buttons/launch.py
    title: header_buttons/launch.py
---

# 页眉按钮机制：从配置到一组 URL

## 设计模式：数据与渲染分离

页眉按钮不是写死在模板里的 HTML，而是两段式：

```text
Python（html-page-context）
  生成 context["header_buttons"] = [ {...}, {...} ]
        ↓
Jinja（components/article-header-buttons.html）
  遍历列表，按 type 选择宏渲染
        ↓
HTML（Bootstrap 按钮 / 下拉组）
```

这样做的好处：按钮的**业务逻辑**（URL 怎么拼、什么时候显示）留在 Python 里可测试；**视觉结构**（图标、提示、下拉）留在模板里可替换。

## 数据结构

每个按钮是一个字典，`type` 决定渲染宏：

```python
{
    "type": "link",                 # link | javascript | group
    "url": "https://...",           # link 必填
    "javascript": "window.print()", # javascript 必填
    "text": ".pdf",                 # 显示文字，可为空
    "icon": "fas fa-file-pdf",      # FontAwesome 类或图片路径
    "tooltip": "Print to PDF",
    "label": "download-pdf-button", # 生成 btn-<label> class，便于 CSS/测试
    "classes": "",                  # 追加 class
}
```

`group` 类型额外带 `buttons` 列表，渲染为 Bootstrap 下拉菜单：

```python
{
    "type": "group",
    "tooltip": "Download this page",
    "icon": "fas fa-download",
    "buttons": [ ... ],
    "label": "download-buttons",
}
```

渲染入口在 `components/article-header-buttons.html`：

```jinja
{% from "../macros/buttons.html" import render_funcs with context %}

<div class="article-header-buttons">
{%- for button in header_buttons -%}
{% set btype = button.get("type") %}
{% set bopts = button.copy() %}
{% set _ = bopts.pop("type") %}
{{ render_funcs[btype](**bopts) }}
{%- endfor -%}

{% include "theme-switcher.html" %}
{% include "search-button.html" %}
{% include "toggle-secondary-sidebar.html" %}
</div>
```

## 生成顺序

| 顺序 | 函数 | 优先级 | 追加内容 |
|------|------|--------|---------|
| 1 | `prep_header_buttons` | 默认 | 创建空列表 |
| 2 | `add_launch_buttons` | 501 | 在线运行按钮组 |
| 3 | `add_source_buttons` | 501 | 仓库/源码/编辑/issue 按钮 |
| 4 | `add_header_buttons` | 501 | 下载组 + 全屏按钮 |

优先级 501 是为了晚于父主题设置 `get_edit_provider_and_url`，否则源码类按钮拿不到编辑 URL。

## 下载与全屏

`add_header_buttons` 负责"不需要仓库信息"的按钮。

### 下载组

条件：`use_download_button` 为真，且当前页有源文件后缀。

组内可能有三项：

| 按钮 | 出现条件 | URL/动作 |
|------|---------|---------|
| `.ipynb` | 页面由 Notebook 生成，`context["ipynb_source"]` 存在 | `_sources/<pagename>.ipynb` |
| 源文件后缀（`.md`/`.rst`） | 始终 | `_sources/<sourcename>` |
| `.pdf` | 始终 | `window.print()`（浏览器打印为 PDF） |

注意 `.pdf` 不是服务端生成 PDF，而是调用浏览器打印。需要真正的 PDF 请用 LaTeX builder 或 WeasyPrint 等方案。

### 全屏按钮

条件：`use_fullscreen_button` 为真（默认真）。动作：

```python
"javascript": "toggleFullScreen()"
```

对应 `assets/scripts/index.js` 中的全屏实现，包含 Safari 的 `webkit` 前缀分支。

### 源文件后缀的默认值

`update_sourcename` 在 `builder-inited` 阶段检查：如果用户没有显式配置 `html_sourcelink_suffix`，就设为空字符串。这样下载链接指向 `.md`/`.rst`/`.ipynb` 原文件，而不是 Sphinx 默认的 `.txt`。

## 仓库信息注入

源码按钮和启动按钮都依赖仓库信息。用户在 `html_theme_options` 只写一个 `repository_url`，主题在 `builder-inited` 阶段把它拆成父主题认识的 `html_context` 变量：

```python
repo_url = opts.get("repository_url", "")
provider_url, org, repo = repo_url.strip("/").rsplit("/", 2)

context.update({
    "github_user": org,        # 以 github 为例
    "github_repo": repo,
    "github_version": branch,  # 默认 main
    "github_url": provider_url,
    "doc_path": relpath,
})
```

规则：

- **最后两段**固定解释为 `org/repo`。
- 未写 `repository_provider` 时，按 URL 中是否含 `github.com` / `gitlab.com` / `bitbucket.org` 推断。
- 推断失败直接抛 `SphinxError`，提示你显式指定 provider。
- `repository_branch` 为空时默认 `main`（启动按钮代码里另有 `master` 回退，见下）。

自建服务示例：

```python
html_theme_options = {
    "repository_provider": "gitlab",
    "repository_url": "https://git.example.org/team/docs",
    "repository_branch": "main",
    "path_to_docs": "docs",
}
```

## 源码类按钮

`add_source_buttons` 支持四个开关：

| 开关 | 文本 | URL 规则 |
|------|------|---------|
| `use_repository_button` | Repository | `https://host/org/repo` |
| `use_source_button` | Show source | 编辑 URL 的 `/edit/` 换成 `/blob/`，GitHub/GitLab 追加 `?plain=1` |
| `use_edit_page_button` | Suggest edit | 父主题 `get_edit_provider_and_url()` 返回的编辑 URL |
| `use_issues_button` | Open issue | GitHub/GitLab 的 `issues/new`，标题带当前页名 |

细节：

- Bitbucket 的源码 URL 是去掉 `?mode=edit`，不追加 `?plain=1`。
- `use_issues_button` 只支持 GitHub 与 GitLab；其他 provider 会记 warning，不生成按钮。
- 只启用一个按钮时，按钮不显示文字，只显示图标；多个按钮时合并为下拉组。
- 按钮是否出现还要求 `doctree` 与源文件后缀存在——纯模板页没有源码按钮。

## 启动按钮

`add_launch_buttons` 只在**当前页是 Notebook** 且配置了任一启动服务时工作。

### 判定 Notebook

```python
metadata = app.env.metadata[pagename]
if "kernelspec" in metadata:
    return True
elif "ipynb" in context.get("page_source_suffix", ""):
    return True
return False
```

两个条件满足其一即可：页面元数据有 `kernelspec`，或源文件后缀含 `ipynb`。

### 生成 `.ipynb` 下载副本

如果页面是 Markdown 写的 Notebook（MyST-NB），构建目录里会有 `jupyter_execute/<pagename>.ipynb`。主题会把它复制到 `_sources/<pagename>.ipynb`，这样"下载 notebook"按钮有真实文件可下。

### 各服务的 URL 规则

记 `path_rel_repo = path_to_docs + pagename + extension`，`ui_pre` 由 `notebook_interface` 决定（`classic` → `tree`，`jupyterlab` → `lab/tree`）。

| 服务 | URL 模式 | 限制 |
|------|---------|------|
| Binder（GitHub） | `<binderhub>/v2/gh/<org>/<repo>/<branch>?urlpath=<ui_pre>/<path>` | — |
| Binder（GitLab） | `<binderhub>/v2/gl/<org>%2F<repo>/<branch>?urlpath=...` | — |
| Binder（自建） | `<binderhub>/v2/git/<完整repo_url>/<branch>?urlpath=...` | 仓库 URL 原样传入 |
| JupyterHub | `<hub>/hub/user-redirect/git-pull?repo=...&urlpath=...&branch=...` | — |
| Colab | `<colab>/github/<org>/<repo>/blob/<branch>/<path>` | 仅 GitHub |
| Deepnote | `<deepnote>/launch?url=https%3A%2F%2Fgithub.com%2F<org>%2F<repo>%2Fblob%2F<branch>%2F<path>` | 仅 GitHub；每次新建项目 |
| JupyterLite | `<jupyterlite_url>?path=<path>` | 可相对路径 |
| Thebe | `initThebeSBT()` | 需 `sphinx_thebe` 扩展 |

`notebook_interface` 只接受 `classic` 或 `jupyterlab`，其他值直接抛 `ValueError`。

### Thebe 的额外协作

当 `launch_buttons["thebe"]` 为真：

- 主题追加一个 JavaScript 按钮，调用 `initThebeSBT()`；
- 设置 `context["use_thebe"] = True`；
- `update_mode_thebe_config` 把 `repository_url` / `repository_branch` 补进 `thebe_config`，供 Thebe 找运行环境；
- 若用户没把 `sphinx_thebe` 放进 `extensions`，只记 warning，不生成可用按钮。

## 按钮的 CSS 钩子

每个按钮的 `label` 会变成 `btn-<label>` class，例如：

- `btn-download-buttons`
- `btn-fullscreen-button`
- `btn-source-buttons`
- `btn-launch-buttons`

回归测试也正是靠这些 class 定位按钮。自定义样式时优先用这些稳定钩子，不要依赖 Bootstrap 的层级选择器。

## 常见问题

### 按钮不出现

按顺序检查：

1. `use_*_button` 是否为真（注意字符串 `"False"` 会被 `as_bool` 判假）。
2. 是否配置了 `repository_url`。
3. 当前页是否有源文件（纯模板页没有）。
4. 启动按钮：当前页是否为 Notebook。
5. 启动按钮：是否配置了对应的服务 URL。

### 仓库 URL 推断失败

报错：

```text
Provider not recognized in repository url ...
```

显式加 `repository_provider`，或把 URL 改成标准 `https://github.com/org/repo` 形式。

### Binder 打开后路径不对

检查 `path_to_docs` 是否相对**仓库根**，而不是相对 `conf.py`。例如文档在 `docs/`，`path_to_docs` 应写 `docs`。

## 相关概念

- [配置选项全解](04-theme-options.md)
- [Notebook 与在线交互](07-jupyter-interactivity.md)
- [仓库按钮与在线启动按钮](../examples/02-repository-and-launch-buttons.md)
