---
type: Reference
title: 构建执行 API 参考
description: src/build.h/cc 源码参考——Plan、Builder、BuildConfig、CommandRunner、RealCommandRunner 完整 API
tags: [reference, api, build, plan, builder, command-runner, c++]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ninja-build
    title: src/build.h
    path: external/libs/tools/ninja/src/build.h
  - id: ninja-build-cc
    title: src/build.cc
    path: external/libs/tools/ninja/src/build.cc
  - id: ninja-real-command-runner
    title: src/real_command_runner.cc
    path: external/libs/tools/ninja/src/real_command_runner.cc
  - id: ninja-build-result
    title: src/build_result.h
    path: external/libs/tools/ninja/src/build_result.h
---

# 构建执行 API 参考

> 信源文件：[build.h](file:///d:/spaces/SpecWeave/external/libs/tools/ninja/src/build.h)、[build.cc](file:///d:/spaces/SpecWeave/external/libs/tools/ninja/src/build.cc)、[real_command_runner.cc](file:///d:/spaces/SpecWeave/external/libs/tools/ninja/src/real_command_runner.cc)

本文档记录 Ninja 构建执行核心模块的完整 API，涵盖构建计划、构建器、配置和命令运行器。

---

## Plan 结构体

**头文件**：`src/build.h`

Plan 存储一次构建计划的状态：要构建哪些目标、哪些步骤已就绪可以执行。它是构建调度的核心数据结构。

### 构造函数

```cpp
Plan(Builder* builder = NULL);
```

- `builder`：关联的 Builder 实例，用于访问构建上下文

### 核心公共方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `AddTarget(const Node* target, string* err)` | `bool` | 将目标节点添加到构建计划（包含其所有依赖）；若目标无需构建返回 false，出错时填充 err |
| `FindWork()` | `Edge*` | 从就绪边队列中弹出一个可执行的 Edge；无工作可做时返回 NULL |
| `more_to_do() const` | `bool` | 是否还有待完成的工作（`wanted_edges_ > 0 && command_edges_ > 0`） |
| `work_ready() const` | `bool` | 是否有就绪工作（就绪队列非空） |
| `EdgeFinished(Edge* edge, EdgeResult result, string* err)` | `bool` | 标记一条边构建完成（成功或失败）；若输出是 dyndep 绑定则加载动态依赖 |
| `CleanNode(DependencyScan* scan, Node* node, string* err)` | `bool` | 在构建过程中清理指定节点（删除输出文件） |
| `command_edge_count() const` | `int` | 需要执行命令的边的总数（非 phony 边） |
| `Reset()` | `void` | 重置状态，清除 want 和 ready 集合 |
| `PrepareQueue()` | `void` | 所有目标添加完毕后，准备就绪队列供 FindWork 使用 |
| `DyndepsLoaded(DependencyScan* scan, const vector<Node*>& dyndep_nodes, const unordered_map<Edge*, Dyndeps>& dyndep_edges, string* err)` | `bool` | 根据从 dyndep 文件加载的信息更新构建计划 |
| `Dump() const` | `void` | 调试输出当前计划状态 |

### EdgeResult 枚举

```cpp
enum EdgeResult {
  kEdgeFailed,     // 边执行失败
  kEdgeSucceeded   // 边执行成功
};
```

### Want 枚举

表示 Plan 对一条边的期望状态：

```cpp
enum Want {
  kWantNothing,   // 不构建此边，但可能构建其依赖者
  kWantToStart,   // 想要构建此边，但尚未调度
  kWantToFinish   // 想要构建此边，已调度，等待完成
};
```

### 私有方法（调度内部）

| 方法 | 说明 |
|------|------|
| `ComputeCriticalPath()` | 计算关键路径权重，用于优先级调度 |
| `ScheduleInitialEdges()` | 将 kWantToStart 状态的边加入就绪队列（必须在 ComputeCriticalPath 后、FindWork 前调用） |
| `NodeFinished(Node* node, string* err)` | 标记节点已更新；若是 dyndep 绑定则加载动态依赖 |
| `EdgeWanted(const Edge* edge)` | 标记一条边为被需要状态 |
| `EdgeMaybeReady(map<Edge*, Want>::iterator want_e, string* err)` | 检查边是否所有依赖都已满足 |
| `ScheduleWork(map<Edge*, Want>::iterator want_e)` | 将就绪边提交为执行候选（可能因池满而延迟） |
| `AddSubTarget(const Node* node, const Node* dependent, string* err, set<Edge*>* dyndep_walk)` | 递归添加子目标 |
| `RefreshDyndepDependents(DependencyScan* scan, const vector<Node*>& dyndep_nodes, string* err)` | 刷新 dyndep 依赖者的脏状态 |
| `UnmarkDependents(const Node* node, set<Node*>* dependents)` | 取消标记依赖者 |

### 私有成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `want_` | `map<Edge*, Want>` | 需要构建的边及其状态映射 |
| `ready_` | `EdgePriorityQueue` | 就绪边优先级队列（按关键路径权重排序） |
| `builder_` | `Builder*` | 关联的构建器 |
| `targets_` | `vector<const Node*>` | 用户指定的目标（按构建顺序，靠前的优先级更高） |
| `command_edges_` | `int` | 有命令要执行的边总数 |
| `wanted_edges_` | `int` | 剩余需要的边数 |

---

## BuildConfig 结构体

**头文件**：`src/build.h`

传递给构建的选项配置（如详细程度、并行度等）。

```cpp
struct BuildConfig {
  BuildConfig() = default;
  // ... 成员
};
```

### 成员

| 成员 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `verbosity` | `Verbosity` | `NORMAL` | 输出详细程度 |
| `dry_run` | `bool` | `false` | 空跑模式（不执行命令但假装成功） |
| `parallelism` | `int` | `1` | 并行作业数 |
| `disable_jobserver_client` | `bool` | `false` | 是否禁用 GNU Make jobserver 客户端 |
| `failures_allowed` | `int` | `1` | 允许的失败数（-k N 参数），0 表示无限 |
| `max_load_average` | `double` | `-0.0f` | 最大负载平均值限制，负值表示无限制 |
| `progress_status_format` | `const char*` | `nullptr` | 进度状态格式（`--status` 参数），非空时覆盖 `$NINJA_STATUS` |
| `depfile_parser_options` | `DepfileParserOptions` | — | depfile 解析器选项 |

### Verbosity 枚举

```cpp
enum Verbosity {
  QUIET,             // 无输出（测试使用）
  NO_STATUS_UPDATE,  // 正常输出但抑制状态更新
  NORMAL,            // 正常输出和状态更新
  VERBOSE            // 详细输出（显示所有命令行）
};
```

### 注意

`build_dir`（构建目录）不是 BuildConfig 的成员，而是存储在 `NinjaMain::build_dir_` 中。

---

## CommandRunner 抽象类

**头文件**：`src/build.h`

CommandRunner 是封装构建子命令运行的接口，允许测试中抽象掉命令执行。`RealCommandRunner` 是实际运行命令的实现。

### 公共虚方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `CanRunMore() const` | `size_t` | 返回还能启动多少个命令（受并行度、负载、池限制约束） |
| `StartCommand(Edge* edge)` | `bool` | 启动一条边的命令执行 |
| `WaitForCommand()` | `BuildResult` | 等待一个命令完成；被中断时返回 false |
| `WaitForCommandOrJobserverToken(bool watch_jobserver)` | `BuildResult` | 等待命令完成或 jobserver token 可用；默认实现仅等待命令，RealCommandRunner 覆盖此方法以同时等待 jobserver |
| `GetActiveEdges()` | `vector<Edge*>` | 返回当前正在运行的边列表；默认返回空 vector |
| `Abort()` | `void` | 中止所有运行中的命令；默认无操作 |

### 工厂方法

```cpp
static CommandRunner* factory(const BuildConfig& config,
                              Jobserver::Client* jobserver);
```

创建 RealCommandRunner 实例。`jobserver` 为 nullptr 表示不使用 jobserver 池。

---

## RealCommandRunner 类

**源文件**：`src/real_command_runner.cc`

CommandRunner 的实际实现，通过 SubprocessSet 执行真实的子进程命令。

```cpp
struct RealCommandRunner : public CommandRunner {
  explicit RealCommandRunner(const BuildConfig& config,
                             Jobserver::Client* jobserver);
  // ... 实现 CommandRunner 的所有虚方法
};
```

### 核心实现逻辑

| 方法 | 实现要点 |
|------|---------|
| `CanRunMore()` | 根据 `config_.parallelism - 当前子进程数` 计算容量；启用 jobserver 时容量设为 INT_MAX；考虑 `max_load_average` 负载限制；确保至少能启动 1 个进程以保证进展 |
| `StartCommand(Edge*)` | 调用 `edge->EvaluateCommand()` 获取命令字符串，通过 `subprocs_.Add()` 启动子进程，建立 Subprocess→Edge 映射 |
| `WaitForCommand()` | 委托给 `WaitForCommandOrJobserverToken(false)` |
| `WaitForCommandOrJobserverToken(bool)` | 设置 jobserver FD 后循环调用 `subprocs_.DoWork()`，根据 WorkResult 类型返回 CommandCompleted、Interrupted 或 JobserverTokenAvailable |
| `GetActiveEdges()` | 遍历 `subproc_to_edge_` 返回所有活跃 Edge |
| `Abort()` | 调用 `ClearJobTokens()` 释放所有 jobserver token，然后清空子进程集合 |

### 成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `config_` | `const BuildConfig&` | 构建配置引用 |
| `subprocs_` | `SubprocessSet` | 子进程集合 |
| `jobserver_` | `Jobserver::Client*` | jobserver 客户端指针（可为空） |
| `subproc_to_edge_` | `map<const Subprocess*, Edge*>` | 子进程到边的映射 |

---

## Builder 结构体

**头文件**：src/build.h

Builder 封装构建过程：启动命令、更新状态、处理依赖加载。

### 构造函数

```cpp
Builder(State* state, const BuildConfig& config, BuildLog* build_log,
        DepsLog* deps_log, DiskInterface* disk_interface, Status* status,
        int64_t start_time_millis);
~Builder();
```

### 核心方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Build(string* err)` | `ExitStatus` | 执行构建，返回 ExitStatus 或最后失败作业的退出码；AlreadyUpToDate() 为 true 时调用属于错误 |
| `AddTarget(const string& name, string* err)` | `Node*` | 通过名称添加目标节点 |
| `AddTarget(Node* target, string* err)` | `bool` | 添加目标节点到构建，扫描依赖；出错返回 false |
| `AlreadyUpToDate() const` | `bool` | 构建目标是否已是最新 |
| `StartEdge(Edge* edge, string* err)` | `bool` | 启动一条边的执行 |
| `FinishCommand(BuildResult::CommandCompleted& result, string* err)` | `bool` | 命令终止后更新状态和日志；致命错误返回 false |
| `Cleanup()` | `void` | 被中断后清理，删除输出文件 |
| `LoadDyndeps(Edge* edge, string* err)` | `bool` | 加载边输出提供的 dyndep 信息 |
| `SetJobserverClient(unique_ptr<Jobserver::Client>)` | `void` | 设置 jobserver 客户端 |
| `SetBuildLog(BuildLog* log)` | `void` | 设置构建日志（供测试使用） |
| `GetExitCode() const` | `ExitStatus` | 获取全局退出码 |

### 公共成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `state_` | `State*` | 构建状态 |
| `config_` | `const BuildConfig&` | 构建配置 |
| `plan_` | `Plan` | 构建计划 |
| `jobserver_` | `unique_ptr<Jobserver::Client>` | jobserver 客户端 |
| `command_runner_` | `unique_ptr<CommandRunner>` | 命令运行器 |
| `status_` | `Status*` | 状态输出接口 |

### 构建执行流程

```
Builder::Build(err)
  ├─ 计划已就绪，plan_.more_to_do() 循环
  │   ├─ while CanRunMore() && plan_.work_ready()
  │   │   ├─ 若使用 jobserver，TryAcquire() 获取 token
  │   │   ├─ edge = plan_.FindWork()
  │   │   └─ StartEdge(edge) → command_runner_->StartCommand(edge)
  │   ├─ result = command_runner_->WaitForCommandOrJobserverToken(true)
  │   ├─ if result.command_completed():
  │   │   └─ FinishCommand(result.GetCommandCompleted(), err)
  │   │       ├─ ExtractDeps()  // 提取 MSVC /showIncludes 依赖
  │   │       ├─ build_log_->RecordCommand()
  │   │       └─ plan_.EdgeFinished()
  │   └─ if result.jobserver_token_available():
  │       └─ 继续循环（新 token 可启动新命令）
  └─ 返回 exit_code_
```

---

## BuildResult 结构体

**头文件**：`src/build_result.h`

存储执行构建命令的结果，使用 `std::variant` 作为代数数据类型。

### 嵌套类型

| 类型 | 说明 |
|------|------|
| `CommandCompleted` | 命令完成，含 edge、status（ExitStatus）、output |
| `JobserverTokenAvailable` | Jobserver token 可用，无命令完成 |
| `Interrupted` | 等待时被中断 |
| `Finished` | 无更多工作（DryCommandRunner/FakeCommandRunner 使用） |

### 辅助方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `finished() const` | `bool` | 是否已完成 |
| `interrupted() const` | `bool` | 是否被中断 |
| `jobserver_token_available() const` | `bool` | jobserver token 是否可用 |
| `command_completed() const` | `bool` | 命令是否完成 |
| `exit_status() const` | `ExitStatus` | 映射到退出码 |
| `success() const` | `bool` | 是否成功退出（ExitSuccess） |
| `GetCommandCompleted()` | `CommandCompleted&` | 获取 CommandCompleted 引用（非 command_completed 时运行时错误） |
