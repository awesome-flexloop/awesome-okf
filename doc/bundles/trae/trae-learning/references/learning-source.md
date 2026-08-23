---
type: Reference
title: 文档站源码索引
description: trae-learning 仓库的信源登记簿，包含 VitePress 配置要点、npm scripts、完整目录结构、主题组件索引和部署配置信息。
tags: [trae-learning, vitepress, vibecoding, documentation, source-index, reference]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/learning-source.md
    title: "Trae Learning 源码信源"
---

# 文档站源码索引

本文档索引 trae-learning 项目的源码结构和关键文件。

## 项目基本信息

| 属性 | 值 |
|------|---|
| npm 包名 | `trae-learning-projects` |
| 版本 | `1.0.0` |
| 描述 | 学习园区 |
| License | ISC |
| 仓库 | <https://github.com/trae-community/trae-learning-projects> |
| 开发依赖 | `vitepress: ^1.6.4`、`vue: ^3.5.27`（无运行时依赖） |
| 模块类型 | `module`（ES Module） |

## npm scripts

| 命令 | 用途 |
|------|------|
| `npm run docs:dev` | 启动 VitePress 开发服务器（本地预览） |
| `npm run docs:build` | 构建静态站点到 `.vitepress/dist` |
| `npm run docs:preview` | 预览构建后的站点 |

## 目录结构

```
trae-learning/
├── .vitepress/
│   ├── config.js              # VitePress 站点配置
│   └── theme/
│       ├── index.js           # 自定义主题入口（注册组件）
│       ├── custom.css         # 全局样式覆盖与自定义
│       └── components/
│           ├── VibeHero.vue   # 首页 Canvas 3D 地球仪组件
│           └── HomeFeatures.vue # 首页玻璃拟态特性卡片组件
├── guide/                     # 基础指南（4 篇）
│   ├── what-is-vibecoding.md  # Vibecoding 核心理念
│   ├── flow-and-efficiency.md # 心流与效率
│   ├── prompt-engineering.md  # Prompt 工程指南
│   └── best-practices.md      # 最佳实践
├── tutorials/                 # 实战教程（7 篇）
│   ├── index.md               # 教程索引与难度分级
│   ├── getting-started.md     # ⭐ 入门：天气查询页面
│   ├── rest-api.md            # ⭐⭐ REST API
│   ├── react-components.md    # ⭐⭐ React 组件
│   ├── automated-testing.md   # ⭐⭐⭐ 自动化测试
│   ├── system-design.md       # ⭐⭐⭐⭐ 系统设计
│   └── performance-optimization.md # ⭐⭐⭐⭐ 性能优化
├── assets/image/
│   └── Learning.gif           # Banner 动图
├── .github/
│   ├── workflows/deploy.yml   # GitHub Pages 自动部署
│   └── ISSUE_TEMPLATE/        # 双语 Issue 模板（7 个 YAML 文件）
├── index.md                   # 首页（layout: home）
├── package.json
├── README.md / README.zh-CN.md
├── CONTRIBUTING.md / CONTRIBUTING.zh-CN.md
└── LICENSE
```

## VitePress 配置要点

- `base: '/trae-learning/'`：GitHub Pages 子路径部署
- `appearance: 'force-dark'`：强制暗色模式
- `cleanUrls: true`：启用干净 URL
- `ignoreDeadLinks: true`：忽略死链接检查
- 品牌色：`#0FDC78`（绿色）
- 字体：Inter（正文）、JetBrains Mono（代码）

## 相关链接

- [VitePress 站点架构](/concepts/01-vitepress-setup.md)
- [自定义主题开发](/concepts/02-custom-theme.md)
- [本地预览与构建示例](/examples/local-preview.md)
