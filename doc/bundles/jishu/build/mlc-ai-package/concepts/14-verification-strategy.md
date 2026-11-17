---
type: concept
title: 验证体系
description: 从哈希到链接、从符号到 ABI——把"用户实际会做的链接"变成可执行断言
tags:
  - mlc-ai
  - verification
  - abi
  - symbols
generated: true
verified: false
status: stable
stale_after: "2027-05-01"
sources:
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/verify_wheel.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/scripts/verify_split_wheels.py"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/verify/"
  - "external/dev/libs/mlc-ai/package/packages/mlc-llvm-static/tests/python/"
---

# 验证体系

## 四层防线

这个仓库的验证不是"跑个 pytest"，而是四层递进：

```text
① 单元测试（tests/python/）        逻辑正确性：划分、排序、派发、解析
② 安装后自检（verify_wheel.py）    制品完整性：哈希、可重定位、无共享库
③ 消费方构建（verify/）            契约可用性：能编译、能链接、能运行、符号干净
④ 安装态矩阵（verify_split_wheels.py）组合正确性：native/all/显式/卸载
```

每层解决前一层的盲区：单测证明"算法对"，但不证明"wheel 里的文件对"；哈希校验证明"文件没变"，但不证明"能链接"；能链接不证明"符号不泄漏"；单态通过不证明"组合态正确"。

## 第一层：单元测试都测什么

| 测试文件 | 覆盖内容 |
|---|---|
| `test_profiles.py` | profile 选择、跨 build_id 拒绝、链接顺序与去重、缺归档提前报错、不支持查询报错、header 派发不覆盖、组件表格式、split 后所有权互斥 |
| `test_coff.py` | COFF 归档解析与符号保护规则 |
| `test_compression.py` | 重压缩前后成员/CRC/属性一致 |
| `test_archives.py` | 归档头与 LTO bitcode 检测 |
| `test_cache.py` | 缓存恢复的路径白名单与权限 |
| `test_sources.py` | 源码下载/解压/戳记 |
| `test_packaging_tools.py` | 7-Zip 定位与单文件提取 |
| `test_versions.py` | `stamp_version` 的版本规则 |
| `test_dependencies.py` | 依赖审计表的机器可读部分 |
| `test_launcher.py` | Windows launcher 定位 |

一个值得学习的细节：`test_profiles.py` 用**手写的最小组件图**驱动真实函数，而不是 mock：

```python
graph = {
    "support": {"library": "LLVMSupport", "requires": []},
    "core": {"library": "LLVMCore", "requires": ["support"]},
    "x86codegen": {"library": "LLVMX86CodeGen", "requires": ["core", "support"]},
    "armcodegen": {"library": "LLVMARMCodeGen", "requires": ["core", "support"]},
    "x86": {"library": None, "requires": ["x86codegen"]},
    "arm": {"library": None, "requires": ["armcodegen"]},
    "native": {"library": None, "requires": ["x86"]},
    "all-targets": {"library": None, "requires": ["x86", "arm"]},
    "all": {"library": None, "requires": ["support", "core", "x86codegen", "armcodegen", "all-targets", "native", "x86", "arm"]},
}
```

这样 `partitions()`、`Configuration`、`filter_headers()` 都能在秒级跑完，且断言的是真实算法而非桩。

## 第二层：安装后自检

`verify_wheel.py` 的 `main()` 按顺序做九件事（F-143 ~ F-147）：

### 1. 版本与 launcher

```python
if run([sdk.get_llvm_config(), "--version"], capture=True) != sdk.LLVM_VERSION:
    raise RuntimeError("The installed llvm-config launcher returned an incorrect version")
if Path(run([sdk.get_llvm_config(), "--prefix"], capture=True)).resolve() != original.resolve():
    raise RuntimeError("The installed llvm-config launcher resolved a different SDK")
```

第二条尤其重要：`--prefix` 必须指回**安装位置**，否则可能有另一个 LLVM 在 PATH 上被命中。

### 2. 全量哈希

```python
for relative, record in metadata["files"].items():
    path = original / relative
    if not path.is_file():
        raise RuntimeError(f"Installed wheel is missing {relative}")
    ...
    if digest != record["sha256"]:
        raise RuntimeError(f"Installed payload checksum mismatch: {relative}")
```

`metadata()` 在 all 档会合并 `extra.json` 的 `files`，因此这一条同时校验两个 wheel 的载荷。

### 3. 配置 CLI

