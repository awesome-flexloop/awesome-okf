---
type: Reference
title: 主入口与工具 API 参考
description: src/ninja.cc、src/status.h、src/status_printer.h、src/clean.h、src/graphviz.h、src/browse.h、src/missing_deps.h 源码参考——NinjaMain、Options、Tool、Status、StatusPrinter、Cleaner、GraphViz、MissingDependencyScanner 完整 API
tags: [reference, api, main, ninja-main, options, tool, status, clean, graphviz, browse, c++]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ninja-ninja
    title: src/ninja.cc
    path: external/libs/tools/ninja/src/ninja.cc
  - id: ninja-status
    title: src/status.h
    path: external/libs/tools/ninja/src/status.h
  - id: ninja-status-printer
    title: src/status_printer.h
    path: external/libs/tools/ninja/src/status_printer.h
  - id: ninja-clean
    title: src/clean.h
    path: external/libs/tools/ninja/src/clean.h
  - id: ninja-graphviz
    title: src/graphviz.h
    path: external/libs/tools/ninja/src/graphviz.h
  - id: ninja-browse
    title: src/browse.h
    path: external/libs/tools/ninja/src/browse.h
  - id: ninja-missing-deps
    title: src/missing_deps.h
    path: external/libs/tools/ninja/src/missing_deps.h
---

# 主入口与工具 API 参考

