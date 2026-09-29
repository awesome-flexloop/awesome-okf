---
type: Reference
title: 共创项目仓库资源索引
description: trae-co-creation-projects 仓库源码位置、Issue 表单驱动投稿、Collaboration 30% 权重审核和分类体系的信源登记簿
tags: [co-creation, trae, issue-driven, collaboration-weight, source-index, trae-co-creation]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/co-creation-source.md
    title: "Trae 共创项目源码信源"
---

# 共创项目仓库资源索引

本文档汇总 trae-co-creation-projects 仓库的定位、投稿机制和审核标准。

## 仓库基本信息

| 项目 | 内容 |
|------|------|
| 仓库地址 | `trae-community/trae-co-creation-projects`（GitHub） |
| 许可证 | MIT License，提交项目版权归各自作者所有 |
| 定位 | 社区驱动的 TRAE 协作 AI 编程项目展示平台 |
| 语言支持 | 中英双语（README.md / README_zh.md） |
| 当前状态 | **初始化阶段**，README 无已收录项目列表 |

## 仓库目录结构

```
trae-co-creation-projects/
├── README.md                 # 英文 README
├── README_zh.md              # 中文 README
├── CONTRIBUTING.md           # 英文贡献指南
├── CONTRIBUTING.zh-CN.md     # 中文贡献指南
├── LICENSE
├── assets/image/
│   └── Co-creation Projects.gif  # 横幅图片（URL 编码空格）
└── .github/ISSUE_TEMPLATE/
    ├── project-submission.md    # 英文投稿模板
    └── project-submission-zh.md # 中文投稿模板
```

## 6 个项目分类

| 分类 | Emoji | 说明 |
|------|-------|------|
| Web Applications | 🌐 | 全栈 Web 应用 |
| Tools & Utilities | 🛠️ | 开发者工具/CLI/效率工具 |
| AI & Machine Learning | 🤖 | AI/ML 项目 |
| Open Source Libraries | 📦 | 可复用库和框架 |
| Learning Resources | 📚 | 教程/指南/教育内容 |
| Other | 🎨 | 游戏/移动/IoT/艺术装置等 |

## 投稿 4 项 Must Have 标准

1. **使用 TRAE 作为核心协作工具**：TRAE 是项目的核心开发协作工具
2. **展示有意义的协作**：团队协作、结对编程，或 AI 结对编程（人机协作）
3. **可访问**：公开仓库或在线演示链接
4. **有基础文档**：README 或文档说明

> 💡 接受个人项目投稿，但需展示 TRAE 如何促进协作（如 AI 结对编程）。接受任何阶段的项目（从想法到生产）。

## 审核评分权重

| 维度 | 权重 | 说明 |
|------|------|------|
| TRAE Usage | 40% | TRAE 在项目中的使用深度 |
| **Collaboration** | **30%** | **第二高权重，体现"共创"核心定位** |
| Code Quality | 20% | 代码质量 |
| Documentation | 10% | 文档质量 |

与 trae-demos 的关键差异：Collaboration 占 30%（vs demos 的 0%），这是"共创"与"演示"的本质定位区别。

## 投稿需提供 4 类信息

1. **Project Information**：名称、仓库链接、演示链接、项目类型
2. **Description**：一句话描述 + 详细描述
3. **Collaboration Details**：团队规模、协作类型、TRAE 使用场景
4. **Technical Details**：技术栈、核心功能、截图

## 投稿流程

```
检查要求 → 创建 Issue（Project Submission 模板）→ 24h 内确认 → 3-5 工作日审核 → 通过后展示
```

与 trae-demos 相同，采用 Issue 表单驱动投稿，贡献者无需 Fork/PR。

## 联系方式

- GitHub Issues
- GitHub Discussions
- TRAE Discord（discord.gg/trae）

## 相关链接

- [共创项目仓库定位与协作核心理念](../concepts/00-introduction.md)
- [项目提交流程与 Issue 表单](../concepts/01-project-submission.md)
- [审核标准与 Collaboration 权重](../concepts/02-review-criteria.md)
- [提交共创项目示例](../examples/submit-project.md)
