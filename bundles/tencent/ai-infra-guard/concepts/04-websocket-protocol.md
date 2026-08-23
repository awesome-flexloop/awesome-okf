---
type: Concept
title: WebSocket 通信协议
description: Agent 与 Server 之间通过 WebSocket 进行双向通信，定义了注册、任务分配、8 种事件上报和终止控制消息格式，配合 SSE 实现前端实时进度推送。
tags: [ai-infra-guard, websocket, protocol, sse, events, agent]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: go-server
    resource: /references/go-server.md
    title: Go WebSocket 与 HTTP Server 信源
---

## 概述

Agent ↔ Server 通信基于 WebSocket 协议，端点为 `/api/v1/agents/ws`。Server 同时通过 SSE（Server-Sent Events）向前端推送任务事件。两套协议共享相同的事件类型定义，确保 Agent → Server → Frontend 的数据透传。

## 连接建立

### Agent 端

Agent 启动时连接 WebSocket：

```go
serverUrl := fmt.Sprintf("ws://%s/api/v1/agents/ws", server)
x := agent.NewAgent(agent.AgentConfig{
    ServerURL: serverUrl,
    Info: agent.AgentInfo{
        ID:       "test_id",
        HostName: "test_hostname",
        IP:       "127.0.0.1",
        Version:  "0.1",
    },
})
```

连接后立即发送注册消息。

### Server 端

Server 使用 gorilla/websocket 升级 HTTP 连接：

```go
agents := v1.Group("/agents")
{
    agents.GET("/ws", agentManager.HandleAgentWebSocket())
}
```

最大消息大小限制为 512MB（`maxMessageSize = 512 * 1024 * 1024`）。

## 消息封装

所有 WebSocket 消息使用统一信封：

```go
type WSMessage struct {
    Type    string      `json:"type"`
    Content interface{} `json:"content"`
}
```

Agent 接收时使用：

```go
type ResponseData struct {
    Type    string          `json:"type"`
    Content json.RawMessage `json:"content"`
}
```

## 消息类型总览

### Agent → Server

| type | 说明 | Content 结构 |
|------|------|-------------|
| `register` | 注册/心跳 | `AgentRegisterContent` |
| `disconnect` | 主动断开 | `DisconnectContent` |
| `liveStatus` | 存活状态文本 | `TaskEventMessage` |
| `planUpdate` | 任务计划更新 | `PlanUpdateEvent` |
| `newPlanStep` | 新执行步骤 | `NewPlanStepEvent` |
| `statusUpdate` | 步骤状态更新 | `StatusUpdateEvent` |
| `toolUsed` | 工具使用状态 | `ToolUsedEvent` |
| `actionLog` | 工具日志 | `ActionLogEvent` |
| `resultUpdate` | 任务最终结果 | `ResultUpdateEvent` |
| `error` | 错误 | 字符串 |

### Server → Agent

| type | 说明 | Content 结构 |
|------|------|-------------|
| `register_ack` | 注册成功响应 | `Response{Status:0}` |
| `task_assign` | 任务分配 | `TaskContent` |
| `terminate` | 终止任务 | `TerminateTaskRequest` |

## 注册流程

### Agent → Server：register

```json
{
  "type": "register",
  "content": {
    "agent_id": "agent-01",
    "hostname": "worker-node-1",
    "ip": "10.0.0.5",
    "version": "0.1",
    "capabilities": ["AI-Infra-Scan", "Mcp-Scan", "Model-Redteam-Report"],
    "meta": ""
  }
}
```

字段验证规则（使用 go-playground/validator）：
- `agent_id` — required
- `hostname` — required
- `ip` — required, 必须是有效 IP
- `version` — required
- `capabilities` — 可选
- `meta` — 可选

若 agent_id 已存在，Server 断开旧连接后注册新连接。

### Server → Agent：register_ack

```json
{
  "type": "register_ack",
  "content": {
    "status": 0,
    "message": "注册成功"
  }
}
```

## 任务分配

Server 通过 round-robin 选择可用 Agent 后发送：

```json
{
  "type": "task_assign",
  "content": {
    "sessionId": "sess_abc123",
    "taskType": "AI-Infra-Scan",
    "content": "192.168.1.0/24",
    "params": {
      "model": {
        "model": "gpt-4",
        "token": "sk-xxx",
        "base_url": "https://api.openai.com/v1"
      }
    },
    "attachments": ["/api/v1/images/targets.txt_uuid.txt"],
    "timeout": 3600,
    "countryIsoCode": "zh"
  }
}
```

