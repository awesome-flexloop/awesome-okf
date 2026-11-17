---
type: concept
title: llvm-config 兼容前端
description: 用构建期生成的组件图复现 llvm-config 查询，保证静态链接顺序与可重定位
tags:
  - mlc-ai
  - llvm-config
  - link-order
  - python-frontend
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/python/mlc_llvm_static/_llvm_config.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/python/mlc_llvm_static/__init__.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/python/mlc_llvm_static/config.py"
---

# llvm-config 兼容前端

## 为什么不直接发上游 llvm-config

上游 `llvm-config` 是一个 C++ 可执行文件，它的输出里包含**配置时的绝对路径**。一旦 SDK 被 pip 装到别的前缀，这些路径就失效。本仓库的解法是：

- 上游可执行文件留在 Reference 分发里，**不进任何 wheel**（F-084）；
- wheel 里放 `bin/llvm-config.py`（Unix 下另有可执行的 `llvm-config` 副本）；
- 该脚本读取构建期生成的 `base.json`，用其中的组件图与旗标重新计算答案。

验证阶段会把 SDK 复制到一个**带空格**的目录，再用 `python /copied/prefix/bin/llvm-config.py` 校验（F-144）——这是对"路径不能写死"的机械证明。

## 三类查询

`Configuration.query(args)` 把参数分成三类处理（F-103 ~ F-106）：

### 1. 直出表（不需要组件）

```python
direct = {
    "--version": self.base["llvm_version"], "--prefix": str(self.prefix),
    "--bindir": ..., "--includedir": ..., "--libdir": ..., "--cmakedir": ...,
    "--obj-root": ..., "--host-target": self.base["host_target"],
    "--targets-built": " ".join(self.targets), "--components": " ".join(sorted(self.components)),
    "--build-mode": self.base["build"]["type"], "--build-system": "cmake",
    "--has-rtti": "YES" if self.base["build"]["rtti"] else "NO",
    "--assertion-mode": "ON" if self.base["build"]["assertions"] else "OFF",
}
```

路径类选项在 `--quote-paths` 下会走 `render()`：Windows 用 `subprocess.list2cmdline`，Unix 用 `shlex.quote`（F-106）。这是一个必要细节——Windows 路径含反斜杠与空格，POSIX 引号规则会把它们解析错。

### 2. 拼装输出（依赖前缀与旗标）

| 参数 | 行为 |
|---|---|
| `--cflags` / `--cppflags` / `--cxxflags` | `-I<prefix>/include` + 上游记录的旗标；native 档追加 `-DMLC_LLVM_STATIC_NATIVE_ONLY=1` |
| `--ldflags` | `-L<prefix>/lib`（Windows `-LIBPATH:`）+ 上游 ldflags |
| `--system-libs` | 把记录中的 `${prefix}` 占位替换成真实前缀后输出 |

### 3. 延迟到组件解析

`--libs`、`--libfiles`、`--libnames`、`--shared-mode`、`--system-libs` 会被放进 `deferred` 集合，等组件参数解析完再统一计算。

## 链接顺序：后序 DFS 再反转

静态链接对顺序敏感：被依赖者必须出现在依赖者之后。`ordered_libraries()` 的算法（F-102）：

```python
def visit(name):
    name = name.lower()
    if name not in graph:
        raise ConfigurationError(f"component {name!r} is unavailable in the {self.profile} profile")
    if name in visited:
        return
    visited.add(name)
    entry = graph[name]
    for dep in entry["requires"]:
        visit(dep)
    library = entry["library"]
    if library:
        path = self.prefix / self.libraries[library]
        if not path.is_file():
            raise ConfigurationError(f"missing static archive: {path}")
        result.append(library)

for component in components or ["all"]:
    visit(component)
return list(reversed(result))
```

要点：

- **后序收集 + 整体反转** = 拓扑序的逆序，即"依赖在前"。
- **`visited` 去重**：同一库被多条路径依赖时只出现一次。
- **缺归档在拼接命令前就报错**：不会生成一条"看起来正常、链接时才失败"的命令。
- **组件名大小写不敏感**：`name.lower()` 匹配图里的键。

`test_profiles.py` 的 `test_dependency_order_and_deduplication` 固定了这个行为：

```python
assert config.query(["--link-static", "--libs", "Core", "native"]) == "-lLLVMX86CodeGen -lLLVMCore -lLLVMSupport\n"
```

## 各输出格式

```python
if deferred & {"--libs", "--libfiles", "--libnames"}:
    for library in libraries:
        path = self.prefix / self.libraries[library]
        if "--libnames" in deferred:
            values.append(path.name)
        elif "--libfiles" in deferred or windows:
            values.append(str(path))
        else:
            values.append("-l" + library)
```

三条规则：

| 平台/参数 | 输出 |
|---|---|
| `--libnames` | 纯文件名（`libLLVMCore.a`），用于交给别的工具做路径解析 |
| `--libfiles` | 绝对路径 |
| 不带以上参数且非 Windows | `-lLLVMCore`（依赖 `--ldflags` 的 `-L`） |
| Windows（任意 lib 参数） | 绝对路径（MSVC 链接器不认 `-l`） |

`--shared-mode` 恒返回 `static`，因为 SDK 只有静态库。

## 拒绝的查询

```python
elif arg == "--link-shared":
    raise ConfigurationError("This SDK only provides static LLVM libraries")
else:
    raise ConfigurationError(f"unknown option: {arg}")
```

还有一条结构约束：

```python
if not args or (components and not deferred):
    raise ConfigurationError("Specify a configuration option; components require a library query")
```

