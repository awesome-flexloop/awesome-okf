---
okf_version: "0.2"
type: Reference
title: "REA 源码事实清单（facts）"
description: "REA rea-agents v6.4.0（main@eaf88aca）源码与官方文档的编号事实登记 F-001~F-135：产品身份、CLI 层、MCP 契约层、Provider 适配器、分析目标域、关键领域类型，docs/ 全量文档深层的 JavaScript/Native/专项 Ghidra/平台/工程事实，及 README_zh 的 showcase 案例/前置依赖/更新机制/运行时权限口径"
tags: [rea, facts, mcp, reverse-engineering, source-code]
generated:
  by: source-code-to-okf-wiki:R
  at: "2026-10-12T09:30:00+08:00"
status: stable
stale_after: 2026-12-31
sources:
  - id: local-source
    url: "https://github.com/morluto/rea @ eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
  - id: rea-tools-doc
    url: "https://rea.tools/zh-CN/"
  - id: docs-full
    url: "file" # 本地官方文档全量：external/dao/rea/docs/（49 个 .md，F-067~F-131 来源）
  - id: readme-zh
    url: "file" # 本地 README 简体中文版：external/dao/rea/README_zh.md（F-132~F-135 来源）
---

# REA 源码事实清单（facts.md）

> **信源**：本地源码 `external/dao/rea`（固定 commit `eaf88aca`，npm 包 `rea-agents` v6.4.0，MIT）+ 官方文档 `docs/`。所有文件名/命令名/工具名称保留英文原文；断言为客观描述，无推断词。
> **F-001~F-066** 基于源码 `src/` 与 `docs/` 目标域概述（提取于 2026-10-12 09:30）；**F-067 起**为 2026-10-12 docs 全量深层扩展（覆盖 `docs/` 全部 49 个 `.md` 文件，含 JS/Web、Native/Ghidra 专项、平台、工程与管理文档），来源行号为各文档文件相对行号；**F-132 起**为 README_zh.md（README 简体中文版）补充扩展（官方 showcase 案例、前置依赖聚合、更新机制、运行时权限口径）。
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
- **F-069** 身份策略集合含 `content-digest`/`source-map-original`/`canonical-path`/`artifact-local-key`/`structural-fingerprint`/`runtime-instance`/`observation-fingerprint` 7 种策略（V 阶段已 Grep 复核：源文档 152-158 行表格实际仅列 7 个策略值，文档上下文"8 种"陈述与表格不符，以表格为准）。来源：`javascript-application-graph.md:151-158`。
- **F-070** JS 工作流 MCP 工具共 6 个：`inspect_analysis_view`/`trace_application_feature`/`trace_javascript_semantics`/`compare_application_versions`/`compare_source_to_bundle`/`compare_javascript_export_shapes`；CLI 命令名用连字符替换下划线同名。来源：`javascript-application-workflows.md:5-8`。
- **F-071** `inspect_analysis_view` 不遍历关系；语义图线格式用 `evidence_contexts` 表承载共享来源。来源：`javascript-application-workflows.md:10,26-28`。
- **F-072** `analyze_javascript_application`（CLI `rea analyze-javascript-application`）为 JavaScript 工件重建入口，支持 `.js/.jsx/.mjs/.cjs/.ts/.tsx/.mts/.cts` 共 8 种扩展名。来源：`javascript-artifact-reconstruction.md:6-7,257-258`。
- **F-073** 重建的 `integrity_policy` 接受 `fail` 或 `record-and-continue`；ASAR 完整性检查使用 SHA-256。来源：`javascript-artifact-reconstruction.md:56-57,110-112`。
- **F-074** JavaScript 恢复解析器接受 Wakaru `^1.13.0`，并以 Wakaru **1.14.0** 验证；其 SHA-256 为 `664fa06782a61eda7ed15885134b52525fd565dd77607e642062ceb6cd927c38`；第三方源代码修订固定于 commit `8219bf5016a063d7fb215101a8c45d5959ec733f`；恢复进程使用 util-linux `prlimit`（默认 `/usr/bin/prlimit`）。来源：`javascript-recovery.md:10-11,19-20,25,47-48`。
- **F-075** JS 运行时观测含 2 个 MCP 工具 `list_javascript_runtime_targets`/`observe_javascript_runtime`（CLI 同名）；声明 4 种角色 `node`/`electron-main`/`electron-preload`/`electron-renderer`；捕获预算 8 MiB 聚合、CDP 消息传输上限 16 MiB。来源：`javascript-runtime-observation.md:5-7,109,122-124`。
- **F-076** `reconcile_javascript_runtime`（CLI `rea reconcile-javascript-runtime`）要求 `static_layers` 恰好一个 `application` 角色；映射类型含 `file-root`/`url-prefix` 两种；跨层 `observed_as` 边缘的 `authority` 为 `cross-layer-reconciliation`、`state` 为 `inferred`。来源：`javascript-runtime-reconciliation.md:5-6,54-56,106-108`。

## I. Web/浏览器域细节（docs 深层）

