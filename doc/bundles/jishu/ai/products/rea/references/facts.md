---
type: Reference
title: "REA 源码事实清单（facts）"
description: "REA 固定源码、技术文档、README 与中文官网的编号事实 F-001~F-180"
tags: [rea, facts, mcp, reverse-engineering, source-code]
generated:
  by: source-code-to-okf-wiki:R
  at: "2026-10-12T09:30:00+08:00"
status: stable
stale_after: 2026-12-31
sources:
  - id: local-source
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
  - id: rea-tools-doc
    resource: "https://rea.tools/zh-CN/"
  - id: docs-full
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/docs"
  - id: readme-zh
    resource: "https://github.com/morluto/rea/blob/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/README_zh.md"
  - id: official-site-full
    resource: official-site-source.md
---

# REA 源码事实清单（facts.md）

> **信源**：本地源码 `external/dao/rea`（固定 commit `eaf88aca`，npm 包 `rea-agents` v6.4.0，MIT）+ 官方文档 `docs/`。所有文件名/命令名/工具名称保留英文原文；断言为客观描述，无推断词。
> **F-001~F-066** 基于源码 `src/` 与 `docs/` 目标域概述（提取于 2026-10-12 09:30）；**F-067 起**为 2026-10-12 docs 深层扩展（固定提交的 `docs/` 含 48 个 `.md` 文件；这是文件计数，不代表每文件均有独立事实条目），来源行号为各文档文件相对行号；**F-132 起**为 README_zh.md（README 简体中文版）补充扩展（官方 showcase 案例、前置依赖聚合、更新机制、运行时权限口径）。
> **计数纪律**：凡「X 个」数量断言均标注计数方法与独立 Grep 输出数字，实施者与独立审查者可复跑。四条核心计数已经实施者独立复核：CLI 顶层命令 129、TOOL_CONTRACTS spread 24 组、官方桥接工具 38、`*ToolContracts.ts` 中 `name:` 工具名 100 处/21 文件。

## A. 产品身份

- **F-001** npm 包名为 `rea-agents`。来源：`package.json:2`（`"name": "rea-agents"`）。
- **F-002** 版本为 `6.4.0`。来源：`package.json:4`（`"version": "6.4.0"`）。
- **F-003** License 为 MIT。来源：`package.json:6`（`"license": "MIT"`）与根 `LICENSE` 文件（首行 "MIT License"，Copyright (c) 2026 morluto，`LICENSE:3`）。
- **F-004** MCP 服务名（mcpName）为 `io.github.morluto/rea`。来源：`package.json:3`。
- **F-005** npm 主仓库为 `morluto/rea`（`git+https://github.com/morluto/rea.git`，homepage `https://github.com/morluto/rea#readme`）。来源：`package.json:9,11`。
- **F-006** 官方定位语：英文 description "Reverse engineer anything from your terminal or agent with one CLI and MCP server."。来源：`package.json:5`。
- **F-007** engines 声明的 Node 支持为 `^22.19.0 || ^24.11.0 || >=26.0.0`（Node 23/25 及 prerelease 不支持）。来源：`package.json:40-42` 与 `docs/installation.md:46`。
- **F-008** 存量包管理器声明为 `npm@11.16.0`。来源：`package.json:43`。
- **F-009** 模块类型为 ESM（`"type": "module"`）。来源：`package.json:32`。

## B. CLI 层

- **F-010** bin 同时注册 `rea` 与 `rea-agents` 两个命令，均指向 `scripts/rea.mjs`。来源：`package.json:36-39`。
- **F-011** `scripts/rea.mjs` 双层路由：单参 `--mcp`/`mcp` 进入 MCP 服务模式（加载 `dist/mcp/main.js`），否则进入 one-shot CLI 模式（加载 `dist/cli.js`）；`mcp doctor` 加载 `dist/mcpDoctor.js`。来源：`scripts/rea.mjs:15-37,45-58`。
- **F-012** CLI 顶层命令由 `CLI_COMMANDS` 对象以 kebab-case 字符串集中声明。来源：`src/cliCommandNames.ts:2-132`。
- **F-013** CLI 顶层命令总数为 **129** 个。计数：`Grep "^  \w+: \"[\w-]+\",$" path=src/cliCommandNames.ts` → `129`（实施者独立复跑一致）。
- **F-014** 一级代表性命令名含 `analyze`、`inspect`、`decompile`、`setup`、`doctor`、`uninstall`、`update`、`xrefs`、`trace`、`search`、`function`、`providers`、`capabilities`、`instructions`、`compare`、`capture-process`、`evidence-import`、`evidence-export` 等。来源：`src/cliCommandNames.ts`。
- **F-015** 命令别名机制：`CLI_COMMAND_ALIASES` 声明一个别名 `compare-bundles`。来源：`src/cliCommandNames.ts:138`。
- **F-016** 命令到 MCP 工具映射在 `CLI_COMMAND_TOOL_ALIASES` 声明，如 `analyze → binary_overview`、`inspect → binary_overview`、`decompile → procedure_pseudo_code`、`function → analyze_function`、`search → search_strings/search_procedures`、`trace → trace_feature`。来源：`src/cliCommandNames.ts:141-151`。
- **F-017** 存在 `MCP_TOOLS_WITHOUT_DEDICATED_CLI`（无专用 CLI、仅 MCP 暴露的工具），含 `analyze_function`、`compare_functions`、`compare_artifacts`、`export_evidence_bundle`、`import_evidence_bundle`、`correlate_static_and_runtime`、`get_call_graph`、`open_binary`、`close_binary`、`binary_session` 等约 50+ 项。来源：`src/cliCommandNames.ts:154-208`。
- **F-018** CLI 由 `createCli()` 构建，各命令族以 `registerXxxCommands()` 注册（如 `registerWasmCommands`、`registerEvmCommands`、`registerSetupCommands`、`registerAdbCommands`、`registerBrowserCommands` 等），CLI 框架依赖 `incur@0.6.1`。来源：`src/cli.ts:1-41`、`package.json:298`。

## C. MCP 契约层

