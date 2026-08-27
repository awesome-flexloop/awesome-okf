---
type: Concept
title: Jupyter 服务器管理
description: JupyterServer 与 JupyterServerFactory 的实现，包括启动脚本生成、进程管理、端口检测、token 生成、自动重启、Factory 模式预创建与复用
tags: [server, jupyter-server, process-management, factory-pattern, port, token, auto-restart]
prerequisites:
  - /concepts/03-session-window-system.md
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: server-source
    resource: /references/server-source.md
    title: Jupyter服务器源码信源
  - id: env-source
    resource: /references/env-source.md
    title: Python环境工具源码信源
---

# Jupyter 服务器管理

## 概述

JupyterLab Desktop 通过子进程方式管理本地 Jupyter Server。`JupyterServer` 类封装单个服务器实例的生命周期，`JupyterServerFactory` 使用对象池模式管理多个服务器实例，支持预创建以加速窗口加载。

## JupyterServer 类

### 核心接口

```typescript
namespace JupyterServer {
  interface IOptions {
    port?: number;              // 端口（可选，自动检测空闲端口）
    token?: string;             // 认证 token（可选，自动生成）
    workingDirectory?: string;  // 工作目录
    environment?: IPythonEnvironment; // Python 环境
  }

  interface IInfo {
    type: 'local' | 'remote';
    url: URL;                   // 服务器完整 URL
    port: number;               // 实际端口
    token: string;              // 认证 token
    environment: IPythonEnvironment;
    workingDirectory: string;
    serverArgs: string;         // 附加启动参数
    overrideDefaultServerArgs: boolean;
    serverEnvVars: KeyValueMap; // 环境变量
    version?: string;
    pageConfig?: any;
  }
}
```

### 服务器 URL 格式

```
http://localhost:{port}/lab?token={token}
```

- 端口：随机空闲端口（通过 `getFreePort()` 检测）或指定端口
- Token：`jlab:srvr:` + `crypto.randomBytes(19).toString('hex')`
  - `SERVER_TOKEN_PREFIX = 'jlab:srvr:'` 用于标识桌面启动的服务器

### 启动脚本生成（createLaunchScript）

由于不同平台（Windows/macOS/Linux）和不同环境类型（conda/venv）的激活方式不同，服务器启动前需要生成临时启动脚本。

**启动命令结构**：

```bash
# 1. 激活环境（conda/venv）
# 2. 设置环境变量
# 3. 执行 python -m jupyterlab [固定参数] [默认参数] [用户参数]
```

**固定参数（不可覆盖）**：
- `--no-browser` - 不打开浏览器
- `--expose-app-in-browser` - 暴露 app 实例到浏览器
- `--ServerApp.port={port}` - 指定端口
- `--ServerApp.password=""` - 禁用密码认证
- `--ServerApp.token="{token}"` - 设置认证 token
- `--LabApp.quit_button=False` - 隐藏退出按钮

**默认参数（可通过 overrideDefaultServerArgs 覆盖）**：
- `--JupyterApp.config_file_name=""` - 不加载用户配置文件
- `--ContentsManager.allow_hidden=True` - 允许访问隐藏文件

**环境激活脚本差异**：

| 环境类型 | Windows | macOS/Linux |
|---------|---------|-------------|
| Conda Root | `call {condaPath}\Scripts\activate.bat {envPath}` | `source {condaPath}/bin/activate {envPath}` |
| Conda Env | `call {condaPath}\Scripts\activate.bat {envPath}` | `source activate {envPath}`（需先激活 base） |
| venv/其他 | `{envPath}\Scripts\activate.bat` | `source {envPath}/bin/activate` |

脚本保存为临时文件：
- Windows：`.bat` 文件，`cmd.exe /c` 执行
- macOS/Linux：`.sh` 文件，设置 0o755 权限后执行

启动成功后删除临时脚本文件。

### 服务器启动流程（start()）

```
start()
  │
  ├─→ 检查 Python 可执行文件存在
  ├─→ 获取空闲端口（或使用指定端口）
  ├─→ 生成随机 token
  ├─→ 构建服务器 URL
  ├─→ 处理 conda 子环境的 base 路径
  ├─→ 创建启动脚本（createLaunchScript）
  ├─→ 设置环境变量：
  │     JUPYTER_CONFIG_DIR
  │     JUPYTERLAB_WORKSPACES_DIR
  │     用户自定义 serverEnvVars
  ├─→ child_process.execFile() 执行启动脚本
  ├─→ waitUntilServerIsUp()  ← 500ms 间隔轮询 HTTP 状态码
  │     超时：30 秒（SERVER_LAUNCH_TIMEOUT）
  │     成功条件：HTTP 200-399
  └─→ 删除临时启动脚本
```

### 服务器进程退出处理

服务器进程意外退出时的处理逻辑：

