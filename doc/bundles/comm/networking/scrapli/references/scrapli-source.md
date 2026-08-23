---
type: Reference
title: scrapli2 源码信源登记
description: scrapli2 0.0.0-dev 源码路径、版本信息、Zig+Python 混合架构、核心模块清单与公开 API
tags: [scrapli, source, reference, zig, ctypes]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:grep-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-github
    resource: https://github.com/scrapli/scrapli
    title: scrapli GitHub 仓库
  - id: libscrapli-github
    resource: https://github.com/scrapli/libscrapli
    title: libscrapli GitHub 仓库（Zig 核心）
---

# scrapli2 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | scrapli（scrapli2 重写版） |
| Python 包版本 | **0.0.0-dev**（`__version__ = "0.0.0"`） |
| libscrapli 版本 | **0.0.1-rc.35** |
| definitions 版本 | 0.0.5 |
| 描述 | Zig 核心 + Python ctypes 绑定的网络设备自动化库 |
| 架构 | 混合语言：Zig 编译共享库 + Python 薄绑定层 |
| 源码仓库 | <https://github.com/scrapli/scrapli> |
| Zig 核心仓库 | <https://github.com/scrapli/libscrapli> |

## 重要架构说明

**这是 scrapli 的大版本重写版（scrapli2），不是旧版纯 Python scrapli。**

scrapli2 将核心协议逻辑迁移到 Zig 语言编写的独立仓库 `libscrapli`，编译为共享库（`.so`/`.dylib`）。Python 层通过 `ctypes` 调用 Zig 共享库，不再包含旧版的 driver/transport/channel 三层 Python 类体系。

与旧版 scrapli（v202x）的关键差异：

| 维度 | 旧版 scrapli | scrapli2（本版本） |
|------|-------------|-------------------|
| 核心语言 | 纯 Python | Zig（libscrapli 共享库） |
| Python 绑定 | 直接实现协议 | ctypes 薄绑定 |
| 主驱动类 | `Scrapli`/`AsyncScrapli`/`NetworkDriver` | `Cli`/`Netconf` |
| Transport 层 | Python 类（SystemTransport/SSH2Transport/TelnetTransport） | `TransportBinOptions`/`TransportSsh2Options`/`TransportTelnetOptions`/`TransportTestOptions`（数据类，由 Zig 实现） |
| Channel 层 | Python `Channel` 类 | 无独立 Python Channel 类，由 Zig 内部管理 |
| 平台定义 | Python 类继承 | YAML 声明式文件（44 个内置平台） |
| 异步支持 | `asyncio` 独立类 | 同步/异步方法对（同一类中） |
| Windows 支持 | 支持 | 不支持（libscrapli 无 Windows 共享库） |

## 源码位置

