---
type: Reference
title: jupyterlab-ui-profiler 核心 API 与 Token 速查
description: jupyterlab-ui-profiler 的核心接口、Token、类和方法签名速查表，基于源码逐行提取
tags: [jupyterlab, ui-profiler, api, token, reference, typescript]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: tokens-ts
    resource: /references/api-tokens.md
    title: src/tokens.ts 核心类型定义
  - id: profiler-ts
    resource: /references/api-tokens.md
    title: src/profiler.ts UIProfiler类实现
  - id: benchmark-ts
    resource: /references/benchmarks-source.md
    title: src/benchmark.ts 基准测量核心函数
  - id: jsbenchmarks-ts
    resource: /references/benchmarks-source.md
    title: src/jsBenchmarks.ts JS自检profiling
---

## Token 注册

### IUIProfiler Token

```typescript
// src/tokens.ts:L226-L228
export const IUIProfiler = new Token<IUIProfiler>(
  '@jupyterlab/ui-profiler:plugin'
);
```

插件ID为 `@jupyterlab/ui-profiler:plugin`，其他扩展可通过 `requires: [IUIProfiler]` 依赖注入。

## 核心接口

### IScenario 场景接口

```typescript
// src/tokens.ts:L16-L65
export interface IScenario {
  id: string;                              // 唯一标识符
  name: string;                            // 用户可见名称
  run: () => Promise<void>;                // 场景执行函数
  setupSuite?: () => Promise<void>;        // 套件级准备（整个benchmark只执行一次）
  cleanupSuite?: () => Promise<void>;      // 套件级清理
  setup?: () => Promise<void>;             // 每次重复前准备
  cleanup?: () => Promise<void>;           // 每次重复后清理
  configSchema?: JSONSchema7;              // JSON Schema配置表单
  setOptions?: (options: any) => void;     // 接收用户配置
}
```

生命周期：`setupSuite()` → 循环N次 [`setup()` → `run()` → `cleanup()`] → `cleanupSuite()`

### IBenchmark<T> 基准接口

```typescript
// src/tokens.ts:L67-L108
export interface IBenchmark<T extends IOutcomeBase = IOutcomeBase> {
  id: string;                              // 唯一标识符
  name: string;                            // 用户可见名称
  run: (
    scenario: IScenario,
    options: any,
    progress?: Signal<any, IProgress>,
    stopSignal?: ISignal<any, void>
  ) => Promise<T>;                         // 执行基准测试
  configSchema: JSONSchema7;               // 配置JSON Schema
  render?: (props: { outcome: T }) => JSX.Element;  // 自定义结果渲染
  isAvailable?: () => boolean;             // 浏览器能力检测
  sortColumn?: string;                     // 默认排序列
  interpretation?: string | JSX.Element;   // 结果解读说明
}
```

泛型参数 `T` 为outcome类型，支持 `ITimingOutcome` 和 `IProfilingOutcome`。

### IUIProfiler 公共API

```typescript
// src/tokens.ts:L184-L221
export interface IUIProfiler {
  addScenario(scenario: IScenario): void;
  runBenchmark<T extends IOutcome = IOutcome>(
    scenario: { id: string; options: JSONObject },
    benchmark: { id: string; options: JSONObject }
  ): Promise<IBenchmarkResult<T>>;
  abortBenchmark(): void;
  readonly scenarioAdded: ISignal<IUIProfiler, IScenario>;
  readonly progress: ISignal<IUIProfiler, IProgress>;
  readonly benchmarks: IBenchmark[];
  readonly scenarios: IScenario[];
}
```

### IBenchmarkResult 结果结构

```typescript
// src/tokens.ts:L160-L179
export interface IBenchmarkResult<T extends IOutcome = IOutcome> {
  options: { scenario: JSONObject; benchmark: JSONObject };
  benchmark: string;                       // benchmark id
  scenario: string;                        // scenario id
  userAgent: string;
  hardwareConcurrency: number;             // CPU核心数
  completed: Date;
  windowSize: { width: number; height: number };
  id: string;                              // 唯一结果ID
  jupyter: IJupyterState;                  // JupyterLab状态
  outcome: T;                              // 测量结果
}

// src/tokens.ts:L6-L11
export interface IJupyterState {
  version: string;
  client: string;
  devMode: boolean;
  mode: DockPanel.Mode;                    // 'single-document' | 'multiple-document'
}
```

