---
okf_version: "0.2"
---

# sphinxext-opengraph

**sphinxext-opengraph** 是一个 Sphinx 扩展，在构建HTML文档时自动为每个页面生成 [Open Graph Protocol (OGP)](https://ogp.me/) 元数据标签。这些标签让社交媒体平台（Twitter/X、LinkedIn、Facebook、Slack、Discord等）在分享文档链接时展示丰富的预览卡片，包含标题、描述、缩略图等信息，显著提升文档链接的点击率和专业形象。

## 版本信息

- **版本**：0.13.0
- **Python 要求**：≥ 3.9
- **Sphinx 要求**：≥ 6.0
- **可选依赖**：matplotlib ≥ 3（社交卡片PNG生成）
- **许可证**：BSD-3-Clause
- **源码仓库**：[sphinx-doc/sphinxext-opengraph](https://github.com/sphinx-doc/sphinxext-opengraph)
- **官方文档**：[sphinxext-opengraph.readthedocs.io](https://sphinxext-opengraph.readthedocs.io/)

## 核心能力

- **自动OGP标签生成**：为每个HTML页面自动生成 og:title、og:type、og:url、og:site_name、og:description、og:image 等核心标签
- **智能描述提取**：通过 docutils NodeVisitor 遍历doctree，自动提取页面描述文本，智能跳过标题、代码块、警告框等
- **四级图片回退**：页面级指定 → 首图自动检测 → 全局默认图 → Matplotlib自动生成社交卡片
- **社交卡片自动生成**：使用Matplotlib为每页生成1146×600px的PNG预览图，支持自定义颜色、字体、logo
- **ReadTheDocs零配置**：在RTD上自动检测站点URL，无需手动设置 ogp_site_url
- **页面级灵活覆盖**：通过RST field lists为任意页面覆盖OGP标签，支持添加任意自定义OGP属性
- **版本化文档支持**：ogp_canonical_url 配置让社交分享链接指向stable版本
- **并行构建安全**：支持Sphinx并行读写构建，Matplotlib对象缓存复用提升构建性能
- **优雅降级**：matplotlib未安装时社交卡片功能静默禁用，不影响基础功能

## 快速开始

1. 安装：`pip install sphinxext-opengraph[social_cards]`
2. 在 `conf.py` 添加：`extensions = ['sphinxext.opengraph']`
3. 设置站点URL：`ogp_site_url = 'https://your-docs.readthedocs.io/en/latest/'`
4. 构建：`make html`

## 文档结构

### 概念文档（Concepts）

按学习路径分为入门篇、核心篇、高级篇三个层次：

**入门篇**：
- [简介](concepts/00-introduction.md) — 功能概览、OGP协议背景、设计理念、安装方法
- [5分钟快速上手](concepts/01-getting-started.md) — 最小配置、构建验证、常见问题

**核心篇**：
- [配置选项全解](concepts/02-configuration.md) — 11个配置项的完整说明
- [核心标签生成流程](concepts/03-tag-generation.md) — html-page-context事件、get_tags()函数、make_tag()输出
- [页面描述自动提取](concepts/04-description-extraction.md) — DescriptionParser遍历逻辑、跳过规则、文本清洗
- [页面图片处理逻辑](concepts/05-image-handling.md) — 四级图片回退、相对路径解析、alt文本链
- [页面级覆盖机制](concepts/06-per-page-overrides.md) — field lists语法、arbitrary tags、ogp_disable

**高级篇**：
- [ReadTheDocs 自动检测与集成](concepts/07-readthedocs-integration.md) — ambient_site_url()、canonical URL、版本化文档
- [社交卡片生成](concepts/08-social-cards.md) — Matplotlib渲染、缓存复用、布局设计、字体配置
- [自定义Meta标签与扩展协作](concepts/09-custom-meta-tags.md) — Twitter Cards、Article标签、与其他扩展共存

### 示例文档（Examples）

- [基础配置示例](examples/basic-setup.md) — 从零开始的最小可用配置
- [社交卡片完整配置示例](examples/social-cards-example.md) — 自定义卡片外观、字体、颜色
- [页面级定制示例](examples/per-page-customization.md) — field lists覆盖实战、多媒体页面、禁用页面
- [高级配置示例](examples/advanced-config.md) — 版本化文档、多语言站点、博客配置、本地开发优化

### 信源登记（References）

- [sphinxext-opengraph 源码信源登记](references/sphinxext-opengraph-source.md) — v0.13.0 源码路径、版本信息、核心模块清单、配置项与公开API完整列表
