---
type: Example
title: "仓库按钮与在线启动按钮"
description: "一次配置打通 GitHub 仓库/编辑/issue/源码按钮与 Binder、Colab、JupyterLite、Thebe 启动链路，含环境文件与验收方法"
tags: [sphinx, theme, example, github, binder, colab, thebe, launch-buttons]
generated: { by: "reference_agent/lobsterai-cn", at: "2026-11-24T03:02:35Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-24T03:02:35Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: sbt-source-doc
    resource: https://sphinx-book-theme.readthedocs.io/en/latest/components/source-files.html
    title: Buttons that link to source files
  - id: sbt-launch-doc
    resource: https://sphinx-book-theme.readthedocs.io/en/latest/content/launch.html
    title: Launch buttons for interactivity
---

# 仓库按钮与在线启动按钮

目标：页面右上角出现一组按钮——打开仓库、看源码、建议编辑、开 issue、下载、在 Binder/Colab 中运行。

## 1. 最小仓库配置

```python
html_theme_options = {
    "repository_url": "https://github.com/your-org/your-repo",
    "repository_branch": "main",
    "path_to_docs": "docs",
}
```

URL 解析规则：`repository_url.strip("/").rsplit("/", 2)`。

| 配置 | 解析结果 |
|------|---------|
| `https://github.com/your-org/your-repo` | host=`https://github.com`，org=`your-org`，repo=`your-repo` |
| `https://gitlab.com/group/sub/repo` | host=`https://gitlab.com/group`，org=`sub`，repo=`repo`（注意：最后两段才是 org/repo） |
| `https://git.example.org/team/docs` | 推断失败，需显式 `repository_provider` |

自建服务：

```python
html_theme_options = {
    "repository_provider": "gitlab",
    "repository_url": "https://git.example.org/team/docs",
    "repository_branch": "main",
    "path_to_docs": "docs",
}
```

## 2. 打开四类源码按钮

```python
html_theme_options = {
    "repository_url": "https://github.com/your-org/your-repo",
    "repository_branch": "main",
    "path_to_docs": "docs",

    "use_repository_button": True,   # 打开仓库首页
    "use_source_button": True,       # 查看本页源码
    "use_edit_page_button": True,    # 建议编辑（PR）
    "use_issues_button": True,       # 就本页开 issue
}
```

生成结果：

| 按钮 | GitHub URL 形态 |
|------|----------------|
| Repository | `https://github.com/your-org/your-repo` |
| Show source | `https://github.com/your-org/your-repo/blob/main/docs/<page>.md?plain=1` |
| Suggest edit | `https://github.com/your-org/your-repo/edit/main/docs/<page>.md` |
| Open issue | `https://github.com/your-org/your-repo/issues/new?title=Issue%20on%20page%20%2F<page>.html...` |

多个按钮会自动合并成一个下拉组；只开一个时只显示图标。

> `use_issues_button` 只支持 GitHub / GitLab。Bitbucket 会记录 warning 并且不生成按钮。

## 3. Binder

### 3.1 主题配置

```python
html_theme_options = {
    "repository_url": "https://github.com/your-org/your-repo",
    "repository_branch": "main",
    "path_to_docs": "docs",
    "launch_buttons": {
        "binderhub_url": "https://mybinder.org",
        "notebook_interface": "jupyterlab",
    },
}
```

生成的 URL（GitHub）：

```text
https://mybinder.org/v2/gh/your-org/your-repo/main?urlpath=lab/tree/docs/<page>.ipynb
```

`notebook_interface` 可选：

| 值 | URL 前缀 |
|----|---------|
| `classic` | `tree` |
| `jupyterlab` | `lab/tree` |

其他值会抛 `ValueError`。

### 3.2 仓库环境文件

Binder 需要能安装依赖。仓库根目录放一个 `environment.yml`：

```yaml
name: my-book
channels:
  - conda-forge
dependencies:
  - python=3.12
  - pip
  - pip:
      - sphinx>=8.2
      - sphinx-book-theme
      - myst-nb
      - numpy
      - matplotlib
      - pandas
```

或更轻的 `requirements.txt`：

```text
sphinx>=8.2
sphinx-book-theme
myst-nb
numpy
matplotlib
pandas
```

也可以放在 `binder/` 子目录，Binder 会优先读取。需要额外构建步骤时加 `postBuild`：

```bash
#!/usr/bin/env bash
set -euo pipefail
python -m pip install -e .
```

### 3.3 常见失败

| 现象 | 排查 |
|------|------|
| Binder 构建失败 | 看 Binder 构建日志；多为依赖版本冲突或缺少系统库 |
| 打开后找不到 notebook | `path_to_docs` 与仓库实际路径不一致 |
| 打开的是 `.md` 不是 `.ipynb` | 仓库里没有同名 `.ipynb`，Binder 只能打开文本 |
| 启动很慢 | Binder 首次构建需要几分钟，之后有缓存 |

## 4. Colab

```python
html_theme_options = {
    "launch_buttons": {
        "colab_url": "https://colab.research.google.com",
    },
}
```

限制：

- 仅 GitHub。
- 打开的是仓库里的 notebook 文件。
- 私有仓库需要 Colab 授权。

生成的 URL：

```text
https://colab.research.google.com/github/your-org/your-repo/blob/main/docs/<page>.ipynb
```

## 5. JupyterLite

JupyterLite 在浏览器里运行，不需要后端。先把 JupyterLite 站点构建到文档站的子目录，例如 `docs/_static/lite/`，然后：

```python
html_theme_options = {
    "launch_buttons": {
        "jupyterlite_url": "_static/lite/lab/index.html",
    },
}
```

生成：

```text
_static/lite/lab/index.html?path=docs/<page>.ipynb
```

`jupyterlite_url` 只去掉尾部斜杠，保留前导相对路径，因此可以放在子目录。

## 6. Thebe

```bash
pip install sphinx-thebe
```

```python
extensions = [
    "myst_nb",
    "sphinx_thebe",
]

html_theme_options = {
    "repository_url": "https://github.com/your-org/your-repo",
    "repository_branch": "main",
    "launch_buttons": {
        "thebe": True,
        "notebook_interface": "jupyterlab",
    },
}
```

页面里第一个可执行单元格加 `thebe-init`：

````md
```{code-cell} python
:tags: [thebe-init]

import numpy as np
```
````

点击"Live Code"后，Thebe 会向 Binder 申请内核，然后把页面上的代码单元格变成可运行状态。

## 7. 一次性配置模板

```python
html_theme_options = {
    "repository_url": "https://github.com/your-org/your-repo",
    "repository_branch": "main",
    "path_to_docs": "docs",

    "use_repository_button": True,
    "use_source_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
    "use_download_button": True,
    "use_fullscreen_button": True,

    "launch_buttons": {
        "binderhub_url": "https://mybinder.org",
        "colab_url": "https://colab.research.google.com",
        "jupyterlite_url": "_static/lite/lab/index.html",
        "thebe": True,
        "notebook_interface": "jupyterlab",
    },
}
```

## 8. 验收方法

| 检查 | 方法 |
|------|------|
| 按钮存在 | 构建后打开任意页面，右上角应有对应图标 |
| URL 正确 | 右键复制链接，检查 org/repo/branch/path 四段 |
| Binder 可用 | 点击后能进入 JupyterLab，且 notebook 能打开 |
| Colab 可用 | 点击后 Colab 能加载仓库文件 |
| Thebe 可用 | 点击 Live Code 后单元格出现运行按钮，执行有输出 |
| 移动端 | 按钮收进侧栏或保持常驻，不遮挡正文 |

## 9. 安全提醒

- Binder/Colab/Thebe 都会把仓库内容暴露给点击者。**不要**在公开仓库放密钥、私有数据、未脱敏日志。
- `path_to_docs` 只是 URL 拼接，不是访问控制。
- 私有仓库的 Binder 需要额外授权配置，默认不可用。

## 相关概念

- [页眉按钮机制](../concepts/05-header-buttons.md)
- [Notebook 与在线交互](../concepts/07-jupyter-interactivity.md)
- [Notebook 内容流水线](04-notebook-content-pipeline.md)
