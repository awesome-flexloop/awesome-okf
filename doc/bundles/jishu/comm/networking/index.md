---
okf_version: "0.2"
type: group
title: "🌐 SSH 与远程控制"
description: "Python SSH/远程控制生态——从底层协议实现到高层自动化框架的系统化中文源码教程"
---

# 🌐 SSH 与远程控制（Networking）

本组收录 Python 生态中 SSH 协议实现与远程控制相关的开源库，覆盖从底层 SSH2 协议栈到高层部署自动化、从同步到异步、从通用 SSH 到网络设备专用的完整范式谱。

> **学习建议**：paramiko 是整个生态的基础层，fabric 和 netmiko 构建于其上；asyncssh 是独立的异步替代实现；pexpect 提供交互式终端控制能力；scrapli 代表 Zig+Python 混合架构的新一代网络自动化。

## 生态关系概览

```
┌─────────────────────────────────────────────────────────────────┐
│            🏢 应用层：部署/运维自动化 & 网络设备管理            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   fabric     │  │   netmiko    │  │      scrapli         │  │
│  │ 高层部署框架  │  │ 多厂商网络SSH │  │ Zig+Python 现代引擎  │  │
│  │(invoke+paramiko)│ │(paramiko)   │  │(CLI/NETCONF 双驱动)  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│         │    ┌────────────┘                      │              │
│         ▼    ▼                                   ▼              │
│  ┌─────────────────┐              ┌─────────────────────────┐   │
│  │    paramiko     │◄─────────────│  asyncssh (独立异步实现)  │   │
│  │ SSH2 协议栈基础  │   transport  │  asyncio SSHv2 客户端    │   │
│  │ Transport/Channel│   插件可选   │  服务端/SFTP/SCP/转发    │   │
│  └─────────────────┘              └─────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    pexpect (互补层)                        │   │
│  │     Expect 式交互控制——spawn/expect/send/interact        │   │
│  │     PTY 子进程、pxssh SSH 登录、REPL 封装                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 推荐学习路径

| 顺序 | 知识包 | 范式 | 一句话简介 |
|------|--------|------|-----------|
| 1 | [paramiko](paramiko/index.md) | 同步·基础 | 纯 Python SSH2 协议库——Transport 加密隧道、Channel 多路复用、SSHClient 高层门面、SFTPClient、密钥体系、端口转发、服务端 |
| 2 | [fabric](fabric/index.md) | 同步·高层 | 基于 paramiko+invoke 的远程执行框架——Connection、Config、Group 并行、Remote Runner、文件传输、Tunnel 跳板机 |
| 3 | [netmiko](netmiko/index.md) | 同步·网络 | 多厂商网络设备 SSH——ConnectHandler 工厂、BaseConnection 模板方法、100+ 驱动、SSHDetect 自动探测 |
| 4 | [asyncssh](asyncssh/index.md) | 异步·全栈 | asyncio SSHv2 全栈——SSHClientConnection 协程、Channel→Stream→Process 三层 IO、SFTP v3-v6、SCP、端口转发、服务端 |
| 5 | [pexpect](pexpect/index.md) | 交互控制 | Expect 式终端自动化——spawn PTY 子进程、expect 正则匹配、pxssh SSH 登录、PopenSpawn 跨平台、REPLWrapper |
| 6 | [scrapli](scrapli/index.md) | 混合架构 | Zig+Python 新一代网络自动化——Cli/Netconf 双驱动、FFI ctypes 绑定、BIN/SSH2/Telnet 可插拔 Transport、YAML 平台定义 |

## 范式对比

| 维度 | paramiko | fabric | netmiko | asyncssh | pexpect | scrapli |
|------|----------|--------|---------|----------|---------|---------|
| 执行模型 | 同步 | 同步 | 同步 | 异步 (asyncio) | 同步 (PTY) | 同步+异步 |
| 抽象层级 | 协议栈 | 应用框架 | 设备驱动 | 协议栈 | 交互控制 | 设备驱动 |
| 底层实现 | 纯 Python | paramiko+invoke | paramiko | 纯 Python | 纯 Python | Zig 核心+Python FFI |
| SFTP 支持 | ✅ | ✅ (封装) | ✅ (SCP) | ✅ 全版本 | ❌ | ❌ |
| 端口转发 | ✅ | ✅ (Tunnel) | ❌ | ✅ | ❌ | ❌ |
| 服务端能力 | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| 网络设备专用 | ❌ | ❌ | ✅ 100+ 驱动 | ❌ | ❌ | ✅ 44 平台 |
| NETCONF | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| 交互式 Shell | ✅ invoke_shell | ✅ | ✅ (PTY) | ✅ create_process | ✅ (核心能力) | ✅ send_input |

## 知识包统计

| 知识包 | 概念 | 示例 | 信源 | 源码事实 | 版本 |
|--------|------|------|------|---------|------|
| [paramiko](paramiko/index.md) | 11 | 5 | 1 | 123 | 5.0.0 |
| [fabric](fabric/index.md) | 9 | 4 | 1 | 92 | 4.0.0 |
| [netmiko](netmiko/index.md) | 10 | 4 | 1 | 120 | 4.7.0 |
| [asyncssh](asyncssh/index.md) | 12 | 4 | 1 | 180 | 2.24.0 |
| [pexpect](pexpect/index.md) | 9 | 4 | 1 | 77 | 4.9.0 |
| [scrapli](scrapli/index.md) | 9 | 4 | 1 | 133 | 2.0-dev |
| **合计** | **60** | **25** | **6** | **725** | — |

```{toctree}
:hidden:
:maxdepth: 7

paramiko/index
fabric/index
netmiko/index
asyncssh/index
pexpect/index
scrapli/index
```
