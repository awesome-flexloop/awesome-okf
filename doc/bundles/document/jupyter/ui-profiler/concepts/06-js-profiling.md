---
type: Concept
title: JS Self-Profiling 与浏览器要求
description: 详解JS Self-Profiling API的工作原理、micro/macro两种采样模式、trace数据结构、浏览器兼容性要求，以及服务端HTTP头配置
tags: [jupyterlab, ui-profiler, javascript, profiling, self-profiling, chrome, performance]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: jsbenchmarks-ts
    resource: /references/benchmarks-source.md
    title: src/jsBenchmarks.ts JS Profiling实现
  - id: benchmark-ts
    resource: /references/benchmarks-source.md
    title: src/benchmark.ts profile函数
  - id: browser-profiler-dts
    resource: /references/benchmarks-source.md
    title: src/browserProfiler.d.ts 类型声明
  - id: init-py
    resource: /references/api-tokens.md
    title: jupyterlab_ui_profiler/__init__.py HTTP头配置
---

## 什么是 JS Self-Profiling

JS Self-Profiling 是 [WICG](https://wicg.github.io/js-self-profiling/) 提出的浏览器标准API，允许网页以编程方式对JavaScript执行进行采样式CPU性能分析，类似于Chrome DevTools Performance面板中的JavaScript Profiler，但可以自动化、持续运行。

### 与DevTools Profiler的区别

| 特性 | JS Self-Profiling | DevTools Profiler |
|------|------------------|-------------------|
| 触发方式 | JavaScript API | 用户手动操作 |
| 自动化 | ✅ 可脚本化 | ❌ 手动 |
| 开销 | 低（采样式） | 较高 |
| 适用场景 | CI性能回归测试、RUM真实用户监控 | 开发调试 |
| 数据粒度 | 函数级（name+line+column） | 函数级+更多细节 |
| 浏览器支持 | Chrome/Edge（需要特殊HTTP头） | 所有浏览器DevTools |

## 浏览器API

### window.Profiler

**文件**: src/browserProfiler.d.ts

```typescript
interface Profiler extends EventTarget {
  readonly stopped: boolean;
  readonly sampleInterval: DOMHighResTimeStamp;  // 实际采样间隔
  new (options: ProfilerInitOptions): Profiler;
  stop(): Promise<ProfilerTrace>;
}

interface ProfilerInitOptions {
  sampleInterval: DOMHighResTimeStamp;  // 期望采样间隔（ms）
  maxBufferSize: number;                // 最大缓冲区大小（采样点数）
}
```

使用方法：
```javascript
const profiler = new window.Profiler({
  sampleInterval: 1,    // 每1ms采样一次
  maxBufferSize: 10000  // 最多10000个采样点
});

// ... 执行要分析的代码 ...

const trace = await profiler.stop();
// trace包含完整的采样数据
```

### ProfilerTrace 数据结构

```typescript
interface ProfilerTrace {
  resources: ProfilerResource[];   // ["https://example.com/app.js", ...]
  frames: ProfilerFrame[];         // 函数帧表
  stacks: ProfilerStack[];         // 调用栈表（树形结构）
  samples: ProfilerSample[];       // 采样点序列
}

interface ProfilerFrame {
  readonly name: string;           // 函数名
  readonly resourceId?: number;    // 对应resources数组的索引
  readonly line?: number;          // 行号
  readonly column?: number;        // 列号
}

interface ProfilerStack {
  readonly parentId?: number;     // 父栈帧ID（undefined=根）
  readonly frameId: number;       // 函数帧ID
}

interface ProfilerSample {
  readonly timestamp: DOMHighResTimeStamp;
  readonly stackId?: number;      // 对应stacks数组的索引（undefined=空栈）
}
```

数据采用**结构数组**（Structure of Arrays）格式而非数组结构（Array of Structures），以减少内存开销。通过索引关联：samples→stacks→frames→resources。

### 调用栈重建

stacks通过parentId形成一棵树：
```
stacks: [
  { frameId: 0 },                    // stackId=0: root (run)
  { frameId: 1, parentId: 0 },       // stackId=1: run → scenarioRun
  { frameId: 2, parentId: 1 },       // stackId=2: run → scenarioRun → handler
  { frameId: 3, parentId: 0 },       // stackId=3: run → layoutReady
]
```

从任意stackId出发，沿着parentId向上追溯即可得到完整调用栈。

## 浏览器兼容性与要求

### 浏览器支持

| 浏览器 | 是否支持 | 版本要求 |
|--------|---------|---------|
| Chrome | ✅ | 94+ |
| Edge | ✅ | 94+ |
| Firefox | ❌ | 不支持 |
| Safari | ❌ | 不支持 |

### HTTP头要求

出于安全考虑，JS Self-Profiling API 需要服务端发送特殊的HTTP响应头才能启用：

```
Document-Policy: js-profiling
```

此外，为了在Firefox中获得高精度`performance.now()`测量（跨源隔离），还需要：

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

### 服务端扩展自动配置

**文件**: jupyterlab_ui_profiler/__init__.py:L24-L32

jupyterlab-ui-profiler的Python服务端扩展自动设置这些HTTP头：

```python
def _load_jupyter_server_extension(server_app):
    if "headers" not in server_app.web_app.settings:
        server_app.web_app.settings["headers"] = {}
    server_app.web_app.settings["headers"].update({
        "Cross-Origin-Opener-Policy": "same-origin",
        "Cross-Origin-Embedder-Policy": "require-corp",
        "Document-Policy": "js-profiling"
    })
```

### 禁用服务端扩展

如果这些HTTP头不适合你的部署环境（例如嵌入在iframe中、跨域资源问题），可以禁用服务端扩展：

```bash
jupyter server extension disable jupyterlab_ui_profiler
```

禁用后：
- Execution Time和所有CSS Benchmark**仍然可用**
- Profile JavaScript Benchmark将不可用（`isAvailable()`返回false）
- Firefox中的高精度时间测量可能降级

### 能力检测

```typescript
// src/jsBenchmarks.ts:L166
isAvailable: () => typeof window.Profiler !== 'undefined'
```

如果浏览器不支持或HTTP头未设置，UI中"Profile JavaScript"选项会被置灰或不显示。

## Micro vs Macro 采样模式

### Micro模式（默认）

**文件**: src/benchmark.ts:L35-L56

每次`scenario.run()`创建一个新的Profiler实例，stop()后获取独立的trace：

```typescript
if (mode === 'micro') {
  for (let i = 0; i < n; i++) {
    if (scenario.setup) await scenario.setup();
    profiler = new window.Profiler(options);
    await scenario.run();
    traces.push(await profiler.stop());
    if (scenario.cleanup) await scenario.cleanup();
    if (!afterMicroStep(i)) break;
  }
}
```

- **优点**：可以看到每次run的独立profile，便于对比多次执行的一致性
- **缺点**：Profiler创建/停止有开销；setup/cleanup不在profile中
- **适用**：短操作（<100ms），需要观察单次执行细节

### Macro模式

**文件**: src/benchmark.ts:L57-L74

一个Profiler覆盖全部N次run，最后stop()获取一次trace：

```typescript
else {
  profiler = new window.Profiler(options);
  for (let i = 0; i < n; i++) {
    if (scenario.setup) await scenario.setup();
    await scenario.run();
    if (scenario.cleanup) await scenario.cleanup();
  }
  traces.push(await profiler.stop());
}
```

- **优点**：减少Profiler创建开销；包含setup/run/cleanup完整流程；看到全局热点
- **缺点**：多次run的profile混合在一起
- **适用**：长操作序列、需要看整体CPU分布

## Trace解析：帧迭代算法

**文件**: src/jsBenchmarks.ts:L31-L90

`iterateFrames(trace)`是核心的trace解析生成器，它遍历采样点序列，重建每个函数帧的进入和退出时机，计算每个帧的持续时间。

### 算法原理

```typescript
export function* iterateFrames(trace: ProfilerTrace): Generator<IFrameLocation> {
  let runningFrames: Map<string, IFrameState> = new Map();

  for (const sample of trace.samples) {
    const now = sample.timestamp;
    const activeFrames = new Map<string, IFrameState>();

    // 1. 从当前sample的stackId出发，遍历栈链构建活跃帧集合
    if (typeof sample.stackId !== 'undefined') {
      let stack = trace.stacks[sample.stackId];
      let depth = 0;
      while (stack) {
        // inverseDepth用于区分同一函数在栈不同层级的出现
        const blockId = stack.frameId + '-' + inverseDepth;
        activeFrames.set(blockId,
          runningFrames.get(blockId) ?? { start: now, stackDepth: inverseDepth, frameId: stack.frameId }
        );
        stack = typeof stack.parentId !== 'undefined' ? trace.stacks[stack.parentId] : null;
        depth++;
      }
    }

    // 2. 找出已退出的帧（上一帧活跃但当前帧不活跃）
    const completedFrames = [...previouslyRunning].filter(a => !activeFrames.has(a));
    for (const frameId of completedFrames) {
      const state = runningFrames.get(frameId)!;
      yield { duration: now - state.start, ...state };
      runningFrames.delete(frameId);
    }

    runningFrames = activeFrames;
  }
}
```

关键点：
- 使用`blockId = frameId + '-' + inverseDepth`区分递归调用中同一函数的不同栈层级
- `inverseDepth`从叶节点往根节点计算，保证同一递归深度的帧有一致ID
- 每个sample对比前一sample的活跃帧集合，差集就是该帧时间区间内退出的帧
- yield的duration是从帧"入栈"到"出栈"的时间差（包含子函数执行时间）

### 函数耗时聚合

**文件**: src/jsBenchmarks.ts:L92-L114

```typescript
export function extractTimes(trace: ProfilerTrace): IFunctionTiming[] {
  const totalFrameTime: Map<number, number> = new Map();
  for (const frameData of iterateFrames(trace)) {
    totalFrameTime.set(
      frameData.frameId,
      (totalFrameTime.get(frameData.frameId) || 0) + frameData.duration
    );
  }
  return [...totalFrameTime.entries()].map(([frameId, time]) => {
    const frame = trace.frames[frameId];
    return {
      resource: typeof frame.resourceId !== 'undefined' ? trace.resources[frame.resourceId] : undefined,
      name: frame.name,
      column: frame.column,
      line: frame.line,
      time
    };
  });
}
```

聚合每个frameId的总耗时，然后关联函数名、源文件、行号列号信息。这是"Self Time"还是"Total Time"？注意：iterateFrames计算的是从帧入栈到出栈的时间，这包含了子函数执行时间，因此是**Total Time**（总时间/包含时间）。

### 采样间隔统计

profile()函数还计算实际平均采样间隔：

```typescript
// src/benchmark.ts:L82-L94
averageSampleInterval: Statistic.mean(
  traces
    .map(trace => {
      let previous = trace.samples[0].timestamp;
      const intervals = [];
      for (const sample of trace.samples.slice(1)) {
        intervals.push(sample.timestamp - previous);
        previous = sample.timestamp;
      }
      return intervals;
    })
    .flat()
)
```

实际采样间隔可能高于请求的`sampleInterval`（主线程繁忙时采样会被延迟），这个指标用于评估profile数据的质量。

## 配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `repeats` | number | 3 | 重复次数 |
| `sampleInterval` | number | 1 | 采样间隔(ms)，实际可能更高 |
| `maxBufferSize` | number | 10000 | 最大采样点缓冲区大小 |
| `scale` | 'micro' \| 'macro' | 'micro' | 采样模式 |

### sampleInterval选择建议

- **1ms**（默认）：细粒度分析，适合找热点函数
- **10ms**：粗粒度，降低开销，适合长时间监控
- 实际间隔受主线程负载影响，可能远大于设定值

### maxBufferSize注意事项

如果trace超过maxBufferSize，旧的采样点会被丢弃。对于长时间macro模式运行，需要增大此值。

## 实际使用建议

### 识别JavaScript热点

1. 使用micro模式运行短Scenario（如"Open Menu"）
2. 查看结果表中`time`最高的函数
3. 通过`resource`列定位到源文件
4. 通过`line`/`column`定位到具体代码行
5. 📦前缀表示node_modules中的第三方库

### 性能回归测试

将Profile JavaScript Benchmark集成到CI中：
1. 固定repeats次数
2. 保存trace结果
3. 对比PR前后关键函数的耗时变化
4. 设定阈值告警

### 注意事项

1. **采样偏差**：采样式profiling不保证捕获所有函数调用，极短函数可能被遗漏
2. **内联函数**：JIT编译器内联的短小函数可能不出现在trace中
3. **优化影响**：浏览器JIT优化可能改变函数内联和调用栈，影响结果
4. **开销**：Profiling本身有~5%性能开销，测量结果不是"无profiler时的真实性能"
5. **跨浏览器**：只在Chrome/Edge中可用，Firefox/Safari需要其他方法

## 相关概念

- (03-benchmarks.md
- (08-statistics-and-results.md
- (11-server-extension.md
- (../references/benchmarks-source.md
