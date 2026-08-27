---
type: Concept
title: 页面级覆盖机制
description: 通过RST field lists为单个页面覆盖或添加任意OGP标签，包括禁用标签、自定义描述、图片和任意OGP属性
tags: [sphinxext-opengraph, per-page, field-lists, override, ogp_disable, arbitrary-tags]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T08:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: sphinxext-opengraph-source
    resource: /references/sphinxext-opengraph-source.md
    title: sphinxext-opengraph 源码信源登记
---

# 页面级覆盖机制

虽然全局配置可以统一设置站点的OGP行为，但不同页面可能需要不同的OGP标签——例如某个页面想使用特定的预览图、自定义描述，或者完全禁用OGP标签。sphinxext-opengraph 通过Sphinx的 **field lists** 机制支持页面级别的细粒度控制。

## 什么是 Field Lists

Field lists是reStructuredText的一种语法，表现为文档顶部以 `:字段名: 值` 形式排列的元数据块。Sphinx会自动解析这些字段，并通过 `context['meta']` 字典传递给扩展。

Field lists**必须放在文档最开头**（在标题之前），否则Sphinx不会将其识别为页面元数据，而是渲染为普通的定义列表。

## 支持的覆盖字段

### :ogp_disable: — 禁用OGP标签

设置此字段后，该页面不会生成任何OGP标签：

```rst
:ogp_disable:

==========
Secret Page
==========

This page should not have social preview.
```

源码处理（`get_tags()` 开头）：

```python
fields = context['meta']
if fields is None:
    fields = {}
if 'ogp_disable' in fields:
    return ''
```

直接返回空字符串，不生成任何meta标签。适用于不希望被分享或预览的页面（如内部页面、404页面等）。

### :ogp_description_length: — 覆盖描述长度

为特定页面设置不同的描述截断长度：

```rst
:ogp_description_length: 300

================
Long Article Page
================

This is a long article that needs a longer description...
```

源码处理：

```python
try:
    desc_len = int(fields.get('ogp_description_length', config.ogp_description_length))
except ValueError:
    desc_len = DEFAULT_DESCRIPTION_LENGTH
```

- 优先使用field值，回退到全局配置
- 值必须能转为整数，否则回退到默认值200
- 不需要给字段赋值，只写字段名即可启用（值可空）

### :og:description: — 覆盖OG描述

手动指定页面的 `og:description`，不使用自动提取的描述：

```rst
:og:description: This is my custom description for social sharing.

==========
My Article
==========
```

这是通过arbitrary tags机制实现的（所有 `og:` 开头的fields自动合并到tags字典）。

### :description: — 设置meta description

设置标准HTML meta description标签（非OGP）：

```rst
:description: Custom meta description for SEO purposes.

==========
My Article
==========
```

也可以使用Sphinx的meta指令实现相同效果：

```rst
.. meta::
   :description: Custom meta description for SEO purposes.
```

这两种方式设置的description会被 `_meta_parser.py` 中的 `get_meta_description()` 检测到，从而阻止扩展自动生成meta description（但og:description仍然会自动生成）。

### :og:title: — 覆盖OG标题

```rst
:og:title: Custom Social Media Title

==============================
Actual Document Title (Longer)
==============================
```

社交媒体分享时显示"Custom Social Media Title"而非页面的长标题。

### :og:type: — 覆盖OG类型

```rst
:og:type: article

==============
Blog Post Title
==============
```

将页面类型从默认的 `website` 改为 `article`，适合博客文章、新闻条目等。

### :og:image: — 设置页面图片

为特定页面设置预览图片：

```rst
:og:image: https://example.com/specific-image.png
:og:image:alt: Specific preview image for this page

==============
My Article
==============
```

**重要限制**：field lists中的图片URL**不支持相对路径**，必须使用绝对URL。源码注释和官方文档都明确指出了这一限制。

```python
if 'og:image' in fields:
    image_url = fields['og:image']
    # ... 后续处理中，field lists的图片跳过相对路径转换
```

在 `get_tags()` 的图片URL处理中，只有非field来源的图片才会进行相对路径解析：

```python
if 'og:image' not in fields:  # 关键判断
    image_url_parsed = urlparse(image_url)
    if not image_url_parsed.scheme:
        # 相对路径转换...
```

