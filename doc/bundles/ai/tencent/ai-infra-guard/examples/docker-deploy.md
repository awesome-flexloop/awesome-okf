---
type: Example
title: Docker 部署
description: 使用 docker-compose 一键部署 AIG Server 和 Agent，包含环境变量配置、数据持久化、端口映射和多 Agent 扩展说明。
tags: [ai-infra-guard, docker, deployment, docker-compose, example]
generated: { by: "reference_agent/trae-solo", at: "2026-08-23T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T00:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: go-server
    resource: /references/go-server.md
    title: Go WebSocket 与 HTTP Server 信源
  - id: python
    resource: /references/python-subsystems.md
    title: Python 子系统信源
---

## 快速启动

项目根目录提供了 `docker-compose.yml`，一键启动完整服务：

```bash
docker-compose up -d
```

启动后访问 `http://127.0.0.1:8088` 进入 Web UI。

## 镜像构建

项目提供两个 Dockerfile：

| Dockerfile | 用途 |
|-----------|------|
| `Dockerfile` | Server 镜像（含 Web UI、Go 二进制、数据文件） |
| `Dockerfile_Agent` | Agent 镜像（含 Go Agent、Python 子系统、uv 环境） |

### 构建 Server 镜像

```bash
docker build -t ai-infra-guard:latest .
```

### 构建 Agent 镜像

```bash
docker build -f Dockerfile_Agent -t ai-infra-guard-agent:latest .
```

## Docker Compose 配置

典型的 `docker-compose.yml` 结构：

```yaml
version: '3.8'

services:
  server:
    build: .
    ports:
      - "8088:8088"
    volumes:
      - aig-data:/app/data
      - aig-uploads:/app/uploads
    environment:
      - AIG_API_CHECKER_URL=http://checker:8000
    restart: unless-stopped

  agent:
    build:
      context: .
      dockerfile: Dockerfile_Agent
    depends_on:
      - server
    environment:
      - AIG_SERVER=server:8088
    restart: unless-stopped

volumes:
  aig-data:
  aig-uploads:
```

## 环境变量

### Server 端

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `AIG_API_CHECKER_URL` | `http://127.0.0.1:8000` | API Checker 服务地址，传空值禁用 |

### Agent 端

| 变量 | 说明 |
|------|------|
| `AIG_SERVER` | Server 地址（host:port），Agent 通过此地址连接 WebSocket |

### Python 子系统（AIG-PromptSecurity）

| 变量 | 说明 |
|------|------|
| `eval_base_url` | 默认评判模型 API 地址 |
| `eval_api_key` | 默认评判模型 API Key |
| `eval_model` | 默认评判模型名称 |

这些变量在 `ModelRedteamReport` 任务中作为默认评判模型使用。

## 端口说明

| 端口 | 用途 |
|------|------|
| 8088 | Web UI + REST API + WebSocket |
| 8000 | API Checker 服务（可选） |

Server 监听地址通过 `--server` 参数指定，默认 `127.0.0.1:8088`。Docker 部署时应绑定到 `0.0.0.0:8088` 以允许外部访问。

## 数据持久化

需要持久化的目录：

| 目录 | 内容 |
|------|------|
| `/app/data/` | 指纹库、漏洞库、MCP 规则、评测集 |
| `/app/uploads/` | 用户上传的文件和附件 |
| `/app/database/` | SQLite 数据库文件（任务历史、模型配置） |

## 部署架构

### 单机部署（默认）

```
┌─────────────────────────────────┐
│        Docker Host              │
│  ┌───────────┐  ┌───────────┐  │
│  │  Server   │◄─┤  Agent    │  │
│  │  :8088    │  │ (本地)    │  │
│  └───────────┘  └───────────┘  │
└─────────────────────────────────┘
```

Server 和 Agent 在同一 Docker 网络中，Agent 通过服务名 `server` 连接。

### 分布式多 Agent 部署

```
┌─────────────┐
│   Server    │  Docker Host A
│   :8088     │
└──────┬──────┘
       │ WebSocket
       ├──────────────────┐
       │                  │
┌──────▼──────┐    ┌──────▼──────┐
│  Agent 1    │    │  Agent 2    │  Docker Host B/C
│  (内网扫描)  │    │  (MCP扫描)  │
└─────────────┘    └─────────────┘
```

在远程机器上启动 Agent 并指定 Server 地址：

```bash
docker run -d \
  -e AIG_SERVER=server.example.com:8088 \
  ai-infra-guard-agent:latest
```

Server 自动通过 round-robin 在多个 Agent 间分配任务。

## Agent 能力注册

Agent 启动时自动注册以下任务能力：

```go
x.RegisterTaskFunc(&agent.AIInfraScanAgent{Server: server})
x.RegisterTaskFunc(&agent.McpTask{Server: server})
x.RegisterTaskFunc(&agent.ModelRedteamReport{Server: server})
x.RegisterTaskFunc(&agent.AgentTask{Server: server})
x.RegisterTaskFunc(&agent.SkillTask{Server: server})
```

这些能力通过 WebSocket `register` 消息的 `capabilities` 字段上报给 Server。

## 验证部署

1. 检查服务状态：

```bash
curl http://127.0.0.1:8088/api/v1/version
```

2. 检查 Agent 连接：在 Web UI 的任务创建页面，确认可以选择任务类型（表示有 Agent 在线）。

3. 提交测试扫描任务：

```bash
curl -X POST http://127.0.0.1:8088/api/v1/app/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-001",
    "sessionId": "test-session-001",
    "taskType": "AI-Infra-Scan",
    "timestamp": 1724371200,
    "content": "https://example.com",
    "countryIsoCode": "zh"
  }'
```

4. 通过 SSE 监听进度：

```bash
curl -N http://127.0.0.1:8088/api/v1/app/tasks/sse/test-session-001
```

## 安全注意事项

- Server 默认监听 `127.0.0.1`，暴露到公网时需配置反向代理和认证
- `--server 0.0.0.0:8088` 会允许外部访问，代码中有安全提示
- 身份中间件从 `username` header 取用户名，默认 `public_user`，生产环境应在反向代理层注入认证
- 文件上传有路径穿越防护，但仍建议限制上传目录的磁盘配额
- API Checker 地址可通过环境变量或 `--api-checker-url` 配置，传空字符串禁用

## 相关概念

- [分布式架构总览](/concepts/00-architecture.md)
- [WebSocket 通信协议](/concepts/04-websocket-protocol.md)
- [四种任务类型](/concepts/01-task-types.md)
- [CLI 扫描示例](/examples/cli-scan.md)
