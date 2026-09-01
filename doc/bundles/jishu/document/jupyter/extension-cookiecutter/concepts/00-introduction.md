---
type: Concept
title: Jupyter Server Extension CookieCutter 介绍
description: 了解 Jupyter Server Extension CookieCutter 是什么、它解决什么问题、与 JupyterLab Extension Template 的区别，以及适用场景。
tags: [introduction, jupyter-server, extension, cookiecutter, overview]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:10:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:10:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/cookiecutter-json.md
    title: cookiecutter.json 参数全参考
---

## 什么是 Jupyter Server Extension CookieCutter

Jupyter Server Extension CookieCutter 是 [Jupyter Server](https://github.com/jupyter-server) 官方维护的项目脚手架模板，用于快速创建一个符合社区规范的 **Jupyter Server 后端扩展**。它基于 [Cookiecutter](https://github.com/audreyr/cookiecutter) 模板引擎，通过交互式问答收集项目信息，自动生成一个可以直接开发、测试和发布的 Python 包骨架。

生成的项目包含一个最简化的工作示例：一个 `/ping` HTTP 端点，返回 JSON 响应 `{"ping_response": "pong"}`。开发者以此为起点，添加自己的 API 端点、业务逻辑和配置项。

## 它解决什么问题

从零创建一个 Jupyter Server 扩展需要配置大量基础设施：

- Python 包构建配置（pyproject.toml、build-backend）
- Jupyter 配置发现机制（jupyter-config 目录）
- 扩展入口注册（`_jupyter_server_extension_points()`）
- ExtensionApp 和 APIHandler 的正确继承和初始化
- Tornado 认证装饰器
- 异步测试基础设施（pytest-jupyter）
- 代码质量工具链（black、ruff、mypy、mdformat）
- CI/CD 工作流（多 OS × 多 Python 版本矩阵）
- Binder 集成
- 发布流程（PyPI、conda-forge、Jupyter Releaser）

Cookiecutter 模板一键生成所有这些配置，开发者只需要关注业务代码。

## 与 JupyterLab Extension Template 的区别

Jupyter 生态中有两个官方扩展模板，它们针对不同的扩展类型：

| 特性 | Extension CookieCutter（本模板） | Extension Template（Copier） |
|------|----------------------------------|------------------------------|
| **扩展层级** | Jupyter Server **后端**扩展 | JupyterLab **前端**扩展 |
| **模板引擎** | Cookiecutter | Copier |
| **技术栈** | 纯 Python | TypeScript + Python（双包） |
| **扩展类型** | 仅后端 API | 前端/MIME/全栈/主题 四种 |
| **前端构建** | ❌ 无 | ✅ Webpack/jlpm |
| **NPM 包** | ❌ 无 | ✅ 有 |
| **适用场景** | 添加 REST API、后端服务、文件处理 | 添加 UI 组件、面板、主题、渲染器 |

如果你的扩展只需要提供后端 API 而不需要 JupyterLab 前端 UI，本模板是更轻量的选择——不引入 Node.js 构建链，项目结构更简洁。

如果需要同时添加 JupyterLab 前端界面（如侧边栏面板、菜单项、Notebook 渲染器），应使用 [JupyterLab Extension Template](https://github.com/jupyterlab/extension-template)（基于 Copier）。

## 核心特性

- **极简骨架**：只包含 ExtensionApp + 一个 PingHandler 示例，代码量最小
- **纯 Python**：不需要 Node.js/npm/jlpm，纯 pip 安装即可开发
- **hatchling 构建**：使用现代 PEP 517 构建后端，通过 shared-data 机制安装配置文件
- **开箱即用测试**：pytest-jupyter 异步测试基础设施，`jp_fetch` fixture 直接测试 API
- **完整工具链**：black + ruff + mypy + mdformat + pre-commit 代码质量保障
- **多平台 CI**：GitHub Actions 矩阵构建（Ubuntu/macOS/Windows × Python 3.8-3.11）
- **自动化发布**：集成 Jupyter Releaser，支持一键发布到 PyPI
- **Binder 支持**：可选生成 Binder 配置，一键在云端试玩
- **BSD 许可证**：与 Jupyter 生态一致的宽松许可证

## 版本要求

| 工具 | 最低版本 |
|------|---------|
| Python | >= 3.8 |
| Jupyter Server | >= 1.6, < 3 |
| Cookiecutter | 最新版（`pip install cookiecutter`） |
| hatchling | >= 1.5（自动作为 build-backend 安装） |

## 适用场景

本模板适合以下场景：

1. **添加后端 API 端点**：为 Jupyter 环境提供自定义 REST API，如文件转换、数据查询、计算服务
2. **集成外部服务**：作为代理层对接数据库、云计算平台、内部 API
3. **内核管理扩展**：扩展 Jupyter Server 的内核生命周期管理
4. **内容管理扩展**：自定义文件存储后端（如 S3、数据库存储）
5. **学习 Jupyter Server 扩展开发**：最小化的代码量帮助理解 ExtensionApp/APIHandler 核心概念

不适合以下场景：

- 需要 JupyterLab 前端 UI 组件 → 使用 [JupyterLab Extension Template](https://github.com/jupyterlab/extension-template)
- 只需要 Notebook 服务端扩展（经典 Notebook） → 使用 notebook server extension 模板
- JupyterLab 3.x 兼容扩展 → 需使用旧版模板

## 相关概念

- [快速开始](01-getting-started.md)
- [Cookiecutter 模板引擎基础](02-cookiecutter-basics.md)
- [生成的项目结构](03-project-structure.md)
