---
okf_version: "0.2"
type: concept-nav
title: 概念知识地图
description: "《嵌入式周报·第三期》概念导航——AI 设计芯片、边缘 AI NPU、Zephyr RTOS 生态、RISC-V 软件栈、社区硬件五条学习路径"
tags: [概念导航, 嵌入式, openTPU, Zephyr, RISC-V, 边缘AI]
generated:
  by: "seven-concepts-cmd"
  at: "2026-10-13T13:20:00+08:00"
status: draft
stale_after: 2027-04-30
---

# 概念知识地图

本包从《嵌入式周报·第三期》（2026-10-05~11 覆盖）提炼五条知识路径，按"现象事实 → 机制原理 → 工程判断"三层组织。阅读顺序建议按序号 00→04。

| 路径 | 概念 | 核心问题 | 对应 F |
|------|------|---------|--------|
| 00 | [openTPU：让 AI agent 去设计一颗跑 AI 的芯片](00-ai-designed-chip.md) | AI 设计硬件为何能可复现？验证如何成为架构问题？ | F-001~F-011 |
| 01 | [NPU 下沉：边缘 AI 从特色到标配](01-edge-ai-npu-trend.md) | 推理加速为何下沉到 MCU？选型真正的门槛是什么？ | F-012~F-019 |
| 02 | [Zephyr 生态：版本节奏、安全与产业投票](02-zephyr-ecosystem.md) | 半年发版节奏怎么跟？高危漏洞 CVE-2026-19569 怎么防？白金会员意味着什么？ | F-020~F-039 |
| 03 | [RISC-V 软件栈：从"猜测"到"可查询"](03-riscv-software-stack.md) | RVA23 基线如何落地？自动向量化值不值得开？ | F-040~F-046 |
| 04 | [社区动手能量：模拟器、微内核与打假](04-community-maker-projects.md) | 完整 VM 为何对嵌入式工程师有价值？一条不实数字如何打假？ | F-047~F-052 |

> **阅读提示**：周报是"快照式综述"，本包保留其时效性与自报口径边界。涉及 openTPO 性能、TI 倍数等数字时，请始终参考 [P0 核验报告](../references/verification.md) 的口径分级，不要把作者自报当作普遍事实。

```{toctree}
:hidden:
:maxdepth: 2

00-ai-designed-chip
01-edge-ai-npu-trend
02-zephyr-ecosystem
03-riscv-software-stack
04-community-maker-projects
```