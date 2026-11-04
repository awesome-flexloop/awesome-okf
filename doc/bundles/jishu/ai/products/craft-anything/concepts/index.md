---
okf_version: "0.2"
type: category
title: "Craft Anything 概念教程"
description: "Craft Anything 从『是什么』到『怎么用』——项目定位、净室与深度两种模式、可量化的相似度检查机制、工具与四步工作流、安装与早期 alpha 边界"
---

# Craft Anything 概念教程

按从「是什么」到「怎么用」再到「现实边界」的路径组织：

| 文档 | 内容 |
|------|------|
| [00 · 项目身份与定位](00-what-is-craft-anything.md) | 是什么、官方定位原句、归属与许可、热度（带时点）、要解决的问题 |
| [01 · 净室与深度两种模式](01-clean-room-and-deep-modes.md) | 默认净室（Clean room）与深度（Deep）之别、强制工具白名单的安全边界 |
| [02 · 相似度检查机制](02-likeness-checking-method.md) | 1440/768/390 三宽度比对、布局+画面细节(SSIM)取均值、跨页平均、最多 6 轮或达 90% 停止 |
| [03 · 工具、四步工作流与运行时](03-tools-workflow-and-runtime.md) | 工具即 CLI 子命令又是 MCP 工具、Study→Build→Check→Ready、项目文件夹结构、Claude Code/Codex 运行时 |
| [04 · 安装与已知边界](04-install-and-known-limits.md) | 安装包形态、Apache-2.0 许可与 Rust 1.97+ 前置、早期 alpha 能力边界与工具数口径提醒 |

```{toctree}
:maxdepth: 2
:hidden:

00-what-is-craft-anything
01-clean-room-and-deep-modes
02-likeness-checking-method
03-tools-workflow-and-runtime
04-install-and-known-limits
```
