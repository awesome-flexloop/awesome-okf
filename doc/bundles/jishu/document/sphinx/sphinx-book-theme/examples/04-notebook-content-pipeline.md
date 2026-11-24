---
type: Example
title: "Notebook 内容流水线"
description: "用 MyST-NB + sphinx-book-theme 构建可执行的 Notebook 文档：配置、单元格标签、缓存、下载 .ipynb、CI 构建与常见故障"
tags: [sphinx, theme, example, myst-nb, notebook, ci, cache]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-notebooks
    resource: https://sphinx-book-theme.readthedocs.io/en/latest/content/notebooks.html
    title: Jupyter notebooks
  - id: myst-nb-docs
    resource: https://myst-nb.readthedocs.io/
    title: MyST-NB documentation
---

# Notebook 内容流水线

目标：把 `.ipynb` 和 MyST 代码单元格纳入书籍构建，输出可复现、可下载、可在线运行的页面。

## 1. 安装

```bash
pip install "sphinx>=8.2" sphinx-book-theme myst-nb \
            numpy matplotlib pandas ipykernel
python -m ipykernel install --user --name python3
```

## 2. conf.py

```python
extensions = [
    "myst_nb",
]

source_suffix = {
    ".md": "myst-nb",
    ".ipynb": "myst-nb",
    ".rst": "restructuredtext",
}

# Notebook 文件与 MyST Markdown 混合时，优先按 myst-nb 解析
nb_execution_mode = "cache"
nb_execution_timeout = 120
nb_execution_allow_errors = False
nb_execution_show_tb = "READTHEDOCS" in os.environ

# 缓存目录不要放进源码树
nb_execution_cache_path = "_build/.jupyter_cache"

html_theme = "sphinx_book_theme"
html_theme_options = {
    "use_download_button": True,
    "repository_url": "https://github.com/your-org/your-repo",
    "repository_branch": "main",
    "path_to_docs": "docs",
}
```

| 配置 | 建议 | 说明 |
|------|------|------|
| `nb_execution_mode` | `cache` | 本地开发快，CI 可改 `force` |
| `nb_execution_timeout` | 60–300 | 防止某个单元格卡死整次构建 |
| `nb_execution_allow_errors` | `False` | 有错就失败，避免发布坏结果 |
| `nb_execution_show_tb` | 仅 CI | 本地不打印长堆栈 |
| `nb_execution_cache_path` | `_build/` 下 | 不污染源码目录 |

## 3. 一个 Notebook 页面

`docs/part-1/analysis.ipynb` 的单元格结构：

```text
[markdown] # 数据分析示例
[markdown] 本页演示如何把计算结果嵌入书中。
[code]     :tags: [hide-cell]
           import numpy as np
           import matplotlib.pyplot as plt
[code]     :tags: [thebe-init]
           np.random.seed(0)
           data = np.random.randn(200)
[code]     fig, ax = plt.subplots()
           ax.hist(data, bins=30)
           plt.show()
[code]     :tags: [hide-input]
           import pandas as pd
           df = pd.DataFrame({"value": data})
           df.describe()
```

在 `.ipynb` 里，标签写在单元格 metadata：

```json
{
  "tags": ["hide-input"]
}
```

在 MyST Markdown 里，用 `:tags:` 选项：

````md
```{code-cell} python
:tags: [hide-input]

import pandas as pd
```
````

## 4. 常用标签组合

| 目标 | 标签 |
|------|------|
| 只显示结果，不显示代码 | `hide-input` |
| 只显示代码，不显示结果 | `hide-output` |
| 完全隐藏但保留执行 | `remove-cell`（不显示） / `hide-cell`（占位隐藏） |
| 结果太长，加滚动条 | `output_scroll` |
| 代码太长，加滚动条 | `scroll-input` |
| 放进右侧留白 | `margin` |
| 全宽展示 | `full-width` |
| Thebe 初始化 | `thebe-init` |

## 5. 下载 `.ipynb`

主题会在页面是 Notebook 时，自动把 `_build/jupyter_execute/<pagename>.ipynb` 复制到 `_build/html/_sources/<pagename>.ipynb`，并在下载组里加 `.ipynb` 按钮。

验收：

1. 构建后检查 `_build/jupyter_execute/part-1/analysis.ipynb` 是否存在。
2. 检查 `_build/html/_sources/part-1/analysis.ipynb` 是否存在。
3. 页面右上角下载菜单里应有 `.ipynb`。

若缺失：

- 页面没有被识别为 Notebook（检查 `kernelspec` 或源文件后缀）；
- `use_download_button` 被关闭；
- 构建没有产生 `jupyter_execute`（执行模式为 `off` 且没有缓存）。

## 6. CI 构建

GitHub Actions 示例：

```yaml
name: docs

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install "sphinx>=8.2" sphinx-book-theme myst-nb numpy matplotlib pandas ipykernel
      - run: python -m ipykernel install --user --name python3
      - name: Build docs
        env:
          NB_EXECUTION_MODE: force
        run: sphinx-build -b html docs _build/html -W --keep-going
      - uses: actions/upload-pages-artifact@v3
        with:
          path: _build/html
```

要点：

- CI 用 `force`，确保结果不是旧缓存。
- `-W --keep-going` 把 warning 当错误，但继续收集全部问题。
- 上传前确认 `_build/html/_sources` 里的 `.ipynb` 也在产物中。

## 7. 常见故障

### `ModuleNotFoundError` 在构建时出现

构建环境缺少 notebook 里 import 的包。把依赖写进 `requirements.txt` 或 `environment.yml`，CI 与 Binder 共用一份。

### 构建卡住

某个单元格在等输入、下载大数据或死循环。加 `nb_execution_timeout`，并检查单元格是否有 `input()`、无限循环、未设超时的网络请求。

### 输出每次构建都变

随机数、时间戳、模型推理会导致 diff 噪音。固定随机种子，或在单元格里隐藏时间戳；必要时把该页设为 `nb_execution_mode = "off"` 并提交输出。

### 图片过大导致页面卡顿

在 Notebook 里控制 `figsize` 与 `dpi`，或把大图生成为静态文件后引用。

### 下载的 `.ipynb` 是旧版本

清理 `_build` 与 `nb_execution_cache_path` 后重新构建。`cache` 模式可能复用旧执行结果。

### Thebe 无法初始化

- 确认 `sphinx_thebe` 在 `extensions`；
- 确认 `launch_buttons["thebe"]` 为 `True`；
- 确认至少有一个 `thebe-init` 单元格；
- 确认 Binder 环境能安装 notebook 依赖。

## 8. 内容组织建议

- 一个 Notebook 只讲一个主题，避免 30 个单元格的"大杂烩"。
- 把 import 与全局配置放进 `hide-cell` 或 `thebe-init` 单元格。
- 数据文件放 `docs/data/`，用相对路径引用；不要把大文件提交进 git。
- 计算结果用 `hide-input` 展示，让读者先看结论。
- 需要读者修改的代码用 Thebe；只读结论用静态输出。

## 相关概念

- [Notebook 与在线交互](../concepts/07-jupyter-interactivity.md)
- [仓库按钮与在线启动按钮](02-repository-and-launch-buttons.md)
- [配置选项全解](../concepts/04-theme-options.md)
