---
type: Facts
okf_version: "0.2"
title: "ui-profiler 源码事实清单"
generated: "2026-08-22"
tags: [jupyter, ui-profiler, performance, jupyterlab, typescript]
sources:
  - ../../../../../external/libs/jupyter/ui-profiler/package.json
  - ../../../../../external/libs/jupyter/ui-profiler/pyproject.toml
  - ../../../../../external/libs/jupyter/ui-profiler/jupyterlab_ui_profiler/__init__.py
  - ../../../../../external/libs/jupyter/ui-profiler/jupyter-config/server-config/jupyterlab_ui_profiler.json
  - ../../../../../external/libs/jupyter/ui-profiler/src/index.ts
  - ../../../../../external/libs/jupyter/ui-profiler/src/profiler.ts
  - ../../../../../external/libs/jupyter/ui-profiler/src/benchmark.ts
  - ../../../../../external/libs/jupyter/ui-profiler/src/jsBenchmarks.ts
  - ../../../../../external/libs/jupyter/ui-profiler/src/styleBenchmarks.tsx
  - ../../../../../external/libs/jupyter/ui-profiler/src/scenarios.ts
  - ../../../../../external/libs/jupyter/ui-profiler/src/dramaturg.ts
  - ../../../../../external/libs/jupyter/ui-profiler/src/statistics.ts
  - ../../../../../external/libs/jupyter/ui-profiler/src/tokens.ts
  - ../../../../../external/libs/jupyter/ui-profiler/src/css.ts
  - ../../../../../external/libs/jupyter/ui-profiler/src/browserProfiler.d.ts
  - ../../../../../external/libs/jupyter/ui-profiler/src/schema/benchmark-profile.json
  - ../../../../../external/libs/jupyter/ui-profiler/src/schema/benchmark-execution.json
  - ../../../../../external/libs/jupyter/ui-profiler/src/ui.tsx
---
# ui-profiler 源码事实清单

## 一、项目元数据与构建

- F-001: package.json:2-3 — npm 包名 `@jupyterlab/ui-profiler`，版本 `0.3.1`。
- F-002: package.json:108-110 — `jupyterlab` 配置声明 `extension: true`、`outputDir: jupyterlab_ui_profiler/labextension`。
- F-003: pyproject.toml:1-3 — Python 构建系统为 `hatchling.build`，requires 含 `hatchling>=1.4.0`、`jupyterlab>=4.0.0,<5.0.0`、`hatch-nodejs-version`。
- F-004: pyproject.toml:6-8 — Python 包名 `jupyterlab-ui-profiler`，`requires-python = ">=3.9"`。
- F-005: pyproject.toml:26-28 — 运行时依赖 `jupyter_server>=1.6,<3`。
- F-006: pyproject.toml:49-50 — `[tool.hatch.version] source = "nodejs"`，Python 版本号取自 Node 包版本。
- F-007: pyproject.toml:59-63 — wheel `shared-data` 把 `jupyterlab_ui_profiler/labextension` 映射到 `share/jupyter/labextensions/@jupyterlab/ui-profiler`，并同步 `install.json` 与 server/nb 两个 jupyter-config 目录。
- F-008: pyproject.toml:68-75 — `hatch-jupyter-builder` hook 以 `npm_builder` 构建，`ensured-targets` 检查 `static/style.js` 与 `package.json`，`skip-if-exists` 列出 `static/style.js`。
- F-009: jupyterlab_ui_profiler/__init__.py:4-8 — `_jupyter_labextension_paths()` 返回 `src: labextension`、`dest: '@jupyterlab/ui-profiler'`。
- F-010: jupyterlab_ui_profiler/__init__.py:11-14 — `_jupyter_server_extension_points()` 声明模块 `jupyterlab_ui_profiler` 为 server extension。
- F-011: jupyterlab_ui_profiler/__init__.py:24-32 — `_load_jupyter_server_extension` 向 `server_app.web_app.settings["headers"]` 写入 `Cross-Origin-Opener-Policy: same-origin`、`Cross-Origin-Embedder-Policy: require-corp` 与 `Document-Policy: js-profiling`。
- F-012: jupyter-config/server-config/jupyterlab_ui_profiler.json:2-6 — server-config JSON 声明 `ServerApp.jpserver_extensions['jupyterlab_ui_profiler']: true`。

## 二、插件注册与命令

