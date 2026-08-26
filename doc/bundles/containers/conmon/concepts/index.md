# 概念文档

本目录包含 conmon OCI 容器监控器的核心概念文档，按学习路径顺序排列。

---

## 入门篇

- [00-conmon定位与架构概览](00-introduction.md) — conmon是什么、在容器栈中的位置、核心职责、架构概览 ⭐ 从这里开始

## 核心篇

- [01-进程生命周期管理](01-process-lifecycle.md) — 双fork守护进程化、setsid新会话、subreaper子收割者、pid_to_handler回调映射
- [02-事件循环与信号处理](02-event-loop.md) — GMainLoop事件驱动架构、signalfd处理SIGCHLD、self-pipe安全唤醒、超时回调
- [03-cgroup与OOM检测](03-cgroup-oom.md) — cgroup v1 eventfd机制 vs v2 inotify+轮询、memory.events解析、OOM分数自我保护
- [04-终端附加与日志管理](04-attach-logging.md) — console socket PTY、FIFO控制协议（窗口调整/日志重开）、stdio_cb日志写入、日志轮转

---

## 推荐学习顺序

1. **理解定位**：先读 [00-introduction](00-introduction.md) 了解 conmon 是什么、解决什么问题
2. **进程模型**：学习 [01-process-lifecycle](01-process-lifecycle.md) 掌握双fork和subreaper机制
3. **事件循环**：学习 [02-event-loop](02-event-loop.md) 理解GMainLoop如何驱动整个监控过程
4. **核心功能**：深入 [03-cgroup-oom](03-cgroup-oom.md) 和 [04-attach-logging](04-attach-logging.md) 了解OOM检测和IO处理
5. **动手实践**：配合 [examples](../examples/index.md) 中的示例实际运行 conmon

```{toctree}
:maxdepth: 1

00-introduction
01-process-lifecycle
02-event-loop
03-cgroup-oom
04-attach-logging
```
