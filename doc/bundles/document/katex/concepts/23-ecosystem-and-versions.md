---
type: Concept
title: 生态与版本
description: KaTeX 的用户生态（知名采用项目）、版本说明（官网版本标注差异与源码基准）、官方扩展入口，以及按平台/语言分类的第三方库索引（React/Vue/Angular/Android/iOS/Rust/Ruby/小程序等）。
tags: [katex, ecosystem, versions, third-party-libraries, integrations, users]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T22:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23T22:30:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/katex-source.md
    title: KaTeX 源码信源
  - id: web-users
    resource: /references/katex-website.md#web-users
    title: KaTeX 官网 Users 页面
  - id: web-versions
    resource: /references/katex-website.md#web-versions
    title: KaTeX 官网 Versions 页面
  - id: web-libs
    resource: /references/katex-website.md#web-libs
    title: KaTeX 官网 Extensions & Libraries 页面
  - id: facts
    resource: /spec/facts.md
    title: KaTeX 事实清单
---

## 概述

本文档汇总 KaTeX 的生态信息：谁在使用 KaTeX、版本号说明、官方扩展入口，以及官网 [Extensions & Libraries](https://katex.org/docs/libs) 页面列出的第三方集成库[^web-libs]。官方 contrib 扩展的详细说明见 [贡献扩展模块](/concepts/14-contrib-extensions.md)。

> 生态信息随时间变化较快，本文档基于 2026-08-23 官网采集，最新列表以 [官网 Users 页面](https://katex.org/users) 和 [Libraries 页面](https://katex.org/docs/libs) 为准。

## 谁在使用 KaTeX

KaTeX 官网 [Users 页面](https://katex.org/users) 列出多个使用 KaTeX 的知名项目[^web-users]：

### 国际项目

- **Khan Academy** — 在线教育平台
- **Dropbox Paper** — 协作文档
- **GitLab** — DevOps 平台（Markdown 数学渲染）
- **Gatsby** — React 静态站点生成器
- **Gitter** — 开发者聊天社区
- **Gradescope** — 在线评分平台
- **Messenger** — Meta 即时通讯
- **Observable** — 交互式笔记本
- **Quill** — 富文本编辑器
- **Rocket.Chat** — 开源团队聊天
- **Slab** — 团队知识库
- **Slides** — 演示文稿平台
- **StackEdit** — 在线 Markdown 编辑器
- **TiddlyWiki** — 非线性笔记本

### 中文/东亚相关项目

- **BearBei 貝貝**
- **Editor.md** — 开源 Markdown 编辑器
- **namu.wiki** — 韩文 Wiki
- **Techambition** — 项目管理工具
- **zzllrr Mather**

每个项目条目在官网包含项目图标和官网链接[^web-users]。

## 版本说明

### 版本标注差异

KaTeX 官网存在版本标注不一致的情况[^web-versions]：

| 来源 | 标注版本 |
|------|---------|
| 官网 Versions 页面（"Current version (Stable)"） | 0.16.47 |
| Node/Browser/Font 页面 CDN 链接 | 0.18.4 |
| Auto-render 页面 CDN 链接 | 0.18.1 |
| 源码 package.json（本 bundle 基准） | **0.18.4** |

官网 Versions 页面更新滞后于文档页面中的 CDN 版本号。本 bundle 以源码 `package.json` 的 **v0.18.4** 为权威基准[^facts]。版本差异的详细记录见 [事实清单修正-8](/spec/facts.md#修正-8官网版本号标注不一致)。

### 版本历史

- 历史版本 Release Notes 见 [GitHub Releases](https://github.com/KaTeX/KaTeX/releases)[^web-versions]
- 各版本文档可通过 Versions 页面的 Documentation 链接访问（部分历史版本托管在 netlify.app）
- 版本迁移指南见 [版本迁移](/concepts/22-migration.md)

## 官方扩展

KaTeX 自带 5 个 contrib 扩展（在 `contrib/` 目录）[^web-libs]：

| 扩展 | 用途 |
|------|------|
| [auto-render](/concepts/13-auto-render.md) | 自动扫描 DOM 文本中的数学分隔符并渲染 |
| copy-tex | 选择复制 KaTeX 渲染元素时，将 LaTeX 源码复制到剪贴板 |
| mathtex-script-type | 自动渲染 `<script type="math/tex">` 标签内的 LaTeX |
| mhchem | 化学方程式扩展（`\ce{}` 命令） |
| render-a11y-string | 生成无障碍字符串表示 |

各扩展的实现细节和用法见 [贡献扩展模块](/concepts/14-contrib-extensions.md)。

## 第三方库索引

官网 Libraries 页面按平台/语言分类列出第三方集成库[^web-libs]。以下为采集时的列表，供技术选型参考。

### 前端框架

| 平台 | 库名 | 说明 |
|------|------|------|
| React | react-katex、react-latex | React 组件封装 |
| Vue | vue-katex | Vue 集成 |
| Angular 2+ | ng-katex | Angular 集成 |
| Web Components | katex-element、katex-expression | 自定义元素（katex-expression 基于 Stencil） |

### 移动端

| 平台 | 库名 | 说明 |
|------|------|------|
| Android | KaTeXView | Android 视图封装 |
| iOS | KaTeX-iOS、KatexUtils | iOS 集成 |

### 服务端/其他语言

| 语言/平台 | 库名 | 说明 |
|----------|------|------|
| Ruby | katex-ruby | 服务端渲染，支持 Rails、Hanami、Sprockets 等框架集成 |
| Rust | katex-rs | Rust 服务端渲染绑定 |
| Jekyll | JekTex | Jekyll 插件 |
| Sphinx | sphinxcontrib-katex | Sphinx 文档集成 |

### 编辑器与工具

| 类型 | 库名 | 说明 |
|------|------|------|
| 编辑器 | Quill | KaTeX 官网列为用户，Quill 社区有 KaTeX 模块 |
| Canvas | canvas-latex | Canvas 渲染 |
| 输入格式 | asciimath2tex | 将 AsciiMath 转换为 LaTeX 后调用 KaTeX |

### 小程序

| 平台 | 库名 | 说明 |
|------|------|------|
| 微信小程序 | @rojer/katex-mini | 微信小程序 KaTeX 适配 |

### AsciiMath 支持

AsciiMath 语法需先通过 [asciimath2tex](https://github.com/ForbesLindesay/asciimath2tex) 转换为 LaTeX，再调用 KaTeX 渲染。该库面向 KaTeX 设计[^web-libs]。

## 选型建议

1. **框架集成**：优先选择对应框架的成熟封装库（如 React 用 react-katex），避免手动管理 DOM 生命周期
2. **服务端渲染**：Ruby 用 katex-ruby、Rust 用 katex-rs；Node.js 直接使用官方 `renderToString` API（见 [基础渲染示例](/examples/basic-render.md)）
3. **编辑器嵌入**：Quill 等编辑器有社区 KaTeX 模块，注意检查与 KaTeX v0.18 的兼容性
4. **小程序**：使用 @rojer/katex-mini，注意小程序 DOM 环境限制可能影响部分功能
5. **安全场景**：任何第三方库都应遵循 [安全与错误处理](/concepts/18-security-and-errors.md) 中的建议，处理不可信输入时配置 `trust: false`、`maxExpand: 1000` 等基线选项

## 相关概念

- [KaTeX 简介](/concepts/00-introduction.md) — 项目定位与核心特点
- [贡献扩展模块](/concepts/14-contrib-extensions.md) — 官方 5 个 contrib 扩展详解
- [安装与运行时](/concepts/15-installation-and-runtime.md) — 各环境安装方式
- [版本迁移](/concepts/22-migration.md) — v0.13-v0.18 升级指南
- [常见问题](/concepts/21-common-issues.md) — 集成排障
- [安全与错误处理](/concepts/18-security-and-errors.md) — 不可信输入安全配置

[^web-users]: 官网 Users 页面，https://katex.org/users
[^web-versions]: 官网 Versions 页面，https://katex.org/versions
[^web-libs]: 官网 Extensions & Libraries 页面，https://katex.org/docs/libs
[^facts]: KaTeX 事实清单，F-001（版本 0.18.4）、W-006~W-013、W-073~W-080
