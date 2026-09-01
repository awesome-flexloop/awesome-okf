---
type: ReferenceIndex
title: conmon-rs 信源参考索引
description: conmon-rs 项目信源文档导航，基于源码和官方文档提取的参考资料
tags: [conmon-rs, reference, index, source-code]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-26T00:00:00+08:00" }
status: stable
stale_after: 2027-08-26
---

# conmon-rs 信源参考索引

本索引列出 conmon-rs 知识包的所有信源参考文档，基于项目源码和官方文档提取。

## 项目概览信源

| 文档 | 源位置 | 内容 |
|------|--------|------|
| [README 信源](readme-source.md) | `README.md` | 项目定位、双组件架构、Pod 级监控设计、目标特性、二进制获取方式 |

## 源码结构信源

### Rust 组件（conmon-rs/）

| Crate | 路径 | 核心内容 |
|-------|------|----------|
| conmon-common | `conmon-rs/common/` | Cap'n Proto 协议定义、共享类型、build.rs 代码生成 |
| conmonrs-cli | `conmon-rs/client/` | Rust 命令行客户端（conmonrs-cli 二进制） |
| conmonrs（服务器） | `conmon-rs/server/` | 核心服务器实现、容器生命周期管理、RPC 服务、日志后端 |

### Rust 服务器核心模块（conmon-rs/server/src/）

| 模块 | 文件 | 职责 |
|------|------|------|
| 主入口 | `main.rs` | 二进制入口点（conmonrs） |
| 服务器 | `server.rs`、`listener.rs` | 服务器主逻辑、连接监听 |
| RPC | `rpc.rs`、`capnp_util.rs` | Cap'n Proto RPC 服务实现 |
| 进程管理 | `child.rs`、`child_reaper.rs` | 容器子进程管理、子进程收割 |
| 容器 IO | `container_io.rs`、`streams.rs`、`terminal.rs`、`attach.rs` | 标准流处理、终端附加 |
| 日志 | `container_log/`、`journal.rs` | 三种日志后端（journald/CRI/JSON） |
| 配置 | `config.rs` | 服务器配置解析 |
| OOM 监控 | `oom_watcher.rs` | cgroup OOM 事件监听 |
| 遥测 | `telemetry.rs` | OpenTelemetry 追踪（可选 feature） |
| 流服务 | `streaming_server.rs`、`fd_socket.rs`、`fd_mapping.rs` | 文件描述符传递、流式服务 |

### Go 客户端（pkg/client/）

| 文件 | 内容 |
|------|------|
| `client.go` | ConmonClient 主结构体、连接管理、容器创建/启动/停止 |
| `attach.go` | 终端附加实现 |
| `capnp_util.go` | Cap'n Proto 序列化工具 |
| `consts.go` | 常量定义 |
| `errors.go` | 错误类型 |
| `remote_fds.go` | 远程文件描述符传递 |

## Cargo Workspace 配置信源

**根 Cargo.toml**：
- Workspace 成员：`conmon-rs/common`、`conmon-rs/client`、`conmon-rs/server`
- 所有 crate 版本：`1.0.1`
- License：`Apache-2.0`
- Rust edition：`2024`

**Release Profile 优化配置**：

```toml
[profile.release]
lto = true
opt-level = "z"
codegen-units = 1
panic = "abort"
strip = true
```

## Go 模块信源

- 模块路径：`github.com/containers/conmon-rs`
- Go 版本：`1.26.3`
- 核心依赖：
  - `capnproto.org/go/capnp/v3` —— Cap'n Proto Go 实现
  - `github.com/opencontainers/runc` —— OCI runc 绑定
  - `go.podman.io/common` —— Podman 通用库

## 相关概念文档

| 概念 | 路径 | 关联信源 |
|------|------|----------|
| Pod 级监控架构 | [../concepts/00-introduction.md](../concepts/00-introduction.md) | [README 信源](readme-source.md) |
| Rust 服务器与 Cap'n Proto RPC | [../concepts/01-rust-server.md](../concepts/01-rust-server.md) | Rust 源码结构、common/server crate |
| Go 客户端库集成 | [../concepts/02-go-client.md](../concepts/02-go-client.md) | pkg/client 模块 |
| 构建优化与日志后端 | [../concepts/03-build-optimization.md](../concepts/03-build-optimization.md) | Cargo.toml、container_log/ 模块 |

```{toctree}
:hidden:
:maxdepth: 7

readme-source
```
