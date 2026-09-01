---
type: Example
title: 结构化输出解析
description: 用 textfsm_parse 把非结构化输出解析为结构化数据：单条与多条结果、ntc-templates 平台映射与自定义模板
tags: [scrapli, example, textfsm, ntc-templates, parsing, structured-data]
generated: { by: "doc_agent/trae-glm", at: "2026-08-28T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T00:00:00Z" }
status: stable
stale_after: 2027-06-30
sources:
  - id: scrapli-source
    resource: /references/scrapli-source.md
    title: scrapli2 源码信源登记
---

## 场景说明

设备返回的 CLI 输出是给人看的非结构化文本。本例使用 textfsm（可选搭配 ntc-templates）把非结构化输出解析为结构化对象——scrapli 本身并不做任何解析，只是提供了一组便捷函数，让解析调用更简单（F-021）。

官方示例位于 `examples/cli/output_parsing/`，核心 API 是 `Result` 上的 `textfsm_parse()`（F-022）。

## 安装依赖

textfsm 与 ntc-templates 是可选依赖，通过 extras 安装（F-048）：

```bash
pip install scrapli[textfsm]
```

## 解析单条结果

`send_input` 返回的结果对象上直接调用 `textfsm_parse()`。下面的代码基于 examples/cli/output_parsing/main.py 改写——由于 ntc-templates 中没有 srlinux 的模板，官方示例自带一个简易模板来演示 `template` 参数；这也说明：你的平台/命令不在 ntc-templates 中时，完全可以提供自己的模板：

```python
from pathlib import Path

from scrapli import AuthOptions, Cli

cli = Cli(
    definition_file_or_name="nokia_srlinux",
    host="172.20.20.16",
    port=22,
    auth_options=AuthOptions(
        username="admin",
        password="NokiaSrl1!",
    ),
)

with cli as c:
    result = c.send_input(input_="show version")

    print(
        result.textfsm_parse(
            template=f"{Path(__file__).resolve().parent}/nokia_srlinux_show_version.tpl",
        )
    )
```

模板文件 `nokia_srlinux_show_version.tpl`：

```text
Value HOSTNAME (\S+)
Value CHASSIS_TYPE (.+)

Start
  ^Hostname\s+:\s+${HOSTNAME}
  ^Chassis\s+Type\s+:\s+${CHASSIS_TYPE} -> Record
```

解析结果（`to_dict=True` 的默认行为，输出示意）：

```python
[{'hostname': 'srl', 'chassis_type': 'Nokia 7250 IXR-10'}]
```

### to_dict 参数

默认 `to_dict=True`，把 textfsm 的"表头 + 行"输出转成更易读的 dict；不需要这层转换时可以跳过（紧接上例，`result` 为 `send_input` 的返回值）：

```python
    print(
        result.textfsm_parse(
            template=f"{Path(__file__).resolve().parent}/nokia_srlinux_show_version.tpl",
            # normally we convert the output to a dict, but you can skip that if you want
            to_dict=False,
        )
    )
```

`to_dict=False` 时得到 textfsm 原生的"列表套列表"：

```python
[['srl', 'Nokia 7250 IXR-10']]
```

## 解析多条结果中的指定条目

`send_inputs` 返回的（复数）结果同样可以解析——用 `index` 指定解析第几条输入/结果，默认 0：

```python
from pathlib import Path

from scrapli import AuthOptions, Cli

cli = Cli(
    definition_file_or_name="nokia_srlinux",
    host="172.20.20.16",
    port=22,
    auth_options=AuthOptions(
        username="admin",
        password="NokiaSrl1!",
    ),
)

with cli as c:
    # parsing works on results that are plural too
    results = c.send_inputs(inputs=["show system lldp neighbor", "show version"])

    print(
        results.textfsm_parse(
            # 解析第 index 条输入/结果，默认 0（即第一条），按需设置
            index=1,
            template=f"{Path(__file__).resolve().parent}/nokia_srlinux_show_version.tpl",
            # normally we convert the output to a dict, but you can skip that if you want
            to_dict=False,
        )
    )
```

上面解析的是第 1 条输入（`show version`）的结果；第 0 条 `show system lldp neighbor` 保持原样。

## ntc-templates 平台映射

不传 `template` 时，scrapli 会按"平台 + 命令"在 ntc-templates 中自动查找模板（官方示例注释明示：平台定义含 `ntc_templates_platform` 字段且安装了 ntc-templates 时，模板将基于平台与输入自动查找）：

```python
from scrapli import AuthOptions, Cli

with Cli(
    host="192.168.1.1",
    definition_file_or_name="cisco_iosxe",
    auth_options=AuthOptions(username="admin", password="admin"),
) as cli:
    result = cli.send_input(input_="show version")

    # cisco_iosxe 定义了 ntc_templates_platform，无需显式传 template
    parsed = result.textfsm_parse()
```

映射链路（每一环都可在源码中验证）：

1. 内置平台 YAML 中带 `ntc_templates_platform` 字段，例如 `cisco_iosxe.yaml` 中为 `ntc_templates_platform: 'cisco_iosxe'`（F-096）
2. `Cli` 暴露只读属性 `ntc_templates_platform`（scrapli/cli.py:616-617），构造结果对象时作为 `textfsm_platform` 传入（scrapli/cli.py:1060）
3. `textfsm_parse()` 未提供 `template` 时，调用 `textfsm_get_template(platform=self.textfsm_platform, command=self.inputs[index])`（scrapli/cli_result.py:342-345）
4. `textfsm_get_template` 用 ntc-templates 的 CliTable 索引按 `{"Platform": platform, "Command": command}` 匹配并打开模板文件（scrapli/cli_parse.py:14-48）

两个异常出口需要留意：

- 未安装可选依赖：`ParsingException("optional extra 'textfsm' not found")`
- 平台/命令在 ntc-templates 中无匹配、又没提供 template：`ParsingException("no template provided or available for input")`

此外 `Result` 还提供 `genie_parse()`（Cisco genie 解析）。官方示例的调侃是：除非愿意安装"天文数字"般多的依赖包，否则别用——对应的安装方式为 `pip install scrapli[genie]`（F-048）。

## 相关概念

- [/concepts/08-advanced-patterns.md](/concepts/08-advanced-patterns.md) — 结果解析等高级模式
- [/concepts/12-repository-examples.md](/concepts/12-repository-examples.md) — 官方示例体系与 output_parsing 的位置
- [/examples/send-commands.md](/examples/send-commands.md) — TextFSM/Genie 解析速览与批量命令发送