```typescript
childProcess.on('exit', (code) => {
  if (server 已启动成功) {
    if (!stopping && restartCount < SERVER_RESTART_LIMIT) {
      // 自动重启（解决 Windows websocket 崩溃问题）
      restartCount++;
      this.start();  // 重新启动
    }
  } else {
    // 启动阶段退出：报告启动失败
    this._serverStartFailed();
  }
});
```

**自动重启**：最多重启 3 次（`SERVER_RESTART_LIMIT = 3`），解决 Windows 平台上 websocket 连接导致进程崩溃的已知问题。

### 服务器停止（stop()）

| 平台 | 停止方式 |
|------|---------|
| Windows | `taskkill /PID {pid} /T /F` 强制终止进程树 |
| macOS/Linux | 1. POST `http://localhost:{port}/api/shutdown`（带 token 认证）优雅关闭<br>2. 若连接被拒绝，等待服务器就绪后重试<br>3. 最后 kill 进程兜底 |

## JupyterServerFactory 类

### IFactoryItem 接口

```typescript
namespace JupyterServerFactory {
  interface IFactoryItem {
    readonly factoryId: number;   // 唯一 ID
    used: boolean;               // 是否已分配
    closing: Promise<void>;      // 关闭中 Promise
    server: JupyterServer;       // 服务器实例
  }
}
```

### Factory 方法

| 方法 | 说明 |
|------|------|
| `createFreeServer(opts?)` | 预创建空闲服务器（used=false），启动失败则移除 |
| `createFreeServersIfNeeded(opts?, freeCount?)` | 确保有指定数量的空闲服务器 |
| `createServer(opts?)` | 创建或复用空闲服务器（used=true） |
| `stopServer(factoryId)` | 停止指定服务器并移除 |
| `killAllServers()` | 停止所有服务器 |
| `isEnvironmentInUse(pythonPath)` | 检查某 Python 环境是否有运行中的服务器 |

### Free Server 复用逻辑

当窗口请求服务器时，Factory 先查找可复用的空闲服务器：

```typescript
_findUnusedServer(workingDirectory, environment):
  查找满足以下条件的服务器：
    - !server.used（未分配）
    - server.workingDirectory === workingDirectory（相同工作目录）
    - server.environment.path === environment.path（相同环境）
  找到 → 标记 used=true，返回
  未找到 → 创建新服务器
```

### 预创建时机

1. **应用启动时**：JupyterApplication 构造函数中调用 `createFreeServer()`，创建一个默认配置的空闲服务器
2. **窗口关闭后**：调用 `createFreeServersIfNeeded()` 补充空闲服务器

### 工厂 ID 分配

使用自增计数器分配唯一 factoryId：

```typescript
private _nextFactoryId = 1;
// 创建时 factoryId = this._nextFactoryId++
```

## 关键常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `SERVER_LAUNCH_TIMEOUT` | 30000 (30秒) | 服务器启动超时时间 |
| `SERVER_RESTART_LIMIT` | 3 | 最大自动重启次数 |
| `SERVER_TOKEN_PREFIX` | `'jlab:srvr:'` | 桌面启动服务器的 token 前缀 |

## 环境变量

服务器启动时设置的关键环境变量：

| 变量 | 说明 |
|------|------|
| `JUPYTER_CONFIG_DIR` | Jupyter 配置目录（避免使用用户全局配置） |
| `JUPYTERLAB_WORKSPACES_DIR` | JupyterLab 工作区目录 |
| `PATH`（追加） | Conda/Venv 的 Scripts/bin 目录（Windows 需要额外的 Library 路径） |
| 用户自定义 | 通过 serverEnvVars 设置的额外环境变量 |

## 服务器健康检查（waitUntilServerIsUp）

以 500ms 为间隔轮询服务器 URL，使用 HTTP 请求检查：

- 响应状态码在 200-399 范围 → 服务器就绪
- 连接错误/超时 → 继续等待
- 超过 30 秒 → 启动超时错误

## 运行中服务器列表

`Registry.getRunningServerList()` 通过执行 `python -m jupyter server list --json` 获取外部运行的服务器：

- 过滤条件：token 不以 `jlab:srvr:` 开头（排除桌面自己启动的）且端口仍在使用
- 这些服务器会显示在"连接到远程服务器"的列表中

## 相关信源

- [Server 信源](../references/server-source.md)
- [Registry 信源](../references/registry-source.md)
- [Env 信源](../references/env-source.md)

## 下一篇

- [Python 环境管理](05-python-env-management.md)
- [会话窗口系统](03-session-window-system.md)

## 相关概念

- [会话窗口系统](03-session-window-system.md) — 服务器为 SessionWindow 的 LabView 提供后端服务
- [Python 环境管理](05-python-env-management.md) — 服务器启动依赖 Python 环境的发现与验证
- [多窗口与会话管理](10-multi-window-multisession.md) — Factory 模式支持多窗口独立服务器实例
