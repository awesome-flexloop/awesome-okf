---
type: Concept
title: 并行执行与并发控制
description: 单线程事件循环+子进程并行模型、-j 参数、Pool 并发池、Jobserver 集成与最佳实践
tags: [ninja, concept, parallel, concurrency, pool, jobserver, subprocess, multiprocess]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# 并行执行与并发控制

Ninja 的核心优势之一是高效的并行构建。Ninja 采用单线程事件循环加多子进程的并行模型，通过 `-j` 参数、Pool 机制和 Jobserver 集成实现灵活的并发控制。

## 并行模型：单线程事件循环 + 多子进程

Ninja **不使用多线程**，而是采用单线程事件循环 + 多子进程的并行模型：

```
┌──────────────────────────────────────────────────────────┐
│                    Ninja 主进程（单线程）                  │
│                                                          │
│  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐     │
│  │  Plan   │   │Builder │   │Command │   │Subproc-│     │
│  │ 调度    │──→│ 主循环  │──→│Runner  │──→│essSet  │     │
│  └────────┘   └────────┘   └────────┘   └────┬───┘     │
│       ↑                                      │          │
│       │ FindWork()              IO多路复用    │          │
│       │                         select/epoll │          │
│       └──────────────────────────────────────┘          │
│                                    │                     │
│                    ┌───────────────┼───────────────┐     │
│                    ↓               ↓               ↓     │
│              ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│              │ 子进程 1  │   │ 子进程 2  │   │ 子进程 N  │ │
│              │ (gcc)    │   │ (gcc)    │   │ (ld)     │ │
│              └──────────┘   └──────────┘   └──────────┘ │
└──────────────────────────────────────────────────────────┘
```

### 为什么不用多线程？

1. **构建命令本身是进程**：编译、链接等操作本身就是独立进程，多线程不会增加并行度
2. **避免同步开销**：单线程不需要锁、互斥量、条件变量等同步原语，代码更简单、更可靠
3. **IO 多路复用更高效**：等待子进程完成本质是 IO 操作（等待管道可读/进程退出），`select`/`epoll`/`WaitForMultipleObjects` 比线程等待更轻量
4. **内存安全**：C++ 多线程编程容易引入数据竞争，单线程天然避免

### 主循环的并行逻辑

```cpp
// Builder::Build() 主循环中的并行调度
while (plan_.more_to_do()) {
  // 启动尽可能多的就绪 Edge（受并行度限制）
  while (command_runner_->CanRunMore() && plan_.work_ready()) {
    Edge* edge = plan_.FindWork();
    StartEdge(edge);  // 启动子进程
  }
  // 等待至少一个子进程完成
  if (command_runner_->size() > 0) {
    auto result = command_runner_->WaitForCommand(err);
    EdgeFinished(result.edge, result.success, err);
  }
}
```

关键：`CanRunMore()` 同时检查全局并行数限制（`-j`）和 Edge 所在 Pool 的深度限制。

## -j 参数：控制最大并行数

`-j N`（或 `--jobs N`）指定最大并行子进程数：

```bash
ninja -j4     # 最多 4 个并行任务
ninja -j8     # 最多 8 个并行任务
ninja         # 不指定 -j 时，默认值通常是 CPU 核心数+2？
              # 实际默认值：Ninja 默认尝试检测 CPU 核心数
```

### 默认并行数

Ninja 的默认并行数在不同版本中有所不同，通常是系统 CPU 核心数。可以通过 `-j` 显式指定以获得确定行为：

```bash
# Linux：查看 CPU 核心数
nproc

# macOS
sysctl -n hw.ncpu

# Windows（PowerShell）
$env:NUMBER_OF_PROCESSORS
```

### 并行数选择策略

| 任务类型 | 推荐 -j 值 | 原因 |
|---------|-----------|------|
| CPU 密集型（编译） | CPU 核心数 | 每个编译任务占满一个 CPU 核心 |
| IO 密集型（小文件复制、脚本） | 核心数 × 2 或更高 | 任务等待 IO 时 CPU 空闲，可以更多并行 |
| 内存密集型（链接 LTO） | 小于核心数 | 每个链接任务消耗大量内存，过多并行会 OOM |
| 混合工作负载 | 核心数 | 默认值通常最佳 |

