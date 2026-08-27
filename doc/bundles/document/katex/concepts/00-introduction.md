---
type: Concept
title: KaTeX 简介
description: KaTeX 是一个快速的 Web 数学排版库，将 LaTeX 数学表达式渲染为 HTML+MathML，支持服务端渲染和浏览器端渲染。
tags: [katex, introduction, math, latex]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T21:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T21:30:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-home
    resource: /references/katex-website.md#web-home
    title: KaTeX 官网首页
  - id: web-users
    resource: /references/katex-website.md#web-users
    title: KaTeX 官网 Users 页面
  - id: web-versions
    resource: /references/katex-website.md#web-versions
    title: KaTeX 官网 Versions 页面
---

## 什么是 KaTeX

KaTeX（/ˈkeɪtɛk/，发音类似 "Kay-Tek"）是一个用于 Web 的数学公式排版库。它将 LaTeX 语法书写的数学表达式解析并渲染为浏览器可显示的 HTML 和 MathML 标记，实现接近印刷级质量的数学公式展示。

KaTeX 由 Emily Eisenberg 和 Sophie Alpert 创建，官网副标题为 "The fastest math typesetting library for the web."

### 四大核心特点

KaTeX 官网首页明确列出四个特点：

- **Fast（快速）**：同步渲染模型，不需要布局回流（reflow）即可完成公式排版，页面无需等待数学排版完成
- **Print quality（印刷品质）**：基于 Donald Knuth 的 TeX 排版算法，输出结果接近 LaTeX 原生印刷质量
- **Self-contained（自包含）**：运行时无外部依赖，可与网站资源一起打包；浏览器端零运行时依赖
- **Server side rendering（服务端渲染）**：同一套代码在浏览器和 Node.js 环境中产生相同输出，可通过 Node.js 预渲染为纯 HTML

## 版本与许可

- **本 bundle 基准版本**：**0.18.4**（以源码 `package.json` 为权威基准）
- **许可证**：**MIT License**（可自由商用）
- **包管理器**：项目源码使用 pnpm 管理依赖，发布到 npm 供 npm/yarn/pnpm/Deno 等所有包管理器使用
- **运行时依赖**：仅 `commander`（供 CLI 使用），浏览器端零依赖
- **仓库**：[https://github.com/KaTeX/KaTeX](https://github.com/KaTeX/KaTeX)
- **官网**：[https://katex.org](https://katex.org)

> **版本标注说明**：KaTeX 官网 Versions 页面标注的"当前稳定版"为 0.16.47，而 Node/Browser/Font 等文档页的 CDN 链接引用 `katex@0.18.4`，Auto-render 页面 CDN 引用 `katex@0.18.1`。官网不同页面的版本标注并非原子更新，Versions 页面更新滞后。本 bundle 统一以源码 v0.18.4 为基准，版本差异详见 [事实清单修正-8](../spec/facts.md#修正-8官网版本号标注不一致)。

## KaTeX 能做什么

KaTeX 支持大部分 LaTeX 数学模式命令，包括：

- 基础数学运算：分数、上下标、根号、求和、积分
- 矩阵与表格：`matrix`、`pmatrix`、`array` 等环境
- 运算符：希腊字母、二元运算符、关系运算符、箭头
- 排版控制：字体切换、颜色、间距、字号
- 文本嵌入：`\text{}` 命令在数学模式中插入普通文本
- 自定义宏：通过配置或扩展 API 添加新命令
- HTML+MathML 双输出：默认同时生成视觉 HTML 与语义 MathML，兼顾视觉效果与无障碍访问

KaTeX **不支持** LaTeX 的全部功能（如 TikZ 绘图、复杂页面布局），它专注于数学模式的排版。

## 谁在使用 KaTeX

KaTeX 官网 Users 页面列出了众多采用 KaTeX 的知名项目，包括 Khan Academy、Dropbox Paper、GitLab、Gatsby、Gitter、Gradescope、Messenger、Observable、Quill、Rocket.Chat、Slab、Slides、StackEdit、TiddlyWiki 等，以及 BearBei 貝貝、Editor.md、namu.wiki、Techambition 等中文/东亚相关项目。

完整生态列表（含第三方库索引）见 [生态与版本](23-ecosystem-and-versions.md)。

## 在项目中的位置

KaTeX 的源码结构清晰地划分为几个层次：

1. **词法层（Lexer/Token）**：将输入字符串切分为 Token 流
2. **宏展开层（MacroExpander）**：展开用户定义的和内置的宏
3. **解析层（Parser）**：将 Token 流解析为抽象语法树（ParseNode 树）
4. **构建层（buildHTML/buildMathML）**：将解析树转换为虚拟 DOM 树
5. **输出层**：虚拟 DOM 序列化为 HTML 字符串或真实 DOM 节点

理解这个分层架构是掌握 KaTeX 的关键。详见 [架构总览](02-architecture-overview.md)。

## 相关概念

- [快速开始](01-getting-started.md)
- [安装与运行时](15-installation-and-runtime.md)
- [架构总览](02-architecture-overview.md)
- [配置系统](10-settings-options.md)
- [命令行接口](16-command-line.md)
