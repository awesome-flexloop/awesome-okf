---
type: Reference
title: "2020年用户调查信源"
description: "docs/surveys/2020-jupyterlab-survey.md 的信源登记，包含20个调查问题，覆盖使用模式、数据、可视化、规模、协作、UI挑战六大维度。"
tags: [reference, source, survey, user-research, 2020]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T11:35:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:35:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: survey
    resource: https://github.com/jupyterlab/frontends-team-compass/blob/main/docs/surveys/2020-jupyterlab-survey.md
    title: "docs/surveys/2020-jupyterlab-survey.md"
---

# 2020年用户调查信源

**原始文件路径**：`docs/surveys/2020-jupyterlab-survey.md`

**内容摘要**：

2020年 JupyterLab 用户调查问卷，共20个问题+1个开放反馈+1个可选访谈邀请。调查数据将在12月中旬投票结束后公开共享。用户邮箱仅用于访谈邀请，不做推广、不共享给第三方。

## 调查结构

| 板块 | 题号 | 主题 |
|------|------|------|
| 使用模式 | Q1-Q7 | 使用频率/时长、语言、角色、工具、运行方式、任务频率与满意度 |
| 数据 | Q8-Q11 | 数据源、数据格式、数据相关问题评分、分析类型 |
| 可视化 | Q12-Q13 | Dashboard工具、可视化问题评分 |
| 规模 | Q14-Q15 | 扩展调度方式、规模问题评分 |
| 协作 | Q16-Q19 | 协作者数量、分享原因、协作性质、协作挑战评分 |
| UI | Q20 | UI挑战评分 |

## 关键发现维度（问题类型）
- **频率/程度题**：使用 Likert 量表（Never→Daily / No→Yes / Not a problem→Critical）
- **多选题**：语言（最多4种）、工具（最多3种）、数据源（最多3种）
- **矩阵题**（Q7）：任务×频率×Jupyter满足度×替代工具满足度（最大一题）
- **评分题**（Q10/Q13/Q15/Q19/Q20）：0-4 或 0-5 级问题严重程度
- **嵌套题**（Q18）：协作性质包含时长/频率/分工三个子问题

**关键事实锚点**：
- F-027: 20个问题分5大板块+开放反馈
