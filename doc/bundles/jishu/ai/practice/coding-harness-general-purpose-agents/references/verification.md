---
type: Reference
title: "Coding Harness for General-Purpose Agents 核验报告"
description: "核验 Radar 发布信息、四家 harness 编程入口、运行时能力、护栏差异与相关 blip，并记录口径勘误与单源边界。"
tags: [thoughtworks, verification, coding-harness, sandboxing, approval, agent-runtime]
generated: { by: "lobsterai/main", at: "2026-11-10T15:05:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T15:05:00+08:00" }
status: stable
stale_after: "2027-04-30"
sources:
  - id: radar
    resource: https://www.thoughtworks.com/radar/techniques/coding-harness-for-general-purpose-agents
  - id: radar-index
    resource: https://www.thoughtworks.com/radar
  - id: claude-sdk
    resource: https://code.claude.com/docs/en/agent-sdk/overview
  - id: claude-hosting
    resource: https://code.claude.com/docs/en/agent-sdk/hosting
  - id: codex-sdk
    resource: https://github.com/openai/codex/blob/main/sdk/typescript/README.md
  - id: codex-app-server
    resource: https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md
  - id: opencode-sdk
    resource: https://opencode.ai/docs/sdk/
  - id: opencode-server
    resource: https://opencode.ai/docs/server/
  - id: opencode-permissions
    resource: https://opencode.ai/docs/permissions/
  - id: pi-sdk
    resource: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md
  - id: pi-cli
    resource: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/cli-integration.md
  - id: pi-readme
    resource: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/README.md
---

# Coding Harness for General-Purpose Agents 核验报告

## 核验结论

| 核验项 | 结果 | 事实编号 |
|---|---|---|
| 发布日、卷号与评级 | ? Radar 页面标注 Published Nov 04, 2026、Nov 2026、Trial；首页标注 Vol 35 / November 2026 | F-002～F-004 |
| 四个编程入口存在且可访问 | ? Claude Agent SDK、Codex SDK、OpenCode SDK、Pi SDK/RPC 官方文档均可访问 | F-007～F-010 |
| Claude Agent SDK 复用 Claude Code 运行时 | ? 官方 overview 明确“same tools, agent loop, and context management” | F-037、F-038 |
| Codex SDK 与 app-server 是两条不同入口 | ? SDK 包装 CLI、走 stdio JSONL；app-server 走 JSON-RPC | F-039、F-040 |
| OpenCode server 与 SDK 的关系 | ? `opencode serve` 暴露 OpenAPI 3.1，SDK 由规范生成 | F-041 |
| Pi SDK 与 RPC 模式 | ? SDK 为进程内嵌入；RPC 为长驻进程 + JSONL 双向控制 | F-042、F-043 |
| 长任务上下文压缩 | ?? Claude 与 Pi 文档明确 compaction/上下文管理；Codex、OpenCode 未逐项核对 | F-011 |
| 会话持久化 | ? 四家均有 session/thread 持久化或恢复机制 | F-012、F-038～F-042 |
| 无头运行 | ? Claude `-p`、Codex SDK、OpenCode server、Pi print/JSON/RPC 均支持 | F-013、F-039～F-042 |
| 复用 skills / subagents / instructions | ? Claude SDK 明确列出；Pi 明确 skills；Codex/OpenCode 有对应机制 | F-013、F-038、F-043 |
| Codex 与 Claude 的沙箱、审批 | ? 两家文档均有 sandbox 与 approval/permission 配置；分层口径见 E-1 | F-017、F-045、F-046 |
| Pi 把护栏留给扩展 | ? 官方定位为 minimal、extensible，默认跳过部分功能；“刻意”为作者措辞，见 E-2 | F-018、F-043 |
| 不同 harness 能力不同 | ? 四家能力表与扩展模型差异明显 | F-016 |
| .NET 迁移内部加速器 | ?? Thoughtworks 自述案例，无公开代码、指标或客户证据 | F-015 |
| token 成本与内置提示开销 | ?? 作者经验判断，无量化数据 | F-022～F-025 |
| 相关 blip 评级 | ? Agent sandboxing=Adopt、Managed agents runtime=Trial、Enterprise harness=Assess、Harness quality evaluation=Assess、Agent plugin marketplace=Trial | F-027～F-031 |
| Enterprise harness 定义 | ? Radar 原文给出组织级资产层定义 | F-032 |
| Harness quality evaluation 方法 | ? Radar 原文点名 PluginEval 与 redproof；两个工具仓库未逐一验证 | F-033 |
| Agent sandboxing 建议 | ? Radar 原文建议默认沙箱、风险分级与最小权限 | F-034 |
| Managed agents runtime 定义 | ? Radar 原文给出平台托管范围 | F-035 |
| Agent Skills 定义与评级 | ? 2026-04-15 发布、Trial、当前期不在榜 | F-026、F-036 |
| Radar 一年两次 | ? Radar 首页原文 “twice-yearly snapshot” | F-047 |

