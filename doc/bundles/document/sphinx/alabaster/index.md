---
okf_version: "0.2"
type: bundle
title: "Alabaster — Sphinx 默认主题"
description: "Alabaster 是 Sphinx 的默认 HTML 主题，极简、响应式、高度可配置，核心仅 130 行 Python 代码，是学习 Sphinx 主题开发的最佳范本"
tags: [sphinx, theme, html, alabaster, jinja2, pygments]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:02:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:02:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: alabaster-repo
    resource: https://github.com/sphinx-doc/alabaster
    title: Alabaster GitHub Repository
    author: team:sphinx-doc
  - id: alabaster-docs
    resource: https://alabaster.readthedocs.io/
    title: Alabaster Documentation
---

# Alabaster — Sphinx 默认主题

Alabaster 是 [Sphinx](/document/sphinx/index.md) 文档生成器的默认 HTML 主题，以视觉简洁、响应式布局、50+ 配置选项著称。它从 Sphinx 1.3 开始成为安装时依赖并设为默认主题，被 Requests、Fabric、Paramiko、Invoke 等知名 Python 项目使用。

> **核心特点**：核心代码仅 **2 个 Python 文件（~130 行）** + **5 个 Jinja2 模板**，是学习 Sphinx 主题开发的最小可行范本。

## 知识地图

```
alabaster/
├── 📖 concepts/       概念文档（7 篇）
│   ├── 入门：简介、快速开始
│   ├── 核心：四要素架构、setup 注册机制、配置选项体系
│   └── 进阶：侧边栏组件化、高级定制开发
├── 💡 examples/       实战示例（3 篇）
│   ├── 基础配置（完整 conf.py）
│   ├── 主题选项定制（7 个场景）
│   └── CSS 品牌化（深色模式、字体、布局）
└── 📚 references/     信源参考（1 篇）
    └── 源码路径映射
```

## 推荐学习路径

### 30 分钟快速上手

1. [简介](concepts/00-introduction.md) → 了解定位和特点（5 分钟）
2. [快速开始](concepts/01-getting-started.md) → 完成安装和最小配置（10 分钟）
3. [基础配置示例](examples/basic-setup.md) → 复制 conf.py 模板，构建你的第一个 Alabaster 文档（15 分钟）

### 深入理解架构（1-2 小时）

4. [主题架构四要素](concepts/02-theme-architecture.md) → entry point、theme.conf、模板继承、事件钩子
5. [setup 函数与注册机制](concepts/03-setup-and-registration.md) → 主题如何被 Sphinx 发现和加载
6. [主题配置选项体系](concepts/04-theme-options.md) → 50+ 选项的完整参考
7. [侧边栏组件化设计](concepts/05-sidebar-components.md) → 5 个组件的职责与组合

### 定制与二次开发

8. [主题选项定制示例](examples/custom-theme-options.md) → 7 个常见配置场景
9. [自定义 CSS 与品牌化](examples/custom-css-and-branding.md) → 品牌配色、深色模式、字体替换
10. [高级定制开发](concepts/06-customization-advanced.md) → Pygments 样式、模板覆盖、二次开发主题

## 核心洞察

| # | 洞察 | 一句话总结 |
|---|------|-----------|
| 1 | 极简架构范本 | 130 行 Python + 5 个模板即可实现生产级 Sphinx 主题 |
| 2 | 配置驱动样式 | 50+ CSS 变量式选项实现"配置即定制"，无需写 CSS |
| 3 | 侧边栏组件化 | 5 个独立模板通过 html_sidebars 自由组合 |
| 4 | 主题即扩展 | setup() 函数同时注册主题和扩展功能（事件钩子+Pygments） |
| 5 | 继承式定制 | 继承 basic 主题，只覆盖差异部分，避免重复造轮子 |

## 架构四要素速查

| 要素 | 关键文件/机制 | 作用 |
|------|-------------|------|
| Entry Point 注册 | `pyproject.toml` 中 `sphinx.html_themes` | 让 Sphinx 发现主题 |
| theme.conf 配置 | `[theme]` + `[options]` 两段 | 声明继承关系、样式表、默认选项 |
| Jinja2 模板继承 | `{% extends "basic/layout.html" %}` | 继承父主题，通过 block 覆盖定制 |
| 事件钩子 | `app.connect("html-page-context", ...)` | 在渲染前注入动态数据到模板上下文 |

## 相关知识束

| 知识束 | 关系 |
|--------|------|
| [sphinx](/document/sphinx/index.md) | Sphinx 核心——主题系统的底层框架 |
| [sphinx-autobuild](/document/sphinx/sphinx-autobuild/index.md) | 实时预览——开发主题时的热重载工具 |
| [sphinx-docker-images](/document/sphinx/sphinx-docker-images/index.md) | Docker 构建——CI/CD 环境下构建文档 |
| [conda-docs](/build/conda/conda-docs/index.md) | 多项目文档——Sphinx 配置深度定制的实战案例 |

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
