# Sphinx 概念文档索引

本目录包含 Sphinx 文档生成器的核心概念文档，按学习路径分为四个部分。

## 入门

| 文档 | 说明 |
|------|------|
| [00-introduction.md](00-introduction.md) | Sphinx 简介、核心特性、技术栈与生态定位 |
| [01-getting-started.md](01-getting-started.md) | 安装、quickstart、sphinx-build用法、conf.py概览 |
| [02-architecture-overview.md](02-architecture-overview.md) | 核心类关系、初始化流程、构建管线总览 |

## 核心架构（源码视角）

| 文档 | 说明 |
|------|------|
| [03-application-class.md](03-application-class.md) | Sphinx主类、扩展API、build方法详解 |
| [04-config-system.md](04-config-system.md) | Config类、_Opt、rebuild级别、add_config_value |
| [05-event-system.md](05-event-system.md) | 核心事件、优先级、订阅/发射机制 |
| [06-registry.md](06-registry.md) | SphinxComponentRegistry、组件注册与去重 |
| [07-build-environment.md](07-build-environment.md) | BuildEnvironment、pickle缓存、增量构建 |
| [08-project-and-docutils.md](08-project-and-docutils.md) | Project类、Parser/Transform/Translator集成 |

## 域与输出（源码视角）

| 文档 | 说明 |
|------|------|
| [09-domain-system.md](09-domain-system.md) | Domain基类、6大内置Domain、交叉引用解析 |
| [10-builder-system.md](10-builder-system.md) | 13种Builder、构建流程模板方法、并行构建 |
| [11-html-builder.md](11-html-builder.md) | StandaloneHTMLBuilder、Jinja2模板、静态文件 |
| [12-autodoc.md](12-autodoc.md) | autodoc从docstring生成API文档 |
| [13-theme-system.md](13-theme-system.md) | 主题继承、配置选项、内置/第三方主题 |
| [14-intersphinx.md](14-intersphinx.md) | intersphinx跨项目引用 |

## 高级主题

| 文档 | 说明 |
|------|------|
| [15-extension-development.md](15-extension-development.md) | 完整扩展开发指南、API分类 |
| [16-i18n.md](16-i18n.md) | gettext翻译工作流 |
| [17-search-system.md](17-search-system.md) | 客户端全文搜索实现 |

## 用户指南

| 文档 | 说明 |
|------|------|
| [18-rest-primer.md](18-rest-primer.md) | reStructuredText完整入门 |
| [19-markdown-and-myst.md](19-markdown-and-myst.md) | MyST-Parser配置、Markdown支持 |
| [20-cross-references-guide.md](20-cross-references-guide.md) | 交叉引用完全指南 |
| [21-deployment.md](21-deployment.md) | RTD/GitHub Pages/Netlify部署 |
| [22-builtin-extensions.md](22-builtin-extensions.md) | 19个内置扩展详解 |
| [23-latex-and-pdf.md](23-latex-and-pdf.md) | LaTeX/PDF输出定制 |
| [24-faq-troubleshooting.md](24-faq-troubleshooting.md) | 常见问题与故障排查 |
| [25-glossary.md](25-glossary.md) | 核心术语速查表 |

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-application-class
04-config-system
05-event-system
06-registry
07-build-environment
08-project-and-docutils
09-domain-system
10-builder-system
11-html-builder
12-autodoc
13-theme-system
14-intersphinx
15-extension-development
16-i18n
17-search-system
18-rest-primer
19-markdown-and-myst
20-cross-references-guide
21-deployment
22-builtin-extensions
23-latex-and-pdf
24-faq-troubleshooting
25-glossary
```
