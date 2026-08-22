---
type: Index
title: 核心概念
description: jupyterlab-ui-profiler 的12个核心概念文档，从入门到精通
tags: [jupyterlab, ui-profiler, concepts, architecture]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
---

## 入门必读

| 序号 | 文档 | 说明 |
|------|------|------|
| 00 | (../concepts/00-introduction.md | 什么是ui-profiler、解决什么问题、安装方法、核心能力概览 |
| 01 | (../concepts/01-architecture-overview.md | N×M测量矩阵、Benchmark-Scenario-Profiler三角架构、5个核心设计洞察 |
| 02 | (../concepts/02-profiler-core.md | UIProfiler类、IUIProfiler Token、生命周期管理、Signal通信机制 |

## 测量方法

| 序号 | 文档 | 说明 |
|------|------|------|
| 03 | (../concepts/03-benchmarks.md | Execution Time/Style Sheets/Style Rules/Style Rule Groups/Rule Usage/JS Self-Profiling详解 |
| 04 | (../concepts/04-scenarios.md | 菜单操作/标签页切换/侧边栏/代码补全/滚动/调试器/单元格创建/自定义命令序列 |
| 05 | (../concepts/05-css-profiling.md | 减法vs加法测量、四层CSS测量粒度、Δ差异指标、Source Map溯源、规则优化建议 |
| 06 | (../concepts/06-js-profiling.md | window.Profiler API、micro/macro采样模式、trace数据结构、帧迭代算法、浏览器兼容性 |

## 内部机制

| 序号 | 文档 | 说明 |
|------|------|------|
| 07 | (../concepts/07-dramaturg-automation.md | 为什么不用Playwright、Observer模式、waitForSelector/waitForLayout/waitForScrollEnd、CM5/CM6兼容 |
| 08 | (../concepts/08-statistics-and-results.md | IQM/Median/MAD/Quartile统计指标、Δ指标计算、统计显著性判断、常见统计陷阱 |
| 09 | (../concepts/09-ui-and-visualization.md | Launcher/Monitor视图、火焰图ProfileTrace、TimingTable/ProfilerTable、进度条、结果导出 |

## 扩展与部署

| 序号 | 文档 | 说明 |
|------|------|------|
| 10 | (../concepts/10-custom-extensions.md | IUIProfiler Token注入、IBenchmark/IScenario接口实现、configSchema编写、编程式调用 |
| 11 | (../concepts/11-server-extension.md | COOP/COEP/Document-Policy三个HTTP头、跨域隔离、禁用扩展、反向代理配置、COEP问题排查 |
