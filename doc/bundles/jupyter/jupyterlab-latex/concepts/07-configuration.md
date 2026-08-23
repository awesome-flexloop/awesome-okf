---
type: concept
title: "配置指南"
description: "jupyterlab-latex 的全部配置项详解，包括后端 traitlets 配置（LaTeX引擎、BibTeX命令、shell escape、编译次数、自定义参数、PDF目录）和前端设置（SyncTeX开关）"
tags: [configuration, traitlets, latex-engine, shell-escape, bibtex, run-times, jupyter-config, settings]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: config-py
    resource: "/references/config-py-source.md"
    title: "配置类源码"
  - id: build-py
    resource: "/references/build-py-source.md"
    title: "编译处理器源码"
  - id: schema-plugin
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/schema/plugin.json"
    title: "前端设置 Schema"
  - id: conf-readme
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/jupyter-config/jupyter_notebook_config.d/jupyterlab_latex.json"
    title: "默认配置 JSON"
---

# 配置指南

jupyterlab-latex 的配置分为两部分：**后端 Python 配置**（通过 traitlets 管理，控制编译行为）和**前端设置**（通过 JupyterLab Settings 管理，控制 SyncTeX 等 UI 行为）。

## 配置层级

```
┌─────────────────────────────────────────────────────┐
│  配置优先级（高→低）                                  │
│                                                     │
│  1. 命令行参数 (--LatexConfig.latex_command=xelatex) │
│  2. 用户配置文件 (~/.jupyter/jupyter_notebook_config.py) │
│  3. 环境变量 (JUPYTER_LATEX_*)                       │
│  4. 扩展默认配置 (jupyter_config/)                   │
│  5. traitlets 默认值 (config.py)                     │
└─────────────────────────────────────────────────────┘
```

## 后端配置项（LatexConfig）

所有后端配置通过 `LatexConfig` 类定义，使用 traitlets 类型系统。配置项在 `jupyter_notebook_config.py` 中以 `c.LatexConfig.<option>` 形式设置。

### latex_command

| 属性 | 值 |
|------|-----|
| 类型 | `Unicode` |
| 默认值 | `'xelatex'` |
| 说明 | LaTeX 编译引擎命令 |

支持的值：
- `'xelatex'`（默认）— XeLaTeX，支持 Unicode 和系统字体，推荐中文用户使用
- `'pdflatex'` — pdfLaTeX，传统引擎，编译速度快
- `'lualatex'` — LuaLaTeX，支持 Lua 脚本和 OpenType 字体
- `'tectonic'` — Tectonic，现代 Rust 引擎，自动下载依赖
- 任意可执行文件名（如 `'latexmk'`、`'arara'`，需配合 `manual_cmd_args` 使用）

**示例：切换为 pdfLaTeX**
```python
# jupyter_notebook_config.py
c.LatexConfig.latex_command = 'pdflatex'
```

**示例：使用 Tectonic**
```python
c.LatexConfig.latex_command = 'tectonic'
```
使用 Tectonic 时，扩展自动切换到 Tectonic 命令序列（`tectonic --synctex --keep-logs --outfmt pdf <file>`），不需要 BibTeX 额外步骤。

### bib_command

| 属性 | 值 |
|------|-----|
| 类型 | `Unicode` |
| 默认值 | `'bibtex'` |
| 说明 | BibTeX 参考文献处理命令 |

当项目中检测到 `.bib` 文件或 `\bibliography`/`\addbibresource` 命令时，扩展会在编译轮次间运行此命令。

**示例：使用 biber（biblatex 后端）**
```python
c.LatexConfig.bib_command = 'biber'
```
注意：使用 `biber` 时，编译序列仍为 `xelatex → biber → xelatex → xelatex`，但 biber 处理 `.bcf` 文件而非 `.aux` 文件。确保文档中使用 `\usepackage[backend=biber]{biblatex}`。

### shell_escape

| 属性 | 值 |
|------|-----|
| 类型 | `Bool` |
| 默认值 | `False` |
| 说明 | 是否启用 `\write18` shell escape |

启用 shell escape 后，LaTeX 可以执行外部系统命令（通过 `\write18` 或 `\ShellEscape`），这是某些宏包（如 `minted` 代码高亮、`asymptote` 绘图、`gnuplot` 绘图）的必需条件。

**安全警告**：shell escape 允许 LaTeX 文档执行任意系统命令，存在安全风险。仅在编译可信文档时启用。

**示例：启用 shell escape（使用 minted 包时必须）**
```python
c.LatexConfig.shell_escape = True
```

启用后编译命令追加 `-shell-escape` 参数：
```bash
xelatex -shell-escape -synctex=1 -interaction=nonstopmode -file-line-error <file>
```

### run_times

| 属性 | 值 |
|------|-----|
| 类型 | `Integer` |
| 默认值 | `1` |
| 说明 | LaTeX 编译轮数 |

LaTeX 需要多轮编译来解析交叉引用、目录、参考文献等。默认 `run_times=1` 仅编译一轮，适合简单文档。

**推荐值**：
| 文档复杂度 | run_times | 说明 |
|-----------|-----------|------|
| 简单文档（无交叉引用） | 1 | 最快 |
| 有目录/交叉引用 | 2 | 解析 ref |
| 有参考文献（无 BibTeX 自动检测） | 3 | 两轮解析引用+一轮生成目录 |
| 使用 latexmk | 1 | latexmk 自动决定轮数（配合 manual_cmd_args） |

