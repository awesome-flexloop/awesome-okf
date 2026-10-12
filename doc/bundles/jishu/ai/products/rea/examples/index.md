---
okf_version: "0.2"
type: category
title: "REA 实操示例"
description: "REA 可照做的上手与接入流程 —— CLI 与 MCP 使用示例（setup、analyze、接入 agent 的 MCP 配置要点）、分析工具安装与 Provider 接入（Ghidra/IDA/Hopper/JADX/ADB/EVM/WASM/固件 doctor 校验）、JavaScript 应用重建、平台深层分析、重建工程工作流"
---

# REA 实操示例

> **可复现性说明**：本章示例的输入（命令）、过程（步骤）明确，理论上可由独立执行者复现。**未在本机实际运行**，命令来自源码/官方文档核对（references/facts.md）；执行时以官方文档/`rea doctor`/`rea setup --help` 当前输出为准。

| 示例 | 内容 |
|------|------|
| [CLI 与 MCP 使用示例](cli-and-mcp-usage.md) | `npx rea-agents setup`、`rea analyze <path>`、`rea doctor` 等单次命令 + 接入 agent 客户端的 MCP 配置要点 |
| [分析工具安装与 Provider 接入](provider-setup.md) | Ghidra/IDA/Hopper/JADX/ADB/EVM/WASM/固件工具链本地准备与 doctor 校验 |
| [JavaScript 应用重建示例](js-reconstruction-example.md) | `analyze_javascript_application` + 应用图 + 运行时观测/协同 + Web 源定位的实际走查（F-067~F-077） |
| [平台深层分析示例](platform-deep-example.md) | Apple/Electron/HarmonyOS/Android/固件 代表性 CLI 命令、环境变量与资源限制（F-103~F-118） |
| [重建工程工作流示例](reconstruction-workflow-example.md) | 按 9 阶段走 `evidence_bundle` + 义务台账 + `closure_digest` 的完整流程（F-129~F-131） |

```{toctree}
:maxdepth: 2
:hidden:

cli-and-mcp-usage
provider-setup
js-reconstruction-example
platform-deep-example
reconstruction-workflow-example
```