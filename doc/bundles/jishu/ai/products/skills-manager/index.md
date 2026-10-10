---
okf_version: "0.2"
type: bundle
title: Skills Manager 跨 AI 编程工具技能库
description: 微信公开文章经官方 README、Release API 与实现源码交叉核验——集中式 Skill 管理、Agent 集成、Windows/WSL 链接边界、Git 备份同步与凭证限制的概念型知识包（非实机操作教程）
tags: [skills-manager, skills, ai-coding, agent, backup, sync, windows, wsl]
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
  - id: github-repo
    url: "https://github.com/xingkongliang/skills-manager"
  - id: github-readme
    url: "https://raw.githubusercontent.com/xingkongliang/skills-manager/9e03d833829bc5e004263f61dec75f3bc8e39062/README.md"
  - id: github-release-api
    url: "https://api.github.com/repos/xingkongliang/skills-manager/releases/latest"
  - id: github-api
    url: "https://api.github.com/repos/xingkongliang/skills-manager"
---

# Skills Manager 跨 AI 编程工具技能库

> **类型**：产品机制与适用边界的概念型知识包（非实机操作教程）
> **信源**：微信公开文章《又一个 skill 神级工具，帮我省了太多时间。》（开源日记，2026-10-04）+ 官方 GitHub 仓库 README、Release API 与实现源码交叉核验
> **P0 核验**：数量、版本、平台、备份阈值、链接回退与凭证机制均登记核验来源与适用边界；作者体验与履历标为单源主张

## 先读结论

Skills Manager 是一款开源的集中式 Skill 管理桌面产品，目标是统一管理散落在各 AI 编程工具中的技能（Skills），并支持跨工具复用、Git 备份与多设备同步。官方 README 在 `Supported Tools` 节称开箱支持 **54 个 Agent**（README 快照对应主分支提交 `9e03d833…`），仓库 API 描述为“50+ coding tools”，与文章所称“54 个 AI 编程工具/Agent”在字面上相互支持，但 `agents` 与 `coding tools` 术语不同，不能据此断言统计对象完全相同。

**时效警示**：本包的版本与数量结论全部来自 **2026-10-10 的官方来源动态快照**（latest release 为 `v1.40.3`，发布于 2026-10-01）。Skills Manager 迭代较快，README、Release 与仓库描述会随时变化；引用本包结论前请先核对当时官方仓库。本文文章本身未标注所介绍功能对应的产品版本，也未提供完整测试环境或逐步输入输出，因此不是可照做的操作教程。

## 文档结构

### concepts/ — 概念解析

| 文档 | 主题 |
|------|------|
| [00-product-and-skill-library.md](concepts/00-product-and-skill-library.md) | 产品定位、技能库与中央库路径、导入/市场、预设、支持数量口径、版本时点与作者主张 |
| [01-tool-integration-and-platform-boundaries.md](concepts/01-tool-integration-and-platform-boundaries.md) | Agent 工作区与管理 CLI、桌面平台与安装资产、Windows junction 与 WSL 边界 |
| [02-git-backup-sync-and-credential-boundaries.md](concepts/02-git-backup-sync-and-credential-boundaries.md) | 私有 GitHub 备份、设备授权、同步冲突/快照、大小限制、凭证与作者体验主张 |

### references/ — 信源登记

| 文档 | 说明 |
|------|------|
| [article-source.md](references/article-source.md) | 原文事实清单（F-001 至 F-044），与 Spec `facts.md` 双份编号一致 |
| [verification.md](references/verification.md) | P0 核验报告：官方来源快照、数量口径对照、版本视口、勘误登记 |
| [source-manifest.md](references/source-manifest.md) | 来源清单：文章、官方仓库/README/API/Release 及观察时间 |

## 主题关联

- [mattpocock-skills](../../learning/mattpocock-skills/index.md)：SKILL.md 技能目录约定的生态对标（Anthropic Agent Skills 范式）
- [todesk-ai](../todesk-ai/index.md)：同为桌面端 Agent/技能管理工具（技能体系视角互补）

## 已知边界

- **未实测**：本包为概念型知识包，未创建 `examples/`。文章未给完整逐平台流程、版本、测试环境与恢复验证步骤，作者未声明亲测；据此两问判定不设实操示例，也不承诺读者可照做安装/恢复。
- **动态快照**：数量（54 agents / 50+ coding tools）与版本（v1.40.3）为 2026-10-10 观测；依赖动态接口的结论仅代表本次观测，不构成长期版本保证。
- **单源主张**：作者履历（前腾讯优图高级研究员/机器学习博士/ICCV 冠军）、使用体验评价与第三方“基本就是刚需”转述均为文章单源，不作为已核实事实。
- **源码边界**：凭证处理与 100 MiB 阈值等结论来自源码阅读（非实机验证或安全审计）；文章单源主张明确标注待核验。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```