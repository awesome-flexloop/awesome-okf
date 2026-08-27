---
type: Reference
title: Python包源码引用
description: jupyterlite-lsp Python 包的 __init__.py、constants.py、js.py 源码引用
tags: [source, python, labextension, packaging]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: py-init
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/src/jupyterlite_lsp/__init__.py
    title: src/jupyterlite_lsp/__init__.py
  - id: py-constants
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/src/jupyterlite_lsp/constants.py
    title: src/jupyterlite_lsp/constants.py
  - id: py-js
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/src/jupyterlite_lsp/js.py
    title: src/jupyterlite_lsp/js.py
  - id: pyproject
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/pyproject.toml
    title: pyproject.toml
---

## Python 包文件清单

`jupyterlite-lsp` Python 包位于 `src/jupyterlite_lsp/`，共3个源文件：

| 文件 | 行数 | 职责 |
|------|------|------|
| `__init__.py` | ~14行 | 包入口，导出 `__version__` 和 `_jupyter_labextension_paths()` |
| `constants.py` | ~20行 | 常量定义（包名、版本、JS命名空间、扩展名列表） |
| `js.py` | ~15行 | JS 静态资源路径解析 |

## __init__.py

```python
"""LSP for JupyterLite."""

from .constants import EXTENSION_NAMES, JS_NAMESPACE, __version__

__all__ = ["__version__", "_jupyter_labextension_paths"]


def _jupyter_labextension_paths():
    from .js import __prefix__

    return [
        dict(src=str(__prefix__ / ext), dest=f"{JS_NAMESPACE}/{ext}")
        for ext in EXTENSION_NAMES
    ]
```

`_jupyter_labextension_paths()` 是 JupyterLab 扩展发现机制的标准入口点，返回 labextension 路径列表。

## constants.py

```python
try:
    from importlib.metadata import version
except:
    from importlib_metadata import version

NAME = "jupyterlite-lsp"
__version__ = version(NAME)
JS_NAMESPACE = "@jupyterlite"
EXTENSION_NAMES = ["lsp", "lsp-yaml"]
__all__ = ["__version__", "JS_NAMESPACE", "EXTENSION_NAMES"]
```

EXTENSION_NAMES 列出两个 JS 扩展包名，对应 `packages/lsp/` 和 `packages/lsp-yaml/`。

## js.py

```python
import sys
from pathlib import Path
from .constants import JS_NAMESPACE

HERE = Path(__file__).parent
IN_TREE = (HERE / f"_d/share/jupyter/labextensions/{JS_NAMESPACE}").resolve()
IN_PREFIX = Path(sys.prefix) / f"share/jupyter/labextensions/{JS_NAMESPACE}"
__prefix__ = IN_TREE if IN_TREE.exists() else IN_PREFIX
```

路径查找逻辑：
1. **开发模式（IN_TREE）**：源码树中 `_d/share/jupyter/labextensions/@jupyterlite/` 目录存在时使用
2. **安装模式（IN_PREFIX）**：安装到 sys.prefix 下的 `share/jupyter/labextensions/@jupyterlite/`

JS 构建产物在 `src/jupyterlite_lsp/_d/` 目录下，由 flit 作为 external-data 打包进 wheel。

## pyproject.toml 关键配置

```toml
[build-system]
requires = ["flit_core >=3.7.1,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "jupyterlite-lsp"
version = "0.1.0a0"
requires-python = ">=3.7"
dependencies = [
    "jupyterlab-lsp >=3.10.2",
    "jupyterlite >=0.1.0b15"
]

[tool.flit.sdist]
include = ["src/jupyterlite_lsp/_d"]

[tool.flit.module]
name = "jupyterlite_lsp"

[tool.flit.external-data]
directory = "src/jupyterlite_lsp/_d"
```

## 相关概念

- [Python包与Labextension注册](../concepts/08-python-package.md)
- [构建系统](../concepts/07-build-system.md)
- [核心包源码引用](core-plugin-source.md)
