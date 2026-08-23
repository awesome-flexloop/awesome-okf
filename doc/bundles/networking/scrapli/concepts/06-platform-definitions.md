---
type: Concept
title: 平台定义系统
description: YAML 声明式平台定义、LoadedDefinition、44个内置平台、模式层级、自定义定义
tags: [scrapli, platform, yaml, definitions, modes, prompt]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:grep-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
---

# 平台定义系统

scrapli2 使用 YAML 声明式文件定义网络设备的提示符模式、模式层级和自动化指令，替代了旧版 scrapli 中庞大的 Python 类继承体系。

## 内置平台

`definitions/` 目录包含 44 个 YAML 平台定义：

| 厂商 | 平台文件名 |
|------|-----------|
| Cisco | cisco_iosxe, cisco_iosxr, cisco_nxos, cisco_asa, cisco_aireos, cisco_cbs, cisco_ftd |
| Arista | arista_eos |
| Juniper | juniper_junos |
| Huawei | huawei_vrp, huawei_smartax |
| Fortinet | fortinet_fortios, fortinet_wlc |
| Palo Alto | paloalto_panos |
| Nokia | nokia_srlinux, nokia_sros, nokia_sros_classic, nokia_sros_classic_aram |
| MikroTik | mikrotik_routeros |
| Aruba | aruba_aoscx, aruba_wlc |
| Dell | dell_emc, dell_enterprisesonic |
| HPE | hp_comware |
| Cumulus | cumulus_linux, cumulus_vtysh |
| VyOS | vyos_vyos |
| 其他 | aethra_atosnt, alcatel_aos, datacom_dmos, datacom_dmswitch, dlink_os, edgecore_ecs, eltex_esr, ipinfusion_ocnos, raisecom_ros, ruckus_fastiron, ruckus_unleashed, ruijie_rgos, siemens_roxii, ubiquiti_edgeswitch, versa_flexvnf, zyxel_dslam |

另外还有 `default.yaml` 提供通用默认定义。

## YAML 定义结构

以 Cisco IOS-XE 为例：

```yaml
---
prompt_pattern: '^\S{1,63}[>#$]\s?+$'
default_mode: 'privileged_exec'

modes:
  - name: 'exec'
    prompt_pattern: '^[\w.\-@/:]{1,63}>\s?+$'
    accessible_modes:
      - name: 'privileged_exec'
        instructions:
          - send_prompted_input:
              input: 'enable'
              prompt_exact: 'Password:'
              response: '__lookup::enable'

  - name: 'privileged_exec'
    prompt_pattern: '^[\w.\-@/:]{1,63}#\s?+$'
    accessible_modes:
      - name: 'exec'
        instructions:
          - send_input:
              input: 'disable'
      - name: 'configuration'
        instructions:
          - send_input:
              input: 'configure terminal'

  - name: 'configuration'
    prompt_pattern: '^[\w.\-@/:]{1,63}\([\w.\-@/:+]{0,32}\)#\s?+$'
    accessible_modes:
      - name: 'privileged_exec'
        instructions:
          - send_input:
              input: 'end'

failure_indicators:
  - '% Ambiguous command'
  - '% Incomplete command'
  - '% Invalid input detected'
  - '% Unknown command'
  - 'Command authorization failed'

on_open_instructions:
  - enter_mode:
      requested_mode: 'privileged_exec'
  - send_input:
      input: 'term width 512'
  - send_input:
      input: 'term len 0'

on_close_instructions:
  - enter_mode:
      requested_mode: 'privileged_exec'
  - write:
      input: 'exit'

ntc_templates_platform: 'cisco_iosxe'
genie_platform: 'iosxe'
```

### 顶层字段

| 字段 | 说明 |
|------|------|
| `prompt_pattern` | 全局提示符正则（兜底匹配） |
| `default_mode` | 连接后默认所在模式名称 |
| `modes` | 模式定义列表 |
| `failure_indicators` | 失败指示器字符串列表，匹配时标记 Result.failed=True |
| `on_open_instructions` | 连接打开后自动执行的指令 |
| `on_close_instructions` | 连接关闭前自动执行的指令 |
| `ntc_templates_platform` | ntc-templates 平台名（用于 TextFSM 解析） |
| `genie_platform` | genie 平台名（用于 Genie 解析） |

