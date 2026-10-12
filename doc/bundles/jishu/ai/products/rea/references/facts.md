---
okf_version: "0.2"
type: Reference
title: "REA 源码事实清单（facts）"
description: "REA rea-agents v6.4.0（main@eaf88aca）源码与官方文档的编号事实登记 F-001~F-066：产品身份、CLI 层、MCP 契约层、Provider 适配器、分析目标域、关键领域类型"
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
---

# REA 源码事实清单（facts.md）

> **信源**：本地源码 `external/dao/rea`（固定 commit `eaf88aca`，npm 包 `rea-agents` v6.4.0，MIT）+ 官方文档 `docs/`。所有文件名/命令名/工具名称保留英文原文；断言为客观描述，无推断词。
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