---
type: reference
title: "配置类源码（jupyterlab_latex/config.py）"
description: "LatexConfig traitlets 配置类，定义 LaTeX 引擎、BibTeX、SyncTeX、shell escape、编译次数、清理策略和自定义命令参数"
tags: [config, traitlets, latex-config, shell-escape, tectonic, manual-cmd]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:13:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: config-py
    resource: "../../../../../external/libs/jupyter/jupyterlab-latex/jupyterlab_latex/config.py"
    title: "jupyterlab_latex/config.py"
---

# 配置类源码（jupyterlab_latex/config.py）

本信源登记 `jupyterlab_latex/config.py`（约33行），定义了基于 traitlets 的 `LatexConfig` 配置类，提供 LaTeX 编译的所有可配置参数。

## LatexConfig 类

继承自 `traitlets.config.Configurable`，通过 `c.LatexConfig.<option>` 在 `jupyter_notebook_config.py` 中配置。

### 配置项

| 配置项 | Traitlet 类型 | 默认值 | 说明 |
|--------|--------------|--------|------|
| `latex_command` | `Unicode` | `'xelatex'` | LaTeX 编译引擎命令（如 xelatex、pdflatex、lualatex、tectonic） |
| `disable_bibtex` | `Bool` | `False` | 是否禁用 BibTeX 编译（v4.2.0 新增） |
| `bib_command` | `Unicode` | `'bibtex'` | BibTeX 参考文献处理命令 |
| `synctex_command` | `Unicode` | `'synctex'` | SyncTeX 同步命令行工具名 |
| `shell_escape` | `CaselessStrEnum` | `'restricted'` | Shell 转义安全级别：`restricted`（默认，仅允许安全命令）、`allow`（允许所有命令）、`disallow`（禁止所有命令） |
| `run_times` | `Integer` | `1` | LaTeX 编译次数（用于处理交叉引用，需要 ≥2） |
| `cleanup` | `Bool` | `False` | 是否清理编译产生的临时文件（非 .pdf/.synctex.gz 等保留文件） |
| `manual_cmd_args` | `List(Unicode())` | `[]` | 用户自定义完整命令参数列表，支持 `{filename}` 占位符（v4.2.0 新增） |

### 导入依赖

```python
from traitlets import Unicode, CaselessStrEnum, Integer, Bool, List as TraitletsList
from traitlets.config import Configurable
```

注意：`List` 被别名为 `TraitletsList`，以避免与 Python 内置 `list` 冲突。

### 配置使用方式

在 `jupyter_notebook_config.py` 中：

```python
# 切换到 pdflatex
c.LatexConfig.latex_command = 'pdflatex'

# 启用完全 shell escape（安全风险！）
c.LatexConfig.shell_escape = 'allow'

# 多次编译以处理交叉引用
c.LatexConfig.run_times = 2

# 使用 Tectonic 引擎
c.LatexConfig.latex_command = 'tectonic'

# 完全自定义命令序列
c.LatexConfig.manual_cmd_args = [
    'lualatex',
    '-interaction=nonstopmode',
    '-halt-on-error',
    '-shell-escape',
    '-synctex=1',
    '{filename}.tex'
]
```

### 实例化方式

在 build.py 和 synctex.py 中通过 `LatexConfig(config=self.config)` 从 handler 的 config 属性创建实例，自动继承 Jupyter 服务器配置系统中的设置值。
