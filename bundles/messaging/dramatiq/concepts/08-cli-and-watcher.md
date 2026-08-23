---
type: concept
title: "CLI 与 Watcher"
description: "dramatiq 命令行参数解析、多进程 fork 模型、信号处理与优雅关闭、watchdog 文件监听热重载"
tags: [dramatiq, task-queue, cli, multiprocessing, signals, watcher, hot-reload]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-23" }
verified: { by: "process:v-pending", at: "2026-08-23" }
status: stable
stale_after: 2027-08-23
sources:
  references: []
  facts: [F-075, F-076, F-077, F-078, F-079, F-080, F-081, F-082, F-096]
---

# 08 · CLI 与 Watcher

## 入口

```bash
python -m dramatiq some_module:broker [options]
# 或
dramatiq some_module:broker [options]
```

`__main__.py` 仅调用 `cli.main()` 并 `sys.exit()`。

## 命令行参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `broker`（位置） | 必填 | Broker 路径，格式 `module` 或 `module:variable` |
| `modules`（位置） | 空 | 额外导入的 Python 模块 |
| `--processes, -p` | CPU 核数 | Worker 进程数 |
| `--threads, -t` | 8 | 每进程 Worker 线程数 |
| `--path, -P` | `.` | 模块导入路径 |
| `--queues, -Q` | 所有队列 | 监听的队列白名单 |
| `--pid-file` | 无 | PID 文件路径 |
| `--log-file` | stderr | 日志文件路径 |
| `--watch` | 无 | 文件监听目录（开发模式热重载） |
| `--watch-use-polling` | False | 使用轮询而非系统事件 |
| `--worker-shutdown-timeout` | 600000 | Worker 关闭超时（毫秒） |
| `--worker-fork-timeout` | 30000 | 等待 Worker 启动超时（毫秒） |
| `--use-spawn` | False | 使用 spawn 而非 fork |
| `--fork-function, -f` | 空 | 在独立 fork 进程中运行的函数 |
| `--skip-logging` | False | 不调用 logging.basicConfig |
| `--verbose, -v` | 0 | 日志详细度（0=INFO, 1=DEBUG） |

## import_broker

支持三种 broker 指定方式：

1. **模块路径**（`some_module`）：模块导入后调用 `get_broker()`
2. **模块:变量**（`some_module:redis_broker`）：导入模块并获取属性
3. **模块:可调用对象**（`some_module:setup_broker`）：导入后调用该函数，再 `get_broker()`
4. **模块:属性链**（`some_module:app.broker`）：用 `functools.reduce(getattr, ...)` 链式访问

变量必须是 `Broker` 实例，否则抛出 `ImportError`。

## 多进程模型

### 主进程职责

1. 解析参数、设置 PID 文件、配置日志
2. fork N 个 worker 进程
3. 等待所有 worker 启动事件（`worker_fork_timeout`）
4. fork 所有 `--fork-function` 进程（包括 middleware.forks）
5. 启动日志监听线程（聚合子进程输出）
6. 启动文件监视线程（若 `--watch`）
7. 注册信号处理器
8. 等待所有 worker 退出，若意外退出则停止其他进程

### Worker 进程

`worker_process` 函数：
1. 设置信号处理器（SIGINT 忽略，SIGTERM/SIGHUP 优雅退出）
2. 解除从主进程继承的信号阻塞
3. `import_broker` → `broker.emit_after("process_boot")`
4. 导入额外 modules
5. 通过 Canteen 共享内存将 middleware.forks 路径传回主进程
6. 创建 `Worker(broker, queues, worker_threads)` 并 `start()`
7. 循环 `time.sleep(1)` 直到 `running=False`
8. `worker.stop(timeout)` → `broker.close()`

### 日志聚合

每个子进程的 stdout/stderr 重定向到 `multiprocessing.Pipe`，主进程的 `watch_logs` 线程通过 `multiprocessing.connection.wait` 多路复用读取所有管道，写入日志文件或 stderr。日志格式包含 PID、线程名、logger 名和级别。

## 信号处理

### 处理的信号

- **SIGINT**（Ctrl+C）：转换为 SIGTERM 发送给子进程
- **SIGTERM**：优雅关闭子进程
- **SIGHUP**（Unix）：热重载——停止所有子进程后 `os.execvp` 重新执行
- **SIGBREAK**（Windows）：等同于 SIGTERM

### 两段式关闭

Worker 子进程的信号处理器：
- **第一次**收到 SIGTERM/SIGHUP：`running = False`，记录"Stopping worker process..."
- **第二次**收到：`sys.exit(RET_KILLED)` 强制杀死

### 信号阻塞

主进程在 fork 子进程前调用 `pthread_sigmask(SIG_BLOCK)` 阻塞信号，防止子进程启动过程中信号被错误处理。子进程启动后重新解除阻塞。

## Canteen 共享内存

Canteen 是基于 `ctypes.Structure` 的 1MB 共享内存缓冲区，用于 worker 进程向主进程传递 middleware.forks 函数路径。使用 double-checked locking 确保只有一个 worker 初始化（`canteen_try_init`）。

## Watcher 热重载

`setup_file_watcher` 基于 watchdog 库：

```python
def setup_file_watcher(path, use_polling=False, include_patterns=None, exclude_patterns=None):
    observer_class = PollingObserver if use_polling else Observer
    handler = _SourceChangesHandler(patterns=include_patterns, ignore_patterns=exclude_patterns)
    observer.schedule(handler, path, recursive=True)
    observer.start()
```

默认监听 `*.py` 文件变化。事件处理：
- 忽略 `opened` 事件（watchdog >= 2.3 会在文件打开时触发）
- 忽略 `closed_no_write` 事件（watchdog >= 5.0）
- 其他事件（modified/created/deleted/moved）：向当前进程发送 SIGHUP

仅支持 Unix 系统（需要 SIGHUP），需安装 `dramatiq[watch]` extra。

## 退出码

| 退出码 | 含义 |
|--------|------|
| 0 (RET_OK) | 正常退出 |
| 1 (RET_KILLED) | 被强制杀死 |
| 2 (RET_IMPORT) | 模块导入失败或参数无效 |
| 3 (RET_CONNECT) | Worker 启动时 broker 连接失败 |
| 4 (RET_PIDFILE) | PID 文件指向运行中进程或无法写入 |

## 相关概念

- [整体架构](/concepts/00-overall-architecture.md)：CLI 启动的多进程模型
- [Worker 线程模型](/concepts/03-worker-threading-model.md)：Worker 进程内的线程编排
- [Broker 抽象基类](/concepts/02-broker-abstraction.md)：worker_process 中 import_broker 与 emit_after
- [Middleware 中间件管道](/concepts/05-middleware-pipeline.md)：middleware.forks 与 after_process_boot 钩子
