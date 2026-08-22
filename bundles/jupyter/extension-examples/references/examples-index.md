---
type: Reference
title: JupyterLab 扩展示例源码索引
description: 28个官方扩展示例的源码路径与功能对照索引
tags: [jupyterlab, examples, source-index, extension-points]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: root-readme
    resource: /references/examples-index.md
    title: extension-examples/README.md 示例列表
---

## 示例目录索引

下表列出所有28个扩展示例及其核心文件路径和演示的扩展点。

| # | 示例目录 | 演示扩展点 | 核心源文件 |
|---|---------|-----------|-----------|
| 1 | hello-world | 最小插件模板 | src/index.ts |
| 2 | commands | 命令注册与执行 | src/index.ts |
| 3 | command-palette | 命令面板集成 | src/index.ts |
| 4 | widgets | 自定义Widget（Lumino） | src/index.ts |
| 5 | launcher | Launcher启动卡片 | src/index.ts |
| 6 | main-menu | 主菜单项添加 | src/index.ts |
| 7 | context-menu | 右键上下文菜单 | src/index.ts |
| 8 | signals | Widget间信号通信 | src/index.ts, src/panel.ts |
| 9 | settings | 设置系统（JSON Schema） | src/index.ts, schema/plugin.json |
| 10 | state | 状态数据库持久化 | src/index.ts |
| 11 | notifications | 通知系统 | src/index.ts |
| 12 | toolbar-button | Notebook工具栏按钮 | src/index.ts, schema/plugin.json |
| 13 | cell-toolbar | Cell工具栏按钮 | src/index.ts |
| 14 | contentheader | 主区域内容头部 | src/index.ts |
| 15 | log-messages | 日志消息发送 | src/index.ts |
| 16 | custom-log-console | 自定义日志控制台 | src/index.ts, src/logLevelSwitcher.tsx |
| 17 | datagrid | Lumino DataGrid表格 | src/index.ts |
| 18 | react-widget | React Widget集成 | src/index.ts, src/widget.tsx |
| 19 | documents | 自定义文档类型（Yjs协作） | src/index.ts, src/factory.ts, src/model.ts, src/widget.tsx |
| 20 | kernel-messaging | Kernel消息通信 | src/index.ts, src/panel.ts, src/model.ts, src/widget.tsx |
| 21 | kernel-output | Kernel输出渲染（OutputArea） | src/index.ts, src/panel.ts |
| 22 | completer | 自定义补全提供者 | src/index.ts, src/customconnector.ts |
| 23 | codemirror-extension | CodeMirror编辑器扩展 | src/index.ts |
| 24 | mimerenderer | MIME类型渲染器 | src/index.ts |
| 25 | server-extension | 前后端混合扩展 | src/index.ts, src/handler.ts, jupyterlab_examples_server/handlers.py |
| 26 | toparea-text-widget | 顶部区域Widget（双兼容） | src/index.ts |
| 27 | shout-button-message | 侧边栏按钮+状态栏（双兼容） | src/index.ts |
| 28 | clap-button-message | 多插件导出双兼容 | src/index.ts |
| 29 | metadata-form | 元数据表单自定义 | src/index.ts |

## 示例分组

按学习路径分组：

**入门级（5个）**：hello-world → commands → command-palette → widgets → launcher

**UI扩展点（8个）**：main-menu → context-menu → toolbar-button → cell-toolbar → contentheader → notifications → signals → toparea-text-widget

**数据与状态（4个）**：settings → state → log-messages → custom-log-console

**高级Widget（3个）**：datagrid → react-widget → mimerenderer

**文档与Kernel（4个）**：documents → kernel-messaging → kernel-output → completer

**编辑器扩展（1个）**：codemirror-extension

**后端扩展（1个）**：server-extension

**双兼容（2个）**：shout-button-message → clap-button-message

**高级UI（1个）**：metadata-form

## 相关概念

- [插件解剖结构](/references/plugin-anatomy.md)
- [核心API与Token](/references/core-api-tokens.md)
