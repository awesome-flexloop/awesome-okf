---
type: Concept
title: "00 · 两个机制与一条时间线"
description: "分清智能应用控制与基线保护：前者判定哪个程序能运行，后者报告这台设备处于什么状态；附 2022 至 2027 的发布时点对齐与同名术语辨析。"
tags: ["windows-baseline-protection", "概念", "时间线", "术语辨析", "SAC"]
generated: { by: "seven-concepts-cmd", at: "2026-11-20" }
verified: { by: "process:seven-concepts-v", at: "2026-11-20" }
status: flagged
stale_after: "2027-03-31"
route: chaptered-summary
sources:
  - id: facts-one
    resource: "/references/article-source.md"
  - id: glossary
    resource: "/references/sources-and-glossary.md"
---

# 00 · 两个机制与一条时间线

源文把两个功能串成一条叙事：「智能应用控制已经很难受，微软现在准备来个更骚的」。读起来顺畅，但**它们回答的不是同一个问题**。先把这一层拆开，后面所有结论才不会串味。

## 一句话区分

| | 智能应用控制（SAC） | Windows 基线保护 |
|---|---|---|
| 问的是 | **这个程序**能不能跑 | **这台设备**处于什么状态 |
| 判定对象 | 单个应用 / 二进制文件 | 整机的一组安全设置 |
| 结果给谁 | 系统自己用来决定放行或阻止 | 用户、IT 管理员、**以及应用** |
| 谁能改变结果 | 用户关闭 SAC，或开发者给程序签名 | 用户/管理员开启缺失防护；应用自己决定怎么对待结果 |
| 起始版本 | Windows 11 22H2（F-015） | 2026-11-17 起 Insider 预览（F-018） |
| 有无单应用豁免 | **没有**（F-013） | 不适用——状态是整机级的 |

换句话说：SAC 是**一道闸**，基线保护是**一块仪表盘**，而且这块仪表盘的读数被接到了每一款应用上。源文真正敏锐的地方正是这句「不是给系统自己用的，是开放给软件开发商读取的」（F-033）——这个转折比「更严了」准确得多。

## 时间线（对齐官方锚点）

| 时点 | 事件 | 信源 |
|---|---|---|
| Windows 11 22H2 起 | SAC 随系统提供；预测服务在应用控制文档中称 ISG | F-015（M6） |
| 2026-02 | 微软阐述「默认更安全」方向：系统强制透明、以用户为中心的同意、易验证的安全基线 | F-023（M2） |
| **2026-11-17** | Ignite 2026 官方宣布 baseline protection 进入预览；Insider Experimental 构建 **26340.10013** 同步标注、逐步推出 | F-018、F-019（M1、M3） |
| 2026-11-18 | Windows Latest 首报，IT之家、Wccftech、超能网等转述；8 项清单广泛传播 | F-022（T1、T2、T5） |
| 2026-11-20 | 本包一手材料 S1 发布 | F-001 |
| **2027（计划）** | 正式可用（general availability） | F-020（M2） |

> ⚠️ 源文写「11月18日…预览添加」（F-017）。**11/18 是媒体转述时点，不是官方发布日**；官方博客与构建说明都锚在 11/17（核验报告 E1）。本包按 11/17 叙述，两种口径并列登记，不做静默替换。

## 两个同名陷阱

1. **Windows 基线保护 ≠ Windows Security Baseline**（F-032）。后者是 2024 年前后经 Security Compliance Toolkit 分发、供组策略 / Intune 使用的**配置策略包**；前者是 2026 年预览、可被应用查询的**设备状态**。搜资料时极易混。
2. **SmartScreen ≠ SAC**（F-009）。SmartScreen 拦截通常还能点「更多信息 → 仍要运行」；SAC 在加载阶段拦下，且官方明确没有单应用豁免。详见[01 · 智能应用控制](01-smart-app-control.md)。

## 为什么值得单独做一包

8 项防护全是既有能力（F-027），真正新增的是「把这些能力合成一个可被第三方读取的状态」。这个变化不体现在功能列表里，而体现在**读出方**上——本包的[洞察 1](../references/insights-and-pattern.md) 由此展开。

> 下一步：[01 · 智能应用控制](01-smart-app-control.md) → [02 · 首版检查项](02-baseline-criteria.md) → [03 · 可验证安全状态](03-verifiable-security-state.md)。只想动手查自己的电脑，直接跳到[设备自查](../examples/01-check-your-device.md)。
