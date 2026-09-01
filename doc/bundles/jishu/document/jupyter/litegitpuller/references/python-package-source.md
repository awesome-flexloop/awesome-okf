---
type: Reference
title: Python包结构源码信源
description: litegitpuller Python包入口litegitpuller/__init__.py和install.json的源码结构信源登记
tags: [python, jupyterlab-extension, labextension, package-entry]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:55:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T15:55:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-python-package
    resource: /references/python-package-source.md
    title: Python包结构源码信源
---

## 文件位置

- Python包入口：`litegitpuller/__init__.py`
- 扩展安装配置：`install.json`

## litegitpuller/__init__.py

该文件是 Python 包的唯一源码文件，整个 Python 包仅包含：

### 版本导入

```python
try:
    from ._version import __version__
except ImportError:
    import warnings
    warnings.warn("Importing 'litegitpuller' outside a proper installation.")
    __version__ = "dev"
```

- 优先从构建时生成的 `_version.py` 导入版本号
- 开发模式下（未安装或未执行 editable install），版本回退为 `"dev"` 并发出警告

### JupyterLab 扩展路径注册

```python
def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "@jupyterlite/litegitpuller"
    }]
```

- JupyterLab 发现扩展的标准入口函数
- `src`：Python包内 labextension 静态资源目录
- `dest`：JupyterLab 扩展安装目标路径（npm 包名）

## install.json

```json
{
  "packageManager": "python",
  "packageName": "litegitpuller",
  "uninstallInstructions": "Use your Python package manager (pip, conda, etc.) to uninstall the package litegitpuller"
}
```

- 指定包管理器为 Python（pip/conda）
- 提供卸载指引
- 安装时由 JupyterLab 读取此文件
