---
type: concept
title: "02 - 架构总览"
description: Cockle 三层 Shell 架构——主线程 Shell、Worker 通信层、ShellImpl 执行引擎
tags: [architecture, layers, worker, thread-model, design]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: worker-source
    resource: /references/worker-source.md
    title: Worker 通信参考
  - id: shell-api
    resource: /references/shell-api.md
    title: Shell API 参考
---

## 三层架构概述

Cockle 采用经典的**三层分离架构**，将 UI 交互、线程通信和命令执行严格解耦到不同的线程和模块中。这种设计确保了 Shell 的命令执行不会阻塞浏览器主线程的 UI 渲染，同时提供了灵活的通信机制以适应不同的浏览器安全策略。

```
┌─────────────────────────────────────────────────────────────┐
│                     浏览器主线程 (Main Thread)                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Shell / BaseShell                                      │ │
│  │  • 创建和管理 Worker 生命周期                            │ │
│  │  • 注册 outputCallback 接收终端输出                      │ │
│  │  • 桥接 External Command（主线程命令）                   │ │
│  │  • 暴露 IShell 公共 API（input/start/setSize 等）        │ │
│  │  • 自动检测 Worker 类型（Coincident/Comlink）            │ │
│  └────────────────────┬────────────────────────────────────┘ │
│                       │ RPC / postMessage / SAB               │
│  ┌────────────────────▼────────────────────────────────────┐ │
│  │  Worker 通信层 (Worker Thread)                           │ │
│  │  ┌─────────────────────────────────────────────────────┐│ │
│  │  │  BaseShellWorker                                    ││ │
│  │  │  • 接收主线程调用，转发到 ShellImpl                  ││ │
│  │  │  • 创建 WorkerIO（SAB 或 Service Worker）            ││ │
│  │  │  • 创建 StdinContext 管理 stdin 后端切换             ││ │
│  │  │  • 实例化 ShellImpl 并连接 IO                        ││ │
│  │  │  • 桥接外部命令的 IO 回主线程                         ││ │
│  │  └────────────────────┬────────────────────────────────┘│ │
│  │                       │                                  │ │
│  │  ┌────────────────────▼────────────────────────────────┐│ │
│  │  │  ComlinkShellWorker / CoincidentShellWorker         ││ │
│  │  │  • Comlink: postMessage RPC，不需要跨域隔离          ││ │
│  │  │  • Coincident: SAB + Atomics 同步通信，需跨域隔离    ││ │
│  │  └─────────────────────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────┘ │
│                       │ 直接方法调用（同线程）                 │
│  ┌────────────────────▼────────────────────────────────────┐ │
│  │  执行引擎层 (Worker Thread)                              │ │
│  │  ShellImpl                                               │ │
│  │  • 命令解析（Tokenizer → Parser → AST）                  │ │
│  │  • 命令执行（管道/重定向/通配符展开）                     │ │
│  │  • 文件系统交互（MEMFS / DriveFS）                       │ │
│  │  • WASM 命令加载和调用                                   │ │
│  │  • 输入处理（Enter/Backspace/Tab/Arrows/Ctrl-D）         │ │
│  │  • 环境变量/别名/历史记录管理                            │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

三层之间的职责边界非常清晰：主线程只关心 UI 交互和外部命令桥接；Worker 通信层只关心跨线程数据传输和 IO 适配；执行引擎层专注于 Shell 语义实现，完全不感知 UI 和通信细节。

## 主线程层：Shell / BaseShell

主线程层是 Cockle 对外暴露的唯一 API 入口，由 `Shell` 类和其抽象基类 `BaseShell` 组成 [F-120][F-130]。

### Shell 类

`Shell` 是唯一的具体实现类，继承自 `BaseShell`，定义在 `src/shell.ts`。它的核心职责是**创建正确类型的 Worker**：

```typescript
class Shell extends BaseShell {
  constructor(readonly options: IShell.IOptions);
  protected initWorker(options: IShell.IOptions): Worker;
}
```

`initWorker` 方法根据 `workerType` 自动选择创建 `coincident.worker.js` 或 `comlink.worker.js` [F-122-F124]。Worker 文件的 URL 基于 `baseUrl` 解析。

### BaseShell 抽象类

`BaseShell` 实现了 `IShell` 接口 [F-130]，承担了主线程侧的所有核心逻辑：

**生命周期管理**：
- 构造函数中保存配置选项，初始化信号（`commandStateChanged`、`disposed`）
- `start()` 方法触发远程连接建立和 Worker 初始化序列
- `dispose()` 方法终止 Worker 并清理资源
- `ready` Promise 在 Worker 初始化完成后 resolve

**Worker 创建与连接**：
- `initWorker()` 是抽象方法，由 `Shell` 子类实现
- `createRemote()` 方法根据 Worker 类型建立远程连接
  - Coincident 模式：直接在 `worker.proxy` 上赋值回调函数，通过 SAB 同步访问
  - Comlink 模式：使用 `Comlink.wrap()` 创建代理，通过 `registerCallbacks()` 注册回调
- 自动检测逻辑：`useCoincidentWorker()` 返回 `crossOriginIsolated` 值 [F-141]，`workerType` 据此决定为 `'coincident'` 或 `'comlink'` [F-142]

**输出桥接**：
- 接收 Worker 端传回的输出文本，通过 `outputCallback` 转发给 UI 层
- 区分 stdout 和 stderr 输出

**External Command 桥接** [F-148]：
- 当 ShellImpl 执行外部命令时，请求通过 Worker 通信层传回主线程
- `_callExternalCommand` 方法创建 `ExternalEnvironment`、`ExternalInput`、`ExternalOutput`、`ExternalTermios` 四个桥接对象
- 调用注册的外部命令函数 `command(context)`，将主线程执行结果回传 Worker

**环境初始化检测** [F-143-F146]：
- `_initialize` 方法检测 `SharedArrayBuffer` 和 `ServiceWorker` 的可用性
- 如果两者都不可用，抛出错误（stdin 无法工作）
- Coincident 模式优先使用 SAB stdin，Comlink 模式使用 Service Worker stdin

### IShell 接口

`IShell` 接口继承自 Lumino 的 `IObservableDisposable`，定义了 Cockle 对外的完整 API [F-100-F-113]：

| 成员 | 类型 | 说明 |
|------|------|------|
| `commandStateChanged` | 信号 | 命令状态变化通知（loading→running→finished） |
| `ready` | `Promise<void>` | Shell 就绪 Promise |
| `shellId` | `string` | Shell 唯一标识 |
| `size` | `ISize` | 当前终端尺寸 |
| `start()` | 方法 | 启动 Shell |
| `input(char)` | 方法 | 输入字符 |
| `exitCode()` | 方法 | 获取退出码 |
| `setSize(size/rows,cols)` | 方法 | 设置终端尺寸 |
| `themeChange(isDark?)` | 方法 | 主题切换通知 |

## Worker 层：BaseShellWorker

Worker 层运行在 Web Worker 线程中，是主线程和执行引擎之间的桥梁。由 `BaseShellWorker` 抽象基类和两个具体子类组成 [F-280-F288]。

### BaseShellWorker

`BaseShellWorker` 定义在 `src/base_shell_worker.ts`，封装了 Worker 端的公共逻辑：

**初始化流程**（`initialize` 方法）：
1. 创建 `StdinContext`（标准输入上下文），管理 SAB 和 Service Worker 两种 stdin 后端的切换
2. 创建 `WorkerIO`（Worker 端 IO），根据运行时可用性选择 SharedArrayBuffer 或 Service Worker 后端 [F-290-F296]
3. 创建 `ShellImpl` 实例，传入虚拟文件系统、环境变量、命令注册表、IO 对象等所有依赖
4. 注册内置命令，初始化 WASM 包加载器

**IO 协调**：
- `enableBufferedStdin(enable)` 方法协调主线程和 Worker 端 IO 的启用/禁用状态，确保两端同步切换缓冲 stdin 后端
- 管理 stdin 的 SAB 和 Service Worker 两种模式的动态切换

**公共方法代理**：
- `input(char: number)`：接收主线程传来的字符，转发给 ShellImpl
- `start()`：启动 ShellImpl 主循环
- `setSize(size)`：更新终端尺寸，设置 LINES/COLUMNS 环境变量
- `exitCode()`：返回最后命令的退出码
- `themeChange(isDark?)`：更新 COCKLE_DARK_MODE 环境变量

**外部命令桥接回主线程**：
- `externalInput(maxChars)`：外部命令请求用户输入，跨线程回调到主线程
- `externalOutput(text, isStderr)`：外部命令输出文本，跨线程回调到主线程
- `externalSetTermios(flags)`：外部命令设置终端属性（如 raw mode）
- `exitExternalCommand(result)`：通知外部命令执行完成

**回调注册**：
- `registerCallbacks(callbacks)`：接收主线程传来的回调函数（output、externalInput、externalOutput 等）

### ComlinkShellWorker

`ComlinkShellWorker` 继承 `BaseShellWorker`，使用 Comlink 库实现异步 RPC 通信：

- **通信机制**：基于 `postMessage`，所有方法调用都返回 Promise
- **暴露方式**：`Comlink.expose(workerInstance)` 将 Worker 实例暴露给主线程
- **DriveFS 初始化**：`initDriveFS()` 是空操作（Comlink 模式下不需要特殊初始化）
- **环境要求**：不需要 `crossOriginIsolated`，兼容性最好
- **stdin 后端**：仅支持 Service Worker 模式 [F-007]

### CoincidentShellWorker

`CoincidentShellWorker` 继承 `BaseShellWorker`，使用 Coincident 库实现基于 SAB 的同步/混合通信：

- **通信机制**：SharedArrayBuffer + Atomics，支持零延迟同步调用
- **暴露方式**：`initProxy()` 方法将所有 Worker 方法直接绑定到 `proxy` 对象，主线程通过 `worker.proxy` 直接访问
- **回调传递**：直接在 `proxy` 对象上赋值回调函数，无需 Comlink.proxy() 包装
- **环境要求**：必须设置 COOP/COEP 头，`crossOriginIsolated === true`
- **stdin 后端**：支持 SAB + Service Worker 双模式 [F-007]

### Worker 入口文件

Worker 通过两个入口文件打包为独立的 Worker bundle [F-280-F288]：

**coincident.worker.ts**（对应 `coincident.worker.js`）：
```typescript
const worker = new CoincidentShellWorker();
worker.initProxy();
// coincident 库负责将 worker.proxy 暴露给主线程
```

**comlink.worker.ts**（对应 `comlink.worker.js`）：
```typescript
const worker = new ComlinkShellWorker();
Comlink.expose(worker);
```

## 执行层：ShellImpl

`ShellImpl` 包含了 Shell 的全部执行逻辑，运行在 Worker 线程中 [F-160-F186]。它是 Cockle 的核心引擎，完全不感知主线程和通信机制的存在。

**命令解析与执行**：
- 输入行缓冲区管理，处理 Enter（执行命令）、Backspace（删除字符）、Tab（补全）、方向键（历史导航）、Ctrl-D（EOF）等特殊按键
- `_runCommands` 方法实现多命令（`;`/`&` 分隔）和管道（`|`）的调度
- `_runCommand` 方法处理单个命令的 I/O 重定向（`>`/`>>`/`<`/`2>`/`2>>`）、文件名通配符展开、运行上下文设置 [F-176]
- 调用 `parse(cmdText, aliases, throwErrors=true)` 进行命令解析 [F-174]
- `PipeNode` 通过 `Pipe` 对象将多个命令链式连接 [F-175]
- 重定向节点创建 `FileInput`/`FileOutput` 替换 stdin/stdout/stderr [F-177]

**文件名通配符** [F-178]：
- `_filenameExpansion` 方法处理 `*` 和 `?` 通配符
- 将通配符模式转为正则表达式，对 `FS.readdir` 结果进行匹配
- 默认过滤隐藏文件（以 `.` 开头的文件）

**WASM 包初始化**：
- `_initWasmPackages` 方法通过 fetch 获取 `cockle-config.json` 配置文件
- 根据配置创建 WASM 命令包（CommandPackage），注册到 CommandRegistry
- 支持惰性加载——WASM 模块仅在首次执行对应命令时下载和实例化

**文件系统初始化**：
- `_initFileSystem` 方法加载 `cockle_fs` WASM 模块，初始化 Emscripten 虚拟文件系统
- 支持 MEMFS（内存文件系统）和 DriveFS（挂载宿主机目录）

**运行环境**：
- 管理 Environment（环境变量，默认设置 COCKLE_SHELL_ID、PS1、TERM、TERMINFO）[F-300-F307]
- 管理 Aliases（命令别名，支持递归解析）
- 管理 History（命令历史，支持上下箭头滚动 `scrollCurrent`）

## 数据流

完整的数据流从用户键盘输入到终端输出呈现，经过以下路径：

```
用户按键
  │
  ▼
