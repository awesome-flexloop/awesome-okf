---
type: Insights
okf_version: "0.2"
title: "governance 架构洞察"
generated: "2026-08-22"
tags: [jupyter, governance, bdfl, decision-making, subprojects]
sources:
  - facts.md
  - ../../../../../external/libs/jupyter/governance/docs/overview.md
  - ../../../../../external/libs/jupyter/governance/docs/executive_council.md
  - ../../../../../external/libs/jupyter/governance/docs/newsubprojects.md
  - ../../../../../external/libs/jupyter/governance/docs/myst.yml
  - ../../../../../external/libs/jupyter/governance/docs/src/team-members.mjs
---

# governance 架构洞察

## I-001：文档库双层结构——根目录重定向占位 + docs/ 单一事实源

**类型**：架构模式

**关联事实**：F-001, F-002, F-005, F-010

**洞察**：governance 仓库把"人读的官方 URL 结构"与"文档唯一事实源"解耦：所有根目录 Markdown（governance.md、newsubprojects.md 等）仅作 "Page Moved" 重定向占位（F-010），真实内容收敛到 docs/ 单目录，由 myst.yml 定义导航与构建（F-001, F-002, F-005）。

正文分析：该仓库承载的是"治理文档"而非软件代码，但采用了与软件文档站点一致的双层布局。第一层是仓库根，保留旧 URL（如 `jupyter/governance/governance.md`）指向新位置的占位页，保证外部链接不失效；第二层是 docs/，是唯一内容源，`myst.yml` 中的 toc 树把全部治理文档组织成六个导航分区，MyST 负责构建为站点（F-001, F-002）。这一结构让"迁移文档"与"维护链接"解耦——移动文件只需更新占位重定向，不需要改导航结构。CI 侧 build workflow 在每个 PR 上执行 `nox -s docs` 与 `nox -s redirects`（F-008），其中 redirects session 专门负责为已迁移页面生成 HTML 层重定向，形成"仓库占位 + 构建期重定向"的双保险。

```
仓库根（占位层）                    docs/（事实源层）
┌─────────────────┐               ┌──────────────────────────┐
│ governance.md   │──重定向──────▶│ archive/governance.md     │
│ newsubprojects.md│──重定向─────▶│ newsubprojects.md         │
│ people.md       │──重定向──────▶│ people.md                 │
│ papers.md       │──重定向──────▶│ papers.md                 │
│ conduct/CoC.md  │──重定向──────▶│ docs/conduct/CoC.md       │
└─────────────────┘               └────────────┬─────────────┘
                                               │ myst.yml toc 导航
                                    ┌──────────▼──────────┐
                                    │ MyST 构建 + nox      │
                                    │ (PR: build workflow) │
                                    └─────────────────────┘
```

**复用价值**：治理/组织文档仓库可复制此双层结构：根层保留历史 URL 占位 + 构建期生成重定向，内容层收敛到单一 docs/ 目录，用站点配置文件驱动导航。任何文档迁移场景（目录重组、站点合并）都应先建立占位重定向机制再移动内容，避免链接断裂。

---

## I-002：三主体治理 + 委派金字塔——EC 全维度最终负责，SSC 软件自治委派，Subproject 自治

**类型**：设计决策

**关联事实**：F-011, F-012, F-013, F-014, F-016, F-017, F-019

**洞察**：Jupyter 2022 年 12 月从 BDFL 独裁转型为三主体模型（F-011, F-012），核心是"委派金字塔"：EC 对所有维度最终负责（F-013），把软件工作委派给 SSC（F-014），SSC 再把日常技术决策自动委派给各 Subproject 自治（F-016）。权力逐级下放，但最终裁决权保留在 EC。

正文分析：三个机构各司其职且权力不对等——EC 是全维度最终决策者（F-019），SSC 只有软件维度管辖权（F-014），Jupyter Foundation 只是提供资源与战略咨询的 Linux Foundation 定向基金（F-015）。金字塔的关键设计是**双重委派**：SSC 对跨项目决策有管辖权，但未明确涉及的日常决策"自动委派"回 Subproject（F-014）；Standing Committees 与 Working Groups 则通过 delegation from EC 承担非软件工作（F-017）。每个 Subproject 通过选举 SSC 代表反向向上参与（F-016），形成自下而上的代表通道与自上而下的委派通道并存。这一模型把旧 BDFL 的"一个人最终负责"（F-018）替换为"一个机构最终负责"，同时保留了对等机构之间的制衡——EC 可覆盖 SSC 决策，但共享职责除外（F-021）。

