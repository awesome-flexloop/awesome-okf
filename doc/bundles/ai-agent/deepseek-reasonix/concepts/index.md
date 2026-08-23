# 概念文档

## 入门

- [00 - Reasonix 简介](/concepts/00-introduction.md)——DeepSeek 开源 Go AI Agent，四种接入方式
- [01 - 项目架构](/concepts/01-project-architecture.md)——包分层、cmd 入口、boot 启动流程

## 核心

- [02 - Agent 运行循环](/concepts/02-agent-run-loop.md)——agent.go 核心、run_loop、arbiter、governor、compaction
- [03 - ACP 协议](/concepts/03-acp-protocol.md)——NDJSON JSON-RPC、能力协商、Factory、inbox 队列
- [04 - Bot 网关](/concepts/04-bot-gateway.md)——QQ/飞书适配器、会话隔离、消息渲染、重连

## 高级

- [05 - CLI 与 TUI](/concepts/05-cli-tui.md)——命令系统、Bubble Tea TUI、MCP/插件管理
- [06 - Checkpoint 与恢复](/concepts/06-checkpoint-recovery.md)——blob 存储、事务回滚、fork/branch
- [07 - Fleet 与 Subagent](/concepts/07-fleet-subagents.md)——并行调度、写路径声明、DAG 依赖
