---
type: Concept
title: 依赖图模型
description: Node-Edge 二分图结构详解，依赖类型、phony 规则、图遍历与拓扑排序
tags: [ninja, concept, dependency-graph, node, edge, bipartite-graph, phony, topology]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# 依赖图模型

Ninja 的核心数据结构是一个**有向二分图（Directed Bipartite Graph）**，由 Node（文件节点）和 Edge（命令边）两类顶点组成。理解这个图模型是理解 Ninja 一切行为的基础。

## Node-Edge 二分图

### 为什么是二分图？

传统构建系统（如 Make）采用"目标-依赖"模型，命令依附于目标文件。这种模型在处理多输出命令（如一次编译同时产生 `.o` 和 `.d`）和隐式输出时会遇到困难。Ninja 将文件（Node）和命令（Edge）都作为一等公民，形成二分图：

- **Node**：代表文件系统中的一个文件（源文件或构建产物）
- **Edge**：代表一条构建命令（将输入文件转换为输出文件）

Node 和 Edge 交替连接，图中的边总是从 Node 指向 Edge 或从 Edge 指向 Node，没有 Node→Node 或 Edge→Edge 的直接连接。

### 基本连接关系

```
     ┌──────┐ out_edges   ┌──────┐  inputs_    ┌──────┐
     │      │────────────→│      │←────────────│      │
     │ Node │             │ Edge │             │ Node │
     │(main │  in_edge    │(cc   │  outputs_   │(main │
     │ .o)  │←────────────│ cmd) │────────────→│ .c)  │
     │      │             │      │             │      │
     └──────┘             └──────┘             └──────┘
```

- 每个 Node 有一个 `in_edge_`（产生它的 Edge，即生产者）和多个 `out_edges_`（消费它的 Edge，即消费者）
- 每个 Edge 有多个 `inputs_`（输入 Node 列表）和多个 `outputs_`（输出 Node 列表）
- **一个 Node 只能有一个 in_edge_**——这意味着 Ninja 隐式禁止同一文件被多条命令生成

### 数据结构定义

Node 结构体的核心字段（见 [graph.h](../references/graph-source.md)）：

```cpp
struct Node {
  std::string path_;           // 文件路径（规范化后）
  uint64_t slash_bits_;        // 斜杠位置位掩码（用于路径反规范化）
  TimeStamp mtime_;            // 文件修改时间（-1 = 未知/不存在）
  ExistenceStatus exists_;     // 存在状态（Unknown/Missing/Exists）
  bool dirty_;                 // 是否需要重建
  Edge* in_edge_;              // 产生此文件的边（nullptr = 源文件）
  vector<Edge*> out_edges_;    // 依赖此文件的边
  int id_;                     // 唯一 ID
  // ...
};
```

Edge 结构体的核心字段：

```cpp
struct Edge {
  const Rule* rule_;               // 使用的规则
  vector<Node*> inputs_;           // 显式输入
  vector<Node*> outputs_;          // 显式输出
  vector<Node*> implicit_deps_;    // 隐式依赖（如头文件）
  vector<Node*> order_only_deps_;  // order-only 依赖
  vector<Node*> validation_deps_;  // 验证依赖
  vector<pair<Node*, bool>> implicit_outs_;  // 隐式输出
  BindingEnv env_;                 // 变量绑定环境
  Pool* pool_;                     // 执行池
  bool outputs_ready_;             // 所有输出是否就绪
  bool deps_loaded_;               // 头依赖是否已加载
  // ...
};
```

## Node 三种存在状态

每个 Node 有一个 `exists_` 字段，追踪文件在文件系统中的存在状态，取值为三态枚举：

```cpp
enum ExistenceStatus {
  ExistenceStatusUnknown = 0,  // 尚未 stat，状态未知
  ExistenceStatusMissing,      // 文件不存在（已 stat 确认）
  ExistenceStatusExists        // 文件存在（已 stat 确认）
};
```

三态设计（而非简单的存在/不存在二元）是为了**避免重复 stat 系统调用**：

- `Unknown`：还没调用过 `Stat()`，需要 stat 文件来确定状态
- `Missing`：已 stat 过，文件确认不存在（如源文件缺失是错误，构建产物不存在是正常的）
- `Exists`：已 stat 过，文件存在，`mtime_` 字段包含最新的修改时间

`StatIfNecessary()` 方法只在状态为 `Unknown` 时才真正调用 `stat()`：

```cpp
bool Node::StatIfNecessary(DiskInterface* disk_interface, string* err) {
  if (status_known())  // exists_ != Unknown
    return true;       // 已经 stat 过，直接返回
  return Stat(disk_interface, err);  // 首次 stat
}
```

