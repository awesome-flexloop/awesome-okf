---
type: Reference
title: "成员准入指南信源"
description: "docs/team/becoming-member.md 的信源登记，包含 Council 成员、Release Team、Admin Team 三个层级的加入流程、职责和维护机制。"
tags: [reference, source, membership, release-team, admin-team]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T11:35:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:35:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: becoming-member
    resource: https://github.com/jupyterlab/frontends-team-compass/blob/main/docs/team/becoming-member.md
    title: "docs/team/becoming-member.md"
---

# 成员准入指南信源

**原始文件路径**：`docs/team/becoming-member.md`

**内容摘要**：

文档定义了 Jupyter Frontends Council 成员的三类身份及各自的加入流程、职责和维护机制。

## Council 成员职责
- 须由现任成员提名
- 可被选举为 SSC 代表
- 投票情境下有投票权
- 计入法定人数（quorum）
- 每年须参与至少 2/3 的投票
- 可提名新成员
- 应积极参与会议（同步或异步）

## 新成员提名流程
1. 提名者先在 Council 内部讨论，确保有广泛共识
2. 如有明显共识则继续，否则可进行内部投票（保护候选人隐私）
3. Council 成员联系潜在成员询问意愿，并提供成员指南

## 成员维护
- 每6个月 bot 开 Issue，成员需3周内回复确认活跃
- 回复"否"则移除；不回复则个人联系；一个月不回复则移除

## Release Team
- 任何 Council 成员可申请加入（建议私聊渠道）
- 获得 GitHub/PyPI/NPM/conda-forge 发布权限
- 可发布主要 JupyterLab 相关包，在包损坏时快速响应

## Admin Team
- 最多7名管理员
- SSC 代表自动成为管理员
- EC（执行委员会）必须拥有至少一个管理员席位
- 拥有 GitHub/PyPI/NPM 组织 owner 权限
- 负责维护 Council 和 Release Team 成员资格

**关键事实锚点**：
- F-013: Council 分两个子组（release + admin）
- F-014: 新成员须现任提名+内部共识
- F-015: 每6个月活跃确认
- F-016: Release Team 的发布权限范围
- F-017: Admin 最多7人，SSC代表自动加入，EC必须占一席
- F-018: Admin 拥有 owner 权限
