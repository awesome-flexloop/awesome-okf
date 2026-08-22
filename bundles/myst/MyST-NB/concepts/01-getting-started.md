---
type: Concept
title: 快速开始
description: 安装 MyST-NB、最小 conf.py 配置、第一个可执行 Notebook 文档
tags: [myst-nb, quickstart, install, setup, conf.py]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## 快速开始

## 安装

```bash
pip install myst-nb
```

MyST-NB 会自动安装 MyST-Parser、nbclient、nbformat、jupyter-cache 等依赖。如果需要执行 Python 代码，还需要安装 ipykernel（已列为依赖，会自动安装）。

## 最小 Sphinx 配置

创建以下项目结构：

```
my-notebook-docs/
├── conf.py
├── index.md
└── notebooks/
    └── first.ipynb
```

### conf.py

```python
# conf.py
project = "My Notebook Docs"
extensions = ["myst_nb"]
master_doc = "index"
exclude_patterns = ["_build", "**.ipynb_checkpoints"]
html_theme = "alabaster"

# MyST-NB 配置（全部可选，以下为默认值）
nb_execution_mode = "auto"       # 自动执行（有缺失输出时执行）
nb_execution_timeout = 30        # 单 cell 执行超时（秒）
```

### index.md

```markdown
# 我的 Notebook 文档

欢迎使用 MyST-NB！

```{toctree}
notebooks/first
```
```

### 创建第一个 Notebook

方式一：使用 Jupyter 创建 `notebooks/first.ipynb`，添加一个代码 cell：

```python
print("Hello, MyST-NB!")
```

方式二：使用文本格式创建 `notebooks/first.md`：

````markdown
---
file_format: mystnb
kernelspec:
  name: python3
---

# 我的第一个 Notebook

这是一个 Markdown cell。

```{code-cell}
print("Hello, MyST-NB!")
```
````

## 构建文档

```bash
sphinx-build -b html . _build/html
```

打开 `_build/html/index.html` 即可看到包含代码执行输出的文档。

## 使用 mystnb-quickstart 脚手架

MyST-NB 提供了快速创建项目模板的 CLI：

```bash
mystnb-quickstart my-docs
cd my-docs
sphinx-build -b html . _build/html
```

该命令会生成：
- `conf.py`：包含所有 `nb_*` 配置项（注释形式）
- `index.md`：包含 toctree 的首页
- `notebook1.ipynb`：Jupyter Notebook 示例
- `notebook2.md`：文本格式 Notebook 示例
- `.gitignore`：排除 _build 和 .ipynb_checkpoints

## 文本格式 Notebook 转换为 .ipynb

```bash
mystnb-to-jupyter notebook.md notebook.ipynb
```

## 执行模式快速选择

| 场景 | 推荐模式 | 配置 |
|------|---------|------|
| 首次构建/CI 构建 | `auto`（默认） | `nb_execution_mode = "auto"` |
| 本地开发频繁构建 | `cache` | `nb_execution_mode = "cache"` |
| 强制重新执行所有代码 | `force` | `nb_execution_mode = "force"` |
| 仅渲染不执行（已有输出） | `off` | `nb_execution_mode = "off"` |

## 相关概念

- [MyST Notebook 文件格式](02-notebook-format.md)
- [执行模式与缓存](05-execution-modes.md)
- [配置系统](04-config-system.md)
- [基础配置示例](/examples/01-basic-setup.md)
