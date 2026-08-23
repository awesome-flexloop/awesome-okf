---
type: "concept"
title: "LaTeX 与 PDF 输出定制"
description: "Sphinx LaTeX/PDF输出定制——latex_engine选择、latex_elements配置、sphinxsetup键、中文支持、字体设置、页眉页脚、封面定制"
tags: [latex, pdf, output, customization, xelatex]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T10:55:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T10:55:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: official-latex
    resource: /references/official-docs.md
    title: "Sphinx 官方文档 LaTeX customization 章节"
---

# LaTeX 与 PDF 输出定制

Sphinx 的 `latex` Builder 生成 `.tex` 文件，可通过 LaTeX 编译器（xelatex/pdflatex/lualatex）编译为 PDF。与HTML Builder有丰富的主题不同，LaTeX输出的定制主要通过 `latex_elements` 和 `sphinxsetup` 配置项完成。

## 快速开始

### 构建PDF

```bash
# 方法一：使用Makefile
make latexpdf

# 方法二：手动两步
sphinx-build -b latex docs/ _build/latex/
cd _build/latex && make
```

### 最小配置

```python
# conf.py
latex_engine = 'xelatex'  # 推荐：支持Unicode和中文
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
}
```

## LaTeX引擎选择

| 引擎 | Unicode | 中文支持 | 推荐场景 |
|------|---------|---------|---------|
| `pdflatex` | ⚠️ 有限 | ❌ 需CJK包 | 纯英文文档 |
| `xelatex` | ✅ 原生 | ✅ 优秀 | **推荐**：中英文文档 |
| `lualatex` | ✅ 原生 | ✅ 良好 | 需要Lua脚本扩展 |

```python
latex_engine = 'xelatex'  # 中文文档必选
```

## latex_elements 配置

`latex_elements` 是一个字典，键对应LaTeX模板中的各个部分：

### 纸张与字体大小

```python
latex_elements = {
    'papersize': 'a4paper',      # 'a4paper' 或 'letterpaper'
    'pointsize': '11pt',         # '10pt', '11pt', '12pt'
    'pxunit': '0.75bp',          # 像素单位定义 (96px=1in)
}
```

### 导言区（preamble）

`preamble` 键插入自定义LaTeX命令到导言区，是最常用的定制入口：

```python
latex_elements = {
    'preamble': r'''
% 自定义包
\usepackage{ctex}                % 中文支持
\usepackage{listings}            % 代码列表
\usepackage{booktabs}            % 表格线
\usepackage{geometry}            % 页边距
\geometry{left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm}

% 代码块样式
\fvset{fontsize=\small}

% 自定义颜色
\definecolor{TitleColor}{RGB}{26,13,171}
''',
}
```

> ⚠️ 注意：Python字符串中反斜杠需要转义，推荐使用raw字符串（`r'...'`）。

### passoptionstopackages

在 `\documentclass` 之后、加载包之前传递选项：

```python
latex_elements = {
    'passoptionstopackages': r'''
\PassOptionsToPackage{svgnames}{xcolor}
''',
}
```

### fontpkg — 字体配置

```python
latex_elements = {
    'fontpkg': r'''
\setmainfont{DejaVu Serif}          % 衬线字体（正文）
\setsansfont{DejaVu Sans}           % 无衬线字体（标题）
\setmonofont{DejaVu Sans Mono}      % 等宽字体（代码）
''',
}
```

**中文字体配置（使用ctex包）**：

```python
latex_engine = 'xelatex'
latex_elements = {
    'preamble': r'''
\usepackage{ctex}
\setCJKmainfont{Noto Serif CJK SC}
\setCJKsansfont{Noto Sans CJK SC}
\setCJKmonofont{Noto Sans Mono CJK SC}
''',
}
```

### fncychap — 章节标题样式

```python
latex_elements = {
    'fncychap': r'\usepackage[Bjornstrup]{fncychap}',
}
```

可用样式：`Sonny`、`Lenny`、`Glenn`、`Conny`、`Rejne`、`Bjarne`、`Bjornstrup`。

### printindex — 索引打印

```python
latex_elements = {
    'printindex': r'\footnotesize\raggedright\printindex',
}
```

### maketitle — 封面页

完全自定义封面：

```python
latex_elements = {
    'maketitle': r'''
\begin{titlepage}
\centering
\vspace*{3cm}
{\Huge\bfseries 项目名称\par}
\vspace{1cm}
{\Large 项目副标题\par}
\vspace{2cm}
{\Large 作者名\par}
\vspace{1cm}
{\large \today\par}
\end{titlepage}
''',
}
```

### tableofcontents — 目录

```python
latex_elements = {
    'tableofcontents': r'''
\tableofcontents
\listoffigures
\listoftables
''',
}
```

## sphinxsetup 配置

`sphinxsetup` 提供CSS-like的键值配置：

```python
latex_elements = {
    'sphinxsetup': '''
TitleColor=DarkGoldenrod,
InnerLinkColor=red,
OuterLinkColor=blue,
VerbatimColor={rgb}{0.95,0.95,0.95},
VerbatimBorderColor={rgb}{0.8,0.8,0.8},
''',
}
```

### 常用sphinxsetup键

