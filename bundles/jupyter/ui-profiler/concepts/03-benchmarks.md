---
type: Concept
title: 六种 Benchmark 测量方法详解
description: 深入解析jupyterlab-ui-profiler的6种内置Benchmark：执行时间测量、CSS样式表/规则/规则组/规则使用分析和JS Self-Profiling的原理、配置和解读方法
tags: [jupyterlab, ui-profiler, benchmark, performance, css, profiling, execution-time]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: benchmark-ts
    resource: /references/benchmarks-source.md
    title: src/benchmark.ts 执行时间测量
  - id: stylebenchmarks-tsx
    resource: /references/benchmarks-source.md
    title: src/styleBenchmarks.tsx CSS benchmarks
  - id: jsbenchmarks-ts
    resource: /references/benchmarks-source.md
    title: src/jsBenchmarks.ts JS Self-Profiling
---

## Benchmark 概览

jupyterlab-ui-profiler 内置6种Benchmark，分为三大类：

| 类别 | Benchmark | ID | 核心原理 | 浏览器 |
|------|-----------|-----|---------|--------|
| 时间测量 | Execution Time | `execution-time` | `performance.now()`计时 | 全部 |
| CSS分析 | Style Sheets | `style-sheet` | 禁用样式表→测量→恢复 | 全部 |
| CSS分析 | Style Rules | `style-rule` | 删除单条规则→测量→恢复 | 全部 |
| CSS分析 | Style Rule Groups | `style-rule-group` | 分块删除规则→测量→恢复 | 全部 |
| CSS分析 | Style Rule Usage | `rule-usage` | MutationObserver+规则匹配 | 全部 |
| JS分析 | Profile JavaScript | `self-profile` | JS Self-Profiling API采样 | Chrome/Edge |

## Execution Time - 执行时间测量

**文件**: src/benchmark.ts:L141-L181
**ID**: `execution-time`
**配置Schema**: `repeats`（重复次数，默认3）

### 原理

最基础的Benchmark，使用浏览器的 `performance.now()` 高精度计时器（微秒级精度）测量Scenario执行的耗时。

执行流程：
1. `scenario.setupSuite()` - 套件级准备
2. `layoutReady()` - 等待浏览器完成布局
3. 执行N次循环：`setup()` → `performance.now()`记录开始 → `run()` → 记录耗时 → `cleanup()`
4. `layoutReady()` - 等待布局稳定
5. `scenario.cleanupSuite()` - 套件级清理
6. 返回结果

### 核心测量函数

```typescript
// src/benchmark.ts:L98-L139
async function benchmark(scenario, n = 3, inSuite = false, afterStep?) {
  if (!inSuite && scenario.setupSuite) await scenario.setupSuite();
  const times = [];
  for (let i = 0; i < n; i++) {
    if (scenario.setup) await scenario.setup();
    const start = performance.now();
    await scenario.run();
    times.push(performance.now() - start);
    if (scenario.cleanup) await scenario.cleanup();
    if (afterStep && !afterStep(i)) break;
  }
  if (!inSuite && scenario.cleanupSuite) await scenario.cleanupSuite();
  return { times, errors };
}
```

注意 `inSuite` 参数：当Benchmark内部需要多次调用benchmark()时（如先测baseline再测每个CSS规则），设为true以避免重复执行setupSuite/cleanupSuite。

### 结果字段

- `reference`: 基线时间数组（首次测量结果）
- `results[0].times`: 与reference相同（execution-time只有一组结果）
- `tags`: DOM标签计数（各HTML标签的数量）
- `totalTime`: 整个benchmark的总耗时

### 解读

Execution Time是所有其他CSS Benchmark的基础——其他Benchmark都在"删除/禁用某些CSS后"重新调用benchmark()测量，然后与reference比较计算差异。

## Style Sheets - 样式表级测量

**文件**: src/styleBenchmarks.tsx:L285-L386
**ID**: `style-sheet`
**配置Schema**: `repeats`（默认3）、`includePattern`（源文件名匹配正则）

### 原理

逐个禁用页面中的每个 `<style>` 样式表，测量禁用后Scenario执行时间的变化，从而定位哪个样式表对性能影响最大。

