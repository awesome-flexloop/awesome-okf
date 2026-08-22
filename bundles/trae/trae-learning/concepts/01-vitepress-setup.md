---
type: Concept
title: VitePress 站点架构
description: trae-learning 基于 VitePress 构建，仅依赖 VitePress 和 Vue 两个开发依赖，通过 .vitepress/config.js 配置导航、侧边栏和首页结构。
tags: [trae-learning, trae, vitepress, setup, configuration, navigation]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/learning-source.md
    title: "Trae Learning 源码信源"
---

# VitePress 站点架构

本文档介绍 TRAE Learning 基于 VitePress 的站点配置架构，包括配置文件结构、导航/侧边栏设置和主题扩展机制。

## 依赖与命令

项目仅依赖 `vitepress: ^1.6.4` 和 `vue: ^3.5.27` 两个开发依赖，无运行时依赖。

npm scripts 定义了三条核心命令：

| 命令 | 用途 |
|------|------|
| `npm run docs:dev` | 启动 VitePress 开发服务器（本地预览） |
| `npm run docs:build` | 构建静态站点到 `.vitepress/dist` |
| `npm run docs:preview` | 预览构建后的生产版本 |

## 配置文件：.vitepress/config.js

VitePress 站点核心配置位于 `.vitepress/config.js`，关键配置项如下：

### 站点基础信息

```js
export default {
  base: '/trae-learning/',        // GitHub Pages 子路径
  title: 'TRAE Learning',         // 站点标题
  description: 'Vibecoding 进阶指南', // 站点描述
  appearance: 'force-dark',       // 强制暗色模式
  cleanUrls: true,                // 干净 URL（无 .html 后缀）
  ignoreDeadLinks: true,          // 忽略死链接检查
  logo: 'https://avatars.githubusercontent.com/u/257951088' // GitHub 头像作为 logo
}
```

### 顶部导航栏

导航栏包含两个核心入口和社交链接：

```js
nav: [
  { text: '指南', link: '/guide/what-is-vibecoding' },
  { text: '社区教程', link: '/tutorials/' }
],
socialLinks: [
  { icon: 'github', link: 'https://github.com/trae-community/trae-learning-projects' }
]
```

### 侧边栏配置

侧边栏按路径分两组：

**Guide 侧边栏**（`/guide/` 路径下）：

| 分组 | 条目 |
|------|------|
| 核心理念 | 什么是 Vibecoding、心流与效率、Prompt 工程指南、最佳实践 |

**Tutorials 侧边栏**（`/tutorials/` 路径下）：

| 分组 | 条目 |
|------|------|
| 实战教程 | 入门项目、REST API、React 组件、自动化测试、系统设计、性能优化 |

## 站点首页

首页 `index.md` 使用 `layout: home` frontmatter，内容极简——仅包含两个自定义 Vue 组件：

```markdown
---
layout: home
---

<VibeHero />
<HomeFeatures />
```

所有视觉效果（3D 地球仪、特性卡片、光条动画等）都封装在这两个组件中。

## 目录与内容分布

```
trae-learning/
├── .vitepress/
│   ├── config.js           # 站点配置
│   └── theme/              # 自定义主题
├── guide/                  # 4 篇核心理念文档
│   ├── what-is-vibecoding.md
│   ├── flow-and-efficiency.md
│   ├── prompt-engineering.md
│   └── best-practices.md
├── tutorials/              # 7 篇实战教程（含 index.md）
│   ├── index.md
│   ├── getting-started.md
│   ├── rest-api.md
│   ├── react-components.md
│   ├── automated-testing.md
│   ├── system-design.md
│   └── performance-optimization.md
├── assets/image/           # 图片资源
│   └── Learning.gif
└── index.md                # 首页
```

## 主题扩展机制

自定义主题通过 `.vitepress/theme/index.js` 实现，继承 VitePress DefaultTheme 并注册全局组件。详见[自定义主题开发](/concepts/02-custom-theme.md)。

## 相关链接

- [Trae Learning 学习站简介](/concepts/00-introduction.md)
- [自定义主题开发](/concepts/02-custom-theme.md)
- [Guide 基础教程](/concepts/03-guide-content.md)
- [GitHub Pages 部署](/concepts/05-deploy-pages.md)
- [本地预览与构建示例](/examples/local-preview.md)
- [文档站源码索引](/references/learning-source.md)
