---
type: Concept
title: 认证与会话配置
description: AuthOptions、SessionOptions 详解——用户名/密码/密钥认证、会话超时、读取参数、录制器
tags: [scrapli, authentication, session, auth-options, timeout]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:grep-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
---

# 认证与会话配置

## AuthOptions

`AuthOptions`（`scrapli.auth.Options` 的别名）配置连接认证信息。所有字段均为可选，但实际连接时至少需要提供用户名和某种凭据（密码或密钥）。

```python
from scrapli import AuthOptions

auth = AuthOptions(
    username="admin",
    password="admin123",
    private_key_path="~/.ssh/id_rsa",
    private_key_passphrase="keypass",
    private_key_content="-----BEGIN OPENSSH PRIVATE KEY-----\n...",
)
```

### 字段一览

| 字段 | 类型 | 说明 |
|------|------|------|
| `username` | `str \| None` | 登录用户名 |
| `password` | `str \| None` | 登录密码 |
| `private_key_path` | `str \| None` | SSH 私钥文件路径 |
| `private_key_passphrase` | `str \| None` | 私钥密码短语 |
| `private_key_content` | `str \| None` | 私钥内容字符串（仅 SSH2 传输支持） |
| `lookups` | `list[LookupKeyValue] \| None` | 模板查找键值对列表 |
| `force_in_session_auth` | `bool \| None` | 强制会话内认证 |
| `bypass_in_session_auth` | `bool \| None` | 跳过会话内认证 |
| `username_pattern` | `str \| None` | 用户名提示符正则 |
| `password_pattern` | `str \| None` | 密码提示符正则 |
| `private_key_passphrase_pattern` | `str \| None` | 密钥密码提示符正则 |

### 安全特性

`AuthOptions.__repr__` 自动对敏感字段脱敏，密码和密钥内容在日志和调试输出中显示为 `REDACTED`：

```python
print(repr(auth))
# AuthOptions(username='admin', password=REDACTED, private_key_path='/home/user/.ssh/id_rsa', ...)
```

### LookupKeyValue

`LookupKeyValue` 用于平台定义模板中的变量替换。YAML 平台定义可通过 `__lookup::key_name` 语法引用查找表中的值：

```python
from scrapli import AuthOptions, LookupKeyValue

auth = AuthOptions(
    username="admin",
    password="admin",
    lookups=[
        LookupKeyValue(key="enable", value="enable_password"),
        LookupKeyValue(key="snmp_community", value="public"),
    ],
)
```

在 Cisco IOS-XE 平台定义中，`enable` 命令的密码提示响应使用 `__lookup::enable`，Zig 层自动从 lookups 列表中查找对应值。这使得敏感的 enable 密码不必硬编码在 YAML 定义中。

`LookupKeyValue.__repr__` 同样将 value 脱敏为 `REDACTED`。

### 会话内认证控制

- `force_in_session_auth=True`：无条件强制执行会话内认证流程（即使传输层已认证）
- `bypass_in_session_auth=True`：跳过会话内认证（即使 Telnet/BIN 传输预期需要）

### 自定义提示符模式

对于非标准设备，可覆盖认证提示符的正则匹配：

```python
AuthOptions(
    username="admin",
    password="admin",
    username_pattern=r"[Uu]sername:",
    password_pattern=r"[Pp]assword:",
)
```

## SessionOptions

`SessionOptions`（`scrapli.session.Options` 的别名）配置会话级别的行为参数。

```python
from scrapli import SessionOptions

session = SessionOptions(
    operation_timeout_s=30,
    read_size=1024,
    return_char="\n",
)
```

