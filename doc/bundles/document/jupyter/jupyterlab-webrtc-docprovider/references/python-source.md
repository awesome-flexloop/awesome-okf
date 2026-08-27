---
type: Reference
title: Python包与构建配置源码
description: Python包初始化、版本管理、构建系统配置（pyproject.toml + setup.py + jupyter_packaging）
tags: [python, packaging, build, jupyter-packaging, labextension, pip]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T07:06:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T07:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: py-init
    resource: https://github.com/jupyterlite/jupyterlab-webrtc-docprovider/blob/main/jupyterlab_webrtc_docprovider/__init__.py
    title: jupyterlab_webrtc_docprovider/__init__.py
  - id: pyproject
    resource: https://github.com/jupyterlite/jupyterlab-webrtc-docprovider/blob/main/pyproject.toml
    title: pyproject.toml
---

## Python包结构分析

### __init__.py

```python
from ._version import __version__, __js__

def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": __js__["name"]}]
```

- 导入版本号和 JS 包元数据
- 实现 `_jupyter_labextension_paths()` 钩子函数，JupyterLab 自动发现 labextension 路径
- `dest` 使用 npm 包名 `@jupyterlite/webrtc-docprovider`

### _version.py

```python
import json
from pathlib import Path

__all__ = ["__js__", "__version__"]
__js__ = json.loads(
    (Path(__file__).parent / "labextension/package.json").read_text(encoding="utf-8")
)
__version__ = (
    __js__["version"]
    .replace("-alpha.", "a")
    .replace("-beta.", "b")
    .replace("-rc.", "rc")
)
```

- 从构建产物 `labextension/package.json` 读取版本信息
- 将 npm 预发布标签转换为 PEP 440 格式：`-alpha.` → `a`，`-beta.` → `b`，`-rc.` → `rc`

### pyproject.toml 构建系统

```toml
[build-system]
requires = ["jupyter_packaging>=0.10,<1", "jupyterlab>=3.1,<4"]
build-backend = "jupyter_packaging.build_api"

[tool.jupyter-packaging.options]
skip-if-exists = ["jupyterlab_webrtc_docprovider/labextension/static/style.js"]
ensured-targets = [
    "jupyterlab_webrtc_docprovider/labextension/package.json",
    "jupyterlab_webrtc_docprovider/labextension/static/style.js",
]

[tool.jupyter-packaging.builder]
factory = "jupyter_packaging.npm_builder"

[tool.jupyter-packaging.build-args]
build_cmd = "build:prod"
npm = ["jlpm"]
```

- 使用 `jupyter_packaging` 作为构建后端
- 构建时调用 `jlpm build:prod`（即 `yarn build:prod`）编译前端资源
- `npm_builder` 工厂处理 npm/yarn 构建流程

### setup.py（兼容入口）

- 从 `package.json` 读取包名、版本、作者等元数据
- 使用 `setuptools.find_packages()` 自动发现 Python 包
- `install_requires` 为空（纯前端扩展，无 Python 运行时依赖）
- `python_requires=">=3.7"`
- 数据文件安装到 `share/jupyter/labextensions/@jupyterlite/webrtc-docprovider/`
- 通过 `jupyter_packaging.wrap_installers` 和 `npm_builder` 集成前端构建

### install.json

```json
{
  "packageManager": "python",
  "packageName": "jupyterlab-webrtc-docprovider",
  "uninstallInstructions": "Use your Python package manager (pip, conda, etc.) to uninstall..."
}
```

JupyterLab 扩展管理器使用的元数据文件。

## 相关概念

- [构建与打包系统](../concepts/10-build-and-packaging.md)
- [安装与快速开始](../concepts/01-getting-started.md)
