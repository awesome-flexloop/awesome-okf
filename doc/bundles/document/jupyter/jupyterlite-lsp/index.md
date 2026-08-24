---
okf_version: "0.2"
---

# jupyterlite-lsp

> Language Server Protocol multiplexing server for JupyterLite — 浏览器端 LSP 支持

jupyterlite-lsp 为 [JupyterLite](https://jupyterlite.rtfd.io)（浏览器端 Jupyter）提供 Language Server Protocol（LSP）支持。它通过 mock-socket 在浏览器内模拟 jupyter-lsp 的 REST 和 WebSocket 端点，使语言服务器能在 Web Worker 中运行，实现零后端依赖的浏览器内代码智能提示。

- **版本**：0.1.0-alpha0
- **许可证**：BSD-3-Clause
- **仓库**：[https://github.com/jupyterlite/lsp](https://github.com/jupyterlite/lsp)
- **内置语言服务器**：YAML（含 JSON 支持）

## 文档导航

### [概念文档](concepts/index.md)

核心概念与架构设计，按学习路径排列：

| 编号 | 文档 | 说明 |
|------|------|------|
| 00 | [项目介绍](concepts/00-introduction.md) | 项目定位、解决的问题、技术栈 |
| 01 | [快速开始](concepts/01-getting-started.md) | 安装方式、开发环境搭建 |
| 02 | [架构总览](concepts/02-architecture-overview.md) | 三层桥接架构、数据流、组件关系 |
| 03 | [三插件体系](concepts/03-plugin-system.md) | hacksPlugin/serverPlugin/routesPlugin 详解 |
| 04 | [IJSONRPCLanguageServer 接口](concepts/04-language-server-interface.md) | 语言服务器统一接口、Session 双向桥接 |
| 05 | [Mock-Socket 桥接机制](concepts/05-mock-socket-bridge.md) | 虚拟 WebSocket、构建时 patch、REST 桥接 |
| 06 | [YAML/JSON 语言服务器](concepts/06-yaml-server.md) | yaml-language-server Worker 封装、WaitQueue 桥接 |
| 07 | [构建系统](concepts/07-build-system.md) | doit/lerna/flit/webpack 构建流程 |
| 08 | [Python 包与 Labextension](concepts/08-python-package.md) | Python 包结构、路径解析、扩展发现 |

### [示例文档](examples/index.md)

| 文档 | 说明 |
|------|------|
| [添加自定义语言服务器](examples/add-custom-language-server.md) | 为 jupyterlite-lsp 添加新语言服务器的完整步骤 |
| [本地开发环境搭建](examples/local-dev-setup.md) | 从零搭建开发环境、调试技巧 |

### [源码引用](references/index.md)

源码级引用文档，直接对应到源文件。

```{toctree}
:hidden:

concepts/index
examples/index
references/index
facts
insights
log
```
