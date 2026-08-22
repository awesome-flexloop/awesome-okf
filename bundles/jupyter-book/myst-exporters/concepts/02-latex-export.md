---
type: concept
title: "LaTeX 导出"
description: "myst-to-tex 将 MDAST 转换为 LaTeX 的 TexSerializer 架构、Handler 映射表、导言区生成和 Beamer 支持"
tags: [myst-exporters, latex, tex, serializer, beamer, cite]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "myst-to-tex/src/index.ts"
    facts: [F-002, F-003, F-004, F-005, F-006, F-007, F-008]
  - path: "myst-to-tex/src/types.ts"
    facts: [F-009]
  - path: "myst-to-tex/src/preamble.ts"
    facts: [F-010]
---

# LaTeX 导出

LaTeX 导出由 `myst-to-tex` 包提供，核心是 `TexSerializer` 类。它将 MDAST 遍历转换为 LaTeX 源代码字符串，并收集导言区所需的包引用、数学宏命令、术语表/缩写定义等结构化信息。

## TexSerializer 架构

```typescript
class TexSerializer implements ITexSerializer {
  file: VFile;
  data: StateData;
  options: Options;
  handlers: Record<string, Handler>;
  references: References;
  footnotes: Record<string, FootnoteDefinition>;
  glossary: Record<string, [string, string]>;
  abbreviations: Record<string, [string, string]>;
}
```

构造函数执行以下步骤：
1. 初始化 `file.result = ''`（输出字符串）
2. 设置 `data: { mathPlugins: {}, imports: new Set() }`
3. 从 tree 中一次性提取 footnotes、glossary、abbreviations 定义
4. 调用 `this.renderChildren(tree)` 遍历整个 AST，写入 LaTeX 到 `file.result`

### 核心方法

| 方法 | 说明 |
|------|------|
| `write(value)` | 直接追加字符串到输出 |
| `text(value, mathMode?)` | 转义后写入文本（数学模式/文本模式不同转义规则） |
| `usePackages(...names)` | 添加 `\usepackage` 到 imports Set |
| `trimEnd()` | 去除末尾空白 |
| `ensureNewLine(trim?)` | 确保以换行结尾 |
| `renderChildren(node, inline?, delim?)` | 遍历子节点，按 type 查 handler 表分发 |
| `renderEnvironment(node, env, opts?)` | 生成 `\begin{env}...\end{env}` 块环境 |
| `renderInlineEnvironment(node, env, opts?)` | 生成 `\env{...}` 内联命令 |
| `closeBlock(node)` | 块结束时确保换行 |

## LatexResult 输出结构

TexSerializer 的 Compiler 不直接输出字符串，而是输出结构化的 `LatexResult`：

```typescript
type LatexResult = {
  value: string;        // LaTeX 正文内容（document 环境内的部分）
  imports: string[];    // 需要 \usepackage 的包列表
  preamble: PreambleData; // 导言区数据
  commands: Record<string, string>; // 数学宏命令（\newcommand）
};

type PreambleData = {
  hasProofs?: boolean;
  hasIndex?: boolean;
  printGlossaries?: boolean;
  glossary: Record<string, [string, string]>;
  abbreviations: Record<string, [string, string]>;
};
```

这种结构化输出允许 jtex 模板引擎将 imports、preamble、commands 正确地插入到模板的导言区位置，而非全部塞到 document 内。

## Handler 映射要点

### 标题层级

MyST heading 的 `depth` 映射到 LaTeX 章节命令：

| depth | LaTeX 命令 | 说明 |
|-------|-----------|------|
| -1 | `\part{}` | 部分 |
| 0 | `\chapter{}` | 章 |
| 1 | `\section{}` | 节 |
| 2 | `\subsection{}` | 小节 |
| 3 | `\subsubsection{}` | 子小节 |
| 4-6 | `\paragraph{}`/`\subparagraph{}` | 段落级标题 |

当 `enumerated !== false` 时带 `*` 星号（不编号），并在标题后输出 `\label{label}`。

### 代码块

