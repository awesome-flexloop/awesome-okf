---
okf_version: "0.2"
type: category
title: "REA 概念教程"
description: "REA（Reverse Engineer Anything）从『是什么』到『怎么工作』再到『能分析什么 / 怎么用』——产品身份与定位、MCP 契约层单一事实源、Provider 适配器、目标域与工具矩阵、CLI/MCP 双入口、领域类型与证据模型"
---

# REA 概念教程

按从「是什么」到「怎么工作」再到「能分析什么 / 怎么用」的路径组织（依据 insights.md 知识地图的 6 个规划文档）：

| 文档 | 内容 |
|------|------|
| [01 · REA 是什么：产品身份与定位](01-rea-overview.md) | 是什么、npm 包身份、MIT 许可、MCP 服务名、官方定位语、目标域概览 |
| [02 · MCP 契约层：单一事实源与工具全集](02-mcp-contract.md) | `TOOL_CONTRACTS` 聚合、统一 `ToolContract` 类型、15 种 kind、38 官方代理工具、命令别名映射 |
| [03 · Provider 适配器：如何接入分析工具](03-provider-adapters.md) | 为什么 REA 不自己反编译、`AnalysisProviderCandidate` 接口、11 类 Provider、桥接脚本 |
| [04 · 支持的分析目标域与工具矩阵](04-analysis-domains.md) | native/EVM/WASM/Android/.NET/固件/网站/进程 八大域的边界与工具要求 |
| [05 · 安装、setup 与 CLI/MCP 双入口](05-cli-and-setup.md) | `npx rea-agents setup`、双层路由、129 顶层命令、命令↔工具映射、双端同源 |
| [06 · 领域类型与证据模型](06-domain-types-and-evidence.md) | `AnalysisSnapshot`、`Evidence<Result>` 泛型、各域领域类型、纯副作用无关设计 |

```{toctree}
:maxdepth: 2
:hidden:

01-rea-overview
02-mcp-contract
03-provider-adapters
04-analysis-domains
05-cli-and-setup
06-domain-types-and-evidence
```