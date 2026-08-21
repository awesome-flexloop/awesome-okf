---
okf_version: "0.2"
type: "concept"
title: "Sphinx 构建系统配置详解"
sources:
  - docs/source/conf.py
  - requirements.txt
  - .readthedocs.yml
  - docs/Makefile
  - docs/source/_static/css/custom.css
  - docs/source/_templates/layout.html
---

# Sphinx 构建系统配置详解

conda-docs 的 Sphinx 配置（`docs/source/conf.py`）是开源项目文档门户的典型配置范式。

## 依赖管理

`requirements.txt` 仅4个包，精简高效：

| 包 | 版本 | 用途 |
|---|------|------|
| conda-sphinx-theme | 0.4.0 | Anaconda 定制 Sphinx 主题 |
| sphinx-sitemap | 2.9.0 | XML 站点地图（SEO） |
| sphinx-design | 0.7.0 | 卡片、网格、标签页等 UI 组件 |
| sphinx-reredirects | 1.1.0 | 外部 URL 页面重定向 |

## 扩展配置

```python
extensions = [
    "sphinx.ext.autodoc",            # 门户中未直接使用，为兼容性保留
    "sphinx.ext.autosummary",
    "sphinx.ext.graphviz",
    "sphinx.ext.ifconfig",
    "sphinx.ext.inheritance_diagram",
    "sphinx_sitemap",               # SEO
    "sphinx_design",                # UI 组件（核心）
    "sphinx_reredirects",           # 外部重定向（核心）
]
```

门户仓库的核心扩展是 sphinx_design 和 sphinx_reredirects。

## 主题与品牌定制

**主题选择**：`conda_sphinx_theme`，统一 Anaconda 品牌视觉。

**主题选项**：
```python
html_theme_options = {
    "show_prev_next": False,              # 门户不需要线性导航
    "use_edit_page_button": True,         # 鼓励社区贡献
    "primary_sidebar_end": [],
    "github_url": "https://github.com/conda/conda-docs",
    "icon_links": [{"name": "Zulip", "url": "https://conda.zulipchat.com", ...}],
}
```

**自定义 CSS**（`_static/css/custom.css`）：
```css
#conda-documentation .sd-tab-content {
    min-height: 9rem;
}
```

**自定义模板**（`_templates/layout.html`）：继承基础 layout，在 footer 块注入 Google Analytics（UA-27761864-11，`anonymizeIp: true`）和 GoatCounter 统计。使用 `{{ super() }}` 保留原始 footer。

## SEO 配置

- **html_baseurl**: `"https://docs.conda.io/"` — 站点地图所需
- **sitemap_locales**: `[None]` — 单语言站点
- **sitemap_url_scheme**: `"{lang}latest/{link}"`
- **html_extra_path**: `["robots.txt"]` — 引导搜索引擎

## GitHub 集成

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

自动生成"编辑此页"按钮，直接链接到 GitHub 源文件。

## 外部重定向

```python
redirects = {
    "conda": "https://docs.conda.io/projects/conda/en/stable",
    "conda-build": "https://docs.conda.io/projects/conda-build/en/stable",
    "miniconda": "https://docs.anaconda.com/free/miniconda/",
}
```

使用 HTTP 重定向（优于 HTML meta refresh），便于统一维护。

## ReadTheDocs CI

`.readthedocs.yml` 配置自动构建：

```yaml
version: 2
sphinx:
  configuration: docs/source/conf.py
build:
  os: ubuntu-24.04
  tools:
    python: "3.14"
python:
  install:
  - requirements: requirements.txt
formats:
- htmlzip
```

## 本地构建

`docs/Makefile` 使用 catch-all 目标：
```makefile
SPHINXBUILD = python3 -msphinx
SOURCEDIR   = source
BUILDDIR    = build

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
```

本地构建命令：
```bash
conda create -n conda-docs pip -y
conda activate conda-docs
pip install -r requirements.txt
cd docs
make html
```

输出位于 `docs/build/html/`。

## 相关概念

- [文档门户架构](01-doc-portal-arch.md)
- [本地构建 conda-docs](../examples/local-build.md)
- [基于 conda-docs 模式搭建文档门户](../examples/doc-portal-template.md)
- [信源：Sphinx 配置 conf.py](../references/conf-py.md)
