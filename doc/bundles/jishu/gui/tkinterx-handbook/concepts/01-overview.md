---
type: Concept
title: "tkinterx 概览：安装与模块地图"
description: "作者自研的 tkinter 扩展库 tkinterx 的项目背景、PyPI 安装方式、模块结构与设计理念总览"
tags: [tkinter, tkinterx, gui, overview, install, pypi]
generated: { by: "blog-article-to-okf-wiki/trae", at: "2026-09-02T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T18:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: tkinterx-handbook-jianshu
    resource: /references/sources.md
---

# tkinterx 概览：安装与模块地图

## 什么是 tkinterx

tkinterx 是作者 xinetzone（简书笔名"水之心"）自研的一个 tkinter 扩展库。作者在 GitHub 放置了名为 xinetzone/pychaos 的项目（仓库地址见[信源登记](../references/sources.md)），该项目以 tkinter 为基础研究如何使用 Python 开发 GUI 接口，tkinterx 即其中提供的扩展包。[^F-TXH-01]

tkinterx 的目标是让 tkinter 的常见 GUI 开发任务更顺手：提供比 `tkinter.Canvas` 更友好的统一画图接口、可在窗体之间传递用户输入的可定制对话框、按行/列批量创建图形的工具类，以及一个带鼠标键盘交互的几何画板。[^F-TXH-01]

## 安装

tkinterx 已发布到 PyPI，直接使用 pip 安装即可：[^F-TXH-01]

```bash
pip install tkinterx
```

安装后通过 `import tkinterx` 调用。

**PyPI 核验信息**（2026-09-02 核验，见[信源登记](../references/sources.md)）：

| 属性 | 值 |
|------|-----|
| 包名 | tkinterx |
| 最新版本 | 0.0.9（2020-05-30 发布） |
| 维护者 | xinetzone |
| 项目主页 | GitHub 仓库 xinetzone/pychaos（见[信源登记](../references/sources.md)） |
| 许可证 | MPL 2.0（Mozilla Public License 2.0） |
| Python 要求 | Python >= 3.7 |
| 开发状态 | 2 - Pre-Alpha（早期预发布阶段） |
| 支持平台 | Windows 7/10、Linux |

需要注意：tkinterx 是作者个人维护的早期项目（Pre-Alpha），本知识包中的 API 形态对应作者 2020 年 4-5 月发布的博文，实际接口以安装版本与 GitHub 仓库为准。

## 模块地图

手册中出现的 tkinterx 模块与类/函数如下，后续概念文档逐一展开：

| 模块 | 主要成员 | 用途 |
|------|----------|------|
| `tkinterx.graph.canvas` | `CanvasMeta` | 统一的 2D 画图接口，替代 `tkinter.Canvas`；提供 `create_graph`、`create_point`、`create_circle`、`create_square` 等方法 |
| `tkinterx.graph.canvas_design` | `SimpleGraph`、`RegularGraph`、`Selector` | 可修改形状/颜色/填充/线宽的图形工具类、规则图形（圆/正方形）类、图形形状与颜色选择面板 |
| `tkinterx.graph.painter` | `GraphMeta`、`GraphPainter` | 几何画板：绑定鼠标/键盘事件实现交互式绘图 |
| `tkinterx.meta` | `WindowMeta`、`ask_window`、`askokcancel`、`showwarning` | 可定制、可在窗体间传值的对话框基类与辅助函数 |
| `tkinterx.param` | `ParamDict` | 图形属性（颜色、形状等）的参数字典描述符 |
| `tkinterx.tools.colors` | `show_colors`、`color_dict` | 一键弹出常用颜色表；140 余条"颜色名 → 十六进制值 + 中文名"颜色字典 |

## 设计理念

手册体现出 tkinterx 的三条设计主线：[^F-TXH-01]

1. **统一画图接口**：用 `CanvasMeta.create_graph(graph_type, directions, ...)` 一个方法覆盖矩形、椭圆、直线、弧、多边形五类图形，并进一步封装出点、圆、正方形等语义化图元。
2. **窗体间传值**：`WindowMeta` 把用户在对话框中录入的"行数据"统一收集到 `table` 字典，配合 `ask_window()` 在主窗体与对话框之间传递值。
3. **组合式交互组件**：`Selector`（选择面板）+ `GraphPainter`（画板）组合成完整的几何画板应用，支持鼠标绘图、拖动、删除与键盘快捷键。

## 手册内容地图

| 博文 | 内容 | 本知识包位置 |
|------|------|--------------|
| F-TXH-01《tkinter 的拓展包：tkinterx》 | 安装、CanvasMeta、WindowMeta、ParamDict、canvas_design、几何画板 | [02-CanvasMeta 统一画图接口](02-canvas-meta.md)、[03-规则图形与批量阵列](03-graph-shapes.md)、[04-可传递值的窗体](04-window-meta.md)、[05-几何画板](05-geometry-painter.md) |
| F-TXH-02《tkinter 界面常用颜色表单》 | show_colors() 与 color_dict 颜色表单 | [06-颜色工具与抠图工具](06-tools-colors-matting.md)、[示例 01](../examples/01-getting-started.md) |
| F-TXH-03《tkinterx 之画图》 | create_point / create_circle / create_square 与彩色矩阵 | [03-规则图形与批量阵列](03-graph-shapes.md) |
| F-TXH-04《tkinterx 之抠图工具》 | 作者待更，仅有效果图 | [06-颜色工具与抠图工具](06-tools-colors-matting.md) |
| F-TXH-05《tkinterx 模拟电子限速》 | CanvasMeta 绘制限速标志完整示例 | [03-规则图形与批量阵列](03-graph-shapes.md)、[示例 03](../examples/03-speed-limit-sign.md) |

## 相关概念

- [CanvasMeta：统一画图接口](02-canvas-meta.md) — tkinterx 画图能力的核心类
- [规则图形与批量阵列](03-graph-shapes.md) — 点/圆/正方形、按行列绘图、图形设计工具
- [可传递值的窗体](04-window-meta.md) — WindowMeta 与 ask_window
- [几何画板](05-geometry-painter.md) — Selector + GraphPainter 交互式绘图
- [颜色工具与抠图工具](06-tools-colors-matting.md) — show_colors、color_dict 与抠图工具待更说明
- [《tkinterx 手册》信源登记](../references/sources.md)

[^F-TXH-01]: 简书《tkinter 的拓展包：tkinterx》，见[信源登记](../references/sources.md)。