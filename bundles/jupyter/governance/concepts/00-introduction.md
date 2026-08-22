---
type: Concept
title: "Jupyter Governance 仓库简介"
description: "jupyter/governance 仓库的定位、内容结构、在线发布地址和文档许可证说明。"
tags: [introduction, overview, governance, repository]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: readme
    resource: /references/infrastructure-history-source.md
    title: "README.md 与仓库基础设施信源"
  - id: intro
    resource: /references/overview-source.md
    title: "治理总览信源"
---

## 什么是 jupyter/governance

`jupyter/governance` 是 Project Jupyter 的**治理文档仓库**，其目的是将 Jupyter 项目的治理流程正式化、文档化。它不是代码库，而是一个**纯文档仓库**，记录了 Jupyter 项目从决策机制、组织架构、行为准则到商标许可的全套治理制度。

该仓库的文档在线发布地址为 [jupyter.org/governance](https://jupyter.org/governance)。

## 仓库包含什么

governance 仓库涵盖 Jupyter 项目治理的方方面面：

| 主题 | 核心文档 |
|------|---------|
| 治理模型总览 | [overview.md](01-governance-model.md) |
| 执行委员会 (EC) | [executive_council.md](/concepts/03-executive-council.md) |
| 软件指导委员会 (SSC) | [software_steering_council.md](/concepts/04-software-steering-council.md) |
| 软件子项目体系 | [software_subprojects.md](/concepts/06-software-subprojects.md) |
| 常设委员会与工作组 | [standing_committees_and_working_groups.md](/concepts/07-committees-and-working-groups.md) |
| 决策制定流程 | [decision_making.md](/concepts/09-decision-making.md) |
| 行为准则 (CoC) | [conduct/code_of_conduct.md](/concepts/13-code-of-conduct.md) |
| 商标政策 | [trademarks.md](/concepts/14-trademarks-and-licensing.md) |
| 新子项目准入 | [newsubprojects.md](/concepts/11-new-subprojects.md) |
| 选举机制 | [elections/](/concepts/10-elections-and-voting.md) |
| 杰出贡献者 | [distinguished_contributors.md](/concepts/12-distinguished-contributors.md) |
| 学术论文流程 | [papers.md](/concepts/15-academic-papers.md) |

## 文档许可证

治理文档本身采用 **CC0 许可证**（Creative Commons Zero，公有领域奉献），这意味着在法律允许的范围内，Project Jupyter 放弃了治理文档的所有版权和邻接权，任何人都可以自由使用、修改和分发这些文档。

这与 Jupyter 代码的许可证（BSD-3-Clause）不同——代码保留版权但开源，而治理文档直接奉献给公有领域。

## 文档构建与发布

文档使用 [MyST](https://mystmd.org)（Markedly Structured Text）构建系统，通过 [nox](https://nox.thea.codes) 任务运行器管理构建流程：

```bash
# 构建 HTML 文档
nox -s docs

# 启动热重载开发服务器
nox -s docs-live
```

领导层目录（成员列表等）从 `docs/_data/` 目录下的 YAML 结构化数据动态生成，而非硬编码在 Markdown 中。构建产物通过 GitHub Pages 自动部署到 jupyter.org/governance。

## 与 Jupyter 生态的关系

governance 仓库是理解 Jupyter 项目如何运作的"宪法"——它定义了谁说了算、决策怎么做、谁能加入、违规如何处理。对于希望：

- **贡献代码**到 Jupyter 各子项目的开发者
- **参与社区治理**（如加入委员会、发起投票）的贡献者
- **理解开源项目治理最佳实践**的研究者
- **在自己的项目中借鉴治理模式**的开源维护者

这个仓库都是极具参考价值的学习材料。

## 相关概念

- [三主体治理模型总览](/concepts/01-governance-model.md)
- [从 BDFL 到分布式治理的历史演进](/concepts/02-history-and-evolution.md)
- [文档基础设施与构建系统](/concepts/16-doc-infrastructure.md)