终端 UI (xterm.js)
  │  term.onData(data)
  ▼
BaseShell.input(char)          ← 主线程
  │
  ├─ Coincident: worker.proxy.input(char)  （直接赋值，SAB 同步）
  └─ Comlink:    remote.input(char)        （postMessage 异步）
  │
  ▼
BaseShellWorker.input(char)    ← Worker 线程
  │
  ▼
ShellImpl 输入缓冲区
  │
  ├─ 普通字符 → 追加到行缓冲，回显
  ├─ Enter    → 解析并执行命令
  ├─ Backspace→ 删除字符
  ├─ Tab      → 触发补全
  ├─ Arrows   → 历史导航
  └─ Ctrl-D   → EOF
  │
  ▼
ShellImpl._runCommands()       ← 命令执行
  │
  ├─ parse() → Tokenizer → Parser → AST
  ├─ PipeNode 链接 → 创建 Pipe 对象
  ├─ RedirectNode → 创建 FileInput/FileOutput
  ├─ 文件名展开 → _filenameExpansion()
  └─ 逐命令执行 → CommandRunner
  │
  ▼
命令输出（stdout/stderr）
  │
  ├─ Builtin 命令 → 直接写入 IOutput
  ├─ WASM 命令   → Emscripten FS → TerminalOutput
  ├─ JS 命令     → 导入模块执行
  └─ External 命令 → 跨线程回调
  │
  ▼