```python
for flag, expected in (("--prefix", sdk.get_prefix()), ("--cmake-dir", sdk.get_cmake_dir()),
                       ("--llvm-config", sdk.get_llvm_config())):
    if run([sys.executable, "-m", "mlc_llvm_static.config", flag], capture=True) != expected:
        raise RuntimeError(f"Configuration helper returned an incorrect {flag}")
```

### 4. 重定位到带空格的目录

```python
with tempfile.TemporaryDirectory(prefix="mlc-llvm-verify-") as temporary:
    root = Path(temporary)
    prefix = root / "relocated SDK with spaces"
    shutil.copytree(original, prefix)
    command = [sys.executable, prefix / "bin/llvm-config.py"]
```

空格是刻意选的：Windows 上路径空格是最常见的引号 bug 触发器。

### 5. 四个路径查询 + 不含工具

```python
for flag, expected in (("--prefix", prefix), ("--includedir", prefix / "include"),
                       ("--libdir", prefix / "lib"), ("--cmakedir", prefix / "lib/cmake/llvm")):
    if Path(run([*command, flag], capture=True)).resolve() != expected.resolve():
        raise RuntimeError(f"llvm-config {flag} is not relocatable")

if any(path.is_file() and path.name not in ("llvm-config", "llvm-config.py")
       for path in (prefix / "bin").iterdir()):
    raise RuntimeError("SDK unexpectedly contains compiled LLVM tools")
```

### 6. system-libs 路径必须在前缀内

```python
system_libs = run([*command, "--quote-paths", "--link-static", "--system-libs"], capture=True)
verify_system_library_paths(system_libs, prefix)
```

`verify_system_library_paths()` 逐 token 判断绝对路径是否落在重定位前缀内：

```python
root = paths.normcase(paths.abspath(str(prefix)))
for token in shlex.split(output, posix=not windows):
    library = token.strip('"')
    if not paths.isabs(library):
        continue
    candidate = paths.normcase(paths.abspath(library))
    try:
        inside = paths.commonpath([root, candidate]) == root
    except ValueError:      # 不同盘符
        inside = False
    if not inside:
        raise RuntimeError(f"llvm-config retained a dependency outside the SDK: {library}")
```

Windows 用 `ntpath` 而非 `posixpath`，且处理了跨盘符 `ValueError`——两处都是平台相关的真实坑。

### 7. 拒绝共享库与不可重定位的 pkg-config

```python
for path in prefix.rglob("*"):
    if path.is_file() and (path.suffix in (".so", ".dll", ".dylib") or ".so." in path.name):
        raise RuntimeError(f"SDK unexpectedly contains a shared library: {path}")
for path in (prefix / "lib" / "pkgconfig").glob("*.pc"):
    if "prefix=${pcfiledir}/../.." not in path.read_text(encoding="utf-8"):
        raise RuntimeError(f"pkg-config metadata is not relocatable: {path}")
```

### 8. 两种链接方式各构建一次

```python
link_modes = ["cmake", "llvm-config"]
if platform.system() == "Windows":
    link_modes.append("whole-archive")
```

- `cmake`：走导入目标 `find_package(LLVM CONFIG)`；
- `llvm-config`：走 `--libfiles --system-libs` 的裸旗标；
- `whole-archive`（仅 Windows）：用 `/WHOLEARCHIVE` 强制拉入每个归档成员。

### 9. 运行探针

```python
run([sys.executable, "-c", """
import ctypes, sys
probe = ctypes.CDLL(sys.argv[1])
probe.mlc_llvm_probe.restype = ctypes.c_int
result = probe.mlc_llvm_probe()
if result != 42:
    raise SystemExit(f"LLVM consumer returned {result}, expected 42")
""", library])
```

用子进程是必要的：Windows 上已加载的 DLL 无法删除，若在当前进程加载会阻塞 `TemporaryDirectory` 清理（代码注释明确说明）。

## 第三层：探针做了什么

`verify/main.cpp` 的 `mlc_llvm_probe()` 是一条完整的 LLVM 使用路径（F-147 相关）：

```text
① mlc_llvm_check_dependencies()   — 压缩与 DWARF 依赖自检
② InitializeNativeTarget / AsmPrinter
③ LLJITBuilder().create()          — 建 JIT
④ parseIR("define i32 @answer() { ret i32 42 }")
⑤ module->setDataLayout / setTargetTriple
⑥ Linker::linkModules(module, empty)
⑦ PassBuilder + O2 默认管线
⑧ WriteBitcodeToFile
⑨ LLJIT.addIRModule + lookup("answer") + 调用
   返回 42
```

