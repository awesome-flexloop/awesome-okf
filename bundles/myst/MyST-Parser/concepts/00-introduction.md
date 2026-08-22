---
type: Concept
title: MyST-Parser 简介
description: MyST-Parser 是什么——Sphinx 的 Markdown 解析器扩展，MyST 语法的核心实现
tags: [myst, sphinx, parser, markdown, introduction, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## MyST-Parser 简介

MyST-Parser 是 [Sphinx](https://www.sphinx-doc.org/) 文档生成器的 Markdown 解析器扩展，实现了 MyST（Markedly Structured Text，标记性结构化文本）Markdown 方言的解析与渲染。它基于 [markdown-it-py](https://markdown-it-py.readthedocs.io/) 作为 Markdown 解析引擎，通过 docutils 桥接 Sphinx 生态系统。

## 定位与核心能力

MyST-Parser 的核心定位是将 Markdown 的简洁性与 reStructuredText（RST）的扩展性结合：

- **CommonMark 兼容**：严格遵循 CommonMark 规范，标准 Markdown 语法开箱可用
- **RST 指令/角色桥接**：通过 `{directive:argument}` 和 `{role}`text`` 语法在 Markdown 中使用任意 RST 指令和角色
- **Sphinx 一等公民**：原生支持交叉引用、域（Domain）、intersphinx、MathJax 等 Sphinx 核心功能
- **可扩展语法**：18 个可选扩展语法（数学公式、任务列表、定义列表、变量替换等）按需启用
- **独立可用**：不仅是 Sphinx 扩展，还提供 docutils 独立解析器和 7 个 CLI 工具

## 三阶段解析架构

MyST-Parser 采用三阶段管线处理 Markdown 文档：

1. **Markdown 解析**：MyST Markdown 文本 → markdown-it-py 解析器（加载插件链）→ Token 流
2. **Token 渲染**：Token 流 → DocutilsRenderer/SphinxRenderer → docutils AST（doctree）
3. **Sphinx 后处理**：doctree → MystReferenceResolver 等 Post-Transform → 最终 doctree 供 Builder 输出

```
MyST Markdown → markdown-it-py (Tokens) → DocutilsRenderer (AST) → Sphinx Post-Transforms → HTML/PDF/LaTeX
```

## 适用场景

MyST-Parser 适合以下场景：

- **Sphinx 项目用 Markdown 写文档**：替代 RST，获得更友好的编写体验
- **技术文档与出版**：支持数学公式、交叉引用、代码执行（配合 MyST-NB）等学术出版需求
- **Jupyter Book 生态**：作为 Jupyter Book 的核心解析层
- **独立 Markdown 转 HTML/LaTeX**：通过 myst-docutils-* CLI 工具脱离 Sphinx 使用

## 环境要求

- Python 3.11+
- docutils 0.20-0.24
- markdown-it-py ~=4.2
- mdit-py-plugins ~=0.6
- Sphinx 8-10（Sphinx 集成时需要）
- PyYAML、Jinja2

## 与其他 Markdown 方案对比

| 方案 | Markdown 引擎 | RST 指令/角色 | Sphinx 集成 | 数学公式 | Notebook 支持 |
|------|--------------|--------------|-------------|---------|--------------|
| MyST-Parser | markdown-it-py | ✅ 完整支持 | ✅ 一等公民 | ✅ dollarmath/amsmath | ✅ 配合 MyST-NB |
| recommonmark | CommonMark-py | ⚠️ 有限支持 | ⚠️ 基础支持 | ❌ | ❌ |
| sphinx-markdown | Python-Markdown | ❌ | ⚠️ 基础 | ❌ | ❌ |

> **注意**：recommonmark 已于 2021 年宣布弃用，MyST-Parser 是其官方推荐替代品。

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [MyST 语法概览](/concepts/02-myst-syntax-overview.md)
- [三阶段解析管线](/concepts/03-architecture-pipeline.md)
