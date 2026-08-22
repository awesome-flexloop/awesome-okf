---
okf_version: "0.2"
type: group
title: "📓 Jupyter 数据科学生态"
description: "Jupyter 交互式计算生态——协议、格式、应用与部署"
---

# 📓 Jupyter 数据科学生态

Jupyter 是数据科学与交互式计算的核心平台，从底层的 ZeroMQ 通信协议到顶层的 Docker 部署镜像与自动化运维工具，形成完整的技术栈。本组按 **协议层 → 格式层 → 应用层 → 部署层 → 自动化层** 的架构层次组织。

## 学习路径

### 入口层：元包与生态总览

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 0 | [jupyter](jupyter/index.md) | Jupyter 元包——一站式安装入口（notebook/jupyterlab/nbconvert/ipykernel/ipywidgets）、配置系统、目录规范、Kernel 架构、.ipynb 文件格式、C/S 通信模型、ipywidgets 交互控件、nbconvert 转换、JupyterHub 多用户部署（v1.2.0.dev0） |

### 协议层：内核通信基础

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 1 | [jupyter-client](jupyter-client/README.md) | Jupyter 协议客户端——ZMQ 五通道通信（Shell/IO/Stdin/Control/HB）、内核生命周期管理、会话与消息签名、KernelManager/AsyncKernelManager、多内核并行（v8.9.1，协议 v5.4） |

### 格式层：数据模型

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 2 | [nbformat](nbformat/index.md) | Notebook 文件格式——NotebookNode 数据模型、v4 JSON 格式、读写 API、验证器、信任签名机制、版本迁移 |

### 应用层：用户交互

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 3 | [jupyter-notebook](jupyter-notebook/index.md) | Jupyter Notebook v7——基于 JupyterLab 的后端 App、前端 Shell、Handler 体系、Shim 兼容层、前后端扩展系统 |

### 部署层：容器化运行

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 4 | [jupyter-docker-stacks](jupyter-docker-stacks/index.md) | Jupyter 官方 Docker 镜像——镜像层级体系（base→minimal→scipy→专业栈）、启动生命周期、Hook 自定义、用户权限、GPU 支持、CI/CD 构建 |
| 5 | [cookiecutter-docker-stacks](cookiecutter-docker-stacks/index.md) | Jupyter Docker 镜像模板生成器——一键生成包含 Dockerfile/pytest测试/CI/CD/DevContainer 的自定义镜像项目，14个基础镜像预设、TrackedContainer测试框架、GitHub Actions自动发布 |

### 自动化层：社区运营工具

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 6 | [pr-triage-board-bot](pr-triage-board-bot/index.md) | PR分类看板机器人——基于GitHub App和Project V2 GraphQL API，按7个维度（作者类型/变更规模/CI状态/审批状态/合并冲突/维护者参与度/创建时间）自动分类同步开放PR，每小时对账更新，TypeScript实现 |

### 治理层：社区治理与决策机制

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 7 | [governance](governance/index.md) | Jupyter 治理模型——EC/SSC/Foundation三主体架构、共识寻求+投票兜底决策流程、子项目自治体系、常设委员会与工作组（DEI/CoC/社区建设）、排序复选选举机制、商标许可与行为准则 |

### 文档工具层：文档生成与渲染

| 顺序 | 知识束 | 一句话简介 |
|------|--------|-----------|
| 8 | [papyri](papyri/index.md) | Python docstring→IR文档生成器——RST解析为类型化中间表示(IR)，三端架构(Python gen/TypeScript ingest/Astro viewer)，跨包交叉引用，CBOR确定性打包，交互式文档浏览 |
