# 概念文档索引

本目录包含 jupyterlab-git 扩展的核心概念文档，从入门到进阶系统讲解架构与实现机制。

## 入门部分

| 文档 | 说明 |
|------|------|
| [扩展简介](00-introduction.md) | jupyterlab-git是什么、核心功能、技术栈、版本信息 |
| [安装与快速上手](01-getting-started.md) | 安装方法、系统要求、首次使用、基本工作流 |
| [架构总览](02-architecture-overview.md) | 三层架构、前后端分离、数据流、核心模块关系 |

## 核心部分

| 文档 | 说明 |
|------|------|
| [插件系统与五个Plugin](03-extension-plugin-system.md) | JupyterFrontEndPlugin机制、5个插件的作用与依赖 |
| [GitExtension核心模型](04-git-extension-model.md) | IGitExtension接口、GitExtension实现、状态管理、方法概览 |
| [REST API通信机制](05-rest-api-and-communication.md) | 前后端HTTP通信、API端点列表、错误处理、版本校验 |
| [可插拔Diff系统](06-diff-provider-system.md) | Diff Provider注册机制、三种内置Provider、自定义扩展点 |

## 进阶部分

| 文档 | 说明 |
|------|------|
| [UI组件与Widget](07-ui-components-and-widgets.md) | GitWidget、React组件树、MUI组件、虚拟滚动 |
| [服务端Git执行引擎](08-server-git-execution.md) | execute()双模式、全局锁、pexpect认证、nbdime集成 |
| [轮询与信号系统](09-polling-and-signals.md) | Poll轮询机制、Lumino Signal事件、刷新链路、路径同步 |
| [命令系统与菜单](10-commands-and-menu.md) | CommandIDs枚举、命令注册、主菜单/右键菜单/命令面板 |
| [配置系统](11-configuration-and-settings.md) | 前端设置、后端traitlets配置、版本校验、.gitignore管理 |
| [Stash与高级操作](12-stash-and-advanced.md) | Stash/Rebase/Merge/Tag/Submodule/SSH/凭证处理等高级功能 |

## 阅读路径建议

1. **初学者**：00 → 01 → 02 → 04（先了解是什么、怎么用、整体结构、核心模型）
2. **前端开发者**：03 → 04 → 06 → 07 → 09 → 10（重点看前端插件系统、UI组件、信号轮询、命令菜单）
3. **后端开发者**：05 → 08 → 11（重点看REST API、Git执行引擎、配置系统）
4. **扩展开发者**：03 → 06 → 05 → 10（重点看插件注册、Diff Provider扩展、API调用、命令注册）
