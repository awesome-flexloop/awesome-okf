---
okf_version: "0.2"
---

# paramiko 知识库

本知识包是纯 Python SSH2 协议库 [paramiko](https://www.paramiko.org/)（v5.0.0）的系统化中文教程，基于源码深度阅读生成，覆盖从快速上手到服务端开发的完整知识体系。所有内容均溯源至 paramiko 源码（`paramiko/` 包核心模块），遵循 [OKF v0.2 规范](/concepts/00-introduction.md)。

## 入门与基础（concepts/）

* [paramiko 简介](concepts/00-introduction.md) — 纯 Python SSH2 协议库的设计哲学、安装方法、与其他 SSH 库的对比。
* [5分钟快速上手](concepts/01-getting-started.md) — 从安装到第一个 SSH 连接、执行命令、传输文件的快速入门。

## 核心概念（concepts/）

* [SSHClient 详解](concepts/02-ssh-client.md) — 高层接口：connect、exec_command、invoke_shell、open_sftp、主机密钥策略。
* [Transport 底层传输](concepts/03-transport.md) — 核心协议引擎：密钥交换、加密协商、认证、通道管理、SecurityOptions。
* [Channel 通道](concepts/04-channel.md) — 多路复用通道：exec/shell/subsystem、PTY、recv/send、exit_status。
* [认证体系](concepts/05-authentication.md) — password/publickey/keyboard-interactive、AuthStrategy、Agent。
* [密钥与主机密钥](concepts/06-keys-and-hostkeys.md) — PKey/RSAKey/Ed25519Key/ECDSAKey、HostKeys、MissingHostKeyPolicy。

## 高级主题（concepts/）

* [SFTP 文件传输](concepts/07-sftp.md) — SFTPClient：put/get/file/stat/listdir/posix_rename/chmod/chown、SFTPFile。
* [端口转发](concepts/08-port-forwarding.md) — 本地/远程/SOCKS 转发、direct-tcpip 通道、隧道。
* [服务端开发](concepts/09-server.md) — ServerInterface、SFTPServer、构建自定义 SSH 服务端。
* [高级模式](concepts/10-advanced-patterns.md) — ProxyCommand 跳板机、连接池、并发通道、日志调试、异常处理。

## 实战示例（examples/）

* [基础连接与命令执行](examples/basic-connection.md) — 从创建 SSHClient 到连接、执行命令、读取输出。
* [多种命令执行模式](examples/execute-commands.md) — exec_command、PTY/sudo、实时输出、环境变量、AuthStrategy。
* [SFTP 文件上传下载](examples/file-transfer.md) — put/get 传输、进度回调、递归目录、属性操作。
* [端口转发隧道](examples/port-forwarding.md) — 本地/远程转发、SOCKS5 代理、数据库隧道。
* [交互式 Shell](examples/interactive-shell.md) — invoke_shell 终端会话、实时收发、全屏程序。

## 信源登记簿（references/）

* [paramiko 源码信源登记](references/paramiko-source.md) — paramiko v5.0.0 源码路径、版本、核心模块清单与公开 API 导出。

## 信任与生命周期说明

* **status 判定依据**：全部 17 个内容文档（11 个概念 + 5 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 paramiko 源码（`external/libs/paramiko/paramiko/` 目录）的逐模块阅读与事实提取（123 条源码事实），经 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。paramiko 5.x API 相对稳定，核心类（SSHClient/Transport/Channel/SFTPClient/PKey）自 2.x 以来变化不大；该日期作为针对未来大版本升级的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-23）；`verified.at` 记录 V 阶段 Grep 验证事件（2026-08-23），两者分离、可追溯。

本知识包共收录 17 个内容文档（11 个概念 + 5 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