错误码是分段的（-1 ~ -8），任何一个环节失败都能从返回值定位。这种"用返回值编码失败点"的手法在 C++ 探针里很实用。

### 依赖自检：真的解压一遍

`verify/dependencies.cpp` 不是"检查库存在"，而是**构造数据走完整路径**：

1. `compression::compress` / `decompress` 对 4096 字节数据做往返；
2. 对无效流断言解压**必须报错**（防止"静默成功"）；
3. 手工拼一个 ELF 目标文件，其 `.debug_info` 节带 `SHF_COMPRESSED` 标志，压缩格式分别为 zlib 与 zstd；
4. 用 `ObjectFile::createObjectFile` 打开，扫描 `section.isCompressed()`；
5. 用 `DWARFContext::create` 解析，断言恰好一个编译单元、DIE 名为 `sdk-probe`。

第 3 步的关键在于"手工拼 ELF"而不是调用外部工具：这样在 macOS/Windows 上也能跑同一段代码，不需要交叉编译器或宿主 LLVM 工具（注释明确说明）。

### 符号与 ABI 检查

```python
if system == "Linux":
    symbols = run(["nm", "-D", "--defined-only", "--format=posix", library], capture=True)
elif system == "Darwin":
    symbols = run(["nm", "-gUj", library], capture=True)
else:
    symbols = run(["dumpbin", "/EXPORTS", library], capture=True)
expected = "_mlc_llvm_probe" if system == "Darwin" else "mlc_llvm_probe"
allowed = {expected}
if system == "Windows":
    allowed.update({"__jit_debug_descriptor", "__jit_debug_register_code"})
exports = exported_symbols(symbols, system)
if expected not in exports or exports - allowed:
    raise RuntimeError(f"Consumer exposes unexpected symbols:\n{symbols}")
```

三个平台三种工具，但断言是同一个：**除了自己的 API，不导出任何符号**。Windows 的两个例外来自 LLVM 的 `LLVM_ALWAYS_EXPORT`（`OrcTargetProcess/JITLoaderGDB.cpp` 把 `/EXPORT` 指令嵌进了归档成员）——这是"无法通过链接选项消除"的例外，只能显式登记。

ABI 上限检查（F-148）：

```python
for namespace, maximum in (("GLIBC", (2, 28)), ("GLIBCXX", (3, 4, 24)),
                           ("CXXABI", (1, 3, 11)), ("GCC", (7, 0, 0))):
    versions = re.findall(r"\b" + namespace + r"_([0-9.]+)", output)
    for version in versions:
        if tuple(map(int, version.split("."))) > maximum:
            raise RuntimeError(f"{path.name} requires {namespace}_{version}, above manylinux_2_28")
```

注意检查对象是**链接后的消费者**，不是归档文件名——这才是"实际运行需要什么"的证据。

### CMake 侧的静态性断言

`verify/CMakeLists.txt` 做了四组断言（F-149 ~ F-151）：

```cmake
# 1) 版本匹配
if(NOT LLVM_PACKAGE_VERSION VERSION_EQUAL MLC_LLVM_EXPECTED_VERSION)
  message(FATAL_ERROR "Unexpected LLVM version: ${LLVM_PACKAGE_VERSION}")
endif()

# 2) 每个可用库都是 STATIC 或 INTERFACE
foreach(name IN LISTS LLVM_AVAILABLE_LIBS)
  if(NOT TARGET "${name}")
    message(FATAL_ERROR "Missing LLVM export: ${name}")
  endif()
  get_target_property(kind "${name}" TYPE)
  if(NOT kind STREQUAL "STATIC_LIBRARY" AND NOT kind STREQUAL "INTERFACE_LIBRARY")
    message(FATAL_ERROR "Unexpected non-static LLVM export: ${name} (${kind})")
  endif()
endforeach()

# 3) 每个导入位置都在前缀内
cmake_path(IS_PREFIX expected "${actual}" NORMALIZE inside)
if(NOT inside)
  message(FATAL_ERROR "${name} resolves outside the SDK: ${actual}")
endif()

# 4) 可选依赖必须全部关闭
foreach(feature LLVM_ENABLE_LIBXML2 LLVM_ENABLE_LIBEDIT LLVM_ENABLE_FFI
    LLVM_WITH_Z3 LLVM_ENABLE_CURL LLVM_ENABLE_HTTPLIB LLVM_ENABLE_DIA_SDK)
  if(${feature})
    message(FATAL_ERROR "Unexpected optional dependency enabled: ${feature}")
  endif()
endforeach()
```

