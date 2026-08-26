# 概念文档索引

- [asyncssh 简介](00-introduction.md) — 基于 asyncio 的异步 SSH2 协议库的设计哲学、安装方法、与 paramiko 对比。
- [5分钟快速上手](01-getting-started.md) — 从安装到第一个异步 SSH 连接、执行命令、传输文件。
- [异步连接详解](02-async-connection.md) — connect() 参数全解析、认证方式、主机密钥验证、跳板机隧道。
- [通道与流](03-channels.md) — SSHChannel、会话/direct-tcpip 通道、PTY、窗口调整。
- [流与进程](04-streams-processes.md) — SSHReader/SSHWriter、create_process、SSHCompletedProcess、stdin/stdout/stderr。
- [认证体系](05-authentication.md) — 密码/公钥/键盘交互/GSSAPI/hostbased、SSHClient 回调、authorized_keys。
- [密钥与证书](06-keys-certificates.md) — generate_private_key、SSHKey 读取/导出、SSHCertificate、SSH Agent、FIDO2。
- [SFTP 文件传输](07-sftp.md) — SFTPClient、get/put/mget/mput、stat/listdir/chmod/chown、SFTPClientFile、VFS。
- [SCP 文件复制](08-scp.md) — scp() 协程、本地/远程/第三方复制、进度回调、与 SFTP 对比。
- [端口转发](09-port-forwarding.md) — forward_local_port/forward_remote_port、SOCKS、UNIX socket、TUN/TAP。
- [服务端开发](10-server.md) — SSHServer 回调、create_server、自定义认证、SFTPServer VFS、进程工厂。
- [高级模式](11-advanced-patterns.md) — 并发连接、加密算法配置、后量子密钥交换、调试日志、异常处理。

```{toctree}
:maxdepth: 7

00-introduction
01-getting-started
02-async-connection
03-channels
04-streams-processes
05-authentication
06-keys-certificates
07-sftp
08-scp
09-port-forwarding
10-server
11-advanced-patterns
```
