---
type: example
title: "自定义 jtex 模板"
description: "创建自定义 LaTeX 模板，定义模板选项、添加自定义宏包、配置页面布局，并在 Jupyter Book 中使用"
tags: [myst-exporters, example, jtex, template, latex, custom]
generated: 2026-08-23
verified: false
status: stable
stale_after: 2027-12-31
sources:
  - path: "jtex/src/jtex.ts"
    facts: [F-025, F-026, F-027]
  - path: "jtex/src/tex/imports.ts"
    facts: [F-029]
---

# 自定义 jtex 模板

本示例演示如何创建一个自定义的 jtex LaTeX 模板，包括修改文档结构、添加自定义包、定义模板选项，并在 Jupyter Book 项目中使用。

## 目标

创建一个适合课程讲义的 LaTeX 模板：
- 使用 article 文档类
- A4 纸张，适中的页边距
- 支持中文（使用 ctex 包）
- 自定义页眉页脚（使用 fancyhdr）
- 显示目录
- 可选的行号显示
- 可选的双色打印模式

## 步骤 1：创建模板目录

```bash
mkdir -p templates/lecture-notes
cd templates/lecture-notes
```

## 步骤 2：创建 template.tex

创建 `templates/lecture-notes/template.tex`：

```latex
%# 使用 article 文档类，支持自定义字体大小和纸张大小 #%
\documentclass[[-options.font_size-]pt, [-options.paper_size-]]{article}

%# ===== 基础包 ===== #%
\usepackage{amsmath, amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{geometry}
\usepackage{fancyhdr}
\usepackage{enumitem}
\usepackage{xcolor}

%# ===== 中文支持（条件包含）#%
[# if options.chinese #]
\usepackage{ctex}
[# endif #]

%# ===== 页面布局 ===== #%
\geometry{
  left=[-options.margin_left-]cm,
  right=[-options.margin_right-]cm,
  top=[-options.margin_top-]cm,
  bottom=[-options.margin_bottom-]cm
}

%# ===== 页眉页脚 ===== #%
\pagestyle{fancy}
\fancyhf{}
\lhead{[-doc.title-]}
\rhead{[-doc.author-]}
\cfoot{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

%# ===== 行号（可选）===== #%
[# if options.line_numbers #]
\usepackage{lineno}
\linenumbers
[# endif #]

%# ===== 双色（可选）===== #%
[# if options.two_color #]
\usepackage[pscoord]{eso-pic}
\newcommand{\bgshift}{0pt}
\AddToShipoutPictureFG*{
  \AtPageUpperLeft{\put(0,0){\color{gray!20}\rule{\paperwidth}{\paperheight}}}
  \AtPageUpperLeft{\put(\bgshift,0){\color{white}\rule{\paperwidth}{\paperheight}}}
}
[# endif #]

%# MyST 自动生成的包导入和宏命令 #%
[-IMPORTS-]

%# ===== 标题信息 ===== #%
\title{[-doc.title-]}
[# for author in doc.authors #]
\author{[-author.name-]}
[# endfor #]
\date{[-doc.date-]}

%# ===== 文档开始 ===== #%
\begin{document}

\maketitle

[# if options.toc #]
\tableofcontents
\newpage
[# endif #]

[# if parts.abstract #]
\begin{abstract}
[-parts.abstract-]
\end{abstract}
[# endif #]

%# ===== 正文内容（MyST 生成）===== #%
[-CONTENT-]

%# ===== 参考文献 ===== #%
[# if frontmatter.bibliography #]
\bibliographystyle{[-options.bib_style-]}
\bibliography{[-frontmatter.bibliography-]}
[# endif #]

\end{document}
```

## 步骤 3：创建 template.yml

创建 `templates/lecture-notes/template.yml`，定义模板元数据和选项：

