---
type: Concept
title: bootstrap() 加载机制
description: "doltlite-python bootstrap() 的幂等性设计、环境标记机制、调用时序要求；__init__.py 自动调用 bootstrap() 的行为；F-008~F-013。"
tags: [doltlite-python, bootstrap, idempotent, loader]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-10" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10" }
status: stable
stale_after: "2027-03-31"
sources:
  - id: doltlite-python-local
    resource: "本地克隆（tag v0.50.7，commit ba3b46fa6f58e42aef4b929d97a28248832079cb）"
    title: doltlite-python 源码逐文件精读
---

# bootstrap() 加载机制

> **对应 F 编号**：F-008 ~ F-013

## 自动 bootstrap 行为

`doltlite` 包采用**副作用导入**模式——`__init__.py` 在模块加载时自动调用 `bootstrap()`，无需用户显式调用：

```python
# __init__.py（23行）
from ._loader import bootstrap, libdoltlite_path
bootstrap()          # ← 自动执行，后续 sqlite3 即被劫持
__all__ = ["bootstrap", "libdoltlite_path"]
__version__ = "0.50.7"
```

因此正确用法是：

```python
import doltlite      # 触发 bootstrap，libdoltlite 注入 sqlite3 符号链
import sqlite3      # 此时 sqlite3 已使用 libdoltlite 的 C API
```

**关键约束**：`import doltlite` 必须在 `import sqlite3` 之前执行。若 sqlite3 已导入，bootstrap 无法在进程内完成劫持，会尝试 re-exec 重新启动解释器。

## 幂等性设计

`bootstrap()` 通过**进程级环境变量**实现幂等，确保多次导入和 re-exec 后不会无限循环：

```python
_BOOTSTRAP_MARKER = "_DOLTLITE_BOOTSTRAPPED"   # F-010

def _is_bootstrapped() -> bool:
    return os.environ.get(_BOOTSTRAP_MARKER) == "1"   # F-011

def bootstrap() -> None:
    if _is_bootstrapped():
        return   # F-013: 幂等返回，后续调用是 no-op
    # ... 实际加载逻辑
```

执行流程：

```
第一次 import doltlite
    └── bootstrap() 调用
        ├── _is_bootstrapped() → False
        ├── 执行平台加载策略
        │   ├── Linux（sqlite3 未导入）→ ctypes.CDLL(RTLD_GLOBAL) + 设置 _DOLTLITE_BOOTSTRAPPED=1
        │   └── 其他情况 → re-exec（env 中带 _DOLTLITE_BOOTSTRAPPED=1）
        └── 新进程中：import doltlite → bootstrap() → _is_bootstrapped() → True → 返回
```

## 库路径解析

`libdoltlite_path()` 提供两级路径解析，支持开发调试场景（F-009）：

```python
def libdoltlite_path() -> str:
    # 优先级 1：DOLTLITE_LIB 环境变量（开发时指向本地编译的 .so/.dylib）
    env = os.environ.get("DOLTLITE_LIB")
    if env:
        if not os.path.exists(env):
            raise DoltliteLoadError(f"DOLTLITE_LIB points to a missing file: {env}")
        return env
    
    # 优先级 2：包内 bundled 库
    name = "libdoltlite.dylib" if sys.platform == "darwin" else "libdoltlite.so"
    bundled = _PKG_LIB_DIR / name
    if bundled.is_file():
        return str(bundled)
    
    raise DoltliteLoadError("libdoltlite not found. ...")
```

开发时可设置 `DOLTLITE_LIB=/path/to/local/libdoltlite.so` 指向本地编译版本，无需重新安装 wheel。

## 异常类

`DoltliteLoadError` 继承自 `RuntimeError`（F-008），在以下情况抛出：

| 触发条件 | 说明 |
|---------|------|
| libdoltlite 库不存在 | bundled 目录无 .so/.dylib，且 DOLTLITE_LIB 未设置 |
| sqlite3 已导入且无法 re-exec | argv[0] 不是可重放脚本路径（REPL/Jupyter） |
| macOS otool/install_name_tool 缺失 | Xcode Command Line Tools 未安装 |

## 学习路径

* [跨平台符号劫持策略](02-platform-strategies.md) — Linux vs macOS 的具体实现差异
* [wheel tag 与构建系统](03-wheel-and-build.md) — py3-none tag 与 lockstep 版本管理
