---
type: Concept
title: 跨平台符号劫持策略
description: "doltlite-python 在 Linux（RTLD_GLOBAL）和 macOS（shim + re-exec）上的不同符号劫持策略及原理；F-013~F-017。"
tags: [doltlite-python, symbol-hijacking, linux, macos, ctypes]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-09-10" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10" }
status: stable
stale_after: "2027-03-31"
sources:
  - id: doltlite-python-local
    resource: "本地克隆（tag v0.50.7，commit ba3b46fa6f58e42aef4b929d97a28248832079cb）"
    title: doltlite-python 源码逐文件精读
---

# 跨平台符号劫持策略

> **对应 F 编号**：F-013 ~ F-017

## 核心挑战

Python 的 `sqlite3` 模块是 libsqlite3 的动态链接封装。要让 Dolt 版本控制功能生效，必须使 libdoltlite 的 `sqlite3_*` 符号在 sqlite3 模块解析符号时**优先于系统 libsqlite3**。不同 OS 的动态链接器行为差异导致了不同的实现策略。

## Linux：flat-namespace + RTLD_GLOBAL

Linux ELF 使用**扁平命名空间**（flat-namespace），符号解析按加载顺序决定优先级：

```
Linux 加载顺序（理想情况）：
1. ctypes.CDLL(libdoltlite, RTLD_GLOBAL)  → libdoltlite 的 sqlite3_* 进入全局命名空间
2. import sqlite3                          → _sqlite3.so 解析 sqlite3_* → 命中 libdoltlite
```

代码实现（F-013、F-014）：

```python
# _loader.py L98-L101
if sys.platform != "darwin" and not _sqlite3_already_imported():
    ctypes.CDLL(lib, mode=ctypes.RTLD_GLOBAL)   # 注入全局符号
    os.environ[_BOOTSTRAP_MARKER] = "1"
    return
```

若 `sqlite3` 已在 bootstrap 前导入（_sqlite3.so 已绑定系统 libsqlite3），则退回到 re-exec 策略：

```python
# _loader.py L110-L114
env["LD_PRELOAD"] = f"{lib} {existing}".strip()
os.execvpe(sys.executable, [sys.executable, *sys.argv], env)
```

`LD_PRELOAD` 在进程启动时优先加载指定库，覆盖系统 libsqlite3。

## macOS：two-level namespace + shim + re-exec

macOS dyld 使用**两层命名空间**（two-level namespace），每个 .dylib 在链接时就确定了依赖哪个具体的 libsqlite3.dylib 路径（通过 `LC_LOAD_DYLIB` 指令）。因此 `ctypes.CDLL` 注入的符号对已链接的 `_sqlite3.so` 不可见。

唯一可行的方案是构建一个 **install_name 匹配的 shim**，使动态链接器认为 shim 就是 _sqlite3.so 原本期望的那个 libsqlite3.dylib（F-015）：

```
macOS 加载流程：
1. _detect_sqlite3_install_name()          → 找出 _sqlite3.so 期望的 libsqlite3 路径
2. _build_macos_shim(lib)                  → copy libdoltlite → shim
3. install_name_tool -id <原路径> <shim>   → 改写 shim 的 install_name
4. re-exec + DYLD_INSERT_LIBRARIES=<shim>  → dyld 加载 shim 替代系统 libsqlite3
```

`_detect_sqlite3_install_name()` 通过 `otool -L` 解析（F-016）：

```python
# _loader.py L150-L174
def _detect_sqlite3_install_name() -> str:
    import _sqlite3
    out = subprocess.run(
        ["otool", "-L", _sqlite3.__file__],
        check=True, capture_output=True, text=True,
    ).stdout
    for line in out.splitlines():
        token = line.strip().split(" ", 1)[0]
        if "/libsqlite3" in token and token.endswith(".dylib"):
            return token
    raise DoltliteLoadError("Could not find a libsqlite3 dependency ...")
```

`_build_macos_shim()` 使用哈希缓存避免重复构建（F-017）：

```python
# _loader.py L177-L206
def _build_macos_shim(lib: str) -> str:
    install_name = _detect_sqlite3_install_name()
    key = f"{abs(hash((lib, src_stat.st_mtime_ns, install_name))):016x}"
    cache_dir = Path(tempfile.gettempdir()) / f"doltlite-shim-{key}"
    shim = cache_dir / "libsqlite3.dylib"
    
    if shim.exists():
        return str(shim)   # 缓存命中，直接返回
    
    # 首次：copy + install_name_tool -id 改写
    shutil.copyfile(lib, shim)
    subprocess.run(
        ["install_name_tool", "-id", install_name, str(shim)],
        check=True, capture_output=True, text=True,
    )
    return str(shim)
```

## 策略对比

| 维度 | Linux | macOS |
|------|-------|-------|
| 命名空间模型 | flat-namespace | two-level namespace |
| 核心机制 | `ctypes.CDLL(RTLD_GLOBAL)` | `install_name_tool` + `DYLD_INSERT_LIBRARIES` |
| 是否需要 re-exec | sqlite3 未导入时无需；已导入时是 | 总是需要（除非已标记 bootstrap） |
| 工具依赖 | 无 | `otool`、`install_name_tool`（Xcode CLT） |
| shim 位置 | 无 | `$TMPDIR/doltlite-shim-<hash>/libsqlite3.dylib` |

## re-exec 约束

两种平台在需要 re-exec 时都调用 `_require_replayable_argv()`（F-018）：

```python
# _loader.py L117-L147
def _require_replayable_argv() -> None:
    arg0 = sys.argv[0] if sys.argv else ""
    if arg0 and arg0 != "-c" and os.path.exists(arg0):
        return   # 合法脚本路径，可以 re-exec
    raise DoltliteLoadError(
        "doltlite bootstrap requires re-execing the interpreter, but the "
        f"current invocation (sys.argv[0]={arg0!r}) does not name a "
        "script that can be replayed..."
    )
```

被排除的场景（F-019）：
- `python3 -c "..."` — 代码字符串不在 argv 中
- 交互式 REPL — argv[0] 为空或为 `-`
- Jupyter/IPython notebook — argv[0] 指向内核进程，非用户脚本

## 学习路径

* [bootstrap() 加载机制](01-bootstrap-mechanism.md) — 幂等性设计与自动调用时序
* [wheel tag 与构建系统](03-wheel-and-build.md) — py3-none tag 如何消除多版本构建负担
