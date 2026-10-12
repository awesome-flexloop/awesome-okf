---
okf_version: "0.2"
type: Concept
title: "领域类型与证据模型"
description: "REA 的分析结果如何被结构化 —— AnalysisSnapshot 快照、Evidence<Result> 泛型与 EvidenceLocation 证据定位、各目标域领域类型（BrowserScenario/EvmInterface/BinaryTarget/Harmony），以及 Domain 层"纯副作用无关"设计；含 nativeCallRoutes 不存在的勘误（证据：F-057~F-066, F-058, F-043）"
tags: [rea, domain, evidence, analysis-snapshot, typescript, pure-functions, reverse-engineering]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T10:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: local-source
    url: "https://github.com/morluto/rea @ eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
  - id: rea-tools-doc
    url: "https://rea.tools/zh-CN/"
---

# 领域类型与证据模型

> ARTICLE-DEPENDENT 前置：先读 [02 MCP 契约层](02-mcp-contract.md) 与 [03 Provider 适配器](03-provider-adapters.md)。本文是洞察一/二/四证据标准化的底层支撑。

## 核心：结果以「证据 + 覆盖率 + unknowns」结构化

洞察四反复强调：一条结果的「可信度」看它的 `evidence` 与 `unknowns` 字段（F-043）——证据非空、unknowns 小的结果才适合直接交给 agent 后续推理。本文梳理承载这一模型的领域类型定义。

## AnalysisSnapshot：一次快照

- `AnalysisSnapshot`（由 `analysisSnapshotSchema` 推导）及 `AnalysisSnapshotEntry/WorkflowEntry/Target/Binding/PreparedSnapshotEntry`（F-057）。

## Evidence：泛型证据模型

- `Evidence<Result>` 泛型 + `EvidenceLocation/EvidenceSubjectTarget/EvidenceProvider/EvidenceObservation`、`createEvidence()`/`immutableEvidence()`（F-058）。

## 各目标域领域类型

| 域 | 关键类型/函数 | 出处 |
|----|--------------|------|
| Browser 场景 | `BrowserScenario` 类型（`browserScenarioSchema` 推导，含 `browserScenarioInputSchema`） | F-059 |
| EVM 接口 | `EvmInterface` 类型（`evmInterfaceSchema` 推导）与 `InspectEvmInterfaceInput` | F-060 |
| Binary 目标 | `ExecutableMetadata` 类型及 `parseExecutableHeader()`/`parsePeRecord()` 函数 | F-061 |
| HarmonyOS | `HarmonyApplicationProjectionInput/Result` 类型 + `projectHarmonyApplication()` 函数 | F-062 |

## 其余领域模块

其余领域模块文件名（F-063）：`callPath.ts`、`artifactComparison.ts`、`bundleComparison.ts`、`functionComparison.ts`、`webBundleAnalysis.ts`、`webNetworkCapture.ts`、`webRuntime.ts`、`evidenceBundle.ts`、`analysisProfile.ts`、`changedBehavior.ts`、`comparisonStatus.ts`、`runtimeVersion.ts`、`canonicalDigest.ts`、`nativeConvention.ts`、`dosMz.ts`、`peMachine.ts`、`localPath.ts` 等。

## ⚠️ 勘误：nativeCallRoutes 不存在

`nativeCallRoutes` 类型**不存在**于源码（`Grep "nativeCallRoutes" path=src` 无匹配；`src/domain/nativeCallRoutes.ts` 不存在）；native 调用相关模块为 `src/domain/native/*`（如 `nativeAotPe.ts`/`binaryLayout.ts`）与 `nativeCallCommands.ts`（F-064）。引用时不要使用该类型名。

## 架构定位：纯副作用无关

- Domain 层被架构文档定位为纯副作用无关模块（"Pure side-effect-free modules: evidence, comparisons, application graphs"）（F-065）——这也是它可被 CLI 与 MCP 两端共同复用的架构原因。

## 补充：EVM worker 限制

- EVM worker 限制类型 `WorkerLimits`/`EvmWorkerLimits` 与适配 `EvmoleInterfaceAdapter`/`EvmoleInterfaceWorker` 存在于 `src/evm/`（依赖 evmole `package.json:295`，F-066）。

## 阅读下一步

- [04 · 支持的分析目标域与工具矩阵](04-analysis-domains.md)——这些领域类型对应哪些目标域行为