---
type: OKFWiki
title: JupyterLab Extension Examples 教程
description: 基于jupyterlab/extension-examples源码的JupyterLab 4.x扩展开发教程，覆盖从入门到进阶的核心扩展点
tags: [jupyterlab, extension, typescript, python, lumino, plugin-development]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
source_repo: "https://github.com/jupyterlab/extension-examples"
target_jupyterlab: ">=4.0,<5"
---

# JupyterLab Extension Examples 教程

基于官方 [jupyterlab/extension-examples](https://github.com/jupyterlab/extension-examples) 仓库源码分析的JupyterLab 4.x扩展开发教程。通过28个官方示例系统学习JupyterLab扩展开发的核心概念和API。

## 快速开始

- **零基础入门**：从 [concepts/00-introduction.md](concepts/00-introduction.md) 开始，按顺序阅读概念文档
- **直接上手**：从 [examples/01-hello-world.md](examples/01-hello-world.md) 开始，边做边学
- **API速查**：查阅 [references/core-api-tokens.md](references/core-api-tokens.md) 和 [references/plugin-anatomy.md](references/plugin-anatomy.md)

## 目录结构

```
extension-examples/
├── concepts/          # 概念文档（15篇，按学习路径排列）
│   ├── index.md
│   ├── 00-introduction.md
│   ├── 01-hello-world.md
│   ├── 02-project-setup.md
│   ├── 03-plugin-basics.md
│   ├── 04-commands.md
│   ├── 05-widgets-shell.md
│   ├── 06-signals.md
│   ├── 07-palette-launcher.md
│   ├── 08-menus-toolbars.md
│   ├── 09-settings-state.md
│   ├── 10-notifications-logging.md
│   ├── 11-kernel-interaction.md
│   ├── 12-documents.md
│   ├── 13-server-extension.md
│   └── 14-advanced-ui.md
├── examples/          # 实战示例（3个可运行示例）
│   ├── index.md
│   ├── 01-hello-world.md
│   ├── 02-commands-palette.md
│   └── 03-custom-widget.md
└── references/        # 参考资料
    ├── index.md
    ├── plugin-anatomy.md       # 插件结构解剖
    ├── core-api-tokens.md      # 核心Token API速查
    └── examples-index.md       # 28个官方示例索引
```

## 覆盖的扩展点

| 类别 | 覆盖内容 |
|------|---------|
| 基础 | 插件定义、依赖注入、生命周期、开发模式 |
| UI框架 | Lumino Widget、ReactWidget、MainAreaWidget、Shell区域 |
| 命令系统 | addCommand、execute、isVisible/isEnabled/isToggled、快捷键 |
| 菜单/工具栏 | 主菜单、右键菜单、Notebook工具栏、Cell工具栏 |
| 设置 | ISettingRegistry（JSON Schema）、IStateDB（状态持久化） |
| 文档 | 自定义文件类型、DocumentModel、WidgetFactory、Yjs协作 |
| Kernel | SessionContext、代码执行、IOPub消息、状态监听 |
| 服务端 | Python tornado APIHandler、ServerConnection |
| 高级 | DataGrid、主题、国际化、通知、日志面板、React集成 |

## 技术栈

- **TypeScript 5.x**：前端开发语言
- **React 18+**：可选的UI框架（原生Lumino也可）
- **Lumino**：JupyterLab底层UI框架（Widget、Signal、DataGrid）
- **Python 3.8+**：服务端扩展和包管理
- **hatchling**：Python构建后端
- **Yjs**：协作编辑底层

## 相关资源

- [JupyterLab官方文档](https://jupyterlab.readthedocs.io/)
- [extension-examples仓库](https://github.com/jupyterlab/extension-examples)
- [JupyterLab Extension Tutorial](https://jupyterlab.readthedocs.io/en/stable/extension/extension_tutorial.html)
- [Lumino文档](https://lumino.readthedocs.io/)

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
