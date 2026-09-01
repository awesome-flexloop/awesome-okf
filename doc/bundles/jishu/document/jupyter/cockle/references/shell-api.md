---
type: Reference
title: Shell API 参考
description: Cockle Shell 类的完整 API 参考，包括 IShell 接口、Shell 构造选项和公共方法
tags: [api, shell, reference, ishell, constructor]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: cockle-defs
    resource: /references/shell-api.md
    title: src/defs.ts IShell Interface
  - id: cockle-shell
    resource: /references/shell-api.md
    title: src/shell.ts Shell Class
  - id: cockle-base-shell
    resource: /references/shell-api.md
    title: src/base_shell.ts BaseShell Abstract Class
---

# Shell API 参考

本文档记录 Cockle 对外暴露的 Shell API，包括 `IShell` 接口、`Shell` 类和构造选项。

## IShell 接口

`IShell` 是 Cockle 对外的核心接口，定义在 `src/defs.ts`。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `commandStateChanged` | `ISignal<this, ICommandStateChangedArgs>` | 命令状态变化信号（loading→running→finished） |
| `ready` | `Promise<void>` | Shell 就绪 Promise，start() 前需等待 |
| `shellId` | `string` | Shell 唯一标识符，同一浏览器标签页内唯一 |
| `size` | `ISize` | 当前终端尺寸 `{rows, columns}` |
| `disposed` | `ISignal<this, void>` | Shell 销毁信号（继承自 IObservableDisposable） |
| `isDisposed` | `boolean` | Shell 是否已销毁 |

### 方法

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `start()` | 无 | `Promise<void>` | 启动 Shell，显示提示符，接受输入 |
| `input(char)` | `char: string` | `Promise<void>` | 向 Shell 输入字符（键盘或粘贴） |
| `exitCode()` | 无 | `Promise<number>` | 获取最后一条命令的退出码 |
| `setSize(size)` | `size: ISize` | `Promise<void>` | 设置终端尺寸（推荐方式） |
| `setSize(rows, columns)` | `rows: number, columns: number` | `Promise<void>` | 设置终端尺寸（兼容方式） |
| `themeChange(isDark?)` | `isDark?: boolean` | `void` | 通知主题变化，自动检测或指定暗色模式 |
| `dispose()` | 无 | `void` | 销毁 Shell，终止 Worker |

### ICommandStateChangedArgs

命令状态变化事件参数：

```typescript
interface ICommandStateChangedArgs {
  commandId: number;        // 命令唯一 ID
  state: 'loading' | 'running' | 'finished';
  name?: string;            // 命令真实名称（别名解析后），仅 loading 时设置
  args?: string[];          // 命令参数（别名/变量替换后），仅 loading 时设置
  exitCode?: number;        // 退出码，仅 finished 时设置
}
```

## Shell 构造选项 IOptions

```typescript
interface IOptions {
  // 必填项
  baseUrl: string;                    // Service Worker stdin/DriveFS 请求的基础 URL
  wasmBaseUrl: string;                // WASM/JS 命令包和 cockle-config.json 的基础 URL
  outputCallback: (output: string) => void;  // 终端输出回调

  // 可选项
  shellId?: string;                   // 自定义 Shell ID，默认 UUID
  color?: boolean;                    // 启用彩色输出和交互特性，默认 true
  mountpoint?: string;                // DriveFS 挂载点，默认 '/drive'
  cwd?: string;                       // 初始工作目录
  wasmUrlQueryParams?: (filename: string) => Record<string, string>;  // WASM 文件 URL 查询参数回调
  browsingContextId?: string;         // Service Worker stdin/drive 请求的唯一标识
  shellManager?: IShellManager;       // Shell 管理器（Service Worker stdin 必需）
  aliases?: Record<string, string>;   // 启动时设置的别名
  environment?: Record<string, string | undefined>;  // 启动时设置的环境变量
  externalCommands?: IExternalCommand.IOptions[];    // 外部命令注册
  initialDirectories?: string[];      // 初始目录（测试用）
  initialFiles?: Record<string, string>;  // 初始文件（测试用）
}
```

## IShellManager 接口

```typescript
interface IShellManager {
  handleStdin(request: IStdinRequest): Promise<IStdinReply>;
  registerShell(shellId: string, shell: IShell, handleStdin: IHandleStdin): void;
  shellIds(): string[];
}
```

## ISize 接口

```typescript
interface ISize {
  rows: number;
  columns: number;
}
```

## Shell 类

`Shell` 类定义在 `src/shell.ts`，继承 `BaseShell`，是唯一的具体实现类。

```typescript
class Shell extends BaseShell {
  constructor(readonly options: IShell.IOptions);
  protected initWorker(options: IShell.IOptions): Worker;
}
```

`initWorker` 根据 `workerType` 创建 `coincident.worker.js` 或 `comlink.worker.js`。

## Worker 类型自动选择

- 当 `crossOriginIsolated === true` 时，使用 Coincident Worker（支持 SAB 同步 stdin）
- 否则使用 Comlink Worker（仅支持 Service Worker stdin）
- 可通过重写 `useCoincidentWorker()` 改变选择逻辑

## 基础使用示例

```typescript
import { Shell } from '@jupyterlite/cockle';

const shell = new Shell({
  baseUrl: '/',
  wasmBaseUrl: '/cockle-assets/',
  outputCallback: (output: string) => {
    terminal.write(output);
  },
  browsingContextId: 'my-context',
  color: true,
  mountpoint: '/drive'
});

await shell.start();
await shell.input('ls -la\n');
```

## 相关概念

- [架构总览](../concepts/02-architecture-overview.md)
- [缓冲 IO 系统](../concepts/07-buffered-io.md)
- [Worker 通信](../concepts/11-worker-communication.md)
- [外部命令](../concepts/09-external-commands.md)
