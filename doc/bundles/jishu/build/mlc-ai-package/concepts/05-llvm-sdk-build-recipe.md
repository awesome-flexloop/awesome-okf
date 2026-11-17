---
type: concept
title: LLVM SDK 构建配方
description: 一次 All-target 构建的完整 CMake 选项、三套导出集、llvm-config 相对化与 ORC 运行时
tags:
  - mlc-ai
  - llvm
  - cmake
  - build-recipe
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/prepare_llvm.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/split_sdk.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/sdk_build_options.cmake"
---

# LLVM SDK 构建配方

## 目标：一份"能被任意构建系统消费"的 LLVM

LLVM 官方并不发布"静态开发 SDK"的 wheel。本仓库要构造的是这样一个制品：

- 全部静态库是 PIC 的、非 LTO 的；
- 头文件与生成配置头齐全；
- CMake 导出可重定位；
- 有一个 `llvm-config` 兼容前端；
- 捆绑静态 zlib/zstd；
- 不含 Clang、LLD、MLIR、共享库与其他工具。

下面按 `prepare_llvm.py` 的执行顺序拆解。

## 第一步：基础 CMake 变量

`configure()` 固定了一组与平台无关的基线（F-056）：

```python
command = [
    "cmake", "-S", source, "-B", build, "-G", "Ninja",
    "-DCMAKE_BUILD_TYPE=Release", f"-DCMAKE_INSTALL_PREFIX={prefix}",
    "-DCMAKE_INSTALL_LIBDIR=lib", "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
    "-DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreadedDLL",
]
```

| 设置 | 作用 |
|---|---|
| `Release` | 无调试信息、开优化；与 SDK 的定位一致 |
| `CMAKE_INSTALL_LIBDIR=lib` | 强制 `lib/`（而不是 `lib64/`），让 CMake 导出与 `llvm-config` 的路径可预测 |
| `POSITION_INDEPENDENT_CODE=ON` | 静态库可被链进共享库（Python 扩展必需） |
| `MultiThreadedDLL` | Windows 上统一用 `/MD`，与下游 MSVC 工程一致 |

Ninja 是默认生成器（不传 `-G` 时 cmake 会自己选，但这里强制 Ninja 以获得单配置语义与更快构建）。

macOS 上若设置 `MACOSX_DEPLOYMENT_TARGET`，会转成 `-DCMAKE_OSX_DEPLOYMENT_TARGET`。CI 里固定为 `14.0`。

## 第二步：受控的段粒度

`sdk_build_options.cmake` 全文只有 10 行（F-056 相关）：

```cmake
include_guard(GLOBAL)
if(MSVC)
  add_compile_options("$<$<COMPILE_LANGUAGE:C,CXX>:/Gw>")
elseif(CMAKE_SYSTEM_NAME STREQUAL "Linux")
  add_compile_options("$<$<COMPILE_LANGUAGE:C,CXX>:-ffunction-sections;-fdata-sections>")
endif()
```

它通过 `-DCMAKE_PROJECT_INCLUDE=<path>` 注入，因此**只影响本 SDK 构建**，不改变编译器默认值，也不覆盖调用者的 `CFLAGS`。用途是让下游开 `--gc-sections` / `/OPT:REF` / `-dead_strip` 时能真正丢弃未用代码。

注意 MSVC 分支只加 `/Gw`：Release 的 `/O2` 已经隐含 `/Gy`（函数级链接），注释写明了这一点。

## 第三步：裁剪——把 LLVM 收窄成"IR + 代码生成 + ORC"

`build_llvm()` 的选项表很长（F-057 ~ F-060），可归为五类：

### 库形态

```text
-DBUILD_SHARED_LIBS=OFF
-DLLVM_BUILD_LLVM_DYLIB=OFF
-DLLVM_BUILD_LLVM_C_DYLIB=OFF
-DLLVM_LINK_LLVM_DYLIB=OFF
-DLLVM_ENABLE_PIC=ON
-DLLVM_ENABLE_LTO=OFF
```

全静态 + PIC + 无 LTO。无 LTO 是硬要求：`validate_native_archive()` 会扫描归档成员，发现 bitcode 魔数就报错（F-067）。

### 编译语义

```text
-DLLVM_ENABLE_ASSERTIONS=OFF
-DLLVM_ABI_BREAKING_CHECKS=FORCE_OFF
-DLLVM_ENABLE_RTTI=OFF
-DLLVM_ENABLE_EH=OFF
-DLLVM_USE_CRT_RELEASE=MD
```

RTTI 与异常关闭是重要契约：下游若对 LLVM 类使用 `dynamic_cast` / `typeid` 会编译失败或行为未定义。SDK 把这个事实通过 `llvm-config --has-rtti` 与 `LLVM_ENABLE_RTTI` 暴露出去（该包 README 明确说明）。

### 压缩库

