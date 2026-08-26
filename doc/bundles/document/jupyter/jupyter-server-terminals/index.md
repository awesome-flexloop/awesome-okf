---
okf_version: "0.2"
---

# jupyter_server_terminals 知识库

本知识包是 [jupyter_server_terminals](https://github.com/jupyter-server/jupyter_server_terminals)（Jupyter Server 终端扩展 v0.5.4）的系统化中文教程，基于源码深度阅读生成，覆盖从快速上手到架构理解的完整知识体系。所有内容均溯源至 jupyter_server_terminals 源码，遵循 [OKF v0.2 规范](/references/jupyter-server-terminals-source.md)。

jupyter_server_terminals 为 JupyterLab、Notebook 等前端提供浏览器内的交互式系统终端能力，是 Jupyter 生态的核心组件之一。

## 入门与基础（concepts/）

* [jupyter_server_terminals 简介](concepts/00-introduction.md) — 什么是 jupyter_server_terminals、与 terminado 的薄层委托关系、核心能力。
* [5分钟快速上手](concepts/01-getting-started.md) — 安装、启用扩展、验证终端功能、REST API 快速体验、基本配置。

## 核心架构（concepts/）

* [TerminalsExtensionApp 扩展应用](concepts/02-extension-app.md) — 扩展生命周期（settings/handlers 初始化→运行→cleanup）、Shell 配置流程、环境变量传递。
* [TerminalManager 终端管理器](concepts/03-terminal-manager.md) — 终端 CRUD、REST JSON 模型、闲置终端自动清理（Culler）、Prometheus 指标、双层活动追踪。

## 通信与接口（concepts/）

* [REST API 处理器](concepts/04-rest-api.md) — 终端集合/单终端路由、@authenticated+@authorized 认证链、cwd 路径三级解析策略。
* [WebSocket 处理器](concepts/05-websocket.md) — TermSocket 四父类多继承、握手认证（execute权限）、JSON 消息协议、活动时间戳更新。

## 配置与平台（concepts/）

* [Shell 配置与平台差异](concepts/06-shell-configuration.md) — Shell 确定优先级链、Windows PowerShell 默认、Login Shell 自动追加、JUPYTER_SERVER_ROOT/URL 环境变量。

## 实战示例（examples/）

* [基础终端操作](examples/basic-operations.md) — REST API CRUD 完整示例（Python requests / curl / JavaScript fetch）。
* [WebSocket 实时通信](examples/websocket-interaction.md) — WebSocket 连接与实时交互（浏览器 JS / Python websockets / Tornado），消息协议详解。
* [配置自动清理与指定工作目录](examples/culler-and-cwd.md) — Culling 配置与验证、cwd 工作目录指定与路径解析。

## 信源登记簿（references/）

* [jupyter_server_terminals 源码信源登记](references/jupyter-server-terminals-source.md) — 源码路径、版本信息（v0.5.4）、核心模块清单、依赖关系、API 端点。

## 信任与生命周期说明

* **status 判定依据**：全部 11 个内容文档（7 个概念 + 3 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 jupyter_server_terminals v0.5.4 源码（7 个核心 Python 文件，约 510 行代码）的逐模块阅读与 59 个事实提取，经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。jupyter_server_terminals 作为 Jupyter Server 生态的稳定扩展，核心 API（ExtensionApp/TerminalManager/REST handlers）自 Jupyter Server 2.0 拆分以来变化不大；该日期作为针对未来大版本升级的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-22）；`verified.at` 记录 V 阶段对抗审查核验事件（2026-08-22），两者分离、可追溯。

本知识包共收录 11 个内容文档（7 个概念 + 3 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
