# asyncssh 知识束生成日志

## R 阶段（事实采集）

- 读取任务简报：`.trae/specs/ssh-python-okf-wiki/asyncssh-task-brief.md`
- 参考格式范例：`bundles/networking/paramiko/`（index.md、concepts/、examples/、references/）
- 逐模块阅读 asyncssh v2.24.0 源码（`external/libs/asyncssh/asyncssh/`）：
  - `__init__.py`（约 170 个公开导出符号）
  - `version.py`（版本 2.24.0）
  - `connection.py`（9800+ 行，SSHConnection/SSHClientConnection/SSHServerConnection/connect/listen/create_server）
  - `channel.py`（SSHChannel/SSHClientChannel/SSHServerChannel/SSHTCPChannel/SSHUNIXChannel）
  - `stream.py`（SSHReader/SSHWriter/SSHStreamSession/SSHClientStreamSession/SSHServerStreamSession）
  - `process.py`（SSHProcess/SSHClientProcess/SSHServerProcess/SSHCompletedProcess/PIPE/DEVNULL/STDOUT）
  - `sftp.py`（8200+ 行，SFTPClient/SFTPClientFile/SFTPServer/SFTPServerFS/SFTPAttrs/SFTPName）
  - `public_key.py`（3800+ 行，SSHKey/SSHCertificate/generate_private_key/read_private_key/export_private_key）
  - `auth.py`（Auth/ClientAuth/ServerAuth/7 种认证方法/register_auth_method）
  - `scp.py`（scp/run_scp_server）
  - `forward.py`（SSHForwarder/SSHLocalForwarder/SSHLocalPortForwarder）
  - `listener.py`（SSHListener/SSHClientListener/SSHForwardListener）
  - `server.py`（SSHServer 回调基类）
  - `client.py`（SSHClient 回调基类）
  - `agent.py`（SSHAgentClient/connect_agent）
  - `known_hosts.py`（SSHKnownHosts/read_known_hosts/match_known_hosts）
  - `auth_keys.py`（SSHAuthorizedKeys）
  - `session.py`（SSHServerSession/SSHClientSession/DataType）
  - `constants.py`（DEFAULT_PORT=22）
  - `encryption.py`（算法注册模式）
  - `crypto/` 子包（cipher/rsa/dsa/ec/ed/dh/kdf/pq/chacha/umac/x509）
  - `logging.py`（set_log_level/set_sftp_log_level/set_debug_level）
  - `subprocess.py`（SSHSubprocessProtocol/Transport）
  - `editor.py`（SSHLineEditorChannel）
  - `socks.py`（SSHSOCKSForwarder）
- 提取 **180 条**编号事实（F-001~F-180），输出至 `.trae/specs/ssh-python-okf-wiki/asyncssh-facts.md`

## I 阶段（架构洞察）

- 提炼 **5 个核心架构洞察**，输出至 `.trae/specs/ssh-python-okf-wiki/asyncssh-insights.md`：
  1. 全异步协程协议栈——asyncio.Protocol 状态机设计（对比 paramiko 线程模型）
  2. Channel→Stream→Process 三层 IO 抽象递进
  3. SFTP v3-v6 多版本协议实现与 OpenSSH 扩展
  4. 模块化加密插件体系（crypto/ 子包注册模式 + 后量子 KEX）
  5. 双端对称设计——客户端和服务端共享基类与回调协议
- 设计知识地图：入门(2篇) → 核心(5篇) → 高级(5篇)，共 12 篇概念文档

## E 阶段（批量生成）

### Step 1: 创建目录结构
- `bundles/networking/asyncssh/concepts/`
- `bundles/networking/asyncssh/examples/`
- `bundles/networking/asyncssh/references/`

### Step 2: 信源先行
- `references/asyncssh-source.md`

### Step 3: concepts/ 批次1（入门+核心，6篇）
1. `concepts/00-introduction.md`
2. `concepts/01-getting-started.md`
3. `concepts/02-async-connection.md`
4. `concepts/03-channels.md`
5. `concepts/04-streams-processes.md`
6. `concepts/05-authentication.md`

