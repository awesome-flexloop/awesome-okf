---
type: concept
title: "jtex 模板引擎"
description: "jtex 基于 Nunjucks 的 LaTeX/Typst 模板渲染引擎，负责将导出器输出的内容片段整合到模板中，处理包导入、宏命令和静态文件复制"
tags: [myst-exporters, jtex, template, nunjucks, latex, typst]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "jtex/src/jtex.ts"
    facts: [F-025, F-026, F-027]
  - path: "jtex/src/render.ts"
    facts: [F-028]
  - path: "jtex/src/tex/imports.ts"
    facts: [F-029]
  - path: "jtex/src/typst/imports.ts"
    facts: [F-031]
  - path: "jtex/src/tex/export.ts"
    facts: [F-030]
  - path: "myst-templates/src/types.ts"
    facts: []
---

# jtex 模板引擎

jtex 是 MyST 生态中用于 LaTeX 和 Typst 模板渲染的引擎，基于 [Nunjucks](https://mozilla.github.io/nunjucks/)（JavaScript 版 Jinja2）实现。它将 myst-to-tex/myst-to-typst 输出的内容片段（正文、包导入、宏命令等）注入到模板文件中，生成完整的可编译文档。

## 为什么需要模板层

直接将 MDAST 转换为完整的 LaTeX/Typst 文件是不够的，因为：

1. **文档结构差异**：LaTeX 需要 `\documentclass`、`\begin{document}` 等固定框架，不同模板的结构不同
2. **包管理**：模板可能已经包含了某些包，需要避免重复 `\usepackage`
3. **排版风格**：不同期刊/模板有不同的字体、页边距、标题格式
4. **模板选项**：模板可能定义了自定义选项（如字体大小、页面大小、单双栏）
5. **静态资源**：模板自带 .cls/.sty 文件、logo 图片等，需要复制到输出目录
6. **自定义导言区**：用户可能需要在导言区添加自定义命令和配置

jtex 的职责就是解决这些问题，将"内容"和"模板"解耦。

## 模板目录结构

一个 jtex 模板目录包含：

```
my-template/
├── template.tex        # LaTeX 模板（或 template.typ 用于 Typst）
├── template.yml        # 模板元数据和选项定义
├── [template.bib]      # 可选：模板自带的参考文献
├── [*.cls, *.sty]      # 可选：LaTeX 类文件和宏包
├── [images/*]          # 可选：图片资源（logo 等）
└── [...其他静态文件]   # 任意额外文件
```

### template.tex 示例

```latex
\documentclass[- options.papersize, 12pt -]{article}
[- IMPORTS -]
\title{[-doc.title-]}
\author{[-doc.authors | join(", ") -]}
\date{[-doc.date-]}
\begin{document}
\maketitle
[-CONTENT-]
\bibliographystyle{plain}
\bibliography{references}
\end{document}
```

### 自定义标签语法

jtex 配置 Nunjucks 使用自定义标签语法（避免与 LaTeX 的 `{}` 和 Jinja2 的 `{{}}` 冲突）：

| 标签类型 | 语法 | 示例 |
|---------|------|------|
| 块标签（Block/控制流）| `[# #]` | `[# for author in doc.authors #]` |
| 变量输出 | `[- -]` | `[-doc.title-]` |
| 注释 | `%# #%` | `%# 这是注释 #%` |

### 模板变量

在模板中可以访问以下变量：

| 变量 | 说明 |
|------|------|
| `CONTENT` | 正文内容（导出器输出的 value） |
| `IMPORTS` | 渲染后的 imports 块（usepackage/newcommand 等） |
| `doc.title` | 文档标题 |
| `doc.authors` | 作者列表（字符串数组）|
| `doc.date` | 日期 |
| `doc.abstract` | 摘要 |
| `options.*` | 模板选项值（如 `options.fontSize`、`options.papersize`）|
| `parts.*` | 文档 parts（如 `parts.abstract`、`parts.acknowledgments`）|
| `frontmatter.*` | 完整 frontmatter 对象 |

## renderTemplate 核心流程

```typescript
renderTemplate(template: MystTemplate, opts: RenderOptions): void
```

执行步骤：

1. **校验输出路径**：检查 outputPath 是否合法，防止越界写入
2. **读取内容**：如果 contentOrPath 是文件路径，读取文件内容
3. **准备渲染数据**（renderer 对象）：
   - `CONTENT`：正文内容（contentOrPath 或文件内容）
   - `IMPORTS`：调用 `renderImports(kind, opts.imports, opts.packages, opts.preamble)` 生成
   - `doc`、`options`、`parts`、`frontmatter`：从 opts 中传入
   - 其他 frontmatter 字段直接平铺到 renderer 顶层
4. **复制模板文件**：`template.copyTemplateFiles(outputPath)` 将静态文件复制到输出目录
5. **配置 Nunjucks 环境**（getDefaultEnv）：
   - `trimBlocks: true`（块标签后自动删空白）
   - `autoescape: false`（输出 LaTeX/Typst 不需要 HTML 转义）
   - 自定义标签语法
   - 添加 `len` filter（数组长度）
6. **渲染模板**：`env.render(template.getTemplateFilename(), renderer)`
7. **写入输出文件**：将渲染结果写入 outputPath
8. **Typst macros 额外处理**：如果是 Typst 模板且有 macros，将 macros 内容写入 `myst-imports.typ` 文件

## LaTeX imports 渲染

`renderTexImports` 函数生成导言区的包导入和宏命令块：

```latex
% Math commands imported from MyST
\newcommand{\RR}{\mathbb{R}}
\newcommand{\fractal}[1]{\mathcal{#1}}

% Packages imported from MyST
\usepackage{url}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{hyperref}
```

### createTexImportCommands

```typescript
function createTexImportCommands(
  commands: string[],        // 需要 usepackage 的包名列表
  existingPackages?: string[] // 模板已包含的包（不重复导入）
): string
```

- 对 commands 去重（Set）、排序（字母序）
- 过滤掉 existingPackages 中的包（模板已有）
- 每个包生成一行 `\usepackage{name}`

### createTexMathCommands

```typescript
function createTexMathCommands(
  plugins: Record<string, string>  // { commandName: latexDefinition }
): string
```

- 将数学宏命令转换为 `\newcommand{\name}[nArgs]{definition}`
- 自动检测参数个数：匹配 definition 中的 `#[1-9]` 确定 nArgs
- 例如 `{ R: "\\mathbb{R}" }` → `\newcommand{\RR}{\mathbb{R}}`
- 例如 `{ frac: "\\frac{#1}{#2}" }` → `\newcommand{\frac}[2]{\frac{#1}{#2}}`

### mergeTexTemplateImports

合并两个 TexTemplateImports 对象：
- `commands`（宏命令）：后者覆盖前者（同名命令）
- `imports`（包列表）：合并去重并集

## Typst imports 渲染

`renderTypstImports` 生成 Typst 的导入和命令块：

```typst
#import "myst-imports.typ": *

#let rr = $RR$
#let fractal = $cal(#1)$
```

- macros 不为空时，生成 `#import "myst-imports.typ": *` 并将 macros 内容写入独立文件
- commands 生成 `#let \name = $definition$` 格式

## MystTemplate 类

MystTemplate 类来自 myst-templates 包，jtex 依赖它来：

1. **定位模板**：从本地模板目录或 myst-templates 仓库查找模板
2. **验证模板**：检查 template.tex/template.typ 和 template.yml 是否存在
3. **解析 template.yml**：读取模板元数据（选项定义、parts、build 配置等）
4. **复制文件**：`copyTemplateFiles(outputDir)` 将模板静态文件复制到输出目录
5. **获取模板文件名**：`getTemplateFilename()` 返回 `template.tex` 或 `template.typ`
6. **获取模板目录**：`templatePath` 属性

## PDF 编译命令生成

jtex 还提供 PDF 编译命令的辅助函数：

### pdfTexExportCommand

```typescript
function pdfTexExportCommand(
  texFile: string,
  logFile: string,
  template?: MystTemplate
): string
```

生成 latexmk 命令：
```bash
latexmk -xelatex -synctex=1 -interaction=nonstopmode -file-line-error
  -outdir=<dir> -pdflogfile=<log> -auxdir=<dir> <texFile>
```

默认引擎是 xelatex，如果 template.yml 中指定了 `tex.engines`（如 `pdflatex`、`lualatex`），会使用对应的 latexmk 参数。

### texMakeGlossariesCommand

```typescript
function texMakeGlossariesCommand(texFile: string, logFile: string): string
```

如果文档包含术语表（glossary），需要在两次 latexmk 之间运行：
```bash
makeglossaries -d <dir> <texFile> 2>&1 > <logFile>
```

## CLI 命令

jtex 提供 CLI 工具用于模板检查：

- `jtex check [path]`：检查模板目录是否合法，验证 template.yml 格式
  - `--all`：列出所有问题
  - `--pdf`：同时验证 PDF 编译可用性（不实际编译）

## 与 myst-cli 的整合

在 myst-cli build 层中，jtex 的使用流程：

1. myst-to-tex/myst-to-typst 转换 MDAST 得到 Result 对象
2. myst-cli 加载/下载模板（MystTemplate 对象）
3. 调用 `renderTemplate(template, opts)` 生成 .tex/.typ 文件
4. 如果需要 PDF，调用 `pdfTexExportCommand`/typst CLI 编译
5. 输出最终文件到 _build/exports/

## 相关概念

- [02-latex-export](02-latex-export.md)：LaTeX 导出（LatexResult 输出）
- [03-pdf-export](03-pdf-export.md)：PDF 生成流程
- [07-typst-export](07-typst-export.md)：Typst 导出（TypstResult 输出）
- [02-custom-jtex-template](../examples/02-custom-jtex-template.md)：自定义 jtex 模板示例
