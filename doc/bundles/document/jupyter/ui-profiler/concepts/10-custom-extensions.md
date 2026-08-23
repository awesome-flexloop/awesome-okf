---
type: Concept
title: 扩展开发：自定义 Benchmark 与 Scenario
description: 如何开发自定义Benchmark和Scenario扩展ui-profiler——插件集成模式、IBenchmark/IScenario接口实现、configSchema编写、结果渲染、以及扩展间通信
tags: [jupyterlab, ui-profiler, extension, plugin, custom-benchmark, custom-scenario, token]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: tokens-ts
    resource: /references/api-tokens.md
    title: src/tokens.ts 核心接口定义
  - id: profiler-ts
    resource: /references/api-tokens.md
    title: src/profiler.ts UIProfiler实现
  - id: index-ts
    resource: /references/api-tokens.md
    title: src/index.ts 插件入口
---

## 扩展架构概述

ui-profiler采用JupyterLab标准的Token依赖注入模式，允许第三方扩展：

1. **注册新的Benchmark**：通过`IUIProfiler` Token注入profiler实例，调用`addBenchmark()`
2. **注册新的Scenario**：通过`IUIProfiler` Token注入profiler实例，调用`addScenario()`
3. **使用profiler执行自定义测量**：调用`runBenchmark()`以编程方式执行性能测量
4. **监听执行事件**：通过`ran` Signal接收Benchmark执行结果

```
┌──────────────────────────────────────────────┐
│         第三方扩展（your-extension）           │
│                                              │
│  ┌─────────┐    ┌─────────┐                 │
│  │ Custom  │    │ Custom  │                 │
│  │Benchmark│    │Scenario │                 │
│  └────┬────┘    └────┬────┘                 │
│       │              │                       │
│       └──────┬───────┘                       │
│              │ requires: IUIProfiler         │
└──────────────┼───────────────────────────────┘
               │
┌──────────────┼───────────────────────────────┐
│     ui-profiler 核心                          │
│              ▼                               │
│       ┌──────────────┐                       │
│       │  UIProfiler  │ ← IUIProfiler Token   │
│       │  (核心类)     │                       │
│       └──────────────┘                       │
└──────────────────────────────────────────────┘
```

## IUIProfiler Token

**文件**: src/tokens.ts:L186-L228

要扩展ui-profiler，需要在你的插件中`requires` IUIProfiler Token：

```typescript
import { IUIProfiler } from '@jupyterlab/ui-profiler';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:profiler-plugin',
  autoStart: true,
  requires: [IUIProfiler],  // 注入profiler实例
  activate: (app: JupyterFrontEnd, profiler: IUIProfiler) => {
    // 注册自定义Benchmark或Scenario
    profiler.addBenchmark(myCustomBenchmark);
    profiler.addScenario(myCustomScenario);
  }
};
```

### IUIProfiler 公共API

```typescript
interface IUIProfiler {
  readonly benchmarks: ReadonlyArray<IBenchmark>;
  readonly scenarios: ReadonlyArray<IScenario>;
  readonly ran: ISignal<any, IBenchmarkResult>;

  addBenchmark(benchmark: IBenchmark): void;
  addScenario(scenario: IScenario): void;
  runBenchmark<T extends IOutcomeBase>(
    benchmark: IBenchmark<T>,
    scenario: IScenario,
    options?: JSONValue,
    progress?: Signal<any, IProgress>,
    stopSignal?: ISignal<any, void>
  ): Promise<T>;
  attachProfiler(node: HTMLElement): void;
}
```

## 开发自定义 Benchmark

### 最小Benchmark示例

```typescript
import { IBenchmark, ITimeMeasurement, ITimingOutcome } from '@jupyterlab/ui-profiler';

const myBenchmark: IBenchmark<ITimingOutcome> = {
  id: 'my-extension:my-benchmark',
  name: 'My Custom Benchmark',

  configSchema: {
    type: 'object',
    properties: {
      repeats: {
        type: 'integer',
        title: 'Number of repeats',
        default: 3,
        minimum: 1,
        maximum: 100
      }
    },
    required: ['repeats']
  } as JSONSchema7,

  async run(scenario, options, progress, stopSignal): Promise<ITimingOutcome> {
    const times: number[] = [];
    const n = options.repeats ?? 3;

    // Suite setup
    if (scenario.setupSuite) await scenario.setupSuite();

    for (let i = 0; i < n; i++) {
      // Check stop signal
      if (stopSignal?.stop) break;

      // Emit progress
      progress?.emit({
        message: `Iteration ${i + 1}/${n}`,
        percentage: Math.round((i / n) * 100)
      });

      // Scenario setup
      if (scenario.setup) await scenario.setup();
      await layoutReady();

      // Measure
      const t0 = performance.now();
      await scenario.run();
      const elapsed = performance.now() - t0;
      times.push(elapsed);

      // Scenario cleanup
      if (scenario.cleanup) await scenario.cleanup();
      await layoutReady();
    }

    // Suite cleanup
    if (scenario.cleanupSuite) await scenario.cleanupSuite();

    return {
      type: 'time-measurement',
      times,
      reference: [],  // Baseline measurements
      interrupted: stopSignal?.stop ?? false
    };
  }
};
```

