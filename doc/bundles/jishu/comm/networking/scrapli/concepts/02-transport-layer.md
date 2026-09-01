---
type: Concept
title: 传输层
description: 四种 Transport 模式——BIN（系统SSH）、SSH2（libssh2）、Telnet、Test 的配置与选择
tags: [scrapli, transport, ssh2, bin, telnet, libssh2]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:grep-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
---

# 传输层

scrapli2 的传输层由 `TransportKind` 枚举定义，共有四种模式。所有传输逻辑在 Zig 层（libscrapli）实现，Python 侧通过 Options 数据类配置参数。

## TransportKind 枚举

| 枚举值 | 字符串 | FFI 值 | 说明 |
|--------|--------|--------|------|
| `BIN` | `"bin"` | 0 | 调用系统 OpenSSH 客户端二进制 |
| `TELNET` | `"telnet"` | 1 | Telnet 协议 |
| `SSH2` | `"ssh2"` | 2 | 通过 libssh2 原生 SSH |
| `TEST` | `"test_"` | 3 | 从文件读取（测试用） |

传输类型在 `transport_options` 中通过传入不同的 Options 类实例来选择。`Cli` 默认使用 `TransportBinOptions`。

## BIN 模式（系统 SSH）

`TransportBinOptions` 调用系统安装的 OpenSSH 客户端（`ssh` 命令），适合利用系统已有 SSH 配置的场景。

```python
from scrapli import Cli, AuthOptions, TransportBinOptions

cli = Cli(
    host="192.168.1.1",
    auth_options=AuthOptions(username="admin", password="admin"),
    transport_options=TransportBinOptions(
        bin="/usr/bin/ssh",              # SSH 二进制路径（默认使用 PATH 中的 ssh）
        ssh_config_path="~/.ssh/config",  # SSH config 文件路径
        known_hosts_path="~/.ssh/known_hosts",  # known_hosts 文件路径
        enable_strict_key=True,           # 启用严格主机密钥检查
        extra_open_args=["-o", "ConnectTimeout=10"],  # 额外命令行参数
        term_height=512,                  # 终端高度
        term_width=512,                   # 终端宽度
    ),
)
```

### BinOptions 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `bin` | `str \| None` | SSH 二进制路径 |
| `extra_open_args` | `list[str] \| None` | 追加的命令行参数 |
| `override_open_args` | `list[str] \| None` | 覆盖所有默认参数 |
| `ssh_config_path` | `str \| None` | SSH config 文件路径 |
| `known_hosts_path` | `str \| None` | known_hosts 文件路径 |
| `enable_strict_key` | `bool \| None` | 是否启用严格密钥检查 |
| `term_height` | `int \| None` | 终端高度（c_uint16） |
| `term_width` | `int \| None` | 终端宽度（c_uint16） |

BIN 模式的优势：可直接复用系统 `~/.ssh/config` 中的 ProxyJump、IdentityFile 等配置，与手动 SSH 体验一致。

## SSH2 模式（libssh2）

`TransportSsh2Options` 通过 Zig 内置的 libssh2 库实现 SSH，不依赖系统 SSH 客户端。

```python
from scrapli import Cli, AuthOptions, TransportSsh2Options

cli = Cli(
    host="192.168.1.1",
    auth_options=AuthOptions(
        username="admin",
        private_key_path="~/.ssh/id_rsa",
        private_key_passphrase="passphrase",
    ),
    transport_options=TransportSsh2Options(
        known_hosts_path="~/.ssh/known_hosts",
        libssh2_trace=False,
    ),
)
```

### SSH2 ProxyJump 支持

SSH2 模式内置 ProxyJump 支持（无需依赖系统 SSH config）：

```python
TransportSsh2Options(
    proxy_jump_host="bastion.example.com",
    proxy_jump_port=22,
    proxy_jump_username="bastion_user",
    proxy_jump_password="bastion_pass",
    proxy_jump_private_key_path="~/.ssh/bastion_key",
    proxy_jump_private_key_passphrase="bastion_passphrase",
    proxy_jump_libssh2_trace=False,
)
```

注意：`proxy_jump_host` 为 None 时，其余 proxy_jump 字段均不生效（必须先设置 host）。

### Ssh2Options 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `known_hosts_path` | `str \| None` | known_hosts 文件路径 |
| `libssh2_trace` | `bool \| None` | 启用 libssh2 跟踪调试 |
| `proxy_jump_host` | `str \| None` | 跳板机目标主机 |
| `proxy_jump_port` | `int \| None` | 跳板机端口 |
| `proxy_jump_username` | `str \| None` | 跳板机用户名 |
| `proxy_jump_password` | `str \| None` | 跳板机密码 |
| `proxy_jump_private_key_path` | `str \| None` | 跳板机私钥路径 |
| `proxy_jump_private_key_passphrase` | `str \| None` | 跳板机私钥密码 |
| `proxy_jump_libssh2_trace` | `bool \| None` | 跳板机会话 libssh2 跟踪 |

SSH2 模式下，`AuthOptions.private_key_content` 可直接传入私钥内容字符串（仅 SSH2 支持，BIN 模式不支持）。

## Telnet 模式

`TransportTelnetOptions` 使用 Telnet 协议，无额外配置字段：

```python
from scrapli import Cli, AuthOptions, TransportTelnetOptions

cli = Cli(
    host="192.168.1.1",
    port=23,  # Telnet 默认端口 23（自动推断）
    auth_options=AuthOptions(username="admin", password="admin"),
    transport_options=TransportTelnetOptions(),
)
```

使用 Telnet 时，`Cli` 自动将默认端口设为 23（SSH 默认为 22）。Telnet 模式通常需要配合 `AuthOptions` 的 `force_in_session_auth=True` 或 `bypass_in_session_auth` 选项。

## TEST 模式

`TransportTestOptions` 从文件读取数据而非建立真实网络连接，主要用于测试和离线开发：

```python
from scrapli import Cli, TransportTestOptions

cli = Cli(
    host="test",
    transport_options=TransportTestOptions(
        f="/path/to/captured_session.txt",
    ),
)
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `f` | `str \| None` | 读取的文件路径 |

## 传输模式选择指南

| 场景 | 推荐模式 | 理由 |
|------|---------|------|
| 日常自动化，系统有 OpenSSH | BIN | 复用 SSH config、ProxyJump、known_hosts |
| 需要嵌入式/无外部依赖 | SSH2 | libssh2 内置，不依赖系统 ssh 二进制 |
| 通过跳板机连接 | SSH2 | 内置 ProxyJump，无需系统配置 |
| 旧设备仅支持 Telnet | TELNET | 唯一选择 |
| 单元测试/离线开发 | TEST | 无需真实设备 |
| Windows 环境 | ❌ | 当前不支持 Windows（libscrapli 无 Windows 共享库） |

## 端口推断规则

`Cli` 根据 `transport_options` 类型自动推断默认端口：

- `TransportTelnetOptions` → 端口 23
- 其他所有传输 → 端口 22

`Netconf` 默认端口为 830（NETCONF 标准端口），不受传输类型影响。

跨束参考：
- [paramiko Transport 底层传输](../../paramiko/concepts/03-transport.md) — 纯 Python SSH 传输实现对比
- [asyncssh 异步连接](../../asyncssh/concepts/02-async-connection.md) — 异步 SSH 连接的传输配置