- **F-077** `trace_web_source_location`（CLI `rea trace-web-source-location`）适配器锁定上游 `@jridgewell/trace-mapping` **0.3.31**；生成位置用从 1 开始的行号、从 0 开始的 UTF-16 列号。来源：`web-source-location.md:3,10,17-18,63`。
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
- **F-111** 固件 CLI：`rea inspect-firmware-regions <path>`、`rea extract-firmware <in> <out>`（支持 `--offset`/`--length`/`--max-depth`）；限制输入 128 MiB、deadline 120 秒、继承地址空间 1 GiB、默认临时预算 256 MiB/10,000 条目、每命令 8 MiB stdout+stderr。来源：`firmware-analysis.md:28,52-55,132,136,141`。
- **F-112** Apple 域：`project_apple_application_graph` 接受 `inventory_evidence`（`inventory_artifact` Evidence 数组）；`trace_dylib_resolution` 支持 `--root`（如 `Contents/MacOS/MyApp`）与 `--architecture`（如 `arm64`）；`bundles` 报告每 bundle 的 `parent_path`/`layout`/`info_plist_path`/`executable_candidates`/`signing_paths`。来源：`apple-application-analysis.md:26,91,153`。
- **F-113** Apple 桥接候选序列化数组限制 2 MiB UTF-8 JSON（超出保留确定性前缀）；路径角色 `role_basis` 值为 `"path-convention"`；`verify:macos-bundle` 针对 `otool -l` 的解析器验证。来源：`apple-application-analysis.md:36,101,226`。
- **F-114** Electron 域：`list_electron_targets` 返回单个内联数组；`inspect_electron_page` 需 `include_script_sources` 才返回脚本源；CLI `rea list-electron-targets` 接受 `http://127.0.0.1:9223` 端点、`rea inspect-electron-page` 支持 `--observation-ms`/`--include-script-sources`；Electron 44.7.0 已验证预加载描述符。来源：`electron-observation.md:28,33-34,38,109`。
- **F-115** `capture-electron-scenario` CLI 接受 JSON 请求文件；Electron 启动超时 60 秒。来源：`electron-observation.md:88,100`。
- **F-116** HarmonyOS 域：识别三种根格式 `.hap`（可安装应用模块）/`.hsp`（运行时共享包）/`.app`（分发 App Pack）；`.har` 因也命名 HTTP Archive JSON 而故意不按后缀分类。来源：`harmony-analysis.md:10,18`。
- **F-117** HarmonyOS CLI `rea inspect-artifact /path/Example.hap --format json`；MCP `project_harmony_application_graph` 接受 `inventory_evidence`；打包模型提示仅从 `module.json` 条目声明 Stage、仅从 `config.json` 声明 FA，否则 `unknown`；FA 资源在 `assets/<module>/resources/`、Stage 资源在 `resources/`。来源：`harmony-analysis.md:29,34,40,42`。
- **F-118** HarmonyOS 运行时族提示（`ark`/`native`/`javascript`）来自路径与格式；路径在字节码与 `libs/<abi>` 原生库间基于 N-API 桥接假设；`npm run fixtures:harmony` 下载 SHA-256 固定的 1.0.1 HAP；验证用 `REA_HARMONY_TEST_HAP` 指向 `_reference/harmony-integration/entry-default-unsigned.hap`。来源：`harmony-analysis.md:45-46,56,65`。

## N. 工程与管理（安装/契约/测试/发布/迁移/工作流，docs 深层）

