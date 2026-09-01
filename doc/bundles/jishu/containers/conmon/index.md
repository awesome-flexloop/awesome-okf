# conmon：OCI 容器运行时监控器

conmon 是一个使用 C 语言编写的 OCI（Open Container Initiative）容器运行时监控器，设计为低内存占用的守护进程。它在容器管理器（Podman、CRI-O）和底层 OCI 运行时（runc、crun）之间充当监控程序和通信工具，每个运行的容器对应一个 conmon 实例。

conmon 的核心职责包括：双 fork 守护进程化、容器生命周期监控、终端附加（attach）、日志记录、cgroup OOM 检测、退出状态持久化。

## 📚 快速导航

### [概念文档](concepts/index.md)

**入门：**
- [00-conmon定位与架构概览](concepts/00-introduction.md) — conmon是什么、在容器栈中的位置、核心职责、架构概览 ⭐

**核心：**
- [01-进程生命周期管理](concepts/01-process-lifecycle.md) — 双fork守护进程化、setsid新会话、subreaper子收割者机制
- [02-事件循环与信号处理](concepts/02-event-loop.md) — GMainLoop事件驱动、signalfd处理SIGCHLD、self-pipe安全唤醒
- [03-cgroup与OOM检测](concepts/03-cgroup-oom.md) — cgroup v1 eventfd vs v2 inotify机制、OOM分数自我保护
- [04-终端附加与日志管理](concepts/04-attach-logging.md) — console socket、FIFO控制协议、日志写入与轮转

### [实践示例](examples/index.md)
- [01-基本命令行使用](examples/01-basic-usage.md) — 编译安装、手动启动容器、观察日志和退出状态 ⭐入门
- [02-与Podman/CRI-O集成](examples/02-integration.md) — 容器管理器调用流程、管道同步、attach流程、OOM检测集成

### [信源参考](references/index.md)
- [README项目说明](references/readme-source.md) — 项目定位、构建依赖、安装方式
- [主入口信源](references/conmon-source.md) — main函数、双fork、GMainLoop、进程管理API
- [cgroup与OOM检测信源](references/cgroup-source.md) — cgroup v1/v2双版本OOM检测实现
- [OOM分数调整信源](references/oom-source.md) — oom_score_adj读写、自我保护机制

## 🚀 核心特性

| 特性 | 说明 |
|------|------|
| 🔄 双fork守护进程化 | 脱离父进程，setsid创建新会话，subreaper收养孤儿进程 |
| 🛡️ OOM自我保护 | oom_score_adj=-1000免疫OOM killer，容器exec前恢复 |
| ⚡ GMainLoop事件驱动 | signalfd处理SIGCHLD、self-pipe安全唤醒、inotify/eventfd监控OOM |
| 🖥️ 终端附加 | Unix socket支持运行时attach，FIFO协议处理窗口调整和日志重开 |
| 📝 日志管理 | 支持文件日志（CRI格式）、journald、passthrough三种后端，支持轮转 |
| 🚨 cgroup OOM检测 | v1使用eventfd即时通知，v2使用inotify+memory.events计数器比较 |
| 📊 退出状态持久化 | exit文件记录退出码，oom文件标记OOM杀死，支持inotify监控 |

## 🎯 推荐学习路径

1. **理解定位**：阅读 [00-introduction](concepts/00-introduction.md) 了解 conmon 解决什么问题
2. **掌握进程模型**：学习 [01-process-lifecycle](concepts/01-process-lifecycle.md) 理解双fork和subreaper机制
3. **理解事件驱动**：学习 [02-event-loop](concepts/02-event-loop.md) 掌握GMainLoop如何驱动整个监控
4. **深入核心功能**：学习 [03-cgroup-oom](concepts/03-cgroup-oom.md) 和 [04-attach-logging](concepts/04-attach-logging.md)
5. **动手实践**：完成 [01-basic-usage](examples/01-basic-usage.md) 手动编译和运行 conmon
6. **理解集成**：阅读 [02-integration](examples/02-integration.md) 了解 Podman 如何使用 conmon
7. **源码精读**：配合 [references](references/index.md) 信源文档直接阅读源码

## 🔗 外部资源

- **GitHub 仓库**：[containers/conmon](https://github.com/containers/conmon)
- **Podman**：[podman.io](https://podman.io/)
- **CRI-O**：[cri-o.io](https://cri-o.io/)
- **OCI 运行时规范**：[opencontainers/runtime-spec](https://github.com/opencontainers/runtime-spec)
- **runc**：[opencontainers/runc](https://github.com/opencontainers/runc)
- **crun**：[containers/crun](https://github.com/containers/crun)

## 🏗️ 架构概览

```
Podman/CRI-O（短生命周期CLI）
    │
    │ fork/exec + 管道同步
    ▼
conmon 守护进程（每个容器一个实例）
    ├── 双fork + setsid + subreaper
    ├── GMainLoop 事件循环
    │   ├── signalfd → SIGCHLD → waitpid → 回调分发
    │   ├── self-pipe → 安全唤醒
    │   ├── inotify/eventfd → cgroup OOM 检测
    │   ├── g_timeout → 超时杀死
    │   ├── stdin/stdout/stderr fd → stdio_cb → 日志写入
    │   └── console socket → terminal_accept_cb → attach
    ├── fork/exec runc create
    │   └── runc init → 容器进程
    │       └── (父runc退出后被conmon subreaper收养)
    └── 退出时：exit文件 + oom文件
```

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
