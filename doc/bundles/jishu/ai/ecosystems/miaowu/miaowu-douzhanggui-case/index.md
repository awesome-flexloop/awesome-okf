---
okf_version: "0.2"
type: bundle
title: "秒悟 Meoo 副业案例：「豆掌柜」拼豆店门店管理应用"
description: 微信公众号「秒悟 Meoo」2026-10-29 公开文章《纳尼?！真有人靠 Meoo 做副业月入过万！》的 OKF v0.2 转化——02 年出生的王玉丹用秒悟 Meoo 为上海一家拼豆店做出门店管理应用「豆掌柜」，跑 5 家店、免费试用一个月、驻店一周、累计迭代数百次，2026 年 8 月底被店主以 1 万元购买；含需求发现、客户开发、试用迭代与成交条款四段拆解，以及承诺边界声明（单源案例、可迁移的是方法而非结果）
tags: [meoo, miaowu, side-hustle, case-study, wechat-article, customer-development, free-trial, single-source]
generated:
  by: seven-concepts-cmd
  at: "2026-10-29T10:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-29T10:10:00+08:00"
status: draft
stale_after: "2027-04-29"
sources:
  - id: wx-dzg
    resource: https://mp.weixin.qq.com/s/LCow44TOI0J-HjINToYWtQ
    title: 纳尼?！真有人靠 Meoo 做副业月入过万！
    author: 秒悟Meoo
    last_modified: 2026-10-29
  - id: bounty-plaza
    resource: ../miaowu-bounty-plaza/index.md
    title: 同库既有束 · 秒悟应用赏金广场（AI Builder Growth 共创计划）
  - id: growth-skills
    resource: ../miaowu-growth-skills/index.md
    title: 同库既有束 · 秒悟 Meoo 产品增长 Skill 包：选型与使用教程
  - id: practice-cases
    resource: ../miaowu-meoo-practice-cases/index.md
    title: 同库既有束 · 秒悟实训案例（7 实操场景 + 5 步应用搭建法）
  - id: meoo-com
    resource: https://meoo.com/
    title: 秒悟 Meoo 官方平台入口
---

# 秒悟 Meoo 副业案例：「豆掌柜」拼豆店门店管理应用

> **类型**：公开文章转化的**单案例拆解**（叙事型知识，**不设 `examples/`**——源文无可复现的安装/配置/代码流程）
> **主源**：微信公众号「秒悟 Meoo」2026-10-29 01:00 发布的《纳尼?！真有人靠 Meoo 做副业月入过万！》（F-001–F-003）
> **采集**：2026-10-29，公开可访问、无登录/验证码，WebFetch 单通道取到完整正文
> **性质声明**：本文是**平台方自述的用户案例**（发布账号即 Meoo 官方公众号），人物经历、金额与数量均为**文章单源**，无第三方凭证；本束忠实登记、不推断补全
> **数据时点**：案例时间线截至 2026 年 9 月前后，`stale_after: 2027-04-29`

## 本文概要

这篇文章讲一个**已完成闭环的副业案例**，而不是一份方法清单。主角王玉丹（02 年出生）2026 年 5 月从北京一家公司辞职、花两个月自学 AI；她在上海一家拼豆店注意到店员反复确认桌位、核销、计时的忙乱（F-011–F-017），由此想到把**桌位、计时和订单**放到一起（F-018）。7 月中旬开始开发，在外滩黑客松 AI Coding 比赛接触 Meoo 后用其重做一版（F-020–F-022）。

产品做完只是开头。她前后**跑了 5 家拼豆店**（F-028），遭遇「已有系统」「太忙没空聊」「加了联系方式没下文」三类失败（F-029–F-031），最后有**一家愿意试**（F-034）。她提出**先免费用一个月**、条件是老板反馈哪里不好用（F-036–F-037），并**在店里待了整整一周**收集真实需求（F-038），补上在线预约、数据仪表盘、套餐设置（F-039–F-041），全程**累计迭代数百次**（F-042）。到 **2026 年 8 月底**，店主决定**以 1 万元购买**「豆掌柜」（F-043、F-045），双方约定**一年内免费维护及需求修改**（F-046）。

本束把这段经历拆成四段可复用的知识：**需求怎么发现**（观察式发现）、**产品怎么落地**（工具层降摩擦）、**客户怎么开发**（跑店与试用）、**成交边界怎么谈**（维护成本与可外推性）。

## ⚠️ 阅读前必知的三件事

1. **这是平台方自述的单源案例**：文章发布账号即 Meoo 官方公众号（F-002），人物、金额、数量均无第三方凭证（见 [verification.md](references/verification.md)）。它证明「存在这样一条路径」，**不证明**「按此操作即可复制」。
2. **可迁移的是方法，不是结果**：文章**明确自述**「豆掌柜」能否卖给第二家、第三家尚无答案（F-047），主角本人也已转向 AI 硬件方向（F-048）。任何「月入过万可复制」的读法都超出源文声明。
3. **成交不是终点**：交易含**一年内免费维护及需求修改**（F-046）。文章据此提示报价、修改范围与维护工时应**在接单时谈清**（F-057）——这是叙事里最容易被「赚到钱」掩盖的成本项。

