---
type: Example
title: 自定义Scenario与编程式测量
description: 两种方式扩展ui-profiler：（1）使用Custom Scenario通过JSON配置自定义命令序列无需写代码，（2）开发自定义Benchmark/Scenario插件
tags: [jupyterlab, ui-profiler, custom-scenario, plugin, extension, api]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
prerequisites:
  - 已完成第一次基准测试
  - 方式2需要JupyterLab扩展开发基础（TypeScript）
---

## 方式1：使用 Custom Scenario（零代码）

**Custom Scenario**允许你通过JSON配置任意JupyterLab命令序列，无需编写TypeScript代码。

### 示例1：测量主题切换性能

假设你想测量切换浅色/深色主题的耗时：

1. Benchmark: **Execution Time**
2. Scenario: **Custom Scenario**
3. 配置JSON：

```json
{
  "setupCommands": [],
  "commands": [
    {
      "id": "apputils:change-theme",
      "args": { "theme": "JupyterLab Dark" }
    }
  ],
  "cleanupCommands": [
    {
      "id": "apputils:change-theme",
      "args": { "theme": "JupyterLab Light" }
    }
  ]
}
```

4. 点击 **Run**

Custom Scenario会：
1. 执行setupCommands（这里为空）
2. 执行commands中的切换主题命令并测量耗时
3. 执行cleanupCommands恢复到浅色主题

### 示例2：测量新建Notebook的性能

```json
{
  "setupCommands": [],
  "commands": [
    { "id": "notebook:create-new", "args": {} }
  ],
  "cleanupCommands": [
    { "id": "notebook:close-and-shutdown", "args": {} }
  ]
}
```

### 示例3：测量运行所有单元格的性能

```json
{
  "setupCommands": [
    { "id": "notebook:create-new", "args": {} },
    { "id": "notebook:insert-cell-below", "args": {} },
    { "id": "notebook:replace-selection", "args": { "text": "import time\ntime.sleep(0.1)" } },
    { "id": "notebook:insert-cell-below", "args": {} },
    { "id": "notebook:replace-selection", "args": { "text": "print('hello')" } }
  ],
  "commands": [
    { "id": "notebook:run-all-cells", "args": {} }
  ],
  "cleanupCommands": [
    { "id": "notebook:close-and-shutdown", "args": {} }
  ]
}
```

### 发现可用命令

如何知道有哪些命令可以用？两种方式：

1. **命令面板**：打开命令面板（Ctrl+Shift+C），搜索你想执行的操作，命令ID通常在提示中显示
2. **浏览器控制台**：
   ```javascript
   // 在JupyterLab页面的DevTools Console中执行
   const commands = Array.from(Object.keys(jupyterapp.commands._commands));
   commands.filter(c => c.includes('theme')).forEach(c => console.log(c));
   ```

### Custom Scenario的限制

- 只能执行已注册的命令（`app.commands.execute()`）
- 命令之间只等待`layoutReady()`（一个rAF），不支持自定义等待条件
- 无法在命令之间插入复杂的等待逻辑（如等待特定DOM元素出现）
- 如果需要自定义等待逻辑或更复杂的交互，需要开发插件（方式2）

## 方式2：开发自定义插件（TypeScript）

如果Custom Scenario无法满足需求（需要自定义等待、复杂交互、特殊测量逻辑），可以开发JupyterLab扩展插件。

### 插件骨架

首先创建一个JupyterLab扩展项目（使用`jupyter labextension create`或cookiecutter），然后：

#### package.json 依赖

```json
{
  "dependencies": {
    "@jupyterlab/ui-profiler": "^0.6.0",
    "@jupyterlab/application": "^4.0.0",
    "@lumino/signaling": "^2.0.0"
  },
  "jupyterlab": {
    "extension": "lib/index.js"
  }
}
```

#### 注册自定义Scenario

```typescript
// src/index.ts
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IUIProfiler, IScenario, Dramaturg, layoutReady } from '@jupyterlab/ui-profiler';
import type { JSONSchema7 } from 'json-schema';

const myScenario: IScenario = {
  id: 'my-extension:open-command-palette',
  name: 'Open Command Palette',

  configSchema: {
    type: 'object',
    properties: {
      searchText: {
        type: 'string',
        title: 'Search text',
        default: ''
      }
    }
  } as JSONSchema7,

  split: 'none',

  async setupSuite() {
    // 一次性准备：确保没有打开的命令面板
  },

  async setup() {
    // 每次迭代前：按Escape关闭可能打开的面板
  },

  async run() {
    const dramaturg = new Dramaturg();

    // 打开命令面板
    await dramaturg.click('[data-command="commandsearch:open"]');

    // 等待命令面板出现
    await dramaturg.waitForSelector('.lm-CommandPalette', { visible: true });

    // 如果有搜索文本，输入
    if (this._options?.searchText) {
      const input = document.querySelector('.lm-CommandPalette-input') as HTMLInputElement;
      if (input) {
        input.value = this._options.searchText;
        input.dispatchEvent(new Event('input'));
        await layoutReady();
      }
    }
  },

  async cleanup() {
    // 按Escape关闭命令面板
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    await layoutReady();
  },

  async cleanupSuite() {
    // 最终清理
  },

  _options: null as any
};

// 插件定义
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'my-extension:profiler-scenario',
  autoStart: true,
  requires: [IUIProfiler],
  activate: (app: JupyterFrontEnd, profiler: IUIProfiler) => {
    profiler.addScenario(myScenario);
    console.log('Custom profiler scenario registered:', myScenario.id);
  }
};

export default plugin;
```