| 键 | 说明 | 默认值 |
|----|------|--------|
| `TitleColor` | 标题颜色 | `{rgb}{0.1,0.1,0.5}` |
| `InnerLinkColor` | 内部交叉链接颜色 | `{rgb}{0.2,0.2,1}` |
| `OuterLinkColor` | 外部URL颜色 | `{rgb}{0,0,0.8}` |
| `VerbatimColor` | 代码块背景色 | `{rgb}{1,1,1}` |
| `VerbatimBorderColor` | 代码块边框颜色 | `{rgb}{0,0,0}` |
| `VerbatimHighlightColor` | 代码高亮行背景色 | — |
| `HeaderFamily` | 标题字体族 | `\rmfamily\bfseries` |
| `verbatimwithframe` | 代码块是否带边框 | `true` |
| `verbatimwrapslines` | 代码行是否自动换行 | `true` |

## 中文PDF输出配置

完整的中文PDF配置示例：

```python
# conf.py
latex_engine = 'xelatex'

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    'preamble': r'''
\usepackage{ctex}
\usepackage{geometry}
\geometry{left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm}

% 中文字体
\setCJKmainfont{Noto Serif CJK SC}[AutoFakeBold]
\setCJKsansfont{Noto Sans CJK SC}[AutoFakeBold]
\setCJKmonofont{Noto Sans Mono CJK SC}

% 代码块样式
\fvset{fontsize=\footnotesize}

% 链接颜色
\usepackage{xcolor}
\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue}
''',
    'printindex': r'\footnotesize\raggedright\printindex',
}

latex_documents = [
    ('index', 'ProjectName.tex', '项目名称',
     '作者名', 'manual'),
]
```

### 中文字体安装

确保系统安装了中文字体：

```bash
# Ubuntu/Debian
sudo apt install fonts-noto-cjk fonts-noto-cjk-extra

# macOS（系统自带思源字体或手动安装）
# Windows（系统自带微软雅黑/宋体）
```

## 文档元数据配置

```python
# 文档信息
project = '项目名称'
author = '作者名'
copyright = '2026, 作者名'
release = '1.0.0'
version = '1.0'

# LaTeX文档列表
latex_documents = [
    (
        'index',          # 源文档名
        'MyProject.tex',  # 输出tex文件名
        '项目标题',        # LaTeX标题
        '作者名',          # 作者
        'manual',         # 文档类：'manual'|'howto'
    ),
]

# LaTeX文档类选项
latex_docclass = {
    'manual': 'ctexbook',      # 中文书籍类
    'howto': 'ctexart',        # 中文文章类
}

# 额外的文档（如附录）
latex_additional_files = []
```

### manual vs howto

| 文档类 | 特点 | 适合场景 |
|--------|------|---------|
| `manual` | 双页、有章（chapter）、标题页、目录 | 书籍、完整手册 |
| `howto` | 单页、无章（section开始）、更简洁 | 简短指南、教程 |

## 其他LaTeX配置选项

```python
# 显示URL在脚注中（避免长URL破坏排版）
latex_show_urls = 'footnote'   # 'inline'|'footnote'|'no'

# 页码显示URL
latex_show_pagerefs = True

# 附录文档
latex_appendices = ['appendix/glossary', 'appendix/changelog']

# 文档域（影响标题文本等）
latex_domain_indices = True     # 生成模块索引

# 主题（影响颜色和布局）
latex_theme = 'default'        # 'default' 是唯一内置主题

# 使用TeXLive的附加包
latex_toplevel_sectioning = None  # None自动选择：manual→chapter, howto→section
```

## PDF构建环境

### 安装LaTeX发行版

```bash
# Ubuntu/Debian（最小安装）
sudo apt install texlive-xetex texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra texlive-lang-chinese

# macOS
brew install --cask mactex

# Windows
# 安装 MiKTeX 或 TeX Live
```

### 使用Docker（推荐CI环境）

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-xetex \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-lang-chinese \
    fonts-noto-cjk \
    make \
    && rm -rf /var/lib/apt/lists/*

RUN pip install sphinx furo myst-parser

WORKDIR /docs
```

## 常见问题

### Q: 中文乱码或不显示？

确保：
1. 使用 `latex_engine = 'xelatex'`
2. 在 `preamble` 中加载 `ctex` 包
3. 设置了中文字体（`\setCJKmainfont` 等）
4. 系统安装了对应中文字体

### Q: 代码块过长超出页面？

```python
latex_elements = {
    'preamble': r'''
\usepackage{fvextra}
\fvset{breaklines=true, breakanywhere=true}
''',
}
```

### Q: 不想用LaTeX生成PDF？

第三方替代方案：
- **rinohtype**：纯Python PDF Builder，无需LaTeX安装
  ```python
  extensions = ['rinoh']
  # 构建：sphinx-build -b rinoh docs/ _build/pdf
  ```
- **weasyprint**：HTML→PDF（需配合html5 Builder）
- **wkhtmltopdf**：HTML→PDF命令行工具

### Q: 生成目录/索引？

```python
latex_elements = {
    'tableofcontents': r'\tableofcontents',
    'printindex': r'\printindex',
}
```

确保 `latex_domain_indices = True`（默认）。

## 相关概念

- [Builder构建器体系](10-builder-system.md)
- [HTML构建器详解](11-html-builder.md)
- [主题系统](13-theme-system.md)
- [配置系统](04-config-system.md)