这是 Ninja 的一个关键性能优化——构建过程中每个文件最多 stat 一次。

## Edge 五种依赖类型

Ninja 的 build 语句支持五种依赖关系，每种在 Edge 中对应不同的列表：

### 1. 显式输入（Explicit Inputs）

build 语句中冒号后面、`|` 之前的文件列表。这些是命令行中直接引用的输入文件，会出现在 `$in` 自动变量中。

```ninja
build main.o: cc main.c util.c
#              ↑↑↑↑↑↑↑↑↑↑↑↑↑ 显式输入
```

### 2. 隐式依赖（Implicit Dependencies）

`|` 后面、`||` 之前的文件列表。这些文件的修改会触发重编译，但不出现在 `$in` 中（即不传递给命令行）。典型用途：C/C++ 头文件。

```ninja
build main.o: cc main.c | main.h util.h
#                         ↑↑↑↑↑↑↑↑↑↑↑ 隐式依赖
```

隐式依赖通过 [depfile 机制](06-incremental-build.md) 自动发现，初始时可以在 build 语句中手动声明，后续由 deps log 缓存。

### 3. Order-only 依赖

`||` 后面、`|@` 之前的文件列表。这些文件必须在当前 Edge 执行**之前**存在，但它们的修改**不触发**当前 Edge 重编译。典型用途：目录创建。

```ninja
build obj/: phony
build main.o: cc main.c || obj/
#                           ↑↑↑ order-only：目录必须先创建，但目录 mtime 变化不重编译
```

### 4. 验证依赖（Validation Dependencies）

`|@` 后面的文件列表。Ninja 1.11+ 引入，这些依赖会在当前 Edge 完成后被构建（用于验证/测试），但不影响当前 Edge 的脏状态判断。如果验证失败，构建失败。

```ninja
build main: link main.o |@ main_test
#                              ↑↑↑↑↑↑↑ 验证依赖：链接完 main 后构建并运行测试
```

### 5. 隐式输出（Implicit Outputs）

编译器或工具一次调用可能产生多个输出文件。除了 build 语句中显式声明的输出外，额外产生的文件称为隐式输出，通过 `implicit_outs_` 列表追踪。典型场景：GCC `-MMD` 同时产生 `.o` 和 `.d` 文件。

```ninja
# GCC -c -MMD 同时产生 main.o 和 main.o.d
build main.o | main.o.d: cc main.c
#     ↑↑↑↑↑↑↑↑ 隐式输出（Ninja 新版本语法）
```

在较旧版本中，隐式输出在 dyndep 文件中声明。新版 Ninja 支持 `build out1 | implicit_out: rule in` 语法。

### 依赖类型语法总结

```
build outputs: rule explicit_inputs | implicit_deps || order_only_deps |@ validation_deps
      ↑↑↑↑↑↑↑             ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑   ↑↑↑↑↑↑↑↑↑↑↑↑↑↑   ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑   ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
      输出                显式输入           隐式依赖          order-only       验证依赖
```

| 分隔符 | 类型 | 影响 $in | 修改触发重编译 | 必须先构建 |
|--------|------|---------|---------------|-----------|
| `:` 后直接 | 显式输入 | ✅ 是 | ✅ 是 | ✅ 是 |
| `\|` | 隐式依赖 | ❌ 否 | ✅ 是 | ✅ 是 |
| `\|\|` | Order-only | ❌ 否 | ❌ 否 | ✅ 是 |
| `\|@` | 验证依赖 | ❌ 否 | 不直接相关 | ✅（但在当前 Edge 之后） |
| 输出侧 `\|` | 隐式输出 | N/A | N/A | N/A |

## phony 规则

phony 是 Ninja 内置的特殊规则，用于创建**别名**和**聚合目标**。phony Edge 不执行任何实际命令，只传播 mtime。

### 别名

```ninja
build all: phony main test libfoo.a
#  "all" 是 main、test、libfoo.a 的别名
#  ninja all → 构建 main、test、libfoo.a
```

### 聚合目标

```ninja
build clean: phony
#  空 phony 目标，配合 -t clean 使用

build objs: phony main.o util.o foo.o
#  "objs" 聚合所有 .o 文件
```

### mtime 传播机制

phony Edge 不执行命令，它通过 `UpdatePhonyMtime()` 传播 mtime：
- phony Node 的 mtime 取其**所有输入中最新的 mtime**
- 如果 phony 没有输入，mtime 设为 0（总是需要"构建"但无操作）
- 当 phony 输入的 mtime 更新时，phony Node 的 mtime 也更新

```
main.o (mtime=100) ──→ phony "objs" (mtime=100)
util.o (mtime=200) ──→
foo.o  (mtime=150) ──→
```

phony 机制使得虚拟目标（如 `all`、`install`、`test`）可以自然地融入依赖图，不需要特殊处理。

