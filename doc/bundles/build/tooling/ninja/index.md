---
type: OKF
title: Ninja 构建系统教程
description: Ninja（ninja-build）极速构建系统的完整源码级教程——二分图依赖模型、构建执行管线、Manifest语言、增量构建、并行调度、子命令工具与生成器集成
tags: [ninja, build-system, c++, make, cmake, meson, incremental-build, parallel-execution]
version: "1.12"
source: https://github.com/ninja-build/ninja
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# Ninja 构建系统教程

Ninja 是一个专注于速度的小型构建系统，由 Evan Martin 在 Google 开发（2010年），设计初衷是作为 Chromium 项目的构建后端。与 Make 不同，Ninja intentionally 不实现条件语句、循环、函数等高级构建逻辑——这些复杂性委托给元构建系统（CMake、Meson、gn），Ninja 自身只做一件事：**快速执行已规划好的构建命令**。

Ninja 的核心设计哲学是"输入文件由程序生成，而非人手写"。它解析极简的 `.ninja` manifest 文件，在内存中构建 Node-Edge 二分依赖图，按关键路径优先级并行调度子进程执行命令，并通过 mtime 比较、depfile 头依赖缓存、dyndep 动态依赖等机制实现精确的增量构建。

## 📚 快速导航

### [概念文档](concepts/index.md)

**入门篇：**
- [00-简介](concepts/00-introduction.md) — Ninja 是什么、设计哲学、与 Make 对比、适用场景
- [01-快速开始](concepts/01-getting-started.md) — 编译安装、第一个 build.ninja、基本命令、自动变量
- [02-架构总览](concepts/02-architecture-overview.md) — 四大模块架构、构建流程七步骤、数据流

**核心篇：**
- [03-依赖图模型](concepts/03-dependency-graph.md) — Node-Edge 二分图、五种依赖类型、phony 规则、拓扑排序
- [04-构建执行管线](concepts/04-build-execution.md) — Builder 主循环、Plan 调度、关键路径优先级、错误处理
- [05-Manifest 语言详解](concepts/05-manifest-language.md) — rule/build/pool/default、变量系统、作用域链、EvalString 延迟求值

**深入篇：**
- [06-增量构建机制](concepts/06-incremental-build.md) — mtime 检测、depfile/depslog、restat、命令哈希、dyndep
- [07-并行执行与并发控制](concepts/07-parallel-execution.md) — 单线程+子进程模型、-j 参数、Pool、Jobserver
- [08-子命令与工具](concepts/08-subcommands-tools.md) — -t clean/compdb/graph/query/deps、-d 调试选项

**高级篇：**
- [09-Ninja 内部实现](concepts/09-ninja-internals.md) — 源码组织、StringPiece、FNVHash、二进制日志格式、性能优化
- [10-构建生成器集成](concepts/10-build-generators.md) — CMake/Meson/gn 集成、ninja_syntax.py、compile_commands.json

### [实践示例](examples/index.md)
- [01-最简构建](examples/01-minimal-build.md) — 编译单个 C 程序、基本命令、mtime 增量检测 ⭐入门
- [02-多文件 C++ 项目](examples/02-cxx-project.md) — 分离编译/链接、deps/depfile 头依赖追踪 ⭐⭐进阶
- [03-并行构建与 Pool 控制](examples/03-parallel-jobs.md) — -j 参数调优、自定义 Pool、console 池、Jobserver ⭐⭐进阶
- [04-增量构建与依赖追踪](examples/04-incremental-deps.md) — 脏标记传播、restat 优化、phony/order-only ⭐⭐⭐高级
- [05-子命令实用指南](examples/05-subcommand-usage.md) — graph/clean/compdb/query/deps 等子命令实战 ⭐⭐进阶

### [信源参考](references/index.md)
- [图结构 API](references/graph-source.md) — Node、Edge、DependencyScan、EdgePriorityQueue
- [构建执行 API](references/build-source.md) — Plan、Builder、BuildConfig、CommandRunner
- [状态管理 API](references/state-source.md) — State、Pool
- [Manifest 解析器 API](references/parser-source.md) — ManifestParser、Lexer、Token 枚举
- [变量求值 API](references/eval-source.md) — Rule、BindingEnv、EvalString
- [日志系统 API](references/logs-source.md) — BuildLog、DepsLog、Dyndeps
- [工具与 IO API](references/util-source.md) — DiskInterface、Subprocess、Jobserver、Metrics、StringPiece
- [主入口 API](references/main-source.md) — NinjaMain、Options、Tool 函数、Status

### [事实清单](facts.md) — 从源码采集的 230+ 条零推测事实
### [架构洞察](insights.md) — 5 个核心洞察四元组与知识地图

## 🚀 快速开始

```bash
# 编译安装 Ninja
git clone https://github.com/ninja-build/ninja.git
cd ninja
cmake -Bbuild
cmake --build build
sudo cp build/ninja /usr/local/bin/

# 或者直接使用包管理器
# Ubuntu/Debian: sudo apt install ninja-build
# macOS: brew install ninja
# conda: conda install ninja
```

