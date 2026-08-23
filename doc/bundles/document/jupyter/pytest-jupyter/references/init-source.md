---
okf_version: "0.2"
type: reference
title: "入口与版本源码（__init__.py, _version.py）"
description: "pytest_jupyter/__init__.py 和 _version.py 的导出结构与版本定义"
tags: [init, version, entry-point, exports, all]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: init-py
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/pytest_jupyter/__init__.py"
    title: "pytest_jupyter/__init__.py"
  - id: version-py
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/pytest_jupyter/_version.py"
    title: "pytest_jupyter/_version.py"
  - id: pyproject-toml
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/pyproject.toml"
    title: "pyproject.toml"
---

# 入口与版本源码（\_\_init\_\_.py, \_version.py）

本信源登记 `pytest_jupyter/__init__.py`（约7行）和 `pytest_jupyter/_version.py`（约5行）的内容。这两个文件构成包的入口点和版本定义。

## \_version.py

```python
"""Version info for pytest_jupyter."""
__version__ = "0.12.0.dev0"
```

- 定义 `__version__` 字符串，当前版本为 `0.12.0.dev0`（开发版）
- 被 `pyproject.toml` 中的 `[tool.hatch.version]` 引用：`path = "pytest_jupyter/_version.py"`

[F-002]

## \_\_init\_\_.py

```python
__all__ = ["__version__"]

from ._version import __version__
from .jupyter_core import *  # noqa: F403
```

**行为：**
1. `__all__` 显式声明仅导出 `__version__`
2. 从 `_version` 导入 `__version__`
3. 通过 `from .jupyter_core import *` 导入core插件的所有公开内容（fixtures、hooks等）
4. `# noqa: F403` 抑制flake8/rf对`import *`的警告

[F-003]

## pyproject.toml关键元数据

| 字段 | 值 |
|------|-----|
| name | `pytest-jupyter` |
| version | 动态（从`_version.py`读取） |
| description | `"A pytest plugin for testing Jupyter libraries and extensions."` |
| license | BSD-3-Clause |
| requires-python | `>=3.10` |
| build-system | hatchling >= 1.10.0 |
| 核心依赖 | `pytest>=7.0`, `jupyter_core>=5.7` |

**可选依赖组（extras）：**

| extra | 依赖 |
|-------|------|
| `client` | `jupyter_client>=7.4.0`, `nbformat>=5.3`, `ipykernel>=6.14` |
| `server` | `jupyter_server>=1.21` + client组全部依赖 |
| `docs` | `myst_parser`, `pydata_sphinx_theme`, `Sphinx`, `sphinxcontrib-spelling` |
| `test` | `pytest-timeout` |

[F-004]

## 插件入口点说明

pytest插件通过模块导入发现，而非entry points。使用方式是在`conftest.py`中设置：

```python
pytest_plugins = [
    "pytest_jupyter",                    # 仅core插件
    "pytest_jupyter.jupyter_client",     # core + client
    "pytest_jupyter.jupyter_server",     # core + client + server + tornasync
]
```

- `import pytest_jupyter` 等价于导入 `pytest_jupyter.jupyter_core`（因为`__init__.py`做了`from .jupyter_core import *`）
- `pytest_jupyter.jupyter_client` 模块自身也做了 `from pytest_jupyter.jupyter_core import *`
- `pytest_jupyter.jupyter_server` 模块做了 `from pytest_jupyter.jupyter_core import *` 和 `from pytest_jupyter.pytest_tornasync import *`，同时通过jupyter_client的传递导入获得client fixtures

[F-005]
