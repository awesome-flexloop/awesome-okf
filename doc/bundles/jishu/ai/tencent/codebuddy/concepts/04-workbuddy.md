---
type: Concept
title: "WorkBuddy 在线助手"
description: "WorkBuddy 是腾讯龙虾团队推出的在线 AI 助手 Web 应用，覆盖日常办公与代码开发两大场景，采用对话式交互、产物面板与来源追踪，当前处于公测阶段。"
tags: [workbuddy, web-app, ai-assistant, office, artifacts, conversation]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-02-23
sources:
  - id: workbuddy-official
    resource: /references/workbuddy.md
    title: WorkBuddy 在线 AI 助手
---

# WorkBuddy 在线助手

WorkBuddy 是腾讯龙虾团队推出的在线 AI 助手 Web 应用，标语为 "WorkBuddy, 我帮你"（F-053）。它覆盖日常办公与代码开发两大场景，以对话式交互提供幻灯片、文档、数据分析、代码开发等能力，当前处于公测阶段（F-060）。

## 产品定位

WorkBuddy 是 CodeBuddy 产品矩阵中面向通用办公与轻量开发场景的在线入口。与 IDE/CLI 聚焦专业编程不同，WorkBuddy 以浏览器为载体，降低使用门槛，服务于更广泛的办公人群与开发者。其顶部导航直接链接 IDE、插件、CLI、文档、定价、博客、API 文档与活动（F-059），表明它是 CodeBuddy 生态体系的组成部分。

## 两大场景

### 日常办公场景

WorkBuddy 日常办公场景覆盖十类能力（F-054）：

| 能力 | 说明 |
|------|------|
| 幻灯片 | AI 生成演示文稿 |
| 视频 | 视频内容创作 |
| 深度研究 | 深度信息检索与分析 |
| 文档 | 文档撰写与处理 |
| 数据分析 | 数据处理与解读 |
| 可视化 | 图表与数据可视化 |
| 金融 | 金融相关分析 |
| 产品 | 产品设计相关工作 |
| 设计 | 设计相关工作 |
| 邮件 | 邮件撰写与处理 |

### 代码开发场景

WorkBuddy 代码开发场景覆盖六类能力（F-055）：

| 能力 | 说明 |
|------|------|
| 日常开发 | 通用编程辅助 |
| 网站 | 网站开发 |
| Agent 应用 | AI Agent 应用构建 |
| Skill 开发 | 技能包开发 |
| CI/CD | 持续集成与部署 |
| 文档 | 技术文档撰写 |

其中 Skill 开发与 CodeBuddy 的 Skills 高级能力（F-018）相呼应，CI/CD 能力与 NPC 的全流程交付（F-045）形成生态协同。

## 交互方式

WorkBuddy 采用对话式交互（F-056），提供两个核心交互机制：

- **`@` 引用**：在对话中引用文件，将文件内容作为上下文
- **`/` 调用**：调用技能（Skills）与指令（Commands）

这种交互方式与 CodeBuddy IDE/CLI 中的 `@workspace` 引用和 slash 命令一脉相承。

## 右侧面板

对话界面右侧面板提供三部分内容（F-057）：

| 区域 | 功能 |
|------|------|
| 概览 | 任务整体情况摘要 |
| 产物（Artifacts） | 生成的交付物，如文档、代码、幻灯片 |
| 引用来源追踪 | 信息来源溯源，保证可审计性 |

产物（Artifacts）面板使用户可直接查看和下载 AI 生成的交付物，引用来源追踪则保证信息可追溯。

## 其他特性

- **代码仓库关联**：支持关联代码仓库（F-058），使开发场景可直接访问仓库上下文。
- **全屏模式**：支持全屏专注模式（F-058）。

## 与 CodeBuddy 生态的关系

WorkBuddy 在 CodeBuddy 产品矩阵中扮演"在线通用入口"角色：

1. **能力承接**：代码开发场景承接 CodeBuddy IDE/CLI 的编程能力，以在线方式提供。
2. **导航入口**：顶部导航直接链接 IDE、插件、CLI（F-059），引导用户下载专业工具。
3. **Skill 生态**：Skill 开发场景与 CodeBuddy Skills 体系（F-018, F-049）共享技能包理念。
4. **公测阶段**：当前处于公测（F-060），能力与定价可能随正式发布调整。

## 适用人群

- 需要 AI 辅助办公（文档、幻灯片、数据分析）的非技术用户
- 需要轻量在线开发环境的开发者
- 希望在浏览器中快速体验 CodeBuddy 能力的新用户
- 需要 Agent 应用与 Skill 开发的进阶用户

## 相关概念

- [产品矩阵总览](00-product-matrix.md) — WorkBuddy 在矩阵中的定位
- [CodeBuddy IDE](01-ide.md) — 顶部导航关联的专业开发工具
- [CLI](02-cli.md) — 顶部导航关联的终端工具
- [NPC 云端 AI 员工](03-npc.md) — CI/CD 与 Skill 生态的协同
- [IDE 工作流示例](../examples/ide-workflow.md) — 专业开发工作流参考
