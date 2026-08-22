---
type: Concept
title: 统计方法与结果解读
description: 详解ui-profiler的统计学方法——IQR四分位距均值、四分位数、Median绝对偏差、outlier处理、Δ指标计算、以及如何正确解读性能测量结果
tags: [jupyterlab, ui-profiler, statistics, iqr, performance, outlier, median, delta]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: statistics-ts
    resource: /references/benchmarks-source.md
    title: src/statistics.ts 统计工具
  - id: table-ts
    resource: /references/benchmarks-source.md
    title: src/table.tsx 结果表格组件
---

## 为什么性能测量需要统计学

性能测量本质上是**带噪声的重复实验**：

1. **JIT编译**：第一次运行代码时JavaScript引擎进行JIT编译，后续运行更快（warm-up效应）
2. **GC暂停**：垃圾回收可能在任意时刻触发，导致某次测量异常慢
3. **浏览器事件循环**：其他标签页、扩展、定时器都会竞争主线程
4. **布局抖动**：某些帧可能触发额外的强制同步布局
5. **系统负载**：操作系统层面的CPU调度、电源管理等

单次测量结果几乎没有意义，必须通过**多次重复+统计分析**才能得到可靠结论。

## Statistic 工具类

**文件**: src/statistics.ts

```typescript
export namespace Statistic {
  export function mean(values: number[]): number;
  export function median(values: number[]): number;
  export function mad(values: number[]): number;       // Median Absolute Deviation
  export function quartile(values: number[], q: number): number;
  export function interQuartileMean(values: number[]): number;
  export function iqr(values: number[]): [number, number];
  export function standardDeviation(values: number[]): number;
}
```

## 核心统计指标

### Mean（算术平均值）

```typescript
export function mean(values: number[]): number {
  return values.reduce((a, b) => a + b, 0) / values.length;
}
```

简单但脆弱——一个离群值可以严重扭曲结果。在ui-profiler中，mean主要用于计算平均采样间隔等对离群值不敏感的场景。

### Median（中位数）

```typescript
export function median(values: number[]): number {
  return quartile(values, 2);
}
```

中位数是排序后位于中间的值：
- 奇数个元素：取中间元素
- 偶数个元素：取中间两个值的平均

中位数对离群值非常鲁棒（一个极端值不会改变中位数），是"典型值"的好代表。

### Quartiles（四分位数）

```typescript
export function quartile(values: number[], q: number): number {
  const sorted = [...values].sort((a, b) => a - b);
  const pos = (sorted.length - 1) * (q / 4);
  const base = Math.floor(pos);
  const rest = pos - base;
  if (sorted[base + 1] !== undefined) {
    return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
  } else {
    return sorted[base];
  }
}
```

- **Q1（q=1）**：第25百分位数，最快的25%执行的最慢值——代表"最好情况"性能
- **Q2（q=2）**：第50百分位数，即中位数——代表"典型情况"
- **Q3（q=3）**：第75百分位数，最慢的25%执行的最快值——代表"最差情况"阈值

线性插值法处理非整数索引位置。

### IQR（四分位距）

```typescript
export function iqr(values: number[]): [number, number] {
  return [quartile(values, 1), quartile(values, 3)];
}
```

IQR = Q3 - Q1，表示中间50%数据的分布范围。IQR越小说明数据越集中（测量稳定），IQR越大说明性能波动大。

**离群值判定**（Tukey围栏法）：
- 下围栏：Q1 - 1.5 × IQR
- 上围栏：Q3 + 1.5 × IQR
- 超出围栏的值为离群值

### IQM（四分位距均值/截尾均值）

```typescript
export function interQuartileMean(values: number[]): number {
  values = [...values].sort((a, b) => a - b);
  const q = Math.floor(values.length / 4);
  if (values.length % 4 === 0) {
    // N是4的倍数：去掉前q和后q个，中间取平均
    return mean(values.slice(q, values.length - q));
  } else {
    // N不是4的倍数：边界值加权
    const iqrSpan = (values.length / 4) * 2;
    const toConsider = values.slice(q, values.length - q);
    const remainder = iqrSpan - toConsider.length + 1;
    const sum = toConsider.reduce((a, b) => a + b, 0)
      - (values[q] * remainder / 2)
      - (values[values.length - 1 - q] * remainder / 2);
    return sum / (iqrSpan - remainder);
  }
}
```

IQM是ui-profiler的**核心聚合指标**，也是CSS Benchmark中Δ计算的基础。

**为什么IQM优于mean和median？**

| 指标 | 优点 | 缺点 |
|------|------|------|
| Mean | 数学性质好，充分利用所有数据 | 对离群值极度敏感 |
| Median | 对离群值鲁棒 | 只利用了中间一个/两个值，信息损失大 |
| **IQM** | **丢弃最高和最低25%后取平均，兼顾鲁棒性和信息利用率** | 实现稍复杂 |

IQM丢弃了25%最快和25%最慢的数据点：
- 最快的25%可能包含warm-up效应、缓存命中异常好的情况
- 最慢的25%可能包含GC暂停、系统中断等噪声
- 中间50%代表"稳定状态"的性能

### MAD（中位绝对偏差）

```typescript
export function mad(values: number[]): number {
  const med = median(values);
  const absoluteDeviations = values.map(v => Math.abs(v - med));
  return median(absoluteDeviations);
}
```

MAD = median(|xᵢ - median(x)|)，衡量数据围绕中位数的离散程度。

比标准差（standardDeviation）对离群值更鲁棒：
- 标准差基于mean，受离群值影响大
- MAD基于median，对离群值鲁棒

MAD可以换算为等效标准差：σ ≈ 1.4826 × MAD（正态分布下的换算系数）。

