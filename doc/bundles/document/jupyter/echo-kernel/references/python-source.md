---
type: Reference
title: Echo Kernel Python包与构建配置源码信源
description: jupyterlite_echo_kernel Python包、pyproject.toml构建配置、install.json安装配置的源码API登记
tags: [python, packaging, hatchling, jupyterlab-extension, build]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:04:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: init-py
    resource: /references/python-source.md
    title: jupyterlite_echo_kernel/__init__.py
  - id: pyproject
    resource: /references/python-source.md
    title: pyproject.toml
  - id: install-json
    resource: /references/python-source.md
    title: install.json
---

## 源码位置

- `jupyterlite_echo_kernel/__init__.py` — Python包入口，约16行
- `pyproject.toml` — Python构建配置，约77行
- `install.json` — JupyterLab扩展安装配置，约5行
- `setup.py` — 兼容 shim，仅1行（调用setuptools.setup()）

## Python包 API（__init__.py）

### \_version 导入（L1-L9）

```python
try:
    from ._version import __version__
except ImportError:
    import warnings
    warnings.warn("Importing 'jupyterlite_echo_kernel' outside a proper installation.")
    __version__ = "dev"
```

- 优先从 `_version.py`（构建时自动生成）导入版本号
- 开发模式（未pip install）下回退到 `"dev"` 并发出警告

### \_jupyter_labextension_paths()（L12-L16）

```python
def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "@jupyterlite/echo-kernel"
    }]
```

JupyterLab扩展发现函数，返回扩展路径映射：
- `src`: Python包内的静态资源目录（`labextension/`，构建产物）
- `dest`: JupyterLab扩展安装目标路径（`@jupyterlite/echo-kernel`）

## pyproject.toml 构建配置

### 构建系统（L1-L3）

| 字段 | 值 |
|------|-----|
| `requires` | `["hatchling>=1.5.0", "jupyterlab>=4.0.0,<5", "hatch-nodejs-version>=0.3.2"]` |
| `build-backend` | `"hatchling.build"` |

### 项目元数据（L5-L27）

| 字段 | 值 |
|------|-----|
| `name` | `"jupyterlite_echo_kernel"` |
| `requires-python` | `">=3.9"` |
| `license` | `{ file = "LICENSE" }` (BSD-3-Clause) |
| `dependencies` | `[]`（无运行时依赖） |
| `dynamic` | `["version", "description", "authors", "urls", "keywords"]` |

版本号从package.json同步（hatch-nodejs-version插件）。

### 构建目标配置

#### sdist（L35-L37）
- artifacts: `["jupyterlite_echo_kernel/labextension"]`
- exclude: `[".github", "binder"]`

#### wheel shared-data（L39-L41）
将labextension静态文件安装到JupyterLab的shared目录：
- `jupyterlite_echo_kernel/labextension` → `share/jupyter/labextensions/@jupyterlite/echo-kernel`
- `install.json` → `share/jupyter/labextensions/@jupyterlite/echo-kernel/install.json`

### Jupyter Builder Hook（L46-L63）

使用 `hatch-jupyter-builder` 在构建时自动编译前端：

| 配置项 | 值 |
|--------|-----|
| `build-function` | `"hatch_jupyter_builder.npm_builder"` |
| `build_cmd`（生产） | `"build:prod"` |
| `build_cmd`（开发） | `"install:extension"` |
| `npm` | `["jlpm"]` |
| `ensured-targets` | `["labextension/static/style.js", "labextension/package.json"]` |

工作原理：pip install时自动调用 `jlpm build:prod`，将TypeScript编译为JS并打包labextension。

## install.json（L1-L5）

```json
{
  "packageManager": "python",
  "packageName": "jupyterlite_echo_kernel",
  "uninstallInstructions": "Use your Python package manager (pip, conda, etc.) to uninstall the package jupyterlite_echo_kernel"
}
```

JupyterLab扩展安装元数据，标识包管理器类型和包名。

## 前端构建脚本（package.json scripts，供hatch-jupyter-builder调用）

| 脚本 | 命令 | 用途 |
|------|------|------|
| `build:prod` | `jlpm clean && jlpm build:lib:prod && jlpm build:labextension` | 生产构建：清理→编译TS→构建labextension |
| `build:lib:prod` | `tsc` | TypeScript编译（无sourceMap） |
| `build:labextension` | `jupyter labextension build .` | JupyterLab扩展打包 |
| `install:extension` | `jlpm build` | 开发模式构建 |

## 构建流程（pip install 时）

```
pip install jupyterlite-echo-kernel
  → hatchling 启动构建
    → hatch-jupyter-builder 触发
      → 执行 jlpm install（安装npm依赖）
      → 执行 jlpm build:prod
        → tsc 编译 src/*.ts → lib/*.js
        → jupyter labextension build . 打包labextension
          → 产物输出到 jupyterlite_echo_kernel/labextension/
    → wheel打包
      → labextension/ → share/jupyter/labextensions/@jupyterlite/echo-kernel/
      → install.json → share/jupyter/labextensions/@jupyterlite/echo-kernel/
```
