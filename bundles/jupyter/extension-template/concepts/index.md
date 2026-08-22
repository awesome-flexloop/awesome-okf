# 概念文档（Concepts）

按学习路径组织的概念性文档，从入门到深入，系统讲解 JupyterLab Extension Template 的核心概念和设计原理。

## 📗 入门组

| 编号 | 文档 | 内容 |
|------|------|------|
| 00 | [Introduction](00-introduction.md) | 模板介绍、支持的扩展类型、核心特性概览 |
| 01 | [快速开始](01-getting-started.md) | 安装 Copier、生成第一个扩展、运行开发环境 |
| 02 | [Copier 模板引擎基础](02-copier-basics.md) | Copier 工作原理、Jinja2 条件渲染、参数类型、后处理任务 |

## 📘 核心组

| 编号 | 文档 | 内容 |
|------|------|------|
| 03 | [四种扩展类型对比与选型](03-four-extension-types.md) | frontend / mimerenderer / frontend-and-server / theme 四种类型的架构差异与选型指南 |
| 04 | [生成项目结构详解](04-project-structure.md) | 项目目录结构、每个文件的作用、条件文件/目录矩阵 |
| 05 | [双包构建系统](05-build-system.md) | NPM+Python 双包架构、hatchling + jupyter-builder + tsc 构建流程、开发模式与生产构建 |
| 06 | [前端扩展开发](06-frontend-extension.md) | JupyterFrontEndPlugin 模型、activate 生命周期、命令注册、Widget、设置集成、前后端通信 |
| 07 | [服务端扩展开发](07-server-extension.md) | APIHandler 模式、路由注册、认证装饰器、前后端通信协议 |
| 08 | [MIME 渲染器开发](08-mime-renderer.md) | IRenderMime 模型、OutputWidget、文件类型注册、安全模型 |
| 09 | [主题扩展开发](09-theme-extension.md) | CSS 变量体系、IThemeManager 注册、亮色/暗色主题创建 |
| 10 | [设置系统与 JSON Schema](10-settings-schema.md) | plugin.json Schema 编写、快捷键绑定、运行时设置监听 |

## 📙 工程组

| 编号 | 文档 | 内容 |
|------|------|------|
| 11 | [三层测试策略](11-testing-strategy.md) | Jest 单元测试、pytest 后端测试、Playwright/Galata 集成测试 |
| 12 | [CI/CD 工作流详解](12-ci-workflows.md) | GitHub Actions 工作流体系、Jupyter Releaser 自动化发布管道 |
| 13 | [打包与发布](13-packaging-release.md) | 手动发布与自动化发布、版本管理、PyPI + NPM 双包发布 |

## 学习路径建议

**初学者**：00 → 01 → 02 → 03 → 04 → 05 → 06 → 做 [示例 01](../examples/01-hello-world.md)

**开发特定类型**：
- 纯前端 UI 扩展：00 → 01 → 06 → 05
- 全栈扩展（前后端）：00 → 01 → 07 → 06 → 做 [示例 02](../examples/02-full-stack-server.md)
- 自定义数据渲染：00 → 01 → 08 → 做 [示例 03](../examples/03-mime-renderer.md)
- 自定义主题：00 → 01 → 09 → 做 [示例 04](../examples/04-custom-dark-theme.md)

**工程化**：11 → 12 → 13
