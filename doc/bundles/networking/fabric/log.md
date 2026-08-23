# fabric 知识束生成日志

## R 阶段（事实采集）

- 读取任务简报：`.trae/specs/ssh-python-okf-wiki/fabric-task-brief.md`
- 参考 OKF 范例：`bundles/networking/paramiko/`（同批次生成的 paramiko 知识束）
- 逐模块阅读 fabric v4.0.0 源码（`external/libs/fabric/fabric/`，commit ded51893f02c）：
  - `__init__.py`、`_version.py`
  - `connection.py`（1122 行，核心文件）
  - `config.py`、`group.py`、`runners.py`
  - `transfer.py`、`tunnels.py`、`executor.py`、`tasks.py`
  - `auth.py`、`main.py`、`exceptions.py`、`util.py`
  - `testing/base.py`、`testing/fixtures.py`、`testing/__init__.py`
- 提取 **92 条**编号事实，输出至 `.trae/specs/ssh-python-okf-wiki/fabric-facts.md`
- 发现：任务简报验证清单中列出的 `create_sftp_conn` 和 `from_context` 方法在 fabric v4.0.0 源码中不存在；实际 SFTP 访问方法名为 `sftp()`（connection.py:880）

## I 阶段（架构洞察）

- 提炼 **5 个核心架构洞察**，输出至 `.trae/specs/ssh-python-okf-wiki/fabric-insights.md`：
  1. Connection 的双层架构——is-a invoke.Context + has-a paramiko.SSHClient
  2. Group 的模板方法模式与 GroupResult 异常聚合
  3. Remote Runner 的模板方法——SSH channel 适配 invoke Runner 抽象
  4. Config 的多层合并与 SSH config 文件的独立体系
  5. 跳板机网关的递归 Connection 链与 direct-tcpip 通道
- 设计知识地图：入门(2篇) → 核心(4篇) → 高级(3篇)，共 9 篇概念文档

## E 阶段（批量生成）

### Step 1: 创建目录结构
- `bundles/networking/fabric/concepts/`
- `bundles/networking/fabric/examples/`
- `bundles/networking/fabric/references/`

### Step 2: 信源先行
- `references/fabric-source.md`

### Step 3: concepts/ 批次1（入门+核心，6篇）
1. `concepts/00-introduction.md`
2. `concepts/01-getting-started.md`
3. `concepts/02-connection.md`
4. `concepts/03-configuration.md`
5. `concepts/04-command-execution.md`
6. `concepts/05-group-parallel.md`

### Step 3: concepts/ 批次2（高级，3篇）
7. `concepts/06-file-transfer.md`
8. `concepts/07-tunnels.md`
9. `concepts/08-advanced-patterns.md`

### Step 4: examples/（4篇）
1. `examples/basic-deploy.md`
2. `examples/multi-server-group.md`
3. `examples/file-upload-download.md`
4. `examples/tunnel-bastion.md`

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
| Connection | connection.py:49 | ✅ |
| Config | config.py:12 | ✅ |
| Group | group.py:9 | ✅ |
| SerialGroup | group.py:204 | ✅ |
| ThreadingGroup | group.py:231 | ✅ |
| GroupResult | group.py:286 | ✅ |
| Remote | runners.py:14 | ✅ |
| RemoteShell | runners.py:167 | ✅ |
| Result (runners) | runners.py:172 | ✅ |
| Transfer | transfer.py:21 | ✅ |
| Result (transfer) | transfer.py:326 | ✅ |
| Tunnel | tunnels.py:109 | ✅ |
| TunnelManager | tunnels.py:17 | ✅ |
| Executor | executor.py:9 | ✅ |
| ConnectionCall | tasks.py:74 | ✅ |
| Task | tasks.py:6 | ✅ |
| OpenSSHAuthStrategy | auth.py:16 | ✅ |
| Fab | main.py:18 | ✅ |
| GroupException | exceptions.py:7 | ✅ |
| NothingToDo | exceptions.py:3 | ✅ |
| InvalidV1Env | exceptions.py:21 | ✅ |
| MockRemote | testing/base.py:360 | ✅ |
| MockSFTP | testing/base.py:495 | ✅ |
| Session | testing/base.py:119 | ✅ |
| MockChannel | testing/base.py:86 | ✅ |
| Command | testing/base.py:31 | ✅ |
| ShellCommand | testing/base.py:75 | ✅ |

