---
type: Concept
title: 构建执行管线
description: Builder 主循环、Plan 调度机制、Edge 生命周期、关键路径调度与错误处理
tags: [ninja, concept, build-execution, builder, plan, command-runner, scheduling, critical-path]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# 构建执行管线

构建执行是 Ninja 的核心功能：从脏状态扫描到命令并行执行，再到结果记录，整个过程由 Builder 主循环驱动。本章详细描述 Plan 的调度机制、Edge 的生命周期、关键路径优先级计算和错误处理。

## Builder 主循环

[Builder](../references/build-source.md) 是构建执行的顶层控制器，其 `Build()` 方法实现了核心主循环：

```cpp
ExitStatus Builder::Build(string* err) {
  // 1. 打开日志、初始化 Plan
  plan_.Reset();
  // 添加目标到 Plan
  for (auto& target : state_->Defaults())
    AddTarget(target, err);
  // 准备就绪队列（计算关键路径）
  plan_.PrepareQueue();

  // 2. 主循环
  while (plan_.more_to_do()) {
    // 启动尽可能多的就绪 Edge
    while (command_runner_->CanRunMore() && plan_.work_ready()) {
      Edge* edge = plan_.FindWork();
      if (!StartEdge(edge, err))
        return kExitFailure;
    }
    // 等待至少一个命令完成
    if (command_runner_->size() > 0) {
      CommandRunner::Result result = command_runner_->WaitForCommand(err);
      EdgeFinished(result.edge, result.status == ExitSuccess, err);
    }
  }
  return kExitSuccess;
}
```

主循环是一个经典的"**拉取-执行-等待**"模式：

```
     ┌─────────────────────────────────────────────┐
     │              Builder 主循环                   │
     │                                              │
     │   ┌───────────┐    No     ┌──────────────┐  │
     │   │ more_to_do│──────────→│ 构建完成，退出 │  │
     │   └─────┬─────┘           └──────────────┘  │
     │         │ Yes                               │
     │         ↓                                   │
     │   ┌──────────────┐                          │
     │   │ CanRunMore() │ ← Pool/并行数限制         │
     │   │   &&         │                          │
     │   │ work_ready() │ ← ready_ 队列非空         │
     │   └─────┬───────┘                          │
     │         │ Yes                               │
     │         ↓                                   │
     │   ┌──────────────┐    ┌──────────────────┐ │
     │   │ FindWork()   │───→│ StartEdge()      │ │
     │   │ (取最高优先级 │    │ (求值命令、启动   │ │
     │   │  Edge)       │    │  子进程)         │ │
     │   └──────────────┘    └────────┬─────────┘ │
     │         ↑ No                    │           │
     │         │                       ↓           │
     │   ┌──────────────┐    ┌──────────────────┐ │
     │   │ WaitForCommand│←──│ 子进程运行中...   │ │
     │   │ (等待完成)    │    └──────────────────┘ │
     │   └──────┬───────┘                         │
     │          ↓                                  │
     │   ┌──────────────┐                          │
     │   │ EdgeFinished │                          │
     │   │ (更新状态、   │                          │
     │   │  记录日志、   │                          │
     │   │  检查新就绪)  │                          │
     │   └──────┬───────┘                          │
     │          └──────────→ 返回 more_to_do 检查   │
     └─────────────────────────────────────────────┘
```

### 主循环关键步骤

1. **FindWork()**：从 Plan 的 `ready_` 优先级队列中取出最高优先级的 Edge
2. **StartEdge()**：求值命令字符串（展开 `$in`/`$out` 等变量），处理 rspfile，提交给 CommandRunner 启动子进程
3. **WaitForCommand()**：阻塞等待任一子进程完成（通过 SubprocessSet 的 IO 多路复用）
4. **EdgeFinished()**：处理命令结果——成功则标记输出 Node 就绪，失败则根据 `-k` 选项决定继续或中止；然后检查是否有消费者 Edge 变为就绪，加入 `ready_` 队列

## Plan 的工作机制

[Plan](../references/build-source.md) 负责维护"哪些 Edge 需要执行"和"哪些 Edge 已经就绪"两个核心状态。

### want_ 映射：需求状态追踪

Plan 使用 `std::map<Edge*, Want> want_` 追踪每个 Edge 的需求状态：

```cpp
enum Want {
  kWantNothing = 0,   // 不需要此 Edge
  kWantToStart,       // 需要启动此 Edge（等待依赖满足）
  kWantToFinish       // 此 Edge 已启动，等待完成
};
```

