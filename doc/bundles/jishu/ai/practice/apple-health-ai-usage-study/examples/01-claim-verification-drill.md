---
type: example
title: 01 · 一条声明的四层核验演练
description: 以「研究数据不会用于训练 AI 模型」为例的纸面判读演练，示范官方原文、媒体转述、未披露项与边界声明四层分离
tags: [example, drill, source-layering, verification, teaching]
generated:
  by: workbuddy/seven-concepts-cmd
  at: "2026-11-17T12:30:00+08:00"
status: stable
stale_after: 2027-05-17
---

# 01 · 一条声明的四层核验演练

> 📝 本页是**纸面练习**，不需要安装 App、不需要参与研究，也不构成任何医疗或参与建议。目标是练会「读到一句话时怎么分层」。

## 题目

> 「Apple 说这次研究的数据不会用来训练 AI。」

请用 [06 篇「公告四层核验」](../concepts/06-transferable-pattern.md) 的前四层拆这句话。

## 第一层：官方原文

Apple Newsroom 稿原文（S1）：

> "The study is designed from the ground up with privacy protections, transparency, and clinical guardrails, and **study data will not be used to train AI models**."

登记为 **F-030**。同一段还给出：参与者保留是否分享 HealthKit 指标与问卷回答的控制权（F-031）；Apple 已实施安全措施保护其持有的研究数据与参与者信息机密性（F-032）。

**结论**：这句话在官方稿中有直接对应，属一手事实。

## 第二层：媒体转述

| 报道 | 怎么写 | 与官方的距离 |
|------|--------|--------------|
| iClarified（S6） | "Study data will not be used to train AI models" | 基本直译，无新增 |
| MacRumors（S4） | 同义改写，并追加去标识化、24 小时删除 | 追加的两条**不在官方稿** |
| Data Studios（S8） | 把「不训练模型」列为两条「中心声明」之一 | 归类整理，未新增事实 |
| 部分聚合稿（S9） | 与「隐私设计」合并成一句概括 | 压缩后容易丢失「参与者控制权」这一并列承诺 |

**练习动作**：把每条转述里**官方稿没有的词**圈出来，单独送到第三层。

## 第三层：未披露项

官方稿没有写明的相邻问题（不要替它回答）：

- 「不用于训练」覆盖哪些数据形态——提问文本、HealthKit 指标、问卷回答、评分行为？
- 数据去向的端到端链路、留存期限、第三方处理方的角色边界；
- 撤回参与后既有数据的处置；
- 「训练」是否包含微调、评测、人工审核等相邻用途。

媒体给出的「问题送达前去标识化」「24 小时内删除问答数据」（F-035、F-036）若被拿来回答上述问题，就犯了**用二手补一手**的错误。本束的处置是登记为媒体单源，不进入结论。

## 第四层：边界声明

把结论写成带边界的一句话：

> ✅ 可写：Apple 在其 2026-11-15 官方公告中声明，本研究数据不会用于训练 AI 模型（F-030）；同一段并列承诺了参与者对 HealthKit 指标与问卷回答的分享控制权。
>
> ❌ 不可写：「Apple 保证所有健康数据都不用于任何 AI 用途」「数据会被立即删除」「因此可以放心输入任何健康信息」。

## 换成另一句试试

请对以下任一句重做四层，答案可在 [verification.md](../references/verification.md) 的未披露项登记里核对：

1. 「这个 App 能帮我准备就诊清单。」
2. 「提问会先去标识化再发给合作方。」
3. 「iPhone 15 Pro 就能参加，没有别的要求。」

> 💡 判分只看一条：**有没有一句话替官方补了它没说的答案**。
