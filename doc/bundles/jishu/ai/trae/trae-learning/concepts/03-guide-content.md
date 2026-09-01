---
type: Concept
title: Guide 基础教程
description: Guide 部分包含 Vibecoding 定义、心流效率、Prompt 工程和最佳实践 4 篇核心理念文档，构建 AI 辅助开发的认知框架。
tags: [trae-learning, trae, vibecoding, guide, prompt-engineering, best-practices]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/learning-source.md
    title: "Trae Learning 源码信源"
---

# Guide 基础教程

Guide 部分包含 4 篇核心理念文档，构成 Vibecoding 的认知框架。学习路径遵循"理念先行"原则——先建立正确的 AI 辅助开发心智模型，再进入实战。

## 内容概览

| 文档 | 核心主题 | 关键内容 |
|------|---------|---------|
| what-is-vibecoding.md | Vibecoding 定义 | 三个核心特征 |
| flow-and-efficiency.md | 心流与效率 | 打断因素与习惯建议 |
| prompt-engineering.md | Prompt 工程 | 技巧与具体示例 |
| best-practices.md | 最佳实践 | 五条实践原则 |

## 1. 什么是 Vibecoding

`what-is-vibecoding.md` 定义了 Vibecoding 的三个核心特征：

- **心流驱动（Flow State）**：AI 处理语法查询、样板代码等低价值工作，让开发者保持创造心流
- **意图传达（Intentionality）**：编程核心能力从"逐行写代码"转向"准确描述意图+审查 AI 输出"
- **即时反馈（Instant Loops）**：快速迭代——描述需求→AI 生成→运行验证→反馈改进

这是整个学习站的哲学基础，强调 AI 时代编程范式的转变。

## 2. 心流与效率

`flow-and-efficiency.md` 分析三类打断心流的因素：

1. **语法和 API 查询**：频繁查文档打断思路
2. **样板代码**：重复编写 CRUD、配置等机械代码
3. **不确定性焦虑**：担心代码有问题、不确定最佳方案

给出四个习惯建议：

- **拆小任务**：将大任务分解为 AI 可处理的小单元
- **Prompt 先于代码**：先用自然语言描述清楚，再让 AI 生成代码
- **不要盲接**：审查 AI 输出，不要不加理解直接使用
- **及时提交**：小步提交，保持代码可回退

## 3. Prompt 工程指南

`prompt-engineering.md` 提供一个具体的 Prompt 示例（Next.js + NextAuth 邮箱密码登录，含表单校验、加载状态、跳转逻辑），并列出四个技巧：

1. **给上下文不给废话**：提供必要的技术栈、约束条件，不要堆砌无关信息
2. **说清约束条件**：明确框架、库版本、编码规范、功能边界
3. **分步处理复杂任务**：复杂需求拆解为多个步骤，逐步与 AI 交互
4. **不满意就直说**：直接告诉 AI 哪里不对、怎么改，不要重新开始

## 4. 最佳实践

`best-practices.md` 提出五条核心原则：

1. **看懂再提交**：理解 AI 生成的代码后再提交，不要盲接
2. **安全问题不能交给 AI 把关**：SQL 注入、密钥管理、输入校验等安全问题必须人工审查
3. **测试不能省**：AI 生成的代码同样需要测试覆盖
4. **提交要小要频繁**：小颗粒度提交便于审查和回退
5. **对 AI 保持合理期望**：了解 AI 擅长和不擅长的领域

文档明确列出 AI 的能力边界：

| AI 擅长 | AI 不那么可靠 |
|---------|-------------|
| 样板代码生成 | 项目特有业务上下文 |
| 设计模式应用 | 最新/冷门知识 |
| 代码解释 | 跨文件复杂重构的一致性 |
| 优化建议 | 未明确描述的隐式需求 |

## 学习建议

Guide 部分建议按顺序阅读（what-is-vibecoding → flow-and-efficiency → prompt-engineering → best-practices），建立完整的 Vibecoding 心智模型后，再进入 Tutorials 实战。这体现了"先建立认知框架，再动手实践"的学习路径设计。

## 相关链接

- [Trae Learning 学习站简介](00-introduction.md)
- [Tutorials 实战教程](04-tutorial-content.md)
- [VitePress 站点架构](01-vitepress-setup.md)
- [添加新教程文档示例](../examples/add-tutorial.md)
