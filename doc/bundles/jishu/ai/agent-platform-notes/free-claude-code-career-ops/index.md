---
okf_version: "0.2"
type: bundle
title: "free-claude-code 与 career-ops：从模型接入到求职工作流"
description: "微信公众号文章的 OKF 七阶段转化——两个开源项目的职责分层、组合闭环、免费额度与隐私边界；开源项目资讯综述，非操作教程。"
tags: [free-claude-code, career-ops, Agent, 开源工具, 求职自动化, 组合架构]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-10-31
sources:
  - { id: blog, resource: "https://mp.weixin.qq.com/s/yEmCTdlwaKyj_h9eQRBsJg" }
  - { id: fcc, resource: "https://github.com/Alishahryar1/free-claude-code" }
  - { id: career, resource: "https://github.com/santifer/career-ops" }
---

# free-claude-code 与 career-ops：从模型接入到求职工作流

> **内容性质：开源项目资讯与组合机制综述，非操作教程。** 文章没有固定版本、完整输入输出和可复现实操步骤，因此本 bundle 不设 `examples/`。

> **证据警示：flagged。** “每月 13 亿 token”“最多节省 90%”和“全程不花一分钱”分别受 provider 免费层、工具自述和外部 API 条件影响，不应视为长期保证。[F-005][F-009][F-013][F-028]

## 这篇文章讲了什么

文章把两个不同层次的开源项目放在一起：`free-claude-code` 负责模型与编码 Agent 的连接，`career-ops` 负责职位筛选、材料生成和投递追踪。[F-002][F-006][F-014]

## 阅读路径

1. [两个项目分别解决什么问题](concepts/00-project-facts.md)
2. [从模型接入到求职工作流的组合闭环](concepts/01-combination-loop.md)
3. [免费访问、隐私与人工确认的边界](concepts/02-access-and-risk-boundaries.md)
4. [P0 声明核验与勘误](references/verification.md)

## 主题关联

本 bundle 与 [Agent 平台散篇笔记](../index.md) 同属 AI Agent 工具资讯聚合；它关注“模型接入层 + 任务工作流层”的组合，不替代单个项目的源码教程。

## 已知边界

- 星标与免费额度是时间快照，须以当前仓库和 provider 页面为准。[F-003][F-004][F-013]
- 作者的职位数量和 offer 是个人案例，不是求职成功率实验。[F-023]
- 本任务未安装项目、未调用 API、未验证 provider 实时限额。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