- F-013: src/index.ts:37-54 — `plugin` 为 `JupyterFrontEndPlugin<IUIProfiler>`，`id: '@jupyterlab/ui-profiler:plugin'`、`autoStart: true`、`provides: IUIProfiler`，activate 返回含 6 个 benchmark 的 `UIProfiler` 实例。
- F-014: src/index.ts:56-60 — `interfacePlugin` id `'@jupyterlab/ui-profiler:user-interface'`、`autoStart: true`，`requires: [IUIProfiler, IDocumentManager]`、`optional: [ILauncher, ILayoutRestorer]`。
- F-015: src/index.ts:68-80 — `interfacePlugin` 创建 `FileBrowserModel` 提供 upload，`getResultsLocation` 读 `PageConfig.getOption('profilerDir')`，缺失时回退 `'/ui-profiler-results/'`。
- F-016: src/index.ts:83-91 — `createWidget()` 构建 `UIProfilerWidget` 并用 `MainAreaWidget` 包装，`widget.id = 'ui-profiler-centre'`、`title.label = 'UI Profiler'`、图标 `offlineBoltIcon`。
- F-017: src/index.ts:97-118 — 注册命令 `ui-profiler:open`，`execute` 复用 `lastWidget` 或新建，`app.shell.add(widget, 'main')` 后 `activateById` 并 `tracker.add`。
- F-018: src/index.ts:127-153 — 注册命令 `ui-profiler:wait-for-selector`，`execute` 内 `page.waitForSelector(args.selector, args.state ?? 'visible')`，`describedBy.args` 定义 `selector`/`state`（enum: visible/hidden/attached/detached）。
- F-019: src/index.ts:162-168 — `restorer.restore(tracker, { command: 'ui-profiler:open', name: widget => widget.title.label })` 恢复会话。
- F-020: src/index.ts:170-176 — `launcher.add({ command: 'ui-profiler:open', category: 'Other', rank: 1 })` 加入启动器。
- F-021: src/index.ts:183 — 默认导出 `[plugin, scenariosPlugin, interfacePlugin]` 三个插件数组。
- F-022: src/scenarios.ts:777-795 — `scenariosPlugin` id `'@jupyterlab/ui-profiler:default-scenarios'`、`autoStart: true`、`requires: [IUIProfiler]`，activate 把 10 个场景对象 `addScenario` 到 profiler。

## 三、性能测量核心（profiler / benchmark / js self-profiling）

- F-023: src/tokens.ts:67-108 — `IBenchmark` 接口定义 `id`/`name`/`run`/`configSchema`/`render`/`isAvailable`/`sortColumn`/`interpretation`。
- F-024: src/tokens.ts:130-144 — `ITimeMeasurement` 含 `times: number[]`；`IProfileMeasurement` 含 `traces`/`averageSampleInterval`/`samplingInterval`。
- F-025: src/tokens.ts:146-156 — `ITimingOutcome` 扩展 `IOutcomeBase` 并含 `reference: number[]`、`type: 'time'`；`IProfilingOutcome` 的 `type: 'profile'`。
- F-026: src/profiler.ts:61-118 — `runBenchmark()` 按 id 查找 benchmark 与 scenario（缺失抛 Error），调 `scenarioInstance.setOptions`，先发 `progress 0%` 再 `benchmarkRunner.run`，完成发 100%（interrupted 时发 NaN）。
- F-027: src/profiler.ts:124-132 — `getJupyterState()` 返回 `client`、`version`、`devMode`（`PageConfig.getOption('devMode')` 转小写比较）、`mode`。
- F-028: src/benchmark.ts:16-29 — `profile()` 检查 `window.Profiler === undefined` 时抛 `Error('Self-profiling is not available')`。
- F-029: src/benchmark.ts:35-56 — micro 模式每次 repeat `new window.Profiler(options)`，`scenario.run()` 后 `profiler.stop()` 收集 trace，支持提前 break。
- F-030: src/benchmark.ts:57-74 — macro 模式只创建一次 profiler，跨全部 repeat 采样，最后 `profiler.stop()` 得到单一 trace。
- F-031: src/benchmark.ts:78-95 — 返回值含 `samplingInterval: profiler.sampleInterval` 与各 trace 相邻样本时间差的均值 `averageSampleInterval`。
- F-032: src/benchmark.ts:98-139 — `benchmark()` 用 `performance.now()` 前后差记录每次 `scenario.run()` 耗时。
- F-033: src/benchmark.ts:141-181 — `executionTimeBenchmark` id `'execution-time'`、name `'Execution Time'`，`configSchema` 引用 `benchmark-execution.json`，run 内 `n = options.repeats || 3`，先 `layoutReady()` 再执行 `benchmark(scenario, n, true, ...)` 并回报进度。
- F-034: src/schema/benchmark-execution.json:5-9 — execution-time 的 `repeats` 属性 `default: 500`、`minimum: 1`。
- F-035: src/jsBenchmarks.ts:116-168 — `selfProfileBenchmark` id `'self-profile'`、name `'Profile JavaScript'`，`isAvailable: () => typeof window.Profiler !== 'undefined'`，run 调 `profile(scenario, {maxBufferSize, sampleInterval}, options.scale, ...)`。
- F-036: src/schema/benchmark-profile.json:18-24 — profile 的 `sampleInterval` 默认 `5`ms、`exclusiveMinimum: 0`，description 标注 Chrome 在 Windows 用 16ms、其余平台 10ms 采样。
- F-037: src/schema/benchmark-profile.json:25-31 — `maxBufferSize` 默认 `10000`，超限时提前终止 profiling。

## 四、rAF 采样与 Dramaturg 浏览器自动化

