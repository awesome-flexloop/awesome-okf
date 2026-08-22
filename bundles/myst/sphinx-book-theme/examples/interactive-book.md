---
type: example
title: 交互式计算书籍配置
description: 配置Binder/Colab/JupyterHub启动按钮、Thebe在线代码执行、Jupyter笔记本下载的完整示例
tags:
- sphinx-book-theme
- example
- interactive
- binder
- colab
- thebe
- jupyter
generated: 2026-08-23
status: stable
stale_after: 2027-08-23
sources:
- src/sphinx_book_theme/header_buttons/launch.py
---

# 交互式计算书籍配置示例

本示例展示如何配置sphinx-book-theme与Jupyter笔记本、Binder、Google Colab、Thebe等交互式计算功能集成。

## 依赖安装

```bash
pip install sphinx-book-theme myst-nb sphinx-thebe
```

`myst-nb` 用于执行和渲染Jupyter笔记本，`sphinx-thebe` 提供在线代码执行功能。

## Binder 配置

Binder 允许读者在云端Jupyter环境中一键运行笔记本：

```python
# conf.py
project = "交互式计算书籍"
author = "作者名"
copyright = "2024, 作者名"

extensions = [
    "sphinx_book_theme",
    "myst_nb",
    "sphinx_thebe",
]

html_theme = "sphinx_book_theme"
html_theme_options = {
    # 仓库配置（Binder需要）
    "repository_url": "https://github.com/username/interactive-book",
    "repository_branch": "main",
    "path_to_docs": "docs",
    # 启动按钮配置
    "launch_buttons": {
        "binderhub_url": "https://mybinder.org",
        "notebook_interface": "jupyterlab",  # 使用JupyterLab界面
    },
    # 源码按钮
    "use_repository_button": True,
    "use_source_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
    # 下载按钮（自动包含ipynb下载）
    "use_download_button": True,
    "use_fullscreen_button": True,
}

# myst-nb 配置
nb_execution_mode = "auto"  # 自动执行笔记本（缓存）
nb_execution_timeout = 60   # 执行超时时间（秒）

# Thebe 配置
thebe_config = {
    "repository_url": "https://github.com/username/interactive-book",
    "repository_branch": "main",
    "selector": "div.cell div.cell_input",  # 选择代码单元
}
```

## 多平台启动按钮配置

同时配置Binder、Colab、JupyterHub、Deepnote、JupyterLite：

```python
html_theme_options = {
    "repository_url": "https://github.com/username/interactive-book",
    "repository_branch": "main",
    "path_to_docs": "docs",
    "launch_buttons": {
        # Binder（公共免费服务）
        "binderhub_url": "https://mybinder.org",
        # Google Colab（仅GitHub仓库）
        "colab_url": "https://colab.research.google.com",
        # JupyterHub（自建或机构JupyterHub）
        "jupyterhub_url": "https://jupyter.example.edu",
        # Deepnote（仅GitHub仓库）
        "deepnote_url": "https://deepnote.com",
        # JupyterLite（纯前端，无需后端）
        "jupyterlite_url": "https://username.github.io/jupyterlite",
        # 界面选择
        "notebook_interface": "jupyterlab",
    },
}
```

> **注意**：Colab和Deepnote仅支持GitHub仓库（F-132、F-184）。使用GitLab/Bitbucket时这些按钮不会显示并发出警告。

## Thebe 在线代码执行配置

Thebe 允许读者直接在网页上运行代码块，无需离开页面或打开外部服务：

```python
extensions = [
    "sphinx_book_theme",
    "myst_nb",
    "sphinx_thebe",  # 必须添加此扩展
]

html_theme_options = {
    "repository_url": "https://github.com/username/interactive-book",
    "repository_branch": "main",
    "path_to_docs": "docs",
    "launch_buttons": {
        "thebe": True,  # 启用Thebe按钮
    },
}

# Thebe 配置（如不在html_theme_options中设置repository_url，需在此设置）
thebe_config = {
    "binderUrl": "https://mybinder.org",
    "binderSettings": {
        "repo": "username/interactive-book",
        "branch": "main",
    },
    "selector": "div.cell_input",
}
```

Thebe按钮点击后会调用 `initThebeSBT()` 函数（F-143-F-156）：
1. 在页面h1标题后插入 thebe-launch-button
2. 调用 sphinx-thebe 提供的 initThebe() 函数
3. 连接到Binder后端，将代码单元变为可执行状态

