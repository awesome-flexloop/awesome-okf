---
type: reference
scope: deepseek-reasonix
name: source
title: DeepSeek-Reasonix 源码信源索引
description: 按包索引的关键源码文件清单，关联事实编号 F-xxx，供概念文档溯源引用
tags: [deepseek-reasonix, source, reference]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-23T00:00:00Z
verified:
  by: process:seven-concepts-v
  at: 2026-08-23T00:00:00Z
status: stable
stale_after: 2027-08-23
sources:
  - id: SRC-001
    resource: /spec/facts.md
    title: DeepSeek-Reasonix 事实清单
---

# DeepSeek-Reasonix 源码信源索引

本文件按包索引关键源码文件，每个文件标注其覆盖的事实编号。所有路径相对于项目根目录 `d:\spaces\SpecWeave\external\libs\ai\agents\DeepSeek-Reasonix\`。

## 项目根目录

| 文件 | 说明 | 事实编号 |
|------|------|---------|
| `go.mod` | Go module 定义，依赖清单 | F-001, F-002 |
| `README.md` | 项目说明、安装、特性 | F-006, F-007 |
| `REASONIX.md` | 项目常驻指令、分层规则、约定 | F-008, F-009 |
| `CLAUDE.md` | Claude Code 指令，引用 REASONIX.md | F-010 |
| `Makefile` | 构建、交叉编译、lint、test 目标 | F-003, F-004, F-005 |

## cmd 入口

| 文件 | 说明 | 事实编号 |
|------|------|---------|
| `cmd/reasonix/main.go` | CLI 主入口，blank import 注册 provider/builtin | F-011, F-012, F-013 |

## internal/agent — Agent 核心

| 文件 | 说明 | 事实编号 |
|------|------|---------|
| `internal/agent/agent.go` | Agent 结构体、New 构造、Run 入口、Gate/Renderer/Asker 接口、Steer 机制、Options | F-014, F-015, F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-023, F-024, F-106, F-107 |
| `internal/agent/run_loop.go` | 运行循环、streamWithSamplingRecovery、beginRunTurn、handleFinalResponse、handleToolRound、deferredStreamSink | F-028, F-029, F-030, F-031, F-032, F-033, F-034 |
| `internal/agent/session.go` | Session 消息历史、Add/Rewrite/Snapshot、并发保护、持久化版本 | F-025, F-026, F-027 |
| `internal/agent/arbiter.go` | verdict 四级阶梯、intervention、applyInterventions | F-036, F-037 |
| `internal/agent/governor.go` | reasoning governor A/B 实验、触发/退出条件、effort 降级 | F-038, F-039, F-040, F-041 |
| `internal/agent/turn_phase.go` | emitTurnPhase、emitCompletionSummary | F-035 |
| `internal/agent/scheduler.go` | SubagentScheduler 并发控制、AcquireRequest、写路径声明 | F-042, F-043 |
| `internal/agent/fleet.go` | FleetTool 2-64 并行任务、depends_on DAG、write_paths | F-044, F-045 |
| `internal/agent/task.go` | subagent system prompt、递归/隐藏工具列表、session temp | F-046, F-047, F-048, F-049 |
| `internal/agent/compact.go` | 自动压缩、compactRatio、summary tag、7 章节摘要 | F-050, F-051, F-052 |
| `internal/agent/fork.go` | ForkBundle 策略实验冻结、forkBundleVersion | F-053, F-054 |
| `internal/agent/branch.go` | BranchMeta 会话分支 sidecar | F-055 |
| `internal/agent/services.go` | agentServices 协作者分离 | F-105 |

## internal/acp — ACP 协议

| 文件 | 说明 | 事实编号 |
|------|------|---------|
| `internal/acp/protocol.go` | ACP v1 线协议类型、InitializeParams/Result、AgentCapabilities、JSON-RPC 错误码 | F-056, F-057, F-058, F-059, F-060 |
| `internal/acp/server.go` | Conn NDJSON JSON-RPC 连接、handler 注册、Serve 读取循环 | F-061, F-062 |
| `internal/acp/service.go` | Factory 接口、SessionParams、Serve 注册全部 handler | F-063, F-064 |
| `internal/acp/dispatch.go` | updateSink 事件映射、tool call 两态、maxResultChars | F-065, F-066 |
| `internal/acp/inbox.go` | session inbox enqueue/list/get、steer/followup 意图 | F-067 |
| `internal/acp/clientio.go` | 客户端 FS/Terminal 能力桥接 | — |

## internal/bot — Bot 网关

| 文件 | 说明 | 事实编号 |
|------|------|---------|
| `internal/bot/types.go` | Platform/ChatType 常量、InboundMessage/OutboundMessage | F-068, F-069, F-070 |
| `internal/bot/gateway.go` | GatewayConfig、ChannelConfig、RouteConfig、AllowlistConfig | F-071 |
| `internal/bot/session.go` | 队列模式常量、BuildSessionKey、QueueOptions | F-072, F-073 |
| `internal/bot/connloop.go` | RunWithRetry 指数退避重连、SleepCtx | F-074, F-075 |
| `internal/bot/render.go` | renderSink、messageEditor 接口、流式渲染常量 | F-079, F-080 |
| `internal/bot/qq/adapter.go` | QQ Bot API v2 WebSocket 适配器 | F-076 |
| `internal/bot/feishu/retry.go` | 飞书传输级重试、幂等 key | F-077, F-078 |

## internal/checkpoint — 检查点与恢复

| 文件 | 说明 | 事实编号 |
|------|------|---------|
| `internal/checkpoint/types.go` | Schema 版本、Coverage、FileRevision、RewindScope/Plan/Result、TransactionManifest/State、BlobStore 常量 | F-081, F-082, F-083, F-084, F-085, F-087 |
| `internal/checkpoint/blob.go` | BlobStore 内容寻址存储、SHA-256 Put/Get | F-086 |
| `internal/checkpoint/load.go` | checkpoint 加载、v1 legacy 标记、按 turn 选择 | F-088 |

## internal/boot — 启动组装

| 文件 | 说明 | 事实编号 |
|------|------|---------|
| `internal/boot/boot.go` | 包注释、Options、ErrUnknownModel、agentKeepPolicy | F-089, F-090, F-094 |
| `internal/boot/runtime.go` | BuildResult、BuildRuntime、runtimeGeneration | F-091, F-092 |
| `internal/boot/resolver.go` | LocalProviderResolver、Catalog/Resolve | F-093 |

## internal/cli — 命令行

| 文件 | 说明 | 事实编号 |
|------|------|---------|
| `internal/cli/cli.go` | RunWithBuildInfo 入口、子命令路由、交互检测 | F-095, F-096 |
| `internal/cli/mcp.go` | parseMCPAdd、MCP 服务器管理语法 | F-097 |
| `internal/cli/provider.go` | /provider 命令、provider picker | F-098 |
| `internal/cli/model.go` | /model 命令、异步切换、历史携带 | F-099 |
| `internal/cli/subagent.go` | subagent 子命令 list/create/edit/delete/try/run | F-100 |
| `internal/cli/plugin.go` | plugin 子命令 install/list/show/remove/enable/disable/doctor/migrate | F-101 |

## desktop — Wails 桌面应用

| 文件 | 说明 | 事实编号 |
|------|------|---------|
| `desktop/app.go` | Wails 应用、eventChannel、singleInstanceID、核心包导入 | F-102, F-103, F-104 |
| `desktop/main.go` | Wails 应用启动入口 | — |

## docs — 文档

| 文件 | 说明 |
|------|------|
| `docs/ACP.md` | ACP 编辑器集成文档 |
| `docs/CLI.md` | CLI 参考 |
| `docs/GUIDE.md` | 使用指南 |
| `docs/CHECKPOINTS.md` | 检查点文档 |
| `docs/SPEC.md` | 技术规范 |
| `docs/EXTENSIONS.md` | 扩展开发 |
| `docs/SUBAGENT_PROFILES.md` | 子代理配置 |
| `docs/TOOL_APPROVAL_MODES.md` | 工具审批模式 |