核心算法（减法测量法）：
1. 先执行2N次baseline测量（reference），获取正常状态下的执行时间
2. 遍历每个`<style>`元素：
   a. 提取CSS source map确定源文件名
   b. `sheet.disabled = true` 禁用样式表
   c. `layoutReady()` 等待浏览器重新计算样式
   d. 执行N次测量
   e. `sheet.disabled = false` 恢复样式表
   f. `layoutReady()` 等待恢复
3. 收集所有结果

### 结果字段

- `source`: source map解析出的源文件路径（如`webpack://./node_modules/package/style.css`）
- `content`: CSS内容（截断至500字符）
- `stylesheetIndex`: 样式表序号
- `times`: 禁用该样式表后的执行时间数组
- （表格计算）`ΔIQM%`: 相对于baseline的IQR均值变化百分比

### 解读

- **负Δ值**（ΔIQM% < 0）：禁用该样式表后执行变快，说明该样式表中的某些规则拖慢了性能
- **正Δ值**：禁用后变慢（通常因为禁用了关键样式导致布局抖动或fallback样式更昂贵）
- Δ值接近0：该样式表对此Scenario无显著影响
- `includePattern`可以过滤只看特定源文件（如设置为`my-extension`只看自己扩展的样式）

## Style Rules - 规则级测量

**文件**: src/styleBenchmarks.tsx:L388-L469
**ID**: `style-rule`
**配置Schema**: `repeats`（默认3）、`skipPattern`、`includePattern`

### 原理

比Style Sheets更细粒度——逐个删除每条CSS规则（`CSSStyleRule`），测量单条规则对性能的影响。

核心算法：
1. 执行2N次baseline获取reference
2. `collectRules()`收集所有CSSStyleRule（支持skip/include过滤）
3. 对每条规则：
   a. `sheet.deleteRule(ruleIndex)` 删除规则
   b. `layoutReady()`
   c. 执行N次测量
   d. `sheet.insertRule(rule.cssText, ruleIndex)` 精确恢复规则
   e. `layoutReady()`
4. 额外记录`bgMatches`：静态状态下`querySelectorAll(selector).length`

### collectRules 规则收集

**文件**: src/css.ts:L65-L108

```typescript
async function collectRules(styles, options): Promise<IRuleData[]> {
  const allRules = [];
  for (const style of styles) {
    const sheet = style.sheet;
    const cssMap = await extractSourceMap(style.textContent);
    const sourceName = cssMap ? cssMap.sources[0] : null;
    for (let i = 0; i < sheet.rules.length; i++) {
      const rule = sheet.rules[i];
      if (!(rule instanceof CSSStyleRule)) continue;  // 只保留样式规则
      // skip/include过滤...
      allRules.push({
        rule, selector: rule.selectorText, sheet,
        source: sourceName, ruleIndex: i, stylesheetIndex: j
      });
    }
  }
  return allRules;
}
```

只处理`CSSStyleRule`类型（普通样式规则），跳过`CSSMediaRule`、`CSSKeyframesRule`等。

### 结果字段

- `selector`: CSS选择器文本
- `source`: 源文件
- `ruleIndex`/`stylesheetIndex`: 位置索引
- `bgMatches`: 静态匹配元素数

### 解读

- **负Δ值**：该规则拖慢性能，需要优化
- **bgMatches高**：选择器匹配了大量元素（如`div`、`.lm-Widget`），可能过于宽泛
- **bgMatches=0 + 负Δ**：零匹配但仍有性能影响——可能是昂贵的选择器匹配过程本身慢（如深层嵌套、属性选择器）
- **bgMatches>0但Δ≈0**：规则匹配了元素但不影响此Scenario的性能

### interpretation

Benchmark内置了解读提示（JSX）：
> - `bgMatches`: how many elements matched the rule at standby; useful to find too broad rules or potentially unused rules with expensive selectors
> - Negative Δ highlights rules which may be deteriorating performance

## Style Rule Groups - 规则分组测量

**文件**: src/styleBenchmarks.tsx:L471-L583
**ID**: `style-rule-group`
**配置Schema**: `repeats`（默认3）、`minBlocks`（默认2）、`maxBlocks`（默认5）、`sheetRandomizations`（默认0）、`skipPattern`、`includePattern`
**自定义渲染**: `renderBlockResult`（特殊可视化）