- **F-119** Node 运行时要求 `22.x`/`24.x`/`26.x`（`installation.md:46`）；`mcp-prompts.md` 提供 6 个 agent 提示词：`investigate_feature`/`compare_application_versions`/`verify_reconstruction`/`trace_crash`/`audit_residual_unknowns`/`prepare_bounded_process_capture`。来源：`mcp-prompts.md:9-14`。
- **F-120** MCP 契约输入 schema profile 机制：环境变量 `REA_MCP_INPUT_SCHEMA_PROFILE` 默认 `compact`；`compact` 模式预算 **13,312** 字节、仅保留 9 个字段（`operation`/`function`/`rva`/`offset`/`registers`/`stack`/`memory`/`timestamp`/`correlation_id`）；`full` 模式含 24 个字段。来源：`mcp-contracts.md:48-62`。
- **F-121** 安装支持 17 个客户端 ID：`claude`/`copilot`/`cursor`/`windsurf`/`codeium`/`trae`/`continue`/`cline`/`roo-cline`/`aider`/`void`/`pearai`/`openai-agent`/`anthropic-agent`/`google-agent`/`llm-cmd`/`cat-ai`。来源：`installation.md:146-164`。
- **F-122** DeepSeek Harness 集成需 `@deepseek-ai/dsh@0.2.0-rc.2`；配置文件路径为 `$DSH_HOME/cordis.patch.yml`；`REA_MCP_INPUT_SCHEMA_PROFILE` 支持 `compact`/`full`。来源：`installation.md:260,271,306-307`。
- **F-123** 工具设计命名族（tool-design）：`inspect`/`search`/`trace`/`compare`/`workflow`/`observe`/`capture`。来源：`tool-design.md:16-22`。
- **F-124** 测试与 CI：`verify:deepseek-client` 需 `@deepseek-ai/dsh@0.2.0-rc.2`；CI 矩阵覆盖 Node `22.x`/`24.x`/`26.x`；`verify:hopper` 需 Hopper Pro `4.x`、`verify:ghidra` 需 Ghidra `11.x`、`verify:ida` 需 IDA Pro `8.x`/`9.x`。来源：`testing.md:45-47,268-269,302,320,338`。
- **F-125** 发布策略：Release Please 使用 `always-bump-minor`；版本格式 `v${major}.${minor}.${patch}`，预发布 `v${major}.${minor}.${patch}-${prerelease}`。来源：`releasing.md:45,47,87-91`。
- **F-126** 6.2 迁移：`evidence` 字段的 MCP wrapper 已移除、`analysis_profile` 由可选变必填；迁移工具路径 `tools/migration-6.2.mjs`。来源：`migration-6.2.md:10-24,50-55,78`。
- **F-127** 已记录崩溃分析：`inspect_recorded_crash` 使用 27-register 扩展 ABI；`mcp_inspect_recorded_crash` 支持 `compact`/`full` profile；测试环境 pwndbg 2026.09.15 + GDB 13.1。来源：`recorded-crashes.md:3,30,33-38,54`。
- **F-128** CLI 退出状态码：`0` 成功、`1` 一般错误、`2` 分析错误、`3` 证据保留错误。来源：`cli.md:206-209`。
- **F-129** 重建就绪（reconstruction-readiness）共 9 阶段：`discover-classify`/`diagnose-environment`/`declare-request`/`static-analysis`/`reactive-scenarios`/`compare-authority-candidate`/`preserve-contradictions`/`verify-reconstruction-closure`/`export-replay`。来源：`reconstruction-readiness.md:35-43`。
- **F-130** 义务台账（reconstruction-obligation-ledgers）：`build_reconstruction_obligation_ledger`（CLI `rea build-reconstruction-obligation-ledger`）接受含 `artifacts`/`providers`/`environments`/`scenarios`/`captures`/`unknowns`/`records` 数组的 `evidence_bundle`；结果含 `ledger_id`/`closure_digest`。来源：`reconstruction-obligation-ledgers.md:7,27,323`。
- **F-131** 义务台账 `manifest` 对象含 `bindings`/`contradictions` 数组；`required_case_kinds` 数组可含 `positive`/`negative`/`malformed`/`cancellation`；`reviewed_obligations` 含 `obligation_id`/`obligation_version`/`title`/`application_layer`/`family` 字段。来源：`reconstruction-obligation-ledgers.md:39,62,74`。

## O. README_zh 补充（showcase 案例 / 前置依赖 / 更新机制 / 运行时口径）

> 本节事实来自 `README_zh.md`（README 简体中文版），与 docs/ 全量同 commit `eaf88aca`。行号为 README_zh.md 各文档文件相对行号；英文目标/工具名保留原文。README 的「能力总表」绝大部分目标域细节已由 docs 深挖覆盖（F-067~F-131），本节仅登记 README_zh 独有的、facts 未覆盖的新增点。

- **F-132** 官方 showcase 案例共三例（README_zh.md 第五节）：① **DX-Ball**——沿声音调用追踪到按位置计算声像的辅助函数，检查指令、将不完整伪代码转为 C；重建结果通过 **3,205 个**原始 x86 测试用例、复现编译后函数的全部 **63 个**字节，重建仓库 `github.com/N0zoM1z0/dx-ball`。② **Notion**——沿渲染进程剪贴板 API → preload → IPC → 主进程追踪 Electron 剪贴板桥，并检查富格式剪贴板数据。③ **TH04**——检查原始 PC-98 游戏 **16 位**指令，恢复固定角度/瞄准角度计算，重建 C++ 并与当年编译器输出对比，重建仓库 `github.com/N0zoM1z0/th04`。来源：`README_zh.md:161-181`。
- **F-133** README 能力总表补充 docs 深挖细分的前置依赖聚合口径：离线 ELF 布局与已记录 Linux 崩溃均需 Linux x64 上「调用方提供的 pwntools」，记录崩溃另可选 GDB/pwndbg；已保存网络捕获需 HAR 输入，原生 mitmproxy 捕获需 Linux 上的 `mitmdump`。来源：`README_zh.md:136,138,141`。
- **F-134** 更新机制两条路径：npm 全局安装的 CLI 用 `rea update`；用 `npx` 时通过 `npx rea-agents@latest setup` 更新智能体注册与 skill（含检查设置变更并重启智能体）；单次 CLI 操作可用 `npx rea-agents@latest <command>`。来源：`README_zh.md:99-117`。
- **F-135** 运行时安全口径（README 明示）：静态 JavaScript 与 .NET 检查读取提供的文件、**不运行应用**；运行时捕获（进程/浏览器/运行时观测）会**以你的用户权限**运行目标或与之交互。来源：`README_zh.md:151`。