---
type: Concept
title: scrapli2 简介
description: Zig+Python 混合架构的网络设备自动化库——什么是 scrapli2、重写背景、架构概览、安装方法
tags: [scrapli, introduction, zig, ctypes, network-automation]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:grep-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
---

# scrapli2 简介

## 什么是 scrapli2

scrapli2 是 scrapli 项目的大版本重写版，是一个面向网络设备自动化的 Python 库。与旧版纯 Python 实现不同，scrapli2 采用 **Zig + Python 混合架构**：核心协议引擎用 Zig 编写并编译为共享库（libscrapli），Python 层通过 ctypes 提供薄绑定。

scrapli2 提供两类驱动：

- **`Cli`**：面向网络设备命令行（CLI），基于 YAML 平台定义自动匹配提示符、管理模式切换、执行命令
- **`Netconf`**：面向 NETCONF 协议，提供标准 NETCONF 操作（get-config、edit-config、commit、lock 等）

> **重要**：scrapli2 仍处于开发阶段（版本 0.0.0-dev，libscrapli 0.0.1-rc.35），API 可能在正式发布前发生变化。本知识包基于 commit 343e149b6eba 的源码。

## 架构概览

```
┌─────────────────────────────────────────┐
│           Python 应用层                   │
├─────────────────────────────────────────┤
│  Cli 类          │      Netconf 类       │
│  (cli.py)        │      (netconf.py)     │
├──────────────────┼──────────────────────┤
│  Options 数据类层                         │
│  AuthOptions / SessionOptions /          │
│  TransportBinOptions / Ssh2Options / ... │
├─────────────────────────────────────────┤
│  ctypes FFI 绑定层                        │
│  ffi_types.py / ffi_mapping*.py /        │
│  ffi_options.py / ZigSlice / Cancel      │
├─────────────────────────────────────────┤
│  libscrapli 共享库（Zig 编译）             │
│  SSH/Telnet 协议 · 提示符匹配 · 模式管理   │
│  NETCONF XML · 平台定义解析               │
└─────────────────────────────────────────┘
```

核心设计特点：

- **Zig 核心**：所有网络 IO、协议状态机、提示符匹配、模式切换在 Zig 层完成
- **Python 薄绑定**：Python 类持有 Zig 对象指针（`c_void_p`），通过 ctypes 调用
- **双 API 设计**：每个操作同时提供同步和异步方法（`send_input` / `send_input_async`）
- **声明式平台定义**：44 个 YAML 文件定义不同厂商设备的提示符、模式和行为
- **可插拔 Transport**：支持系统 SSH（BIN）、libssh2（SSH2）、Telnet、测试模式

## 与其他 SSH 库的定位对比

| 特性 | scrapli2 | paramiko | asyncssh | netmiko |
|------|----------|----------|----------|---------|
| 定位 | 网络设备自动化专用 | SSH2 协议通用库 | 异步 SSH2 协议库 | 网络设备 SSH 封装 |
| 实现语言 | Zig + Python ctypes | 纯 Python | 纯 Python（asyncio） | 纯 Python（基于 paramiko） |
| 网络设备感知 | 原生支持（YAML 平台定义） | 无 | 无 | 原生支持（Python 驱动类） |
| 异步支持 | 同步/异步双 API | 仅同步 | 仅异步 | 同步/异步独立类 |
| NETCONF | 原生 `Netconf` 类 | 无 | 有（NETCONF 子系统） | 无 |
| 传输模式 | BIN/SSH2/Telnet/Test | SSH2 | SSH2 | SSH/Telnet/serial |
| Windows | 不支持 | 支持 | 支持 | 支持 |

跨束参考：
- [paramiko SSHClient 详解](../../paramiko/concepts/02-ssh-client.md) — 纯 Python SSH2 的高层接口
- [asyncssh 异步连接](../../asyncssh/concepts/02-async-connection.md) — 基于 asyncio 的异步 SSH 连接

## 安装方法

scrapli2 可通过 pip 安装（开发版）：

```bash
pip install scrapli
```

> 注意：scrapli2 的包导入名为 `scrapli`，但它是大版本重写版。旧版 scrapli（v202x）的 API 完全不兼容。

libscrapli 共享库会随 wheel 包分发，包含预编译的二进制文件。也可通过环境变量 `LIBSCRAPLI_PATH` 指定自定义路径：

```bash
export LIBSCRAPLI_PATH=/path/to/libscrapli-x86_64-linux-gnu.so.0.0.1-rc.35
```

Python 版本要求：≥ 3.10（使用了 `match/case` 语句、`X | Y` 类型联合语法等）。

### 平台支持

| 平台 | 架构 | 支持 |
|------|------|------|
| Linux glibc | x86_64, aarch64 | ✅ |
| Linux musl | x86_64, aarch64 | ✅ |
| macOS | x86_64, aarch64 | ✅ |
| Windows | 任意 | ❌（libscrapli 无 Windows 共享库） |

验证安装：

```bash
python -c "from scrapli import Cli; print('scrapli2 ready')"
```

## 核心概念速览

- **Cli**：CLI 驱动主类，管理连接生命周期和命令发送
- **Netconf**：NETCONF 驱动类，管理 NETCONF 会话和 RPC 操作
- **Options 数据类**：`AuthOptions`、`SessionOptions`、`TransportBinOptions` 等配置容器
- **Result**：操作结果对象，包含输出、失败状态、耗时、结构化解析
- **平台定义**：YAML 文件描述设备提示符、模式层级和自动化指令
- **Transport**：底层传输方式（系统 SSH / libssh2 / Telnet / 测试文件）