## Pool 机制：限制特定规则的并发度

[Pool](../references/state-source.md) 提供细粒度的并发控制，允许限制特定类型命令的最大并行数，而不影响其他命令。

### 为什么需要 Pool？

`-j` 参数控制全局并行度，但某些操作需要不同的并发限制：
- **链接**：内存密集型，并行太多会耗尽内存（特别是 LTO 链接）
- **代码生成**：可能使用大量内存或有特殊的资源限制
- **交互式命令**：需要独占终端（console 池）

### Pool 定义和使用

```ninja
# 定义池
pool <name>
  depth = <N>    # 最大并行数
```

**示例：限制链接并发**

```ninja
# 链接池：最多 2 个链接任务并行
pool link_pool
  depth = 2

# 编译不受限制（使用 -j 全局并行度）
rule cc
  command = gcc -c $in -o $out
  description = CC $out

# 链接使用 link_pool
rule link
  command = gcc $in -o $out
  description = LINK $out
  pool = link_pool    # 规则级别指定池

build main.o: cc main.c
build util.o: cc util.c
build main: link main.o util.o
```

**示例：build 块级别覆盖池**

```ninja
rule heavy_link
  command = g++ -flto $in -o $out
  pool = link_pool

# 特定目标使用更深的池
build huge_app: heavy_link $(all_objs)
  pool = console    # build 块覆盖：直接终端输出
```

### console 池

Ninja 内置了一个特殊的池 `console`，深度为 1：

```ninja
rule configure
  command = cmake ..
  pool = console
  generator = 1
```

console 池的特点：
- **深度始终为 1**：同一时间只能有一个 console 池命令运行
- **直接终端访问**：命令直接连接到标准输入/输出/错误，不缓冲输出
- **实时交互**：可以接收用户输入（如 `cmake` 的交互提示）
- **输出不混叠**：console 池命令的输出直接打印，不被 Ninja 的 `[N/M]` 前缀包装

非 console 池的命令输出被 Ninja 缓冲，命令完成后才一次性打印（带 `[N/M]` 前缀），避免并行构建时输出交错混乱。

### Pool 计数机制

```cpp
// StartEdge 中检查 Pool
bool CommandRunner::CanRunMore() {
  if (subprocs_.size() >= config_.parallelism)
    return false;  // 全局并行度限制
  // 具体 Edge 的 Pool 检查在 StartEdge 中
  return true;
}

bool Builder::StartEdge(Edge* edge, string* err) {
  // 检查 Pool 深度
  if (edge->pool_ && edge->pool_->current_use_ >= edge->pool_->depth()) {
    return false;  // 该池已满，不能启动
  }
  // ... 启动命令
  edge->pool_->current_use_++;
  return true;
}

// FinishEdge 中释放
void Builder::FinishEdge(Edge* edge, ...) {
  edge->pool_->current_use_--;
  // ...
}
```

### Pool 的实际使用场景

| 场景 | Pool 配置 | 原因 |
|------|----------|------|
| 限制链接并发 | `pool link_pool / depth = 2` | 链接（尤其 LTO）内存消耗大 |
| CMake 重新配置 | `pool = console` | 需要终端输出和交互 |
| 代码生成器 | `pool codegen_pool / depth = 1` | 生成器可能写入同一文件 |
| 测试执行 | `pool test_pool / depth = N` | 测试可能有端口等资源限制 |
| 打包/安装 | `pool = console` | 需要看到进度输出 |

## Jobserver 集成：与 GNU Make 共享并行令牌

Ninja 支持 GNU Make 的 **jobserver 协议**，允许 Ninja 作为 Make 的子进程时共享并行令牌，避免过度并行。

### 问题背景

当 Make 调用 Ninja（或反过来）时，如果各自使用 `-j`，并行数会相乘：

```
make -j8
  └─ ninja -j8    # 总共可能 64 个并行进程！
       └─ gcc (×8)
       └─ gcc (×8)
```