创建最简单的 `build.ninja`：

```ninja
rule cc
  command = gcc -c $in -o $out
  description = CC $out

rule link
  command = gcc $in -o $out
  description = LINK $out

build main.o: cc main.c
build main: link main.o
default main
```

构建：

```bash
$ ninja
[2/2] LINK main
$ ./main
Hello, Ninja!
```

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| ⚡ 极速启动 | 极简 manifest 语法，无脚本解释，C++ 实现启动毫秒级 |
| 📊 精确增量 | mtime 比较 + depfile 头依赖 + 命令哈希 + restat 优化 |
| 🔀 并行调度 | 关键路径优先级队列，Pool 并发控制，Jobserver 共享令牌 |
| 🔗 五种依赖 | 显式输入、隐式依赖、order-only、验证依赖、隐式输出 |
| 📝 二进制日志 | .ninja_log（命令历史）+ .ninja_deps（头依赖缓存） |
| 🧩 动态依赖 | dyndep 机制支持构建过程中发现新依赖（Fortran 模块等） |
| 🛠️ 丰富工具 | -t 子命令：clean/compdb/graph/query/deps/targets/commands 等 |
| 🔌 跨平台 | POSIX（Linux/macOS）+ Windows（MSVC/MinGW）原生支持 |

## 📖 推荐学习路径

1. **入门体验**：阅读 [00-简介](concepts/00-introduction.md) 和 [01-快速开始](concepts/01-getting-started.md)，跟着 [01-最简构建](examples/01-minimal-build.md) 动手
2. **理解架构**：学习 [02-架构总览](concepts/02-architecture-overview.md)，掌握四大模块和构建流程
3. **掌握核心**：深入 [03-依赖图模型](concepts/03-dependency-graph.md)、[04-构建执行管线](concepts/04-build-execution.md)、[05-Manifest 语言](concepts/05-manifest-language.md)
4. **动手实践**：完成 [02-多文件 C++ 项目](examples/02-cxx-project.md)，理解 depfile/deps 头依赖追踪
5. **深入机制**：学习 [06-增量构建](concepts/06-incremental-build.md)、[07-并行执行](concepts/07-parallel-execution.md)、[08-子命令工具](concepts/08-subcommands-tools.md)
6. **高级应用**：[04-增量构建实战](examples/04-incremental-deps.md) 和 [05-子命令指南](examples/05-subcommand-usage.md)
7. **源码精读**：学习 [09-Ninja 内部实现](concepts/09-ninja-internals.md)，配合 [API 参考](references/index.md) 阅读源码
8. **生成器集成**：[10-构建生成器集成](concepts/10-build-generators.md) 了解 CMake/Meson 如何生成 build.ninja

## 📊 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    Ninja 构建执行流程                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  build.ninja ──→ Lexer ──→ ManifestParser ──→ State         │
│                  (词法)      (语法解析)       (Node/Edge/   │
│                                              Rule/Pool)     │
│                                                             │
│  .ninja_log  ──→ BuildLog     ┐                              │
│  .ninja_deps ──→ DepsLog     ├──→ DependencyScan            │
│                               │    (脏状态计算)              │
│  DiskInterface ──→ Stat()   ─┘                              │
│                                                             │
│  State(干净?) ──→ Plan ──→ EdgePriorityQueue                │
│                  (调度)     (关键路径排序)                    │
│                    │                                        │
│                    ▼                                        │
│              Builder 主循环                                  │
│         ┌──── FindWork() ────┐                             │
│         │                     │                             │
│         ▼                     │                             │
│    StartEdge()                │ more_to_do()?               │
│         │                     │                             │
│         ▼                     │                             │
│    CommandRunner ──→ Subprocess ──→ WaitForCommand()        │
│         │                     │                             │
│         ▼                     │                             │
│    EdgeFinished() ────────────┘                             │
│         │                                                   │
│         ▼                                                   │
│    BuildLog::RecordCommand()                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔗 外部资源

- **官方网站**：[ninja-build.org](https://ninja-build.org/)
- **GitHub 仓库**：[ninja-build/ninja](https://github.com/ninja-build/ninja)
- **手册页**：[ninja manual](https://ninja-build.org/manual.html)
- **CMake 集成**：[cmake.org](https://cmake.org/cmake/help/latest/generator/Ninja.html)
- **Meson 构建系统**：[mesonbuild.com](https://mesonbuild.com/)
- **GN 元构建系统**：[gn.googlesource.com/gn](https://gn.googlesource.com/gn/)
- **Python 生成器库**：[ninja_syntax.py](https://github.com/ninja-build/ninja/blob/master/misc/ninja_syntax.py)

```{toctree}
:hidden:

concepts/index
examples/index
references/index
facts
insights
log
```
