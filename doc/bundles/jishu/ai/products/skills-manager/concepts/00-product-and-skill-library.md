---
okf_version: "0.2"
type: concept
title: 产品定位与技能库
description: Skills Manager 的产品定位、中央技能库、导入/市场、预设与支持数量口径
tags: [skills-manager, skill-library, central-library, presets]
generated:
  by: process:seven-concepts
  at: "2026-10-10T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-10T00:00:00+08:00"
status: flagged
stale_after: "2026-12-31"
sources:
  - id: wechat-article
    url: "https://mp.weixin.qq.com/s/G4jm1Y2wAJUWSSnazAGdxg"
  - id: github-readme
    url: "https://raw.githubusercontent.com/xingkongliang/skills-manager/9e03d833829bc5e004263f61dec75f3bc8e39062/README.md"
  - id: github-api
    url: "https://api.github.com/repos/xingkongliang/skills-manager"
  - id: github-release-api
    url: "https://api.github.com/repos/xingkongliang/skills-manager/releases/latest"
---

# 产品定位与技能库

## 产品定位

Skills Manager 是一套开源的集中式 Skill 管理桌面产品，面向跨 AI 编程工具统一管理与复用技能（Skills）。文章将其描述为“集中管理 AI 编程工具 Skills 的桌面产品”（F-005）；官方 README 也将其描述为统一技能库，并说明技能可以在支持的 AI 编程工具之间复用（F-022）。

- 官方仓库为 `xingkongliang/skills-manager`，公开许可为 MIT（F-021）。
- 文章称产品开源，并指向公开 GitHub 仓库（F-017）。
- **作者身份**：文章称作者曾任腾讯优图高级研究员、拥有机器学习博士学位并获得 ICCV 挑战赛冠军，但未提供可独立核实的身份材料，因此按单源主张处理，不作为已核实履历（F-042）。

## 中央技能库

- 技能库以卡片形式呈现技能，并展示来源及同步目标等信息（F-006）。
- 文章称中央技能库默认位于 `~/.skills-manager`；该默认路径在官方 README 同一快照中亦有记载（F-034）。
- 首次启动时应用会自动创建中央技能库，并扫描电脑上已有的 AI 工具，将技能集中纳入统一技能库（F-008、F-035）。

## 导入与市场

- 文章称技能可从 **Git 仓库、本地文件夹及 `.zip`/`.skill` 压缩包**导入（F-033）。
- 文章称可在内置 skills.sh 市场浏览技能，并按关键词搜索（F-033）。

## 预设

- 文章称技能可分组为**命名预设**，并按当前工具一键启用或停用整组技能；官方 README 同一快照也描述预设功能（F-040）。

## 支持数量口径

截至 2026-10-10 的快照：

- 文章称支持 54 个 AI 编程工具/Agent（F-007）。
- 官方英文 README `Supported Tools` 节称支持 **54 agents ... out of the box**，并列出部分具名集成；还说明设置中可添加自定义工具。该 README 快照对应主分支提交 `9e03d833…`（F-023）。
- 官方仓库 API 描述为 **50+ coding tools**（F-021）。

三处数字在字面上相互支持，但 `agents` 与 `coding tools` 术语不同，**不能据此断言统计集合完全相同**（F-024）。引用动态数量时务必保留来源字段与观察日期。

## 版本时点

- 2026-10-10 复核的 `releases/latest` API、Release 列表首项与网页 `/releases/latest` 均指向 **v1.40.3**（发布于 2026-10-01）（F-030）。
- 仓库 API `updated_at` 为 `2026-10-10T04:32:24Z`；主分支 README 快照对应提交 `9e03d833…`（2026-10-09 提交）（F-031）。
- 文章本身未标明所介绍功能对应的产品版本，也未提供测试环境、逐步输入输出或独立复核记录（F-019）；文章不是可照做的操作教程（F-020）。

## 适用性边界

- 文章以“省了太多时间”表达个人体验，该项为作者评价，无独立量化数据，不推导为普遍收益（F-018）。
- 文章引用第三方软件站称多工具用户使用“基本就是刚需”，并认为只用单一工具时 Git 仓库加软链接可能更简单——此为该语境的**价值判断**，不作普遍结论（F-044）。