### 字段一览

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `read_size` | `int \| None` | None（Zig 层默认） | 每次读取的缓冲区大小 |
| `read_min_delay_ns` | `int \| None` | None | 读取最小延迟（纳秒） |
| `read_max_delay_ns` | `int \| None` | None | 读取最大延迟（纳秒） |
| `return_char` | `str \| None` | None（Zig 层默认） | 回车符（如 `"\n"` 或 `"\r\n"`） |
| `operation_timeout_s` | `int \| None` | None | 操作超时（秒），自动转换为纳秒 |
| `operation_timeout_ns` | `int \| None` | 10,000,000,000（10秒） | 操作超时（纳秒） |
| `operation_max_search_depth` | `int \| None` | None | 操作最大搜索深度 |
| `scratch_initial_size` | `int \| None` | None | 临时缓冲区初始大小 |
| `scratch_retain_max` | `int \| None` | None | 临时缓冲区最大保留量 |
| `recorder_path` | `str \| None` | None | 会话录制输出文件路径 |
| `recorder_callback` | `Callable[[str], None] \| None` | None | 会话录制回调函数 |

### 超时配置

默认操作超时为 **10 秒**（`DEFAULT_OPERATION_TIMEOUT_NS = 10_000_000_000`）。可通过两种方式设置：

```python
# 方式一：秒（自动转换为纳秒）
SessionOptions(operation_timeout_s=30)

# 方式二：纳秒（更精确）
SessionOptions(operation_timeout_ns=30_000_000_000)
```

当同时设置 `operation_timeout_s` 和 `operation_timeout_ns` 时，`__post_init__` 仅在 `operation_timeout_ns` 未设置时从秒转换。

操作级超时可在每次调用时覆盖：

```python
result = cli.send_input("show version", operation_timeout_ns=60_000_000_000)
```

`handle_operation_timeout` 装饰器在操作前后临时设置和重置超时值，操作完成后（无论成功或异常）无条件恢复 SessionOptions 中的默认值。

### 会话录制

SessionOptions 支持两种录制方式：

**文件录制**：

```python
SessionOptions(recorder_path="/tmp/session_record.txt")
```

**回调录制**：

```python
def record_session(data: str) -> None:
    print(f"[RECORD] {data}")

SessionOptions(recorder_callback=record_session)
```

录制器通过 ctypes 回调函数（`RecorderCallbackC`）从 Zig 层接收数据。

### 回车符配置

大多数网络设备使用 `\n`，但某些设备（如 MikroTik RouterOS）需要 `\r\n`。平台定义钩子可自动设置此值（MikroTik 的 post_init 钩子设置 `return_char = "\r\n"`）。

## Cli 专属选项

`cli.Options`（CliOptions）配置 CLI 驱动特有的输出处理行为：

```python
from scrapli.cli import Options as CliOptions

cli_opts = CliOptions(
    normalize_line_feeds=True,
    normalize_trailing_whitespace=True,
)
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `normalize_line_feeds` | `bool \| None` | 将 `\r\n` 规范化为 `\n` |
| `normalize_trailing_whitespace` | `bool \| None` | 去除行尾空白 |

## 完整配置示例

```python
from scrapli import (
    Cli, AuthOptions, SessionOptions,
    TransportSsh2Options,
)
from scrapli.cli import Options as CliOptions

cli = Cli(
    host="router.example.com",
    port=22,
    definition_file_or_name="cisco_iosxe",
    auth_options=AuthOptions(
        username="admin",
        password="secret",
        lookups=[LookupKeyValue(key="enable", value="enable_secret")],
    ),
    session_options=SessionOptions(
        operation_timeout_s=30,
        read_size=4096,
        recorder_path="/tmp/router_session.log",
    ),
    transport_options=TransportSsh2Options(
        known_hosts_path="~/.ssh/known_hosts",
    ),
    cli_options=CliOptions(
        normalize_line_feeds=True,
    ),
)
```

跨束参考：
- [paramiko 认证体系](../../paramiko/concepts/05-authentication.md) — paramiko 的多种认证方式对比
- [asyncssh 认证](../../asyncssh/concepts/05-authentication.md) — asyncssh 的密钥和证书认证