状态转换：

```
kWantNothing ──(AddTarget/依赖扫描发现)──→ kWantToStart
kWantToStart ──(所有输入就绪，进入ready_)──→ kWantToFinish（StartEdge后）
kWantToFinish ──(命令完成 EdgeFinished)──→ kWantNothing（从want_移除）
```

### ready_ 优先级队列

`EdgePriorityQueue ready_` 存储所有依赖已满足、可以立即执行的 Edge。这是一个按优先级排序的最大堆，优先级由 `ComputeCriticalPath()` 计算。

### 计数字段

Plan 维护两个计数器：

- **wanted_edges_**：`want_` 中状态为 `kWantToStart` 或 `kWantToFinish` 的 Edge 数量。`more_to_do()` 返回 `wanted_edges_ > 0 && command_edges_ > 0`（或类似逻辑）。
- **command_edges_**：当前已启动但尚未完成的 Edge 数（即运行中的子进程数）。

### 调度方法

Plan 的核心调度方法：

| 方法 | 作用 |
|------|------|
| `AddTarget(Node*)` | 添加目标 Node，递归标记其 in_edge 为 kWantToStart |
| `ScheduleInitialEdges()` | 遍历所有 wanted Edge，检查依赖是否满足，满足则加入 ready_ |
| `NodeFinished(Node*)` | Node 就绪后，检查其 out_edges_，对每个消费者 Edge 检查所有输入是否就绪 |
| `EdgeMaybeReady(want_e)` | 检查 Edge 的所有输入（explicit + implicit + order-only）是否都就绪 |
| `ScheduleWork(want_e)` | 将 Edge 加入 ready_ 队列 |
| `FindWork()` | 从 ready_ 取出最高优先级的 Edge，标记为 kWantToFinish |
| `EdgeFinished(edge, result)` | 处理 Edge 完成，对其所有 outputs 调用 NodeFinished |
| `DyndepsLoaded(...)` | 加载 dyndep 后更新依赖关系，重新检查就绪状态 |

## Edge 生命周期

一个 Edge 从创建到完成经历以下阶段：

```
┌─────────────┐
│  创建        │ ManifestParser 解析 build 语句时创建
│  (解析阶段)  │ Edge* edge = new Edge(rule_);
└──────┬──────┘
       ↓
┌─────────────┐
│  标记 Dirty  │ DependencyScan::RecomputeDirty 发现需要重建
│  (脏扫描)    │ 或 AddTarget 沿 in_edge 标记为 kWantToStart
└──────┬──────┘
       ↓
┌─────────────┐
│  等待依赖    │ Edge 在 want_ 中状态为 kWantToStart
│              │ 等待所有 inputs_/implicit_deps_/order_only_deps_ 就绪
└──────┬──────┘
       ↓ 所有输入 Node 都 exists() 且 dirty_=false
┌─────────────┐
│  进入就绪队列│ ScheduleWork() 将 Edge 加入 ready_ 优先级队列
│  (ready_)   │
└──────┬──────┘
       ↓ FindWork() 取出
┌─────────────┐
│  启动执行    │ Builder::StartEdge()
│              │ - 求值命令字符串（EvaluateCommand）
│              │ - 生成 rspfile（如需要）
│              │ - 检查 Pool 深度
│              │ - CommandRunner::StartCommand()
└──────┬──────┘
       ↓ Subprocess 运行中
┌─────────────┐
│  子进程执行  │ gcc/ld/其他命令在子进程中运行
│              │ SubprocessSet::DoWork() 等待 IO 事件
└──────┬──────┘
       ↓ 子进程退出
┌─────────────┐
│  完成处理    │ Builder::FinishEdge()
│              │ - 检查退出码
│              │ - restat 检查（如设置了 restat）
│              │ - 加载 depfile（如设置了 depfile）
│              │ - 更新输出 Node 的 mtime
│              │ - 标记 outputs_ready_ = true
│              │ - Plan::NodeFinished() 传播就绪状态
│              │ - BuildLog::RecordCommand()
└──────┬──────┘
       ↓
┌─────────────┐
│  结束        │ Edge 从 want_ 移除，输出 Node 可被消费者使用
└─────────────┘
```

### StartEdge 详细流程

