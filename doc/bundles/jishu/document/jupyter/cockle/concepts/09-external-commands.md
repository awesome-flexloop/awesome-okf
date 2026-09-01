---
type: concept
title: 09 - 外部命令
description: 在主线程执行的 External Command——注册方法、IRunContext接口、Tab补全和与Worker的桥接机制
tags: [external-commands, main-thread, bridge, custom-commands, integration]
generated:
  by: "agent:source-code-to-okf-wiki"
  at: "2026-08-22T00:00:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-22T00:00:00+08:00"
status: stable
stale_after: "2027-08-22"
sources:
  - id: shell-api
    resource: /references/shell-api.md
    title: Shell API参考
  - id: cmd-source
    resource: /references/command-source.md
    title: 命令系统参考
---

# 外部命令

外部命令（External Commands）是在浏览器**主线程**执行的自定义命令，由宿主应用通过 Shell 构造函数的 `externalCommands` 选项注册。与在 Worker（工作线程）中执行的内置命令和 WASM（WebAssembly）命令不同，外部命令可以直接访问 DOM（文档对象模型）、浏览器 API 和主线程上的 JavaScript 库，是 Cockle（浏览器Shell）与宿主应用集成的主要扩展点。

## 什么是外部命令

Cockle 有三种命令类型，执行位置和能力各有不同：

| 命令类型 | 执行线程 | 语言 | 能访问浏览器API | 典型用途 |
|----------|----------|------|----------------|----------|
| 内置命令 | Worker | TypeScript | ❌ 不能 | Shell 核心功能 |
| WASM 命令 | Worker | C/C++→WASM | ❌ 不能 | Unix 工具（ls、cat、vim等） |
| JavaScript 命令 | Worker | JavaScript | ❌ 不能 | 轻量脚本 |
| **外部命令** | **主线程** | **JavaScript** | **✅ 可以** | **应用集成、DOM操作、调用主线程库** |

### 主线程执行的优势

外部命令在主线程执行，可以：

- 操作 DOM 元素（更新页面内容、操作编辑器等）
- 调用浏览器 API（fetch 跨域资源、Notification、Clipboard 等）
- 使用主线程上已加载的库（React、Vue、Monaco Editor 等）
- 访问宿主应用的状态和方法（如 JupyterLab 的 notebook API）

### PromiseDelegate 防死锁

外部命令虽然在主线程执行，但 Worker 端的命令执行流程需要等待其完成。为了防止 Worker 等待导致消息循环阻塞，Cockle 使用 PromiseDelegate（承诺委托）模式处理跨线程异步等待：

```
Worker 线程                           主线程
    │                                   │
    │ 解析到外部命令                      │
    │ ExternalCommandRunner             │
    │ ── _callExternalCommand ─────────►│
    │                                   │ 创建ExternalEnvironment/IO
    │                                   │ 执行用户定义的command函数
    │                                   │ ...（可以异步操作DOM、fetch等）
    │                                   │ command返回exitCode
    │ ◄─────── 退出码 ──────────────────┤
    │ 继续下一条命令                      │
```

关键设计点：Worker 发起外部命令调用后，通过 Promise 等待结果；此时 Worker 的消息循环仍然可以处理其他消息（如终端渲染），不会完全阻塞。

## 注册外部命令

外部命令通过 Shell 构造函数的 `externalCommands` 选项注册，是一个数组，每个元素符合 `IExternalCommand.IOptions` 接口。

### IExternalCommand.IOptions 接口

```typescript
namespace IExternalCommand {
  interface IOptions {
    // 命令名称（用户输入的命令名）
    name: string;
    
    // 命令执行函数，接收运行上下文，返回退出码的Promise
    command: (context: IExternalCommand.IRunContext) => Promise<number>;
    
    // 可选：Tab补全函数
    tabComplete?: (
      context: IExternalCommand.ITabCompleteContext
    ) => IExternalCommand.ITabCompleteResult;
  }
}
```

### 基本注册示例

