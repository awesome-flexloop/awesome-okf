---
type: category
title: "TokenEconomizer 实战示例"
description: "两篇检查清单式示例：安装验证与状态观测；均为官方文档转述，本束未实测"
status: stable
stale_after: 2027-02-28
generated: { by: "reference_agent", at: "2026-11-17T12:45:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-17T12:45:00+08:00" }
sources:
  - id: repo
    resource: https://github.com/microsoft/TokenEconomizer
---

# 实战示例

> **⚠️ 两篇均为「官方文档转述 + 检查清单」，不是运行记录**。本束未安装插件、未采集真实输出。之所以仍设 `examples/`，是因为本知识包有明确的官方安装命令、状态命令与可复现 harness（`experiments/`），操作可复现性两问中至少一问成立；这与同域「纯资讯解读束不设 examples」的处理不同。

| 想做什么 | 阅读 |
|---|---|
| 装上插件、确认信任与 hooks 生效、避开版本坑 | [安装与验证](01-install-and-verify.md) |
| 读 status / config、按全栈对齐、观测活动计数 | [读状态、调参与观测](02-status-and-tuning.md) |

```{toctree}
:hidden:
:maxdepth: 2

01-install-and-verify
02-status-and-tuning
```
