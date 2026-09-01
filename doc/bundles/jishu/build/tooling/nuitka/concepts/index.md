---
okf_version: "0.2"
type: concepts-index
title: "Nuitka 概念文档索引"
description: "Nuitka V4.1rc11 核心概念文档——按学习路径排列"
---

# Nuitka 概念文档索引

本索引列出Nuitka编译器核心概念的14篇文档，按学习路径从入门到高级排列。

## 入门篇

| 序号 | 文档 | 说明 |
|------|------|------|
| 00 | [Nuitka 简介](00-introduction.md) | Nuitka是什么，与CPython/PyPy/Cython的区别 |
| 01 | [编译流水线](01-compilation-pipeline.md) | 四阶段流水线：AST→IR→优化→C生成→C编译 |
| 02 | [架构总览](02-architecture-overview.md) | 源码目录分层架构与模块依赖关系 |

## 基础篇

| 序号 | 文档 | 说明 |
|------|------|------|
| 03 | [AST 树构建](03-ast-tree-building.md) | CPython AST→Nuitka IR树的dispatch调度与递归构建 |
| 04 | [节点 IR 系统](04-node-ir-system.md) | NodeCheckMetaClass元类、基类层次、Mixin组合 |
| 05 | [类型 Shape 系统](05-type-shapes.md) | ShapeBase层次、12种内置类型单例、类型推断 |
| 06 | [模块导入系统](06-module-import-system.md) | locateModule定位、recurseTo决策、ImportCache缓存 |

## 核心篇

| 序号 | 文档 | 说明 |
|------|------|------|
| 07 | [优化遍机制](07-optimization-passes.md) | TagSet不动点迭代、SSA值追踪、常量折叠、内联 |
| 08 | [C 代码生成](08-c-code-generation.md) | Context层次、Emitter、双dispatch字典、临时变量 |
| 09 | [C 编译后端](09-c-compilation-backend.md) | SCons构建、编译器检测、static_src运行时、缓存 |

## 高级篇

| 序号 | 文档 | 说明 |
|------|------|------|
| 10 | [打包分发](10-freezer-distribution.md) | Standalone/Onefile、DLL检测、数据文件、反膨胀 |
| 11 | [插件系统](11-plugin-system.md) | NuitkaPluginBase 60+钩子、YAML插件、34标准插件 |
| 12 | [变量与闭包](12-variables-closures.md) | Variable层次、ClosureGiver/Taker、C分配策略 |
| 13 | [命令行选项系统](13-cli-options.md) | 500+选项分类、配置文件、环境变量、速查表 |

## 学习路径

```
00-introduction → 01-compilation-pipeline → 02-architecture-overview
    → 03-ast-tree-building → 04-node-ir-system → 05-type-shapes
    → 06-module-import-system → 07-optimization-passes
    → 08-c-code-generation → 09-c-compilation-backend
    → 10-freezer-distribution → 11-plugin-system
    → 12-variables-closures → 13-cli-options
```

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-compilation-pipeline
02-architecture-overview
03-ast-tree-building
04-node-ir-system
05-type-shapes
06-module-import-system
07-optimization-passes
08-c-code-generation
09-c-compilation-backend
10-freezer-distribution
11-plugin-system
12-variables-closures
13-cli-options
```
