---
type: Concept
title: 架构总览
description: Ninja 四大核心模块架构、构建流程七步骤、数据流与关键设计决策
tags: [ninja, concept, architecture, parser, state, plan, builder, overview]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# 架构总览

Ninja 的内部架构采用分层设计，从 manifest 文件解析到命令执行，经过四大核心模块处理。本章从宏观视角描述 Ninja 的整体架构、数据流和构建流程。

## 整体架构

Ninja 的核心由四大模块组成，形成清晰的流水线：

```
┌─────────────────────────────────────────────────────────────────┐
│                        Ninja 构建引擎                            │
│                                                                 │
│  ┌─────────────┐   ┌─────────────────────┐   ┌───────────────┐ │
│  │  解析层      │   │  状态层              │   │  计划层        │ │
│  │  Parser     │──→│  State (Graph)       │──→│  Plan         │ │
│  │  Lexer      │   │  Node / Edge / Rule  │   │  就绪队列      │ │
│  │             │   │  Pool / BindingEnv   │   │  优先级调度    │ │
│  └─────────────┘   └─────────────────────┘   └───────┬───────┘ │
│        ↑                                             │         │
│        │ build.ninja                                 ↓         │
│  ┌─────────────┐   ┌─────────────────────┐   ┌───────────────┐ │
│  │  持久层      │   │  执行层              │   │  调度器        │ │
│  │  BuildLog   │←──│  Builder             │←──│  CommandRunner│ │
│  │  DepsLog    │   │  主循环控制           │   │  Subprocess   │ │
│  │             │   │  错误处理             │   │  Jobserver    │ │
│  └─────────────┘   └─────────────────────┘   └───────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 模块职责

| 模块 | 核心文件 | 主要类型 | 职责 |
|------|---------|---------|------|
| **解析层** | [manifest_parser.h/cc](../references/parser-source.md)、[lexer.h/cc](../references/parser-source.md) | ManifestParser、Lexer、Token | 词法分析、语法解析、构建 State 对象 |
| **状态层** | [state.h/cc](../references/state-source.md)、[graph.h/cc](../references/graph-source.md)、[eval_env.h/cc](../references/eval-source.md) | State、Node、Edge、Rule、Pool、BindingEnv | 维护构建图（二分图）、规则、变量绑定 |
| **计划层** | [build.h/cc](../references/build-source.md) | Plan、EdgePriorityQueue、DependencyScan | 脏状态扫描、就绪边调度、关键路径计算 |
| **执行层** | [build.h/cc](../references/build-source.md)、[command_runner.h](../references/util-source.md)、[subprocess.h/cc](../references/util-source.md) | Builder、CommandRunner、SubprocessSet、Subprocess | 命令执行、子进程管理、IO 多路复用 |
| **持久层** | [build_log.h/cc](../references/logs-source.md)、[deps_log.h/cc](../references/logs-source.md) | BuildLog、DepsLog | 二进制日志持久化，支持增量构建 |

## 四大核心模块详解

### 1. 解析器（Parser/Lexer）

解析层负责将 `build.ninja` 文本文件转换为内存中的构建图。

```
build.ninja 文本
    │
    ↓
┌─────────┐  Token流   ┌────────────────┐  Node/Edge   ┌─────────┐
│  Lexer  │ ─────────→ │ ManifestParser │ ───────────→ │  State  │
└─────────┘            └────────────────┘              └─────────┘
```

- **Lexer**：逐字符扫描输入，产生 Token 流。Token 类型包括 `kBuild`、`kRule`、`kPool`、`kDefault`、`kPipe`、`kPipe2`、`kPipeAt`、`kIdentifier`、`kEquals` 等约 20 种。
- **ManifestParser**：递归下降解析器，处理 rule/build/pool/default/include/subninja/变量赋值 七种语句。解析 build 语句时创建 Edge 和 Node 对象，解析 rule 时创建 Rule 对象。

详见 [Manifest 语言详解](05-manifest-language.md) 和 [Manifest解析器 API](../references/parser-source.md)。

### 2. 状态（State/Graph）

状态层维护构建过程中所有数据的内存表示，核心是 Node-Edge 二分图。

```
         ┌──────┐  in_edge   ┌──────┐  inputs_   ┌──────┐
         │ Node │←──────────│ Edge │───────────→│ Node │
         │(文件)│ out_edges_ │(命令) │ outputs_  │(文件) │
         └──────┘──────────→└──────┘←───────────└──────┘
                        outputs_
