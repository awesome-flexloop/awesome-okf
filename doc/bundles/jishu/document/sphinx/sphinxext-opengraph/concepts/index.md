# 概念文档（Concepts）

本目录包含 sphinxext-opengraph 的结构化概念文档，按学习路径分为入门篇、核心篇和高级篇三个层次。

## 入门篇

- [sphinxext-opengraph 简介](00-introduction.md) — 功能概述、Open Graph协议背景、设计理念、安装方法与适用场景
- [5分钟快速上手](01-getting-started.md) — 从安装到配置到验证的完整快速入门流程，最小可用配置与构建验证

## 核心篇

- [配置选项全解](02-configuration.md) — 11个conf.py配置项的类型、默认值、用法示例与注意事项
- [核心标签生成流程](03-tag-generation.md) — 深入解析get_tags()函数，从事件触发到meta标签HTML输出的完整流程
- [页面描述自动提取](04-description-extraction.md) — DescriptionParser如何从doctree智能提取页面描述，包括跳过规则、文本清洗和长度截断
- [页面图片处理逻辑](05-image-handling.md) — 四级图片来源回退机制（页面覆盖/全局配置/首图检测/社交卡片）、相对路径解析与alt文本
- [页面级覆盖机制](06-per-page-overrides.md) — 通过RST field lists为单个页面覆盖或添加任意OGP标签

## 高级篇

- [ReadTheDocs 自动检测与集成](07-readthedocs-integration.md) — RTD环境URL自动检测、canonical URL配置、版本化文档最佳实践
- [社交卡片生成](08-social-cards.md) — 基于Matplotlib的社交预览卡片生成机制，图片渲染、缓存复用、样式自定义与字体配置
- [自定义Meta标签与扩展协作](09-custom-meta-tags.md) — 通过ogp_custom_meta_tags添加Twitter Cards、Article元数据，以及与其他扩展的协作注意事项

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-configuration
03-tag-generation
04-description-extraction
05-image-handling
06-per-page-overrides
07-readthedocs-integration
08-social-cards
09-custom-meta-tags
```
