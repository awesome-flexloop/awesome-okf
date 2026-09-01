---
type: Concept
title: "扩展贡献到 JupyterLab 组织"
description: "了解将第三方 JupyterLab 扩展贡献到 JupyterLab GitHub 组织的完整流程、评审标准和后续步骤。"
tags: [jupyter, jupyterlab, extension, contributing, subproject, adoption]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T11:38:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:38:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: "README 文档信源"
---

# 扩展贡献到 JupyterLab 组织

JupyterLab 的设计理念是培育丰富的插件生态。当第三方扩展成熟后，维护者可能希望将其贡献给 Project Jupyter，在 JupyterLab GitHub 组织下维护，接受 Jupyter 官方治理。本文档描述这一过程的完整流程。

## 前置条件

将扩展贡献到 JupyterLab 组织意味着接受 Jupyter 项目的治理框架，包括：

- ✅ 采用标准的 Jupyter 许可证（3-Clause BSD）和共享版权模型
- ✅ 遵守 Project Jupyter 社区指南
- ✅ 接受 BDFL、Steering Council 和 Jupyter 治理体系的管辖

## 四步贡献流程

```
┌──────────────────────────────────────────────────────────┐
│ 第一步：考虑 jupyterlab-contrib                          │
│ 许多扩展更适合放在社区维护的 jupyterlab-contrib 组织中    │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ 第二步：在 frontends-team-compass 提 Issue               │
│ 描述扩展、链接现有代码、回应子项目准入标准的每一点         │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ 第三步：社区评审（至少一周）                              │
│ - 核心维护者审查代码质量                                  │
│ - 评估维护者的社区参与度                                  │
│ - 可能建议归入 jupyterlab-contrib                         │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│ 第四步：正式并入（如被接受）                              │
│ - 遵循 Jupyter 官方并入指南                               │
│ - 配置 npm 包发布权限                                     │
│ - 代码迁移到 JupyterLab 组织                              │
└──────────────────────────────────────────────────────────┘
```

### 第一步：考虑 jupyterlab-contrib

并非所有扩展都需要成为 Jupyter 官方核心扩展。[jupyterlab-contrib](https://github.com/jupyterlab-contrib) 是社区维护的扩展集合，适合：

- 功能特定但用户面较窄的扩展
- 实验性或快速迭代的扩展
- 维护者希望保持更高独立性的扩展

jupyterlab-contrib 提供社区曝光度和协作支持，但不进入 Jupyter 官方治理体系。

### 第二步：提交正式提案

如果认为扩展应作为核心扩展，在 frontends-team-compass 仓库提 Issue，内容必须包含：

1. **扩展描述**：扩展做什么、解决什么问题
2. **现有代码链接**：GitHub 仓库地址
3. **逐项回应子项目准入标准**：参照 [Jupyter 官方新子项目标准](https://github.com/jupyter/governance/blob/master/newsubprojects.md#criteria-for-official-subprojects)的每一条说明情况

准入标准通常包括：
- 有明确的用途和用户群体
- 有活跃的维护者
- 代码质量符合 Jupyter 标准
- 遵循 Jupyter 许可证和 CoC
- 与 Jupyter 生态方向一致

### 第三步：社区评审

社区评审期**至少一周**，期间：

1. **代码审查**：一名核心维护者将审查现有代码质量
2. **社区参与度评估**：评估扩展维护者在 JupyterLab 社区的参与程度
   - 是否参与过 Issue 讨论
   - 是否审查过其他 PR
   - 是否参加过社区会议
3. **可能推荐 jupyterlab-contrib**：如果评审认为扩展更适合社区维护，会推荐放入 jupyterlab-contrib 而非核心组织

### 第四步：正式并入

如果 JupyterLab 维护者决定接受扩展，将执行以下操作：

#### 治理层面
- 遵循 Jupyter 官方[并入指南](https://github.com/jupyter/governance/blob/master/newsubprojects.md#incorporation)
- JupyterLab 维护者和相关领导层（如 BDFL）获得包发布权限

#### 权限配置（npm）
扩展维护者将获得对应 `@jupyterlab/extension` npm 包的管理员权限。配置流程：

1. 管理员登录 https://www.npmjs.com
2. 点击头像下拉菜单 → "Profile Settings"
3. 选择 jupyterlab 组织
4. 进入 Members
5. 点击 "Invite Members..."
6. 添加用户名或邮箱
7. 点击 "Invite"
8. 点击 "Continue"

#### 代码迁移
- 仓库迁移到 JupyterLab GitHub 组织下
- 遵循 Jupyter 项目的发布流程和版本管理

## 选择路径的决策参考

| 情况 | 建议路径 |
|------|---------|
| 扩展功能通用、用户面广、维护者愿意长期投入 | JupyterLab 核心组织 |
| 扩展功能有价值但较特定 | jupyterlab-contrib |
| 扩展尚在实验阶段 | 个人/独立组织，待成熟后再申请 |
| 维护者只想分享、不想承担官方维护责任 | jupyterlab-contrib 或发布到 PyPI/npm |

## 并入后的期望

并入 JupyterLab 组织后，维护者应：

- 继续积极维护扩展
- 参与 JupyterLab 社区讨论和会议
- 遵循 Jupyter 的发布流程和版本管理规范
- 接受社区的 PR 审查和反馈
- 与其他核心扩展保持兼容性

## 相关概念

- [Frontends Council 架构](01-team-council.md) — 决策者的构成和权限
- [决策制定流程](03-decision-making.md) — 提案评审中的共识机制
- [成员行为指南](04-member-guide.md) — 并入后的社区参与期望
