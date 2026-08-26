---
type: Index
title: "governance 信源索引"
description: "jupyter/governance 仓库核心文档的信源登记索引。"
tags: [index, references, sources]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
---

# governance 信源索引

本目录登记 jupyter/governance 仓库中所有核心原始文档的路径和内容摘要，供概念文档通过 `sources` 字段引用。

| 信源文件 | 对应原始文档 | 内容 |
|---------|------------|------|
| [overview-source.md](overview-source.md) | docs/overview.md | 治理模型总览：三大主体、子项目、委员会、UoC、DC |
| [executive-council-source.md](executive-council-source.md) | docs/executive_council.md | 执行委员会（EC）：职责、选举、任期、罢免 |
| [ssc-source.md](ssc-source.md) | docs/software_steering_council.md | 软件指导委员会（SSC）：软件决策、JEP、安全、成员构成 |
| [decision-making-source.md](decision-making-source.md) | docs/decision_making.md | 决策制定流程：共识寻求→投票→参与率→记录 |
| [subprojects-source.md](subprojects-source.md) | docs/software_subprojects.md, docs/list_of_subprojects.md, docs/newsubprojects.md | 软件子项目：责任、分类、准入标准、孵化流程 |
| [committees-source.md](committees-source.md) | docs/standing_committees_and_working_groups.md, docs/list_of_standing_committees_and_working_groups.md | 常设委员会与工作组：区别、职责、当前列表 |
| [coc-source.md](coc-source.md) | docs/conduct/code_of_conduct.md, docs/conduct/enforcement.md | 行为准则：期望行为、举报、执行手册、处理措施 |
| [trademarks-license-source.md](trademarks-license-source.md) | docs/trademarks.md, docs/projectlicense.md | 商标政策与代码许可证（BSD-3-Clause） |
| [foundation-dc-source.md](foundation-dc-source.md) | docs/jupyter_foundation.md, docs/distinguished_contributors.md | Jupyter 基金会与杰出贡献者制度 |
| [elections-papers-source.md](elections-papers-source.md) | docs/elections/README.md, docs/papers.md | STV选举计票工具与学术论文流程 |
| [infrastructure-history-source.md](infrastructure-history-source.md) | noxfile.py, README.md, docs/archive/governance.md, docs/_data/ | 文档构建基础设施（MyST+Nox）与BDFL历史 |

```{toctree}
:hidden:
:maxdepth: 7

coc-source
committees-source
decision-making-source
elections-papers-source
executive-council-source
foundation-dc-source
infrastructure-history-source
overview-source
ssc-source
subprojects-source
trademarks-license-source
```
