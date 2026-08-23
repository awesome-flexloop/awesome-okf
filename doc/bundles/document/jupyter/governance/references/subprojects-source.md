---
type: Reference
title: "软件子项目文档源码"
description: "Software Subprojects 文档（docs/software_subprojects.md、docs/list_of_subprojects.md、docs/newsubprojects.md）的信源登记。"
tags: [reference, source, subprojects, software]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: subprojects-doc
    resource: https://github.com/jupyter/governance/blob/main/docs/software_subprojects.md
    title: "docs/software_subprojects.md"
  - id: list-subprojects-doc
    resource: https://github.com/jupyter/governance/blob/main/docs/list_of_subprojects.md
    title: "docs/list_of_subprojects.md"
  - id: newsubprojects-doc
    resource: https://github.com/jupyter/governance/blob/main/docs/newsubprojects.md
    title: "docs/newsubprojects.md"
---

# 软件子项目信源

**原始文件路径**：
- `docs/software_subprojects.md` - 子项目责任定义
- `docs/list_of_subprojects.md` - 官方子项目列表
- `docs/newsubprojects.md` - 新子项目准入流程

**内容摘要**：

**子项目责任**：
- 遵守行为准则和决策流程
- 指定并维护一名 SSC 代表
- 遵循许可证和商标/品牌指南
- 开放、透明、包容地开展活动
- 源代码托管在 Jupyter GitHub Enterprise 组织中
- PyPI 包发布在 Jupyter PyPI 组织下
- 维护公开的 Team Compass 和 Subproject Council 成员列表

**两类子项目**：
1. **有 SSC 代表的官方子项目**：Jupyter Frontends、JupyterHub and Binder、Voilà、Jupyter Server、Jupyter Widgets、Jupyter Kernels、Jupyter Foundations and Standards、Jupyter Security、Jupyter Accessibility、Jupyter Book
2. **无独立 SSC 代表的子项目**：较小/低活跃度，SSC 直接担任其 Council，包括 nbdime、nbgrader、nbviewer、ipyparallel 等

**新子项目准入标准**：
- 活跃的开发者社区（可持续发展模式）
- 活跃的用户社区
- 扎实的软件工程（文档+测试）
- 持续增长和发展
- 与现有子项目良好集成
- 遵循 Jupyter 治理和贡献模型
- 明确的范围
- 使用适当的打包技术（pip/conda/npm/docker等）

**两条准入路径**：
1. 直接创建：SSC 共识→EC 批准 PR
2. 外部项目并入：JEP 提案→社区讨论→SSC 推荐→EC 决定

**孵化**：jupyter-incubator 组织提供中立孵化场地，通常需6个月到1年孵化期。

**关键事实锚点**：F-014, F-026, F-027, F-028, F-041, F-042
