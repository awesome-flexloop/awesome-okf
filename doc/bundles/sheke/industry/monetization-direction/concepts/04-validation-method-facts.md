---
type: Concept
title: "C4 需求验证 / 最小可行验证 · 权威方法事实登记"
description: "C4 类需求验证事实层逐条登记（F-071~F-082）：Lean Startup / MVP、Jobs to be Done、Mom Test、价值主张画布（VPC）、Steve Blank 客户开发四步；含 MVP 定义逐字与口径对照（MVP ≠ 功能简陋半成品）。"
tags: ["monetization-direction", "事实层", "需求验证", "MVP", "JTBD", "Mom Test"]
generated: { by: "reference_agent/okf-writer", at: "2026-10-17T00:00:00Z" }
verified: [{ by: "process:seven-concepts-v", at: "2026-10-17T00:00:00Z" }]
status: stable
stale_after: "2027-06-30"
sources:
  - id: spec-facts
    resource: ".trae/specs/create-monetization-direction-okf-wiki/facts.md"
    title: "spec 区事实登记（F 编号基准）"
  - id: spec-sources
    resource: ".trae/specs/create-monetization-direction-okf-wiki/sources.md"
    title: "spec 区信源候选清单（S 编号出处）"
  - id: verification
    resource: "/references/verification.md"
    title: "核验报告（P0 结论与勘误清单）"
---

# C4 需求验证 / 最小可行验证 · 权威方法事实登记

> 本篇为**事实层**：仅登记「有哪些权威需求验证方法、它们是谁在何时提出、核心主张归属」。观点与主张以〔主张〕标注；方法性主张标〔方法〕；**只登记事实、不教方法**（可照做的验证脚本与实验模板归 examples，操作步骤见方法层 [07 篇](07-needs-validation-method.md)）。

本篇覆盖 C4 类事实 **F-071 ~ F-082**，共 12 条。

## 一、Lean Startup 与 MVP（F-071 ~ F-073）

- **Eric Ries 于 2011 年**出版《The Lean Startup》，提出 **build-measure-learn（构建-测量-学习）循环、最小可行产品（MVP）、转型（pivot）** 等概念（F-071）。
- MVP 定义（**逐字**，书 p.77）：开发中的产品版本，能「以最少努力与最短开发时间完成一次完整 Build-Measure-Learn 循环」（F-072）。
- 〔方法〕Ries 建议**优先测试计划中风险最高的要素**（F-073）。

### 1.1 口径对照（防混用）

| 口径 | 表述 | 来源层级 | F 编号 |
|---|---|---|---|
| **正确值** | MVP = 用于**验证最风险假设**的最小实验，目的为**学习**而非省成本 | F-071/F-072（逐字定义经第三方书摘，标降级） | F-071、F-072 |
| 常见误传 | MVP = 「功能简陋的半成品」 | —— | —— |

> MVP 的目的为**学习**（完成一次 Build-Measure-Learn 循环）而非省成本，禁混用。

## 二、Jobs to be Done（F-074 ~ F-075）

- **Clayton Christensen、Scott Cook 与 Taddy Hall 于 2005 年**在《哈佛商业评论》发表文章，首次系统表述「待办任务（Jobs to be Done, JTBD）」思想（"The Cause and the Cure of Marketing Malpractice"；亦有 2006-01-16 HBS 版）（F-074）。
- 〔主张〕JTBD 核心主张：顾客不是「购买产品」，而是「雇佣」方案来完成生活中的某项进展（job）；含**功能、社会、情感**三个维度（F-075）。

> **口径对照（防混用）**：F-074 的 2005 HBR 文章与 2006-01-16 HBS 摘录为**同一思想的先后发表渠道，非两套理论**。

## 三、The Mom Test（F-076 ~ F-078）

- **Rob Fitzpatrick 于 2013 年**自出版《The Mom Test》（F-076）。
- 〔方法〕Mom Test 三类误导性反馈：**compliments（恭维）、fluff（空话 / 泛化断言）、ideas（对方的点子）**（F-077）。
- 〔主张〕Mom Test 方法主张：应问**过去的具体行为**而非未来承诺与假设（「你会不会买」→「你上次是怎么做的」）（F-078）。

## 四、价值主张画布 VPC（F-079 ~ F-080）

- **Alexander Osterwalder 等 2014 年**出版《Value Proposition Design》（Wiley，2014-10，320 页），提出**价值主张画布（VPC）**（F-079）。
- VPC 结构：Customer Profile（jobs / pains / gains）与 Value Map（products & services / pain relievers / gain creators），追求两者「fit」（F-080）。

## 五、客户开发四步（F-081 ~ F-082）

- **Steve Blank 于 2005 年**自出版《The Four Steps to the Epiphany》，提出「客户开发（Customer Development）」四步框架（F-081）。
- Eric Ries 曾在 Steve Blank 门下（IMVU），精益创业建立在客户发现 / 客户开发之上（F-082）。

## 六、口径对照小结

| 对照对象 | 口径 A | 口径 B | 禁止混用说明 | F 编号 |
|---|---|---|---|---|
| 精益创业 MVP | 用于**验证最风险假设**的最小实验 | 误传：功能简陋的半成品 | 目的为学习而非省成本，禁混用 | F-071、F-072 |
| JTBD | 2005 HBR 文章 | 2006-01-16 HBS 摘录 | 同一思想先后渠道，非两套理论 | F-074 |

## 本篇要点小结

1. 本篇登记 C4 类五组需求验证方法：Lean Startup / MVP（2011）、JTBD（2005/2006）、The Mom Test（2013）、价值主张画布（2014）、客户开发四步（2005），共 F-071 ~ F-082。
2. MVP 定义逐字项（F-072）经第三方书摘，标降级；其核心为「以最少努力完成一次 Build-Measure-Learn 循环」用于**验证最风险假设**。
3. 口径对照：MVP ≠ 功能简陋半成品；JTBD 2005 HBR 与 2006 HBS 为同一思想的两渠道。
4. 主张分层：JTBD「雇佣方案完成进展」（F-075）、Mom Test「问过去行为」（F-078）等均标〔主张〕/〔方法〕，不作客观结论。
5. 全量核验结论见 [核验报告](../references/verification.md)。
