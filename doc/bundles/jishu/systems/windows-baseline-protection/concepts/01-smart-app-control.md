---
type: Concept
title: "01 · 智能应用控制：判定通路、两阶段与正确关闭方式"
description: "SAC 的云端预测加有效签名双通路、评估与强制两模式、无单应用豁免的官方依据，以及源文把局部开关写成禁用整个安全中心的口径纠偏。"
tags: ["windows-baseline-protection", "概念", "SAC", "代码签名", "口径纠偏"]
generated: { by: "seven-concepts-cmd", at: "2026-11-20" }
verified: { by: "process:seven-concepts-v", at: "2026-11-20" }
status: flagged
stale_after: "2027-03-31"
route: chaptered-summary
sources:
  - id: facts-one
    resource: "/references/article-source.md"
  - id: verification
    resource: "/references/verification.md"
---

# 01 · 智能应用控制（Smart App Control）

源文前半段描述的「打开软件提示某个 DLL 被禁用」（F-005）、「新版 Quicker2 与网络工具受影响」（F-006），指向的是 SAC 而非基线保护。这一节把机制和边界说清楚。

## 判定通路：三步，不是只看签名

微软支持 FAQ 给的顺序是（F-012）：

1. 运行应用时，先问**云端应用智能服务**能否对其安全性作出有信心的预测；
2. 判为恶意或可能不需要的应用（PUA）→ 阻止；判为安全 → 放行；
3. **只有云端答不上来时**，才检查是否有有效签名：签名有效 → 放行；未签名或签名无效 → 视为不受信任并阻止。

所以源文「结合数字签名和微软云端的信誉库」（F-010）意思对，但顺序被压平了：签名是**兜底**通路，不是第一道。官方称谓是应用智能服务 / Intelligent Security Graph (ISG)（F-015、核验报告 E6），「信誉库」是通俗说法。

## 两个模式

| 模式 | 含义 |
|---|---|
| 评估模式（evaluation） | 系统在观察这台设备是否适合启用该保护；进入强制模式会发 Toast 通知 |
| 强制模式（enforcement） | 只有被应用智能服务识别、或用受信任证书签名的程序才能运行 |

官方还列了会自动关闭 SAC 的情形（F-014）：企业托管设备、已配置开发者模式、S 模式、关闭可选诊断数据、被用户手动关闭。这解释了一个反直觉现象——**同一款绿色软件，在不同人机器上可能一边被拦、一边照跑**，因为 SAC 未必处于强制模式。

## 「连仍要运行的按钮都没有」——官方逐字确认

这是源文最准确的一处（F-009）。微软 FAQ 原文：`There is currently no way to bypass Smart App Control protection for individual apps`，给出的两条出路是**关闭 SAC** 或**联系开发者用有效证书签名**（F-013）。对比 SmartScreen 的「更多信息 → 仍要运行」，SAC 没有逐应用白名单，这是二者最实质的差别。

## 一处需要纠正的操作口径

源文推论「以后禁用 Windows 安全中心要成玩机必选项了」（F-011）。核验后应写成：

- 官方路径是在 **Windows 安全中心 → 应用和浏览器控制** 里**单独关闭 SAC**，不必把整个安全中心或 Defender 下线；
- 近期 Windows 更新已允许**无需全新安装**就在安全中心内启用/重新启用 SAC（F-016），旧资料里「必须重置电脑」的说法已过时；
- SAC 与第三方杀软并行工作、不替代杀软（F-016）。

把「关一个开关」写成「禁用整个安全组件」，是典型的操作放大（核验报告 E3）。本包按官方路径呈现，不照搬。

## 哪些属于作者观察

「被拦得最多的就是个人开发者的小工具和绿色软件」（F-011）、Quicker2 受影响、V2EX 有人提问（F-006、F-007），源文均未附出处链接，**无法独立复核**（缺口 G5）。机制上「未签名且云端无预测的程序会被拦」成立，但影响范围没有官方统计，本包不把它当规模结论。

> 下一步：[02 · 首版检查项与 7/8 口径](02-baseline-criteria.md)。术语对照见[信源与术语表](../references/sources-and-glossary.md)。
