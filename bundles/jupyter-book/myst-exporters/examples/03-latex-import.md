---
type: example
title: "LaTeX/JATS 导入示例"
description: "使用 jats-to-myst 和 tex-to-myst 将 JATS XML 学术论文和 LaTeX 文档导入为 MyST Markdown，并继续多格式导出"
tags: [myst-exporters, example, import, jats, latex, conversion]
generated: 2026-08-23
verified: false
status: exploratory
stale_after: 2027-12-31
sources:
  - path: "jats-to-myst/src/index.ts"
    facts: [F-032, F-033, F-034]
  - path: "tex-to-myst/src/index.ts"
    facts: [F-035]
---

# LaTeX/JATS 导入示例

本示例演示如何将现有的 JATS XML 学术论文和 LaTeX 文档导入为 MyST Markdown 格式，然后继续进行多格式导出。

## 场景一：从 JATS XML 导入

JATS（Journal Article Tag Suite）是学术出版的标准 XML 格式。许多期刊（PubMed Central、eLife、PLOS 等）提供 JATS XML 格式的论文全文。

### 前提条件

- 一个 JATS XML 文件（如从 PMC 下载）
- 已安装 mystmd 或 Jupyter Book v2

### 步骤 1：获取 JATS XML 文件

从 PubMed Central 下载一篇开放获取论文的 JATS XML：

```bash
# 示例：下载 PMC100000 的 JATS XML
curl -o paper.xml "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1000000/"
# 或使用 PMC 的 FTP 服务获取 .nxml 文件
```

JATS XML 结构示例：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<article article-type="research-article">
  <front>
    <journal-meta>
      <journal-title-group>
        <journal-title>Example Journal</journal-title>
      </journal-title-group>
    </journal-meta>
    <article-meta>
      <title-group>
        <article-title>An Example Research Paper</article-title>
      </title-group>
      <contrib-group>
        <contrib contrib-type="author">
          <name><surname>Smith</surname><given-names>John</given-names></name>
        </contrib>
      </contrib-group>
      <abstract>
        <p>This paper demonstrates JATS to MyST conversion.</p>
      </abstract>
    </article-meta>
  </front>
  <body>
    <sec>
      <title>Introduction</title>
      <p>This is the introduction with <bold>bold text</bold>
      and inline math <inline-formula><mml:math><mml:mi>E</mml:mi>
      <mml:mo>=</mml:mo><mml:mi>m</mml:mi><mml:msup><mml:mi>c</mml:mi>
      <mml:mn>2</mml:mn></mml:msup></mml:math></inline-formula>.</p>
      <fig id="fig1">
        <label>Figure 1</label>
        <caption><p>An example figure.</p></caption>
        <graphic xlink:href="fig1.png"/>
      </fig>
    </sec>
    <sec>
      <title>Methods</title>
      <p>...</p>
      <disp-formula id="eq1">
        <label>(1)</label>
        <mml:math><mml:mi>f</mml:mi><mml:mo>(</mml:mo><mml:mi>x</mml:mi>
        <mml:mo>)</mml:mo><mml:mo>=</mml:mo><mml:msup><mml:mi>x</mml:mi>
        <mml:mn>2</mml:mn></mml:msup></mml:math>
      </disp-formula>
    </sec>
  </body>
  <back>
    <ref-list>
      <ref id="ref1">
        <mixed-citation>Author A. (2023) Example paper. <italic>J. Example</italic> 1:1-10.</mixed-citation>
      </ref>
    </ref-list>
  </back>
</article>
```

### 步骤 2：使用编程 API 转换

```typescript
import { readFileSync, writeFileSync } from 'fs';
import { jatsToMystTransform } from 'jats-to-myst';
import { mystToHtmlPlugin } from 'myst-to-html';
import { unified } from 'unified';

// 读取 JATS XML
const xml = readFileSync('paper.xml', 'utf-8');

// 转换为 MDAST
const { tree, references } = jatsToMystTransform(xml, {
  // 可选：指定图片路径转换器
  // imageResolver: (href) => `/images/${href}`,
});

console.log(`Extracted ${Object.keys(references).length} references`);

// 转换为 HTML 预览
const htmlResult = unified()
  .use(mystToHtmlPlugin, { formatHtml: true })
  .stringify(
    unified().use(mystToHtmlPlugin).runSync(tree)
  );
writeFileSync('paper.html', htmlResult.toString());

// tree 是 MDAST，可以传递给任何 myst-to-xxx 导出器
```

### 步骤 3：通过 myst-cli 初始化项目

```bash
myst init paper.xml
# 自动检测 JATS 格式，调用 jats-to-myst 转换
# 生成 paper.md 和 myst.yml
```

### 步骤 4：构建为多种格式

转换为 MyST Markdown 后，可以像普通 MyST 文档一样构建：

```bash
myst build paper.md --pdf --html --docx
```

## 场景二：从 LaTeX 导入

LaTeX 导入比 JATS 更复杂，因为 LaTeX 是一种编程语言（宏展开），完整解析非常困难。tex-to-myst 支持常见的 LaTeX 结构。

### 前提条件

- 一个 LaTeX 文件（.tex）
- 注意：tex-to-myst 的成熟度低于 jats-to-myst，复杂宏包和自定义命令可能无法正确转换

### 示例 LaTeX 文件

创建 `paper.tex`：

```latex
\documentclass{article}
\usepackage{amsmath,graphicx}
\usepackage{hyperref}

