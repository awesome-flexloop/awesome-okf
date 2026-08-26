---
type: Reference
title: README 信源
description: conmon-rs 项目 README 文档信源，包含项目定位、架构说明、目标特性与获取方式
tags: [conmon-rs, reference, readme, source]
sources:
  - d:\spaces\SpecWeave\external\dao\action\Containers\conmon-rs\README.md
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
---

# README 信源

本文档基于 conmon-rs 项目官方 README 提取，为其他概念文档和示例提供信源依据。

## 项目定位

**原文**：
> A pod level OCI container runtime monitor.

conmon-rs 是一个 **Pod 级别**的 OCI（Open Container Initiative）容器运行时监视器，使用 Rust（Rust编程语言）编写。

## 与 C 版本 conmon 的关系

**原文**：
> The scope of conmon-rs encompasses the scope of the c iteration of conmon, including daemonizing, holding open container standard streams, writing the exit code.
>
> However, the goal of conmon-rs also extends past that of conmon, attempting to become a monitor for a full pod (or a group of containers). Instead of a container engine creating a conmon per container (as well as subsequent conmons per container exec), the engine will spawn a conmon-rs instance when a pod is created. That instance will listen over an UNIX domain socket for new requests to create containers, and exec processes within them.

**关键差异总结**：

| 特性 | C 版本 conmon | Rust 版本 conmon-rs |
|------|---------------|---------------------|
| 监控粒度 | 单个容器 | 整个 Pod（容器组） |
| 实例数量 | 每个容器一个实例，每个 exec 再创建 | 每个 Pod 一个实例，复用处理多个容器和 exec |
| 通信方式 | 传统 Unix 信号/管道 | UNIX domain socket + RPC |
| 内存目标 | - | RSS 控制在 3-4 MB 以下 |

## 架构组成

**原文**：
> The whole application consists of two main components:
>
> 1. The Rust server: conmon-rs/server
> 1. A golang client: pkg/client
>
> The golang client should act as main interface while it takes care of creating the server instance via the Command Line Interface (CLI) as well as communicating to the server via Cap'n Proto. The client itself hides the raw Cap'n Proto parts and exposes dedicated golang structures to provide a clean API surface.

**双组件架构**：

```
┌─────────────────────────────────────────────────────────┐
│                    容器引擎 (CRI-O/Podman)                │
└───────────────────────┬─────────────────────────────────┘
                        │ Go 客户端调用
                        ▼
┌─────────────────────────────────────────────────────────┐
│              Go 客户端 (pkg/client)                      │
│  - 创建/启动 Rust 服务器进程                              │
│  - 封装 Cap'n Proto RPC 细节                             │
│  - 提供干净的 Go API                                     │
└───────────────────────┬─────────────────────────────────┘
                        │ UNIX domain socket
                        │ Cap'n Proto RPC
                        ▼
┌─────────────────────────────────────────────────────────┐
│           Rust 服务器 (conmon-rs/server)                 │
│  - 监听 RPC 请求                                         │
│  - 管理 Pod 内多个容器生命周期                            │
│  - 持有容器标准流（stdin/stdout/stderr）                 │
│  - 记录容器退出码                                        │
│  - 处理 exec 进程（无需重启实例）                        │
└───────────────────────┬─────────────────────────────────┘
                        │ fork/exec
                        ▼
              ┌──────────┴──────────┐
              ▼                     ▼
        ┌───────────┐         ┌───────────┐
        │ 容器 A    │         │ 容器 B    │  ... Pod 内多个容器
        └───────────┘         └───────────┘
```

## 目标特性

**已实现（✅）**：

- [x] Single conmon per pod —— 每个 Pod 单个 conmon 实例（MVP 后扩展目标）
- [x] Keeping RSS under 3-4 MB —— 内存占用控制在 3-4 MB 以下
- [x] Support exec without respawning a new conmon —— 支持 exec 无需重新生成 conmon 实例
- [x] API with RPC to make it extensible (should support golang clients) —— 基于 RPC 的可扩展 API，支持 Go 客户端
- [x] Use pidfds for async process exit waiting —— 使用 pidfd 进行异步进程退出等待

**计划中（🔲）**：

- [ ] Act as pid namespace init —— 作为 PID 命名空间的 init 进程
- [ ] Join network namespace to solve running hooks inside the pod context —— 加入网络命名空间以解决在 Pod 上下文中运行 hooks
- [ ] Use io_uring —— 使用 io_uring 异步 IO
- [ ] Plugin support for seccomp notification —— seccomp 通知插件支持
- [ ] Logging rate limiting (double buffer?) —— 日志速率限制
- [ ] Stats —— 统计信息
- [ ] IPv6 port forwarding —— IPv6 端口转发

## 二进制获取

**原文**：
> We provide statically linked binaries for every successfully built commit on main via our Google Cloud Storage Bucket. Our provided get script can be used to download the latest version:
>
> ```console
> > curl https://raw.githubusercontent.com/containers/conmon-rs/main/scripts/get | bash
> ```
>
> It is also possible to select a specific git SHA or the output binary path by:
>
> ```console
> > curl https://raw.githubusercontent.com/containers/conmon-rs/main/scripts/get | \
>     bash -s -- -t $GIT_SHA -o $OUTPUT_PATH
> ```
>
> The script automatically verifies the created sigstore signatures if the local system has cosign available in its $PATH.

**静态二进制下载要点**：

- 每个 main 分支成功构建的 commit 都提供静态链接二进制
- 托管在 Google Cloud Storage（cri-o/conmon-rs bucket）
- `scripts/get` 脚本自动下载最新版本
- 支持通过 `-t` 指定 git SHA，`-o` 指定输出路径
- 本地安装 cosign 时自动验证 sigstore 签名

## 相关文档

- [使用文档](https://github.com/containers/conmon-rs/blob/main/usage.md) —— conmon-rs 使用指南
- [发布文档](https://github.com/containers/conmon-rs/blob/main/release.md) —— 创建新版本流程
- [Rust API 文档](https://containers.github.io/conmon-rs/conmonrs/index.html) —— conmonrs 服务器文档
- [Go API 文档](https://pkg.go.dev/github.com/containers/conmon-rs/pkg/client) —— ConmonClient 文档
