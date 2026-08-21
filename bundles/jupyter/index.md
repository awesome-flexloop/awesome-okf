---
okf_version: "0.2"
type: group
title: "📓 Jupyter 数据科学生态"
description: "Jupyter 交互式计算生态——协议、格式、应用与部署"
---

# 📓 Jupyter 数据科学生态

Jupyter 是数据科学与交互式计算的核心平台，从底层的 ZeroMQ 通信协议到顶层的 Docker 部署镜像，形成完整的技术栈。本组按 **协议层 → 格式层 → 应用层 → 部署层** 的架构层次组织。

## 学习路径

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
