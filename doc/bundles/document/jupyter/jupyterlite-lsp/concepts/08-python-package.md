---
type: Concept
title: Python 包与 Labextension 注册
description: jupyterlite-lsp Python 包的极简结构、JS 资源路径查找机制与 JupyterLab 扩展发现
tags: [python, packaging, labextension, flit, path-resolution]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: python
    resource: /references/python-source.md
    title: Python包源码引用
  - id: build
    resource: /references/build-source.md
    title: 构建系统源码引用
---

## Python 包的角色

jupyterlite-lsp 的 Python 包**不包含任何 LSP 服务端逻辑**。它的唯一职责是作为 JupyterLab/Labextension 的分发容器——将 JS 构建产物打包为 Python wheel，通过 pip/conda 安装后，JupyterLab 能自动发现并加载前端扩展。

这与传统 jupyter-lsp Python 包不同：后者包含真正的后端服务（管理语言服务器子进程、WebSocket 代理等），而 jupyterlite-lsp 的 Python 包完全是"壳"。

## 包结构

```
src/jupyterlite_lsp/
├── __init__.py       # 包入口，导出 _jupyter_labextension_paths()
├── constants.py      # 常量（版本、JS命名空间、扩展名列表）
├── js.py             # JS 资源路径解析
└── _d/               # JS 构建产物（external-data，不纳入版本控制）
    └── share/jupyter/labextensions/@jupyterlite/
        ├── lsp/      # @jupyterlite/lsp labextension 产物
        └── lsp-yaml/ # @jupyterlite/lsp-yaml labextension 产物
```

Python 源码仅约 50 行（3个文件）。

## constants.py：常量定义

```python
from importlib.metadata import version

NAME = "jupyterlite-lsp"
__version__ = version(NAME)        # 从安装元数据动态获取版本
JS_NAMESPACE = "@jupyterlite"      # JupyterLab 扩展命名空间
EXTENSION_NAMES = ["lsp", "lsp-yaml"]  # 两个 JS 扩展包名
```

版本号通过 `importlib.metadata.version()` 动态获取，支持 Python 3.7+（3.7 使用 importlib_metadata backport）。

## js.py：路径解析

```python
HERE = Path(__file__).parent
IN_TREE = (HERE / f"_d/share/jupyter/labextensions/{JS_NAMESPACE}").resolve()
IN_PREFIX = Path(sys.prefix) / f"share/jupyter/labextensions/{JS_NAMESPACE}"
__prefix__ = IN_TREE if IN_TREE.exists() else IN_PREFIX
```

双路径策略支持两种安装模式：

| 模式 | 路径 | 条件 |
|------|------|------|
| **开发模式**（IN_TREE） | `src/jupyterlite_lsp/_d/share/jupyter/labextensions/@jupyterlite/` | 源码树中 `_d/` 目录存在时 |
| **安装模式**（IN_PREFIX） | `<sys.prefix>/share/jupyter/labextensions/@jupyterlite/` | pip 安装后，资源位于 Python 环境的 share 目录 |

优先使用 IN_TREE，这样在开发时（`pip install -e .`）不需要每次安装都复制文件。

## __init__.py：扩展入口

```python
from .constants import EXTENSION_NAMES, JS_NAMESPACE, __version__

def _jupyter_labextension_paths():
    from .js import __prefix__
    return [
        dict(src=str(__prefix__ / ext), dest=f"{JS_NAMESPACE}/{ext}")
        for ext in EXTENSION_NAMES
    ]
```

`_jupyter_labextension_paths()` 是 JupyterLab 扩展发现的标准入口点。JupyterLab 启动时会扫描所有已安装的 Python 包，查找这个函数并调用它，获取 labextension 路径列表。

返回值是一个字典列表，每个字典包含：

| 字段 | 值 | 含义 |
|------|-----|------|
| src | `__prefix__/lsp` 等 | JS 静态资源所在目录的绝对路径 |
| dest | `@jupyterlite/lsp` 等 | JupyterLab 中挂载的目标路径（URL 前缀） |

EXTENSION_NAMES 中列出的两个扩展名 `lsp` 和 `lsp-yaml` 分别对应两个 JS 包构建的 labextension。

## flit 打包配置

```toml
[tool.flit.sdist]
include = ["src/jupyterlite_lsp/_d"]

[tool.flit.external-data]
directory = "src/jupyterlite_lsp/_d"
```

- **external-data**：`_d/` 目录标记为外部数据，flit 会将其包含在 wheel 中
- **sdist.include**：源码分发包也包含 `_d/` 目录

`_d/` 目录中的文件是 JS 构建产物（由 `jupyter labextension build` 生成），它们不纳入 git 版本控制，但必须包含在分发包中。

## Python 依赖

```toml
dependencies = [
    "jupyterlab-lsp >=3.10.2",
    "jupyterlite >=0.1.0b15"
]
requires-python = ">=3.7"
```

| 依赖 | 版本 | 作用 |
|------|------|------|
| jupyterlab-lsp | >=3.10.2 | 提供前端 LSP 功能（LSP 编辑器集成、诊断显示等） |
| jupyterlite | >=0.1.0b15 | JupyterLite 核心（Service Worker、虚拟文件系统等） |

注意：虽然 jupyterlab-lsp 包含 Python 服务端组件，但在 JupyterLite 环境中这些服务端组件不会运行——它们被 jupyterlite-lsp 的浏览器端 Mock 实现替代。

## 为什么不把 JS 代码放在 Python 包源码中

jupyterlite-lsp 采用 JS/Python 分离的结构是因为：

1. **构建工具链独立**：JS 使用 yarn/lerna/webpack/tsc，Python 使用 flit，两者构建流程独立
2. **npm 分发**：JS 包也可以独立发布到 npm，供直接使用 JS 的场景
3. **源码树清晰**：`packages/` 放 TS 源码，`src/jupyterlite_lsp/` 放 Python 源码，`_d/` 是纯构建产物
4. **Jupyter 生态惯例**：JupyterLab 扩展通常采用这种"JS 源码 + Python 打包壳"的双语言结构

## 版本兼容性

| jupyterlite-lsp | Python | JupyterLab | jupyterlab-lsp | JupyterLite | Node.js |
|-----------------|--------|------------|----------------|-------------|---------|
| 0.1.0a0 | >=3.7 | >=3.5,<4.0 | >=3.10.2 | >=0.1.0b15 | >=18,<19 |

## 相关概念

- [构建系统详解](07-build-system.md)
- [快速开始](01-getting-started.md)
- [三插件体系](03-plugin-system.md)
- [Python包源码引用](../references/python-source.md)
