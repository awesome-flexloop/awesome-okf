---
type: Concept
title: 文件系统与Stdin路由
description: DriveFS挂载机制、两种Worker模式下的文件IO路由、stdin处理流程和ContentsManager集成
tags: [drivefs, stdin, contents-manager, service-worker, sharedarraybuffer, file-system, mounting]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: shell-source
    resource: /references/shell-source.md
    title: Shell与Worker源码信源
  - id: plugin-source
    resource: /references/plugin-source.md
    title: 插件系统源码信源
  - id: client-source
    resource: /references/client-source.md
    title: LiteTerminalAPIClient API信源
---

# 文件系统与Stdin路由

JupyterLite Terminal 通过 DriveFS 将 JupyterLite 的虚拟文件系统挂载到 shell 中，使得终端命令可以读写 JupyterLite 环境中的文件。同时，stdin（标准输入）在不同 Worker 模式下有不同的路由机制。

## DriveFS 概述

DriveFS 是 `@jupyterlite/services` 提供的浏览器端文件系统层，它实现了类POSIX文件系统接口，将文件操作请求路由到 JupyterLite 的 ContentsManager。终端默认将 DriveFS 挂载到 `/drive` 目录。

```
WASM shell (Worker)
    │
    │ 文件操作 (open/read/write/stat...)
    ▼
DriveFS (Worker侧)
    │
    │ 请求路由（两种模式）
    ▼
┌───────────────────────────────────────┐
│ 模式A: Coincident (SAB)               │ 模式B: Comlink (SW)
│ SharedBufferContentsAPI.request()     │ DriveFS.request()
│ → coincident proxy (同步)             │ → Service Worker postMessage
│ → 主线程 DriveContentsProcessor       │ → 主线程 StdinHandler
│ → ContentsManager API                 │ → Private.shellManager
│                                       │ → ContentsManager API
└───────────────────────────────────────┘
```

## 挂载点配置

创建TerminalShell时，`mountpoint: '/drive'`被传入。在Worker的initDriveFS中：

```typescript
// 两种模式都检查相同条件
if (mountpoint !== '' && baseUrl !== undefined) {
  // 创建DriveFS实例并挂载
  FS.mount(driveFS, {}, mountpoint);
} else {
  console.warn('Terminal not connected to shared drive');
}
```

在shell中可以通过以下命令验证挂载：

```bash
ls /drive
# 如果contentsPlugin未激活或ContentsManager未注入，/drive可能为空或不存在
```

## SAB模式下的文件IO

### SharedBufferContentsAPI

在coincident模式下，自定义了ContentsAPI子类：

```typescript
class SharedBufferContentsAPI extends ContentsAPI {
  request<T extends TDriveMethod>(data: TDriveRequest<T>): TDriveResponse<T> {
    return proxy.processDriveRequest(data) as unknown as TDriveResponse<T>;
  }
}
```

关键特征：
- `request()`是**同步方法**（没有async/await）
- 通过`proxy.processDriveRequest(data)`直接调用主线程方法
- coincident在底层处理Atomics.wait/notify同步等待
- 从WASM程序视角，文件IO是同步操作（与真实OS一致）

### SharedArrayBufferFS

```typescript
class SharedArrayBufferFS extends DriveFS {
  createAPI(options: DriveFS.IOptions): ContentsAPI {
    return new SharedBufferContentsAPI(options);
  }
}
```

工厂方法返回SharedBufferContentsAPI而非默认ContentsAPI。

### 主线程回调

```typescript
remote.processDriveRequest = async <T extends TDriveMethod>(data: TDriveRequest<T>) => {
  if (!this._contentsProcessor) {
    this._contentsProcessor = new DriveContentsProcessor({
      contentsManager: this._contentsManager
    });
  }
  return this._contentsProcessor.processDriveRequest(data);
};
```

- **懒初始化**：DriveContentsProcessor在第一次文件IO请求时创建
- 使用注入的`_contentsManager`（来自terminalContentsPlugin设置的`app.serviceManager.contents`）
- 虽然主线程侧是async，但coincident等待Promise resolve后再返回Worker

## SW模式下的文件IO

### 标准DriveFS

comlink模式直接使用@jupyterlite/services的DriveFS，不需要自定义子类：

```typescript
const driveFS = new DriveFS({
  FS, PATH, ERRNO_CODES,
  baseUrl,
  driveName: '',
  mountpoint,
  browsingContextId  // 关键参数：SW路由标识符
});
```

### 请求路径

