---
type: Concept
title: "从 BDFL 到分布式治理的历史演进"
description: "Jupyter 在2022年12月从BDFL+指导委员会模式转型为三主体分布式治理的背景、过程和意义。"
tags: [history, bdfl, evolution, governance-transition, fernando-perez]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: overview
    resource: /references/overview-source.md
    title: "治理总览信源"
  - id: infra-history
    resource: /references/infrastructure-history-source.md
    title: "基础设施与历史信源"
---

## 旧治理模型：BDFL + Steering Council

2022年12月之前，Jupyter（及其前身 IPython）长期采用开源社区常见的 **BDFL（Benevolent Dictator For Life，终身仁慈独裁者）+ Steering Council（指导委员会）** 模式：

- **BDFL**：Fernando Pérez（[@fperez](https://github.com/fperez)），IPython/Jupyter 的创始人，拥有最终决策权
- **Steering Council**：由核心贡献者组成的指导委员会，协助 BDFL 进行日常决策
- **NumFOCUS Subcommittee**：与 NumFOCUS（Jupyter 的上级非营利组织）对接的小组委员会

这种模式在项目早期非常高效——创始人有清晰愿景，快速决策推动项目发展。但随着 Jupyter 成长为涵盖多个子项目（JupyterLab、JupyterHub、Jupyter Server、nbformat、ipywidgets 等）、拥有数百名核心贡献者、年预算达数百万美元的大型生态系统，BDFL 模式的可持续性面临挑战。

## 2022年12月：治理模式转型

2022年12月，Jupyter 正式实施新的治理模型，这是开源社区中罕见的**创始人主动推动权力分散化**的成功案例。

### 关键变化

| 方面 | 旧模型 | 新模型 |
|------|--------|--------|
| 最终决策者 | BDFL (Fernando Pérez) | Executive Council (6人，选举产生) |
| 软件决策 | Steering Council | Software Steering Council (子项目代表制) |
| 法律/财务 | BDFL + NumFOCUS | EC + Jupyter Foundation (Linux Foundation) |
| 非软件工作 | 无正式结构 | 常设委员会 + 工作组 |
| 选举机制 | BDFL 指定核心成员 | UoC 民主选举，排序复选制 |
| 行为准则执行 | 非正式流程 | 正式 CoC 委员会 + 执行手册 |

### BDFL 的自愿卸任

Fernando Pérez 在转型中**自愿放弃**了 BDFL 角色。这不是被迫的权力交接，而是主动的制度设计——他和核心团队认识到，一个健康的开源项目不能永远依赖单一创始人。新治理模型的 bootstrapping 文档详细记录了首届 EC 的创建过程。

### 旧机构的处置

- BDFL 职位：废除，Fernando Pérez 成为普通社区成员（仍可通过选举进入 EC）
- 旧 Steering Council：解散
- NumFOCUS Subcommittee：解散
- 旧治理文档：归档至 `docs/archive/governance.md`

## 转型的意义

Jupyter 的治理转型在开源史上具有重要意义：

1. **可持续性优先**：项目不再依赖任何单一个体，即使创始人离开或减少参与，项目仍能正常运作
2. **制度化分权**：通过 EC/SSC/Foundation 三权分立，避免权力过度集中
3. **正式化非软件工程**：DEI、CoC、社区建设等"软"议题获得了与软件开发同等的制度地位
4. **可复制的模板**：为其他大型开源项目（尤其是从 BDFL 模式"毕业"的项目）提供了可参考的转型路径

## Bootstrapping 文档

转型过程中产生了两个重要的 bootstrapping 文档：

- [bootstrapping_executive_council.md](https://github.com/jupyter/governance/blob/main/docs/bootstrapping_executive_council.md)：记录首届 EC 的创建过程
- [bootstrapping_subproject_councils.md](https://github.com/jupyter/governance/blob/main/docs/bootstrapping_subproject_councils.md)：记录各子项目 Council 的初始建立

这些文档对于研究开源项目治理转型具有一手资料价值。

## 当前状态

转型后的治理模型从2022年12月运行至今，经历了多次 EC 选举、新子项目加入（如 Jupyter Book）、工作组和委员会的运作，展现了分布式治理模型的可行性。

## 反常识要点

- **不是所有开源项目都适合 BDFL 到分布式的转型**：转型需要成熟的社区、足够多的活跃贡献者、以及愿意放弃权力的创始人。小项目强行模仿可能导致决策瘫痪。
- **BDFL 模式本身不是问题**：在项目早期，BDFL 模式往往是最高效的。问题出在项目规模增长后，单一决策者的带宽和认知成为瓶颈。
- **转型不是革命**：Jupyter 的转型是渐进的、有文档记录的、和平的权力交接，而非社区分裂或"fork"。

## 相关概念

- [三主体治理模型总览](01-governance-model.md)
- [执行委员会详解](03-executive-council.md)
- [理事会联盟与选举人团](08-union-of-councils.md)
- [选举与投票机制](10-elections-and-voting.md)
