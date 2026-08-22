---
type: concept
title: "CMake 整体架构与执行流程"
description: "CMake 的整体分层架构：从命令行入口到 Configure/Generate 两阶段执行，再到构建系统输出的完整流程"
sources:
  references: [../references/cmake-class.md, ../references/cmstate.md, ../references/cmglobalgenerator.md, ../references/cmdexec.md]
  facts: [F-001, F-003, F-004, F-007, F-028, F-051, F-068, F-083]
---

# CMake 整体架构与执行流程

## 核心理解

CMake 不是构建工具本身，而是一个**构建系统生成器（Build System Generator）**。它读取 CMakeLists.txt 脚本，分析项目结构，然后输出目标构建系统的文件（Makefile、build.ninja、.vcxproj 等）。

整个系统采用**分层架构**：

```
┌─────────────────────────────────────────────────────────┐
│                   命令行入口 (cmakemain.cxx)             │
│              解析参数 → 分发 WorkingMode                 │
├─────────────────────────────────────────────────────────┤
│                   cmake 类（会话门面）                    │
│         Configure() ──────── Generate()                 │
│            ↓                      ↓                     │
│   ┌─────────────────┐  ┌─────────────────────┐         │
│   │   cmMakefile    │  │ cmGlobalGenerator   │         │
│   │  (目录执行上下文)│  │ (构建系统抽象基类)   │         │
│   │   ├─ cmCommand  │  │  ├─ cmLocalGenerator│         │
│   │   ├─ 变量/属性  │  │  └─ 输出构建文件     │         │
│   │   └─ 子目录管理  │  └─────────────────────┘         │
│   └─────────────────┘                                   │
│            ↓                                            │
│   ┌─────────────────┐                                  │
│   │   cmState       │                                  │
│   │ (不可变快照状态)  │                                  │
│   │  └─ Snapshot 树  │                                  │
│   └─────────────────┘                                  │
└─────────────────────────────────────────────────────────┘
```

## 两阶段执行模型

CMake 的核心执行分为 **Configure** 和 **Generate** 两个阶段：

### Configure 阶段（配置）

```cmake
# 这是一个标准的 CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(MyApp CXX)
add_executable(myapp main.cpp)
target_link_libraries(myapp PRIVATE fmt::fmt)
```

Configure 阶段执行 CMakeLists.txt 脚本：
1. **解析脚本**：`cmListFile` 将 CMakeLists.txt 分词为命令+参数列表
2. **执行命令**：`cmMakefile::ExecuteCommand()` 逐个调用命令（`project()`、`add_executable()` 等）
3. **状态累积**：每个命令调用修改 cmState 快照（添加目标、设置变量、注册依赖）
4. **工具链检测**：`EnableLanguage()` 检测编译器 ABI、特性
5. **依赖发现**：`find_package(fmt)` 查找依赖库

### Generate 阶段（生成）

Configure 成功后，GlobalGenerator 使用累积的状态输出构建文件：
1. **Compute**：计算目标依赖图（链接传递性、编译标志传播）
2. **本地生成**：每个 cmLocalGenerator 输出对应目录的构建规则
3. **全局输出**：写入 Makefile / build.ninja / .sln 等顶层文件

```
Configure 结束 → cmState 完整状态树
                      ↓
Generate 开始 → cmGlobalGenerator::Generate()
                      ↓
              ┌─ Makefile / build.ninja
              ├─ CMakeFiles/ 元数据
              └─ CTestTestfile.cmake / CPackConfig.cmake
```

## 关键设计洞察

1. **门面模式**：`cmake` 类是唯一对外入口，内部协调 cmState、cmGlobalGenerator、cmMakefile
2. **不可变快照**：cmStateSnapshot 确保 Configure 阶段状态可回滚、作用域隔离
3. **多态生成器**：同一个 Configure 结果可以生成不同构建系统（Unix Makefiles、Ninja、VS...）
4. **命令模式**：所有脚本操作通过 cmCommand 子类实现，支持 function/macro 扩展

## 为什么不是直接构建？

CMake 的设计哲学是**生成器而非执行器**：
- **跨平台**：一份 CMakeLists.txt 可以在 Linux/macOS/Windows 生成对应平台的原生构建文件
- **IDE 集成**：Visual Studio / Xcode 用户可以在原生 IDE 中工作
- **增量构建**：生成的 build.ninja/Makefile 支持高效增量编译
- **可复现**：Configure 是确定性的（给定同样输入产生同样输出）

## 关联概念

- [工作模式与工具链分发](working-mode.md) — 了解 NORMAL/SCRIPT/HELP 等模式
- [状态快照机制](state-snapshot.md) — 深入 cmStateSnapshot 设计
- [变量作用域链](variable-scope.md) — 理解 set()/PARENT_SCOPE 的作用域规则
- [多生成器工厂模式](generator-pattern.md) — 了解不同构建系统如何适配
- [配置-生成两阶段](configure-generate.md) — 深入两阶段的具体细节
