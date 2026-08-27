---
type: Reference
title: 日志与动态依赖 API 参考
description: src/build_log.h/cc、src/deps_log.h/cc、src/dyndep.h/cc、src/dyndep_parser.h/cc 源码参考——BuildLog、DepsLog、Dyndeps、DyndepLoader、DyndepParser 完整 API
tags: [reference, api, build-log, deps-log, dyndep, dependency, c++]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ninja-build-log
    title: src/build_log.h
    path: external/libs/tools/ninja/src/build_log.h
  - id: ninja-build-log-cc
    title: src/build_log.cc
    path: external/libs/tools/ninja/src/build_log.cc
  - id: ninja-deps-log
    title: src/deps_log.h
    path: external/libs/tools/ninja/src/deps_log.h
  - id: ninja-dyndep
    title: src/dyndep.h
    path: external/libs/tools/ninja/src/dyndep.h
  - id: ninja-dyndep-parser
    title: src/dyndep_parser.h
    path: external/libs/tools/ninja/src/dyndep_parser.h
---

# 日志与动态依赖 API 参考

> 信源文件：build_log.h、deps_log.h、dyndep.h、dyndep_parser.h

本文档记录 Ninja 构建日志、依赖日志和动态依赖加载模块的完整 API。

---

## BuildLog 结构体

**头文件**：`src/build_log.h`

BuildLog 存储每次构建中每条命令运行的日志。用途包括：
1. 现有输出文件的命令行哈希（用于检测命令变更导致的重建）
2. 计时信息（用于生成报告和 ETA 预测）
3. restat 信息

日志文件通常为 `.ninja_log`，位于构建目录中。

### 构造/析构

```cpp
BuildLog();
~BuildLog();
```

### 写入接口

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `OpenForWrite(const string& path, const BuildLogUser& user, string* err)` | `bool` | 准备写入日志文件（延迟实际打开，直到首次需要写入） |
| `RecordCommand(Edge* edge, int start_time, int end_time, TimeStamp mtime = 0)` | `bool` | 记录一条边的命令执行结果 |
| `Close()` | `void` | 关闭日志文件 |
| `WriteEntry(FILE* f, const LogEntry& entry)` | `bool` | 将条目序列化写入日志文件 |

### 读取接口

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Load(const string& path, string* err)` | `LoadStatus` | 加载磁盘上的日志文件 |
| `LookupByOutput(const string& path) const` | `LogEntry*` | 按输出路径查找之前运行的命令记录 |
| `entries() const` | `const Entries&` | 获取所有日志条目 |

### 维护接口

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Recompact(const string& path, const BuildLogUser& user, string* err)` | `bool` | 重写已知日志条目，丢弃旧数据 |
| `Restat(StringPiece path, const DiskInterface& disk_interface, int output_count, char** outputs, string* err)` | `bool` | 重新 stat 日志中的所有输出（`-t restat` 工具使用） |

### LogEntry 嵌套结构体

