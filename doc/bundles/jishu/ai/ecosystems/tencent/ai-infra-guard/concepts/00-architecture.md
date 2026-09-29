---
type: Concept
title: 分布式 Server-Agent 架构总览
description: AI-Infra-Guard 采用 Go 编写的 Server 调度层与多语言 Agent 执行层分离的分布式架构，通过 WebSocket 双向通信和 SSE 前端推送实现任务编排。
tags: [ai-infra-guard, architecture, distributed, websocket, server, agent]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: go-server
    resource: /references/go-server.md
    title: Go WebSocket 与 HTTP Server 信源
  - id: scan-engine
    resource: /references/scan-engine.md
    title: 扫描引擎与指纹 DSL 信源
---

## 架构分层

AI-Infra-Guard（A.I.G）由三个独立部署的组件构成：

```
┌─────────────┐     REST/SSE      ┌──────────────────┐     WebSocket     ┌──────────────┐
│  Frontend   │ ◄──────────────► │      Server      │ ◄──────────────► │    Agent     │
│  (React SPA)│   /api/v1/app/*  │  (Go + Gin)      │  /api/v1/agents/ws │  (Go binary) │
└─────────────┘                  └──────────────────┘                   └──────────────┘
                                         │                                      │
                                         │ SQL                                  │ uv run
                                         ▼                                      ▼
                                  ┌──────────────┐                       ┌──────────────┐
                                  │  Database    │                       │ Python 子进程 │
                                  │  (SQLite)    │                       │ mcp-scan 等   │
                                  └──────────────┘                       └──────────────┘
```

### Server 层

Server 是系统的调度核心，由 `common/websocket/RunWebServer` 启动（[go-server.md](../references/go-server.md)）。它承担以下职责：

- **REST API**：基于 Gin 框架，提供任务 CRUD、模型管理、知识库管理等接口
- **WebSocket 接入**：在 `/api/v1/agents/ws` 路径接受 Agent 注册和事件上报
- **SSE 推送**：在 `/api/v1/app/tasks/sse/:sessionId` 向前端实时推送任务进度
- **任务调度**：`TaskManager` 使用 round-robin 策略将任务分发给可用 Agent
- **数据持久化**：通过 GORM 将任务、事件、模型配置存入 SQLite
- **文件管理**：支持完整上传和分片上传，含路径穿越防护

### Agent 层

Agent 是独立的 Go 二进制（`cmd/agent/main.go`），启动后连接 Server 并注册自身能力。每个 Agent 可以注册多种任务处理器（`TaskInterface`），当前包括：

- `AIInfraScanAgent` — 纯 Go 基础设施扫描
- `McpTask` — MCP 安全扫描（调用 Python mcp-scan）
- `ModelRedteamReport` — 大模型安全体检（调用 Python AIG-PromptSecurity）
- `AgentTask` — Agent 安全评估（调用 Python agent-scan）
- `SkillTask` — Skill 代码审计（调用 Python skill-scan）

Agent 不是被动执行器——它自己维护任务计划（SubTask 列表）、工具状态（Tool doing/done）和动作日志，Server 只做路由和存储。

### Frontend 层

前端是 React + TypeScript SPA，嵌入在 Server 二进制中（通过 `//go:embed static/*`）。它通过 REST API 创建任务，通过 SSE 接收实时进度，通过 WebSocket 间接获取 Agent 状态。

## 核心通信流

### 任务创建到执行的完整链路

1. 前端 `POST /api/v1/app/tasks` 提交 `TaskCreateRequest`
2. Server 预存任务到数据库（状态 doing），等待 SSE 连接建立
3. `TaskManager.dispatchTask` 从 `GetAvailableAgents()` 中 round-robin 选择一个 Agent
4. Server 通过 WebSocket 发送 `task_assign` 消息，内容为 `TaskContent`
5. Agent 的 `processMessage` 匹配 `ServerMsgTypeTaskAssign`，查找注册的 `TaskInterface`
6. Agent 在 goroutine 中异步执行 `Execute(ctx, request, callbacks)`
7. 执行过程中，Agent 通过 callbacks 发送 8 种事件类型：
   - `planUpdate` — 更新整体计划
   - `newPlanStep` — 新建执行步骤
   - `statusUpdate` — 更新步骤状态
   - `toolUsed` — 工具使用状态
   - `actionLog` — 工具日志输出
   - `resultUpdate` — 最终结果
   - `error` — 错误
   - `liveStatus` — 存活状态
8. Server 的 `HandleAgentEvent` 将事件存入数据库并通过 SSE 推送给前端
9. 收到 `resultUpdate` 后，Server 更新任务状态为 done，异步清理资源

### 多 Agent 负载均衡

`TaskManager` 维护原子计数器 `dispatchCounter`：

```go
idxDisp := atomic.AddUint64(&tm.dispatchCounter, 1) - 1
selectedAgent := availableAgents[idxDisp%uint64(len(availableAgents))]
```

每次分发任务时计数器递增，对可用 Agent 数量取模，实现均匀分配。Agent 注册时上报 `Capabilities` 列表，Server 可据此过滤（当前实现为全部可用 Agent 轮询）。

## 心跳与连接管理

AgentConnection 维护 WebSocket 连接的健康状态：

- `pongWait = 120s` — 读超时
- `pingPeriod = 96s`（pongWait 的 80%）— 心跳发送间隔
- `writeWait = 60s` — 写超时

`writePump` goroutine 定期发送 PingMessage，失败时重试一次，仍失败则标记连接非活跃。Agent 断线后 Server 在下次分发时自动跳过该连接。

## 部署模式

### 单机模式

Server 和 Agent 在同一主机运行，Agent 通过 `ws://127.0.0.1:8088/api/v1/agents/ws` 连接。适用于个人使用或小规模扫描。

### 分布式模式

多个 Agent 部署在不同机器，通过 `--server` 参数或 `AIG_SERVER` 环境变量指定 Server 地址。适用于：
- 大规模并发扫描
- 网络隔离环境（Agent 部署在内网，Server 在 DMZ）
- 异构环境（不同 Agent 配置不同的 Python 环境）

### Docker Compose

项目根目录提供 `docker-compose.yml`，一键启动 Server + Agent。详见 [Docker 部署示例](../examples/docker-deploy.md)。

## 相关概念

- [四种任务类型](01-task-types.md)
- [WebSocket 通信协议](04-websocket-protocol.md)
- [Go/Python 桥接](05-python-bridge.md)
- [CLI 命令行扫描](../examples/cli-scan.md)
