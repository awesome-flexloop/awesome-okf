---
type: Concept
title: "ER-100 首针人体：事件时间线（What/When/Who）"
description: "ER-100 与 Life Biosciences 归属、Sinclair 身份、核验后的三段时间线，以及动物实验三重限定词与两项失实数字"
tags: [er-100, life-biosciences, sinclair, clinical-trial, timeline]
generated: { by: process:seven-concepts-blog-okf, at: "2026-10-15T15:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-15T15:00:00+08:00" }
status: flagged
stale_after: "2027-06-30"
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/J86wj_jTrBpXBiuzf_82JQ
    title: "美因（公众号）：人类第一针「逆龄基因药」打进人体！8 周细胞生物年龄逆转约 75%，我们即将迎来不老时代？"
  - id: src-lb-ind
    resource: https://www.lifebiosciences.com/life-biosciences-announces-fda-clearance-of-ind-application-for-er-100-in-optic-neuropathies/
    title: "Life Biosciences Announces FDA Clearance of IND Application for ER-100 in Optic Neuropathies"
  - id: src-lb-dosed
    resource: https://www.lifebiosciences.com/life-biosciences-announces-first-patient-dosed-in-phase-1-trial-of-er-100-for-optic-neuropathies/
    title: "Life Biosciences Announces First Patient Dosed in Phase 1 Trial of ER-100 for Optic Neuropathies（June 9, 2026）"
  - id: src-lb-fih
    resource: https://www.lifebiosciences.com/life-biosciences-announces-first-in-human-data-from-ongoing-phase-1-trial-evaluating-er-100-in-optic-neuropathies/
    title: "First-in-Human Data from Ongoing Phase 1 Trial Evaluating ER-100 in Optic Neuropathies（October 8, 2026）"
  - id: src-nature
    resource: https://www.nature.com/articles/d41586-026-01836-7
    title: "World-first: therapy to make cells young again trialled in a person（Heidi Ledford, Nature）"
  - id: src-nmnlife
    resource: https://pubmed.ncbi.nlm.nih.gov/38979132/
    title: "Long-term NMN treatment increases lifespan and healthspan in mice in a sex dependent manner"
  - id: src-reprog
    resource: https://onlinelibrary.wiley.com/doi/full/10.1111/acel.14039
    title: "Partial cellular reprogramming: A deep dive into an emerging rejuvenation technology（Aging Cell 2024）"
---

# ER-100 首针人体：事件时间线（What/When/Who）

本篇回答「发生了什么、谁做的、什么时候」。全部具体声明附 F 编号（来源见 [博文事实清单](../references/article-source.md)），核验后的正确值与源文差异见 [核验报告](../references/verification.md)。

## 一、主体与归属

- **ER-100**：源文称的「人类第一针瞄准逆转衰老的基因疗法」，指一款以 **AAV2 载体递送 OSK 三基因**（Oct4/Sox2/Klf4）的基因治疗产品（F-001、F-088）。
- **归属**：ER-100 出自 **Life Biosciences**——由哈佛遗传学教授 **David Sinclair** 联合创办的公司（F-001）。核验确认：OSK 平台在 Sinclair 实验室发明并授权 Life Biosciences，ER-100 即 AAV2-OSK（来源：Life Biosciences 官方新闻稿）。
- **David Sinclair**：哈佛医学院遗传学教授、衰老研究领域的知名科学家，著《Lifespan》（F-002）。头衔与共同创办人身份经核验属实；出生年与畅销书未单独逐项核验（按常识层接受）。

> **口径提示**：源文（F-004）称 Sinclair 团队「2026 年正式向 FDA 提交人体临床试验申请」。核验结果为 Life Biosciences 的 IND **获 FDA 放行（clearance）**（2026-01-15），而非「提交申请」——同一件事的表述被改写。

## 二、人体时间线（核验后的正确值）

| 事件 | 源文口径（F-005） | 核验正确值 | 状态 |
|---|---|---|---|
| FDA / IND 放行 | 2026 年 1 月 | **2026-01-15** | ✅ 相符 |
| 首位患者给药 | 「3 月」（源文口径） | **2026-06-09**（Life Biosciences 新闻稿） | 🔴 **源文错误**（勘-01） |
| 一期（首例人体）数据公布 | 10 月 | **2026-10-08** | ✅ 相符 |

