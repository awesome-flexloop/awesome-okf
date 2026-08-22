---
type: Reference
title: Benchmark 源码分析参考
description: jupyterlab-ui-profiler 6种Benchmark的源码实现分析，包含执行时间测量、CSS样式表/规则/规则组/规则使用测量和JS Self-Profiling的详细实现机制
tags: [jupyterlab, ui-profiler, benchmark, css-profiling, js-profiling, source-analysis]
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
    title: src/styleBenchmarks.tsx CSS相关benchmark
  - id: jsbenchmarks-ts
    resource: /references/benchmarks-source.md
    title: src/jsBenchmarks.ts JS Self-Profiling
  - id: browser-profiler-dts
    resource: /references/benchmarks-source.md
    title: src/browserProfiler.d.ts 浏览器Profiler类型声明
---

## execution-time Benchmark

**文件**: src/benchmark.ts:L141-L181
**ID**: `execution-time`
**配置Schema**: src/schema/benchmark-execution.json

这是最基础的benchmark，使用 `performance.now()` 测量场景执行时间。

核心流程：
1. 调用 `scenario.setupSuite()` 进行套件级准备
2. 等待 `layoutReady()`（requestAnimationFrame）确保布局稳定
3. 调用 `benchmark()` 函数执行N次（默认3次）场景测量
4. 每次迭代执行 `setup()` → `performance.now()` 计时 → `run()` → 记录时间差 → `cleanup()`
5. 等待 `layoutReady()`
6. 调用 `scenario.cleanupSuite()`
7. 返回 `{ reference: times, results: [reference], tags, totalTime, type: 'time', interrupted }`

`benchmark()` 函数（src/benchmark.ts:L98-L139）是核心测量原语：
```typescript
async function benchmark(scenario, n = 3, inSuite = false, afterStep?) {
  if (!inSuite && scenario.setupSuite) await scenario.setupSuite();
  const times = [];
  for (let i = 0; i < n; i++) {
    if (scenario.setup) await scenario.setup();
    const start = performance.now();
    await scenario.run();
    times.push(performance.now() - start);
    if (scenario.cleanup) await scenario.cleanup();
    if (afterStep && !afterStep(i)) break;  // 支持中断
  }
  if (!inSuite && scenario.cleanupSuite) await scenario.cleanupSuite();
  return { times, errors };
}
```

支持通过 `stopSignal` 中断执行。结果使用 `renderTimings` 渲染（boxplot+表格）。

## style-sheet Benchmark

**文件**: src/styleBenchmarks.tsx:L285-L386
**ID**: `style-sheet`
**配置Schema**: src/schema/benchmark-sheet.json

测量禁用单个样式表后场景执行时间的变化。

核心算法（减法测量法）：
1. 先执行2N次baseline测量获取reference基线
2. 遍历所有 `<style>` 元素：
   a. 提取CSS source map确定源文件
   b. 如果有 `includePattern`，过滤不匹配的样式表
   c. 设置 `sheet.disabled = true` 禁用样式表
   d. 等待 `layoutReady()`
   e. 执行N次场景测量
   f. 设置 `sheet.disabled = false` 恢复样式表
   g. 等待 `layoutReady()`
3. 返回每个样式表的测量结果

结果包含字段：
- `content`: 样式表CSS内容（截断至500字符用于显示）
- `source`: source map解析出的源文件路径
- `stylesheetIndex`: 样式表索引
- `times`: 每次测量的耗时数组
- （由TimingTable计算）`min`, `mean`, `Q1`, `IQM`, `ΔIQM`, `ΔIQM%`, `ΔQ1`, `ΔQ1%`

## style-rule Benchmark

**文件**: src/styleBenchmarks.tsx:L388-L469
**ID**: `style-rule`
**配置Schema**: src/schema/benchmark-rule.json

逐规则测量CSS规则对性能的影响。比style-sheet更细粒度。

核心算法：
1. 执行2N次baseline获取reference
2. 使用 `collectRules()` 收集所有 `CSSStyleRule`（支持 `skipPattern`/`includePattern` 过滤）
3. 对每条CSS规则：
   a. `sheet.deleteRule(ruleIndex)` 删除规则
   b. 等待 `layoutReady()`
   c. 执行N次场景测量
   d. `sheet.insertRule(rule.cssText, ruleIndex)` 恢复规则
   e. 等待 `layoutReady()`
4. 额外记录 `bgMatches: document.querySelectorAll(rule.selector).length`（静态匹配元素数）

结果包含字段：
- `selector`: CSS选择器文本
- `source`: 源文件
- `ruleIndex`, `stylesheetIndex`: 位置索引
- `bgMatches`: 静态状态下匹配的元素数（识别过于宽泛的选择器）

**解读说明**（interpretation）：
- `bgMatches`高说明选择器过于宽泛或可能未使用但有昂贵选择器
- 负Δ值表示该规则可能拖慢性能

## style-rule-group Benchmark

**文件**: src/styleBenchmarks.tsx:L471-L583
**ID**: `style-rule-group`
**配置Schema**: src/schema/benchmark-rule-group.json
**自定义渲染**: `renderBlockResult`