```
                ┌─────────────────────────┐
                │  Executive Council (EC)  │  最终负责/可覆盖
                │ 全维度：软件/法律/财务/   │
                │ 社区/运营/DEI/品牌       │
                └───────────┬─────────────┘
      委派（非软件）         │  共享批准（治理变更/子项目增删）
      ┌─────────┬──────────┼─────────────┬────────────┐
      ▼         ▼          ▼             ▼            ▼
Standing    Working    SSC            Foundation    Community
Committees  Groups  ────软件管辖权────   (定向基金)   Advisory Panel
(永久)      (临时)      │
              ┌─────────┴─────────┐
              ▼                   ▼
      跨项目技术决策         日常技术决策
       (JEP/Incubation)   自动委派 → Subprojects
                           (选举 SSC 代表上行)
```

**复用价值**：大型开源社区治理可借鉴"全维度负责机构 + 专项负责机构 + 高度自治的项目单元"三层委派模型，并明确"哪些决策共享批准、哪些可被上级覆盖、哪些自动委派下级"。委派边界必须写入文档（本仓库由 decision_making.md 统一约束，见 I-003）。

---

## I-003：共识优先 + 投票兜底——统一决策机制与双主体联合批准闸门

**类型**：架构模式

**关联事实**：F-022, F-030, F-031, F-032, F-033, F-021

**洞察**：Jupyter 用一份《Decision-Making Guide》统一约束所有治理机构的决策方式（F-030）：先 consensus seeking（F-031），失败后由任何成员叫投票，走"seconded → 7 天投票期 → 简单多数/ranked choice"流程（F-032），并设 2/3 参与率与 50% 法定人数防僵尸机构（F-033）。高影响决策（治理模型变更、子项目增删）额外要求 EC 与 SSC 双主体独立投票、双双批准才生效（F-022）。

正文分析：这是典型的"双层决策闸门"架构。第一层是常规决策：共识优先，投票是升级机制而非日常手段（F-031, F-032）；为了防止多数暴政与消极参与，同时规定 blank 选项计入法定人数、年度 2/3 参与率否则自动退出（F-033）。第二层是"重大变更"双闸门：凡触及治理模型、子项目创建/移除的决策，EC 与 SSC 各自独立投票且均批准才通过（F-022）——这既防止单一机构独断（EC 不能覆盖这类共享决策，F-021），也防止单一子项目团体挟持全局。整个机制与 EC/SSC 的委派金字塔（I-002）配套：常规决策下放到最合适的层级，重大决策收敛到双机构联合批准，形成"分散决策 + 集中审批"的平衡。

```
        决策请求
           │
           ▼
   ┌─ consensus seeking 讨论 ──达成共识──▶ 记录决策 (Team Compass issues)
   │          │ 未达成
   │          ▼
   │   成员叫投票 (sponsor)
   │   另一成员 seconded
   │          ▼
   │   7 天投票期 (≥2/3 参与 / 50% 法定人数 / blank 选项)
   │          │
   │          ▼
   │   简单多数(二值) / ranked choice(多类)
   │
   └──▶ 是否重大变更？(治理模型/子项目增删)
                │ 是
                ▼
   EC 独立投票 ──┤── SSC 独立投票 ──双方均通过──▶ 批准
                │ 任一否决                          （拒绝）
```

**复用价值**：任何组织/社区可复制"统一决策手册 + 共识优先投票兜底 + 重大变更双主体批准"三板斧。要点：参与率与法定人数写入制度防消极机构；blank 作为显式选项而非默认弃权；重大变更设置多于一个批准主体。

---

## I-004：子项目全生命周期治理——双路径进入、孵化到官方、类别化分级

**类型**：设计决策

**关联事实**：F-034, F-035, F-036, F-037, F-038, F-039, F-040, F-041, F-042, F-043

**洞察**：governance 仓库把子项目管理编码为完整的生命周期流程：新项目经"直接创建"或"外部纳入"两条路径进入（F-034），纳入须先孵化（jupyter-incubator，非官方状态，F-035）并满足明确标准（F-036）；SC 给出四种建议之一（F-039）；最终列表将子项目分级为"有 SSC 代表"与"无 SSC 代表"两类（F-041, F-042）。

