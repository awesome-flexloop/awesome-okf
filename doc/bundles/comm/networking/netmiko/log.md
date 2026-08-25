# netmiko 知识包生成日志

## R 阶段（事实采集）

- 读取任务简报：`.trae/specs/ssh-python-okf-wiki/netmiko-task-brief.md`
- 参考格式范例：`projects/awesome-okf-xs/bundles/networking/paramiko/index.md`
- 逐模块阅读 netmiko v4.7.0 源码（`external/libs/netmiko/netmiko/`）：
  - `__init__.py` — 版本、导出、Python 版本检查
  - `ssh_dispatcher.py` — ConnectHandler 工厂、CLASS_MAPPER_BASE/CLASS_MAPPER、FILE_TRANSFER_MAP、platforms、redispatch、ssh_dispatcher、FileTransfer 工厂、TelnetFallback/ConnLogOnly/ConnUnify
  - `base_connection.py` — BaseConnection 核心基类（连接生命周期、命令执行、配置管理、输出处理）
  - `ssh_autodetect.py` — SSHDetect 类、SSH_MAPPER_DICT 指纹库、三种探测方法
  - `exceptions.py` — 异常层次体系
  - `cisco_base_connection.py` — CiscoBaseConnection、CiscoSSHConnection、CiscoFileTransfer
  - `scp_handler.py` — SCPConn、BaseFileTransfer
  - `scp_functions.py` — file_transfer、progress_bar、verifyspace_and_transferfile
  - `no_enable.py`、`no_config.py` — Mixin 类
  - `utilities.py` — 工具函数索引（structured_data_converter 等）
- 采样5个厂商驱动：
  - `cisco/cisco_ios.py` — CiscoIosBase/CiscoIosSSH/CiscoIosTelnet/CiscoIosSerial/InLineTransfer
  - `arista/arista.py` — AristaBase/AristaSSH
  - `juniper/juniper.py` — JuniperBase/JuniperSSH（含 commit 方法）
  - `linux/linux_ssh.py` — LinuxSSH
  - `hp/hp_comware.py` — HPComwareBase
- 提取 **120 条**编号事实（F-001~F-120），输出至 `.trae/specs/ssh-python-okf-wiki/netmiko-facts.md`

## I 阶段（架构洞察）

- 提炼 **5 个核心架构洞察**，输出至 `.trae/specs/ssh-python-okf-wiki/netmiko-insights.md`：
  1. ConnectHandler 工厂 + CLASS_MAPPER 字典驱动的多厂商架构（注册表模式）
  2. BaseConnection 模板方法模式——连接生命周期骨架
  3. 三种命令发送模式的分层设计（模式匹配 vs 延迟驱动）
  4. SSHDetect 自动探测——命令输出指纹匹配
  5. 基于 paramiko 的 CLI screen-scraping 模型
- 设计知识地图：入门(2篇) → 核心(4篇) → 架构进阶(4篇)，共 10 篇概念文档

## E 阶段（批量生成）

### Step 1: 创建目录结构
- `bundles/networking/netmiko/concepts/`
- `bundles/networking/netmiko/examples/`
- `bundles/networking/netmiko/references/`

### Step 2: 生成信源登记簿
- `references/netmiko-source.md`

### Step 3: 生成概念文档（10篇）
- `concepts/00-introduction.md` — netmiko 简介
- `concepts/01-getting-started.md` — 5分钟快速上手
- `concepts/02-connect-handler.md` — ConnectHandler 工厂
- `concepts/03-base-connection.md` — BaseConnection 核心
- `concepts/04-command-execution.md` — 命令执行
- `concepts/05-config-mgmt.md` — 配置管理
- `concepts/06-driver-hierarchy.md` — 驱动继承体系
- `concepts/07-ssh-autodetect.md` — SSH 自动探测
- `concepts/08-file-transfer.md` — SCP 文件传输
- `concepts/09-advanced-patterns.md` — 高级模式

### Step 4: 生成示例文档（4篇）
- `examples/multi-vendor-connect.md`
- `examples/send-commands.md`
- `examples/config-changes.md`
- `examples/output-parsing-textfsm.md`

### Step 5: 生成索引文件
- `concepts/index.md`
- `examples/index.md`
- `references/index.md`
- `index.md`（根索引）
- `log.md`（本文件）

## V 阶段（Grep 验证）

在 `external/libs/netmiko/netmiko/` 中对所有类名、方法名、函数名进行 Grep 验证，确保无虚构 API。验证清单见任务简报。

## 统计

- 事实数：120 条
- 概念文档：10 篇
- 示例文档：4 篇
- 信源登记：1 篇
- 索引文件：4 篇
- 总文档数：19 个文件（含 log.md）
- 跨束引用：paramiko（`../../paramiko/concepts/`）
