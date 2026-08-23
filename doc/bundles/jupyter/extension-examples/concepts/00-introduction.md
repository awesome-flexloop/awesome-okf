---
type: Concept
title: JupyterLab 扩展开发入门
description: 了解JupyterLab扩展的基本概念、开发环境搭建和扩展能做什么，为后续学习奠定基础
tags: [jupyterlab, extension, introduction, getting-started]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: root-readme
    resource: /references/examples-index.md
    title: extension-examples 根README和示例索引
  - id: env-yml
    resource: /references/plugin-anatomy.md
    title: environment.yml 开发环境配置
---

## 什么是 JupyterLab 扩展

JupyterLab 扩展（Extension）是一种插件机制，允许开发者向 JupyterLab 添加新功能、自定义界面、集成外部工具。扩展基于 TypeScript/JavaScript 开发前端，必要时可搭配 Python 后端。

JupyterLab 4.x 的扩展系统建立在 **Lumino**（底层Widget库）和 **Token依赖注入** 之上，每个扩展是一个 `JupyterFrontEndPlugin` 对象，通过声明依赖 Token 获取 JupyterLab 核心服务。

## 扩展能做什么

通过官方28个示例可以看到，扩展覆盖以下能力：

- **添加命令**：注册可执行命令，绑定快捷键或菜单项
- **自定义Widget**：在主区域、侧边栏、顶部栏添加自定义UI组件
- **UI扩展点**：命令面板、Launcher、主菜单、右键菜单、工具栏
- **设置系统**：通过JSON Schema定义可配置项
- **状态持久化**：使用StateDB保存用户偏好
- **通知系统**：向用户发送成功/错误/进度通知
- **自定义文档类型**：创建新的文件类型，支持Yjs协同编辑
- **Kernel交互**：向Kernel发送代码执行请求，接收输出
- **MIME渲染器**：为特定MIME类型（如video/mp4）添加渲染器
- **CodeMirror扩展**：为编辑器添加语法高亮、斑马纹等功能
- **补全提供者**：自定义代码自动补全数据源
- **日志控制台**：创建自定义日志面板
- **React组件**：在扩展中使用React构建UI
- **后端API**：通过Tornado添加服务端HTTP接口
- **双兼容**：同一扩展同时支持JupyterLab和Jupyter Notebook v7+

## 开发环境要求

根据 `environment.yml`：

- **JupyterLab** >= 4.3.0
- **Node.js** 22
- **Python** 3
- **jlpm**（JupyterLab内置的yarn包管理器）
- **TypeScript** ~5.8.0

创建开发环境：

```bash
conda env create -f environment.yml
conda activate jupyterlab-extension-examples
```

## 快速开始流程

以hello-world为例，最小开发流程：

```bash
# 1. 进入示例目录
cd hello-world

# 2. 创建yarn.lock（Yarn 3工作区需要）
touch yarn.lock

# 3. 以可编辑模式安装Python包
pip install -e .

# 4. 将扩展链接到JupyterLab（开发模式）
jupyter labextension develop . --overwrite

# 5. 构建TypeScript
jlpm run build

# 6. 启动JupyterLab
jupyter lab
```

开发迭代模式（双终端）：

```bash
# 终端1：监听TypeScript变化自动重编译
jlpm watch

# 终端2：启动JupyterLab
jupyter lab
# 修改代码后刷新浏览器即可看到变化
```

## 技术栈概览

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端语言 | TypeScript | 所有扩展示例使用TypeScript |
| UI框架 | Lumino | JupyterLab底层Widget库，提供Widget生命周期、布局、消息传递 |
| 前端构建 | jlpm + @jupyterlab/builder | 基于webpack的扩展构建工具链 |
| 状态/事件 | Lumino Signals | 轻量级信号系统，用于Widget间通信 |
| 协同编辑 | Yjs + @jupyter/ydoc | 自定义文档类型使用Yjs CRDT实现实时协作 |
| 包管理 | hatchling + hatch-jupyter-builder | Python包构建，自动调用前端构建 |
| UI可选 | React | 可选使用React构建Widget（react-widget示例） |
| 编辑器 | CodeMirror 6 | JupyterLab 4.x使用CodeMirror 6作为编辑器 |
| 数据表格 | Lumino DataGrid | 高性能虚拟滚动表格 |
| 后端 | Jupyter Server + Tornado | 服务端扩展基于Tornado的APIHandler |

## Monorepo 结构

extension-examples 使用 Lerna 管理多包仓库：

- `lerna.json` 配置 npmClient 为 `jlpm`，version 为 `independent`
- 每个示例是独立的 npm 包和 Python 包
- 根目录的 `environment.yml` 定义统一的开发环境
- 可用 `jlpm build-ext` 一次性构建所有示例

## 相关概念

- [Hello World：最小插件](/concepts/01-hello-world.md)
- [项目结构与构建系统](/concepts/02-project-setup.md)
- [插件基础与依赖注入](/concepts/03-plugin-basics.md)
- [插件解剖结构参考](/references/plugin-anatomy.md)
