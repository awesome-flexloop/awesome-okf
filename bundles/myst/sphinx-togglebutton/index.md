---
okf_version: "0.2"
type: bundle
title: "sphinx-togglebutton — Sphinx 内容折叠按钮扩展"
description: "为 Sphinx 文档添加折叠/展开切换按钮的轻量扩展，支持提示框折叠和任意内容折叠，核心仅 107 行 Python 代码"
tags: [sphinx, toggle, collapsible, dropdown, extension, executable-books, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:15:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: togglebutton-repo
    resource: https://github.com/executablebooks/sphinx-togglebutton
    title: sphinx-togglebutton GitHub Repository
    author: team:executablebooks
---

# sphinx-togglebutton — Sphinx 内容折叠按钮扩展

sphinx-togglebutton 是 Executable Books 生态中的轻量级 Sphinx 扩展，为文档页面添加"折叠/展开"切换按钮，允许将提示框（admonition）和任意内容区域设为可折叠状态。核心 Python 代码仅约 107 行，被 Jupyter Book、MyST-NB 等项目广泛使用。

> **核心特点**：双轨 DOM 策略——admonition 使用 CSS 类切换方案，普通内容使用原生 `<details>/<summary>` 元素；打印友好（自动展开）；30+ 语言国际化支持。

## 知识地图

```
sphinx-togglebutton/
├── 📖 concepts/       概念文档（4 篇）
│   ├── 入门：简介、快速开始
│   └── 核心：toggle 指令、配置项参考
├── 💡 examples/       实战示例（2 篇）
│   ├── 基础使用（提示框折叠/答案/代码）
│   └── 打印与国际化配置
└── 📚 references/     信源参考（1 篇）
    └── 源码路径映射
```

## 推荐学习路径

### 10 分钟快速上手

1. [简介](concepts/00-introduction.md) → 了解定位和功能特点（3 分钟）
2. [快速开始](concepts/01-getting-started.md) → 安装配置，实现第一个折叠提示框（7 分钟）

### 深入理解

3. [toggle 指令详解](concepts/02-toggle-directive.md) → 理解指令语法和两种 DOM 策略
4. [配置项参考](concepts/03-configuration.md) → 掌握全部配置项

### 实战参考

5. [基础使用示例](examples/basic-usage.md) → 常见场景的 RST 代码
6. [打印与国际化配置](examples/print-and-i18n.md) → 打印行为和多语言设置

## 核心洞察

| # | 洞察 | 一句话总结 |
|---|------|-----------|
| 1 | 双轨 DOM 策略 | admonition 用 CSS 类切换，普通内容用原生 details，智能分发 |
| 2 | 选择器驱动折叠 | `:class: dropdown` 即可折叠提示框，无需指令，零侵入 |
| 3 | 打印友好设计 | beforeprint/afterprint 状态快照与恢复，确保打印输出完整 |
| 4 | 内联 JS 配置注入 | 构建时将配置序列化为 JS 变量内联到 HTML，零运行时开销 |

## 相关知识束

| 知识束 | 关系 |
|--------|------|
| [sphinx-tabs](https://github.com/executablebooks/sphinx-tabs) | 同生态标签页组件扩展 |
| [sphinx-exercise](https://github.com/executablebooks/sphinx-exercise) | 同生态练习/答案指令扩展（答案折叠是典型应用场景） |
| [sphinx-design](https://github.com/executablebooks/sphinx-design) | 更丰富的 UI 组件库（含 dropdown 指令） |
