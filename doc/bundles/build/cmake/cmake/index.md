---
okf_version: "0.2"
---

# CMake 构建系统知识库

本知识包是跨平台构建系统生成器 [CMake](https://cmake.org/)（BSD-3-Clause 许可证）的系统化中文源码教程，基于 CMake 源码（`external/libs/tools/CMake/Source/` 目录）深度阅读生成，覆盖从整体架构到构建/测试/打包全流程的完整知识体系。所有内容均溯源至 CMake C++ 源码核心类（cmake/cmState/cmGlobalGenerator/cmCommand/cmMakefile 等），遵循 [OKF v0.2 规范](concepts/overall-architecture.md)。

## 架构基础篇（concepts/）

* [CMake 整体架构与执行流程](concepts/overall-architecture.md) — 构建系统生成器定位、四层分层架构、Configure-Generate 两阶段模型、门面模式+多态生成器+不可变快照。
* [工作模式与工具链分发](concepts/working-mode.md) — cmake/ctest/cpack 三工具架构、7 种 WorkingMode、cmake -E 跨平台工具。
* [配置-生成两阶段执行](concepts/configure-generate.md) — Configure 脚本执行→cmState 状态累积→Generate 输出构建文件的完整流程、file-api JSON 输出。

## 核心机制篇（concepts/）

* [状态快照机制 (cmStateSnapshot)](concepts/state-snapshot.md) — 16字节值语义句柄、7种SnapshotType、快照树结构、写时复制与状态回滚。
* [变量作用域链](concepts/variable-scope.md) — 普通变量vs缓存变量、目录/函数/宏/块作用域规则、PARENT_SCOPE、常见陷阱。
* [多生成器工厂模式](concepts/generator-pattern.md) — cmGlobalGenerator 抽象基类、静态工厂自注册、Makefile/Ninja/VS/Xcode 分类、单/多配置生成器差异。
* [目标模型 (Target Model)](concepts/target-model.md) — executable/library/custom 目标类型、PUBLIC/PRIVATE/INTERFACE 传播、传递性链接、INTERFACE 库、生成器表达式。

## 功能模块篇（concepts/）

* [查找模块机制 (find_package)](concepts/find-module.md) — Module/Config 双模式、搜索路径顺序、导入目标、版本检查、COMPONENTS 多组件、Config 文件安装。
* [策略系统 (Policy System)](concepts/policy-system.md) — CMPxxxx 策略号、NEW/OLD 行为选择、cmake_policy PUSH/POP 堆栈、版本基线。
* [构建类型与多配置](concepts/build-type.md) — Debug/Release/RelWithDebInfo/MinSizeRel、单配置vs多配置、CMAKE_BUILD_TYPE 陷阱。
* [工具链检测与语言启用](concepts/toolchain-detection.md) — EnableLanguage 流程、编译器/ABI检测、工具链文件交叉编译、try_compile/try_run。

## 集成工具链篇（concepts/）

* [CTest 测试集成](concepts/ctest-integration.md) — add_test 注册、过滤/并行/Fixture、LABELS标签、CDash Dashboard上报。
* [CPack 打包集成](concepts/cpack-integration.md) — install()规则收集、TGZ/DEB/RPM/NSIS/DMG多格式、组件化打包。

## 实战示例（examples/）

* [基础项目配置：从零开始的 CMakeLists.txt](examples/basic-project.md) — 最小完整 C++ 项目模板：cmake_minimum_required→project→add_executable→install，含默认构建类型设置。
* [现代 CMake 目标使用：PUBLIC/PRIVATE/INTERFACE 传播](examples/modern-targets.md) — 多层库+可执行项目、目标属性传播、头文件-only库、find_package导入目标、别名目标。
* [跨平台构建与 find_package](examples/cross-platform.md) — Linux/macOS/Windows 三平台适配、find_package使用、平台特定源文件、工具链文件交叉编译、GNUInstallDirs。

## 信源登记簿（references/）

* [cmake 类：CMake 会话顶层门面](references/cmake-class.md) — `cmake` 类（cmake.h/cmake.cxx）核心 API 源码片段。
* [cmState：不可变状态管理核心](references/cmstate.md) — `cmState`/`cmStateSnapshot` 类（cmState.h/cxx、cmStateSnapshot.h/cxx）源码片段。
* [cmGlobalGenerator：多生成器工厂与构建模型](references/cmglobalgenerator.md) — `cmGlobalGenerator` 工厂模式（cmGlobalGenerator.h/cxx、cmGlobalGeneratorFactory.h）源码片段。
* [cmCommand：CMake 命令执行体系](references/cmdexec.md) — `cmCommand` 基类与命令注册（cmCommand.h/cxx、cmCommands.cxx）源码片段。
* [cmMakefile：目录级执行上下文](references/cmmakefile.md) — `cmMakefile` 类（cmMakefile.h/cxx）源码片段。
* [ctest/cpack：集成工具链](references/ctest-cpack.md) — CTest/CPack 工具链（ctest.cxx、cpack.cxx、CTest/、CPack/）源码片段。

## 信任与生命周期说明

* **status 判定依据**：全部 22 个内容文档（13 个概念 + 3 个示例 + 6 个信源登记）均 `status: stable`。内容基于对 CMake 源码（`external/libs/tools/CMake/Source/` 目录）核心类的逐文件阅读与事实提取（113+ 条源码事实 F-001~F-113），经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。CMake 核心架构（cmake门面/cmStateSnapshot快照/cmGlobalGenerator工厂/cmCommand命令）自 3.x 以来极其稳定，新生成器和命令不断添加但核心设计不变；该日期作为针对未来大版本（如 4.x）的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段对抗审查核验事件，两者分离、可追溯。

本知识包共收录 22 个内容文档（13 个概念 + 3 个示例 + 6 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
