---
type: Concept
title: jupyter-resource-usage 简介与功能概述
description: jupyter-resource-usage 是什么、核心功能、支持的资源类型、三种UI展示方式、版本兼容性说明
tags: [jupyter-resource-usage, introduction, resource-monitoring, jupyterlab, notebook]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-code
    resource: /references/source-code.md
---

# jupyter-resource-usage 简介与功能概述

## 什么是 jupyter-resource-usage

**jupyter-resource-usage** 是 Jupyter Notebook 和 JupyterLab 的扩展，用于在界面中实时显示当前 Notebook 服务器及其子进程（内核、终端等）的资源使用情况。指标每5秒刷新一次，帮助用户在内存/CPU/磁盘接近上限时及时感知。

该扩展同时支持 **JupyterLab 4.x** 和 **Notebook 7.x**（基于 JupyterLab 架构），旧版本（JupyterLab 3.x / Notebook 6.x）需安装 `<1.0.0` 版本。

## 核心功能

jupyter-resource-usage 监控三类资源：

| 资源类型 | 默认启用 | 显示内容 | 说明 |
|---------|:-------:|---------|------|
| **内存（Memory）** | ✅ 是 | 当前用量 / 限制值 | PSS优先（Linux），回退RSS；支持配置显示限制值（不强制） |
| **CPU** | ❌ 否 | CPU使用率百分比 | 需配置 `track_cpu_percent=True` 启用 |
| **磁盘（Disk）** | ❌ 否 | 已用 / 总量 | 需配置 `track_disk_usage=True` 启用，监控指定分区 |

当资源使用接近配置的阈值时，显示区域会变为**红底红字**警告样式。

## 三种 UI 展示方式

jupyter-resource-usage 提供三个独立的前端插件，覆盖不同场景：

### 1. 状态栏（Status Bar）—— 默认启用

在 JupyterLab 底部状态栏左侧显示资源使用文本，格式为：

```
Mem: 256.00 / 1024.00 MB
```

启用CPU和磁盘后变为：

```
| Disk: 1.50 / 10.00 GB | CPU: 12.00 % | Mem: 256.00 / 1024.00 MB
```

- 插件ID: `@jupyter-server/resource-usage:status-item`
- 位置：状态栏左侧，rank=2
- 始终注册到IStatusBar

### 2. 顶栏监控（Top Bar）—— 默认禁用

在 JupyterLab 顶部工具栏显示彩色进度条指示器，支持点击切换为迷你趋势图（Sparklines）。需通过 **Settings → Settings Editor → Resource Usage Indicator** 勾选启用。

- 插件ID: `@jupyter-server/resource-usage:topbar-item`
- 位置：TopBar工具栏（cpu rank=120, memory rank=130, disk rank=140）
- 颜色：CPU蓝色(#00B35B不对，实际蓝色#0072B3)、内存绿色(#00B35B)、磁盘紫色(#c27ba0)

### 3. 内核使用侧边栏（Kernel Usage Panel）—— 默认启用

在右侧边栏提供内核资源详情面板，点击转速表图标打开。显示：

- 内核主机名、时间戳、进程ID
- 内核CPU和内存使用量
- 宿主机CPU使用率和虚拟内存详情（active/available/free/inactive/percent/total/used/wired）

- 插件ID: `@jupyter-server/resource-usage:kernel-panel-item`
- 位置：右侧边栏，rank=200
- 命令ID: `kernel-usage:get`
- 需要 ipykernel >= 6.9.0（通过ZMQ control channel发送usage_request消息）

## 内核级资源监控

除了服务器级别的进程树资源统计，jupyter-resource-usage 还支持**单个内核**的资源使用详情。此功能通过向 ipykernel 发送 ZMQ `usage_request` 消息实现，要求：

- ipykernel 版本 >= 6.9.0（代码中硬编码版本检查）
- 内核响应超时时间为10秒
- 响应中包含 kernel_cpu、kernel_memory、hostname、pid、host_cpu_percent、host_virtual_memory 等字段

不满足条件时，侧边栏会显示友好的提示信息（版本不支持、无内核、超时、正在加载等）。

## 经典 Notebook 支持

对于经典 Jupyter Notebook（<7.0），扩展提供基于 RequireJS + jQuery 的 `static/main.js`，将资源指标显示在**顶部工具栏**（`#maintoolbar-container`），而非状态栏。经典前端：

- CPU和磁盘指示器默认隐藏（`jupyter-resource-usage-hide` CSS类）
- 内存始终显示，CPU/磁盘在数据可用时显示
- 页面不可见时（`document.hidden`）暂停轮询
- 切回标签页时立即刷新（visibilitychange事件）

## 版本兼容性

| jupyter-resource-usage | JupyterLab | Notebook | Python | ipykernel（内核监控） |
|:---------------------:|:----------:|:--------:|:------:|:-------------------:|
| >=1.0.0 (当前1.3.0) | 4.x | 7.x | >=3.10 | >=6.9.0 |
| <1.0.0 | 3.x / 2.x | 6.x / 5.x | - | - |

## Prometheus 集成

扩展默认启用 Prometheus 指标导出，通过 tornado PeriodicCallback 每秒更新6个 Gauge 指标：

- `total_memory_usage` / `max_memory_usage`
- `total_cpu_usage` / `max_cpu_usage`
- `current_disk_usage` / `max_disk_usage`

存在已知UI卡顿问题（GitHub issue #123），可通过 `--ResourceUseDisplay.enable_prometheus_metrics=False` 禁用。

## 相关概念

- [安装与启用](01-installation.md) — pip/conda安装、自动启用机制、旧版本手动启用
- [架构总览](02-architecture.md) — 后端+前端双架构、双API端点、数据流
- [配置系统详解](05-configuration.md) — 所有配置项、环境变量、命令行参数
- [内核资源监控](04-kernel-usage.md) — ZMQ usage_request协议、版本要求、侧边栏
