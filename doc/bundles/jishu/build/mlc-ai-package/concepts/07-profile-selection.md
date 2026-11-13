---
type: concept
title: profile 选择与派发
description: auto/native/all 三档如何在头文件、CMake 与 Python 三处保持一致
tags:
  - mlc-ai
  - llvm
  - profile
  - cmake
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/split_sdk.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/python/mlc_llvm_static/_llvm_config.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/README.md"
---

# profile 选择与派发

## 三个取值，一条规则

`MLC_LLVM_STATIC_PROFILE` 接受三个值：

| 值 | 含义 | 前提 |
|---|---|---|
| `auto`（默认） | 有 add-on 就 `all`，没有就 `native` | 无 |
| `native` | 只用本机后端 | 无（即使 add-on 已装） |
| `all` | 使用全部标准后端 | 必须已安装 add-on |

非法值一律报错，不做"猜一个"的容错。三个包的实现措辞不同但语义一致：

```cmake
# profile_cmake() 注入到 LLVMConfig.cmake
if(NOT MLC_LLVM_STATIC_PROFILE OR MLC_LLVM_STATIC_PROFILE STREQUAL "auto")
  if(_mlc_has_extra)
    set(MLC_LLVM_STATIC_PROFILE "all")
  else()
    set(MLC_LLVM_STATIC_PROFILE "native")
  endif()
endif()
if(MLC_LLVM_STATIC_PROFILE STREQUAL "all" AND NOT _mlc_has_extra)
  message(FATAL_ERROR "The all LLVM profile requires mlc-llvm-static-extra-targets")
elseif(NOT MLC_LLVM_STATIC_PROFILE MATCHES "^(native|all)$")
  message(FATAL_ERROR "LLVM profile must be auto, native, or all")
endif()
```

```python
# Configuration.__init__()
self.profile = profile or os.environ.get("MLC_LLVM_STATIC_PROFILE", "auto")
if self.profile not in ("auto", "native", "all"):
    raise ConfigurationError("LLVM profile must be auto, native, or all")
if self.profile == "auto":
    self.profile = "all" if self.extra else "native"
if self.profile == "all" and self.extra is None:
    raise ConfigurationError("The all profile requires the matching mlc-llvm-static-extra-targets wheel")
```

## 为什么"安装态即开关"

两个 wheel 共享同一个 `site-packages/mlc_llvm_static/static/` 前缀。如果安装 add-on 时改写 base 拥有的文件（例如重写 `Targets.def`），那么：

- 卸载 add-on 就无法恢复原状（除非备份，而备份本身又要占空间）；
- 两个 wheel 的文件所有权不再互斥，`pip` 的 RECORD 卸载语义会互相破坏。

所以设计选择是：**任何一方都不写对方的文件**，只在自己拥有的路径下放"候选内容"，由读取侧决定用哪一份。这正是"安装态即开关"的含义。

## 三处派发点

### 1. C 预处理器：`__has_include`

`filter_headers()` 生成的派发器（F-079）：

```c
#if !defined(MLC_LLVM_STATIC_NATIVE_ONLY) && __has_include("llvm/Config/mlc-all/Targets.def")
#include "llvm/Config/mlc-all/Targets.def"
#else
#include "llvm/Config/mlc-native/Targets.def"
#endif
```

行为矩阵：

| 安装态 | 编译宏 | `mlc-all/` 是否存在 | 实际生效 |
|---|---|---|---|
| 只装 base | 无 | 否 | native |
| 只装 base | `MLC_LLVM_STATIC_NATIVE_ONLY` | 否 | native |
| 装 base + extra | 无 | 是 | all |
| 装 base + extra | `MLC_LLVM_STATIC_NATIVE_ONLY` | 是 | native |

这个宏由 CMake（native 档）与 `llvm-config --cflags/--cppflags/--cxxflags`（native 档）自动注入（F-082、F-104）。因此走 CMake 的用户和走裸旗标的用户拿到一致行为。

### 2. CMake：读取 `base.json` / `extra.json`

`profile_cmake()` 把一段逻辑注入 `LLVMConfig.cmake`（F-080、F-081），核心是三步：

```cmake
file(READ "${LLVM_INSTALL_PREFIX}/share/mlc-llvm-static/base.json" _mlc_base)
string(JSON _mlc_build GET "${_mlc_base}" build_id)
string(JSON _mlc_version GET "${_mlc_base}" sdk_version)
set(_mlc_has_extra OFF)
if(EXISTS "${LLVM_INSTALL_PREFIX}/share/mlc-llvm-static/extra.json")
  file(READ ... _mlc_extra)
  string(JSON _mlc_extra_build GET "${_mlc_extra}" build_id)
  string(JSON _mlc_extra_version GET "${_mlc_extra}" sdk_version)
  if(NOT _mlc_extra_build STREQUAL _mlc_build OR NOT _mlc_extra_version STREQUAL _mlc_version)
    message(FATAL_ERROR "LLVM base and extra-targets packages have different build IDs or versions")
  endif()
  set(_mlc_has_extra ON)
endif()
```

然后按 profile 设置可用库与目标：

```cmake
if(MLC_LLVM_STATIC_PROFILE STREQUAL "native")
  set(LLVM_AVAILABLE_LIBS <base 库列表>)
  set(LLVM_TARGETS_TO_BUILD <本机后端>)
else()
  set(LLVM_AVAILABLE_LIBS <全部库列表>)
  set(LLVM_TARGETS_TO_BUILD <全部后端>)
endif()
```

