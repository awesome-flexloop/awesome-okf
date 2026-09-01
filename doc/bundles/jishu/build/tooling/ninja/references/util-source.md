---
type: Reference
title: 工具集与基础设施 API 参考
description: src/util.h/cc、src/disk_interface.h/cc、src/string_piece.h、src/subprocess.h/cc、src/jobserver.h、src/metrics.h/cc 源码参考——工具函数、磁盘接口、字符串切片、子进程、Jobserver、指标收集完整 API
tags: [reference, api, util, disk, string-piece, subprocess, jobserver, metrics, c++]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ninja-util
    title: src/util.h
    path: external/libs/tools/ninja/src/util.h
  - id: ninja-disk-interface
    title: src/disk_interface.h
    path: external/libs/tools/ninja/src/disk_interface.h
  - id: ninja-string-piece
    title: src/string_piece.h
    path: external/libs/tools/ninja/src/string_piece.h
  - id: ninja-subprocess
    title: src/subprocess.h
    path: external/libs/tools/ninja/src/subprocess.h
  - id: ninja-jobserver
    title: src/jobserver.h
    path: external/libs/tools/ninja/src/jobserver.h
  - id: ninja-metrics
    title: src/metrics.h
    path: external/libs/tools/ninja/src/metrics.h
  - id: ninja-exit-status
    title: src/exit_status.h
    path: external/libs/tools/ninja/src/exit_status.h
---

# 工具集与基础设施 API 参考

> 信源文件：util.h、disk_interface.h、string_piece.h、subprocess.h、jobserver.h、metrics.h

本文档记录 Ninja 基础设施模块的完整 API，包括工具函数、磁盘 I/O、字符串处理、子进程管理、GNU Make 兼容 Jobserver 和性能指标收集。

---

## 工具函数（util.h）

### 日志与错误处理

| 函数 | 返回类型 | 说明 |
|------|---------|------|
| `Fatal(const char* msg, ...)` | `void NORETURN` | 记录致命错误并退出程序 |
| `Warning(const char* msg, ...)` | `void` | 记录警告消息 |
| `Warning(const char* msg, va_list ap)` | `void` | va_list 版本 |
| `Error(const char* msg, ...)` | `void` | 记录错误消息 |
| `Error(const char* msg, va_list ap)` | `void` | va_list 版本 |
| `Info(const char* msg, ...)` | `void` | 记录信息消息 |
| `Info(const char* msg, va_list ap)` | `void` | va_list 版本 |
| `Win32Fatal(const char* function, const char* hint = NULL)` | `void NORETURN` | Windows 专用：以函数名和 GetLastError 信息调用 Fatal |
| `GetLastErrorString()` | `string` | Windows 专用：将 GetLastError() 转换为字符串 |

### 路径处理

| 函数 | 返回类型 | 说明 |
|------|---------|------|
| `CanonicalizePath(string* path, uint64_t* slash_bits)` | `void` | 规范化路径（解析 `..`、`.`、重复斜杠）；`slash_bits` 记录 Windows 下被转换为正斜杠的反斜杠位置位掩码 |
| `CanonicalizePath(char* path, size_t* len, uint64_t* slash_bits)` | `void` | 原地修改版本 |

> **路径分隔符**：Ninja 内部统一使用 `/` 作为路径分隔符。Windows 下反斜杠在规范化时转换为正斜杠，原始位置记录在 `slash_bits` 中，可通过 `Node::PathDecanonicalized()` 恢复。磁盘接口中使用 `kPathSeparators`（Windows 为 `"\\/"`，POSIX 为 `"/"`）进行路径操作。

### 文件操作

| 函数 | 返回类型 | 说明 |
|------|---------|------|
| `ReadFile(const string& path, string* contents, string* err)` | `int` | 读取文件到字符串（文本模式，Windows 下 CRLF 转换）；返回 -errno 并填充 err |
| `Truncate(const string& path, size_t size, string* err)` | `bool` | 将文件截断为指定大小 |
| `ReplaceContent(const string& file_dst, const string& new_content, string* err)` | `bool` | 替换文件内容；POSIX 下保留 uid/gid |
| `platformAwareUnlink(const char* filename)` | `int` | 平台感知的文件删除 |
| `SetCloseOnExec(int fd)` | `void` | 设置文件描述符在 exec() 时不继承 |

### 字符串处理

