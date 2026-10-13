---
type: Concept
title: "Provider 适配器：如何接入分析工具"
description: "REA 为什么不自做反编译 —— 通过可插拔的 Provider 适配器把用户自备的分析工具接入统一 MCP 契约：AnalysisProviderCandidate 接口、Ghidra/IDA/Hopper/JEB/ADB/JADX/Apktool/EVM/WASM/.NET/Browser/Firmware 十二类 Provider 与桥接脚本（证据：F-030~F-042, F-023）"
tags: [rea, provider, adapter, ghidra, ida, hopper, jadx, evm, wasm, reverse-engineering, bridge]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T10:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: local-source
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
  - id: rea-tools-doc
    resource: "https://rea.tools/zh-CN/"
---

# Provider 适配器：如何接入分析工具

> ARTICLE-DEPENDENT 前置：先读 [01 REA 是什么](01-rea-overview.md)。本文与洞察一对应（见 [references/insights.md](../references/insights.md)「洞察一」），是理解「REA 不自做反编译」的核心篇。

## 核心论断：REA 是适配编排层，不是逆向引擎

REA 的「厚度」**不在分析引擎，而在编排与证据标准化**。它把用户自备的逆向工具（native 域的 Ghidra/IDA/Hopper，Android 域的 JADX/Apktool/ADB，字节码域的 EVM/WASM 等）经 Provider 适配器接入统一 MCP 服务，再向 agent 暴露契约化工具。真正的分析计算发生在被适配的工具内（依赖第三方引擎如 evmole、WABT、Binwalk/Unblob、playwright-core）；REA 的职责是「把工具结果 + 静态元数据 + 运行时观测」规整为可被 agent 消费的证据。

## 统一可插拔接口：AnalysisProviderCandidate

原生 Provider 入口统一实现 `AnalysisProviderCandidate` 接口——说明存在**可插拔适配器契约**，而非硬编码单一路径（F-042）：

- `GhidraProvider`（src/ghidra/GhidraProvider.ts，F-030）
- `IdaProvider`（src/ida/IdaProvider.ts，F-031）
- `HopperProvider`（src/hopper/HopperProvider.ts，F-032）

## 各域 Provider（存在证据按厂商/协议）

| Provider | 文件 | 关键组件 | 出处 |
|----------|------|---------|------|
| Ghidra | `src/ghidra/GhidraProvider.ts` | `GhidraClient/GhidraLauncher/GhidraTransport/GhidraDoctor/GhidraInstallation` | F-030 |
| IDA | `src/ida/IdaProvider.ts` | `IdaSessionClient/IdaCallGraph/IdaDoctor/IdaConfiguration` | F-031 |
| Hopper | `src/hopper/HopperProvider.ts` | `BridgeLauncher/HopperClient/HopperRegexSearch/protocol.ts`；`bridge/hopper_bridge.py` 在 Hopper 内适配其 Python API | F-032 |
| JEB | `src/jeb/JebProvider.ts` | `JebMcpConnection/JebMcpEndpoint` 与 `JEB_PROVIDER_IDENTITY`，实现 `JebAnalysisPort` | F-033 |
| ADB | `src/adb/AdbProvider.ts` | `ADB_PROVIDER_IDENTITY`、`AdbConfiguration/AdbDeviceOutput/AdbHostFileName` | F-034 |
| Android(JADX) | `src/android/JadxProvider.ts` | `JadxProtocol/JadxSession/JadxMcpTransport`，实现 `AndroidAnalysisPort`；Java 桥 `bridge/android/ReaJadxBridge.java` | F-035 |
| Apktool | `src/apktool/ApktoolProvider.ts` | `APKTOOL_PROVIDER_IDENTITY` | F-036 |
| EVM | `src/evm/` | `EvmBytecodeCarrier/EvmoleInterfaceAdapter/EvmoleInterfaceWorker/EvmoleRelease`，依赖 `evmole@0.9.3` | F-037 |
| WASM | `src/wasm/WabtArtifactProvider.ts` | `WabtOutput/WasmGlueAdapter`（依赖 WABT），实现 `WasmArtifactPort` | F-038 |
| .NET Managed | `src/dotnet/` | `ManagedPeReader/ManagedMemberRows/ManagedDecodeBudget`（PE/CLI 元数据读取） | F-039 |
| Browser | `src/browser/` | `CdpBrowserProvider/CdpConnection/CdpPageCapture/CdpScreenshot/CdpCaptureEvents/HarCapture`，依赖 `playwright-core@1.58.2`、`har-schema@2.0.0` | F-040 |
| Firmware | `src/firmware/FirmwareProvider.ts` | `FirmwareCommand/FirmwareFiles/FirmwareRelease`，实现 `FirmwareAnalysisPort` | F-041 |

> 注：Provider 是「与工具的真实接口面」——含真实桥接脚本（如 Hopper 的 `bridge/hopper_bridge.py`、JADX 的 Java 桥 `ReaJadxBridge.java`）。想深挖某目标域，从对应 `*Provider.ts` 入手，而不是从 CLI 命令入手。

## 与 kind 的对应

每种 Provider 对应契约层的一种 kind（F-023，见 [02 MCP 契约层](02-mcp-contract.md)）：如 `native-provider`（Ghidra/IDA/Hopper）、`android-provider`（JADX）、`apktool-provider`、`jeb-provider`、`adb-provider`、`firmware-provider`、`browser-provider`、`electron-provider` 等。新增目标域支持时，参照 `AnalysisProviderCandidate`/`*Provider.ts` 的适配器模式 + 在 `TOOL_KINDS` 新增一个 kind，而非在 CLI 层硬塞命令。

## 价值主张与边界

- **价值**：让 agent 不必分别学 Ghidra 脚本、ADB 命令、evmole 接口——它们统一成同构工具名与证据返回，把 agent 的学习成本从「每工具一套协议」降为「一套 REA 契约」。
- **代价**：能力上限受用户自备工具与环境约束；REA 不绑定分析引擎，用它前先确认已有对应工具。

## 阅读下一步

- [04 · 支持的分析目标域与工具矩阵](04-analysis-domains.md)——这些 Provider 支撑哪些目标域与边界
- [06 · 领域类型与证据模型](06-domain-types-and-evidence.md)——分析结果如何被规整为证据
