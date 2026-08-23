---
okf_version: "0.2"
type: reference
title: NumPy 核心初始化（_core/__init__.py）
description: NumPy _core 模块的初始化流程——C扩展加载、OPENBLAS线程亲和性设置、multiarray/umath合并导入
sources:
  - id: numpy-core
    resource: external/libs/python/NumPy/numpy/numpy/_core/__init__.py
    title: NumPy _core 初始化源码
---

# NumPy 核心初始化（_core/__init__.py）

NumPy 的核心功能（ndarray、ufunc、dtype 等）由 C 扩展模块 `_multiarray_umath` 提供。`numpy._core` 是一个私有模块，所有公开 API 都通过 `numpy` 命名空间暴露。

## 初始化流程

```python
# numpy/_core/__init__.py 关键流程
import os
from numpy.version import version as __version__

# 1. 设置 OPENBLAS_MAIN_FREE=1 防止OpenBLAS将线程绑定到单核
env_added = []
for envkey in ['OPENBLAS_MAIN_FREE']:
    if envkey not in os.environ:
        os.putenv(envkey, '1')
        env_added.append(envkey)

# 2. 导入C扩展 multiarray（封装 _multiarray_umath）
try:
    from . import multiarray
except ImportError as exc:
    # 详细的C扩展导入失败诊断信息
    # 检查 _multiarray_umath 模块文件是否存在
    # 输出 Python版本/NumPy版本/平台信息

# 3. 导入 umath 模块
from . import umath

# 4. 验证 multiarray 和 umath 都是纯Python封装模块（非旧C扩展）
if not (hasattr(multiarray, '_multiarray_umath') and
        hasattr(umath, '_multiarray_umath')):
    raise ImportError(...)

# 5. 清理环境变量
for envkey in env_added:
    os.unsetenv(envkey)
```

**关键设计要点**：

1. **OPENBLAS线程亲和性修复**：设置 `OPENBLAS_MAIN_FREE=1` 防止 OpenBLAS 将主线程绑定到单核，导致多线程/多进程只能用一个CPU核心。使用 `os.putenv()` 而非 `os.environ[]` 是为了避免竞态条件（gh-30627）。

2. **C扩展合并**：NumPy v1.16 将 `multiarray` 和 `umath` 两个 C 扩展模块合并为单一的 `_multiarray_umath`，`multiarray.py` 和 `umath.py` 成为纯 Python 封装层，向后兼容导入。

3. **导入失败诊断**：当 C 扩展导入失败时，NumPy 会检查是否存在编译好的模块文件，并输出包含 Python 版本、NumPy 版本、平台、编译模块列表的详细诊断信息，帮助用户排查安装问题。
