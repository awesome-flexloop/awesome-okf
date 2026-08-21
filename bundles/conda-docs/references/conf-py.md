---
okf_version: "0.2"
type: reference
title: "Sphinx 配置文件 conf.py 关键配置"
sources:
  - docs/source/conf.py
  - requirements.txt
  - .readthedocs.yml
  - docs/Makefile
---

# Sphinx 配置文件 conf.py 关键配置

`conf.py` 是 Sphinx 文档构建的核心配置文件，位于 `docs/source/conf.py`。以下按功能模块提取关键配置。

## 基础配置

- **master_doc**: `"index"` — 主文档为 index.rst
- **project**: `"conda-docs"` — 项目名称
- **copyright**: `"2017, Anaconda, Inc."`
- **version / release**: `" "`（空字符串）— conda-docs 作为门户仓库本身无版本号
- **source_suffix**: `".rst"` — 使用 reStructuredText 格式
- **pygments_style**: `"sphinx"` — 代码高亮风格

## 扩展列表（extensions）

```python
extensions = [
    "sphinx.ext.autodoc",            # 自动文档生成
    "sphinx.ext.autosummary",        # 自动摘要
    "sphinx.ext.graphviz",           # Graphviz 图表
    "sphinx.ext.ifconfig",           # 条件配置
    "sphinx.ext.inheritance_diagram", # 继承图
    "sphinx_sitemap",               # 站点地图（SEO）
    "sphinx_design",                # 卡片/网格/标签页设计组件
    "sphinx_reredirects",           # 页面重定向
]
```

## HTML 输出配置

- **html_theme**: `"conda_sphinx_theme"` — Anaconda 定制主题（0.4.0）
- **html_static_path**: `["_static"]` — 静态资源目录
- **html_css_files**: `["css/custom.css"]` — 自定义样式
- **html_extra_path**: `["robots.txt"]` — 额外文件（SEO）
- **html_baseurl**: `"https://docs.conda.io/"` — 站点基础 URL

## GitHub 集成上下文

```python
html_context = {
    "github_user": "conda",
    "github_repo": "conda-docs",
    "github_version": "main",
    "display_github": True,
    "source_suffix": ".rst",
    "doc_path": "docs/source",
}
```

## 主题选项

```python
html_theme_options = {
    "show_prev_next": False,              # 隐藏上一页/下一页
    "use_edit_page_button": True,         # 显示"编辑本页"按钮
    "primary_sidebar_end": [],
    "github_url": "https://github.com/conda/conda-docs",
    "icon_links": [{"name": "Zulip", "url": "https://conda.zulipchat.com", ...}],
}
```

## 站点地图与重定向

- **sitemap_locales**: `[None]` — 单语言站点
- **sitemap_url_scheme**: `"{lang}latest/{link}"` — 固定 latest 版本
- **redirects**: 配置三个外部重定向（conda、conda-build、miniconda → 对应外部文档 URL）

## 构建依赖（requirements.txt）

```
conda-sphinx-theme==0.4.0
sphinx-sitemap==2.9.0
sphinx-design==0.7.0
sphinx-reredirects==1.1.0
```

## ReadTheDocs CI 配置（.readthedocs.yml）

- 构建镜像：Ubuntu 24.04 + Python 3.14
- 从 requirements.txt 安装依赖
- 额外输出格式：htmlzip

## 本地构建（Makefile）

```makefile
SPHINXBUILD = python3 -msphinx
SOURCEDIR   = source
BUILDDIR    = build
```

使用 catch-all 目标将 `make` 命令传递给 sphinx-build。

## 自定义模板与统计

`_templates/layout.html` 继承基础模板，在 footer 注入 Google Analytics（UA-27761864-11，开启 IP 匿名化）和 GoatCounter 统计。

## 相关概念

- [文档门户架构](../concepts/01-doc-portal-arch.md)
- [Sphinx 构建系统配置](../concepts/02-sphinx-config.md)
- [首页结构](index-rst.md)