将CSS规则分组成块，测量不同分块数对性能的影响。用于评估CSS代码分割策略。

核心算法：
1. 执行2N次baseline获取reference
2. 支持 `randomizations`（默认0）次随机打乱规则顺序
3. 对每个分块数 `blocks`（从 `minBlocks` 到 `maxBlocks`，默认2-5）：
   a. 计算每块规则数 `rulesPerBlock = allRules.length / blocks`
   b. 逐块删除规则 → 测量 → 逆序恢复规则
4. 结果包含 `rulesInBlock`（该块包含哪些规则）、`block`（块索引）、`divisions`（总分块数）、`randomization`（随机化轮次）

这个benchmark回答的问题："将CSS分成多少个按需加载的块，性能最优？"

## rule-usage Benchmark

**文件**: src/styleBenchmarks.tsx:L78-L283
**ID**: `rule-usage`
**配置Schema**: src/schema/benchmark-rule-usage.json
**默认排序列**: `elementsSeen`

最复杂的CSS benchmark，结合MutationObserver分析哪些CSS规则实际被场景使用。

两阶段设计：

**第一阶段 - 发现相关规则**：
1. 执行2N次reference基线
2. 使用MutationObserver监听document.body的所有变化（subtree+childList+attributes）
3. 执行N次场景，收集所有被修改的DOM节点
4. 从受影响节点提取class names和IDs
5. 通过selector字符串匹配（`.className`/`#id`）找出相关CSS规则

**第二阶段 - 测量相关规则影响**：
1. 使用MutationObserver记录规则匹配情况：
   - `touches`: 规则匹配被修改元素的次数
   - `elementsTouched`: 被修改子树中匹配规则的唯一元素数
   - `elementsSeen`: 整个页面中匹配规则的唯一元素数
2. 执行N次场景收集上述统计
3. 逐规则删除→测量→恢复（同style-rule）

结果包含三个使用度指标：
- `touchCount`: 规则匹配被修改元素的次数上限
- `elementsTouched`: 场景执行中被修改子树内匹配的元素数
- `elementsSeen`: 场景执行期间整个页面匹配的元素数

**解读说明**：
- `elementsSeen`低 → 可能是未使用的规则
- 负Δ值 → 该规则可能拖慢性能

## self-profile Benchmark

**文件**: src/jsBenchmarks.ts:L116-L168
**ID**: `self-profile`
**配置Schema**: src/schema/benchmark-profile.json
**能力检测**: `isAvailable: () => typeof window.Profiler !== 'undefined'`
**自定义渲染**: `renderProfile`

使用浏览器JS Self-Profiling API进行函数级CPU采样分析。

支持两种模式：
- **micro模式**（src/benchmark.ts:L35-L56）：每次run创建新Profiler实例，stop后获取trace，适合短操作
- **macro模式**（src/benchmark.ts:L57-L74）：单个Profiler覆盖全部N次run，适合长操作序列

trace解析（src/jsBenchmarks.ts:L31-L114）：
- `iterateFrames(trace)` 生成器：遍历ProfilerTrace的samples，通过stackId→parentId链重建调用栈，计算每个帧的持续时间
- `extractTimes(trace)`：聚合每个frameId的总时间，关联frame的name/resource/line/column信息

ProfilerTrace结构（src/browserProfiler.d.ts）：
```typescript
interface ProfilerTrace {
  resources: ProfilerResource[];  // 资源URL数组（按resourceId索引）
  frames: ProfilerFrame[];         // 函数帧（name, resourceId?, line?, column?）
  stacks: ProfilerStack[];         // 调用栈（parentId?, frameId）
  samples: ProfilerSample[];       // 采样点（timestamp, stackId?）
}
```

**浏览器要求**：
- Chrome/Chromium-based浏览器（Edge也支持）
- 需要服务端设置 `Document-Policy: js-profiling` HTTP头
- Firefox不支持此API
- Safari不支持此API

结果渲染分为macro trace视图（函数耗时汇总表）和micro details视图（调用栈详情）。

## CSS Source Map 解析

**文件**: src/css.ts:L37-L63

`extractSourceMap()` 函数支持两种source map嵌入方式：
1. **Base64内联**: `/*# sourceMappingURL=data:application/json;base64,... */` → `atob()`解码后JSON.parse
2. **外部URL**: `/*# sourceMappingURL=url */` → fetch获取后JSON.parse

解析出的 `ISourceMap` 遵循 [Source Map Revision 3](https://sourcemaps.info/spec.html) 规范。

## 规则收集

**文件**: src/css.ts:L65-L108

`collectRules()` 遍历所有 `<style>` 元素的 `sheet.rules`，只保留 `CSSStyleRule` 类型（排除CSSMediaRule等），支持skip/include正则过滤。每条规则记录：
- `rule`: CSSStyleRule对象
- `selector`: selectorText
- `sheet`: 所属CSSStyleSheet
- `source`: source map解析出的源文件名
- `ruleIndex`: 在stylesheet中的索引
- `stylesheetIndex`: 样式表序号

## 相关概念

- (../concepts/03-benchmarks.md
- (../concepts/05-css-profiling.md
- (../concepts/06-js-profiling.md
- (api-tokens.md
