# 概念文档

系统讲解 Jupyter Server Extension CookieCutter 的核心概念和设计原理，按学习路径组织。

## 入门

- [00 介绍](00-introduction.md) — 什么是 Jupyter Server Extension CookieCutter、与其他模板的区别、适用场景
- [01 快速开始](01-getting-started.md) — 安装 Cookiecutter、生成项目、开发安装、运行测试
- [02 Cookiecutter 模板引擎基础](02-cookiecutter-basics.md) — Cookiecutter 核心概念、Jinja2 渲染、Hooks 钩子
- [03 生成的项目结构](03-project-structure.md) — 目录结构、每个文件的作用、文件依赖关系

## 核心开发

- [04 ExtensionApp 开发](04-extension-app.md) — ExtensionApp 基类、traitlets 配置、settings 传递、生命周期
- [05 API Handler 开发](05-api-handlers.md) — Handler 继承体系、认证装饰器、HTTP 动词、JSON 响应
- [06 配置发现机制](06-config-discovery.md) — jupyter-config 目录、shared-data 安装、自动启用原理
- [07 测试策略](07-testing.md) — pytest-jupyter、jp_fetch fixture、异步测试、配置覆盖

## 工程化

- [08 构建系统](08-build-system.md) — hatchling、PEP 517/621、shared-data、wheel/sdist
- [09 CI/CD 工作流](09-ci-workflows.md) — 多平台矩阵构建、链接检查、Jupyter Releaser
- [10 Binder 集成](10-binder-integration.md) — Binder 配置、environment.yml、postBuild、PR 自动链接
- [11 代码质量工具](11-code-quality.md) — ruff、black、mypy、mdformat、pre-commit
- [12 打包发布](12-packaging-release.md) — 手动发布、Jupyter Releaser、conda-forge

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-cookiecutter-basics
03-project-structure
04-extension-app
05-api-handlers
06-config-discovery
07-testing
08-build-system
09-ci-workflows
10-binder-integration
11-code-quality
12-packaging-release
```
