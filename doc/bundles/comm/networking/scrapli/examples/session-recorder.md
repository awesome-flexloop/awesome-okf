---
type: Example
title: 会话录制
description: 通过 SessionOptions 配置 recorder_path，将底层 session 的全部读取录制到文件，与 logging 调试日志互补
tags: [scrapli, example, session, recorder, logging, observability]
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

会话录制（session recorder）把底层 session 的**所有读取**记录到一个文件（F-031）。官方示例位于 `examples/cli/session_recorder/`，配置只需一步：在 `SessionOptions` 上指定 `recorder_path` 路径（F-032）。

## 配置录制路径

基于 examples/cli/session_recorder/main.py 改写：

```python
from pathlib import Path

from scrapli import AuthOptions, Cli, SessionOptions

cli = Cli(
    definition_file_or_name="nokia_srlinux",
    host="172.20.20.16",
    port=22,
    auth_options=AuthOptions(
        username="admin",
        password="NokiaSrl1!",
    ),
    # 把 recorder 指向一个写入路径，即可"录制" session——即 Zig 层那个
    # 负责向底层 transport 读写的对象所读到的全部内容
    session_options=SessionOptions(
        recorder_path=f"{Path(__file__).resolve().parent}/session_record.log",
    ),
)

with cli as c:
    # 发送点东西，让录制文件里有内容可看
    result = c.send_input(input_="show version")

    print(result)
```

运行后，`session_record.log` 记录了这次会话读到的全部内容（官方示例目录的 `.gitignore` 正是忽略了 `session_record.log`）。

## 录制的内容是什么

这里的 "session" 指 Zig 层中负责向底层 transport 读写的对象（scrapli2 的核心逻辑都在 Zig 里）。录制器抓取的是它读到的原始数据——设备真实发回的字节流，包含提示符、分页等未经清理的内容。`Result.result` 是清理后的输出，录制文件则保留会话的"原貌"，适合事后审计、取证或离线分析。

一个已知边界（源自官方示例注释）：录制几乎总会错过结尾的 "exit"/"quit"——设备关闭会话后读取循环随即终止，而那正是录制器收集数据的位置。

## 与日志的区别

会话录制不等于日志。官方 `logging_setup` 示例演示的是标准 Python logging 的配置方式（F-017、F-018）——没有任何特殊魔法，就像普通 Python 程序一样挂一个 logging handler：

```python
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

from scrapli import AuthOptions, Cli

with Cli(
    definition_file_or_name="nokia_srlinux",
    host="172.20.20.16",
    port=22,
    auth_options=AuthOptions(username="admin", password="NokiaSrl1!"),
) as c:
    result = c.send_input(
        input_="show version",
        retain_trailing_prompt=True,
    )

    print(result.result)
```

两者定位不同：

| 维度 | 会话录制（recorder） | 日志（logging） |
|------|--------------------|----------------|
| 捕获内容 | 底层 session 的原始读取（设备真实输出） | 库自身的运行事件与调试信息 |
| 配置方式 | `SessionOptions(recorder_path=...)` | 标准 `logging.basicConfig(...)` |
| 典型用途 | 会话审计、离线回放、取证 | 排障、观察内部状态与超时行为 |
| 粒度控制 | 无（全量录制） | DEBUG/INFO/… 分级（trace 级用 `logging.NOTSET`） |

若需要 "trace" 级别的日志，`logging_setup` 示例特别说明：使用 `logging.NOTSET` 级别。

官方示例体系中，`logging_setup` 与 `session_recorder` 被并称为可观测性两件套——一个向内看库的行为，一个向外看设备的回应。

## 相关概念

- [/concepts/03-auth-session.md](/concepts/03-auth-session.md) — SessionOptions 全部字段与认证、会话配置
- [/concepts/12-repository-examples.md](/concepts/12-repository-examples.md) — 官方示例体系与可观测性两件套的定位
- [/examples/custom-driver.md](/examples/custom-driver.md) — 自定义平台定义示例中的会话录制速览
