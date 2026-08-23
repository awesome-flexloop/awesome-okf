---
type: Reference
title: asyncssh 源码信源登记
description: asyncssh v2.24.0 源码路径、版本信息、核心模块清单与公开 API 导出
tags: [asyncssh, source, reference, v2.24.0]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: asyncssh-github
    resource: https://github.com/ronf/asyncssh
    title: asyncssh GitHub 仓库
    author: human:ronf
  - id: asyncssh-docs
    resource: https://asyncssh.readthedocs.io
    title: asyncssh 官方文档
---

# asyncssh 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | asyncssh |
| 版本 | **2.24.0**（commit 25370783e5c1） |
| 描述 | An asynchronous SSH2 library for Python（基于 asyncio 的异步 SSH2 客户端/服务端库） |
| 作者 | Ron Frederick (ronf@timeheart.net) |
| 许可证 | Eclipse Public License v2.0 (EPL-2.0) OR GPL-2.0-or-later |
| Python 要求 | ≥ 3.10（依赖 cryptography） |
| 官方文档 | <https://asyncssh.readthedocs.io> |
| 源码仓库 | <https://github.com/ronf/asyncssh> |

## 源码位置

asyncssh 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/asyncssh/asyncssh/
```

该目录通过 git submodule 引入，本地不做修改。

## 核心模块清单

| 模块 | 说明 |
|------|------|
| `__init__.py` | 包入口，导出约 170 个公开符号：connect/create_server/listen、SSHClientConnection/SSHServerConnection、SSHChannel/SSHClientChannel/SSHServerChannel、SSHReader/SSHWriter、SSHProcess/SSHClientProcess/SSHServerProcess/SSHCompletedProcess、SFTPClient/SFTPClientFile/SFTPServer、SSHKey/SSHCertificate、SSHAgentClient、SSHForwarder、SSHListener、SSHClient/SSHServer、异常类、常量等；通过导入 sk_eddsa/sk_ecdsa/eddsa/ecdsa/rsa/dsa/kex_dh/kex_rsa 触发算法注册 |
| `version.py` | 版本信息：`__version__ = '2.24.0'`，`__author__ = 'Ron Frederick'` |
| `connection.py` | 核心协议实现（最大文件，9800+ 行）：`SSHConnection` 继承 `asyncio.Protocol`，管理密钥交换、加密协商、认证、通道多路复用；`SSHClientConnection`（line 3415）提供 run/create_process/open_session/start_sftp_client/create_connection/create_server/forward_local_port/forward_remote_port 等客户端 API；`SSHServerConnection`（line 5828）服务端实现；`SSHAcceptor`（line 759）包装 asyncio.Server；`connect()`（line 9180）、`listen()`（line 9400）、`create_server()`（line 9691）、`create_connection()`（line 9665）等模块级协程 |
| `channel.py` | SSH 通道抽象：`SSHChannel`（line 86）泛型基类，提供 write/writelines/write_eof/close/abort/wait_closed/pause_reading/resume_reading/get_extra_info 等；`SSHClientChannel`（line 1119）增加 get_exit_status/get_returncode/change_terminal_size/send_break/send_signal/terminate/kill；`SSHServerChannel`（line 1497）增加 write_stderr/exit/exit_with_signal/get_terminal_type/get_terminal_size；`SSHTCPChannel`/`SSHUNIXChannel`/`SSHTunTapChannel` 通道变体；`SSHForwardChannel` 转发通道基类 |
| `stream.py` | 异步流抽象：`SSHReader`（line 72）提供 read/readline/readuntil/readexactly/at_eof；`SSHWriter`（line 257）提供 write/writelines/write_eof/drain/close/wait_closed/is_closing；`SSHStreamSession`（line 373）桥接通道与流，实现背压；`SSHClientStreamSession`（line 689）、`SSHServerStreamSession`（line 694）、`SSHSocketStreamSession`（line 806）会话变体 |
| `process.py` | 进程抽象：`SSHProcess`（line 819）继承 SSHStreamSession，管理 stdin/stdout/stderr 重定向；`SSHClientProcess`（line 1240）提供 stdin/stdout/stderr 属性、wait/communicate/redirect/collect_output/change_terminal_size/send_break/send_signal/terminate/kill；`SSHServerProcess`（line 1607）增加 term_type/term_size 属性；`SSHCompletedProcess`（line 774）Record 数据类，含 env/command/subsystem/exit_status/exit_signal/returncode/stdout/stderr 字段；`ProcessError`/`TimeoutError` 异常；`PIPE`/`DEVNULL`/`STDOUT` 常量 |
| `session.py` | 会话基类：`SSHSession`、`SSHClientSession`（line 223）、`SSHServerSession`、`SSHTCPSession`、`SSHUNIXSession`、`SSHTunTapSession`；`DataType` 枚举 |
| `auth.py` | 认证框架：`Auth`（line 75）基类、`ClientAuth`（line 116）/`ServerAuth`（line 528）双端对称；none/GSSAPI-KEX/GSSAPI-MIC/hostbased/publickey/keyboard-interactive/password 七种认证方法；`register_auth_method()`（line 948）注册机制；`get_supported_client_auth_methods()`/`get_supported_server_auth_methods()` 查询 |
| `public_key.py` | 公钥管理（3800+ 行）：`SSHKey`（line 247）基类，含 generate/export_private_key/export_public_key/write_private_key/write_public_key/append_private_key/append_public_key/convert_to_public/sign/verify/get_fingerprint/get_algorithm；`SSHCertificate`（line 1351）及 OpenSSH/X.509 证书子类；`generate_private_key()`（line 3065）、`import_private_key()`（line 3165）、`import_public_key()`（line 3204）、`read_private_key()`（line 3292）、`read_public_key()`（line 3325）、`load_keypairs()`（line 3442）、`load_resident_keys()`（line 3829）等模块函数；`KeyGenerationError`/`KeyImportError`/`KeyExportError` 异常 |
| `sftp.py` | SFTP 实现（8200+ 行）：`SFTPClient`（line 3829）提供 get/put/mget/mput/copy/mcopy/remote_copy/stat/lstat/setstat/chmod/chown/mkdir/rmdir/makedirs/rmtree/listdir/readdir/scandir/rename/posix_rename/remove/unlink/open/open56/truncate/utime/statvfs/exists/isdir/isfile/islink/getcwd/chdir/realpath/readlink/symlink/link/glob/exit/wait_closed；`SFTPClientFile`（line 3310）文件对象，支持 read/write/seek/tell/stat/chmod/chown/utime/truncate/fsync/lock/unlock/read_parallel；`SFTPServer`（line 6991）、`SFTPServerFS`（line 8153）VFS 抽象、`SFTPServerFile`（line 8099）；`SFTPAttrs`（line 1658）、`SFTPVFSAttrs`（line 2028）、`SFTPName`（line 2107）、`SFTPLimits`（line 2159）数据类；30+ SFTP 异常子类；SFTP 版本 3-6 |
| `scp.py` | SCP 协议：`scp()`（line 931）协程支持本地/远程/第三方复制，源/目标可为路径字符串或 `(conn, path)` 元组；`run_scp_server()`（line 1129）服务端处理器；默认块大小 256 KiB |
| `forward.py` | 端口转发：`SSHForwarder`（line 41）基类继承 asyncio.BaseProtocol；`SSHLocalForwarder`（line 192）、`SSHLocalPortForwarder`（line 229）、`SSHLocalPathForwarder`（line 245） |
| `listener.py` | 监听器：`SSHListener`（line 52）基类，支持异步上下文管理器；`SSHClientListener`（line 114）、`SSHTCPClientListener`（line 150）、`SSHUNIXClientListener`（line 199）、`SSHForwardListener`（line 234）；`create_tcp_local_listener()`/`create_tcp_forward_listener()`/`create_unix_forward_listener()`/`create_socks_listener()` 工厂函数 |
| `server.py` | SSH 服务端回调：`SSHServer`（line 66）定义 connection_made/connection_lost/begin_auth/auth_completed/validate_password/validate_public_key/kbdint_auth_supported/session_requested/connection_requested/server_requested 等回调 |
| `client.py` | SSH 客户端回调：`SSHClient`（line 35）定义 connection_made/connection_lost/password_auth_requested/public_key_auth_requested/kbdint_auth_requested/kbdint_challenge_received/auth_banner_received/auth_completed 等回调 |
| `agent.py` | SSH Agent 客户端：`SSHAgentClient`（line 183）、`SSHAgentKeyPair`（line 108）、`connect_agent()`（line 634）协程；`agent_unix.py`/`agent_win32.py` 平台实现 |
| `known_hosts.py` | 已知主机密钥：`SSHKnownHosts`（line 117）、`import_known_hosts()`（line 285）、`read_known_hosts()`（line 302）、`match_known_hosts()`（line 327） |
| `auth_keys.py` | authorized_keys 解析：`SSHAuthorizedKeys`、`import_authorized_keys()`、`read_authorized_keys()` |
| `config.py` | OpenSSH 配置解析：`ConfigParseError`；解析 ssh_config 格式 |
| `editor.py` | 行编辑器：`SSHLineEditorChannel` 提供终端行编辑功能 |
| `subprocess.py` | asyncio subprocess 桥接：`SSHSubprocessReadPipe`/`SSHSubprocessWritePipe`/`SSHSubprocessProtocol`/`SSHSubprocessTransport` |
| `logging.py` | 日志：`logger`、`set_log_level()`（line 177）、`set_sftp_log_level()`（line 196）、`set_debug_level()`（line 215） |
| `misc.py` | 工具函数与异常：`Error` 异常基类、`BytesOrStr` 类型别名、`MaybeAwait` 类型；`DisconnectError`/`ChannelOpenError`/`ConnectionLost`/`HostKeyNotVerifiable`/`KeyExchangeFailed`/`PermissionDenied`/`ProtocolError`/`BreakReceived`/`SignalReceived`/`TerminalSizeChanged` 等异常 |
| `constants.py` | 常量：`DEFAULT_PORT = 22`、`DEFAULT_LANG = 'en-US'` |
| `encryption.py` | 加密算法注册：`_enc_algs`/`_default_enc_algs` 列表、`register_cipher()` |
| `kex.py`/`kex_dh.py`/`kex_rsa.py` | 密钥交换算法实现 |
| `mac.py` | MAC 算法 |
| `compression.py` | 压缩算法 |
| `packet.py` | SSH 数据包处理 |
| `socks.py` | SOCKS 代理：`SSHSOCKSForwarder` |
| `tuntap.py` | TUN/TAP 设备支持 |
| `x11.py` | X11 转发 |
| `pkcs11.py` | PKCS#11 硬件安全模块：`load_pkcs11_keys()` |
| `sk.py`/`sk_ecdsa.py`/`sk_eddsa.py` | FIDO2 安全密钥支持 |
| `sshsig.py` | SSH 签名：`SSHAllowedSigners`、`create_sshsig()`、`validate_sshsig()` |
| `gss.py`/`gss_unix.py`/`gss_win32.py` | GSSAPI/Kerberos 认证 |
| `crypto/` | 加密原语封装子包：`cipher.py`（BasicCipher/GCMCipher/ChachaCipher）、`rsa.py`、`dsa.py`、`ec.py`、`ed.py`、`dh.py`、`kdf.py`（pbkdf2_hmac）、`pq.py`（MLKEM/SNTRUP 后量子 KEX）、`umac.py`（可选）、`x509.py`（可选）、`chacha.py`、`misc.py`（CryptoKey/PyCAKey） |

## 公开 API 导出分类

### 连接与服务器

`connect`、`create_connection`、`create_server`、`listen`、`connect_reverse`、`listen_reverse`、`run_client`、`run_server`、`get_server_host_key`、`get_server_auth_methods`、`SSHAcceptor`、`SSHClientConnection`、`SSHServerConnection`、`SSHClientConnectionOptions`、`SSHServerConnectionOptions`、`SSHAcceptHandler`

### 通道与流

`SSHClientChannel`、`SSHServerChannel`、`SSHTCPChannel`、`SSHUNIXChannel`、`SSHTunTapChannel`、`SSHReader`、`SSHWriter`、`SSHSocketSessionFactory`、`SSHServerSessionFactory`

### 进程

`SSHClientProcess`、`SSHServerProcess`、`SSHServerProcessFactory`、`SSHCompletedProcess`、`ProcessError`、`TimeoutError`、`DEVNULL`、`PIPE`、`STDOUT`

### SFTP

`SFTPClient`、`SFTPClientFile`、`SFTPServer`、`SFTPServerFactory`、`SFTPError` 及 30+ 异常子类、`SFTPAttrs`、`SFTPVFSAttrs`、`SFTPName`、`SFTPLimits`、`SEEK_SET`/`SEEK_CUR`/`SEEK_END`

### SCP

`scp`

### 密钥与证书

`SSHKey`、`SSHKeyPair`、`SSHCertificate`、`generate_private_key`、`import_private_key`、`import_public_key`、`import_certificate`、`read_private_key`、`read_public_key`、`read_certificate`、`read_private_key_list`、`read_public_key_list`、`read_certificate_list`、`load_keypairs`、`load_public_keys`、`load_certificates`、`load_resident_keys`、`load_pkcs11_keys`、`KeyGenerationError`、`KeyImportError`、`KeyExportError`、`set_default_skip_rsa_key_validation`

### 认证与主机密钥

`SSHClient`、`SSHServer`、`SSHAuthorizedKeys`、`import_authorized_keys`、`read_authorized_keys`、`SSHKnownHosts`、`import_known_hosts`、`read_known_hosts`、`match_known_hosts`、`SSHAllowedSigners`、`import_allowed_signers`、`read_allowed_signers`、`create_sshsig`、`validate_sshsig`

### Agent

`SSHAgentClient`、`SSHAgentKeyPair`、`connect_agent`

### 转发与监听

`SSHForwarder`、`SSHListener`

### 会话

`DataType`、`SSHClientSession`、`SSHServerSession`、`SSHTCPSession`、`SSHUNIXSession`、`SSHTunTapSession`

### 编辑器与子进程

`SSHLineEditorChannel`、`SSHSubprocessReadPipe`、`SSHSubprocessWritePipe`、`SSHSubprocessProtocol`、`SSHSubprocessTransport`

### 日志

`logger`、`set_log_level`、`set_sftp_log_level`、`set_debug_level`

### 异常

`Error`、`DisconnectError`、`ChannelOpenError`、`ChannelListenError`、`ConnectionLost`、`CompressionError`、`HostKeyNotVerifiable`、`KeyExchangeFailed`、`IllegalUserName`、`MACError`、`PermissionDenied`、`ProtocolError`、`ProtocolNotSupported`、`ServiceNotAvailable`、`PasswordChangeRequired`、`BreakReceived`、`SignalReceived`、`TerminalSizeChanged`、`KeyEncryptionError`、`ConfigParseError`

### 类型

`BytesOrStr`

## 关键常量

| 常量 | 值 | 位置 |
|------|-----|------|
| `DEFAULT_PORT` | 22 | constants.py:27 |
| `DEFAULT_LANG` | `'en-US'` | constants.py:24 |
| `_DEFAULT_WINDOW` | 2 MiB（2097152） | connection.py:277 |
| `_DEFAULT_MAX_PKTSIZE` | 32 KiB（32768） | connection.py:278 |
| `MIN_SFTP_VERSION` | 3 | sftp.py:172 |
| `MAX_SFTP_VERSION` | 6 | sftp.py:173 |

## 依赖

- **cryptography**：核心加密原语（AES、RSA、ECDSA、Ed25519、X25519 等）
- **typing_extensions**：类型扩展（Self 等）
- 可选依赖：`python-gssapi`（GSSAPI/Kerberos）、`pkcs11`（PKCS#11）、`libnacl`（额外加密）、`bcrypt`（某些密钥加密）