### Step 3: concepts/ 批次2（高级，6篇）
7. `concepts/06-keys-certificates.md`
8. `concepts/07-sftp.md`
9. `concepts/08-scp.md`
10. `concepts/09-port-forwarding.md`
11. `concepts/10-server.md`
12. `concepts/11-advanced-patterns.md`

### Step 4: examples/（4篇）
1. `examples/async-command.md`
2. `examples/parallel-connections.md`
3. `examples/sftp-transfer.md`
4. `examples/port-forward-tunnel.md`

### Step 5: index 与日志
- `concepts/index.md`
- `examples/index.md`
- `references/index.md`
- `index.md`（根，带 okf_version frontmatter）
- `log.md`（本文件）

## V 阶段（独立验证）

### Grep API 验证结果

**类名验证（全部通过）**：

| 类名 | 源码位置 | 状态 |
|------|---------|------|
| `SSHClientConnection` | connection.py:3415 | ✅ |
| `SSHServerConnection` | connection.py:5828 | ✅ |
| `SSHConnection` | connection.py:867 | ✅ |
| `SSHChannel` | channel.py:86 | ✅ |
| `SSHClientChannel` | channel.py:1119 | ✅ |
| `SSHServerChannel` | channel.py:1497 | ✅ |
| `SSHReader` | stream.py:72 | ✅ |
| `SSHWriter` | stream.py:257 | ✅ |
| `SSHProcess` | process.py:819 | ✅ |
| `SSHClientProcess` | process.py:1240 | ✅ |
| `SSHServerProcess` | process.py:1607 | ✅ |
| `SSHCompletedProcess` | process.py:774 | ✅ |
| `SFTPClient` | sftp.py:3829 | ✅ |
| `SFTPClientFile` | sftp.py:3310 | ✅ |
| `SFTPServer` | sftp.py:6991 | ✅ |
| `SFTPAttrs` | sftp.py:1658 | ✅ |
| `SFTPName` | sftp.py:2107 | ✅ |
| `SFTPLimits` | sftp.py:2159 | ✅ |
| `SFTPVFSAttrs` | sftp.py:2028 | ✅ |
| `SSHKey` | public_key.py:247 | ✅ |
| `SSHCertificate` | public_key.py:1351 | ✅ |
| `SSHAgentClient` | agent.py:183 | ✅ |
| `SSHForwarder` | forward.py:41 | ✅ |
| `SSHListener` | listener.py:52 | ✅ |
| `SSHServer` | server.py:66 | ✅ |
| `SSHClient` | client.py:35 | ✅ |
| `SSHServerSession` | session.py:223 | ✅ |
| `SSHAcceptor` | connection.py:759 | ✅ |
| `SSHLineEditorChannel` | editor.py | ✅ |

**模块级函数验证（全部通过）**：

| 函数 | 源码位置 | 状态 |
|------|---------|------|
| `connect()` | connection.py:9180 | ✅ |
| `listen()` | connection.py:9400 | ✅ |
| `create_server()` | connection.py:9691 | ✅ |
| `create_connection()` | connection.py:9665 | ✅ |
| `connect_reverse()` | connection.py:9299 | ✅ |
| `listen_reverse()` | connection.py:9525 | ✅ |
| `get_server_host_key()` | connection.py:9709 | ✅ |
| `get_server_auth_methods()` | connection.py:9853 | ✅ |
| `run_client()` | connection.py:9077 | ✅ |
| `run_server()` | connection.py:9131 | ✅ |
| `scp()` | scp.py:931 | ✅ |
| `connect_agent()` | agent.py:634 | ✅ |
| `generate_private_key()` | public_key.py:3065 | ✅ |
| `import_private_key()` | public_key.py:3165 | ✅ |
| `import_public_key()` | public_key.py:3204 | ✅ |
| `read_private_key()` | public_key.py:3292 | ✅ |
| `read_public_key()` | public_key.py:3325 | ✅ |
| `load_keypairs()` | public_key.py:3442 | ✅ |
| `set_log_level()` | logging.py:177 | ✅ |
| `set_sftp_log_level()` | logging.py:196 | ✅ |
| `set_debug_level()` | logging.py:215 | ✅ |

