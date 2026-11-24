---
type: Concept
title: "配置选项全解：theme.conf、html_theme_options 与模板变量"
description: "sphinx-book-theme 的三层配置映射、theme.conf 全部选项分类表、继承自 pydata-sphinx-theme 的选项，以及字符串/布尔/列表的类型陷阱"
tags: [sphinx, theme, configuration, html_theme_options, theme.conf]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-theme-conf
    resource: external/libs/docs/sphinx-contrib/sphinx-book-theme/src/sphinx_book_theme/theme/sphinx_book_theme/theme.conf
    title: theme.conf
  - id: sbt-docs-sections
    resource: https://sphinx-book-theme.readthedocs.io/en/latest/sections/index.html
    title: Layout and major sections
  - id: pst-options
    resource: https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/index.html
    title: PyData Sphinx Theme user guide
---

# 配置选项全解：theme.conf、html_theme_options 与模板变量

## 三层配置映射

```text
theme.conf 的 [options]        提供默认值
        ↓
conf.py 的 html_theme_options  用户覆盖（只写差异）
        ↓
Jinja 模板中的 theme_<name>    渲染时读取
```

举例：`theme.conf` 写 `show_navbar_depth = 1`，用户在 `conf.py` 写 `"show_navbar_depth": 2`，模板里读 `theme_show_navbar_depth` 得到 `2`。

规则：

- `theme.conf` 的键名不带 `theme_` 前缀；模板变量自动带前缀。
- 用户只需覆盖想改的键，未覆盖的沿用 `theme.conf`。
- 值的类型由 Sphinx 配置系统决定，`theme.conf` 里的字面量经常以字符串到达模板。

## 类型陷阱

`theme.conf` 的值看起来像布尔，实际可能是字符串 `"True"` / `"False"`：

```ini
use_sidenotes = False
```

Python 侧必须用主题自带的 `as_bool()`：

```python
def as_bool(var):
    if isinstance(var, str):
        return var.lower() == "true"
    elif isinstance(var, bool):
        return var
    return False
```

模板侧必须用 `|tobool`：

```jinja
{% if theme_home_page_in_toc == True %}   {# 不可靠：可能是字符串 #}
{% if theme_collapse_navbar|tobool %}     {# 正确 #}
```

自己写模板或子主题时，这条规则同样适用。

## 本书主题自有选项

### 公告与页眉

| 选项 | 默认 | 类型 | 作用 |
|------|------|------|------|
| `announcement` | 空 | str/HTML | 顶部公告横幅，滚动后消失 |
| `article_header_start` | `toggle-primary-sidebar.html` | str/list | 正文工具条左侧模板 |
| `article_header_end` | `article-header-buttons.html` | str/list | 正文工具条右侧模板 |
| `navbar_start` | 空 | str/list | 页眉最左区域 |
| `navbar_center` | 空 | str/list | 页眉中间区域 |
| `navbar_end` | 空 | str/list | 页眉最右区域 |
| `navbar_persistent` | 空（运行时强制 `[]`） | str/list | 移动端仍常驻的页眉项 |

### 侧边栏与目录

| 选项 | 默认 | 类型 | 作用 |
|------|------|------|------|
| `secondary_sidebar_items` | `page-toc.html` | str/list | 右侧栏组件 |
| `toc_title` | `Contents` | str | 页内目录标题 |
| `home_page_in_toc` | `False` | bool | 是否把根文档加入左侧目录 |
| `show_navbar_depth` | `1` | int | 左侧目录默认展开层数 |
| `max_navbar_depth` | `4` | int | 左侧目录最大渲染层数 |
| `collapse_navbar` | `False` | bool | 是否禁用展开/折叠 |
| `expand_toc_sections` | `[]` | list | 已废弃，保留兼容 |

### 页眉按钮

| 选项 | 默认 | 类型 | 作用 |
|------|------|------|------|
| `use_download_button` | `True` | bool | 下载源文件 / `.ipynb` / 打印 PDF |
| `use_fullscreen_button` | `True` | bool | 全屏按钮 |
| `use_source_button` | `False` | bool | 查看在线源码 |
| `use_edit_page_button` | 继承父主题 | bool | 建议编辑（跳转 PR 页面） |
| `use_issues_button` | `False` | bool | 就当前页开 issue |
| `use_repository_button` | `False` | bool | 跳转仓库首页 |

### 仓库信息

