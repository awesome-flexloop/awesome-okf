---
type: OKFBundle
title: JupyterLab Extension Template
description: 基于 Copier 的 JupyterLab 扩展项目模板，支持四种扩展类型（前端、MIME渲染器、全栈、主题），提供完整的双包构建、测试、CI/CD 和发布基础设施。
version: "4.0"
source: https://github.com/jupyterlab/extension-template
okf_version: "0.2"
generated:
  by: source-code-to-okf-wiki
  date: "2026-08-22"
tags: [jupyter, jupyterlab, extension, copier, template, typescript, python]
---

# JupyterLab Extension Template — OKF Wiki 教程

[JupyterLab Extension Template](https://github.com/jupyterlab/extension-template) 是 Jupyter 官方维护的项目模板，使用 [Copier](https://copier.readthedocs.io) 引擎生成 JupyterLab 4.x 扩展项目的脚手架。它通过 Jinja2 条件渲染在同一套模板中支持四种扩展类型，并预置了完整的构建、测试、CI/CD 和发布配置。

## ✨ 核心特性

- **四种扩展类型**：前端扩展（frontend）、MIME 渲染器（mimerenderer）、全栈扩展（frontend-and-server）、主题（theme）
- **双包分发**：TypeScript 前端 + Python wheel，用户只需 `pip install` 即可使用
- **条件渲染**：Jinja2 模板根据参数动态生成类型专属代码，一套模板覆盖所有场景
- **完整工具链**：TypeScript 严格模式、ESLint/Prettier/Stylelint、Jest/pytest、Playwright 集成测试
- **CI/CD 就绪**：GitHub Actions 工作流（构建、测试、Lint、链接检查、隔离安装测试）
- **自动化发布**：集成 Jupyter Releaser，一键发布到 PyPI + NPM
- **项目更新**：Copier update 支持，模板改进可合入已有项目

## 📚 文档导航

### [📗 概念文档](concepts/index.md)

系统讲解模板的核心概念和设计原理，按学习路径组织：

- **入门**：[介绍](concepts/00-introduction.md) · [快速开始](concepts/01-getting-started.md) · [Copier 基础](concepts/02-copier-basics.md)
- **核心**：[四种类型对比](concepts/03-four-extension-types.md) · [项目结构](concepts/04-project-structure.md) · [双包构建](concepts/05-build-system.md) · [前端开发](concepts/06-frontend-extension.md) · [服务端开发](concepts/07-server-extension.md) · [MIME 渲染器](concepts/08-mime-renderer.md) · [主题开发](concepts/09-theme-extension.md) · [设置系统](concepts/10-settings-schema.md)
- **工程**：[三层测试](concepts/11-testing-strategy.md) · [CI/CD 工作流](concepts/12-ci-workflows.md) · [打包发布](concepts/13-packaging-release.md)

### [🎯 实战示例](examples/index.md)

可直接运行的完整示例：

- [01 Hello World 前端扩展](examples/01-hello-world.md)
- [02 全栈扩展：前后端通信](examples/02-full-stack-server.md)
- [03 自定义 MIME 渲染器](examples/03-mime-renderer.md)
- [04 自定义暗色主题](examples/04-custom-dark-theme.md)

### [📖 参考文档](references/index.md)

从源码提取的精确参考：

- [Copier 配置参数全参考](references/copier-config.md)
- [package.json 模板字段解析](references/package-json-source.md)
- [pyproject.toml 模板字段解析](references/pyproject-source.md)
- [前端入口模板解析](references/frontend-entry-source.md)
- [Python 服务端模板解析](references/server-routes-source.md)
- [CI/CD 工作流源码解析](references/ci-workflows-source.md)

### [🧩 可复用模式](patterns/index.md)

从源码中提炼的设计模式，可应用于其他项目：

- [条件渲染模板模式](patterns/conditional-rendering.md)
- [双包分发模式](patterns/dual-package-distribution.md)
- [认证 API Handler 模式](patterns/authenticated-api-handler.md)

## 🚀 快速开始

```bash
# 安装 Copier
pip install "copier~=9.2" jinja2-time

# 生成扩展项目
copier copy --trust https://github.com/jupyterlab/extension-template myextension
cd myextension

# 安装开发环境
pip install -e ".[dev]"
jupyter-builder develop . --overwrite
jlpm install
jlpm build

# 启动开发
jlpm run watch    # 终端 1：监听构建
jupyter lab       # 终端 2：启动 JupyterLab
```

详细步骤参见 [快速开始](concepts/01-getting-started.md)。

## 🗂️ 扩展类型速查

| 类型 | 技术栈 | 后端 | 适用场景 |
|------|--------|------|---------|
| **frontend** | TypeScript | ❌ | 添加 UI、命令、面板、菜单项 |
| **mimerenderer** | TypeScript | ❌ | 自定义 MIME 类型数据渲染 |
| **frontend-and-server** | TS + Python | ✅ Tornado APIHandler | 需要后端计算、文件系统访问、API 代理 |
| **theme** | CSS + TypeScript | ❌ | 修改界面外观、颜色、字体 |

选型指南详见 [四种扩展类型对比](concepts/03-four-extension-types.md)。

## 🔗 外部资源

- [JupyterLab Extension Developer Guide](https://jupyterlab.readthedocs.io/en/stable/extension/extension_dev.html)
- [JupyterLab API Reference](https://jupyterlab.readthedocs.io/en/latest/api/index.html)
- [Extension Examples Repository](https://github.com/jupyterlab/extension-examples)
- [Jupyter Releaser](https://github.com/jupyter-server/jupyter_releaser)
- [Copier Documentation](https://copier.readthedocs.io)

```{toctree}
:hidden:

concepts/index
examples/index
references/index
patterns/index
facts
insights
log
```
