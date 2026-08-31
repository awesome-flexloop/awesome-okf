---
type: Reference
title: 交叉引用——跨束知识关联登记
description: tcm-overview 束与知识库其他束的交叉引用：think/huangdi-neijing 内经阅读束（四大经典之一深入研读）、think/laozi 帛书异文研读束（双源核对方法的平行实践）、本域 waijing-weiyan 外经微言束（单书精读样例）
tags: [reference, 交叉引用, 黄帝内经, 老子, 外经微言, 知识关联]
generated: { by: "agent:create-tcm-okf", at: "2026-08-30T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-30T12:00:00+08:00" }
status: stable
stale_after: 2027-08-30
sources:
  - id: waijing-weiyan
    resource: ../../waijing-weiyan/index.md
    title: 《外经微言》阅读教程束（本域）
  - id: neijing-reading
    resource: ../../../../think/huangdi-neijing/neijing-reading/index.md
    title: 《黄帝内经》阅读束（think 域）
  - id: boshu-reading
    resource: ../../../../think/laozi/boshu-reading/index.md
    title: 老子帛书阅读束（think 域）
---

# 交叉引用：跨束知识关联登记

本束是总览束，深入研读需进入各单书束。以下登记与本束关系最密切的跨束引用（均为 bundles/ 树内相对路径链接）。

## tcm 域（中医）

| 目标束 | 关系 | 协作建议 |
|---|---|---|
| [waijing-weiyan：《外经微言》（黄帝外经）阅读教程](../../waijing-weiyan/index.md) | 本域首束。单书精读的完整样例：文献学三层分离（著录层/托名层/文本层）、13 篇双源核对精读、68 篇存目提要 | 读完本束[概念 02 版本学](../concepts/02-philology-basics.md)与[双源核对演示](../examples/dual-source-verification-demo.md)后，可到该束看同一方法在单书上的全程应用（其"通读路径与校勘实操"与本束演示互为印证） |

## think 域（思想文献）

| 目标束 | 关系 | 协作建议 |
|---|---|---|
| [neijing-reading：《黄帝内经》阅读教程](../../../../think/huangdi-neijing/neijing-reading/index.md) | 四大经典之首的深入研读束（12 篇概念 + 9 篇精读示例），与本束构成"总览 → 单书"两级结构 | 按本束[通读计划](../examples/four-classics-reading-plan.md)阶段 1 进入《内经》时切换到该束；该束的版本与注家登记可视为本束[概念 03 五问法](../concepts/03-pseudepigrapha-dating.md)在《内经》上的完整答案 |
| [boshu-reading：老子帛书阅读](../../../../think/laozi/boshu-reading/index.md) | 平行方法束：出土简帛本与传世本的**异文研读**（四本系统、避讳字、关键异文），是"双源逐字核读法"在子部文献上的同构实践 | 关心[概念 02 异文五分法](../concepts/02-philology-basics.md)的读者可对照该束的版本系统分析——医经的"版本系统差异"与子书的"简帛本/通行本差异"是同一现象的两个领域实例 |
| [laozi-works：老子著作与研究](../../../../think/laozi/laozi-works/index.md) | 该束含出土本汇校（unerthed-collation）与历代注家研究，注家链存录体例与本束"注家异说并列不裁决"原则一致（INS-005） | 研究托名与注家谱系方法时可跨域参照 |

## 域内规划中的束（占位）

tcm/classics 域规划中的单书束（nanjing、shanghan-zabinglun、shennong-bencaojing 等）建立后，本束[概念 03 五问对照表](../concepts/03-pseudepigrapha-dating.md)中标注"待某束登记"的单元格与[概念 04 扩展占位清单](../concepts/04-graded-bibliography.md)中的条目应更新为指向对应束的交叉引用。

## 引用约定

- 跨束链接一律使用相对路径 + `.md` 后缀（如 `../../waijing-weiyan/index.md`），不用绝对路径。
- 断链（目标束未建或移动）不视为格式错误（OKF v0.2 容忍断链），但发现后应更新本表。
