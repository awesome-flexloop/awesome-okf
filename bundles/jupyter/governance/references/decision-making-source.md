---
type: Reference
title: "决策制定指南源码"
description: "Decision-Making Guide（docs/decision_making.md）的信源登记。"
tags: [reference, source, decision-making, voting, consensus]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T08:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T08:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: dm-doc
    resource: https://github.com/jupyter/governance/blob/main/docs/decision_making.md
    title: "docs/decision_making.md"
---

# 决策制定指南信源

**原始文件路径**：`docs/decision_making.md`

**内容摘要**：

所有 Jupyter 治理机构统一使用"寻求共识+投票兜底"的决策流程。

**必要流程（所有机构必须遵循）**：

1. **非正式共识寻求**：通过讨论完善提案、考虑替代方案、权衡取舍、寻求非正式共识。所有利益相关者必须有发言机会。达成共识后可直接记录和执行决策。

2. **发起投票**：共识阶段讨论成熟后，任何成员可发起投票。发起者需总结当前提案；另一成员附议后进入7天投票期。二选一决策使用简单多数，多选项决策使用排序复选制（ranked choice）。发起者可在投票期更新提案，此时投票期重置。

3. **投票参与率和法定人数**：所有成员每年必须参与至少2/3的正式投票，未达标者自动被要求卸任（可未来重新加入）。法定人数为50%，始终包含"空白"选项，空白票计入法定人数但不计入结果计算。

4. **记录**：决策通过后必须公开记录（如 GitHub Team Compass issues）。

**可选建议**：
- 不应通过投票来短路仍在有效进行的讨论
- 应主动征求利益相关者意见，不假设沉默即同意
- 区分"双向门"（易逆转）和"单向门"（难逆转）决策，单向门需更谨慎
- 软件项目建议使用 `seeking consensus`、`vote`、`decision made` 标签

**EC 可干预场景**：流程模糊、违反决策流程、需要流程例外等。

**关键事实锚点**：F-021, F-022, F-023
