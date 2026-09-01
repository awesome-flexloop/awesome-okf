---
type: Concept
title: sphinx-copybutton 简介
description: sphinx-copybutton 是什么——为 Sphinx 代码块添加一键复制按钮的轻量扩展，定位、特点与适用场景
tags: [sphinx, sphinx-extension, copybutton, introduction, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: copybutton-source
    resource: /references/copybutton-source.md
    title: sphinx-copybutton 源码路径映射
---

# sphinx-copybutton 简介

sphinx-copybutton 是 [Executable Book Project](https://executablebooks.org/) 开发的 Sphinx 扩展，为文档中的每个代码块添加一个小的"复制"按钮。用户点击按钮即可将代码块内容复制到剪贴板，无需手动选中拖拽。它是 Jupyter Book、MyST 生态的默认依赖之一，被广泛应用于技术文档、教程、API 参考站点。

## 定位与特点

sphinx-copybutton 的核心设计哲学是**极简与实用**：

- **超轻量级**：核心仅 1 个 Python 文件（99 行）、1 个 CSS 文件、2 个 JavaScript 文件，总代码量不足 500 行
- **零配置可用**：安装并添加到 `extensions` 列表后即生效，无需额外配置即可在所有代码块显示复制按钮
- **智能文本清洗**：不仅是"复制 innerText"，还支持剥离 shell/REPL 提示符（`$`、`>>>` 等）、排除行号、处理行续接和 HERE 文档，确保"复制→粘贴→运行"一步到位
- **渐进增强 UX**：按钮默认隐藏仅悬停显示、打印时自动隐藏、复制成功后短暂显示对勾反馈、支持 7 种语言本地化
- **高度可定制**：支持自定义 CSS 选择器、自定义 SVG 图标、自定义提示符匹配规则

## 技术栈

sphinx-copybutton 基于以下技术构建：

- **Python 端**：使用 Sphinx 扩展 API（`add_config_value`、`add_css_file`、`add_js_file`、事件钩子）
- **前端**：原生 JavaScript（无框架依赖）+ [ClipboardJS](https://clipboardjs.com/) 库处理剪贴板 API 兼容性
- **样式**：纯 CSS，GitHub 风格配色，包含 CSS-only tooltip
- **模板**：Jinja2 模板（`.js_t` 后缀）实现 Python→JS 配置注入

## 适用场景

sphinx-copybutton 适合以下场景：

- **技术文档与教程**：读者经常需要复制代码示例到终端或编辑器运行
- **API 参考文档**：代码示例需要一键复制
- **Jupyter Book / MyST 文档**：作为默认组件提供交互式阅读体验
- **任何包含代码块的 Sphinx 站点**：提升文档的实用性和用户体验

## 环境要求

- Python 3.7+
- Sphinx 1.8+
- 浏览器支持：所有现代浏览器（ClipboardJS 处理了旧浏览器兼容性）

sphinx-copybutton 没有额外的 Python 第三方依赖（除了 Sphinx 本身）。

## 与同类方案对比

| 方案 | 特点 | 适用场景 |
|------|------|---------|
| sphinx-copybutton | 轻量、智能提示符剥离、可定制 | 大多数技术文档 |
| sphinx-tabs / sphinx-design 内置复制 | 与组件绑定，功能简单 | 配合特定组件使用 |
| 自定义 JS 实现 | 完全可控但需自行维护 | 有特殊需求的大型站点 |
| 浏览器扩展（如 Copy All Urls） | 用户端安装，非站点提供 | 不适合面向公众的文档 |

## 相关概念

- [快速开始](01-getting-started.md)
- [扩展架构与注册机制](02-extension-architecture.md)
- [基础配置示例](../examples/basic-setup.md)
