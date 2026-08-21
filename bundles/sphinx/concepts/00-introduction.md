---
type: "concept"
title: "Sphinx 简介"
description: "Sphinx 是什么——Python 生态最主流的文档生成器，核心能力、版本信息、许可证与项目定位"
tags: [introduction, overview, basics]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: sphinx-init
    resource: /references/sphinx-app-init.md
    title: "Sphinx 应用初始化源码"
  - id: pyproject
    resource: pyproject.toml
    title: "Sphinx pyproject.toml"
---

# Sphinx 简介

## 什么是 Sphinx

Sphinx 是一个**智能且美观的文档生成器**（Python documentation generator）[F-001]。它最初由 Georg Brandl 为 Python 官方文档创建，现已成为 Python 生态乃至更广泛开源社区中最主流的文档工具。Sphinx 使用 reStructuredText（reST）作为默认标记语言，通过扩展也支持 Markdown，能够将纯文本源文件转换为 HTML、PDF（LaTeX）、EPUB、man 手册页、Texinfo、XML 等多种输出格式。

Sphinx 完全使用 Python 编写，采用 **BSD-2-Clause** 开源许可证发布 [F-002]，项目托管于 GitHub（https://github.com/sphinx-doc/sphinx）。当前版本为 **9.1.1**（beta 开发版本），构建系统使用 flit_core，要求 Python ≥ 3.12 [F-003]。

## 核心能力

### 多格式输出

Sphinx 通过 Builder（构建器）抽象层支持 13 种内置输出格式 [F-004]：

| 格式 | 构建器 | 说明 |
|------|--------|------|
| HTML | `html` | 标准HTML网站（主要输出格式） |
| 目录式HTML | `dirhtml` | 每个文档一个目录，index.html作为入口 |
| 单页HTML | `singlehtml` | 所有内容合并为一个HTML页面 |
| LaTeX/PDF | `latex` | 生成LaTeX源码，可编译为PDF |
| 纯文本 | `text` | 纯文本输出 |
| man手册 | `manpage` | Unix man page格式 |
| Texinfo | `texinfo` | GNU Texinfo格式 |
| EPUB3 | `epub3` | 电子书格式 |
| XML | `xml` | XML格式输出 |
| gettext | `gettext` | 生成POT翻译模板 |
| 链接检查 | `linkcheck` | 检查文档中所有链接的有效性 |
| 变更日志 | `changes` | 收集版本变更指令输出 |
| 空构建 | `dummy` | 不输出任何文件，用于调试 |

### 交叉引用与语义标记

Sphinx 最核心的能力之一是**跨文档智能交叉引用**。通过 Domain（领域）抽象，Sphinx 能够为不同编程语言（Python、C、C++、JavaScript）和知识域提供语义化的描述指令和引用角色。例如，在 Python 域中可以使用 `:py:func:\`funcname\`` 引用函数、`:py:class:\`Classname\`` 引用类，Sphinx 会自动解析这些引用并生成正确的超链接。

### 扩展体系

Sphinx 的几乎所有功能都可以通过扩展机制添加或修改。内置 20 个扩展（`sphinx.ext.*`），包括：

- **autodoc**：从 Python docstring 自动提取文档
- **intersphinx**：链接到其他Sphinx项目的文档（如Python标准库文档）
- **napoleon**：支持NumPy和Google风格的docstring
- **doctest**：在文档中嵌入可执行的测试代码
- **todo**：在文档中插入TODO项并汇总
- **viewcode**：链接到源代码
- **graphviz**：嵌入Graphviz图表
- **autosummary**：自动生成API摘要页

### 主题系统

Sphinx 内置 13 个主题（basic、default、classic、sphinxdoc、scrolls、agogo、nature、pyramid、haiku、traditional、epub、nonav、bizstyle），默认使用 **alabaster** 主题 [F-005]。主题通过 `theme.toml` 或 `theme.conf` 配置，支持继承和定制。

## 核心依赖

Sphinx 的核心运行依赖包括 [F-006]：

- **docutils** (≥0.21, <0.23)：reStructuredText 解析引擎，提供文档树（doctree）表示
- **Jinja2** (≥3.1)：HTML/模板渲染引擎
- **Pygments** (≥2.17)：代码语法高亮
- **Babel** (≥2.13)：国际化（i18n）支持
- **snowballstemmer** (≥2.2)：词干提取（用于搜索）
- **alabaster** (≥0.7.14)：默认主题
- **sphinxcontrib-*** 系列：HTML帮助、DevHelp、QtHelp、AppleHelp、序列化HTML、JSMath等输出支持
- **requests** (≥2.30.0)：HTTP请求（用于intersphinx等）
- **packaging** (≥23.0)：版本号处理
- **imagesize** (≥1.3)：图片尺寸获取
- **roman-numerals** (≥1.0.0)：罗马数字转换

## Sphinx vs 其他文档工具

| 特性 | Sphinx | MkDocs | Docusaurus | Javadoc/pdoc |
|------|--------|--------|------------|-------------|
| **默认标记语言** | reStructuredText | Markdown | MDX | 从源码注释生成 |
| **多语言域支持** | ✅ Python/C/C++/JS/更多 | ❌ | ❌ | 单语言 |
| **PDF输出** | ✅ LaTeX原生支持 | ⚠️ 需插件 | ⚠️ 需插件 | ❌ |
| **交叉引用** | ✅ 语义级跨域引用 | ⚠️ 链接级 | ⚠️ 链接级 | ⚠️ 单项目内 |
| **API文档自动生成** | ✅ autodoc+breathe等 | ⚠️ 需插件 | ⚠️ 需插件 | ✅ 核心功能 |
| **扩展生态** | ✅ 成熟且丰富 | ⚠️ 较丰富 | ✅ 丰富 | ❌ 弱 |
| **i18n支持** | ✅ 内置gettext | ⚠️ 需插件 | ⚠️ 需插件 | ❌ |
| **适合场景** | 大型技术文档、API参考、多格式输出 | 快速项目文档 | 网站风格文档 | 快速API参考 |

Sphinx 的独特优势在于：
1. **语义级交叉引用**：不是简单的超链接，而是理解代码实体间的关系
2. **多格式输出**：同一源文件可输出HTML、PDF、EPUB等
3. **成熟的扩展生态**：20年积累的扩展体系覆盖几乎所有文档需求
4. **Python生态标准**：Python官方文档、Django、Flask、NumPy、Pandas等大量知名项目都使用Sphinx

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [架构总览](02-architecture-overview.md)