```cpp
bool Builder::StartEdge(Edge* edge, string* err) {
  // 1. 检查 Pool 深度限制
  if (edge->pool_ && edge->pool_->current_use_ >= edge->pool_->depth_)
    return false;  // Pool 满了，不能启动

  // 2. 求值命令
  string command = edge->EvaluateCommand();

  // 3. 处理 dry run
  if (config_.dry_run) {
    cout << command << endl;
    // 直接标记为完成，不实际执行
    return FinishEdge(edge, true, err);
  }

  // 4. 生成 rspfile（响应文件，用于超长命令行）
  if (edge->rule_->rspfile_used_) {
    string rspfile = edge->GetBinding("rspfile");
    string rspfile_content = edge->GetBinding("rspfile_content");
    disk_interface_->WriteFile(rspfile, rspfile_content);
  }

  // 5. 启动子进程
  command_runner_->StartCommand(edge);
  edge->pool_->current_use_++;
  edge->command_start_time_ = GetTimeMillis();
  return true;
}
```

### FinishEdge 详细流程

```cpp
bool Builder::FinishEdge(Edge* edge, bool success, string* err) {
  edge->outputs_ready_ = true;
  edge->pool_->current_use_--;

  if (success) {
    // 1. restat：重新 stat 输出，检查 mtime 是否真的变化
    if (edge->rule_->restat_) { /* 重新 stat，如果 mtime 未变则下游不重建 */ }

    // 2. 加载 depfile（头文件依赖）
    if (!edge->deps_loaded_ && edge->rule_->deps_type_ != Rule::deps_unknown) {
      scan_.LoadDepsFromLog(edge, err);  // 从 deps log 加载
      // 或从刚生成的 depfile 加载
    }

    // 3. 更新输出 Node 的 mtime
    TimeStamp mtime = 0;
    for (auto* output : edge->outputs_) {
      output->Stat(disk_interface_, err);
      mtime = max(mtime, output->mtime());
    }

    // 4. 记录到 BuildLog
    build_log_->RecordCommand(edge, start_time, end_time, mtime);

    // 5. 通知 Plan：输出 Node 完成
    plan_.EdgeFinished(edge, kEdgeSucceeded, err);
  } else {
    // 失败处理
    plan_.EdgeFinished(edge, kEdgeFailed, err);
    if (!config_.keep_going) return false;
  }
  return true;
}
```

## 关键路径调度

Ninja 不使用简单 FIFO 调度，而是采用**关键路径优先（Critical Path Scheduling）**策略来最小化总构建时间。

### 什么是关键路径？

关键路径是从一个 Edge 到最终目标的最长路径（按执行时间估计）。关键路径上的任何延迟都会直接增加总构建时间，因此应该优先执行。

### ComputeCriticalPath 算法

```cpp
void Plan::ComputeCriticalPath() {
  // 从目标 Node 反向遍历，计算每个 Edge 的"剩余路径长度"
  // priority = 此 Edge 的执行时间 + 下游最长路径时间

  // 使用后序遍历（先处理消费者，再处理生产者）
  for (Edge* edge : edges_in_reverse_topological_order) {
    int max_priority = 0;
    for (Node* output : edge->outputs_) {
      for (Edge* out_edge : output->out_edges_) {
        max_priority = max(max_priority, out_edge->priority_);
      }
    }
    edge->priority_ = edge->estimated_duration_ + max_priority;
  }
}
```

EdgePriorityQueue 是一个最大堆，`FindWork()` 总是取出 `priority_` 最高的 Edge。

### 调度效果

```
不使用关键路径调度（FIFO）:
  gcc main.o  ────────┐
  gcc util.o  ──┐     ├── link main ──→ 总时间 = 最长链
  gcc foo.o   ──┼─────┤
  gcc bar.o   ─┼─┐   │
               │ └───┘
               └────────→ 短任务先完成，但长任务在关键路径上可能被延迟

使用关键路径调度:
  gcc main.o  ────────┐ (main.o 在关键路径上，优先执行)
  gcc util.o  ──┐     ├── link main ──→ 总时间更短
  gcc foo.o   ──┼─────┤
  gcc bar.o   ─┼─┐   │
               │ └───┘
               └────────→ 关键路径上的任务优先，非关键路径填充空隙
```

Ninja 使用历史执行时间（从 `.ninja_log` 中获取）来估计 Edge 持续时间。首次构建时使用默认估计值。

## 错误处理

### -k 选项：继续构建

默认情况下，Ninja 在遇到第一个错误时立即中止构建。使用 `-k N` 选项可以在遇到 N 个错误后继续构建不相关的目标。`-k 0` 表示无限继续。

```bash
ninja -k0    # 尽可能多地构建，即使有错误
ninja -k2    # 遇到2个错误后停止
```