| 函数 | 返回类型 | 说明 |
|------|---------|------|
| `GetShellEscapedString(const string& input, string* result)` | `void` | Bash shell 转义，追加到 result |
| `GetWin32EscapedString(const string& input, string* result)` | `void` | Win32 CommandLineToArgvW() 转义 |
| `StripAnsiEscapeCodes(const string& in)` | `string` | 移除所有 ANSI 转义码 |
| `SpellcheckStringV(const string& text, const vector<const char*>& words)` | `const char*` | 在词表中查找最接近的拼写建议 |
| `SpellcheckString(const char* text, ...)` | `const char*` | NULL 终止列表版本 |
| `islatinalpha(int c)` | `bool` | 判断是否为拉丁字母 |

### 系统信息

| 函数 | 返回类型 | 说明 |
|------|---------|------|
| `GetProcessorCount()` | `int` | 返回机器处理器数量；错误返回 0 |
| `GetLoadAverage()` | `double` | 返回系统负载平均值；错误返回负值 |
| `GetWorkingDirectory()` | `string` | getcwd() 包装 |

---

## 时间函数（metrics.h）

| 函数 | 返回类型 | 说明 |
|------|---------|------|
| `GetTimeMillis()` | `int64_t` | 获取当前时间（相对某纪元的毫秒数），仅用于测量经过时间 |

---

## StringPiece 结构体

**头文件**：`src/string_piece.h`

StringPiece 表示一个外部管理内存的字符串切片，用于减少 std::string 分配。支持从 `std::string` 和 `const char*` 的隐式转换。

### 构造函数

```cpp
StringPiece();                                    // 空切片
StringPiece(const std::string& str);              // 从 std::string 隐式构造
StringPiece(const char* str);                     // 从 C 字符串隐式构造
StringPiece(const char* str, size_t len);         // 指定长度构造
```

### 方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `AsString() const` | `string` | 转换为完整 std::string（复制数据） |
| `begin() const` | `const_iterator` | 起始迭代器 |
| `end() const` | `const_iterator` | 结束迭代器 |
| `operator[](size_t pos) const` | `char` | 下标访问 |
| `size() const` | `size_t` | 长度 |
| `empty() const` | `size_t` | 是否为空（注意：返回 size_t，非 bool） |
| `substr(size_t pos = 0, size_t count = -1) const` | `StringPiece` | 子切片 |
| `operator==` / `operator!=` | `bool` | 友元比较运算符 |

### 成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `str_` | `const char*` | 指向字符串数据的指针 |
| `len_` | `size_t` | 长度 |

---

## FileReader 接口

**头文件**：`src/disk_interface.h`

从磁盘读取文件的最小接口，是 DiskInterface 的基类。

```cpp
struct FileReader {
  enum Status { Okay, NotFound, OtherError };
  virtual Status ReadFile(const string& path, string* contents, string* err) = 0;
};
```

---

## DiskInterface 接口

**头文件**：`src/disk_interface.h`

磁盘访问抽象接口，可 mock 用于测试。实际实现为 `RealDiskInterface`。

继承自 FileReader，添加了更多磁盘操作：

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Stat(const string& path, string* err) const` | `TimeStamp` | stat() 文件，返回 mtime；缺失返回 0，错误返回 -1 |
| `MakeDir(const string& path)` | `bool` | 创建目录，失败返回 false |
| `WriteFile(const string& path, const string& contents, bool crlf_on_windows)` | `bool` | 创建文件并写入内容；crlf_on_windows 时 Windows 下 \n 转换为 \r\n |
| `RemoveFile(const string& path)` | `int` | 删除文件（类似 `rm -f`）；返回 0=成功, 1=不存在, -1=错误 |
| `ReadFile(const string& path, string* contents, string* err)` | `Status` | （继承自 FileReader）读取文件内容 |
| `MakeDirs(const string& path)` | `bool` | 递归创建所有父目录（类似 `mkdir -p`） |

### RealDiskInterface 实现

```cpp
struct RealDiskInterface : public DiskInterface {
  RealDiskInterface();
  // 实现所有 DiskInterface 虚方法
  void AllowStatCache(bool allow);    // Windows：启用/禁用 stat 缓存
#ifdef _WIN32
  bool AreLongPathsEnabled() const;  // Windows：长路径是否启用
#endif
};
```

| 成员 | 类型 | 说明 |
|------|------|------|
| `use_cache_` | `bool` | Windows：是否缓存 stat 信息 |
| `long_paths_enabled_` | `bool` | Windows：长路径支持 |
| `cache_` | `Cache`（`map<string, DirCache>`） | Windows：目录缓存 |

---

## Subprocess 结构体

**头文件**：`src/subprocess.h`

Subprocess 封装单个异步子进程。它是完全被动的：期望调用者在 fd 可读时通知它，并在 Done() 为 true 后调用 Finish() 回收子进程。

### 公共方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Finish()` | `ExitStatus` | 回收子进程并返回退出状态：ExitSuccess/ExitInterrupted/ExitFailure |
| `Done() const` | `bool` | 子进程是否已完成 |
| `GetOutput() const` | `const string&` | 获取子进程的标准输出/错误内容 |

