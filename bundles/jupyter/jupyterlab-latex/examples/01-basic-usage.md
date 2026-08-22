---
type: example
title: "基本使用示例"
description: "从零开始使用 jupyterlab-latex 编写和预览 LaTeX 文档的完整操作步骤，包括新建文档、编写内容、实时预览、格式化编辑"
tags: [basic-usage, hello-world, preview, editing, formatting]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: readme
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/README.md"
    title: "README.md"
  - id: sample-tex
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/sample.tex"
    title: "示例 LaTeX 文件"
  - id: basic-ipynb
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/examples/basic-example.ipynb"
    title: "basic-example.ipynb"
prerequisites:
  - concepts/01-getting-started
  - concepts/06-editing-tools
---

# 基本使用示例

本示例演示安装扩展后，从新建 LaTeX 文件到实时预览的完整流程。

## 目标

- 新建一个 `.tex` 文件
- 编写包含标题、段落、列表和数学公式的 LaTeX 文档
- 打开实时 PDF 预览
- 使用工具栏按钮格式化文本
- 观察保存后自动编译更新预览

## 示例 1：Hello World 文档

### 步骤 1：新建文件

点击 Launcher 中的 **LaTeX File** 卡片（Other 分类），或通过菜单 File → New → LaTeX File。

新文件默认名为 `untitled.tex`，你可以通过右键 Rename 改为 `hello.tex`。

### 步骤 2：写入最小文档

在编辑器中输入以下内容：

```latex
\documentclass{article}
\title{My First LaTeX Document}
\author{Your Name}
\date{\today}

\begin{document}
\maketitle

Hello, \LaTeX! This is my first document created in JupyterLab.

\end{document}
```

### 步骤 3：保存并预览

1. 按 **Ctrl+S** 保存文件
2. 点击编辑器工具栏上的 **Preview** 按钮
3. 右侧面板出现 PDF 预览，显示编译后的文档

此时观察 Jupyter Server 终端日志，应看到类似输出：
```
[I] Building: xelatex -synctex=1 -interaction=nonstopmode -file-line-error hello
```

### 步骤 4：实时更新

在文档末尾 `\end{document}` 前添加内容：

```latex
\section{Introduction}
LaTeX is a high-quality typesetting system. It is widely used in academia for
publishing scientific papers, books, and technical documentation.

\subsection{Features}
\begin{itemize}
    \item Professional typesetting
    \item Excellent math support
    \item Cross-referencing
    \item Bibliography management
\end{itemize}
```

再次按 **Ctrl+S**，观察 PDF 预览自动更新，新添加的章节和列表出现在 PDF 中。

## 示例 2：数学公式

在文档中添加数学公式部分：

```latex
\section{Mathematics}

Inline math: Euler's identity $e^{i\pi} + 1 = 0$ is often considered the most
beautiful equation in mathematics.

Display math:
\begin{equation}
    \int_{-\infty}^{\infty} e^{-x^2} \, dx = \sqrt{\pi}
\end{equation}

The quadratic formula:
\begin{equation}
    x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
\end{equation}
```

**使用工具栏插入**：
1. 将光标放在要插入分数的位置
2. 点击工具栏上的 **X/Y** 分数按钮
3. 在弹出的对话框中输入分子 `-b \pm \sqrt{b^2 - 4ac}`
4. 在第二个对话框中输入分母 `2a`
5. 自动插入 `\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}`

## 示例 3：格式化文本

使用工具栏按钮格式化文本：

1. 选中一段文字
2. 点击 **B**（粗体）按钮 → 文字被包裹为 `\textbf{文字}`
3. 点击 **I**（斜体）按钮 → 文字被包裹为 `\textit{文字}`
4. 点击居中按钮 → 文字被包裹为 `\centerline{文字}`

不选中文字直接点击按钮时：
- 插入空命令（如 `\textbf{}`）
- 光标自动定位到花括号内
- 直接输入文字即可应用格式

## 示例 4：插入表格

1. 点击工具栏上的**表格**按钮
2. 在第一个对话框输入列数：`3`
3. 在第二个对话框输入行数：`4`（含表头）
4. 自动生成以下代码：

```latex
\begin{tabular}{|c|c|c|}
    \hline
     &  & \\
    \hline
     &  & \\
    \hline
     &  & \\
    \hline
     &  & \\
    \hline
\end{tabular}
```

填入内容：

```latex
\begin{tabular}{|c|c|c|}
    \hline
    \textbf{Name} & \textbf{Age} & \textbf{City} \\
    \hline
    Alice & 28 & Beijing \\
    \hline
    Bob & 35 & Shanghai \\
    \hline
    Charlie & 22 & Guangzhou \\
    \hline
\end{tabular}
```

保存后 PDF 中显示一个带边框的 3×4 表格。

## 示例 5：参考文献

创建一个简单的文档，手动运行 BibTeX 处理流程（扩展自动检测）：

创建 `references.bib` 文件：
```bibtex
@article{knuth1984literate,
    title={Literate programming},
    author={Knuth, Donald E},
    journal={The Computer Journal},
    volume={27},
    number={2},
    pages={97--111},
    year={1984},
    publisher={Oxford University Press}
}
```

在 `hello.tex` 中添加：
```latex
\section{References}
As described by Knuth~\cite{knuth1984literate}, literate programming combines
documentation and code in a single document.

\bibliographystyle{plain}
\bibliography{references}
```

保存后，扩展检测到 `\bibliography{references}` 命令，自动执行4轮编译序列：
```
xelatex → bibtex → xelatex → xelatex
```

PDF 末尾出现参考文献列表，引用编号正确显示。

## 预期结果

完成以上示例后，你应该能够：
- ✅ 看到 PDF 在右侧面板实时显示
- ✅ 每次保存后 PDF 自动更新
- ✅ 使用工具栏按钮插入格式化命令
- ✅ 编译成功时无错误面板弹出
- ✅ 包含参考文献的文档正确编译

## 常见操作速查

| 操作 | 方法 |
|------|------|
| 打开预览 | 工具栏 Preview 按钮 / 右键 Show LaTeX Preview |
| 手动刷新预览 | 再次点击 Preview 按钮 |
| 编译保存 | Ctrl+S 自动触发 |
| 插入粗体 | 选中文本 → B 按钮 |
| 插入公式 | 输入 `$...$`（行内）或 equation 环境（显示） |
| 新建 .tex | Launcher → LaTeX File |

---

**相关概念文档**：
- [编辑工具栏与快捷操作](../concepts/06-editing-tools.md) — 所有按钮的详细说明
- [LaTeX 编译流程](../concepts/03-latex-compilation.md) — 了解编译背后发生了什么
