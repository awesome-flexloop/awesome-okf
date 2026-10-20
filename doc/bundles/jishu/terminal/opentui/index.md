---
okf_version: "0.2"
type: Index
title: OpenTUI 终端 UI 开发 OKF 知识包
description: 基于固定源码快照与官方文档，系统梳理 OpenTUI 的发布包、Core renderer、native 渲染、输入焦点、React/Solid 绑定、生命周期与测试。
tags: [opentui, tui, terminal, typescript, zig, okf]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-20T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-20T00:00:00+08:00" }
status: stable
stale_after: 2027-04-20
sources:
  - id: opentui-source
    resource: /references/source-code-snapshot.md
    title: OpenTUI 源码快照登记
  - id: opentui-docs
    resource: /references/official-documentation.md
    title: OpenTUI 官方文档登记
  - id: opentui-packages
    resource: /references/package-surface.md
    title: OpenTUI 发布包与入口面登记
---

# OpenTUI 终端 UI 开发 OKF 知识包

本知识包以 OpenTUI 固定源码 commit `f8f608e2b9a41685d613a1156708ff06c826c3ce` 和官方文档为依据，介绍一套由 TypeScript API 与 Zig native core 协作的终端 UI 技术栈。官方文档中的 `0.6.6` release notes、Core manifest 版本字段与源码 commit 分别登记，不将它们合并为同一发布坐标。

教程覆盖发布包与入口面、Core renderer/renderable tree、Yoga layout 与 native scene、键盘鼠标及焦点、资源所有权、React/Solid bindings、测试渲染器和扩展包，并以 5 个示例串联主要使用路径。

## 核心认识

1. **从 Core 对象树追到 native scene**：声明式组件和 renderables 最终进入布局、cell 绘制及帧输出流程；native 内部结构不等于应用层 API。
2. **native 渲染不包办宿主运行时**：终端输入、事件循环、帧调度和输出交付需区分理解。
3. **renderer 与框架 root 的所有权分离**：卸载 React/Solid 树与销毁 renderer 是不同操作，应用关闭时应明确完成 renderer 清理。
4. **终端焦点不是浏览器焦点**：terminal-window focus、renderable focus 和键盘分发各有边界，Core 不自动提供 Tab 遍历。
5. **包数、入口数是不同口径**：发布脚本登记 7 个 release package roots；subpath exports 不另算独立发布包。

## 学习路径

1. 从[生态总览](/concepts/00-ecosystem-overview.md)和[包与入口面](/concepts/01-packages-and-entrypoints.md)开始，确认项目边界和版本坐标。
2. 学习[Core renderer 与 renderables](/concepts/02-core-renderer-and-renderables.md)，再阅读[布局与 native 渲染](/concepts/03-layout-and-native-rendering.md)及[输入、焦点与 Keymap](/concepts/04-input-focus-and-keymap.md)。
3. 先掌握[生命周期与资源所有权](/concepts/05-lifecycle-and-resource-ownership.md)，再按项目需要选择[React](/concepts/06-react-binding.md)或[Solid](/concepts/07-solid-binding.md)绑定。
4. 通过[测试概念](/concepts/08-testing.md)和[示例索引](/examples/index.md)练习，再查阅[生态扩展包](/concepts/09-ecosystem-packages.md)。
5. 遇到版本或入口问题时回到[信源索引](/references/index.md)，以固定源码和对应官方页面复核。

## 文档导航

- [概念教程](concepts/index.md)：10 篇，按生态、Core、交互与生命周期、bindings、测试和扩展包递进。
- [实战示例](examples/index.md)：5 篇，覆盖 Core、test renderer、React、Solid 与 native 渲染观测边界。
- [信源登记](references/index.md)：3 份，区分固定源码、官方文档和发布包入口清单。
- [更新日志](log.md)：记录本 bundle 的内容范围与验证状态。

## 来源与范围

- 源码事实固定于 [OpenTUI 源码快照](/references/source-code-snapshot.md)，不引用本机绝对路径或浮动分支。
- 面向用户的学习路径参照[官方文档登记](/references/official-documentation.md)；文档 `next` 内容不自动视为发布版事实。
- 本教程聚焦公开包面和核心机制，不声称逐行覆盖仓库全部源码、测试或生成文件。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
