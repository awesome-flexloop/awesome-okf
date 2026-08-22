---
type: concept
title: "模板系统"
description: "Jupyter Book/myst-cli 的模板系统：myst-templates 仓库结构、template.yml 配置、模板下载解析和 jtex 渲染整合"
tags: [jupyter-book, templates, myst-templates, jtex, latex, typst]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "ts/templates.ts"
    facts: [F-021, F-022, F-023, F-024]
  - path: "jtex/src/jtex.ts"
    facts: [F-025, F-026, F-027]
  - path: "myst-templates/src/types.ts"
    facts: []
---

# 模板系统

Jupyter Book 的多格式导出（尤其是 PDF）依赖模板系统。模板定义了文档的排版框架（documentclass/页面设置/样式等），jtex 引擎将 MyST 内容注入模板生成可编译文档。模板由 myst-templates 包管理。

## 模板的作用

MyST 内容本身只包含语义标记（标题/段落/图片/公式），不包含排版信息。模板负责：

1. **文档结构**：提供 LaTeX/Typst 的文档框架（documentclass、导言区等）
2. **排版风格**：字体、页边距、行距、标题格式、页眉页脚
3. **期刊格式**：特定期刊的格式要求（如 arXiv 双栏、IEEE 单栏）
4. **静态资源**：logo 图片、cls/sty 文件、参考文献样式
5. **模板选项**：用户可配置的参数（如字体大小、是否双栏、页面大小）

## myst-templates 公共模板仓库

MyST 团队维护一个公共模板仓库，`jupyter-book templates list` 命令从中获取可用模板列表。

### 模板类型

按输出格式分类：

| 类型 | 标识 | 说明 |
|------|------|------|
| LaTeX/PDF | `tex` | 生成 .tex 文件，用 latexmk 编译为 PDF |
| Typst/PDF | `typst` | 生成 .typ 文件，用 typst 编译为 PDF |
| DOCX | `docx` | Word 模板（目前较少） |
| Site | `site` | 网站主题模板 |
| Beamer | `tex` (presentation) | LaTeX Beamer 演示文稿 |

### 模板目录结构

公共模板仓库中每个模板是一个目录：

```
templates/arxiv_two_column/
├── template.tex         # LaTeX 模板文件（Nunjucks 语法）
├── template.yml         # 模板元数据和选项定义
├── [template.bib]       # 可选：默认参考文献样式
├── [*.cls]              # 可选：LaTeX 类文件
├── [*.sty]              # 可选：LaTeX 宏包
├── [images/logo.png]    # 可选：logo 等图片
└── [README.md]          # 可选：模板说明
```

### template.yml 格式

```yaml
version: 1

template:
  kind: tex                    # tex / typst / docx / site
  title: "arXiv Two Column"    # 模板显示名
  description: "Two column arXiv preprint style"
  tags: [paper, preprint, arxiv]
  authors: [...]
  license: MIT

# 模板选项（用户可配置）
options:
  - id: papersize
    type: string
    default: letter
    choices: [letter, a4]
    description: Paper size
  - id: font_size
    type: number
    default: 11
    description: Font size in points
  - id: line_numbers
    type: boolean
    default: false
    description: Show line numbers
  - id: keywords
    type: boolean
    default: true
    description: Show keywords

# 文档 parts（模板支持的特殊部分）
parts:
  - id: abstract
    required: false
    description: Abstract
  - id: acknowledgments
    required: false
    description: Acknowledgments

# 构建配置
build:
  engine: xelatex              # LaTeX 引擎
  latexmk: true                # 使用 latexmk
  makeglossaries: false        # 是否需要术语表
```

## templates 命令

Jupyter Book 提供 templates 子命令管理模板：

### templates list

```bash
jupyter-book templates list [name] [--tag tag] [--pdf|--tex|--typst|--docx|--site]
```

- 不带参数：列出所有可用模板（表格格式：名称、描述、类型、标签）
- 指定 name：显示特定模板的详情（选项列表、parts、作者等）
- 类型过滤：`--pdf`（tex+typst）、`--tex`、`--typst`、`--docx`、`--site`
- 标签过滤：`--tag paper` 只显示带 paper 标签的模板

