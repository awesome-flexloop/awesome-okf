---
type: reference
title: "cmake 类：CMake 会话顶层门面"
description: "CMake 执行入口 cmake 类的核心 API、状态管理、执行模式与工作流程的信源登记"
sources:
  - path: "external/libs/tools/CMake/Source/cmake.h"
    facts: [F-001, F-003, F-005, F-008, F-009, F-010, F-011, F-013, F-014, F-017, F-020, F-022, F-024, F-035]
  - path: "external/libs/tools/CMake/Source/cmake.cxx"
    facts: [F-002, F-004, F-006, F-007, F-012, F-015, F-016, F-018, F-019, F-021, F-023, F-025, F-026, F-027]
---

# cmake 类：CMake 会话顶层门面

## 信源概述

| 信源 | 类型 | 行数 | 职责 |
|------|------|------|------|
| `Source/cmake.h` | 头文件 | ~300行 | cmake 类声明、WorkingMode 枚举、公共 API |
| `Source/cmake.cxx` | 实现文件 | ~1000行 | 构造/析构、Configure/Generate/Run 实现、工具链分发 |

## 关键事实登记

### F-001：cmake 类是会话级门面

**信源**：`Source/cmake.h`

`cmake` 类继承自 `cmStandardProps`，是 CMake 一次运行的顶级控制器。持有 `cmState* State`、`cmGlobalGenerator* GlobalGenerator`、`cmMakefile* Makefile` 等核心对象。

```cpp
class cmake : public cmStandardProps {
public:
  enum class WorkingMode { /* ... */ };
  // ...
protected:
  cmState* State;
  cmGlobalGenerator* GlobalGenerator;
  std::unique_ptr<cmMakefile> Makefile;
  // ...
};
```

### F-002：WorkingMode 枚举定义 7 种执行模式

**信源**：`Source/cmake.h`

| 模式 | 用途 |
|------|------|
| `NORMAL` | 标准 Configure+Generate 模式 |
| `FIND_PACKAGE` | `--find-package` 模式 |
| `HELP` | 帮助信息输出 |
| `VERSION` | 输出版本信息 |
| `SCRIPT` | 脚本模式（`-P`） |
| `SERVER` | CMake Server 模式 |
| `OPEN` | Open 模式 |

### F-003：Configure 方法执行配置阶段

**信源**：`Source/cmake.h` / `Source/cmake.cxx`

签名：`bool Configure(const std::string& sourceDir, const std::string& buildDir, bool clean);`

Configure 阶段执行：
1. 设置源码/构建目录
2. 创建 `cmGlobalGenerator` 实例
3. 加载 CMake 内置模块（`CMakeGenericSystem.cmake` 等）
4. 读取 `CMakeLists.txt` 并执行解析
5. 返回 bool 表示成功/失败

### F-004：Generate 方法执行生成阶段

**信源**：`Source/cmake.h` / `Source/cmake.cxx`

签名：`bool Generate();`

Generate 阶段使用 Configure 阶段积累的状态，调用 `GlobalGenerator->Generate()` 输出构建系统文件。

### F-005：SetHomeDirectory / SetHomeOutputDirectory

**信源**：`Source/cmake.cxx`

分别设置源码目录和构建目录的绝对路径，Configure 前必须调用。

### F-006：CreateGlobalGenerator 工厂方法

**信源**：`Source/cmake.cxx`

`void CreateGlobalGenerator(const std::string& genset);`

根据 `-G` 参数指定的生成器名称，从 `cmGlobalGeneratorFactory` 注册表查找并实例化对应的 GlobalGenerator。

### F-007：Run 方法统一分发执行

**信源**：`Source/cmake.cxx`

`int Run(const std::vector<std::string>& args);`

主入口方法：解析命令行参数 → 根据 WorkingMode 分发执行 → 返回退出码。是 `cmakemain.cxx` 调用的核心入口。

### F-008：AddCMakePaths 设置 CMake 模块搜索路径

**信源**：`Source/cmake.cxx`

设置 `CMAKE_ROOT`、`CMAKE_MODULE_PATH`、`CMAKE_COMMAND` 等内置路径变量，确保 `include()`、`find_package()` 能找到内置模块。

### F-009：cmListFileCache 持有解析后的命令缓存

**信源**：`Source/cmake.h`

`cmListFileCache* ListFileCache;` 缓存所有已解析的 CMakeLists.txt 和 .cmake 文件，避免重复解析。

## 代码引用

```cpp
// cmake.cxx - 核心执行流程（简化）
int cmake::Run(const std::vector<std::string>& args) {
  // 1. 解析参数
  // 2. 根据 WorkingMode 分发
  if (this->WorkingMode == WorkingMode::SCRIPT) {
    return this->RunScript(args);
  }
  // 3. Configure + Generate
  if (!this->Configure(srcDir, buildDir, clean)) return 1;
  if (!this->Generate()) return 1;
  return 0;
}
```
