---
type: Concept
title: "支持的分析目标域与工具矩阵"
description: "REA 八大分析目标域的边界与工具要求 —— native 二进制、EVM 字节码、WASM 工制、Android APK/设备（ADB）、.NET managed、固件（Binwalk/Unblob）、进程行为捕获、网站/browser（CDP），含各域的离线/附着/不执行边界（证据：F-043~F-056）"
tags: [rea, analysis-domains, ghidra, evm, wasm, android, dotnet, firmware, browser, process-capture, reverse-engineering]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T10:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: local-source
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
  - id: rea-tools-doc
    resource: "https://rea.tools/zh-CN/"
---

# 支持的分析目标域与工具矩阵

> ARTICLE-DEPENDENT 前置：先读 [03 Provider 适配器](03-provider-adapters.md) 理解 Provider 与工具的关系。本文按目标域查边界（与 insights 知识地图学习路径第 3 步对应）。

## 目标域总览

官网把支持目标概括为（F-055）：

> "native binaries, JavaScript and Electron apps, .NET assemblies, Android packages, firmware, and websites."

加上进程行为与 Android 设备，实际可整理为下表八大域。

## 工具矩阵

| 域 | 入口工具/命令 | 关键性质 | 出处 |
|----|--------------|---------|------|
| Native 二进制 | `inspect_macho`（含选中架构、`file_offset` 语义）等 | "Native UI and dispatch investigation"：静态资源 + native 元数据 + 代码事实结合；每条结果报告 evidence、目标身份、覆盖率与 unknowns | F-043 |
| EVM 字节码 | `inspect_evm_interface`（CLI `inspect-evm-interface`） | 从本地字节码载体推断接口候选，不要求活动 native 目标；载体格式 `hex`/`raw` | F-044 |
| WASM 工制 | `inspect_wasm_artifact`（CLI `inspect-wasm-artifact`） | 用 WABT 检查本地 WASM 字节，**不执行 WASM**；WASM v1 头识别后路由到静态检查而非 `open_binary` | F-045 |
| Android APK | `src/android/` 包装 headless JADX 引擎 | CLI 与 MCP 共用统一应用工作流，返回绑定工制的 Evidence | F-046 |
| Android 设备 | `list-adb-devices`/`capture-adb-screen`/`read-adb-logcat`/`collect-adb-bugreport` 等（ADB） | 对应 ADB 目标域 | F-047 |
| .NET managed | shipped 工具 **7** 个 | 不加载/不执行代码地检查 .NET PE/CLI 工制：识别程序集、检查元数据与 CIL、跨 build 比较成员、把声明原生调用关联到 native 证据 | F-048 |
| 固件 | Binwalk / Unblob | **Binwalk 3.1.x** 做分区检查、**Unblob 26.6.x** 做显式提取；解析器对 Binwalk 3.1.0 与 Unblob 26.6.4 验证；首个固件里程碑在 Linux x64 验证 | F-049 |
| 进程行为 | Process Capture | 运行调用方选择的命令并记录终端行为、计划交互、进程生命周期与有界文件系统状态；支持对同一场景两次直接运行比较；**非沙箱** | F-050 |
| 网站 / Browser | CDP（Chrome DevTools Protocol） | 附加到 user-owned Chrome 系浏览器，对被观察页面产生有界 Evidence；**被动逆向而非通用浏览器自动化** | F-051 |
| Web runtime 源归因 | `observe-web-execution` | 组合 CDP 与 V8 coverage；需要既有 loopback CDP 端点 + 来自 `list_browser_targets` 的 page target；浏览器/页面保持外部拥有 | F-052 |
| Web 网络捕获 | `inspect_web_network_capture`（CLI `inspect-web-network-capture`） | **离线操作**：检查保留的 producer evidence（HAR 输入），不重新拉取 URL、不启动浏览器或 proxy 监听 | F-053 |
| HarmonyOS 包 | `src/artifacts/` 共享 ZIP 工制读取器 | 盘点 HarmonyOS 应用包，把认证清单投影为不执行的程序图；HarmonyOS roadmap(#1431) 第一期增量 | F-054 |

## 默认行为：rea analyze

`rea analyze PATH` 对目录 / `.asar` 文件（未给 `--provider`/`--snapshot` 时）自动选择静态 JavaScript 应用图 + Evidence 工作流（F-056）。

## 边界主题（本地优先、显式选择、有界证据）

洞察四概括了贯穿各域的设计原则（见 [references/insights.md](../references/insights.md)「洞察四」）：REA 不做运行时托管——二进制留在分析工具进程、网站留在用户浏览器、捕获命令留在用户临时环境；只负责发起、收束、把产出规整成证据返回。安全评估时注意 REA 本身不虚拟化/沙箱目标。

## 阅读下一步

- [02 · MCP 契约层](02-mcp-contract.md)——这些目标域对应的契约工具全集
- [06 · 领域类型与证据模型](06-domain-types-and-evidence.md)——结果如何被结构化
