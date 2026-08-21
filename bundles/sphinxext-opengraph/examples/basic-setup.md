---
type: Example
title: 基础配置示例
description: 从零开始配置sphinxext-opengraph的最小可用示例，包含安装、conf.py配置和构建验证
tags: [sphinxext-opengraph, example, basic-setup, getting-started, configuration]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T08:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: sphinxext-opengraph-source
    resource: /references/sphinxext-opengraph-source.md
    title: sphinxext-opengraph 源码信源登记
---

# 基础配置示例

本示例演示如何在Sphinx项目中从零开始配置sphinxext-opengraph，实现最基本的社交分享预览功能。

## 前置条件

- Python 3.9+
- 一个已有的Sphinx文档项目（或使用 `sphinx-quickstart` 创建）

## 第一步：安装

```bash
pip install sphinxext-opengraph
```

## 第二步：最小 conf.py 配置

在你的 `conf.py` 中，只需添加两行配置：

```python
# conf.py

# -- Project information -----------------------------------------------------
project = 'My Awesome Project'
copyright = '2025, Your Name'
author = 'Your Name'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinxext.opengraph',  # 添加这一行
]

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'

# -- Open Graph configuration -----------------------------------------------
ogp_site_url = 'https://my-awesome-project.readthedocs.io/en/latest/'
```

这就是全部！`ogp_site_url` 是唯一**必须**设置的配置项。

## 第三步：构建文档

```bash
make html
```

## 第四步：验证输出

构建完成后，打开 `_build/html/index.html`，查看源码中的 `<head>` 部分，你应该能看到类似以下的输出：

```html
<meta property="og:title" content="My Awesome Project documentation" />
<meta property="og:type" content="website" />
<meta property="og:url" content="https://my-awesome-project.readthedocs.io/en/latest/index.html" />
<meta property="og:site_name" content="My Awesome Project" />
<meta property="og:description" content="My Awesome Project documentation..." />
<meta name="description" content="My Awesome Project documentation..." />
```

## 带默认图片的配置

如果你想为所有页面设置一个统一的预览图（如项目logo）：

```python
# conf.py
extensions = ['sphinxext.opengraph']

ogp_site_url = 'https://my-awesome-project.readthedocs.io/en/latest/'
ogp_image = '_static/logo.png'  # 相对于ogp_site_url根目录
ogp_image_alt = 'My Awesome Project Logo'
```

将 `logo.png` 放在 `_static/` 目录下，构建后每个页面都会有：

```html
<meta property="og:image" content="https://my-awesome-project.readthedocs.io/en/latest/_static/logo.png" />
<meta property="og:image:alt" content="My Awesome Project Logo" />
```

## ReadTheDocs零配置

如果你的文档托管在ReadTheDocs上，甚至不需要设置 `ogp_site_url`：

```python
# conf.py - RTD托管的最小配置
extensions = ['sphinxext.opengraph']
# ogp_site_url 不需要设置！RTD自动检测
```

ReadTheDocs构建时会设置 `READTHEDOCS` 和 `READTHEDOCS_CANONICAL_URL` 环境变量，扩展会自动从中提取站点URL。

## 常见配置变体

### 自定义描述长度

默认描述长度为200字符，如果想让分享卡片显示更多内容：

```python
ogp_description_length = 300
```

### 禁用自动meta description

如果你有其他SEO扩展负责生成meta description：

```python
ogp_enable_meta_description = False
```

### 自定义站点名称

默认使用 `project` 配置值，如果想显示不同的名称：

```python
ogp_site_name = 'My Awesome Docs'  # 自定义
ogp_site_name = False               # 完全禁用site_name
```

### 自定义OG类型

对于博客/文章类文档：

```python
ogp_type = 'article'
```

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [配置选项全解](/concepts/02-configuration.md)
- [社交卡片配置示例](/examples/social-cards-example.md)
- [高级配置示例](/examples/advanced-config.md)
- [sphinxext-opengraph 源码信源登记](/references/sphinxext-opengraph-source.md)
