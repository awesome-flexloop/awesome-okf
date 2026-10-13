---
type: Concept
title: "JavaScript 应用图与 Web/浏览器域"
description: "REA 的 JavaScript 应用图（JavaScriptApplicationGraph schema、12 关系词汇、身份策略）、JS 工作流 6 工具、工件重建 analyze_javascript_application、Wakaru 恢复、运行时观测与协同，以及 Web 源定位 / 模块追踪 / 脚本导出 / 浏览器场景契约与观测（事实层 F-067~F-082）"
tags: [rea, javascript, application-graph, web, browser, cdp, electron, wakaru, reconciliation, source-map, source-code]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T14:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: docs-full
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/docs"
  - id: local-source
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
---

# JavaScript 应用图与 Web/浏览器域

> 事实层（What / How）。本文只陈述从 `docs/` 深层登记的可核验事实（F-067~F-082）：JavaScript 应用图、JS 工作流、工件重建、Wakaru 恢复、运行时观测与协同，以及 Web 源定位 / 模块追踪 / 脚本导出 / 浏览器场景契约与观测。工具与 Provider 的契约层机制见 [02 · MCP 契约层](02-mcp-contract.md)，适配器见 [03 · Provider 适配器](03-provider-adapters.md)，成员与证据模型见 [06 · 领域类型与证据模型](06-domain-types-and-evidence.md)。

## 一句话定位

JavaScript/Web 域是 REA 的「跨层实体身份 + 承载证据的关系 + 规范化承诺」层：它以一张名为 `JavaScriptApplicationGraph` 的有向图为持久化数据契约，把 shipped application bytes、JavaScript 结构、Electron 进程边界、被动的浏览器观测与 native add-on 连起来；它**不是**抽取器、**不是**新的 CLI/MCP 工具，而是 provider 无关的领域模型（F-067）。它只校验调用方提供的事实、派生语义标识符、强制图完整性与序列化规范化 JSON，不做文件系统/CDP I/O、不执行 JavaScript、没有应用特定的节点种类（F-067 源文件 javascript-application-graph.md）。

## JavaScript 应用图：作为数据契约的领域模型

### schema 与标识符

存储图顶层形状为 `schema: "JavaScriptApplicationGraph"`，含 `graph_id`（`jag_<sha256 of normalized graph semantics>`）、`root_node_ids`、`nodes`、`edges`、`coverage` 与 `limitations`（F-067）。观察 ID 用 `semantic-content-sha256` 推导、稳定性为 `observation-exact`；边缘 ID 用同一推导、稳定性为 `relationship-exact`。解析时会重算节点/观察/边缘/图 ID，因此调用方在改变语义内容后无法保留过期 ID（F-067）。解析拒绝未知字段、非规范化排序、重复 ID、过期语义承诺、缺失根、悬挂端点、自环，以及非同种节点之间的 `changed_from` 边（F-067 源文件）。

该图不施加强制性的根/节点/边缘/观察/JSON 属性总数上限；字段级校验仍适用于路径、标识符与证据值（F-067 源文件 javascript-application-graph.md）。

### 有向关系词汇表

应用图的有向关系词汇表含 **12** 个值（F-068）：

> `contains`、`loads`、`imports`、`maps_to`、`exposes`、`sends`、`invokes`、`handles`、`calls`、`persists_to`、`observed_as`、`changed_from`

Provider 名称刻意不出现在该词汇表中（F-068）。其中 `loads`/`exposes`/`invokes`/`handles`/`imports` 保持为静态推断（static inference）；动态或歧义 IPC 不产生配对边；运行时实体保留被动 CDP authority，而一次成功的静态/运行时对应是另一类被单独标注的跨层推断（F-068 源文件）。

### 身份策略

节点把稳定的实体身份与单条观察分离：改变 label、抽取器或证据记录会改变观察 ID，但不必然改变节点 ID（F-069）。身份策略集合含（F-069）：

| 策略 | 稳定性范围 | 用途 |
|---|---|---|
| `content-digest` | Globally exact bytes | 工制物与字节相同的资产 |
| `source-map-original` | One source-map commitment | 恢复的原始源模块 |
| `canonical-path` | One artifact version | ASAR 条目与规范化路径上的资产 |
| `artifact-local-key` | One artifact version | IPC 通道、handler、exports 及其它有名字实体 |
| `structural-fingerprint` | Explicit cross-version inference | 从有界结构推断出关系的模块 |
| `runtime-instance` | One capture only | targets、frames、运行时脚本与 workers |
| `observation-fingerprint` | One observation scope | 无更强合理身份的事实 |

