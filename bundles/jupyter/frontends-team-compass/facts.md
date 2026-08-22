---
type: Facts
okf_version: "0.2"
title: "frontends-team-compass 源码事实清单"
generated: "2026-08-22"
tags: [jupyter, frontends, team-compass, community]
sources:
  - ../../../../../external/libs/jupyter/frontends-team-compass/README.md
  - ../../../../../external/libs/jupyter/frontends-team-compass/LICENSE
  - ../../../../../external/libs/jupyter/frontends-team-compass/.readthedocs.yml
  - ../../../../../external/libs/jupyter/frontends-team-compass/docs/index.rst
  - ../../../../../external/libs/jupyter/frontends-team-compass/docs/team.md
  - ../../../../../external/libs/jupyter/frontends-team-compass/docs/team/becoming-member.md
  - ../../../../../external/libs/jupyter/frontends-team-compass/docs/team/decision-making.md
  - ../../../../../external/libs/jupyter/frontends-team-compass/docs/team/member-guide.md
  - ../../../../../external/libs/jupyter/frontends-team-compass/docs/team/contributors.yaml
  - ../../../../../external/libs/jupyter/frontends-team-compass/docs/scripts/gen_contributors.py
  - ../../../../../external/libs/jupyter/frontends-team-compass/docs/host-guide.md
  - ../../../../../external/libs/jupyter/frontends-team-compass/docs/conf.py
  - ../../../../../external/libs/jupyter/frontends-team-compass/docs/requirements.txt
  - ../../../../../external/libs/jupyter/frontends-team-compass/docs/surveys/2020-jupyterlab-survey.md
---

# frontends-team-compass 源码事实清单

## 项目元数据与文档基础设施

- F-001: README.md:1-3 — 仓库标题为 "Jupyter Frontends team-compass"，用于 JupyterLab 生态系统的团队互动、同步与会议纪要 (team interaction, syncing, and handling meeting notes)。
- F-002: README.md:5-9 — 两类周会：团队会议（周三太平洋时间 9:00am）与 triage 会议（周二太平洋时间 9:00am），均通过 Jupyter Zoom room 举行；会议纪要托管于 HackMD，每次纪要以本仓库 issue 的评论形式添加。
- F-003: README.md:13-14 — 作为官方 Jupyter 项目，本 organization 所有仓库的沟通遵循 Project Jupyter Code of Conduct。
- F-004: README.md:16-24 — 将扩展贡献到 JupyterLab GitHub organization 需采用标准 Jupyter 许可与版权、遵守 Project Jupyter 社区准则、并受 Project Jupyter BDFL、Steering Council 与治理约束。
- F-005: LICENSE:1-2 — 仓库采用 BSD 3-Clause License，版权 (c) 2019 Project Jupyter Contributors。
- F-006: .readthedocs.yml:1-11 — Read the Docs 配置版本 2，构建 OS ubuntu-22.04、Python 3.11，Sphinx 配置指向 docs/conf.py，安装 docs/requirements.txt。
- F-007: docs/requirements.txt:1-6 — 文档构建依赖 sphinx>=3、sphinx_copybutton、sphinx_book_theme、pandas、ruamel.yaml、myst_parser。
- F-008: docs/conf.py:34,41,88 — Sphinx 扩展为 sphinx.ext.mathjax 与 myst_parser，源文件后缀为 ['.rst', '.md']，HTML 主题为 sphinx_book_theme。

## 团队结构与数据驱动名册

- F-009: docs/team.md:1-5 — team 页列出官方命名的 Jupyter Frontends Council 成员；成员积极参与 JupyterLab GitHub organization 与 Jupyter Notebook 项目中的开发、维护、规划与讨论。
- F-010: docs/team.md:7-11 — team.md 通过 `.. include:: team/active.txt` 引用构建脚本生成的成员名单文件。
- F-011: docs/team.md:14-18 — 每个官方 subproject 获得单一 Software Steering Council Representative；Frontends 代表由成员选举产生，应每年（一月）重新选举，当前代表为 Jérémy Tuloup。
- F-012: docs/team/contributors.yaml:1-6 — 文件注释说明该文件由 jupyterlab/council 仓库的 update-members.yml workflow 自动生成，禁止手动编辑，应从 council/members.json 编辑后执行 mention workflow；成员按 GitHub handle 排序。
- F-013: docs/team/contributors.yaml:8-96 — 成员记录含 name、handle、affiliation、last-check-in 字段，共 18 名成员（如 @fperez 加州大学伯克利分校、@fcollonval WebScIT、@SylvainCorlay QuantStack、@Zsailer Apple 等）。
- F-014: docs/scripts/gen_contributors.py:9-16,19-49 — 脚本定义 N_PER_ROW=4，从 docs/team/ 读取 contributors.yaml（ruamel.yaml 解析），将成员渲染为含 GitHub avatar、名称、affiliation 的 HTML 表格（`.. raw:: html` RST 块）。