即 `llvm-config Core` 这种"只给组件不给选项"的调用会失败——上游在这种情况下会输出帮助，这里选择显式报错，避免脚本误用。

## Python 包侧的定位 API

`mlc_llvm_static/__init__.py` 提供一组薄封装（F-099）：

```python
def _require(relative, *, executable=False):
    path = Path(__file__).resolve().parent / relative
    if not path.exists():
        raise FileNotFoundError(f"LLVM SDK artifact is missing: {path}")
    if executable and not os.access(path, os.X_OK):
        raise PermissionError(f"LLVM SDK executable is not executable: {path}")
    return str(path)

def get_prefix() -> str: return _require("static")
def get_cmake_dir() -> str: return _require("static/lib/cmake/llvm")
def get_include_dir() -> str: return _require("static/include")
def get_library_dir() -> str: return _require("static/lib")
```

设计原则写在该模块 docstring 里：「importing never downloads files」。所有路径都基于 `__file__` 相对推导，因此天然可重定位。

### Windows 的 launcher 定位

`get_llvm_config()` 在 Windows 上走 `_windows_launcher()`（F-100）：

```python
installed = distribution("mlc-llvm-static")
for record in installed.files or []:
    if record.name.lower() == "llvm-config.exe":
        path = Path(installed.locate_file(record)).resolve()
        if path.is_file():
            return str(path)
path = Path(sysconfig.get_path("scripts")) / "llvm-config.exe"
if not path.is_file():
    raise FileNotFoundError(f"The pip-installed llvm-config launcher is missing: {path}")
```

两段注释解释了为什么不简化：

- **不能只查 `sysconfig` 的默认 Scripts 目录**：`pip install --user` 会装到用户目录。
- **不能查 PATH**：可能命中另一个 LLVM 发行版，导致版本错配。

`llvm-config.exe` 由 `[project.scripts]` 注册（`llvm-config = "mlc_llvm_static._llvm_config:main"`），所以它其实是 pip 生成的 launcher，不是原生可执行文件。这也是为什么"复制出来的 Windows SDK 不是独立可执行工具链"——该包 README 明确提示：复制的前缀要用 `python /copied/prefix/bin/llvm-config.py`。

## `config.py`：给构建脚本用的四个路径

```python
for flag in ("prefix", "cmake-dir", "include-dir", "library-dir", "llvm-config"):
    group.add_argument(f"--{flag}", action="store_true")
```

互斥且必选。典型用法：

```bash
cmake -S . -B build \
  -DLLVM_DIR="$(python -m mlc_llvm_static.config --cmake-dir)" \
  -DCMAKE_PREFIX_PATH="$(python -m mlc_llvm_static.config --prefix)" \
  -DZLIB_USE_STATIC_LIBS=ON
```

## 与上游 llvm-config 的对齐验证

`build_wheels.py` 在分片后做一次逐组件比对（F-087）：

```python
for profile in ("native", "all"):
    reference = copy.copy(config)
    reference.prefix = raw / "static"
    reference.profile = profile
    reference.components = config.base["profiles"][profile]["components"]
    reference.libraries = config.base["profiles"][profile]["libraries"]
    for component in sorted(reference.components):
        expected = subprocess.check_output([str(executable), "--link-static", "--libnames", component], text=True).strip()
        actual = reference.query(["--link-static", "--libnames", component]).strip()
        if actual != expected:
            raise RuntimeError(f"Python llvm-config differs from upstream for {profile}/{component}")
```

注意 `reference.prefix` 被指向 raw 前缀（含全部归档），因此可以在**不安装 add-on**的情况下比对 all 档。这是"用参照物校验替代物"的典型手法。

## 自检方式

```bash
# 1) 前端与上游对拍（需要已构建的 raw SDK）
python - <<'PY'
import subprocess, sys
print(subprocess.run([sys.executable, "-m", "mlc_llvm_static.config", "--llvm-config"],
                     capture_output=True, text=True).stdout.strip())
PY

# 2) 可重定位：复制到带空格目录后查询
python - <<'PY'
import shutil, subprocess, sys, tempfile
from pathlib import Path
import mlc_llvm_static as sdk
with tempfile.TemporaryDirectory() as t:
    dst = Path(t) / "relocated SDK with spaces"
    shutil.copytree(sdk.get_prefix(), dst)
    print(subprocess.run([sys.executable, str(dst / "bin/llvm-config.py"), "--prefix"],
                         capture_output=True, text=True).stdout.strip())
PY

# 3) 不支持的模式必须失败
python -m mlc_llvm_static._llvm_config --link-shared --libs ; echo "exit=$?"
```

## 陷阱

- **`--system-libs` 的上游语义很窄**：`DEPENDENCIES.md` 指出上游只从 Support 与 WindowsManifest 构造该输出，且不随请求组件变化（F-160）。前端忠实复现了这个行为，不要期待它包含 Windows HTTP 之类的新增依赖。
- **`/MD` 与编译器默认库不在 `--system-libs` 里**：下游仍需自行提供匹配的 CRT 运行时。
- **不要用 `--libfiles` 的输出直接拼 shell 字符串**：路径含空格，务必用 `--quote-paths` 或让构建系统按列表处理。
- **`MLC_LLVM_STATIC_SDK_PREFIX` 只用于测试**：它允许指定任意前缀，生产路径应走 `__file__` 相对推导。

## 延伸阅读

- profile 语义：[profile 选择与派发](07-profile-selection.md)
- 链接验证的完整链路：[验证体系](14-verification-strategy.md)
- 消费者用法：[消费 LLVM SDK](../examples/00-consume-llvm-sdk.md)
