---
type: Reference
title: Go WebSocket 与 HTTP Server 信源
description: 记录 common/websocket 包中 Server、AgentManager、TaskManager 的结构体、方法和消息类型。
tags: [ai-infra-guard, go, websocket, gin, server]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: src-websocket
    resource: /references/go-server.md
    title: Go WebSocket 与 HTTP Server 信源
---

## 源码路径

- `common/websocket/server.go`
- `common/websocket/agent.go`
- `common/websocket/task_manager.go`
- `common/websocket/task.go`
- `common/websocket/types.go`
- `common/websocket/sse_manager.go`
- `cmd/cli/cmd/webserver.go`
- `cmd/agent/main.go`

## HTTP 路由表

函数 `RunWebServer(options *version.Options)` 初始化 gin 引擎，注册以下路由组：

| 路由前缀 | 子路由 | 方法 |
|---------|--------|------|
| `/api/v1/knowledge/fingerprints` | `` / `/:name` | GET, POST, PUT, DELETE |
| `/api/v1/knowledge/vulnerabilities` | `` / `/:cve` | GET, POST, PUT, DELETE |
| `/api/v1/knowledge/evaluations` | `` / `/:name` | GET, POST, PUT, DELETE |
| `/api/v1/knowledge/mcp` | `/names` / `` / `/:id` | GET, POST, PUT, DELETE |
| `/api/v1/knowledge/prompt_collections` | `` / `/:id` | GET, POST, PUT, DELETE |
| `/api/v1/knowledge/agent` | `/names` / `/:name` / `/connect` / `/prompt_test` / `/template` | GET, POST, DELETE |
| `/api/v1/knowledge/jailbreak` |  | GET |
| `/api/v1/app/tasks` | `` / `/:sessionId` / `/share` / `/sse/:sessionId` / `/uploadFile` / `/uploadChunk` / `/mergeChunks` / `/:sessionId/downloadFile` / `/:sessionId/terminate` | GET, POST, PUT, DELETE |
| `/api/v1/app/models` | `` / `/:modelId` | GET, POST, PUT, DELETE |
| `/api/v1/agents/ws` |  | GET (WebSocket升级) |
| `/api/v1/app/taskapi` | `/tasks` / `/status/:id` / `/result/:id` / `/upload` / `/uploadChunk` / `/mergeChunks` | GET, POST |
| `/api/v1/version` |  | GET |
| `/api/v1/system` | `/update-data` / `/version` | GET, POST |

## 核心结构体

### AgentManager

```go
type AgentManager struct {
    connections map[string]*AgentConnection
    mu          sync.RWMutex
    taskManager *TaskManager
}
```

方法：
- `NewAgentManager() *AgentManager`
- `HandleAgentWebSocket() gin.HandlerFunc`
- `GetAvailableAgents() []*AgentConnection`
- `SetTaskManager(taskManager *TaskManager)`

### AgentConnection

```go
type AgentConnection struct {
    conn      *websocket.Conn
    agentID   string
    stateMu   sync.RWMutex
    writeMu   sync.Mutex
    isActive  bool
}
```

### TaskManager

```go
type TaskManager struct {
    mu              sync.RWMutex
    tasks           map[string]*TaskCreateRequest
    agentManager    *AgentManager
    taskStore       *database.TaskStore
    modelStore      *database.ModelStore
    fileConfig      *FileUploadConfig
    sseManager      *SSEManager
    dispatchCounter uint64
}
```

关键方法：
- `NewTaskManager(agentManager, taskStore, modelStore, fileConfig, sseManager) *TaskManager`
- `AddTask(req *TaskCreateRequest, traceID string) error`
- `AddTaskApi(req *TaskCreateRequest) error`
- `dispatchTask(sessionId string, traceID string) error`
- `HandleAgentEvent(sessionId string, eventType string, event interface{})`
- `TerminateTask(sessionId, username, traceID string) error`
- `UploadFile(file *multipart.FileHeader, traceID string) (*UploadFileResult, error)`
- `UploadFileChunk(fileID, filename string, chunkIndex, totalChunks int, chunkData []byte, traceID string) (*ChunkUploadResult, error)`
- `MergeFileChunks(fileID, filename string, totalChunks int, fileSize int64, traceID string) (*MergeChunksResult, error)`
- `EstablishSSEConnection(w http.ResponseWriter, sessionId, username, traceID string) error`

### 任务与事件结构

```go
type TaskCreateRequest struct {
    ID             string                 `json:"id"`
    SessionID      string                 `json:"sessionId"`
    Username       string                 `json:"username,omitempty"`
    Task           string                 `json:"taskType"`
    Timestamp      int64                  `json:"timestamp"`
    Content        string                 `json:"content"`
    Params         map[string]interface{} `json:"params,omitempty"`
    Attachments    []string               `json:"attachments,omitempty"`
    CountryIsoCode string                 `json:"countryIsoCode,omitempty"`
}

type WSMessage struct {
    Type    string      `json:"type"`
    Content interface{} `json:"content"`
}

type TaskContent struct {
    SessionID      string                 `json:"sessionId"`
    TaskType       string                 `json:"taskType"`
    Content        string                 `json:"content"`
    Params         map[string]interface{} `json:"params,omitempty"`
    Attachments    []string               `json:"attachments,omitempty"`
    Timeout        int                    `json:"timeout,omitempty"`
    CountryIsoCode string                 `json:"countryIsoCode,omitempty"`
}
```

## WebSocket 消息类型常量

Agent→Server：
- `register` — 注册
- `disconnect` — 主动断开
- `liveStatus` — 存活状态
- `planUpdate` — 计划更新
- `newPlanStep` — 新计划步骤
- `statusUpdate` — 状态更新
- `toolUsed` — 工具使用
- `resultUpdate` — 结果更新
- `actionLog` — 动作日志
- `error` — 错误

Server→Agent：
- `register_ack` — 注册响应
- `task_assign` — 任务分配
- `terminate` — 终止任务

## 心跳常量

```go
const (
    maxMessageSize = 512 * 1024 * 1024
    pongWait       = 120 * time.Second
    pingPeriod     = (pongWait * 8) / 10
    writeWait      = 60 * time.Second
)
```

## 任务状态常量

```go
const (
    TaskStatusTodo       = "todo"
    TaskStatusDoing      = "doing"
    TaskStatusDone       = "done"
    TaskStatusError      = "error"
    TaskStatusTerminated = "terminated"
)
```

## 相关概念

- [分布式架构总览](/concepts/00-architecture.md)
- [WebSocket 协议](/concepts/04-websocket-protocol.md)
- [四种任务类型](/concepts/01-task-types.md)
