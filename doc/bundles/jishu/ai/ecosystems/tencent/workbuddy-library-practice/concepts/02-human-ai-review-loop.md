---
type: Concept
title: "人机共编：把修改建议放进可审阅的闭环"
description: "从明确修改范围到检查差异、确认写回，建立人保留决定权的文档协作方式。"
tags: [WorkBuddy, 人机协作, 文档审阅, 修改边界, 内容治理]
generated: { by: "process:seven-concepts-e", at: "2026-10-19" }
status: draft
stale_after: "2026-12-31"
sources:
  - { id: S06, resource: "https://www.workbuddy.cn/space/d/f6dhUR3e5ZAfXJJVDIOxSG", title: "人机协作：和 AI 一起改文档" }
  - { id: S01, resource: "https://www.workbuddy.cn/space/d/guTORrnry3ajlXZ275LEgI?source=3", title: "资料库新手教程" }
  - { id: official-library, resource: "../../workbuddy-official-docs/concepts/06-knowledge-base-and-library.md", title: "官方编辑行为与载体差异" }
---

# 人机共编：把修改建议放进可审阅的闭环

## 读者问题

怎样让 Agent 帮忙修改文档，同时让作者清楚知道改了什么，并保留接受、拒绝或继续调整的决定权？

S06 将协作关系概括为“人提出范围和意图，AI 生成修改，人审阅并决定是否生效”；页面还把流程拆为提出诉求、AI 修订、展示对比、人工定夺四步（F-012、F-043）。S01 也描述了选中内容后提出修改要求的用法（F-003）。这里沉淀的是协作原则，而不是重复官方编辑器操作手册。

## 四步审阅闭环

| 阶段 | 人与 Agent 的分工 | 审阅问题 |
| --- | --- | --- |
| 界定范围 | 人指出要修改的段落、目标或评论 | 选区是否准确？要求是否说明受众和目的？ |
| 生成建议 | Agent 按指定意图提出修改 | 是否保留了原意、证据和必要限定？ |
| 检查差异 | 人比较原文与修改稿 | 新增、删除或改写是否改变事实口径？ |
| 作出决定 | 人接受、拒绝或要求继续调整 | 是否需要作者、业务负责人或专业人员复核？ |

这张表是对 S06 流程的结构化整理（F-043）。它强调“可审阅”而非“自动正确”：即使修改范围很小，也应检查数字、限定词、承诺语气和引用是否被改变。

## 按风险决定审阅强度

- **低风险表达调整**：例如简化句子或改善排版，可由内容负责人快速检查。
- **涉及事实或对外承诺**：核对引用、数字、责任主体与适用条件，再决定写回。
- **涉及权限、合规或专业判断**：交由相应负责人复核，不把语言流畅误当作判断正确。

这是本页的审阅建议，不是 S06 原文规定，也不代表平台具备自动风险识别。需要形成团队约定时，可为不同类型文档指定审批人和回退方式。

## MD 与 HTML 的行为边界

S06 描述了 Markdown 修改以修订方式呈现并由人确认，以及 HTML 划词后直接修改、即时可见的差别（F-013）。产品编辑行为以[官方资料库文档](../../workbuddy-official-docs/concepts/06-knowledge-base-and-library.md)的 F-169–F-170 为准。两种载体的交互不能混为同一种审阅机制；尤其对直接写回的页面，应在修改前保留必要副本或确认页面的回退能力。

## 适用边界

- Agent 的修改是候选文本，不自动构成事实核验。
- 对照原文时，优先检查数字、条件、否定词、因果关系和出处。
- 如果协作者无法确认修改的影响范围，先拒绝写回或请责任人复核。
- 官方编辑入口与产品行为参见[官方概念页](../../workbuddy-official-docs/concepts/06-knowledge-base-and-library.md)，不要依据本页推断版本功能。

## 来源与参照

- 来源事实：F-003、F-012、F-013、F-043。
- 产品编辑机制：[资料库与知识库](../../workbuddy-official-docs/concepts/06-knowledge-base-and-library.md)。
- 完整来源与边界：[来源台账](../references/article-source.md)、[核验记录](../references/verification.md)。
