---
type: Insights
okf_version: "0.2"
title: "ui-profiler 架构洞察"
generated: "2026-08-22"
tags: [jupyter, ui-profiler, performance, jupyterlab, typescript]
sources:
  - facts.md
  - ../../../../../external/libs/jupyter/ui-profiler/src/benchmark.ts
  - ../../../../../external/libs/jupyter/ui-profiler/src/jsBenchmarks.ts
  - ../../../../../external/libs/jupyter/ui-profiler/src/profiler.ts
  - ../../../../../external/libs/jupyter/ui-profiler/src/dramaturg.ts
  - ../../../../../external/libs/jupyter/ui-profiler/src/styleBenchmarks.tsx
  - ../../../../../external/libs/jupyter/ui-profiler/src/scenarios.ts
  - ../../../../../external/libs/jupyter/ui-profiler/jupyterlab_ui_profiler/__init__.py
---
# ui-profiler 架构洞察

## I-001：双模测量架构——`performance.now()` 计时与 `window.Profiler` 采样的互补分工

**类型**：架构模式
**关联事实**：F-028, F-029, F-030, F-031, F-032, F-033, F-035, F-036, F-037

**洞察**：ui-profiler 内置两类结果语义不同的测量基准（benchmark）：`execution-time` 走"计时"路径，`self-profile` 走"采样"路径，二者都跑同一个 `IScenario` 但产出 `ITimingOutcome` / `IProfilingOutcome` 两种结果类型（F-025）。计时路径用 `performance.now()` 前后差测出每次 repeat 的精确耗时（F-032），`executionTimeBenchmark` 默认重复 500 次并回报进度（F-033/F-034）；采样路径则依赖浏览器自带的 JavaScript 自采样 API `window.Profiler`——不存在时 `profile()` 直接抛 `Error('Self-profiling is not available')`（F-028），其采样周期由 `sampleInterval`（默认 5ms，F-036）与 `maxBufferSize`（默认 10000，F-037）共同控制。

采样路径内部又细分为 micro / macro 两种粒度（F-048 schema 的 scale 枚举，映射到 F-029/F-030）：micro 模式每次 repeat 都 `new window.Profiler(...)`、stop 出独立 trace，可逐次观察波动；macro 模式跨全部 repeat 只创建一次 profiler，得到一个平均意义上的 trace。`profile()` 的返回值在 trace 之外还携带 `samplingInterval` 与相邻样本间隔的均值 `averageSampleInterval`（F-031）——后者是衡量采样稳定性的关键信号：若浏览器实际采样间隔远大于请求值（Chrome 在 Windows 强制 16ms、其余 10ms，F-036），则 trace 的时序分辨率随之下降。

```
                    IScenario（run/setup/cleanup，F-030）
                              │
        ┌─────────────────────┴──────────────────────┐
        ▼                                            ▼
execution-time（计时，F-033）                  self-profile（采样，F-035）
performance.now() 前后差（F-032）              window.Profiler（F-028 缺失则抛错）
  ├─ repeats=500（F-034）                       ├─ sampleInterval 5ms 默认（F-036）
  └─ ITimingOutcome.type='time'（F-025）        ├─ maxBufferSize 10000（F-037）
                                               ├─ micro: 每 repeat 独立 trace（F-029）
                                               └─ macro: 全部 repeat 单一 trace（F-030）
                                                       │
                                                       ▼
                                    IProfilingOutcome.type='profile'（F-025）
                                    + samplingInterval / averageSampleInterval（F-031）
```

**复用价值**：做前端性能基建时，把"整体耗时（计时）"与"函数级时间分布（采样）"拆成两个可插拔 benchmark，让用户按分析目标选路；采样类基准必须显式声明 `isAvailable`（F-035 中 `typeof window.Profiler !== 'undefined'`）并在运行时先探测后执行，否则在旧浏览器会直接抛错中断整个分析流程。

## I-002：服务端 header 前置条件——COOP/COEP 与 `Document-Policy: js-profiling` 是采样类基准的使能开关

**类型**：架构约束
**关联事实**：F-011, F-014, F-028, F-035, F-036

**洞察**：`self-profile` 与高精度计时能否真正生效，取决于 Python server extension 在响应头写入的三组 header（F-011）：`Cross-Origin-Opener-Policy: same-origin` 与 `Cross-Origin-Embedder-Policy: require-corp` 用于解锁 Firefox 79+ 的高精度 `performance.now()`（消除 cross-origin 隔离削弱），`Document-Policy: js-profiling` 用于在 Chrome 启用 JavaScript 自采样（F-028 依赖的 `window.Profiler` 只有在此策略下才存在）。这三者被统一塞进 `server_app.web_app.settings["headers"]`（F-011），与 labextension 分属两套 Jupyter 扩展机制：labextension 由 `_jupyter_labextension_paths()` 注册（F-009），server extension 由 `_jupyter_server_extension_points()` + `jpserver_extensions: true`（F-012）注册，最终通过 wheel `shared-data` 把二者与 `install.json` 一并装入 labextensions 目录（F-007）。

