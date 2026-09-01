---
type: Reference
title: JupyterServer 服务器管理源码信源
description: src/main/server.ts Jupyter 服务器管理源码登记，包含 JupyterServer 类（本地服务器启停、进程管理、自动重启）和 JupyterServerFactory 类（预创建 free server、服务器池管理）
tags: [server, jupyter-server, factory, process, port, token, auto-restart]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: server-ts
    resource: https://github.com/jupyterlab/jupyterlab-desktop/blob/master/src/main/server.ts
    title: server.ts source on GitHub
---

# JupyterServer 服务器管理源码信源

## 源码路径

`src/main/server.ts`

## 文件职责

管理本地 Jupyter 服务器的生命周期，包括服务器启动脚本生成、进程管理、健康检查、自动重启、工厂模式预创建。

## JupyterServer 类

### 核心接口

```typescript
export namespace JupyterServer {
  export interface IOptions {
    port?: number;
    token?: string;
    workingDirectory?: string;
    environment?: IPythonEnvironment;
  }
  export interface IInfo {
    type: 'local' | 'remote';
    url: URL;
    port: number;
    token: string;
    environment: IPythonEnvironment;
    workingDirectory: string;
    serverArgs: string;
    overrideDefaultServerArgs: boolean;
    serverEnvVars: KeyValueMap;
    version?: string;
    pageConfig?: any;
  }
}
```

### createLaunchScript() 函数

为不同平台和环境类型生成服务器启动脚本：

- **启动命令**：`python -m jupyterlab` 附加固定参数和默认参数
- **固定参数**（`serverLaunchArgsFixed`）：`--no-browser`、`--expose-app-in-browser`、`--ServerApp.port={port}`、`--ServerApp.password=""`、`--ServerApp.token="{token}"`、`--LabApp.quit_button=False`
- **默认参数**（`serverLaunchArgsDefault`）：`--JupyterApp.config_file_name=""`、`--ContentsManager.allow_hidden=True`
- **Conda 激活**：根据 conda 环境类型（root/env）和平台（win/mac/linux）生成不同的激活脚本路径和命令
- **非 Conda 环境**：使用 `activatePathForEnvPath()` 生成的激活脚本
- 脚本保存为临时文件（`.bat` 或 `.sh`），非 Windows 平台设置 0o755 权限

### 服务器启动流程（start() 方法）

1. 检查 Python 可执行文件是否存在
2. 获取空闲端口（`getFreePort()`）或使用指定端口
3. 生成随机 token（`randomBytes(19).toString('hex')`，前缀 `SERVER_TOKEN_PREFIX`）
4. 构建服务器 URL：`http://localhost:{port}/lab?token={token}`
5. 处理 conda 子环境需要 base conda 路径的特殊情况
6. 创建启动脚本
7. 设置环境变量（`JUPYTER_CONFIG_DIR`、`JUPYTERLAB_WORKSPACES_DIR`、自定义 serverEnvVars）
8. 使用 `child_process.execFile` 执行启动脚本
9. 使用 `Promise.race` 等待服务器就绪（`waitUntilServerIsUp` 轮询 HTTP 检查，超时 30 秒）
10. 服务器启动成功后删除临时启动脚本

### 服务器进程退出处理

- **已启动后退出**：清理监听器，若未在停止过程中且重启次数 < 3，则自动重启服务器（解决 Windows websocket 连接崩溃问题）
- **启动前退出**：调用 `_serverStartFailed()` 拒绝 Promise

### 服务器停止（stop() 方法）

- Windows：使用 `taskkill /PID /T /F` 强制终止进程树
- 非 Windows：先调用 `/api/shutdown` POST API（带 token 认证）优雅关闭，若连接被拒绝则等待服务器就绪后再尝试；最后 kill 进程

### waitUntilServerIsUp()

以 500ms 间隔轮询服务器 URL，HTTP 状态码 200-399 判定为就绪。

## JupyterServerFactory 类

实现 `IServerFactory` 接口，管理服务器池：

| 方法 | 说明 |
|------|------|
| `createFreeServer(opts?)` | 预创建空闲服务器（不标记 used），启动失败则从池中移除 |
| `createFreeServersIfNeeded(opts?, freeCount?)` | 确保有指定数量的空闲服务器 |
| `createServer(opts?)` | 创建或复用空闲服务器，标记 used=true |
| `stopServer(factoryId)` | 停止指定服务器并从池中移除 |
| `killAllServers()` | 停止所有服务器 |
| `isEnvironmentInUse(pythonPath)` | 检查某 Python 环境是否有服务器在运行 |

### Free Server 复用逻辑

`_findUnusedServer()` 匹配条件：`!server.used && workingDirectory 相同 && environment.path 相同`

### IFactoryItem 接口

```typescript
export namespace JupyterServerFactory {
  export interface IFactoryItem {
    readonly factoryId: number;
    used: boolean;
    closing: Promise<void>;
    server: JupyterServer;
  }
}
```

## 关键常量

- `SERVER_LAUNCH_TIMEOUT = 30000`（30 秒启动超时）
- `SERVER_RESTART_LIMIT = 3`（最大自动重启次数）
- 服务器 token 前缀从 registry.ts 的 `SERVER_TOKEN_PREFIX` 导入

## 相关概念

- [Jupyter 服务器管理](../concepts/04-server-management.md)
- [Python 环境管理](../concepts/05-python-env-management.md)
- [会话窗口系统](../concepts/03-session-window-system.md)