#### 注册自定义Benchmark

```typescript
import { IBenchmark, ITimingOutcome, layoutReady, Statistic } from '@jupyterlab/ui-profiler';
import { Signal } from '@lumino/signaling';

const memoryBenchmark: IBenchmark<ITimingOutcome> = {
  id: 'my-extension:memory-usage',
  name: 'Memory Usage',

  configSchema: {
    type: 'object',
    properties: {
      repeats: {
        type: 'integer',
        title: 'Repeats',
        default: 3,
        minimum: 1,
        maximum: 20
      }
    },
    required: ['repeats']
  } as JSONSchema7,

  sortColumn: 'ΔIQM%',

  async run(scenario, options, progress, stopSignal): Promise<ITimingOutcome> {
    const times: number[] = [];
    const n = options.repeats ?? 3;

    if (scenario.setupSuite) await scenario.setupSuite();

    // Baseline measurement
    const baseline: number[] = [];
    for (let i = 0; i < n; i++) {
      if (scenario.setup) await scenario.setup();
      await layoutReady();
      const mem0 = (performance as any).memory?.usedJSHeapSize ?? 0;
      await scenario.run();
      await layoutReady();
      const mem1 = (performance as any).memory?.usedJSHeapSize ?? 0;
      baseline.push(mem1 - mem0);
      if (scenario.cleanup) await scenario.cleanup();
      await layoutReady();
    }

    // Measurement (same as baseline for this simple example)
    for (let i = 0; i < n; i++) {
      if (stopSignal?.stop) break;

      progress?.emit({ message: `Iteration ${i + 1}/${n}`, percentage: (i / n) * 100 });

      if (scenario.setup) await scenario.setup();
      await layoutReady();
      const mem0 = (performance as any).memory?.usedJSHeapSize ?? 0;
      const t0 = performance.now();
      await scenario.run();
      const elapsed = performance.now() - t0;
      times.push(elapsed);
      if (scenario.cleanup) await scenario.cleanup();
      await layoutReady();
    }

    if (scenario.cleanupSuite) await scenario.cleanupSuite();

    return {
      type: 'time-measurement',
      times,
      reference: baseline,
      interrupted: stopSignal?.stop ?? false
    };
  },

  isAvailable: () => {
    // performance.memory 只在Chrome中可用
    return 'memory' in performance;
  }
};
```

### 编程式调用（不需要UI）

你也可以在插件代码中直接调用profiler进行自动化测量：

```typescript
import { IUIProfiler, Statistic } from '@jupyterlab/ui-profiler';

async function runAutomatedBenchmark(profiler: IUIProfiler) {
  // 查找已注册的benchmark和scenario
  const benchmark = profiler.benchmarks.find(b => b.id === 'execution-time');
  const scenario = profiler.scenarios.find(s => s.id === 'menuOpen');

  if (!benchmark || !scenario) {
    console.error('Benchmark or scenario not found');
    return;
  }

  // 创建进度信号
  const progress = new Signal<any, any>({});
  progress.connect((sender, msg) => {
    console.log(`Progress: ${msg.message} (${msg.percentage}%)`);
  });

  // 执行测量
  const result = await profiler.runBenchmark(
    benchmark,
    scenario,
    { menu: 'file', repeats: 5 },
    progress
  );

  // 分析结果
  if (result.type === 'time-measurement') {
    const iqm = Statistic.interQuartileMean(result.times);
    const median = Statistic.median(result.times);
    const mad = Statistic.mad(result.times);
    console.log(`IQM: ${iqm.toFixed(2)}ms, Median: ${median.toFixed(2)}ms, MAD: ${mad.toFixed(2)}ms`);
  }
}
```

### 监听所有Benchmark结果

```typescript
profiler.ran.connect((sender, result) => {
  console.log(`Benchmark completed: ${result.benchmark.id}`);
  console.log(`Scenario: ${result.scenario.id}`);
  console.log(`Outcome type: ${result.outcome.type}`);

  // 可以将结果发送到监控服务
  // fetch('/api/performance-results', {
  //   method: 'POST',
  //   body: JSON.stringify(result)
  // });
});
```

### 构建和安装

```bash
# 构建扩展
jlpm install
jlpm build

# 安装到JupyterLab
jupyter labextension develop . --overwrite
jupyter lab build  # 如果需要
```

## 方式选择指南

| 需求 | 推荐方式 |
|------|---------|
| 测量已有命令的执行时间 | Custom Scenario（方式1） |
| 需要DOM等待/复杂交互 | 自定义Scenario插件（方式2） |
| 需要自定义测量逻辑（内存、帧率等） | 自定义Benchmark插件（方式2） |
| CI中自动化性能测试 | 编程式调用（方式2） |
| 快速验证性能假设 | Custom Scenario（方式1） |
| 需要自定义结果可视化 | 自定义Benchmark + render方法（方式2） |

## 相关概念

- (../concepts/10-custom-extensions.md
- (../concepts/04-scenarios.md
- (../concepts/02-profiler-core.md
- (../concepts/07-dramaturg-automation.md
