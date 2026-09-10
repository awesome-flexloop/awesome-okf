---
type: Reference
title: doltlite-python 源码事实登记
description: "doltlite-python 源码信源登记——仓库元信息、_loader.py 核心加载机制、bootstrap() 平台策略、re-exec 约束、smoke 测试，F-001~F-022 编号事实零推测登记"
tags: [doltlite-python, doltlite, sqlite3, python, source-code, facts, dolthub]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-10" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10" }
status: stable
stale_after: "2027-03-31"
sources:
  - id: doltlite-python-repo
    resource: https://github.com/dolthub/doltlite-python
    title: "dolthub/doltlite-python（官方仓库）"
  - id: doltlite-python-local
    resource: "本地克隆（tag v0.50.7，commit ba3b46fa6f58e42aef4b929d97a28248832079cb）"
    title: "doltlite-python 源码逐文件精读"
---

# doltlite-python 源码事实登记

> 本文件是知识包全部正文的事实底账，编号 **F-001 ~ F-022**。所有正文中的数字、类型名、方法名、参数均可在下表找到逐字出处。

## 一、仓库元信息与包结构

| 编号 | 事实 | 出处 |
|---|---|---|
| F-001 | 仓库 `https://github.com/dolthub/doltlite-python`，描述："Python loader for doltlite — Dolt version control through SQLite's drop-in API" | README.md L1-L4 |
| F-002 | 包名 `doltlite`，版本 `0.50.7`，requires-python `>=3.9`，license `Apache-2.0` | pyproject.toml L6-L28 |
| F-003 | 源码目录：`src/doltlite/__init__.py`（入口，23行）、`src/doltlite/_loader.py`（核心 loader，206行）、`src/doltlite/_lib/`（存放 libdoltlite.dylib/so，仅 `.gitkeep`） | Glob 结果 |
| F-004 | 构建后端：`setuptools.build_meta`，非 scikit-build-core（注释：纯 Python 文件+二进制 bundle 的混合包） | pyproject.toml L1-L3 |
| F-005 | wheel tag 策略：通过自定义 `PlatformWheel.get_tag()` 返回 `("py3", "none", plat)`，使 wheel 标记为 `py3-none-<platform>`（非 `py3-none-any`，非 `cp312-cp312-...`） | setup.py L17-L25 |
| F-006 | cibuildwheel 配置：build `cp39-*` 至 `cp313-*`，skip `*-musllinux_* *-win_* *-manylinux_i686`；只构建 macOS arm64/x86_64 和 Linux x86_64/aarch64；Intel Mac（macos-13）故意跳过 | pyproject.toml L52-L61、wheels.yml L29-L40 |
| F-007 | 上游 doltlite 库固定版本：`DOLTLITE_REF="${DOLTLITE_REF:-v0.50.7}"`，与包版本同步递增；脚本通过 `scripts/build-libdoltlite.sh` 在 before-build 阶段从源码编译 libdoltlite | pyproject.toml L8-L9、build-libdoltlite.sh L18 |

## 二、_loader.py 核心加载机制

| 编号 | 事实 | 出处 |
|---|---|---|
| F-008 | 类 `DoltliteLoadError(RuntimeError)`：加载失败时抛出的异常类 | _loader.py L41-L42 |
| F-009 | 函数 `libdoltlite_path() -> str`：解析 libdoltlite 路径，优先级：① `DOLTLITE_LIB` 环境变量（绝对路径）② 包内 bundled `<pkg>/_lib/libdoltlite.{dylib,so}` | _loader.py L45-L74 |
| F-010 | 常量 `_BOOTSTRAP_MARKER = "_DOLTLITE_BOOTSTRAPPED"`：用于判断当前进程是否已完成 bootstrap 的环境变量标记 | _loader.py L37 |
| F-011 | 函数 `_is_bootstrapped() -> bool`：检查 `_DOLTLITE_BOOTSTRAPPED` 环境变量是否为 `"1"` | _loader.py L77-L78 |
| F-012 | 函数 `_sqlite3_already_imported() -> bool`：检查 `"sqlite3"` 或 `"_sqlite3"` 是否在 `sys.modules` 中 | _loader.py L81-L82 |

