---
type: Concept
title: Profiler 核心类与 Token 依赖注入
description: UIProfiler核心类的实现细节、IUIProfiler Token的依赖注入机制、Signal信号通信、命令注册，以及如何从其他扩展与Profiler交互
tags: [jupyterlab, ui-profiler, profiler, token, dependency-injection, signal, lumino]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: profiler-ts
    resource: /references/api-tokens.md
    title: src/profiler.ts UIProfiler类实现
  - id: tokens-ts
    resource: /references/api-tokens.md
    title: src/tokens.ts Token和接口定义
  - id: index-ts
    resource: /references/api-tokens.md
    title: src/index.ts 插件注册和命令
---

## IUIProfiler Token 与依赖注入

JupyterLab 使用 Lumino 的 Token 机制实现依赖注入（DI）。每个可被其他扩展依赖的服务都需要一个唯一的Token。

**文件**: src/tokens.ts:L226-L228

```typescript
export const IUIProfiler = new Token<IUIProfiler>(
  '@jupyterlab/ui-profiler:plugin'
);
```

Token字符串 `'@jupyterlab/ui-profiler:plugin'` 是全局唯一标识符，与plugin的id一致。其他扩展通过在`requires`或`optional`中引用此Token来获取Profiler实例：

```typescript
const myPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:my-plugin',
  autoStart: true,
  requires: [IUIProfiler],  // 依赖Profiler
  activate: (app: JupyterFrontEnd, profiler: IUIProfiler) => {
    // 使用profiler实例
    profiler.addScenario(myScenario);
  }
};
```

## UIProfiler 类详解

**文件**: src/profiler.ts:L26-L138

`UIProfiler` 是 `IUIProfiler` 接口的唯一实现，它管理Benchmark和Scenario的注册、查找和执行。

### 构造函数

```typescript
class UIProfiler implements IUIProfiler {
  constructor(protected options: UIProfiler.IOptions);
}

namespace UIProfiler {
  export interface IOptions {
    app: JupyterFrontEnd;    // JupyterLab应用实例
    benchmarks: IBenchmark[]; // 预注册的Benchmark列表
  }
}
```

构造函数只做一件事：保存options。Benchmark通过构造函数传入（而非addBenchmark方法），这意味着核心Benchmark在插件激活时一次性注册，而Scenario通过`addScenario()`动态添加。

### Scenario 管理

```typescript
// 注册新Scenario
addScenario(scenario: IScenario): void {
  this._scenarios.push(scenario);
  this._scenarioAdded.emit(scenario);  // 通知UI更新
}

// 只读访问
get scenarios(): IScenario[] { return this._scenarios; }
get benchmarks(): IBenchmark[] { return this.options.benchmarks; }
```

Scenario存储在私有数组`_scenarios`中，通过`scenarioAdded`信号通知订阅者（UI组件）有新Scenario可用。这是Lumino Signal的典型用法——数据变更时emit信号，UI自动响应更新。

### runBenchmark 核心执行方法

```typescript
async runBenchmark<T extends IOutcome = ITimingOutcome | IProfilingOutcome>(
  scenario: { id: string; options: JSONObject },
  benchmark: { id: string; options: JSONObject }
): Promise<IBenchmarkResult<T>>
```

执行流程逐行解析：

**1. 查找Benchmark和Scenario**（L71-L80）：
```typescript
const benchmarkRunner = this.options.benchmarks.find(b => b.id === benchmark.id);
if (!benchmarkRunner) throw Error(`Benchmark with id ${benchmark} not found`);
const scenarioInstance = this._scenarios.find(s => s.id === scenario.id);
if (!scenarioInstance) throw Error(`Scenario with id ${scenario} not found`);
```

**2. 传入Scenario配置**（L82-L84）：
```typescript
if (scenarioInstance.setOptions) {
  scenarioInstance.setOptions(scenario.options);
}
```
在运行前将用户配置传给Scenario（如选择哪个菜单、设置滚动距离等）。

**3. 执行Benchmark**（L85-L91）：
```typescript
this._progress.emit({ percentage: 0 });
const result = await benchmarkRunner.run(
  scenarioInstance,
  benchmark.options,
  this._progress,       // 进度信号
  this._abortBenchmark  // 中止信号
) as T;
```
注意：Profiler将自己的_progress和_abortBenchmark信号传递给Benchmark，Benchmark在执行过程中通过这些信号报告进度和检查中止状态。

**4. 收集环境信息**（L92-L113）：
```typescript
const data = {
  outcome: result,
  options: { benchmark: benchmark.options, scenario: scenario.options },
  benchmark: benchmark.id,
  scenario: scenario.id,
  userAgent: window.navigator.userAgent,
  hardwareConcurrency: window.navigator.hardwareConcurrency,
  completed: new Date(),
  windowSize: { width: window.innerWidth, height: window.innerHeight },
  jupyter: this.getJupyterState()
};
```

**5. 生成结果ID并返回**（L114-L117）：
```typescript
return { ...data, id: benchmarkId(data) };
```
ID格式：`{benchmarkId}_{scenarioId}_{ISO时间戳}`（L18-L24）。

### 中止机制

```typescript
abortBenchmark(): void {
  this._abortBenchmark.emit();
}
```

通过Signal实现松耦合的中止机制：Profiler发出abort信号，Benchmark在其run()方法中connect这个信号，在每次迭代后检查是否需要停止。以executionTimeBenchmark为例（src/benchmark.ts:L151-L155）：

