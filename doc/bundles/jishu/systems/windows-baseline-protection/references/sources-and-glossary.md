---
type: Reference
title: "信源清单与术语表"
description: "13 个信源的分级清单（1 个一手评论源、7 个微软官方源、5 组媒体交叉源）与 16 个术语的中英对照、白话释义及易混名词辨析。"
tags: ["windows-baseline-protection", "信源清单", "术语表", "中英对照", "溯源"]
generated: { by: "seven-concepts-cmd", at: "2026-11-20" }
verified: { by: "process:seven-concepts-v", at: "2026-11-20" }
status: flagged
stale_after: "2027-03-31"
route: chaptered-summary
sources:
  - id: S1
    url: "https://mp.weixin.qq.com/s/sIb3u-ZMf-l2sRrz2iB8Vg"
    title: "果核剥壳：Win11 智能应用控制与基线保护（2026-11-20）"
---

# 信源清单与术语表

## 一、信源分级

| 级别 | 定义 | 本包用途 |
|---|---|---|
| **A · 官方一手** | 微软官方博客、产品文档、支持页、Insider 发行说明 | 机制、清单、时间线、策略归属的**唯一判定依据** |
| **B · 独立媒体交叉** | 多家科技媒体与聚合站 | 伙伴名单、先例、7/8 口径差异的交叉印证 |
| **C · 评论源（一手材料）** | 微信公众号文章 S1 | **切入案例与观点来源**，不作机制判定依据 |

### A 类 · 微软官方一手（M1~M7）

| ID | 信源 | 定位 | 支撑事实 |
|---|---|---|---|
| M1 | Windows Experience Blog《Windows security at Ignite 2026: Start secure, protect what matters, prepare for AI》（2026-11-17） | Ignite 2026 安全总览，首次宣布 preview | F-018、F-023 |
| M2 | Windows IT Pro Blog《A verifiable security state with Windows baseline protection》 | **机制骨架**：8 项清单、三种读出、启动测量、版本化、2027 GA、管理端 | F-020、F-026~F-031、F-034、F-036、F-041、F-043 |
| M3 | Microsoft Learn · Windows 11 Insider Experimental Preview Build 26340.10013 发行说明 | 构建号、11-17 更新、逐步推出、设置路径 | F-019、F-043 |
| M4 | Microsoft Support · Smart App Control Frequently Asked Questions | SAC 判定顺序、无单应用豁免、关闭/重启用、与杀软并行 | F-012~F-014、F-016 |
| M5 | Microsoft Learn · Smart App Control overview（开发者版） | 评估/强制两模式 | F-014 |
| M6 | Microsoft Learn · 适用于 Windows 的应用程序控制 | 22H2 起始版本、Intelligent Security Graph (ISG) | F-015 |
| M7 | Microsoft Support · Baseline protection 支持页（经 B 类转引） | 7 类口径、测试签名保护、Attention needed 与重启态 | F-029 |

### B 类 · 独立媒体交叉（T1~T5）

| ID | 信源 | 交叉用途 |
|---|---|---|
| T1 | IT之家（2026-11-18） | 8 项中文清单、伙伴名单、11/18 媒体时点 |
| T2 | Wccftech（2026-11-18） | 伙伴名单、无伙伴承诺拦截、战地风云 6 先例 |
| T3 | Windows Latest（经 T1/T2/T4 转引） | 首报口径、8 项拆分来源 |
| T4 | ghacks / neoteo / sffgeek / pureinfotech / global-insight | 7 类 vs 8 项口径、构建号、Bray 引述、Secure Boot UEFI 流程 |
| T5 | 超能网（2026-11-18） | 中文交叉、8 项清单、游戏性能与双系统影响 |

### C 类 · 评论源

| ID | 信源 | 边界 |
|---|---|---|
| S1 | 微信公众号「果核剥壳」《Win11新功能上线，以后你要用「和谐版」软件难了》，署名果核，2026-11-20 08:40，四川 | 公开无访问控制；`page_fact` 为源文陈述、`author_claim` 为作者判断；**本包不逐字转录**，走 `route: chaptered-summary` |

---

## 二、术语表（中英对照 + 白话）

| 术语 | 英文 / 缩写 | 白话释义 |
|---|---|---|
| 智能应用控制 | Smart App Control, SAC | 运行应用前先问云端「这程序安全吗」，答不上来就看有没有有效签名；都没有就拦。**不支持单个应用放行**。 |
| 基线保护 | Windows baseline protection | 把多项系统防护合成一个「通过/不通过」，开放给用户、IT 和应用查询。 |
| 安全处理器 | Security processor / TPM 2.0 | 主板上的独立安全芯片，用来保管密钥并测量启动状态。 |
| 安全启动 | Secure Boot | 开机时只允许受信任的引导程序加载，挡住启动阶段的恶意代码。 |
| 基于虚拟化的安全性 | Virtualization-Based Security, VBS | 用硬件虚拟化隔出一块受保护区域，把关键系统进程放进去。 |
| 内存完整性 | Memory Integrity / HVCI | 阻止恶意代码写进 Windows 受保护的内存区域；部分玩家曾为帧数关闭它。 |
| 仅加载已签名驱动 | Signed drivers only | 只加载带有效签名的驱动。 |
| Windows 认证驱动 | Windows-certified drivers | 驱动还需满足微软的硬件签名与认证规则。 |
| 测试签名保护 | Test signing protection | 支持页把上面两条驱动规则**合并**后的统称，是 7 类口径的来源。 |
| 内核调试保护 | Kernel debugger protection | 阻止调试工具绕过内核安全机制。 |
| 易受攻击驱动保护 | Vulnerable driver protection | 拦截已知有漏洞的驱动。 |
| 可版本化状态 | versioned security state | 基线标准会升级；今天通过首版，不代表通过以后每一版。 |
| 证明令牌 | attestation token | 硬件签发、服务端可验的密码学凭证，比本地回答更难伪造。 |
| 安全依赖方 | relying party | 接收并验证证明令牌的一方，通常是应用开发商的服务端。 |
| 应用智能服务 | app intelligence services / ISG | 微软云端信誉预测服务；源文俗称「云端信誉库」（E6）。 |
| 基线安全模式 | baseline security mode | Microsoft 365 管理中心里供 IT 管理员管理受管理设备的开关。 |

### 易混名词辨析

| 易混对 | 区别 |
|---|---|
| **Windows 基线保护** vs **Windows Security Baseline** | 前者是 2026 年预览、可被应用查询的**设备状态**；后者是 2024 年前后经 Security Compliance Toolkit 分发、供组策略/Intune 使用的**配置策略包**。同名不同物（F-032）。 |
| **SmartScreen** vs **SAC** | SmartScreen 拦截时通常有「更多信息 → 仍要运行」；SAC 在加载阶段拦截且**无单应用豁免**（F-009、F-013）。 |
| **能力** vs **策略** | 平台提供 allow/warn/limit/block 四档是**能力**；某个应用选哪一档是**策略**。源文 E4 把两者混为一谈。 |

---

> 所有外部链接均为可读引用，本包不缓存、不镜像原文；预览期细则可能变化，复核触发见[bundle 根时效表](../index.md)。
