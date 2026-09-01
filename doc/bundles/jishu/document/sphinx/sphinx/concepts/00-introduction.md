---
type: "concept"
title: Sphinx 简介
description: Sphinx是Python生态最主流的文档生成器，支持reStructuredText/Markdown、多输出格式、扩展机制和API文档自动生成。
tags: [sphinx, introduction, documentation, python]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:30:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-22T15:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: facts
    resource: /spec/facts.md
    title: Sphinx源码事实清单
  - id: application-api
    resource: /references/application-api.md
    title: Sphinx应用类API参考
---
# Sphinx 简介

Sphinx 是 Python 生态系统中最主流的文档生成工具，最初为 Python 官方文档而创建，现已成为众多开源项目（包括 Python 本身、Django、Flask、NumPy、PyTorch 等）的文档标准工具。

## 什么是 Sphinx

Sphinx 是一个将 reStructuredText（reST）或 Markdown 源文件转换为多种输出格式（HTML、PDF、ePub、man page 等）的文档生成器。它不仅仅是简单的标记语言转换器，而是一个完整的文档工程框架：

- **智能交叉引用**：自动为函数、类、章节、引用建立链接，支持跨文档和跨项目引用（intersphinx）
- **层次化结构**：通过 toctree 指令组织文档树结构
- **自动API文档**：从 Python 源代码 docstring 自动生成 API 文档（autodoc 扩展）
- **多输出格式**：一次编写，输出 HTML、LaTeX/PDF、ePub、Texinfo、man page、纯文本、XML 等
- **扩展体系**：丰富的内置扩展和第三方扩展生态
- **主题系统**：可切换的 HTML 主题，支持自定义主题
- **多语言支持**：内置国际化（i18n）支持，文档可翻译为多种语言

## 核心特性

| 特性 | 说明 |
|------|------|
| 📝 标记语言 | 原生 reStructuredText，通过 MyST 扩展支持 Markdown |
| 🔗 交叉引用 | 语义化引用角色（:class:、:func:、:mod: 等），自动解析 |
| 🌳 文档树 | toctree 指令声明式组织文档层次 |
| 🤖 API文档 | autodoc + napoleon 支持 NumPy/Google 风格 docstring |
| 🔍 全文搜索 | 内置离线全文搜索（HTML输出） |
| 🎨 主题 | 内置10+主题，支持第三方主题（如 Read the Docs） |
| 🔌 扩展 | 50+内置扩展，PyPI 上数百个第三方扩展 |
| 🌐 多语言 | gettext 兼容的翻译工作流 |
| 📦 多输出 | HTML/PDF/ePub/man/TeXinfo/text/XML |

## 技术栈

- **语言**：Python 3.10+（Sphinx 9.x）
- **核心依赖**：docutils（reST解析基础库）、Jinja2（模板引擎）、Pygments（语法高亮）
- **构建系统**：自有的增量构建引擎，通过 environment.pickle 缓存解析结果
- **版本**：当前版本 9.1.1（beta），见 [F-001](../spec/facts.md)

## 架构概览

Sphinx 采用"应用-事件-注册表"三位一体的核心架构（见 [I-001](../spec/insights.md)）：

```
┌─────────────────────────────────────────────────────┐
│                    Sphinx App                       │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Config   │  │EventManager  │  │  Registry    │  │
│  │ (配置)   │  │ (事件总线)   │  │ (组件注册)   │  │
│  └──────────┘  └──────────────┘  └──────────────┘  │
│                                                     │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Project  │  │BuildEnvironment│  │   Builder   │  │
│  │ (源文件) │  │ (doctree缓存)│  │ (输出格式)  │  │
│  └──────────┘  └──────────────┘  └──────────────┘  │
│                                                     │
│  Extensions: setup(app) → add_* + connect()         │
└─────────────────────────────────────────────────────┘
```

- **Sphinx App** 是中心编排器，持有所有子系统引用
- **Config** 管理 conf.py 配置和扩展注册的配置值
- **EventManager** 提供松耦合的扩展点（17个核心事件）
- **Registry** 统一注册所有可扩展组件（Builder、Domain、Directive、Role 等）
- **BuildEnvironment** 是增量构建的核心，缓存解析后的 doctree
- **Builder** 负责将 doctree 转换为最终输出格式
- **扩展** 通过 `setup(app)` 函数调用 app.add_* 和 app.connect() 接入

## 源码目录结构

Sphinx 源码位于 `sphinx/` 包下，主要模块：

| 目录 | 职责 |
|------|------|
| `sphinx/application.py` | Sphinx 主类和扩展 API |
| `sphinx/config.py` | 配置系统 |
| `sphinx/events.py` | 事件系统 |
| `sphinx/registry.py` | 组件注册表 |
| `sphinx/builders/` | 各格式构建器 |
| `sphinx/domains/` | 语言领域（py/c/cpp/js/rst/std等） |
| `sphinx/directives/` | 内置 reST 指令实现 |
| `sphinx/roles/` | 内置角色实现 |
| `sphinx/transforms/` | 文档转换器 |
| `sphinx/writers/` | 输出写入器 |
| `sphinx/environment/` | 构建环境 |
| `sphinx/ext/` | 内置扩展（autodoc/intersphinx等） |
| `sphinx/util/` | 工具函数库 |
| `sphinx/themes/` | 内置主题 |

## 相关概念

- [01-快速开始](01-getting-started.md) — 安装和第一个Sphinx项目
- 02-应用类 — Sphinx主类详解
- 07-扩展开发 — 如何编写Sphinx扩展
