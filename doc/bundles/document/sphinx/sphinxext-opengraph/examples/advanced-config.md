---
type: Example
title: 高级配置示例
description: 包含版本化文档canonical URL、Twitter Cards、Article元数据、自定义标签等高级配置的完整conf.py示例
tags: [sphinxext-opengraph, example, advanced, canonical-url, twitter-cards, article-tags, versioned-docs]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T08:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: sphinxext-opengraph-source
    resource: /references/sphinxext-opengraph-source.md
    title: sphinxext-opengraph 源码信源登记
---

# 高级配置示例

本示例展示sphinxext-opengraph在复杂场景下的完整配置，包括版本化文档、多语言站点、Twitter Cards集成、自定义标签等。

## 完整高级 conf.py 示例

```python
# conf.py - 完整高级配置示例

from __future__ import annotations
import os
import sys
from pathlib import Path

# -- Project information -----------------------------------------------------
project = 'MyProject'
copyright = '2025, MyProject Team'
author = 'MyProject Team'

# 从包导入版本号
try:
    import myproject
    version = myproject.__version__
    release = version
except ImportError:
    version = 'latest'
    release = 'latest'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinxext.opengraph',
    'sphinx_sitemap',       # 配合站点地图
    'sphinx_design',        # 配合UI组件
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'furo'
html_static_path = ['_static']
html_logo = '_static/logo.png'
html_favicon = '_static/favicon.ico'

# -- Sitemap configuration (sphinx-sitemap) ---------------------------------
html_baseurl = 'https://myproject.readthedocs.io/en/latest/'

# -- Open Graph configuration ------------------------------------------------

# 基础URL配置
ogp_site_url = f'https://myproject.readthedocs.io/en/{version}/'

# Canonical URL：社交分享指向stable版本（如果当前是latest）
if version == 'latest':
    ogp_canonical_url = 'https://myproject.readthedocs.io/en/stable/'
else:
    ogp_canonical_url = ogp_site_url

# 描述配置
ogp_description_length = 200
ogp_enable_meta_description = True

# 站点信息
ogp_site_name = 'MyProject Documentation'
ogp_type = 'website'

# 图片配置：不设置全局默认图片，优先使用页面首图，
# 无图时自动生成社交卡片
ogp_use_first_image = True
ogp_image_alt = 'MyProject Documentation'

# 社交卡片配置
ogp_social_cards = {
    "enable": True,
    "image": "_static/og-logo.png",       # 右上角大图
    "line_color": "#2980B9",              # 蓝色主题线
    "font": "Noto Sans CJK SC",           # 中文字体支持
    "description_max_length": 160,
}

# 自定义meta标签
ogp_custom_meta_tags = [
    # Twitter Cards
    '<meta name="twitter:card" content="summary_large_image" />',
    '<meta name="twitter:site" content="@myproject" />',
    '<meta name="twitter:creator" content="@myproject_team" />',

    # Facebook App ID（如需要Facebook Insights）
    '<meta property="fb:app_id" content="1234567890" />',

    # 多语言替代版本（如适用）
    '<meta property="og:locale" content="en_US" />',
    '<meta property="og:locale:alternate" content="zh_CN" />',
    '<meta property="og:locale:alternate" content="ja_JP" />',

    # 忽略canonical标签（某些SEO场景）
    # '<meta property="og:ignore_canonical" content="true" />',
]
```

## 版本化文档配置详解

对于有多个版本的文档（latest/stable/v1.x/v2.x），推荐的配置策略：

```python
# conf.py - 版本化文档配置

# 检测RTD环境
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if on_rtd:
    # RTD自动设置READTHEDOCS_VERSION环境变量
    rtd_version = os.environ.get('READTHEDOCS_VERSION', 'latest')
    ogp_site_url = f'https://myproject.readthedocs.io/en/{rtd_version}/'

    # stable版本使用自身URL作为canonical
    if rtd_version == 'stable':
        ogp_canonical_url = ogp_site_url
    else:
        # 其他版本（latest/旧版本）指向stable
        ogp_canonical_url = 'https://myproject.readthedocs.io/en/stable/'
else:
    # 本地构建
    ogp_site_url = 'http://localhost:8000/'
    ogp_social_cards = {"enable": False}  # 本地构建禁用卡片加快速度
```

### 为什么需要 ogp_canonical_url？

