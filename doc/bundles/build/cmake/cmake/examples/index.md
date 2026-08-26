# 实战示例

本目录包含 3 个完整的 CMake 项目示例，每个示例对应核心概念，提供从基础到跨平台的渐进式学习路径。

* [基础项目配置：从零开始的 CMakeLists.txt](basic-project.md) — 最小但完整的 C++ 项目模板：cmake_minimum_required、project、add_executable、target_sources、install、默认构建类型设置。对应概念：[CMake 整体架构与执行流程](../concepts/overall-architecture.md)、[配置-生成两阶段执行](../concepts/configure-generate.md)、[工具链检测与语言启用](../concepts/toolchain-detection.md)。
* [现代 CMake 目标使用：PUBLIC/PRIVATE/INTERFACE 传播](modern-targets.md) — 多层库+可执行项目、target_include_directories/compile_features/link_libraries 的 PUBLIC/PRIVATE/INTERFACE 传播、头文件-only INTERFACE 库、find_package 导入目标使用、别名目标。对应概念：[目标模型 (Target Model)](../concepts/target-model.md)、[变量作用域链](../concepts/variable-scope.md)。
* [跨平台构建与 find_package](cross-platform.md) — Linux/macOS/Windows 三平台适配、find_package Config/Module 模式使用、平台特定源文件和链接库、工具链文件交叉编译、GNUInstallDirs、BUILD_INTERFACE/INSTALL_INTERFACE 路径分离。对应概念：[查找模块机制 (find_package)](../concepts/find-module.md)、[多生成器工厂模式](../concepts/generator-pattern.md)、[构建类型与多配置](../concepts/build-type.md)、[工具链检测与语言启用](../concepts/toolchain-detection.md)。

```{toctree}
:hidden:
:maxdepth: 7

basic-project
cross-platform
modern-targets
```