第 3 条对 `ZLIB::ZLIB` 与 `zstd::libzstd_static` 也适用——这正是"防止 `find_package(ZLIB)` 命中系统 zlib"的机械检查。`DEPENDENCIES.md` 指出当前导出的确会调用 `find_package(ZLIB)`/`find_package(zstd)`，可能复用系统包；这条断言把风险变成红灯。

### 跨目标验证

`verify/targets/targets.cpp`（F-152）对每个传入 triple：

```cpp
llvm::InitializeAllTargetInfos();
llvm::InitializeAllTargets();
llvm::InitializeAllTargetMCs();
llvm::InitializeAllAsmPrinters();
llvm::InitializeAllAsmParsers();
llvm::InitializeAllDisassemblers();
...
if ((*object)->getArch() != triple.getArch()) return 6;
if (triple.isOSBinFormatELF() && !(*object)->isELF()) return 8;
if (triple.isOSBinFormatCOFF() && !(*object)->isCOFF()) return 9;
if (triple.isOSBinFormatMachO() && !(*object)->isMachO()) return 10;
if (triple.isOSBinFormatWasm() && !(*object)->isWasm()) return 11;
```

`verify_split_wheels.py` 的 all 档传入六个 triple：

```python
triples = ["x86_64-unknown-linux-gnu", "aarch64-unknown-linux-gnu",
           "riscv64-unknown-linux-gnu", "wasm32-unknown-unknown",
           "x86_64-pc-windows-msvc", "aarch64-apple-macosx14.0.0"]
```

注释强调：这些调用会展开生成的 profile 头文件，因此"profile/库不匹配必须导致链接失败，即使宿主 JIT 本身能工作"。

## 第四层：四态安装矩阵

`verify_split_wheels.py` 的序列已在[分片](06-split-sdk-partitioning.md)说明，这里强调它验证的是**转移**而非静态状态：

| 步骤 | 被验证的转移 |
|---|---|
| 只装 base → 断言 native | 初始态 |
| 装 extra → 断言 all | 安装触发切换 |
| 显式 native → 断言仍可链接 | 显式覆盖优先于安装态 |
| 卸载 extra → 断言回 native | 卸载触发回退 |

第三步最容易漏。它的存在证明"装了 add-on 也能退回 native"，而这依赖于头文件派发器与 CMake 分支都对 `MLC_LLVM_STATIC_PROFILE` 敏感。

## 三个包的验证差异

| 包 | 验证重点 | 不验证什么 |
|---|---|---|
| llvm | 静态链接、符号、ABI、跨目标代码生成、四态 profile | 不执行跨架构机器码（只生成目标文件） |
| z3 | 消费者不链动态 `libz3` | 不做符号泄漏检查 |
| doxygen | 三条调用通路 + 真实生成 HTML | 不校验文档输出内容正确性 |

## 自检方式

```bash
# 1) 不需要真实 LLVM 的快速验证
pytest packages/mlc-llvm-static/tests/python -q

# 2) 安装后完整验证（需要已装 wheel 与 C++ 编译器）
python packages/mlc-llvm-static/scripts/verify_wheel.py

# 3) 四态矩阵（需要 wheelhouse）
python packages/mlc-llvm-static/scripts/verify_split_wheels.py wheelhouse

# 4) ABI 上限（Linux）
readelf --version-info $(python -c "import mlc_llvm_static as s; print(s.get_prefix())")/lib/libLLVMCore.a 2>/dev/null | head

# 5) 符号导出（Linux）
nm -D --defined-only <consumer.so> | head
```

## 陷阱

- **验证脚本本身不构建 LLVM**：`verify_wheel.py` 需要已安装的 wheel，`verify_split_wheels.py` 需要已构建的 wheelhouse。
- **不要在 Windows 当前进程加载探针 DLL**：会阻塞临时目录清理。
- **`nm -gUj` 只在 macOS 有效**：Linux 参数不同，跨平台脚本要分支。
- **ABI 上限检查依赖 `readelf`**：Windows/macOS 上直接跳过，不是失败。
- **不要用"归档齐全"替代链接验证**：静态链接的顺序错误只有在真正链接时才暴露。

## 延伸阅读

- 分片设计与四态语义：[SDK 分片](06-split-sdk-partitioning.md)
- profile 三处派发：[profile 选择与派发](07-profile-selection.md)
- 依赖审计的完整表格：[依赖审计要点](../references/02-dependency-audit.md)