Jobserver 协议解决了这个问题：父进程（如 make）创建一个令牌管道，子进程在启动任务前必须先获取令牌。

### Ninja 的 Jobserver 实现

[Jobserver::Client](../references/util-source.md) 实现 POSIX 平台的 jobserver 客户端：

```cpp
namespace Jobserver {
class Client {
public:
  void Init();     // 从 MAKEFLAGS 环境变量解析 jobserver 参数
  bool Acquire();  // 获取一个令牌（从管道读一个字节）
  void Release();  // 释放一个令牌（向管道写一个字节）
};
}
```

### 工作机制

1. Make 通过 `MAKEFLAGS` 环境变量传递 jobserver 文件描述符（如 `--jobserver-fds=3,4`）
2. Ninja 启动时，`Jobserver::Client::Init()` 解析 `MAKEFLAGS`，获取读/写管道 FD
3. 启动子进程前，`Acquire()` 从管道读取一个字节（阻塞直到有令牌可用）
4. 子进程完成后，`Release()` 向管道写入一个字节（归还令牌）

```
Make (父进程，-j4)
  │ 创建管道，写入 3 个令牌（N-1 个用于子进程）
  │
  ├─ ninja (子进程)
  │    │ Jobserver::Client 从 MAKEFLAGS 获取管道 FD
  │    │ 启动 gcc 前 Acquire() → 读一个字节（获得令牌）
  │    │ gcc 完成后 Release() → 写一个字节（归还令牌）
  │    └─ gcc × (动态数量，受 Make 总令牌限制)
  │
  └─ 其他 make 子任务
       └─ 同样通过令牌获取并行权限
```

### Windows 上的 Jobserver

Windows 不支持 POSIX 管道继承方式的 jobserver 协议，Ninja 在 Windows 上使用信号量实现类似机制（或较新版本支持 named semaphore）。

### 使用方式

通常不需要显式配置——当 Ninja 检测到 `MAKEFLAGS` 环境变量包含 jobserver 信息时，自动启用 Jobserver 集成。如果你通过 Make 调用 Ninja，Make 会自动设置这个环境变量。

如果你想让 Ninja 扮演类似 make 的角色（向子进程传递 jobserver），需要使用 Ninja 的 jobserver 支持（较新版本）。

## SubprocessSet IO 多路复用

[SubprocessSet](../references/util-source.md) 是跨平台的子进程管理器，使用 IO 多路复用等待子进程完成。

### POSIX 实现：select/poll/epoll

```
┌─────────────────────────────────────────────┐
│           SubprocessSet (POSIX)              │
│                                              │
│  子进程管道 FD 集合：                          │
│    fd 3 (gcc stdout) ──→ 读取输出             │
│    fd 4 (gcc stderr) ──→ 读取错误输出         │
│    fd 5 (ld stdout)  ──→ ...                 │
│                                              │
│  DoWork():                                   │
│    1. 用 ppoll/epoll 等待所有 FD 可读         │
│    2. 可读的 FD → 读取数据到输出缓冲区         │
│    3. 检查子进程是否退出（waitpid WNOHANG）   │
│    4. 返回已完成的子进程列表                   │
└─────────────────────────────────────────────┘
```

### Windows 实现：WaitForMultipleObjects

```
┌─────────────────────────────────────────────┐
│         SubprocessSet (Windows)              │
│                                              │
│  进程句柄 + 管道句柄集合：                     │
│    hProcess (gcc 进程句柄)                    │
│    hStdout_R (gcc stdout 读端)               │
│    ...                                       │
│                                              │
│  DoWork():                                   │
│    WaitForMultipleObjects(handles, ...)      │
│    → 等待任一对象变为 signaled                │
│    → 进程句柄 signaled = 进程退出             │
│    → 管道句柄 signaled = 有数据可读           │
└─────────────────────────────────────────────┘
```

### 输出缓冲

对于非 console 池的命令，Ninja 缓冲其 stdout/stderr 输出。当命令完成时，一次性打印缓冲的输出（带 `[N/M]` 前缀）。这确保并行构建时多个命令的输出不会交错：

