---
type: concept
title: "Article 主题：单页文章布局"
description: "Article 主题的简洁设计——无侧边栏的单页文章布局，适合论文、报告和博客文章"
tags: [myst-theme, article-theme, remix, layout]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "themes/article/"
    facts: [F-026, F-027]
---

# Article 主题：单页文章布局

## 概述

Article 主题是 myst-theme 的轻量主题，面向单页文档：学术论文、技术报告、博客文章、新闻稿。与 Book 主题相比，它去除了多项目导航和侧边栏，聚焦于内容本身的阅读体验。

## 与 Book 主题的差异

| 特性 | Book 主题 | Article 主题 |
|------|----------|-------------|
| 页面结构 | 多页面站点 | 单页文章 |
| 侧边栏 | PrimarySidebar（项目 TOC） | 无 |
| 顶部导航 | TopNav（项目切换、搜索） | 简化导航 |
| 页内 TOC | 右侧 gutter | 可选（内容顶部或浮动） |
| 多项目 | 支持 | 不适用 |
| 路由复杂度 | `($project)/...$slug` | 直接页面路由 |
| 适用场景 | 文档站、书籍、课程 | 论文、报告、博客 |

## 核心组件

Article 主题包含：

- **Article**：文章主体容器，提供排版（prose 类）和最大宽度
- **ArticlePage**：完整页面布局（Article + 可选 FrontmatterBlock + Downloads）
- **ArticlePageAndNavigation**：带简化导航的文章页面
- **Downloads**：下载按钮组（PDF、LaTeX、DOCX 等格式导出链接）

## Frontmatter 渲染

Article 主题特别重视 frontmatter 的视觉呈现：

- 标题（大字号、居中或左对齐）
- 作者列表（带 ORCID 图标、机构上标）
- 机构/隶属关系
- 日期
- 摘要
- 关键词/标签
- 资助信息
- 许可证徽章
- 下载按钮（多种格式）
- 启动按钮（Binder/Colab/JupyterLite）

这些由 `@myst-theme/frontmatter` 的 `FrontmatterBlock` 组件渲染。

## 导出集成

Article 主题天然适合多格式导出场景。myst CLI 构建 Article 主题时，同一内容可以：
- 导出为 HTML 文章页（Article 主题渲染）
- 导出为 PDF（通过 LaTeX 或 Typst）
- 导出为 DOCX
- 导出为 JATS XML（学术出版）
- 导出为 Markdown

Downloads 组件自动展示可用的导出格式链接。