固定文档的身份策略表列出上述 **7** 种；本轮机械计数回验一致。此前“8 种”及“待复核”是知识包的陈旧表述，不归因于上游。

## JS 工作流：跨层应用图上的 6 个 MCP 工具

JS 工作流 MCP 工具共 **6** 个（F-070）：

> `inspect_analysis_view`、`trace_application_feature`、`trace_javascript_semantics`、`compare_application_versions`、`compare_source_to_bundle`、`compare_javascript_export_shapes`

CLI 命令名用连字符替换同名（F-070）。`inspect_analysis_view` 从已完成的应用 Evidence 投影一个 summary、模块页或单个模块，**不遍历关系**（F-071）；语义图线格式用 `evidence_contexts` 表承载共享来源（非共享位置的 provenance，每节点/关系/指纹/unknown 用 `evidence.context_id` 命名所属上下文，F-071）。其余工作流消费 `analyze_javascript_application` 或 `reconcile_javascript_runtime` 产生的 Evidence，不读工制物、不执行应用代码、不附加进程、不打开 native-provider（F-071 源文件）。

## 工件重建：analyze_javascript_application

`analyze_javascript_application`（CLI `rea analyze-javascript-application`）是 JavaScript 工件重建入口，把目录或 ASAR 投影进应用图**而不执行任何应用代码**，返回含图与 Electron 边界 summary 的 Evidence 信封（F-072）。支持 `.js/.jsx/.mjs/.cjs/.ts/.tsx/.mts/.cts` 共 **8** 种扩展名，均作为惰性文本解析（F-072）。它不需要活动的 Hopper、Ghidra、browser 或 Electron 进程（F-072 源文件）。

重建的 `integrity_policy` 接受 `fail` 或 `record-and-continue` 两种取值，CLI 与 MCP 均默认 `fail`（F-073）。ASAR 完整性检查使用 **SHA-256**，能识别匹配失败、`observed-untrusted` 信任；`record-and-continue` 在保留每条矛盾的 declared/observed hash 同时继续分析观察到的字节，并把应用图覆盖率标为 partial、把所有矛盾的路径列入 limitations（F-073 源文件 javascript-artifact-reconstruction.md）。

## 恢复：Wakaru 引擎

`recover_javascript_sources` / `recover-javascript-sources` 从显式选中的 UTF-8 JavaScript 文件或 bundle 派生可读模块，从不执行选中或恢复的应用代码（F-074 源文件 javascript-recovery.md）。恢复解析器接受 Wakaru **^1.13.0**，并以 Wakaru **1.14.0** 验证（F-074）。其 SHA-256 为 `664fa06782a61eda7ed15885134b52525fd565dd77607e642062ceb6cd927c38`；第三方源代码修订固定于 commit `8219bf5016a063d7fb215101a8c45d5959ec733f`（Apache-2.0，`third_party/wakaru`）；恢复进程使用 util-linux `prlimit`（默认 `/usr/bin/prlimit`，可用 `REA_JAVASCRIPT_PRLIMIT_COMMAND` 覆盖）。REA 不安装 Wakaru 或 prlimit，用 `REA_WAKARU_COMMAND` 指定调用方自备引擎（F-074）。

## 运行时观测与协同

### 被动运行时观测

JS 运行时观测含 **2** 个 MCP 工具 `list_javascript_runtime_targets`/`observe_javascript_runtime`，CLI 同名（F-075）。调用方声明 4 种角色：`node`/`electron-main`/`electron-preload`/`electron-renderer`（F-075）。捕获预算为 8 MiB 聚合、CDP 消息传输上限 16 MiB；超过传输上限以 `payload_limit` 失败，超过聚合预算则丢弃后续元数据并以 `events_dropped`/`truncated: true` 报告（F-075）。provider 只发送 `Runtime.enable` 与 `Debugger.enable` 两个协议命令，从不 `Runtime.evaluate`、不读脚本源、不装断点、不暂停/恢复执行（F-075 源文件）。

### 静态/运行时协同

