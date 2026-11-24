---
type: Concept
title: 快速开始
description: 安装、最小 conf.py、首次构建与验收清单
tags: [sphinx, theme, pydata, install, quickstart]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T02:52:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
  - id: pst-official
    resource: /references/official-docs.md
    title: 官方文档与仓库入口
---

# 快速开始

## 1. 环境准备

PST 要求 Python 3.11+ 与 Sphinx 8.2+。推荐在独立虚拟环境中安装：

```console
$ python -m venv .venv
$ . .venv/bin/activate        # Windows: .venv\Scripts\activate
$ pip install -U pip
$ pip install "pydata-sphinx-theme" sphinx
```

也可以使用 conda：

```console
$ conda install pydata-sphinx-theme --channel conda-forge
```

验证安装：

```console
$ python -c "import pydata_sphinx_theme; print(pydata_sphinx_theme.__version__)"
```

## 2. 最小项目

目录结构：

```text
mydocs/
├── conf.py
├── index.md
└── _static/
    └── logo.svg
```

`conf.py` 的最小可用配置：

```python
project = "My Project"
author = "My Team"
copyright = "2026, My Team"

extensions = ["myst_parser"]

html_theme = "pydata_sphinx_theme"
html_title = "My Project"
html_static_path = ["_static"]
html_logo = "_static/logo.svg"

html_theme_options = {
    "github_url": "https://github.com/my-org/my-repo",
    "show_prev_next": True,
}
```

`index.md`：

````markdown
# My Project

Welcome!

```{toctree}
:maxdepth: 2
:caption: Guide

install
usage
```
````

`install.md` 与 `usage.md` 按普通 Markdown 编写即可。

## 3. 构建与预览

```console
$ sphinx-build -b html . _build/html
$ python -m http.server -d _build/html 8000
```

Windows PowerShell 同样适用。打开 `http://127.0.0.1:8000/` 检查：

1. 顶部导航是否出现项目名与 GitHub 图标。
2. 左侧是否出现 `Guide` 分区与两个子页。
3. 右侧是否出现页内目录与 "View source"。
4. 右上角是否可切换 light / dark / auto。
5. 窄屏（< 960px）下是否出现汉堡按钮与抽屉式侧栏。

## 4. 常见初体验问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 顶部没有导航项 | `index.md` 的 toctree 是隐藏的，或没有顶层条目 | 用非隐藏 toctree，或配置 `external_links` |
| 左侧空白 | 当前页没有祖先章节，或 `html_sidebars` 被清空 | 检查页面是否挂在某个顶层 toctree 下 |
| 右侧没有目录 | 页面只有一个 `h1` 且没有 `h2` | 增加二级标题，或配置 `show_toc_level` |
| 暗色模式闪烁 | 自定义脚本在主题脚本之前改了 `data-theme` | 使用主题的 `setTheme` 机制或避免首屏改属性 |
| 本地打开 `file://` 时版本切换器为空 | 浏览器禁止 `file://` 下的 fetch | 用本地 HTTP 服务器预览 |
| 字体/图标不显示 | 静态资源路径错误或被 CSP 拦截 | 检查 `html_static_path` 与浏览器控制台 |

## 5. 验收清单

- [ ] `html_theme = "pydata_sphinx_theme"` 生效（页面含 `pst-` 前缀类名）。
- [ ] 顶部、左侧、右侧三块区域都有内容或明确为空。
- [ ] light/dark/auto 切换后刷新仍保持选择（`localStorage` 生效）。
- [ ] 搜索按钮可用（`Ctrl+K` / `Cmd+K`）。
- [ ] 窄屏下侧栏可打开、可关闭、可用 Escape 关闭。
- [ ] 控制台无 404（尤其 `_static/styles/pydata-sphinx-theme.css` 与 `pygments.css`）。

## 6. 下一步

- 想让布局更贴合项目：读[布局与模板区段](03-layout-and-sections.md)。
- 想配置导航深度与折叠：读[导航与 toctree](04-navigation-and-toctree.md)。
- 想做品牌化与暗色模式：读[品牌、样式与暗色模式](07-branding-styling-and-dark-mode.md)。
- 想加版本切换器：读[搜索、版本切换与公告](08-search-versioning-and-announcements.md)。

## 相关概念

- [简介](00-introduction.md)
- [架构总览](02-architecture-overview.md)
- [基础站点示例](../examples/01-basic-site.md)
