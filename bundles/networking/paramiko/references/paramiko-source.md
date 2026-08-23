---
type: Reference
title: paramiko 源码信源登记
description: paramiko v5.0.0 源码路径、版本信息、核心模块清单与公开 API
tags: [paramiko, source, reference, v5.0.0]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: paramiko-github
    resource: https://github.com/paramiko/paramiko
    title: paramiko GitHub 仓库
    author: human:bitprophet
  - id: paramiko-docs
    resource: https://docs.paramiko.org
    title: paramiko 官方文档
---

# paramiko 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | paramiko |
| 版本 | **5.0.0**（commit d60d5c17d78f） |
| 描述 | Pure Python SSH2 protocol library（纯 Python SSH2 协议库） |
| 作者 | Jeff Forcier (jeff@bitprophet.org) |
| 许可证 | GNU Lesser General Public License (LGPL) |
| Python 要求 | ≥ 3.7（依赖 cryptography、bcrypt、pynacl） |
| 官方文档 | <https://docs.paramiko.org> |
| 源码仓库 | <https://github.com/paramiko/paramiko> |

## 源码位置

paramiko 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/paramiko/paramiko/
```

该目录通过 git submodule 引入，本地不做修改。

## CLI 入口点

paramiko 本身不定义命令行入口。它是一个纯库，通过 Python API 调用。`__init__.py` 通过 `importlib.metadata.version("paramiko")` 获取版本号。

## 核心模块清单

| 模块 | 说明 |
|------|------|
| `__init__.py` | 包入口，导出所有公开 API：Transport、SSHClient、Channel、SFTPClient、PKey 及子类、HostKeys、Agent、ProxyCommand、异常类、认证策略类、常量等；定义 `key_classes = [RSAKey, Ed25519Key, ECDSAKey]` |
| `client.py` | 高层 SSH 客户端：`SSHClient` 封装连接/认证/通道/SFTP 全流程；`MissingHostKeyPolicy` 及 `AutoAddPolicy`/`RejectPolicy`/`WarningPolicy` 三种主机密钥策略 |
| `transport.py` | 核心协议实现（最大文件，3100+ 行）：`Transport` 继承 threading.Thread，管理密钥交换、加密协商、认证、通道多路复用；`SecurityOptions` 算法配置；`ServiceRequestingTransport` v3.2 新增；`ChannelMap` 通道映射 |
| `channel.py` | SSH 通道抽象：`Channel` 模拟 socket 接口（recv/send/settimeout/setblocking），支持 PTY、shell、exec、subsystem、X11/agent 转发；`ChannelFile`/`ChannelStderrFile`/`ChannelStdinFile` 文件对象 |
| `auth_handler.py` | 内部认证状态机：`AuthHandler` 管理 none/password/publickey/keyboard-interactive 认证流程 |
| `auth_strategy.py` | 新版可插拔认证框架：`AuthStrategy` 基类、`AuthSource` 及子类（`NoneAuth`/`Password`/`PrivateKey`/`InMemoryPrivateKey`/`OnDiskPrivateKey`）、`AuthResult`、`AuthFailure` |
| `pkey.py` | 公钥基类：`PKey` 定义密钥加载/签名/验签/序列化接口；`PublicBlob` 公钥 blob；`UnknownKeyType` 异常；支持 PEM 和 OpenSSH 两种私钥格式 |
| `rsakey.py` | RSA 密钥：`RSAKey`，name="ssh-rsa"，HASHES 映射 rsa-sha2-256/512 |
| `ed25519key.py` | Ed25519 密钥：`Ed25519Key`，name="ssh-ed25519"，基于 pynacl，仅支持 OpenSSH 格式 |
| `ecdsakey.py` | ECDSA 密钥：`ECDSAKey`，`_ECDSACurve`/`_ECDSACurveSet` 管理 nistp256/384/521 曲线 |
| `sftp_client.py` | SFTP 客户端：`SFTPClient` 提供文件/目录操作（listdir/stat/chmod/chown/put/get 等）；`SFTP` 别名 |
| `sftp_server.py` | SFTP 服务端：`SFTPServer` 继承 BaseSFTP 和 SubsystemHandler |
| `sftp_si.py` | SFTP 服务端接口：`SFTPServerInterface` 定义回调方法 |
| `sftp_file.py` | SFTP 文件对象：`SFTPFile` 继承 BufferedFile，支持 prefetch 预取和 pipeline 流水线 |
| `sftp_attr.py` | SFTP 文件属性：`SFTPAttributes` 镜像 os.stat 字段 |
| `sftp_handle.py` | SFTP 文件句柄：`SFTPHandle` 服务端文件句柄抽象 |
| `sftp.py` | SFTP 协议常量：CMD_INIT/CMD_OPEN/CMD_READ 等命令码，SFTP_OK/SFTP_EOF 等状态码，BaseSFTP 基类 |
| `server.py` | SSH 服务端接口：`ServerInterface` 定义通道/认证/转发回调；`SubsystemHandler` 子系统处理器线程；`InteractiveQuery` 交互式认证查询 |
| `hostkeys.py` | 主机密钥管理：`HostKeys` 继承 MutableMapping，解析/写入 OpenSSH known_hosts 格式；`HostKeyEntry`；支持 hashed hostname |
| `agent.py` | SSH Agent 客户端：`Agent`/`AgentKey`/`AgentSSH`；agent 转发代理类（`AgentLocalProxy`/`AgentRemoteProxy`/`AgentClientProxy`/`AgentServerProxy`/`AgentRequestHandler`） |
| `proxy.py` | 代理命令：`ProxyCommand` 通过 subprocess 包装 ProxyCommand，实现 socket-like 接口 |
| `common.py` | 通用常量：SSH 消息 ID（MSG_DISCONNECT 等）、认证返回码、通道打开结果码、窗口/包大小常量、日志级别别名、io_sleep |
| `message.py` | SSH 消息：`Message` 类封装二进制读写（get_int/add_string 等） |
| `packet.py` | 数据包处理：`Packetizer` 加密/解密/组包；`NeedRekeyException` |
| `buffered_pipe.py` | 缓冲管道：`BufferedPipe` 线程安全字节缓冲；`PipeTimeout` |
| `file.py` | 文件缓冲基类：`BufferedFile` 实现 Python 文件接口（read/write/seek/close），子类覆盖 _read/_write |
| `config.py` | SSH config 解析：`SSHConfig`/`SSHConfigDict`，解析 OpenSSH ssh_config 格式；`SSH_PORT=22` |
| `compress.py` | 压缩：`ZlibCompressor`/`ZlibDecompressor` |
| `ssh_exception.py` | 异常体系：`SSHException` 基类及 15+ 子类 |
| `util.py` | 工具函数：`ClosingContextManager`、b()/u() 转换、`constant_time_bytes_eq`、`get_logger`、`clamp_value`、`load_host_keys`、`format_binary` 等 |
| `kex_curve25519.py` | 密钥交换：`KexCurve25519`（curve25519-sha256） |
| `kex_ecdh_nist.py` | 密钥交换：`KexNistp256`/`KexNistp384`/`KexNistp521`（ECDH NIST 曲线） |
| `kex_gex.py` | 密钥交换：`KexGexSHA256`（DH GEX） |
| `kex_group14.py` | 密钥交换：`KexGroup14SHA256`（DH group14） |
| `kex_group16.py` | 密钥交换：`KexGroup16SHA512`（DH group16） |
| `ber.py` | BER 编码工具 |
| `primes.py` | DH 素数包：`ModulusPack` |
| `pipe.py` | Windows 管道支持 |
| `win_openssh.py` | Windows OpenSSH agent 支持 |
| `win_pageant.py` | Windows Pageant 支持 |
| `_winapi.py` | Windows API 封装 |

## 公开 API 导出

`paramiko/__init__.py` 通过显式导入导出以下核心符号：

- **核心类**：`Transport`、`SSHClient`、`Channel`、`SFTPClient`、`SFTPServer`、`ServerInterface`
- **传输类**：`SecurityOptions`、`ServiceRequestingTransport`
- **通道文件类**：`ChannelFile`、`ChannelStderrFile`、`ChannelStdinFile`
- **认证策略**：`AuthStrategy`、`AuthSource`、`AuthResult`、`AuthFailure`、`SourceResult`、`NoneAuth`、`Password`、`PrivateKey`、`InMemoryPrivateKey`、`OnDiskPrivateKey`
- **认证处理器**：`AuthHandler`
- **密钥类**：`PKey`、`RSAKey`、`Ed25519Key`、`ECDSAKey`、`PublicBlob`、`UnknownKeyType`
- **主机密钥**：`HostKeys`
- **主机密钥策略**：`MissingHostKeyPolicy`、`AutoAddPolicy`、`RejectPolicy`、`WarningPolicy`
- **SFTP 类**：`SFTP`、`SFTPAttributes`、`SFTPHandle`、`SFTPServerInterface`、`SFTPFile`、`SFTPError`、`BaseSFTP`
- **Agent**：`Agent`、`AgentKey`
- **代理**：`ProxyCommand`
- **配置**：`SSHConfig`、`SSHConfigDict`
- **协议工具**：`Message`、`Packetizer`、`BufferedFile`
- **服务端**：`SubsystemHandler`、`InteractiveQuery`
- **异常类**：`SSHException`、`AuthenticationException`、`BadAuthenticationType`、`BadHostKeyException`、`ChannelException`、`ConfigParseError`、`CouldNotCanonicalize`、`IncompatiblePeer`、`MessageOrderError`、`PasswordRequiredException`、`ProxyCommandFailure`
- **常量**：`AUTH_SUCCESSFUL`、`AUTH_PARTIALLY_SUCCESSFUL`、`AUTH_FAILED`、`OPEN_SUCCEEDED`、`OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED`、`OPEN_FAILED_CONNECT_FAILED`、`OPEN_FAILED_UNKNOWN_CHANNEL_TYPE`、`OPEN_FAILED_RESOURCE_SHORTAGE`、`SFTP_OK`、`SFTP_EOF`、`SFTP_NO_SUCH_FILE`、`SFTP_PERMISSION_DENIED`、`SFTP_FAILURE`、`SFTP_BAD_MESSAGE`、`SFTP_NO_CONNECTION`、`SFTP_CONNECTION_LOST`、`SFTP_OP_UNSUPPORTED`、`io_sleep`

[^paramiko-github]: paramiko 源码仓库：<https://github.com/paramiko/paramiko>
[^paramiko-docs]: paramiko 官方文档：<https://docs.paramiko.org>