\title{Sample LaTeX Document}
\author{Alice Author}
\date{\today}

\begin{document}
\maketitle

\begin{abstract}
This is a sample document for LaTeX to MyST conversion.
\end{abstract}

\section{Introduction}
\label{sec:intro}

This document demonstrates \textbf{bold} and \textit{italic} text.
We can reference Section~\ref{sec:methods}.

The famous equation is $E = mc^2$.

\begin{equation}
\label{eq:maxwell}
\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}
\end{equation}

See Equation~\ref{eq:maxwell}.

\section{Methods}
\label{sec:methods}

\begin{figure}[h]
  \centering
  \includegraphics[width=0.7\textwidth]{diagram.png}
  \caption{This is a diagram.}
  \label{fig:diagram}
\end{figure}

As shown in Figure~\ref{fig:diagram}, the method works.

\begin{table}[h]
  \centering
  \begin{tabular}{|c|c|}
    \hline
    \textbf{Parameter} & \textbf{Value} \\
    \hline
    Alpha & 0.05 \\
    Beta & 0.80 \\
    \hline
  \end{tabular}
  \caption{Parameter values.}
  \label{tab:params}
\end{table}

\subsection{Data Collection}
We collected data using the method described in \cite{smith2023}.

\section{Conclusion}
We conclude that the method is effective.

\begin{thebibliography}{9}
\bibitem{smith2023} Smith, J. (2023). A method. \textit{Journal of Methods}, 5(2), 1-10.
\end{thebibliography}

\end{document}
```

### 步骤 1：使用 tex-to-myst 转换

```typescript
import { readFileSync, writeFileSync } from 'fs';
import { unified } from 'unified';
// tex-to-myst 目前主要通过 CLI 集成，编程 API 较基础
```

### 步骤 2：通过 myst-cli 导入

```bash
myst init paper.tex
# 检测到 .tex 文件，调用 tex-to-myst 转换
```

### 预期输出（转换后的 MyST Markdown）

转换后大致得到以下 MyST 内容（具体取决于源文件复杂度）：

```markdown
---
title: "Sample LaTeX Document"
authors:
  - name: "Alice Author"
---

# Introduction

This document demonstrates **bold** and *italic* text.
We can reference [](#sec:methods).

The famous equation is $E = mc^2$.

$$
\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}
$$ (eq:maxwell)

See [](#eq:maxwell).

# Methods

![This is a diagram.](diagram.png){#fig:diagram}

As shown in [](#fig:diagram), the method works.

| Parameter | Value |
|-----------|-------|
| Alpha     | 0.05  |
| Beta      | 0.80  |

Table: Parameter values. {#tab:params}

## Data Collection

We collected data using the method described in [](#smith2023).

# Conclusion

We conclude that the method is effective.
```

### LaTeX 导入限制

tex-to-myst 目前有以下已知限制：

| LaTeX 功能 | 支持程度 | 说明 |
|-----------|---------|------|
| section/subsection | ✅ 良好 | 转换为 #/## 标题 |
| \textbf/\textit | ✅ 良好 | 转换为 **/*** |
| $...$ / $$...$$ | ✅ 良好 | 保留 LaTeX 数学语法 |
| equation 环境 | ✅ 良好 | 转换为 $$ 块公式 |
| figure/includegraphics | ⚠️ 基本 | 图片路径可能需要调整 |
| table/tabular | ⚠️ 基本 | 简单表格支持，复杂表格可能失败 |
| cite/bibitem | ⚠️ 基本 | 引用 key 保留，需要补全 bib 文件 |
| \ref | ⚠️ 基本 | 转换为 crossReference |
| \newcommand | ❌ 有限 | 自定义命令不展开 |
| TikZ/pgfplots | ❌ 不支持 | 需要特殊处理 |
| 复杂嵌套 | ❌ 可能失败 | 深层嵌套环境可能解析错误 |
| 宏包特有命令 | ❌ 不支持 | 如 algorithmic、chemformula 等 |

### 导入后的手动调整

LaTeX 导入后通常需要手动调整：

1. **检查图片路径**：确保图片文件在正确位置
2. **修复表格**：复杂表格可能需要手动重写
3. **补全参考文献**：将 bibitem 转换为 .bib 文件
4. **处理自定义命令**：手动展开 `\newcommand` 定义的命令
5. **修复特殊字符**：LaTeX 特殊字符（`~`, `\\`, `\,` 等）
6. **检查交叉引用**：确保 label 和引用对应正确

## 场景三：转换后多格式导出

无论是从 JATS 还是 LaTeX 导入，转换为 MyST 后都可以自由导出到任何格式：

```bash
# 从 JATS 导入后
myst init paper.xml
myst build paper.md --all

# 从 LaTeX 导入后
myst init paper.tex
myst build paper.md --pdf --html --docx
```

这实现了格式的自由转换：
- JATS → HTML（网页发布）
- JATS → PDF（排版出版）
- JATS → DOCX（编辑审阅）
- LaTeX → Markdown（简化内容）
- LaTeX → Typst PDF（现代排版）
- LaTeX → HTML（在线发布）

## 相关概念

- [05-jats-export](/concepts/05-jats-export.md)：JATS XML 导出（对称反向）
- [02-latex-export](/concepts/02-latex-export.md)：LaTeX 导出（对称反向）
- [09-import-converters](/concepts/09-import-converters.md)：导入转换器详解
