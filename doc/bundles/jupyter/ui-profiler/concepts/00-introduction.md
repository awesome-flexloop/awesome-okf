---
type: Concept
title: jupyterlab-ui-profiler 入门介绍
description: JupyterLab UI性能分析扩展的功能概览、安装方法、快速开始和基本使用流程
tags: [jupyterlab, ui-profiler, introduction, getting-started, installation]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: readme
    resource: /references/api-tokens.md
    title: README.md 项目说明
  - id: init-py
    resource: /references/api-tokens.md
    title: jupyterlab_ui_profiler/__init__.py 服务端入口
  - id: index-ts
    resource: /references/api-tokens.md
    title: src/index.ts 插件入口
---

## 什么是 jupyterlab-ui-profiler

jupyterlab-ui-profiler 是 JupyterLab 官方维护的 UI 性能分析扩展（Extension），用于测量和分析 JupyterLab 界面操作的性能表现。它提供了一套系统化的基准测试（Benchmark）框架，可以量化各种用户操作的响应时间、CSS 样式对渲染性能的影响、JavaScript 函数级 CPU 使用情况等。

该扩展的核心设计理念是：将**测量方法**（Benchmark）与**用户操作场景**（Scenario）解耦，形成一个可扩展的性能测量矩阵。

## 核心能力

jupyterlab-ui-profiler 提供 6 种内置 Benchmark：

| Benchmark | 功能 | 浏览器要求 |
|-----------|------|-----------|
| Execution Time | 测量操作执行时间（`performance.now()`） | 所有现代浏览器 |
| Style Sheets | 逐样式表禁用，测量对性能的影响 | 所有现代浏览器 |
| Style Rules | 逐CSS规则删除，测量单条规则影响 | 所有现代浏览器 |
| Style Rule Groups | 按块分组删除CSS规则，评估代码分割策略 | 所有现代浏览器 |
| Style Rule Usage | 结合MutationObserver分析规则实际使用率 | 所有现代浏览器 |
| Profile JavaScript | 使用JS Self-Profiling API进行函数级采样 | Chrome/Edge（需特殊HTTP头） |

内置 10 种 Scenario（用户操作场景）：打开/切换菜单、切换标签页、打开侧边栏、代码补全、滚动、调试器操作、创建单元格、自定义命令序列等。

## 安装

### 环境要求

- JupyterLab >= 3.0（源码基于 JupyterLab 4.x 开发）
- Python 3
- Node.js（开发模式需要）

### pip 安装

```bash
pip install jupyterlab-ui-profiler
```

安装后启动 JupyterLab，扩展会自动激活。

### 开发模式安装

```bash
git clone https://github.com/jupyterlab/ui-profiler.git
cd ui-profiler
pip install -e .
jupyter labextension develop . --overwrite
jlpm install
jlpm build
```

开发迭代（双终端模式）：

```bash
# 终端1：监听TypeScript变化自动重编译
jlpm watch

# 终端2：启动JupyterLab
jupyter lab
# 修改代码后刷新浏览器即可
```

### 卸载

```bash
pip uninstall jupyterlab-ui-profiler
```

## 快速开始

### 1. 打开 UI Profiler

安装后，可以通过以下方式打开 UI Profiler：

- **命令面板**：按 `Ctrl+Shift+C`（macOS: `Cmd+Shift+C`）打开命令面板，搜索 "UI Profiler" 执行
- **Launcher**：在 Launcher 的 "Other" 分类中点击 "UI Profiler" 卡片
- **命令**：执行命令 `ui-profiler:open`

打开后会在主工作区显示 "UI Profiler" 面板。

### 2. 选择 Benchmark 和 Scenario

面板中有两个下拉选择器：
- **Benchmark**：选择测量方法（如 "Execution Time"）
- **Scenario**：选择要测量的用户操作场景（如 "Switch Menu"）

### 3. 配置参数

每个 Benchmark 和 Scenario 都有对应的 JSON Schema 配置表单（基于 `@rjsf/core` 渲染）：
- Benchmark 通常可配置 `repeats`（重复次数，默认3）
- Scenario 根据类型有不同配置项（如菜单名、标签页路径、滚动距离等）

### 4. 运行测量

点击运行按钮开始测量。测量过程中：
- 进度条显示当前进度百分比
- 可点击中止按钮中断测量
- 测量完成后结果自动展示

### 5. 查看结果

结果以表格形式展示（使用 Lumino DataGrid 高性能虚拟滚动表格），包含：
- 统计指标：min、Q1（第一四分位数）、IQM（四分位距均值）、mean
- 差异指标：ΔIQM、ΔIQM%、ΔQ1、ΔQ1%（相对于基线的变化）
- 某些Benchmark有自定义可视化（boxplot箱线图、调用栈火焰图等）

## 服务端HTTP头说明

启用扩展后，Jupyter Server 会自动添加以下HTTP响应头：

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
Document-Policy: js-profiling
```

- **COOP/COEP**：允许 Firefox 79+ 使用高精度 `performance.now()` 测量（跨源隔离）
- **Document-Policy: js-profiling**：允许 Chrome 使用 JS Self-Profiling API

如果不需要这些功能，可以禁用服务端扩展：

```bash
jupyter server extension disable jupyterlab_ui_profiler
```

禁用后，Execution Time和CSS相关Benchmark仍可正常使用，但Profile JavaScript功能将不可用。

## 扩展架构概览

```
┌──────────────────────────────────────────────┐
│            JupyterLab Frontend               │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │   UI     │  │ Profiler │  │    Scenarios│ │
│  │ (React)  │←→│ (Core)   │←→│ (10 built-in)│
│  └──────────┘  └────┬─────┘  └────────────┘ │
│                     │                        │
│              ┌──────┴──────┐                 │
│              │ Benchmarks  │                 │
│              │ (6 built-in)│                 │
│              └──────┬──────┘                 │
│                     │                        │
│              ┌──────┴──────┐                 │
│              │  Dramaturg  │                 │
│              │ (Automation)│                 │
│              └─────────────┘                 │
└──────────────────────┬───────────────────────┘
                       │ HTTP
┌──────────────────────┴───────────────────────┐
│         Jupyter Server (Python)              │
│  ┌──────────────────────────────────────┐    │
│  │  Server Extension (HTTP headers)     │    │
│  └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

核心三角关系：
- **Profiler**：核心调度器，管理Benchmark/Scenario注册，协调测量执行
- **Benchmark**：定义"怎么测"（测量方法）
- **Scenario**：定义"测什么"（用户操作）
- **Dramaturg**：底层浏览器自动化层，提供Playwright-like API供Scenario模拟用户操作

## 插件结构

扩展由三个 JupyterFrontEndPlugin 组成（src/index.ts）：

1. **`@jupyterlab/ui-profiler:plugin`**：核心Profiler服务，`provides: IUIProfiler`，注册6个内置Benchmark
2. **`@jupyterlab/ui-profiler:user-interface`**：UI界面插件，创建Profiler Widget、注册命令和Launcher卡片
3. **`@jupyterlab/ui-profiler:default-scenarios`**：默认Scenario插件，注册10个内置Scenario

这种三插件分离设计允许其他扩展单独依赖 `IUIProfiler` Token 添加自定义Benchmark/Scenario，而不需要UI界面。

## 相关概念

- (01-architecture-overview.md
- (02-profiler-core.md
- (03-benchmarks.md
- (04-scenarios.md
- (../examples/00-first-benchmark.md
