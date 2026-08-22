---
type: reference
title: "cmCommand：CMake 命令执行体系"
description: "cmCommand 基类、命令参数解析、执行流程与内置命令注册机制的信源登记"
sources:
  - path: "external/libs/tools/CMake/Source/cmCommand.h"
    facts: [F-068, F-069, F-070, F-071, F-072, F-073, F-074, F-078]
  - path: "external/libs/tools/CMake/Source/cmCommand.cxx"
    facts: [F-075, F-076, F-077]
  - path: "external/libs/tools/CMake/Source/cmCommands.cxx"
    facts: [F-079, F-080, F-081, F-082]
---

# cmCommand：CMake 命令执行体系

## 信源概述

| 信源 | 类型 | 核心职责 |
|------|------|----------|
| `Source/cmCommand.h` | 头文件 | cmCommand 基类声明、命令参数结构 |
| `Source/cmCommand.cxx` | 实现文件 | 命令基类通用逻辑 |
| `Source/cmCommands.cxx` | 实现文件 | 内置命令注册入口 `GetPredefinedCommands()` |

## 关键事实登记

### F-068：cmCommand 是所有内置命令的基类

**信源**：`Source/cmCommand.h`

```cpp
class cmCommand {
public:
  virtual ~cmCommand() = default;
  virtual std::unique_ptr<cmCommand> Clone() = 0;
  virtual bool InitialPass(std::vector<std::string> const& args,
                           cmExecutionStatus& status) = 0;
  virtual std::string GetName() const = 0;
  virtual bool IsScriptable() const { return true; }
  // ...
  cmMakefile* Makefile;
};
```

每个 CMake 命令（`if`、`set`、`add_executable` 等）都继承 `cmCommand` 并实现 `InitialPass`。

### F-069：命令通过 Clone 模式执行

**信源**：`Source/cmCommand.h`

`cmMakefile` 持有命令原型（prototype）注册表，每次执行命令时先 `Clone()` 创建一个新实例，设置 `Makefile` 指针后调用 `InitialPass()`。

### F-070：cmExecutionStatus 控制执行流

**信源**：`Source/cmCommand.h`

```cpp
class cmExecutionStatus {
  bool ReturnInvoked = false;
  bool BreakInvoked = false;
  bool ContinueInvoked = false;
  bool NestingError = false;
  // ...
};
```

`return()`、`break()`、`continue()` 命令通过设置 status 标志位控制 `cmMakefile::ExecuteCommand` 的执行流。

### F-071：命令参数为 std::string 数组

**信源**：`Source/cmCommand.h`

`InitialPass` 接收 `std::vector<std::string> const& args`，即已经过分词但未解析的原始参数列表。各命令自行负责参数解析（使用 `cmArgumentParser` 或手动解析）。

### F-072：Scriptable vs Builtin 命令

**信源**：`Source/cmCommand.h`

- `IsScriptable() const { return true; }` — 默认可在脚本模式（`-P`）中使用
- 某些命令（如 `project()`、`add_executable()`）重写返回 `false`，只能在 CMakeLists.txt 构建配置中使用

### F-073：cmMakefile::ExecuteCommand 执行单个命令

**信源**：`Source/cmMakefile.cxx`

执行流程：
1. 根据命令名从命令注册表查找原型
2. Clone 原型 → 设置 Makefile
3. 调用 `InitialPass(args, status)`
4. 处理 Return/Break/Continue 状态
5. 返回 bool 表示成功/失败

### F-074：命令分为 Builtin 和 Scripted 两类

**信源**：`Source/` 目录结构

- **Builtin 命令**：C++ 实现，位于 `Source/cm*Command.cxx`（如 `cmSetCommand.cxx`、`cmIfCommand.cxx`）
- **Scripted 命令**：CMake 模块实现（如 `Find*.cmake`），通过 function/macro 定义

### F-079：GetPredefinedCommands 注册所有内置命令

**信源**：`Source/cmCommands.cxx`

`void GetPredefinedCommands(std::list<std::unique_ptr<cmCommand>>& commands);`

在此函数中逐个 `commands.emplace_back(new cmXxxCommand)` 注册所有内置命令（约 100+ 个）。

### F-080：内置命令覆盖范围

**信源**：`Source/cmCommands.cxx`

| 类别 | 代表命令 | 文件命名模式 |
|------|----------|-------------|
| 脚本控制 | `if`, `else`, `foreach`, `while`, `function`, `macro`, `return`, `break`, `continue` | `cmIfCommand.cxx` |
| 变量操作 | `set`, `unset`, `list`, `string`, `math` | `cmSetCommand.cxx` |
| 目标定义 | `add_executable`, `add_library`, `add_custom_target` | `cmAddExecutableCommand.cxx` |
| 构建规则 | `target_link_libraries`, `target_include_directories`, `target_compile_options` | `cmTarget*Command.cxx` |
| 查找模块 | `find_package`, `find_library`, `find_path`, `find_program`, `find_file` | `cmFind*Command.cxx` |
| 安装 | `install`, `install(FILES|PROGRAMS|DIRECTORY|TARGETS)` | `cmInstallCommand.cxx` |
| 文件操作 | `file`, `configure_file`, `file(GLOB)` | `cmFileCommand.cxx` |
| 包含 | `include`, `add_subdirectory`, `include_guard` | `cmIncludeCommand.cxx` |
| 测试 | `enable_testing`, `add_test` | `cmAddTestCommand.cxx` |
| 属性 | `set_property`, `set_target_properties`, `set_source_files_properties` | `cmSetPropertyCommand.cxx` |
| 消息 | `message`, `cmake_minimum_required`, `project` | `cmMessageCommand.cxx` |
| 策略 | `cmake_policy` | `cmCMakePolicyCommand.cxx` |
| 自定义命令 | `add_custom_command`, `add_custom_target` | `cmAddCustomCommandCommand.cxx` |

### F-081：模块路径搜索遵循固定顺序

**信源**：`Source/cmMakefile.cxx`

`include()` 和 `find_package()` 搜索模块路径顺序：
1. `CMAKE_MODULE_PATH` 中的目录
2. `CMAKE_ROOT/Modules/` 内置模块目录

### F-082：Find 命令使用 Config/Module 双模式

**信源**：`Source/cmFindPackageCommand.cxx`

`find_package(Xxx)` 按顺序查找：
1. Module 模式：查找 `FindXxx.cmake`（用户编写或内置）
2. Config 模式：查找 `XxxConfig.cmake` / `xxx-config.cmake`（包安装时提供）