```typescript
import { CockleShell } from '@jupyter/cockle';

// 创建Shell实例时注册外部命令
const shell = new CockleShell({
  // ...其他选项
  externalCommands: [
    {
      name: 'open',
      command: async (context) => {
        const url = context.args[0];
        if (!url) {
          context.stderr.write('Usage: open <url>\n');
          return 1;
        }
        // 主线程可以直接调用window.open
        window.open(url, '_blank');
        return 0;
      }
    },
    {
      name: 'notify',
      command: async (context) => {
        const message = context.args.join(' ');
        if (!message) {
          context.stderr.write('Usage: notify <message>\n');
          return 1;
        }
        // 使用浏览器Notification API
        if (Notification.permission === 'granted') {
          new Notification('Cockle', { body: message });
        } else {
          context.stderr.write('Notification permission not granted\n');
          return 1;
        }
        return 0;
      }
    }
  ]
});
```

使用：

```bash
open https://jupyter.org
notify "Task completed!"
```

### 多个外部命令

可以注册任意数量的外部命令：

```typescript
const shell = new CockleShell({
  externalCommands: [
    { name: 'open', command: openCommand },
    { name: 'notify', command: notifyCommand },
    { name: 'save', command: saveCommand, tabComplete: saveTabComplete },
    { name: 'clipboard', command: clipboardCommand },
    { name: 'theme', command: themeCommand },
  ]
});
```

外部命令名不能与内置命令重名，否则内置命令会优先执行。

## IRunContext 接口

外部命令的 `command` 函数接收一个 `IRunContext` 参数，提供命令执行所需的所有上下文信息。

```typescript
namespace IExternalCommand {
  interface IRunContext {
    // 命令参数（不包括命令名本身）
    args: string[];
    
    // 当前工作目录
    cwd: string;
    
    // 环境变量（只读副本）
    env: Record<string, string>;
    
    // 标准输入流
    stdin: IExternalInput;
    
    // 标准输出流
    stdout: IExternalOutput;
    
    // 标准错误流
    stderr: IExternalOutput;
    
    // 退出码（命令执行前为0，可修改）
    exitCode: number;
    
    // 外部输出回调（用于发送非文本输出，如文件数据）
    externalOutput: (data: any) => void;
    
    // 设置终端模式
    setTermios: (termios: Partial<Termios>) => void;
  }
}
```

### args：命令参数

`args` 是命令名之后的参数数组，已完成引号解析和通配符展开：

```typescript
{
  name: 'greet',
  command: async (context) => {
    // 用户输入: greet "Hello World" foo bar
    // context.args = ["Hello World", "foo", "bar"]
    const name = context.args[0] || 'World';
    context.stdout.write(`Hello, ${name}!\n`);
    return 0;
  }
}
```

### cwd：当前工作目录

`cwd` 是命令执行时的工作目录，文件操作应基于此路径：

```typescript
{
  name: 'pwd',
  command: async (context) => {
    context.stdout.write(context.cwd + '\n');
    return 0;
  }
}
```

注意：外部命令不能直接访问 Worker 内的 Emscripten FS 对象。如果需要读写文件，应通过 `context.stdin` 读取或通过主线程与 DriveFS 交互。

### env：环境变量

`env` 是当前环境变量的只读副本：

```typescript
{
  name: 'shell-info',
  command: async (context) => {
    context.stdout.write(`Shell ID: ${context.env.COCKLE_SHELL_ID}\n`);
    context.stdout.write(`TERM: ${context.env.TERM}\n`);
    context.stdout.write(`Dark mode: ${context.env.COCKLE_DARK_MODE === '1' ? 'on' : 'off'}\n`);
    return 0;
  }
}
```

### stdin/stdout/stderr：IO 流

IO 流用于与用户交互。`IExternalOutput` 接口是简单的可写流：

```typescript
interface IExternalOutput {
  write(data: string): void;
}
```

读取用户输入的示例：

```typescript
{
  name: 'prompt-demo',
  command: async (context) => {
    context.stdout.write('What is your name? ');
    // 从stdin读取一行
    const name = await readLine(context.stdin);
    context.stdout.write(`Hello, ${name}!\n`);
    return 0;
  }
}

// 辅助函数：从stdin读取一行
function readLine(stdin: IExternalInput): Promise<string> {
  return new Promise(resolve => {
    let buffer = '';
    const onData = (data: string) => {
      buffer += data;
      if (buffer.includes('\n')) {
        stdin.removeEventListener('data', onData);
        resolve(buffer.trim());
      }
    };
    stdin.addEventListener('data', onData);
  });
}
```

