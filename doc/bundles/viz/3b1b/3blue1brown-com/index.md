---
type: bundle
title: 3Blue1Brown.com 官网源码解析
okf_version: "0.2"
description: 3Blue1Brown官方网站（3Blue1Brown.com）前端架构源码深度解析，涵盖React Router v7框架模式SSG、Tailwind v4 CSS-first配置、MDX数学内容双阶段渲染（remark-math+MathJax4）、Custom Elements视频播放器、Jotai原子状态管理等现代前端最佳实践
tags: [3blue1brown, react, react-router, tailwindcss, mdx, mathjax, ssg, vite, bun, jotai, web-components, 前端架构]
generated:
  at: 2026-08-26
  by: source-code-to-okf-wiki skill
verified:
  at: 2026-08-26
  by: grep-api-verification
status: stable
stale_after: 2027-08-26
sources:
  - /references/tech-stack.md
  - /spec/facts.md
---

# 3Blue1Brown.com 知识库

3Blue1Brown.com是3Blue1Brown的官方视频网站，采用2024-2025年前沿技术栈（Bun+React19+React Router v7框架模式+Vite+Tailwind v4+MDX+MathJax 4），是学习现代React SSG网站架构的优秀范例。本知识包基于源码逐模块阅读与事实提取（130条源码事实 F-001~F-130），经 seven-concepts 方法论 R→I→E 三阶段流程生成，涵盖框架选型、项目结构、路由系统、内容渲染、组件状态、样式系统、构建部署全链路。

## 概念文档（concepts/）

* [00 官网技术栈总览](concepts/00-website-overview.md) — 核心技术选型理由（为什么选 React Router v7 而非 Next.js）、架构特色概览与本地开发快速上手。
* [01 项目结构与目录组织](concepts/01-project-structure.md) — 完整目录树解析、app/ 目录 React Router 约定、按领域共置原则、关键配置文件职责。
* [02 路由与 SSG 预渲染](concepts/02-routing-and-pages.md) — React Router v7 框架模式路由系统、ssr:false 纯预渲染配置、prerender 动态路由收集。
* [03 MDX内容系统与数学渲染](concepts/03-mdx-content-system.md) — Vite 插件链配置、frontmatter 元数据系统、MathJax 4 双阶段数学渲染。
* [04 核心组件与状态管理](concepts/04-components-and-state.md) — Web Components 视频播放器、Jotai 原子状态管理、暗色模式 FOUC 预防。
* [05 Tailwind v4 CSS-first 样式系统](concepts/05-styling-with-tailwind4.md) — @theme 设计令牌、@custom-variant 自定义状态变体、oklch 颜色系统。
* [06 构建系统、包管理与静态部署](concepts/06-build-and-deploy.md) — Bun 包管理器选型、Vite 插件链架构、静态托管部署方案。

## 实战示例（examples/）

* [创建带数学公式的 MDX 页面](examples/minimal-mdx-page.md) — 完整演示如何创建包含 LaTeX 数学公式的 MDX 课程页面。
* [Tailwind v4 主题与自定义变体配置](examples/tailwind-theme-setup.md) — 从零配置 Tailwind v4 CSS-first 主题系统，含 v3/v4 对比。

## 信源登记簿（references/）

* [3Blue1Brown.com 完整技术栈清单](references/tech-stack.md) — 所有核心 npm 依赖完整清单，区分 dependencies/devDependencies。
* [3Blue1Brown.com 核心组件索引](references/component-index.md) — app/ 目录下核心组件路径索引，按功能分组标注核心功能。

## 信任与生命周期说明

* **status 判定依据**：当前 11 个内容文档（7 个概念 + 2 个示例 + 2 个信源登记）均基于 130 条源码事实 F-001~F-130 生成，经 seven-concepts 方法论 R→I→E 三阶段流程，V 阶段 Grep API 验证已完成，标记为 `stable`。
* **stale_after 解释**：统一设置为 `2027-08-26`。3Blue1Brown.com 作为内容站点，核心架构（React Router SSG、Tailwind v4 CSS-first、MDX 双阶段渲染、Custom Elements 视频播放器）在 2025 年重构后保持稳定；该日期作为针对未来大版本重构的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段 Grep 对抗验证事件（类名/方法签名/字段/配置项逐一比对源码），两者分离、可追溯。

本知识包共收录 11 个内容文档（7 个概念 + 2 个示例 + 2 个信源登记），另含 3 个子目录 index.md、2 个 spec 文档（facts/insights）与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
