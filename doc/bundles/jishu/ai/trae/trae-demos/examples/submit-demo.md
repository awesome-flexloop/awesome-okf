---
type: Example
title: 提交 Demo 示例
description: 通过 Issue 模板向 trae-demos 提交 Demo 的完整流程示例，包含表单填写内容和审核要点
tags: [example, demos, submit, issue-form, trae-demos, trae]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/demos-source.md
    title: "Trae Demos 源码信源"
---

# 提交 Demo 示例

本示例演示如何通过 Issue 表单向 trae-demos 提交一个 Demo 项目。

## 场景假设

假设你用 TRAE 开发了一个 AI 写诗 Web 应用，仓库地址 `https://github.com/yourname/ai-poet`，有在线演示，想提交到 trae-demos 展示。

## 步骤一：自检 Must Have 标准

| 标准 | 自检结果 |
|------|---------|
| 使用 TRAE 作为核心技术 | ✅ 全程使用 TRAE 开发，TRAE 辅助了代码生成、调试和重构 |
| 可访问 | ✅ GitHub 仓库公开，有 Vercel 在线演示 |
| 代码质量良好 | ✅ 有完整 README，代码结构清晰 |
| 完成度较高 | ✅ 功能完整可用，非半成品 |

## 步骤二：选择合适的模板

1. 打开 trae-demos 仓库的 Issues 页面
2. 点击 "New Issue"
3. 根据你的语言选择：
   - 中文用户：选择 "提交 Demo / Submit Demo (中文)" 模板
   - 英文用户：选择 "Submit Demo" 模板

## 步骤三：填写 Issue 表单

以下是中文模板的填写示例：

**项目名称**：AI Poet - AI 诗词生成器

**项目简介（一句话）**：基于 TRAE 开发的 AI 诗词生成 Web 应用，支持多种风格和词牌。

**GitHub 仓库链接**：https://github.com/yourname/ai-poet

**在线演示链接**：https://ai-poet.vercel.app

**项目类型**（选择一个）：Web Applications

**技术栈**：React + TypeScript + Node.js + OpenAI API

**TRAE 使用场景描述**：
> 在开发过程中，TRAE 帮我完成了：
> 1. 初始化 React + TypeScript 项目脚手架
> 2. 生成了诗词生成的核心 prompt 工程代码
> 3. 调试了 API 调用和状态管理的多个 bug
> 4. 帮助编写了 CSS 样式和动画效果
> TRAE 是本项目的核心编程伙伴，约 60% 的代码由 TRAE 辅助生成。

**核心亮点（3-4 条）**：
> 1. 支持唐诗、宋词、现代诗等多种风格切换
> 2. 实时生成动画效果，展示"思考过程"
> 3. 支持收藏和分享生成的诗词
> 4. 响应式设计，手机端完美适配

**本地运行方式**：
> ```bash
> git clone https://github.com/yourname/ai-poet.git
> cd ai-poet
> npm install
> npm run dev
> ```

**截图/演示**：（粘贴 1-2 张项目截图）

**补充说明**：项目使用了 TRAE 的 Agent 模式进行结对编程。

## 步骤四：提交 Issue

确认所有字段填写完毕后，点击 "Submit new issue"。

## 步骤五：等待审核

1. **24 小时内**：维护者会给 Issue 添加标签或评论确认收到
2. **3-5 工作日**：维护者按权重标准审核
3. **可能的反馈**：
   - 需要补充信息（如更详细的 TRAE 使用说明、更多截图）
   - 需要调整描述（如亮点不够突出）
   - 直接通过

## 审核通过后

维护者会：
1. 在最新的 `period-N/` 目录下创建 `demo-N.md` 和 `demo-N.zh-CN.md`
2. 更新主 README 的 Past Issues 表格
3. 关闭 Issue 并通知你

你不需要自己创建 Markdown 文件或提交 PR。

## 提高通过率的建议

1. **突出 TRAE Usage**：这是 40% 权重项，详细描述 TRAE 在项目中的具体使用场景
2. **有在线演示**：可访问的 Demo 链接让审核者能直接体验
3. **清晰的亮点**：3-4 条核心亮点，每条说明"为什么这个项目值得展示"
4. **截图**：视觉效果能直观展示项目质量
5. **完整的运行说明**：确保审核者能本地运行验证

## 不被收录的常见原因

| 原因 | 说明 |
|------|------|
| TRAE 只是辅助 | 项目核心代码非 TRAE 辅助，仅偶尔用了一下 |
| 完成度不足 | 是原型/半成品，功能不完整 |
| 无法访问 | 仓库私有、链接失效、演示不可用 |
| 缺少文档 | 无 README 或 README 信息不全 |
| 重复类项目 | 已有非常类似的 Demo 收录 |

## 其他场景：want_demo 模板

如果你想看某种类型的 Demo 但自己没有项目，可以使用 "Want a Demo" 模板：

1. 描述你想看的 Demo 类型
2. 说明为什么这类 Demo 有价值
3. 其他社区成员可以点赞/评论表达兴趣
4. 开发者可以根据需求认领并制作

这是需求侧驱动的内容征集方式。

## 相关链接

- [TRAE Demos 定位与期数制组织](../concepts/00-introduction.md)
- [Demo Markdown 文档格式](../concepts/01-demo-format.md)
- [投稿流程与多场景 Issue 模板](../concepts/02-contribution-process.md)
- [TRAE Demos 仓库资源索引](../references/demos-source.md)