正文分析：这一流程呈现三个关键设计。其一，**双路径**：与现有团队强关联的新仓库走轻量"直接创建"路径（SSC 共识 + EC 批准 PR 即可，F-037）；外部已有项目走正式"纳入"路径（JEP → 社区讨论 → SC 推荐 → EC 决定，F-038）。其二，**孵化作为缓冲带**：jupyter-incubator 明确标记为"非官方"，作为实验与接纳的中间地带，须活跃 SSC 成员任 Advocate 推动（F-040），项目在孵化期证明自身生命力。其三，**分级而非一刀切**：小规模/低活跃子项目不设独立 Council，其 Council 即 SSC 本身（F-042），避免为每个小项目维护冗余治理层——这是对治理成本的务实收敛。子项目还需承担统一义务（源码托管位置、PyPI org、公开 Team Compass，F-043），保证治理一致性可审计。

```
  新子项目
     │
     ├── 与现有项目强关联 ──▶ 直接创建路径 (SSC共识 + EC批准PR) ──┐
     │                                                          │
     └── 外部已有项目 ──▶ jupyter-incubator 孵化 (非官方, Advocate) ──▶ 纳入提案(JEP)
                                                                    │  SC 四建议
                                                ┌───────────────────┼────────────────┐
                                                ▼                   ▼                ▼
                                      整合进现有项目      纳入为新官方子项目      进一步孵化/拒绝
                                                                  │
                                                                  ▼
                                        官方子项目列表 (list_of_subprojects.md)
                                        ├── 有 SSC 代表 (大, 独立 Council)
                                        └── 无 SSC 代表 (小, Council = SSC)
```

**复用价值**：多项目生态可套用"双路径进入 + 孵化缓冲 + 分级治理"框架。重点：对低活跃项目提供降级治理而不降级官方身份；为孵化项目设置明确的毕业信号（活跃社区/增长/集成）；所有子项目绑定统一义务清单以便审计。

---

## I-005：数据驱动的人员目录——YAML 结构化数据 + 自定义 MyST directive 自动渲染

**类型**：架构模式

**关联事实**：F-005, F-046, F-047, F-048

**洞察**：governance 的人员目录不手写 HTML 表格，而是把"人/组织/团队"建模为三个 YAML 数据文件（F-046），通过注册到 MyST 的自定义 `{team-members}` directive（F-005, F-047）在构建期加载、过滤、排序并生成 markdown 表格写入站点（F-047），还内置 union_of_councils 的派生逻辑（F-048）。

正文分析：这是"内容与表现分离"的典型实现。数据层：contributors.yml（人 + 所属团队与任期）、organizations.yml（单位与 URL）、jupyter-teams.yml（团队 ID/名称/首页/team compass）三者独立维护（F-046）。表现层：`{team-members} <team-id>` directive 在文档中按团队 ID 声明即可，无需知道成员是谁（F-047）。构建层：directive 运行 `getTeamMembers()` 从 contributors.authors 中按 `teams[].team == teamId` 过滤，按名字字母序排序，生成含 Name/Subproject/Organization/GitHub/Term 列的 markdown 表格，并同时落盘到 `_build/site/public/team-tables/<team-id>.md` 供外部复用（F-047）。最有意思的是 union_of_councils 的特殊分支（F-048）：UoC 不是一个独立数据实体，而是构建期从全部活跃团队（排除 former_ 前缀）成员聚合派生的视图——"选举人团"这种跨团队概念被实现为查询而非存储。数据模型把治理规则（哪些团队算活跃、如何排序、如何派生 UoC）下沉到代码，使人员目录与治理模型保持一致。

```
                    数据层 (docs/_data/)
  ┌──────────────────┬─────────────────┬───────────────────┐
  │ contributors.yml │ organizations.yml│ jupyter-teams.yml │
  │ 人+团队+任期     │ 单位+URL         │ 团队ID/名称/首页   │
  └──────────────────┴─────────────────┴───────────────────┘
                     │ 构建期加载
                     ▼
        {team-members} directive (src/team-members.mjs)
           │ 按 teamId 过滤 + 名字字母序排序
           │ union_of_councils → 聚合所有活跃团队 (排除 former_)
           ▼
      markdown 表格 ──▶ 写入站点页面
           └─────────▶ _build/.../team-tables/<team-id>.md (可复用)
```

**复用价值**：组织型文档站点可复制"YAML 数据 + 自定义构建 directive"模式管理领导层名册。好处：新增成员只改数据不改页面；跨团队视图（如 UoC）用构建期派生而非重复维护；团队表格可落盘为独立 md 供其他文档项目引用。维护流程（_data/README.md 的增删成员/团队步骤）应一并文档化。
