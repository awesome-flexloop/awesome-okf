---
okf_version: "0.2"
---

# netmiko 知识库

本知识包是多厂商网络设备 SSH/Telnet CLI 自动化库 [netmiko](https://github.com/ktbyers/netmiko)（v4.7.0）的系统化中文教程，基于源码深度阅读生成，覆盖从快速上手到高级模式的完整知识体系。所有内容均溯源至 netmiko 源码（`netmiko/` 包核心模块），遵循 [OKF v0.2 规范](/concepts/00-introduction.md)。

netmiko 基于 [paramiko](../paramiko/concepts/00-introduction.md) 构建，通过 PTY 交互式 shell 和 CLI screen-scraping 模型统一管理 100+ 种网络平台。

## 入门与基础（concepts/）

* [netmiko 简介](concepts/00-introduction.md) — 多厂商网络设备 SSH 自动化库、设计哲学、CLI vs API。
* [5分钟快速上手](concepts/01-getting-started.md) — 从安装到第一个连接、执行命令、关闭连接。

## 核心概念（concepts/）

* [ConnectHandler 工厂](concepts/02-connect-handler.md) — 工厂函数、CLASS_MAPPER 注册表、ssh_dispatcher、redispatch 动态切换。
* [BaseConnection 核心](concepts/03-base-connection.md) — 连接生命周期、session_preparation、disable_paging、终端设置。
* [命令执行](concepts/04-command-execution.md) — send_command/send_command_timing/send_command_expect 三种模式、read_timeout、expect_string。
* [配置管理](concepts/05-config-mgmt.md) — send_config_set/send_config_from_file、enable/config 模式、save_config、commit。

## 架构与进阶（concepts/）

* [驱动继承体系](concepts/06-driver-hierarchy.md) — BaseConnection→CiscoBaseConnection→厂商驱动、NoEnable/NoConfig Mixin。
* [SSH 自动探测](concepts/07-ssh-autodetect.md) — SSHDetect 指纹匹配自动识别设备类型。
* [SCP 文件传输](concepts/08-file-transfer.md) — FileTransfer/SCPConn/file_transfer、MD5 校验、verify_space。
* [高级模式](concepts/09-advanced-patterns.md) — session_log、global_delay_factor、TextFSM/Genie 解析、异常处理、并发连接。

## 实战示例（examples/）

* [多厂商设备连接](examples/multi-vendor-connect.md) — Cisco/Arista/Juniper/Linux/HP Comware 统一连接。
* [命令执行模式对比](examples/send-commands.md) — 三种命令发送方式的使用场景和参数。
* [批量配置变更](examples/config-changes.md) — send_config_set、配置文件、多设备并发、Juniper commit、回滚。
* [TextFSM 输出解析](examples/output-parsing-textfsm.md) — use_textfsm、ntc-templates、TTP、Genie 结构化输出。

## 信源登记簿（references/）

* [netmiko 源码信源登记](references/netmiko-source.md) — netmiko v4.7.0 源码路径、版本、核心模块清单与公开 API。

## 信任与生命周期说明

* **status 判定依据**：全部 15 个内容文档（10 个概念 + 4 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 netmiko 源码（`external/libs/netmiko/netmiko/` 目录）核心模块的逐模块阅读与事实提取（120 条源码事实），经 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-06-30`。网络设备驱动迭代较快，厂商 CLI 输出格式和新增平台可能导致部分内容需要更新；该日期作为针对 netmiko 大版本升级和新平台支持的重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-23）；`verified.at` 记录 V 阶段 Grep 验证事件（2026-08-23），两者分离、可追溯。

本知识包共收录 15 个内容文档（10 个概念 + 4 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
