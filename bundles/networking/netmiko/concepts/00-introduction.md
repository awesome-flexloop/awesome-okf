---
type: Concept
title: netmiko 简介
description: 多厂商网络设备 SSH 自动化库——什么是 netmiko、设计哲学、安装方法、CLI vs API
tags: [netmiko, introduction, network-automation, ssh]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: netmiko-source
    resource: /references/netmiko-source.md
---

# netmiko 简介

## 什么是 netmiko

netmiko 是一个纯 Python 编写的**多厂商网络设备 SSH/Telnet CLI 自动化库**。它由 Kirk Byers 创建，基于 [paramiko](../../paramiko/concepts/02-ssh-client.md) 构建，旨在简化通过命令行界面（CLI）管理网络设备的过程。

netmiko 支持 100+ 种网络平台，涵盖 Cisco、Arista、Juniper、HP、Huawei、Fortinet、Palo Alto 等主流厂商。与 paramiko 作为通用 SSH 库不同，netmiko 专门针对网络设备的交互特性进行了深度封装：自动处理分页、终端宽度、特权模式、配置模式、提示符识别等网络设备特有的交互细节。

## 设计哲学

- **多厂商统一接口**：通过 `ConnectHandler(device_type=...)` 工厂函数，无论底层设备是 Cisco IOS 还是 Juniper Junos，上层代码使用相同的 `send_command()`、`send_config_set()` 等方法
- **CLI screen-scraping 模型**：通过 PTY（伪终端）交互式 shell 发送命令、读取输出，使用正则表达式匹配提示符判断命令完成。这种模型适用于所有支持 SSH CLI 的设备
- **模板方法模式**：`BaseConnection` 定义连接生命周期骨架，厂商驱动重写特定步骤（如 `session_preparation`、`disable_paging`、`config_mode`）
- **注册表驱动**：`CLASS_MAPPER` 字典维护 device_type 字符串到驱动类的映射，新增厂商只需注册新类
- **结构化输出补完**：内置 TextFSM、TTP、Genie/pyATS 三种解析器集成，将非结构化 CLI 输出转为结构化数据

## 安装方法

```bash
pip install netmiko
```

netmiko 4.7.0 要求 Python 3.10+。核心依赖包括 paramiko（SSH）、scp（文件传输）、pyserial（串口支持）。

可选安装以启用结构化解析：

```bash
pip install netmiko textfsm ttp genie
```

## CLI vs API

网络设备管理存在两种范式：

| 维度 | CLI（netmiko） | API（NETCONF/RESTCONF） |
|------|----------------|------------------------|
| 协议 | SSH/Telnet + PTY | NETCONF/RESTCONF over SSH/HTTPS |
| 数据格式 | 非结构化文本 | XML/JSON 结构化数据 |
| 可靠性 | 依赖文本解析，输出格式变化可能破坏脚本 | Schema 约束，变更可检测 |
| 设备覆盖 | 几乎所有网络设备 | 仅支持 API 的较新设备 |
| 学习曲线 | 网络工程师熟悉 CLI 命令 | 需要学习 YANG 模型和 API 操作 |
| 适用场景 | 遗留设备、快速运维、show 命令批量执行 | 配置管理、事务提交、模型驱动编程 |

netmiko 选择 CLI 路线，因为它能覆盖最广泛的设备——包括大量不支持 API 的遗留网络设备。对于需要结构化数据的场景，netmiko 通过 TextFSM 模板等方式弥补。

## 跨束参考

- [paramiko SSHClient 详解](../../paramiko/concepts/02-ssh-client.md) — netmiko 的底层 SSH 引擎
- [paramiko Channel 通道](../../paramiko/concepts/04-channel.md) — netmiko 使用 invoke_shell 建立 PTY 通道
