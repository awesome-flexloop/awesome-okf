---
type: Concept
title: 架构总览：Benchmark-Scenario-Profiler 三角模型
description: 深入理解jupyterlab-ui-profiler的核心架构设计——Benchmark（测量方法）与Scenario（用户操作）的解耦矩阵模型，以及Profiler核心调度器如何协调两者
tags: [jupyterlab, ui-profiler, architecture, benchmark, scenario, profiler, design-pattern]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: profiler-ts
    resource: /references/api-tokens.md
    title: src/profiler.ts UIProfiler类
  - id: tokens-ts
    resource: /references/api-tokens.md
    title: src/tokens.ts 核心接口定义
  - id: index-ts
    resource: /references/api-tokens.md
    title: src/index.ts 插件入口
---

## 三角模型：解耦的设计哲学

jupyterlab-ui-profiler 的核心架构可以用一个三角模型来理解：

```
              Profiler（调度器）
               /            \
              /              \
      Benchmark ←——————→ Scenario
     （怎么测）  组合矩阵  （测什么）
```

**关键设计决策：Benchmark和Scenario完全解耦。** 一个Benchmark可以测量任意Scenario，一个Scenario也可以被任意Benchmark测量。这形成了一个 N×M 的测量矩阵，6个内置Benchmark × 10个内置Scenario = 60种组合，且可以无限扩展。

### 为什么解耦？

在传统性能测试中，"测什么"和"怎么测"经常耦合在一起（比如一个"菜单打开性能测试"函数既定义了打开菜单的操作，又硬编码了用`performance.now()`计时）。这种耦合导致：
- 无法用不同方法测量同一个操作（比如既看执行时间又看CSS影响）
- 无法复用测量逻辑到不同操作
- 扩展困难（每加一个测试就要从头写）

解耦后：
- **Benchmark** 关注"如何获得准确的性能数据"（减法测量、采样profiling、统计处理）
- **Scenario** 关注"如何可靠地复现用户操作"（DOM等待、状态准备、清理恢复）
- **Profiler** 负责将两者组合、管理生命周期、收集结果

## Profiler：核心调度器

**文件**: src/profiler.ts

`UIProfiler` 类实现 `IUIProfiler` 接口，是整个框架的中枢：

```typescript
class UIProfiler implements IUIProfiler {
  constructor(options: { app: JupyterFrontEnd; benchmarks: IBenchmark[] });

  // 注册Scenario
  addScenario(scenario: IScenario): void;

  // 核心方法：运行Benchmark×Scenario组合
  async runBenchmark<T>(
    scenario: { id: string; options: JSONObject },
    benchmark: { id: string; options: JSONObject }
  ): Promise<IBenchmarkResult<T>>;

  // 中止当前测量
  abortBenchmark(): void;

  // 信号
  readonly scenarioAdded: ISignal<IUIProfiler, IScenario>;
  readonly progress: ISignal<IUIProfiler, IProgress>;

  // 只读访问
  readonly benchmarks: IBenchmark[];
  readonly scenarios: IScenario[];
}
```

### runBenchmark 执行流程

`runBenchmark()` 方法（src/profiler.ts:L61-L118）的执行流程：

```
1. 查找benchmarkRunner（按benchmark.id匹配）
2. 查找scenarioInstance（按scenario.id匹配）
3. 如果scenario有setOptions，传入配置
4. 发出progress: 0%
5. 调用benchmarkRunner.run(scenarioInstance, options, progressSignal, abortSignal)
6. 如果interrupted，发出progress: NaN；否则发出progress: 100%
7. 收集环境信息（userAgent、hardwareConcurrency、windowSize、jupyter状态）
8. 生成唯一result ID并返回IBenchmarkResult
```

关键点：Profiler本身不执行测量，它只是查找对应的Benchmark和Scenario实例，然后委托给Benchmark的`run()`方法。Benchmark收到Scenario接口，通过调用`scenario.run()`、`scenario.setup()`等方法执行操作。

### 插件注册流程

三个插件按依赖顺序激活（src/index.ts）：

1. **plugin**（核心服务）：最先激活，创建UIProfiler实例并注册6个内置Benchmark，`provides: IUIProfiler`导出Token
2. **scenariosPlugin**（默认场景）：`requires: [IUIProfiler]`，在Profiler就绪后注册10个内置Scenario
3. **interfacePlugin**（UI界面）：`requires: [IUIProfiler, IDocumentManager]`，最后创建UI组件、注册命令和Launcher卡片

这种分层设计使得其他JupyterLab扩展可以在自己的插件中：
```typescript
// 其他扩展可以依赖IUIProfiler添加自定义Benchmark/Scenario
const myPlugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:profiler-addon',
  autoStart: true,
  requires: [IUIProfiler],
  activate: (app: JupyterFrontEnd, profiler: IUIProfiler) => {
    profiler.addScenario(myCustomScenario);
    // 注意：当前API只支持addScenario，添加自定义Benchmark需在构造时传入
  }
};
```

## Benchmark 接口：定义"怎么测"

**文件**: src/tokens.ts:L67-L108

每个Benchmark是一个满足`IBenchmark<T>`接口的对象：

```typescript
interface IBenchmark<T extends IOutcomeBase = IOutcomeBase> {
  id: string;                                        // 唯一标识
  name: string;                                      // 显示名称
  run: (scenario: IScenario, options: any,
        progress?: Signal<any, IProgress>,
        stopSignal?: ISignal<any, void>) => Promise<T>;  // 执行测量
  configSchema: JSONSchema7;                         // 配置表单Schema
  render?: (props: { outcome: T }) => JSX.Element;  // 自定义结果渲染
  isAvailable?: () => boolean;                       // 浏览器能力检测
  sortColumn?: string;                               // 默认排序列
  interpretation?: string | JSX.Element;            // 结果解读说明
}
```