支持三种代码样式，通过 `options.codeStyle` 或代码块 class 控制：
- **verbatim**（默认）：`\begin{verbatim}...\end{verbatim}`
- **listings**：`\begin{lstlisting}[language=xx]...\end{lstlisting}`，使用 `\usepackage{listings}`
- **minted**：`\begin{minted}[breaklines]{lang}...\end{minted}`，使用 `\usepackage{minted}`

### 列表

- 无序列表：`itemize` 环境
- 有序列表：`enumerate` 环境（start≠1 时加 `resume` 参数）
- 任务列表（checked）：`\item[$\blacksquare$]`（已完成）或 `\item[$\square$]`（未完成）
- 表格内列表：使用 `\textbullet~~`/`N.~~` + `\newline` 而非嵌套环境

### 引用

- 普通链接：`\url{url}`（URL 即显示文本）或 `\href{url}{text}`
- 交叉引用：`\ref{id}`，支持模板字符串（`%s` 替换为引用编号）
- 术语表引用：`\gls{id}`
- 缩写引用：`\acrshort{id}`

### 参考文献

支持两种引用风格：
- **natbib**（默认）：`\cite{key}`、`\citet{key}`（叙述式）、`\citep{key}`（括号式）
- **biblatex**：`\textcite{key}`、`\parencite{key}`
- 数字模式：`numerical-only` 选项使用 `\cite{key}`

### 图片

```latex
\includegraphics[width=0.7\textwidth]{path/to/image}
```

默认宽度 `DEFAULT_IMAGE_WIDTH = 0.7`（70% 文本宽度），通过 `getLatexImageWidth` 计算。

### 数学

MATH_HANDLERS 处理 math/inlineMath 节点，`withRecursiveCommands(state)` 处理递归的数学宏定义。数学节点输出 LaTeX 数学环境（`$...$` 或 `\[...\]`/`equation` 环境）。

### 原始 LaTeX 透传

`raw` 节点如果有 `node.tex` 属性，直接写入输出，实现 LaTeX 原生命令透传。

## Beamer 演示支持

当 `options.beamer = true` 时：
- `block` 节点映射到 `\begin{frame}...\end{frame}`
- `block` 的第一个 `heading` 子节点映射到 `\frametitle{...}`
- 带 `outline` metadata tag 的 block 不包装为 frame，直接渲染内容（用于大纲页）

## 导言区生成

`generatePreamble(data)` 函数（preamble.ts）根据 PreambleData 生成导言区：

- **hasProofs**：添加证明环境的宏定义（`TexProofSerializer`）
- **hasIndex**：添加 `\makeindex`
- **printGlossaries**：
  - 添加 `\usepackage[acronym]{glossaries}` + `\makeglossaries`
  - 为每个术语生成 `\newglossaryentry{key}{name=..., description={...}}`
  - 为每个缩写生成 `\newacronym{key}{acronym}{expansion}`
  - suffix 包含 `\printglossaries`

`mergePreambles(current, next, warningLogFn)` 合并多个 PreambleData，重复 key 时发出警告。

## 包依赖追踪

Handler 中通过 `state.usePackages('packagename')` 按需引用包，最终收集到 `LatexResult.imports` 中：

| 功能 | 引用的包 |
|------|---------|
| URL/链接 | url, hyperref |
| 图片 | graphicx |
| 删除线 | ulem |
| 代码（listings 样式）| listings |
| 代码（minted 样式）| minted |
| 警示框 | framed |
| 索引 | imakeidx |
| 术语表 | glossaries |
| 缩写 | glossaries[acronym] |
| SI 单位 | siunitx |
| 参考文献 | natbib（默认）或 biblatex |

## 相关概念

- [00-exporter-architecture](/concepts/00-exporter-architecture.md)：统一导出架构
- [03-pdf-export](/concepts/03-pdf-export.md)：PDF 生成（LaTeX→latexmk）
- [07-typst-export](/concepts/07-typst-export.md)：Typst 导出（与 LaTeX 对比）
- [08-jtex-template-engine](/concepts/08-jtex-template-engine.md)：jtex 模板引擎整合 LaTeX 输出
- [02-custom-jtex-template](/examples/02-custom-jtex-template.md)：自定义 LaTeX 模板示例
