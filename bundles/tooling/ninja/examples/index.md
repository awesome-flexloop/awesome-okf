---
type: ExampleIndex
title: Ninja 构建系统示例教程
description: 通过5个循序渐进的可运行示例，从最简C程序编译到并行构建、增量依赖追踪和子命令使用，动手掌握Ninja构建系统的核心功能。
tags: [ninja, example, index, tutorial, hands-on]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# Ninja 构建系统示例教程

本教程包含 5 个循序渐进、可动手实践的示例，每个示例都提供完整的代码、逐步的执行指引和预期输出。通过这些示例，你将从零基础掌握 Ninja 构建系统的核心用法。

> **配套文档**：概念讲解见 [概念文档](../concepts/index.md)，命令参考见 [参考文档](../references/index.md)。

---

## 前置条件

在开始之前，请确保你的系统已安装以下工具：

### 必需工具

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| **Ninja** ≥ 1.10 | 构建系统本身 | `apt install ninja-build` / `brew install ninja` / [官方下载](https://ninja-build.org/) |
| **GCC/G++** | C/C++编译器 | `apt install build-essential` / `brew install gcc` / Xcode Command Line Tools |
| **Bash** | Shell环境（运行脚本和命令） | Linux/macOS自带；Windows推荐WSL2或Git Bash |

### 可选工具

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| **Graphviz** | 渲染依赖图（示例05使用） | `apt install graphviz` / `brew install graphviz` |
| **Python 3** | ninja -t browse 等辅助功能 | `apt install python3` / `brew install python3` |
| **clangd** | 使用compile_commands.json进行代码补全 | `apt install clangd` / `brew install llvm` |

### 验证环境

```shell
$ ninja --version
1.11.1

$ g++ --version
g++ (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0

$ dot -V  # 可选
dot - graphviz version 2.43.0
```

---

## 推荐学习顺序

建议按照以下顺序学习（按依赖关系排列）：

```
01-minimal-build ──→ 02-cxx-project ──→ 04-incremental-deps
                                              ↑
                       03-parallel-jobs ──────┘
                                              ↓
                                    05-subcommand-usage
```

| 序号 | 示例 | 难度 | 核心知识点 |
|------|------|------|-----------|
| 1 | [最简构建：编译单个C程序](01-minimal-build.md) | ⭐ 入门 | build.ninja结构、rule/build/default、$in/$out自动变量、-n/-v/-d explain |
| 2 | [多文件C++项目](02-cxx-project.md) | ⭐⭐ 进阶 | 分离编译与链接、depfile/deps=gcc头依赖追踪、构建变量、.ninja_deps |
| 4 | [增量构建与依赖追踪](04-incremental-deps.md) | ⭐⭐⭐ 高级 | 脏标记传播、头文件重编译验证、restat规则、phony目标、order-only依赖、目录创建 |
| 3 | [并行构建与Pool控制](03-parallel-jobs.md) | ⭐⭐ 进阶 | -j并行度、Pool并发限制、console pool、-d stats并行统计 |
| 5 | [子命令实用指南](05-subcommand-usage.md) | ⭐⭐ 进阶 | targets/commands/deps/inputs/query/graph/compdb/clean/recompact |

### 为什么03和04的顺序调换？

- 02（多文件C++）建立在01之上，自然紧随其后
- 04（增量构建）深入讲解02中使用的depfile/deps机制，建议在02之后立即学习以巩固理解
- 03（并行构建）是相对独立的话题，使用sleep模拟任务即可，不依赖04的知识
- 05（子命令）基于02的项目结构，放在最后可以综合运用前面所有知识

当然，你也可以按编号顺序学习（01→02→03→04→05），不会有知识断层。

---

## 示例列表

### 1. [最简构建：编译单个C程序](01-minimal-build.md)

**难度**：⭐ 入门

从零开始，用 Ninja 编译一个 Hello World C 程序。学习 `build.ninja` 的基本结构——`rule` 定义编译命令、`build` 声明目标依赖关系、`default` 指定默认目标。理解 `$in` 和 `$out` 自动变量的展开方式，以及 Ninja 如何通过 mtime 比较判断是否需要重编译。

```ninja
rule cc
  command = gcc -Wall -o $out $in
  description = CC $out

build main: cc main.c
default main
```

你将学会：
- 编写第一个 build.ninja
- 使用 `ninja`、`ninja -v`、`ninja -n` 命令
- 用 `ninja -d explain` 诊断重建原因
- 理解增量构建的基本原理

---

### 2. [多文件C++项目](02-cxx-project.md)

**难度**：⭐⭐ 进阶

构建一个包含 `main.cpp`、`util.cpp`、`util.h` 的典型 C++ 项目。掌握分离编译模式（每个 `.cpp` 独立编译为 `.o`，再统一链接）和头文件依赖追踪——通过 `-MMD -MF` 编译器选项生成 `.d` 依赖文件，配合 `depfile` 和 `deps = gcc` 让 Ninja 自动追踪头文件变化。

```ninja
rule cxx
  command = $cxx $cxxflags -MMD -MT $out -MF $out.d -c $in -o $out
  depfile = $out.d
  deps = gcc
```

你将学会：
- 分离编译与链接的两个规则
- 使用变量（`cxxflags`、`ldflags`）管理编译选项
- 配置 depfile + deps 自动追踪头文件依赖
- 查看 `.ninja_deps` 和 `.ninja_log` 验证依赖
- 修改头文件后验证增量重编译的正确性

---

### 3. [并行构建与Pool控制](03-parallel-jobs.md)

**难度**：⭐⭐ 进阶

使用 `sleep` 命令模拟长时间编译任务，直观感受并行构建的加速效果。通过对比 `-j1`、`-j4`、`-j8` 的构建时间理解关键路径和并行上限。学习使用 `pool` 机制限制特定类型任务的并发数（如限制链接任务为1以避免OOM），以及 `console` pool 让交互式命令独占终端。

```ninja
pool link_pool
  depth = 1

rule link
  command = sleep 2 && ...
  pool = link_pool
```

你将学会：
- `-j N` 参数控制并行度，默认值=CPU核心数+2
- 定义和使用 Pool 限制并发
- `console` pool 处理交互式命令
- 使用 `time` 命令和 `ninja -d stats` 分析并行效率

---

### 4. [增量构建与依赖追踪](04-incremental-deps.md)

**难度**：⭐⭐⭐ 高级

深入 Ninja 增量构建机制的 4 个核心场景：(1) 修改源文件触发重编译+重链接的脏标记传播链；(2) 修改头文件触发所有包含它的源文件重编译；(3) `restat` 规则——智能代码生成器未改变输出时不触发下游重建；(4) `phony` 目标创建别名、`order-only` 依赖处理目录创建。

```ninja
rule generate
  command = bash gen.sh $in $out
  restat = 1

build build/: mkdir
build build/main.o: cxx main.cpp | build/
```

你将学会：
- 脏标记在依赖图中的传播机制
- restat 规则避免不必要的级联重建
- phony 目标定义别名（all/test）
- order-only 依赖（`|`）只保证顺序不触发重建
- 目录创建的标准模式
- 综合使用 `-d explain`、`-t deps`、`.ninja_log` 诊断构建问题

---

### 5. [子命令实用指南](05-subcommand-usage.md)

**难度**：⭐⭐ 进阶

基于多文件C++项目，系统掌握 Ninja 的 `-t` 工具集。涵盖日常开发中最常用的子命令：列出目标（`targets`）、查看命令（`commands`）、查询依赖（`deps`/`inputs`/`query`）、生成可视化图（`graph`）、清理产物（`clean`）、生成编译数据库（`compdb`）、压缩日志（`recompact`）。每个命令都附带实际输出示例和适用场景。

```shell
$ ninja -t targets all
$ ninja -t commands main
$ ninja -t deps main.o
$ ninja -t graph main | dot -Tpng -o deps.png
$ ninja -t compdb cxx > compile_commands.json
```

你将学会：
- 使用 `ninja -t` 子命令查询和调试构建系统
- 生成 `compile_commands.json` 配置 IDE/编辑器代码补全
- 渲染 Graphviz 依赖图
- 清理构建产物和压缩日志

---

## 快速开始

```shell
# 创建工作目录
$ mkdir -p ~/ninja-demo && cd ~/ninja-demo

# 从第一个示例开始
$ mkdir 01-minimal && cd 01-minimal
# 创建 main.c 和 build.ninja（按照01-minimal-build.md中的内容）
$ ninja
$ ./main
Hello, Ninja!
```

完成第一个示例后，按照推荐顺序依次学习后续示例。每个示例都是独立的完整项目，可以在单独的目录中完成。

---

## 常见问题

### Q: ninja: error: 'build.ninja' not found
A: 你不在包含 `build.ninja` 的目录中。使用 `cd` 切换到正确目录，或使用 `-f` 指定文件路径：`ninja -f path/to/build.ninja`。

### Q: 修改了头文件但Ninja没有重编译
A: 检查是否配置了 `depfile` 和 `deps = gcc`。确保编译命令包含 `-MMD -MF $out.d` 选项。如果 `.ninja_deps` 损坏，尝试 `ninja -t clean` 后重新构建。

### Q: 如何查看Ninja正在做什么？
A: 使用 `ninja -v` 显示完整命令，`ninja -d explain` 解释重建原因，`ninja -n` 干运行显示将要执行的命令。

### Q: Windows上可以使用这些示例吗？
A: 推荐使用 WSL2（Windows Subsystem for Linux）获得完整的 Linux 环境。也可以使用 Git Bash 或 MSYS2，但部分命令（如 `sleep`、`time`、`touch`）的行为可能略有差异。纯 Windows CMD/PowerShell 环境需要适当调整 shell 命令。

---

## 延伸阅读

- [Ninja 官方手册](https://ninja-build.org/manual.html)
- [概念文档](../concepts/index.md) —— 深入理解Ninja的设计原理
- [参考文档](../references/index.md) —— 源代码级别的参考
- [Ninja 源码仓库](https://github.com/ninja-build/ninja)