### setTermios：设置终端模式

`setTermios` 用于切换终端模式，比如需要逐字符输入的场景（如交互式程序）：

```typescript
{
  name: 'keypress',
  command: async (context) => {
    context.stdout.write('Press any key (q to quit):\n');
    
    // 设置为原始模式（逐字符输入，不回显）
    context.setTermios({
      ICANON: false,  // 禁用规范模式
      ECHO: false     // 禁用回显
    });
    
    try {
      while (true) {
        const char = await readChar(context.stdin);
        if (char === 'q' || char === '\x03') break;  // q或Ctrl+C
        context.stdout.write(`You pressed: ${char}\r\n`);
      }
    } finally {
      // 恢复默认模式
      context.setTermios({ ICANON: true, ECHO: true });
    }
    return 0;
  }
}
```

## ExternalEnvironment/ExternalInput/ExternalOutput/ExternalTermios

当外部命令被调用时，Worker 端通过 `_callExternalCommand` 方法创建一套隔离的 IO 环境，通过消息传递到主线程。

### _callExternalCommand 流程

```typescript
// ShellImpl._callExternalCommand 简化流程
private async _callExternalCommand(
  name: string,
  args: string[],
  runContext: RunContext
): Promise<number> {
  // 创建隔离的IO环境
  const externalEnv = new ExternalEnvironment(runContext.env);
  const externalInput = new ExternalInput();
  const externalOutput = new ExternalOutput(runContext.stdout);
  const externalErrOutput = new ExternalOutput(runContext.stderr);
  const externalTermios = new ExternalTermios(runContext.termios);
  
  const context: IExternalCommand.IRunContext = {
    args,
    cwd: this._cwd,
    env: externalEnv.toObject(),
    stdin: externalInput,
    stdout: externalOutput,
    stderr: externalErrOutput,
    exitCode: 0,
    externalOutput: (data) => this._handleExternalOutput(data),
    setTermios: (t) => externalTermios.update(t)
  };
  
  // 通过Worker通信机制将调用转发到主线程
  const exitCode = await this._callback.callExternalCommand(name, context);
  
  // 将外部命令期间产生的输出刷新到真实stdout
  externalOutput.flush();
  externalErrOutput.flush();
  
  return exitCode;
}
```

这四个包装类的作用：

| 类 | 作用 |
|---|---|
| **ExternalEnvironment** | 将 Worker 端的 Environment Map 转换为普通对象传递到主线程 |
| **ExternalInput** | 代理 Worker 端的 stdin，通过消息将主线程读取请求转发回 Worker |
| **ExternalOutput** | 缓冲输出数据，命令结束后一次性刷新到 Worker 端的真实 stdout |
| **ExternalTermios** | 代理终端模式设置，通过消息同步 Worker 端的 termios 状态 |

### 为什么需要缓冲输出

ExternalOutput 采用缓冲设计是因为：
1. 主线程的输出需要通过 postMessage 传回 Worker
2. 批量传输减少跨线程消息次数
3. 命令执行期间输出先累积，结束后一次性写入真实终端

## 跨线程桥接流程

外部命令的完整执行涉及 Worker 和主线程之间的多次消息往返：