**注意**：如果检测到 `.bib` 文件，无论 `run_times` 设置多少，都会使用4轮序列（latex → bibtex → latex → latex）。`run_times` 仅在无 BibTeX 时生效。

**示例：编译3轮以确保交叉引用正确**
```python
c.LatexConfig.run_times = 3
```
生成命令序列：`[xelatex, xelatex, xelatex]`（每轮都带相同参数）。

### manual_cmd_args

| 属性 | 值 |
|------|-----|
| 类型 | `List(Unicode)` |
| 默认值 | `[]` |
| 说明 | 完全自定义编译命令参数列表 |

设置后将完全替代自动构建的命令序列，只执行一条命令。命令格式为 `manual_cmd_args + [tex_base_name]`。

如果 `run_synctex=1`，会额外追加 `['-synctex=1', '-interaction=nonstopmode']`。

**示例：使用 latexmk**
```python
c.LatexConfig.manual_cmd_args = ['latexmk', '-xelatex', '-synctex=1', '-interaction=nonstopmode']
```
注意：使用 manual_cmd_args 时，`latex_command`、`bib_command`、`shell_escape`、`run_times` 的设置将被忽略。

**示例：使用 arara**
```python
c.LatexConfig.manual_cmd_args = ['arara']
```

### pdf_dir

| 属性 | 值 |
|------|-----|
| 类型 | `Unicode` |
| 默认值：`'.'` |
| 说明 | PDF 输出目录 |

默认情况下，PDF 输出到 `.tex` 文件所在目录。设置此选项可将 PDF 输出到指定子目录。

**示例：PDF 输出到 build 子目录**
```python
c.LatexConfig.pdf_dir = 'build'
```
注意：扩展会在编译后查找 PDF 文件，如果设置了非默认目录，确保 SyncTeX 和文件管理器能正确定位 PDF。当前实现中 `.synctex.gz` 也在编译目录中生成，自定义 pdf_dir 时需要验证同步功能正常。

## 前端设置项

前端设置通过 JupyterLab Settings 系统管理，在 Settings → Settings Editor → LaTeX 中配置。设置定义在 `schema/plugin.json` 中。

### synctex

| 属性 | 值 |
|------|-----|
| 类型 | `boolean` |
| 默认值 | `true` |
| 说明 | 是否启用 SyncTeX 双向同步 |

关闭后：
- 编译请求不发送 `synctex=1` 参数
- 编译命令不包含 `-synctex=1`
- 编辑器光标移动不触发正向同步
- PDF Shift+Click 不触发反向同步
- `.synctex.gz` 文件不会生成（减小磁盘占用）

**示例：关闭 SyncTeX**

在 JupyterLab Settings Editor 中找到 LaTeX 插件，取消勾选 "Enable SyncTeX"，或在 User Preferences 中设置：
```json
{
    "synctex": false
}
```

## 配置文件位置

### Jupyter 配置文件

Jupyter Server 配置文件位置：

| 平台 | 路径 |
|------|------|
| Linux/macOS | `~/.jupyter/jupyter_notebook_config.py` |
| Windows | `%USERPROFILE%\.jupyter\jupyter_notebook_config.py` |

如果文件不存在，生成默认配置：
```bash
jupyter server --generate-config
```

### 扩展默认配置

扩展自带的默认配置位于 `jupyter-config/jupyter_notebook_config.d/jupyterlab_latex.json`：
```json
{
    "LatexConfig": {
        "latex_command": "xelatex",
        "bib_command": "bibtex",
        "shell_escape": false,
        "run_times": 1,
        "pdf_dir": "."
    }
}
```
此文件随 pip/conda 包安装到 Jupyter 配置目录，提供默认值。用户配置文件中的设置会覆盖这些默认值。

## 配置验证

配置加载后，可通过以下方式验证：

### 检查后端配置

```bash
jupyter server --show-config
```
在输出中查找 `LatexConfig` 段，确认配置项值正确。

### 检查编译命令

在 JupyterLab 中打开 `.tex` 文件，触发编译后查看 Jupyter Server 日志输出，可以看到实际执行的编译命令：
```
[I 2024-01-01 12:00:00. LatexBuildHandler] Building: xelatex -synctex=1 -interaction=nonstopmode -file-line-error test
```

## 常见配置场景

### 场景1：中文文档

中文文档推荐使用 XeLaTeX + 系统字体：
```python
c.LatexConfig.latex_command = 'xelatex'
c.LatexConfig.shell_escape = False  # 除非需要 minted
```
文档中使用 `ctex` 文档类或 `xeCJK` 宏包：
```latex
\documentclass{ctexart}
\begin{document}
中文内容
\end{document}
```

### 场景2：使用 BibLaTeX + Biber

```python
c.LatexConfig.bib_command = 'biber'
c.LatexConfig.run_times = 1  # BibTeX 自动检测时会覆盖为4轮
```

### 场景3：使用 minted 代码高亮

```python
c.LatexConfig.shell_escape = True  # minted 需要 pygmentize
```
文档中：
```latex
\usepackage{minted}
\begin{document}
\begin{minted}{python}
print("Hello")
\end{minted}
\end{document}
```

### 场景4：使用 latexmk 全自动编译

```python
c.LatexConfig.manual_cmd_args = [
    'latexmk', '-xelatex',
    '-synctex=1', '-interaction=nonstopmode',
    '-file-line-error'
]
```
latexmk 自动检测依赖变化，决定需要重新编译的轮数。

---

**下一步阅读：**
- [配置示例](../examples/03-configuration.md) — 完整配置示例
- [故障排查](../examples/04-troubleshooting.md) — 常见配置问题诊断