### configSchema 编写指南

configSchema必须是有效的JSON Schema 7：

```typescript
configSchema: {
  type: 'object',
  title: 'My Benchmark Configuration',
  properties: {
    // 数字参数
    repeats: {
      type: 'integer',
      title: 'Repeats',
      description: 'Number of iterations to run',
      default: 3,
      minimum: 1,
      maximum: 100
    },
    // 枚举选择
    mode: {
      type: 'string',
      title: 'Mode',
      enum: ['fast', 'accurate'],
      default: 'fast',
      enumNames: ['Fast (lower precision)', 'Accurate (slower)']
    },
    // 布尔开关
    warmup: {
      type: 'boolean',
      title: 'Enable warmup run',
      default: true
    },
    // 嵌套对象
    advanced: {
      type: 'object',
      title: 'Advanced options',
      properties: {
        timeout: { type: 'number', title: 'Timeout (ms)', default: 5000 }
      }
    }
  },
  required: ['repeats']
} as JSONSchema7
```

### 自定义结果渲染（render方法）

默认情况下，Execution Time类型的Benchmark使用TimingTable渲染。如果你的Benchmark返回自定义Outcome类型，可以提供`render`方法：

```typescript
const myBenchmark: IBenchmark<IMyCustomOutcome> = {
  id: 'my-benchmark',
  name: 'My Benchmark',
  configSchema: { /* ... */ },
  run: async (scenario, options, progress, stopSignal) => { /* ... */ },

  render: (props: { outcome: IMyCustomOutcome }) => {
    return React.createElement('div', null,
      React.createElement('h3', null, 'Custom Result'),
      React.createElement('pre', null, JSON.stringify(props.outcome, null, 2))
    );
  },

  sortColumn: 'customMetric',  // 默认排序列

  interpretation: React.createElement('div', null,
    'This benchmark measures X. Lower values are better. ',
    'Values above Y indicate a performance issue.'
  )
};
```

### isAvailable 可用性检测

```typescript
isAvailable: () => {
  return 'IntersectionObserver' in window;  // 只在支持IntersectionObserver的浏览器中显示
}
```

如果isAvailable返回false，该Benchmark在UI中会置灰并显示不可用状态。

## 开发自定义 Scenario

### 最小Scenario示例

```typescript
import { IScenario } from '@jupyterlab/ui-profiler';

const myScenario: IScenario = {
  id: 'my-extension:my-scenario',
  name: 'My Custom Scenario',
  configSchema: {
    type: 'object',
    properties: {
      target: {
        type: 'string',
        title: 'Target element',
        default: '.my-widget'
      }
    }
  } as JSONSchema7,

  async setupSuite(options) {
    // 一次性准备：创建widget、打开文件等
  },

  async setup() {
    // 每次迭代前的准备：重置状态、聚焦等
  },

  async run() {
    // 核心操作：点击按钮、输入文本等
    // 注意：run()中不应该有手动计时，由Benchmark负责
    const button = document.querySelector('.my-button') as HTMLElement;
    button?.click();
  },

  async cleanup() {
    // 每次迭代后的清理：关闭弹窗、重置状态等
  },

  async cleanupSuite() {
    // 一次性清理：关闭widget、关闭文件等
  }
};
```

### Scenario生命周期详解

```
setupSuite()                    ← 整个benchmark开始前调用一次
  │
  ├── setup()                   ← 第1次迭代前
  │   └── run()                 ← 第1次测量（Benchmark在run()前后计时）
  │   └── cleanup()             ← 第1次迭代后
  ├── setup()                   ← 第2次迭代前
  │   └── run()                 ← 第2次测量
  │   └── cleanup()             ← 第2次迭代后
  ├── ... (重复n次)
  │
cleanupSuite()                  ← 整个benchmark结束后调用一次
```

**setupSuite vs setup的区分**：
- **setupSuite**：一次性操作，如创建Notebook widget、打开文件——这些操作开销大且不需要每次重复
- **setup/cleanup**：每次迭代的状态重置，如关闭弹窗、回到顶部、清空输入

### split 属性

```typescript
interface IScenario {
  // ...
  readonly split?: 'first' | 'all' | 'none';
}
```

`split`控制widget添加到JupyterLab shell的模式：
- `'first'`（默认）：第一个widget以split-right模式添加，后续添加到同一区域
- `'all'`：所有widget都split-right（分屏模式）
- `'none'`：不使用split模式

