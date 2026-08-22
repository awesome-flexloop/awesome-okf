---
type: Concept
title: 架构概览
description: JupyterLite Terminal的六插件分层架构、双Worker通信模式、数据流和核心设计决策
tags: [architecture, plugin, worker, websocket, mock-socket, data-flow]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: client-source
    resource: /references/client-source.md
    title: LiteTerminalAPIClient API信源
  - id: plugin-source
    resource: /references/plugin-source.md
    title: 插件系统源码信源
  - id: shell-source
    resource: /references/shell-source.md
    title: Shell与Worker源码信源
---

# 架构概览

JupyterLite Terminal 的架构可以用一句话概括：**通过替换JupyterLab的TerminalManager，在浏览器内用mock-socket+WebAssembly模拟出一个完整的终端后端**。

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    JupyterLab UI (主线程)                     │
│                                                              │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────────┐  │
│  │ xterm.js │◄──►│ mock-socket  │◄──►│ LiteTerminalAPI   │  │
│  │ (终端UI)  │    │ WebSocket   │    │ Client (核心控制器) │  │
│  └──────────┘    │ Server/Client│    └───────┬───────────┘  │
│                  └──────────────┘            │              │
│       ▲                                      │              │
│       │ 6个JupyterLab插件协作                  │              │
│  ┌────┴──────────────────────────────────────┴───────────┐  │
│  │ ① client      → 提供ILiteTerminalAPIClient            │  │
│  │ ② manager     → 替换ITerminalManager                  │  │
│  │ ③ contents    → 注入ContentsManager(DriveFS)          │  │
│  │ ④ service-worker → StdinHandler注册                   │  │
│  │ ⑤ theme-change → 主题同步                             │  │
│  │ ⑥ exec        → 无头shell命令池                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                               │                             │
│                               │ new TerminalShell()          │
│                               ▼                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              TerminalShell (extends BaseShell)         │  │
│  │  - Web Worker管理（coincident/comlink自动选择）        │  │
│  │  - DriveFS请求处理                                    │  │
│  │  - WebSocket消息路由                                  │  │
│  └───────────────┬───────────────────────────────────────┘  │
└──────────────────┼──────────────────────────────────────────┘
                   │ postMessage / SharedArrayBuffer
┌──────────────────┼──────────────────────────────────────────┐
│   Web Worker     ▼                                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  cockle WASM shell + DriveFS                          │  │
│  │                                                       │  │
│  │  ┌─────────────────┐    ┌─────────────────────────┐  │  │
│  │  │ Coincident模式   │    │ Comlink模式              │  │  │
│  │  │ (SAB+Atomics)   │    │ (Service Worker中转)     │  │  │
│  │  │ SharedBuffer-   │    │ DriveFS通过SW异步通信    │  │  │
│  │  │ ContentsAPI     │    │                         │  │  │
│  │  └─────────────────┘    └─────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 六插件分层架构

6个插件不是平铺的，而是有明确的依赖层次：

```
                    ┌──────────────┐
                    │  client      │ 提供 ILiteTerminalAPIClient
                    │ (基础层)      │
                    └──────┬───────┘
           ┌───────────┬───┴───┬───────────┬──────────────┐
           ▼           ▼       ▼           ▼              ▼
      ┌─────────┐ ┌────────┐ ┌──────┐ ┌──────────┐ ┌────────┐
      │manager  │ │contents│ │  SW  │ │  theme   │ │ exec   │
      │(终端管理)│ │(文件系统)│ │(Stdin)│ │(主题同步) │ │(命令执行)│
      └─────────┘ └────────┘ └──────┘ └──────────┘ └────────┘
```

### 依赖关系

| 插件 | 依赖 | 职责 |
|------|------|------|
| client | 无（可选IServerSettings） | 创建LiteTerminalAPIClient，注入mock WebSocket |
| manager | ILiteTerminalAPIClient | 创建TerminalManager，替换默认终端管理器 |
| contents | ILiteTerminalAPIClient | 将app.serviceManager.contents注入客户端 |
| service-worker | ILiteTerminalAPIClient, IServiceWorkerManager(可选) | 注册stdin handler到Service Worker |
| theme-change | ILiteTerminalAPIClient, ISettingRegistry; 可选IThemeManager | 监听主题变化，同步到所有终端 |
| exec | ILiteTerminalAPIClient | 创建HeadlessShellPool，注册4个编程式命令 |

除了client以外的5个插件都`requires: [ILiteTerminalAPIClient]`，确保client插件最先激活。

## 核心数据流

### 交互式终端的数据流

1. **用户打开终端**（File→New→Terminal）：
   - JupyterLab的终端插件调用ITerminalManager.startNew()
   - 请求被路由到LiteTerminalAPIClient.startNew()