### 模式定义

每个模式包含：

- `name`：模式唯一标识
- `prompt_pattern`：该模式的提示符正则
- `prompt_excludes`：排除匹配的字符串列表（可选）
- `accessible_modes`：可切换到的其他模式及切换指令

### 指令类型

`instructions` 和 `on_open_instructions`/`on_close_instructions` 支持以下指令：

- `send_input`：发送命令并等待结果
- `send_prompted_input`：发送命令并响应后续提示符（如 enable 密码）
- `enter_mode`：切换到指定模式
- `write`：写入文本（不等待完整操作结果）

## 默认定义

`default.yaml` 提供最简化的通用定义：

```yaml
---
prompt_pattern: '^.*[>#$]\s?+$'
default_mode: 'cli'
modes:
  - name: 'cli'
    prompt_pattern: '^.*[>#$]\s?+$'
on_close_instructions:
  - write:
      input: 'exit'
```

不指定 `definition_file_or_name` 时使用此默认定义。

## 模板变量查找

平台定义支持 `__lookup::key_name` 语法，从 `AuthOptions.lookups` 列表中查找值：

```yaml
response: '__lookup::enable'
```

对应 Python 代码：

```python
AuthOptions(
    username="admin",
    password="login_pass",
    lookups=[
        LookupKeyValue(key="enable", value="enable_pass"),
    ],
)
```

这使得敏感信息（如 enable 密码）不必硬编码在 YAML 文件中。

## 加载机制

`Cli._load_definition()` 按以下顺序查找定义：

1. **环境变量覆盖**：如果设置了 `SCRAPLI_DEFINITIONS_PATH`，从该目录加载 `{name}.yaml`
2. **内置定义**：从 `scrapli.definitions` 包资源目录加载
3. **文件路径**：将 `definition_file_or_name` 作为文件系统路径加载
4. **失败**：以上均未找到时抛出 `OptionsException`

也可通过 `LoadedDefinition` 直接传入已加载的定义字符串：

```python
from scrapli import Cli, LoadedDefinition

my_def = LoadedDefinition(
    platform_name="my_platform",
    definition="""
---
prompt_pattern: '^.*[>#$]\\s?+$'
default_mode: 'cli'
modes:
  - name: 'cli'
    prompt_pattern: '^.*[>#$]\\s?+$'
""",
)

cli = Cli(host="192.168.1.1", definition_file_or_name=my_def)
```

## 平台特定 Python 钩子

对于 YAML 无法表达的平台"怪癖"，`definition_options/` 目录提供 Python 钩子。当前仅有 `mikrotik_routeros.py`：

```python
def mikrotik_routeros_post_init(c: Cli) -> None:
    c.auth_options.username = f"{c.auth_options.username}+tc"
    c.session_options.return_char = "\r\n"
```

钩子函数命名规则为 `{platform_name}_post_init(c: Cli)`，在 `Cli.__init__` 中通过 `importlib.import_module` 动态加载并执行。可通过 `skip_static_options=True` 跳过。

## 运行时替换定义

`replace_definition()` 方法可在连接建立后切换平台定义：

```python
with Cli(host="...", definition_file_or_name="cisco_iosxe") as cli:
    cli.send_input("show version")
    cli.replace_definition("cisco_iosxr")
    cli.send_input("show version")
```

这会更新 Zig 层的提示符模式和模式配置，适用于设备在会话中切换操作系统上下文的场景。

## 创建自定义平台定义

创建自定义 YAML 文件即可添加新平台支持，无需修改 Python 代码：

```yaml
---
prompt_pattern: '^.*[>#$]\s?+$'
default_mode: 'cli'
modes:
  - name: 'cli'
    prompt_pattern: '^.*[>#$]\s?+$'
failure_indicators:
  - 'Error:'
  - 'Invalid command'
on_open_instructions:
  - send_input:
      input: 'set cli screen-length 0'
on_close_instructions:
  - write:
      input: 'exit'
```

使用时传入文件路径：

```python
cli = Cli(
    host="192.168.1.1",
    definition_file_or_name="/path/to/my_device.yaml",
    auth_options=AuthOptions(username="admin", password="admin"),
)
```
