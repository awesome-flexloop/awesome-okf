# fabric 概念文档

## 入门

* [fabric 简介](00-introduction.md) — fabric v4 是什么、基于 invoke+paramiko 的架构设计、安装与 v1 区别。
* [5分钟快速上手](01-getting-started.md) — 从安装到第一个 fab 任务、Connection 基本用法和 Result 对象。

## 核心

* [Connection 详解](02-connection.md) — 构造参数、open/close 生命周期、SSH config 集成、gateway 跳板机、命令与文件操作。
* [配置体系](03-configuration.md) — Config 六层合并、SSH config 文件独立体系、环境变量、CLI 选项与认证配置。
* [命令执行](04-command-execution.md) — run/sudo/local/shell 方法、Result 对象、PTY、warn/hide/echo、inline_ssh_env。
* [多主机并行](05-group-parallel.md) — Group/SerialGroup/ThreadingGroup、GroupResult 结果聚合、GroupException 部分失败处理。

## 高级

* [文件传输](06-file-transfer.md) — Transfer 类、get/put、SFTP 封装、路径插值、file-like 对象与权限保留。
* [隧道与跳板机](07-tunnels.md) — forward_local/forward_remote、Tunnel/TunnelManager、ProxyJump/ProxyCommand 多跳代理。
* [高级模式](08-advanced-patterns.md) — Executor 按主机分组、ConnectionCall、OpenSSHAuthStrategy、MockRemote 测试工具。

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-connection
03-configuration
04-command-execution
05-group-parallel
06-file-transfer
07-tunnels
08-advanced-patterns
```
