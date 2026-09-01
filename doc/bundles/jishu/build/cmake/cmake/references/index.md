---
okf_version: "0.2"
type: index
title: CMake 源码信源参考
sources:
  - external/libs/tools/CMake/Source/
---

# 信源登记簿

本目录登记本知识包所有内容据以派生的 CMake 源码信源。所有概念文档和示例文档的 `sources` 字段均指向此目录下的信源登记条目。信源基于 CMake 源码（`external/libs/tools/CMake/Source/` 目录）的核心头文件和实现文件。

* [cmake 类：CMake 会话顶层门面](cmake-class.md) — `cmake` 类（`Source/cmake.h` / `Source/cmake.cxx`）：Configure()/Generate()/Run() 核心方法、WorkingMode 7 种执行模式、cmGlobalGenerator 工厂创建、AddCMakePaths 路径设置、cmListFileCache 命令缓存。
* [cmState：不可变状态管理核心](cmstate.md) — `cmState` 与 `cmStateSnapshot`（`Source/cmState.h`、`Source/cmState.cxx`、`Source/cmStateSnapshot.h`、`Source/cmStateSnapshot.cxx`）：全局状态容器、16字节轻量值语义句柄、7 种 SnapshotType、快照树结构、变量沿作用域链查找。
* [cmGlobalGenerator：多生成器工厂与构建模型](cmglobalgenerator.md) — `cmGlobalGenerator` 抽象基类与工厂模式（`Source/cmGlobalGenerator.h`、`Source/cmGlobalGenerator.cxx`、`Source/cmGlobalGeneratorFactory.h`）：Generate 三阶段执行、LocalGenerators 目录级生成器、Unix Makefiles/Ninja/Visual Studio/Xcode 生成器注册表、EnableLanguage 编译器初始化。
* [cmCommand：CMake 命令执行体系](cmdexec.md) — `cmCommand` 基类与命令注册（`Source/cmCommand.h`、`Source/cmCommand.cxx`、`Source/cmCommands.cxx`）：Clone 模式执行、cmExecutionStatus 控制流、Builtin vs Scripted 命令分类、GetPredefinedCommands 注册 100+ 内置命令、find_package Module/Config 双模式查找。
* [cmMakefile：目录级执行上下文](cmmakefile.md) — `cmMakefile` 类（`Source/cmMakefile.h`、`Source/cmMakefile.cxx`）：单目录执行上下文、ReadListFile 解析执行、变量管理 API、AddSubDirectory 递归子目录、Properties 多层属性存储、cmCacheManager 缓存变量、IssueMessage 错误报告。
* [ctest/cpack：集成工具链](ctest-cpack.md) — CTest（`Source/ctest.cxx`、`Source/CTest/`）和 CPack（`Source/cpack.cxx`、`Source/CPack/`）：add_test 注册、CTestTestfile.cmake 测试发现、Fixture 依赖排序、CDash HTTP 上报、install() 规则收集、TGZ/DEB/RPM/NSIS/DMG 多格式生成器工厂、CPackComponent 组件打包。

```{toctree}
:hidden:
:maxdepth: 7

cmake-class
cmdexec
cmglobalgenerator
cmmakefile
cmstate
ctest-cpack
```
