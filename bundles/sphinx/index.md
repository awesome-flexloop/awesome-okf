---
type: "index"
title: "Sphinx 文档生成器教程"
description: "Sphinx 9.1.1 源码学习教程——从入门到扩展开发的系统化知识"
tags: [sphinx, documentation, python, docs-generator]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: sphinx-init, resource: "sphinx/__init__.py", title: "Sphinx version info" }
  - { id: sphinx-app, resource: "sphinx/application.py", title: "Sphinx application class" }
  - { id: sphinx-config, resource: "sphinx/config.py", title: "Configuration system" }
  - { id: sphinx-events, resource: "sphinx/events.py", title: "Event system" }
  - { id: sphinx-builder, resource: "sphinx/builders/__init__.py", title: "Builder base class" }
---

# Sphinx 文档生成器教程

> 基于 Sphinx 9.1.1 源码（BSD-2-Clause）的系统化学习教程

Sphinx 是 Python 生态最主流的文档生成器，最初为 Python 官方文档创建，现已成为开源社区广泛使用的文档工具。本教程从源码出发，系统讲解 Sphinx 的核心架构、扩展机制和实战用法。

## 快速导航

### 入门

| 文档 | 说明 |
|------|------|
| [Sphinx 简介](concepts/00-introduction.md) | 是什么、核心能力、与其他工具对比 |
| [5分钟快速上手](concepts/01-getting-started.md) | 安装、初始化、构建、conf.py配置 |
| [架构总览](concepts/02-architecture-overview.md) | 核心类关系、构建管线、错误体系 |

### 核心架构

| 文档 | 说明 |
|------|------|
| [Sphinx应用类](concepts/03-application-class.md) | Sphinx主类、扩展API、build方法 |
| [配置系统](concepts/04-config-system.md) | Config类、_Opt、rebuild级别 |
| [事件系统](concepts/05-event-system.md) | 16个核心事件、优先级、订阅/发射 |
| [组件注册中心](concepts/06-registry.md) | Registry、组件注册、扩展加载 |
| [构建环境](concepts/07-build-environment.md) | BuildEnvironment、pickle缓存、增量构建 |
| [项目管理与Docutils集成](concepts/08-project-and-docutils.md) | Project类、Parser/Transform/Translator |

### 领域与输出

| 文档 | 说明 |
|------|------|
| [Domain领域系统](concepts/09-domain-system.md) | Domain基类、6大内置域、交叉引用解析 |
| [Builder构建器体系](concepts/10-builder-system.md) | 13种Builder、构建流程、并行构建 |
| [HTML构建器详解](concepts/11-html-builder.md) | StandaloneHTMLBuilder、模板、静态文件 |
| [Autodoc自动文档](concepts/12-autodoc.md) | 从docstring生成API文档 |
| [主题系统](concepts/13-theme-system.md) | 主题继承、配置、内置/第三方主题 |
| [Intersphinx跨项目引用](concepts/14-intersphinx.md) | 链接到外部Sphinx项目的文档 |

### 高级主题

| 文档 | 说明 |
|------|------|
| [扩展开发详解](concepts/15-extension-development.md) | 完整扩展开发指南、API分类 |
| [国际化与本地化](concepts/16-i18n.md) | gettext翻译工作流 |
| [搜索系统](concepts/17-search-system.md) | 客户端全文搜索实现 |

### 实战示例

| 示例 | 说明 |
|------|------|
| [编写第一个Sphinx扩展](examples/01-first-extension.md) | Hello World扩展完整教程 |
| [自定义指令和角色](examples/02-custom-directive.md) | Directive/Role/Node/Transform实战 |
| [使用Autodoc生成API文档](examples/03-autodoc-api.md) | autodoc+napoleon配置和使用 |
| [自定义Builder输出Markdown](examples/04-custom-builder.md) | 创建Markdown Builder完整代码 |

### 信源登记簿

* [信源登记](references/index.md) — 源码关键片段和API签名的原始记录

## 学习路径建议

```
入门：00 → 01 → 02
         ↓
核心架构：03 → 04 → 05 → 06 → 07 → 08
              ↓
领域输出：09 → 10 → 11 → 12 → 13 → 14
              ↓
高级主题：15 → 16 → 17
              ↓
实战示例：examples/01 → 02 → 03 → 04
```

## 源码版本

本教程基于 Sphinx **9.1.1**（beta开发版本），源码路径：`external/libs/docs/sphinx/`。

- 许可证：BSD-2-Clause
- Python要求：≥ 3.12
- 核心依赖：docutils ≥0.21、Jinja2 ≥3.1、Pygments ≥2.17、Babel ≥2.13