```text
-DLLVM_ENABLE_ZLIB=FORCE_ON -DZLIB_USE_STATIC_LIBS=ON
-DLLVM_ENABLE_ZSTD=FORCE_ON -DLLVM_USE_STATIC_ZSTD=ON
```

`FORCE_ON` 而非 `ON`：后者在找不到时只是警告降级，前者直接失败。这保证 SDK 一定具备处理压缩节的能力。

### 关闭的可选依赖

```text
libxml2 / libedit / ffi / Z3 solver / curl / httplib / libpfm / DIA SDK / bindings / ICU / iconv
```

`DEPENDENCIES.md` 逐项解释了后果（F-159）：关掉 libxml2 会失去 Windows manifest 合并；关掉 libedit 会失去交互式编辑；关掉 ffI 会让解释器无法调用任意外部函数（ORC 不受影响）。

### 工具与产物

```text
-DLLVM_BUILD_TOOLS=ON -DLLVM_BUILD_UTILS=OFF
-DLLVM_INCLUDE_TESTS=OFF -DLLVM_INCLUDE_BENCHMARKS=OFF
-DLLVM_INCLUDE_EXAMPLES=OFF -DLLVM_INCLUDE_DOCS=OFF
```

`LLVM_BUILD_TOOLS=ON` 看起来矛盾（SDK 不含工具），但注释解释了原因：**只有定义工具安装目标，`llvm-config` 才能作为 distribution component 被安装**。真正的裁剪靠下面的逐工具开关。

## 第四步：逐个工具关掉

```python
for tool in sorted((source / "llvm/tools").iterdir()):
    if tool.is_dir() and (tool / "CMakeLists.txt").is_file():
        name = tool.name.upper().replace("-", "_")
        options.append(f"-DLLVM_TOOL_{name}_BUILD={'ON' if tool.name == 'llvm-config' else 'OFF'}")
```

注释说明了为什么必须这样写：某些被排除的工具目录自己会定义导出库（例子：`LLVMExegesisX86`），如果不显式关闭，这些库会把后端依赖泄漏进 base 导出集。

这是一处典型的"配置变量比直觉更细"：`LLVM_INCLUDE_TOOLS=OFF` 是粗粒度开关，而 `LLVM_TOOL_<NAME>_BUILD` 才是逐项开关。

## 第五步：三套导出集

这是整份配方里最关键的结构设计。`distribution_options()` 返回（F-062）：

```text
-DLLVM_DISTRIBUTIONS=Base;Extra;Reference
-DLLVM_Base_DISTRIBUTION_COMPONENTS=llvm-headers;llvm-libraries;cmake-exports;base-cmake-exports
-DLLVM_Extra_DISTRIBUTION_COMPONENTS=<extra libraries>;extra-cmake-exports
-DLLVM_Reference_DISTRIBUTION_COMPONENTS=llvm-config;reference-cmake-exports
```

为什么要三套而不是两套？

| 分发 | 内容 | 最终去处 |
|---|---|---|
| Base | 头文件、通用静态库、CMake 导出 | `mlc-llvm-static` wheel |
| Extra | 非本机后端库、Extra 导出 | `mlc-llvm-static-extra-targets` wheel |
| Reference | `llvm-config` 可执行文件、Reference 导出 | **只留在构建缓存**，不进任何 wheel |

Reference 的存在是为了"参照物"：`build_wheels.py` 用它来逐组件比对 Python 前端的输出（F-087），`split_sdk.py` 之后会删除 base 里的 `LLVMReferenceExports*.cmake` 与 `bin/llvm-config`。

### 两次 configure 的原因

```python
configure(source / "llvm", build, prefix, options)
configure(source / "llvm", build, prefix, options + distribution_options(build))
```

第一次配置的目的不是编译，而是**得到 LLVM 真实的组件依赖图**——`distribution_options()` 需要读取 `tools/llvm-config/LibraryDependencies.inc` 与 `LLVMConfig.cmake` 里的 `LLVM_TARGETS_TO_BUILD` / `LLVM_NATIVE_ARCH`。此时还没有编译任何目标文件（注释明确说「No LLVM objects have been compiled at this point」）。

第二次配置才带上导出集划分，然后依次 `install-base-distribution`、`install-extra-distribution`、`install-reference-distribution`。

## 第六步：修掉 llvm-config 里的绝对路径

静态 zstd 会让上游把归档的**绝对路径**写进 `LLVM_SYSTEM_LIBS`。这会被 `llvm-config --system-libs` 输出，重定位后失效。代码直接改写生成的 `BuildVariables.inc`（F-063）：

```python
for library in (prefix / "lib").iterdir():
    if library.suffix not in (".a", ".lib"):
        continue
    flag = library.name if os.name == "nt" else "-l" + library.stem.removeprefix("lib")
    normalized = normalized.replace(library.as_posix(), flag)
```

Unix 上变成 `-lz` / `-lzstd`（依赖 `--ldflags` 提供的 `-L` 搜索路径），Windows 上保留裸库名。

