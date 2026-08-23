---
type: Concept
title: 投稿流程与多场景 Issue 模板
description: trae-demos 的投稿审核流程、5 种场景 7 个 YAML Issue 模板设计、TRAE Usage 40% 最高权重的审核标准
tags: [demos, contribution, issue-templates, review-criteria, trae-demos, trae]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/demos-source.md
    title: "Trae Demos 源码信源"
---

# 投稿流程与多场景 Issue 模板

## 投稿流程

向 trae-demos 提交 Demo 的流程为：

```
检查 Must Have 标准 → 通过 Issue 模板提交 → 24h 内确认 → 3-5 工作日审核 → 通过后展示
```

1. **检查要求**：投稿前自检是否满足 4 项 Must Have 标准
2. **Issue 提交**：选择对应语言的 submit_demo 模板填写（非 PR 提交）
3. **确认**：维护者在 24 小时内确认收到投稿
4. **审核**：3-5 个工作日内按权重评分完成审核
5. **展示**：审核通过后，维护者将 Demo 添加到对应期数目录

> 💡 注意：trae-demos 采用**Issue 驱动**投稿，投稿者无需 Fork 仓库或编写 Markdown 文件，只需在 GitHub 网页填写 Issue 表单即可。审核通过后由维护者负责创建 Demo Markdown 文件并展示。

## 投稿 4 项 Must Have 标准

| 标准 | 说明 |
|------|------|
| 使用 TRAE 作为核心技术 | 项目构建过程中 TRAE 是核心开发工具，非偶尔使用 |
| 可访问 | 开源仓库或在线演示链接可公开访问 |
| 代码质量良好 | 代码质量达标，有基本文档（README） |
| 完成度较高（polished） | 非半成品原型，功能完整可用 |

## 审核权重：TRAE Usage 最高

trae-demos 的审核评分权重设计强调平台定位——**展示用 TRAE 构建的项目**：

| 维度 | 权重 | 说明 |
|------|------|------|
| **TRAE Usage** | **40%** | 最高权重，TRAE 在项目中使用的深度和核心性 |
| Code Quality | 25% | 代码质量和工程规范 |
| Completeness | 20% | 项目完成度和 polished 程度 |
| Documentation | 15% | README 和使用说明质量 |

TRAE Usage 占 40% 是关键设计——这确保平台聚焦"用 TRAE 构建"而非泛项目展示。一个质量很高但未使用 TRAE 的项目不会被收录。

## 5 种场景的 Issue 模板

项目配置了 7 个 YAML Issue 模板文件，覆盖 5 种社区互动场景：

| 场景 | 模板文件 | 语言 | 用途 |
|------|---------|------|------|
| 投稿 Demo | submit_demo_en.yml / submit_demo_zh.yml | 中英双语 | 提交新 Demo |
| 报告问题 | report_demo_en.yml / report_demo.yml | 中英双语 | 反馈已收录 Demo 的问题（链接失效等） |
| 更新信息 | update_demo.yml | - | 请求更新已收录 Demo 的信息 |
| 需求征集 | want_demo.yml | - | 提出想看的 Demo 类型或投票 |

config.yml 配置了两个关键设置：
- `blank_issues_enabled: false`：**禁止空 Issue**，所有互动必须通过结构化表单
- 提供联系链接：指向 `https://github.com/orgs/trae-community-org/discussions` 讨论区

## 多场景模板的设计意义

相比多数项目只用一个"submit"模板，trae-demos 区分 4 种社区行为：

1. **投稿（submit）**：提交新项目
2. **报告（report）**：反馈现有项目问题
3. **更新（update）**：修正已有信息
4. **需求（want）**：提出想看的内容

特别是 **want_demo** 模板让社区可以投票/提出想看的 Demo 类型，形成**需求侧驱动**，而非仅由维护者决定收录什么。

## 5 个项目分类

审核时投稿项目归入以下分类：

- 🌐 Web Applications
- 🛠️ Tools & Utilities
- 🎮 Games
- 🤖 AI Applications
- 🎨 Other

## 相关链接

- [TRAE Demos 定位与期数制组织](/concepts/00-introduction.md)
- [Demo Markdown 文档格式](/concepts/01-demo-format.md)
- [提交 Demo 示例](/examples/submit-demo.md)
- [TRAE Demos 仓库资源索引](/references/demos-source.md)