```yaml
version: 1

template:
  kind: tex
  title: "Lecture Notes"
  description: "A simple template for course lecture notes"
  tags: [notes, lecture, education]
  license: MIT

# 模板选项定义
options:
  - id: font_size
    type: number
    default: 11
    description: "Font size in points"
    choices: [10, 11, 12]

  - id: paper_size
    type: string
    default: a4paper
    description: "Paper size"
    choices: [a4paper, letterpaper]

  - id: margin_left
    type: number
    default: 2.5
    description: "Left margin in cm"

  - id: margin_right
    type: number
    default: 2.5
    description: "Right margin in cm"

  - id: margin_top
    type: number
    default: 2.5
    description: "Top margin in cm"

  - id: margin_bottom
    type: number
    default: 2.5
    description: "Bottom margin in cm"

  - id: chinese
    type: boolean
    default: false
    description: "Enable Chinese support (ctex package)"

  - id: line_numbers
    type: boolean
    default: false
    description: "Show line numbers"

  - id: two_color
    type: boolean
    default: false
    description: "Two-color (duplex) printing mode"

  - id: toc
    type: boolean
    default: true
    description: "Include table of contents"

  - id: bib_style
    type: string
    default: plain
    description: "Bibliography style"
    choices: [plain, alpha, unsrt, abbrv]

# 文档 parts
parts:
  - id: abstract
    required: false
    description: "Document abstract"

  - id: acknowledgments
    required: false
    description: "Acknowledgments section"

# 构建配置
build:
  engine: xelatex
  latexmk: true
  makeglossaries: false
```

## 步骤 4：在项目中使用自定义模板

### 方法一：直接引用本地模板路径

在项目的 `myst.yml` 中配置：

```yaml
version: 1
project:
  title: "机器学习讲义"
  author: "张教授"

build:
  exports:
    - format: pdf
      template: templates/lecture-notes
      output: exports/lecture-notes.pdf
      template_options:
        font_size: 12
        chinese: true
        toc: true
        line_numbers: false
        margin_left: 3.0
        margin_right: 3.0
```

### 方法二：先下载再使用

```bash
jupyter-book templates download templates/lecture-notes ./_templates/notes
```

然后在 myst.yml 中引用 `_templates/notes`。

## 步骤 5：构建 PDF

```bash
jupyter-book build notes.md --pdf
```

jtex 会：
1. 读取 `templates/lecture-notes/template.yml` 验证选项
2. 使用 myst-to-tex 转换 Markdown 为 LaTeX
3. 自动去重包导入（模板已有 hyperref，MyST 不会重复添加）
4. Nunjucks 渲染 template.tex，将 CONTENT/IMPORTS/options 注入
5. 复制模板静态文件到输出目录
6. 执行 latexmk -xelatex 编译 PDF

## 模板变量参考

### 可用的顶层变量

| 变量 | 类型 | 说明 |
|------|------|------|
| `CONTENT` | string | MyST 正文 LaTeX 内容 |
| `IMPORTS` | string | 自动生成的 usepackage/newcommand 块 |
| `doc` | object | 文档元数据（title, authors, date, doi 等）|
| `options` | object | 模板选项值（用户配置或默认值）|
| `parts` | object | 文档 parts（abstract, acknowledgments 等）|
| `frontmatter` | object | 完整文档 frontmatter |

### 控制流标签

```
[# if condition #]...[# endif #]
[# for item in list #]...[# endfor #]
[# for key, value in object #]...[# endfor #]
```

### 注释

```
%# 这是模板注释，不会出现在输出中 #%
```

## 常见自定义场景

### 添加自定义宏

在 template.tex 的导言区直接添加：

```latex
% 自定义数学命令
\newcommand{\E}{\mathbb{E}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\N}{\mathbb{N}}
\newcommand{\argmin}{\operatorname*{arg\,min}}
```

### 条件化内容块

使用 parts 机制让用户可选地包含某些部分：

```latex
[# if parts.preface #]
\section*{Preface}
[-parts.preface-]
\newpage
[# endif #]
```

然后在 template.yml 中声明：

```yaml
parts:
  - id: preface
    required: false
    description: "Preface section"
```

在 Markdown 文档中使用：

```markdown
---
parts:
  preface: |
    这是前言内容...
---
```

### 导入额外的 .tex 文件

如果模板需要额外的 .tex 文件（如自定义宏定义文件），放在模板目录中，`copyTemplateFiles` 会自动复制：

```
templates/lecture-notes/
├── template.tex
├── template.yml
└── macros.tex       # 自动复制到输出目录
```

在 template.tex 中通过 `\input{macros}` 引入。

## 验证模板

使用 jtex CLI 检查模板：

```bash
npx jtex check templates/lecture-notes
```

这会验证 template.tex 和 template.yml 的格式正确性，报告缺失的变量或语法错误。

## 相关概念

- [08-jtex-template-engine](/concepts/08-jtex-template-engine.md)：jtex 模板引擎详解
- [02-latex-export](/concepts/02-latex-export.md)：LaTeX 导出
- [03-pdf-export](/concepts/03-pdf-export.md)：PDF 生成流程
- [04-template-system](../../jupyter-book/concepts/04-template-system.md)：模板系统
