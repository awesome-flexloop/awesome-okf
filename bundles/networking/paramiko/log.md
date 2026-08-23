# paramiko 知识束生成日志

## R 阶段（事实采集）

- 读取任务简报：`.trae/specs/ssh-python-okf-wiki/paramiko-task-brief.md`
- 参考 OKF 范例：`projects/awesome-okf-xs/bundles/tooling/pyinvoke/`（index.md、concepts/00-introduction.md、references/pyinvoke-source.md）
- 逐模块阅读 paramiko v5.0.0 源码（`external/libs/paramiko/paramiko/`）：
  - `__init__.py`、`client.py`、`transport.py`、`channel.py`
  - `auth_handler.py`、`auth_strategy.py`
  - `pkey.py`、`rsakey.py`、`ed25519key.py`、`ecdsakey.py`
  - `sftp_client.py`、`sftp_file.py`、`sftp_attr.py`、`sftp_server.py`、`sftp_si.py`、`sftp_handle.py`、`sftp.py`
  - `server.py`、`hostkeys.py`、`agent.py`、`proxy.py`
  - `common.py`、`message.py`、`packet.py`、`buffered_pipe.py`、`file.py`、`config.py`、`compress.py`
  - `ssh_exception.py`、`util.py`、`kex_*.py`
- 提取 **123 条**编号事实，输出至 `.trae/specs/ssh-python-okf-wiki/paramiko-facts.md`
- 发现：DSSKey 类在 paramiko v5.0.0 中已不存在（任务简报验证清单中列出，但源码中无此类定义）

## I 阶段（架构洞察）

- 提炼 **5 个核心架构洞察**，输出至 `.trae/specs/ssh-python-okf-wiki/paramiko-insights.md`：
  1. 三层 API 架构——SSHClient 门面 / Transport 引擎 / Channel 多路复用
  2. 认证双轨制——legacy _auth 与 AuthStrategy 并存
  3. ClosingContextManager 贯穿所有资源类
  4. 主机密钥策略的可插拔设计
  5. SFTP 请求-应答模型与流水线优化
- 设计知识地图：入门(2篇) → 核心(5篇) → 高级(4篇)，共 11 篇概念文档

## E 阶段（批量生成）

### Step 1: 创建目录结构
- `bundles/networking/paramiko/concepts/`
- `bundles/networking/paramiko/examples/`
- `bundles/networking/paramiko/references/`

### Step 2: 信源先行
- `references/paramiko-source.md`

### Step 3: concepts/ 批次1（入门+核心，7篇）
1. `concepts/00-introduction.md`
2. `concepts/01-getting-started.md`
3. `concepts/02-ssh-client.md`
4. `concepts/03-transport.md`
5. `concepts/04-channel.md`
6. `concepts/05-authentication.md`
7. `concepts/06-keys-and-hostkeys.md`

### Step 3: concepts/ 批次2（高级，4篇）
8. `concepts/07-sftp.md`
9. `concepts/08-port-forwarding.md`
10. `concepts/09-server.md`
11. `concepts/10-advanced-patterns.md`

### Step 4: examples/（5篇）
1. `examples/basic-connection.md`
2. `examples/execute-commands.md`
3. `examples/file-transfer.md`
4. `examples/port-forwarding.md`
5. `examples/interactive-shell.md`

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
| SSHClient | client.py:47 | ✅ |
| Transport | transport.py:153 | ✅ |
| Channel | channel.py:75 | ✅ |
| SFTPClient | sftp_client.py:90 | ✅ |
| SFTPServer | sftp_server.py:86 | ✅ |
| ServerInterface | server.py:34 | ✅ |
| MissingHostKeyPolicy | client.py:786 | ✅ |
| AutoAddPolicy | client.py:807 | ✅ |
| RejectPolicy | client.py:825 | ✅ |
| WarningPolicy | client.py:843 | ✅ |
| PKey | pkey.py:118 | ✅ |
| RSAKey | rsakey.py:35 | ✅ |
| Ed25519Key | ed25519key.py:30 | ✅ |
| ECDSAKey | ecdsakey.py:97 | ✅ |
| DSSKey | — | ❌ 不存在（v5.0.0 已移除，文档中未引用） |
| HostKeys | hostkeys.py:33 | ✅ |
| Agent | agent.py:391 | ✅ |
| ProxyCommand | proxy.py:39 | ✅ |
| BufferedFile | file.py:31 | ✅ |
| SSHException | ssh_exception.py:22 | ✅ |
| AuthenticationException | ssh_exception.py:30 | ✅ |
| BadHostKeyException | ssh_exception.py:115 | ✅ |

**方法名验证（全部通过）**：

connect、exec_command、invoke_shell、open_sftp、open_channel、start_client、start_server、set_missing_host_key_policy、get_transport、close、recv、send、recv_exit_status、get_pty（非 request_pty）、resize_pty、put、get、chdir、chmod、chown、stat、listdir、posix_rename、from_transport、request_port_forward、cancel_port_forward 均在源码中验证存在。

**注意**：任务验证清单中的 `request_pty` 实际方法名为 `get_pty`（channel.py:162）；`file` 实际方法名为 `open`（sftp_client.py:326）。文档中均使用正确名称。

### Frontmatter 检查

17 个内容文件（11 概念 + 5 示例 + 1 信源）全部包含 type/title/description/tags/generated/verified/status/stale_after/sources 九个字段。

### 链接检查

所有 `/concepts/`、`/examples/`、`/references/` 开头的交叉链接目标文件均存在，无断裂链接。

### 虚构 API 修复

1. **NoValidConnectionsError 引用路径错误**：examples/basic-connection.md 中误用 `paramiko.NoValidConnectionsError`，该类未在 `__init__.py` 中导出，已修正为 `paramiko.ssh_exception.NoValidConnectionsError`。
2. **缺少 import 语句**：examples/interactive-shell.md 的非阻塞读取示例使用 `socket.timeout` 但未导入 socket 模块，已添加 `import socket`。
3. **事实清单推断词**：F-105 中"用于"一词违反事实格式规范（禁止因果推断词），已修改为客观描述。

### 验证结论

- 零虚构 API（所有文档引用的类/方法均经 Grep 验证存在）
- Frontmatter 完整率 100%
- 交叉链接无断裂
- 事实清单 123 条，无因果推断词