Benchmark的核心职责：
1. 接收一个IScenario实例
2. 通过scenario的生命周期方法（setupSuite→setup→run→cleanup→cleanupSuite）控制执行
3. 在scenario.run()前后执行测量逻辑（计时、profiling、CSS操作等）
4. 返回结构化的测量结果（IOutcome）
5. 支持进度报告和中止
6. 可选提供自定义结果渲染器和解读说明

### 两种Outcome类型

```typescript
// 时间测量结果
interface ITimingOutcome {
  results: ITimeMeasurement[];   // 每次测量的时间数组
  reference: number[];           // 基线时间数组
  tags: Record<string, number>;  // DOM标签计数
  totalTime: number;             // 总耗时
  type: 'time';
  interrupted: boolean;
}

// Profiling结果
interface IProfilingOutcome {
  results: IProfileMeasurement[];  // trace数据
  tags: Record<string, number>;
  totalTime: number;
  type: 'profile';
  interrupted: boolean;
}
```

时间型Benchmark（Execution Time、CSS系列）返回`ITimingOutcome`，JS Profiling返回`IProfilingOutcome`。

## Scenario 接口：定义"测什么"

**文件**: src/tokens.ts:L16-L65

每个Scenario是一个满足`IScenario`接口的对象（或类实例）：

```typescript
interface IScenario {
  id: string;                              // 唯一标识
  name: string;                            // 显示名称
  run: () => Promise<void>;                // 执行操作
  setupSuite?: () => Promise<void>;        // 套件准备（一次）
  cleanupSuite?: () => Promise<void>;      // 套件清理（一次）
  setup?: () => Promise<void>;             // 每次重复前准备
  cleanup?: () => Promise<void>;           // 每次重复后清理
  configSchema?: JSONSchema7;              // 配置表单Schema
  setOptions?: (options: any) => void;     // 接收用户配置
}
```

### Scenario 生命周期

Scenario的生命周期由Benchmark控制，标准执行顺序为：

```
setupSuite()                     // 整个benchmark只执行一次
  │
  ├── setup() → run() → cleanup()    // 重复N次
  ├── setup() → run() → cleanup()
  ├── ...
  └── setup() → run() → cleanup()
  │
cleanupSuite()                   // 整个benchmark只执行一次
```

- **setupSuite/cleanupSuite**：重量级准备/清理，如打开文件、创建widget、关闭widget
- **setup/cleanup**：轻量级重复前/后操作，如关闭菜单、重置滚动位置
- **run**：核心操作，其执行时间/性能被Benchmark测量

以MenuOpenScenario为例（src/scenarios.ts:L76-L93）：
- 无setupSuite（不需要重量级准备）
- 无setup
- `run()`: 打开指定菜单
- `cleanup()`: 按Escape关闭菜单
- 无cleanupSuite

以CompleterScenario为例（src/scenarios.ts:L235-L338）：
- `setupSuite()`: 创建文件、插入token变量、预运行一次消除warm-up影响
- 无setup
- `run()`: 聚焦编辑器、触发补全、等待补全弹出
- `cleanup()`: 按Escape关闭补全
- `cleanupSuite()`: 保存文件、关闭widget

## 扩展点

### 添加自定义Scenario

通过`profiler.addScenario()`方法添加：

```typescript
const myScenario: IScenario = {
  id: 'my-custom-action',
  name: 'My Custom Action',
  setupSuite: async () => { /* 准备 */ },
  run: async () => { /* 执行操作 */ },
  cleanupSuite: async () => { /* 清理 */ },
  configSchema: { /* JSON Schema */ },
  setOptions: (options) => { /* 处理配置 */ }
};
profiler.addScenario(myScenario);
```

内置的CustomScenario已经支持通过JSON配置任意命令序列，无需写代码。

### 添加自定义Benchmark

当前版本（v0.3.1）添加自定义Benchmark需要在创建UIProfiler实例时传入，或通过fork扩展。Benchmark对象只需实现IBenchmark接口，核心是实现`run()`方法中调用scenario的生命周期方法并执行测量。

## 三插件分离的好处

将核心服务、默认Scenario、UI界面拆分为三个独立插件带来了：

1. **无UI运行**：其他扩展可以依赖IUIProfiler在后台运行性能测试，不需要打开UI面板
2. **按需加载Scenario**：不同的扩展包可以注册自己的Scenario，而不需要修改核心包
3. **UI可替换**：核心服务和Scenario逻辑与UI渲染解耦，可以自定义结果展示方式
4. **可测试性**：核心Profiler逻辑不依赖UI组件，可以在Node环境中单元测试

## 结果数据结构

`IBenchmarkResult`（src/tokens.ts:L160-L179）包含完整的可复现实验数据：

```typescript
interface IBenchmarkResult<T> {
  options: { scenario: JSONObject; benchmark: JSONObject };  // 使用的配置
  benchmark: string;                    // benchmark id
  scenario: string;                     // scenario id
  userAgent: string;                    // 浏览器UA
  hardwareConcurrency: number;          // CPU核心数
  completed: Date;                      // 完成时间
  windowSize: { width: number; height: number };  // 窗口尺寸
  id: string;                           // 唯一ID
  jupyter: IJupyterState;              // JupyterLab状态（版本、模式等）
  outcome: T;                           // 测量结果
}
```

结果可以序列化为JSON导出，包含了重现实验所需的所有环境信息。

## 相关概念

- (02-profiler-core.md
- (03-benchmarks.md
- (04-scenarios.md
- (08-statistics-and-results.md
- (../references/api-tokens.md
