---
type: Concept
title: Ninja 简介
description: Ninja 是 Google 开发的专注于速度的小型构建系统，设计为元构建系统的后端执行引擎
tags: [ninja, concept, introduction, build-system, overview]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# Ninja 简介

## Ninja 是什么

Ninja 是一个专注于**速度**的小型构建系统，由 Google 工程师 Evan Martin 开发，其自我描述为 "a small build system with a focus on speed"。Ninja 的设计灵感来源于 Google 内部用于构建 Chrome 的构建系统，目标是在大型项目中实现尽可能快的增量构建。

Ninja 的核心定位不是一个通用的"可编程"构建系统（如 Make 或 SCons），而是一个**构建执行引擎**——它接收一份描述构建依赖关系的 manifest 文件（通常是 `build.ninja`），然后以最高效的方式并行执行构建命令。

```
┌─────────────┐     生成      ┌──────────────┐    执行     ┌─────────────┐
│  元构建系统   │ ───────────→ │  build.ninja  │ ─────────→ │   Ninja     │
│ (CMake/Meson│               │  (manifest)   │            │  (执行引擎)  │
│  /gn)       │               └──────────────┘            └─────────────┘
└─────────────┘
```

## 设计哲学

Ninja 的设计哲学可以概括为三个关键词：

### 速度优先

Ninja 的一切设计都以速度为首要目标：
- **无解释开销**：manifest 语法极简，没有函数、循环、条件语句，无需解释器
- **零拷贝字符串**：使用 [StringPiece](../references/util-source.md) 避免字符串拷贝
- **二进制日志**：构建日志（`.ninja_log`）和依赖日志（`.ninja_deps`）使用二进制格式，启动时快速加载
- **避免冗余 stat**：[Node::StatIfNecessary](../references/graph-source.md) 缓存文件状态，避免重复系统调用
- **并行优化**：关键路径优先调度 + IO 多路复用，最大化 CPU 利用率

### 极简设计

Ninja 故意不提供高级构建特性：
- **无内置条件逻辑**：没有 if/else、循环、函数
- **无字符串操作**：所有变量都是简单的字符串替换
- **无内置编译器规则**：不预设任何编译规则，所有命令由生成器提供
- **单文件 manifest**：通过 include/subninja 组织，但没有复杂的模块系统

这种极简设计意味着 Ninja 文件几乎总是由程序生成，而不是手写。

### 职责分离

Ninja 严格区分"描述构建"和"执行构建"两个阶段：
- **构建描述**（条件逻辑、依赖计算、平台适配）→ 交给元构建系统（CMake、Meson、gn）
- **构建执行**（依赖图遍历、并行调度、增量检测）→ Ninja 负责

## Ninja vs Make

| 特性 | Ninja | Make |
|------|-------|------|
| **设计目标** | 速度优先，作为元构建后端 | 通用构建工具，支持手写 |
| **条件/循环** | 无（故意不提供） | 有（函数、条件、循环） |
| **字符串操作** | 无（仅变量替换） | 丰富（patsubst、wildcard 等） |
| **增量检测** | mtime + depfile + 命令哈希 + restat | mtime 为主 |
| **头依赖追踪** | 内置 depfile/depslog 机制 | 需要手动编写 gcc -MMD 规则 |
| **并行模型** | 单线程事件循环 + 子进程 + 关键路径调度 | 多进程 jobserver |
| **构建日志** | 二进制格式，快速加载 | 无内置持久化日志 |
| **启动速度** | 极快（大型项目 < 100ms） | 较慢（需要解释 Makefile） |
| **典型增量构建** | Chrome 增量构建 < 1 秒 | 数十秒甚至更长 |

> **关键差异**：Make 既是构建描述语言又是构建执行器；Ninja 只是执行器，构建描述完全由生成器负责。

## 适用场景

Ninja 最适合以下场景：

1. **大型项目增量构建**：如 Chrome、LLVM、Android 等数万文件的项目，需要快速增量编译
2. **元构建系统后端**：作为 CMake（`-G Ninja`）、Meson、gn 等工具的执行引擎
3. **CI/CD 构建加速**：快速的启动和增量检测可以减少 CI 等待时间
4. **需要编译数据库的项目**：通过 `ninja -t compdb` 生成 `compile_commands.json` 供 clangd 等工具使用

## 不适用场景

Ninja 不适合以下场景：

1. **手写复杂构建逻辑**：没有条件/循环/函数，复杂逻辑无法在 Ninja 文件中表达
2. **简单脚本式构建**：对于只有几个文件的项目，直接用 shell 脚本或 Make 更简单
3. **需要动态依赖发现的复杂场景**（Ninja 的 dyndep 机制有但较复杂，多数情况由生成器处理）
4. **跨平台打包/安装逻辑**：CMake/Meson 的 install 逻辑在生成器层处理更合适

## 核心特性

### 增量构建

Ninja 通过比较输出文件和输入文件的修改时间（mtime）来判断是否需要重建，配合 [depfile 机制](06-incremental-build.md) 和命令哈希检测，实现精确的增量构建。

### 并行执行

Ninja 使用单线程事件循环驱动多个子进程，通过 `-j` 参数控制最大并行数，支持 [Pool 机制](07-parallel-execution.md) 限制特定规则的并发度，并集成 GNU Make 的 jobserver 协议。

### 头依赖追踪

通过 `deps = gcc/msvc` + `depfile =` 声明，Ninja 可以自动追踪 C/C++ 头文件依赖，缓存到 `.ninja_deps` 二进制日志中，避免每次构建都重新扫描。

### 动态依赖

Ninja 支持 `dyndep` 机制，允许在构建过程中发现和加载额外的依赖关系（主要用于 Fortran 模块依赖等场景）。

### 跨平台支持

Ninja 原生支持 Windows（MSVC、MinGW）、Linux、macOS 等平台，自动处理路径分隔符、子进程创建、IO 多路复用等平台差异。

## Ninja 生态

| 工具 | 类型 | 与 Ninja 的关系 |
|------|------|----------------|
| **CMake** | 元构建系统 | `cmake -G Ninja` 生成 build.ninja，最广泛使用的组合 |
| **Meson** | 元构建系统 | 原生使用 Ninja 作为后端，默认生成器 |
| **gn** | 元构建系统 | Google 开发，生成 `.ninja` 文件，用于 Chrome/V8 等项目 |
| **Bazel** | 构建系统 | 底层采用类似 Ninja 的 DAG 执行模型，但不直接生成 Ninja 文件 |
| **Buck2** | 构建系统 | Meta 开发，使用类似的并行 DAG 执行模型 |
| **Samurai** | Ninja 兼容实现 | C99 编写的 Ninja 兼容实现，更轻量 |
| **n2** | Ninja 后继 | Ninja 作者开发的实验性后继项目 |

## 相关概念

- [快速开始](01-getting-started.md) — 编译安装 Ninja 并运行第一个构建
- [架构总览](02-architecture-overview.md) — Ninja 的四大核心模块和构建流程
- [依赖图模型](03-dependency-graph.md) — Node-Edge 二分图详解
