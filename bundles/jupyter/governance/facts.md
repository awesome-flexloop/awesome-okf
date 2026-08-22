---
type: Facts
okf_version: "0.2"
title: "governance 源码事实清单"
generated: "2026-08-22"
tags: [jupyter, governance, bdfl, decision-making, subprojects]
sources:
  - ../../../../../external/libs/jupyter/governance/README.md
  - ../../../../../external/libs/jupyter/governance/docs/overview.md
  - ../../../../../external/libs/jupyter/governance/docs/executive_council.md
  - ../../../../../external/libs/jupyter/governance/docs/software_steering_council.md
  - ../../../../../external/libs/jupyter/governance/docs/decision_making.md
  - ../../../../../external/libs/jupyter/governance/docs/newsubprojects.md
  - ../../../../../external/libs/jupyter/governance/docs/list_of_subprojects.md
  - ../../../../../external/libs/jupyter/governance/docs/people.md
  - ../../../../../external/libs/jupyter/governance/docs/papers.md
  - ../../../../../external/libs/jupyter/governance/docs/projectlicense.md
  - ../../../../../external/libs/jupyter/governance/docs/conduct/code_of_conduct.md
  - ../../../../../external/libs/jupyter/governance/docs/conduct/enforcement.md
  - ../../../../../external/libs/jupyter/governance/docs/elections/README.md
  - ../../../../../external/libs/jupyter/governance/docs/_data/README.md
  - ../../../../../external/libs/jupyter/governance/docs/myst.yml
  - ../../../../../external/libs/jupyter/governance/docs/src/team-members.mjs
  - ../../../../../external/libs/jupyter/governance/noxfile.py
  - ../../../../../external/libs/jupyter/governance/.github/workflows/build.yml
  - ../../../../../external/libs/jupyter/governance/.github/workflows/deploy.yml
---

# governance 源码事实清单

## 项目元数据与文档基础设施

