---
type: Reference
title: Textual 仓库信源登记
description: Textualize/Textual 仓库信源登记：仓库定位、本地路径、远程 URL、分支、commit 哈希、盘点日期与核心模块清单。
tags: [textual, textualize, source-code, tui-framework]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
status: stable
stale_after: 2027-03-01
sources: []
---

# Textual 仓库信源登记

Textual 是 Python 终端用户界面（TUI）框架，以组件化 Widget、CSS 式样式、消息驱动架构构建交互式终端应用，是 Textualize 生态的核心框架。

## 信源信息

| 项目 | 值 |
|---|---|
| 仓库定位 | Python TUI 框架（Rapid Terminal Application Development） |
| 本地路径 | `external/dao/action/Textualize/textual` |
| 远程 URL | `git@github.com:Textualize/textual.git` |
| 分支 | `main` |
| commit hash | `06dbeef4bb70fb718236aa418ed658ef4667a126` |
| 盘点日期 | 2026-09-01 |

## 核心模块清单

核心包 `src/textual/`（120+ 文件）关键模块：

- `app.py`、`screen.py`、`widget.py`、`dom.py`、`compose.py`：应用-屏幕-组件-DOM 核心骨架
- `reactive.py`、`message.py`、`message_pump.py`、`events.py`、`signal.py`、`binding.py`、`actions.py`：响应式与消息系统
- `css/`：CSS 解析与样式系统子包
- `widgets/`：内置组件库子包
- `drivers/`：终端驱动子包
- `layouts/`、`layout.py`、`box_model.py`、`geometry.py`、`map_geometry.py`、`_layout_resolve.py`：布局系统
- `renderables/`、`render.py`、`strip.py`、`_segment_tools.py`、`content.py`、`markup.py`：渲染层
- `worker.py`、`worker_manager.py`、`await_complete.py`、`_work_decorator.py`：异步工作线程
- `command.py`、`system_commands.py`、`pilot.py`、`timer.py`、`notifications.py`：命令与测试驾驶
- `document/`、`tree-sitter/`、`_tree_sitter.py`、`_text_area_theme.py`：文档与语法解析
- `theme.py`、`color.py`、`style.py`、`filter.py`、`highlight.py`：主题与颜色
- `demo/`：内置演示应用

辅助目录：`docs/`（MkDocs 文档源，含 guide/api/widgets/events/styles 等）、`examples/`、`tests/`、`tools/`、`reference/`。