```
WASM程序 → DriveFS.request()
    → postMessage({ type: 'stdin', data, browsingContextId })
    → Service Worker
    → 根据browsingContextId找到目标tab
    → postMessage到主线程
    → registerStdinHandler注册的回调
    → LiteTerminalAPIClient.handleStdin()
    → Private.shellManager处理
    → DriveContentsProcessor.processDriveRequest()
    → ContentsManager API
    → 结果沿原路返回
```

### browsingContextId的作用

每个浏览器标签页有唯一的browsingContextId，Service Worker用它来路由消息到正确的页面：

```typescript
// terminalServiceWorkerPlugin激活时设置
liteTerminalAPIClient.browsingContextId = serviceWorkerManager.browsingContextId;
```

在shell创建时，browsingContextId通过createShell参数传递给Worker。

## ContentsManager注入

terminalContentsPlugin负责将ContentsManager注入：

```typescript
activate: (app, liteTerminalAPIClient) => {
  const { contents: contentsManager } = app.serviceManager;
  liteTerminalAPIClient.contentsManager = contentsManager;
}
```

如果没有这个插件（不应该发生，因为requires确保依赖），shell仍然能创建，但文件IO会失败：
- SAB模式：processDriveRequest回调未设置，调用会报错
- SW模式：browsingContextId可能未设置，DriveFS初始化跳过

## Stdin处理流程

Stdin（标准输入）在终端中有两种场景：

### 1. 交互式终端的用户输入

用户在xterm.js中输入字符 → WebSocket发送`['stdin', text]` → shell.input(text)

这是最直接的路径，不经过DriveFS或Service Worker。

### 2. Shell程序的文件IO请求（SAB模式下）

通过SharedBufferContentsAPI → coincident proxy → DriveContentsProcessor。这在SAB模式下是同步的。

### 3. Shell程序的文件IO请求（SW模式下）

```
Worker中的DriveFS
    ↓ postMessage到Service Worker
Service Worker
    ↓ 根据browsingContextId路由
主线程 StdinHandler (registerStdinHandler('terminal', handler))
    ↓
LiteTerminalAPIClient.handleStdin(request)
    ↓
Private.shellManager (cockle ShellManager模块级单例)
    ↓ 根据shellId路由到正确的shell实例
DriveContentsProcessor.processDriveRequest(data)
    ↓
ContentsManager API
    ↓ 结果异步返回
```

## 交互式命令的Stdin

对于需要用户输入的命令（如`grep`等待stdin输入）：

- **SAB模式**：通过coincident proxy同步请求主线程获取输入
- **SW模式**：通过Service Worker异步请求

用户在xterm.js中的输入通过shell.input()流入，cockle shell内部根据stdin模式（通过`cockle-config stdin`切换）路由到正确的通道。

### stdin模式切换

```bash
# 查看当前stdin模式
cockle-config stdin

# 切换到SAB模式（需要COOP/COEP头）
cockle-config stdin sab

# 切换到SW模式
cockle-config stdin sw
```

## 文件操作示例

在终端中可以操作`/drive`目录下的文件，这些文件对应JupyterLite ContentsManager中的文件：

```bash
# 列出DriveFS根目录（对应JupyterLite文件浏览器根目录）
ls /drive

# 查看文件
cat /drive/months.txt

# 创建目录
mkdir /drive/newdir

# 复制文件
cp /drive/months.txt /drive/backup.txt

# 重定向输出到文件
echo "hello" > /drive/output.txt

# 管道操作
cat /drive/months.txt | grep ember
```

> **注意**：文件操作通过DriveFS→ContentsManager路由，实际存储由JupyterLite的存储后端决定（通常是浏览器IndexedDB或通过Service Worker的内存存储）。

## 文件路径映射

| Shell路径 | 对应JupyterLite位置 |
|-----------|-------------------|
| `/` | cockle WASM虚拟文件系统根（包含/bin、/dev等） |
| `/drive/` | JupyterLite ContentsManager根目录 |
| `/drive/data.csv` | JupyterLite文件浏览器中的data.csv |
| `/tmp/` | cockle虚拟tmp目录（内存，不持久化） |

## 相关概念

- [Shell与Worker机制](04-shell-and-worker.md)：Worker初始化和通信细节
- [插件系统](03-plugin-system.md)：contentsPlugin和serviceWorkerPlugin职责
- [示例：基础终端使用](../examples/01-basic-terminal-usage.md)：终端内文件操作示例
- [Shell与Worker源码信源](../references/shell-source.md)：DriveFS完整实现
