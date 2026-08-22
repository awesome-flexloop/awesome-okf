---
type: concept
title: "工具链检测与语言启用"
description: "CMake EnableLanguage 流程：编译器检测、ABI 识别、编译特性探测与工具链文件的工作原理"
sources:
  references: [../references/cmglobalgenerator.md, ../references/cmmakefile.md, ../references/cmdexec.md]
  facts: [F-058, F-092]
---

# 工具链检测与语言启用

## 核心理解

CMake 的核心能力之一是**跨平台编译器检测**。`project(... LANGUAGES CXX C)` 命令触发语言启用流程：检测编译器路径、ABI 信息、编译特性（如 `-std=c++20` 支持）、默认标志等。这些信息在 Configure 阶段一次性检测完毕，供后续所有目标构建使用。

## language 启用流程

```
project(MyProject LANGUAGES CXX)
        │
        ▼
cmProjectCommand::InitialPass()
        │
        ▼
cmMakefile::EnableLanguage(["CXX"], false)
        │
        ▼
┌─────────────────────────────────────────────┐
│ 1. 确定编译器路径                             │
│    ├─ 检查 CMAKE_CXX_COMPILER 缓存变量        │
│    ├─ 如果未设置，自动检测（g++/clang++/cl）  │
│    └─ 使用工具链文件时直接使用指定路径         │
│                                              │
│ 2. 编译器标识检测                             │
│    ├─ 运行编译器获取版本信息                   │
│    ├─ 确定 CMAKE_CXX_COMPILER_ID             │
│    │   (GNU/Clang/MSVC/AppleClang/Intel...)  │
│    └─ 确定 CMAKE_CXX_COMPILER_VERSION        │
│                                              │
│ 3. ABI 检测                                  │
│    ├─ 编译测试程序确定 sizeof(void*)          │
│    ├─ 检测字节序 (big/little endian)          │
│    ├─ 检测目标架构 (x86_64/aarch64/...)      │
│    └─ 检测 libc++/libstdc++/msvcrt           │
│                                              │
│ 4. 编译特性检测                               │
│    ├─ 支持哪些 C++ 标准 (98/11/14/17/20/23) │
│    ├─ 检测编译选项 (cxx_constexpr 等)         │
│    └─ 写入 CMakeCXXCompiler.cmake            │
│                                              │
│ 5. 加载编译器配置文件                          │
│    └─ Modules/Compiler/GNU-CXX.cmake 等      │
└─────────────────────────────────────────────┘
        │
        ▼
编译器信息存入缓存变量 + cmState，后续目标使用
```

## 关键缓存变量

语言检测完成后，以下缓存变量可供使用：

| 变量 | 说明 | 示例 |
|------|------|------|
| `CMAKE_CXX_COMPILER` | C++ 编译器路径 | `/usr/bin/c++` |
| `CMAKE_CXX_COMPILER_ID` | 编译器 ID | `GNU`, `Clang`, `MSVC` |
| `CMAKE_CXX_COMPILER_VERSION` | 编译器版本 | `11.4.0` |
| `CMAKE_CXX_STANDARD_DEFAULT` | 默认 C++ 标准 | `17` |
| `CMAKE_CXX_COMPILER_LOADED` | CXX 是否已启用 | `1` |
| `CMAKE_C_COMPILER` | C 编译器路径 | `/usr/bin/cc` |
| `CMAKE_Fortran_COMPILER` | Fortran 编译器 | `/usr/bin/gfortran` |
| `CMAKE_SIZE_OF_VOID_P` | 指针大小（字节） | `8` |
| `CMAKE_SYSTEM_PROCESSOR` | 目标处理器 | `x86_64` |
| `CMAKE_SYSTEM_NAME` | 目标系统 | `Linux`, `Windows`, `Darwin` |
| `CMAKE_CXX_COMPILER_ABI` | ABI 标识 | `ELF` |

## 工具链文件（Toolchain File）

交叉编译或使用自定义编译器时，通过工具链文件指定编译器和目标平台：

```cmake
# toolchain-clang.cmake
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

set(CMAKE_C_COMPILER /usr/bin/aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER /usr/bin/aarch64-linux-gnu-g++)

set(CMAKE_FIND_ROOT_PATH /usr/aarch64-linux-gnu)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
```

使用：
```bash
cmake -S . -B build --toolchain toolchain-clang.cmake
```

工具链文件在编译器检测**之前**加载，确保 `CMAKE_CXX_COMPILER` 等变量已预设。

