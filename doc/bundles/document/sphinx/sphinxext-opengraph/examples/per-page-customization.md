---
type: Example
title: 页面级定制示例
description: 使用RST field lists为特定页面自定义OGP标签，包括自定义标题/描述/图片、添加视频标签、禁用页面等实战示例
tags: [sphinxext-opengraph, example, per-page, field-lists, override, custom-tags]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T08:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: sphinxext-opengraph-source
    resource: /references/sphinxext-opengraph-source.md
    title: sphinxext-opengraph 源码信源登记
---

# 页面级定制示例

本示例演示如何使用reStructuredText field lists为单个页面定制Open Graph标签，覆盖全局配置或添加页面特有的元数据。

## Field Lists基本语法

Field lists必须放在**文档最开头**（在标题之前），格式为：

```rst
:字段名: 字段值

========
页面标题
========

正文内容...
```

## 示例1：自定义页面描述

为特定页面设置自定义社交分享描述，不使用自动提取的文本：

```rst
:og:description: 学习如何在5分钟内为你的Sphinx文档添加社交媒体预览卡片，提升文档分享效果。

=====================================
快速入门：为文档添加社交分享预览
=====================================

本章将带你快速了解 sphinxext-opengraph 的基本用法...
```

构建后，该页面的 `og:description` 和 `meta description` 将使用你指定的文本。

## 示例2：自定义页面标题

社交媒体分享时显示更吸引人的标题：

```rst
:og:title: 5分钟搞定文档社交预览 — sphinxext-opengraph完全指南

=====================================
sphinxext-opengraph 快速入门
=====================================
```

这样页面的HTML标题（浏览器标签栏显示）仍然是"Sphinx文档标题"，但社交媒体分享时显示自定义的更吸引眼球的标题。

## 示例3：指定页面预览图

为重要页面设置专属预览图片：

```rst
:og:image: https://example.com/images/tutorial-social-card.png
:og:image:alt: 教程预览图：Sphinx + 社交媒体图标

=====================================
教程：从零搭建文档站点
=====================================
```

**注意**：field lists中的图片URL必须是**绝对URL**（以http://或https://开头），不支持相对路径。

## 示例4：设置文章类型和作者标签

博客文章类页面使用article类型，并添加文章相关标签：

```rst
:og:type: article
:og:description: 深入解析Python 3.13的GIL移除实验，了解自由线程模式的性能影响。
:article:published_time: 2025-01-15
:article:author: John Doe
:article:section: Python Internals
:article:tag: Python
:article:tag: GIL
:article:tag: Free-threading

=====================================
Python 3.13 GIL移除深度解析
=====================================

:author: John Doe
:date: 2025-01-15

Python 3.13引入了实验性的自由线程模式...
```

注意：`article:*` 标签虽然不是 `og:` 前缀，但会通过arbitrary tags机制添加（所有以 `og:` 或其他OGP命名空间开头的字段都会被处理——实际上源码只合并 `og:` 前缀的字段，`article:` 需要通过全局 `ogp_custom_meta_tags` 配置）。对于页面级别的article标签，建议结合模板使用。

## 示例5：自定义描述长度

长文页面使用更长的描述：

```rst
:ogp_description_length: 400

=====================================
深度技术指南
=====================================

这是一篇非常长的技术文章...
```

或者短页面使用更短的描述：

```rst
:ogp_description_length: 100

=====
FAQ
=====

常见问题解答...
```

如果字段值不是有效整数，会回退到全局配置的 `ogp_description_length`（默认200）。

## 示例6：禁用特定页面的OGP标签

某些页面（如搜索页、404页、内部页面）不需要社交分享：

```rst
:ogp_disable:

======
搜索
======

.. search::
```

或者内部参考页面：

```rst
:ogp_disable:

================
内部API参考（草稿）
================

.. warning:: 本页为内部草稿，请勿分享。
```

设置后该页面不会生成任何OGP meta标签。

## 示例7：多媒体内容页面

为包含视频的页面添加视频标签：

```rst
:og:type: video.other
:og:image: https://example.com/thumbs/demo-screenshot.jpg
:og:image:alt: 演示视频截图
:og:video: https://example.com/videos/demo.mp4
:og:video:type: video/mp4
:og:video:width: 1280
:og:video:height: 720

================
产品演示视频
================

.. raw:: html

   <video controls>
     <source src="_static/demo.mp4" type="video/mp4">
   </video>
```

## 示例8：多字段组合

一个页面可以同时使用多个field lists：

```rst
:og:title: Sphinx文档社交分享最佳实践（2025更新）
:og:description: 全面掌握sphinxext-opengraph配置，从基础标签到自定义社交卡片，让你的技术文档在社交媒体上脱颖而出。
:og:image: https://example.com/images/best-practices-2025.png
:og:image:alt: 2025年Sphinx文档社交预览最佳实践指南封面
:og:type: article
:ogp_description_length: 300

=====================================
Sphinx文档社交分享最佳实践
=====================================

在本文中，我们将探讨...
```

## Field Lists与Sphinx meta指令对比

除了field lists，Sphinx还提供了 `.. meta::` 指令来设置meta标签：

```rst
.. meta::
   :description: 这是meta指令设置的description
   :keywords: sphinx, opengraph, documentation

=====================================
页面标题
=====================================
```

两种方式的区别：

| 特性 | field lists (`:field:`) | `.. meta::` 指令 |
|------|------------------------|------------------|
| 位置 | 必须在标题之前 | 可在文档任意位置 |
| 可见性 | 不会渲染到HTML输出 | 不会渲染到HTML输出 |
| og:* 标签 | ✅ 支持 | ❌ 需要手动写HTML |
| description | 通过og:description | ✅ 直接设置name=description |
| ogp_disable | ✅ 支持 | ❌ 不支持 |
| ogp_description_length | ✅ 支持 | ❌ 不支持 |

对于sphinxext-opengraph的覆盖功能，推荐使用field lists；对于标准HTML meta标签，两种方式都可以。

## 常见错误

### 错误1：Field lists放在标题之后

```rst
==========
页面标题    ← 标题在field lists之前
==========

:og:description: 我的描述  ← 错误！这会被渲染为普通文本

正文...
```

**正确做法**：field lists必须在文档最开头。

### 错误2：Field lists中使用相对图片路径

```rst
:og:image: _static/my-image.png  ← 错误！相对路径不被解析
```

**正确做法**：使用绝对URL。

### 错误3：Field lists值中包含换行

Field lists是单行的，值中不能换行。如果需要长描述，保持在一行内：

```rst
:og:description: 这是一段较长的描述文本，虽然很长但必须保持在同一行内，不能换行。
```

## 相关概念

- [页面级覆盖机制](/concepts/06-per-page-overrides.md)
- [核心标签生成流程](/concepts/03-tag-generation.md)
- [配置选项全解](/concepts/02-configuration.md)
- [基础配置示例](/examples/basic-setup.md)
- [高级配置示例](/examples/advanced-config.md)
- [sphinxext-opengraph 源码信源登记](/references/sphinxext-opengraph-source.md)