| 选项 | 默认 | 类型 | 作用 |
|------|------|------|------|
| `repository_url` | 空 | str | 仓库地址；最后两段视为 `org/repo` |
| `repository_branch` | 空 → `main` | str | 源码/启动链接使用的分支 |
| `repository_provider` | 空 → 自动推断 | str | `github` / `gitlab` / `bitbucket` |
| `path_to_docs` | 空 | str | 文档相对仓库根的路径 |
| `launch_buttons` | `{}` | dict | 在线运行服务配置，见下 |

### 在线启动按钮

`launch_buttons` 是嵌套字典：

```python
html_theme_options = {
    "launch_buttons": {
        "binderhub_url": "https://mybinder.org",
        "jupyterhub_url": "https://hub.example.org",
        "colab_url": "https://colab.research.google.com",
        "deepnote_url": "https://deepnote.com",
        "jupyterlite_url": "interact/lab/index.html",
        "thebe": True,
        "notebook_interface": "jupyterlab",
    },
}
```

| 键 | 作用 | 限制 |
|----|------|------|
| `binderhub_url` | Binder 启动 | GitHub / GitLab / 自建仓库 |
| `jupyterhub_url` | JupyterHub 启动 | 通过 `git-pull` 重定向 |
| `colab_url` | Google Colab | 仅 GitHub |
| `deepnote_url` | Deepnote | 仅 GitHub；每次点击新建项目 |
| `jupyterlite_url` | 浏览器内 JupyterLite | 可相对路径 |
| `thebe` | 页面内实时运行 | 需启用 `sphinx_thebe` 扩展 |
| `notebook_interface` | 打开的界面 | `classic`（默认）或 `jupyterlab` |

### 页脚

| 选项 | 默认 | 类型 | 作用 |
|------|------|------|------|
| `footer_content_items` | `author.html, copyright.html, last-updated.html, extra-footer.html` | str/list | 正文末尾页脚组件 |
| `extra_footer` | 空 | HTML | 追加到内容页脚 |
| `footer_start` | 空 | str/list | 站点页脚左侧 |
| `footer_end` | 空 | str/list | 站点页脚右侧 |

### 内容表现

| 选项 | 默认 | 类型 | 作用 |
|------|------|------|------|
| `use_sidenotes` | `False` | bool | 把脚注转成边注/margin note |

## 继承自 pydata-sphinx-theme 的常用选项

本书主题没有重新声明、但可直接使用的父主题选项：

| 选项 | 作用 |
|------|------|
| `logo` | 高级 logo 配置：`image_light`、`image_dark`、`text`、`alt_text` |
| `icon_links` | 侧栏图标链接与徽章列表 |
| `use_edit_page_button` | 建议编辑按钮（本书主题继承） |
| `search_as_you_type` | 搜索即输 |
| `show_toc_level` | 页内目录常驻层级 |
| `navigation_with_keys` | 键盘左右键翻页 |
| `check_switcher` | 版本切换器校验 |
| `switcher` | 版本文档切换器配置 |
| `analytics` | 分析脚本配置 |
| `primary_sidebar_end` | 主侧栏末尾追加组件 |

使用前建议查父主题文档确认当前版本行为；本书主题锁定的父主题版本是 `0.23.0`。

## 特殊选项：search_bar_text

`add_metadata_to_page` 中有一段特判：

```python
theme_options = get_theme_options_dict(app)
if "search_bar_text" not in theme_options:
    context["theme_search_bar_text"] = translation("Search") + "..."
```

含义：只有用户**没有**显式配置 `search_bar_text` 时，才用翻译后的默认占位符。若你要自定义搜索框文案：

```python
html_theme_options = {
    "search_bar_text": "搜索全书…",
}
```

## 配置优先级与调试

排查"为什么我的配置没生效"时按顺序检查：

1. 键名是否写对（`show_navbar_depth` 不是 `navbar_show_depth`）。
2. 是否写在了 `html_theme_options` 里，而不是模块级变量。
3. 值的类型是否符合预期（布尔是否被写成字符串 `"false"`）。
4. 是否被 `html_sidebars` 的页面级覆盖遮蔽。
5. 是否被模板硬编码覆盖（例如 `sections/header.html` 整体替换）。
6. 是否被父主题同名选项覆盖（查 pydata 文档）。

打印实际主题选项：

```python
# conf.py 临时调试
def setup(app):
    @app.connect("builder-inited")
    def _dump(app):
        from pydata_sphinx_theme.utils import get_theme_options_dict
        print(get_theme_options_dict(app))
```

## 相关概念

- [页面分区与导航](03-layout-and-navigation.md)
- [页眉按钮机制](05-header-buttons.md)
- [主题选项速查](../references/theme-options-reference.md)