### 私有方法（仅 SubprocessSet 可调用）

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Subprocess(bool use_console)` | — | 构造函数（私有） |
| `Start(SubprocessSet* set, const string& command)` | `bool` | 启动子进程（由 SubprocessSet::Add 调用） |
| `OnPipeReady()` | `void` | 管道可读时的回调 |

SubprocessSet 被声明为 friend。

### 平台相关成员

| 平台 | 成员 | 类型 | 说明 |
|------|------|------|------|
| Win32 | `child_` | `HANDLE` | 子进程句柄 |
| Win32 | `pipe_` | `HANDLE` | 父端管道 |
| POSIX | `fd_` | `int` | 管道读端 fd（-1 表示 console 模式） |
| POSIX | `pid_` | `pid_t` | 子进程 PID |
| POSIX | `exit_status_` | `ExitStatus` | console 模式下 waitpid(WNOHANG) 后存储 |

| 成员 | 类型 | 说明 |
|------|------|------|
| `buf_` | `string` | 输出缓冲区 |
| `use_console_` | `bool` | 是否直接使用控制台（console 池的边） |

---

## SubprocessSet 结构体

**头文件**：`src/subprocess.h`

SubprocessSet 在一组 Subprocess 周围运行 ppoll/pselect() 循环，管理子进程集合。

### WorkResult 枚举

```cpp
enum class WorkResult {
  NoWork,                    // 无工作可做（被虚假信号中断）
  JobserverTokenAvailable,   // jobserver token 可用
  SubprocFinished,           // 至少一个子进程完成
  Interrupted                // 用户中断（SIGINT/SIGHUP/SIGTERM）
};
```

### 方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Add(const string& command, bool use_console = false)` | `Subprocess*` | 添加命令启动子进程，返回 Subprocess 指针 |
| `DoWork()` | `WorkResult` | 等待子进程状态变化 |
| `NextFinished()` | `Subprocess*` | 获取下一个已完成的子进程 |
| `HasFinished() const` | `bool` | 是否有已完成的子进程 |
| `Clear()` | `void` | 清空所有子进程 |

### 公共成员

| 成员 | 类型 | 说明 |
|------|------|------|
| `running_` | `vector<Subprocess*>` | 正在运行的子进程列表 |
| `finished_` | `queue<Subprocess*>` | 已完成的子进程队列 |

### POSIX 特有

| 方法/成员 | 类型 | 说明 |
|----------|------|------|
| `SetJobserverFD(int fd)` | `void` | 设置用于监控 jobserver token 可用性的 fd |
| `IsInterrupted()` | `static bool` | 是否检测到中断信号 |
| `interrupted_` | `static volatile sig_atomic_t` | 中断信号编号（0=未中断） |
| `s_sigchld_received` | `static volatile sig_atomic_t` | SIGCHLD 信号标志 |
| `jobserver_fd_` | `int` | jobserver 监控 fd（-1=未设置） |

### Windows 特有

| 方法/成员 | 类型 | 说明 |
|----------|------|------|
| `NotifyInterrupted(DWORD dwCtrlType)` | `static BOOL WINAPI` | 控制台控制事件处理 |
| `ioport_` | `static HANDLE` | IO 完成端口 |

---

## Jobserver 命名空间

**头文件**：`src/jobserver.h`

提供 GNU Make jobserver 协议兼容的类型，用于与父 make 进程协调并发度。

### Jobserver::Slot 类

单个 job 槽位的 move-only 类型。

| 方法/静态方法 | 返回类型 | 说明 |
|-------------|---------|------|
| `IsValid() const` | `bool` | 是否为有效槽位（implicit 或 explicit） |
| `IsImplicit() const` | `bool` | 是否为隐式槽位（父进程分配的初始槽位） |
| `IsExplicit() const` | `bool` | 是否为显式槽位（从池中获取的实际 token） |
| `GetExplicitValue() const` | `uint8_t` | 获取显式槽位的字节值（无效实例调用为运行时错误） |
| `CreateExplicit(uint8_t value)` | `static Slot` | 创建显式槽位 |
| `CreateImplicit()` | `static Slot` | 创建隐式槽位 |

槽位类型：
- **无效**（默认）：获取失败
- **隐式**：父进程隐式分配的槽位（`kImplicitValue = 256`）
- **显式**：从 POSIX 管道读取或 Win32 信号量获取的实际字节值

### Jobserver::Config 结构体