```
┌─────────────────────────────────────────────────────────────────┐
│ Worker 线程 (ShellImpl)                                          │
│                                                                   │
│ 1. 解析命令行 → 发现是外部命令                                    │
│ 2. ExternalCommandRunner.run()                                   │
│ 3. 创建 ExternalEnvironment/Input/Output/Termios                 │
│ 4. 调用 callback.callExternalCommand(name, context)              │
│    │                                                              │
│    │  {via Comlink/Coincident RPC}                                │
│    ▼                                                              │
│ ───────────────────────────────────────────────────────────────► │
│                                                                   │
│    ▼                                                              │
│ 5. 等待 Promise...                                               │
│                                                                   │
│                                       ┌─────────────────────────┐│
│                                       │ 主线程 (BaseShell)       ││
│                                       │                           ││
│                                       │ 6. 接收 callExternalCommand │
│                                       │ 7. 查找注册的命令函数     ││
│                                       │ 8. 调用 command(context) ││
│                                       │    │                      ││
│                                       │    │ 执行用户逻辑...       ││
│                                       │    │ 可以操作DOM、fetch  ││
│                                       │    │                      ││
│                                       │    │ context.stdout.write │
│                                       │    │ → 数据写入ExternalOutput │
│                                       │    │                      ││
│                                       │    │ await context.stdin.read │
│                                       │    │ → 发消息回Worker请求输入 │
│                                       │ ◄──┘                      ││
│                                       │    │                      ││
│                                       │ 9. command返回exitCode   ││
│                                       └────────┬────────────────┘│
│                                                │                  │
│ ◄──────────────────────────────────────────────┘                  │
│    ▲                                                              │
│ 10. 接收exitCode                                                 │
│ 11. flush ExternalOutput 到终端                                  │
│ 12. 返回exitCode，继续执行                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Comlink vs Coincident 的桥接差异

桥接机制根据 Worker 通信模式有所不同：

- **Comlink 模式**：使用 `Comlink.wrap(worker)` 创建代理，通过 `proxy()` 传递回调函数。外部命令调用是标准的 RPC（远程过程调用）。
- **Coincident 模式**：直接在 `worker.proxy` 对象上赋值回调，外部命令调用通过共享代理直接执行，延迟更低。

详见 [11 - Worker 通信机制](11-worker-communication.md)。

## 自定义 Tab 补全

外部命令可以提供 `tabComplete` 函数，实现自定义的 Tab 补全逻辑。

### ITabCompleteContext 和 ITabCompleteResult

```typescript
namespace IExternalCommand {
  interface ITabCompleteContext {
    // 当前正在补全的参数（部分输入）
    args: string[];
    // 当前光标所在的参数索引
    currentArg: number;
    // 当前工作目录
    cwd: string;
    // 环境变量
    env: Record<string, string>;
  }
  
  interface ITabCompleteResult {
    // 补全候选列表
    completions: string[];
    // 所有候选项的公共前缀（用于自动补全到公共部分）
    commonPrefix?: string;
  }
}
```

### Tab 补全示例

```typescript
const themeCommand: IExternalCommand.IOptions = {
  name: 'theme',
  command: async (context) => {
    const theme = context.args[0];
    if (!theme) {
      context.stderr.write('Usage: theme <light|dark|auto>\n');
      return 1;
    }
    document.documentElement.setAttribute('data-theme', theme);
    context.stdout.write(`Theme set to ${theme}\n`);
    return 0;
  },
  tabComplete: (context) => {
    const themes = ['light', 'dark', 'auto'];
    const partial = context.args[context.currentArg] || '';
    return {
      completions: themes.filter(t => t.startsWith(partial))
    };
  }
};
```

更复杂的补全（如文件名补全）可以结合宿主应用的 API：

```typescript
{
  name: 'open-file',
  command: async (context) => {
    const filename = context.args[0];
    // 使用主线程的文件API
    const content = await readFileFromDrive(filename);
    context.stdout.write(content);
    return 0;
  },
  tabComplete: async (context) => {
    const partial = context.args[context.currentArg] || '';
    // 从DriveFS获取文件列表
    const files = await listFilesInDirectory(context.cwd);
    return {
      completions: files
        .filter(f => f.startsWith(partial))
        .map(f => f.includes(' ') ? `"${f}"` : f)
    };
  }
}
```

## 使用场景

外部命令是 Cockle 与浏览器环境和宿主应用集成的核心机制，以下是常见使用场景。

### 集成浏览器 API

```typescript
// 复制到剪贴板
{
  name: 'copy',
  command: async (context) => {
    const text = context.args.join(' ');
    await navigator.clipboard.writeText(text);
    context.stdout.write('Copied to clipboard\n');
    return 0;
  }
}

