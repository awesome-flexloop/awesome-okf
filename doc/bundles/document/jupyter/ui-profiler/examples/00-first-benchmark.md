---
type: Example
title: 第一次运行基准测试
description: 从零开始使用jupyterlab-ui-profiler运行第一个性能基准测试——安装、打开Profiler面板、选择Benchmark和Scenario、运行并解读结果
tags: [jupyterlab, ui-profiler, getting-started, tutorial, benchmark]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
prerequisites:
  - JupyterLab 3.0+ 或 4.0+
  - Chrome/Edge 浏览器（推荐，JS Profiling需要）
  - Python 3.8+
---

## 目标

运行第一个UI性能基准测试，测量JupyterLab打开文件菜单的响应时间，并理解结果。

## 步骤1：安装

```bash
pip install jupyterlab-ui-profiler
```

安装完成后启动JupyterLab：

```bash
jupyter lab
```

## 步骤2：打开UI Profiler面板

1. 在JupyterLab顶部菜单栏，找到 **Settings** 菜单
2. 点击 **UI Profiler**（或在命令面板中搜索"UI Profiler"）
3. Profiler面板会在主区域打开

你会看到一个配置界面，包含：
- **Benchmark** 下拉选择器
- **Scenario** 下拉选择器
- **Options** 配置表单（根据选择动态变化）
- **Run** 按钮

## 步骤3：选择Benchmark

从Benchmark下拉列表中选择 **Execution Time**。

这是最简单的Benchmark，它使用`performance.now()`测量从scenario开始到结束的时间。

## 步骤4：选择Scenario

从Scenario下拉列表中选择 **Open Menu**。

这个Scenario模拟用户点击并打开一个主菜单的操作。

## 步骤5：配置参数

在Options表单中，可以看到配置项：

- **menu**: 选择要打开的菜单，默认是 `file`
- **repeats**: 重复次数，默认是 `3`

保持默认值即可。

## 步骤6：运行

点击 **Run** 按钮。

你会看到：
1. 进度条出现，显示"Iteration 1/3"等状态
2. 文件菜单自动打开和关闭3次（每次重复打开→测量→关闭）
3. 测量完成后结果自动显示

## 步骤7：解读结果

结果表格会显示类似以下数据：

| Scenario | IQM (ms) | Q1 (ms) | Median (ms) | Q3 (ms) | N |
|----------|----------|---------|-------------|---------|---|
| Open Menu | 15.23 | 14.87 | 15.31 | 16.02 | 6 |

各指标含义：

- **IQM (ms)**: 15.23ms — 这是最可靠的结果，表示打开菜单大约需要15毫秒
- **Q1 (ms)**: 14.87ms — 最快25%的执行在15ms以内完成
- **Median (ms)**: 15.31ms — 中位数，一半的执行快于15ms
- **Q3 (ms)**: 16.02ms — 75%的执行在16ms以内完成
- **N**: 6 — 实际采样数（repeats=3，但setup/cleanup阶段也有测量）

### 如何判断结果是否正常

| 菜单打开时间 | 评价 |
|-------------|------|
| < 16ms (60fps帧内) | 🟢 优秀，用户感知不到延迟 |
| 16-50ms | 🟡 良好，轻微延迟但可接受 |
| 50-100ms | 🟠 一般，用户能感觉到延迟 |
| > 100ms | 🔴 较差，明显卡顿 |

你的结果如果在10-30ms范围内都是正常的。

## 步骤8：尝试其他Scenario

回到配置界面，尝试不同的Scenario组合：

### 组合A：测量标签页切换性能

- Benchmark: Execution Time
- Scenario: **Switch Tabs**
- 配置：保持默认tabs配置（创建多个launcher标签）

### 组合B：测量侧边栏打开性能

- Benchmark: Execution Time
- Scenario: **Open Sidebar**
- 配置：sidebars = `["filebrowser", "jp-table-of-contents"]`

### 组合C：测量代码补全性能

- Benchmark: Execution Time
- Scenario: **Completer**
- 配置：保持默认（会创建一个Notebook，插入变量，触发补全）

## 常见问题

### Q: 为什么要重复多次？

单次测量受JIT编译、GC、系统负载等因素影响，重复3+次并使用IQR统计方法能得到可靠结果。

### Q: 为什么N=6而不是3？

Execution Time Benchmark在正式测量前会运行warm-up和baseline测量，所以总采样数可能大于repeats。

### Q: 结果差异很大怎么办？

1. 关闭其他浏览器标签页和扩展
2. 确保JupyterLab不在开发模式下运行
3. 增加repeats到10次
4. 多次运行benchmark看结果是否稳定

### Q: Profile JavaScript选项为什么是灰色的？

JS Self-Profiling需要Chrome/Edge浏览器且需要特殊HTTP头。如果服务端扩展未正确加载，或你在使用Firefox/Safari，该选项不可用。详见(../concepts/11-server-extension.md。

## 下一步

- 学习使用(01-css-profiling.md找出拖慢UI的CSS规则
- 尝试(02-custom-scenario.md测量你自己的操作
- 了解(../concepts/08-statistics-and-results.md以正确解读结果
