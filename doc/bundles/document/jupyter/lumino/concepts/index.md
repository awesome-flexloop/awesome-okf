---
type: Index
title: Lumino 核心概念
description: Lumino 概念文档索引，包含12个核心概念文档，覆盖基础设施到应用框架的完整知识体系
tags: [lumino, index, concepts]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:55:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: lumino-source
    resource: /external/libs/jupyter/lumino
    title: Lumino 源码根目录
---

# Lumino 核心概念

本文档包含 Lumino 框架的核心概念文档，按从基础到应用的顺序排列。

## 学习路径

```
入门基础（00-02）
  ├── 00. Lumino简介与定位
  ├── 01. 架构总览与包层次
  └── 02. IDisposable资源管理模式
        ↓
核心抽象（03-05）
  ├── 03. Signal/Slot类型安全事件系统
  ├── 04. MessageLoop消息循环机制
  └── 05. Widget生命周期与DOM管理
        ↓
UI系统（06-08）
  ├── 06. 布局系统详解
  ├── 07. 命令系统与快捷键
  └── 08. 虚拟DOM渲染引擎
        ↓
应用与进阶（09-11）
  ├── 09. 插件化应用框架
  ├── 10. 高级组件与DataGrid
  └── 11. 算法工具与集合库
```

## 概念文档列表

### 入门基础

| 编号 | 文档 | 核心内容 |
|------|------|----------|
| 00 | [Lumino简介与定位](00-introduction.md) | 什么是 Lumino、历史背景、与其他框架的关系、核心特性、适合场景 |
| 01 | [架构总览与包层次](01-architecture-overview.md) | 四层架构模型、19个包的职责划分、模块依赖关系、设计原则 |
| 02 | [IDisposable资源管理模式](02-disposable-pattern.md) | IDisposable接口、DisposableDelegate/DisposableSet、幂等释放、AttachedProperty清理 |

### 核心抽象

| 编号 | 文档 | 核心内容 |
|------|------|----------|
| 03 | [Signal/Slot类型安全事件系统](03-signaling-system.md) | ISignal/Signal类、connect/emit/disconnect、Slot类型参数、与DOM事件/EventEmitter对比、内存安全 |
| 04 | [MessageLoop消息循环机制](04-messaging-loop.md) | Message/ConflatableMessage、sendMessage/postMessage、消息队列、消息合并(Conflation)、MessageHook拦截、compression |
| 05 | [Widget生命周期与DOM管理](05-widget-lifecycle.md) | Widget基类、node/title/layout属性、Flag状态系统、HiddenMode、attach/detach/show/hide/dispose消息序列、生命周期钩子重写 |

### UI系统

| 编号 | 文档 | 核心内容 |
|------|------|----------|
| 06 | [布局系统详解](06-layout-system.md) | Layout抽象基类、LayoutItem、FitPolicy、对齐属性、BoxLayout/SplitLayout/DockLayout/StackedLayout/GridLayout内置布局引擎 |
| 07 | [命令系统与快捷键](07-command-system.md) | CommandRegistry、命令选项(label/icon/enabled/toggled)、KeyBinding、keys格式(Accel/Ctrl/Cmd/Alt/Shift)、selector优先级、与Menu/CommandPalette集成 |
| 08 | [虚拟DOM渲染引擎](08-virtual-dom.md) | VirtualElement/VirtualText、h()函数、属性/事件/子节点、VirtualDOM.render()差异更新、hpass透传、与React对比 |

### 应用与进阶

| 编号 | 文档 | 核心内容 |
|------|------|----------|
| 09 | [插件化应用框架](09-plugin-application.md) | Application类、Token类型标记、IPlugin接口(requires/optional/provides/activate)、PluginRegistry依赖注入、拓扑排序激活、autoStart策略、Shell、ContextMenu |
| 10 | [高级组件与DataGrid](10-advanced-widgets.md) | TabBar/TabPanel、Menu/MenuBar/ContextMenu、DockPanel停靠面板、DragDrop拖拽、DataGrid高性能表格(Canvas渲染/虚拟滚动)、Poll轮询、AttachedProperty |
| 11 | [算法工具与集合库](11-algorithm-utilities.md) | @lumino/algorithm迭代器函数式操作(range/map/filter/reduce/chain/zip/topologicSort)、BTree/LinkedList、ArrayExt原地操作、PromiseDelegate、UUID/JSONExt/MimeData、KeyboardLayout、domutils |

## 关联文档

- [参考资料索引](../references/index.md) — 源码信源登记、API速查表
- [示例教程索引](../examples/index.md) — 可运行的代码示例
- [Lumino 主页](../index.md) — 回到 Lumino bundle 首页

```{toctree}
:maxdepth: 7

00-introduction
01-architecture-overview
02-disposable-pattern
03-signaling-system
04-messaging-loop
05-widget-lifecycle
06-layout-system
07-command-system
08-virtual-dom
09-plugin-application
10-advanced-widgets
11-algorithm-utilities
```
