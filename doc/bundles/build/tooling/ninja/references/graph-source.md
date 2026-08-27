---
type: Reference
title: 图结构 API 参考
description: src/graph.h/cc 源码参考——Node、Edge、DependencyScan 完整 API
tags: [reference, api, graph, node, edge, dependency-scan, c++]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ninja-graph
    title: src/graph.h
    path: external/libs/tools/ninja/src/graph.h
  - id: ninja-graph-cc
    title: src/graph.cc
    path: external/libs/tools/ninja/src/graph.cc
---

# 图结构 API 参考

> 信源文件：graph.h、graph.cc

本文档记录 Ninja 依赖图核心数据结构的完整 API。

## Node 结构体

**头文件**：`src/graph.h`

Node 表示构建图中的一个文件节点（输入或输出）。

### 构造函数

```cpp
explicit Node(const std::string& path, uint64_t slash_bits);
```

- `path`：规范化后的文件路径
- `slash_bits`：路径中斜杠位置的位掩码，用于 PathDecanonicalized() 反规范化

### 状态查询方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Stat(DiskInterface*, string* err)` | `bool` | 查询文件系统获取 mtime 和存在状态 |
| `StatIfNecessary(DiskInterface*, string* err)` | `bool` | 仅在状态未知时 Stat |
| `exists() const` | `bool` | 文件是否存在（exists_ == ExistenceStatusExists） |
| `status_known() const` | `bool` | 状态是否已知（非 Unknown） |
| `mtime() const` | `TimeStamp` | 文件修改时间（-1 表示未知/不存在） |
| `dirty() const` | `bool` | 节点是否标记为脏（需要重建） |
| `dyndep_pending() const` | `bool` | dyndep 是否待加载 |

### 状态修改方法

| 方法 | 说明 |
|------|------|
| `MarkDirty()` | 标记为脏（dirty_ = true） |
| `set_dirty(bool)` | 设置脏标志 |
| `MarkMissing()` | 标记文件缺失 |
| `UpdatePhonyMtime(TimeStamp)` | 更新 phony 节点的 mtime |
| `ResetState()` | 重置节点状态到初始值 |
| `set_dyndep_pending(bool)` | 设置 dyndep 待加载标志 |
| `set_generated_by_dep_loader(bool)` | 设置是否由 dep_loader 生成 |

### 图连接方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `in_edge() const` | `Edge*` | 产生此节点的命令边（nullptr 表示源文件） |
| `out_edges() const` | `const vector<Edge*>&` | 消费此节点的命令边列表 |
| `validation_out_edges() const` | `const vector<Edge*>&` | 以此节点为 validation 依赖的边 |
| `set_in_edge(Edge*)` | `void` | 设置产生此节点的边 |
| `AddOutEdge(Edge*)` | `void` | 添加消费边 |
| `AddValidationOutEdge(Edge*)` | `void` | 添加验证输出边 |

### 属性方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `path() const` | `const string&` | 规范化路径 |
| `PathDecanonicalized() const` | `string` | 反规范化路径（恢复平台路径分隔符） |
| `slash_bits() const` | `uint64_t` | 斜杠位掩码 |
| `id() const` | `int` | 全局唯一 ID（-1 表示未分配） |
| `set_id(int)` | `void` | 设置 ID |
| `generated_by_dep_loader() const` | `bool` | 是否由 dep loader 生成 |
| `Dump(const char* prefix) const` | `void` | 调试输出 |

### ExistenceStatus 枚举

```cpp
enum ExistenceStatus : char {
  ExistenceStatusUnknown = 0,  // 尚未 stat
  ExistenceStatusMissing,      // stat 确认不存在
  ExistenceStatusExists        // stat 确认存在
};
```

---

## Edge 结构体

**头文件**：`src/graph.h`

Edge 表示构建图中的一条构建命令（build 语句）。