> 信源文件：[ninja.cc](file:///d:/spaces/SpecWeave/external/libs/tools/ninja/src/ninja.cc)、[status.h](file:///d:/spaces/SpecWeave/external/libs/tools/ninja/src/status.h)、[status_printer.h](file:///d:/spaces/SpecWeave/external/libs/tools/ninja/src/status_printer.h)、[clean.h](file:///d:/spaces/SpecWeave/external/libs/tools/ninja/src/clean.h)、[graphviz.h](file:///d:/spaces/SpecWeave/external/libs/tools/ninja/src/graphviz.h)、[browse.h](file:///d:/spaces/SpecWeave/external/libs/tools/ninja/src/browse.h)、[missing_deps.h](file:///d:/spaces/SpecWeave/external/libs/tools/ninja/src/missing_deps.h)

本文档记录 Ninja 主入口、命令行选项、子工具和状态输出接口的完整 API。

---

## Options 结构体

**源文件**：`src/ninja.cc`（匿名命名空间）

命令行选项。

```cpp
struct Options {
  const char* input_file;           // 构建文件名（-f 参数，默认 build.ninja）
  const char* working_dir;          // 工作目录（-C 参数）
  const Tool* tool;                 // 要运行的子工具（-t 参数，NULL=正常构建）
  bool phony_cycle_should_err;      // phony 循环是否应报错（-w phonycycle=err）
};
```

---

## Tool 结构体

**源文件**：`src/ninja.cc`（匿名命名空间）

子工具定义，通过 `-t <name>` 调用。

```cpp
struct Tool {
  const char* name;     // 短名称
  const char* desc;     // 描述（-t list 显示）
  enum {
    RUN_AFTER_FLAGS,   // 解析命令行 flag 后立即运行（尽早）
    RUN_AFTER_LOAD,    // 加载 build.ninja 后运行
    RUN_AFTER_LOGS,    // 加载 build/deps 日志后运行
  } when;
  NinjaMain::ToolFunc func;  // 工具实现函数指针
};
```

### 内置工具列表（kTools 数组）

| 工具名 | 描述 | 运行时机 | 方法 |
|--------|------|---------|------|
| `browse` | 在 Web 浏览器中浏览依赖图 | RUN_AFTER_LOAD | `ToolBrowse` |
| `clean` | 清理构建文件 | RUN_AFTER_LOAD | `ToolClean` |
| `cleandead` | 清理清单中不再产出的构建文件 | RUN_AFTER_LOGS | `ToolCleanDead` |
| `commands` | 列出重建指定目标所需的所有命令 | RUN_AFTER_LOAD | `ToolCommands` |
| `compdb` | 输出 JSON 编译数据库到 stdout | RUN_AFTER_LOAD | `ToolCompilationDatabase` |
| `compdb-targets` | 输出指定目标的 JSON 编译数据库 | RUN_AFTER_LOAD | `ToolCompilationDatabaseForTargets` |
| `deps` | 显示 deps 日志中存储的依赖 | RUN_AFTER_LOGS | `ToolDeps` |
| `graph` | 输出目标的 GraphViz .dot 文件 | RUN_AFTER_LOAD | `ToolGraph` |
| `inputs` | 列出重建指定目标所需的所有输入 | RUN_AFTER_LOAD | `ToolInputs` |
| `missingdeps` | 检查 deps 日志对生成文件的依赖 | RUN_AFTER_LOGS | `ToolMissingDeps` |
| `msvc` | MSVC cl.exe 构建辅助（已废弃，仅 Windows） | RUN_AFTER_FLAGS | `ToolMSVC` |
| `multi-inputs` | 打印一组或多组构建目标的输入 | RUN_AFTER_LOAD | `ToolMultiInputs` |
| `query` | 显示路径的输入/输出 | RUN_AFTER_LOGS | `ToolQuery` |
| `recompact` | 重压缩 ninja 内部数据结构 | RUN_AFTER_LOAD | `ToolRecompact` |
| `restat` | 重新 stat 构建日志中的所有输出 | RUN_AFTER_FLAGS | `ToolRestat` |
| `rules` | 列出所有规则 | RUN_AFTER_LOAD | `ToolRules` |
| `targets` | 按规则或 DAG 深度列出目标 | RUN_AFTER_LOAD | `ToolTargets` |
| `urtle` | （无描述，调试工具） | RUN_AFTER_FLAGS | `ToolUrtle` |
| `wincodepage` | 打印 ninja 使用的 Windows 代码页（仅 Windows） | RUN_AFTER_FLAGS | `ToolWinCodePage` |

---

## NinjaMain 结构体

**源文件**：`src/ninja.cc`（匿名命名空间）

NinjaMain 是 Ninja 主程序的核心对象，加载一系列数据结构供各工具使用。它同时实现 `BuildLogUser` 接口。

### 构造函数

```cpp
NinjaMain(const char* ninja_command, const BuildConfig& config);
```

- `ninja_command`：用于调用 ninja 的命令字符串（browse 模式传递给 Python 脚本）
- `config`：构建配置

### 核心方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `RunBuild(int argc, char** argv, Status* status)` | `ExitStatus` | 构建命令行指定的目标，返回退出码 |
| `RebuildManifest(const char* input_file, string* err, Status* status)` | `bool` | 必要时重新生成构建清单（bootstrap）；返回 true 表示清单被重建 |
| `OpenBuildLog(bool recompact_only = false)` | `bool` | 打开构建日志（.ninja_log） |
| `OpenDepsLog(bool recompact_only = false)` | `bool` | 打开依赖日志（.ninja_deps）：先加载再打开写入 |
| `EnsureBuildDirExists()` | `bool` | 确保构建目录存在，必要时创建 |
| `ParsePreviousElapsedTimes()` | `void` | 为每条边从 build log 查找上次执行耗时，记录到 `edge->prev_elapsed_time_millis` 用于 ETA 预测 |
| `SetupJobserverClient(Status* status)` | `unique_ptr<Jobserver::Client>` | 根据 MAKEFLAGS 创建 jobserver 客户端；不需要时返回 nullptr |
| `DumpMetrics()` | `void` | 输出 `-d stats` 请求的指标数据 |
| `IsPathDead(StringPiece s) const` | `bool` | BuildLogUser 接口实现：判断路径是否已不在清单中 |

### 目标收集方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `CollectTarget(const char* cpath, string* err)` | `Node*` | 将命令行路径收集为目标节点；支持 `foo^` 语法（foo 的第一个反向依赖）；支持 build_dir 回退查找；拼写检查建议 |
| `CollectTargetsFromArgs(int argc, char* argv[], vector<Node*>* targets, string* err)` | `bool` | 收集所有命令行参数为目标节点 |

### 工具方法（ToolFunc 签名）

所有工具方法签名为 `int (NinjaMain::*)(const Options*, int, char**)`，返回退出码。

| 方法 | 功能 |
|------|------|
| `ToolGraph` | 生成 GraphViz .dot 输出 |
| `ToolQuery` | 查询节点的输入/输出边 |
| `ToolDeps` | 显示 deps 日志内容 |
| `ToolMissingDeps` | 扫描缺失的依赖声明 |
| `ToolBrowse` | 启动 Python Web 服务器浏览依赖图 |
| `ToolMSVC` | MSVC 辅助模式（Windows） |
| `ToolTargets` | 按规则/DAG 深度列出目标 |
| `ToolCommands` | 列出构建命令 |
| `ToolInputs` | 列出输入文件 |
| `ToolMultiInputs` | 列出多组输入 |
| `ToolClean` | 清理构建产物 |
| `ToolCleanDead` | 清理死亡产物 |
| `ToolCompilationDatabase` | 生成完整 compile_commands.json |
| `ToolCompilationDatabaseForTargets` | 生成指定目标的编译数据库 |
| `ToolRecompact` | 重压缩日志 |
| `ToolRestat` | 重新 stat 输出 |
| `ToolUrtle` | 调试工具（无描述） |
| `ToolRules` | 列出所有规则 |
| `ToolWinCodePage` | 显示 Windows 代码页（Windows） |

### 成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `ninja_command_` | `const char*` | 调用 ninja 的命令 |
| `config_` | `const BuildConfig&` | 构建配置引用 |
| `state_` | `State` | 加载的状态（规则、节点、边） |
| `disk_interface_` | `RealDiskInterface` | 实际磁盘访问接口 |
| `build_dir_` | `string` | 构建目录（存储 build log 等） |
| `build_log_` | `BuildLog` | 构建日志实例 |
| `deps_log_` | `DepsLog` | 依赖日志实例 |
| `start_time_millis_` | `int64_t` | 构建开始时间 |

### NinjaMain 执行流程

```
main()
  ├─ 解析命令行参数，填充 Options 和 BuildConfig
  ├─ 创建 NinjaMain 实例
  ├─ 若指定 -C DIR：chdir
  ├─ RUN_AFTER_FLAGS 工具：直接运行退出
  ├─ 加载 build.ninja（ManifestParser::Load）
  │   └─ 若清单自身是构建目标且过期：RebuildManifest()
  ├─ RUN_AFTER_LOAD 工具：运行退出
  ├─ OpenBuildLog() / OpenDepsLog()
  ├─ EnsureBuildDirExists()
  ├─ ParsePreviousElapsedTimes()
  ├─ RUN_AFTER_LOGS 工具：运行退出
  ├─ SetupJobserverClient()
  ├─ 创建 Status（Status::factory）
  ├─ RunBuild() → Builder::Build()
  └─ DumpMetrics()（若启用 -d stats）
```

---

## Status 接口

**头文件**：`src/status.h`

跟踪构建状态的抽象接口：完成分数、打印更新。

```cpp
struct Status {
  virtual void EdgeAddedToPlan(const Edge* edge) = 0;
  virtual void EdgeRemovedFromPlan(const Edge* edge) = 0;
  virtual void BuildEdgeStarted(const Edge* edge, int64_t start_time_millis) = 0;
  virtual void BuildEdgeFinished(Edge* edge, int64_t start_time_millis,
                                 int64_t end_time_millis, ExitStatus exit_code,
                                 const string& output) = 0;
  virtual void BuildStarted() = 0;
  virtual void BuildFinished() = 0;
  virtual void SetExplanations(Explanations*) = 0;
  virtual void NewLine() = 0;
  virtual void Info(const char* msg, ...) = 0;
  virtual void Warning(const char* msg, ...) = 0;
  virtual void Error(const char* msg, ...) = 0;
  virtual ~Status() { }

  static Status* factory(const BuildConfig&);  // 创建实际实现
};
```

### StatusPrinter 实现

**头文件**：`src/status_printer.h`

Status 接口的具体实现，将状态作为人类可读字符串打印到 stdout。没有单独的 "DefaultStatusPrinter" 或 "SmartStatusPrinter" 类——智能终端行为由内部的 LinePrinter 控制。

```cpp
struct StatusPrinter : Status {
  explicit StatusPrinter(const BuildConfig& config);
  // 实现所有 Status 虚方法
  string FormatProgressStatus(const char* progress_status_format,
                              int64_t time_millis) const;
  string FormatStatusVariable(StringPiece name) const;
  void SetExplanations(Explanations* explanations) override;
};
```

### StatusPrinter 进度预测

StatusPrinter 维护 ETA 预测相关状态：

| 成员 | 类型 | 说明 |
|------|------|------|
| `started_edges_` | `int` | 已启动边数 |
| `finished_edges_` | `int` | 已完成边数 |
| `total_edges_` | `int` | 总边数 |
| `running_edges_` | `int` | 运行中边数 |
| `time_millis_` | `int64_t` | 经过的墙钟时间 |
| `cpu_time_millis_` | `int64_t` | 经过的 CPU 时间 |
| `current_rate_` | `SlidingRateInfo` | 滑动窗口速率（边/秒） |
| `printer_` | `LinePrinter` | 底层行打印机（支持智能终端覆写） |
| `progress_status_format_` | `const char*` | 进度格式字符串 |
| `status_eval_` | `unique_ptr<EvalString>` | `--status` 解析后的格式 |

进度格式占位符（NINJA_STATUS 环境变量或 `--status` 参数）：
- `%e`：已运行边数
- `%f`：总边数
- `%r`：当前运行边数
- `%u`：剩余边数
- `%p`：完成百分比
- `%t`：已用时间
- `%l`：剩余时间估计
- `%c`：每秒完成边数（速率）
- `%%`：字面 `%`

---

## Cleaner 结构体

**头文件**：`src/clean.h`

实现 `-t clean` 工具，清理构建产物。

```cpp
struct Cleaner {
  Cleaner(State* state, const BuildConfig& config,
          DiskInterface* disk_interface);

  int CleanTarget(Node* target);           // 清理目标及其所有构建文件
  int CleanTarget(const char* target);     // 按名称清理
  int CleanTargets(int target_count, char* targets[]);  // 批量清理
  int CleanAll(bool generator = false);    // 清理所有构建文件
  int CleanRule(const Rule* rule);         // 清理指定规则产出的文件
  int CleanRule(const char* rule);         // 按规则名清理
  int CleanRules(int rule_count, char* rules[]);  // 批量按规则清理
  int CleanDead(const BuildLog::Entries& entries);  // 清理死亡文件
  int cleaned_files_count() const;         // 已清理文件数
  bool IsVerbose() const;                  // 是否为详细模式
};
```

| 成员 | 类型 | 说明 |
|------|------|------|
| `state_` | `State*` | 构建状态 |
| `config_` | `const BuildConfig&` | 构建配置 |
| `dyndep_loader_` | `DyndepLoader` | 动态依赖加载器 |
| `removed_` | `set<string>` | 已删除文件集合（去重） |
| `cleaned_` | `set<Node*>` | 已清理节点集合 |
| `cleaned_files_count_` | `int` | 已清理文件计数 |
| `disk_interface_` | `DiskInterface*` | 磁盘接口 |
| `status_` | `int` | 清理状态（0=成功） |

---

## GraphViz 结构体

**头文件**：`src/graphviz.h`

实现 `-t graph` 工具，生成 GraphViz `.dot` 文件输出。

```cpp
struct GraphViz {
  GraphViz(State* state, DiskInterface* disk_interface);
  void Start();                              // 开始输出（写入 dot 文件头）
  void AddTarget(Node* node);                // 添加目标节点到图
  void Finish();                             // 完成输出（写入 dot 文件尾）
};
```

| 成员 | 类型 | 说明 |
|------|------|------|
| `dyndep_loader_` | `DyndepLoader` | 动态依赖加载器 |
| `visited_nodes_` | `set<Node*>` | 已访问节点集合 |
| `visited_edges_` | `EdgeSet` | 已访问边集合 |

---

## Browse 函数

**头文件**：`src/browse.h`

实现 `-t browse` 工具，启动 Python Web 服务器浏览依赖图。

```cpp
void RunBrowsePython(State* state, const char* ninja_command,
                     const char* input_file, int argc, char* argv[]);
```

- 执行 `src/browse.py` 脚本
- 成功时不返回（exec Python 进程）
- 通过 `ninja_command` 定位 ninja 可执行文件，进而查找 browse.py

---

## MissingDependencyScanner 结构体

**头文件**：`src/missing_deps.h`

实现 `-t missingdeps` 工具，扫描 deps 日志中对生成文件的缺失依赖声明。

### MissingDependencyScannerDelegate 接口

```cpp
class MissingDependencyScannerDelegate {
 public:
  virtual ~MissingDependencyScannerDelegate();
  virtual void OnMissingDep(Node* node, const string& path,
                            const Rule& generator) = 0;
};
```

### MissingDependencyPrinter

```cpp
class MissingDependencyPrinter : public MissingDependencyScannerDelegate {
  void OnMissingDep(Node* node, const string& path, const Rule& generator);
  void OnStats(int nodes_processed, int nodes_missing_deps,
               int missing_dep_path_count, int generated_nodes,
               int generator_rules);
};
```

### MissingDependencyScanner

```cpp
struct MissingDependencyScanner {
  MissingDependencyScanner(MissingDependencyScannerDelegate* delegate,
                           DepsLog* deps_log, State* state,
                           DiskInterface* disk_interface);
  void ProcessNode(Node* node);                           // 处理单个节点
  void PrintStats();                                      // 打印统计
  bool HadMissingDeps();                                  // 是否有缺失依赖
  void ProcessNodeDeps(Node* node, Node** dep_nodes, int dep_nodes_count);
  bool PathExistsBetween(Edge* from, Edge* to);          // 判断边之间是否存在路径
};
```

| 成员 | 类型 | 说明 |
|------|------|------|
| `delegate_` | `MissingDependencyScannerDelegate*` | 结果回调 |
| `deps_log_` | `DepsLog*` | 依赖日志 |
| `state_` | `State*` | 构建状态 |
| `disk_interface_` | `DiskInterface*` | 磁盘接口 |
| `seen_` | `set<Node*>` | 已处理节点 |
| `nodes_missing_deps_` | `set<Node*>` | 有缺失依赖的节点 |
| `generated_nodes_` | `set<Node*>` | 生成节点集合 |
| `generator_rules_` | `set<const Rule*>` | 生成器规则集合 |
| `missing_dep_path_count_` | `int` | 缺失依赖路径计数 |

---

## 辅助数据结构

### InputsCollector（graph.h）

`-t inputs` 工具使用，收集从起始节点传递闭包的输入节点：

```cpp
struct InputsCollector {
  void VisitNode(const Node* node);
  const vector<const Node*>& inputs() const;
  vector<string> GetInputsAsStrings(bool shell_escape = false) const;
  void Reset();
};
```

### CommandCollector（command_collector.h）

`-t compdb-targets` 工具使用，收集从起始节点传递闭包的边：

```cpp
struct CommandCollector {
  void CollectFrom(const Node* node);
  vector<Edge*> in_edges;  // 公共成员：收集结果（按依赖顺序）
};
```

### LinePrinter（line_printer.h）

底层终端行打印，支持智能终端覆写：

```cpp
struct LinePrinter {
  LinePrinter();
  bool is_smart_terminal() const;
  void set_smart_terminal(bool smart);
  bool supports_color() const;
  enum LineType { FULL, ELIDE };
  void Print(string to_print, LineType type);       // 覆写当前行
  void PrintOnNewLine(const string& to_print);      // 新行打印
  void SetConsoleLocked(bool locked);               // 锁定/解锁控制台
};
```

---

## 代码示例

```cpp
// 基本 Ninja 主流程
BuildConfig config;
config.parallelism = GuessParallelism();  // 默认 CPU+2
config.verbosity = BuildConfig::NORMAL;

NinjaMain ninja(ninja_command, config);

// 加载清单
ManifestParser parser(&ninja.state_, &ninja.disk_interface_, parser_options);
string err;
if (!parser.Load("build.ninja", &err)) {
  Fatal("load error: %s", err.c_str());
}

// 重建清单（自举）
Status* status = Status::factory(config);
if (ninja.RebuildManifest("build.ninja", &err, status)) {
  // 清单被重建，重新加载
  ninja.state_.Reset();
  parser.Load("build.ninja", &err);
}

// 打开日志
ninja.OpenBuildLog();
ninja.OpenDepsLog();
ninja.EnsureBuildDirExists();
ninja.ParsePreviousElapsedTimes();

// 构建目标
vector<Node*> targets;
ninja.CollectTargetsFromArgs(argc, argv, &targets, &err);
ExitStatus result = ninja.RunBuild(argc, argv, status);

// 清理
delete status;
return result;
```
