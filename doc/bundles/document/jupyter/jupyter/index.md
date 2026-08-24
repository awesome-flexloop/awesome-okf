---
type: "index"
title: "Jupyter 交互式计算教程"
description: "Jupyter 1.2.0.dev0 源码学习教程——从元包架构到多用户部署的系统化知识，结合官方文档的实战教程"
tags: [jupyter, notebook, ipython, interactive-computing, data-science]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T11:45:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00+08:00" }
status: active
stale_after: 2027-08-22
sources:
  - { id: jupyter-metasource, resource: "references/jupyter-metasource.md", title: "Jupyter 元包源码信源登记" }
  - { id: jupyter-docs, resource: "https://docs.jupyter.org/", title: "Jupyter 官方文档" }
  - { id: jupyter-protocol, resource: "https://jupyter-client.readthedocs.io/en/latest/messaging.html", title: "Jupyter Protocol 规范" }
---

# Jupyter 交互式计算教程

> 基于 Jupyter 1.2.0.dev0 源码（BSD-3-Clause）+ 官方文档的系统化学习教程

Jupyter 是 Project Jupyter 的元包（metapackage），作为安装入口点一键安装 Notebook、JupyterLab、nbconvert、ipykernel、ipywidgets 等核心组件。Jupyter 项目开创了 Literate Computing（文学化计算）范式，让代码、叙述文本、可视化结果和交互控件在同一文档中共存，是数据科学、科学研究、教学和技术写作的事实标准工具。

本教程从 jupyter/jupyter 元包源码出发，系统讲解 Jupyter 的核心架构（Kernel、C/S 通信、Notebook 格式、配置系统），同时覆盖日常使用、环境管理、交互式控件、文档转换和多用户部署等全部场景。

## 快速导航

### 入门

| 文档 | 说明 |
|------|------|
| [Jupyter 元包与核心组件](concepts/00-introduction.md) | 元包定位、五大核心依赖、学习路径 |
| [什么是计算笔记本与核心架构](concepts/01-what-is-jupyter.md) | Literate Computing、REPL、Kernel 抽象、C/S 架构 |
| [Jupyter 生态架构总览](concepts/02-ecosystem-architecture.md) | 五层生态全景（UI/Apps/Kernels/Deployment/Building Blocks） |
| [安装与环境管理](concepts/12-installation.md) | pip/conda 安装、虚拟环境与 Kernel 关系、常见问题 |

### 核心架构

| 文档 | 说明 |
|------|------|
| [jupyter 命令与子命令发现](concepts/03-jupyter-command.md) | jupyter CLI 入口、子命令机制、核心命令、通用选项 |
| [Jupyter 通用配置系统](concepts/04-config-system.md) | traitlets 配置、Python 配置文件、命令行覆盖、搜索路径 |
| [目录结构与文件位置](concepts/05-directories.md) | Config/Data/Runtime 三类文件分离、各平台路径、环境变量 |
| [Kernel 架构](concepts/06-kernel-architecture.md) | IPython/ipykernel、三种内核开发模式、Kernel 生命周期、kernelspec |
| [Notebook 文件格式](concepts/07-notebook-format.md) | .ipynb JSON 结构、单元格类型、输出类型、nbformat API、信任签名 |
| [客户端-服务器架构详解](concepts/08-client-server.md) | 三角色模型、ZMQ 五通道、消息格式、WebSocket 代理、REST API |

### 交互与输出

| 文档 | 说明 |
|------|------|
| [交互式控件与富显示（ipywidgets）](concepts/09-widgets-display.md) | Widget 架构、interact 装饰器、富显示协议、第三方 Widget 生态、Voilà |
| [Notebook 作为文档与转换（nbconvert）](concepts/10-notebook-doc-convert.md) | nbconvert 六阶段流程、输出格式、模板系统、Preprocessor、papermill |

### 部署与管理

| 文档 | 说明 |
|------|------|
| [JupyterHub 多用户部署](concepts/11-jupyterhub.md) | Hub/Proxy/Authenticator/Spawner 四组件、TLJH/Docker/Z2JH/HPC 部署模式 |

### 实战示例

| 示例 | 说明 |
|------|------|
| [创建你的第一个 Jupyter Notebook](examples/01-first-notebook.md) | 启动 JupyterLab、创建/执行 Notebook、Markdown、魔法命令、快捷键 |
| [Jupyter 配置基础操作](examples/02-config-basics.md) | 生成配置文件、修改常用配置、密码认证、命令行覆盖 |
| [多环境 Kernel 管理](examples/03-multi-env-kernels.md) | 一个 JupyterLab + 多个项目 Kernel、venv/conda 注册切换、问题排查 |
| [使用 ipywidgets 构建交互式 Notebook](examples/04-widgets-interact.md) | 滑块/按钮/下拉控件、交互式可视化、事件回调、布局组织、Voilà |
| [nbconvert 自动化转换与报告生成](examples/05-nbconvert-automation.md) | HTML/PDF/Markdown 转换、执行后转换、papermill 参数化、CI/CD 集成 |

### 信源登记簿

* [参考资料索引](references/index.md) — 源码信源登记、官方文档链接、协议规范链接

## 学习路径建议

**新手上路（第一次使用 Jupyter）**：
```
00 → 01 → 12（安装）→ examples/01（第一个Notebook）→ examples/02（配置）
```

**日常使用者路径（数据科学/分析）**：
```
01 → examples/01 → 04（配置）→ 05（目录结构）→ examples/03（多环境Kernel）
  → 09（Widgets交互）→ examples/04（控件实战）→ 10（文档转换）→ examples/05（自动化报告）
```

**架构理解路径（源码/内核开发者）**：
```
00 → 02（生态全景）→ 03（命令系统）→ 04（配置）→ 05（目录）
  → 06（Kernel架构）→ 07（文件格式）→ 08（C/S架构）
  → 09（Widget架构）→ 10（nbconvert架构）
```

**运维/部署路径（团队/平台）**：
```
01 → 02 → 04（配置）→ 05（目录）→ 11（JupyterHub）→ examples/02（密码/安全配置）
```

## 源码版本

本教程基于 Jupyter **1.2.0.dev0**（元包开发版本），源码路径：`external/libs/jupyter/jupyter/`。文档部分基于 [Jupyter 官方文档](https://docs.jupyter.org/) 及各子项目文档（ipykernel、nbformat、nbconvert、ipywidgets、jupyter-server、jupyterhub 等）。

- 许可证：BSD-3-Clause
- Python 要求：≥ 3.7
- 核心依赖（install_requires）：notebook、nbconvert、ipykernel、ipywidgets、jupyterlab
- 文档系统：Sphinx + MyST Markdown（pydata_sphinx_theme）
- 注意事项：jupyter/jupyter 本身是元包，不含 Python 源代码；核心实现分布在各子项目中

```{toctree}
:hidden:

concepts/index
examples/index
references/index
facts
insights
log
```