- **F-019** MCP 工具契约单一聚合清单为 `TOOL_CONTRACTS`，以只读 `as const` 数组聚合导出。来源：`src/contracts/toolContracts.ts:27-52`。
- **F-020** `TOOL_CONTRACTS` 由 **24** 个工具契约数组 spread 汇总而成。计数：`Grep "^  \.\.\.[A-Z_]+" path=src/contracts/toolContracts.ts` → `24`（实施者独立复跑一致）。
- **F-021** 这 24 组聚合自 24 个导入变量（如 `OFFICIAL_TOOL_CONTRACTS`、`ENHANCED_TOOL_CONTRACTS`、`NATIVE_TOOL_CONTRACTS`、`EVM_TOOL_CONTRACTS`、`WASM_TOOL_CONTRACTS`、`ADB_TOOL_CONTRACTS`、`FIRMWARE_TOOL_CONTRACTS` 等）。来源：`src/contracts/toolContracts.ts:1-24`。
- **F-022** 通用契约类型 `ToolContract<Name, InputSchema, OutputSchema>`，字段含 `name/title/description/kind/inputSchema/outputSchema/effects/annotations/examples`。来源：`src/contracts/toolContractTypes.ts:43-61`。
- **F-023** `TOOL_KINDS` 定义 **15** 种 kind：`official-proxy`、`enhanced`、`native-provider`、`artifact-provider`、`managed-provider`、`android-provider`、`apktool-provider`、`jeb-provider`、`adb-provider`、`firmware-provider`、`browser-provider`、`electron-provider`、`runtime-provider`、`application`、`session`。来源：`src/contracts/toolContractTypes.ts:21-37`。
- **F-024** 官方桥接工具 `OFFICIAL_TOOL_CONTRACTS`（kind=official-proxy）在 `officialToolContracts.ts` 以 `official("name", ...)` 声明 **38** 个。计数：`Grep "^  official\(" path=src/contracts/officialToolContracts.ts` → `38`（实施者独立复跑一致）。
- **F-025** 官方工具名含 `annotate_native_function`、`inspect_native_load_image`、`inspect_native_data_type`、`inspect_native_instruction`、`resolve_native_call_targets`、`address_name`、`comment`、`current_address`、`goto_address`、`inline_comment`、`list_bookmarks`、`list_documents`、`list_names`、`list_procedures`、`list_segments`、`list_strings`、`procedure_pseudo_code`、`read_function_instructions`、`search_procedures`、`search_strings`、`set_address_name`、`xrefs` 等。来源：`src/contracts/officialToolContracts.ts:39-237`。
- **F-026** 官方工具另含来自 Hopper 内存契约扩展（`...HOPPER_MEMORY_TOOL_DEFINITIONS.map(...official)`），定义于 `src/contracts/hopperMemoryContracts.ts`。来源：`officialToolContracts.ts:170-172`。
- **F-027** 各域工具契约按子域文件分散：`wasm/wasmToolContracts.ts`、`evm/evmToolContracts.ts`、`firmware/firmwareToolContracts.ts`、`android/androidToolContracts.ts`、`apktool/apktoolToolContracts.ts`、`jeb/jebToolContracts.ts`、`adb/adbToolContracts.ts`、`managed/managedToolContracts.ts`、`javascript/electronToolContracts.ts`、`javascript/javascriptRecoveryToolContracts.ts`、`native/nativeToolContracts.ts`、`native/binaryDiagnosticsToolContracts.ts` 等。来源：`src/contracts/toolContracts.ts:1-24` import 路径。
- **F-028** 21 个 `*ToolContracts.ts` 文件中，以 `name: "..."` 属性形式直接声明工具名合计 **100** 处（不含 `official("...")` 函数形式的 `officialToolContracts.ts`）。计数：`Grep glob="*ToolContracts.ts" pattern="name: \"" path=src/contracts` → `100` total / `21` files（实施者独立复跑一致）。
- **F-029** 会话健康/目录身份工具 `binary_session` 是运行中服务目录身份与工具可用性的权威来源（`tools/list` 返回完整工具清单、含当前不可用工具）。来源：`docs/mcp-contracts.md:13-24`。

## D. Provider 适配器（存在证据按厂商/协议）

- **F-030** Ghidra Provider：`src/ghidra/GhidraProvider.ts` 导出 `class GhidraProvider implements AnalysisProviderCandidate`（`:70`），含 `GhidraClient/GhidraLauncher/GhidraTransport/GhidraDoctor/GhidraInstallation` 等。
- **F-031** IDA Provider：`src/ida/IdaProvider.ts` 导出 `class IdaProvider implements AnalysisProviderCandidate`（`:36`），含 `IdaSessionClient/IdaCallGraph/IdaDoctor/IdaConfiguration` 等。
- **F-032** Hopper Provider：`src/hopper/HopperProvider.ts` 导出 `class HopperProvider implements AnalysisProviderCandidate`（`:38`），含 `BridgeLauncher/HopperClient/HopperRegexSearch/protocol.ts`；`bridge/hopper_bridge.py` 在 Hopper 内适配其 Python API。
- **F-033** JEB Provider：`src/jeb/JebProvider.ts` 导出 `class JebProvider implements JebAnalysisPort`（`:102`），含 `JebMcpConnection/JebMcpEndpoint` 与 `JEB_PROVIDER_IDENTITY`。
- **F-034** ADB Provider：`src/adb/AdbProvider.ts` 导出 `class AdbProvider`（`:470`），含 `ADB_PROVIDER_IDENTITY`、`AdbConfiguration/AdbDeviceOutput/AdbHostFileName`。
- **F-035** Android(JADX) Provider：`src/android/JadxProvider.ts` 导出 `class JadxProvider implements AndroidAnalysisPort`（`:222`），含 `JadxProtocol/JadxSession/JadxMcpTransport`；Java 桥 `bridge/android/ReaJadxBridge.java`。
- **F-036** Apktool Provider：`src/apktool/ApktoolProvider.ts` 导出 `class ApktoolProvider`（`:312`），含 `APKTOOL_PROVIDER_IDENTITY`。
- **F-037** EVM Provider：`src/evm/` 含 `EvmBytecodeCarrier.ts`、`EvmoleInterfaceAdapter.ts`、`EvmoleInterfaceWorker.ts`、`EvmoleRelease.ts`，依赖 `evmole@0.9.3`（`package.json:295`）。
- **F-038** WASM Provider：`src/wasm/WabtArtifactProvider.ts` 导出 `class WabtArtifactProvider implements WasmArtifactPort`（`:43`），含 `WabtOutput/WasmGlueAdapter`（依赖 WABT）。
- **F-039** .NET Managed Provider：`src/dotnet/` 含 `ManagedPeReader.ts`、`ManagedMemberRows.ts`、`ManagedDecodeBudget.ts`（PE/CLI 元数据读取）。
- **F-040** Browser Provider：`src/browser/` 含 `CdpBrowserProvider.ts`、`CdpConnection.ts`、`CdpPageCapture.ts`、`CdpScreenshot.ts`、`CdpCaptureEvents.ts`、`HarCapture.ts` 等，依赖 `playwright-core@1.58.2`、`har-schema@2.0.0`。
- **F-041** Firmware Provider：`src/firmware/FirmwareProvider.ts` 导出 `class FirmwareProvider implements FirmwareAnalysisPort`（`:104`），含 `FirmwareCommand/FirmwareFiles/FirmwareRelease`。
- **F-042** 原生 Provider 入口统一实现 `AnalysisProviderCandidate` 接口：`GhidraProvider`/`IdaProvider`/`HopperProvider` 三类均实现。来源：`GhidraProvider.ts:70`、`IdaProvider.ts:36`、`HopperProvider.ts:38`。

## E. 分析目标域（docs 功能描述）

