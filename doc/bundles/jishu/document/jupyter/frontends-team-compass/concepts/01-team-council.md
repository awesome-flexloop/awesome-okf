---
type: Concept
title: "Frontends Council 架构"
description: "理解 Jupyter Frontends Council 的三层成员体系、职责划分、加入流程和维护机制。"
tags: [jupyter, frontends, council, membership, governance, release-team, admin-team]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T11:36:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:36:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: team
    resource: /references/team-source.md
    title: "团队成员页面信源"
  - id: becoming-member
    resource: /references/becoming-member-source.md
    title: "成员准入指南信源"
---

# Frontends Council 架构

Jupyter Frontends Council 是 JupyterLab 前端子项目的决策机构，采用**三层成员体系**：普通 Council 成员 → Release Team（发布组）→ Admin Team（管理组）。三层呈金字塔结构，权限逐级递增，但所有决策均以共识为基础。

## 三层成员体系

```
                    ┌─────────────────────┐
                    │    Admin Team       │
                    │  （最多7人，Owner）  │
                    │  SSC代表自动加入     │
                    │  EC必须占至少1席     │
                    └─────────┬───────────┘
                              │ 包含
                    ┌─────────▼───────────┐
                    │   Release Team      │
                    │  （发布权限组）       │
                    │  PyPI/NPM/conda-forge│
                    └─────────┬───────────┘
                              │ 包含
                    ┌─────────▼───────────┐
                    │  Council Members    │
                    │  （无人数上限）       │
                    │  投票权/提名权       │
                    └─────────────────────┘
```

### Council 成员（基础层）

Council 成员是 Frontends 团队的核心参与者，**无人数上限**——这遵循 Jupyter 治理模型鼓励大型、高参与度决策机构的原则。

**核心权利**：

| 权利 | 说明 |
|------|------|
| 投票权 | 投票情境下有一票表决权 |
| 提名权 | 可提名新成员加入 Council |
| SSC 代表选举权 | 可选举和被选举为 SSC 代表 |
| 法定人数计入 | 投票时计入 quorum |

**核心义务**：

- 须由现任成员提名并获得内部共识
- 每年参与至少 **2/3** 的投票
- 积极参与会议（同步或异步均可）
- Watch team-compass 和 council 仓库
- 长期不在时告知团队

### Release Team（发布组）

任何 Council 成员均可申请加入 Release Team（建议通过私聊渠道申请，以安全为由限制信息曝光）。Release Team 成员获得各包管理平台的发布权限：

| 平台 | 权限级别 |
|------|---------|
| GitHub JupyterLab 组织 | release team 成员 |
| PyPI Jupyter 组织 | JupyterLab team 管理员 |
| NPM jupyterlab 组织 | jupyterlab team 成员 |
| conda-forge jupyterlab recipes | maintainer 权限 |

Release Team 成员可以发布主要的 JupyterLab 相关包，并在已发布包出现问题时快速响应（如损坏的包需要紧急修复重发）。

### Admin Team（管理组）

Admin Team 是最高权限层，有以下特殊规则：

- **人数上限**：最多 **7 名**管理员
- **自动成员**：SSC 代表自动成为 Admin
- **EC 保障席位**：Executive Council 必须拥有至少一个 Admin 席位；若最后一位 EC 管理员辞职，EC 必须提名新管理员
- **权限**：GitHub/PyPI/NPM 组织的 **Owner** 级别权限，conda-forge maintainer 权限
- **职责**：维护 Council 成员和 Release Team 成员的资格管理（添加/移除成员）

## 成员加入流程

新成员必须通过**提名-共识-邀请**三步流程：

1. **内部共识**：提名者先在 Council 内部讨论，确认有广泛共识；如共识不明显，可进行内部投票（保护候选人隐私）
2. **正式联系**：Council 成员联系候选人，询问其是否有兴趣加入，并提供成员指南
3. **加入确认**：候选人理解职责并确认意愿后正式加入

新成员的期望标准是：已经是社区中**持续、积极、有建设性**的参与者，且有意向**长期投入**（至少一年）。贡献不限于代码——协助论坛/Issue、审查 PR、参与会议等非代码贡献同样被认可。

## 成员维护机制

所有三个层级均采用**半年活跃度确认**机制：

1. 每 6 个月，bot 在 council 仓库开一个 Issue
2. 成员需在 3 周内回复确认仍然活跃
3. 回复"否"则自动移除
4. 不回复则个人联系；一个月仍不回复则移除
5. 移除的 Release/Admin 成员同时撤销各平台发布/管理权限

## SSC 代表

每个 Jupyter 官方子项目向 **Software Steering Council**（软件指导委员会）派遣一名代表。Frontends 的 SSC 代表：

- **产生方式**：由 Council 成员选举产生
- **任期**：每年1月应重新选举
- **现任代表**：Jérémy Tuloup（@jtpio，QuantStack）
- **特殊地位**：自动成为 Admin Team 成员

## 成员数据的自动管理

截至 2026 年 4 月，活跃 Council 成员共 19 人，来自 QuantStack、Anaconda、Apple、AWS、IBM、Bloomberg、UC Berkeley 等组织。成员列表存储在 `contributors.yaml` 中，由 [jupyterlab/council](https://github.com/jupyterlab/council) 仓库的 GitHub Actions workflow 自动更新，**不应手动编辑**。Sphinx 构建时通过 `gen_contributors.py` 脚本生成 HTML 展示表格。

## 相关概念

- [决策制定流程](03-decision-making.md) — 共识优先、投票兜底的决策机制
- [成员行为指南](04-member-guide.md) — 成员日常职责、沟通渠道和PR合并规范
- [仓库简介](00-introduction.md) — 回到仓库定位与整体结构