## 编译器标识条件判断

```cmake
# 针对不同编译器设置不同标志
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
  target_compile_options(myapp PRIVATE -Wall -Wextra -Wpedantic)
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
  target_compile_options(myapp PRIVATE -Wall -Wextra -Wpedantic)
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
  target_compile_options(myapp PRIVATE /W4 /permissive-)
endif()

# 编译器版本判断
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" AND CMAKE_CXX_COMPILER_VERSION VERSION_LESS 10)
  message(FATAL_ERROR "GCC >= 10 required")
endif()
```

生成器表达式更简洁：
```cmake
target_compile_options(myapp PRIVATE
  $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall -Wextra>
  $<$<CXX_COMPILER_ID:MSVC>:/W4>
)
```

## 编译特性检测（Compile Features）

CMake 维护一个编译器特性列表，`target_compile_features()` 自动选择正确的标准标志：

```cmake
target_compile_features(myapp PRIVATE
  cxx_std_20       # 需要 C++20
  cxx_constexpr    # 需要 constexpr 支持
  cxx_auto_type    # 需要 auto 支持
  cxx_lambdas      # 需要 lambda 支持
)
```

常见 `cxx_std_*` 特性：
- `cxx_std_98`, `cxx_std_11`, `cxx_std_14`, `cxx_std_17`, `cxx_std_20`, `cxx_std_23`

CMake 自动将 `cxx_std_20` 映射为 `-std=c++20`（GCC/Clang）或 `/std:c++20`（MSVC）。

## CMakeDetermineCompilerABI：ABI 检测

ABI 检测的核心步骤是**编译并运行测试程序**：

```cpp
// Modules/CMakeDetermineCompilerABI.cxx.in 生成的测试程序
#include <cstdio>
int main() {
  printf("sizeof(void*)=%zu\n", sizeof(void*));
  printf("endianness=%s\n", (...) ? "big" : "little");
  return 0;
}
```

编译运行后解析输出，确定：
- 指针大小（32位/64位）
- 字节序
- 目标架构
- 二进制格式（ELF/PE/Mach-O）

如果交叉编译（目标平台无法在宿主机运行），CMake 通过 CMakeTryRun 模拟或依赖工具链文件预设。

## try_compile / try_run：自定义检测

项目可以使用 `try_compile()` 和 `try_run()` 进行额外的编译器/库检测：

```cmake
# 测试编译器是否支持某个标志
include(CheckCXXCompilerFlag)
check_cxx_compiler_flag("-fsanitize=address" HAS_SANITIZE)

# 测试代码是否能编译
try_compile(HAS_FEATURE
  ${CMAKE_BINARY_DIR}/cmake_tests
  SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/test_feature.cpp
  CXX_STANDARD 20
)

# 测试代码是否能编译并运行
try_run(RUN_RESULT COMPILE_RESULT
  ${CMAKE_BINARY_DIR}/cmake_tests
  SOURCES test_code.cpp
)
```

## 常见问题

### 问题 1：编译器路径缓存后不更新

```bash
# 第一次 cmake 检测到了错误的编译器
CC=gcc-9 CXX=g++-9 cmake -S . -B build  # 错误
# 之后即使改了 CC/CXX，CMakeCache.txt 中缓存了旧路径

# 解决方案：删除缓存或指定编译器
rm build/CMakeCache.txt
CXX=clang++ cmake -S . -B build
# 或
cmake -S . -B build -DCMAKE_CXX_COMPILER=clang++
```

### 问题 2：交叉编译时 try_run 无法运行

交叉编译时 `try_run()` 不能在宿主机运行目标平台的二进制文件。需要通过工具链文件预设结果：

```cmake
set(CMAKE_CROSSCOMPILING ON)
# 预设 try_run 结果
set(RUN_RESULT_EXITCODE 0 CACHE INTERNAL "")
```

### 问题 3：多编译器并行构建

使用不同构建目录：
```bash
cmake -S . -B build-gcc -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++
cmake -S . -B build-clang -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
cmake --build build-gcc
cmake --build build-clang
```

## 关联概念

- [多生成器工厂模式](generator-pattern.md) — EnableLanguage 在 GlobalGenerator 上调用
- [配置-生成两阶段](configure-generate.md) — 工具链检测在 Configure 早期执行
- [目标模型](target-model.md) — 编译特性在 target_compile_features 中使用
- [策略系统](policy-system.md) — CMP0065/CMP0088 等策略与编译器行为相关
