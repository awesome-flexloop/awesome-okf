---
type: Concept
title: JupyterLab Desktop 简介
description: JupyterLab Desktop 是基于 Electron 的跨平台 JupyterLab 桌面应用，提供本地 Python 环境管理、一键启动服务器、多窗口会话等桌面体验
tags: [introduction, overview, jupyterlab, electron, desktop]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: main-source
    resource: /references/main-source.md
    title: 应用入口源码信源
  - id: app-source
    resource: /references/app-source.md
    title: 主应用类源码信源
---

# JupyterLab Desktop 简介

## 什么是 JupyterLab Desktop

JupyterLab Desktop 是 Jupyter 官方团队推出的跨平台桌面应用，将 JupyterLab 集成到 Electron 外壳中，为数据科学家和开发者提供开箱即用的 Notebook 开发环境。它解决了传统 JupyterLab 使用中的几个痛点：

- **无需手动配置 Python 环境**：内置捆绑 Python 环境（bundled environment），安装即可使用
- **多环境管理**：支持 Conda、venv、系统 Python 等多种环境类型，可在 GUI 中切换
- **多窗口多会话**：每个工作目录/项目可独立窗口运行，互不干扰
- **服务器自动管理**：自动启动/停止 Jupyter Server，无需手动运行 `jupyter lab` 命令
- **远程服务器连接**：支持连接到已有的远程 Jupyter Server

## 核心特性

| 特性 | 说明 |
|------|------|
| 捆绑 Python 环境 | 安装包内置 Conda 环境，开箱即用 |
| 环境自动发现 | 自动扫描 PATH、Conda 目录、Windows 注册表中的 Python 环境 |
| Factory 模式 | 预创建空闲 Jupyter Server，加速窗口打开 |
| 工作区设置 | 支持每个项目目录独立的 `.jupyter/desktop-settings.json` 配置 |
| CLI 命令 | `jlab` 命令支持从终端打开文件/目录、管理环境 |
| 自动更新 | macOS 使用 Squirrel 自动更新，其他平台通过 GitHub Releases 检查 |
| 单实例锁 | 确保只有一个应用实例运行，避免端口冲突 |
| 跨平台 | 支持 Windows、macOS、Linux（含 Snap 包） |

## 技术栈

| 层 | 技术 | 版本参考 |
|----|------|---------|
| 桌面框架 | Electron | 42.x |
| UI 渲染 | JupyterLab (Web) | 4.x |
| 主进程语言 | TypeScript | 编译为 Node.js |
| 服务器管理 | Jupyter Server | Python subprocess |
| 包管理 | conda / pip | 通过 CLI 调用 |
| 打包 | electron-builder | 26.x |
| 日志 | electron-log | 写入文件 |
| 信号机制 | @lumino/signaling | 模块间事件通信 |

## 应用架构总览

JupyterLab Desktop 采用经典的 Electron 架构，分为主进程和渲染进程：

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron 主进程 (Node.js)                │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │JupyterApplication│ │SessionWindowManager│ │ JupyterServerFactory │  │
│  │  (主控制器)   │  │  (窗口管理)   │  │  (服务器池管理)    │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬──────────┘  │
│         │                 │                    │             │
│  ┌──────┴───────┐  ┌─────┴────────┐  ┌───────┴──────────┐  │
│  │  Registry    │  │ SessionWindow│  │  JupyterServer   │  │
│  │ (环境注册表)  │  │  (单窗口)    │  │  (单服务器实例)   │  │
│  └──────────────┘  └──────┬───────┘  └───────┬──────────┘  │
│                           │                   │             │
│                    ┌──────┴───────┐    ┌─────┴─────┐       │
│                    │ TitleBarView │    │ Python    │       │
│                    │ WelcomeView  │    │ subprocess│       │
│                    │ LabView      │    └───────────┘       │
│                    │ Dialog Views │                         │
│                    └──────────────┘                         │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ EventManager │  │ UserSettings │  │  ApplicationData │  │
│  │  (IPC事件)   │  │  (全局设置)  │  │   (持久化数据)   │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │ IPC (ipcMain/ipcRenderer)
┌────────┴────────────────────────────────────────────────────┐
│                   渲染进程 (Chromium)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ TitleBar HTML│  │ Welcome Page │  │   JupyterLab UI  │  │
│  │ (自定义标题栏)│  │ (欢迎页面)   │  │  (Notebook编辑)  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 版本与要求

- **最低 jupyterlab 版本**：3.0.0（Python 环境必须满足）
- **Node.js**：用于开发构建
- **Python**：服务器端运行 JupyterLab

## 下一篇

- [架构概览](/concepts/01-architecture-overview.md) - 深入了解核心模块与数据流
- [应用入口与生命周期](/concepts/02-app-entry-lifecycle.md) - 了解应用启动流程

## 相关概念

- [架构概览](/concepts/01-architecture-overview.md) — 了解核心模块架构、依赖关系与数据流
- [应用入口与生命周期](/concepts/02-app-entry-lifecycle.md) — 掌握从进程启动到应用就绪的完整流程
