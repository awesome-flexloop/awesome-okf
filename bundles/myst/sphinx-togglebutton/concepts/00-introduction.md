---
type: Concept
title: sphinx-togglebutton 简介
description: sphinx-togglebutton 是什么——为 Sphinx 文档添加折叠/切换按钮的轻量扩展，支持提示框折叠和任意内容折叠
tags: [sphinx, toggle, collapsible, introduction, extension]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:02:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: togglebutton-source
    resource: /references/togglebutton-source.md
    title: sphinx-togglebutton 源码路径映射
---

# sphinx-togglebutton 简介

sphinx-togglebutton 是 Executable Books 生态中的一个轻量级 Sphinx 扩展，为文档页面添加"折叠/展开"切换按钮（toggle button），允许将内容区域设为可折叠状态。它被 Jupyter Book、MyST-NB 等项目广泛使用，核心 Python 代码仅约 100 行。

## 核心功能

sphinx-togglebutton 支持两种折叠场景：

- **提示框折叠**：为 Sphinx 内置的 admonition（note、warning、tip 等）添加折叠按钮，默认隐藏内容，点击标题栏展开
- **任意内容折叠**：通过 `.. toggle::` 指令将任意内容块（图片、代码、表格等）包装为可折叠区域

## 设计特点

- **双轨 DOM 策略**：对 admonition 使用 CSS 类切换方案，对普通内容使用原生 `<details>/<summary>` HTML 元素
- **零侵入 admonition**：提示框折叠完全由前端 JS 驱动，Python 端不需要修改 admonition 输出
- **打印友好**：打印时自动展开所有折叠内容，打印后恢复状态
- **国际化支持**：按钮提示文本支持 30+ 种语言
- **无障碍支持**：使用 ARIA 属性（`aria-expanded`、`aria-label`、`aria-controls`）
- **渐进增强**：JS 未加载时所有内容完全可见

## 环境要求

- Python 3（sphinx 和 docutils 作为依赖自动安装）
- Sphinx（版本随 setup.cfg 依赖声明）

## 与其他折叠扩展的关系

在 Executable Books 生态中，sphinx-togglebutton 是最早的折叠实现，后续 sphinx-design 扩展中的 `dropdown` 指令提供了更丰富的折叠样式。sphinx-togglebutton 保持极简定位，仅专注于折叠切换功能。

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [toggle 指令详解](/concepts/02-toggle-directive.md)
- [配置项参考](/concepts/03-configuration.md)
