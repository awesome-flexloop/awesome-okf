---
type: Concept
title: 平台定义分类目录
description: scrapli/definitions/ 下 44 个平台 YAML 的厂商分类全景、共性字段、从 9 行到 88 行的复杂度谱系与加载覆盖机制
tags: [scrapli, platform, definitions, catalog, yaml]
generated: { by: "doc_agent/trae-glm", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T00:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
    title: scrapli2 源码信源登记
---

`scrapli/definitions/` 目录以纯 YAML 承载全部平台适配——目录中共 44 个 YAML 文件（含 `default.yaml` 兜底定义），另有 `__init__.py` 使其成为可被 `importlib.resources` 加载的包资源。本文给出 44 个定义的厂商分类全景、共性结构与复杂度谱系；字段语义与模式层级详见[平台定义系统](/concepts/06-platform-definitions.md)。

## 完整平台清单

按厂商归类，43 个平台定义 + 1 个 `default.yaml` 兜底定义，共 44 个 YAML：

| 厂商 | 数量 | 平台文件名 |
|------|------|-----------|
| Cisco | 7 | cisco_iosxe, cisco_iosxr, cisco_nxos, cisco_asa, cisco_aireos, cisco_cbs, cisco_ftd |
| Nokia | 4 | nokia_srlinux, nokia_sros, nokia_sros_classic, nokia_sros_classic_aram |
| Aruba | 2 | aruba_aoscx, aruba_wlc |
| Fortinet | 2 | fortinet_fortios, fortinet_wlc |
| Cumulus | 2 | cumulus_linux, cumulus_vtysh |
| Datacom | 2 | datacom_dmos, datacom_dmswitch |
| Dell | 2 | dell_emc, dell_enterprisesonic |
| Ruckus | 2 | ruckus_fastiron, ruckus_unleashed |
| Huawei | 2 | huawei_vrp, huawei_smartax |
| Arista | 1 | arista_eos |
| Juniper | 1 | juniper_junos |
| MikroTik | 1 | mikrotik_routeros |
| Palo Alto | 1 | paloalto_panos |
| HPE | 1 | hp_comware |
| VyOS | 1 | vyos_vyos |
| Aethra | 1 | aethra_atosnt |
| Alcatel | 1 | alcatel_aos |
| D-Link | 1 | dlink_os |
| Edgecore | 1 | edgecore_ecs |
| Eltex | 1 | eltex_esr |
| IP Infusion | 1 | ipinfusion_ocnos |
| Raisecom | 1 | raisecom_ros |
| Ruijie | 1 | ruijie_rgos |
| Siemens | 1 | siemens_roxii |
| Ubiquiti | 1 | ubiquiti_edgeswitch |
| Versa | 1 | versa_flexvnf |
| Zyxel | 1 | zyxel_dslam |
| （兜底） | 1 | default |

## 共性结构

绝大多数平台定义由以下顶层字段组合而成：

| 字段 | 说明 |
|------|------|
| `prompt_pattern` | 全局提示符正则（兜底匹配） |
| `default_mode` | 连接后默认所在模式名称 |
| `modes` | 模式定义列表（name/prompt_pattern/accessible_modes） |
| `failure_indicators` | 失败指示器字符串列表，匹配时 Result.failed=True |
| `on_open_instructions` | 连接打开后自动执行的指令（常见：进默认模式、关分页） |
| `on_close_instructions` | 连接关闭前自动执行的指令（常见：回默认模式、`exit`） |
| `prompt_excludes` | 排除匹配的字符串列表（可选，消歧相近提示符） |
| `ntc_templates_platform` | ntc-templates 平台名（TextFSM 解析用） |
| `genie_platform` | genie 平台名（Genie 解析用） |

并非每个平台都用齐全部字段——`mikrotik_routeros.yaml` 只用前三个加关闭指令，`ntc_templates_platform`/`genie_platform` 也只在部分平台（如 cisco_iosxe、cisco_nxos、juniper_junos、huawei_vrp）中出现。指令类型（`send_input`/`send_prompted_input`/`enter_mode`/`write`）与 `__lookup::` 模板变量的语义见[平台定义系统](/concepts/06-platform-definitions.md)。

## 复杂度谱系

44 个定义覆盖从 9 行到 88 行的复杂度谱系，体现"声明式定义按需伸缩"的设计。

### 最小可用：mikrotik_routeros.yaml（9 行）

```yaml
---
prompt_pattern: '\[[a-z0-9@.\-_+\s]{1,48}@[a-z0-9.\-_\s]{1,64}\].{1,16}>'
default_mode: 'cli'
modes:
  - name: 'cli'
    prompt_pattern: '\[[a-z0-9@.\-_+\s]{1,48}@[a-z0-9.\-_\s]{1,64}\].{1,16}>'
on_close_instructions:
  - write:
      input: 'quit'
```

只有一个 `cli` 模式，关闭时写 `quit`。RouterOS 的"怪癖"（用户名加 `+tc` 后缀、`\r\n` 回车符）无法用 YAML 表达，由下文的 Python 钩子补齐。

### 多模式与升降级密码：juniper_junos.yaml（88 行）

定义 exec、configuration、configuration_exclusive、configuration_private、shell、root_shell 六个模式。亮点包括：

- `root_shell` 通过 `send_prompted_input`（prompt_pattern 匹配 `^[pP]assword:\s?$`，响应用 `__lookup::root`）走密码升级
- `shell` 模式以 `prompt_excludes: ['root']` 与 `root_shell` 的提示符区分
- `failure_indicators` 含 'is ambiguous'、'unknown command'、'syntax error' 等六项
- on_open 依次执行 `set cli screen-width 511`、`set cli screen-length 0`、`set cli complete-on-space off`
- 声明 `ntc_templates_platform: 'juniper_junos'`

### 解析器集成：cisco_nxos.yaml

exec、privileged_exec、configuration、tclsh 四个模式之外，同时声明 `ntc_templates_platform: 'cisco_nxos'` 与 `genie_platform: 'nxos'`，把平台目录与结构化解析器（TextFSM/Genie）关联起来。

### write 指令的容错用法：huawei_vrp.yaml

configuration 模式的 prompt 正则用负向前瞻排除 `[V200R009C00SPC500]` 式版本字符串（防止 `display current-configuration` 输出被误判为提示符）。on_open 指令刻意用 `write` 而非 `send_input` 发送：

```yaml
on_open_instructions:
  - enter_mode:
      requested_mode: 'privileged_exec'
  - write:
      # Attempt to set screen width as a fallback in case the device does not accept the
      # ptyprocess/cols property when using system transport (observed on some firmware versions).
      input: 'screen-width 255\ny\n\n'
```

`screen-width` 指令在部分老版本设备上不存在、部分设备会追问 Y/N——`write` 不等待结果，设备不认该命令时静默失败，兼容多固件行为。

### 控制台重配置：fortinet_fortios.yaml（20 行）

on_open 通过 `config system console` → `set output standard` → `end` 三连指令重设 FortiOS 控制台输出格式，再走常规的进模式与退出流程。

### prompt_excludes 消歧：nokia_srlinux.yaml

SR Linux 的 bash 模式与 exec/configuration 提示符形状相近，bash 模式以 `prompt_excludes: ['--{']` 排除 SR Linux 风格提示符，避免模式误判；on_open 执行 `environment cli-engine type basic` 与 `environment complete-on-space false`。

## 加载机制与覆盖

`Cli._process_definition_file_or_name()` 接受三种形态的 `definition_file_or_name`：

- **`LoadedDefinition` 对象**：直接使用其 `platform_name` 与 `definition` 字符串，不再查盘
- **平台名**（如 `"cisco_iosxe"`）：走 `_load_definition()` 查找
- **文件路径**（如 `/path/to/my.yaml`）：按文件系统路径加载，`_platform_name` 取文件名去后缀

`_load_definition()` 的查找顺序：

1. 设置了环境变量 `SCRAPLI_DEFINITIONS_PATH` 时（读入常量 `CLI_DEFINITIONS_PATH_OVERRIDE`），优先从该目录加载 `{name}.yaml`
2. 否则从 `scrapli.definitions` 包资源目录加载内置定义
3. 内置未命中时，把入参当作文件路径尝试加载
4. 以上均失败抛出 `OptionsException`

不传 `definition_file_or_name` 时落到 `default.yaml`——只有一条 `'^.*[>#$]\s?+$'` 提示符正则、单 `cli` 模式和 `exit` 关闭指令的通用兜底。迁移自旧版 scrapli 时，旧的 scrapli community 平台定制已由这套 YAML definitions 取代（详见[迁移指南](/concepts/11-migration.md)）。

## 平台专属 Python 钩子

YAML 无法表达的"怪癖"由 `scrapli/definition_options/` 下的 Python 扩展补齐。当前仅有 `mikrotik_routeros.py`：

```python
def mikrotik_routeros_post_init(c: Cli) -> None:
    c.auth_options.username = f"{c.auth_options.username}+tc"
    c.session_options.return_char = "\r\n"
```

`Cli.__init__` 末尾尝试 `import_module(f"scrapli.definition_options.{self._platform_name}")` 并调用 `{platform_name}_post_init(c)`——模块不存在时静默跳过（并非每个平台都有钩子）。可用 `skip_static_options=True` 跳过这一步。RouterOS 的 `+tc` 用户名后缀用于切换设备的完整终端行为，这类逻辑只能在代码层完成。

## 相关概念

- [平台定义系统](/concepts/06-platform-definitions.md) — YAML 字段语义、模式层级与指令类型详解
- [自定义驱动示例](/examples/custom-driver.md) — 用自定义 YAML 接入未内置平台的实践
- [迁移指南](/concepts/11-migration.md) — scrapli community 被 definitions 取代的背景
