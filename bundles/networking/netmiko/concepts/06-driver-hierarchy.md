---
type: Concept
title: 驱动继承体系
description: BaseConnection → CiscoBaseConnection → 厂商驱动的继承层次，Cisco/Arista/Juniper/Linux/HP 对比
tags: [netmiko, driver, inheritance, hierarchy, vendor]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: netmiko-source
    resource: /references/netmiko-source.md
---

# 驱动继承体系

netmiko 的多厂商支持建立在精心设计的类继承层次之上。`BaseConnection` 是所有驱动的根类，`CiscoBaseConnection` 是 Cisco 风格设备的中间基类，大量厂商驱动直接或间接继承它。

## 继承层次总览

```
BaseConnection
├── CiscoBaseConnection
│   ├── CiscoSSHConnection (= CiscoBaseConnection)
│   │   ├── CiscoIosBase
│   │   │   ├── CiscoIosSSH
│   │   │   ├── CiscoIosTelnet
│   │   │   └── CiscoIosSerial
│   │   ├── AristaBase
│   │   │   ├── AristaSSH
│   │   │   └── AristaTelnet
│   │   ├── LinuxSSH
│   │   ├── HPComwareBase
│   │   │   ├── HPComwareSSH
│   │   │   └── HPComwareTelnet
│   │   └── ... (HP Procurve, Huawei, Dell, 等)
│   ├── CiscoAsaSSH
│   ├── CiscoNxosSSH
│   ├── CiscoXrSSH
│   └── ...
├── JuniperBase(NoEnable, BaseConnection)
│   ├── JuniperSSH
│   └── JuniperTelnet
└── TerminalServerSSH
```

注意：Juniper 不继承 CiscoBaseConnection，而是直接继承 `BaseConnection` 并混入 `NoEnable`。

## BaseConnection（根基类）

`BaseConnection` 定义了所有驱动共有的接口和默认实现：

- **连接管理**：`establish_connection()`, `disconnect()`, `_open()`, `is_alive()`
- **会话准备**：`session_preparation()`, `set_base_prompt()`, `disable_paging()`, `set_terminal_width()`
- **命令执行**：`send_command()`, `send_command_timing()`, `send_command_expect()`, `send_config_set()`
- **模式管理**：`enable()`, `config_mode()`, `check_enable_mode()`, `check_config_mode()`
- **输出处理**：`strip_prompt()`, `strip_command()`, `normalize_linefeeds()`, `strip_ansi_escape_codes()`
- **文件传输钩子**：`_enter_shell()`, `_return_cli()`, `_autodetect_fs()`（均为 NotImplementedError）
- **保存/提交**：`save_config()`（NotImplementedError）, `commit()`（AttributeError）

## CiscoBaseConnection（Cisco 风格基类）

`CiscoBaseConnection` 为 Cisco 风格 CLI 提供默认值：

| 方法 | 默认值/行为 |
|------|------------|
| `enable()` cmd | `"enable"` |
| `enable()` pattern | `"ssword"` |
| `exit_enable_mode()` | `"disable"` |
| `check_enable_mode()` | `"#"` |
| `config_mode()` | `"configure terminal"` |
| `exit_config_mode()` | `"end"`, pattern `r"#.*"` |
| `check_config_mode()` | `")#"` |
| `disable_paging()` | `"terminal length 0"` |
| `save_config()` | `"copy running-config startup-config"` |
| `cleanup()` | 发送 `"exit"` |
| `_autodetect_fs()` | 使用 `"dir"` 命令检测文件系统 |

`CiscoSSHConnection` 是 `CiscoBaseConnection` 的空子类（`pass`），作为 SSH 驱动的语义别名。

## Cisco IOS 驱动

`CiscoIosBase` 重写了以下行为：

```python
class CiscoIosBase(CiscoBaseConnection):
    def session_preparation(self):
        # 顺序与基类不同：先设宽度，再禁分页，最后设提示符
        self.set_terminal_width(command="terminal width 511", pattern=cmd)
        self.disable_paging()
        self.set_base_prompt()

    def set_base_prompt(self, ...):
        # IOS 在配置模式下缩写提示符到20字符，因此 base_prompt 截断为16字符
        base_prompt = super().set_base_prompt(...)
        self.base_prompt = base_prompt[:16]

    def save_config(self, cmd="write mem", ...):
        # IOS 传统上使用 "write memory" 而非 "copy run start"
        return super().save_config(cmd=cmd, ...)
```

