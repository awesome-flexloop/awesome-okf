---
type: "index"
title: "Sphinx 文档生成器教程"
description: "Sphinx 9.1.1 源码学习教程——从入门到扩展开发的系统化知识，结合官方用户指南的实战教程"
tags: [sphinx, documentation, python, docs-generator]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T11:10:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: sphinx-init, resource: "sphinx/__init__.py", title: "Sphinx version info" }
  - { id: sphinx-app, resource: "sphinx/application.py", title: "Sphinx application class" }
  - { id: sphinx-config, resource: "sphinx/config.py", title: "Configuration system" }
  - { id: sphinx-events, resource: "sphinx/events.py", title: "Event system" }
  - { id: sphinx-builder, resource: "sphinx/builders/__init__.py", title: "Builder base class" }
  - { id: official-docs, resource: "https://www.sphinx-doc.org/en/master/", title: "Sphinx官方文档" }
---

# Sphinx 文档生成器教程

> 基于 Sphinx 9.1.1 源码（BSD-2-Clause）+ 官方用户指南的系统化学习教程

Sphinx 是 Python 生态最主流的文档生成器，最初为 Python 官方文档创建，现已成为开源社区广泛使用的文档工具。本教程从源码出发系统讲解核心架构与扩展机制，同时结合官方用户指南覆盖日常使用的全部场景。

## 快速导航

### 入门

| 文档 | 说明 |
|------|------|
| [Sphinx 简介](concepts/00-introduction.md) | 是什么、核心能力、与其他工具对比 |
| [5分钟快速上手](concepts/01-getting-started.md) | 安装（pip/conda/Docker）、初始化、构建、Markdown快速开始 |
| [架构总览](concepts/02-architecture-overview.md) | 核心类关系、构建管线、错误体系 |

### 核心架构（源码视角）

| 文档 | 说明 |
|------|------|
| [Sphinx应用类](concepts/03-application-class.md) | Sphinx主类、扩展API、build方法 |
| [配置系统](concepts/04-config-system.md) | Config类、_Opt、rebuild级别 |
| [事件系统](concepts/05-event-system.md) | 16个核心事件、优先级、订阅/发射 |
| [组件注册中心](concepts/06-registry.md) | Registry、组件注册、扩展加载 |
| [构建环境](concepts/07-build-environment.md) | BuildEnvironment、pickle缓存、增量构建 |
| [项目管理与Docutils集成](concepts/08-project-and-docutils.md) | Project类、Parser/Transform/Translator |

### 域与输出（源码视角）

| 文档 | 说明 |
|------|------|
| [Domain域系统](concepts/09-domain-system.md) | Domain基类、6大内置域、交叉引用解析 |
| [Builder构建器体系](concepts/10-builder-system.md) | 13种Builder、构建流程、并行构建 |
| [HTML构建器详解](concepts/11-html-builder.md) | StandaloneHTMLBuilder、模板、静态文件 |
| [Autodoc自动文档](concepts/12-autodoc.md) | 从docstring生成API文档 |
| [主题系统](concepts/13-theme-system.md) | 主题继承、配置、内置/第三方主题 |
| [Intersphinx跨项目引用](concepts/14-intersphinx.md) | 链接到外部Sphinx项目的文档 |

### 高级主题（源码视角）

| 文档 | 说明 |
|------|------|
| [扩展开发详解](concepts/15-extension-development.md) | 完整扩展开发指南、API分类 |
| [国际化与本地化](concepts/16-i18n.md) | gettext翻译工作流 |
| [搜索系统](concepts/17-search-system.md) | 客户端全文搜索实现 |

### 用户指南（使用视角）

| 文档 | 说明 |
|------|------|
| [reStructuredText基础语法](concepts/18-rest-primer.md) | reST完整入门：段落/列表/表格/代码块/指令/角色 |
| [Markdown与MyST支持](concepts/19-markdown-and-myst.md) | MyST-Parser配置、Markdown中指令/角色、Notebook集成 |
| [交叉引用完全指南](concepts/20-cross-references-guide.md) | :ref:/:doc:/:numref:/域角色/intersphinx引用大全 |
| [部署到线上](concepts/21-deployment.md) | RTD/GitHub Pages/GitLab Pages/Netlify部署方案 |
| [内置扩展完整参考](concepts/22-builtin-extensions.md) | 19个内置扩展详解与配置示例 |
| [LaTeX与PDF输出定制](concepts/23-latex-and-pdf.md) | xelatex配置、中文PDF、latex_elements/sphinxsetup定制 |
| [常见问题与故障排查](concepts/24-faq-troubleshooting.md) | 安装/构建/中文/性能常见问题与诊断命令 |
| [术语表](concepts/25-glossary.md) | Builder/Domain/Directive/Role等核心术语速查 |

### 实战示例

| 示例 | 说明 |
|------|------|
| [编写第一个Sphinx扩展](examples/01-first-extension.md) | Hello World扩展完整教程 |
| [自定义指令和角色](examples/02-custom-directive.md) | Directive/Role/Node/Transform实战 |
| [使用Autodoc生成API文档](examples/03-autodoc-api.md) | autodoc+napoleon配置和使用 |
| [自定义Builder输出Markdown](examples/04-custom-builder.md) | 创建Markdown Builder完整代码 |
| [部署到Read the Docs全流程](examples/05-readthedocs-deployment.md) | RTD配置、多版本管理、私有依赖处理 |

### API参考与信源

* [信源索引](references/index.md) — 源码关键片段、API参考手册、官方文档URL索引、reST语法速查表
* [Sphinx应用类API](references/application-api.md) — Sphinx类完整方法参考
* [事件系统API](references/events-api.md) — EventManager与核心事件参考
* [配置系统API](references/config-api.md) — Config/_Opt/ENUM API参考
* [组件注册表API](references/registry-api.md) — SphinxComponentRegistry方法参考
* [Builder基类API](references/builder-api.md) — Builder类属性与方法参考
* [核心事件完整列表](references/core-events-list.md) — 17个核心事件参数与触发时机
* [扩展元数据格式](references/extension-metadata.md) — ExtensionMetadata字段说明

## 学习路径建议

**使用者路径（写文档）**：
```
00 → 01 → 18（reST语法）→ 19（Markdown可选）→ 20（交叉引用）
       → 22（常用扩展）→ 21（部署）→ 24（遇到问题查FAQ）→ 25（术语速查）
```

**源码/扩展开发者路径（写插件）**：
```
00 → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08
  → 09 → 10 → 11 → 12 → 13 → 14
  → 15（扩展开发）→ examples/01-04 → 16 → 17
```

**PDF/出版路径**：
```
00 → 01 → 18（reST语法）→ 23（LaTeX/PDF定制）
```

## 源码版本

本教程基于 Sphinx **9.1.1**（beta开发版本），源码路径：`external/libs/docs/sphinx/`。用户指南部分基于 [Sphinx官方文档](https://www.sphinx-doc.org/en/master/) 最新版。

- 许可证：BSD-2-Clause
- Python要求：≥ 3.12
- 核心依赖：docutils ≥0.21、Jinja2 ≥3.1、Pygments ≥2.17、Babel ≥2.13
- Markdown支持：MyST-Parser ≥4.0（第三方扩展）

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
