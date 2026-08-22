# 概念文档

核心概念与架构设计，建议按编号顺序阅读。

| 编号 | 文档 | 说明 |
|------|------|------|
| 00 | [项目介绍](00-introduction.md) | 项目定位、解决的问题、核心特性、技术栈 |
| 01 | [快速开始](01-getting-started.md) | 安装方式、开发环境搭建、基本使用 |
| 02 | [架构总览](02-architecture-overview.md) | 三层桥接架构、数据流图、扩展点设计 |
| 03 | [三插件体系](03-plugin-system.md) | hacksPlugin、serverPlugin、routesPlugin 职责与依赖 |
| 04 | [IJSONRPCLanguageServer 接口与 Session](04-language-server-interface.md) | 统一接口定义、Session 双向消息桥接、LanguageServers 注册中心 |
| 05 | [Mock-Socket 桥接机制](05-mock-socket-bridge.md) | 构建时+运行时双阶段 patch、mock-socket 工作原理、REST 桥接 |
| 06 | [YAML/JSON 语言服务器](06-yaml-server.md) | @jupyterlite/lsp-yaml 实现、Worker 封装、WaitQueue 消息桥接 |
| 07 | [构建系统](07-build-system.md) | doit 任务编排、lerna monorepo、flit 打包、完整构建流程 |
| 08 | [Python 包与 Labextension 注册](08-python-package.md) | Python 包极简结构、双路径查找、JupyterLab 扩展发现 |

## 学习路径建议

```
入门路径：00 → 01 → 02
核心理解：03 → 04 → 05
深入实现：06 → 07 → 08
```
