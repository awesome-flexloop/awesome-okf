# sphinx-demo 实践示例

本文档目录包含 JupyterLite Sphinx Demo 的实践教程，从最小站点到完整双内核配置，每个示例都可以直接参照操作。

## 示例文档列表

| 文档 | 难度 | 核心内容 |
|------|------|----------|
| [01-最小可运行站点](01-minimal-site.md) | ⭐ 入门 | 6步从零搭建：安装→目录→conf.py→index.md→构建→预览，含启用TryExamples扩展 |
| [02-Pyodide内核完整配置](02-pyodide-setup.md) | ⭐⭐ 中级 | 复刻sphinx-demo Pyodide示例：完整conf.py、四层JSON配置、自定义CSS、示例模块 |
| [03-Xeus内核完整配置](03-xeus-setup.md) | ⭐⭐ 中级 | Xeus特有配置：environment.yml包管理、XPython内核名、micromamba构建、CI差异 |
| [04-嵌入可交互Matplotlib笔记本](04-matplotlib-notebook.md) | ⭐⭐ 中级 | notebooklite实战：strip标签、remove-input、多子图绘图、ipywidgets交互 |

## 前置知识

| 示例 | 建议先读 |
|------|---------|
| 01-最小站点 | 无需前置知识 |
| 02-Pyodide配置 | [01-最小站点](01-minimal-site.md) + [conf.py配置](/concepts/03-sphinx-conf.md) |
| 03-Xeus配置 | [02-Pyodide配置](02-pyodide-setup.md) + [内核对比](/concepts/04-kernel-comparison.md) |
| 04-Matplotlib笔记本 | [02或03配置示例](02-pyodide-setup.md) + [NotebookLite](/concepts/07-notebook-embedding.md) |

## 快速选择

- **第一次接触** → 从 [01-最小站点](01-minimal-site.md) 开始
- **要做Pyodide文档** → [02-Pyodide配置](02-pyodide-setup.md)
- **需要预编译包（ipycanvas等）** → [03-Xeus配置](03-xeus-setup.md)
- **要嵌入可视化Notebook** → [04-Matplotlib笔记本](04-matplotlib-notebook.md)

```{toctree}
:hidden:
:maxdepth: 7

01-minimal-site
02-pyodide-setup
03-xeus-setup
04-matplotlib-notebook
```
