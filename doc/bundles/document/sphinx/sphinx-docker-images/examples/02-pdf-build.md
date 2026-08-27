---
type: example
title: "PDF 文档构建（含中文）"
description: "使用 sphinx-latexpdf 镜像构建 LaTeX/PDF 文档，包括中文 PDF 的完整配置"
tags: [example, pdf, latex, chinese, cjk]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:49:00Z" }
status: active
stale_after: 2027-08-21
sources:
  - { id: readme, resource: "/references/readme-source.md", title: "README 原文与使用说明" }
  - { id: latexpdf, resource: "/references/dockerfile-latexpdf.md", title: "LaTeX/PDF 镜像 Dockerfile 源码" }
---

# PDF 文档构建（含中文）

本示例演示如何使用 `sphinxdoc/sphinx-latexpdf` 镜像构建 PDF 文档，重点讲解中文 PDF 的配置。

## 前置条件

- 已安装 Docker
- 有一个已初始化的 Sphinx 项目（参见 [基础 HTML 构建](01-basic-html-build.md)）
- 首次使用需拉取 latexpdf 镜像（>2GiB，请耐心等待）：
  ```bash
  docker pull sphinxdoc/sphinx-latexpdf:8.2.3
  ```

## 配置中文 PDF

### 步骤 1：修改 conf.py

在你的 Sphinx 项目的 `conf.py` 中添加或修改以下配置：

```python
# -- LaTeX/PDF 输出配置 ------------------------------------------------

# 使用 XeLaTeX 引擎（中文推荐）
latex_engine = 'xelatex'

# 文档类配置
latex_documents = [
    ('index', 'mydocs.tex', 'My Docs', 'Author Name', 'manual'),
]

# LaTeX 元素配置
latex_elements = {
    # 纸张大小和字号
    'papersize': 'a4paper',
    'pointsize': '11pt',

    # 中文支持（使用 ctex 宏包）
    'preamble': r'''
        \usepackage{ctex}
        \usepackage{indentfirst}
        \setlength{\parindent}{2em}
    ''',

    # 额外选项
    'extraclassoptions': 'openany,oneside',
}
```

**配置说明**：

| 配置项 | 说明 |
|--------|------|
| `latex_engine = 'xelatex'` | 使用 XeTeX 引擎，原生支持 Unicode 和系统字体 |
| `\usepackage{ctex}` | ctex 宏包自动处理中文排版（字体、缩进、间距） |
| `\usepackage{indentfirst}` | 首段缩进（中文排版习惯） |
| `openany` | 章节可以在任意页开始（避免空白页） |
| `oneside` | 单面排版（适合电子版阅读） |

### 步骤 2：构建 PDF

```bash
# 在文档目录下执行
docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx-latexpdf \
  sphinx-build -M latexpdf . _build
```

Windows PowerShell：
```powershell
docker run --rm -v "${PWD}:/docs" sphinxdoc/sphinx-latexpdf `
  sphinx-build -M latexpdf . _build
```

### 步骤 3：获取 PDF

构建成功后，PDF 文件位于：
- `_build/latex/mydocs.pdf`（文件名由 latex_documents 中指定）
- 或 `_build/latex/<project-name>.pdf`

## 英文 PDF（无需特殊配置）

如果文档是纯英文，不需要 ctex，使用最简配置即可：

```python
# conf.py
latex_engine = 'xelatex'  # 或 pdflatex
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
}
```

构建命令相同：
```bash
docker run --rm -v "$(pwd):/docs" sphinxdoc/sphinx-latexpdf \
  sphinx-build -M latexpdf . _build
```

## 多语言 PDF（中日韩）

latexpdf 镜像内置了日文支持。如果需要日文文档：

```python
latex_engine = 'xelatex'
latex_elements = {
    'preamble': r'''
        \usepackage{ctex}  % 中文
        % 日文使用 pxjahyper 或 jlreq
        % \usepackage{pxjahyper}
    ''',
}
```

## 自定义封面

通过 `latex_elements` 自定义封面页：

```python
latex_elements = {
    'preamble': r'''
        \usepackage{ctex}
        \usepackage{graphicx}
    ''',
    'maketitle': r'''
        \begin{titlepage}
            \centering
            \vspace*{3cm}
            {\Huge\bfseries My Documentation\par}
            \vspace{1cm}
            {\Large\itshape 技术文档\par}
            \vspace{2cm}
            {\Large Author Name\par}
            \vfill
            {\large \today\par}
        \end{titlepage}
    ''',
}
```

## 常见问题

**Q: 构建报错 `Package ctex Error: The font "FandolSong" cannot be found`**

ctex 宏包默认使用 Fandol 字体。latexpdf 镜像中已包含该字体，如果仍然报错，可以手动指定字体：

```python
latex_elements = {
    'preamble': r'''
        \usepackage{ctex}
        \setCJKmainfont{Noto Serif CJK SC}  % 使用 Noto 字体
    ''',
}
```

**Q: PDF 中代码块显示异常（中文乱码或空白）**

确保在 `conf.py` 中设置：
```python
latex_engine = 'xelatex'
```
不要使用 `pdflatex`，它不支持 Unicode 字符。

**Q: 如何生成带目录和书签的 PDF？**

sphinx-build 默认会生成目录和 PDF 书签。如果需要在 PDF 侧边栏显示书签，确保使用 `xelatex` 引擎并安装了正确的宏包。

**Q: PDF 构建很慢（几分钟）正常吗？**

正常。LaTeX 需要多次编译（latexmk 自动运行 2-3 次）以生成正确的目录、交叉引用和索引。

## 相关概念

- [LaTeX/PDF 镜像详解](../concepts/04-latexpdf-image.md)：了解 TeXLive 包选择
- [5 分钟快速上手](../concepts/01-getting-started.md)：基本的 Docker 使用
- [自定义镜像扩展](03-custom-image.md)：安装额外 LaTeX 包