**SSHClientConnection 方法验证（全部通过）**：

| 方法 | 源码位置 | 状态 |
|------|---------|------|
| `run()` | connection.py:4641 | ✅ |
| `create_process()` | connection.py:4489 | ✅ |
| `create_session()` | connection.py:4241 | ✅ |
| `open_session()` | connection.py:4463 | ✅ |
| `create_connection()` | connection.py:4687 | ✅ |
| `open_connection()` | connection.py:4761 | ✅ |
| `create_server()` | connection.py:4791 | ✅ |
| `start_server()` | connection.py:4881 | ✅ |
| `start_sftp_client()` | connection.py:5764 | ✅ |
| `forward_local_port()` | connection.py:3252 | ✅ |
| `forward_remote_port()` | connection.py:5476 | ✅ |
| `forward_local_path()` | connection.py:3342 | ✅ |
| `forward_remote_path()` | connection.py:5521 | ✅ |
| `forward_socks()` | connection.py:5639 | ✅ |
| `forward_tun()` | connection.py:5695 | ✅ |
| `forward_tap()` | connection.py:5730 | ✅ |
| `get_server_host_key()` | connection.py:3659 | ✅ |
| `get_server_auth_methods()` | connection.py:3673 | ✅ |
| `validate_server_host_key()` | connection.py:3641 | ✅ |

**SSHChannel 方法验证（全部通过）**：

| 方法 | 源码位置 | 状态 |
|------|---------|------|
| `write()` | channel.py:896 | ✅ |
| `writelines()` | channel.py:952 | ✅ |
| `write_eof()` | channel.py:981 | ✅ |
| `close()` | channel.py:768 | ✅ |
| `abort()` | channel.py:749 | ✅ |
| `wait_closed()` | channel.py:794 | ✅ |
| `is_closing()` | channel.py:789 | ✅ |
| `pause_reading()` | channel.py:999 | ✅ |
| `resume_reading()` | channel.py:1020 | ✅ |
| `get_extra_info()` | channel.py:804 | ✅ |
| `set_extra_info()` | channel.py:833 | ✅ |
| `get_exit_status()` | channel.py:1323 | ✅ |
| `get_returncode()` | channel.py:1354 | ✅ |
| `change_terminal_size()` | channel.py:1374 | ✅ |
| `send_break()` | channel.py:1405 | ✅ |
| `send_signal()` | channel.py:1424 | ✅ |
| `terminate()` | channel.py:1462 | ✅ |
| `kill()` | channel.py:1479 | ✅ |

**SSHReader/SSHWriter 方法验证（全部通过）**：

`SSHReader.read()` (stream.py:137)、`readline()` (159)、`readuntil()` (180)、`readexactly()` (223)、`at_eof()` (241)
`SSHWriter.write()` (333)、`writelines()` (347)、`write_eof()` (352)、`drain()` (320)、`close()` (295)、`wait_closed()` (310)、`is_closing()` (305)

**SSHProcess 方法验证（全部通过）**：

`wait()` (process.py:1551)、`communicate()` (1451)、`redirect()` (1323)、`collect_output()` (1435)、`change_terminal_size()` (1480)、`send_break()` (1506)、`send_signal()` (1520)、`terminate()` (1533)、`kill()` (1542)、`close()` (1216)、`wait_closed()` (1228)

**SFTPClient 方法验证（全部通过）**：

`get()` (sftp.py:4118)、`put()` (4229)、`mget()` (4455)、`mput()` (4478)、`copy()` (4340)、`stat()` (5033)、`lstat()` (5062)、`setstat()` (5088)、`chmod()` (5211)、`chown()` (5165)、`mkdir()` (5639)、`rmdir()` (5660)、`makedirs()` (4639)、`rmtree()` (4701)、`listdir()` (5618)、`readdir()` (5589)、`scandir()` (5544)、`rename()` (5474)、`posix_rename()` (5513)、`remove()` (5453)、`unlink()` (5469)、`open()` (4806)、`truncate()` (5135)、`utime()` (5236)、`statvfs()` (5114)、`exists()` (5271)、`isdir()` (5413)、`isfile()` (5426)、`islink()` (5439)、`getcwd()` (5769)、`chdir()` (5784)、`realpath()` (5693)、`readlink()` (5803)、`symlink()` (5827)、`link()` (5854)、`glob()` (4564)、`exit()` (5880)、`wait_closed()` (5890)

