---
type: Concept
title: "软件子项目体系"
description: "Jupyter软件开发以官方子项目(Subprojects)形式组织，分为有SSC代表的成熟子项目和由SSC代管的小型子项目两类，各子项目高度自治。"
tags: [subprojects, software, ecosystem, autonomy, incubation]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: subprojects
    resource: /references/subprojects-source.md
    title: "软件子项目信源"
---

## 子项目的定位

Jupyter 的软件开发组织为一组**软件子项目（Software Subprojects）**。子项目通常对应一个 GitHub 组织，是 Jupyter 生态系统中官方认可的重点领域。

核心设计原则是**最大化自治**：除非 SSC 或 EC 另有指示，子项目在遵循 Jupyter 整体治理模型的前提下，尽可能自主管理。

## 子项目的共同责任

所有 Jupyter 治理下的子项目必须：

| 责任领域 | 具体要求 |
|---------|---------|
| 行为准则 | 遵守 [Jupyter 行为准则](13-code-of-conduct.md) |
| 决策流程 | 遵循 Jupyter 决策制定指南和流程 |
| SSC 代表 | 如适用，提名并维护一名 SSC 代表 |
| 许可 | 遵循 Jupyter 许可指南和实践（BSD-3-Clause） |
| 商标品牌 | 遵循 Jupyter 商标、品牌和知识产权指南 |
| 开放透明 | 以开放、透明、包容的方式开展活动，与 SSC/EC 协调信息流通 |
| 代码托管 | 在 [Jupyter GitHub Enterprise 组织](https://github.com/enterprises/jupyter) 中维护源代码 |
| PyPI 发布 | 在 [Jupyter PyPI 组织](https://pypi.org/org/jupyter/) 下发布 Python 包 |
| Team Compass | 维护公开的 Team Compass，列出 Subproject Council 成员 |

## 两类官方子项目

### 第一类：有独立 Council 和 SSC 代表的子项目

这些是规模较大、活跃度高的子项目，拥有独立的 Subproject Council，并选举一名代表参加 SSC。

当前包括10个子项目/团队：

| 子项目 | 核心组件 |
|--------|---------|
| **Jupyter Frontends** | JupyterLab、Jupyter Notebook、JupyterLite |
| **JupyterHub and Binder** | JupyterHub、Binder、BinderHub、JupyterHealth |
| **Voilà** | Voilà 仪表盘 |
| **Jupyter Server** | Jupyter Server、Enterprise Gateway、Kernel Gateway |
| **Jupyter Widgets** | ipywidgets 等交互组件 |
| **Jupyter Kernels** | jupyter-xeus、IPykernel、IPython |
| **Jupyter Foundations and Standards** | Jupyter Client、nbformat、JEPs repo、标准协议等 |
| **Jupyter Security** | 安全响应 |
| **Jupyter Accessibility** | 无障碍访问 |
| **Jupyter Book** | Jupyter Book 出版工具 |

### 第二类：无独立 SSC 代表的子项目

这些是规模较小或活跃度较低的子项目，其正式 Subproject Council 由 SSC 直接担任。SSC 将没有广泛跨项目影响的决策委托给子项目维护者自主处理。

当前包括：
- **nbdime**：Notebook diff/merge 工具
- **nbgrader**：Notebook 评分工具
- **nbviewer**：Notebook 在线查看器（可重用部分，服务运营由 EC 工作组管理）
- **ipyparallel**：IPython 并行计算
- 其他未明确归属上述组织的官方仓库

这类子项目如果成长壮大，SSC 可随时为其选举独立 Council，届时该子项目将获得独立的 SSC 代表。

## 孵化子项目（Incubator Subprojects）

[Jupyter Incubator](https://github.com/jupyter-incubator) 是实验性和早期项目的家园。孵化中的项目：

- 承担与正式子项目相同的责任
- 不拥有官方 SSC 代表权
- 只有"毕业"为正式子项目后才获得 SSC 代表

## 子项目服务管理

需要注意的是，**实际运行的服务**（如 Binder、nbviewer、jupyter.org 网站）与代码仓库的治理归属不同：

- 服务涉及法律、财务和运营事务，由向 EC 报告的 Working Group 管理
- 例如 nbviewer 的可重用代码部分是无 SSC 代表的子项目，但 nbviewer 的在线服务由向 EC 报告的工作组管理
- Jupyter 网站由向 EC 报告的工作组管理

## 反常识要点

- **"官方子项目"不等于"Jupyter 组织下的所有仓库"**：Jupyter GitHub 组织中有大量仓库，但只有经过正式准入流程的才是官方子项目。
- **子项目自治是默认状态**：SSC 不干预子项目日常决策，只处理跨项目协调问题。这与一些开源基金会中"技术委员会审批一切"的模式形成对比。
- **小项目也有位置**：通过 SSC 代管机制，小项目不需要建立复杂的治理结构就能成为 Jupyter 官方子项目。

## 相关概念

- [软件指导委员会（SSC）](04-software-steering-council.md)
- [新子项目准入与孵化](11-new-subprojects.md)
- [决策制定流程](09-decision-making.md)
- [常设委员会与工作组](07-committees-and-working-groups.md)