### 核心成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `rule_` | `const Rule*` | 使用的构建规则 |
| `inputs_` | `vector<Node*>` | 显式输入文件 |
| `outputs_` | `vector<Node*>` | 显式输出文件 |
| `implicit_deps_` | `vector<Node*>` | 隐式依赖（如头文件） |
| `order_only_deps_` | `vector<Node*>` | order-only 依赖 |
| `validation_deps_` | `vector<Node*>` | 验证依赖（构建后验证） |
| `implicit_outs_` | `vector<pair<Node*, bool>>` | 隐式输出（bool 表示是否 order-only） |
| `env_` | `BindingEnv` | 此边的变量绑定环境 |
| `pool_` | `Pool*` | 执行池（控制并发度） |
| `outputs_ready_` | `bool` | 所有输出是否已就绪 |
| `deps_loaded_` | `bool` | 头依赖是否已从 deps log 加载 |
| `deps_mtime_` | `int` | 头依赖的 mtime 记录 |
| `skip_outputs_` | `bool` | 是否跳过输出检查 |
| `command_start_time_` | `TimeStamp` | 命令开始执行时间 |

### 核心方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `is_phony() const` | `bool` | 是否为 phony 规则（不执行实际命令） |
| `outputs_ready() const` | `bool` | 所有输出是否就绪 |
| `GetBinding(const string& key)` | `string` | 获取变量绑定值（在 env_ 中查找） |
| `EvaluateCommand()` | `string` | 求值完整命令字符串 |
| `GetBindingWithEnv(const string& key, BindingEnv* env)` | `string` | 在指定环境中获取绑定 |
| `MarkInputsDirty()` | `void` | 标记所有输入为脏 |
| `Dump(const char* prefix) const` | `void` | 调试输出 |

### 依赖类型说明

| 依赖类型 | 语法 | 语义 |
|---------|------|------|
| 显式输入 | `build out: rule in1 in2` | 列出在 build 行 rule 后、`\|` 前 |
| 隐式依赖 | `build out: rule in \| dep1 dep2` | `\|` 后列出，修改触发重编译 |
| Order-only | `build out: rule in \|\| oodep` | `\|\|` 后列出，仅保证顺序，不触发重编译 |
| 验证依赖 | `build out: rule in \|@ vdep` | `\|@` 后列出，构建完成后验证 |
| 隐式输出 | 与 dyndep 配合 | 编译器生成的未显式声明的输出文件 |

---

## DependencyScan 类

**头文件**：`src/graph.h`

DependencyScan 负责依赖扫描和脏状态计算。

### 构造函数

```cpp
DependencyScan(State* state, DepsLog* deps_log);
```

### 核心方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `LoadDepsFromLog(Edge* edge, string* err)` | `bool` | 从 .ninja_deps 加载头依赖 |
| `RecomputeDirty(Edge* edge, string* err)` | `bool` | 递归计算边的脏状态 |
| `RecomputeOutputDirty(Edge* edge, Node* most_recent_input, TimeStamp mtime, string* err)` | `bool` | 计算输出脏状态 |
| `LoadDyndeps(Node* dyndep_node, Dyndeps* dyndep, string* err)` | `bool` | 加载 dyndep 文件中的动态依赖 |
| `RecomputeDirty(Node* node, string* err)` | `bool` | 计算节点的脏状态 |

### 脏状态计算逻辑

1. 递归检查所有输入的 mtime
2. 比较输出 mtime 与最新输入 mtime
3. 检查命令行哈希是否变化（通过 BuildLog）
4. 对于 depfile 边，加载 DepsLog 中的头依赖
5. 对于 dyndep 边，加载 dyndep 文件后重新检查
6. restat 规则在命令执行后重新 stat 输出，若 mtime 未变则下游不标记为脏

---

## EdgePriorityQueue

**头文件**：`src/graph.h`（通过 build.h 使用）

按关键路径优先级排序的边就绪队列。

```cpp
struct EdgeCmp {
  bool operator()(const Edge* a, const Edge* b);
};
using EdgePriorityQueue = priority_queue<Edge*, vector<Edge*>, EdgeCmp>;
```

- 优先队列中，关键路径更长的 Edge 优先级更高
- Plan::FindWork() 从队列顶部取下一个要执行的 Edge
- Plan::ScheduleWork() 将 Edge 加入就绪队列
