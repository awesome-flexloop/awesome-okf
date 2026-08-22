---
type: example
title: "配置示例"
description: "jupyterlab-latex 的典型配置场景实例，包括切换 LaTeX 引擎、使用 BibLaTeX+Biber、启用 shell escape、自定义编译命令、配置 Tectonic"
tags: [configuration, xelatex, pdflatex, tectonic, biber, shell-escape, latexmk, ctex]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: config-py
    resource: "/references/config-py-source.md"
    title: "配置类源码"
  - id: conf-default
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/jupyter-config/jupyter_notebook_config.d/jupyterlab_latex.json"
    title: "默认配置"
prerequisites:
  - concepts/07-configuration
  - examples/01-basic-usage
---

# 配置示例

本示例提供常见配置场景的完整代码，可直接复制到 `jupyter_notebook_config.py` 中使用。

## 配置文件基础

找到或创建 Jupyter 配置文件：

```bash
# 生成默认配置（如果不存在）
jupyter server --generate-config

# 配置文件位置
# Linux/macOS: ~/.jupyter/jupyter_notebook_config.py
# Windows: %USERPROFILE%\.jupyter\jupyter_notebook_config.py
```

所有配置以 `c.LatexConfig.` 为前缀。配置修改后需要**重启 Jupyter Server** 生效。

## 场景 1：中文文档（XeLaTeX + ctex）

适用于中文用户，使用 XeLaTeX 引擎配合 ctex 文档类。

```python
# jupyter_notebook_config.py
c.LatexConfig.latex_command = 'xelatex'
c.LatexConfig.shell_escape = False
c.LatexConfig.run_times = 1
```

对应的 LaTeX 文档：
```latex
\documentclass{ctexart}
\title{中文测试文档}
\author{作者名}
\date{\today}

\begin{document}
\maketitle

\section{简介}
这是一个使用 ctex 文档类的中文文档。XeLaTeX 直接支持系统字体，
无需额外配置即可正确排版中文。

\begin{itemize}
    \item 支持中文标点
    \item 支持段落缩进
    \item 行距自动调整
\end{itemize}

\end{document}
```

## 场景 2：使用 pdfLaTeX（英文文档最快）

pdfLaTeX 编译速度快，但对 Unicode 支持有限，适合纯英文文档。

```python
c.LatexConfig.latex_command = 'pdflatex'
c.LatexConfig.run_times = 2  # 两轮编译以解析交叉引用
```

## 场景 3：使用 Tectonic（现代引擎，无需安装 TeX Live）

Tectonic 是基于 XeTeX 的现代引擎，自动下载所需宏包，适合不想安装完整 TeX Live 的用户。

首先安装 Tectonic：
```bash
# 方式一：conda
conda install tectonic

# 方式二：下载二进制
# https://github.com/tectonic-typesetting/tectonic/releases
```

配置：
```python
c.LatexConfig.latex_command = 'tectonic'
```

Tectonic 配置特点：
- 自动下载缺失的宏包（首次使用需要联网）
- 内置 BibTeX 处理，不需要额外配置 bib_command
- 自动处理多轮编译
- 生成的 PDF 输出到当前目录

## 场景 4：BibLaTeX + Biber（现代参考文献）

使用 biblatex 宏包配合 biber 后端，比传统 BibTeX 更灵活。

```python
c.LatexConfig.latex_command = 'xelatex'
c.LatexConfig.bib_command = 'biber'
c.LatexConfig.run_times = 1  # 检测到 .bib 自动使用4轮序列
```

对应的 LaTeX 文档：
```latex
\documentclass{article}
\usepackage[backend=biber,style=authoryear]{biblatex}
\addbibresource{references.bib}

\begin{document}
See \textcite{knuth1984literate} for more details.

\printbibliography
\end{document}
```

注意：使用 biber 时确保 biber 版本与 biblatex 版本兼容。

## 场景 5：启用 Shell Escape（minted 代码高亮）

使用 `minted` 包进行代码高亮需要启用 shell escape（minted 调用 pygmentize）。

```python
c.LatexConfig.shell_escape = True
```