- F-001: README.md:3 — 仓库的目的为将 Project Jupyter 的治理流程正式化 (formalize the governance process)。
- F-002: README.md:11-12 — 仓库内容通过 GitHub Pages 在线托管，HTML 文件由 MyST (https://mystmd.org) 构建。
- F-003: intro.md:7 — 治理文档按 Creative Commons CC0 license 放弃版权，作品发布地美国，详见仓库 LICENSE.md。
- F-004: myst.yml:9-10 — MyST 项目 github 字段为 https://github.com/jupyter/governance，license 字段为 CC0-1.0。
- F-005: myst.yml:16 — MyST 注册 src/team-members.mjs 为自定义插件。
- F-006: requirements.txt:1-2 — Python 依赖仅包含 mystmd 与 pyyaml 两个包。
- F-007: .github/workflows/build.yml:5-7 — build workflow 在每个 pull request 上运行。
- F-008: .github/workflows/build.yml:36-39 — build workflow 依次执行 `nox -s docs` 与 `nox -s redirects`。
- F-009: .github/workflows/deploy.yml:5-8 — deploy workflow 仅在 main 分支 push 时运行。
- F-010: governance.md:1-3 — 根目录 governance.md 为重定向占位页，指向 docs/archive/governance.md。

## 治理结构与历史转型

- F-011: overview.md:4 — Jupyter 于 2022 年 12 月从 BDFL + Steering Council 治理模型转型到当前治理模型。
- F-012: overview.md:9-11 — 治理模型锚定在三个相互补充的机构：Executive Council (EC)、Software Steering Council (SSC) 与 Jupyter Foundation。
- F-013: overview.md:11 — EC 对项目所有维度（软件、法律、财务、社区、运营、包容与多元化等）最终负责，通过委派给 SSC、Software Subprojects、Standing Committees 与 Working Groups 支持运营。
- F-014: overview.md:18 — SSC 对跨项目软件相关决策有管辖权；未明确涉及的日常技术决策自动委派给各 Subproject 独立自治。
- F-015: overview.md:25 — Jupyter Foundation 是 Linux Foundation 501(c)(6) 的定向基金 (directed fund)。
- F-016: overview.md:40 — 每个 Subproject 维护 Subproject Council，并从该 Council 选举一人进入 SSC。
- F-017: overview.md:46-47 — Standing Committees 仅由 EC 与 SSC 联合投票创建/解散；Working Groups 可由 EC 单独创建/解散。
- F-018: archive/governance.md:74-80 — 旧治理模型中 BDFL（Fernando Perez）通过 Core Developers 的 consensus 决策，拥有可覆盖 Core Developers 的最终裁决权（称为 "special"/"overriding" vote）。

## Executive Council

- F-019: executive_council.md:18 — EC 对项目所有维度最终负责，其他机构向其汇报。
- F-020: executive_council.md:26-37 — EC 独有职责包括建立/解散/管理 Working Groups、维护与执行 Code of Conduct、筹集与管理项目资金、管理法律/品牌/服务、撰写年度 stakeholders letter 等。
- F-021: executive_council.md:45 — EC 作为项目最终决策者可在例外情况下覆盖 SSC、Software Subprojects、Standing Committees、Working Groups 的决策，但不能覆盖双方共享职责的 SSC 决策。
- F-022: executive_council.md:51-55 — EC 与 SSC 共享批准治理模型变更、新 Subproject 创建、Subproject 移除；双方各自独立投票且须双方均批准。
- F-023: executive_council.md:63 — EC 由 6 名成员组成。
- F-024: executive_council.md:68-72 — EC 成员任期为 2 年；连选可连任；过去 4 年内在 EC 任职满 3 年者不得开始新任期。
- F-025: executive_council.md:87 — 同一人不得同时在 EC 与 SSC 任职。
- F-026: executive_council.md:104-110 — UoC 是全部 Subproject Councils、Standing Committees、Working Groups 成员的并集，构成选举 EC 成员的投票主体。

## Software Steering Council

- F-027: software_steering_council.md:20-27 — SSC 独有职责包括定义 JEP 提交/评审/批准流程、拥有并实施 Incubation 与 Jupyter Attic 流程、管理跨项目安全漏洞、投票接受 EC 提名的 Working Group 在 SSC 的代表。
- F-028: software_steering_council.md:41 — SSC 成员为各 Subproject 的代表；一人可代表多个 Subproject，并为每个所代表 Subproject 各投一票。
- F-029: software_steering_council.md:49 — SSC 由每个 Jupyter Subproject 各一名代表，外加对 SSC 活动有重要影响的 Working Groups/Standing Committees（如 DEI、Internationalization）成员组成。

## 决策流程

- F-030: decision_making.md:3 — 该文档描述 Jupyter 各治理机构（统称 "councils"）的决策方式，所有 Jupyter 治理机构须遵循。
- F-031: decision_making.md:13 — 所有官方项目/工作组/治理机构须有明确定义的 council，通过 consensus seeking 决策并可调用投票推进。
- F-032: decision_making.md:19 — 任何 council 成员可在讨论成熟时叫投票（成为 sponsor）；提案被另一成员 seconded 后成员有 7 天投票期；二进制决策按非空白票简单多数、多类决策按 ranked choice；sponsor 在投票期内更新提案会使投票期重置。
- F-033: decision_making.md:21 — 每位成员每年须参与至少 2/3 的正式投票，否则年底自动被要求退出；正式投票法定人数为 50%，始终包含 "blank" 选项且 blank 计入法定人数但不计入结果。

## 子项目管理

- F-034: newsubprojects.md:14-25 — 创建新 Subproject 有两条路径：直接创建（Direct Subproject creation）与纳入现有外部 Subproject（Incorporation）。
- F-035: newsubprojects.md:27-30 — jupyter-incubator 中的项目不被视为官方支持的 Subproject，直到满足标准并完成纳入流程。
- F-036: newsubprojects.md:38-48 — 官方 Subproject 评估标准包括活跃开发者社区、活跃用户社区、健全软件工程与文档测试、持续增长、与其他官方 Subproject 良好集成、范围明确、适当打包等。
- F-037: newsubprojects.md:64-71 — 直接创建路径：SSC 成员就创建达成共识并通知主 Jupyter 列表；EC 批准将新项目加入 list_of_subprojects.md 的 PR 后流程完成。
- F-038: newsubprojects.md:99-106 — 正式纳入流程：向 jupyter/enhancement-proposals 提交增强提案 → 社区讨论 → SC 共识给出建议 → 提交加入 list_of_subprojects.md 的 PR → EC 通过合并或拒绝决定。
- F-039: newsubprojects.md:122-129 — SC 的四种可能建议：整合进现有官方 Subproject、纳入为新官方 Subproject、进一步内外部孵化、拒绝。
- F-040: newsubprojects.md:207-217 — 孵化提案流程：向 jupyter-incubator/proposals 提交 PR、在主列表公告、须有活跃 SSC 成员任 Advocate、由 SC 共识批准或拒绝。
- F-041: list_of_subprojects.md:6-32 — 有 SSC 代表的官方 Subprojects 列表：Jupyter Frontends、JupyterHub and Binder、Voilà、Jupyter Server、Jupyter Widgets、Jupyter Kernels、Jupyter Foundations and Standards、Jupyter Security、Jupyter Accessibility、Jupyter Book。
- F-042: list_of_subprojects.md:36-42 — 无 SSC 代表的官方 Subprojects（nbdime、nbgrader、nbviewer、ipyparallel 及其他未明确归属仓库），其正式 Subproject Council 为 SSC 本身。
- F-043: software_subprojects.md:15-18 — Subproject 职责包括：源码托管于 Project Jupyter GitHub enterprise organization、PyPI 包置于 jupyter PyPI organization、维护含 Subproject Council 成员列表的公开 Team Compass。

## 人员目录

- F-044: people.md:3 — 该文档为 Project Jupyter 现任与历任领导层目录 (Leadership Directory)。
- F-045: people.md:86-87 — Fernando Pérez (@fperez) 曾任 BDFL，在 2022 年 12 月 Jupyter 转型新治理模型后自愿放弃该角色。
- F-046: _data/README.md:7-9 — docs/_data/ 目录含 contributors.yml（MyST authors 格式）、organizations.yml（MyST affiliations 格式）、jupyter-teams.yml（治理团队定义）三个数据文件。
- F-047: src/team-members.mjs:19-46 — team-members directive 从三个 YAML 文件加载数据、按名字字母序排序、生成 markdown 表格并写入 _build/site/public/team-tables/<team-id>.md。
- F-048: src/team-members.mjs:53-54 — union_of_councils 团队有特殊分支：聚合所有非 former_ 前缀团队的成员。

## Code of Conduct

- F-049: docs/conduct/code_of_conduct.md:35-41 — CoC 适用于 Project Jupyter（含 IPython）管理的所有空间：邮件列表、GitHub organizations、聊天室、线下活动、Discourse 论坛等。
- F-050: docs/conduct/code_of_conduct.md:132-134 — 报告途径为邮箱 conduct@jupyter.org 或在线表单；表单支持匿名报告。
- F-051: docs/conduct/enforcement.md:9-14 — 违规报告由 Code of Conduct Committee 管理；EC 负责任命委员会；未任命或不可用时 EC 作为临时委员会。
- F-052: docs/conduct/reporting_online.md:60-63 — 对委员会决定的申诉联系 EC（steeringcouncil@jupyter.org），EC 两周内提供决议。

## 论文流程

- F-053: docs/papers.md:28-41 — 论文创作四原则：作者包容与慷慨、明确可审计的作者标准、公开性（论文在 GitHub 公开写作）、问责。
- F-054: docs/papers.md:53-55 — 作者排序政策：第一作者列为 "Project Jupyter"，其余个人作者按字母序排列。
- F-055: docs/papers.md:63-76 — 计划为每个主要用户导向 Subproject（Notebook、JupyterLab、JupyterHub、nbconvert、ipywidgets 等）发布 JOSS 论文。
- F-056: docs/papers.md:99-121 — JOSS 论文流程：有人担任 Coordinator → 开 issue 并公告 → 在仓库起草（paper/paper.md + paper.bib）→ 邮件潜在作者（Git log 名单 + 主 Google Group）。

## 许可证

- F-057: docs/projectlicense.md:3-4 — Jupyter 代码采用 3-Clause BSD License。
- F-058: docs/projectlicense.md:37-45 — 共享版权模型：每位贡献者保留其贡献的版权，项目代码整体为贡献者的集体版权。

## 选举机制

- F-059: docs/elections/README.md:3-8 — process-votes.py 将 EC 选举的 CSV 文件转换为 .ini 与 .txt 文件，供 Apache STeVe 脚本 stv_tool.py 计票。
- F-060: docs/elections/README.md:91 — 计票命令为 `stv_tool.py -s 2 votedata.txt`（-s 指定当选席位数）。
