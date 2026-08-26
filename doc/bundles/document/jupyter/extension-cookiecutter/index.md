---
type: OKFBundle
title: Jupyter Server Extension CookieCutter
description: 基于 Cookiecutter 的 Jupyter Server 纯后端扩展项目模板，生成 Python-only 的 ExtensionApp 脚手架，预置 Tornado APIHandler、pytest-jupyter 测试、Hatchling 构建、CI/CD 和 Jupyter Releaser 发布流程。
version: "3.0"
source: https://github.com/jupyter-server/extension-cookiecutter
okf_version: "0.2"
generated:
  by: source-code-to-okf-wiki
  date: "2026-08-22"
tags: [jupyter, jupyter-server, extension, cookiecutter, python, tornado, backend]
---

# Jupyter Server Extension CookieCutter — OKF Wiki 教程

[Jupyter Server Extension CookieCutter](https://github.com/jupyter-server/extension-cookiecutter) 是 Jupyter Server 官方维护的项目模板，使用 [Cookiecutter](https://cookiecutter.readthedocs.io) 引擎生成纯后端 Jupyter Server 扩展项目的脚手架。它面向需要为 Jupyter Server 添加 REST API、自定义业务逻辑、服务集成等后端功能的 Python 开发者，预置了完整的构建、测试、CI/CD 和发布配置。

## ✨ 核心特性

- **纯后端聚焦**：生成 Python-only 的 ExtensionApp，无前端依赖，代码量极小（核心约 30 行）
- **Cookiecutter 模板引擎**：Jinja2 变量渲染 + post_gen_project 钩子，支持 Binder 开关等条件生成
- **ExtensionApp 基类**：继承官方 ExtensionApp，自动获得配置发现、生命周期管理、settings 注入
- **Tornado APIHandler**：预置认证装饰器（@tornado.web.authenticated）的 API 端点示例
- **自动配置发现**：jupyter-config 目录 + Hatchling shared-data 安装，pip install 即自动启用
- **pytest-jupyter 测试**：预置 jp_fetch fixture，异步测试 Jupyter Server 扩展端点
- **Hatchling 构建**：PEP 517/621 现代构建后端，wheel/sdist 双格式分发
- **CI/CD 就绪**：GitHub Actions 多平台矩阵（Ubuntu/macOS/Windows × Python 3.8-3.10）、Lint 检查、链接检查、Release 检查
- **Jupyter Releaser 集成**：一键自动化发布到 PyPI
- **可选 Binder**：一键开关生成 Binder 配置 + PR 自动评论 Binder 链接

## 📚 文档导航

### [📗 概念文档](concepts/index.md)

系统讲解模板的核心概念和设计原理，按学习路径组织：

- **入门**：[介绍](concepts/00-introduction.md) · [快速开始](concepts/01-getting-started.md) · [Cookiecutter 基础](concepts/02-cookiecutter-basics.md) · [项目结构](concepts/03-project-structure.md)
- **核心开发**：[ExtensionApp 开发](concepts/04-extension-app.md) · [API Handler 开发](concepts/05-api-handlers.md) · [配置发现机制](concepts/06-config-discovery.md) · [测试策略](concepts/07-testing.md)
- **工程化**：[构建系统](concepts/08-build-system.md) · [CI/CD 工作流](concepts/09-ci-workflows.md) · [Binder 集成](concepts/10-binder-integration.md) · [代码质量工具](concepts/11-code-quality.md) · [打包发布](concepts/12-packaging-release.md)

### [🎯 实战示例](examples/index.md)

可直接运行的完整示例：

- [01 基础 Ping 扩展示例](examples/01-basic-ping-extension.md) — 逐行解析模板生成的完整代码
- [02 添加自定义 API 端点](examples/02-custom-endpoint.md) — CRUD REST API、路径参数、错误处理
- [03 添加可配置参数](examples/03-configurable-extension.md) — traitlets 配置类型、验证器、测试覆盖

### [📖 参考文档](references/index.md)

从源码提取的精确参考：

- [cookiecutter.json 模板变量全解析](references/cookiecutter-json.md)
- [post_gen_project.py 生成后钩子解析](references/post-gen-hook-source.md)
- [ExtensionApp 类源码解析](references/extension-app-source.md)
- [PingHandler 请求处理器源码解析](references/handler-source.md)
- [pyproject.toml 模板字段全解析](references/pyproject-source.md)
- [测试源码解析](references/test-source.md)
- [CI/CD 工作流源码解析](references/ci-workflow-source.md)

## 🚀 快速开始

```bash
# 安装 Cookiecutter
pip install cookiecutter

# 生成扩展项目
cookiecutter https://github.com/jupyter-server/extension-cookiecutter
# 按提示输入：
#   author_name [Your Name (or your organization)]: Jovian
#   author_email: jovian@example.com
#   package_name [my_extension]: my_extension
#   project_short_description [A Jupyter Server extension.]: My first extension
#   has_binder [n]: n

# 进入项目并开发安装
cd my_extension
pip install -e ".[test]"

# 运行测试
pytest

# 启动 Jupyter Server 测试
jupyter server --autoreload
# 浏览器访问 http://localhost:8888/my-extension/ping?token=<token>
```

详细步骤参见 [快速开始](concepts/01-getting-started.md)。

## 🗂️ 模板 vs 其他 Jupyter 模板速查

| 模板 | 技术栈 | 前端 | 适用场景 |
|------|--------|------|---------|
| **extension-cookiecutter**（本模板） | Python | ❌ 无 | 纯后端 REST API、服务集成、业务逻辑 |
| [extension-template](https://github.com/jupyterlab/extension-template) | TS + Python | ✅ Lumino | JupyterLab UI 扩展（命令、面板、菜单、主题） |
| [extension-examples](https://github.com/jupyterlab/extension-examples) | TS + Python | ✅ Lumino | JupyterLab 扩展示例集合（学习参考） |

选型指南：如果你只需要添加后端 HTTP 端点、访问文件系统、代理外部服务，用本模板即可；如果你需要在 JupyterLab UI 中添加按钮、面板、菜单项，使用 [extension-template](https://github.com/jupyterlab/extension-template)。

## 🔗 外部资源

- [Jupyter Server Documentation](https://jupyter-server.readthedocs.io/)
- [Jupyter Server Extension Developer Guide](https://jupyter-server.readthedocs.io/en/latest/developers/extensions.html)
- [Cookiecutter Documentation](https://cookiecutter.readthedocs.io)
- [pytest-jupyter Documentation](https://pytest-jupyter.readthedocs.io)
- [Hatchling Build Backend](https://hatch.pypa.io/latest/)
- [Jupyter Releaser](https://github.com/jupyter-server/jupyter_releaser)
- [traitlets Documentation](https://traitlets.readthedocs.io)

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