```
[1/4] CC main.o
[2/4] CC util.o
[3/4] CC foo.o
[4/4] LINK main
```

而不是实时交错的混乱输出：

```
main.c: In function 'main':
util.c: In function 'util':
main.c:5:2: warning: ...
util.c:10:3: warning: ...
```

console 池的命令不缓冲，直接连接终端。

## 并行调度策略

Ninja 的并行调度结合了关键路径优先级和 Pool 限制：

```
调度决策过程：

1. Plan.FindWork() 从 ready_ 队列取出最高优先级 Edge
   （优先级 = 关键路径长度，ComputeCriticalPath 计算）

2. Builder.StartEdge() 检查是否可以启动：
   a. 全局并行数 < -j？
   b. Edge 的 Pool 当前使用数 < depth？
   c. （如果启用了 Jobserver）能获取令牌？

3. 如果可以启动 → 启动子进程
   如果不行 → 尝试下一个优先级较低的 Edge
   （避免因为高优先级 Edge 被 Pool 阻塞而空等）
```

这种策略确保：
- 关键路径上的任务优先启动
- 但不会因为等待 Pool 资源而让 CPU 空闲（低优先级的非 Pool 任务可以填充）
- Pool 限制被严格遵守

## 并行构建最佳实践

### 1. 合理设置 -j

```bash
# 编译为主：-j 设为 CPU 核心数
ninja -j$(nproc)

# 内存有限的机器：适当减少
ninja -j4   # 在 8 核但内存只有 8GB 的机器上

# CI 环境：通常使用核心数或容器限制的 CPU 数
```

### 2. 对链接使用 Pool

```ninja
# 强烈推荐：大项目链接非常耗内存
pool link_pool
  depth = 1    # 保守值：一次只链接一个
  # 或 depth = 2

rule link
  command = g++ $in -o $out
  pool = link_pool
```

### 3. 对 LTO 链接使用更深的限制

```ninja
# LTO（链接时优化）链接极其耗内存和 CPU
pool lto_pool
  depth = 1

rule lto_link
  command = g++ -flto $in -o $out
  pool = lto_pool
```

### 4. 交互式命令使用 console 池

```ninja
rule cmake_configure
  command = cmake ..
  pool = console
  generator = 1

rule install
  command = cmake --install .
  pool = console
```

### 5. 使用 depfile 最大化并行度

正确配置 `deps = gcc/msvc` + `depfile =` 可以让 Ninja 发现更多隐式依赖，从而更精确地确定哪些任务可以并行：

```ninja
# 好：deps + depfile 让 Ninja 知道 main.o 依赖哪些头文件
rule cc
  command = gcc $cflags -MMD -MF $out.d -c $in -o $out
  depfile = $out.d
  deps = gcc
```

没有正确的 depfile，要么会遗漏依赖导致错误的并行构建（编译时找不到头文件），要么过于保守（不并行）。

### 6. 利用 restat 减少连锁重建

```ninja
# 对可能输出相同内容的生成器使用 restat
rule generate
  command = codegen $in -o $out
  restat = 1
```

restat 可以避免不必要的下游重建，保持更多任务可并行。

### 7. 监控并行效率

```bash
# 查看实际执行了多少任务
ninja -d stats  # 输出性能统计

# 查看依赖图和关键路径
ninja -t graph main | dot -Tpng -o graph.png

# dry run 查看将执行的命令数
ninja -n | wc -l
```

## 相关概念

- [构建执行管线](04-build-execution.md) — Builder 主循环和 StartEdge/FinishEdge 流程
- [Manifest 语言详解](05-manifest-language.md) — pool 语句语法
- [子命令与工具](08-subcommands-tools.md) — -t graph 可视化依赖图
- [工具与IO API](../references/util-source.md) — Subprocess、SubprocessSet、Jobserver 的完整 API
- [构建执行 API](../references/build-source.md) — Builder、Plan、BuildConfig 的完整 API
- [状态管理 API](../references/state-source.md) — Pool 的完整 API
