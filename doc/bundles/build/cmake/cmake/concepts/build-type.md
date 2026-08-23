---
type: concept
title: "构建类型与多配置"
description: "CMAKE_BUILD_TYPE 与多配置生成器（VS/Xcode/Ninja Multi-Config）的区别，Debug/Release/RelWithDebInfo/MinSizeRel 四种标准配置"
sources:
  references: [../references/cmglobalgenerator.md, ../references/cmmakefile.md]
  facts: [F-056, F-091]
---

# 构建类型与多配置

## 核心理解

CMake 支持两种构建配置模式：**单配置（Single-Config）**和**多配置（Multi-Config）**。这由生成器决定，影响整个构建流程。

| 特性 | 单配置生成器 | 多配置生成器 |
|------|------------|------------|
| 生成器 | Ninja, Unix Makefiles, MinGW Makefiles | Visual Studio, Xcode, Ninja Multi-Config |
| 配置选择时机 | Configure 时（`-DCMAKE_BUILD_TYPE=Debug`） | Build 时（`--config Debug`） |
| 构建目录 | 每个配置一个独立目录 | 一个目录包含所有配置 |
| 配置隔离 | 完全隔离（不同 build 目录） | 共享 CMakeCache.txt，输出到子目录 |

## 四种标准构建类型

CMake 预定义了四种标准 `CMAKE_BUILD_TYPE`：

| 类型 | 编译标志（GCC/Clang） | 用途 |
|------|---------------------|------|
| `Debug` | `-g`（调试信息，无优化） | 开发调试 |
| `Release` | `-O3 -DNDEBUG`（最高优化，无调试信息） | 发布版本 |
| `RelWithDebInfo` | `-O2 -g -DNDEBUG`（优化+调试信息） | 发布但可调试 |
| `MinSizeRel` | `-Os -DNDEBUG`（最小体积优化） | 嵌入式/空间受限 |

每种类型的标志存储在缓存变量中：
- `CMAKE_C_FLAGS_<TYPE>` / `CMAKE_CXX_FLAGS_<TYPE>` — C/C++ 编译标志
- `CMAKE_EXE_LINKER_FLAGS_<TYPE>` — 可执行文件链接标志
- `CMAKE_SHARED_LINKER_FLAGS_<TYPE>` — 共享库链接标志

## 单配置生成器用法

```bash
# Configure 时指定构建类型
cmake -S . -B build-debug -DCMAKE_BUILD_TYPE=Debug
cmake -S . -B build-release -DCMAKE_BUILD_TYPE=Release

# 分别构建
cmake --build build-debug
cmake --build build-release

# 输出在对应构建目录下
# build-debug/myapp
# build-release/myapp
```

```cmake
# CMakeLists.txt 中设置默认构建类型（如果用户未指定）
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS
    Debug Release RelWithDebInfo MinSizeRel)
endif()
```

## 多配置生成器用法

```bash
# Configure 时不需要指定 CMAKE_BUILD_TYPE（指定了也会被忽略）
cmake -S . -B build -G "Visual Studio 17 2022"
cmake -S . -B build -G "Xcode"
cmake -S . -B build -G "Ninja Multi-Config"

# Build 时通过 --config 指定
cmake --build build --config Debug
cmake --build build --config Release

# 输出在配置子目录下
# build/Debug/myapp.exe
# build/Release/myapp.exe
```

## CMAKE_CONFIGURATION_TYPES

多配置生成器使用 `CMAKE_CONFIGURATION_TYPES` 指定可用配置列表：

```cmake
# 默认可用配置
set(CMAKE_CONFIGURATION_TYPES "Debug;Release;RelWithDebInfo;MinSizeRel" CACHE STRING "")

# 自定义配置（如添加 Sanitize 配置）
list(APPEND CMAKE_CONFIGURATION_TYPES Sanitize)
set(CMAKE_C_FLAGS_SANITIZE "-fsanitize=address -g -O1" CACHE STRING "")
set(CMAKE_CXX_FLAGS_SANITIZE "-fsanitize=address -g -O1" CACHE STRING "")
```

单配置生成器忽略此变量，使用 `CMAKE_BUILD_TYPE`。

## 输出目录与配置

多配置下，输出自动按配置分子目录：

```cmake
# 单配置
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
# → build/bin/myapp

# 多配置（自动添加 Debug/Release 子目录）
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
# → build/bin/Debug/myapp.exe
# → build/bin/Release/myapp.exe

# 使用生成器表达式在多配置中控制输出
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY $<1:${CMAKE_BINARY_DIR}/bin>)
```

## 生成器表达式与配置

当代码需要区分配置时，使用生成器表达式：

```cmake
target_compile_definitions(myapp PRIVATE
  $<$<CONFIG:Debug>:DEBUG_BUILD>          # Debug: 定义 DEBUG_BUILD
  $<$<CONFIG:Release>:NDEBUG RELEASE>     # Release: 定义 NDEBUG RELEASE
)

target_link_libraries(myapp PRIVATE
  $<$<CONFIG:Debug>:debug-helper-lib>     # 仅 Debug 链接
)

# 多配置通用
add_custom_command(TARGET myapp POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy
    $<TARGET_FILE:myapp>
    ${CMAKE_BINARY_DIR}/output/$<CONFIG>/myapp
)
```

## 检查当前配置类型

```cmake
# 单配置：直接检查 CMAKE_BUILD_TYPE
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
  message(STATUS "Debug build")
endif()

# ⚠️ 多配置：Configure 时 CMAKE_BUILD_TYPE 为空！
# 在 CMakeLists.txt 中不要依赖 CMAKE_BUILD_TYPE 判断多配置！

# 兼容写法：使用生成器表达式或在 add_custom_command 中判断
if(CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Multi-config generator: ${CMAKE_CONFIGURATION_TYPES}")
else()
  message(STATUS "Single-config generator, build type: ${CMAKE_BUILD_TYPE}")
endif()
```

## 常见问题

### 问题 1：忘记设置 CMAKE_BUILD_TYPE

单配置生成器不设置 `CMAKE_BUILD_TYPE` 时，编译标志为空（无 `-g`、无 `-O2`），导致既慢又无法调试。

解决方案：在顶层 CMakeLists.txt 中设置默认值：

```cmake
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE "RelWithDebInfo" CACHE STRING "Choose build type" FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS
    "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()
```

### 问题 2：单配置生成器误设 CMAKE_CONFIGURATION_TYPES

```cmake
# ❌ 错误：在 Ninja/Makefile 上设置配置列表
set(CMAKE_CONFIGURATION_TYPES Debug Release)  # 不生效
# ✅ 正确：使用 CMAKE_BUILD_TYPE
set(CMAKE_BUILD_TYPE Debug CACHE STRING "")
```

### 问题 3：install() 在多配置下的路径

```cmake
# install 的 CONFIGURATIONS 参数
install(TARGETS myapp DESTINATION bin CONFIGURATIONS Release)
install(TARGETS myapp DESTINATION bin/debug CONFIGURATIONS Debug)
```

## 关联概念

- [多生成器工厂模式](generator-pattern.md) — 生成器决定单/多配置
- [目标模型](target-model.md) — 生成器表达式在目标属性中的使用
- [配置-生成两阶段](configure-generate.md) — 配置类型在 Generate 阶段确定编译命令