// 分享文件
{
  name: 'download',
  command: async (context) => {
    const filename = context.args[0];
    const blob = await getFileBlob(filename);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    return 0;
  }
}
```

### 操作 DOM

```typescript
// 页面操作命令
{
  name: 'focus-cell',
  command: async (context) => {
    const cellId = context.args[0];
    const cell = document.querySelector(`[data-cell-id="${cellId}"]`);
    if (cell) {
      (cell as HTMLElement).focus();
      return 0;
    }
    context.stderr.write(`Cell ${cellId} not found\n`);
    return 1;
  }
}
```

### 调用主线程 JavaScript 库

```typescript
// 使用已加载的Chart.js绘图
{
  name: 'chart',
  command: async (context) => {
    const data = JSON.parse(context.args.join(' '));
    // Chart.js 已在主线程加载
    const canvas = document.getElementById('chart-canvas') as HTMLCanvasElement;
    new Chart(canvas, {
      type: 'bar',
      data: data
    });
    return 0;
  }
}
```

### 与编辑器交互

在 JupyterLab 等集成场景中，可以通过外部命令与 notebook 编辑器交互：

```typescript
{
  name: 'run-cell',
  command: async (context) => {
    // 调用JupyterLab的API执行当前cell
    await app.commands.execute('notebook:run-cell');
    return 0;
  }
},
{
  name: 'insert-cell',
  command: async (context) => {
    const code = context.args.join(' ');
    await app.commands.execute('notebook:insert-cell-below');
    // 将代码插入新cell
    const notebook = app.shell.currentWidget.widget;
    notebook.activeCell.model.value.text = code;
    return 0;
  }
}
```

### CORS 代理支持

Demo 中提供了一个实用的外部命令示例：CORS（跨域资源共享）代理支持，用于 `git clone` 等需要跨域 fetch 的操作。通过环境变量配置 CORS 代理：

```typescript
// 当设置了CORS_PROXY环境变量时，fetch请求会走代理
const shell = new CockleShell({
  environment: {
    CORS_PROXY: 'https://cors-anywhere.example.com/'
  },
  externalCommands: [
    // ...
  ]
});
```

## 与其他命令类型对比

理解四种命令类型的区别有助于选择正确的扩展方式：

| 特性 | 内置命令 | WASM命令 | JS命令 | 外部命令 |
|------|----------|----------|--------|----------|
| 执行线程 | Worker | Worker | Worker | **主线程** |
| 加载方式 | 编译时包含 | 动态下载 | 动态下载 | 构造时注册 |
| 启动速度 | 即时 | 首次需下载 | 首次需下载 | 即时 |
| 文件IO | FS API | libc/FS API | FS API | 间接（通过消息） |
| DOM访问 | ❌ | ❌ | ❌ | **✅** |
| 浏览器API | 受限 | ❌ | ❌ | **✅** |
| 阻塞stdin | ✅ | ✅ | ✅ | ✅ |
| 实现语言 | TS | C/C++ | JS | JS |
| 适合场景 | Shell核心 | Unix工具 | 轻量脚本 | **应用集成** |

### 选择建议

- **核心 Shell 功能**（cd、export、help 等）→ 内置命令
- **Unix 工具**（ls、cat、grep、vim 等）→ WASM 命令（通过 emscripten-forge 编译）
- **简单的 Worker 内脚本** → JavaScript 命令（纯 JS 模块）
- **需要访问 DOM/浏览器API/应用状态** → **外部命令**

## 相关概念

- [03 - 命令系统](03-command-system.md)：CommandRegistry 和 CommandRunner 架构
- [08 - 内置命令详解](08-builtin-commands.md)：Worker 内的 TypeScript 命令
- [10 - WASM 与 JavaScript 命令](10-wasm-js-commands.md)：动态加载的 WASM/JS 命令
- [11 - Worker 通信机制](11-worker-communication.md)：Comlink/Coincident 如何桥接跨线程调用
- [07 - 缓冲 IO 系统](07-buffered-io.md)：外部命令的 stdin 如何同步读取
- [Shell API 参考](../references/shell-api.md)：Shell 构造函数完整选项
- [命令系统参考](../references/command-source.md)：CommandRegistry 和 Runner 完整接口
