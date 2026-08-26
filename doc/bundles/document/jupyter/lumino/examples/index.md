---
type: Index
title: Lumino 示例教程
description: Lumino 实战示例索引，从Hello World到插件化应用，包含完整代码和说明
tags: [lumino, index, examples, tutorial]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:20:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: lumino-source
    resource: /external/libs/jupyter/lumino
    title: Lumino 源码根目录
---

# Lumino 示例教程

以下示例按学习难度递增排列，每个示例都包含完整代码和关键点说明。

## 示例列表

| 编号 | 示例 | 核心知识点 | 难度 |
|------|------|-----------|------|
| 01 | [创建第一个 Widget](01-create-widget.md) | Widget子类化、生命周期钩子、DOM事件、挂载到页面 | ⭐ |
| 02 | [使用Signal实现组件通信](02-signal-communication.md) | Signal定义、Slot连接/断开、ISignal只读暴露、内存安全 | ⭐⭐ |
| 03 | [使用布局排列Widget](03-layout-basics.md) | BoxPanel/SplitPanel/TabPanel/DockPanel、stretch因子、spacing | ⭐⭐ |
| 04 | [命令与快捷键绑定](04-commands-shortcuts.md) | CommandRegistry、KeyBinding、Menu、CommandPalette、动态状态 | ⭐⭐⭐ |
| 05 | [构建插件化应用](05-plugin-app.md) | Application、Token、IPlugin、依赖注入、拓扑排序激活 | ⭐⭐⭐⭐ |

## 学习建议

### 入门路径（推荐）

1. 先阅读[核心概念](../concepts/00-introduction.md)了解 Lumino 是什么
2. 按顺序完成示例 01-02：掌握 Widget 和 Signal 两个最基础的概念
3. 完成示例 03：理解布局系统，能搭建基础 UI
4. 完成示例 04：掌握命令系统，实现应用交互
5. 完成示例 05：理解插件架构，构建可扩展应用

### 快速参考

- 如果你只需要构建 UI 组件 → 重点看示例 01-03
- 如果你需要快捷键和菜单 → 看示例 04
- 如果你要构建类似 JupyterLab 的大型应用 → 重点看示例 05

## 前置知识

所有示例假设你已了解：
- TypeScript 基础（类、接口、泛型、箭头函数）
- HTML DOM 基础操作
- ES6 Promise 和模块系统
- npm/包管理基础

## 运行环境

所有示例需要以下环境：

```bash
# Node.js 16+
node --version

# 创建项目
mkdir lumino-demo && cd lumino-demo
npm init -y
npm install @lumino/widgets @lumino/commands @lumino/application @lumino/default-theme
npm install -D typescript vite
```

使用 Vite 作为开发服务器：

```bash
npx vite
```

## 关联文档

- [核心概念文档](../concepts/index.md) — 每个示例对应的概念文档
- [参考资料索引](../references/index.md) — API 速查表和源码信源
- [Lumino 主页](../index.md) — 回到 Lumino bundle 首页

```{toctree}
:hidden:
:maxdepth: 7

01-create-widget
02-signal-communication
03-layout-basics
04-commands-shortcuts
05-plugin-app
```