```cpp
struct LogEntry {
  std::string output;
  uint64_t command_hash = 0;
  int start_time = 0;
  int end_time = 0;
  TimeStamp mtime = 0;

  explicit LogEntry(std::string output);
  LogEntry(const std::string& output, uint64_t command_hash,
           int start_time, int end_time, TimeStamp mtime);

  static uint64_t HashCommand(StringPiece command);

  bool operator==(const LogEntry& o) const;
};
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `output` | `string` | 输出文件路径 |
| `command_hash` | `uint64_t` | 命令字符串的哈希值 |
| `start_time` | `int` | 命令开始时间（毫秒，相对构建开始） |
| `end_time` | `int` | 命令结束时间 |
| `mtime` | `TimeStamp` | 输出文件的 mtime |

`HashCommand()` 静态方法计算命令字符串的哈希值，用于检测命令行变更。这是 Ninja 判断是否需要重建的依据之一（命令哈希变化 → 重建）。

### BuildLogUser 接口

```cpp
struct BuildLogUser {
  virtual bool IsPathDead(StringPiece s) const = 0;
};
```

BuildLogUser 接口在重压缩时判断某个输出路径是否已不在构建清单中（"死亡"路径）。NinjaMain 实现此接口。

### 私有成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `entries_` | `Entries`（`ExternalStringHashMap<unique_ptr<LogEntry>>::Type`） | 路径→LogEntry 的哈希映射 |
| `log_file_` | `FILE*` | 日志文件句柄 |
| `log_file_path_` | `string` | 日志文件路径 |
| `needs_recompaction_` | `bool` | 是否需要重压缩 |

---

## DepsLog 结构体

**头文件**：`src/deps_log.h`

构建命令运行时可能输出额外的依赖信息（如 C 源文件的头依赖）。DepsLog 在构建时收集这些信息，并在后续构建中用于增量构建判断。

日志文件通常为 `.ninja_deps`。

### 磁盘格式设计

文件结构为版本头 + 记录序列。记录分两种类型：
- **路径记录**：路径字符串，按文件顺序分配密集整数 ID
- **依赖列表记录**：映射输出 ID → 输入 ID 列表 + 输出 mtime

```
记录格式：
  4 字节记录长度（高位表示类型：0=路径，1=依赖）
  路径记录：路径字符串 + 填充字节 + 期望索引的补码
  依赖记录：[输出ID, 输出mtime低4字节, 输出mtime高4字节, 输入ID, 输入ID, ...]
```

同一输出的后一条记录覆盖前一条。单独的 repack 步骤可偶尔运行以清理死记录。

### 构造/析构

```cpp
DepsLog();
~DepsLog();
```

### 写入接口（构建时）

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `OpenForWrite(const string& path, string* err)` | `bool` | 打开日志文件用于写入 |
| `RecordDeps(Node* node, TimeStamp mtime, const vector<Node*>& nodes)` | `bool` | 记录节点的依赖列表 |
| `RecordDeps(Node* node, TimeStamp mtime, int node_count, Node* const* nodes)` | `bool` | 记录依赖列表（数组版本） |
| `Close()` | `void` | 关闭日志文件 |

### 读取接口（启动时）

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Load(const string& path, State* state, string* err)` | `LoadStatus` | 加载磁盘上的 deps 日志 |
| `GetDeps(Node* node)` | `Deps*` | 获取节点的依赖记录 |
| `GetFirstReverseDepsNode(Node* node)` | `Node*` | 获取第一个反向依赖节点（用于 `target^` 语法） |
| `nodes() const` | `const vector<Node*>&` | 测试用：返回所有节点 |
| `deps() const` | `const vector<Deps*>&` | 测试用：返回所有依赖记录 |

### 维护接口

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Recompact(const string& path, string* err)` | `bool` | 重写已知条目，丢弃旧数据 |
| `IsDepsEntryLiveFor(const Node* node)` | `static bool` | 判断节点的 deps 条目是否仍可从清单访问 |

### Deps 嵌套结构体

```cpp
struct Deps {
  Deps(int64_t mtime, int node_count);
  ~Deps();
  TimeStamp mtime;
  int node_count;
  Node** nodes;
};
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `mtime` | `TimeStamp` | 输出文件的 mtime（用于验证存储数据是否最新） |
| `node_count` | `int` | 依赖节点数量 |
| `nodes` | `Node**` | 依赖节点指针数组 |

### 私有成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `needs_recompaction_` | `bool` | 是否需要重压缩 |
| `file_` | `FILE*` | 日志文件句柄 |
| `file_path_` | `string` | 文件路径 |
| `nodes_` | `vector<Node*>` | ID → Node 映射 |
| `deps_` | `vector<Deps*>` | ID → Deps 映射 |

---

## Dyndeps 结构体

**头文件**：`src/dyndep.h`

存储一条边动态发现的依赖信息。由 `dyndep` 绑定指定的文件在构建时生成，Ninja 在边的 dyndep 输出就绪后加载。