## 文档结构

### concepts/ — 案例拆解

| 文档 | 主题 |
|---|---|
| [00-case-overview.md](concepts/00-case-overview.md) | 案例全景：人物与背景、时间线、产品与交易要素、与同分组既有束的关系 |
| [01-need-discovery-and-tooling.md](concepts/01-need-discovery-and-tooling.md) | 需求发现（观察店员的忙乱）与工具层降摩擦（Meoo 处理服务器/数据库/部署）+ 观察问题清单 |
| [02-customer-development-and-trial.md](concepts/02-customer-development-and-trial.md) | 客户开发与试用迭代：跑 5 家店的三类失败、话术导图、免费试用条件、驻店一周与数百次迭代 |
| [03-deal-boundaries-and-insights.md](concepts/03-deal-boundaries-and-insights.md) | 成交条款与边界（1 万元 / 一年免费维护 / 第二家未验证）、五条四元组洞察、两个可迁移模式 |

### references/ — 信源登记与核验

| 文档 | 说明 |
|---|---|
| [source-ledger.md](references/source-ledger.md) | S1–S5 信源台账 + F-001–F-060 编号事实 + 单源声明 + 放弃核验清单 |
| [verification.md](references/verification.md) | P0 核验报告（文章身份、时间线自洽、平台能力声明、金额与数量口径、可外推性边界） |

## 核心事实速查

| 项 | 值 |
|---|---|
| 文章 | 《纳尼?！真有人靠 Meoo 做副业月入过万！》（F-001） |
| 账号 / 发布 | 微信公众号「秒悟Meoo」/ 2026-10-29 01:00（F-002、F-003） |
| 主角 | 王玉丹，02 年出生（F-005） |
| 起点 | 2026-05 辞职；两个月自学 AI（F-006、F-009） |
| 需求场景 | 上海一家拼豆店，三四十张桌子，两名店员（F-011–F-013） |
| 产品 | 「豆掌柜」门店管理应用：桌位 / 计时 / 订单 / 核销 / 在线预约 / 数据仪表盘 / 套餐设置（F-027） |
| 开发起点 | 2026 年 7 月中旬；工具为秒悟 Meoo（F-020–F-022） |
| 客户开发 | 跑 5 家店 → 1 家愿试（F-028、F-034） |
| 试用机制 | 免费一个月 + 老板反馈不足；驻店一周；累计迭代数百次（F-036–F-042） |
| 成交 | 2026 年 8 月底，1 万元；含一年内免费维护及需求修改（F-043、F-045、F-046） |
| 事实规模 | F-001–F-060（60 条，全部主源单源） |

## 阅读路径

1. **我要了解这个案例本身** → [00-case-overview.md](concepts/00-case-overview.md)；
2. **我想知道需求是怎么被发现的** → [01-need-discovery-and-tooling.md](concepts/01-need-discovery-and-tooling.md)；
3. **我想知道客户是怎么找的、试用怎么做的** → [02-customer-development-and-trial.md](concepts/02-customer-development-and-trial.md)；
4. **我要评估风险、看可迁移模式** → [03-deal-boundaries-and-insights.md](concepts/03-deal-boundaries-and-insights.md)。

## 主题关联

- [秒悟实训案例](../miaowu-meoo-practice-cases/index.md)：同分组既有束——7 个实操场景 + 5 步应用搭建法，回答「怎么搭」；本束是**一个已走完全程的真实案例**，与之互补。
- [秒悟 Meoo 产品增长 Skill 包](../miaowu-growth-skills/index.md)：同分组既有束——按阶段选 Skill 的选型导航；本束对应其「获取用户 / 商业化」环节的**具体一次实践**。
- [秒悟应用赏金广场](../miaowu-bounty-plaza/index.md)：同分组既有束——平台侧共创计划与七阶段增长分类法；本束是该分类法在单个案例上的展开。
- [秒悟大使入驻指南](../miaowu-ambassador-guide/index.md)：同分组既有束——创作者激励体系，与本束的「个人用平台接单」形成供给侧对照。
- [秒悟产品功能全景指南](../miaowu-product-guide/index.md)：同分组既有束——官方文档教程，解释本束中「免服务器/数据库/部署」「生成访问链接」背后的平台能力面。

## 已知边界

- **单源自述案例**：文章由 Meoo 官方公众号发布（F-002），人物、金额、数量均无第三方核验；本束登记为「存在性证据」，不作可复制性结论。
- **无可复现操作**：源文无安装、配置、代码或参数流程，可复现性两问皆为「否」，**不设 `examples/`**。
- **结果不可外推**：源文自述「能否卖给第二家、第三家尚无答案」（F-047），主角已转向其他方向（F-048）。
- **量级为模糊表述**：「累计迭代数百次」（F-042）为文章定性表述，无精确计数。
- **工具能力为文章转述**：Meoo 对服务器/数据库/部署与访问链接的处理（F-024、F-025）为文章口径，未与官方文档逐条交叉。
- **时效敏感**：Meoo 平台能力与人物后续进展易变，`stale_after: 2027-04-29`。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
