---
type: ConceptIndex
title: Ninja 概念文档索引
description: Ninja 构建系统概念文档导航，按学习路径分组：入门→核心→深入→高级
tags: [ninja, concept, index, learning-path]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# Ninja 概念文档索引

本目录包含 Ninja 构建系统的核心概念文档，按学习路径组织，建议按编号顺序阅读。

## 学习路径

```
入门篇 → 核心篇 → 深入篇 → 高级篇
```

**入门篇**回答"Ninja 是什么、怎么用"；**核心篇**深入理解依赖图、执行管线和语言语法；**深入篇**掌握增量构建、并行控制和工具使用；**高级篇**面向源码阅读者和生成器开发者。

---

## 入门篇

了解 Ninja 的定位、基本用法和宏观架构。

| 编号 | 文档 | 描述 |
|------|------|------|
| 00 | [Ninja 简介](00-introduction.md) | Ninja 是什么：Google 开发的专注于速度的小型构建系统；设计哲学（速度优先、极简设计、职责分离）；与 Make 的对比；适用/不适用场景；核心特性与生态概览 |
| 01 | [快速开始](01-getting-started.md) | 编译安装 Ninja；第一个 build.ninja（编译 C 程序）；基本命令（ninja/-j/-n/-v/-t clean/-t targets）；build.ninja 文件结构；自动变量（$in/$out 等）；从 CMake 生成 |
| 02 | [架构总览](02-architecture-overview.md) | 四大核心模块架构图（Parser/Lexer → State/Graph → Plan → Builder/CommandRunner）；构建流程七步骤；数据流；关键设计决策（二分图、优先级调度、延迟求值、二进制日志、单线程事件循环） |

---

## 核心篇

深入理解 Ninja 的数据模型、执行机制和语法规范。

| 编号 | 文档 | 描述 |
|------|------|------|
| 03 | [依赖图模型](03-dependency-graph.md) | Node-Edge 二分图详解；Node 三种存在状态（Unknown/Missing/Exists）；Edge 五种依赖类型（显式输入/隐式依赖/order-only/验证依赖/隐式输出）；phony 规则与 mtime 传播；图遍历与拓扑排序；多文件 C 项目图结构示例 |
| 04 | [构建执行管线](04-build-execution.md) | Builder 主循环（FindWork→StartEdge→WaitForCommand→EdgeFinished）；Plan 工作机制（want_映射/ready_优先级队列/计数）；Edge 生命周期（创建→dirty→等待→就绪→启动→执行→完成）；关键路径调度（ComputeCriticalPath）；错误处理（-k 选项）；BuildConfig 配置；Subprocess IO 多路复用 |
| 05 | [Manifest 语言详解](05-manifest-language.md) | 七种语法元素（变量/rule/build/pool/default/include/subninja）；Lexer Token 类型；Rule 属性完整说明（command/description/depfile/deps/generator/restat/pool/rspfile）；Build 语句语法（四种依赖分隔符）；变量系统与转义序列；作用域链（文件级→rule级→build块级）；自动变量详解；EvalString 延迟求值机制；完整示例 |

---

## 深入篇

掌握增量构建原理、并行调优和诊断工具。

| 编号 | 文档 | 描述 |
|------|------|------|
| 06 | [增量构建机制](06-incremental-build.md) | mtime 基础检测；Stat/StatIfNecessary 缓存；DependencyScan::RecomputeDirty 递归算法；depfile 机制（GCC -MMD / MSVC /showIncludes）；DepsLog 二进制日志（.ninja_deps）格式与生命周期；restat 优化；命令哈希检测（.ninja_log）；dyndep 动态依赖；-d explain 调试增量构建 |
| 07 | [并行执行与并发控制](07-parallel-execution.md) | 单线程事件循环+多子进程并行模型；-j 参数控制并行数；Pool 机制（console 池/自定义池）；Pool 计数机制；Jobserver 集成（与 GNU Make 共享令牌）；SubprocessSet IO 多路复用（select/poll/epoll/WaitForMultipleObjects）；关键路径优先调度；并行构建最佳实践 |
| 08 | [子命令与工具](08-subcommands-tools.md) | -t 子命令完整说明：clean/cleandead/compdb/graph/targets/commands/query/deps/inputs/rules/recompact/restat/missingdeps/browse；-d 调试选项（explain/stats/keeprsp/keepdepfile）；实用命令组合；GraphViz 可视化 |

---

## 高级篇

面向源码阅读者、性能调优者和生成器开发者。

| 编号 | 文档 | 描述 |
|------|------|------|
| 09 | [Ninja 内部实现](09-ninja-internals.md) | 源码文件组织；StringPiece 零拷贝字符串；FNVHash 哈希；PathCanonicalize 路径规范化与 slash_bits；DiskInterface 磁盘抽象；METRIC 宏与 ScopedMetric 性能指标；.ninja_log 二进制格式；.ninja_deps 二进制格式；Windows/POSIX 平台抽象；内存管理；十大性能优化总结 |
| 10 | [构建生成器集成](10-build-generators.md) | 为什么 Ninja 文件不手写；CMake 集成（-G Ninja/常用配置/生成器规则）；Meson 集成（meson setup）；gn 集成（gn gen）；手写 Ninja 的合理场景；编写自定义生成器（ninja_syntax.py/depfile/Pool/rspfile/generator规则）；compile_commands.json 与工具链集成；最佳实践清单 |

---

## 相关资源

| 资源 | 路径 | 说明 |
|------|------|------|
| 信源参考 | [references/](../references/index.md) | 按源码模块组织的 API 参考文档 |
| 源码事实清单 | [facts.md](../facts.md) | R阶段产出：零推测事实，每条指向源码位置 |
| 架构洞察 | [insights.md](../insights.md) | I阶段产出：核心洞察四元组与可复用设计模式 |

## API 参考快速索引

| 概念文档 | 主要相关 API 参考 |
|---------|------------------|
| [依赖图模型](03-dependency-graph.md) | [图结构 API](../references/graph-source.md)（Node/Edge/DependencyScan） |
| [构建执行管线](04-build-execution.md) | [构建执行 API](../references/build-source.md)（Plan/Builder/BuildConfig） |
| [Manifest 语言详解](05-manifest-language.md) | [Manifest解析器 API](../references/parser-source.md)（ManifestParser/Lexer）、[变量求值 API](../references/eval-source.md)（Rule/BindingEnv/EvalString） |
| [增量构建机制](06-incremental-build.md) | [日志系统 API](../references/logs-source.md)（BuildLog/DepsLog/Dyndeps） |
| [并行执行与并发控制](07-parallel-execution.md) | [工具与IO API](../references/util-source.md)（Subprocess/Jobserver）、[状态管理 API](../references/state-source.md)（Pool） |
| [子命令与工具](08-subcommands-tools.md) | [主入口 API](../references/main-source.md)（NinjaMain/Tool函数） |
| [Ninja 内部实现](09-ninja-internals.md) | 全部 API 参考 |
| [构建生成器集成](10-build-generators.md) | [Manifest解析器 API](../references/parser-source.md) |

```{toctree}
:hidden:

00-introduction
01-getting-started
02-architecture-overview
03-dependency-graph
04-build-execution
05-manifest-language
06-incremental-build
07-parallel-execution
08-subcommands-tools
09-ninja-internals
10-build-generators
```