- **源文口径须显式标注**：源文写「3 月第一位患者注射」，与 Life Biosciences 官方新闻稿（June 9, 2026）及文中图 02 的 Nature 新闻日期（09 June 2026）**自相矛盾**。本束正文一律呈现 **2026-06-09**，并标注源文误作「3 月」（勘-01）。
- **一期数据口径**（F-006）：核验为官方 2026-10-08 公告——**3 名 OAG（视神经病变）受试者在 Day 56 均耐受良好，其中 2 名视野测试出现初步改善信号**。源文「安全性良好，两名受试者出现视力改善迹象」中的「两名」与官方一致；但此为**视野测试初步信号**，源文亦自承「还只是初步迹象」，不可读作疗效证明。
- **试验设计边界**（F-017、F-020）：本次人体试验选择**眼睛**，因眼睛相对独立、便于观察；一期主要验证**安全性**，而非疗效。源文称从眼睛到全身，业内人士普遍认为至少还要 **5 到 10 年**（属行业预期，非承诺）。

## 三、动物实验的成效口径（本文最需警惕处）

源文（F-007）写「动物实验中 ER-100 在 6 到 8 周让细胞生物年龄回退约 75%」。核验结论：该表述**丢失了三重限定词**，不能作为「人体疗效」或「寿命延长」的表述。

- **限定一（物种）**：证据来自**小鼠**。（勘-02）
- **限定二（读数类型）**：「生物年龄」指**表观遗传（DNA 甲基化）时钟读数**，**不是**生理年龄、**不是**寿命（勘-02、勘误③口径对照表）。
- **限定三（组织范围）**：多组织为 **50–95%，视组织而定**；「6–8 周」是**变化出现的时间**，而非一个固定的「回退 75%」周期（勘-02）。
- **不得三级跳跃**：表观遗传时钟读数变化 ≠ 生理年龄逆转 ≠ 寿命延长 ≠ 人体疗效。源文从「时钟读数」直接推向「不老时代」，是本 bundle 判 `flagged` 的核心原因之一。

### 两项经核验失实的动物实验数字

| 源文声明 | 核验结果 | 判定 |
|---|---|---|
| 「垂暮小鼠的剩余寿命近乎翻倍」（F-008） | 权威数值：**长期 NMN 补充小鼠中位寿命 +8.5%（雌）**；**OSK 全身重编程约 +7%**；无任何权威支持「近乎翻倍」 | 🔴 ❌（勘-03） |
| 「恶性肿瘤细胞失去失控增殖特征、部分凋亡」（F-009） | **未检索到**支持该具体成效的独立来源；且部分重编程与**肿瘤风险**恰是学界关注的安全议题 | 🔴 ❌ |

## 四、本篇要点速览

- ER-100 = Life Biosciences 的 AAV2-OSK 基因疗法，Sinclair 为联合创办人（F-001、F-002）。
- 人体时间线：**2026-01-15** IND 放行 → **2026-06-09** 首位患者给药（源文误作 3 月）→ **2026-10-08** 一期数据（F-005、勘-01）。
- 一期数据：3 名 OAG 受试者 Day 56 耐受良好、2 名视野测试初步改善信号（F-006）。
- 动物实验 75% 口径须补**小鼠 / 表观遗传时钟 / 多组织 50–95%** 三重限定词；「寿命近乎翻倍」判 ❌，正确量级为 **+7%~+8.5%**（F-007、F-008、勘-02、勘-03）。
- 从眼睛到全身 5–10 年为行业预期，非承诺（F-020）。

延伸：机制层见 [衰老信息论与 OSK 部分重编程](01-aging-information-theory.md)；成本与可及性见 [费用、口服小分子与到全身的时间表](03-cost-and-access-timeline.md)。本束的核验更正值与核验衍生值另登记为 F-075 起（见 [博文事实清单](../references/article-source.md)）；时间线更正登记为 F-075（源文「3 月」更正为 2026-06-09），正文涉及更正处均已按正确值呈现。