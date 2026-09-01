---
type: Concept
title: jupyter_server_terminals 简介
description: 什么是 jupyter_server_terminals——Jupyter Server 的终端扩展，为 Notebook/Lab 提供 Web 终端能力
tags: [jupyter, terminals, introduction, extension]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T06:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T07:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jst-source
    resource: /references/jupyter-server-terminals-source.md
---

# jupyter_server_terminals 简介

## 什么是 jupyter_server_terminals

**jupyter_server_terminals** 是 Jupyter Server 的一个官方扩展（extension），为 Jupyter 环境（JupyterLab、Notebook 等）提供基于浏览器的交互式终端（Web Terminal）能力。它允许用户在 Jupyter 界面中打开一个完整的系统 Shell（Bash/PowerShell 等），直接在运行 Jupyter Server 的机器上执行命令。

简单来说，当你在 JupyterLab 中点击 "File → New → Terminal" 打开一个终端标签页时，背后负责创建 Shell 进程、管理终端会话、通过 WebSocket 传输输入输出的，就是这个扩展。

## 与 terminado 的关系

jupyter_server_terminals 的核心终端能力**并非自己实现**，而是建立在 [terminado](https://github.com/jupyter/terminado) 库之上：

- **terminado** 负责底层 PTY（伪终端）管理、进程派生、终端 I/O、WebSocket 协议处理
- **jupyter_server_terminals** 负责将 terminado 集成到 Jupyter Server 生态中，提供：
  - Jupyter Server 扩展生命周期管理（ExtensionApp）
  - Jupyter 认证授权集成
  - REST API（创建/列表/删除终端）
  - 配置系统（Shell 命令、自动清理等）
  - Prometheus 指标
  - 活动追踪与闲置终端自动清理

这种"薄层扩展"架构意味着：如果你想理解终端如何与浏览器通信，需要看 terminado 的源码；如果你想理解 Jupyter 如何管理终端配置和权限，则看 jupyter_server_terminals。

## 核心能力

jupyter_server_terminals 提供以下核心功能：

1. **终端生命周期管理**：创建、查询、列出、删除终端会话
2. **REST API**：标准化的 HTTP 接口管理终端
3. **WebSocket 通信**：实时双向通信传输终端输入输出
4. **认证授权**：集成 Jupyter Server 的安全体系，所有操作需认证
5. **自动清理（Culling）**：可配置的闲置终端超时自动回收
6. **Shell 配置**：支持自定义 Shell 命令、跨平台默认 Shell、Login Shell 模式
7. **活动监控**：Prometheus 指标 + 最后活动时间戳追踪
8. **工作目录控制**：创建终端时可指定初始工作目录（cwd）

## 在 Jupyter 生态中的位置

jupyter_server_terminals 是 Jupyter Server 2.0+ 的独立扩展包。在 Jupyter Server 1.x 时代，终端功能是内置的；2.0 版本将终端功能拆分为独立扩展，使核心 Server 更精简，终端功能可独立迭代。

```
┌─────────────────────────────────────┐
│         JupyterLab / Notebook       │  前端界面
├─────────────────────────────────────┤
│           Jupyter Server            │  核心服务
│  ┌───────────────────────────────┐  │
│  │   jupyter_server_terminals    │  │  本扩展
│  │  ┌─────────────────────────┐  │  │
│  │  │       terminado        │  │  │  底层终端库
│  │  │  (PTY / WebSocket /    │  │  │
│  │  │   进程管理)            │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## 安装与启用

该扩展通常作为 JupyterLab 或 Notebook 的依赖自动安装。手动安装：

```bash
pip install jupyter_server_terminals
```

安装后，通过自动配置文件 `jupyter_server_terminals.json` 默认启用，无需手动配置。你可以通过 Jupyter Server 配置禁用：

```python
# jupyter_server_config.py
c.ServerApp.terminals_enabled = False
```

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [TerminalsExtensionApp 扩展应用](02-extension-app.md)
- [TerminalManager 终端管理器](03-terminal-manager.md)
- [jupyter_server_terminals 源码信源登记](../references/jupyter-server-terminals-source.md)

[^jst-source]: jupyter_server_terminals 源码信源，见 [jupyter-server-terminals-source.md](../references/jupyter-server-terminals-source.md)。