## JupyterLite 配置

JupyterLite 是纯前端的Jupyter环境（基于Pyodide），不需要后端服务器：

```python
html_theme_options = {
    "launch_buttons": {
        "jupyterlite_url": "https://username.github.io/jupyterlite",
        "jupyterlite_ext": ".ipynb",  # 可选，指定文件扩展名
    },
}
```

## 使用MyST Markdown写笔记本

使用MyST Markdown（.md文件）编写内容时，SBT自动检测并提供ipynb下载：

```markdown
---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# 第一章

这是一个包含代码的笔记本页面。

```{code-cell}
print("Hello, World!")
```

```{code-cell}
import numpy as np
x = np.linspace(0, 2*np.pi, 100)
print(f"x shape: {x.shape}")
```
```

`kernelspec` 元数据是触发"笔记本页面"检测的关键（F-255-F-257）。没有kernelspec但文件扩展名为.ipynb的页面也会被检测为笔记本（F-258-F-260）。

构建时，myst-nb将.md文件编译为.ipynb，SBT自动将ipynb复制到_sources目录（F-067-F-082），下载按钮组中自动出现.ipynb下载选项。

## 完整项目结构

```
interactive-book/
├── docs/
│   ├── _static/
│   │   └── ...
│   ├── _toc.yml
│   ├── conf.py
│   ├── index.md
│   ├── chapter1/
│   │   ├── intro.md         # MyST笔记本（含code-cell）
│   │   ├── code-basics.md
│   │   └── notebook.ipynb   # 原生Jupyter笔记本
│   └── chapter2/
│       └── advanced.md
├── requirements.txt
└── README.md
```

requirements.txt：
```
sphinx-book-theme
myst-nb
sphinx-thebe
sphinx-copybutton
sphinx-design
```

## 要求文件配置（.binder/）

为了让Binder正确构建环境，在仓库根目录创建 `.binder/` 目录：

```
interactive-book/
├── .binder/
│   ├── requirements.txt    # Binder环境依赖
│   └── postBuild           # 构建后脚本（可选）
└── docs/
```

`.binder/requirements.txt`：
```
numpy
matplotlib
pandas
```

## 按钮组合效果

配置完成后，文章头部右侧会出现以下按钮：

1. **🚀 启动按钮组**（下拉）：
   - Binder
   - JupyterLab
   - Colab
   - Deepnote
   - JupyterLite
   - Live Code（Thebe）

2. **📥 下载按钮组**（下拉）：
   - .ipynb（笔记本页面）
   - .md/.rst（源文件）
   - .pdf（打印）

3. **🔧 源码按钮组**（下拉或单图标）：
   - Repository（仓库主页）
   - Show source（查看源码）
   - Suggest edit（建议编辑）
   - Open issue（提交Issue）

4. **独立按钮**：
   - 🔳 全屏模式
   - 🎨 主题切换
   - 🔍 搜索
   - 📑 次级侧边栏切换

## 启动按钮URL构建参考

各平台URL构建规则（源码实现）：

| 平台 | URL格式 |
|------|---------|
| Binder(GitHub) | `{binderhub_url}/v2/gh/{org}/{repo}/{branch}?urlpath=lab/tree/{path}` |
| Binder(GitLab) | `{binderhub_url}/v2/gl/{org}%2F{repo}/{branch}?urlpath=...` |
| Binder(通用Git) | `{binderhub_url}/v2/git/{quoted_url}/{branch}?urlpath=...` |
| JupyterHub | `{hub_url}/hub/user-redirect/git-pull?repo={url}&urlpath=tree/{repo}/{path}&branch={branch}` |
| Colab | `https://colab.research.google.com/github/{org}/{repo}/blob/{branch}/{path}` |
| Deepnote | `https://deepnote.com/launch?url=https%3A%2F%2Fgithub.com%2F{org}%2F{repo}%2Fblob%2F{branch}%2F{path}` |
| JupyterLite | `{jl_url}?path={path}` |

## 相关概念

- [头部按钮系统](/concepts/04-header-buttons.md)
- [交互功能详解](/concepts/06-interactive-features.md)
- [配置系统详解](/concepts/03-configuration.md)
- [基础书籍配置](/examples/basic-book-setup.md)
