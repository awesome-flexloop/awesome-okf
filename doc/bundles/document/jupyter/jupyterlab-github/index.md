---
okf_version: "0.2"
type: bundle
title: "jupyterlab-github"
description: "JupyterLab GitHub 浏览器扩展——通过 Contents.IDrive 接口将 GitHub 仓库映射为只读虚拟文件系统，支持在 JupyterLab 中直接浏览、打开和运行 GitHub 仓库中的 Notebook 和文件。"
---

# jupyterlab-github

> JupyterLab 官方 GitHub 浏览器扩展：在左侧面板直接浏览 GitHub 仓库、打开 Notebook 并运行，支持 MyBinder 一键启动。

`jupyterlab-github` 是 JupyterLab 的官方扩展，通过实现 JupyterLab 的 `Contents.IDrive` 接口，将 GitHub 仓库映射为一个只读虚拟文件系统。用户无需离开 JupyterLab 即可浏览 GitHub 上的公开（或私有）仓库、打开 Notebook 并在本地 Kernel 中运行代码、一键在 MyBinder 上启动仓库环境。

## 快速导航

### 📘 核心概念（7 篇）

**入门**
- [简介](concepts/00-introduction.md) — 扩展定位、只读设计、双组件架构概览、项目信息
- [安装与快速上手](concepts/01-getting-started.md) — pip 安装、Token 获取、启动浏览、速率限制说明

**核心**
- [架构总览](concepts/02-architecture-overview.md) — 四层架构、Contents.IDrive 模式、代理模式、数据流
- [GitHubDrive 虚拟文件系统](concepts/03-github-drive.md) — Drive 类详解、路径解析、四级导航、大文件降级、格式转换
- [浏览器 UI 组件与交互](concepts/04-browser-ui.md) — 三个 Lumino 控件、工具栏按钮、MyBinder 集成、事件防循环

**进阶**
- [服务端代理与认证](concepts/05-server-proxy.md) — Tornado 代理处理器、Token 优先级、分页聚合、安全机制
- [配置与设置系统](concepts/06-configuration.md) — 前端设置 Schema、服务端 traitlets 配置、GitHub Enterprise、SSL 配置
- [概念文档索引](concepts/index.md) — 概念文档总目录

### 💻 示例代码（2 个）

- [基础浏览：浏览 GitHub 仓库](examples/01-basic-browsing.md) — 打开浏览器、输入用户名、浏览仓库、打开 Notebook、使用工具栏
- [配置认证：避免速率限制](examples/02-setup-authentication.md) — 服务端/客户端 Token 配置、GHE 部署、验证方法
- [示例文档索引](examples/index.md) — 示例总目录

### 📄 源码信源（5 个文件）

- [插件入口 src/index.ts](references/index-ts-source.md) — 插件注册、激活函数、设置集成
- [API 请求层 src/github.ts](references/github-ts-source.md) — 请求函数、TypeScript 类型定义
- [GitHub Drive src/contents.ts](references/contents-ts-source.md) — Drive 核心实现、路径解析、API 路由、格式转换
- [浏览器 UI src/browser.ts](references/browser-ts-source.md) — 控件实现、工具栏、Binder 集成
- [服务端 jupyterlab_github/\_\_init\_\_.py](references/init-py-source.md) — Tornado 代理、配置类、认证分页
- [源码信源索引](references/index.md) — 信源文档总目录

## 版本信息

| 属性 | 值 |
|------|-----|
| 版本 | **v4.0.0** |
| JupyterLab 要求 | ≥ 4.0.0, < 5 |
| Python 要求 | ≥ 3.8 |
| 构建系统 | Hatchling + hatch-jupyter-builder |
| 前端依赖 | @jupyterlab/application, @jupyterlab/apputils, @jupyterlab/filebrowser, @lumino/widgets 等 |
| 后端依赖 | jupyterlab≥4.0.0, tornado, traitlets |
| 许可证 | BSD-3-Clause |
| 作者 | Ian Rose |
| 仓库 | https://github.com/jupyterlab/jupyterlab-github |
| 源码路径 | `external/libs/jupyter/jupyterlab-github/` |

## 核心特点

| 特点 | 说明 |
|------|------|
| **只读浏览** | 专注于浏览和打开文件，不做写入操作（save/delete/rename 全部拒绝） |
| **双模式请求** | 自动检测服务端扩展，代理可用时走认证代理，不可用时直连 GitHub API |
| **速率限制防护** | 5分钟刷新间隔、服务端 Token 代理、限流状态可观察 |
| **大文件支持** | >1MB 文件自动降级到 Git Blob API 获取 |
| **MyBinder 集成** | 自动检测 Binder 配置文件，一键在 Binder 上启动仓库 |
| **GHE 支持** | 通过 api_url 配置支持 GitHub Enterprise 私有部署 |

---

**推荐阅读顺序：** [简介](concepts/00-introduction.md) → [安装与快速上手](concepts/01-getting-started.md) → [架构总览](concepts/02-architecture-overview.md) → [GitHubDrive 虚拟文件系统](concepts/03-github-drive.md) → [浏览器 UI](concepts/04-browser-ui.md)
