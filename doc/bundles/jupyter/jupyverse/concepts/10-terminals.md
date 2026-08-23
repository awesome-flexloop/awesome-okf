---
type: Concept
title: "终端服务"
description: "Terminals 模块提供 Jupyter 终端 REST API 和 WebSocket 通道，支持在浏览器中打开交互式终端，通过 anyio 进程管理实现跨平台终端会话。"
tags: [terminals, shell, websocket, process, pty, terminal-session]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: terminals_api
    resource: /references/terminals-api-source.md
    title: Terminals API 信源
---

# 终端服务

Terminals 服务提供浏览器内交互式终端功能，用户可以在 JupyterLab 中打开终端窗口，执行 shell 命令。

## REST API 端点

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/terminals` | terminals:read | 获取所有终端会话列表 |
| POST | `/api/terminals` | terminals:write | 创建新终端 |
| GET | `/api/terminals/{name}` | terminals:read | 获取指定终端信息 |
| DELETE | `/api/terminals/{name}` | terminals:write | 关闭终端 |
| WebSocket | `/terminals/websocket/{name}` | terminals:execute | 终端 WebSocket 通信通道 |

## 数据模型

```python
class Terminal(BaseModel):
    name: str           # 终端名称（自动生成，如 "1"、"2"）
```

## WebSocket 通信协议

终端 WebSocket 使用 JSON 消息格式：

```json
// 前端发送输入
["stdin", "ls -la\r"]

// 服务端发送输出
["stdout", "file1.txt  file2.txt\r\n$ "]

// 设置终端大小
["set_size", 24, 80]  // rows, cols
```

### 消息类型

| 类型 | 方向 | 说明 |
|------|------|------|
| `stdin` | 前端→服务端 | 用户键盘输入 |
| `stdout` | 服务端→前端 | 终端输出（ANSI 转义码支持） |
| `set_size` | 前端→服务端 | 终端窗口大小变化（行列数） |
| `disconnect` | 双向 | 断开连接 |

## TerminalsConfig

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| name | str | "bash" | 默认 shell 名称（Unix） |
| cmd | list[str] | `[]` | 自定义命令（覆盖默认 shell） |
| argv | list[str] | `[]` | 额外启动参数 |

### Shell 选择逻辑

- **Windows**：默认使用 `powershell.exe`
- **Unix/Linux/macOS**：默认使用 `bash` 或 `cmd` 配置的 shell

## 工作原理

1. **创建终端**：POST 请求触发启动一个子进程（shell），分配 PTY（伪终端）
2. **WebSocket 连接**：前端通过 WebSocket 连接到终端
3. **输入转发**：前端键盘输入通过 WebSocket 发送到 stdin 消息，写入 PTY
4. **输出转发**：PTY 输出通过 stdout 消息经 WebSocket 发送到前端
5. **大小调整**：set_size 消息调整 PTY 的行列数
6. **关闭**：DELETE 请求或 WebSocket 断开时终止子进程

## 终端与协作

与内核和文件不同，终端不支持多用户协作——一个终端会话一次只能由一个用户使用。这是因为终端是顺序交互界面，多用户同时输入会导致命令混乱。

## 相关概念

- [认证授权系统](05-auth-system.md) — 终端端点的权限控制
- [App 与 Router 基础设施](04-app-and-router.md) — Terminals 继承 Router
- [内核管理](07-kernel-management.md) — 内核和终端都使用子进程+WebSocket 模式