两处细节值得注意：

- **`LLVMExtraExports.cmake` 的 include 被包进 all 分支**：native 档不 include，避免引用已被移走的库。
- **`LLVMReferenceExports.cmake` 的 include 被删除**：该导出集只在构建缓存里存在。

最后追加：

```cmake
if(MLC_LLVM_STATIC_PROFILE STREQUAL "native")
  string(APPEND LLVM_DEFINITIONS " -DMLC_LLVM_STATIC_NATIVE_ONLY=1")
endif()
set_property(GLOBAL PROPERTY LLVM_COMPONENT_LIBS ${LLVM_AVAILABLE_LIBS})
```

### 3. Python：`Configuration`

`Configuration.__init__()` 读同一批 JSON，做同一套校验（F-101），并把 `targets`、`components`、`libraries` 按 profile 取不同来源：

```python
self.targets = self.base["targets"] if self.profile == "native" else self.extra["targets"]
self.components = self.base["profiles"][self.profile]["components"]
self.libraries = self.base["profiles"][self.profile]["libraries"]
```

注意 native 档的组件图与库映射都来自 **base** 的 `profiles.native`，all 档来自 **base** 的 `profiles.all`——组件图只存一份，避免两份图漂移。

## 用户可用的三种设置方式

该包 README 写明三种等效方式：

```bash
# 1) 环境变量
MLC_LLVM_STATIC_PROFILE=native python -m pip ...   # 影响 Python 侧查询
export MLC_LLVM_STATIC_PROFILE=all

# 2) CMake 变量
cmake -S . -B build -DMLC_LLVM_STATIC_PROFILE=native

# 3) llvm-config 命令行参数
python -m mlc_llvm_static.config --llvm-config   # 拿到前端路径
<prefix>/bin/llvm-config --profile=native --libs Core native
```

`--profile=` 由 `_llvm_config.main()` 从 `argv` 中剥离（F-104 相关）：

```python
for arg in list(args):
    if arg.startswith("--profile="):
        profile = arg.partition("=")[2]
        args.remove(arg)
```

优先级：显式参数 > 环境变量 > `auto`。

## CMake 与 Python 的一致性从哪来

三处实现共享同一份事实源（`base.json` / `extra.json`），但代码是三份。一致性靠两个机制维持：

1. **单元测试固定 fixture**：`test_profiles.py` 用一份手写 `base.json` 同时驱动 `Configuration` 与 `split_sdk.partitions()`，断言两者对同一图的解释一致。
2. **真实 wheel 四态验证**：`verify_split_wheels.py` 在每种安装态下既跑 Python 断言，又用 CMake 构建消费者（F-153）。

如果只改一处，第一个机制会红；如果三处都改但语义错了，第二个机制会红。

## 一个容易误解的点：`--targets-built` 不是"宿主架构"

`Configuration.query(["--targets-built"])` 返回的是**已编译进 SDK 的后端列表**，而不是构建机架构。在 x86_64 机器上装 all-profile 的 SDK，它会返回包含 AArch64、RISCV、WebAssembly 等的一长串名字。

这带来两个推论：

- x86_64 wheel 里的 AArch64 后端是"x86_64 代码生成 AArch64 目标文件"，不是"能在 AArch64 上运行"；
- 判断"能否在本机 JIT"要用 `host_target` 与 `native` 组件，而不是看 `targets-built` 长度。

## 自检方式

```bash
# 1) 三处实现都接受同一组取值
grep -n "native|all" packages/mlc-llvm-static/scripts/split_sdk.py
grep -n "native.*all" packages/mlc-llvm-static/python/mlc_llvm_static/_llvm_config.py

# 2) 头文件派发器存在且引用 mlc-all/mlc-native
head -5 packages/mlc-llvm-static/python/mlc_llvm_static/static/include/llvm/Config/Targets.def

# 3) 各安装态下的实际解析结果
python - <<'PY'
from pathlib import Path
from mlc_llvm_static._llvm_config import Configuration
import mlc_llvm_static as sdk
for p in ("auto", "native"):
    c = Configuration(Path(sdk.get_prefix()), p)
    print(p, "→", c.profile, c.targets[:3], len(c.libraries))
PY
```

## 陷阱

- **不要只删 `extra.json` 而保留库文件**：`auto` 会回到 native，但 all 档会因缺 `extra.json` 报错——这是有意的（避免"库在但元数据不在"的中间态）。
- **不要让 `extra.json` 与 `base.json` 的 `build_id` 不同源**：`profile_cmake` 与 `Configuration` 都会硬失败；这不是可以"跳过"的警告。
- **`MLC_LLVM_STATIC_NATIVE_ONLY` 只在 native 档定义**：下游若手工定义它，可以强制 native 编译，但要自行保证不调用后端 API。
- **`--link-shared` 永远失败**：SDK 只提供静态库，这不是配置项。

## 延伸阅读

- 分片如何产生这两份元数据：[SDK 分片](06-split-sdk-partitioning.md)
- 前端如何用 profile 组装链接命令：[llvm-config 兼容前端](08-llvm-config-frontend.md)
- 四态验证细节：[验证体系](14-verification-strategy.md)
