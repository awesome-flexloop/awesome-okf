---
type: bundle
title: jupyter-cache
description: Executable Books 生态的 Jupyter Notebook 执行缓存层，基于内容哈希避免重复执行，支持SQLite持久化、CLI/Python API、插件化执行器和CI集成
tags:
- jupyter
- cache
- notebook
- execution
- sqlalchemy
- sqlite
- cli
- mybinder
- executable-books
- ci-cd
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23T04:56:00Z"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
- id: jc-repo
  resource: "https://github.com/executablebooks/jupyter-cache"
  title: jupyter-cache GitHub Repository
okf_version: '0.2'
---

# jupyter-cache

jupyter-cache 是 Executable Books 生态中的 Jupyter Notebook 执行缓存工具。它为 Notebook 执行结果提供通用的缓存层，通过内容哈希机制避免重复执行未修改的 Notebook，显著加速文档构建和CI/CD流水线。

## 核心功能

- **内容哈希缓存**：基于代码单元格内容计算hashkey，相同代码复用执行结果
- **SQLite持久化**：缓存元数据存储在SQLite数据库中，支持跨构建会话
- **双表分离**：项目Notebook列表与缓存结果独立管理，支持多项目共享缓存
- **插件化架构**：通过entry points支持自定义执行器（Docker/远程Kernel等）和读取器（S3/GCS等）
- **命令行工具**：`jcache` CLI 管理缓存和执行流程
- **Python API**：完整的编程接口
- **LRU自动淘汰**：缓存超限时自动清理最久未访问的记录
- **Artifact管理**：Notebook执行产生的关联文件（图片、数据）一并缓存
- **MyST-NB集成**：与jupyter-book/MyST-NB无缝集成

## 文档导航

| 章节 | 链接 |
|------|------|
| 📖 入门 | [概念文档](/concepts/index.md) |
| 💡 示例 | [示例代码](/examples/index.md) |
| 📚 参考 | [源码参考](/references/index.md) |
| 🔬 规格 | [事实清单](/spec/facts.md) · [架构洞察](/spec/insights.md) |

## 快速开始

```bash
pip install jupyter-cache
```

```bash
# 添加Notebook到项目
jcache notebook add notebooks/*.ipynb

# 执行（已缓存的跳过）
jcache notebook execute-all

# 再次执行（仅执行修改过的Notebook）
jcache notebook execute-all
```

Python API：

```python
from jupyter_cache import get_cache
cache = get_cache(".jupyter_cache")
cache.add_notebook_file("notebook.ipynb")
cache.execute_all_notebooks()
```

## 更新日志

见 [log.md](/log.md)。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