## 成员与决策流程

- F-015: docs/team/becoming-member.md:1-5 — 文档描述如何成为 Jupyter Frontends Council 成员，包含两个子组：release 组（Release team member）与 admin 组（Admin team member）。
- F-016: docs/team/becoming-member.md:11-19 — Council 成员职责：须由现任成员提名、可被选为 Jupyter Frontends 的 SSC 代表、投票时拥有投票权、计入法定人数、参与 2/3 的投票、可提名新成员。
- F-017: docs/team/becoming-member.md:33-44 — 新成员须由现任 active 成员提名（champion）：先与 Council 内部确认共识 → 达成后联系候选人并让其了解 membership_guidelines；若内部无共识可进行内部投票以保护候选人隐私。
- F-018: docs/team/becoming-member.md:48 — 每六个月 bot 在 council 仓库开 issue 要求 active 成员三周内确认活跃状态；回复否或未回复者将被移除出 Council。
- F-019: docs/team/becoming-member.md:50-69 — release 组成员加入 GitHub JupyterLab release team、PyPI JupyterLab manager、NPM jupyterlab team、conda-forge recipes 维护者；拥有 JupyterLab 主要包的发布权，可快速响应损坏或损坏包。
- F-020: docs/team/becoming-member.md:75-86 — admin 组人数不超过七人；SSC 代表自动成为 admin 组成员；Executive Council 必须保有至少一个 admin 席位，若最后的 EC 管理员辞职须由 EC 提名新管理员。
- F-021: docs/team/becoming-member.md:90-97 — admin 组成员加入 GitHub JupyterLab owners、PyPI JupyterLab manager、NPM jupyterlab owners、conda-forge jupyterlab recipe 维护者。
- F-022: docs/team/decision-making.md:3-5 — Jupyter Frontends Council 遵循 Jupyter 治理文档中的 "Decision Making" 准则：先寻求非正式共识，无法达成时由 active 成员呼叫投票，投票流程遵循 Jupyter 治理模型。
- F-023: docs/team/decision-making.md:9-11 — Council 规模无上限，遵循鼓励大型、高参与决策主体的 Jupyter 治理准则。
- F-024: docs/team/member-guide.md:51-70 — 新成员职责：watch team-compass 与 council 仓库、跟进团队会议纪要、参与至少 2/3 投票、缺席时告知团队、促进开放包容的讨论。

## 会议主持与文档组织

- F-025: docs/host-guide.md:16-25 — 主持人职责：提醒签到并分享会议纪要链接、推进议程（时间检查）、朗读聊天内容、维护秩序（举手发言）、提及并链接 Jupyter Code of Conduct。
- F-026: docs/host-guide.md:27-38 — 主持人应搭档一名协作者（facilitator）：登录 "Project Jupyter" 主持人账号、添加今日议程与签到表；会议含 on-record 与 off-record 两段；需移除疑似 AI 录音的机器人账号。
- F-027: docs/host-guide.md:61-64 — 会后工作：完善会议纪要使其对未参与者可读，并以评论形式发布到 frontends-team-compass 的 GitHub issue。
- F-028: docs/index.rst:18-25 — Sphinx toctree 包含 team、team/becoming-member、team/decision-making、team/member-guide、host-guide 五个页面。
- F-029: docs/surveys/2020-jupyterlab-survey.md:1-14 — 2020 JupyterLab 社区调查含使用模式、数据、可视化、规模、协作五部分共 20 个问题；聚合数据在投票结束后（mid-December）公开分享给 Jupyter 社区。
