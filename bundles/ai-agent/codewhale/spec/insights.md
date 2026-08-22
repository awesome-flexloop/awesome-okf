---
type: spec
title: CodeWhale 架构洞察
description: 从 CodeWhale 源码中提炼的核心设计决策、机制与反直觉约束
tags: [codewhale, rust, agent, insight]
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# CodeWhale 深度洞察

## 1. `Op`-in / `EventMsg`-out：一种格式统一所有客户端

**陈述**：CodeWhale 的核心引擎向所有消费者（TUI、CLI exec、app-server、测试）暴露同一条 `OpEnvelope` 进 / `EventMsg` 出的通道契约，使有头与无头两种运行方式共享同一套状态机代码路径。

**证据**：[F-014] 定义 `EngineHandle` 持有 `tx_op` / `rx_event`；[F-044][F-045] 定义可序列化的 `OpEnvelope` 与 `Op` 枚举；[F-046] 定义 `EventMsg` 输出枚举；[F-019][F-020] 显示 `spawn_engine` 与 `spawn_headless_thread` 都回到同一个 `EngineHandle`。

**反常识**：传统上「交互式 TUI」与「无头 CLI」通常是两套独立的调度逻辑，各自维护自己的消息循环。CodeWhale 却把引擎做成「TUI 无关」的 mailbox（`core/src/engine/mod.rs` 明确声明 engine 是 terminal-free 的），把 TUI 降级为这个 mailbox 的一个消费者。这意味着「无头会话」不是降级特性，而是首类（first-class）路径。

**行动**：学习一个 Agent 框架时，先找它的「通道契约」而非 UI 入口。若你能画出一张 `Op → Engine → EventMsg` 的时序图，就抓住了这类架构的骨架。

## 2. 三层边界是逐步落地的「迁移前沿」，而非一次性重构

**陈述**：`crates/core`、`crates/protocol`、`crates/tools` 等 crate 是正在从巨型 `tui` crate 中「搬家」出去的边界产物，注释里保留了明确的分期规划（issue #5261/#5262）与「哪些已搬、哪些未搬」的状态声明。

**证据**：[F-007] 显示 `core` 只声明了 7 个子模块；[F-012] 的引擎注释声明「此模块刻意很小，先形式化 ThreadId/SessionId 与 Op-in/EventMsg-out 边界」；[F-021][F-024] 注释写明 `Thread`/`Session` split 跟随 #5261、journal 树操作跟随 #5262；[F-086] 表明真正的大 `EngineConfig`（含 `allow_shell`、`trust_mode`、`mcp_config_path`）仍在 `tui` crate 中。

**反常识**：初次阅读会以为 `crates/core` 的 `Engine` 就是整个运行时，但注释明确指出真实的 turn loop 仍在 `crates/tui` 里，`core` 目前只承担「无 TUI 也能启动会话」的最小证明。所谓「核心 crate」在早期并非拥有核心逻辑的地方。

**行动**：读一个进行中的大型重构代码库时，不要用目录名推断职责；要读模块头部的 doc comment——它们常常是「迁移地图」，比类型签名更能说明「谁才是当前真正的 owner」。

## 3. 工具系统的分级裁判：校验、资源调度、终态三者分离

**陈述**：CodeWhale 把「一次工具调用」的生命周期拆成三个独立的类型层：`ToolCall`（未校验的原始请求）→ `PreparedToolCall`（校验与资源声明）→ `ToolExecutionOutcome`（机器可读的终态），每一层只处理一个关注点。

**证据**：[F-056] 定义原始 `ToolCall`；[F-061] 定义 `PreparedToolCall` 携带 `read_only`/`approval`/`resources: Vec<ResourceClaim>`；[F-062] 定义七种 `ResourceClaim` 及其 `conflicts_with`；[F-063] `schedule_non_conflicting` 用资源声明做并行分批；[F-064][F-065] 定义 `ToolTerminalStatus` 与 `ToolExecutionOutcome`。

**反常识**：多数工具系统只关心「成功/失败」二元结果。CodeWhale 额外把「取消」「超时」「拒绝」「参数非法」做成一等终态（`ToolTerminalStatus` 六变体），并在注释里说明这是为了「转录仍能闭合、运行时不能把取消误报为失败」。终态语义与用户可见结果（`ToolResult::success`）被刻意分开。

**行动**：设计自己的工具/函数调用层时，把「校验」「并发调度」「终态建模」分成独立类型；尤其是「取消」与「超时」应作为显式终态，而不是塞进一个 `Failed` 字符串里。

## 4. MCP 的「管理」与「传输」被 trait 隔离，无头服务器是一个纯函数协议循环

**陈述**：`McpManager` 只负责 name→config/client 的登记与限定名（`mcp__server__tool`）去重，真正的通信由 `McpManagedClient` trait 抽象，且提供了一个从 stdin 逐行读 JSON-RPC 的 `run_stdio_server` 纯函数入口。

**证据**：[F-070] 定义 `McpManagedClient` trait 的四个方法；[F-071] 定义 `McpManager` 只持有 `configs` 与 `clients` 两个 HashMap；[F-066] 公开 `ChildProcessMcpClient`；[F-072] 定义 `run_stdio_server(initial_definitions) -> Result<Vec<McpServerDefinition>>`。

**反常识**：MCP 常被想象成一个庞大的远程调用栈，但 CodeWhale 的 MCP crate 核心是「把每个服务器当成一个可替换的 `Box<dyn McpManagedClient>`」；测试内存客户端（`InMemoryMcpClient`）之所以存在，注释里写的是「曾在 mcp-server 路径里塞假数据会让坏集成看起来和好的一样（#4727）」。抽象的作用首先是为测试保真，其次才是多传输支持。

**行动**：为外部协议写集成层时，先定义最小 trait（list/call/read），把具体传输（stdio/http）放到 trait 实现之后；用一个内存实现锁死测试，避免「假成功」污染看似正常的集成。

## 5. Workflow/Fleet 是「声明式 IR + 命令式 JS VM」的双轨，且容量被常量硬编码封顶

**陈述**：Workflow 被拆成两个 crate：`workflow` 承载静态的声明式 IR（gates、fleet、replay、红线），`workflow-js` 承载沙箱化的 QuickJS（rquickjs）命令式运行时，脚本通过 `task()`/`parallel()`/`pipeline()` 派发子代理，容量上限以常量形式写死。

**证据**：[F-073] 列出 `workflow` 的 16 个子模块（含 `gates`、`fleet_snapshot`、`replay`、`review_repair`）；[F-074] `gates` 公开 `GateKind`/`GateOutcome`/`stopship_gate_pipeline`；[F-075] `DEFAULT_FLEET_WORKFLOW_MAX_AGENTS = 1000`、`MAX_DEPTH = 5`；[F-077][F-078] `workflow-js` 只有 5 个模块且 `WORKFLOW_LIFETIME_CAP = 1000`、`WORKFLOW_MAX_CONCURRENT = 16`。

**反常识**：一个「Agent 编排」能力被同时实现为两套看起来重叠的机制（静态 IR 与 JS VM），但注释明确画了边界——静态 IR 负责 record/replay 与 model policy，JS VM 只经 `WorkflowDriver` 与外界交谈、且 `Date.now()`/`Math.random()` 直接抛错以保证可重放。这不是功能重复，而是「确定性（可回放）与命令式表达力」的刻意分工。

**行动**：在 Agent 编排里区分「要重放/审计的」与「要表达自由的」两层。凡是会被回放、比对、审计的路径，就要像这里一样把时间与随机数的入口全部掐死。