`CiscoIosSSH`, `CiscoIosTelnet`, `CiscoIosSerial` 均为空类，仅通过 `device_type` 区分协议。

## Arista EOS 驱动

`AristaBase(CiscoSSHConnection)` 的差异：

- `session_preparation()` 启用 `ansi_escape_codes = True`（EOS 输出含 ANSI 码）
- 使用自定义 `prompt_pattern = r"[$>#]"`
- `disable_paging()` 使用 `pattern=r"Pagination disabled"`
- `check_config_mode()` 去除 `(s1)`/`(s2)` 会话标识后检查
- `config_mode()` 使用 `re.DOTALL` 标志匹配跨行提示符
- `enable()` 增加 `enable_pattern=r"\#"` 验证

## Juniper Junos 驱动

`JuniperBase(NoEnable, BaseConnection)` 是最显著的非 Cisco 风格驱动：

- 混入 `NoEnable`（Junos 无 enable 概念）
- `session_preparation()` 需要先从 shell 进入 CLI（`enter_cli_mode()`）
- 使用 `set cli screen-width 511` 和 `set cli screen-length 0`
- 还需 `set cli complete-on-space off` 禁用空格补全
- `config_mode()` 命令为 `"configure"`，pattern 匹配 `Entering configuration mode`
- `exit_config_mode()` 命令为 `"exit configuration-mode"`，处理未提交变更确认
- 实现了 `commit()` 方法（支持 confirm/check/comment/and_quit）
- `check_config_mode()` 使用 `"]"` 而非 `)#`

## Linux 驱动

`LinuxSSH(CiscoSSHConnection)` 虽然继承了 Cisco 基类，但大幅调整：

- `disable_paging()` 为空操作（Linux 默认无分页）
- `session_preparation()` 不设置终端宽度
- `config_mode()` 使用 `"sudo -s"` 提权（映射到 enable 逻辑）
- `check_config_mode()` 映射到 `check_enable_mode()`（root 提示符 `#`）
- `exit_config_mode()` 映射到 `exit_enable_mode()`（发送 `"exit"`）
- root 用户不退出配置模式
- 提示符支持环境变量 `NETMIKO_LINUX_PROMPT_PRI`/`ALT`/`ROOT` 自定义

## HP Comware 驱动

`HPComwareBase(CiscoSSHConnection)` 的特点：

- 构造函数默认禁用 `global_cmd_verify`（Comware 无法设置终端宽度导致回显验证问题）
- `session_preparation()` 处理 "Press Y or ENTER to continue" 横幅
- `disable_paging()` 使用 `"screen-length disable"`
- `config_mode()` 命令为 `"system-view"`
- `exit_config_mode()` 命令为 `"return"`，pattern 为 `">"`
- `check_config_mode()` 使用 `"]"` 标识
- `send_config_set()` terminator 为 `r"\]"` 而非 `"#"`

## Mixin 设计模式

netmiko 使用 mixin 处理正交的行为变体：

### NoEnable

```python
class NoEnable:
    def check_enable_mode(self, check_string=""):
        return True  # 始终视为在特权模式
    def enable(self, ...):
        return ""    # 空操作
    def exit_enable_mode(self, ...):
        return ""
```

Juniper Junos 使用此 mixin，因为 Junos 的权限模型基于用户登录权限而非 enable 密码。

### NoConfig

```python
class NoConfig:
    def check_config_mode(self, ...):
        return True
    def config_mode(self, ...):
        return ""
    def exit_config_mode(self, ...):
        return ""
```

适用于配置命令可直接执行的设备（如终端服务器）。

## 驱动注册

每个驱动类通过 `CLASS_MAPPER_BASE` 字典注册到一个或多个 device_type 字符串：

```python
CLASS_MAPPER_BASE = {
    "cisco_ios": CiscoIosSSH,
    "cisco_xe": CiscoIosSSH,      # IOS XE 使用相同驱动
    "cisco_ioswlc": CiscoIosSSH, # WLC 也使用 IOS 驱动
    "arista_eos": AristaSSH,
    "juniper": JuniperSSH,
    "juniper_junos": JuniperSSH,
    "linux": LinuxSSH,
    "hp_comware": HPComwareSSH,
    "h3c_comware": HPComwareSSH,
    ...
}
```

多个 device_type 可以映射到同一个驱动类，实现平台别名。
