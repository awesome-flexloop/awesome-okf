# paramiko 实战示例

* [基础连接与命令执行](basic-connection.md) — 从创建 SSHClient 到连接、执行命令、读取输出、关闭连接。
* [多种命令执行模式](execute-commands.md) — exec_command、PTY/sudo、长时间命令实时输出、环境变量、AuthStrategy。
* [SFTP 文件上传下载](file-transfer.md) — put/get 传输、进度回调、目录递归上传下载、文件属性操作。
* [端口转发隧道](port-forwarding.md) — 本地转发、远程转发、SOCKS5 代理、数据库隧道。
* [交互式 Shell](interactive-shell.md) — invoke_shell 终端会话、实时收发、全屏程序、终端大小调整。

```{toctree}
:maxdepth: 7

basic-connection
execute-commands
file-transfer
interactive-shell
port-forwarding
```
