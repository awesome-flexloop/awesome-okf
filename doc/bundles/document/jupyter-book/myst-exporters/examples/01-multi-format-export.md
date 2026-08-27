---
type: example
title: "多格式到处示例"
description: "使用 myst-cli/Jupyter Book 将 MyST 文档同时导出为 HTML、PDF、DOCX、Markdown、JATS XML 和 Typst 等多种格式"
tags: [myst-exporters, example, multi-format, build, export]
generated: 2026-08-23
verified: false
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-cli/src/build/utils/localArticleExport.ts"
    facts: [F-039, F-040]
  - path: "myst-to-html/src/renderMdast.ts"
    facts: [F-036]
---

# 多格式到处示例

本示例演示如何使用 Jupyter Book/myst-cli 将一份 MyST Markdown 文档导出为多种目标格式。

## 前提条件

- 已安装 Jupyter Book v2（`pip install jupyter-book>=2.0`）或 mystmd
- 如需 PDF 导出，需要系统安装 LaTeX 发行版（TeX Live/MiKTeX，含 xelatex 和 latexmk）
- 如需 Typst PDF，需要安装 typst CLI

## 步骤 1：创建项目和内容

首先创建一个项目目录和示例文档：

```bash
mkdir my-paper && cd my-paper
jupyter-book init
```

创建 `paper.md`：

````markdown
---
title: "My Research Paper"
authors:
  - name: "Alice Researcher"
    affiliations:
      - "University of Example"
date: 2026-08-23
---

# Introduction

This is a sample paper demonstrating **multi-format export** with Jupyter Book v2.

We can write inline math like $E = mc^2$ and block math:

$$
\int_0^\infty e^{-x^2} \, dx = \frac{\sqrt{\pi}}{2}
$$

## Methods

| Parameter | Value |
|-----------|-------|
| Alpha     | 0.05  |
| Beta      | 0.80  |

```{note}
This is an important note.
```

## Results

