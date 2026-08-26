---
type: Changelog
title: 3Blue1Brown.com 知识包变更日志
description: 3Blue1Brown.com OKF知识包的生成与变更记录
tags: [changelog, 3blue1brown, react, react-router, ssg]
generated:
  at: 2026-08-26
  by: source-code-to-okf-wiki skill
verified:
  at: 2026-08-26
  by: grep-api-verification
status: stable
stale_after: 2027-08-26
sources:
  - /spec/facts.md
---

# 更新日志

## 2026-08-26

- 初始化 3Blue1Brown.com OKF 知识包，基于 3Blue1Brown.com 官方源码。
- R阶段：逐模块阅读源码核心代码，提取 130 条编号事实 F-001~F-130。
- I阶段：提炼 5 个架构洞察（React Router框架模式反常识选型、Tailwind v4 CSS-first零配置、MDX双阶段内容加载、Custom Elements视频播放器、MathJax 4双阶段数学渲染）。
- E阶段：生成 11 个内容文档：
  - 2 个信源登记（references/）：tech-stack、component-index；
  - 7 个概念文档（concepts/）：00 官网技术栈总览、01 项目结构与目录组织、02 路由与 SSG 预渲染、03 MDX内容系统与数学渲染、04 核心组件与状态管理、05 Tailwind v4 CSS-first 样式系统、06 构建系统包管理与静态部署；
  - 2 个示例（examples/）：minimal-mdx-page、tailwind-theme-setup。
- 生成各级 index.md（concepts/examples/references 子目录无 frontmatter，根 index.md 含 `okf_version: "0.2"`）。
- V阶段：Grep API 验证已完成，标记为 stable。