## 第七步：pkg-config 相对化

```python
text = re.sub(r"^prefix=.*$", "prefix=${pcfiledir}/../..", text, flags=re.MULTILINE)
```

`${pcfiledir}` 是 pkg-config 的相对路径变量：`.pc` 文件位于 `<prefix>/lib/pkgconfig/`，因此 `../..` 正好回到前缀根。

## 第八步：Linux 额外的 ORC 运行时

```python
if platform.system() == "Linux":
    triple = run([prefix / "bin" / "llvm-config", "--host-target"], capture=True)
    configure(source / "compiler-rt", build, prefix / "lib" / "clang" / LLVM_VERSION.split(".")[0], [...])
    install(build, "install-orc")
```

只构建 ORC 部分（`COMPILER_RT_BUILD_ORC=ON`，其余 sanitizer/xray/fuzzer/profile/gwp_asan/scudo 全关），安装到 `lib/clang/<major>/`。这个路径与 TVM-FFI ORC addon 的发现约定一致（该包 README「Usage」段）。

`validate_prefix()` 会在 Linux 上强制检查 `lib/clang/*/lib/**/liborc_rt*.a` 存在（F-070）。

## 第九步：校验与元数据落盘

`validate_prefix()` 的检查项（F-068 ~ F-070）：

1. 若已有 `base.json`：逐文件校验 SHA-256（重打包路径）。
2. 否则要求三个关键文件存在：`bin/llvm-config`、`include/llvm/IR/Module.h`、`lib/cmake/llvm/LLVMConfig.cmake`。
3. `bin/` 下只允许 `llvm-config` 一个文件——这是"不含工具"的机械证明。
4. 不含任何 `.so` / `.dylib` / `.dll` / `.so.N`。
5. 每个 `.a`/`.lib` 通过 `validate_native_archive()`：正确的归档头、无 LTO bitcode。
6. `llvm-config --version` 等于钉扎版本；`--prefix` 等于实际前缀（可重定位）。
7. Linux 上 ORC 运行时存在。

最后写入 `staticlib.json`（F-071 相关）：

```python
details.update({
    "schema_version": 1, "sources": SOURCES,
    "source_overrides": [...],
    "system": platform.system(), "machine": platform.machine(),
    "build": {"type": "Release", "pic": True, "lto": False,
              "assertions": False, "rtti": False, "exceptions": False},
    "files": {相对路径: {"sha256": ..., "size": ...}},
})
```

这些字段后续会成为 `base.json` 的骨架（`split_sdk.py` 复制除 `files` 外的键，并补 `schema_version=2`、`sdk_version`、`build_id`、`targets`）。

## 成本与运行位置

该包 README 明确建议**用远程构建机编译 LLVM**。原因是单次全量 All-target 构建是小时级。CI 用两层措施降低重复成本：

1. `actions/cache` 按 `llvm-all-sdk-<platform>-<recipe key>` 缓存整个编译结果（F-137）；
2. `MLC_LLVM_STATIC_CLEAN_BUILD=1` 在分片前删除源码构建树，释放磁盘（注释：「Free only our own managed build tree」）。

## 自检方式

```bash
# 1) 关键裁剪项齐全
grep -n "LLVM_ENABLE_RTTI\|LLVM_ENABLE_LTO\|BUILD_SHARED_LIBS\|LLVM_ENABLE_ZLIB" \
  packages/mlc-llvm-static/scripts/prepare_llvm.py

# 2) 三套导出集存在
grep -n "LLVM_DISTRIBUTIONS" packages/mlc-llvm-static/scripts/split_sdk.py

# 3) 无 LTO bitcode 的校验存在
grep -n "LTO bitcode is not allowed" packages/mlc-llvm-static/scripts/prepare_llvm.py

# 4) 段粒度钩子
cat packages/mlc-llvm-static/scripts/sdk_build_options.cmake
```

## 陷阱

- **不要打开 `LLVM_ENABLE_RTTI`**：会改变 ABI 约定，且与已发布的 wheel 不一致；下游 `dynamic_cast` 需求应作为"不支持"处理。
- **不要打开 `LLVM_BUILD_TOOLS=OFF`**：`llvm-config` 会失去安装目标，`install-reference-distribution` 失败。
- **`LLVM_TARGETS_TO_BUILD` 默认 `all`**：分片逻辑要求至少两个目标且包含本机后端（F-076），单目标构建无法分片。
- **修改 `sdk_build_options.cmake` 会让缓存失效**：它被读入 recipe 指纹（F-136），这是有意为之。

## 延伸阅读

- 分片如何切：[SDK 分片：一次构建、两个 wheel](06-split-sdk-partitioning.md)
- 依赖为何这样关：[依赖审计要点](../references/02-dependency-audit.md)
- 构建命令实操：[从源码构建 LLVM SDK](../examples/01-build-llvm-sdk-from-source.md)
