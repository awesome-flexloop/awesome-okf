---
type: Reference
title: "团队成员页面信源"
description: "docs/team.md 页面的信源登记，包含 Frontends Council 现任成员列表和 SSC 代表信息。"
tags: [reference, source, team, council, members]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T11:35:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:35:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: team-md
    resource: https://github.com/jupyterlab/frontends-team-compass/blob/main/docs/team.md
    title: "docs/team.md"
  - id: contributors-yaml
    resource: https://github.com/jupyterlab/frontends-team-compass/blob/main/docs/team/contributors.yaml
    title: "docs/team/contributors.yaml"
---

# 团队成员页面信源

**原始文件路径**：`docs/team.md` + `docs/team/contributors.yaml`

**内容摘要**：

team.md 列出 Jupyter Frontends Council 的现任成员（随机顺序排列）。成员列表通过 MyST 的 `eval-rst` 指令包含 `team/active.txt` 文件（由 gen_contributors.py 脚本从 contributors.yaml 自动生成的 HTML 表格）。

**关键信息**：
- Council 成员积极参与 JupyterLab GitHub 组织和 Jupyter Notebook 项目的开发、维护、规划和讨论
- SSC（Software Steering Council）代表：每个 Jupyter 官方子项目有一名 SSC 代表，由 Frontends 成员选举产生，每年1月应重新选举
- 现任 SSC 代表：Jérémy Tuloup（@jtpio）
- contributors.yaml 由 jupyterlab/council 仓库的 GitHub Actions workflow 自动生成，不应手动编辑
- 截至 2026-04-27，活跃成员共19人，来自 QuantStack、Anaconda、Apple、AWS、IBM、Bloomberg、UC Berkeley 等机构

**关键事实锚点**：
- F-011: 成员列表自动生成，不手动编辑
- F-012: 现任 SSC 代表为 Jérémy Tuloup
- F-028: gen_contributors.py 构建时生成 HTML 表格
