# JupyterLab Extension Examples - Concepts

概念文档按学习路径排列，建议按顺序阅读。

## 入门阶段

| 编号 | 文档 | 说明 |
|------|------|------|
| 00 | [introduction.md](00-introduction.md) | JupyterLab扩展开发入门：什么是扩展、核心架构、技术栈、前置知识 |
| 01 | [hello-world.md](01-hello-world.md) | 第一个扩展：环境准备、Hello World、开发模式运行 |
| 02 | [project-setup.md](02-project-setup.md) | 项目结构与构建系统：目录布局、package.json、pyproject.toml、双构建系统 |
| 03 | [plugin-basics.md](03-plugin-basics.md) | 插件基础与依赖注入：JupyterFrontEndPlugin接口、Token机制、requires/optional/provides |

## 核心UI阶段

| 编号 | 文档 | 说明 |
|------|------|------|
| 04 | [commands.md](04-commands.md) | 命令系统：addCommand、execute、动态状态（isVisible/isEnabled/isToggled） |
| 05 | [widgets-shell.md](05-widgets-shell.md) | Widget与Shell布局：Lumino Widget生命周期、Shell区域、MainAreaWidget、WidgetTracker |
| 06 | [signals.md](06-signals.md) | 信号与事件通信：Signal的connect/emit/disconnect模式、Model→View通信 |
| 07 | [palette-launcher.md](07-palette-launcher.md) | 命令面板与Launcher：ICommandPalette.addItem、ILauncher.add、LabIcon |
| 08 | [menus-toolbars.md](08-menus-toolbars.md) | 菜单与工具栏：schema声明式、主菜单、右键菜单、Cell工具栏、对话框 |

## 数据与状态阶段

| 编号 | 文档 | 说明 |
|------|------|------|
| 09 | [settings-state.md](09-settings-state.md) | 设置与状态持久化：ISettingRegistry（JSON Schema配置）、IStateDB（轻量级存储）、ILayoutRestorer |
| 10 | [notifications-logging.md](10-notifications-logging.md) | 通知与日志：Notification API（success/error/promise）、Logger/LogConsole |

## 进阶阶段

| 编号 | 文档 | 说明 |
|------|------|------|
| 11 | [kernel-interaction.md](11-kernel-interaction.md) | Kernel交互：SessionContext、requestExecute、IOPub消息流、Kernel状态监听 |
| 12 | [documents.md](12-documents.md) | 自定义文档类型：FileType注册、DocumentModel/WidgetFactory、Yjs协作编辑 |
| 13 | [server-extension.md](13-server-extension.md) | 服务端扩展：Python tornado APIHandler、路由注册、前端ServerConnection调用 |
| 14 | [advanced-ui.md](14-advanced-ui.md) | 进阶UI模式：React集成、DataGrid、国际化i18n、主题扩展、顶部栏Widget |

## 学习路径建议

```
00 → 01 → 02 → 03（入门：理解扩展是什么）
       ↓
04 → 05 → 06 → 07 → 08（核心UI：能创建可交互的面板）
       ↓
09 → 10（状态：能持久化数据、反馈给用户）
       ↓
11 → 12 → 13 → 14（进阶：Kernel、自定义文档、服务端、React）
```

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-hello-world
02-project-setup
03-plugin-basics
04-commands
05-widgets-shell
06-signals
07-palette-launcher
08-menus-toolbars
09-settings-state
10-notifications-logging
11-kernel-interaction
12-documents
13-server-extension
14-advanced-ui
```
