---
type: concept
title: "工作模式与工具链分发"
description: "cmake::WorkingMode 枚举定义的 7 种执行模式，以及 ctest/cpack 工具链的统一分发机制"
sources:
  references: [../references/cmake-class.md, ../references/ctest-cpack.md]
  facts: [F-002, F-007, F-098, F-107]
---

# 工作模式与工具链分发

## 核心理解

CMake 套件实际上包含三个独立的可执行程序，但共享同一套代码基础：

| 可执行文件 | 入口 | 核心功能 |
|-----------|------|---------|
| `cmake` | `Source/cmakemain.cxx` → `cmake::Run()` | Configure + Generate（默认模式） |
| `ctest` | `Source/ctest.cxx` → `cmCTest` | 测试驱动与 CDash 上报 |
| `cpack` | `Source/cpack.cxx` → `cmCPackGenerator` | 安装包生成 |

`cmake` 程序本身通过 `WorkingMode` 枚举支持 7 种工作模式。

## cmake 的 7 种 WorkingMode

```cpp
// cmake.h
enum class WorkingMode {
  NORMAL,       // 标准模式：Configure + Generate
  FIND_PACKAGE, // --find-package：pkg-config 兼容模式
  HELP,         // 帮助输出（--help, --help-command 等）
  VERSION,      // 版本输出（--version）
  SCRIPT,       // 脚本模式（-P script.cmake）
  SERVER,       // CMake Server 模式（IDE 通信协议）
  OPEN          // Open 模式（打开已有构建目录）
};
```

### NORMAL 模式（默认）

这是最常用的模式，执行完整的 Configure + Generate 两阶段流程：

```bash
# 标准构建配置
cmake -S . -B build -G Ninja
cmake --build build
```

Run() 方法中的执行路径：
1. 解析 `-S`（源码目录）、`-B`（构建目录）、`-G`（生成器）参数
2. 调用 `SetHomeDirectory()` / `SetHomeOutputDirectory()`
3. 调用 `CreateGlobalGenerator()` 创建生成器
4. 调用 `Configure()` 执行 CMakeLists.txt
5. 调用 `Generate()` 输出构建文件

### SCRIPT 模式（-P）

不执行 Configure/Generate，直接运行一个 CMake 脚本文件：

```bash
cmake -P myscript.cmake
```

特点：
- **无构建目录**要求，不需要 CMakeLists.txt
- 不可使用构建类命令（`add_executable`、`project` 等，这些 IsScriptable() 返回 false）
- 支持所有脚本类命令（`message`、`set`、`if/foreach/while`、`file`、`math`、`string`、`list`、`execute_process` 等）
- 常用于 CI 脚本、文件操作、文本处理

### HELP 模式

输出各种帮助信息：

```bash
cmake --help              # 总帮助
cmake --help-command set  # 特定命令帮助
cmake --help-module FindBoost  # 模块帮助
cmake --help-property     # 属性列表
cmake --help-variable     # 变量列表
cmake --help-generator    # 生成器列表
```

### VERSION 模式

```bash
cmake --version
# 输出：cmake version 3.x.x
```

### FIND_PACKAGE 模式

`--find-package` 是兼容 pkg-config 的查询模式，用于外部构建系统查询已安装的 CMake 包信息：

```bash
cmake --find-package -DNAME=Boost -DCOMPILER_ID=GNU -DLANGUAGE=CXX -DMODE=EXIST
```

这是一个遗留模式，现代项目应直接使用 `find_package()` 在 CMakeLists.txt 中。

### SERVER 模式

CMake Server 是 IDE 集成使用的通信协议，通过 JSON over stdin/stdout 进行通信：

```bash
cmake -E server --debug
# > {"type":"handshake","sourceDirectory":"/path/to/src","buildDirectory":"/path/to/build","generator":"Ninja"}
# < {"type":"reply","cookie":"...","inReplyTo":"handshake"}
```

支持的操作：configure、compute、codemodel、cache 等。现代 IDE 多使用 file-api 替代。

### OPEN 模式

打开一个已存在的构建目录，通常由 IDE 使用以获取 code model 信息。

## 工具链关系

```
cmake.exe (cmake.cxx)
├── -P script.cmake    → WorkingMode::SCRIPT（脚本执行）
├── --find-package     → WorkingMode::FIND_PACKAGE
├── --help / --version → HELP / VERSION
├── -E server          → SERVER（IDE 通信）
└── (默认)             → NORMAL（Configure + Generate）

ctest.exe (ctest.cxx)
├── (默认)             → 运行测试
├── -N                 → 列出测试
├── -R/-E              → 过滤测试
└── -D Experimental    → CDash 完整 Dashboard

cpack.exe (cpack.cxx)
├── (默认)             → 生成所有 CPACK_GENERATOR 指定的包
├── -G DEB             → 指定生成器
└── -C Debug           → 指定配置
```

## -E 模式：cmake 内置命令行工具

除了 7 种 WorkingMode，`cmake -E` 提供跨平台命令行工具：

```bash
cmake -E echo "Hello"         # 跨平台 echo
cmake -E make_directory dir   # mkdir -p
cmake -E copy src dst         # 跨平台 copy
cmake -E copy_directory src dst
cmake -E remove_directory dir # rm -rf
cmake -E tar cfz out.tar.gz dir  # 打包
cmake -E sha256sum file       # 哈希计算
cmake -E sleep 5              # 跨平台 sleep
cmake -E capabilities         # 查询 CMake 能力
```

这使得 CMake 可在 CTest/CPack 脚本中作为跨平台文件操作工具使用。

## 关联概念

- [整体架构](overall-architecture.md) — 理解 cmake 类在架构中的位置
- [配置-生成两阶段](configure-generate.md) — NORMAL 模式的核心流程
- [CTest 测试集成](ctest-integration.md)
- [CPack 打包集成](cpack-integration.md)
