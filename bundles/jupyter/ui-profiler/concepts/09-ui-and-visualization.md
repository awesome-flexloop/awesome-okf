---
type: Concept
title: UI界面与结果可视化
description: 详解ui-profiler的用户界面——Launcher启动页、Monitor监控页、ProfileTrace火焰图、TimingTable时序表格、ResultTable结果表格、进度条与JSON配置表单
tags: [jupyterlab, ui-profiler, ui, react, flame-graph, table, json-form, progress]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: ui-tsx
    resource: /references/api-tokens.md
    title: src/ui.tsx UI组件实现
  - id: table-tsx
    resource: /references/benchmarks-source.md
    title: src/table.tsx 表格组件
---

## UI架构概述

ui-profiler的UI是一个React应用，通过JupyterLab的`ReactWidget`嵌入到JupyterLab的主界面中。整个UI分为三个主要视图：

```
┌─────────────────────────────────────────────┐
│  UIProfiler (顶部标题 + 标签页切换)          │
├──────────────┬──────────────────────────────┤
│  LauncherTab │  MonitorTab                  │
│  (配置+运行) │  (实时监控)                   │
└──────────────┴──────────────────────────────┘
```

UI的核心交互流程：
1. 用户选择Benchmark和Scenario
2. 通过JSON Schema表单配置参数
3. 点击"Run"开始执行
4. 进度条实时显示执行进度
5. 结果以表格/火焰图形式展示
6. 可保存结果为JSON

## Launcher 启动页

**文件**: src/ui.tsx

Launcher是主要的配置和运行界面，包含：

### Benchmark选择器

下拉列表显示所有可用的Benchmark，包括：
- 名称（从`benchmark.name`获取）
- 可用性状态（如果`isAvailable()`返回false则置灰）
- 不可用的原因提示（例如需要Chrome浏览器）

### Scenario选择器

下拉列表显示所有已注册的Scenario。与Benchmark选择器联动——某些Benchmark可能对Scenario有特殊要求。

### 配置表单（JSON Schema Form）

使用`@rjsf/validator-ajv8` + `@jupyterlab/ui-components`的FormComponent，根据Benchmark和Scenario的`configSchema`动态生成配置表单：

```typescript
// configSchema是JSON Schema 7格式
// FormComponent根据schema自动渲染表单控件：
// - type: "number" → 数字输入框
// - type: "integer" → 整数输入框
// - type: "string" → 文本输入框
// - enum: [...] → 下拉选择框
// - type: "boolean" → 复选框
// - type: "object" → 嵌套表单（可折叠）
// - type: "array" → 列表编辑器
```

CustomScenario的特殊之处：它的configSchema是动态生成的——在`app.restored`后遍历所有JupyterLab命令ID并构建oneOf。

### 运行按钮

- 点击后禁用（防止重复点击）
- 触发`profiler.runBenchmark()`执行
- 完成后自动跳转到结果展示

## Monitor 监控页

**文件**: src/ui.tsx（IMonitorProps）

Monitor提供实时监控视图，在Benchmark执行过程中显示：
- 当前正在执行的步骤
- 已完成/总迭代数
- 估计剩余时间

通过`progress` Signal接收实时更新。

## ProfileTrace 火焰图组件

**文件**: src/ui.tsx:L78-L300+

ProfileTrace是JS Self-Profiling结果的可视化组件，实现了一个交互式火焰图（Flame Graph）。

### 火焰图数据模型

火焰图的每一行代表一个时间区间，每个矩形代表一个函数调用帧：
- **宽度**：函数在CPU上的时间占比
- **Y轴位置**：调用栈深度（底部是根函数，上方是被调用者）
- **颜色**：按函数名/源文件着色
- **X轴**：时间顺序（从左到右）

### 交互功能

| 交互 | 行为 |
|------|------|
| **鼠标悬停** | 显示tooltip：函数名、源文件、行号、列号、耗时、占比 |
| **鼠标滚轮** | 缩放（scale.x调整） |
| **拖拽** | 平移（position.x/position.y调整） |
| **点击** | 选中帧，高亮显示 |

### 缩放和平移实现

```typescript
// 状态
state = {
  scale: { x: 1, y: 1 },     // 缩放比例
  position: { x: 0, y: 0 }, // 平移偏移
  dimensions: null,          // 容器尺寸
  inDrag: false              // 是否在拖拽中
}
```

- **Wheel事件**：`handleWheel`调整scale.x实现缩放，以鼠标位置为缩放中心
- **MouseDown**：`handleMouseDown`标记拖拽开始，记录起始位置
- **MouseMove**：`handleMouseMove`更新position实现平移
- **MouseUp**：`handleMouseUp`结束拖拽
- **ResizeObserver**：监听容器尺寸变化，更新dimensions

### 渲染优化

火焰图使用Canvas或SVG渲染（根据实现），在缩放/平移时只重绘可见区域内的帧。`deepest`属性记录最深的调用栈深度，用于计算初始Y轴缩放。

## TimingTable 时序表格

**文件**: src/table.tsx