### 测量结果类型

```typescript
// src/tokens.ts:L110-L158
export interface ITimeMeasurement extends IMeasurement {
  times: number[];                         // 每次执行的耗时数组(ms)
}

export interface IProfileMeasurement extends IMeasurement {
  traces: ProfilerTrace[];                 // JS Profiler traces
  averageSampleInterval: number;           // 实际平均采样间隔
  samplingInterval: number;                // 配置的采样间隔
}

export interface ITimingOutcome<T extends ITimeMeasurement = ITimeMeasurement>
  extends IOutcomeBase<T> {
  reference: number[];                     // 基线测量时间数组
  type: 'time';
}

export interface IProfilingOutcome<T extends IProfileMeasurement = IProfileMeasurement>
  extends IOutcomeBase<T> {
  type: 'profile';
}

interface IOutcomeBase<T extends IMeasurement = IMeasurement> {
  results: T[];
  tags: Record<string, number>;            // DOM标签计数
  totalTime: number;                       // 总耗时(ms)
  type: string;
  interrupted: boolean;                    // 是否被用户中断
}
```

### 进度信号

```typescript
// src/tokens.ts:L124-L128
export interface IProgress {
  percentage: number;                      // 0-100
  interrupted?: boolean;
  errored?: boolean;
}
```

## 内置Benchmark ID

| ID | 名称 | 结果类型 | 文件 |
|----|------|---------|------|
| `execution-time` | Execution Time | ITimingOutcome | src/benchmark.ts |
| `style-sheet` | Style Sheets | ITimingOutcome<IStylesheetResult> | src/styleBenchmarks.tsx |
| `style-rule` | Style Rules | ITimingOutcome<IRuleResult> | src/styleBenchmarks.tsx |
| `style-rule-group` | Style Rule Groups | ITimingOutcome<IRuleBlockResult> | src/styleBenchmarks.tsx |
| `rule-usage` | Style Rule Usage | ITimingOutcome<IRuleResult> | src/styleBenchmarks.tsx |
| `self-profile` | Profile JavaScript | IProfilingOutcome | src/jsBenchmarks.ts |

## 内置Scenario ID

| ID | 名称 | 类名 | 文件 |
|----|------|------|------|
| `menuOpen` | Open Menu | MenuOpenScenario | src/scenarios.ts |
| `menuSwitch` | Switch Menu | MenuSwitchScenario | src/scenarios.ts |
| `tabSwitch` | Switch Tabs | SwitchTabScenario | src/scenarios.ts |
| `tabSwitchFocus` | Switch Tab Focus | SwitchTabFocusScenario | src/scenarios.ts |
| `sidebarOpen` | Open Sidebar | SidebarOpenScenario | src/scenarios.ts |
| `completer` | Completer | CompleterScenario | src/scenarios.ts |
| `scroll` | Scroll | ScrollScenario | src/scenarios.ts |
| `debugger` | Debugger | DebuggerScenario | src/scenarios.ts |
| `create-cells` | Create cells | CreateCellsScenario | src/scenarios.ts |
| `custom` | Custom Scenario | CustomScenario | src/scenarios.ts |

## 插件命令ID

```typescript
// src/index.ts:L27-L32
namespace CommandIDs {
  export const openProfiler = 'ui-profiler:open';
  export const waitForLayout = 'ui-profiler:wait-for-layout';
  export const waitForSelector = 'ui-profiler:wait-for-selector';
}
```

## UIProfiler 类方法

```typescript
// src/profiler.ts:L26-L138
class UIProfiler implements IUIProfiler {
  constructor(options: UIProfiler.IOptions);  // { app: JupyterFrontEnd, benchmarks: IBenchmark[] }
  addScenario(scenario: IScenario): void;
  runBenchmark<T>(scenario, benchmark): Promise<IBenchmarkResult<T>>;
  abortBenchmark(): void;
  get benchmarks(): IBenchmark[];
  get scenarios(): IScenario[];
  get scenarioAdded(): ISignal<IUIProfiler, IScenario>;
  get progress(): ISignal<IUIProfiler, IProgress>;
}
```

