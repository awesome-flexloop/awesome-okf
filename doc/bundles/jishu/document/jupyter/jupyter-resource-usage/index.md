---
type: Bundle
title: Jupyter Resource Usage
description: jupyter-resource-usage 1.3.0 — JupyterLab/Notebook 资源使用监控扩展的源码学习与使用指南
tags: [jupyter, jupyterlab, notebook, resource-monitoring, memory, cpu, disk, kernel-monitoring, psutil, zmq]
version: 1.3.0
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:45:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:45:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-code
    resource: /references/source-code.md
---

# Jupyter Resource Usage (jupyter-resource-usage)

**版本**：1.3.0 | **JupyterLab兼容**：4.x / Notebook 7.x | **Python要求**：≥3.10

jupyter-resource-usage 是 JupyterLab 和 Jupyter Notebook 的官方资源监控扩展，在界面中实时显示内存、CPU、磁盘使用率，支持单内核精确监控。

## 功能概览

| 功能 | 默认状态 | 说明 |
|------|---------|------|
| 内存监控 | ✅ 启用 | 基于psutil遍历进程树，RSS/PSS采集 |
| CPU监控 | ❌ 需配置 | 需 `track_cpu_percent=True` |
| 磁盘监控 | ❌ 需配置 | 需 `track_disk_usage=True` |
| 状态栏显示 | ✅ 启用 | 底部状态栏纯文本显示，5秒刷新 |
| 顶栏进度条 | ❌ 需启用 | Settings Editor开启，彩色进度条+Sparklines趋势图 |
| 内核侧边栏 | ✅ 启用 | ipykernel ≥6.9.0时可用，单内核精确资源 |
| Prometheus指标 | ✅ 启用 | 通过jupyter-server /metrics端点导出 |
| 经典Notebook支持 | ✅ 启用 | nbextension自动启用 |

## 文档结构

```
jupyter-resource-usage/
├── index.md                    ← 本文件（总入口）
├── concepts/                   ← 概念文档
│   ├── index.md                ← 概念索引
│   ├── 00-introduction.md      ← 简介与功能概述
│   ├── 01-installation.md      ← 安装与启用
│   ├── 02-architecture.md      ← 架构总览
│   ├── 03-backend-api.md       ← 后端API与指标采集
│   ├── 04-kernel-usage.md      ← 内核资源监控
│   ├── 05-configuration.md     ← 配置系统详解
│   ├── 06-statusbar.md         ← 状态栏显示
│   ├── 07-topbar-monitor.md    ← 顶栏监控面板
│   ├── 08-kernel-sidebar.md    ← 内核使用侧边栏
│   ├── 09-classic-notebook.md  ← 经典Notebook支持
│   ├── 10-prometheus.md        ← Prometheus指标集成
│   └── 11-custom-metrics.md    ← 工具函数与扩展开发
├── examples/                   ← 使用示例
│   ├── index.md                ← 示例索引
│   └── 01-basic-usage.md       ← 基本使用示例（11个场景）
└── references/                 ← 信源登记
    ├── index.md                ← 信源索引
    └── source-code.md          ← 源码信源登记
```

## 快速开始

```bash
pip install jupyter-resource-usage
```

安装后启动JupyterLab，底部状态栏自动显示内存使用量。

## 核心API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/metrics/v1` | GET | 获取服务器进程树总资源指标（内存/CPU/磁盘） |
| `/api/metrics/v1/kernel_usage/get_usage/{kernel_id}` | GET | 获取单个内核的精确资源指标（ZMQ通信） |
| `/metrics` | GET | Prometheus格式指标（通过jupyter-server内置端点） |

## 架构要点

```
┌─────────────────────────────────────────────────────┐
│  前端 (TypeScript/React/Lumino)                      │
│  ┌──────────┐ ┌──────────┐ ┌───────────────────────┐│
│  │ 状态栏    │ │ 顶栏进度条│ │ 内核侧边栏            ││
│  │ (默认启用)│ │(需设置启用)││ (ipykernel≥6.9.0)     ││
│  └─────┬────┘ └─────┬────┘ └──────────┬────────────┘│
│        │5秒轮询     │5秒轮询          │5秒轮询       │
└────────┼────────────┼─────────────────┼─────────────┘
         │            │                 │
         ▼            ▼                 ▼
┌─────────────────────────────────────────────────────┐
│  后端 (Python/Tornado/psutil)                        │
│  ┌──────────────────────┐  ┌───────────────────────┐│
│  │ /api/metrics/v1      │  │ /api/metrics/v1/       ││
│  │ ApiHandler           │  │ kernel_usage/...       ││
│  │ psutil进程树遍历      │  │ KernelUsageHandler    ││
│  │ RSS/PSS/CPU/磁盘     │  │ ZMQ control channel   ││
│  │ ThreadPoolExecutor   │  │ usage_request消息     ││
│  └──────────────────────┘  └───────────────────────┘│
│  ┌──────────────────────────────────────────────────┐│
│  │ ResourceUseDisplay (traitlets.Configurable)      ││
│  │ 环境变量 / 命令行 / 配置文件 → 配置项             ││
│  └──────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

## 关键依赖

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| jupyter_server | ≥2.0 | 后端服务器框架 |
| psutil | （自动安装） | 进程和系统资源采集 |
| ipykernel | ≥6.9.0（内核侧边栏） | 内核端ZMQ响应usage_request |
| @jupyterlab/application | ^4.0.0 | 前端插件框架 |
| @lumino/polling | （自动安装） | 前端轮询机制 |

## 外部链接

- GitHub：https://github.com/jupyter-server/jupyter-resource-usage
- PyPI：https://pypi.org/project/jupyter-resource-usage/
- 官方文档：https://jupyter-server.github.io/jupyter-resource-usage/

## 文档导航

- 📖 **概念文档**：[concepts/index.md](concepts/index.md) — 深入理解各模块
- 💡 **使用示例**：[examples/index.md](examples/index.md) — 实际使用场景
- 📋 **信源登记**：[references/index.md](references/index.md) — 事实来源

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
