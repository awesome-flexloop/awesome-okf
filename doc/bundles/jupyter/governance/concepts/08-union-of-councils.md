---
type: Concept
title: "理事会联盟（UoC）与选举人团"
description: "Union of Councils是所有子项目Council、常设委员会和工作组成员的联合，是EC选举的投票主体，体现Jupyter的分布式民主基础。"
tags: [union-of-councils, UoC, electorate, voting, democracy]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ec
    resource: /references/executive-council-source.md
    title: "执行委员会信源"
  - id: committees
    resource: /references/committees-source.md
    title: "委员会与工作组信源"
---

## 什么是理事会联盟

理事会联盟（Union of Councils，简称 UoC）是 Jupyter 治理中的**选举人团**，它不是一个常设决策机构，而是所有治理机构成员的联合。UoC 的核心职能是作为 EC 选举中社区代表席位的投票主体。

## UoC 的组成

UoC 由以下所有成员组成：

```
Union of Councils (UoC)
├── 所有 Subproject Councils 的成员
│   ├── Jupyter Frontends Council
│   ├── JupyterHub and Binder Council
│   ├── Jupyter Server Council
│   ├── Jupyter Widgets Council
│   ├── Jupyter Kernels Council
│   ├── Jupyter Foundations and Standards Council
│   ├── Jupyter Security Council
│   ├── Jupyter Accessibility Council
│   ├── Jupyter Book Council
│   ├── Voilà Council
│   └── ...（其他有独立Council的子项目）
├── 所有 Standing Committees 的成员
│   ├── DEI Committee
│   ├── CoC Incident Response Committee
│   ├── Conflict of Interest Committee
│   └── Community Advisory Panel
└── 所有 Working Groups 的成员
    ├── Trademark and Branding WG
    ├── Community Building WG
    ├── Media Strategy WG
    └── Documentation WG
```

每个属于上述任一 Council/Committee/WG 的个人都是 UoC 成员，在 EC 选举中拥有一票。

## UoC 在 EC 选举中的角色

EC 有6个席位，分为两部分选举：

| 选举人 | 席位数规则 |
|--------|-----------|
| **UoC** | 席位数与 EC 自选席位数相等，或多1席 |
| **现任 EC** | 剩余席位 |

这意味着 UoC 选举的席位总是**等于或多于** EC 自选的席位。这种设计确保了：

1. **社区代表性**：大多数 EC 成员由广泛的 UoC 选举产生
2. **机构连续性**：EC 保留部分自选席位以维持经验传承
3. **权力平衡**：社区不会完全"推翻"现有领导，但也确保新血液能进入

举例：如果某次选举 UoC 分配到3席，EC 自选3席；下次如果 UoC 分配到4席，则 EC 自选2席。具体分配遵循"UoC席位数 = EC自选席位数 或 EC自选席位数+1"的规则。

## UoC 成员的权利与义务

作为 UoC 成员，你有权：

- 在 EC 选举中**一人一票**投票选举 EC 成员
- 提名 EC 候选人（包括自荐）
- 作为候选人参与 EC 选举（前提是不违反任期限制）

需要注意的是，UoC **不是一个决策机构**——它不行使日常治理权力，只在 EC 选举时作为投票团体发挥作用。日常决策由各 Council/Committee/WG 按各自职责范围分别做出。

## 与其他治理机构的关系

```
UoC（选举人团）
  │
  │ 选举
  ▼
EC（最高决策机构）──┬──委派──→ SSC（软件决策）
  │                ├──委派──→ Standing Committees（常设非软件工作）
  │                └──委派──→ Working Groups（专项非软件工作）
  │                                    │
  └────── 成员构成 ────────────────────┘
         （各Councils/Committees/WGs成员 → UoC）
```

这形成了一个闭环：各治理机构的成员通过 UoC 选举产生 EC，EC 又委派授权给各治理机构。

## 选举资格

任何 UoC 成员都有资格成为 EC 候选人，前提是：
- 不违反 EC 任期限制（过去4年中未在 EC 服务3年以上）
- 不同时在 SSC 任职（EC 和 SSC 成员不可兼任）

## 反常识要点

- **UoC 不是"上议院"或"参议院"**：它不进行日常立法或监督，只在 EC 选举时作为选民团体存在。
- **一人一票不是"一项目一票"**：UoC 是按人投票而非按子项目/机构投票。一个人如果同时属于多个 Council/WG，也只有一票。
- **选举制度是"排序复选制"而非简单多数**：这确保获胜者获得更广泛的支持，而非仅靠简单多数票胜选（尤其是在多候选人竞争时）。

## 相关概念

- [执行委员会（EC）](/concepts/03-executive-council.md)
- [选举与投票机制](/concepts/10-elections-and-voting.md)
- [决策制定流程](/concepts/09-decision-making.md)
- [常设委员会与工作组](/concepts/07-committees-and-working-groups.md)