`params` 中的 model_id 会被 Server 解析为完整模型配置（model name/token/base_url/limit）后再下发。agent_id 会被解析为 agent_data（YAML 文本）。

## 事件上报格式

所有 Agent → Server 的进度事件使用双层封装：

```json
{
  "type": "<eventType>",
  "content": {
    "id": "msg-uuid",
    "type": "event",
    "sessionId": "sess_abc123",
    "timestamp": 1724371200,
    "event": {
      "id": "event-uuid",
      "type": "<eventType>",
      "timestamp": 1724371200,
      ...
    }
  }
}
```

外层 `type` 用于 Server 路由，内层 `content` 是前端期望的 SSE 格式。

### planUpdate（计划更新）

```json
{
  "event": {
    "id": "plan-001",
    "type": "planUpdate",
    "timestamp": 1724371200,
    "tasks": [
      {"stepId": "1", "status": "done", "title": "准备扫描环境", "startedAt": 1724371200},
      {"stepId": "2", "status": "doing", "title": "执行深度扫描", "startedAt": 1724371210},
      {"stepId": "3", "status": "todo", "title": "生成报告", "startedAt": 0}
    ]
  }
}
```

子任务状态：`todo` → `doing` → `done`。

### newPlanStep（新步骤）

```json
{
  "event": {
    "id": "step-001",
    "type": "newPlanStep",
    "timestamp": 1724371200,
    "stepId": "1",
    "title": "准备扫描环境"
  }
}
```

### statusUpdate（状态更新）

```json
{
  "event": {
    "id": "status-001",
    "type": "statusUpdate",
    "timestamp": 1724371200,
    "agentStatus": "running",
    "brief": "Thinking",
    "description": "正在初始化扫描配置...",
    "noRender": false,
    "planStepId": "1"
  }
}
```

Agent 状态：`running`、`completed`、`failed`、`idle`、`terminated`。

### toolUsed（工具使用）

```json
{
  "event": {
    "id": "tool-001",
    "type": "toolUsed",
    "timestamp": 1724371200,
    "description": "执行扫描",
    "planStepId": "2",
    "statusId": "status-002",
    "tools": [
      {
        "toolId": "tool-uuid",
        "tool": "ai_scanner",
        "status": "doing",
        "brief": "正在执行AI基础设施扫描",
        "message": {"action": "扫描", "param": "目标系统"},
        "result": ""
      }
    ]
  }
}
```

工具状态：`doing` → `done`。

### actionLog（动作日志）

```json
{
  "event": {
    "id": "log-001",
    "type": "actionLog",
    "timestamp": 1724371200,
    "actionId": "action-uuid",
    "tool": "nmap",
    "planStepId": "1",
    "actionLog": "发现端口: 192.168.1.1:11434"
  }
}
```

### resultUpdate（最终结果）

```json
{
  "event": {
    "id": "result-001",
    "type": "resultUpdate",
    "timestamp": 1724371500,
    "result": {
      "total": 3,
      "score": 60,
      "results": [...]
    }
  }
}
```

Server 收到此事件后更新任务状态为 `done`，异步清理内存和 SSE 资源。

## 任务终止

### Server → Agent：terminate

用户在前端点击终止时，Server 发送：

```json
{
  "type": "terminate",
  "content": {
    "session_id": "sess_abc123",
    "reason": "用户主动终止"
  }
}
```

Agent 收到后调用对应任务的 `context.Cancel()`，Python 子进程通过 ctx 取消。

## SSE 前端推送

Server 在收到 Agent 事件后，通过 `SSEManager` 转发给前端：

```
GET /api/v1/app/tasks/sse/sess_abc123
```

SSE 消息格式：

```
id: <event-id>
event: <eventType>
data: {"id":"...","type":"...","sessionId":"...","timestamp":...,"event":{...}}
```

任务创建时 Server 会等待最多 100 秒让前端建立 SSE 连接，超时则任务创建失败并清理预存数据。

## 心跳机制

Server 端：
- 每 `pingPeriod`（96秒）发送 WebSocket Ping
- Agent 需在 `pongWait`（120秒）内回复 Pong
- 写超时 `writeWait`（60秒）
- Ping 失败后重试一次，仍失败标记连接非活跃

Agent 端：
- 设置 PingHandler 自动回复 Pong
- 设置 PongHandler 续期读超时
- 连接断开后 `handleReceive` 退出循环

## 相关概念

- [分布式架构总览](/concepts/00-architecture.md)
- [四种任务类型](/concepts/01-task-types.md)
- [Go/Python 桥接](/concepts/05-python-bridge.md)