## 勘误与口径

### E-1 “Claude Agent SDK 提供沙箱”是分层表述

博文把 Codex 与 Claude Agent SDK 并列，称两者都提供 sandboxing 与 approval policies。官方文档的拆分更细：Agent SDK overview 把 permissions 列为 SDK 能力（哪些工具自动运行、哪些需要审批）；sandbox 更多出现在托管与运行时层（每个会话启动 `claude` CLI 子进程、容器化沙箱、`sandboxNetworkConfig` 等）。

处理：正文保留博文结论，但把“审批策略”归到 SDK 能力层，把“沙箱”归到运行时/托管层，避免读者误以为沙箱是 SDK 的一个开关。该差异是口径细化，不是源文硬错误。

### E-2 Pi “刻意”是作者概括

博文称 Pi “deliberately leaves guardrails to extensions”。Pi 官方 README 的原文是 “minimal, extensible agent harness”，并说明默认跳过 sub-agents 与 plan mode，鼓励用扩展、技能、提示模板与主题定制。官方没有逐字说“刻意放弃护栏”。

处理：正文保留“Pi 把护栏留给扩展”的结论，同时标注“刻意”为作者措辞；官方可核验的是“最小、可扩展、默认功能克制”。

### E-3 Codex 的 SDK 与 app-server 不是同一层

博文用 “Codex SDK and app-server” 并列。官方仓库显示：TypeScript SDK 包装 `codex` CLI，通过 stdin/stdout 交换 JSONL 事件；app-server 是 JSON-RPC 服务端，暴露线程、审批、记忆等接口。

处理：正文分栏呈现两条入口，避免把“SDK”与“app-server”当成同一个包的两个名字。

### E-4 OpenCode 文档存在 V1/V2 版本分界

核验时 `opencode.ai/docs/sdk/` 与 `/docs/server/` 会重定向到 `/v1/docs/...`，页面顶部提示 V1 文档，并给出 V2 文档入口。博文未标注版本。

处理：正文以“核验时的 V1 文档”标注 SDK/server 细节；提醒读者以当前版本文档为准，SDK 形态可能随 V2 变化。

## 单源与边界

- 本文是 Thoughtworks 的观点型技术雷达条目，不是独立 benchmark，也不是四家 harness 的对照实测。
- `.NET 应用迁移内部加速器` 只有 Thoughtworks 自述，无公开证据；正文按“厂商自述案例”标注，不当作可复现结论。
- token 成本、内置提示开销、编码偏向均为作者经验判断，正文标注“作者观点”，不写成量化事实。
- 四家 SDK 的能力、包名、传输方式与版本会快速变化；本包以 2026-11-10 可访问的官方文档为准，`stale_after` 设为 2027-04-30。
- Radar 相关 blip 的评级与定义以 2026 年 11 月页面为准；下一期雷达可能调整。
