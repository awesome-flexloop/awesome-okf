---
type: concept
title: 06 · 可迁移模式「公告四层核验」
description: 从厂商公告提炼的可迁移判读模式——触发场景、五步做法、四条反模式、检验标准与跨领域迁移示例；单案例 L1 待验证
tags: [pattern, announcement, source-layering, adversarial-review, transferable, okf-wiki, l1]
generated:
  by: workbuddy/seven-concepts-cmd
  at: "2026-11-17T12:30:00+08:00"
status: stable
stale_after: 2027-05-17
sources:
  - id: apple-newsroom-2026-11-15
    resource: https://www.apple.com/newsroom/2026/11/apple-launches-research-study-to-explore-the-use-of-ai-for-health/
    title: 本模式的主案例来源（Apple Newsroom 官方公告）
  - id: okf-u2flash-bundle
    resource: ../../u2flash-free-month/references/verification.md
    title: 库内旁证：同组资讯核验束的 P0 核验与对抗审查记录
---

# 06 · 可迁移模式「公告四层核验」

> 模式名称：**公告四层核验**（5 字）
> 成熟度：**L1 · 单案例待验证**（主案例仅本束一项；库内同组束作旁证，尚未做过跨领域对照实验）

## 触发场景

**适用于**：把厂商/机构的一手公告（发布稿、更新说明、研究启动公告）转成教学材料、知识包或判读报告，且公告会被大量二手媒体转述时。

**不适用于**：

- 材料本身是二手汇总、无一手原文可回查；
- 目标是复现产品操作（应走实测教程，而非判读）；
- 涉及需要专业资质判断的医疗、法律结论（本模式只处理「谁说了什么」，不替代专业判断）。

## 核心做法（五步）

| 步 | 动作 | 产出 |
|----|------|------|
| 1 | **划边界**：先写「是什么 / 不是什么」两张清单，锁定研究对象、载体、发布状态 | 边界块（见 [00 篇](00-study-overview.md)） |
| 2 | **定一手**：确定唯一官方原文，逐句登记事实并连续编号（F-xxx） | 事实清单（见 [facts.md](../references/facts.md)） |
| 3 | **分二手**：把媒体补充逐条挂到原始出处；多家转引同一出处时仍只算一个独立信源，标「单源/未证实」 | 信源分层表（见 [source-manifest.md](../references/source-manifest.md)） |
| 4 | **记空白**：单列「官方未说明」清单，不推测、不用同类项目经验跨对象套用 | 未披露项登记（见 [verification.md](../references/verification.md)） |
| 5 | **过对抗**：四视角攻击产出，至少采纳两条并实际改写正文，留痕 | 对抗审查记录 |

## 反模式（四条，均来自实际案例教训）

| # | 反模式 | 实际教训 |
|---|--------|----------|
| 1 | **多家媒体 = 多方印证** | 本例中「24 小时删除问答数据」被多家报道转述，追到源头仍是 MacRumors 一处（部分报道还注明经 CNET / 9to5Mac 二手转引，F-036）→ 已降级为媒体单源 |
| 2 | **用合作方能力数字给研究目标背书** | OpenEvidence 的 USMLE 分数、注册医师数、估值（S10、S14）与本研究「测什么」无关；[01 篇](01-four-measurement-axes.md) 曾面临把它写进评测对照的诱惑 → 已隔离到背景层 |
| 3 | **把研究公告读成产品发布** | 媒体标题普遍写「Apple 推出健康 AI」，而官方稿是独立研究 App、未宣布 Siri / 健康 App 集成（F-002、F-003）→ 已在束首页与 00 篇加统一边界块 |
| 4 | **跨对象套用规则** | 2025 Apple Health Study 官网写明「可随时退出」，不代表 2026 本研究同样如此（S12）→ [04 篇](04-eligibility-and-enrollment.md) 已把它列为未披露项，不套用 |

反模式 1 与库内 [u2flash-free-month](../../u2flash-free-month/references/verification.md) 处理「无限量 vs RPM/TPM 限流」的口径矛盾同源：**流传广的表述最需要回到一手参数卡**。

## 检验标准

做完这五步，应满足：

1. 任一结论句都能指回 F 编号或明确标注「媒体单源/未证实」；
2. 「官方未说明」清单非空，且正文没有任何一句替官方补答案；
3. 边界块出现在知识包首页，而非埋在末页；
4. 对抗审查记录中至少两条意见导致了**正文可见的改写**（本束为 5 条，见 [verification.md](../references/verification.md)）。

## 跨领域迁移示例

**开源项目 Release Notes 教学化**：把某框架的 `v2.0` 发布说明当一手（第 2 步），社区公众号的「十大新特性」当二手（第 3 步），把「性能提升 3×」的测试环境、基准版本、是否官方实测登记为未披露项（第 4 步），再让新人视角检查「升级前要改什么」是否被说明（第 5 步）。四层结构不变，只换信源类型——**先划边界、再定一手**这一步在任何领域都先于事实摘录。

同理可迁移到：医学科普稿的「研究结论 vs 媒体报道」判读、上市公司公告的「正式披露 vs 解读文章」分层。

## 与本知识库的关系

本模式可直接补入 [AI 工程方法论](../../ai-engineering-methodology/index.md) 的方法论谱系；其第 5 步与七概念方法论的 V（对抗审查）门同构。作为 L1 模式，建议在下一次「官方公告 → OKF 知识包」任务中复用并记录是否仍成立，届时升级为 L2。