### Standard Deviation（标准差）

```typescript
export function standardDeviation(values: number[]): number {
  const avg = mean(values);
  const squareDiffs = values.map(v => (v - avg) ** 2);
  return Math.sqrt(mean(squareDiffs));
}
```

注意这是**总体标准差**（除以N而非N-1）。

在ui-profiler中标准差使用较少，因为性能数据通常不正态分布（右偏——大部分测量较快，少量异常慢）。

## 时间格式化

**文件**: src/utils.ts:L17-L37

```typescript
export function formatTime(value: number): string {
  if (value < 1000) {
    return value.toFixed(2) + 'ms';
  } else if (value < 60000) {
    return (value / 1000).toFixed(2) + 's';
  } else {
    const minutes = Math.floor(value / 60000);
    const seconds = ((value % 60000) / 1000).toFixed(2);
    return `${minutes}m${seconds}s`;
  }
}
```

自动选择最合适的单位：
- < 1秒 → 毫秒（2位小数）
- < 1分钟 → 秒（2位小数）
- ≥ 1分钟 → 分+秒

## Δ指标计算

**文件**: src/table.tsx:L128-L146

CSS Benchmark中的Δ差异指标是核心解读工具：

```typescript
// 以TimingTable为例
const referenceIQM = Statistic.interQuartileMean(options.reference);
const referenceQ1 = Statistic.quartile(options.reference, 1);

// 对每一行结果
result['ΔIQM'] = Statistic.interQuartileMean(result.times) - referenceIQM;
result['ΔIQM%'] = (100 * result['ΔIQM']) / referenceIQM;
result['ΔQ1'] = Statistic.quartile(result.times, 1) - referenceQ1;
result['ΔQ1%'] = (100 * result['ΔQ1']) / referenceQ1;
```

### 为什么用2N次基线？

CSS Benchmark在开始测量前先执行2N次baseline：

```typescript
// src/styleBenchmarks.tsx
for (let i = 0; i < 2 * n; i++) {
  await scenario.run();
  baseline.push(performance.now() - t0);
  // ...
}
```

2N次基线取IQM作为reference，原因：
1. 前N次可能包含warm-up（JIT编译、缓存填充）
2. 2N次提供更稳定的统计基础
3. IQM会自动丢弃最快的25%（包含warm-up）和最慢的25%（包含噪声）

## 结果排序

### TimingTable排序

**文件**: src/table.tsx:L160-L174

```typescript
sortColumn: 'ΔIQM%'  // 默认排序列
```

默认按ΔIQM%降序排列，让影响最大的CSS规则/规则组排在最前面。

用户可以点击其他列头切换排序。

### ProfilerTable排序

**文件**: src/table.tsx:L251

```typescript
sortColumn: 'time'  // JS Profile结果按总时间排序
```

## 统计显著性判断

ui-profiler没有内置统计显著性检验（如t-test、Mann-Whitney U），但可以通过以下经验法则判断Δ是否有意义：

### 判断标准

| Δ值 | 统计显著性 | 行动建议 |
|-----|-----------|---------|
| \|Δ%\| < 5% | 不显著 | 噪声范围内，忽略 |
| 5% ≤ \|Δ%\| < 15% | 可能显著 | 增加repeats次数验证 |
| \|Δ%\| ≥ 15% | 很可能显著 | 需要关注 |
| \|Δ%\| ≥ 30% | 高度显著 | 强烈瓶颈，必须优化 |

### 验证方法

1. **增加repeats**：从默认3次增加到10次或更多，看Δ是否稳定
2. **反向测试**：先删除规则测一次，恢复后再删除再测一次，看结果是否一致
3. **多次运行**：关闭浏览器重新打开，重新运行benchmark，跨session对比
4. **检查MAD**：如果MAD很大（数据离散），Δ可能不可靠

## 常见统计陷阱

### 陷阱1：只看Mean

**错误**：mean = 100ms，比baseline的80ms慢了25%！
**真相**：可能是一次GC暂停导致mean偏高，median和IQM可能只有85ms（6%差异）

### 陷阱2：N=1得出结论

单次测量没有统计意义，至少3次（默认值），关键测量建议10次以上。

### 陷阱3：忽略warm-up效应

第一次执行通常明显偏慢（JIT、缓存、懒加载）。ui-profiler在setupSuite中预运行一次来消除这个效应。

### 陷阱4：在开发环境测量

开发模式（`jupyter lab --dev-mode`）包含未压缩代码、source map、HMR开销，性能特征与生产环境完全不同。**始终在生产构建上做性能测量**。

### 陷阱5：混淆Correlation和Causation

删除CSS规则A后操作变快了≠规则A本身是瓶颈。可能是：
- 规则A触发了重排，影响了相邻元素
- 删除规则A改变了CSSOM结构，加速了其他规则的匹配
- 规则A的选择器匹配了大量元素，删除后减少了匹配开销

需要进一步分析：看selector复杂度、bgMatches数量、影响的CSS属性（是否触发layout/paint）。

### 陷阱6：跨浏览器比较

Chrome和Firefox的CSS引擎不同，同一条规则在两个浏览器中的性能影响可能完全不同。JS Self-Profiling只在Chrome/Edge中可用。

## 结果导出

UI界面提供"Save to JSON"功能，可以将完整结果保存为JSON文件供后续分析。结果格式遵循 `IOutcome` 接口，包含所有原始times数据和聚合统计值。

可以使用Python/pandas等工具对导出的JSON进行更深入的统计分析。

## 相关概念

- (03-benchmarks.md
- (05-css-profiling.md
- (09-ui-and-visualization.md
- (../references/benchmarks-source.md
