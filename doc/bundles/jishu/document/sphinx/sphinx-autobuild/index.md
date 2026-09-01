---
okf_version: "0.2"
---

# sphinx-autobuild 知识库

本知识包是 Sphinx 生态中的实时预览工具 [sphinx-autobuild](https://github.com/sphinx-doc/sphinx-autobuild) 的系统化中文教程，基于源码深度阅读生成，覆盖从快速上手到核心架构的完整知识体系。所有内容均溯源至 sphinx-autobuild 源码（`sphinx_autobuild/` 包的 7 个核心模块），遵循 [OKF v0.2 规范](concepts/00-introduction.md)。

## 入门与基础（concepts/）

* [sphinx-autobuild 简介](concepts/00-introduction.md) — 什么是 sphinx-autobuild、设计理念、安装方法、与其他方案对比。
* [5分钟快速上手](concepts/01-getting-started.md) — 基本命令、autobuild 专有选项、默认忽略目录、Makefile 集成。

## 核心架构（concepts/）

* [架构概览](concepts/02-architecture-overview.md) — 整体架构图、四大核心组件、从文件变化到浏览器刷新的完整链路、异步任务模型。
* [CLI 入口与参数解析](concepts/03-cli-and-entrypoint.md) — 双解析器策略、Sphinx 参数复用原理、选项组设计、Make Mode 支持。
* [构建系统](concepts/04-builder-system.md) — Builder 类的子进程调用机制、前后置命令钩子、错误容错策略、进程隔离设计。
* [文件监听与过滤](concepts/05-file-watching.md) — watchfiles 异步监听、IgnoreFilter 双模式匹配（glob+正则）、默认忽略目录清单、SPHINX_AUTOBUILD_DEBUG 调试模式。
* [服务器与热重载](concepts/06-server-and-hotreload.md) — Starlette ASGI 应用组装、WebSocket 通信、asyncio.Event 信号机制、Lifespan 生命周期管理、多客户端支持。
* [中间件注入机制](concepts/07-middleware-injection.md) — JavascriptInjectorMiddleware 的 ASGI 中间件实现、HTML 响应拦截、Content-Length 修正、Cache-Control 处理。

## 实战示例（examples/）

* [基础使用](examples/basic-usage.md) — 从零开始：安装、初始化项目、启动预览、常用选项组合、调试忽略规则。
* [自定义前后置命令](examples/custom-pre-post-build.md) — 使用 --pre-build/--post-build 集成桌面通知、API 文档生成、资源复制、错误处理行为。
* [主题开发工作流](examples/theme-development.md) — Sphinx 主题开发配置：监听主题目录、-a 全量重建、多目录监听、性能优化。
* [多项目并行开发](examples/multi-project-setup.md) — 同时运行多个预览实例：--port=0 自动端口分配、后台运行、启动脚本、进程管理。

## 信源登记簿（references/）

* [sphinx-autobuild 源码信源登记](references/sphinx-autobuild-source.md) — 源码路径、版本号 2025.08.25、依赖清单、7 个核心模块完整 API 导出列表、测试覆盖范围。

## 信任与生命周期说明

* **status 判定依据**：全部 13 个内容文档（8 个概念 + 4 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 sphinx-autobuild 源码（`external/libs/docs/sphinx-autobuild/sphinx_autobuild/` 目录，7 个 Python 文件约 500 行核心代码）的逐模块阅读与事实提取，经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。sphinx-autobuild 核心架构稳定（Starlette+watchfiles+WebSocket 组合），主要 API（Builder/IgnoreFilter/RebuildServer/JavascriptInjectorMiddleware）自 2024 年大重构以来变化不大；该日期作为针对未来大版本升级的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-21）；`verified.at` 记录 V 阶段对抗审查核验事件（2026-08-21），两者分离、可追溯。

本知识包共收录 13 个内容文档（8 个概念 + 4 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