## 核心测量函数

```typescript
// src/benchmark.ts
async function benchmark(           // 执行时间测量
  scenario: IScenario,
  n?: number,                       // 重复次数，默认3
  inSuite?: boolean,                // 是否在套件内（跳过setupSuite/cleanupSuite）
  afterStep?: (step: number) => boolean
): Promise<ITimeMeasurement>;

async function profile(             // JS Self-Profiling
  scenario: IScenario,
  options: ProfilerInitOptions,     // { sampleInterval, maxBufferSize }
  mode: 'micro' | 'macro',          // micro:每次run创建新profiler; macro:单次profiler覆盖全部
  afterMicroStep: (step: number) => boolean,
  n?: number,
  inSuite?: boolean
): Promise<IProfileMeasurement>;
```

## 统计工具

```typescript
// src/statistics.ts:L3-L97
namespace Statistic {
  min(numbers: number[]): number;
  mean(numbers: number[]): number;
  percentile(numbers: number[], percentile: number): number;  // CDF-based方法
  quartile(numbers: number[], quartile: 1|2|3): number;
  standardDeviation(numbers: number[]): number;              // 校正样本标准差
  standardError(numbers: number[]): number;
  interQuartileMean(numbers: number[]): number;              // 四分位距均值(IQM)
  round(n: number, precision?: number): number;
  sum(numbers: number[]): number;
  kernelDensityEstimate(sample: number[], x: number, h?: number): number;  // KDE
}
```

## Dramaturg 自动化API

```typescript
// src/dramaturg.ts
export const page = {
  waitForSelector(selector, options): Promise<ElementHandle>;  // 等待元素状态
  press(key: string, options?): Promise<void>;                 // 模拟按键
  $(selector): Promise<ElementHandle | null>;                  // 查询元素
  type(selector, text, options?): Promise<void>;              // 输入文本
  click(selector): Promise<void>;                              // 点击元素
  focus(selector): Promise<void>;                              // 聚焦元素
  mouse: { wheel(deltaX, deltaY): Promise<void> };            // 鼠标滚轮
};

export class ElementHandle {
  constructor(element: Element);
  $(selector): Promise<ElementHandle | null>;
  click(): Promise<void>;
  focus(): Promise<void>;
  press(key, options?): Promise<void>;
  type(text, options?): Promise<void>;
  isVisible(): Promise<boolean>;
  waitForSelector(selector, options): Promise<ElementHandle>;
}

// 辅助函数
export function layoutReady(): Promise<void>;                   // 等待requestAnimationFrame
export function waitForScrollEnd(element, requiredRestTime): Promise<void>;
export function waitUntilDisappears(selector): Promise<void>;
```

waitForSelector支持四种状态：`'attached'`、`'detached'`、`'visible'`、`'hidden'`。

## CSS工具函数

```typescript
// src/css.ts
export async function collectRules(
  styles: HTMLStyleElement[],
  options: { skipPattern?: RegExp; includePattern?: RegExp }
): Promise<IRuleData[]>;               // 收集所有CSSStyleRule

export async function extractSourceMap(
  cssContent: string | null
): Promise<ISourceMap | null>;         // 提取CSS source map
```

## 服务端HTTP头

```python
# jupyterlab_ui_profiler/__init__.py:L26-L32
server_app.web_app.settings["headers"].update({
    "Cross-Origin-Opener-Policy": "same-origin",      # Firefox高精度时间
    "Cross-Origin-Embedder-Policy": "require-corp",   # Firefox高精度时间
    "Document-Policy": "js-profiling"                 # Chrome JS Self-Profiling
})
```

## 相关概念

- (../concepts/02-profiler-core.md
- (../concepts/03-benchmarks.md
- (../concepts/04-scenarios.md
- (../concepts/07-dramaturg-automation.md
- (../concepts/08-statistics-and-results.md
