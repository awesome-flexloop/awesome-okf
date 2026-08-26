---
type: bundle
title: MyST-NB
description: MyST-NB——Jupyter Notebook 的 Sphinx/docutils 解析器中文 Wiki 教程
tags: [myst-nb, jupyter, notebook, sphinx, myst]
okf_version: "0.2"
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
  - id: mystnb-github
    url: https://github.com/executablebooks/MyST-NB
    title: MyST-NB GitHub 仓库
  - id: mystnb-docs
    url: https://myst-nb.readthedocs.io
    title: MyST-NB 官方文档
---

# MyST-NB

**MyST-NB**（MyST Notebook）是 Executable Books 生态中的 Jupyter Notebook 解析器与执行引擎，版本 **v1.5.0.dev**。它建立在 MyST-Parser 之上，使 Sphinx 和 docutils 能够读取、执行和渲染 Jupyter Notebook（`.ipynb`）及 MyST 文本格式 Notebook（`.md`，标记为 `file_format: mystnb`）。

> MyST-NB 在 MyST Markdown 的基础上增加了**代码执行与输出渲染**能力，实现「计算叙事」——将代码、输出、图表、叙述文本整合在单一可复现文档中。

## 核心能力

- ✅ 双格式输入：`.ipynb`（Jupyter Notebook）和 `.md`（MyST 文本格式 Notebook）
- ✅ 自动代码执行：5 种执行模式（off/auto/force/cache/inline），集成 nbclient 和 jupyter-cache
- ✅ MIME 多格式输出渲染：HTML/图片/Markdown/LaTeX/ipywidgets/ANSI 彩色终端
- ✅ Glue 变量粘贴：代码中存储变量，文档任意位置引用（跨页面）
- ✅ Eval 内联求值：正文中实时计算并插入变量值
- ✅ 细粒度输出控制：remove/hide/scroll/collapse 代码和输出
- ✅ 三层配置覆盖：全局 conf.py → 文件 frontmatter → Cell metadata
- ✅ ipywidgets 交互支持：自动加载 RequireJS 和 Jupyter Widgets
- ✅ Sphinx/Docutils 双模式：既作为 Sphinx 扩展，也可独立 CLI 使用
- ✅ 自定义扩展：entry points 注册自定义 Reader、渲染器、MIME 插件

## 快速入口

### 我想快速上手
- [快速开始](concepts/01-getting-started.md)——安装与最小配置
- [基础配置示例](examples/01-basic-setup.md)——完整 conf.py 模板

### 我想编写 Notebook
- [MyST Notebook 文件格式](concepts/02-notebook-format.md)——.ipynb 和 .md（mystnb）格式
- [MyST Notebook 语法速查](references/notebook-cheatsheet.md)——code-cell/glue/eval 语法速查
- [代码隐藏与输出控制](examples/04-hiding-code.md)——tags 和 metadata 详解

### 我想理解原理
- [四阶段处理管线](concepts/03-processing-pipeline.md)——读取→执行→转换→渲染
- [执行模式与缓存](concepts/05-execution-modes.md)——5 种模式对比与 jupyter-cache
- [渲染与 MIME 类型](concepts/06-render-and-mime.md)——MIME 优先级与输出渲染

### 我想使用高级功能
- [Glue 变量粘贴](concepts/07-glue.md)——代码→文档的数据桥梁
- [Eval 内联求值](concepts/08-eval.md)——正文内联计算
- [Glue & Eval 实战](examples/03-glue-and-eval.md)——数据叙事完整示例
- [执行模式配置](examples/02-execution-config.md)——CI/CD、本地开发场景配置

### 我想独立使用或扩展
- [CLI 工具独立使用](examples/05-cli-standalone.md)——mystnb-* 命令与 Python API
- [Docutils 独立使用](concepts/11-docutils-standalone.md)——脱离 Sphinx 的转换
- [自定义格式与扩展](concepts/12-custom-formats.md)——自定义 Reader、渲染器、MIME 插件

## Bundle 目录结构

```
MyST-NB/
├── index.md                  ← 当前文件（Bundle 根索引）
├── log.md                    ← 变更日志
├── spec/                     ← R→I 阶段产出
│   ├── facts.md              ← 源码事实采集（170 条事实）
│   └── insights.md           ← 架构洞察（5 条洞察）
├── concepts/                 ← 概念文档（13 篇）
│   ├── index.md
│   ├── 00-introduction.md
│   ├── 01-getting-started.md
│   ├── 02-notebook-format.md
│   ├── 03-processing-pipeline.md
│   ├── 04-config-system.md
│   ├── 05-execution-modes.md
│   ├── 06-render-and-mime.md
│   ├── 07-glue.md
│   ├── 08-eval.md
│   ├── 09-hiding-code.md
│   ├── 10-sphinx-integration.md
│   ├── 11-docutils-standalone.md
│   └── 12-custom-formats.md
├── examples/                 ← 实战示例（5 篇）
│   ├── index.md
│   ├── 01-basic-setup.md
│   ├── 02-execution-config.md
│   ├── 03-glue-and-eval.md
│   ├── 04-hiding-code.md
│   └── 05-cli-standalone.md
└── references/               ← 信源参考（2 篇）
    ├── index.md
    ├── mystnb-source.md
    └── notebook-cheatsheet.md
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
