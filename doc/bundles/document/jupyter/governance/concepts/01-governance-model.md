---
type: Concept
title: "三主体治理模型"
description: "Jupyter 以执行委员会(EC)、软件指导委员会(SSC)和Jupyter基金会为三大支柱，辅以子项目、委员会、工作组的分层委派治理架构。"
tags: [governance-model, three-bodies, EC, SSC, foundation, architecture]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: overview
    resource: /references/overview-source.md
    title: "治理总览信源"
  - id: ec
    resource: /references/executive-council-source.md
    title: "执行委员会信源"
  - id: ssc
    resource: /references/ssc-source.md
    title: "SSC信源"
  - id: foundation
    resource: /references/foundation-dc-source.md
    title: "基金会与DC信源"
---

## 三主体治理架构

Jupyter 当前的治理模型（2022年12月起实施）以**三个互补的主体**为支柱：

```
┌─────────────────────────────────────────────────────┐
│                  Executive Council (EC)              │
│          最终决策者 · 全维度责任 · 6名成员            │
│  ┌───────────┐  ┌────────────┐  ┌────────────────┐  │
│  │ 委派给SSC  │  │ 委派给委员会│  │ 委派给工作组    │  │
│  └─────┬─────┘  └─────┬──────┘  └───────┬────────┘  │
│        │              │                 │           │
│  ┌─────▼─────┐  ┌─────▼──────┐  ┌──────▼────────┐  │
│  │    SSC    │  │  常设委员会 │  │   工作组      │  │
│  │ 软件决策   │  │  DEI/CoC等 │  │ 商标/社区/媒体│  │
│  └─────┬─────┘  └────────────┘  └───────────────┘  │
│        │                                            │
│  ┌─────▼──────────┐                                 │
│  │ 软件子项目自治  │◄── 日常技术决策自主              │
│  └────────────────┘                                 │
├─────────────────────────────────────────────────────┤
│            Jupyter Foundation (LF 定向基金)           │
│         资金资源 · 战略咨询 · 理事会含EC成员          │
└─────────────────────────────────────────────────────┘
```

## 主体一：Executive Council (EC)

执行委员会是 Jupyter 项目的**最高决策机构**，对项目的所有维度（包括但不限于软件、法律、财务、社区、运营、多元公平包容等）负有最终责任。

- **规模**：6名成员，任期2年
- **核心定位**：最终决策者和项目使命的守护者
- **关键权力**：可推翻 SSC/子项目/委员会/工作组的决定（特殊情况下作为最终仲裁者）
- **选举**：由理事会联盟（UoC）和 EC 自身分别选举产生
- **Team Compass**：https://ec.jupyter.org

## 主体二：Software Steering Council (SSC)

软件指导委员会管辖 Jupyter 项目中**与软件相关的跨项目决策**，主要关注各子项目之间的协调和影响多个子项目的决策。

- **核心定位**：软件领域的协调者和跨项目决策者
- **成员构成**：每个官方软件子项目派一名代表，部分委员会/工作组也有代表
- **无固定任期**：各子项目自行决定代表轮换
- **关键职责**：JEP 流程管理、安全漏洞管理、孵化/归档流程、跨项目架构标准
- **自治原则**：SSC 未明确参与的技术决策自动下放给各子项目自主管理

## 主体三：Jupyter Foundation

Jupyter 基金会是在 Linux Foundation 501(c)(6) 下设立的**定向基金**，为 Project Jupyter 提供资金资源和战略咨询。

- **核心定位**：资金与资源支撑
- **理事会构成**：EC 全体成员 + Premier Member 代表 + General Member 代表
- **职责**：批准年度预算、批准章程变更、支持项目使命

## 委派与自治

Jupyter 治理的核心设计原则是**委派与自治**：

1. **EC 委派**：EC 将日常软件管理委派给 SSC，将非软件工作委派给常设委员会和工作组
2. **子项目高度自治**：SSC 未明确介入的技术决策，各子项目自主管理（创建仓库、日常开发、发布等）
3. **委员会/工作组在章程范围内自主决策**：在各自章程定义的范围内，常设委员会和工作组可自主做出决策

## 共享决策领域

并非所有决策都由单一主体做出。以下事项需要 **EC 和 SSC 分别独立投票通过**（双重批准）：

- 修改 Jupyter 治理模型本身
- 创建新的官方子项目
- 移除现有子项目

这种双重批准机制确保了治理变更和生态扩张需要同时获得"全维度治理者"和"软件代表"的同意。

## 其他治理组件

三大主体之外，还有几个重要组件：

| 组件 | 定位 |
|------|------|
| **Community Advisory Panel** | 社区顾问小组，向 EC 提供超越活跃社区的视角和人脉 |
| **Union of Councils (UoC)** | 理事会联盟，所有子项目 Council + 常设委员会 + 工作组成员的联合，是 EC 的选举人团 |
| **Distinguished Contributors** | 杰出贡献者，终身荣誉，有权选举新成员 |

## 反常识要点

- **与多数开源项目不同**，Jupyter 的最终决策权不在纯技术机构（SSC），而在负责全维度的 EC。这反映了 Jupyter 作为一个大型成熟项目，其法律、财务、社区运营等非技术事务与技术事务同等重要。
- **SSC 不是"技术独裁者"**：它的主要角色是协调和跨项目决策，日常技术决策大量下放给子项目。
- **基金会不是治理主体**：Jupyter Foundation 是资源提供者而非决策者，EC 成员在基金会理事会中任职，确保项目方向由社区主导。

## 相关概念

- [执行委员会详解](/concepts/03-executive-council.md)
- [软件指导委员会详解](/concepts/04-software-steering-council.md)
- [Jupyter 基金会](/concepts/05-jupyter-foundation.md)
- [决策制定流程](/concepts/09-decision-making.md)
- [从 BDFL 到分布式治理](/concepts/02-history-and-evolution.md)