TerminalOutput.write(text)     ← Worker 端输出
  │
  ├─ Coincident: proxy.callbacks.output(text, isStderr)
  └─ Comlink:    callbacks.output(text, isStderr)
  │
  ▼
BaseShell 接收输出回调         ← 主线程
  │
  ▼
outputCallback(output)
  │
  ▼
终端 UI 渲染 (term.write)
```

### 关键数据流转节点

1. **输入路径**：键盘事件 → xterm.js 编码为转义序列 → `shell.input()` → Worker 通信层 → ShellImpl 输入处理。整个路径中，字符数据始终以原始字符串形式传递，不做额外编码转换。

2. **命令调度**：ShellImpl 解析命令行后，根据命令类型选择对应 CommandRunner，创建 RunContext（包含 stdin/stdout/stderr/cwd/env 等执行上下文），通过 Runner 执行命令。

3. **输出路径**：命令输出写入 IOutput 对象（通常是 TerminalOutput），TerminalOutput 的 write 方法通过 Worker 回调机制传回主线程，最终经 `outputCallback` 渲染到终端。

4. **外部命令特殊路径**：External 命令的 IO 不经过 Worker 端的虚拟文件系统，而是通过 ExternalInput/ExternalOutput 桥接到主线程，命令函数直接在主线程执行，可以访问 DOM 和浏览器 API。

## 初始化序列

从创建 Shell 到进入交互状态的完整序列：

```typescript
// 1. 主线程：创建 Shell 实例
const shell = new Shell(options);
//    → 保存 options，初始化信号
//    → 检测 workerType（crossOriginIsolated ? 'coincident' : 'comlink'）

// 2. 主线程：调用 start()
await shell.start();
//    → initWorker() 创建对应类型的 Worker
//    → createRemote() 建立远程连接
//    → 注册主线程回调（output、externalInput 等）
//    → 调用 remote.initialize(options)

// 3. Worker 线程：initialize()
//    → 创建 StdinContext
//    → 创建 WorkerIO（SAB 或 Service Worker 后端）
//    → 创建 ShellImpl 实例
//    → 注册内置命令
//    → 加载 cockle_fs WASM，初始化文件系统

// 4. 主线程：等待 ready Promise resolve
//    → Shell 就绪，显示提示符

// 5. 交互循环
//    → 用户输入字符 → shell.input(char) → Worker
//    → ShellImpl 处理输入，Enter 时执行命令
//    → 输出通过回调传回主线程 → outputCallback → UI 渲染
```

## 相关概念

- [Cockle 简介](00-introduction.md)
- [快速开始](01-getting-started.md)
- [命令系统](03-command-system.md)
- [命令解析管线](04-parsing-pipeline.md)
- [IO 系统](05-io-system.md)