错误处理逻辑：

```cpp
void Plan::EdgeFinished(Edge* edge, EdgeResult result, string* err) {
  if (result == kEdgeFailed) {
    // 标记此 Edge 的所有输出为失败
    for (Node* output : edge->outputs_) {
      // 通知依赖这些输出的其他 Edge：它们也无法构建了
      for (Edge* out_edge : output->out_edges_) {
        if (want_[out_edge] == kWantToStart) {
          want_[out_edge] = kWantNothing;  // 取消这些 Edge
          wanted_edges_--;
        }
      }
    }
  } else {
    // 成功：传播 Node 就绪状态
    NodeFinished(output, err);
  }
}
```

当一个 Edge 失败时：
- 其输出 Node 不会被标记为就绪
- 依赖这些输出的下游 Edge 被取消（从 want_ 移除）
- 不依赖失败 Edge 的其他分支可以继续构建（如果使用了 `-k`）

## BuildConfig 配置

[BuildConfig](../references/build-source.md) 结构体控制构建行为：

```cpp
struct BuildConfig {
  int parallelism = 1;          // 最大并行子进程数（-j 参数）
  bool verbose = false;         // 详细输出（-v）
  bool dry_run = false;         // 空跑模式（-n）
  bool keep_going = false;      // 出错继续（-k）
  bool depfile_pruning = false; // depfile 裁剪
  string build_dir;             // 构建目录
  enum EdgeMode { kEdgeModeNormal, ... };
  // ...
};
```

常用配置与命令行参数的对应：

| 配置项 | 命令行参数 | 默认值 | 说明 |
|--------|-----------|--------|------|
| `parallelism` | `-j N` | CPU核心数？ | 最大并行任务数 |
| `verbose` | `-v` | false | 显示完整命令行 |
| `dry_run` | `-n` | false | 只打印命令不执行 |
| `keep_going` | `-k N` | false (N=0) | 出错继续 |
| `build_dir` | `-C DIR` | 无 | 切换到构建目录 |

## Subprocess 执行

Ninja 使用**单线程事件循环 + 多子进程**模型，而非多线程。

### 为什么不用多线程？

1. 构建命令本身就是独立进程（gcc、ld 等），多线程不会带来额外并行度
2. 单线程避免了锁、同步、线程安全等复杂性
3. 等待子进程完成是 IO 密集型操作，IO 多路复用（select/poll/epoll）比线程等待更高效

### SubprocessSet IO 多路复用

[SubprocessSet](../references/util-source.md) 管理所有运行中的子进程，使用平台特定的 IO 多路复用机制：

| 平台 | 机制 | 说明 |
|------|------|------|
| Linux | `epoll` | 高效的事件通知 |
| macOS/BSD | `poll`/`kqueue` | POSIX 标准 |
| Windows | `WaitForMultipleObjects` | Windows 原生等待 |
| 其他 POSIX | `select` | 最通用的 fallback |

```cpp
// SubprocessSet::DoWork() 核心逻辑
void SubprocessSet::DoWork() {
  // POSIX: 使用 select/poll/epoll 等待任一管道有数据可读或子进程退出
  // Windows: 使用 WaitForMultipleObjects 等待进程句柄或管道事件

  for (auto* subproc : running_) {
    if (subproc->Done()) {
      // 子进程已退出，从 running_ 中移除
      finished_.push_back(subproc);
    }
  }
}
```

每个 Subprocess 通过管道捕获标准输出/错误，SubprocessSet 在管道可读时读取输出，避免子进程因管道缓冲区满而阻塞。

### 命令输出缓冲

Ninja 会缓冲每个子进程的输出，直到命令完成后一次性打印（加上 `[N/M]` 前缀），而不是实时混在一起打印。这保证了并行构建时输出不会交错混乱。使用 `console` Pool 的命令例外——它们直接连接到终端，输出实时显示。

## 相关概念

- [架构总览](02-architecture-overview.md) — 四大模块位置与数据流
- [依赖图模型](03-dependency-graph.md) — Node-Edge 二分图与图遍历
- [并行执行与并发控制](07-parallel-execution.md) — Pool、Jobserver、并行策略
- [增量构建机制](06-incremental-build.md) — 脏状态扫描与 depfile 加载
- [构建执行 API](../references/build-source.md) — Plan、Builder、BuildConfig 的完整 API
- [工具与IO API](../references/util-source.md) — Subprocess、SubprocessSet 的完整 API