- F-038: src/dramaturg.ts:158-164 — `layoutReady()` 返回 Promise，在下一个 `requestAnimationFrame` 回调内 resolve——作为"等待一帧渲染完成"的统一原语。
- F-039: src/dramaturg.ts:137-156 — `waitForScrollEnd()` 以 `setInterval(requiredRestTime)` 轮询 `scrollTop`/`scrollLeft` 不再变化即 resolve。
- F-040: src/dramaturg.ts:68-110 — `waitForElement()` 用 `MutationObserver` 监听 `addedNodes` 与属性变化定位元素。
- F-041: src/dramaturg.ts:207-255 — `waitForSelector()` 按 state（attached/detached/visible/hidden）分派实现，默认超时 `5 * 1000`ms，超时 reject。
- F-042: src/dramaturg.ts:257-290 — `press()` 用 `@lumino/keyboard` 的 `getKeyboardLayout()` 反查 key→code，派发 `keydown`/`keypress`/`keyup` 三个 KeyboardEvent。
- F-043: src/dramaturg.ts:332-363 — 导出 `page` 对象含 `waitForSelector`/`press`/`$`/`type`/`click`/`focus`/`mouse.wheel`。

## 五、样式性能基准（styleBenchmarks / css）

- F-044: src/styleBenchmarks.tsx:78-283 — `styleRuleUsageBenchmark` id `'rule-usage'`、name `'Style Rule Usage'`，先收集"相关节点"再用 MutationObserver 统计 `touches`/`elementsSeen`/`elementsTouched`。
- F-045: src/styleBenchmarks.tsx:285-386 — `styleSheetsBenchmark` id `'style-sheet'`、name `'Style Sheets'`，遍历 `document.querySelectorAll('style')`，逐个 `sheet.disabled = true` 后 benchmark 再恢复。
- F-046: src/styleBenchmarks.tsx:388-469 — `styleRuleBenchmark` id `'style-rule'`、name `'Style Rules'`，对每条规则 `sheet.deleteRule` → benchmark → `sheet.insertRule` 恢复，记录 `bgMatches`。
- F-047: src/styleBenchmarks.tsx:471-583 — `styleRuleGroupBenchmark` id `'style-rule-group'`、name `'Style Rule Groups'`，支持 `minBlocks`/`maxBlocks`/`sheetRandomizations`（用 `shuffled` 打乱顺序）。
- F-048: src/css.ts:37-63 — `extractSourceMap()` 解析 CSS 内 `# sourceMappingURL=` 注释，base64 内联用 `atob` 解析、否则 `fetch(url)`。
- F-049: src/css.ts:65-108 — `collectRules()` 遍历 style 的 `sheet.rules`，仅收集 `CSSStyleRule`，按 `skipPattern`/`includePattern` 过滤 selector。

## 六、统计与结果展示

- F-050: src/statistics.ts:18-26 — `percentile()` 实现 jse.amstat.org 的 CDF 分位数方法四（Langford），先排序再按整数/小数判定插值。
- F-051: src/statistics.ts:28-30 — `quartile()` 为 `percentile(numbers, 0.25 * quartile)`。
- F-052: src/statistics.ts:52-69 — `interQuartileMean()` 按长度是否 4 的倍数分支计算截尾均值。
- F-053: src/statistics.ts:83-96 — `standardNormalDensity()` 与 `kernelDensityEstimate()` 实现标准正态密度与核密度估计。
- F-054: src/ui.tsx:296-428 — `renderTimings()` 输出 `up-BoxPlot` SVG：箱体用 q1/q3、须线取 `q ± 1.5 * IQR`（钳制到 min/max）、散点按核密度在纵轴展开，含 quartile 线与 0ms/max 刻度。
- F-055: src/ui.tsx:78-267 — `ProfileTrace` React 组件把 Profiler trace 渲染为帧条带，支持 wheel 缩放、鼠标拖拽平移，并用 `ResizeObserver` 自适应尺寸。

## 七、场景定义（scenarios）

- F-056: src/scenarios.ts:59-93 — `MenuSwitchScenario` id `'menuSwitch'`（run 依次打开 edit/view/run/kernel/settings/help 六个主菜单）与 `MenuOpenScenario` id `'menuOpen'`（`setOptions` 接收 `menu` 字段）。
- F-057: src/scenarios.ts:106-134 — `SidebarOpenScenario` id `'sidebarOpen'`、name `'Open Sidebar'`，默认 `_sidebars: ['filebrowser']`，run 内 `shell.activateById(sidebar)`。
- F-058: src/scenarios.ts:235-338 — `CompleterScenario` id `'completer'`、name `'Completer'`，执行 `completer:invoke-notebook`/`completer:invoke-file` 并等待 `.jp-Completer.jp-HoverBox[style]` 出现。
- F-059: src/scenarios.ts:546-626 — `CustomScenario` id `'custom'`、name `'Custom Scenario'`，构造时在 `jupyterApp.restored` 后动态生成 command 的 `oneOf` schema，run 按 `commands` 数组逐个 execute。
- F-060: src/scenarios.ts:628-775 — `ScrollScenario` id `'scroll'`（支持 `cellByCell` 逐格移动或 `scrollBy` 后 `waitForScrollEnd`）、`SwitchTabScenario` id `'tabSwitch'`、`SwitchTabFocusScenario` id `'tabSwitchFocus'`（`split: 'all'`）。