- **F-043** Native 二进制域：`docs/native-investigation.md` 定义 "Native UI and dispatch investigation"，静态资源、native 元数据与代码事实结合，每条结果报告 evidence、目标身份、覆盖率与 unknowns；含 `inspect_macho` 选中架构、`file_offset` 语义。
- **F-044** EVM 字节码域：`inspect_evm_interface`（CLI `inspect-evm-interface`）从用户选择的本地字节码载体推断接口候选，不要求活动 native 目标；载体格式支持 `hex`/`raw`。来源：`docs/evm-bytecode.md:1-11`。
- **F-045** WASM 工制域：`inspect_wasm_artifact`（CLI `inspect-wasm-artifact`）用调用方提供的 WABT 检查本地 WASM 字节，不执行 WASM；WASM v1 头识别后路由到静态检查而非 `open_binary`。来源：`docs/wasm-artifacts.md:1-11`。
- **F-046** Android APK 域：REA 通过 `src/android/` 包装固定 headless JADX 引擎，CLI 与 MCP 共用统一应用工作流并返回绑定工制的 Evidence。来源：`docs/android-analysis.md:1-6`。
- **F-047** Android 设备域：`docs/adb-device-analysis.md` 对应 ADB 目标；`cliCommandNames.ts` 含 `list-adb-devices`、`capture-adb-screen`、`read-adb-logcat`、`collect-adb-bugreport` 等命令族。
- **F-048** .NET managed 域：REA 不加载/执行代码地检查 .NET PE/CLI 工制，识别程序集、检查元数据与 CIL、跨 build 比较成员、把声明原生调用关联到 native 证据；文档声明 shipped 工具 **7** 个。来源：`docs/managed-code-analysis.md:1-9`。
- **F-049** 固件域：REA 接受 **Binwalk 3.1.x** 做分区检查、**Unblob 26.6.x** 做显式提取；解析器对 Binwalk 3.1.0 与 Unblob 26.6.4 验证；首个固件里程碑在 Linux x64 验证。来源：`docs/firmware-analysis.md:1-10`。
- **F-050** 进程行为域：Process Capture 运行调用方选择的命令并记录终端行为、计划交互、进程生命周期与有界文件系统状态；支持对同一场景的两次直接运行做比较；非沙箱。来源：`docs/process-capture.md:1-11`。
- **F-051** 网站/browser 域：REA 通过 Chrome DevTools Protocol（CDP）附加到 user-owned Chrome 系浏览器，对被观察页面产生有界 Evidence，是被动逆向能力而非通用浏览器自动化。来源：`docs/browser-observation.md:1-9`。
- **F-052** Web runtime 源归因域：`observe-web-execution` 组合 CDP 与 V8 coverage 两个工具，需要既有 loopback CDP 端点 + 来自 `list_browser_targets` 的 page target；浏览器/页面保持外部拥有。来源：`docs/web-runtime.md:1-9`。
- **F-053** Web 网络捕获域：`inspect_web_network_capture`（CLI `inspect-web-network-capture`）为离线操作，检查保留的 producer evidence（HAR 输入），不重新拉取 URL、不启动浏览器或 proxy 监听。来源：`docs/web-network-captures.md:1-9`。
- **F-054** HarmonyOS 包域：REA 经 `src/artifacts/` 共享 ZIP 工制读取器盘点 HarmonyOS 应用包，把认证清单投影为不执行的程序图；为 HarmonyOS roadmap(#1431) 第一期增量。来源：`docs/harmony-analysis.md:1-9`。
- **F-055** 官网把目标域概括为 "native binaries, JavaScript and Electron apps, .NET assemblies, Android packages, firmware, and websites"。来源：`docs/index.md:21`。
- **F-056** `rea analyze PATH` 对目录/`.asar` 文件在未给 `--provider`/`--snapshot` 时自动选择静态 JavaScript 应用图 + Evidence 工作流。来源：`docs/cli.md:16-17`。

## F. 关键领域类型（src/domain）

- **F-057** `AnalysisSnapshot`（由 `analysisSnapshotSchema` 推导）及 `AnalysisSnapshotEntry/WorkflowEntry/Target/Binding/PreparedSnapshotEntry`。来源：`src/domain/analysisSnapshot.ts:154-171`。
- **F-058** `Evidence<Result>` 泛型 + `EvidenceLocation/EvidenceSubjectTarget/EvidenceProvider/EvidenceObservation`、`createEvidence()`/`immutableEvidence()`。来源：`src/domain/evidence.ts:172-345`。
- **F-059** `BrowserScenario` 类型（`browserScenarioSchema` 推导，含 `browserScenarioInputSchema`）。来源：`src/domain/browserScenario.ts:137`。
- **F-060** `EvmInterface` 类型（`evmInterfaceSchema` 推导）与 `InspectEvmInterfaceInput`。来源：`src/domain/evm/evmInterface.ts:73-76`。
- **F-061** `BinaryTarget` 域：`ExecutableMetadata` 类型及 `parseExecutableHeader()`/`parsePeRecord()` 函数。来源：`src/domain/binaryTarget.ts:10,43,212`。
- **F-062** HarmonyOS 域：`HarmonyApplicationProjectionInput/Result` 类型 + `projectHarmonyApplication()` 函数。来源：`src/domain/harmony/harmonyApplication.ts:74-83`。
- **F-063** 其余领域模块文件名：`callPath.ts`、`artifactComparison.ts`、`bundleComparison.ts`、`functionComparison.ts`、`webBundleAnalysis.ts`、`webNetworkCapture.ts`、`webRuntime.ts`、`evidenceBundle.ts`、`analysisProfile.ts`、`changedBehavior.ts`、`comparisonStatus.ts`、`runtimeVersion.ts`、`canonicalDigest.ts`、`nativeConvention.ts`、`dosMz.ts`、`peMachine.ts`、`localPath.ts` 等。来源：`src/domain/` 目录清单。
- **F-064** `nativeCallRoutes` 类型**不存在**于源码（`Grep "nativeCallRoutes" path=src` 无匹配；`src/domain/nativeCallRoutes.ts` 不存在）；native 调用相关模块为 `src/domain/native/*`（如 `nativeAotPe.ts`/`binaryLayout.ts`）与 `nativeCallCommands.ts`。修正了任务预置名称。
- **F-065** Domain 层被架构文档定位为纯副作用无关模块（"Pure side-effect-free modules: evidence, comparisons, application graphs"）。来源：`docs/architecture.mermaid:56-57`。
- **F-066** EVM worker 限制类型 `WorkerLimits`/`EvmWorkerLimits` 与适配 `EvmoleInterfaceAdapter`/`EvmoleInterfaceWorker` 存在于 `src/evm/`。来源：`src/evm/` 目录 + `package.json:295`（evmole 依赖）。

## H. JavaScript 应用图与工作流（docs 深层）

- **F-067** JavaScript 应用图是一种 schema 值为 `"JavaScriptApplicationGraph"` 的有向图；观察 ID 用 `semantic-content-sha256` 推导、边缘 ID 用 `relationship-exact` 稳定性。来源：`javascript-application-graph.md:40,167-168`。
- **F-068** 应用图有向关系词汇表含 `contains`/`loads`/`imports`/`maps_to`/`exposes`/`sends`/`invokes`/`handles`/`calls`/`persists_to`/`observed_as`/`changed_from` 共 **12** 个值（V 阶段已 Grep 复核：源文档 71-73 行清单 12 项核实无误）。来源：`javascript-application-graph.md:71-73`。
- **F-069** 身份策略表列 `content-digest`/`source-map-original`/`canonical-path`/`artifact-local-key`/`structural-fingerprint`/`runtime-instance`/`observation-fingerprint` 7 种策略；对固定文档表格行逐项匹配计数为7。此前“上游上下文声称8种”是本知识包错误归因，本轮回读未发现该上游声明。来源：`javascript-application-graph.md:151-158`。
- **F-070** JS 工作流 MCP 工具共 6 个：`inspect_analysis_view`/`trace_application_feature`/`trace_javascript_semantics`/`compare_application_versions`/`compare_source_to_bundle`/`compare_javascript_export_shapes`；CLI 命令名用连字符替换下划线同名。来源：`javascript-application-workflows.md:5-8`。
- **F-071** `inspect_analysis_view` 不遍历关系；语义图线格式用 `evidence_contexts` 表承载共享来源。来源：`javascript-application-workflows.md:10,26-28`。
- **F-072** `analyze_javascript_application`（CLI `rea analyze-javascript-application`）为 JavaScript 工件重建入口，支持 `.js/.jsx/.mjs/.cjs/.ts/.tsx/.mts/.cts` 共 8 种扩展名。来源：`javascript-artifact-reconstruction.md:6-7,257-258`。
- **F-073** 重建的 `integrity_policy` 接受 `fail` 或 `record-and-continue`；ASAR 完整性检查使用 SHA-256。来源：`javascript-artifact-reconstruction.md:56-57,110-112`。
- **F-074** JavaScript 恢复解析器接受 Wakaru `^1.13.0`，并以 Wakaru **1.14.0** 验证；其 SHA-256 为 `664fa06782a61eda7ed15885134b52525fd565dd77607e642062ceb6cd927c38`；第三方源代码修订固定于 commit `8219bf5016a063d7fb215101a8c45d5959ec733f`；恢复进程使用 util-linux `prlimit`（默认 `/usr/bin/prlimit`）。来源：`javascript-recovery.md:10-11,19-20,25,47-48`。
- **F-075** JS 运行时观测含 2 个 MCP 工具 `list_javascript_runtime_targets`/`observe_javascript_runtime`（CLI 同名）；声明 4 种角色 `node`/`electron-main`/`electron-preload`/`electron-renderer`；捕获预算 8 MiB 聚合、CDP 消息传输上限 16 MiB。来源：`javascript-runtime-observation.md:5-7,109,122-124`。
- **F-076** `reconcile_javascript_runtime`（CLI `rea reconcile-javascript-runtime`）要求 `static_layers` 恰好一个 `application` 角色；映射类型含 `file-root`/`url-prefix` 两种；跨层 `observed_as` 边缘的 `authority` 为 `cross-layer-reconciliation`、`state` 为 `inferred`。来源：`javascript-runtime-reconciliation.md:5-6,54-56,106-108`。

## I. Web/浏览器域细节（docs 深层）

- **F-077** `trace_web_source_location`（CLI `rea trace-web-source-location`）适配器锁定上游 `@jridgewell/trace-mapping` **0.3.31**；六个位置参数依次为 manifest、从0开始的 script index、绝对 map path、绝对 map URL context、从1开始的 generated line、从0开始的 UTF-16 column。URL作为 sources/sourceRoot 解析上下文，不指示网络获取。来源：`docs/web-source-location.md`「CLI」与参数说明。
- **F-078** `trace_web_module_imports`（CLI `rea trace-web-module-imports`）中 `script_index` 在 `manifest.scripts` 内从 0 开始；`additional_paths` 最多接受 16 个额外文件；清单/源/导入映射分别限制 32 MiB/16 MiB/4 MiB。来源：`website-module-trace.md:3,17,38,78-79` + `javascript-artifact-reconstruction.md:81`。
- **F-079** `export_web_scripts`（CLI `rea export-web-scripts`）将脚本源写入目标文件，目标须不存在；被动检查选择 `include_script_sources: true`（CLI `--include-script-sources`），场景须 `capture.network.response_body: true`。来源：`website-script-export.md:3,10-12,20,30-31`。
- **F-080** `capture_browser_scenario`（CLI `rea capture-browser-scenario INPUT_JSON`）支持 `launch`/`connect` 两种浏览器模式，`headless` 默认 `true`，`environment.service_workers` 默认阻止、可设为 `allow`。来源：`browser-scenario-contract.md:3,5,11,16-17,31,134-135`。
- **F-081** 浏览器观测共享排除词汇 `BrowserExclusionReason` 覆盖所有栈的每条拒绝原因；`discover_webmcp_tools` 使用实验性 CDP WebMCP 域返回每个注册及其完整 observed `input_schema` 声明与规范 `input_schema_sha256` 摘要。来源：`browser-observation.md:17,60-61`。
- **F-082** CDP 连接对每条 WebSocket 消息强制 **64 MiB** 上限；默认检查窗口 500 毫秒；CLI 端点为 `http://127.0.0.1:9222` 格式（`rea list-browser-targets`、`rea inspect-web-page --observation-ms`）。来源：`browser-observation.md:87,106-107,185`。

## J. Native 域与二进制诊断（docs 深层）

- **F-083** `inspect_macho` 的 `selected_architecture` 报告 `container_file_offset` 与所选架构 `file_offset`；`trace_dylib_resolution` 解析 Mach-O load commands 并跟踪 `@rpath`/`@loader_path`/`@executable_path`。来源：`native-investigation.md:9-13,42-48`。
- **F-084** `inspect_asset_catalog` 经 macOS `assetutil --info` 读取编译后的 `Assets.car`；`inspect_keyed_archive` 读取 XML 或 binary Foundation keyed archives，限制 64 MiB 输入、200,000 objects/references、128 嵌套层级。来源：`native-investigation.md:49-65`。
- **F-085** `trace_native_ui_action` 接受 authored selector/object ID、native symbol 或 exact function address；`observe_native_calls` 通过 LLDB 启动 Mach-O 并记录 breakpoints，限制 8 MiB retained event JSON、65,536 caller frames。来源：`native-investigation.md:274-281,349-391`。
- **F-086** `inspect_binary_layout` 需要 pwntools 4.15.0、pyelftools 0.33、Unicorn 2.1.2，可用环境变量 `REA_PWNTOOLS_PYTHON` 指定 Python 可执行文件；限制 32 MiB 输入、64 MiB 回复、1 MiB 组合诊断、30 秒命令期限；Python 进程限制 3 GiB 虚拟地址空间/30 CPU 秒/64 MiB 文件输出。来源：`binary-diagnostics.md:11-17,100-109`。
- **F-087** raw-binary 模式经 `--target-format raw-binary` + `--architecture` 选择，映射表为 `x86→x86:LE:32:default`、`x86_64→x86:LE:64:default`、`arm→ARM:LE:32:v7`、`arm64→AARCH64:LE:64:v8A`；ARM/AArch64 须 4-byte 对齐、x86 可 byte 对齐；Ghidra 用 `BinaryLoader`。来源：`raw-binary.md:10-13,31,37,42-45`。

## K. 专项 Ghidra 支持（docs 深层）

- **F-088** Ghidra Provider 支持 Linux x64/arm64 与 macOS x64/arm64；实验性 Windows x64 P0 为只读、无 database mutation authority；需 Ghidra 12.1.x 与 64-bit full JDK；`analyzeHeadless` import 产生 exactly one Program。来源：`ghidra-provider.md:4-5,16-18,28`。
- **F-089** Ghidra Provider 地址格式为 `0x` 小写十六进制或 `<percent-encoded-space>:0x<hex>`；字符串搜索仅覆盖 Ghidra-defined string `Data`；p-code value flow 限制 3,000 operations、64 inputs/operation、12,000 def-use edges。来源：`ghidra-provider.md:29,38-42,55`。
- **F-090** DOS 支持 MZ executables 与 explicit COM images（验证用 Ghidra 12.1.4 + JDK 21）；MZ 用 `MzLoader` + `x86:LE:16:Real Mode`；COM 用 `BinaryLoader`，文件 offset zero 映射到 `1000:0100`（linear `0x10100`），COM 大小限制 1..65280 bytes。来源：`ghidra-dos.md:3,6-7,34-35,67-69`。
- **F-091** MIPS 支持 ELF32 `ET_EXEC`/`ET_REL`（little/big endian），要求 explicit o32 与 `EF_MIPS_ARCH_32R2`，拒绝 `EF_MIPS_FP64`/`EF_MIPS_NAN2008`；MIPS16 共享库支持 ELF32 `ET_DYN`。来源：`ghidra-mips.md:16-17,25-26,53-56`。
- **F-092** MIPS soft-float 原型策略键值 `mips_soft_float_storage: o32-soft-float-prototype-v1`；可重定位对象轨道键值 `mips_support_lane: elf32-rel-o32-arch32r2-standard-v1`。来源：`ghidra-mips.md:126-127,156-157`。
- **F-093** PSP 支持 Linux x64、little-endian ELF32 `ET_EXEC`/`EM_MIPS`，PSPSDK `e_flags=0x10a23001`（MIPS II, Allegrex, EABI32, NOREORDER）；验证环境 PSPDEV v20261001（GNU readelf 2.44）+ Ghidra 12.1.3 + extension v21.4 + JDK 21；Loader `PspElfLoader`、language `Allegrex:LE:32:default`。来源：`ghidra-psp.md:11-18,35-36,60-62`。
- **F-094** NativeAOT 支持 x64 PE32+ 与 .NET 8 RTR 9.1 metadata，基于 Washi1337/ghidra-nativeaot commit `effeb734fc570c32650f88b159608979dc7b423e`，并交叉核对 .NET MethodTable.h commit `a3b2d40328be0be3f8dd43f0e5cc925b8827b044`。来源：`ghidra-nativeaot.md:3,7-10,17-18`。
- **F-095** ghidra-nativeaot 限制 128 MiB captured PE bytes、64 MiB-equivalent parser work、64 MiB overlay/index Buffers、4 MiB serialized JSON；Windows P0 无 database mutation authority。来源：`ghidra-nativeaot.md:94-97,109-110`。
- **F-096** Windows P0 支持 Windows 10+ x64、local NTFS target 与 temporary volumes；Ghidra 12.1.x（验证 12.1.4）+ 64-bit full JDK 21+；提供 **25** 个只读 Ghidra inventory/memory/function-analysis 操作；MCP `timeoutMs` 默认 300000；验证命令 `npm run verify:ghidra:windows`。来源：`windows-ghidra-p0.md:16-21,98,169-177`。

## L. 其他反编译工具 Provider（docs 深层）

- **F-097** IDA Provider 基于 mrexodia/ida-pro-mcp，支持 upstream **1.4.0 legacy tools**（`get_metadata`/`list_functions`/`decompile_function`）；环境变量 `REA_IDA_MCP_CONFIG` 指定配置、`REA_ANALYSIS_PROVIDER=ida` 选择 provider；支持 attached（GUI）与 headless（`--stdio`）模式。来源：`ida-provider.md:3,5-9,25-26,39-47`。
- **F-098** IDA MCP `timeoutMs` 默认 300000（5 分钟）；验证环境 IDA 9.3（Windows）+ IDA Professional 9.1 build 9.1.250226（macOS arm64）；验证命令 `npm run verify:ida -- --target <path> --procedure main`。来源：`ida-provider.md:95,111,113`。
- **F-099** JEB 分析默认 endpoint `http://127.0.0.1:8425/mcp`；验证版本 JEB 5.48.0（Linux x64）+ `jeb-mcp-server` 1.3.0；headless JEB 5.48 `-c` 模式不直接接受 `--mcp`；提供 4 个 MCP 工具/CLI 命令（`inspect_jeb_client`/`open_jeb_project`/`list_jeb_units`/`decompile_jeb_item`）。来源：`jeb-analysis.md:9,11,13,19-22`。
- **F-100** JEB `list_units` 分页上限 100。来源：`jeb-analysis.md:32`。
- **F-101** Apktool 验证版本 2.7.0；环境变量 `REA_APKTOOL_COMMAND` 指定启动器；readiness 检查 `rea inspect-apktool-client`；Smali 被跳过（`apktool d --no-src`）。来源：`apktool-resource-analysis.md:11,15-22,63-65,89-90`。
- **F-102** Apktool 解码限制 600 秒 deadline、4 MiB output capture、Manifest 读取 512 KiB、Strings XML 8 MiB、`decoded_file_count` 上限 100,000；验证命令 `npm run verify:apktool -- --apk PATH`。来源：`apktool-resource-analysis.md:74,77-81,88`。

## M. 平台分析域（Android/ADB/Managed/Firmware/Apple/Electron/Harmony 深层）

- **F-103** Android (JADX) 域：`inspect_android_package`/`search_android_classes`/`inspect_android_class`/`inspect_android_method`/`trace_android_references` 为等价 MCP 方法；需 JDK 17+ 与 `jadx-headless-mcp 0.7.1`；环境变量 `REA_JADX_MCP_JAR` 指向 JAR、可选 `JAVA_HOME`。来源：`android-analysis.md:14-15,21-23,70`。
- **F-104** Android 执行受限：deadline 120 秒（上游反编译 90 秒）、清单与方法文本预算 1 MiB、类名页面索引切片最多 4096 名称、协议帧 8 MiB、stdout/stderr 32 MiB、会话 60 秒不活动清理。来源：`android-analysis.md:185,230,233-235`。
- **F-105** ADB 域：`inspect_adb_client`/`list_adb_devices`/`inspect_adb_device`/`inspect_adb_display`/`list_adb_features`/`list_adb_services` 为 ADB 设备操作；支持 adb **34.0.5**、环境变量 `REA_ADB_PATH` 指定二进制。来源：`adb-device-analysis.md:16,21,33`。
- **F-106** ADB 命令族含 `rea inspect-adb-client`（运行 `adb version`）、`rea list-adb-devices`、`rea inspect-adb-device <serial>`、`rea pull-adb-package --output-directory`、`rea capture-adb-screen`、`rea collect-adb-bugreport`、`rea install-adb-package --replace`；每个调用组合固定 adb 参数向量，调用值仅作位置参数被引用。来源：`adb-device-analysis.md:7-8,25,34-60`。
- **F-107** .NET Managed 域的 7 个 MCP 工具为 `inspect_managed_artifact`/`inspect_managed_members`/`inspect_managed_native_boundaries`/`compare_managed_members`/`verify_managed_native_boundaries`/`import_managed_reconstruction`/`project_managed_application_graph`；CLI 用连字符同名（如 `rea inspect-managed-artifact`）。来源：`managed-code-analysis.md:10,21`。
- **F-108** Managed 静态提供者承认最大 128 MiB 常规输入；元数据/CIL 解码/投影检查各 64 MiB 表示预算；`il_sha256` 基于精确 `il_size` 原始 CIL 字节（tiny/fat 方法头之后）、`normalized_il_sha256` 基于 UTF-8 `JSON.stringify` 的 `[opcode,operand_kind,operand]` 指令数组。来源：`managed-code-analysis.md:49,51,196-197`。
- **F-109** 解码 `nop; ret` 序列化为 `[["nop","none",null],["ret","none",null]]`，其摘要为 `5e5fad7741cb44bca3a4f045546b7449990da343f612f5f34c0ca30e9eee0636`。来源：`managed-code-analysis.md:220`。
- **F-110** 固件域：接受 Binwalk 3.1.x（区域检查）与 Unblob 26.6.x（显式提取），解析器验证 Binwalk 3.1.0 与 Unblob 26.6.4；环境变量 `REA_BINWALK_COMMAND`/`REA_UNBLOB_COMMAND`；检查与提取都需 util-linux `prlimit`（正常路径 `/usr/bin/prlimit`，可用 `REA_FIRMWARE_PRLIMIT_COMMAND` 覆盖）。来源：`firmware-analysis.md:3-4,17-18,25-26`。
- **F-111** 固件 CLI：`rea inspect-firmware-regions <path>`、`rea extract-firmware <in> <out>`（`--offset`/`--length`必须成对，可选`--max-depth`）；提取写文件，输出绝对路径须不存在且父目录已存在，CLI将相对路径解析为绝对路径。`complete`仅指声明范围内提取完成。限制输入128 MiB、deadline120秒、继承地址空间1 GiB、默认临时预算256 MiB/10,000条目、每命令8 MiB stdout+stderr。来源：`docs/firmware-analysis.md`「CLI」「Extraction」与`src/cli/firmwareCommands.ts`。
- **F-112** Apple 域：`project_apple_application_graph` 接受 `inventory_evidence`（`inventory_artifact` Evidence 数组）；`trace_dylib_resolution` 支持 `--root`（如 `Contents/MacOS/MyApp`）与 `--architecture`（如 `arm64`）；`bundles` 报告每 bundle 的 `parent_path`/`layout`/`info_plist_path`/`executable_candidates`/`signing_paths`。来源：`apple-application-analysis.md:26,91,153`。
- **F-113** Apple 桥接候选序列化数组限制 2 MiB UTF-8 JSON（超出保留确定性前缀）；路径角色 `role_basis` 值为 `"path-convention"`；`verify:macos-bundle` 针对 `otool -l` 的解析器验证。来源：`apple-application-analysis.md:36,101,226`。
- **F-114** Electron 域：`list_electron_targets` 返回单个内联数组；`inspect_electron_page` 需 `include_script_sources` 才返回脚本源；CLI `rea list-electron-targets` 接受 `http://127.0.0.1:9223` 端点、`rea inspect-electron-page` 支持 `--observation-ms`/`--include-script-sources`；Electron 44.7.0 已验证预加载描述符。来源：`electron-observation.md:28,33-34,38,109`。
- **F-115** `capture-electron-scenario` CLI 接受符合`capture_electron_scenario`的内联JSON或JSON请求文件；该主动场景启动应用并管理生命周期，Electron启动超时60秒。来源：`docs/electron-observation.md`「Owned scenarios」与`src/cli/electronCommands.ts`的`inputJson`注册。
- **F-116** HarmonyOS 域：识别三种根格式 `.hap`（可安装应用模块）/`.hsp`（运行时共享包）/`.app`（分发 App Pack）；`.har` 因也命名 HTTP Archive JSON 而故意不按后缀分类。来源：`harmony-analysis.md:10,18`。
- **F-117** HarmonyOS CLI `rea inspect-artifact /path/Example.hap --format json`；MCP `project_harmony_application_graph` 接受 `inventory_evidence`；打包模型提示仅从 `module.json` 条目声明 Stage、仅从 `config.json` 声明 FA，否则 `unknown`；FA 资源在 `assets/<module>/resources/`、Stage 资源在 `resources/`。来源：`harmony-analysis.md:29,34,40,42`。
- **F-118** HarmonyOS 运行时族提示（`ark`/`native`/`javascript`）来自路径与格式；路径在字节码与 `libs/<abi>` 原生库间基于 N-API 桥接假设；`npm run fixtures:harmony` 下载 SHA-256 固定的 1.0.1 HAP；验证用 `REA_HARMONY_TEST_HAP` 指向 `_reference/harmony-integration/entry-default-unsigned.hap`。来源：`harmony-analysis.md:45-46,56,65`。

## N. 工程与管理（安装/契约/测试/发布/迁移/工作流，docs 深层）

- **F-119** Node运行时支持范围为`^22.19.0 || ^24.11.0 || >=26.0.0`（F-007）；`mcp-prompts.md`提供6个agent提示词：`investigate_feature`/`compare_application_versions`/`verify_reconstruction`/`trace_crash`/`audit_residual_unknowns`/`prepare_bounded_process_capture`。来源：`installation.md:46`、`package.json:40-42`、`mcp-prompts.md:9-14`。
- **F-120** `REA_MCP_INPUT_SCHEMA_PROFILE`默认`full`；可选`compact`将每个广告输入JSON Schema限制在13,312字节，启动时读取、改动需重启。它仅改变广告输入schema，不改变工具全集、输出schema、annotations及canonical服务端验证；六个复杂工具允许约化广告。没有固定“9字段/24字段”分档。来源：固定`docs/mcp-contracts.md`「Compact input schema profile」。
- **F-121** 固定`SUPPORTED_CLIENT_DEFINITIONS`登记18项，其中17项为文件型配置：`claude_code`/`claude_desktop`/`codex`/`cursor`/`gemini_cli`/`windsurf`/`devin`/`opencode`/`antigravity`/`copilot_cli`/`commandcode`/`qwen_code`/`vscode`/`grok_build`/`omp`/`pi`/`hermes`；额外`grok_bot`为`format: "unsupported"`，需在账户中手动接入，不写本地连接器文件。计数：固定blob中定义数组的`name`匹配18、唯一18，`format: "unsupported"`匹配1；与`docs/installation.md`「Supported agents」的17行表对账。
- **F-122** DeepSeek Harness 集成需 `@deepseek-ai/dsh@0.2.0-rc.2`；配置文件路径为 `$DSH_HOME/cordis.patch.yml`；`REA_MCP_INPUT_SCHEMA_PROFILE` 支持 `compact`/`full`。来源：`installation.md:260,271,306-307`。
- **F-123** 工具设计命名族（tool-design）：`inspect`/`search`/`trace`/`compare`/`workflow`/`observe`/`capture`。来源：`tool-design.md:16-22`。
- **F-124** 固定CI多数job读取`.nvmrc`的24.18.0，路径边界专项另用Node22.19.0；package矩阵按变更选Linux/macOS的x64/arm64，不是22/24/26主版本矩阵。Ghidra接受12.1.x，记录基线12.1.4/JDK21；Hopper FAT/FAT64轨道验证于6.1.0-demo，不证明原生FAT64 loader支持。IDA记录Windows x64 9.3及macOS arm64 headless Professional9.1 build9.1.250226，modern supervisor固定`c133c3853faa111a9b00ee615c013b720d0c4acd`，legacy attached GUI为upstream1.4.0；Linux headless、其他版本/架构及真实HTTP supervisor仍未验证。`verify:deepseek-client`需`@deepseek-ai/dsh@0.2.0-rc.2`。来源：`.nvmrc`、`.github/workflows/ci.yml`、`scripts/ci/plan.mjs:175-185`、`docs/testing.md`与`docs/ida-provider.md`。
- **F-125** 发布策略：Release Please 使用 `always-bump-minor`；版本格式 `v${major}.${minor}.${patch}`，预发布 `v${major}.${minor}.${patch}-${prerelease}`。来源：`releasing.md:45,47,87-91`。
- **F-126** 6.2 迁移：`evidence` 字段的 MCP wrapper 已移除、`analysis_profile` 由可选变必填；迁移工具路径 `tools/migration-6.2.mjs`。来源：`migration-6.2.md:10-24,50-55,78`。
- **F-127** 已记录崩溃分析：`inspect_recorded_crash` 使用 27-register 扩展 ABI；`mcp_inspect_recorded_crash` 支持 `compact`/`full` profile；测试环境 pwndbg 2026.09.15 + GDB 13.1。来源：`recorded-crashes.md:3,30,33-38,54`。
- **F-128** CLI 退出状态码：`0` 成功、`1` 一般错误、`2` 分析错误、`3` 证据保留错误。来源：`cli.md:206-209`。
- **F-129** 重建就绪（reconstruction-readiness）共 9 阶段：`discover-classify`/`diagnose-environment`/`declare-request`/`static-analysis`/`reactive-scenarios`/`compare-authority-candidate`/`preserve-contradictions`/`verify-reconstruction-closure`/`export-replay`。来源：`reconstruction-readiness.md:35-43`。
- **F-130** 义务台账（reconstruction-obligation-ledgers）：`build_reconstruction_obligation_ledger`（CLI `rea build-reconstruction-obligation-ledger`）接受含 `artifacts`/`providers`/`environments`/`scenarios`/`captures`/`unknowns`/`records` 数组的 `evidence_bundle`；结果含 `ledger_id`/`closure_digest`。来源：`reconstruction-obligation-ledgers.md:7,27,323`。
- **F-131** 义务台账 `manifest` 对象含 `bindings`/`contradictions` 数组；`required_case_kinds` 数组可含 `positive`/`negative`/`malformed`/`cancellation`；`reviewed_obligations` 含 `obligation_id`/`obligation_version`/`title`/`application_layer`/`family` 字段。来源：`reconstruction-obligation-ledgers.md:39,62,74`。

## O. README_zh 补充（showcase 案例 / 前置依赖 / 更新机制 / 运行时口径）

> 本节事实来自 `README_zh.md`（README 简体中文版），与 docs/ 全量同 commit `eaf88aca`。行号为 README_zh.md 各文档文件相对行号；英文目标/工具名保留原文。README 的「能力总表」绝大部分目标域细节已由 docs 深挖覆盖（F-067~F-131），本节仅登记 README_zh 独有的、facts 未覆盖的新增点。

- **F-132** README_zh 的 showcase 列三例：DX-Ball 声像重建、Notion 剪贴板桥、TH04 DOS 环形子弹恢复；README 自述 DX-Ball 通过 3,205 个原始 x86 用例并匹配完整函数 63 字节。来源：`README_zh.md:160-178`。此为 README 范围，不代表官网只有三例；各案例证据强度与历史版本见 F-153~F-172。
- **F-133** README 能力总表补充 docs 深挖细分的前置依赖聚合口径：离线 ELF 布局与已记录 Linux 崩溃均需 Linux x64 上「调用方提供的 pwntools」，记录崩溃另可选 GDB/pwndbg；已保存网络捕获需 HAR 输入，原生 mitmproxy 捕获需 Linux 上的 `mitmdump`。来源：`README_zh.md:135,137,140`。
- **F-134** 更新机制两条路径：npm 全局安装的 CLI 用 `rea update`；用 `npx` 时通过 `npx rea-agents@latest setup` 更新智能体注册与 skill（含检查设置变更并重启智能体）；单次 CLI 操作可用 `npx rea-agents@latest <command>`。来源：`README_zh.md:99-117`。
- **F-135** 运行时安全口径（README 明示）：静态 JavaScript 与 .NET 检查读取提供的文件、**不运行应用**；运行时捕获（进程/浏览器/运行时观测）会**以你的用户权限**运行目标或与之交互。来源：`README_zh.md:150`。

## P. 中文官网安装与首次调查

本轮从 F-136 续接。W01~W17 的完整 URL 和已读章节见 [官网台账](official-site-source.md)。下列页面与证据资产属于同一上游；历史成绩均为官方记录（SINGLE-SOURCE），不声称本机重新完成目标实验。固定证据文件均位于 `website/evidence/`，提交同本地基线。

- **F-136** 中文 sitemap 去重集合与按来源页解析的站内链接集合均为 17 页，两集合差集为空。来源：sitemap XML 与 W01~W17 HTML；口径排除语言副本及资源文件。
- **F-137** 官网 setup 命令为 `npx rea-agents@latest setup`；页面说明先展示配置计划、确认后写入 MCP 连接及调查技能、备份旧配置，完成后重启客户端。来源：W02「连接编程助手」、W03 第1步。
- **F-138** 官网区分静态 JS/ASAR 调查与原生引擎；Windows Ghidra 路径使用 `GHIDRA_INSTALL_DIR`/`JAVA_HOME`，实验性只读支持本地固定 NTFS 驱动器上的 x86/x64 PE 与 DLL。来源：W02「配置原生分析」；固定技术文档见 F-088/F-096。
- **F-139** 官网 IDA doctor 仅检查注册，不启动 IDA；headless 记录覆盖 IDA 9.3 Windows x64 supervisor，Linux/macOS headless 尚未验证。来源：W02「IDA」；此为官网 headless 范围，不否定 F-098 的其他历史配置。
- **F-140** 官网说明 one-shot CLI 每条命令导入、分析、关闭二进制会话；MCP 可在会话保持打开时复用导入。来源：W02「原生分析会话如何工作」。
- **F-141** 首次调查示例是六文件 Notes Electron fixture，静态记录解析四个 JS 文件、零解析失败、一个字面 IPC 唯一配对。来源：W03、W07；`guide-examples.md`「Notes Electron example」。六文件不等于六个 JS 文件。
- **F-142** Notes 路径由 `renderer.js` 调用 `notes.exportCsv()`、`preload.js` invoke `notes:export`、`main.js` handler 调用 `toCsv` 并将 `notes.csv` 写入 `app.getPath("downloads")`；CSV 列为 id/title。来源：W03 第3步、W07「follow」、fixture 源码。
- **F-143** 输入 id=1、title=`Hello, "REA"`，formatter 输出 `id,title` 与 `1,"Hello, ""REA"""`，末尾有换行。上游执行的是提取 ZIP 的 `csv.js`，未启动 Electron。来源：W03 第4步、`guide-examples.md`「First-investigation formatter check」。
- **F-144** Notes 浏览器捕获记录一次 GET notes.json、200/application-json，JSON 包含 notes 数组；CSV 在前端构造。捕获期间由独立 Playwright controller 点击，REA 未执行点击。来源：W08；`guide-examples.md`「Notes browser example」。
- **F-145** 浏览器指南先发现 page target，再对已启动用户浏览器观察有界窗口；只能覆盖附着后发生的请求。来源：W08；固定文档 F-051/F-082。

## Q. 首页与恐龙实验

- **F-146** 官网计算器记录的目标为 Windows Calculator 11.2508.4.0 x64；calc.exe 调用 `ShellExecuteW` 的 ms-calculator launcher，百分比逻辑在 CalcViewModel.dll。来源：W01 计算器；`calculator-and-dino.md`「Inspected artifacts」。
- **F-147** 计算器函数选择经人工指令扫描辅助；示例 prompt 不是自主端到端发现的录屏。Microsoft 固定源码是交叉解释依据，未识别为该安装包 build commit。来源：W01 证据；`calculator-and-dino.md`「Source interpretation and check」。
- **F-148** 百分比摘要：乘除路径当前值除100；其他操作路径当前值乘前值/100。官网固定输入200和10的控件按摘要计算；Microsoft tests只读未执行，Windows GUI输入验证未完成。来源：W01、`calculator-and-dino.md`。
- **F-149** 恐龙原目标是 wayou HTTP 浏览器版本，非 chrome://dino/。REA4.1.0返回其 index.js，摘要匹配 wayou commit `5455bfa408ec6b707c7300ff194b7390733a766d`。来源：W01、W15；`calculator-and-dino.md`「Running target and source」。
- **F-150** 速度起始6、阈值13、增量0.001；collision-free update 先比较 speed<13再相加。独立 controller 对原 Runner.update() 的10000次调用记录13.000999999997896，三位小数13.001。来源：W15；`calculator-and-dino.md`「Controlled original-game check」。
- **F-151** 教学 dino-speed.js 复用速度更新规则；小游戏按60updates/sec推进，绘图、跳跃、碰撞和控件是新教学代码，重建范围只含速度。来源：W15、`calculator-and-dino.md`「New game and reader experiment」。
- **F-152** 首页实验、三类指南和 DX-Ball/Notion/TH04/CTF 的大部分分析记录使用REA4.1.0；Aegis使用6.1.0。本知识包固定源码6.4.0不等于历史实验运行版本。来源：上述固定证据文件的版本头。

## R. 五项官网 showcase

- **F-153** DX-Ball目标1.07，PE i386；函数0x406400..0x40643e为63字节（末地址包含在内）。记录环境REA4.1.0/Ghidra12.1.4/Linuxx64。来源：W06/W10、`dx-ball-sound-pan.md`「Artifact and provider」。
- **F-154** DX-Ball指令读取栈[EBP+8]整型x，依次乘1.5625、减500、乘存储scale、调用__ftol转整数；caller计算20+30×砖块横坐标。可读函数名属于维护源码，原伪代码未完整恢复栈输入及x87表达式。来源：W10、`dx-ball-sound-pan.md`「Observations and interpretation」。
- **F-155** DX-Ball3205用例口径为整数位置0..640共641项×五个scale {0,0.5,1,20,-1}；VC4.0完整函数63字节匹配包括已审重定位和引用常量核对。官网复用历史结果，未重跑compiler/runtime；游戏级集成另行验证。来源：W10、`dx-ball-sound-pan.md`「Validation scope」。
- **F-156** Notion案例目标Desktop7.6.1，REA4.1.0检查tab preload发现动态__electronApi与动态invoke(channel=null)。来源：W11、`notion-clipboard.md`「Fresh REA result」。
- **F-157** Notion API seed trace为partial，17nodes/16edges/零terminal；字面channel seed无graphmatch。完整四步clipboard route来自额外wrapper源码阅读，不是自动配对图或真实desktop capture。来源：W11、`notion-clipboard.md`。
- **F-158** Notion web editor模块来自2026-07-13缓存build，与Desktop ASAR分别登记身份；marker+本地private MIME恢复以提取/提升helpers及stub harness检查，不证明OS clipboard hydration或复杂block实际保真。来源：W11、`notion-clipboard.md`「Separately cached web-editor code」。
- **F-159** Notion SQLite初始化通过MessageChannelMain转移port，后续statement batch/results经该port；此为源码handoff解释，未捕获SQL session。来源：W11、`notion-clipboard.md`「SQLite follow-up」。
- **F-160** Aegis3.4.3 APK，REA6.1.0/jadx-headless-mcp0.7.1/OpenJDK21/Linuxx64；默认SHA1、六位、30秒，不是所有账户固定参数。来源：W13、`aegis-login-code.md`「Target/Interpretation」。
- **F-161** Aegis timestamp先floor(seconds/period)，counter以八字节big-endian编码、HMAC、末hash低四位选offset、31bit正整数、mod10^digits并补零。APK的generateOTP/getHash在kotlin.ExceptionsKt，不能只按原源码HOTP类名找。来源：W13、`aegis-login-code.md`。
- **F-162** Aegis133输入分解为0..120每整秒121输入+六个RFC6238 SHA1八位向量+对应六个六位结果=133；提取Java方法harness、独立Python与WebCrypto一致。APK未执行。来源：W13、`aegis-login-code.md`「Reconstruction checks」。
- **F-163** Aegis公开测试key为ASCII12345678901234567890；30/59秒六位结果287082，60秒359152；相邻时间块重新计算，但不能保证任意相邻验证码都不同。来源：W13、`aegis-login-code.md`。
- **F-164** Aegis证据不覆盖AndroidUI、vault、signature verification、splitAPK或native libraries。来源：W13、`aegis-login-code.md`「Scope and maintenance」。
- **F-165** CTF目标为DownUnderCTF2023 masked-squares-flag-checker，strippedELFx86-64，15248bytes；REA4.1.0/Ghidra12.1.4/Linuxx64。来源：W14、`ctf-masked-squares.md`「Target」。
- **F-166** CTF36输入字符、26mask×24bytes；0x270/0x18=26。读取target144bytes中前104bytes为26个little-endian int，后部含padding/table；mask总读取624bytes。来源：W14、`ctf-masked-squares.md`「Discovery/Interpretation」。
- **F-167** CTF mask为signed runlength，正数写1、负数写0、零结束；第七项eb01f200表示-21,+1,-14，只选index21，target55即字符7。来源：W14、`ctf-masked-squares.md`。
- **F-168** CTF solver附加的alphabet及DUCTF前后缀为分析者假设，非二进制事实。返回候选DUCTF{ezzzpzzz_07bcda7bfe81faf43caa}满足26方程；第二模型搜索超时，未证明唯一解。来源：W14、`ctf-masked-squares.md`「Solver and source cross-check」。
- **F-169** 上游CTF原程序正例输出Correct!/exit0，改单字符负例输出Incorrect!/exit255；本轮未重跑原程序。来源：W14、`ctf-masked-squares.md`「Original-program verification」。
- **F-170** TH04 MAIN.EXE为DOSMZ，156258bytes=6144header+150114module；loadsegment0x1000，helper entry0x2cfc8对应fileoffset0x1e7c8。来源：W12、`th04-bullet-ring.md`「Original target and analysis」。
- **F-171** TH04 helper body非连续：两范围共503bytes，包围span517bytes；index*256/count后加aim与rotation，最终bytewrap。count16是tune前模板初值；aimed_ring_angle是教学摘要，非完整compiler-sensitive helper。来源：W12、`th04-bullet-ring.md`「Instructions and source meaning/Figure」。
- **F-172** TH04历史TurboC++4.0J两次coldbuild匹配2139byte完整bullet-add extent及MAP/relocation，不是摘要函数、整EXE或全游戏；原target provenance为candidate-local-attested，未增加独立pristine证明；nearcall segmentalias可能产生误导静态图边。来源：W12、`th04-bullet-ring.md`。

## S. 东方博客与命令勘误依据

- **F-173** 博客耗时是UTC commit committer timestamp间隔/86400的calendar days，非personhours、compute或受控speedup；函数分母随审查变动，未采用跨游戏完成率。来源：W17、`touhou-reconstruction-method.md`「Collection and counting」。
- **F-174** TH08续作继承GensokyoClub历史和署名，TH04引用ReC98；历史项目另用专用bridges/scripts，不能将所有结果重新标为REA产出。来源：W17、`touhou-reconstruction-method.md`「Method sources」。
- **F-175** TH08旧比较器把reference地址写入指令重定位字段后仅比指令，未核对引用浮点数据；ItemManager::OnUpdate源码0.0曾对目标128.0通过。来源：W17、`touhou-reconstruction-method.md`「TH08's floating-literal oracle failure」。
- **F-176** 上游后续审计1548个floating-literal references（非不同常量或函数数），修复另12个stale references/5已accepted函数；加入故意无效literal声明与表示的负例测试。来源：W17、同证据章节。
- **F-177** 后来推荐顺序为exact code/data基线→原平台working wholeprogram→双验证路径semantic reconstruction→现代port；TH08早期portable releases先于部分历史平台audit。来源：W17、`touhou-reconstruction-method.md`「Readability and the learned phase order」。
- **F-178** TH04 Normal routes/endings/saves为维护者人工Windows观察；64bitport仍开发，非官网新自动测试。source ownership及名称解释仍需producer/consumer证据。来源：W17、`touhou-reconstruction-method.md`「TH04's current DOS and 64-bit phases/Readability」。
- **F-179** 固定6.4.0 CLI function/decompile均有path及可选address位置参数、--procedure选择器；本轮采用已知地址。其schema无--function选项。来源：W02 function示例；固定`src/cli/coreBinaryCommands.ts`的function/decompile注册。
- **F-180** inspect-electron-page必填endpoint/targetId；本轮旧示例漏参应修为发现target后再观察。来源：W02/W08发现后观察流程；固定`src/cli/electronCommands.ts`注册。

## 本轮勘误轨迹

2026-10-12：F-132/133/135的README行号分别收窄到160-178、135/137/140、150；保留原编号。官网新增五项案例不改变README“三例”范围。旧showcase示例中的sound-pan/ring_bullets未经证明是目标符号，改用证据地址；移除不存在的--function，补齐Electron endpoint/targetId。完整核验记录见本轮验证文档。

2026-10-12：修正F-069的8种错误归因、F-119的宽泛Node版本；补齐CLI目标路径及EVM/网络捕获的格式位置参数。JS后续工作流改读完整Evidence，删除虚构的`from`结构及输入生成前的调用。`closure_digest`是包含unknowns与矛盾的台账结果标识，不证明闭包完成；Electron/Browser主动capture及ADB副作用不受被动inspect边界概括。详见[本轮验证记录](official-site-verification.md)。

2026-10-12：固定提交`git ls-tree`计数将docs的49改为48，收窄全读断言；F-120默认compact与9/24字段均无源文依据，改为默认full和广告输入schema预算。F-121替换无依据客户端列表，区分18登记/17文件型/1手动；F-124删除旧引擎版本与Node矩阵断言，分别列验证轨道。F-077/F-111/F-115补全参数、写入与内联JSON边界，原编号不变。