**方法名验证（全部通过）**：

| 方法 | 源码位置 | 状态 |
|------|---------|------|
| Connection.open | connection.py:596 | ✅ |
| Connection.close | connection.py:716 | ✅ |
| Connection.run | connection.py:756 | ✅ |
| Connection.sudo | connection.py:773 | ✅ |
| Connection.local | connection.py:866 | ✅ |
| Connection.shell | connection.py:787 | ✅ |
| Connection.sftp | connection.py:880 | ✅ |
| Connection.get | connection.py:895 | ✅ |
| Connection.put | connection.py:906 | ✅ |
| Connection.forward_local | connection.py:922 | ✅ |
| Connection.forward_remote | connection.py:1021 | ✅ |
| Connection.open_gateway | connection.py:676 | ✅ |
| Connection.create_session | connection.py:744 | ✅ |
| Connection.from_v1 | connection.py:145 | ✅ |
| Connection.is_connected | connection.py:588 | ✅ |
| Connection.resolve_connect_kwargs | connection.py:478 | ✅ |
| Connection.get_gateway | connection.py:507 | ✅ |
| Config.from_v1 | config.py:42 | ✅ |
| Config.load_ssh_config | config.py:176 | ✅ |
| Config.set_runtime_ssh_path | config.py:165 | ✅ |
| Config.global_defaults | config.py:277 | ✅ |
| Group.run/sudo/put/get/close | group.py:104-188 | ✅ |
| Group.from_connections | group.py:87 | ✅ |
| Remote.start | runners.py:48 | ✅ |
| Remote.returncode | runners.py:117 | ✅ |
| Remote.generate_result | runners.py:120 | ✅ |
| Remote.handle_window_change | runners.py:139 | ✅ |
| Transfer.get | transfer.py:43 | ✅ |
| Transfer.put | transfer.py:187 | ✅ |
| Tunnel.read_and_write | tunnels.py:143 | ✅ |
| Executor.normalize_hosts | executor.py:24 | ✅ |
| Executor.expand_calls | executor.py:50 | ✅ |
| Executor.parameterize | executor.py:101 | ✅ |
| ConnectionCall.make_context | tasks.py:104 | ✅ |
| OpenSSHAuthStrategy.get_pubkeys | auth.py:91 | ✅ |
| OpenSSHAuthStrategy.get_sources | auth.py:184 | ✅ |

**任务简报验证清单中不存在的 API**：

| 清单中列出的名称 | 实际情况 | 文档处理 |
|-----------------|---------|---------|
| `create_sftp_conn` | 源码中不存在；实际方法为 `sftp()`（connection.py:880） | 文档中使用正确名称 `sftp()`，未引用 `create_sftp_conn` |
| `from_context` | 源码中不存在；fabric 无此方法 | 文档中未引用 |

### Frontmatter 检查

14 个内容文件（9 概念 + 4 示例 + 1 信源）全部包含 type/title/description/tags/generated/verified/status/stale_after/sources 九个字段。

### 交叉引用检查

- 跨束引用 paramiko 使用相对路径 `../../paramiko/concepts/` 格式（子目录内）
- 跨组引用 pyinvoke 使用相对路径 `../../../tooling/pyinvoke/index.md` 格式（子目录内，需三层 `../` 到达 bundles/）
- 束内引用使用相对路径（如 `02-connection.md`）
- 所有引用目标文件均存在（2026-08-23 全局验证修正：pyinvoke 链接路径从 `../../tooling/pyinvoke/concepts/` 修正为 `../../../tooling/pyinvoke/index.md`）

### 虚构 API 修复记录

无虚构 API。所有文档引用的类名、方法名、属性名均通过 Grep 在 `external/libs/fabric/fabric/` 中验证存在。任务简报中列出的 `create_sftp_conn` 和 `from_context` 在源码中不存在，但文档生成过程中未引用这两个名称（使用了正确的 `sftp()` 方法名）。

### 验证结论

- 零虚构 API（所有文档引用的类/方法均经 Grep 验证存在）
- Frontmatter 完整率 100%
- 跨束交叉链接使用正确的相对路径格式
- 事实清单 92 条，无因果推断词