```typescript
let stop = false;
const stopListener = () => { stop = true; };
stopSignal?.connect(stopListener);
// ...在afterStep回调中检查stop状态
reference = await benchmark(scenario, n, true, i => {
  progress?.emit({ percentage: (100 * (i + 1)) / n });
  return !stop;  // 返回false时停止迭代
});
```

### 进度报告

进度通过`_progress`信号传递，值为`IProgress`对象：
- `{ percentage: 0 }` - 开始
- `{ percentage: 50 }` - 进行中（具体含义由Benchmark定义）
- `{ percentage: 100 }` - 完成
- `{ percentage: NaN, interrupted: true }` - 被中止
- `{ percentage: N, errored: true }` - 出错

### Jupyter状态采集

```typescript
protected getJupyterState(): IJupyterState {
  return {
    client: app.name,                                    // 'JupyterLab'
    version: app.version,                                // 版本号
    devMode: PageConfig.getOption('devMode') === 'true', // 是否开发模式
    mode: PageConfig.getOption('mode') as DockPanel.Mode // 'single-document'|'multiple-document'
  };
}
```

使用`PageConfig`从页面配置中读取JupyterLab部署信息，这些信息被记录在结果中用于跨环境对比。

## 三个Signal详解

UIProfiler暴露三个Lumino Signal：

| Signal | 类型 | 触发时机 | 用途 |
|--------|------|---------|------|
| `scenarioAdded` | `ISignal<IUIProfiler, IScenario>` | addScenario()调用后 | UI刷新Scenario下拉列表 |
| `progress` | `ISignal<IUIProfiler, IProgress>` | Benchmark执行过程中 | UI更新进度条 |
| `_abortBenchmark` | `Signal<UIProfiler, void>` | abortBenchmark()调用后 | Benchmark停止执行（内部） |

Lumino Signal的使用模式（以progress为例）：

```typescript
// 发送方（Profiler）
private _progress: Signal<UIProfiler, IProgress> = new Signal(this);
get progress(): ISignal<IUIProfiler, IProgress> { return this._progress; }
this._progress.emit({ percentage: 50 });

// 接收方（Benchmark内部）
progress?.emit({ percentage: value });

// 接收方（UI组件）
profiler.progress.connect((sender, progress) => {
  updateProgressBar(progress.percentage);
});
```

关键设计：`_progress`是private的Signal实例，通过public的getter返回`ISignal`（只读接口），外部只能connect不能emit，封装了信号发送权限。

## 命令系统

**文件**: src/index.ts:L27-L153

interfacePlugin注册了三个命令：

### ui-profiler:open

打开UI Profiler面板。使用Widget单例模式：
```typescript
if (!lastWidget || lastWidget.isDisposed) {
  widget = createWidget();  // 创建新widget
} else {
  widget = lastWidget;      // 复用已有widget
}
```

Widget管理：
- `MainAreaWidget<UIProfilerWidget>` 包装在主区域
- `WidgetTracker` 跟踪widget实例用于布局恢复
- `ILayoutRestorer` 支持刷新页面后恢复profiler面板状态
- Launcher卡片在"Other"分类，rank=1（最前面）

### ui-profiler:wait-for-layout

等待一个layoutReady（requestAnimationFrame）。这是一个辅助命令，主要供E2E测试和外部自动化使用。

### ui-profiler:wait-for-selector

等待指定CSS选择器达到指定状态。参数：
```typescript
{
  selector: string;              // CSS选择器
  state?: 'visible'|'hidden'|'attached'|'detached';  // 默认'visible'
}
```

这个命令暴露了Dramaturg的waitForSelector能力给外部自动化脚本使用。

## UI Widget 创建

**文件**: src/index.ts:L83-L91

```typescript
const createWidget = () => {
  const content = new UIProfilerWidget(options);
  const widget = new MainAreaWidget({ content });
  widget.id = 'ui-profiler-centre';
  widget.title.label = 'UI Profiler';
  widget.title.closable = true;
  widget.title.icon = offlineBoltIcon;
  return widget;
};
```

UIProfilerWidget接收的options包括：
- `translator`: 国际化翻译器（使用nullTranslator，即英文）
- `profiler`: ConstrainedUIProfiler（UI使用的受限Profiler接口）
- `upload`: 文件上传函数（通过FileBrowserModel处理结果导出）
- `getResultsLocation`: 结果保存路径（可通过PageConfig配置`profilerDir`）

## 文件上传与结果导出

**文件**: src/index.ts:L74-L80

```typescript
upload: (file: File) => {
  return fileBrowserModel.upload(file);
},
getResultsLocation: () =>
  PageConfig.getOption('profilerDir') || '/ui-profiler-results/'
```

结果可以通过文件浏览器上传保存，默认路径为`/ui-profiler-results/`，可通过`PageConfig.setOption('profilerDir', '/custom/path/')`自定义。

## 插件导出

**文件**: src/index.ts:L180-L183

```typescript
export * from './tokens';   // 重新导出所有Token和接口
export * from './types';    // 重新导出类型定义
export default [plugin, scenariosPlugin, interfacePlugin];  // 默认导出三个插件
```

其他扩展可以从包中导入Token和接口：
```typescript
import { IUIProfiler, IScenario, IBenchmark } from '@jupyterlab/ui-profiler';
```

## 相关概念

- (01-architecture-overview.md
- (03-benchmarks.md
- (04-scenarios.md
- (09-ui-and-visualization.md
- (../references/api-tokens.md