![Example figure](images/figure1.png){#fig:example}

See @fig:example for an illustration.

## Conclusion

The results demonstrate the power of unified multi-format export.
````

## 步骤 2：配置导出格式

编辑 `myst.yml`，配置需要导出的格式：

```yaml
version: 1
project:
  title: "My Research Paper"
  author: "Alice Researcher"

site:
  template: book-theme

build:
  exports:
    - format: html
    - format: pdf
      template: default
      output: exports/paper.pdf
    - format: docx
      output: exports/paper.docx
    - format: md
      output: exports/paper.md
    - format: xml
      output: exports/paper.xml
    - format: typst
      output: exports/paper.pdf
```

## 步骤 3：命令行导出

### 导出所有格式

```bash
jupyter-book build paper.md --all
```

这会生成所有配置的格式。输出目录结构：

```
_build/
├── exports/
│   ├── paper.html
│   ├── paper.pdf        (LaTeX 路径)
│   ├── paper.docx
│   ├── paper.md
│   ├── paper.xml        (JATS)
│   └── paper-typst.pdf  (Typst 路径，如配置)
└── site/                (HTML 站点)
```

### 选择性导出特定格式

```bash
# 仅 HTML
jupyter-book build paper.md --html

# PDF (LaTeX 路径)
jupyter-book build paper.md --pdf

# DOCX (Word)
jupyter-book build paper.md --docx

# Markdown
jupyter-book build paper.md --md

# JATS XML
jupyter-book build paper.md --jats

# Typst PDF
jupyter-book build paper.md --typst

# LaTeX 源码（不编译 PDF）
jupyter-book build paper.md --tex
```

### 开发服务器模式

启动开发服务器，浏览器实时预览，文件变化自动重新构建：

```bash
jupyter-book start
# 打开 http://localhost:3000
```

## 步骤 4：编程式使用（Node.js）

如果你需要在代码中使用导出器：

```typescript
import { unified } from 'unified';
import mystParse from 'myst-parser';
import { mystToHtmlPlugin } from 'myst-to-html';
import { mystToTexPlugin } from 'myst-to-tex';
import { mystToDocxPlugin, createDocxFile } from 'myst-to-docx';
import { mystToJatsPlugin } from 'myst-to-jats';
import { mystToMdPlugin } from 'myst-to-md';
import { writeFileSync } from 'fs';

// 解析 Markdown
const source = `# Hello

This is a **test** with $E=mc^2$.
`;

const pipe = unified().use(mystParse);
const tree = pipe.runSync(pipe.parse(source));

// 导出 HTML
const htmlFile = unified().use(mystToHtmlPlugin).stringify(
  unified().use(mystToHtmlPlugin).runSync(tree)
);
writeFileSync('output.html', htmlFile.toString());

// 导出 LaTeX
const texFile = unified().use(mystToTexPlugin).processSync(tree);
console.log('LaTeX imports:', texFile.result.imports);
console.log('LaTeX value:', texFile.result.value);

// 导出 DOCX（需要异步）
const docxBuffer = await createDocxFile(tree);
writeFileSync('output.docx', docxBuffer);

// 导出 JATS
const jatsFile = unified().use(mystToJatsPlugin).processSync(tree);
writeFileSync('output.xml', jatsFile.toString());

// 导出 Markdown
const mdFile = unified().use(mystToMdPlugin).processSync(tree);
writeFileSync('output.md', mdFile.toString());
```

## 格式特性对比

| 特性 | HTML | PDF(LaTeX) | PDF(Typst) | DOCX | JATS | Markdown |
|------|------|-----------|-----------|------|------|---------|
| 排版精度 | 低 | 极高 | 高 | 中 | 低 | 低 |
| 可编辑性 | 低 | 低 | 低 | 高 | 低 | 极高 |
| 数学公式 | ✅ KaTeX | ✅ 原生 | ✅ 原生 | ✅ OMML | ⚠️ 标签 | ⚠️ 源码 |
| 表格 | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ 简单 |
| 图片 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 交叉引用 | ✅ JS | ✅ | ✅ | ✅ 域代码 | ✅ rid/id | ⚠️ |
| 参考文献 | ✅ | ✅ BibTeX | ✅ | ❌ | ✅ ref-list | ⚠️ |
| 代码高亮 | ✅ | ✅ listings/minted | ✅ | ⚠️ 等宽 | ❌ | ✅ |
| 自定义样式 | ✅ CSS | ✅ 模板 | ✅ 模板 | ⚠️ 样式 | ❌ | ❌ |
| 编译速度 | 快 | 慢(多次) | 快(秒级) | 中 | 快 | 最快 |

## 常见问题

### PDF 编译失败

- 确保安装了完整的 TeX Live/MiKTeX
- 检查 `.log` 文件中的错误信息
- 缺失包时通过 tlmgr 安装：`tlmgr install packagename`
- 尝试切换模板：`--template simple_book`

### 图片不显示

- 使用相对路径，图片应在项目目录内
- 支持的格式：PNG、JPG、PDF、SVG
- PDF 输出推荐使用 PDF/EPS 矢量图以获得最佳质量

### 中文支持

PDF 导出需要配置支持中文的模板，或自定义模板添加 ctex 包：

```latex
% 在自定义模板中
\usepackage{ctex}
```

## 相关概念

- [00-exporter-architecture](../concepts/00-exporter-architecture.md)：统一导出架构
- [01-html-export](../concepts/01-html-export.md)：HTML 导出
- [02-latex-export](../concepts/02-latex-export.md)：LaTeX 导出
- [03-pdf-export](../concepts/03-pdf-export.md)：PDF 导出
- [04-docx-export](../concepts/04-docx-export.md)：DOCX 导出
- [05-jats-export](../concepts/05-jats-export.md)：JATS 导出
- [06-markdown-export](../concepts/06-markdown-export.md)：Markdown 导出
- [07-typst-export](../concepts/07-typst-export.md)：Typst 导出
