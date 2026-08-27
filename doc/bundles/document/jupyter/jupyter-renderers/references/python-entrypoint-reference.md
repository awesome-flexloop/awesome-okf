---
type: Reference
title: Python 入口点与打包参考
description: JupyterLab 预构建扩展的 Python 打包配置，包括 _jupyter_labextension_paths、hatchling 构建系统、hatch-jupyter-builder 配置
tags: [python, packaging, hatchling, jupyter-builder, reference]
sources:
  - id: fasta-pyproject
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/pyproject.toml
    title: fasta-extension/pyproject.toml
  - id: fasta-init
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/jupyterlab_fasta/__init__.py
    title: jupyterlab_fasta/__init__.py
  - id: geojson-init
    resource: external/libs/jupyter/jupyter-renderers/packages/geojson-extension/jupyterlab_geojson/__init__.py
    title: jupyterlab_geojson/__init__.py
  - id: katex-init
    resource: external/libs/jupyter/jupyter-renderers/packages/katex-extension/jupyterlab_katex/__init__.py
    title: jupyterlab_katex/__init__.py
  - id: mathjax2-init
    resource: external/libs/jupyter/jupyter-renderers/packages/mathjax2-extension/jupyterlab_mathjax2/__init__.py
    title: jupyterlab_mathjax2/__init__.py
  - id: vega3-init
    resource: external/libs/jupyter/jupyter-renderers/packages/vega3-extension/jupyterlab_vega3/__init__.py
    title: jupyterlab_vega3/__init__.py
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# Python 入口点与打包参考

JupyterLab 3.0+ 支持预构建扩展（prebuilt extensions），通过 pip/conda 安装，无需 Node.js 编译。本文档说明 jupyter-renderers 各包的 Python 端实现和打包配置。

## Python 包结构

每个扩展的 Python 包结构极简：

```
jupyterlab_<name>/
├── __init__.py          # 入口点（3行代码）
├── _version.py          # 自动生成的版本号
└── labextension/        # 编译后的 JS/CSS 静态资源（构建产物）
    ├── package.json
    ├── static/
    │   ├── style.js
    │   └── ...
    └── install.json
```

## _jupyter_labextension_paths 入口点

JupyterLab 发现扩展的标准入口点。所有5个包的 `__init__.py` 结构完全一致：[^fasta-init] [^geojson-init] [^katex-init] [^mathjax2-init] [^vega3-init]

```python
# jupyterlab_fasta/__init__.py（示例）
from ._version import __version__

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "@jupyterlab/fasta-extension"
    }]
```

**字段说明**：

| 字段 | 说明 |
|------|------|
| `src` | 静态资源在 Python 包内的相对目录名（固定为 `"labextension"`） |
| `dest` | JupyterLab 中安装的目标路径，必须与 npm 包名一致 |

**各包的 dest 值**：

| Python 包 | dest（npm 包名） |
|-----------|-----------------|
| jupyterlab_fasta | `@jupyterlab/fasta-extension` |
| jupyterlab_geojson | `@jupyterlab/geojson-extension` |
| jupyterlab_katex | `@jupyterlab/katex-extension` |
| jupyterlab_mathjax2 | `@jupyterlab/mathjax2-extension` |
| jupyterlab_vega3 | `@jupyterlab/vega3-extension` |

## pyproject.toml 构建配置

以 fasta-extension 为例，所有包使用相同的构建系统。[^fasta-pyproject]

### 构建系统

```toml
[build-system]
requires = ["hatchling>=1.5.0", "jupyterlab>=4.0.0,<5", "hatch-nodejs-version"]
build-backend = "hatchling.build"
```

| 依赖 | 用途 |
|------|------|
| `hatchling` | Python 构建后端（替代 setuptools） |
| `jupyterlab>=4.0.0,<5` | 提供 `jupyter labextension build` 命令 |
| `hatch-nodejs-version` | 从 package.json 读取版本号 |

### 项目元数据

