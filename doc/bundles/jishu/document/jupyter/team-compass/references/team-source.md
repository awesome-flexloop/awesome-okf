---
type: Reference
title: "团队成员列表信源"
description: "docs/team.md 与 contributors-jupyter-server.yaml 的核心内容摘录，包含活跃/不活跃成员分类、SSC代表机制。"
tags: [reference, team, members, ssc, yaml]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: team-md
    resource: https://github.com/jupyter-server/team-compass/blob/main/docs/team.md
    title: "docs/team.md"
  - id: contributors-yaml
    resource: https://github.com/jupyter-server/team-compass/blob/main/docs/team/contributors-jupyter-server.yaml
    title: "docs/team/contributors-jupyter-server.yaml"
---

## docs/team.md 核心内容

### 成员分类

- **Active members**：积极参与 Jupyter Server GitHub 组织中项目的开发、维护、规划和讨论
- **Inactive members**：（暂时或永久）暂停积极参与，可随时自行重新激活，无需当前活跃成员提名

### SSC Representative

每个 Jupyter 官方子项目有一名 Software Steering Council（软件指导委员会）代表。Jupyter Server 的代表由活跃团队成员选举产生，任期一年。

当前 SSC 代表通过 `team/ssc-current.txt` 包含展示，历任代表通过 `team/ssc-past.txt` 展示。

## contributors-jupyter-server.yaml 数据结构

YAML 列表，每个成员包含字段：
- `name`: 全名
- `handle`: GitHub 用户名（带 @ 前缀）
- `affiliation`: 所属机构
- `team`: "active" 或 "inactive"
- `last-check-in`: 最后确认日期（YYYY-MM 格式）
- `ssc`: （可选）SSC 任期列表，格式如 `2024/04-`（现任，无结束日期）或 `2023/01-2024/04`（已结束）

### 截至2025-02的活跃成员（10人，按姓氏字母序）

| 姓名 | GitHub | 机构 |
|------|--------|------|
| Damian Avila | @damianavila | UMSI and 2i2c |
| David Brochart | @davidbrochart | Quantstack |
| Sylvain Corlay | @SylvainCorlay | QuantStack |
| Afshin Darian | @afshin | QuantStack |
| Vidar Fauske | @vidartf | J.P. Morgan Chase |
| Brian Granger | @ellisonbg | Amazon Web Services |
| Piyush Jain | @3coins | Amazon Web Services |
| Luciano Resende | @lresende | Apple |
| Zach Sailer | @Zsailer | Apple |
| Carol Willing | @willingc | Noteable |

### 不活跃成员（6人）

Kevin Bates (@kevin-bates, Veritone), Rahul Goyal (@rahul26goyal, AWS), Paul Ivanov (@ivanov, Noteable), Jeremy Tuloup (@jtpio, Quantstack), Mariko Wakabayashi (@mwakaba2, OpenZeppelin), Jessica Xu (@jess-x, Cal Poly)

### SSC代表

- **现任**：Vidar Fauske (@vidartf)，任期 2024/04-
- **前任**：Zach Sailer (@Zsailer)，任期 2023/01-2024/04
