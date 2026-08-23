---
type: ReferenceIndex
title: Ninja 信源参考索引
description: 按源码模块组织的 Ninja API 参考文档导航
tags: [reference, index, api, source-code]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# Ninja 信源参考索引

本索引列出所有基于 Ninja 源码的 API 参考文档，按核心模块组织。

## 核心数据结构

| 文档 | 源文件 | 核心类型 |
|------|--------|---------|
| [图结构 API](graph-source.md) | `src/graph.h/cc` | Node、Edge、DependencyScan、EdgePriorityQueue |
| [状态管理 API](state-source.md) | `src/state.h/cc` | State、Pool |

## 构建执行

| 文档 | 源文件 | 核心类型 |
|------|--------|---------|
| [构建执行 API](build-source.md) | `src/build.h/cc` | Plan、Builder、BuildConfig、CommandRunner、SubprocessCommandRunner |

## 解析与求值

| 文档 | 源文件 | 核心类型 |
|------|--------|---------|
| [Manifest解析器 API](parser-source.md) | `src/manifest_parser.h/cc`、`src/lexer.h/cc` | ManifestParser、Lexer、Token 枚举 |
| [变量求值 API](eval-source.md) | `src/eval_env.h/cc` | Rule、BindingEnv、EvalString |

## 持久化与日志

| 文档 | 源文件 | 核心类型 |
|------|--------|---------|
| [日志系统 API](logs-source.md) | `src/build_log.h/cc`、`src/deps_log.h/cc`、`src/dyndep.h/cc` | BuildLog、DepsLog、Dyndeps、DependencyScan |

## 工具与基础设施

| 文档 | 源文件 | 核心类型 |
|------|--------|---------|
| [工具与IO API](util-source.md) | `src/util.h/cc`、`src/disk_interface.h`、`src/subprocess.h/cc`、`src/jobserver.h/cc`、`src/metrics.h/cc` | DiskInterface、StringPiece、Subprocess、SubprocessSet、Jobserver::Client、Metrics |

## 主入口

| 文档 | 源文件 | 核心类型 |
|------|--------|---------|
| [主入口 API](main-source.md) | `src/ninja.cc` | NinjaMain、Options、Tool 函数、Status、Clean、GraphViz |