```cpp
struct Config {
  enum Mode {
    kModeNone = 0,
    kModePipe,             // --jobserver-auth=R,W（不支持但可识别）
    kModePosixFifo,        // --jobserver-auth=fifo:PATH（POSIX FIFO）
    kModeWin32Semaphore,   // --jobserver-auth=SEMAPHORE_NAME（Win32）
    kModeDefault,          // 平台默认：POSIX=FIFO, Windows=Semaphore
  };
  Mode mode = kModeNone;
  std::string path;       // FIFO 路径或信号量名称
  bool HasMode();
};
```

### Jobserver 静态方法

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `ParseMakeFlagsValue(const char* makeflags_env, Config* config, string* error)` | `static bool` | 解析 MAKEFLAGS 环境变量值 |
| `ParseNativeMakeFlagsValue(const char* makeflags_env, Config* config, string* error)` | `static bool` | 解析并验证与本机系统兼容的 MAKEFLAGS |

### Jobserver::Client 类

Jobserver 客户端实例，用于从外部 jobserver 池获取/释放槽位。

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `TryAcquire()` | `virtual Slot` | 尝试获取槽位；失败返回无效 Slot |
| `Release(Slot slot)` | `virtual void` | 释放槽位回池中 |
| `GetJobserverFD() const` | `virtual int` | POSIX：返回可用于 ppoll/pselect 监控 token 可用性的 fd（-1=不可用） |
| `Create(const Config&, string* error)` | `static unique_ptr<Client>` | 从 Config 创建 Client 实例 |

---

## Metrics 模块

**头文件**：`src/metrics.h`

Metrics 模块用于调试模式（`-d stats`）下收集各操作的耗时统计。

### Metric 结构体

```cpp
struct Metric {
  std::string name;  // 指标名称
  int count;         // 命中次数
  int64_t sum;       // 总耗时（平台相关单位）
};
```

### ScopedMetric 结构体

RAII 风格的作用域计时器，构造时记录开始时间，析构时累加耗时。

```cpp
struct ScopedMetric {
  explicit ScopedMetric(Metric* metric);
  ~ScopedMetric();
};
```

### Metrics 单例

```cpp
struct Metrics {
  Metric* NewMetric(const string& name);
  void Report();  // 打印摘要报告到 stdout
};

extern Metrics* g_metrics;  // 全局指标单例指针
```

### 宏

```cpp
#define METRIC_RECORD(name)
  // 在函数顶部使用，自动记录每次函数调用的耗时
  static Metric* metrics_h_metric = g_metrics ? g_metrics->NewMetric(name) : NULL;
  ScopedMetric metrics_h_scoped(metrics_h_metric);

#define METRIC_RECORD_IF(name, condition)
  // 条件版本：condition 为 false 时不记录
```

### Stopwatch 结构体

简单秒表：

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `Elapsed() const` | `double` | Restart() 以来经过的秒数 |
| `Restart()` | `void` | 重置计时器 |

---

## ExitStatus 枚举

**头文件**：`src/exit_status.h`

```cpp
enum ExitStatus : EXIT_STATUS_TYPE {
  ExitSuccess = 0,
  ExitFailure = 1,
  ExitInterrupted = 130,
};
```

- `ExitSuccess`（0）：成功
- `ExitFailure`（1）：失败
- `ExitInterrupted`（130）：被中断（与 shell 惯例一致）

Windows 下底层类型为 `unsigned long`，POSIX 下为 `int`。

---

### 代码示例

```cpp
// 路径规范化
string path = "foo/../bar/baz.h";
uint64_t slash_bits = 0;
CanonicalizePath(&path, &slash_bits);
// path → "bar/baz.h"

// 文件读取
string contents, err;
int result = ReadFile("build.ninja", &contents, &err);
if (result < 0) {
  Error("read failed: %s", err.c_str());
}

// 子进程管理
SubprocessSet subprocs;
Subprocess* subproc = subprocs.Add("gcc -c foo.c -o foo.o");
while (!subproc->Done()) {
  auto wr = subprocs.DoWork();
  if (wr == SubprocessSet::WorkResult::Interrupted) break;
}
ExitStatus status = subproc->Finish();
string output = subproc->GetOutput();
delete subproc;

// Jobserver 客户端
Jobserver::Config config;
string error;
if (Jobserver::ParseNativeMakeFlagsValue(getenv("MAKEFLAGS"), &config, &error)
    && config.HasMode()) {
  auto client = Jobserver::Client::Create(config, &error);
  if (client) {
    auto slot = client->TryAcquire();
    if (slot.IsValid()) {
      // 执行命令...
      client->Release(std::move(slot));
    }
  }
}

// 指标记录
// 在函数开头：
METRIC_RECORD("parse manifest");
// 函数执行期间自动计时
```
