# 概念文档

本目录包含 CMake 的 13 个核心概念文档，按学习路径排列：从架构总览到具体机制逐步深入。

## 架构基础篇

* [CMake 整体架构与执行流程](overall-architecture.md) — 构建系统生成器定位、四层分层架构、Configure-Generate 两阶段执行模型、门面模式+多态生成器+不可变快照核心设计。
* [工作模式与工具链分发](working-mode.md) — cmake/ctest/cpack 三工具统一代码基础、7 种 WorkingMode（NORMAL/SCRIPT/HELP/VERSION/FIND_PACKAGE/SERVER/OPEN）、cmake -E 跨平台命令行工具。
* [配置-生成两阶段执行](configure-generate.md) — Configure 阶段（脚本解析、命令执行、状态累积）与 Generate 阶段（Compute、LocalGenerator 输出、构建文件生成）的详细流程，file-api 现代 IDE 输出。

## 核心机制篇

* [状态快照机制 (cmStateSnapshot)](state-snapshot.md) — 不可变值语义快照句柄、7 种 SnapshotType、快照树结构、写时复制与状态回滚原理。
* [变量作用域链](variable-scope.md) — 普通变量 vs 缓存变量、目录/函数/宏/块四种作用域、PARENT_SCOPE、变量查找优先级链、常见陷阱。
* [多生成器工厂模式](generator-pattern.md) — cmGlobalGenerator 抽象基类、静态工厂自注册机制、Makefile/Ninja/VS/Xcode 生成器分类、单配置 vs 多配置生成器差异。
* [目标模型 (Target Model)](target-model.md) — executable/library/custom 目标类型、属性系统、PUBLIC/PRIVATE/INTERFACE 传播关键字、传递性链接、INTERFACE 库、生成器表达式。

## 功能模块篇

* [查找模块机制 (find_package)](find-module.md) — Module 模式 vs Config 模式、搜索路径顺序、导入目标 vs 变量返回、版本检查、COMPONENTS 多组件、CMakePackageConfigHelpers 配置安装。
* [策略系统 (Policy System)](policy-system.md) — CMPxxxx 策略号、NEW/OLD 行为选择、cmake_minimum_required 隐式基线、cmake_policy PUSH/POP 堆栈、策略与快照机制关系。
* [构建类型与多配置](build-type.md) — Debug/Release/RelWithDebInfo/MinSizeRel 四种标准类型、单配置（Ninja/Makefile）vs 多配置（VS/Xcode/Ninja Multi-Config）、CMAKE_CONFIGURATION_TYPES、CMAKE_BUILD_TYPE 陷阱。
* [工具链检测与语言启用](toolchain-detection.md) — EnableLanguage 流程、编译器/ABI/编译特性检测、工具链文件交叉编译、try_compile/try_run 自定义检测、编译器标识条件判断。

## 集成工具链篇

* [CTest 测试集成](ctest-integration.md) — enable_testing()、add_test() 注册、测试过滤/并行/超时、Fixture 测试依赖排序、LABELS 标签、CDash Dashboard 上报、CTest 脚本模式。
* [CPack 打包集成](cpack-integration.md) — install() 规则收集、TGZ/DEB/RPM/NSIS/DMG 多格式生成、组件化打包（COMPONENT）、CPackConfig.cmake 配置、cpack 命令行选项。

```{toctree}
:hidden:

build-type
configure-generate
cpack-integration
ctest-integration
find-module
generator-pattern
overall-architecture
policy-system
state-snapshot
target-model
toolchain-detection
variable-scope
working-mode
```
