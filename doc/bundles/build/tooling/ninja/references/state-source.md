---
type: Reference
title: 状态与池 API 参考
description: src/state.h/cc 源码参考——State、Pool 完整 API
tags: [reference, api, state, pool, node, edge, c++]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ninja-state
    title: src/state.h
    path: external/libs/tools/ninja/src/state.h
  - id: ninja-state-cc
    title: src/state.cc
    path: external/libs/tools/ninja/src/state.cc
---

# 状态与池 API 参考

> 信源文件：state.h、state.cc

本文档记录 Ninja 全局构建状态和并发池的完整 API。

---

## Pool 结构体

**头文件**：`src/state.h`

Pool 用于延迟边执行的并发控制。池的作用域为一个 State，同一 State 内的 Edge 共享 Pool。Pool 维护当前已调度边的总"权重"计数；当 Plan 尝试调度一条边会导致总权重超过池的 depth 时，该边被入队延迟，直到正在运行的边完成释放资源。

### 构造函数

```cpp
Pool(const std::string& name, int depth);
```

- `name`：池名称（如 `"console"`）
- `depth`：池深度（并发度），**0 表示无限并发**

### 静态池实例

State 提供两个预定义的静态池：

| 静态成员 | 说明 |
|---------|------|
| `State::kDefaultPool` | 默认池（depth=0，无限并发），未指定 pool 的边使用此池 |
| `State::kConsolePool` | 控制台池（depth=1），`pool = console` 的边串行执行并直接访问终端 |

### 方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `is_valid() const` | `bool` | 池是否有效（`depth_ >= 0`） |
| `depth() const` | `int` | 池深度（0=无限） |
| `name() const` | `const string&` | 池名称 |
| `current_use() const` | `int` | 当前已使用的权重 |
| `ShouldDelayEdge() const` | `bool` | 池是否可能延迟边（`depth_ != 0`） |
| `EdgeScheduled(const Edge& edge)` | `void` | 通知池给定边已提交运行，计入资源占用 |
| `EdgeFinished(const Edge& edge)` | `void` | 通知池给定边已完成，释放资源 |
| `DelayEdge(Edge* edge)` | `void` | 将边加入延迟队列 |
| `RetrieveReadyEdges(EdgePriorityQueue* ready_queue)` | `void` | 从延迟队列中取出现在可运行的边，加入就绪队列 |
| `Dump() const` | `void` | 调试输出池及其边 |

### 私有成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `name_` | `string` | 池名称 |
| `current_use_` | `int` | 当前已调度边的总权重 |
| `depth_` | `int` | 池深度（最大并发权重） |
| `delayed_` | `DelayedEdges`（`set<Edge*, WeightedEdgeCmp>`） | 延迟边集合，按权重和优先级排序 |

### WeightedEdgeCmp 比较器

延迟队列使用 `WeightedEdgeCmp` 排序：先按 `edge->weight()` 升序，权重相同时使用 `EdgePriorityGreater()`（关键路径权重大的优先、ID 小的优先）。

---

## State 结构体

**头文件**：`src/state.h`

State 存储单次运行的全局状态（规则、节点、边、池、默认目标）。

### 构造函数

```cpp
State();
```

初始化空状态，自动包含 `kDefaultPool` 和 `kConsolePool`。

### 静态成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `kDefaultPool` | `Pool` | 默认池（depth=0，无限并发） |
| `kConsolePool` | `Pool` | 控制台池（depth=1，串行访问终端） |

### 池管理方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `AddPool(Pool* pool)` | `void` | 向状态添加一个池 |
| `LookupPool(const string& pool_name)` | `Pool*` | 按名称查找池，未找到返回 NULL |

### 边管理方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `AddEdge(const Rule* rule)` | `Edge*` | 创建一条新边并关联指定规则，添加到 edges_ 列表 |

### 节点管理方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `GetNode(StringPiece path, uint64_t slash_bits)` | `Node*` | 获取路径对应的 Node；若不存在则创建新节点并加入 paths_ 映射 |
| `LookupNode(StringPiece path) const` | `Node*` | 按路径查找节点，不存在返回 NULL |
| `SpellcheckNode(const string& path)` | `Node*` | 拼写检查，返回最接近的节点或 NULL |
| `AddIn(Edge* edge, StringPiece path, uint64_t slash_bits)` | `void` | 向边添加输入节点，设置 `generated_by_dep_loader=false` |
| `AddOut(Edge* edge, StringPiece path, uint64_t slash_bits, string* err)` | `bool` | 向边添加输出节点，重复输出报错；设置 `generated_by_dep_loader=false` |
| `AddValidation(Edge* edge, StringPiece path, uint64_t slash_bits)` | `void` | 向边添加验证依赖节点 |
| `AddDefault(StringPiece path, string* error)` | `bool` | 添加默认目标节点 |

### 图遍历方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `RootNodes(string* error) const` | `vector<Node*>` | 返回图的根节点（无输出边的节点） |
| `DefaultNodes(string* error) const` | `vector<Node*>` | 返回默认目标节点列表 |
| `Reset()` | `void` | 重置状态：保留所有节点和边，但恢复到未检查磁盘脏状态的初始状态 |
| `Dump()` | `void` | 调试输出节点和池 |

### 公共成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `paths_` | `Paths`（`ExternalStringHashMap<Node*>::Type`） | 路径到 Node 的映射 |
| `pools_` | `map<string, Pool*>` | 所有池（含默认池和控制台池） |
| `edges_` | `vector<Edge*>` | 图中所有边 |
| `bindings_` | `BindingEnv` | 顶层变量绑定环境（规则和变量存储在此） |
| `defaults_` | `vector<Node*>` | 默认目标节点列表 |

### 说明

- **规则查找**：规则不直接存储在 State 的独立 map 中，而是通过 `bindings_`（BindingEnv 类型）进行管理。使用 `bindings_.AddRule()` 添加规则，`bindings_.LookupRule()` 查找规则。
- **节点 ID**：节点没有全局递增 ID（`id_` 字段由 DepsLog 在加载时分配，默认为 -1）。
- **路径规范化**：所有路径在加入 State 前必须通过 `CanonicalizePath()` 规范化，`slash_bits` 记录 Windows 下被转换为正斜杠的反斜杠位置。

### 代码示例

```cpp
// 创建状态和解析清单
State state;
RealDiskInterface disk_interface;
ManifestParser parser(&state, &disk_interface);
string err;
if (!parser.Load("build.ninja", &err)) {
  Error("load failed: %s", err.c_str());
  return 1;
}

// 查找节点
Node* node = state.LookupNode("build/output.o");
if (node) {
  printf("node found: %s\n", node->path().c_str());
}

// 查找池
Pool* console_pool = state.LookupPool("console");
// console_pool == &State::kConsolePool

// 遍历所有边
for (Edge* edge : state.edges_) {
  printf("edge using rule: %s\n", edge->rule().name().c_str());
}

// 获取默认目标
vector<Node*> defaults = state.DefaultNodes(&err);
```
