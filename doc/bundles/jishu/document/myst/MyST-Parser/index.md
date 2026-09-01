---
type: bundle
title: MyST-Parser
description: MyST Markdown 解析器的中文 Wiki 教程——从安装配置到深度定制
tags: [myst, sphinx, markdown, parser, myst-parser]
okf_version: "0.2"
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
  - id: myst-github
    url: https://github.com/executablebooks/MyST-Parser
    title: MyST-Parser GitHub 仓库
  - id: myst-docs
    url: https://myst-parser.readthedocs.io
    title: MyST-Parser 官方文档
---

# MyST-Parser

**MyST（Markedly Structured Text）Parser** 是 Sphinx 生态中的 MyST Markdown 解析器，版本 **v5.1.0**。它将 MyST 方言的 Markdown 文档解析为 docutils AST，使 Sphinx 能够构建以 Markdown 为源格式的文档项目。

> MyST Markdown 是 CommonMark 的超集，添加了 RST 的指令、角色、交叉引用等结构化写作能力。

## 核心能力

- ✅ 完全兼容 CommonMark Markdown
- ✅ 支持 18 种可选语法扩展（数学公式、定义列表、任务列表等）
- ✅ 所有 Sphinx/RST 指令和角色均可在 Markdown 中使用
- ✅ Sphinx 生态完整集成（交叉引用、intersphinx、toctree）
- ✅ 支持 docutils 独立模式（无需 Sphinx）
- ✅ CLI 工具（myst-docutils-html5、myst-anchors 等）
- ✅ 并行构建安全

## 快速入口

### 我想快速上手
- [快速开始](concepts/01-getting-started.md)——安装与最小配置
- [基础配置示例](examples/01-basic-setup.md)——完整 conf.py 模板

### 我想了解语法
- [MyST 语法概览](concepts/02-myst-syntax-overview.md)——指令、角色、交叉引用
- [扩展语法系统](concepts/05-extension-system.md)——18 个扩展详解
- [扩展语法速查](references/extensions-cheatsheet.md)——格式与配置项速查表

### 我想理解原理
- [三阶段解析管线](concepts/03-architecture-pipeline.md)——Markdown→Token→AST→输出
- [配置系统](concepts/04-config-system.md)——MdParserConfig 与自动注册机制
- [解析器与渲染器](concepts/06-parser-and-renderer.md)——核心组件工作原理

### 我想高级定制
- [自定义指令与角色](examples/03-custom-directives.md)——编写并注册自定义扩展
- [交叉引用实战](examples/04-cross-references.md)——高级引用技巧
- [CLI 独立使用](examples/05-standalone-cli.md)——脱离 Sphinx 的转换工作流

## Bundle 目录结构

```
MyST-Parser/
├── index.md                  ← 当前文件（Bundle 根索引）
├── log.md                    ← 变更日志
├── spec/                     ← R→I 阶段产出
│   ├── facts.md              ← 源码事实采集（117 条事实）
│   └── insights.md           ← 架构洞察与知识地图（5 条洞察）
├── concepts/                 ← 概念文档（16 篇）
│   ├── index.md
│   ├── 00-introduction.md
│   ├── 01-getting-started.md
│   ├── 02-myst-syntax-overview.md
│   ├── 03-architecture-pipeline.md
│   ├── 04-config-system.md
│   ├── 05-extension-system.md
│   ├── 06-parser-and-renderer.md
│   ├── 07-directives-and-roles.md
│   ├── 08-cross-references.md
│   ├── 09-slug-and-anchors.md
│   ├── 10-cli-tools.md
│   ├── 11-sphinx-integration.md
│   ├── 12-frontmatter.md
│   ├── 13-math-and-mathjax.md
│   ├── 14-warning-system.md
│   └── 15-docutils-standalone.md
├── examples/                 ← 实战示例（5 篇）
│   ├── index.md
│   ├── 01-basic-setup.md
│   ├── 02-enable-extensions.md
│   ├── 03-custom-directives.md
│   ├── 04-cross-references.md
│   └── 05-standalone-cli.md
└── references/               ← 信源参考（2 篇）
    ├── index.md
    ├── myst-parser-source.md
    └── extensions-cheatsheet.md
```

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
