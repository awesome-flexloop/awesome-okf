---
type: concept
title: "PDF 导出"
description: "myst-exporters 通过 LaTeX 路径（myst-to-tex + jtex + latexmk）或 Typst 路径生成 PDF 的完整流程"
tags: [myst-exporters, pdf, latexmk, typst, jtex]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "jtex/src/tex/export.ts"
    facts: [F-030]
  - path: "myst-cli/src/build/utils/localArticleExport.ts"
    facts: [F-039, F-040]
  - path: "myst-to-tex/src/index.ts"
    facts: [F-002, F-003]
---

# PDF 导出

myst-exporters 本身不直接生成 PDF，PDF 是通过两条间接路径产生的：
1. **LaTeX 路径**（主要路径）：MDAST → LaTeX（myst-to-tex）→ 注入 jtex 模板（renderTemplate）→ 编译 .tex（latexmk）→ .pdf
2. **Typst 路径**：MDAST → Typst（myst-to-typst）→ 注入 jtex 模板 → 编译 .typ（typst CLI）→ .pdf

两种路径都依赖外部编译器（latexmk/xelatex 或 typst CLI），myst-cli 的 build 层负责编排。

## LaTeX PDF 路径（默认）

### 流程概览

```
MDAST
  │ myst-to-tex
  ▼
LatexResult { value, imports, preamble, commands }
  │ jtex renderTemplate(template, opts)
  ▼
template.tex (完整 LaTeX 文件，含导言区和 document 环境)
  │ latexmk -xelatex
  ▼
output.pdf
```

### 第一步：myst-to-tex 生成结构化结果

参见 [LaTeX 导出](02-latex-export.md)。TexSerializer 输出 `LatexResult`，包含正文 value、包 imports、导言区 preamble 和数学宏 commands。这些信息不会自动组装为完整 .tex 文件，而是交给 jtex 注入模板。

### 第二步：jtex 模板渲染

jtex 的 `renderTemplate` 函数将 LatexResult 注入到 Nunjucks 模板中：

```typescript
renderTemplate(template, {
  contentOrPath: latexResult.value,
  imports: latexResult,         // 包含 imports/commands/preamble
  preamble: '自定义导言区内容',
  frontmatter: pageFrontmatter, // 标题/作者/日期/摘要等
  parts: { abstract, ... },     // 文档 parts
  options: templateOptions,     // 模板选项（如字体、页面大小）
  outputPath: '_build/output.tex',
  sourceFile: 'source.md',
  filesPath: template.filesPath,
});
```

模板通过 Nunjucks 变量注入：
- `[-CONTENT-]`：正文内容（LaTeXResult.value）
- `[-IMPORTS-]`：jtex 渲染的 usepackage/newcommand 块
- `[-doc.title-]`、`[-doc.authors-]` 等：frontmatter 变量
- `[-parts.abstract-]`：文档 parts

同时 `copyTemplateFiles` 将模板目录中的静态文件（cls/sty/bib/图片等）复制到输出目录。

### 第三步：latexmk 编译

jtex 的 `pdfTexExportCommand` 生成编译命令：

```bash
latexmk -xelatex -synctex=1 -interaction=nonstopmode -file-line-error -outdir=dir
  -pdflogfile=logfile -auxdir=dir input.tex
```

默认引擎是 **xelatex**（通过 `-xelatex` 参数），支持 Unicode 和 TTF/OTF 字体。如果 LaTeX 模板指定了其他引擎，会从 template opts 中读取。

如果 preamble 包含 `printGlossaries`，还需要运行 makeglossaries（由 `texMakeGlossariesCommand` 生成命令），然后再运行 latexmk 确保目录被写入。

#### latexmk 多次编译的原因

latexmk 会自动判断需要多少次编译：
1. 第一次编译：生成 .aux/.toc/.bbl 等辅助文件
2. 运行 bibtex/biber（如果有参考文献）
3. 运行 makeglossaries（如果有术语表）
4. 后续编译：解析交叉引用、目录、引用编号
5. 直到所有辅助文件不再变化

### 第四步：清理临时文件

编译完成后，myst-cli build 层可选清理辅助文件（.aux/.log/.out/.toc 等）。

## Typst PDF 路径

当使用 Typst 模板或 `--typst` flag 时：

```
MDAST
  │ myst-to-typst
  ▼
TypstResult { value, macros, commands }
  │ jtex renderTemplate(template, opts)  // kind: 'typst'
  ▼
template.typ (完整 Typst 文件)
  │ typst compile
  ▼
output.pdf
```

jtex 的 Typst 路径与 LaTeX 路径对称：
- macros 写入 `myst-imports.typ` 文件，通过 `#import "myst-imports.typ": *` 引入
- commands 生成 `#let \name = $definition$` 格式的命令
- renderTemplate 中 `renderImports` 按 kind='typst' 分发到 `renderTypstImports`

## 输出格式控制

在 myst.yml 中可以配置导出选项：

```yaml
exports:
  - format: pdf
    template: arxiv_two_column      # 使用 arXiv 模板
    output: exports/paper.pdf
  - format: pdftex
    template: lapreprint
  - format: typst
    template: typst/article
```

CLI flag 也可控制：
- `--pdf`：生成 PDF（自动选择路径）
- `--tex`：仅生成 .tex 文件（不编译）
- `--typst`：生成 Typst PDF

## 错误处理

LaTeX 编译失败时：
1. latexmk 返回非零退出码
2. .log 文件包含编译错误信息
3. myst-cli 解析 .log 文件，提取关键错误并展示给用户
4. 常见错误：缺失包、图片路径错误、数学宏未定义、参考文献 key 不存在

## 模板选择

Jupyter Book / MyST 提供官方模板库（通过 myst-templates）：
- **default**：简单 LaTeX 文章
- **arxiv_two_column**：arXiv 双栏格式
- **lapreprint**：LaTeX 预印本风格
- **typst/article**：Typst 文章模板

用户也可以下载自定义模板（`jupyter-book templates download`）。

## 相关概念

- [02-latex-export](02-latex-export.md)：LaTeX 序列化器
- [07-typst-export](07-typst-export.md)：Typst 导出
- [08-jtex-template-engine](08-jtex-template-engine.md)：jtex 模板引擎
- [02-custom-jtex-template](../examples/02-custom-jtex-template.md)：自定义模板示例
