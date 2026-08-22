---
type: Insights
okf_version: "0.2"
title: "team-compass 架构洞察"
generated: "2026-08-22"
tags: [jupyter, team-compass, community, governance]
sources:
  - facts.md
  - ../../../../../external/libs/jupyter/team-compass/docs/team.md
  - ../../../../../external/libs/jupyter/team-compass/docs/team/becoming-member.md
  - ../../../../../external/libs/jupyter/team-compass/docs/team/decision-making.md
  - ../../../../../external/libs/jupyter/team-compass/docs/scripts/gen_contributors.py
---

# team-compass 架构洞察

## I-001：数据驱动名册的三层架构——YAML 单一事实源 → 构建脚本生成名单 → Sphinx include 装配

**类型**：架构模式
**关联事实**：F-010, F-014, F-015, F-018, F-019
**洞察**：team-compass 的团队名册采用"单一事实源 + 构建期生成 + 文档装配"三层分离架构，把成员身份数据与其呈现形式彻底解耦。

- **事实源层**：`contributors-jupyter-server.yaml` 是唯一手工维护的数据文件，每条记录含 name、handle、affiliation、team（active/inactive）、last-check-in 字段（F-015），部分记录含 ssc 任期字段；文件注释强制按姓氏字母序排列（F-015）。成员状态变更只需编辑此文件并通过 pull request 声明（F-021），不触碰任何渲染层。
- **生成层**：`gen_contributors.py` 在 Sphinx 构建期被 `conf.py` 的 setup 阶段以 subprocess 调用（F-010），按 `team=="active"` / `team=="inactive"` 过滤生成 active.txt 与 inactive.txt（F-018），并依据 ssc 字段最新任期是否以空结束日期结尾判定现任 SSC 代表，生成 ssc-current.txt 与 ssc-past.txt（F-019）。
- **装配层**：`team.md` 不直接书写成员名单，而是通过 `.. include:: team/active.txt` 等指令引用生成文件（F-014），使渲染逻辑与数据变更互不干扰。

```
        【单一事实源】                  【构建期生成】                 【文档装配】
  contributors-jupyter-server.yaml  ──►  gen_contributors.py   ──►   active.txt / inactive.txt
  (name/handle/affiliation/team/     conf.py setup 阶段调用         ssc-current.txt / ssc-past.txt
   last-check-in/ssc 任期)                                          ▲
        │  成员状态变更(PR 声明)                                      │  .. include:: team/*.txt
        └──────────────────────────────────────────────────────────┘  team.md 页面
```

**复用价值**：凡需要"数据驱动 + 文档自动同步"的名册类场景（团队、成员、认证清单），可采用此三层模式：YAML 单一事实源保证可审计性，构建期脚本保证一致性，文档 include 装配保证单一职责——数据变更无需改动页面结构。

## I-002：复用 Jupyter 全局治理而非自建——team-compass 的轻量治理委托模式

**类型**：设计决策
**关联事实**：F-020, F-025, F-026, F-027
**洞察**：team-compass 不重新发明治理规则，而是将决策流程、成员分类、投票规则全部委托给 Jupyter 全局治理文档，自身仅保留少量"团队特有"的操作性细则。

- **决策流程委托**：决策文档首行即声明遵循 Jupyter 治理文档中的 "Decision Making" 准则（F-025）——先寻求非正式共识，无法达成时由 active 成员呼叫投票，投票细则完全引用 Jupyter 治理模型（F-025）。团队规模"无上限"也直接引用鼓励大型高参与决策主体的 Jupyter 治理准则（F-026）。
- **成员分类与投票权继承**：active/inactive 二分法及其权限差异（投票、法定人数、提名资格）来自全局治理语义（F-020），team-compass 只补充"如何切换状态"与"如何提名"的操作流程（F-021, F-023）。
- **本地化落地**：真正属于团队自身的细则只有两类——① 成员职责清单（watch 仓库、跟进纪要、参与 2/3 投票，F-027）；② 合并 PR 的操作准则（F-028）。这些是全局治理无法覆盖的"团队日常"。

```
        Jupyter 全局治理文档（被委托的规则源）
   ┌───────────────┬───────────────────────┬───────────────────┐
   │ Decision Making│ active/inactive 语义  │ 大型决策主体准则    │
   └───────┬───────┴──────────┬────────────┴─────────┬─────────┘
           │ 引用              │ 继承                  │ 引用
   ┌───────▼─────────┐  ┌─────▼───────────┐  ┌───────▼────────┐
   │ decision-making │  │ becoming-member │  │ decision-making│
   │ 共识→投票        │  │ 提名/状态切换    │  │ 规模无上限      │
   └───────┬─────────┘  └─────┬───────────┘  └───────┬────────┘
           └──────────── team-compass 本地细则 ────────┘
                    （成员职责 F-027 + 合并准则 F-028）
```

**复用价值**：当子项目需要治理但资源有限时，应先"引用/继承"上层或全局治理框架（决策流程、成员语义、投票规则），只为本团队补充最小化操作细则。这既保证与生态治理一致性，又避免维护一套重复且易漂移的独立规则。
