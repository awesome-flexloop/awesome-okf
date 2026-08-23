---
type: example
title: "跨平台构建与 find_package"
description: "跨 Linux/macOS/Windows 项目配置，find_package 查找第三方依赖，平台条件判断，工具链文件示例"
sources:
  concepts: [../concepts/find-module.md, ../concepts/generator-pattern.md, ../concepts/build-type.md, ../concepts/toolchain-detection.md]
  references: [../references/cmdexec.md]
---

# 跨平台构建与 find_package

## 目标

构建一个跨平台（Linux/macOS/Windows）应用，使用多个第三方依赖（fmt、Boost、ZLIB），演示：
- 平台/编译器条件判断
- find_package Module/Config 模式
- 导入目标（Imported Targets）使用
- 平台特定源文件和链接库
- 工具链文件交叉编译

## 项目结构

```
network_tool/
├── CMakeLists.txt
├── cmake/
│   └── toolchain-aarch64.cmake    # 交叉编译工具链
├── include/
│   └── nettool/
│       └── client.h
├── src/
│   ├── client.cpp
│   ├── client_linux.cpp           # Linux 平台特定实现
│   ├── client_macos.cpp           # macOS 平台特定实现
│   └── client_win.cpp             # Windows 平台特定实现
└── app/
    └── main.cpp
```

## 完整 CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.20)
project(NetworkTool VERSION 1.0.0 LANGUAGES CXX)

# ── 全局设置 ──
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE RelWithDebInfo CACHE STRING "" FORCE)
endif()

# 输出目录统一
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# ── 第三方依赖 ──

# fmt: 使用 Config 模式（现代库通常提供 Config 文件）
find_package(fmt 9.0 REQUIRED CONFIG)
# 导入目标：fmt::fmt（header-only 是 fmt::fmt-header-only）

# Boost: Module 模式（CMake 内置 FindBoost.cmake）
find_package(Boost 1.70 REQUIRED COMPONENTS system filesystem)
# 导入目标：Boost::system, Boost::filesystem, Boost::boost（header-only）

# ZLIB: Module 模式
find_package(ZLIB REQUIRED)
# 导入目标：ZLIB::ZLIB

# 可选依赖：OpenSSL
find_package(OpenSSL QUIET)
if(OpenSSL_FOUND)
  set(NETTOOL_HAS_SSL ON)
endif()

# ── 平台特定设置 ──

# 操作系统判断
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
  set(NETTOOL_PLATFORM "Linux")
  set(PLATFORM_SOURCES src/client_linux.cpp)
  set(PLATFORM_LIBS pthread)  # Linux 需要显式链接 pthread
elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
  set(NETTOOL_PLATFORM "macOS")
  set(PLATFORM_SOURCES src/client_macos.cpp)
  set(PLATFORM_LIBS "-framework CoreFoundation -framework Security")
elseif(CMAKE_SYSTEM_NAME STREQUAL "Windows")
  set(NETTOOL_PLATFORM "Windows")
  set(PLATFORM_SOURCES src/client_win.cpp)
  set(PLATFORM_LIBS ws2_32 Iphlpapi)  # Windows Socket 库
endif()

message(STATUS "Building for ${NETTOOL_PLATFORM}")

