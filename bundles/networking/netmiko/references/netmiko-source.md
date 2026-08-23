---
type: Reference
title: netmiko 源码信源登记
description: netmiko v4.7.0 源码路径、版本信息、核心模块清单与公开 API
tags: [netmiko, source, reference, v4.7.0]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: netmiko-github
    resource: https://github.com/ktbyers/netmiko
    title: netmiko GitHub 仓库
    author: human:ktbyers
  - id: netmiko-docs
    resource: https://github.com/ktbyers/netmiko/blob/develop/README.md
    title: netmiko README
---

# netmiko 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | netmiko |
| 版本 | **4.7.0**（commit 8ace5f2ae7da） |
| 描述 | Multi-vendor library to simplify legacy CLI connections to network devices（多厂商网络设备 SSH/Telnet CLI 自动化库） |
| 作者 | Kirk Byers |
| 许可证 | MIT |
| Python 要求 | ≥ 3.10 |
| 核心依赖 | paramiko（SSH）、scp（SCP 文件传输）、pyserial（串口）、textfms/ttp/genie（可选解析器） |
| 源码仓库 | <https://github.com/ktbyers/netmiko> |

## 源码位置

netmiko 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/netmiko/netmiko/
```

该目录通过 git submodule 引入，本地不做修改。包含 348 个 `.py` 文件，支持 100+ 网络平台。

## 核心模块清单

| 模块 | 说明 |
|------|------|
| `__init__.py` | 包入口，版本号、Python 版本检查、公开 API 导出 |
| `ssh_dispatcher.py` | ConnectHandler 工厂、CLASS_MAPPER/CLASS_MAPPER_BASE、platforms 列表、redispatch、FileTransfer 工厂 |
| `base_connection.py` | BaseConnection 核心基类（最大文件），连接生命周期、命令执行、配置管理 |
| `ssh_autodetect.py` | SSHDetect 自动设备类型探测，SSH_MAPPER_DICT 指纹库 |
| `cisco_base_connection.py` | CiscoBaseConnection（Cisco 设备基类）、CiscoSSHConnection、CiscoFileTransfer |
| `scp_handler.py` | SCPConn、BaseFileTransfer（SCP 文件传输核心） |
| `scp_functions.py` | file_transfer() 便捷函数、progress_bar()、verifyspace_and_transferfile() |
| `exceptions.py` | 异常体系（NetmikoTimeoutException、NetmikoAuthenticationException 等） |
| `utilities.py` | 工具函数（structured_data_converter、TextFSM/TTP/Genie 解析等） |
| `channel.py` | Channel/SSHChannel/TelnetChannel/SerialChannel 通道抽象 |
| `session_log.py` | SessionLog 会话日志 |
| `ssh_auth.py` | SSH 认证处理 |
| `no_enable.py` | NoEnable mixin（无特权模式平台） |
| `no_config.py` | NoConfig mixin（无配置模式平台） |
| `netmiko_globals.py` | 全局常量（BACKSPACE_CHAR 等） |

## 厂商驱动目录（采样）

| 目录 | 驱动类 | device_type | 继承关系 |
|------|--------|-------------|----------|
| `cisco/` | CiscoIosSSH | cisco_ios | CiscoIosBase → CiscoBaseConnection → BaseConnection |
| `arista/` | AristaSSH | arista_eos | AristaBase → CiscoSSHConnection → CiscoBaseConnection → BaseConnection |
| `juniper/` | JuniperSSH | juniper_junos | JuniperBase(NoEnable, BaseConnection) |
| `linux/` | LinuxSSH | linux | LinuxSSH → CiscoSSHConnection → CiscoBaseConnection → BaseConnection |
| `hp/` | HPComwareSSH | hp_comware | HPComwareBase → CiscoSSHConnection → CiscoBaseConnection → BaseConnection |

## 公开 API 导出

`__init__.py` 通过 `__all__` 导出以下公开 API：

**工厂与连接：**
- `ConnectHandler` — 主工厂函数
- `ssh_dispatcher` — 设备类型到类的查找函数
- `redispatch` — 动态切换驱动类
- `platforms` — 支持的 device_type 排序列表
- `FileTransfer` — 文件传输工厂
- `SCPConn` — SCP 连接类
- `InLineTransfer` — Cisco IOS TCL 内联传输
- `SSHDetect` — 设备类型自动探测
- `BaseConnection` — 连接基类
- `TelnetFallback` — SSH 失败回退 Telnet
- `ConnLogOnly` — 仅记录日志的连接器
- `ConnUnify` — 统一异常连接器
- `Netmiko` — ConnectHandler 别名

**异常类：**
- `NetmikoBaseException`, `ConnectionException`
- `NetmikoTimeoutException`, `NetMikoTimeoutException`（别名）
- `NetmikoAuthenticationException`, `NetMikoAuthenticationException`（别名）
- `ConfigInvalidException`, `ReadException`, `ReadTimeout`

**便捷函数：**
- `file_transfer` — SCP 文件传输一站式函数
- `progress_bar` — 进度条回调

## CLASS_MAPPER 结构

`CLASS_MAPPER` 是 netmiko 多厂商架构的核心数据结构：

1. `CLASS_MAPPER_BASE` 包含约170个基础映射（device_type → 驱动类）
2. 自动为每个 key 生成 `_ssh` 后缀别名
3. 单独追加约60个 `_telnet` 驱动
4. 追加2个 `_serial` 驱动
5. `"terminal_server"` 和 `"autodetect"` 映射到 TerminalServerSSH

`FILE_TRANSFER_MAP` 包含18个支持 SCP 的平台，同样自动生成 `_ssh` 后缀别名。

## 版本说明

- netmiko 4.x 废弃了 `delay_factor` 和 `max_loops` 参数（仍在部分方法中保留但发出 DeprecationWarning）
- `fast_cli=True` 为默认行为，将 global_delay_factor 降至 0.1
- `send_command_expect` 为 `send_command` 的别名（向后兼容）
- 支持 TextFSM、TTP、Genie/pyATS 三种结构化输出解析器
