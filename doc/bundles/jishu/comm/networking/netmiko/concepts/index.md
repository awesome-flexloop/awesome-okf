---
okf_version: "0.2"
---

# netmiko 概念文档索引

| 编号 | 文档 | 说明 |
|------|------|------|
| 00 | [netmiko 简介](00-introduction.md) | 多厂商网络设备 SSH 自动化库、设计哲学、CLI vs API |
| 01 | [5分钟快速上手](01-getting-started.md) | 安装、第一个连接、device_type 字典、核心参数 |
| 02 | [ConnectHandler 工厂](02-connect-handler.md) | 工厂函数、CLASS_MAPPER、ssh_dispatcher、redispatch |
| 03 | [BaseConnection 核心](03-base-connection.md) | 连接生命周期、session_preparation、终端设置 |
| 04 | [命令执行](04-command-execution.md) | send_command/send_command_timing/send_command_expect 对比 |
| 05 | [配置管理](05-config-mgmt.md) | send_config_set、enable/config 模式、save_config、commit |
| 06 | [驱动继承体系](06-driver-hierarchy.md) | BaseConnection→CiscoBaseConnection→厂商驱动、Mixin 设计 |
| 07 | [SSH 自动探测](07-ssh-autodetect.md) | SSHDetect、指纹库、三种探测方法 |
| 08 | [SCP 文件传输](08-file-transfer.md) | FileTransfer/SCPConn、file_transfer、MD5 校验 |
| 09 | [高级模式](09-advanced-patterns.md) | session_log、TextFSM、异常处理、并发连接 |

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-connect-handler
03-base-connection
04-command-execution
05-config-mgmt
06-driver-hierarchy
07-ssh-autodetect
08-file-transfer
09-advanced-patterns
```