TimingTable用于显示Execution Time和所有CSS Benchmark的结果。

### 列定义

根据Benchmark类型显示不同列：

**Execution Time（基准测试）**:
| 列 | 说明 |
|----|------|
| Scenario | 场景名称 |
| IQM (ms) | 四分位距均值 |
| Q1 (ms) | 第一四分位数 |
| Median (ms) | 中位数 |
| Q3 (ms) | 第三四分位数 |
| MAD | 中位绝对偏差 |
| N | 采样数 |

**CSS Benchmarks（额外列）**:
| 列 | 说明 |
|----|------|
| Selector/Block | CSS选择器或规则块索引 |
| Source | 源文件路径（美化后） |
| ΔIQM (ms) | 与基线的IQM差异 |
| ΔIQM% | IQM差异百分比 |
| ΔQ1 (ms) | Q1差异 |
| ΔQ1% | Q1差异百分比 |
| bgMatches | 静态匹配元素数（仅Style Rules） |
| matches | 动态匹配元素数（仅Rule Usage） |

### 排序

- 默认按`ΔIQM%`降序排列（影响最大的排在最前）
- 点击列头切换排序
- 数字列按数值排序，文本列按字母排序

### 源路径美化

```typescript
// src/table.tsx:L148-L152
result['source'] = result['source']
  .replace('webpack://./', '')
  .replace('webpack://../', '')
  .replace('node_modules', '📦');
```

- `webpack://./`前缀移除：webpack打包时的虚拟路径
- `node_modules`替换为📦emoji：一目了然地看出第三方依赖
- 本地源码路径保持原样

### 颜色编码

Δ%列使用条件着色：
- **红色系**：负Δ（删除后变快=该规则拖慢性能）
- **绿色系**：正Δ（删除后变慢=该规则有优化效果）
- 颜色深浅反映Δ%的绝对值大小

## ResultTable / ProfilerTable

**文件**: src/table.tsx（ResultTable部分）

用于JS Self-Profiling结果的表格展示：

| 列 | 说明 |
|----|------|
| Function | 函数名 |
| Resource | 源文件URL |
| Line | 行号 |
| Column | 列号 |
| Time (ms) | 总耗时（Total Time） |
| Time % | 占总时间百分比 |

默认按Time降序排列——最耗时的函数排在最前面。

## ProgressBar 进度条

**文件**: src/ui.tsx（使用`@jupyterlab/statusbar`的ProgressBar）

使用JupyterLab官方的ProgressBar组件，在Benchmark执行期间显示在状态栏或UI中。

进度更新通过`Signal<any, IProgress>`传递：

```typescript
// IProgress接口（定义在tokens.ts）
interface IProgress {
  message?: string;   // 当前步骤描述
  percentage?: number; // 0-100
}
```

在benchmark run()方法中：
```typescript
progress?.emit({ message: `Running iteration ${i+1}/${n}`, percentage: (i/n)*100 });
```

## 结果保存

### Save to JSON

运行完成后，用户可以点击"Save"按钮将结果保存为JSON文件。实现使用JupyterLab的Contents API：

```typescript
const upload = async (file: File): Promise<Contents.IModel> => {
  return await app.serviceManager.contentsUpload(file, getResultsLocation());
};
```

文件保存到`getResultsLocation()`指定的目录（默认为JupyterLab的根目录下`profiler-results/`文件夹）。

### JSON结果结构

```json
{
  "benchmark": "execution-time",
  "scenario": "menuOpen",
  "options": { "menu": "file", "repeats": 3 },
  "browser": { "name": "Chrome", "version": "120.0" },
  "results": [
    {
      "times": [45.2, 42.1, 43.8, 41.5, 44.0, 43.2],
      "iqm": 43.1,
      "q1": 41.8,
      "median": 43.2,
      "q3": 44.2
    }
  ],
  "reference": [48.5, 46.2, 47.1, ...],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 浏览器信息提取

**文件**: src/utils.ts:L1-L15

```typescript
export function extractBrowserVersion(): { name: string; version: string } {
  const ua = navigator.userAgent;
  // 解析user-agent提取浏览器名和版本
  // Chrome/xx.x.x.x → {name: 'Chrome', version: 'xx.x.x.x'}
  // Firefox/xx.x → {name: 'Firefox', version: 'xx.x'}
  // ...
}
```

结果中包含浏览器信息，便于跨浏览器/跨版本比较。

## UI交互设计原则

1. **Schema驱动**：所有配置通过JSON Schema自动生成表单，新增Benchmark/Scenario无需修改UI代码
2. **渐进式披露**：高级参数折叠在"Advanced options"中，默认只显示关键参数
3. **实时反馈**：进度条+状态消息让用户知道正在发生什么
4. **数据可导出**：所有结果可保存为JSON，支持离线分析
5. **可排序表格**：结果表格支持多列排序，方便快速定位瓶颈
6. **视觉编码**：颜色（红/绿）和emoji（📦）帮助快速扫描结果

## 相关概念

- (02-profiler-core.md
- (08-statistics-and-results.md
- (03-benchmarks.md
- (../references/api-tokens.md