# 编译器判断
if(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
  add_compile_options(/W4 /permissive- /utf-8)
  add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
else()
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# ── 核心库 ──
add_library(nettool)

target_sources(nettool PRIVATE
  src/client.cpp
  ${PLATFORM_SOURCES}    # 平台特定源文件
)

target_include_directories(nettool PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

target_compile_definitions(nettool PRIVATE
  NETTOOL_PLATFORM_${NETTOOL_PLATFORM}=1
)
if(NETTOOL_HAS_SSL)
  target_compile_definitions(nettool PUBLIC NETTOOL_HAS_SSL=1)
endif()

# 链接依赖（使用导入目标，自动传递 include/flags）
target_link_libraries(nettool
  PUBLIC
    Boost::system
    ZLIB::ZLIB
  PRIVATE
    fmt::fmt
    Boost::filesystem
    ${PLATFORM_LIBS}
)
if(OpenSSL_FOUND)
  target_link_libraries(nettool PRIVATE OpenSSL::SSL OpenSSL::Crypto)
endif()

# 别名
add_library(NetTool::nettool ALIAS nettool)

# ── 可执行文件 ──
add_executable(nettool_app app/main.cpp)
target_link_libraries(nettool_app PRIVATE NetTool::nettool)
set_target_properties(nettool_app PROPERTIES OUTPUT_NAME nettool)

# ── 安装与包配置 ──
include(GNUInstallDirs)
install(TARGETS nettool nettool_app
  EXPORT NetToolTargets
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
  FILES_MATCHING PATTERN "*.h")

# 导出目标供下游 find_package 使用
install(EXPORT NetToolTargets
  FILE NetToolTargets.cmake
  NAMESPACE NetTool::
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/NetTool
)
```

## 平台特定源文件示例

### src/client_linux.cpp

```cpp
#include "nettool/client.h"
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

namespace nettool {
bool Client::connectImpl(const std::string& host, int port) {
  // Linux epoll/socket 实现
  int sock = socket(AF_INET, SOCK_STREAM, 0);
  // ...
  return true;
}
}
```

### src/client_win.cpp

```cpp
#include "nettool/client.h"
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")

namespace nettool {
bool Client::connectImpl(const std::string& host, int port) {
  WSADATA wsa;
  WSAStartup(MAKEWORD(2, 2), &wsa);
  SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
  // ...
  return true;
}
}
```

## BUILD_INTERFACE / INSTALL_INTERFACE 生成器表达式

```cmake
target_include_directories(nettool PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
```

这是跨构建/安装路径的关键技巧：
- **构建时**（`cmake --build build`）：头文件路径指向源码目录 `include/`
- **安装后**（`find_package(NetTool)`）：头文件路径指向安装位置 `include/`

生成器表达式 `$<...>` 在 Generate 阶段求值，确保两种场景路径都正确。

## GNUInstallDirs

`include(GNUInstallDirs)` 提供平台标准安装路径变量：

| 变量 | Linux 默认值 | Windows 默认值 |
|------|------------|--------------|
| `CMAKE_INSTALL_BINDIR` | `bin` | `bin` |
| `CMAKE_INSTALL_LIBDIR` | `lib` / `lib64` | `lib` |
| `CMAKE_INSTALL_INCLUDEDIR` | `include` | `include` |
| `CMAKE_INSTALL_DATADIR` | `share` | `share` |

避免硬编码 `lib`（64 位系统可能是 `lib64`）。

## 构建命令

### 本地构建（Linux/macOS）

```bash
# 使用 Ninja（推荐）
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)

# 使用 Unix Makefiles
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j$(nproc)
```

### Windows (Visual Studio)

```powershell
# VS 2022
cmake -S . -B build -G "Visual Studio 17 2022" -A x64
cmake --build build --config Release -- /m

# MSVC + Ninja（更快速）
# 先从 VS Developer Command Prompt 运行
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

### macOS (Xcode)

```bash
cmake -S . -B build -G Xcode
cmake --build build --config Release
```

## 交叉编译：ARM64 Linux 工具链

### cmake/toolchain-aarch64.cmake

```cmake
# 目标系统
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

# 交叉编译器
set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)

# 根文件系统（sysroot）
set(CMAKE_SYSROOT /usr/aarch64-linux-gnu)
set(CMAKE_FIND_ROOT_PATH /usr/aarch64-linux-gnu)

# 搜索路径配置
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)   # 不在 sysroot 查找主机程序
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)    # 库仅在 sysroot 查找
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)    # 头文件仅在 sysroot 查找
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)    # CMake 包仅在 sysroot 查找
```

### 交叉编译命令

```bash
cmake -S . -B build-arm64 \
  --toolchain cmake/toolchain-aarch64.cmake \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build-arm64
# 产物为 ARM64 二进制
file build-arm64/bin/nettool
# build-arm64/bin/nettool: ELF 64-bit LSB executable, ARM aarch64, ...
```

## find_package 常见问题排查

### 找不到 fmt（Config 模式）

```bash
# 方法 1：设置 CMAKE_PREFIX_PATH
cmake -S . -B build -DCMAKE_PREFIX_PATH=/path/to/fmt/install

# 方法 2：设置 <Package>_DIR
cmake -S . -B build -Dfmt_DIR=/path/to/fmt/lib/cmake/fmt

# 方法 3：查看详细搜索日志
cmake -S . -B build --debug-find-pkg=fmt
```

### 找不到 Boost（Module 模式）

```bash
# Boost 安装到非标准路径
cmake -S . -B build \
  -DBOOST_ROOT=/path/to/boost \
  -DBoost_NO_SYSTEM_PATHS=ON \
  -DBoost_DEBUG=ON  # 开启调试输出
```

### Windows 上 ZLIB 找不到

```powershell
cmake -S . -B build `
  -DZLIB_ROOT="C:\path\to\zlib" `
  -DZLIB_INCLUDE_DIR="C:\path\to\zlib\include" `
  -DZLIB_LIBRARY="C:\path\to\zlib\lib\zlib.lib"
```

## 验证平台检测

```bash
# 构建后查看平台宏
grep -r "NETTOOL_PLATFORM" build/CMakeCache.txt
# NETTOOL_PLATFORM:STRING=Linux (或 Darwin/Windows)

# 运行
./build/bin/nettool
# [Linux] NetworkTool v1.0.0 running on Linux
```

## 延伸阅读

- [查找模块机制](../concepts/find-module.md) — Config vs Module 模式详解
- [多生成器工厂模式](../concepts/generator-pattern.md) — 不同平台的生成器选择
- [构建类型与多配置](../concepts/build-type.md) — 单/多配置平台差异
- [工具链检测与语言启用](../concepts/toolchain-detection.md) — 交叉编译原理
- [现代 CMake 目标使用](modern-targets.md) — PUBLIC/PRIVATE 传播规则
