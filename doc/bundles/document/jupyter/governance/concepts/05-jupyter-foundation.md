---
type: Concept
title: "Jupyter 基金会"
description: "Jupyter Foundation是Linux Foundation下的定向基金，为Jupyter提供资金资源和战略咨询，EC成员在基金会理事会任职确保社区主导。"
tags: [jupyter-foundation, linux-foundation, funding, nonprofit, governing-board]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: foundation
    resource: /references/foundation-dc-source.md
    title: "基金会与DC信源"
---

## Jupyter 基金会的定位

Jupyter Foundation 是在 **Linux Foundation 501(c)(6)** 下设立的**定向基金**（directed fund），其核心目的是：

- **筹集资金**：为 Project Jupyter 及其使命筹集资金
- **预算管理**：制定和批准年度预算，指导资金使用
- **战略咨询**：为项目提供战略层面的建议
- **资源支撑**：为项目运营提供财务和组织资源

需要注意的是，Jupyter Foundation **不是治理主体**——它不做项目方向或技术决策。项目方向由 EC/SSC 等社区治理机构决定，基金会是这些决策的资源支撑者。

## 法律架构

```
Project Jupyter（社区治理）
       │
       │  EC 成员在理事会任职
       ▼
Jupyter Foundation（LF 定向基金，501(c)(6)）
       │
       │  资产托管
       ▼
Linux Foundation（法律实体）
       │
       │  上级非营利
       ▼
LF Charities（501(c)(3)，Jupyter 商标持有方）
```

Jupyter 的法律实体关系涉及三个层次：
1. **LF Charities**：501(c)(3) 公益慈善组织，持有 Jupyter 商标，是 Jupyter 的上级非营利法人
2. **Linux Foundation**：为 Jupyter 提供资产托管服务
3. **Jupyter Foundation**：501(c)(6) 定向基金，专注于资金筹集和行业合作

## 理事会构成

Jupyter Foundation 理事会（Governing Board）由以下成员组成：

| 成员类别 | 人数 | 说明 |
|---------|------|------|
| **EC 全体成员** | 6人 | 确保社区治理机构对基金会的控制权 |
| **Premier Member 代表** | 每个 Premier Member 1名 | 付费最高级别会员，通常为大公司 |
| **General Member 代表** | 1-3名（总计） | 普通级别会员的集体代表 |

这种设计确保了**社区代表在理事会中占主导地位**——6名 EC 成员加上少数企业代表，使得 Jupyter 的方向始终由社区而非企业赞助者主导。

## 理事会职责

- **支持项目使命**：所有理事会成员的首要职责
- **整体管理**：基金会的日常运营和管理
- **批准年度预算**：审批 Jupyter Foundation 资金的使用方向
- **批准章程变更**：修改基金会章程需要理事会批准

## 会员级别

Jupyter Foundation 设有不同级别的企业会员：

- **Premier Members**：最高级别，在理事会拥有独立席位
- **General Members**：普通级别，集体拥有1-3个理事会席位

企业通过缴纳会员费为 Jupyter 提供资金支持，同时获得在基金会理事会的话语权，但不能控制项目方向。

## Team Compass

Jupyter Foundation 理事会的运营信息发布在：[jupyter-governance.github.io/jupyter-foundation-governing-board](https://jupyter-governance.github.io/jupyter-foundation-governing-board)

## 基金会章程

Jupyter Foundation 的正式章程文档：[Jupyter Foundation Charter (PDF)](https://cdn.platform.linuxfoundation.org/agreements/jupyter-foundation.pdf)

## 反常识要点

- **基金会不是"老板"**：与一些人想象的"基金会控制开源项目"不同，Jupyter 中是社区治理机构（EC）控制基金会理事会，而非反过来。EC 全体成员在理事会任职，确保了社区对资金的主导权。
- **501(c)(6) 而非 501(c)(3)**：Jupyter Foundation 是 501(c)(6)（行业协会类），而非典型的 501(c)(3)（公益慈善类）。这与其作为"定向基金"服务于项目生态建设的定位一致。商标持有和慈善接收方是 LF Charities（501(c)(3)）。
- **企业会员不等于控制权**：虽然有企业代表在理事会，但 EC 成员占多数，且基金会不决定技术方向。

## 相关概念

- [三主体治理模型](01-governance-model.md)
- [执行委员会（EC）](03-executive-council.md)
- [商标政策与许可证](14-trademarks-and-licensing.md)
