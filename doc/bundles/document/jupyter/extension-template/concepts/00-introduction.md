---
type: Concept
title: JupyterLab Extension Template 介绍
description: 了解 JupyterLab Extension Template 是什么、它解决什么问题、支持哪些扩展类型，以及它与旧版 cookiecutter 模板的区别。
tags: [introduction, jupyterlab, extension, copier, overview]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:20:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:20:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/copier-config.md
    title: Copier 配置参数全参考
---

## 什么是 JupyterLab Extension Template

JupyterLab Extension Template 是 JupyterLab 官方维护的项目脚手架模板，用于快速创建符合社区规范的 JupyterLab 4.x 扩展项目。它基于 [Copier](https://copier.readthedocs.io) 模板引擎，通过交互式问答收集项目信息，然后自动生成一个完整的、可直接开发和发布的扩展项目骨架。

与传统的"Hello World"模板不同，这个模板生成的项目已经包含了完整的工程化配置：TypeScript 编译、ESLint/Stylelint/Prettier 代码检查、Jest/pytest/Playwright 三层测试、GitHub Actions CI/CD 流水线、双包（NPM + Python）构建配置、以及可选的 AI 编码规范文件（AGENTS.md）。

## 支持的扩展类型

模板支持生成四种类型的 JupyterLab 扩展：

1. **frontend（纯前端扩展）**：使用 TypeScript 编写，运行在浏览器中，为 JupyterLab 添加新的 UI 组件、命令、菜单项、面板等。这是最常见的扩展类型。

2. **mimerenderer（MIME 渲染器）**：为特定 MIME 类型的输出提供自定义渲染方式。例如，当 notebook 输出 GeoJSON 数据时，可以自动渲染为交互式地图。

3. **frontend-and-server（全栈扩展）**：同时包含 TypeScript 前端和 Python 后端。前端通过 REST API 与后端通信，后端可以访问文件系统、启动进程、调用其他 Python 库等。

4. **theme（主题扩展）**：通过 CSS 变量自定义 JupyterLab 的外观，支持亮色/暗色模式切换。

## 核心特性

- **双包分发架构**：前端代码是 NPM 包，但通过 Python wheel 分发给终端用户。用户只需 `pip install` 即可安装扩展，无需 NodeJS 环境。
- **条件渲染**：四种扩展类型共享同一套模板，通过 Jinja2 条件块（`{% if kind == ... %}`）根据用户选择生成差异化代码。
- **开箱即用的工程化**：生成的项目已配置好构建、测试、Lint、CI/CD，开发者可以立即开始写业务代码。
- **可更新性**：基于 Copier 的项目支持 `copier update` 命令，可以将模板的更新（如依赖版本升级、新配置）合并到已有项目中。
- **AI 辅助开发支持**：可选生成 AGENTS.md 文件，为 Cursor、GitHub Copilot、Claude Code 等 AI 编程工具提供 JupyterLab 扩展开发规范上下文。

## 与旧版 cookiecutter 模板的区别

在 JupyterLab 4.0 之前，官方推荐使用 cookiecutter 模板（`extension-cookiecutter-ts`）。Copier 模板相比 cookiecutter 有以下改进：

- 支持 `copier update` 更新已有项目（cookiecutter 不支持）
- 更丰富的参数验证和条件逻辑
- 内置四种扩展类型（旧版需要不同的 cookiecutter 模板）
- 更现代化的工具链（ESLint 9 flat config、TypeScript 5.x、Playwright）
- 可选的 AI 编码规范文件

> **注意**：如果需要为 JupyterLab 3.x 创建扩展，仍需使用旧版 cookiecutter 模板。本模板仅支持 JupyterLab >= 4.0.0。

## 版本要求

| 工具 | 最低版本 |
|------|---------|
| JupyterLab | >= 4.0.0 |
| Python | >= 3.10 |
| Copier | >= 9.2, < 10 |
| Node.js | LTS 版本（推荐 >= 18） |

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [Copier 模板引擎基础](/concepts/02-copier-basics.md)
- [四种扩展类型对比](/concepts/03-four-extension-types.md)
- [Copier 配置参数参考](/references/copier-config.md)
