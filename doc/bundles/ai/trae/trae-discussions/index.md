---
type: Index
title: TRAE 社区讨论
description: trae-discussions 是 TRAE 社区讨论区的知识整理，涵盖讨论分类、社区礼仪和参与指南，帮助用户高效参与社区交流。
tags: [trae-discussions, trae, discussion, community, forum, etiquette]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/discussions-source.md
    title: "Trae Discussions 源码信源"
---

# TRAE 社区讨论知识包

本知识包系统介绍 [trae-discussions](https://github.com/trae-community/trae-discussions) 仓库——TRAE 社区的技术讨论和知识分享导向枢纽。内容涵盖 GitHub Discussions 论坛模式、5 大讨论分类、社区礼仪以及发起讨论的实战指南。

## 概念篇（concepts/）

- [GitHub Discussions 作为社区论坛](/concepts/00-introduction.md) — 导向枢纽定位（不承载讨论内容，只做路标）、组织级 vs 仓库级 Discussions 区别、3 文件极简仓库模式（README 中英+LICENSE）、Quick Links 串联分散资源。
- [讨论分类与使用指南](/concepts/01-discussion-categories.md) — 5 个讨论分类（📚General / 💡Ideas / ❓Q&A / 📖Knowledge Sharing / 🤝Collaboration）的用途详解、分类选择决策逻辑、4 步参与流程。
- [社区礼仪与有效提问指南](/concepts/02-community-etiquette.md) — 4 条行为准则（尊重他人/保持主题/先搜索/质量内容）、中英文双语规范、Q&A 有效提问模板、知识分享和协作配对指南。

## 示例篇（examples/）

- [发起讨论示例](/examples/start-discussion.md) — 4 种讨论类型的发帖实战：Q&A 提问（含完整模板）、Knowledge Sharing 经验分享（TDD 工作流示例）、Ideas 功能建议、Collaboration 招募合作者，含发帖注意事项。

## 信源登记簿（references/）

- [社区讨论仓库资源索引](/references/discussions-source.md) — 仓库基本信息、3 文件目录结构、5 分类速查表、4 步参与指南、4 条社区准则、Quick Links 映射。

## 关键事实

- trae-discussions 是**极简导航枢纽**：整个仓库仅 3 个文件（README.md 英文、README.zh-CN.md 中文、LICENSE），无代码、无模板、无资源文件
- 讨论实际发生在**GitHub 组织级 Discussions**（`github.com/orgs/trae-community/discussions`），而非仓库级 Discussions
- ⚠️ README 引用的横幅图片路径 `./assets/images/` **目录不存在**，图片无法显示，可能是模板生成后未完全配置，但不影响核心导航功能
- 定义 **5 个讨论分类**覆盖社区互动全场景：社交（General）、建议（Ideas）、求助（Q&A）、分享（Knowledge）、协作（Collaboration）
- Quick Links 指向的治理文档（CONTRIBUTING.md / CODE_OF_CONDUCT.md）位于 GitHub Organization 的 `.github` 仓库中，不在本仓库内

```{toctree}
:hidden:
:maxdepth: 7

concepts/00-introduction
concepts/01-discussion-categories
concepts/02-community-etiquette
examples/start-discussion
references/discussions-source
spec/facts
spec/insights
```