### 原理

将所有CSS规则分成N个块，逐块删除测量，评估CSS代码分割（code splitting）对性能的影响。支持多次随机打乱规则顺序，排除规则顺序对结果的干扰。

核心算法：
1. 执行2N次baseline
2. 对每个randomization（0到randomizations次）：
   - 如果randomization>0，随机打乱styles顺序
   - collectRules()收集所有规则
   - 对每个分块数blocks（从minBlocks到maxBlocks）：
     - 计算每块规则数 rulesPerBlock = totalRules / blocks
     - 逐块：删除块内规则 → layoutReady → 测量N次 → 逆序恢复规则 → layoutReady
3. 收集不同分块策略的结果

### 解决的问题

这个Benchmark回答的问题是：**"如果我将CSS分成K个按需加载的文件，对性能有多大改善？"**

例如，如果分成5块时有显著负Δ（删除第3块性能提升30%），说明第3块中的规则对性能影响最大，应该优先异步加载或优化。

### 结果字段

- `rulesInBlock`: 该块包含的规则描述列表（selector数组）
- `block`: 块索引（0到blocks-1）
- `divisions`: 当前分块总数
- `randomization`: 随机化轮次（0=原始顺序）

## Style Rule Usage - 规则使用率分析

**文件**: src/styleBenchmarks.tsx:L78-L283
**ID**: `rule-usage`
**配置Schema**: `repeats`（默认3）、`skipPattern`、`includePattern`、`excludeMatchPattern`
**默认排序列**: `elementsSeen`

### 原理

这是最智能的CSS Benchmark，结合MutationObserver分析在Scenario执行过程中哪些CSS规则实际被使用（匹配到被修改的DOM节点），然后只对相关规则进行逐一测量。

两阶段设计：

**第一阶段 - 发现相关规则**：
1. 执行2N次reference基线
2. MutationObserver监听document.body的所有变化（subtree+childList+attributes）
3. 执行N次Scenario
4. 收集所有被修改的DOM节点（排除body本身）
5. 从受影响节点提取class names和element IDs
6. 通过selector字符串匹配（`.className`/`#id`子串匹配）找出相关CSS规则

**第二阶段 - 测量相关规则影响**：
1. 用MutationObserver记录规则匹配情况：
   - `touches`: 规则匹配被修改元素的次数
   - `elementsTouched`: 被修改子树中匹配规则的唯一元素数
   - `elementsSeen`: 整个页面中匹配规则的唯一元素数
2. 执行N次Scenario收集上述统计
3. 逐相关规则：删除→测量N次→恢复（同style-rule逻辑）

### 三个使用率指标

| 指标 | 含义 | 计算方式 |
|------|------|---------|
| `touchCount` | 规则匹配被修改元素的次数上限 | MutationObserver回调中对每个被修改节点检查matches() |
| `elementsTouched` | 被修改子树内匹配的唯一元素数 | RuleSetMap去重计数 |
| `elementsSeen` | 场景执行中全页面匹配的唯一元素数 | querySelectorAllAll + MutationObserver合并 |

### RuleSetMap 工具类

**文件**: src/styleBenchmarks.tsx:L58-L76

```typescript
class RuleSetMap<T = HTMLElement, S = string> extends Map<T, Set<S>> {
  add(element: T, rule: S): void { /* 添加元素-规则映射 */ }
  countRulesUsage(): Map<S, number> { /* 统计每条规则匹配的唯一元素数 */ }
}
```

这是一个双向索引结构：Element → Set<RuleSelector>，用于高效统计"哪些元素匹配了哪些规则"。

### 解读

- **elementsSeen低 + Δ≈0**：规则几乎没被使用且不影响性能，可以考虑删除
- **elementsSeen低 + 负Δ**：规则很少匹配但选择器匹配过程本身昂贵（如`*`通配符、复杂属性选择器）
- **elementsTouched高 + 负Δ大**：核心性能瓶颈，匹配了大量被操作的元素
- **touchCount高**：元素被反复修改且匹配该规则（如动画/频繁更新的元素）

## Profile JavaScript - JS函数级自检