### :og:image:alt: — 设置图片alt文本

```rst
:og:image: https://example.com/image.png
:og:image:alt: A beautiful sunset over the mountains
```

如果不设置此值，社交卡片的alt文本会回退到页面描述。

## Arbitrary Tags：任意OGP标签

除了上述预设字段，你还可以添加**任意**以 `og:` 开头的字段，扩展会自动将其转换为meta标签：

```rst
:og:video: https://example.com/demo.mp4
:og:audio: https://example.com/podcast.mp3
:og:locale: zh_CN
:og:locale:alternate: en_US

==========
Multimedia Page
==========
```

源码实现：

```python
tags.update({k: v for k, v in fields.items() if k.startswith('og:')})
```

这一行代码是arbitrary tags机制的核心——遍历fields中所有键值对，将 `og:` 开头的键值合并到tags字典中。这意味着你可以添加任何OGP协议支持的标签，包括：

- `og:video` / `og:video:url` / `og:video:type` / `og:video:width` / `og:video:height`
- `og:audio` / `og:audio:url` / `og:audio:type`
- `og:locale` / `og:locale:alternate`
- `article:published_time` / `article:author` / `article:tag`
- `og:updated_time`
- 等等

### Twitter Cards 支持

虽然扩展自动设置了 `twitter:card = summary_large_image`（社交卡片模式），你可以通过 `ogp_custom_meta_tags` 添加更多Twitter标签，或在field lists中...等等，field lists的arbitrary tags只处理 `og:` 前缀的字段。Twitter标签需要通过全局配置添加：

```python
ogp_custom_meta_tags = [
    '<meta name="twitter:site" content="@yourhandle" />',
    '<meta name="twitter:creator" content="@authorhandle" />',
]
```

## Field Lists 使用注意事项

### 位置要求

Field lists**必须**放在文档的最开头（在任何标题或正文之前）：

```rst
:og:description: My custom description.  ← 正确位置

==========
Page Title
==========

Content...
```

```rst
==========
Page Title
==========

:og:description: My custom description.  ← 错误！会被渲染为普通文本
```

验证方法：构建后检查HTML输出，如果field lists没有出现在最终HTML中（被Sphinx消费了），说明位置正确。

### 值的格式

- Field lists的值是纯文本，不需要引号
- 值中可以包含空格和大部分标点
- 值中不能包含换行（field lists是单行的）

```rst
:og:title: This is a valid title with spaces and punctuation!
```

### 覆盖优先级总结

所有配置来源的优先级（从高到低）：

1. **页面field lists**（`:og:*` 字段）— 最高优先级，覆盖任何全局设置
2. **conf.py全局配置**（`ogp_*` 变量）
3. **环境自动检测**（ReadTheDocs）
4. **内置默认值**— 最低优先级

例外：`ogp_custom_meta_tags` 是追加而非覆盖——自定义标签始终被添加。

## 实际使用示例

### 博客文章页面

```rst
:og:type: article
:og:description: Learn how to use sphinxext-opengraph to add social media previews to your documentation.
:og:image: https://example.com/blog/ogp-tutorial-card.png

=====================================
Adding Social Previews to Your Sphinx Docs
=====================================

:author: John Doe
:date: 2025-01-15

Content of the blog post...
```

### 禁用特殊页面

```rst
:ogp_disable:

=====
Search
=====

.. searchpage::
```

### 多媒体页面

```rst
:og:type: video.movie
:og:image: https://example.com/video-thumb.jpg
:og:video: https://example.com/demo-video.mp4
:og:video:type: video/mp4
:og:video:width: 1280
:og:video:height: 720

============
Demo Video
============
```

### 多语言页面

```rst
:og:locale: zh_CN
:og:locale:alternate: en_US
:og:locale:alternate: ja_JP

============
国际化页面
============
```

## 相关概念

- [核心标签生成流程](03-tag-generation.md)
- [配置选项全解](02-configuration.md)
- [自定义Meta标签](09-custom-meta-tags.md)
- [页面级定制示例](../examples/per-page-customization.md)
- [sphinxext-opengraph 源码信源登记](../references/sphinxext-opengraph-source.md)
