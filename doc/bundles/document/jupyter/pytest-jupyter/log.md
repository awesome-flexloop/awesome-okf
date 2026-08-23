# Changelog for pytest-jupyter OKF bundle

本文件记录此OKF知识束的文档变更历史。

## 2026-08-22 — 初始版本（v0.1.0）

### Added
- **概念文档（9篇）**：
  - `concepts/00-introduction.md` — pytest-jupyter 简介与核心能力概览
  - `concepts/01-getting-started.md` — 5分钟快速上手指南
  - `concepts/02-architecture-overview.md` — 三层插件架构与模块设计
  - `concepts/03-core-plugin.md` — Core插件fixtures详解
  - `concepts/04-client-plugin.md` — Client插件fixtures详解
  - `concepts/05-server-plugin.md` — Server插件fixtures详解
  - `concepts/06-tornasync-plugin.md` — 内嵌pytest-tornasync异步测试支持
  - `concepts/07-echo-kernel.md` — Echo测试内核实现与扩展
  - `concepts/08-fixture-factories.md` — Fixture工厂模式设计模式
  - `concepts/index.md` — 概念文档索引

- **示例文档（4篇）**：
  - `examples/01-basic-core-test.md` — Core插件基础测试示例
  - `examples/02-kernel-testing.md` — 内核启动与消息通信测试示例
  - `examples/03-server-api-test.md` — Jupyter Server REST API与WebSocket测试示例
  - `examples/04-custom-server-config.md` — 自定义Server配置示例
  - `examples/index.md` — 示例文档索引

- **源码信源文档（8篇）**：
  - `references/utils-source.md` — utils.py 工具函数信源
  - `references/jupyter-core-source.md` — jupyter_core.py Core插件信源
  - `references/jupyter-client-source.md` — jupyter_client.py Client插件信源
  - `references/echo-kernel-source.md` — echo_kernel.py Echo内核信源
  - `references/pytest-tornasync-source.md` — pytest_tornasync.py 内嵌插件信源
  - `references/jupyter-server-source.md` — jupyter_server.py Server插件信源
  - `references/init-source.md` — __init__.py 入口信源
  - `references/index.md` — 信源索引

- **根文档**：
  - `index.md` — 知识束首页与导航
  - `log.md` — 变更日志（本文件）

### Source Analysis
- 基于源码 `d:\spaces\SpecWeave/external/libs/jupyter/pytest-jupyter` 版本 v0.12.0.dev0
- 覆盖模块：`pytest_jupyter/jupyter_core.py`, `pytest_jupyter/jupyter_client.py`, `pytest_jupyter/jupyter_server.py`, `pytest_jupyter/echo_kernel.py`, `pytest_jupyter/pytest_tornasync.py`, `pytest_jupyter/utils.py`, `pytest_jupyter/__init__.py`
- 覆盖fixtures：jp_environ, jp_asyncio_loop, jp_zmq_context, jp_start_kernel, jp_serverapp, jp_configurable_serverapp, jp_fetch, jp_ws_fetch, jp_create_notebook, send_request, 以及所有目录/内核/认证fixtures
- 覆盖核心模式：Factory Fixture模式、环境隔离模式、三层插件架构、异步测试钩子
