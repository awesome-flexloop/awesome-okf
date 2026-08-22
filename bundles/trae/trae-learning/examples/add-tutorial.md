---
type: Example
title: 添加新教程文档示例
description: 创建新教程 Markdown 文件、更新 VitePress 侧边栏配置和首页索引的完整步骤示例。
tags: [trae-learning, vitepress, example, tutorial, content-creation, sidebar]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/learning-source.md
    title: "Trae Learning 源码信源"
---

# 添加新教程文档示例

本示例演示如何为 TRAE Learning 添加一篇新的实战教程。

## 步骤 1：确定教程位置和难度

首先确定教程放在哪个目录：

- **Guide（指南）**：`guide/` 目录——理念性内容（如新增一篇 Prompt 技巧文档）
- **Tutorials（实战教程）**：`tutorials/` 目录——动手实践内容

Tutorials 需要确定难度级别（⭐ 入门 / ⭐⭐ 进阶 / ⭐⭐⭐ / ⭐⭐⭐⭐ 高级）。

## 步骤 2：创建 Markdown 文件

在对应目录下创建新的 `.md` 文件，例如 `tutorials/docker-basics.md`。

遵循 Vibecoding 教程四步范式：

```markdown
---
title: Docker 基础入门
---

# Docker 基础入门

## 项目描述

（用自然语言描述要构建的项目，例如：构建一个 Docker 化的 Node.js Web 应用）

## 步骤 1：生成项目骨架

（描述需求给 AI，让 AI 生成 Dockerfile 和 docker-compose.yml）

## 步骤 2：理解关键代码

（逐段解释 AI 生成的关键代码，帮助读者"看懂"）

## 步骤 3：运行验证

（指导填入必要配置、运行容器、验证结果）

## 步骤 4：迭代改进

（提出改进方向，让读者自己或借助 AI 扩展功能）
```

## 步骤 3：更新 VitePress 配置

编辑 `.vitepress/config.js`，在对应的侧边栏中添加新教程条目。

如果是 Tutorials 教程，在 `tutorials/` 的 sidebar 配置中添加：

```js
{
  text: 'Docker 基础入门',
  link: '/tutorials/docker-basics'
}
```

如果是 Guide 文档，在 `guide/` 的 sidebar 分组"核心理念"下添加。

## 步骤 4：更新教程索引

编辑 `tutorials/index.md`，在对应的难度级别下添加新教程的链接和简介，标注难度星级。

## 步骤 5：本地预览验证

```bash
npm run docs:dev
```

打开本地开发服务器（通常是 http://localhost:5173/trae-learning/），验证：

- 新教程在侧边栏中正确显示
- 页面内容渲染正常
- 内部链接可跳转
- 代码块高亮正常

## 步骤 6：构建验证

```bash
npm run docs:build
npm run docs:preview
```

确认构建无错误，预览页面正常。

## 写作建议

- **理念先行**：教程不仅是教技术，更是教"如何用 AI 学技术"
- **看懂再提交**：每个代码块后应有解释，帮助读者理解 AI 生成的代码
- **小步迭代**：步骤拆分要细，每步可独立验证
- **提供完整代码**：关键步骤给出可运行的完整代码参考
- **难度标注准确**：入门教程不假设框架知识，高级教程可以更开放

## 相关链接

- [Tutorials 实战教程](/concepts/04-tutorial-content.md)
- [Guide 基础教程](/concepts/03-guide-content.md)
- [VitePress 站点架构](/concepts/01-vitepress-setup.md)
- [本地预览与构建示例](/examples/local-preview.md)