`reconcile_javascript_runtime`（CLI `rea reconcile-javascript-runtime`）把已有静态应用图与被动 capture 组合而不合并其 authority（F-076）。`static_layers` 要求**恰好一个** `application` 角色（另可加 `cache`/`assets` 角色）（F-076）。映射类型含 `file-root`/`url-prefix` 两种（F-076）。跨层 `observed_as` 边缘的 `authority` 为 `cross-layer-reconciliation`、`state` 为 `inferred`（F-076）。该操作不做文件系统/browser/Electron I/O，只接受 `analyze_javascript_application`/`inspect_web_page`/`inspect_electron_page`/`observe_javascript_runtime` 产生的语义校验 Evidence（F-076 源文件）。

## Web 源定位：trace_web_source_location

`trace_web_source_location`（CLI `rea trace-web-source-location`）把一份被 `export_web_scripts` 保留的脚本里的一个选定位置，经一份显式配对的本地 source map 映射回原始位置（F-077）。适配器锁定上游 `@jridgewell/trace-mapping` **0.3.31** 而不改其代码（F-077）。生成位置用**从 1 开始**的行号、**从 0 开始**的 UTF-16 列号（F-077）；查找遵循 ECMA-426 GetOriginalPositions 语义，取小于等于选定点的最大生成位置并返回该位置的**全部** segment（F-077 源文件）。

## 模块追踪与脚本导出

### 模块追踪：trace_web_module_imports

`trace_web_module_imports`（CLI `rea trace-web-module-imports`）追踪一份脚本对外部的 native ES imports 与 re-exports（F-078）。其中 `script_index` 在 `manifest.scripts` 内**从 0 开始**；`additional_paths` 最接受 **16** 个额外文件（F-078）。清单/源/导入映射分别限制 **32 MiB/16 MiB/4 MiB**（F-078）。它需要调用方自备、支持 `import.meta.resolve` 的 Chromium 可执行文件，REA 不安装/升级浏览器；其把应用当作数据解析、从不执行（F-078 源文件）。

### 脚本导出：export_web_scripts

`export_web_scripts`（CLI `rea export-web-scripts`）把保留的浏览器源桥接进本地 JavaScript 分析器，把脚本写进**目标须不存在**的目录并附带验证过的 manifest（F-079）。被动检查需选择 `include_script_sources: true`（CLI `--include-script-sources`），场景则需选中 `capture.network.response_body: true`（F-079）。导出不回取 URL、不执行 JavaScript；内联结果含 `analysis_input`，可直接传给 `analyze_javascript_application`（F-079 源文件）。

## 浏览器场景契约与观测

### 场景契约：capture_browser_scenario

`capture_browser_scenario`（CLI `rea capture-browser-scenario INPUT_JSON`）接受 provider 中立的 `browserScenarioSchema`，请求是声明式的（固定动作词汇、显式 HTTP(S) target、确定性浏览器设置、显式存储 seeds 与 provider-owned 存活期限，F-080）。支持 `launch`/`connect` 两种浏览器模式，`headless` 默认 `true` 可设为 `false`（F-080）；`environment.service_workers` 默认**阻止**、可设为 `allow`（F-080）。`launch` 模式使用 provider-owned 临时 profile（结束后关停删除），`connect` 模式只接受显式端口 loopback CDP endpoint 且只断开外部浏览器而不关闭它（F-080 源文件 browser-scenario-contract.md）。

### 浏览器观测

浏览器观测共享一个排除词汇 `BrowserExclusionReason`，覆盖所有栈中每条拒绝原因的映射，即使 wire schema 保留一个更窄的历史 bucket（F-081）。`discover_webmcp_tools` 使用实验性 CDP WebMCP 域，返回每个注册及其完整 observed `input_schema` 声明与规范 `input_schema_sha256` 摘要；声明是被当作不可信的 JSON 数据处理，REA 不解析 schema 引用，也从不暴露 `WebMCP.invokeTool`（F-081）。CDP 连接对每条 WebSocket 消息强制 **64 MiB** 上限，超过（即使是 Chrome 的合法回复）以 `payload_limit` 失败（F-082）。默认检查窗口 **500ms**，调用方可选择时长（F-082）。CLI 端点格式为 `http://127.0.0.1:9222`，如 `rea list-browser-targets`、`rea inspect-web-page --observation-ms`（F-082）。

## 阅读下一篇

- [08 · Native 域与专项 Ghidra 深度适配](08-native-ghidra-specialty.md)——Native 调查能力、离线二进制诊断、raw-binary 架构映射，以及 DOS/MIPS/PSP/.NET NativeAOT/Windows P0 专项 Ghidra 适配与其他反编译 Provider（F-083~F-102）