2. **创建Shell**：
   - 生成终端名称（1, 2, 3...）
   - 创建TerminalShell实例（自动选择Worker类型）
   - 在`${wsUrl}/terminals/websocket/${name}`创建mock-socket WebSocketServer

3. **xterm.js连接**：
   - JupyterLab终端代码创建WebSocket连接到上述URL
   - mock-socket在浏览器内拦截此连接
   - hook函数建立socket与shell的双向绑定

4. **消息路由**：
   - 用户输入 → xterm.js → WebSocket.send(JSON.stringify(['stdin', data])) → socket.on('message') → shell.input(data)
   - shell输出 → outputCallback → JSON.stringify(['stdout', text]) → socket.send → xterm.js渲染
   - 终端大小变化 → ['set_size', rows, cols] → shell.setSize()

5. **Shell在Worker中执行**：
   - TerminalShell.initWorker()创建Web Worker
   - cockle WASM在Worker中加载运行
   - 文件IO通过DriveFS处理（SAB模式同步，SW模式异步）

6. **终端关闭**：
   - shell.disposed信号触发shutdown()
   - 发送disconnect消息、关闭socket、清理资源

### 文件系统数据流

```
WASM程序(Worker) → 文件IO调用
    │
    ├── Coincident模式: SharedBufferContentsAPI.request()
    │       → coincident proxy → Atomics.wait/notify
    │       → 主线程 DriveContentsProcessor.processDriveRequest()
    │       → ContentsManager API
    │
    └── Comlink模式: DriveFS.request()
            → Service Worker postMessage
            → 主线程 ContentsManager API
```

## 双Worker模式自动选择

TerminalShell 根据cockle BaseShell自动检测的`workerType`选择加载哪种Worker：

| 特性 | Coincident (SAB) | Comlink (SW) |
|------|------------------|--------------|
| 触发条件 | 页面有COOP/COEP头，SAB可用 | SAB不可用时的降级方案 |
| 通信方式 | SharedArrayBuffer + Atomics（同步） | postMessage + Comlink（异步） |
| 文件IO延迟 | 低（直接函数调用语义） | 较高（消息中转） |
| HTTP头要求 | 需要COEP/COOP | 不需要 |
| Worker文件 | coincident.worker.js | comlink.worker.js |
| DriveFS实现 | SharedArrayBufferFS（自定义ContentsAPI） | 标准DriveFS（传入browsingContextId） |

开发者无需关心选择哪种模式——TerminalShell.initWorker()自动处理。

## mock-socket的关键作用

mock-socket库是整个架构的"魔术"所在：

- **JupyterLab前端不做任何修改**：它仍然使用标准`new WebSocket(url)`创建终端连接
- **mock-socket拦截WebSocket构造函数**：当WebSocket URL匹配注册的模式时，连接在浏览器内闭环
- **LiteTerminalAPIClient创建WebSocketServer**：监听虚拟URL，将连接hook到shell
- **协议完全兼容**：xterm.js发送的`['stdin', data]`、`['set_size', rows, cols]`和期望接收的`['stdout', text]`、`['setup']`格式与标准Jupyter终端协议一致

这是一个经典的"依赖倒置+接口替换"模式：JupyterLab依赖WebSocket抽象，mock-socket提供了一个浏览器内的替代实现。

## HeadlessShellPool：独立于UI的命令通道

exec插件维护的HeadlessShellPool是另一条独立通道：

- 不创建WebSocketServer、不连接xterm.js
- 直接调用liteTerminalAPIClient.createHeadlessShell()创建shell
- outputCallback直接累积字符串而非通过WebSocket
- 会话命名为`headless-1`、`headless-2`等
- 不注册到Private.shells Map（不出现在终端列表中）
- 共享全局的aliases、environment、externalCommands

这为其他扩展提供了编程式访问shell的能力，类似于后端系统的`exec()` API。

## 关键设计决策

1. **复用JupyterLab终端UI**：不重写终端Widget，只替换后端通信层
2. **mock-socket而非自定义协议**：保持与标准Jupyter终端协议100%兼容
3. **六插件分离**：每个插件职责单一（客户端/管理器/文件系统/STDIN/主题/命令）
4. **双Worker自动降级**：SAB优先，SW兜底
5. **Shell池分离**：交互式终端和无头shell独立管理，避免状态交叉

## 相关概念

- [插件系统](03-plugin-system.md)：每个插件的详细实现
- [Shell与Worker机制](04-shell-and-worker.md)：TerminalShell和双Worker深入
- [无头命令执行](05-headless-exec.md)：HeadlessShellPool和编程式API
- [文件系统与Stdin路由](06-drivefs-and-stdin.md)：DriveFS挂载和stdin处理