**SSHKey 方法验证（全部通过）**：

`generate()` (public_key.py:268, classmethod)、`export_private_key()` (1042)、`export_public_key()` (1223)、`write_private_key()` (1282)、`write_public_key()` (1299)、`append_private_key()` (1316)、`append_public_key()` (1333)、`convert_to_public()` (634)、`get_algorithm()` (415)、`get_fingerprint()` (512)、`sign()` (567)、`verify()` (579)

### 关键常量验证

| 常量 | 值 | 位置 |
|------|-----|------|
| DEFAULT_PORT | 22 | constants.py:27 |
| _DEFAULT_WINDOW | 2 MiB | connection.py:277 |
| _DEFAULT_MAX_PKTSIZE | 32 KiB | connection.py:278 |
| MIN_SFTP_VERSION | 3 | sftp.py:172 |
| MAX_SFTP_VERSION | 6 | sftp.py:173 |

### Frontmatter 检查

17 个内容文件（12 概念 + 4 示例 + 1 信源）全部包含 type/title/description/tags/generated/verified/status/stale_after/sources 九个字段。tags 包含 asyncssh，stale_after 统一为 2027-06-30。

### 链接检查

所有 `/concepts/`、`/examples/`、`/references/` 开头的交叉链接目标文件均存在。跨束引用 `../../paramiko/concepts/` 路径格式正确。

### 虚构 API 修复记录

1. **`asyncssh.sp()` 拼写错误**：`concepts/08-scp.md` 第 93 行误写为 `asyncssh.sp('local.txt', ...)`，实际函数名为 `asyncssh.scp()`（scp.py:931），已修正。
2. **`asyncssh.run_scp_server()` 未导出**：`concepts/08-scp.md` 和 `concepts/10-server.md` 中误用 `asyncssh.run_scp_server()`，该函数存在于 scp.py:1129 但未在 `__init__.py` 中导出（`__all__` 仅包含 `'scp'`）。已修正为 `from asyncssh.scp import run_scp_server` 导入形式，并补充说明该函数由 `SSHServerStreamSession` 内部自动调用（stream.py:766）。
3. **`process.create_sftp_server()` 方法不存在**：SCP 服务端示例中误写 `await process.create_sftp_server()`，该方法在源码中不存在。实际 SCP 服务端通过 `create_server()` 的 `sftp_factory=True` 和 `allow_scp=True` 参数自动处理，已重写相关示例。
4. **不存在的服务端连接选项**：`concepts/10-server.md` 原列出 `permit_root_login`、`max_sessions`、`max_startups`、`allow_agent_forwarding` 四个参数，经 Grep 验证在 `SSHServerConnectionOptions` 中均不存在。已移除并替换为实际存在的 `keepalive_count_max`、`rekey_seconds`、`agent_forwarding`、`sftp_factory`、`allow_scp` 参数。
5. **不存在的客户端转发权限参数**：`concepts/11-advanced-patterns.md` 原文规划中曾考虑使用 `permit_remote_port_forwards`/`permit_open_direct_tcpip`/`permit_tun_device`，经 Grep 验证不存在；最终文档未使用这些参数，转发权限通过 SSHServer 回调（`connection_requested`/`server_requested`）控制。

### 验证结论

- 零虚构 API（所有文档引用的类/方法/函数均经 Grep 在 `external/libs/asyncssh/asyncssh/` 源码中验证存在）
- 5 处文档生成过程中的 API 名称错误已在 V 阶段发现并修正
- Frontmatter 完整率 100%
- 交叉链接无断裂
- 事实清单 180 条，无因果推断词
