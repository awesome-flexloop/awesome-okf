---
type: Facts
okf_version: "0.2"
title: "team-compass 源码事实清单"
generated: "2026-08-22"
tags: [jupyter, team-compass, community, governance]
sources:
  - ../../../../../external/libs/jupyter/team-compass/README.md
  - ../../../../../external/libs/jupyter/team-compass/CODE_OF_CONDUCT.md
  - ../../../../../external/libs/jupyter/team-compass/.pre-commit-config.yaml
  - ../../../../../external/libs/jupyter/team-compass/docs/index.rst
  - ../../../../../external/libs/jupyter/team-compass/docs/team.md
  - ../../../../../external/libs/jupyter/team-compass/docs/team/becoming-member.md
  - ../../../../../external/libs/jupyter/team-compass/docs/team/decision-making.md
  - ../../../../../external/libs/jupyter/team-compass/docs/team/member-guide.md
  - ../../../../../external/libs/jupyter/team-compass/docs/team/contributors-jupyter-server.yaml
  - ../../../../../external/libs/jupyter/team-compass/docs/scripts/gen_contributors.py
  - ../../../../../external/libs/jupyter/team-compass/docs/conf.py
  - ../../../../../external/libs/jupyter/team-compass/readthedocs.yml
---

# team-compass 源码事实清单

## 项目元数据与文档基础设施

- F-001: README.md:1-3 — 仓库标题为 "Jupyter Server Team Compass"，用于团队讨论、同步与会议纪要 (team discussion, syncing, and meeting notes)。
- F-002: README.md:7-8 — 每周团队会议：周四太平洋时间 8:00am，通过 Zoom 举行。
- F-003: README.md:10-11 — 会议议程托管于 HackMD，会议纪要作为 GitHub issue #57 的评论发布。
- F-004: README.md:16 — 向 Jupyter Server GitHub organization 贡献扩展遵循与 JupyterLab team-compass 相同的准则。
- F-005: CODE_OF_CONDUCT.md:3-4 — JupyterHub organizations 托管项目遵循 Project Jupyter Code of Conduct。
- F-006: .pre-commit-config.yaml:1-5 — pre-commit 配置仅启用 pre-commit-hooks 仓库的 end-of-file-fixer hook（rev v6.0.0）。
- F-007: LICENSE:1-3 — 仓库采用 BSD 3-Clause License，版权 (c) 2020 Jupyter Server。
- F-008: readthedocs.yml:5,18-19 — Read the Docs 配置文件版本 2，Sphinx 配置指向 docs/conf.py。
- F-009: docs/conf.py:34,41,88 — Sphinx 扩展为 sphinx.ext.mathjax 与 myst_parser，源文件后缀为 ['.rst', '.md']，HTML 主题为 sphinx_book_theme。
- F-010: docs/conf.py:200-202 — Sphinx setup 阶段通过 subprocess 运行 `python scripts/gen_contributors.py` 更新贡献者列表。

## 团队结构与数据驱动名册

- F-011: docs/team.md:3,5-7 — team 页按字母序列出官方命名的 Jupyter Server 团队；Active 成员积极参与 Jupyter Server organization 内项目的开发、维护、规划与讨论。
- F-012: docs/team.md:17 — Inactive 成员可随时自我激活，无需现任 active 成员提名。
- F-013: docs/team.md:27 — SSC 代表由 active 团队成员选举产生，任期一年。
- F-014: docs/team.md:9-13,19-23,31-35 — team.md 通过 `.. include:: team/active.txt`、`team/inactive.txt`、`team/ssc-current.txt`、`team/ssc-past.txt` 引用构建脚本生成的名单文件。
- F-015: docs/team/contributors-jupyter-server.yaml:1-8 — 每条成员记录含 name、handle、affiliation、team（active/inactive）、last-check-in 字段，部分记录含 ssc 任期字段；文件注释要求按姓氏字母序排列。
- F-016: docs/team/contributors-jupyter-server.yaml:33-34 — Vidar Fauske (@vidartf) 的 ssc 字段为 "2024/04-"（无结束日期，表示现任 SSC 代表）。
- F-017: docs/team/contributors-jupyter-server.yaml:59-60 — Zach Sailer (@Zsailer) 的 ssc 字段为 "2023/01-2024/04"（前任 SSC 代表）。
- F-018: docs/scripts/gen_contributors.py:59-69 — 脚本读取 contributors-jupyter-server.yaml，按 team=="active" 过滤生成 active.txt、按 team=="inactive" 过滤生成 inactive.txt 写入 docs/team/。
- F-019: docs/scripts/gen_contributors.py:71-87 — 脚本依据 ssc 字段最新任期是否以空结束日期结尾（`latest_term.split("-")[-1] == ""`）判定现任 SSC 代表，生成 ssc-current.txt 与 ssc-past.txt。

## 成员与决策流程

- F-020: docs/team/becoming-member.md:9-19 — 团队成员分 active 与 inactive 两类；active 成员须被现任成员提名、可被选为 SSC 代表、可投票、计入法定人数、可提名新成员；inactive 成员不投票且不计入法定人数。
- F-021: docs/team/becoming-member.md:28-32 — 成员可随时在 active/inactive 间切换，须通过更新 contributors-jupyter-server.yaml 的 pull request 公开声明状态变更。
- F-022: docs/team/becoming-member.md:34-45 — 新成员候选人须已是社区持续、积极、有产出的成员，且承诺长期（至少一年）持续参与。
- F-023: docs/team/becoming-member.md:48-62 — 提名流程：champion 先与团队内部确认共识 → 联系候选人 → 在 team-compass 仓库开 issue 表达支持 → issue 保持约 7 天供反馈 → 无未解决异议即欢迎加入。
- F-024: docs/team/becoming-member.md:64-66 — 每六个月由一名 active 成员在 team-compass 仓库开 issue 要求所有 active 成员确认活跃状态，无回应者视为转为 inactive。
- F-025: docs/team/decision-making.md:3-5 — Jupyter Server 团队遵循 Jupyter 治理文档中的 "Decision Making" 准则：先寻求非正式共识，无法达成时由 active 成员呼叫投票。
- F-026: docs/team/decision-making.md:9 — 团队规模无上限，遵循鼓励大型高参与决策主体的 Jupyter 治理准则。
- F-027: docs/team/member-guide.md:54-58 — 新团队成员职责：watch team-compass 仓库、跟进团队会议纪要、参与至少 2/3 的团队投票。
- F-028: docs/team/member-guide.md:75-110 — 合并 PR 准则包括使用最佳判断、确保代码质量、确保有测试、留足讨论时间、不要害怕合并。