**文件**: src/jsBenchmarks.ts:L116-L168
**ID**: `self-profile`
**配置Schema**: `repeats`（默认3）、`sampleInterval`（采样间隔）、`maxBufferSize`（缓冲区大小）、`scale`（'micro'|'macro'）
**能力检测**: `isAvailable: () => typeof window.Profiler !== 'undefined'`
**浏览器要求**: Chrome/Edge + 服务端`Document-Policy: js-profiling`头

### 原理

使用浏览器内置的 [JS Self-Profiling API](https://wicg.github.io/js-self-profiling/) 进行采样式CPU分析。与Chrome DevTools的Performance面板类似，但可以编程控制。

两种采样模式：
- **micro模式**（默认）：每次`scenario.run()`创建新的Profiler实例，run()结束后stop()获取trace。适合短操作，可看到每次run的独立profile
- **macro模式**：单个Profiler覆盖全部N次run，最后stop()获取一次trace。适合长操作序列

### 核心profile函数

**文件**: src/benchmark.ts:L16-L96

```typescript
async function profile(scenario, options, mode, afterMicroStep, n, inSuite) {
  // micro模式：每次run创建新profiler
  if (mode === 'micro') {
    for (let i = 0; i < n; i++) {
      profiler = new window.Profiler(options);
      await scenario.run();
      traces.push(await profiler.stop());
      if (!afterMicroStep(i)) break;
    }
  } else {
    // macro模式：一个profiler覆盖全部
    profiler = new window.Profiler(options);
    for (let i = 0; i < n; i++) {
      await scenario.run();
    }
    traces.push(await profiler.stop());
  }
  return { traces, errors, samplingInterval: profiler.sampleInterval, averageSampleInterval };
}
```

### Trace数据结构

```typescript
// src/browserProfiler.d.ts
interface ProfilerTrace {
  resources: string[];    // 资源URL（脚本文件），按resourceId索引
  frames: ProfilerFrame[]; // 函数帧：{name, resourceId?, line?, column?}
  stacks: ProfilerStack[]; // 调用栈：{parentId?, frameId} 形成树形结构
  samples: ProfilerSample[]; // 采样点：{timestamp, stackId?}
}
```

### 帧迭代与时间聚合

**文件**: src/jsBenchmarks.ts:L31-L114

`iterateFrames(trace)` 生成器遍历采样数据重建调用栈帧的生命周期：
1. 维护`runningFrames: Map<blockId, IFrameState>`记录当前活跃帧
2. 每个sample：对比当前栈与上一个栈，找出已退出的帧（出栈）
3. 对退出的帧yield `{duration, start, stackDepth, frameId}`
4. 新出现的帧加入runningFrames

`extractTimes(trace)` 聚合每个函数帧的总耗时：
```typescript
function extractTimes(trace): IFunctionTiming[] {
  const totalFrameTime = new Map();
  for (const frameData of iterateFrames(trace)) {
    totalFrameTime.set(frameId, (totalFrameTime.get(frameId) || 0) + frameData.duration);
  }
  return [...totalFrameTime.entries()].map(([frameId, time]) => ({
    resource: trace.resources[frame.resourceId],
    name: frame.name, line: frame.line, column: frame.column, time
  }));
}
```

### 浏览器兼容性

| 浏览器 | 是否支持 | 需要的HTTP头 |
|--------|---------|-------------|
| Chrome | ✅ | Document-Policy: js-profiling |
| Edge | ✅ | Document-Policy: js-profiling |
| Firefox | ❌ | 不支持JS Self-Profiling API |
| Safari | ❌ | 不支持JS Self-Profiling API |

服务端扩展自动设置了所需HTTP头（见(11-server-extension.md）。如果`isAvailable()`返回false，UI中"Profile JavaScript"选项会被禁用。

## Benchmark通用配置

所有时间型Benchmark共享的配置：
- `repeats`: 重复次数（默认3次）。次数越多统计越稳定，但总耗时越长。

CSS Benchmark额外支持：
- `skipPattern`: 跳过匹配的selector（正则字符串）
- `includePattern`: 只包含匹配的selector/源文件（正则字符串）

## 相关概念

- (05-css-profiling.md
- (06-js-profiling.md
- (08-statistics-and-results.md
- (../references/benchmarks-source.md
- (../references/api-tokens.md