假设用户访问 `en/latest/api.html` 并分享链接：
- 如果不设置 `ogp_canonical_url`，`og:url` 指向latest版URL
- 搜索引擎和社交平台可能将latest和stable视为重复内容
- 设置后，`og:url` 指向stable版URL，集中SEO权重

## 多语言站点配置

```python
# conf.py - 多语言配置

# 语言检测（根据构建参数）
language = os.environ.get('SPHINX_LANGUAGE', 'en')

ogp_site_url = f'https://myproject.readthedocs.io/{language}/latest/'

ogp_custom_meta_tags = [
    f'<meta property="og:locale" content="{language_map[language]}" />',
]

# 添加其他语言作为alternate
for lang_code, og_locale in language_map.items():
    if lang_code != language:
        ogp_custom_meta_tags.append(
            f'<meta property="og:locale:alternate" content="{og_locale}" />'
        )
```

其中 `language_map` 映射Sphinx语言代码到OG locale代码：

```python
language_map = {
    'en': 'en_US',
    'zh': 'zh_CN',
    'ja': 'ja_JP',
    'fr': 'fr_FR',
    'de': 'de_DE',
}
```

## 博客/文章站点配置

对于包含博客文章的文档站点：

```python
# conf.py - 博客类站点配置

# 默认OG类型为website
ogp_type = 'website'

# 博客文章页面通过field list覆盖为article
# 在每个博客文章的.rst文件顶部：
# :og:type: article

ogp_custom_meta_tags = [
    '<meta name="twitter:card" content="summary_large_image" />',
    '<meta name="twitter:site" content="@myproject" />',
    # article:published_time和article:author
    # 通过页面field list或模板设置
]
```

博客文章页面的field lists示例：

```rst
:og:type: article
:og:title: My Amazing Blog Post Title for Social Media
:og:description: A compelling description that makes people want to click and read more.
:og:image: https://myproject.readthedocs.io/en/latest/_static/blog/my-post-card.png
:article:published_time: 2025-01-15T09:00:00Z
:article:author: Jane Developer
:article:section: Tutorials
:article:tag: Python
:article:tag: Sphinx

==========================
Blog Post Title
==========================

:author: Jane Developer
:date: 2025-01-15

Content...
```

## 本地开发优化配置

本地开发时加快构建速度、避免不必要的社交卡片生成：

```python
# conf.py - 本地开发配置

# 检测本地构建
if not os.environ.get('READTHEDOCS') and not os.environ.get('CI'):
    # 本地开发配置
    ogp_site_url = 'http://127.0.0.1:8000/'
    ogp_social_cards = {
        "enable": False,  # 禁用社交卡片加速构建
    }
    ogp_enable_meta_description = True
```

## 与furo主题配合

furo主题原生支持 `metatags`，无需额外配置。但可以通过主题选项进一步定制：

```python
html_theme = 'furo'
html_theme_options = {
    # furo的社交媒体按钮（与OGP标签独立）
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/myorg/myproject",
            "html": "...",
            "class": "",
        },
    ],
}
```

## 与sphinx-rtd-theme配合

```python
html_theme = 'sphinx_rtd_theme'

# sphinx-rtd-theme 同样支持metatags，无需额外配置
```

## 验证配置正确性

构建完成后，运行以下检查：

### 1. 检查HTML输出中的meta标签

```bash
grep -o '<meta[^>]*og:[^>]*>' _build/html/index.html
```

### 2. 检查社交卡片文件是否生成

```bash
ls _build/html/_images/social_previews/
```

### 3. 使用Python验证

```python
from pathlib import Path
from html.parser import HTMLParser

class OGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.og_tags = {}
    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            attrs_dict = dict(attrs)
            prop = attrs_dict.get('property', '')
            if prop.startswith('og:'):
                self.og_tags[prop] = attrs_dict.get('content', '')

with open('_build/html/index.html', encoding='utf-8') as f:
    html = f.read()

parser = OGParser()
parser.feed(html)
for tag, content in sorted(parser.og_tags.items()):
    print(f'{tag}: {content[:80]}...' if len(content) > 80 else f'{tag}: {content}')
```

## 相关概念

- [配置选项全解](/concepts/02-configuration.md)
- [ReadTheDocs 自动检测与集成](/concepts/07-readthedocs-integration.md)
- [社交卡片生成](/concepts/08-social-cards.md)
- [自定义Meta标签与扩展协作](/concepts/09-custom-meta-tags.md)
- [页面级定制示例](/examples/per-page-customization.md)
- [sphinxext-opengraph 源码信源登记](/references/sphinxext-opengraph-source.md)