### setOptions 钩子

```typescript
async setOptions?(options: JSONObject, app: JupyterFrontEnd): Promise<void>;
```

在Benchmark开始前调用，允许Scenario验证/修改配置。例如：

```typescript
async setOptions(options, app) {
  // 强制使用Notebook编辑器
  options.editor = 'Notebook';
  // 验证配置
  if (options.count < 1) options.count = 1;
}
```

## Outcome 类型系统

**文件**: src/tokens.ts

ui-profiler定义了两种Outcome基类型：

### ITimeMeasurement（时序测量结果）

```typescript
interface ITimeMeasurement extends IOutcomeBase {
  type: 'time-measurement';
  times: number[];           // 每次迭代的耗时(ms)
  reference: number[];       // 基线耗时(ms)
  interrupted?: boolean;     // 是否被用户中断
}
```

### IProfilingOutcome（Profiling结果）

```typescript
interface IProfilingOutcome extends IOutcomeBase {
  type: 'profiling';
  traces: ProfilerTrace[];   // JS Self-Profiling trace数据
  times: number[];
  reference: number[];
  averageSampleInterval: number;
  interrupted?: boolean;
}
```

### 自定义Outcome类型

你可以定义自己的Outcome类型，但必须继承`IOutcomeBase`：

```typescript
interface IMyCustomOutcome extends IOutcomeBase {
  type: 'my-custom-type';
  customMetric: number[];
  details: { key: string; value: number }[];
}
```

需要同时提供对应的render方法来渲染结果。

## 编程式调用 Profiler

除了UI交互，你还可以在代码中直接调用profiler：

```typescript
// 获取已注册的benchmark和scenario
const benchmark = profiler.benchmarks.find(b => b.id === 'execution-time');
const scenario = profiler.scenarios.find(s => s.id === 'menuOpen');

if (benchmark && scenario) {
  // 执行测量
  const progress = new Signal<any, IProgress>({});
  const stopSignal = { stop: false };

  const result = await profiler.runBenchmark(
    benchmark,
    scenario,
    { menu: 'file', repeats: 5 },
    progress,
    stopSignal
  );

  console.log('IQM:', Statistic.interQuartileMean(result.times));
}
```

### 监听所有Benchmark结果

```typescript
profiler.ran.connect((sender, result) => {
  console.log(`Benchmark ${result.benchmark.id} completed`);
  console.log(`Scenario: ${result.scenario.id}`);
  console.log(`Outcome:`, result.outcome);
  // 可以将结果发送到监控服务、保存到文件等
});
```

## 实用模式

### 模式1：引用内置Scenario的setupSuite

如果你的Scenario与内置Scenario有相似的setup逻辑（比如都需要创建编辑器），可以参考`SingleEditorScenario`的模式——创建一个基类封装通用逻辑。

### 模式2：使用Dramaturg进行DOM操作

在自定义Scenario的run()方法中，使用ui-profiler导出的Dramaturg类进行DOM等待：

```typescript
import { Dramaturg } from '@jupyterlab/ui-profiler';

async run() {
  const dramaturg = new Dramaturg();
  await dramaturg.click('.my-button');
  await dramaturg.waitForSelector('.my-modal', { visible: true });
  await dramaturg.waitForLayout(document.querySelector('.my-modal'));
}
```

### 模式3：使用insertText

```typescript
import { insertText } from '@jupyterlab/ui-profiler';

async setup() {
  await insertText(app, 'print("hello")');
}
```

`insertText`自动适配Notebook/Console/File Editor三种编辑器。

### 模式4：使用layoutReady

```typescript
import { layoutReady } from '@jupyterlab/ui-profiler';

async run() {
  someElement.classList.add('active');
  await layoutReady();  // 等待浏览器处理样式变化
  // 现在测量或进行下一步操作
}
```

## 注意事项

1. **不要在run()中手动计时**：Benchmark负责在`scenario.run()`前后计时，Scenario只负责执行操作
2. **始终在DOM操作后等待**：点击按钮、修改DOM后需要`await layoutReady()`或Dramaturg的waitFor*，否则测量的是未完成状态
3. **cleanup要彻底**：每次迭代后的cleanup必须将UI恢复到与setup后相同的状态，否则后续迭代测量不准确
4. **setupSuite要幂等**：如果benchmark被多次运行，setupSuite不应该产生副作用（如创建重复的widget）
5. **id命名空间**：使用`your-extension:name`格式作为id，避免与其他扩展冲突
6. **configSchema默认值**：始终为配置项提供合理的default值
7. **处理中断**：在长循环中检查`stopSignal?.stop`，允许用户取消长时间运行的benchmark

## 相关概念

- (02-profiler-core.md
- (01-architecture-overview.md
- (07-dramaturg-automation.md
- (../examples/02-custom-scenario.md
- (../references/api-tokens.md
