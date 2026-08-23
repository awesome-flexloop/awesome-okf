---
okf_version: "0.2"
---

# asyncssh 知识库

本知识包是基于 asyncio 的异步 SSH2 协议库 [asyncssh](https://asyncssh.readthedocs.io)（v2.24.0）的系统化中文教程，基于源码深度阅读生成，覆盖从快速上手到服务端开发的完整知识体系。所有内容均溯源至 asyncssh 源码（`asyncssh/` 包核心模块），遵循 [OKF v0.2 规范](/concepts/00-introduction.md)。

## 入门与基础（concepts/）

* [asyncssh 简介](concepts/00-introduction.md) — 异步 SSH2 协议库的设计哲学、异步模型、安装方法、与 paramiko 对比。
* [5分钟快速上手](concepts/01-getting-started.md) — 从安装到第一个异步连接、执行命令、传输文件。

## 核心概念（concepts/）

* [异步连接详解](concepts/02-async-connection.md) — connect() 函数参数、SSHClientConnection、认证方式、主机密钥验证、跳板机。
* [通道与流](concepts/03-channels.md) — SSHChannel 通道抽象、会话/direct-tcpip 通道、PTY 伪终端、窗口调整。
* [流与进程](concepts/04-streams-processes.md) — SSHReader/SSHWriter、create_process、SSHCompletedProcess、IO 重定向。
* [认证体系](concepts/05-authentication.md) — 密码/公钥/键盘交互/GSSAPI/hostbased 认证、SSHClient 回调。
* [密钥与证书](concepts/06-keys-certificates.md) — generate_private_key、SSHKey 读取/导出、SSHCertificate、SSH Agent、FIDO2。

## 高级主题（concepts/）

* [SFTP 文件传输](concepts/07-sftp.md) — SFTPClient、get/put/mget/mput、stat/listdir/chmod/chown、SFTPClientFile、VFS。
* [SCP 文件复制](concepts/08-scp.md) — scp() 协程、本地/远程/第三方复制、进度回调。
* [端口转发](concepts/09-port-forwarding.md) — forward_local_port/forward_remote_port、SOCKS、UNIX socket、TUN/TAP。
* [服务端开发](concepts/10-server.md) — SSHServer 回调、create_server、自定义认证、SFTPServer VFS。
* [高级模式](concepts/11-advanced-patterns.md) — 并发连接、加密算法配置、后量子密钥交换、调试日志、异常处理。

## 实战示例（examples/）

* [异步执行命令](examples/async-command.md) — conn.run()/create_process() 执行命令、交互式进程、超时与错误处理。
* [多主机并行连接](examples/parallel-connections.md) — asyncio.gather 并行、信号量限流、批量运维检查。
* [SFTP 文件传输](examples/sftp-transfer.md) — 上传下载、进度回调、目录操作、并行传输。
* [端口转发隧道](examples/port-forward-tunnel.md) — 本地/远程转发、SOCKS 代理、数据库隧道。

## 信源登记簿（references/）

* [asyncssh 源码信源登记](references/asyncssh-source.md) — asyncssh v2.24.0 源码路径、版本、核心模块清单与公开 API 导出。

## 信任与生命周期说明

* **status 判定依据**：全部 17 个内容文档（12 个概念 + 4 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 asyncssh 源码（`external/libs/asyncssh/asyncssh/` 目录）的逐模块阅读与事实提取（180 条源码事实），经 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-06-30`。asyncssh 迭代活跃，后量子密码、SFTP v6、FIDO2 等特性仍在演进；该日期作为保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-23）；`verified.at` 记录 V 阶段 Grep 验证事件（2026-08-23），两者分离、可追溯。

本知识包共收录 17 个内容文档（12 个概念 + 4 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。
