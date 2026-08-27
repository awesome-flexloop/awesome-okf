---
type: Concept
title: Alabaster 简介
description: Alabaster 是什么——Sphinx 默认主题的定位、特点、历史渊源与设计理念
tags: [sphinx, theme, alabaster, introduction]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:52:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: alabaster-source
    resource: /references/alabaster-source.md
    title: Alabaster 源码路径映射
---

# Alabaster 简介

Alabaster 是 [Sphinx](https://www.sphinx-doc.org/) 文档生成器的默认 HTML 主题，以简洁、响应式、高度可配置著称。它从 Sphinx 1.3 版本开始成为 Sphinx 安装时的依赖并被设为默认主题，是 Python 生态最广泛使用的文档主题之一。

## 定位与特点

Alabaster 的设计目标是提供一个视觉干净（clean）、响应式、可配置的文档主题，核心特点包括：

- **极简代码base**：核心仅 2 个 Python 文件（约 130 行）+ 5 个 Jinja2 模板，是学习 Sphinx 主题开发的最佳入门范本
- **高度可配置**：通过 50+ 个 `html_theme_options` 配置项控制颜色、字体、布局、侧边栏组件、服务链接等，无需写 CSS 即可定制外观
- **组件化侧边栏**：5 个独立模板组件（about/navigation/relations/donate/searchfield）可自由组合
- **响应式布局**：支持桌面端固定侧边栏和移动端自适应布局
- **内置服务集成**：GitHub 按钮/角标、Google Analytics、Travis-CI/CodeCov 徽章、Open Collective/Tidelift 捐赠链接

## 历史渊源

Alabaster 并非从零设计——它的视觉血统可以追溯到 Python 社区多个经典主题：

1. **Armin Ronacher 的 Flask 主题**：最初的设计基础
2. **Kenneth Reitz 的 krTheme**：在 Flask 主题基础上改进，被 Requests 项目使用
3. **Alabaster**：Jeff Forcier 在 krTheme 基础上修改并获得许可后发布，增加了大量定制选项和改进

这种"站在前人肩膀上"的演进方式也体现在它的技术架构中——Alabaster 继承 Sphinx 内置的 basic 主题，只覆盖差异部分。

## 适用场景

Alabaster 适合以下场景：

- **Python 开源项目文档**：Requests、Fabric、Paramiko、Invoke 等知名项目均使用 Alabaster 或其衍生主题
- **API 文档**：简洁的单列布局和侧边栏导航非常适合技术参考文档
- **个人/团队博客文档**：支持自定义 Logo、描述、外部链接

如果你的项目需要更复杂的导航（如顶部导航栏、多版本切换），可能需要考虑 sphinx-rtd-theme、Furo、PyData Sphinx Theme 等更重型的主题。

## 环境要求

- Python 3.10+
- Sphinx 6.2+
- Pygments（Sphinx 依赖，用于代码高亮）

Alabaster 本身没有第三方 Python 依赖（除了 Sphinx），安装 Sphinx 时会自动安装。

## 相关概念

- [快速开始](01-getting-started.md)
- [主题架构四要素](02-theme-architecture.md)
- [Sphinx 核心主题系统](../../sphinx/concepts/13-theme-system.md)