因此这是一个"前端能力依赖后端头"的硬约束：移除 server extension（README 给出 `jupyter server extension disable jupyterlab_ui_profiler`）则保底仍有计时基准可用，但采样基准与高精度计时会静默降级或不可用。`load_jupyter_server_extension = _load_jupyter_server_extension`（notebook server 兼容别名）则保证 Binder/JupyterHub 等仍走 notebook server 的环境同样能获得这些头。

```
jupyter_server 进程
┌──────────────────────────────────────────────┐
│ labextension（前端，F-009）                    │
│   └─ execution-time / self-profile 基准        │
│              ▲                                │
│              │ 需要 header 使能                │
│              │                                │
│ server extension（F-010/F-011）                │
│   └─ settings["headers"]                       │
│       ├─ COOP: same-origin          → Firefox 高精度 performance.now() │
│       ├─ COEP: require-corp         → 同上（F-011）                     │
│       └─ Document-Policy: js-profiling → window.Profiler 存在（F-028）  │
│                    │                                                   │
│   jpserver_extensions: true（F-012）  <- wheel shared-data 安装（F-007） │
└──────────────────────────────────────────────┘
```

**复用价值**：浏览器能力探测（`window.Profiler`）与使能策略（响应头）必须放在一起设计——前端判断"有 API"还不够，后端要保证"该 API 被策略打开"。对依赖浏览器新 API 的扩展，建议把策略头与功能开关同生命周期管理，并在文档中给出"禁用后哪些功能降级"的清单。

## I-003：`layoutReady` + Dramaturg——用 `requestAnimationFrame` 同步屏障构建 Playwright 式原生测试工具

**类型**：架构模式
**关联事实**：F-038, F-039, F-040, F-041, F-042, F-043, F-056, F-058, F-060

**洞察**：所有基准在测量前后都会调用 `layoutReady()`（F-033 execution-time、F-035 self-profile 及全部 style benchmark），其实现仅一行——`requestAnimationFrame(() => resolve())`（F-038）。这是整个测量精度的基石：性能数字只有在"上一帧已渲染完成、DOM 处于稳定态"时采样才有意义，rAF 回调恰好保证同步点位于浏览器新帧起点，等价于"等一帧渲染完成"的屏障原语。基准与场景都在这个屏障上串行推进，避免异步更新（如 cells 插入、菜单打开）污染下一次测量起点。

与 rAF 屏障配套的是 `dramaturg.ts`——一个"Playwright 式 API 子集"（F-054）的原生实现，把场景编写者从 Playwright 依赖中解放：`waitForSelector` 按 attached/detached/visible/hidden 四种 state 分派实现（MutationObserver 监听 DOM 增删 + ResizeObserver 判定可见，F-040/F-041），`waitForScrollEnd` 轮询滚动位置静止（F-039），`press` 用 `@lumino/keyboard` 反查 key→code 并派发 keydown/keypress/keyup（F-042），最终聚合成 `page` 对象（F-043）。场景（F-056~F-060）因此可以写出"打开菜单 → 等待 selector → 等待布局稳定"的命令式脚本，而 `layoutReady` 则是其中每次动作后的通用停顿。

```
Benchmark.run(...)                                  场景脚本（scenarios.ts）
      │                                                    │
      ▼                                                    ▼
  layoutReady()  ◄──── requestAnimationFrame（F-038）    page.waitForSelector(...)（F-041）
      │       （每帧渲染完成的同步屏障）                     waitForScrollEnd(...)（F-039）
      ▼                                                    press('Escape')（F-042）
  benchmark / profile（F-032/F-029）                       page.$ / click / focus（F-043）
      │                                                    │
      ▼                                                    ▼
  结果 time/profile（F-025）                        Dramaturg page 对象（F-043）
```

**复用价值**：在纯前端环境下做自动化测试，可以借鉴"原生实现 Playwright 子集"的思路：rAF 屏障 + MutationObserver/ResizeObserver 两个观察器 + 键盘事件合成，足以覆盖常见 UI 交互断言，免去 Playwright 依赖。关键取舍是 `requestAnimationFrame` 不适用于所有场景——需要在"下一帧"而非"渲染完成"后的后续步骤时，应改用 `double rAF` 或显式等待。

## I-004：三插件编排 + `IUIProfiler` token 服务化——核心、默认场景、UI 三层解耦

**类型**：设计决策
**关联事实**：F-013, F-014, F-021, F-022, F-026, F-027

**洞察**：扩展把职责切成三个 `JupyterFrontEndPlugin` 并整体导出（F-021）：`@jupyterlab/ui-profiler:plugin` 提供核心服务 `IUIProfiler`（F-013），只负责持有 6 个 benchmark 与场景注册/执行入口（F-026 `runBenchmark` 按 id 查找并驱动执行）；`@jupyterlab/ui-profiler:default-scenarios` 只负责把 10 个内置场景 `addScenario` 进服务（F-022）；`@jupyterlab/ui-profiler:user-interface` 才负责 UI——构建 `UIProfilerWidget`、注册命令、接入 Launcher 与 LayoutRestorer（F-014~F-020）。三层通过 Lumino token 依赖注入连接：`IUIProfiler` 是 `new Token('@jupyterlab/ui-profiler:plugin')`（F-029），`interfacePlugin` 的 `requires: [IUIProfiler, IDocumentManager]`（F-014）即声明"我要用这个服务"。

