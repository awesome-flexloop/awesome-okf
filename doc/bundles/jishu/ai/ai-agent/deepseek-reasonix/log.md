---
type: Changelog
scope: deepseek-reasonix
name: log
version: "0.1.0"
description: DeepSeek-Reasonix OKF Wiki bundle 变更日志
tags: [deepseek-reasonix, changelog]
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-23T00:00:00Z
status: stable
stale_after: 2027-08-23
---

# 变更日志

## 0.1.0 — 2026-08-23

### 新增

初始版本，基于 DeepSeek-Reasonix 源码（main-v2 分支）生成 OKF v0.2 Wiki bundle。

**R 阶段（事实采集）**：
- 读取关键文件 40+：go.mod、README、REASONIX.md、Makefile、cmd/reasonix/main.go
- 核心包：internal/agent（agent.go、run_loop.go、session.go、arbiter.go、governor.go、scheduler.go、fleet.go、task.go、compact.go、fork.go、branch.go、services.go、turn_phase.go）
- ACP 包：protocol.go、server.go、service.go、dispatch.go、inbox.go
- Bot 包：gateway.go、session.go、connloop.go、types.go、render.go、qq/adapter.go、feishu/retry.go
- CLI 包：cli.go、mcp.go、provider.go、model.go、subagent.go、plugin.go
- Checkpoint 包：types.go、load.go、blob.go
- Boot 包：boot.go、runtime.go、resolver.go
- Desktop：app.go（Wails 概览）
- 文档：docs/ACP.md 等
- 产出 107 条编号事实（F-001 至 F-107），每条标注源码路径与行号

**I 阶段（架构洞察）**：
- 5 个核心洞察：ACP 适配层设计、运行循环双层容错、Bot 三层解耦、Checkpoint 事务回滚、Fleet 写路径安全
- 每个洞察含陈述/证据/反常识/行动四元组

**E 阶段（文档生成）**：
- references/source.md：按包索引的信源登记
- 8 个概念文档：00-introduction 至 07-fleet-subagents
- 2 个示例文档：01-basic-usage、02-bot-gateway
- 根 index.md（type: bundle, okf_version: 0.2）+ 子目录索引
- 所有交叉链接使用 `/` 开头 bundle-relative 路径
- 中文内容，Go 代码片段来自实际源码

### 覆盖范围

- 项目结构与构建系统
- Agent 核心运行循环（采样恢复、仲裁、governor、compaction、steer）
- ACP v1 协议（JSON-RPC、能力协商、Factory、inbox 队列）
- Bot 多平台网关（QQ/飞书/微信/钉钉、会话隔离、消息渲染、重连）
- CLI/TUI（子命令、MCP 管理、provider/model 切换、插件系统）
- Checkpoint 系统（schema 版本、blob 存储、事务回滚、fork/branch）
- Fleet/Subagent（并发调度、写路径声明、DAG 依赖、profile 管理）
- Boot 启动组装（配置→Controller、provider 解析、extension 快照）
- Desktop（Wails v2 概览）