列表数据来自 myst-templates 的公共模板 API（或本地缓存）。

### templates download

```bash
jupyter-book templates download <template> [path] [--force]
```

- `template`：模板名称（如 `arxiv_two_column`）或本地路径/URL
- `path`：下载目标目录（默认当前目录下创建 `_templates/` 目录）
- `--force`：如果目标目录已有模板文件，覆盖之

下载流程：
1. `resolveInputs(session, templatePath, opts)`：解析模板来源
   - 如果是公共模板名 → 从公共仓库下载
   - 如果是本地路径 → 直接使用
   - 如果是 URL → 下载并解压
2. `downloadTemplate(session, templatePath, opts)`：下载模板文件到本地
3. 模板文件包括 template.tex/template.yml 和所有静态资源

下载后的模板可以在 myst.yml 中引用：

```yaml
exports:
  - format: pdf
    template: _templates/my-custom-template
```

## 模板解析与渲染流程

当用户执行 `jupyter-book build --pdf` 时，模板系统的工作流程：

```
1. 确定模板来源
   ├── myst.yml 中指定 template 字段？→ 使用该模板
   ├── 命令行 --template 参数？→ 使用该模板
   └── 默认 → 使用默认模板（如 `default`/`book`）

2. 解析模板
   ├── resolveInputs() 定位模板目录
   ├── MystTemplate 类验证模板文件存在
   ├── 读取 template.yml 获取选项定义和 build 配置

3. 准备模板选项
   ├── 合并默认选项 + myst.yml 中的 template_options + CLI 参数
   ├── 验证选项值（类型、choices 范围）

4. 渲染内容
   ├── myst-to-tex 转换 MDAST → LatexResult
   ├── renderTemplate(template, {
   │     contentOrPath: latexResult.value,
   │     imports: latexResult,
   │     frontmatter: docFrontmatter,
   │     parts: { abstract: ..., ... },
   │     options: resolvedOptions,
   │     outputPath: '_build/exports/paper.tex',
   │   })
   ├── Nunjucks 渲染 template.tex
   ├── 复制模板静态文件到输出目录

5. 编译（如需 PDF）
   ├── pdfTexExportCommand() 生成 latexmk 命令
   ├── 执行 latexmk 编译
   └── 检查编译结果
```

## jtex 模板语法

模板使用 Nunjucks 语法，但自定义了标签分隔符以避免与 LaTeX 冲突：

```latex
% template.tex 示例
\documentclass[[-options.font_size-]pt, [-options.papersize-]]{article}

%# 这是注释（不会出现在输出中） #%

\usepackage{graphicx}
\usepackage{hyperref}
[-IMPORTS-]  %  jtex 自动生成的 usepackage/newcommand 块

\title{[-doc.title-]}
[# for author in doc.authors #]
\author{[-author.name-]}
[# endfor #]
\date{[-doc.date-]}

\begin{document}
\maketitle

[# if parts.abstract #]
\begin{abstract}
[-parts.abstract-]
\end{abstract}
[# endif #]

[-CONTENT-]

\bibliographystyle{plain}
\bibliography{references}
\end{document}
```

可用变量：
- `[-CONTENT-]`：MyST 正文
- `[-IMPORTS-]`：自动生成的包导入
- `[-doc.*-]`：frontmatter 字段（title/authors/date/abstract）
- `[-options.*-]`：模板选项
- `[-parts.*-]`：文档 parts
- `[-frontmatter.*-]`：完整 frontmatter 对象

## 自定义模板

用户可以基于现有模板创建自定义模板：

1. 下载模板：`jupyter-book templates download arxiv_two_column ./my-template`
2. 修改 template.tex 或 template.yml
3. 在 myst.yml 中指定本地路径：`template: ./my-template`
4. 构建时使用自定义模板

详见 [自定义 jtex 模板示例](/examples/02-custom-jtex-template.md)。

## 相关概念

- [08-jtex-template-engine](/myst-exporters/concepts/08-jtex-template-engine.md)：jtex 模板引擎详解
- [03-pdf-export](/myst-exporters/concepts/03-pdf-export.md)：PDF 导出流程
- [02-custom-jtex-template](/myst-exporters/examples/02-custom-jtex-template.md)：自定义模板示例