## 图遍历

Ninja 从构建目标出发，**反向遍历**依赖图来确定需要执行的 Edge。

### 反向遍历算法

```
给定目标 Node T:
  如果 T.dirty 或 T 不存在:
    edge = T.in_edge_
    如果 edge 是 phony:
      递归遍历 edge 的所有 inputs_
    否则:
      标记 edge 为需要执行（kWantToStart）
      递归遍历 edge 的所有 inputs_、implicit_deps_、order_only_deps_
```

遍历时沿 `in_edge_` 反向追踪生产者链：

```
main (目标)
  │ in_edge: link Edge
  ↓
link Edge 需要执行吗？
  ├─ inputs: main.o → 检查 main.o
  └─ inputs: util.o → 检查 util.o
       │
       ↓
main.o 的 in_edge: cc Edge
cc Edge 需要执行吗？
  └─ inputs: main.c (源文件，in_edge=nullptr) → 存在且有 mtime，不需要构建
```

### 拓扑排序

执行顺序必须满足：一个 Edge 的所有输入 Node 都就绪（其生产者 Edge 已完成）后，该 Edge 才能执行。这本质上是 DAG（有向无环图）的拓扑排序。

Ninja 通过 Plan 实现增量式拓扑排序：
1. 初始时，所有源文件（无 in_edge 的 Node）是"就绪"的
2. 当一个 Edge 完成时，其输出 Node 标记为就绪
3. 检查该 Node 的 out_edges_（消费者 Edge），看它们的所有输入是否都就绪
4. 如果是，将该 Edge 加入就绪队列

这比预先计算完整拓扑序列更灵活，因为它能处理 dyndep（动态依赖加载后新节点加入图）的情况。

## default 目标

如果命令行没有指定目标，Ninja 构建 `default` 语句指定的目标：

```ninja
default main test
#  ninja → 构建 main 和 test
```

如果没有 `default` 语句，Ninja 构建 manifest 中**第一个** build 语句的输出（不包括以 `.` 开头的输出）。

可以有多个 `default` 语句，它们是累积的：

```ninja
default main
default test
# 等价于 default main test
```

## 多文件 C 项目图结构示例

以下是一个多文件 C 项目及其对应的依赖图：

**文件**：
- `main.c`（包含 `main.h`、`util.h`）
- `util.c`（包含 `util.h`）
- `main.h`
- `util.h`

**build.ninja**：

```ninja
rule cc
  command = gcc -c $in -o $out
  depfile = $out.d
  deps = gcc

rule link
  command = gcc $in -o $out

build main.o: cc main.c | main.h util.h
build util.o: cc util.c | util.h
build main: link main.o util.o

default main
```

**依赖图**：

```
                    ┌─────────┐
                    │  main   │ ← 目标（可执行文件）
                    └────┬────┘
                         │ in_edge = link Edge
                    ┌────┴────┐
                    │  link   │ ← 链接命令
                    └────┬────┘
              inputs_/         \inputs_
          ┌───────┘             └───────┐
    ┌─────┴─────┐                 ┌─────┴─────┐
    │  main.o   │                 │  util.o   │
    └─────┬─────┘                 └─────┬─────┘
          │ in_edge = cc Edge           │ in_edge = cc Edge
    ┌─────┴─────┐                 ┌─────┴─────┐
    │ cc main.o │                 │ cc util.o │ ← 编译命令
    └─────┬─────┘                 └─────┬─────┘
     inputs/|implicit             inputs/|implicit
     ┌──┘  ┌──┴──┐                 ┌─┘    └─┐
┌────┴──┐┌─┴───┐┌┴─────┐     ┌────┴──┐ ┌────┴──┐
│main.c ││main.││util. │     │util.c │ │util.h │
│(源)   ││h    ││h     │     │(源)   │ │(头)   │
└───────┘└─────┘└──────┘     └───────┘ └───────┘
```

**构建顺序（拓扑排序）**：
1. `cc main.c → main.o`（依赖 main.c、main.h、util.h）
2. `cc util.c → util.o`（依赖 util.c、util.h）
3. `link main.o util.o → main`（依赖 main.o、util.o）

步骤 1 和 2 可以**并行执行**，因为它们互不依赖。

## 相关概念

- [架构总览](02-architecture-overview.md) — 四大核心模块的位置
- [构建执行管线](04-build-execution.md) — Plan 如何遍历图并调度 Edge
- [增量构建机制](06-incremental-build.md) — 脏状态计算与依赖扫描
- [Manifest 语言详解](05-manifest-language.md) — build 语句的完整语法
- [图结构 API](../references/graph-source.md) — Node、Edge、DependencyScan 的完整 API