确保系统已安装 Python 和 Pygments：
```bash
pip install Pygments
```

对应的 LaTeX 文档：
```latex
\documentclass{article}
\usepackage{minted}

\begin{document}
Python code example:

\begin{minted}{python}
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
\end{minted}

\end{document}
```

**安全提醒**：启用 shell_escape 后，LaTeX 文档可以执行任意系统命令，只编译信任的文档。

## 场景 6：使用 latexmk（全自动编译）

latexmk 是 Perl 编写的自动化编译工具，自动决定需要运行 LaTeX 和 BibTeX 的次数。

首先安装 latexmk：
```bash
# TeX Live 自带，MiKTeX 通过包管理器安装
# 或：conda install latexmk
```

配置：
```python
c.LatexConfig.manual_cmd_args = [
    'latexmk',
    '-xelatex',
    '-synctex=1',
    '-interaction=nonstopmode',
    '-file-line-error',
]
```

使用 `manual_cmd_args` 时，其他编译选项（latex_command, bib_command, shell_escape, run_times）都被忽略。latexmk 会自动：
- 检测依赖变化（源码、图片、参考文献）
- 运行必要的编译轮数
- 调用 BibTeX/Biber 处理参考文献
- 在源码稳定时停止编译

## 场景 7：多轮编译（复杂交叉引用）

对于有目录、索引、多轮交叉引用的复杂文档，增加编译次数：

```python
c.LatexConfig.latex_command = 'xelatex'
c.LatexConfig.run_times = 3  # 编译3轮
```

编译序列变为：`[xelatex, xelatex, xelatex]`。

注意：如果检测到 `.bib` 文件，无论 run_times 设为多少，都会使用 `[latex, bibtex, latex, latex]` 四遍序列。

## 场景 8：关闭 SyncTeX（性能模式）

在大文档或低性能环境中，关闭 SyncTeX 可以减少编译开销：

在 JupyterLab Settings Editor 中设置：
```json
{
    "synctex": false
}
```

或在 User Preferences 中添加上述配置。关闭后编译命令不包含 `-synctex=1`，不生成 `.synctex.gz` 文件。

## 完整配置示例

一个适合中文论文写作的完整配置：

```python
# ~/.jupyter/jupyter_notebook_config.py

# 使用 XeLaTeX 引擎（支持中文和 Unicode）
c.LatexConfig.latex_command = 'xelatex'

# 使用 BibTeX（传统后端，兼容性最好）
c.LatexConfig.bib_command = 'bibtex'

# 不启用 shell escape（安全）
c.LatexConfig.shell_escape = False

# 默认编译1轮（检测到 .bib 时自动4轮）
c.LatexConfig.run_times = 1

# PDF 输出到当前目录
c.LatexConfig.pdf_dir = '.'
```

## 验证配置生效

修改配置后，重启 Jupyter Server：

1. 在 JupyterLab 菜单选择 File → Shut Down
2. 重新启动 `jupyter lab`
3. 打开一个 `.tex` 文件
4. 触发编译，查看终端日志中的编译命令：
   - 确认使用的引擎正确
   - 确认包含/不包含 `-shell-escape` 参数
   - 确认包含/不包含 `-synctex=1` 参数

## 配置项速查表

| 配置项 | 类型 | 默认值 | 何时修改 |
|--------|------|--------|---------|
| `latex_command` | str | `'xelatex'` | 切换引擎（pdflatex/lualatex/tectonic） |
| `bib_command` | str | `'bibtex'` | 使用 biber 时改为 `'biber'` |
| `shell_escape` | bool | `False` | 使用 minted/asymptote 时改为 `True` |
| `run_times` | int | `1` | 复杂文档需要多轮编译时增加 |
| `manual_cmd_args` | list | `[]` | 使用 latexmk 等外部工具时设置 |
| `pdf_dir` | str | `'.'` | 需要将 PDF 输出到子目录时设置 |

---

**相关概念文档**：
- [配置指南](../concepts/07-configuration.md) — 所有配置项的详细说明
- [LaTeX 编译流程](../concepts/03-latex-compilation.md) — 编译命令序列构建逻辑