```

- **State**：全局状态容器，持有所有 Node、Edge、Rule、Pool，以及文件级变量绑定。
- **Node**：表示文件系统中的一个文件（输入源文件或构建产物），记录路径、mtime、脏状态、存在状态。
- **Edge**：表示一条构建命令，引用输入/输出 Node，关联一个 Rule，持有自己的变量绑定环境。
- **Rule**：命令模板，定义 command、depfile、deps、pool、rspfile 等属性。
- **Pool**：并发控制池，限制特定类型命令的最大并行数。
- **BindingEnv**：链式变量绑定环境，支持作用域嵌套。

详见 [依赖图模型](03-dependency-graph.md) 和 [图结构 API](../references/graph-source.md)。

### 3. 计划（Plan）

计划层负责决定哪些 Edge 需要执行、以什么顺序执行。

```
目标 Node
    │
    ↓ AddTarget()
┌──────────────────────────────────────┐
│  Plan                                │
│  ┌───────────────────────────────┐   │
│  │ want_: map<Edge*, Want>       │   │  ← 标记哪些 Edge 需要执行
│  │   kWantNothing / kWantToStart │   │
│  │   / kWantToFinish             │   │
│  ├───────────────────────────────┤   │
│  │ ready_: EdgePriorityQueue     │   │  ← 所有依赖满足的 Edge
│  ├───────────────────────────────┤   │
│  │ ComputeCriticalPath()         │   │  ← 关键路径优先级计算
│  └───────────────────────────────┘   │
│              │ FindWork()             │
└──────────────┼───────────────────────┘
               ↓
           下一个 Edge
```

- **Plan** 维护一个 `want_` 映射，追踪每个 Edge 的需求状态（不需要/需要启动/需要完成）。
- **DependencyScan::RecomputeDirty** 递归扫描依赖图，标记脏 Node 和需要执行的 Edge。
- **ready_** 是一个按关键路径长度排序的优先级队列，`FindWork()` 从中取出最高优先级的 Edge。
- **ComputeCriticalPath()** 计算每个 Edge 到终点的最长路径，用于优先级调度——优先执行关键路径上的任务。

详见 [构建执行管线](04-build-execution.md) 和 [构建执行 API](../references/build-source.md)。

### 4. 执行（Builder/CommandRunner）

执行层负责实际运行命令并管理子进程。

```
    Edge (来自 Plan)
        │
        ↓ StartEdge()
┌─────────────────┐     ┌──────────────────┐
│     Builder      │     │  CommandRunner   │
│  主循环控制器     │────→│  (抽象接口)       │
│                 │     │  CanRunMore()    │
│  FindWork()     │     │  StartCommand()  │
│  StartEdge()    │     │  WaitForCommand()│
│  FinishEdge()   │     └────────┬─────────┘
│                 │              │
└─────────────────┘     ┌────────┴─────────┐
                        │ SubprocessSet    │
                        │ (IO多路复用)      │
                        │  select/poll/epoll│
                        │  WaitForMultiple- │
                        │  Objects (Win)    │
                        └────────┬─────────┘
                                 ↓
                          ┌─────────────┐
                          │ Subprocess   │
                          │ (子进程)      │
                          │ gcc/ld/...   │
                          └─────────────┘