scrapli2 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/scrapli/scrapli/
```

## 核心模块清单

| 模块 | 说明 |
|------|------|
| `__init__.py` | 包入口，导出公开 API：Cli、Netconf、AuthOptions、SessionOptions、TransportBinOptions、TransportSsh2Options、TransportTelnetOptions、TransportTestOptions、LookupKeyValue、ReadCallback、NetconfOptions |
| `cli.py` | CLI 驱动主类 `Cli`、`LoadedDefinition` dataclass、`InputHandling` 枚举、`ReadCallback` dataclass、Cli `Options` dataclass |
| `netconf.py` | NETCONF 驱动类 `Netconf`、NETCONF 枚举（Version/DatastoreType/FilterType/DefaultsType/SchemaFormat/ConfigFilter/DefaultOperation/TestOption/ErrorOption）、Netconf `Options` dataclass |
| `cli_result.py` | CLI `Result` 类：命令结果封装、TextFSM/Genie 解析集成、原始输出延迟重构 |
| `netconf_result.py` | NETCONF `Result` dataclass：RPC 结果封装、XML header 剥离、原始输出延迟重构 |
| `cli_decorators.py` | `handle_operation_timeout`/`handle_operation_timeout_async` 装饰器 |
| `netconf_decorators.py` | NETCONF 操作超时装饰器 |
| `cli_parse.py` | TextFSM 和 Genie 输出解析函数（可选依赖） |
| `transport.py` | `TransportKind` 枚举、`Options` 抽象基类、`BinOptions`/`Ssh2Options`/`TelnetOptions`/`TestOptions` |
| `session.py` | Session `Options` dataclass：读大小、超时、回车符、录制器配置 |
| `auth.py` | `LookupKeyValue` dataclass、Auth `Options` dataclass：用户名/密码/密钥/lookups |
| `exceptions.py` | 异常层次：ScrapliException 基类及 16 个子类（共 17 个异常类） |
| `ffi.py` | libscrapli 共享库定位与加载，支持 Linux（musl/gnu）和 macOS |
| `ffi_types.py` | ctypes 类型定义：ZigSlice、ZigU64Slice、Cancel、LibScrapliFFIResult、回调包装器 |
| `ffi_options.py` | ctypes Structure 定义：CLI/Netconf/Session/Auth/Transport 选项结构体 |
| `ffi_mapping.py` | `LibScrapliSharedMapping`：共享 FFI 函数映射（alloc/free/poll_fd/options） |
| `ffi_mapping_cli.py` | CLI 专属 FFI 函数映射 |
| `ffi_mapping_netconf.py` | NETCONF 专属 FFI 函数映射 |
| `helper.py` | 工具函数：文件解析、同步/异步操作结果等待、时间转换 |
| `definitions/` | 44 个 YAML 平台定义文件（cisco_iosxe、arista_eos、juniper_junos 等） |
| `definition_options/` | 平台特定 Python 钩子（mikrotik_routeros.py） |
| `lib/` | 预编译共享库存放目录（wheel 安装时包含） |

## 公开 API（从 `__init__.py` 确认）

```python
from scrapli import (
    Cli,                    # CLI 驱动主类
    Netconf,                # NETCONF 驱动类
    AuthOptions,            # 认证选项（auth.Options 别名）
    SessionOptions,         # 会话选项（session.Options 别名）
    NetconfOptions,         # NETCONF 选项（netconf.Options 别名）
    TransportBinOptions,    # BIN 传输选项（系统 ssh）
    TransportSsh2Options,   # SSH2 传输选项（libssh2）
    TransportTelnetOptions, # Telnet 传输选项
    TransportTestOptions,   # 测试传输选项
    LookupKeyValue,         # 键值查找对
    ReadCallback,           # 读回调描述符
)
```

## 四种 Transport 模式

| 模式 | TransportKind | Options 类 | 说明 |
|------|--------------|-----------|------|
| BIN | `"bin"` (FFI=0) | `TransportBinOptions` | 调用系统 OpenSSH 客户端二进制，支持 ssh_config、known_hosts、ProxyJump |
| TELNET | `"telnet"` (FFI=1) | `TransportTelnetOptions` | Telnet 协议，无额外选项 |
| SSH2 | `"ssh2"` (FFI=2) | `TransportSsh2Options` | 通过 libssh2（Zig 内置），支持 ProxyJump、known_hosts |
| TEST | `"test_"` (FFI=3) | `TransportTestOptions` | 从文件读取数据，用于测试 |

## 平台支持

内置 44 个平台 YAML 定义，包括但不限于：Cisco IOS-XE/IOS-XR/NX-OS/ASA/AireOS/FTD、Arista EOS、Juniper Junos、Huawei VRP、Fortinet FortiOS、Palo Alto PAN-OS、Nokia SR OS/SR Linux、MikroTik RouterOS、Aruba AOS-CX、Dell EMC、Cumulus Linux、VyOS 等。

## FFI 架构

- Python 通过 `ctypes.CDLL` 加载 libscrapli 共享库
- 共享库文件名格式：`libscrapli-{arch}-linux-{abi}.so.{version}` 或 `libscrapli-{arch}-macos.{version}.dylib`
- 支持架构：x86_64、aarch64
- 支持的 libc ABI：glibc、musl
- 环境变量 `LIBSCRAPLI_PATH` 可覆盖共享库路径