这带来两个直接收益：其一，`IUIProfiler` 作为 token 服务可被第三方扩展消费——自定义 benchmark 或 scenario 只需拿到 token 即可与内置机制拼接（CustomScenario 的 command schema 动态生成 F-059 也依赖 command 注册表）；其二，UI 与核心彻底分离，无头环境可只启用核心插件而屏蔽界面。`getJupyterState()`（F-027）把 `client/version/devMode/mode` 写进每次结果，保证"谁测的、什么模式"可审计。

```
JupyterFrontEnd 插件容器
┌──────────────────────────────────────────────────────────┐
│ plugin（核心，F-013）  ──provides──►  IUIProfiler token（F-029）│
│   benchmarks: [6 个]                                      │
│   runBenchmark()（F-026）/ getJupyterState()（F-027）       │
│         ▲  requires [IUIProfiler]（F-022）                 │
│         │                                                 │
│ scenariosPlugin（F-022）     interfacePlugin（UI，F-014）    │
│   10 个内置场景 addScenario    requires [IUIProfiler, IDocumentManager] │
│                              optional [ILauncher, ILayoutRestorer]    │
│                              命令：ui-profiler:open（F-017）           │
│                              launcher.add（F-020）/ restorer.restore（F-019）│
└──────────────────────────────────────────────────────────┘
```

**复用价值**：功能复杂的 JupyterLab 扩展可按"核心服务 + 默认内容 + 界面"三插件拆分，核心服务用 `Token<T>` 暴露给第三方，界面插件通过 `requires/optional` 声明依赖；这样既能被其他扩展复用，也能在无界面环境下运行核心逻辑。注意 `optional: [ILauncher, ILayoutRestorer]` 的容错写法（F-014）让 UI 在宿主缺少这些服务时仍可加载。

## I-005："删除-测量-恢复"实验协议——CSS 规则级基准的原位 A/B 测量

**类型**：架构模式
**关联事实**：F-044, F-045, F-046, F-047, F-048, F-049

**洞察**：针对 CSS 的 4 个 style benchmark 共享一个实验协议：**先测量基线，再删除/禁用被测对象，测量，最后原位恢复，比较 Δ**。`styleSheetsBenchmark` 对每个 `<style>` 把 `sheet.disabled = true` 再跑场景（F-045）；`styleRuleBenchmark` 对每条规则 `sheet.deleteRule(ruleIndex)` → 测量 → `sheet.insertRule(rule.cssText, ruleIndex)` 恢复（F-046）；`styleRuleGroupBenchmark` 按 `minBlocks~maxBlocks` 分块删除并支持 `shuffled` 随机化打乱顺序以消除顺序偏差（F-047）；`styleRuleUsageBenchmark` 则先识别"相关节点/规则"再统计 `touches`/`elementsSeen`/`elementsTouched`，估计每条规则的真实影响面（F-044）。所有 delete/insert 都发生在 `layoutReady()` 屏障之后（F-038），确保恢复与测量都基于稳定帧。

规则收集与源映射是这套协议的支撑层：`collectRules()` 遍历 `sheet.rules`、只取 `CSSStyleRule` 并按 `skipPattern`/`includePattern` 过滤（F-049）；`extractSourceMap()` 从 CSS 尾部 `# sourceMappingURL=` 注释解析出源文件（base64 内联用 `atob`、外链则 `fetch`，F-048），使结果能回溯到具体源文件而非压缩后的 bundle。实验协议的可审计性因此从"样式名"延伸到"源文件 + 行"。

```
styleRuleBenchmark.run（F-046）                    styleRuleUsageBenchmark（F-044）
      │                                                    │
      ▼                                                    ▼
  collectRules 全部 CSSStyleRule（F-049）            MutationObserver 收集相关节点（F-044）
      │                                                    │
      ▼                                                    ▼
  for each rule:                                    统计 touches / elementsSeen / elementsTouched
    deleteRule(ruleIndex)（删除）                            │
    layoutReady()（F-038 屏障）                              ▼
    benchmark(scenario, n)（测量）                   对每条规则估计影响面后排序（sortColumn）
    insertRule(cssText, ruleIndex)（原位恢复）                 │
    layoutReady()（F-038 屏障）                              ▼
      │                                            解释 Δ 为负 → 规则可能拖慢性能
      ▼
  结果含 selector/source/stylesheetIndex（F-046）
```

**复用价值**：做"哪个规则/文件拖慢渲染"类分析时，"删除-测量-恢复"是侵入最小且可逆的实验协议，但必须保证三点：恢复用 `insertRule(cssText, 原 index)` 保持规则顺序不变（顺序漂移会改变级联结果）；每步测量前用 rAF 屏障等待布局稳定；对多规则场景用随机化（shuffled）抵消顺序偏差（F-047）。`deleteRule/insertRule` 的原位操作能精确控制变量，避免整表 disable 带来的连锁样式失效。