```cpp
struct Dyndeps {
  Dyndeps() : used_(false), restat_(false) {}
  bool used_;
  bool restat_;
  std::vector<Node*> implicit_inputs_;
  std::vector<Node*> implicit_outputs_;
};
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `used_` | `bool` | 此 dyndep 信息是否已被使用 |
| `restat_` | `bool` | 此边是否应在命令后重新 stat 输出 |
| `implicit_inputs_` | `vector<Node*>` | 动态发现的隐式输入 |
| `implicit_outputs_` | `vector<Node*>` | 动态发现的隐式输出 |

### DyndepFile 类型

```cpp
struct DyndepFile : public std::map<Edge*, Dyndeps> {};
```

从单个 dyndep 文件加载的数据：Edge → Dyndeps 的映射。

---

## DyndepLoader 结构体

**头文件**：`src/dyndep.h`

加载 dyndep 文件并更新构建图。

### 构造函数

```cpp
DyndepLoader(State* state, DiskInterface* disk_interface,
             Explanations* explanations = nullptr);
```

### 方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `LoadDyndeps(Node* node, string* err) const` | `bool` | 从指定节点路径加载 dyndep 文件并更新图 |
| `LoadDyndeps(Node* node, DyndepFile* ddf, string* err) const` | `bool` | 加载到调用者提供的 DyndepFile 对象中 |

### 私有方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `LoadDyndepFile(Node* file, DyndepFile* ddf, string* err) const` | `bool` | 读取并解析 dyndep 文件 |
| `UpdateEdge(Edge* edge, Dyndeps const* dyndeps, string* err) const` | `bool` | 用 dyndep 信息更新边 |

### 私有成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `state_` | `State*` | 构建状态 |
| `disk_interface_` | `DiskInterface*` | 磁盘接口 |
| `explanations_` | `OptionalExplanations` | 可选的解释输出 |

---

## DyndepParser 结构体

**头文件**：`src/dyndep_parser.h`

解析 dyndep 文件格式，继承自 Parser 基类。

### 构造函数

```cpp
DyndepParser(State* state, FileReader* file_reader, DyndepFile* dyndep_file);
```

### 方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `ParseTest(const string& input, string* err)` | `bool` | 解析文本字符串（测试用） |

### 私有方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Parse(const string& filename, const string& input, string* err)` | `bool` | 实现 Parser::Parse |
| `ParseDyndepVersion(string* err)` | `bool` | 解析 `ninja_dyndep_version` 声明 |
| `ParseLet(string* key, EvalString* val, string* err)` | `bool` | 解析变量赋值 |
| `ParseEdge(string* err)` | `bool` | 解析边的 dyndep 信息 |

### 私有成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `dyndep_file_` | `DyndepFile*` | 输出：解析结果存储 |
| `env_` | `BindingEnv` | dyndep 文件内的变量绑定环境 |

---

## DependencyScan 中的 dyndep 加载

DependencyScan（在 [graph-source.md](graph-source.md) 中描述）持有 DyndepLoader 实例：

- `LoadDyndeps(Node* node, string* err)`：加载 dyndep 文件
- dyndep 文件在边的输出构建完成后加载（通过 Plan::NodeFinished/EdgeFinished）
- 加载后，新发现的隐式输入/输出被加入构建图，可能使原本认为就绪的边变为需要重新构建

### 动态依赖流程

```
1. Manifest 中 build 声明使用 dyndep 绑定指定 dyndep 文件
2. dyndep 输出节点被标记 dyndep_pending_ = true
3. 构建执行到 dyndep 输出节点的边
4. 边完成后，Plan::EdgeFinished() 检测到 dyndep 绑定
5. 调用 DyndepLoader::LoadDyndeps() 解析 dyndep 文件
6. DyndepParser 解析文件，填充 DyndepFile
7. DyndepLoader::UpdateEdge() 将隐式输入/输出添加到对应边
8. Plan::DyndepsLoaded() 更新构建计划，可能将新发现的边加入队列
```
