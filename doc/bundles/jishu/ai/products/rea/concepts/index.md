---
okf_version: "0.2"
type: category
title: "REA 概念教程"
description: "REA（Reverse Engineer Anything）从『是什么』到『怎么工作』再到『能分析什么 / 怎么用』——产品身份与定位、MCP 契约层单一事实源、Provider 适配器、目标域与工具矩阵、CLI/MCP 双入口、领域类型与证据模型，以及 docs/ 全量深层的 JS/Web、专项 Ghidra、平台深层与工程重建工作流"
---

# REA 概念教程

按从「是什么」到「怎么工作」再到「能分析什么 / 怎么用」的路径组织（依据 insights.md 知识地图的 10 个规划文档，01~06 为基础，07~10 为 docs/ 全量深层扩展）：

| 文档 | 内容 |
|------|------|
| [01 · REA 是什么：产品身份与定位](01-rea-overview.md) | 是什么、npm 包身份、MIT 许可、MCP 服务名、官方定位语、目标域概览 |
| [02 · MCP 契约层：单一事实源与工具全集](02-mcp-contract.md) | `TOOL_CONTRACTS` 聚合、统一 `ToolContract` 类型、15 种 kind、38 官方代理工具、命令别名映射 |
| [03 · Provider 适配器：如何接入分析工具](03-provider-adapters.md) | 为什么 REA 不自己反编译、`AnalysisProviderCandidate` 接口、11 类 Provider、桥接脚本 |
| [04 · 支持的分析目标域与工具矩阵](04-analysis-domains.md) | native/EVM/WASM/Android/.NET/固件/网站/进程 八大域的边界与工具要求 |
| [05 · 安装、setup 与 CLI/MCP 双入口](05-cli-and-setup.md) | `npx rea-agents setup`、双层路由、129 顶层命令、命令↔工具映射、双端同源 |
| [06 · 领域类型与证据模型](06-domain-types-and-evidence.md) | `AnalysisSnapshot`、`Evidence<Result>` 泛型、各域领域类型、纯副作用无关设计 |
| [07 · JavaScript 应用图与 Web/浏览器域](07-js-web-domains.md) | 应用图 schema/12 关系词汇、6 工作流工具、工件重建、Wakaru 恢复、运行时协同、Web 源定位/模块追踪/浏览器场景 |
| [08 · Native 与专项 Ghidra 深度适配](08-native-ghidra-specialty.md) | Native 调查、二进制诊断、raw-binary 映射、DOS/MIPS/PSP/NativeAOT/Windows P0 专项 Ghidra、IDA/JEB/Apktool |
| [09 · 平台分析域深层](09-platform-domains-deep.md) | Android/JADX、ADB、.NET Managed、固件、Apple、Electron、HarmonyOS 的精确版本与环境变量/资源限制 |
| [10 · 工程与管理/重建工作流](10-engineering-workflow.md) | 重建就绪 9 阶段、义务台账、MCP 输入 schema profile、测试/CI/发布、6.2 迁移 |

```{toctree}
:maxdepth: 2
:hidden:

01-rea-overview
02-mcp-contract
03-provider-adapters
04-analysis-domains
05-cli-and-setup
06-domain-types-and-evidence
07-js-web-domains
08-native-ghidra-specialty
09-platform-domains-deep
10-engineering-workflow
```