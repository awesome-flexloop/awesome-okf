---
type: Index
title: TRAE 学习资源
description: trae-learning 是 TRAE 学习资源仓库，基于 VitePress 构建，提供自定义主题、指南内容、教程内容和部署方案，助力用户系统学习 TRAE。
tags: [trae-learning, trae, learning, tutorial, vitepress, documentation]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/learning-source.md
    title: "Trae Learning 源码信源"
---

# trae-learning 文档

trae-learning 是 TRAE Community 维护的 Vibecoding 进阶指南文档站，基于 VitePress 构建，定位为 AI 辅助开发的学习资源中心。项目仅依赖 VitePress 和 Vue 两个开发依赖，通过自定义主题实现了强品牌视觉风格。

## 核心概念

| 文档 | 说明 |
|------|------|
| [Trae Learning 学习站简介](/concepts/00-introduction.md) | VitePress 文档站定位、Vibecoding 理念（心流/意图/反馈）、双语支持 |
| [VitePress 站点架构](/concepts/01-vitepress-setup.md) | .vitepress/config.js 配置、导航/侧边栏、首页结构、内容分布 |
| [自定义主题开发](/concepts/02-custom-theme.md) | Canvas 3D 地球仪组件 VibeHero、玻璃拟态卡片 HomeFeatures、CSS 定制、动画效果 |
| [Guide 基础教程](/concepts/03-guide-content.md) | 4 篇核心理念：Vibecoding 定义、心流效率、Prompt 工程、最佳实践 |
| [Tutorials 实战教程](/concepts/04-tutorial-content.md) | 6 篇实战案例按难度三级分布，从看懂到提交的 Vibecoding 学习路径 |
| [GitHub Pages 部署](/concepts/05-deploy-pages.md) | Actions 工作流（build+deploy 双 job）、自动部署配置、双语 Issue 模板 |

## 示例

| 文档 | 说明 |
|------|------|
| [添加新教程文档示例](/examples/add-tutorial.md) | 创建教程 Markdown 文件、更新侧边栏配置、更新索引的步骤 |
| [自定义主题样式示例](/examples/customize-theme.md) | 修改品牌色、添加全局组件、覆盖默认样式、CSS 动画 |
| [本地预览与构建示例](/examples/local-preview.md) | npm ci/docs:dev/docs:build/docs:preview 命令使用、自动部署流程 |

## 参考

| 文档 | 说明 |
|------|------|
| [文档站源码索引](/references/learning-source.md) | 项目信息、npm scripts、完整目录结构、VitePress 配置要点 |

```{toctree}
:hidden:
:maxdepth: 7

concepts/00-introduction
concepts/01-vitepress-setup
concepts/02-custom-theme
concepts/03-guide-content
concepts/04-tutorial-content
concepts/05-deploy-pages
examples/add-tutorial
examples/customize-theme
examples/local-preview
references/learning-source
spec/facts
spec/insights
```