```

- **Builder**：顶层控制器，驱动 `FindWork → StartEdge → WaitForCommand → EdgeFinished` 主循环。
- **CommandRunner**：抽象命令执行接口，`SubprocessCommandRunner` 是其实现，使用子进程执行实际命令。
- **SubprocessSet**：管理多个子进程的 IO 多路复用，POSIX 上使用 `select`/`poll`/`epoll`，Windows 上使用 `WaitForMultipleObjects`。
- **Subprocess**：封装单个子进程的创建、管道 IO 和等待。

详见 [构建执行管线](04-build-execution.md) 和 [并行执行与并发控制](07-parallel-execution.md)。

## 构建流程七步骤

当执行 `ninja` 命令时，Ninja 按以下七个步骤完成构建：

```
┌────────────────────────────────────────────────────────────────┐
│                     Ninja 构建流程                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ① 解析 Manifest                                              │
│     build.ninja → Lexer → Parser → State graph               │
│                         │                                      │
│                         ↓                                      │
│  ② 重建 Manifest（可选）                                       │
│     如果 build.ninja 自身有构建规则（如 CMake 重新生成），       │
│     先执行 manifest 重建，然后重新解析                          │
│                         │                                      │
│                         ↓                                      │
│  ③ 加载持久化日志                                              │
│     .ninja_log (BuildLog) → 命令哈希/历史mtime                │
│     .ninja_deps (DepsLog) → 缓存的头依赖                      │
│                         │                                      │
│                         ↓                                      │
│  ④ 脏状态扫描                                                  │
│     DependencyScan::RecomputeDirty()                          │
│     递归遍历目标依赖，比较 mtime/命令哈希/depfile              │
│     标记 dirty Node 和需要执行的 Edge                          │
│                         │                                      │
│                         ↓                                      │
│  ⑤ 构建计划                                                    │
│     Plan::AddTarget() → ScheduleInitialEdges()                │
│     ComputeCriticalPath() → 准备 ready_ 队列                  │
│                         │                                      │
│                         ↓                                      │
│  ⑥ 并行执行                                                    │
│     Builder 主循环：                                           │
│     while (plan.more_to_do()):                                │
│       while (CanRunMore() && work_ready()):                   │
│         edge = plan.FindWork() → StartEdge()                  │
│       WaitForCommand() → EdgeFinished() → 记录日志            │
│                         │                                      │
│                         ↓                                      │
│  ⑦ 记录日志                                                    │
│     BuildLog::RecordCommand() → .ninja_log                    │
│     DepsLog::RecordDeps() → .ninja_deps                       │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 步骤详解

**步骤 ① 解析 Manifest**：[ManifestParser::Load](../references/parser-source.md) 读取 `build.ninja` 文件，通过 Lexer 进行词法分析，Parser 构建完整的 State 图。如果 manifest 中通过 `include`/`subninja` 引用了其他文件，Parser 会递归加载。

**步骤 ② 重建 Manifest**：如果 `build.ninja` 本身是某个 build edge 的输出（如 CMake 配置的 `build build.ninja: RERUN_CMAKE`），Ninja 会先执行构建 `build.ninja` 的命令。如果 manifest 被重新生成，Ninja 从头重新解析（步骤 ①）。这确保构建规则始终是最新的。

**步骤 ③ 加载日志**：Ninja 加载 `.ninja_log`（记录历史命令的哈希值和输出 mtime）和 `.ninja_deps`（缓存的头文件依赖列表）。这些二进制文件使 Ninja 无需在每次启动时重新扫描所有依赖。

**步骤 ④ 脏状态扫描**：[DependencyScan::RecomputeDirty](../references/graph-source.md) 从目标 Node 开始递归遍历依赖图，对每个 Node 调用 `Stat()` 获取文件 mtime，比较输出 mtime 与输入 mtime，同时与 BuildLog 中的命令哈希对比，确定哪些 Edge 需要重新执行。

**步骤 ⑤ 构建计划**：[Plan::AddTarget](../references/build-source.md) 将目标加入构建计划，`ScheduleInitialEdges()` 遍历所有依赖 Edge，将需要执行的 Edge 标记为 `kWantToStart`，所有依赖满足的 Edge 加入 `ready_` 优先级队列。

