---
okf_version: "0.2"
type: concept
title: "Zephyr 生态：版本节奏、高危漏洞与产业投票"
description: "Zephyr 4.3 EOL 与 4.5/4.6 版本节奏、CVE-2026-19569 userspace 整数溢出漏洞细节、十周年白金会员与 Arduino Zephyr 迁移完成"
tags: [Zephyr, RTOS, CVE, 版本管理, 安全漏洞, Arduino, LoRaWAN]
generated:
  by: "seven-concepts-cmd"
  at: "2026-10-13T13:20:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: mp-weekly-03
    resource: "https://mp.weixin.qq.com/s/yD0epaC9Xm16UVZYojqWOA"
    title: "嵌入式周报·第三期"
---

# Zephyr 生态：版本节奏、高危漏洞与产业投票

## 版本节奏：一个只剩 4 天的决定（F-020 ~ F-025）

Zephyr 现在是**固定的半年节奏**（4 月和 10 月各一版）。当周（2026-10-12）的关键时点：

| 版本 | 时点 | 说明 |
|------|------|------|
| 4.3.1 | **2026-10-15 结束支持（EOL）** | 比 4.5 正式发布早 11 天 |
| 4.4.1 | 维护到 2027-04 | 中间过渡档 |
| 4.5 RC2 | 2026-10-12（下周一） | |
| 4.5 RC3 硬冻结 | 2026-10-19 | |
| **4.5 正式发布** | **2026-10-26**（官方口径为"2026-10"） | 维护到 2027-10 |
| 4.6 | 2027-04 | 下一个 LTS |

> ⚠️ 官方 release 表对 4.5 仅写"October 2026"，精确 10-26 为周报作者口径（[V5](../references/verification.md)），消费时以官方发布为准。

**核心建议**（作者，F-025）：还在 4.3 的项目，当周直接排 **4.5 的迁移评估**。分两步走（4.3→4.4→4.5）看着稳，其实把迁移工作摊成了**两轮重复**；现在评估 4.5，是把成本摊在两个版本上，而不是明年 4 月一次性吃到。

**LoRaWAN 变更**（F-026、F-027）：4.5 引入 LoRaWAN **原生后端**，直接跑在 Zephyr 的 radio driver 上，不再依赖 Semtech 的 LoRaMac-node，目前仅支持 EU868；但**运行时配置（速率、ADR）的调用顺序变了，老代码需要改**。核验确认原生后端存在且属性正确，"4.5 新增"的版本归属为 single-source（[V13](../references/verification.md)）。

## 高危漏洞：CVE-2026-19569——user space 沙箱可逃逸（F-033 ~ F-039）

2026-10-09 披露的 **CVE-2026-19569**，评分 **8.8（HIGH）**（[V7](../references/verification.md)，NVD 可查）。

**根因**（F-034~F-036）：`kernel/userspace/userspace.c` 的 `dynamic_object_create()` 在计算动态内核对象的分配大小时**没有检查无符号整数溢出**：

```c
obj_size_get(otype) + size          // 没查溢出
STACK_ELEMENT_DATA_SIZE(size)        // 同样没查
```

`size` 参数**直接从用户态传进来**。传一个接近 `SIZE_MAX` 的值，加法回绕成一个极小的数——分配出去的是几字节的堆块，对象描述符却仍带完整类型标记登记在对象表。随后 `k_mutex_init()` / `k_sem_init()` / `k_thread_create()` 会把完整对象写进被截短的分配，造成**监督态越界写**，破坏堆元数据与相邻内核对象；在 `CONFIG_GEN_PRIV_STACKS` 下还会写入一个受攻击者影响的野指针作为特权栈基址。

**影响范围**（F-037）：Zephyr **3.5.0 至 4.4.2**，需同时打开 `CONFIG_USERSPACE` 与 `CONFIG_DYNAMIC_OBJECTS`（或 `CONFIG_DYNAMIC_THREAD`），调用线程需已被分配 resource pool。**未特权用户线程可借此逃出 userspace 沙箱**。

**处理**（F-038、F-039）：升级到打了补丁 **85c1c4c2** 的版本；短期缓解是关掉 `CONFIG_DYNAMIC_OBJECTS` / `CONFIG_DYNAMIC_THREAD`。完整描述见官方安全公告 **GHSA-fg8c-9fhq-q7hv**。

> 🧠 **模式**：这是典型的"**边界未验证使约定可被打破**"——无符号溢出把"几字节分配"伪装成"合法对象"，进而越界写。凡是从用户态进内核的 size，都必须先做上界校验再参与布局计算。对用 Zephyr 用户态隔离做产品的团队，这条直接影响安全性。

## 产业投票：Zephyr 十周年（F-028 ~ F-032）

Zephyr 十周年不是办活动办出来的，是**产业自己投票投出来的**：

- **白金会员**（F-028）：2026-10-01 官宣**英飞凌（Infineon）和 TI 双双升级为白金会员**（[V9](../references/verification.md)）。TI 自 2016 年项目创立起就在贡献，英飞凌是多个平台活跃贡献者。
- **活动时间线**（F-029）：10-06 Maintainers Forum；10-07~09 Zephyr Developer Summit（40+ 场技术演讲、45+ 位讲者）都在布拉格，与 Open Source Summit Europe 同期；10-07 颁发**首届 Zephyr Community Awards**。
- **对工程师的意义**（F-031，作者）：白金会员意味着更多资源投入技术开发、基础设施与社区项目——**支持面越宽，你的 BSP 越不容易在换料号时断掉**。

**Arduino 完成 Zephyr 迁移**（F-032）：Arduino 官宣 **Arduino Core for Zephyr RTOS v1.0.0**（⚠️ 官方发布为 **2026-09-03**，核验更正周报所述 10-04，[V10](../references/verification.md)），正式走完从 MbedOS 到 Zephyr 的迁移：源码与 loader 公开在 GitHub、基于 Zephyr SDK v0.16.8 验证、用 west 与 sync-zephyr-artifacts 标准工具、依赖 llext 动态扩展与 zephyr-sketch-tool，通过 ArduinoCore-API 保持向后兼容；首批受益硬件为 **Arduino UNO Q**（及 VENTUNO Q 变体），开箱即用 Zephyr 内核。如果有老 Arduino 项目，迁移路径从「能用」变成了「有官方支持」。

---

## 工程启示

1. **半年节奏就得半年一跟**：固定半年发版意味着 EOL 是计划的；别把迁移拖成两轮重复（F-025）。
2. **用户态安全要追补丁日**：CVE-2026-19569 影响面大（3.5~4.4.2 全带 user space 的产品）；优先升级 85c1c4c2，临时关 `CONFIG_DYNAMIC_*`（F-038）。
3. **生态多元度高=换料安全**：多白金会员、多 vendor 贡献降低单供应商断供风险（F-031）。
4. **工具链官方化是迁移信号**：Arduino→Zephyr v1.0.0 标志 MbedOS 时代结束，老项目获得官方迁移路径（F-032）。

```{toctree}
:hidden:
:maxdepth: 1

../references/index
```