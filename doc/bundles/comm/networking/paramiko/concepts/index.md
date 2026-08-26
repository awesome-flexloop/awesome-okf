# paramiko 概念文档

## 入门

* [paramiko 简介](00-introduction.md) — 纯 Python SSH2 协议库的设计哲学、安装方法、与其他 SSH 库的对比。
* [5分钟快速上手](01-getting-started.md) — 从安装到第一个 SSH 连接、执行命令、传输文件的快速入门。

## 核心

* [SSHClient 详解](02-ssh-client.md) — 高层接口：connect、exec_command、invoke_shell、open_sftp、主机密钥策略。
* [Transport 底层传输](03-transport.md) — 核心协议引擎：密钥交换、加密协商、认证、通道管理、SecurityOptions。
* [Channel 通道](04-channel.md) — 多路复用通道：exec/shell/subsystem、PTY、recv/send、exit_status、X11/agent 转发。
* [认证体系](05-authentication.md) — password/publickey/keyboard-interactive、AuthStrategy 可插拔框架、Agent 集成。
* [密钥与主机密钥](06-keys-and-hostkeys.md) — PKey/RSAKey/Ed25519Key/ECDSAKey、HostKeys、MissingHostKeyPolicy 策略。

## 高级

* [SFTP 文件传输](07-sftp.md) — SFTPClient：put/get/file/stat/listdir/posix_rename/chmod/chown、SFTPFile、SFTPAttributes。
* [端口转发](08-port-forwarding.md) — 本地/远程/SOCKS 转发、direct-tcpip 通道、隧道实现。
* [服务端开发](09-server.md) — ServerInterface、SFTPServer、SFTPServerInterface、构建自定义 SSH 服务端。
* [高级模式](10-advanced-patterns.md) — ProxyCommand 跳板机、连接池、并发通道、日志调试、异常处理最佳实践。

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-ssh-client
03-transport
04-channel
05-authentication
06-keys-and-hostkeys
07-sftp
08-port-forwarding
09-server
10-advanced-patterns
```