**步骤 ⑥ 并行执行**：Builder 主循环持续从 Plan 获取就绪 Edge，提交给 CommandRunner 执行。多个子进程并行运行，SubprocessSet 通过 IO 多路复用等待任一子进程完成。命令完成后，`EdgeFinished()` 更新 Node 状态，并检查是否有新的 Edge 变为就绪。

**步骤 ⑦ 记录日志**：每个 Edge 执行成功后，Builder 将命令哈希、执行时间、输出 mtime 记录到 BuildLog，将头文件依赖记录到 DepsLog。日志在构建结束时写入磁盘。

## 数据流

完整的数据流从文本文件到命令执行，再到持久化日志：

```
build.ninja (文本)
    │
    ▼ Lexer::Start / ReadToken
Tokens (kBuild, kRule, kIdentifier, ...)
    │
    ▼ ManifestParser::Parse
State graph (Nodes + Edges + Rules + Pools + Bindings)
    │
    ▼ DependencyScan::RecomputeDirty
Dirty state (dirty Nodes, wanted Edges)
    │
    ▼ Plan::ScheduleInitialEdges / ComputeCriticalPath
ready_ queue (priority-sorted Edges)
    │
    ▼ Plan::FindWork / Builder::StartEdge
Commands (shell commands with $in/$out expanded)
    │
    ▼ Subprocess::Start
Process execution (gcc, ld, ...)
    │
    ▼ Command completed
BuildLog entries + DepsLog entries
    │
    ▼ BuildLog::RecordCommand / DepsLog::RecordDeps
.ninja_log + .ninja_deps (binary, on disk)
```

## 关键设计决策

Ninja 的架构体现了几个关键设计决策，这些决策共同造就了 Ninja 的速度和可靠性：

### 1. 二分图模型

构建依赖表示为 Node（文件）和 Edge（命令）的二分图，而非传统 Make 风格的"目标-依赖"模型。这使得隐式输出、多输出命令、phony 规则等场景都能自然表达。详见 [依赖图模型](03-dependency-graph.md)。

### 2. 优先级调度

就绪 Edge 不是简单 FIFO 执行，而是通过 `ComputeCriticalPath()` 计算关键路径，优先执行在关键路径上的命令。这最大化了并行效率，减少了总构建时间。详见 [构建执行管线](04-build-execution.md)。

### 3. 延迟求值

Rule 中的命令字符串包含变量引用（如 `$in`、`$cflags`），这些引用在解析时不立即求值，而是通过 [EvalString](../references/eval-source.md) 记录"文本片段+变量引用"，等到 Edge 执行时才在该 Edge 的变量环境中求值。这使得 build 块可以覆盖 rule 级变量。详见 [Manifest 语言详解](05-manifest-language.md)。

### 4. 二进制日志

BuildLog 和 DepsLog 使用自定义二进制格式而非文本格式。定长记录、追加写入、快速加载是设计目标。启动时 Ninja 可以在毫秒级加载数万条历史记录，而文本日志需要逐行解析。详见 [Ninja 内部实现](09-ninja-internals.md)。

### 5. 单线程事件循环

Ninja 不使用多线程，而是采用单线程事件循环 + 多子进程模型。这避免了线程同步开销，利用了编译/链接等构建任务本身就是独立进程的特性。IO 多路复用（select/poll/epoll/WaitForMultipleObjects）高效地等待子进程完成。详见 [并行执行与并发控制](07-parallel-execution.md)。

## 相关概念

- [Ninja 简介](00-introduction.md) — 设计哲学和生态定位
- [快速开始](01-getting-started.md) — 编译安装和第一个构建
- [依赖图模型](03-dependency-graph.md) — Node-Edge 二分图详解
- [构建执行管线](04-build-execution.md) — Builder/Plan/CommandRunner 的详细工作机制
- [图结构 API](../references/graph-source.md) — Node/Edge/DependencyScan 的完整 API 参考
- [构建执行 API](../references/build-source.md) — Plan/Builder 的完整 API 参考
