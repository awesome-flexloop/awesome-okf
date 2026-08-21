---
type: Concept
title: 5分钟快速上手
description: 从安装到配置到验证的完整快速入门流程，最小可用配置与构建验证
tags: [sphinxext-opengraph, getting-started, quickstart, setup, configuration]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T08:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: sphinxext-opengraph-source
    resource: /references/sphinxext-opengraph-source.md
    title: sphinxext-opengraph 源码信源登记
---

# 5分钟快速上手

## 前置条件

在开始之前，请确保你有：

- Python 3.9 或更高版本
- 一个已有的 Sphinx 文档项目（或可新建一个）
- pip 或 uv 包管理器

## 第一步：安装

安装扩展包：

```bash
pip install sphinxext-opengraph
```

如果需要社交媒体预览卡片功能（推荐），安装带matplotlib的完整版本：

```bash
pip install sphinxext-opengraph[social_cards]
```

## 第二步：启用扩展

在你的 Sphinx 项目的 `conf.py` 中，将 `sphinxext.opengraph` 添加到 `extensions` 列表：

```python
extensions = [
    'sphinx.ext.autodoc',  # 你已有的扩展
    # ...
    'sphinxext.opengraph',  # 添加这一行
]
```

## 第三步：配置站点URL

在 `conf.py` 中添加唯一必需的配置项——你的文档站点的公开URL：

```python
ogp_site_url = "https://your-project.readthedocs.io/en/latest/"
```

这是唯一必填的配置项。如果你在 ReadTheDocs 上托管文档，甚至可以不设置此值——扩展会自动从 `READTHEDOCS_CANONICAL_URL` 环境变量检测。

## 第四步：构建文档

正常构建你的Sphinx文档：

```bash
make html
```

## 第五步：验证结果

构建完成后，打开构建输出目录中的任意HTML文件（如 `_build/html/index.html`），查看页面源码中的 `<head>` 部分，你应该能看到自动生成的OGP标签：

```html
<meta property="og:title" content="你的文档标题" />
<meta property="og:type" content="website" />
<meta property="og:url" content="https://your-project.readthedocs.io/en/latest/index.html" />
<meta property="og:site_name" content="你的项目名" />
<meta property="og:description" content="自动从页面内容提取的描述文本..." />
<meta name="description" content="自动从页面内容提取的描述文本..." />
<meta name="twitter:card" content="summary_large_image" />
```

如果安装了matplotlib，你还会看到社交卡片图片相关标签：

```html
<meta property="og:image" content="https://your-project.readthedocs.io/en/latest/_images/social_previews/summary_index_*.png" />
<meta property="og:image:width" content="1146" />
<meta property="og:image:height" content="600" />
<meta property="og:image:alt" content="页面描述文本" />
```

## 最小配置示例

一个完整的最小化 `conf.py` 配置：

```python
project = 'My Project'
copyright = '2025, Your Name'
author = 'Your Name'
release = '1.0.0'

extensions = [
    'sphinxext.opengraph',
]

html_theme = 'alabaster'

# Open Graph 配置
ogp_site_url = "https://my-project.readthedocs.io/en/latest/"
```

这就是全部！不需要其他配置即可生成完整的OGP标签。

## ReadTheDocs 零配置

如果你的文档托管在 ReadTheDocs 上，你甚至不需要设置 `ogp_site_url`。扩展会自动检测 `READTHEDOCS` 和 `READTHEDOCS_CANONICAL_URL` 环境变量：

```python
# conf.py - ReadTheDocs托管时最小配置
extensions = ['sphinxext.opengraph']
# ogp_site_url 不需要设置，自动检测！
```

当检测到 `READTHEDOCS` 环境变量存在时，扩展调用 `ambient_site_url()` 函数从 `READTHEDOCS_CANONICAL_URL` 解析出站点根URL。

## 验证社交卡片效果

构建完成后，可以使用以下方式预览社交卡片效果：

1. **[opengraph.xyz](https://www.opengraph.xyz/)**：输入你的文档URL，预览各平台展示效果
2. **[Twitter Card Validator](https://cards-dev.twitter.com/validator)**：预览Twitter/X卡片效果
3. **本地预览**：社交卡片PNG文件位于 `_build/html/_images/social_previews/` 目录，可直接打开查看

## 常见问题快速排查

**Q: 为什么看不到og:description标签？**
A: 确保你的页面有正文内容。描述是从doctree中提取的，如果页面只有标题没有段落文本，描述会为空。

**Q: 为什么没有生成社交卡片图片？**
A: 检查是否安装了matplotlib（`pip install matplotlib`）。如果matplotlib未安装，扩展会打印"matplotlib is not installed, social cards will not be generated"提示并跳过卡片生成。

**Q: 构建后页面中看不到任何OGP标签？**
A: 检查是否使用了epub构建器——epub构建器会被跳过（`app.builder.name == 'epub'` 时直接返回）。确保使用html构建器。

## 下一步

完成快速上手后，你可能想了解：

- [配置选项全解](/concepts/02-configuration.md) — 了解所有11个配置项的作用
- [核心标签生成流程](/concepts/03-tag-generation.md) — 理解标签生成的内部逻辑
- [社交卡片生成](/concepts/08-social-cards.md) — 自定义社交媒体预览图
- [页面级覆盖](/concepts/06-per-page-overrides.md) — 为特定页面定制OGP标签

## 相关概念

- [配置选项全解](/concepts/02-configuration.md)
- [核心标签生成流程](/concepts/03-tag-generation.md)
- [页面描述自动提取](/concepts/04-description-extraction.md)
- [基础配置示例](/examples/basic-setup.md)
- [sphinxext-opengraph 源码信源登记](/references/sphinxext-opengraph-source.md)
