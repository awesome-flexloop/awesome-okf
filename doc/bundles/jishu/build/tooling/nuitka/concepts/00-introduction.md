---
okf_version: "0.2"
type: Concept
title: "Nuitka 简介"
description: "Nuitka V4.1rc11是什么——Python源码到C二进制的AOT编译器，与CPython、PyPy、Cython的核心区别"
tags: ["nuitka", "introduction", "compiler", "python"]
sources:
  - id: REF-INTRO-001
    path: "nuitka/Version.py"
    description: "版本定义"
  - id: REF-INTRO-002
    path: "README.txt"
    description: "项目说明"
  - id: REF-INTRO-003
    path: "LICENSE.txt"
    description: "Apache 2.0许可证"
prerequisites: []
next:
  - "01-compilation-pipeline"
related:
  - "../references/main-control-entry.md"
  - "../examples/basic-compilation.md"
verified: true
status: active
---

# Nuitka 简介

## Nuitka 是什么

Nuitka是一个**Python源码到C代码的提前（AOT）编译器**。它读取你的Python源代码，不做任何类型标注要求，通过静态分析理解你的代码，将其翻译为C代码，然后调用系统C编译器（gcc/clang/MSVC）将这些C代码编译为本地机器码——最终产出一个**不需要Python解释器即可运行**的可执行文件（standalone模式）或一个Python C扩展模块（module模式）。

Nuitka由Kay Hayen自2012年开始开发，本教程基于 **Nuitka V4.1rc11**（版权年份2026），采用Apache 2.0许可证。

> **源码定位**：版本字符串定义于 Version.py:6-8：
> ```python
> version_string = "Nuitka V4.1rc11\nCopyright (C) 2026 Kay Hayen."
> ```

## Nuitka 不是什么

理解Nuitka的定位，关键是搞清楚它**不是**什么：

| 对比项 | Nuitka | CPython | PyPy | Cython |
|--------|--------|---------|------|--------|
| 编译方式 | **AOT提前编译** | 解释执行 | JIT即时编译 | AOT（需类型标注） |
| 类型标注 | **不需要** | 不需要 | 不需要 | **推荐/必需** |
| 运行方式 | 本地二进制 | `.pyc`字节码解释 | tracing JIT | C扩展模块 |
| 与CPython关系 | 深度依赖C/API | 就是CPython | 独立VM | 依赖C/API |
| 兼容性 | 高度兼容（全Python语法） | 标准 | 良好（偶有兼容问题） | 类Python语法（超集） |
| 分发方式 | standalone/onefile | 需Python环境 | 需PyPy环境 | 需Python环境 |

### 核心区别

1. **vs CPython（标准解释器）**：CPython读取.py→编译为字节码→在VM中逐条解释执行；Nuitka读取.py→构建IR树→优化→生成C→编译为机器码，**直接在CPU上执行**，跳过了解释开销。

2. **vs PyPy**：PyPy是一个带Tracing JIT的Python解释器，运行时收集类型信息并热编译；Nuitka是**编译时**做静态分析，不依赖运行时profiling，启动无预热开销。PyPy需要自己的VM运行时；Nuitka编译的程序通过Python C/API与CPython运行时交互。

3. **vs Cython**：Cython要求你写一种Python超集（.pyx），可以添加类型标注来加速；Nuitka**编译普通的Python代码**，不需要你修改任何源码，通过值追踪自动推断类型。

## Nuitka 的核心能力

- **完整Python语法支持**：支持Python 2.6~2.7和Python 3.4~3.13的全部语法特性，包括async/await、生成器、装饰器、元类、描述符等
- **无源码修改**：不需要修改你的Python代码，不需要添加类型标注
- **全程序编译**：不仅编译你的主脚本，还递归编译依赖的所有模块（可配置）
- **分发模式**：
  - `--standalone`：生成包含所有依赖的目录分发
  - `--onefile`：生成单个压缩可执行文件
  - `--module`：编译为Python可导入的扩展模块
- **插件系统**：34个标准插件，支持NumPy/PyTorch/Qt/Tkinter/Pandas等主流库
- **性能优化**：
  - 常量折叠与传播
  - 逃逸分析（变量不逃逸则不上堆）
  - 类型特化代码生成（已知类型时生成直接C操作）
  - 函数内联
  - 内置调用快速路径
  - SSA（静态单赋值）风格的值追踪
- **跨平台**：Windows（MSVC/MinGW）、Linux（gcc/clang）、macOS（clang）、Android（NDK）

## 基本使用

最简单的编译命令：

```bash
# 将script.py编译为可执行文件
nuitka script.py

# 生成独立可执行文件（包含所有依赖）
nuitka --standalone script.py

# 生成单文件可执行文件
nuitka --onefile script.py

# 编译为Python扩展模块
nuitka --module mymodule.py
```

详见 [基本编译示例](../examples/basic-compilation.md)。

## 学习路径

```
00-introduction（本文档）
  → 01-compilation-pipeline：理解四阶段编译流水线
    → 02-architecture-overview：模块分层架构总览
      → 03-ast-tree-building：AST如何变为内部树
        → 04-node-ir-system：元类、基类、Mixin机制
          → 05-type-shapes：类型推断如何驱动优化
            → 06-module-import-system：模块导入递归决策
              → 07-optimization-passes：优化遍与值追踪
                → 08-c-code-generation：C代码如何生成
                  → 09-c-compilation-backend：SCons如何编译C
                    → 10-freezer-distribution：standalone/onefile打包
                      → 11-plugin-system：插件扩展机制
                        → 12-variables-closures：变量与闭包
                          → 13-cli-options：命令行选项
```
