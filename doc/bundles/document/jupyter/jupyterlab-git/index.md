---
okf_version: "0.2"
type: Bundle
title: jupyterlab-git OKF Wiki
description: JupyterLab Git版本控制扩展的完整知识文档，涵盖前后端架构、插件系统、Diff机制、命令系统和高级操作
---

# jupyterlab-git

jupyterlab-git 是 JupyterLab 官方的 Git 版本控制扩展，在 JupyterLab 左侧面板提供完整的 Git GUI 操作界面，支持提交、推送、拉取、分支管理、文件 Diff、Stash 等常见 Git 操作。

**版本**：0.54.1  
**许可证**：BSD-3-Clause  
**仓库**：https://github.com/jupyterlab/jupyterlab-git

## 核心特性

- **完整 Git 工作流**：支持 add/commit/push/pull/branch/merge/stash 等标准 Git 操作
- **可视化 Diff**：内置三种 Diff Provider（Notebook 单元格级 diff、图片 diff、纯文本 CodeMirror 高亮 diff）
- **Notebook 友好**：集成 nbdime 进行 Notebook 语义 diff，支持清除输出后提交
- **双端架构**：前端 TypeScript+React+MUI，后端 Python+Tornado 通过 REST API 通信
- **可扩展设计**：Token 依赖注入、可插拔 Diff Provider、命令系统支持自定义扩展
- **实时状态**：Lumino Poll 轮询自动刷新状态，Signal 事件驱动 UI 更新
- **认证支持**：支持 Username/Password 密码认证、SSH known_hosts 管理、凭证缓存

## 文档索引

### 概念文档（Concepts）

| 文档 | 说明 |
|---|---|
| [扩展简介](concepts/00-introduction.md) | 功能概览、技术栈、版本依赖 |
| [安装与快速上手](concepts/01-getting-started.md) | 安装方法、系统要求、首次使用 |
| [架构总览](concepts/02-architecture-overview.md) | 三层架构、前后端分离、数据流、核心模块 |
| [插件系统与五个Plugin](concepts/03-extension-plugin-system.md) | JupyterFrontEndPlugin 机制、5个插件作用与依赖 |
| [GitExtension核心模型](concepts/04-git-extension-model.md) | IGitExtension 接口、GitExtension 实现、状态管理 |
| [REST API通信机制](concepts/05-rest-api-and-communication.md) | HTTP 通信、API 端点、错误处理、版本校验 |
| [可插拔Diff系统](concepts/06-diff-provider-system.md) | Diff Provider 注册、三种内置 Provider、扩展点 |
| [UI组件与Widget](concepts/07-ui-components-and-widgets.md) | GitWidget、React 组件树、MUI 组件、虚拟滚动 |
| [服务端Git执行引擎](concepts/08-server-git-execution.md) | execute() 双模式、全局锁、pexpect 认证、nbdime 集成 |
| [轮询与信号系统](concepts/09-polling-and-signals.md) | Poll 轮询、Signal 事件、刷新链路、路径同步 |
| [命令系统与菜单](concepts/10-commands-and-menu.md) | CommandIDs 枚举、命令注册、菜单/快捷键绑定 |
| [配置系统](concepts/11-configuration-and-settings.md) | 前端设置、后端 traitlets 配置、版本校验 |
| [Stash与高级操作](concepts/12-stash-and-advanced.md) | Stash/Rebase/Merge/Tag/SSH/凭证等高级功能 |

### 源码信源（References）

| 文档 | 说明 |
|---|---|
| [插件入口](references/index-ts-source.md) | src/index.ts — 5个Plugin定义、activate生命周期 |
| [Token与类型定义](references/tokens-ts-source.md) | src/tokens.ts — IGitExtension接口、类型定义、命令ID |
| [GitExtension核心模型](references/model-ts-source.md) | src/model.ts — GitExtension类实现、轮询、任务队列 |
| [Python Git执行引擎](references/git-py-source.md) | packages/core/git.py — Git类、execute函数、subprocess/pexpect |
| [Tornado处理器](references/handlers-py-source.md) | packages/jupyterlab/handlers.py — /git/* REST API处理器 |
| [服务端扩展入口](references/init-py-source.md) | packages/jupyterlab/__init__.py — 配置类、extension加载 |

### 示例（Examples）

| 文档 | 说明 |
|---|---|
| [基础使用示例](examples/01-basic-usage.md) | 安装→克隆→暂存→提交→推送→拉取的完整基础流程 |
| [分支管理与合并工作流](examples/02-branch-merge-workflow.md) | 创建分支→切换→开发→合并→冲突解决→变基的工作流 |
| [Diff查看与Stash使用](examples/03-diff-and-stash.md) | 文件Diff查看、提交历史Diff、Stash储藏/应用/弹出 |

## 快速开始

1. 阅读[扩展简介](concepts/00-introduction.md)了解功能概览
2. 按照[安装与快速上手](concepts/01-getting-started.md)安装并启动扩展
3. 参考[基础使用示例](examples/01-basic-usage.md)完成第一次 Git 操作
4. 阅读[架构总览](concepts/02-architecture-overview.md)理解系统设计
5. 通过[插件系统](concepts/03-extension-plugin-system.md)学习扩展开发

## 源码结构

```
jupyterlab-git/
├── src/                          # 前端 TypeScript 源码
│   ├── index.ts                  # 插件入口（5个Plugin定义）
│   ├── tokens.ts                 # Token、接口、命令ID定义
│   ├── model.ts                  # GitExtension 核心模型
│   ├── git.ts                    # HTTP 请求工具函数
│   ├── components/               # React UI 组件
│   │   ├── GitPanel.tsx          # 主面板
│   │   ├── FileList.tsx          # 文件列表（虚拟滚动）
│   │   ├── HistorySideBar.tsx    # 提交历史
│   │   ├── CommitBox.tsx         # 提交输入框
│   │   ├── BranchMenu.tsx        # 分支菜单
│   │   ├── diffs/                # Diff Provider 组件
│   │   └── style/                # CSS-in-JS 样式
│   ├── commandsAndMenu.tsx       # 命令注册与菜单
│   ├── codecoverage/             # 代码覆盖率工具
│   ├── contexts/                 # GitContext React Context
│   ├── hooks/                    # React Hooks
│   ├── store/                    # Redux 状态管理
│   ├── utils.ts                  # 工具函数（decodeStage等）
│   └── widgets/                  # Lumino Widget 封装
├── packages/
│   ├── core/
│   │   └── jupyterlab_git_core/  # Python 核心包（Git执行+前端静态资源）
│   │       ├── git.py            # Git 命令执行引擎
│   │       ├── ssh.py            # SSH known_hosts 管理
│   │       └── labextension/     # 构建后的前端静态资源
│   └── jupyterlab/
│       └── jupyterlab_git/       # Python 服务端包（Tornado handlers）
│           ├── __init__.py       # 扩展入口、配置类
│           └── handlers.py       # REST API 处理器
├── schema/
│   └── plugin.json               # JupyterLab 设置 Schema
├── style/                        # 全局 CSS 样式
└── package.json                  # NPM 包配置
```

```{toctree}
:hidden:

concepts/index
examples/index
references/index
facts
insights
log
```
