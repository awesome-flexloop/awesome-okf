---
type: "index"
title: "Jupyter 概念文档索引"
description: "Jupyter 元包核心概念文档目录——13篇从入门到进阶的系统化概念讲解"
tags: [jupyter, concepts, index]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22" }
status: active
---

# 概念文档（concepts/）

本目录包含13篇从入门到进阶的 Jupyter 概念文档，按学习路径分为四篇。

## 入门篇（00-05）

* [00. Jupyter 元包与核心组件](00-introduction.md) — jupyter 元包的定位、Project Jupyter 生态概览、五大核心组件、本教程学习路径。
* [01. 什么是计算笔记本与 Jupyter 核心架构](01-what-is-jupyter.md) — Literate Computing 理念、REPL 模式、计算笔记本概念、Kernel 抽象、客户端-服务器架构、多语言支持。
* [02. Jupyter 生态架构总览](02-ecosystem-architecture.md) — 生态全景图（User Interfaces / Core Applications / Kernels / Deployment / Building Blocks）、各层项目介绍、与相关项目关系。
* [03. jupyter 命令与子命令发现](03-jupyter-command.md) — jupyter 命令行入口、子命令发现机制、核心命令（notebook/lab/console/nbconvert等）、扩展子命令、通用选项。
* [04. Jupyter 通用配置系统](04-config-system.md) — traitlets 配置框架、Python 配置文件语法、命令行覆盖配置、集合类型配置方法、搜索路径优先级、密码设置。
* [05. 目录结构与文件位置](05-directories.md) — Config/Data/Runtime 三类文件分离、各平台默认路径、环境变量覆盖、搜索路径机制、kernelspec 位置、连接文件。

## 核心架构篇（06-08）

* [06. Kernel 架构](06-kernel-architecture.md) — IPython 内核角色、ipykernel 包装机制、三种内核开发模式（Wrapper/Native/Xeus）、多前端连接、内核生命周期、kernelspec 结构、ZMQ 五通道通信。
* [07. Notebook 文件格式（.ipynb）](07-notebook-format.md) — .ipynb JSON 结构、nbformat v4 规范、Markdown/Code/Raw 单元格类型、输出类型（stream/display_data/execute_result/error）、NotebookNode 对象、信任签名机制。
* [08. 客户端-服务器架构详解](08-client-server.md) — 三角色模型（前端/Server/Kernel）、Jupyter Server 枢纽角色、ZeroMQ 五通道通信模型、消息格式、WebSocket 代理机制、REST API、安全认证。

## 交互与输出篇（09-10）

* [09. 交互式控件与富显示（ipywidgets）](09-widgets-display.md) — ipywidgets 模型-视图-同步架构、Comm 通道、基础控件使用、富显示协议（_repr_*_ 方法）、MIME 类型映射、第三方 Widget 生态、Voilà。
* [10. Notebook 作为文档与转换（nbconvert）](10-notebook-doc-convert.md) — Literate Computing 理念、nbconvert 六阶段流程、支持的输出格式、Exporter 与 Jinja2 模板系统、Preprocessor 预处理链、单元格标签控制、papermill 参数化。

## 部署与管理篇（11-12）

* [11. JupyterHub 多用户部署](11-jupyterhub.md) — JupyterHub 四个核心子系统（Hub/Proxy/Authenticator/Spawner）、用户登录流程、四种部署模式（TLJH/Docker/Z2JH/HPC）、用户隔离与资源管理。
* [12. 安装与环境管理](12-installation.md) — pip/conda/mamba 安装方法、虚拟环境与 Jupyter 的关系、多 Kernel 工作流、ipykernel install 命令、常见安装问题排查、升级与验证。

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-what-is-jupyter
02-ecosystem-architecture
03-jupyter-command
04-config-system
05-directories
06-kernel-architecture
07-notebook-format
08-client-server
09-widgets-display
10-notebook-doc-convert
11-jupyterhub
12-installation
```