## 三、bootstrap() 平台策略

| 编号 | 事实 | 出处 |
|---|---|---|
| F-013 | `bootstrap() -> None` 函数逻辑分支：① 若已 bootstrap → 直接返回（幂等）② Linux + sqlite3 未导入 → `ctypes.CDLL(lib, mode=ctypes.RTLD_GLOBAL)` + 设置环境标记 ③ 其他情况 → `_require_replayable_argv()` 后 re-exec | _loader.py L85-L114 |
| F-014 | Linux 策略：ELF flat-namespace symbol resolution；`ctypes.CDLL(lib, mode=ctypes.RTLD_GLOBAL)` 使 libdoltlite 的 `sqlite3_*` 符号进入全局命名空间；若 sqlite3 已导入 → fallback 到 `os.execvpe(sys.executable, [sys.executable, *sys.argv], env)`，在 env 中设置 `LD_PRELOAD=<lib>` | _loader.py L98-L113、README.md L76-L86 |
| F-015 | macOS 策略：two-level namespace；`_sqlite3.so` 通过 `LC_LOAD_DYLIB` 绑定到特定 `libsqlite3.dylib` 路径；plain `ctypes.CDLL` 无法重定向该查找；必须构建 shim（copy libdoltlite 到 `$TMPDIR/.../libsqlite3.dylib`，用 `install_name_tool -id <path>` 改写 install_name），然后 re-exec 设置 `DYLD_INSERT_LIBRARIES=<shim>` | _loader.py L108-L109、README.md L89-L108 |
| F-016 | 函数 `_detect_sqlite3_install_name() -> str`：调用 `otool -L $(python3 -c 'import _sqlite3; print(_sqlite3.__file__)')`，从输出中找出含 `/libsqlite3` 且以 `.dylib` 结尾的第一行 token | _loader.py L150-L174 |
| F-017 | 函数 `_build_macos_shim(lib: str) -> str`：检测 install_name → 用 `(lib, mtime, install_name)` 哈希生成缓存目录 `Path(tempfile.gettempdir()) / f"doltlite-shim-{key}"` → 若 shim 已存在则直接返回路径，否则 copy + `install_name_tool -id` 重写 → 返回 shim 路径 | _loader.py L177-L206 |

## 四、re-exec 约束与 API

| 编号 | 事实 | 出处 |
|---|---|---|
| F-018 | 函数 `_require_replayable_argv() -> None`：检查 `sys.argv[0]` 是否为非空、非 `"-c"`、且文件存在；不满足则抛出 `DoltliteLoadError`，提示用户手动设置 `DYLD_INSERT_LIBRARIES`（macOS）或 `LD_PRELOAD`（Linux） | _loader.py L117-L147 |
| F-019 | 不支持的 Python 调用方式：`python3 -c "..."`（代码字符串不在 argv 中）、交互式 REPL、Jupyter/IPython notebook——均会触发 `DoltliteLoadError` | README.md L119-L126、_loader.py L121-L123 |
| F-020 | 公共 API（`__init__.py` 的 `__all__`）：`bootstrap()`、`libdoltlite_path()`；`__version__ = "0.50.7"` | __init__.py L18-L22 |

## 五、Smoke 测试

| 编号 | 事实 | 出处 |
|---|---|---|
| F-021 | smoke 测试连接 `:memory:` 数据库，执行 `SELECT dolt_version()` 验证返回值以 `"v"` 开头；创建表 `t(x INT)` 插入3行后执行 `dolt_commit('-A', '-m', 'smoke')` | tests/smoke.py L9-L17 |
| F-022 | smoke 测试验证 `dolt_log` 虚拟表中存在 message == `"smoke"` 的记录；最终打印 `doltlite.libdoltlite_path()` 确认库路径 | tests/smoke.py L19-L24 |
