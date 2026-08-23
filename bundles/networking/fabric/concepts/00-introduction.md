---
type: Concept
title: fabric 简介
description: fabric v4 是什么——基于 invoke+paramiko 的高层 SSH 命令执行库，架构设计、安装与 v1 区别
tags: [fabric, introduction, overview]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: fabric-source
    resource: /references/fabric-source.md
---

# fabric 简介

## fabric 是什么

fabric 是一个高层 Python 库，用于通过 SSH 执行 shell 命令和管理远程主机。它建立在两个成熟的底层库之上：

- **[invoke](../../../tooling/pyinvoke/index.md)**：任务执行框架，提供 Context、Config、Runner、Task、CLI Program 等基础设施
- **[paramiko](../../paramiko/concepts/00-introduction.md)**：纯 Python SSH2 协议库，提供 SSHClient、Transport、Channel、SFTPClient 等 SSH 原语

fabric 的定位是"胶水层"——它将 invoke 的任务执行模型和 paramiko 的 SSH 能力组合成一套面向远程运维的 API。

## v4 架构

```
┌─────────────────────────────────────────────┐
│              fab CLI (main.py)              │
│         Fab(Program) + Executor             │
├─────────────────────────────────────────────┤
│  Connection        Config        Group      │
│  (is-a Context)   (is-a Invoke   (list of   │
│   has-a SSHClient)  Config)      Connections)│
├─────────────────────────────────────────────┤
│  Remote Runner    Transfer     TunnelManager │
│  (is-a Runner)    (SFTP封装)   (端口转发)    │
├──────────────┬──────────────────────────────┤
│   invoke     │         paramiko             │
│ (任务/配置/   │  (SSHClient/Transport/       │
│  Runner框架)  │   Channel/SFTP/AuthStrategy) │
└──────────────┴──────────────────────────────┘
```

核心设计决策：

1. **继承而非组合 invoke 上下文**：`Connection` 直接继承 `invoke.Context`，因此可以无缝使用 invoke 的配置系统、sudo 机制、watcher 等功能
2. **组合 paramiko 客户端**：Connection 内部持有 `paramiko.SSHClient` 实例，但不暴露其完整接口，而是提供更高层的 `run`/`sudo`/`get`/`put` 方法
3. **模板方法适配 Runner**：`Remote` 继承 `invoke.Runner` 并实现 SSH channel 版本的 start/read/returncode，使 invoke 的命令执行主循环无需感知底层差异
4. **SSH config 独立体系**：OpenSSH 的 `~/.ssh/config` 文件作为独立配置层存在，不与 invoke 的配置合并体系混淆

## 安装

```bash
pip install fabric
```

带测试工具的安装：

```bash
pip install "fabric[testing]"
pip install "fabric[pytest]"
```

验证安装：

```bash
fab --version
```

fabric 4.0.0 要求 Python 3.7+，依赖 invoke、paramiko 和 decorator。

## 与 fabric v1 的区别

fabric v2（及后续 v3/v4）是对 v1 的完全重写，两者不兼容：

| 方面 | v1.x | v2+/v4 |
|------|------|--------|
| 编程模型 | 全局 `env` 字典 + 模块级函数 | 面向对象：Connection/Config/Group |
| 任务框架 | 自建 | 基于 invoke |
| 配置方式 | `env.hosts`、`env.user` 等 | invoke 六层配置 + SSH config 文件 |
| 本地执行 | `local()` 函数 | `Connection.local()` 方法 |
| 并行执行 | `@parallel` 装饰器 | `ThreadingGroup` 类 |
| 上下文管理 | 无 | Connection/Group 支持 with 语句 |
| Python 版本 | Python 2 | Python 3 only |
| 环境变量传递 | 无特殊处理 | `inline_ssh_env`（3.0 起默认 True） |

### v1 迁移

fabric 提供了 `Connection.from_v1(env)` 和 `Config.from_v1(env)` 两个备选构造器，帮助从 v1 的 `env` 字典迁移。这两个方法映射了常用的 v1 环境变量：

- `env.host_string` → `host`
- `env.user` → `user`
- `env.port` → `port`
- `env.key_filename` → `connect_kwargs.key_filename`
- `env.gateway` → `gateway`
- `env.forward_agent` → `forward_agent`
- `env.sudo_password` / `env.password` → `sudo.password` / `connect_kwargs.password`
- `env.always_use_pty` → `run.pty`
- `env.warn_only` → `run.warn`
- `env.use_ssh_config` → `load_ssh_configs`

## 适用场景

- 自动化部署脚本（fabfile）
- 批量远程命令执行
- 多主机编排与并行操作
- 文件上传下载
- SSH 隧道/跳板机端口转发
- 作为库嵌入更大的 Python 运维系统

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [Connection 详解](02-connection.md)
- [配置体系](03-configuration.md)
- [paramiko SSHClient](../../paramiko/concepts/02-ssh-client.md) — fabric 的 SSH 底层
- [pyinvoke Context 对象](../../../tooling/pyinvoke/index.md) — Connection 的父类
