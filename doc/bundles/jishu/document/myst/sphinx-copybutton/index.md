---
okf_version: "0.2"
type: bundle
title: "sphinx-copybutton — 代码块一键复制"
description: "sphinx-copybutton 是为 Sphinx 代码块添加复制按钮的轻量扩展，支持智能提示符剥离、多语言本地化、自定义图标，核心仅99行Python代码"
tags: [sphinx, sphinx-extension, copybutton, clipboard, javascript, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: copybutton-repo
    resource: https://github.com/executablebooks/sphinx-copybutton
    title: sphinx-copybutton GitHub Repository
    author: team:executablebooks
  - id: copybutton-docs
    resource: https://sphinx-copybutton.readthedocs.io/
    title: sphinx-copybutton Documentation
---

# sphinx-copybutton — 代码块一键复制

sphinx-copybutton 是 [Executable Book Project](https://executablebooks.org/) 开发的 Sphinx 扩展，为文档中的每个代码块添加一个轻量的"复制"按钮。点击按钮即可将代码内容复制到剪贴板，支持智能剥离 shell/REPL 提示符，确保"复制→粘贴→运行"一步到位。

> **核心特点**：Python 端仅 **99 行代码**，通过 Jinja2 模板桥接 Python 配置与 JavaScript 运行时，是学习 Sphinx 前端增强类扩展开发的极简范本。

## 知识地图

```
sphinx-copybutton/
├── 📖 concepts/       概念文档（5 篇）
│   ├── 入门：简介、快速开始
│   ├── 核心：扩展架构、文本处理机制
│   └── 进阶：自定义样式与图标
├── 💡 examples/       实战示例（2 篇）
│   ├── 基础配置（完整 conf.py）
│   └── 多语言 REPL 提示符配置
└── 📚 references/     信源参考（1 篇）
    └── 源码路径映射
```

## 推荐学习路径

### 15 分钟快速上手

1. [简介](concepts/00-introduction.md) → 了解定位和特点（3 分钟）
2. [快速开始](concepts/01-getting-started.md) → 完成安装和最小配置（5 分钟）
3. [基础配置示例](examples/basic-setup.md) → 复制 conf.py 模板，为你的文档添加复制按钮（7 分钟）

### 深入理解机制（30-60 分钟）

4. [扩展架构与注册机制](concepts/02-extension-architecture.md) → setup三步范式、Jinja2模板桥接、静态资源管理
5. [文本处理与提示符剥离](concepts/03-text-processing.md) → 智能文本清洗原理、正则匹配、行续接/HERE文档处理
6. [多语言 REPL 提示符配置](examples/shell-prompts.md) → Bash/Python/IPython/PowerShell等场景配置

### 定制开发

7. [自定义样式与图标](concepts/04-customization.md) → CSS覆盖、SVG图标、选择器定制、本地化

## 核心洞察

| # | 洞察 | 一句话总结 |
|---|------|-----------|
| 1 | Jinja2 模板桥接 | `.js_t`模板在构建时将Python配置"编译"进JS源码，是静态站点特有的配置注入模式 |
| 2 | 智能文本清洗 | 核心价值不是放按钮，而是剥离提示符/行号/续接符，让复制内容可直接运行 |
| 3 | 极简微扩展范式 | 99行Python+2个JS文件，三步注册（资源路径→配置项→静态文件）即可完成 |
| 4 | 渐进增强UX | 默认隐藏悬停显示、打印隐藏、成功反馈、异步轮询、7语言本地化 |

## 配置项速查

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `copybutton_prompt_text` | `""` | 提示符文本（字面量或正则） |
| `copybutton_prompt_is_regexp` | `False` | prompt_text 是否为正则 |
| `copybutton_only_copy_prompt_lines` | `True` | 只复制含提示符的行 |
| `copybutton_remove_prompts` | `True` | 复制时移除提示符 |
| `copybutton_copy_empty_lines` | `True` | 保留空行 |
| `copybutton_line_continuation_character` | `""` | 行续接字符 |
| `copybutton_here_doc_delimiter` | `""` | HERE文档分隔符 |
| `copybutton_selector` | `"div.highlight pre"` | 目标选择器 |
| `copybutton_exclude` | `".linenos"` | 排除元素选择器 |
| `copybutton_image_svg` | `""` | 自定义按钮SVG |

## 相关知识包

| 知识包 | 关系 |
|--------|------|
| [sphinx-book-theme](https://github.com/executablebooks/sphinx-book-theme) | Jupyter Book 主题——sphinx-copybutton 的主要使用场景之一 |
| [sphinx-design](https://github.com/executablebooks/sphinx-design) | Sphinx 设计组件——配合使用提供更丰富的代码展示 |
| [MyST Parser](https://github.com/executablebooks/MyST-Parser) | MyST Markdown 解析器——Executable Books 生态核心 |

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
