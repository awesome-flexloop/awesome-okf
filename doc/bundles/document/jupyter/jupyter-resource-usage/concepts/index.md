---
type: Concept
title: 概念文档索引
description: jupyter-resource-usage 概念文档索引，按学习路径排列
tags: [jupyter-resource-usage, concepts, index]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:45:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources: []
---

# 概念文档索引

本目录包含 jupyter-resource-usage 的概念文档，按推荐学习顺序排列。

## 入门篇

| 序号 | 文档 | 说明 |
|------|------|------|
| 00 | [简介与功能概述](00-introduction.md) | 扩展功能、UI展示方式、版本兼容性 |
| 01 | [安装与启用](01-installation.md) | pip/conda安装、自动启用、开发安装 |
| 02 | [架构总览](02-architecture.md) | 前后端分层、API设计、数据流、设计决策 |

## 后端篇

| 序号 | 文档 | 说明 |
|------|------|------|
| 03 | [后端API与指标采集](03-backend-api.md) | ApiHandler实现、psutil进程树遍历、RSS/PSS、内存/CPU/磁盘指标采集、响应格式、PSUtilMetricsLoader引擎 |
| 04 | [内核资源监控](04-kernel-usage.md) | KernelUsageHandler、ZMQ control channel、usage_request消息协议、ipykernel版本要求、轮询与竞态防护 |
| 05 | [配置系统详解](05-configuration.md) | 所有traitlets配置项、环境变量、命令行参数、配置文件、Callable动态限制、前端Settings Editor配置 |
| 10 | [Prometheus指标集成](10-prometheus.md) | PSUtilMetricsLoaderMixin、Gauge指标注册、PSUtilMetric自定义指标、已知UI卡顿bug |

## 前端篇

| 序号 | 文档 | 说明 |
|------|------|------|
| 06 | [状态栏显示](06-statusbar.md) | VDomRenderer文本渲染、Poll轮询、警告样式、Model数据模型、环形缓冲区 |
| 07 | [顶栏监控面板](07-topbar-monitor.md) | CpuView/MemoryView/DiskView进度条、Sparklines趋势图、IndicatorComponent、Settings Editor启用 |
| 08 | [内核使用侧边栏](08-kernel-sidebar.md) | KernelWidgetTracker活动内核跟踪、useInterval自定义Hook、竞态防护、五种空白状态 |
| 09 | [经典Notebook支持](09-classic-notebook.md) | nbextension机制、RequireJS模块、D3.js图标、与JupyterLab前端的区别 |

## 扩展篇

| 序号 | 文档 | 说明 |
|------|------|------|
| 11 | [工具函数与扩展开发](11-custom-metrics.md) | 单位格式化函数、useInterval模式、VDomRenderer/ReactWidget组件模式、添加新API端点和前端组件、开发安装 |

## 学习路径建议

1. **快速上手**：00 → 01 → 02
2. **理解后端**：02 → 03 → 04 → 05
3. **理解前端**：02 → 06 → 07 → 08 → 09
4. **运维配置**：05 → 10
5. **二次开发**：02 → 03 → 05 → 11

```{toctree}
:hidden:

00-introduction
01-installation
02-architecture
03-backend-api
04-kernel-usage
05-configuration
06-statusbar
07-topbar-monitor
08-kernel-sidebar
09-classic-notebook
10-prometheus
11-custom-metrics
```
