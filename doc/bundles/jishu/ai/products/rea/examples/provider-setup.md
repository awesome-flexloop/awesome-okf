---
type: Example
title: "REA：分析工具安装与 Provider 接入"
description: "Ghidra/IDA/Hopper/JADX/ADB/EVM/WASM/固件工具链的本地准备与 REA doctor 校验——按目标域安装自备分析工具并让 Provider 可被 REA 识别（证据 F-030~F-041, F-049）"
tags: [rea, example, provider, ghidra, ida, hopper, jadx, adb, evm, wasm, firmware, setup]
generated: { by: "source-code-to-okf-wiki:E", at: "2026-10-12T10:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: local-source
    resource: "https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a"
  - id: rea-tools-doc
    resource: "https://rea.tools/zh-CN/"
---

# 示例：分析工具安装与 Provider 接入

> ⚠️ **可复现性说明**：本示例为「外部分析工具 + Provider」的接入对号表。REA **不自带**这些引擎，而是在你已安装的前提下通过 Provider 适配器接入（F-030~F-041）。具体安装命令为第三方工具官方安装操作，本示例仅罗列 REA 侧的「Provider 存在证据」；工具安装形态以各自官方文档为准，**未在本机逐项实跑**。

## 目标

确认你的目标分析域所需的自备工具已装好，且 REA 侧对应 Provider 存在、可被 `rea doctor`/`rea capabilities` 校验。

## 输入

- 已用 `npx rea-agents setup` 初始化的 REA（见 [cli-and-mcp-usage.md](cli-and-mcp-usage.md)）。
- 按目标域安装相应第三方工具。

## 步骤

### 1. 确认 REA 侧 Provider 存在证据（按目标域对号）

| 目标域 | 需要自备 | REA 侧 Provider（facts 证据） | 说明 |
|--------|---------|------------------------------|------|
| Native 二进制 | Ghidra | `GhidraProvider`/`GhidraClient/GhidraLauncher/GhidraDoctor/GhidraInstallation`（F-030） | 实现 `AnalysisProviderCandidate`（F-042） |
| Native 二进制 | IDA | `IdaProvider`/`IdaSessionClient/IdaDoctor`（F-031） | 实现 `AnalysisProviderCandidate`（F-042） |
| Native 二进制 | Hopper | `HopperProvider`/`BridgeLauncher/HopperClient`；`bridge/hopper_bridge.py` 在 Hopper 内适配其 Python API（F-032） | 实现 `AnalysisProviderCandidate`（F-042） |
| Android APK | JADX | `JadxProvider`/`JadxProtocol/JadxMcpTransport`；Java 桥 `bridge/android/ReaJadxBridge.java`（F-035） | 实现 `AndroidAnalysisPort`；headless JADX 引擎（F-046） |
| Android | Apktool | `ApktoolProvider`（F-036） | - |
| Android 设备 | ADB | `AdbProvider`/`AdbConfiguration`（F-034） | 见 `list-adb-devices` 等命令（F-047） |
| Android 包混排 | JEB | `JebProvider`/`JebMcpConnection`（F-033） | 实现 `JebAnalysisPort` |
| EVM 字节码 | (内置 evmole) | `src/evm/`，依赖 `evmole@0.9.3`（F-037） | 载体 `hex`/`raw`（F-044） |
| WASM 工制 | WABT | `WabtArtifactProvider`/`WasmGlueAdapter`（F-038） | 不执行 WASM（F-045） |
| .NET managed | (REA 自带读器) | `src/dotnet/`：`ManagedPeReader` 等（F-039） | 不加载/不执行（F-048），shipped 工具 7 个 |
| 固件 | Binwalk / Unblob | `FirmwareProvider`（F-041） | **Binwalk 3.1.x**、**Unblob 26.6.x**（F-049） |
| 网站 / Browser | user-owned Chrome | `src/browser/`：`CdpBrowserProvider` 等（F-040） | 依赖 `playwright-core`/`har-schema`（F-040） |

### 2. 安装第三方工具（按目标域）

- **Ghidra / IDA / Hopper**：从各自官网/仓库安装到本机；REA 通过 `GhidraDoctor`/`IdaDoctor`/`HopperBridgeLauncher` 等识别与拉起（F-030/031/032）。具体安装二进制请遵循官方发布。
- **Android**：`adb`（Android SDK platform-tools，F-034）；JADX（F-035）；Apktool（F-036）。
- **固件**：安装 **Binwalk 3.1.x** 与 **Unblob 26.6.x**（官方解析器对 3.1.0 / 26.6.4 验证，F-049）。
- **WASM**：本机具备 WABT 工具链供 `WabtArtifactProvider` 使用（F-038）。
- **网站**：准备 user-owned Chrome 系浏览器 + 可附加的 CDP 端点（F-051）。

> EVM、.NET 为目标内置能力（evmole / PE-CLI 读器），无需额外第三方引擎（F-037/039）。

### 3. REA 侧校验

```bash
rea doctor        # 检查 Provider / 工具链就绪（F-014）
rea capabilities  # 查看能力全集（F-014）
rea providers     # 查看已注册 Provider（F-014）
rea mcp doctor    # 若走 MCP，单独校验 MCP doctor（F-011）
```

**预期**：doctor/`capabilities` 报告对应 Provider 就绪；未就绪项提示缺失的工具链。

### 4. 校验目标域特定命令可用

```bash
rea inspect-evm-interface "D:/analysis/bytecode.hex" hex --json
rea inspect-wasm-artifact "D:/analysis/module.wasm" --json
rea inspect-web-network-capture "D:/analysis/capture.har" har --json
rea list-adb-devices        # ADB 设备（F-047）
```

路径须替换为真实文件。EVM 的第二位置参数是 `raw` 或 `hex`；网络捕获的第二位置参数是 `har` 或 `mitmproxy`。这些调用处理实际输入，不是仅查询命令是否注册，本轮未执行。

## 输出 / 验收

- [ ] 目标域所需第三方工具已装好
- [ ] `rea doctor` / `rea capabilities` 报告对应 Provider 就绪（F-014）
- [ ] 目标域代表命令可运行（如 `rea list-adb-devices`）

## 反模式提醒

- **REA 不自带分析引擎**：仅装 REA、未装 Ghidra/IDA/Hopper/JADX 等，native/Android 域将不可用（F-030~F-036）——务必按目标域对号安装。
- **版本要对**：固件需要 Binwalk 3.1.x / Unblob 26.6.x 的验证口径（F-049）。
- **网站分析是被动附着**：CDP 附加到 user-owned 浏览器（F-051），不是通用自动化——预期要你有浏览器/CDP 端点。

## 阅读下一步

- [CLI 与 MCP 使用示例](cli-and-mcp-usage.md)——工具链就绪后跑 `rea analyze <path>`
- [支持的分析目标域与工具矩阵](../concepts/04-analysis-domains.md)——各域边界与工具要求
