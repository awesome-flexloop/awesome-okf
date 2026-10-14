---
okf_version: "0.2"
type: group
title: "🖥️ 系统与基础设施"
description: "操作系统与基础设施知识包——WSL 子系统与 PowerShell 困境防御等 Windows/Linux 系统层主题"
---

# 🖥️ 系统与基础设施

本组收录操作系统与基础设施相关的知识包：WSL 子系统、PowerShell 5 困境防御，以及 openKylin 默认 Wayland 合成器 kylin-wayland-compositor 的源码架构精读。Git 系主题见 [开发与协作（dev）](../dev/index.md) 分组。

## 知识包列表

| 知识包 | 定位 | 说明 |
|--------|------|------|
| [wsl/](wsl/index.md) | WSL 中文教程 | 安装/CLI/架构/文件系统互操作/WSLc API/网络与 systemd/调试与最佳实践 |
| [powershell-hell/](powershell-hell/index.md) | PowerShell 5 困境防御 | AI 智能体在 PS5.1 环境的失败模式、防御模式与检查清单 |
| [kylin-wayland-compositor/](kylin-wayland-compositor/index.md) | Wayland 合成器源码精读 | openKylin 默认显示服务器 kylin-wlcom（wlroots 0.17）：启动/后端/渲染/场景/输出/输入/视图工作区/特效/插件/协议/XWayland/安全门户/libkywc，16 概念 + 3 走读 + 851 条编号事实 |

```{toctree}
:hidden:
:maxdepth: 7

kylin-wayland-compositor/index
wsl/index
powershell-hell/index
```