```toml
[project]
name = "jupyterlab_fasta"
readme = "README.md"
license = { file = "LICENSE" }
requires-python = ">=3.8"
classifiers = [
    "Framework :: Jupyter",
    "Framework :: Jupyter :: JupyterLab",
    "Framework :: Jupyter :: JupyterLab :: 4",
    "Framework :: Jupyter :: JupyterLab :: Extensions",
    "Framework :: Jupyter :: JupyterLab :: Extensions :: Prebuilt",
    "License :: OSI Approved :: BSD License",
]
dependencies = []  # 无运行时 Python 依赖
dynamic = ["version", "description", "authors", "urls", "keywords"]
```

**注意**：`dependencies = []` 为空——所有渲染逻辑在 JS 端，Python 包仅提供静态资源入口。

### 版本管理

```toml
[tool.hatch.version]
source = "nodejs"  # 从 package.json 读取版本号

[tool.hatch.metadata.hooks.nodejs]
fields = ["description", "authors", "urls"]
```

版本号从 `package.json` 的 `"version"` 字段自动读取，确保 JS 和 Python 版本一致。

### 构建目标配置

```toml
[tool.hatch.build.targets.sdist]
artifacts = ["jupyterlab_fasta/labextension"]
exclude = [".github", "binder"]

[tool.hatch.build.targets.wheel.shared-data]
"jupyterlab_fasta/labextension" = "share/jupyter/labextensions/@jupyterlab/fasta-extension"
"install.json" = "share/jupyter/labextensions/@jupyterlab/fasta-extension/install.json"
```

**关键路径**：
- 源码中的 `jupyterlab_fasta/labextension/` → 安装到 `share/jupyter/labextensions/@jupyterlab/fasta-extension/`
- `install.json` → 也复制到 labextension 目录
- 这是 JupyterLab 发现预构建扩展的标准路径

### Jupyter Builder Hook

```toml
[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"
ensured-targets = [
    "jupyterlab_fasta/labextension/static/style.js",
    "jupyterlab_fasta/labextension/package.json",
]
skip-if-exists = ["jupyterlab_fasta/labextension/static/style.js"]

[tool.hatch.build.hooks.jupyter-builder.build-kwargs]
build_cmd = "build:prod"
npm = ["jlpm"]

[tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs]
build_cmd = "install:extension"
npm = ["jlpm"]
source_dir = "src"
build_dir = "jupyterlab_fasta/labextension"
```

**构建流程**：
1. 构建时自动调用 `hatch_jupyter_builder.npm_builder`
2. 生产构建：执行 `jlpm build:prod`（clean + tsc + labextension build）
3. 开发安装（pip install -e .）：执行 `jlpm install:extension`（开发模式构建）
4. `ensured-targets`：构建完成后必须存在的文件（验证构建成功）
5. `skip-if-exists`：如果产物已存在则跳过构建（加速 CI）

### 版本 Hook

```toml
[tool.hatch.build.hooks.version]
path = "jupyterlab_fasta/_version.py"
```

自动生成 `_version.py` 文件，包含 `__version__` 变量。

## 安装方式

### pip 安装（用户推荐）

```bash
pip install jupyterlab-fasta
pip install jupyterlab-geojson
pip install jupyterlab-katex
pip install jupyterlab-mathjax2
pip install jupyterlab-vega3
```

JupyterLab 3.0+ 自动发现并加载预构建扩展，无需 `jupyter labextension install` 或 Node.js。

### 开发模式安装

```bash
cd packages/fasta-extension
pip install -e .
jupyter labextension develop . --overwrite
jlpm run watch  # 监听 TS 变化自动重编译
```

开发模式下需要：
1. `pip install -e .`：安装 Python 包为可编辑模式
2. `jupyter labextension develop . --overwrite`：创建符号链接到 JupyterLab
3. `jlpm run watch`：TypeScript 监听模式自动重编译

### Monorepo 批量构建

```bash
# 根目录执行，构建所有包的 Python wheel
jlpm build-py

# 产物输出到 dist/ 目录
# dist/jupyterlab_fasta-*.whl
# dist/jupyterlab_geojson-*.whl
# ...
```

[^fasta-init]: jupyterlab_fasta/__init__.py
[^fasta-pyproject]: fasta-extension/pyproject.toml
[^geojson-init]: jupyterlab_geojson/__init__.py
[^katex-init]: jupyterlab_katex/__init__.py
[^mathjax2-init]: jupyterlab_mathjax2/__init__.py
[^vega3-init]: jupyterlab_vega3/__init__.py
