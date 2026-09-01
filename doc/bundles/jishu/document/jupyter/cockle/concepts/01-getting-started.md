---
type: concept
title: "01 - 快速开始"
description: 安装 Cockle、创建第一个 Shell 实例、发送命令和接收输出的完整入门指南
tags: [getting-started, installation, setup, integration, hello-world]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: shell-api
    resource: /references/shell-api.md
    title: Shell API 参考
---

## 安装

Cockle 以 npm 包的形式发布，包名为 `@jupyterlite/cockle`。使用 npm 或其他包管理器安装即可：

```bash
npm install @jupyterlite/cockle
```

安装后，可以通过 ES Module 方式导入：

```typescript
import { Shell } from '@jupyterlite/cockle';
```

Cockle 也支持通过 `<script type="module">` 标签在浏览器中直接导入（需使用打包工具或 CDN）。包内导出了 `Shell` 类（主要入口）、`IOptions` 接口、以及若干工具类型。

## 前置条件

Cockle 运行在浏览器环境中，有几个关键的环境要求需要注意：

### 跨域隔离（推荐配置）

为了获得最佳性能和完整功能（特别是同步 stdin），推荐为页面设置跨域隔离头（Cross-Origin Isolation）。这需要在服务器响应中添加两个 HTTP 头：

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

设置后，`crossOriginIsolated` 属性为 `true`，Cockle 会自动选择 Coincident Worker 模式，该模式支持 SharedArrayBuffer（SAB）+ Service Worker 双模式的同步标准输入 [F-142][F-007]。

### Service Worker（备选方案）

如果无法设置跨域隔离头，Cockle 会降级到 Comlink Worker 模式 [F-006]。Comlink 模式仅支持 Service Worker 方式的 stdin [F-007]，需要注册 Cockle 提供的 Service Worker：

```javascript
// 注册 Service Worker（Comlink 模式下 stdin 必需）
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/service-worker.js');
}
```

### 环境检测逻辑

Cockle 初始化时会检测 SharedArrayBuffer 和 Service Worker 的可用性 [F-143-F146]。如果两者都不可用（既没有跨域隔离也没有 Service Worker），初始化会抛出错误，因为 stdin 无法工作。

### 静态资源部署

Cockle 运行时需要加载 WASM 命令包和配置文件（`cockle-config.json`），这些文件需要部署在 Web 服务器上，通过 `wasmBaseUrl` 指定路径。确保以下资源可以被浏览器访问：

- `cockle-config.json`（WASM 包配置清单）
- `cockle_fs.wasm`（文件系统 WASM 模块）
- 各 WASM 命令的 `.wasm` 和 `.js` 文件（按需加载）
- Worker 文件：`coincident.worker.js` 和 `comlink.worker.js`

## 创建第一个 Shell

以下是一个完整的最小示例，展示如何创建 Shell 实例、连接终端 UI 并执行命令：

```typescript
import { Shell } from '@jupyterlite/cockle';

// 1. 创建 Shell 实例
const shell = new Shell({
  // 必填项
  baseUrl: '/',                          // Service Worker/DriveFS 的基础 URL
  wasmBaseUrl: '/cockle-assets/',        // WASM 包和配置文件的 URL
  outputCallback: (output: string) => {  // 输出回调——将 Shell 输出渲染到终端
    console.log('[Shell Output]', output);
    // 在真实场景中，这里会调用 xterm.js 的 terminal.write(output)
  },

  // 可选项
  browsingContextId: 'my-terminal-001', // Service Worker 请求的上下文标识
  color: true,                           // 启用彩色输出
  mountpoint: '/drive',                  // DriveFS 挂载点
  cwd: '/home/user',                     // 初始工作目录
});

// 2. 监听命令状态变化
shell.commandStateChanged.connect((_, args) => {
  switch (args.state) {
    case 'loading':
      console.log(`命令加载中: ${args.name}`);
      break;
    case 'running':
      console.log('命令运行中...');
      break;
    case 'finished':
      console.log(`命令结束，退出码: ${args.exitCode}`);
      break;
  }
});

// 3. 启动 Shell（异步，等待就绪）
await shell.start();
console.log('Shell 已就绪！');

// 4. 发送命令（注意末尾的换行符）
await shell.input('echo "Hello, Cockle!"\n');
```

运行后，你将在控制台看到类似以下的输出：

```
Shell 已就绪！
[Shell Output] /home/user $ echo "Hello, Cockle!"
[Shell Output] Hello, Cockle!
[Shell Output] /home/user $
命令结束，退出码: 0
```

### 输出回调详解

`outputCallback` 是 Shell 与 UI 层通信的唯一桥梁。每当 Shell 有输出需要显示（包括提示符、命令回显、命令输出、ANSI 转义序列等），都会调用此回调。回调接收一个 `string` 参数，该字符串可能包含：

- 普通文本（命令输出内容）
- ANSI 转义序列（颜色、光标移动、清屏等）
- 提示符（如 `$ `、`/home/user $ `）
- 用户输入的回显

在真实应用中，通常将输出直接传递给 xterm.js 等终端模拟器进行渲染：

```typescript
import { Terminal } from 'xterm';

const term = new Terminal();
term.open(document.getElementById('terminal'));

const shell = new Shell({
  baseUrl: '/',
  wasmBaseUrl: '/cockle-assets/',
  outputCallback: (data: string) => term.write(data),
});
```

### 键盘输入转发

Shell 的 `input()` 方法接受单个字符或字符串，用于向 Shell 发送键盘输入。终端 UI 需要将用户按键事件转发给 Shell：

```typescript
term.onData((data: string) => {
  // xterm.js 将特殊按键编码为转义序列，直接转发即可
  shell.input(data);
});
```

对于回车键，需要发送换行符 `\n`；对于 Ctrl 组合键（如 Ctrl+C、Ctrl+D），xterm.js 会自动编码为对应的控制字符。

## 基本交互

### 发送命令

命令通过 `input()` 方法发送，注意命令末尾必须加上换行符 `\n` 才会执行：

```typescript
// 执行单条命令
await shell.input('ls -la\n');

// 执行多条命令（用 ; 分隔）
await shell.input('cd /home; pwd; ls\n');

// 使用管道
await shell.input('ls | grep test\n');

// 使用重定向
await shell.input('echo "hello" > test.txt\n');
```

### 处理命令状态变化

`commandStateChanged` 信号在命令生命周期中会触发三次 [F-101]：

```typescript
interface ICommandStateChangedArgs {
  commandId: number;        // 命令唯一 ID（自增）
  state: 'loading' | 'running' | 'finished';
  name?: string;            // 命令真实名称（别名展开后），仅 loading 时设置
  args?: string[];          // 命令参数（变量替换后），仅 loading 时设置
  exitCode?: number;        // 退出码，仅 finished 时设置
}
```

典型使用场景：显示"命令执行中"的加载指示器，或在命令完成后执行后续操作。

### 获取退出码

`exitCode()` 方法返回最后一条命令的退出码：

```typescript
await shell.input('ls /nonexistent\n');
const code = await shell.exitCode();
console.log(code);  // 非 0 表示错误
```

退出码遵循 Unix 惯例 [F-215]：

| 退出码 | 常量名 | 含义 |
|--------|--------|------|
| 0 | `SUCCESS` | 成功 |
| 1 | `GENERAL_ERROR` | 一般错误 |
| 2 | `IMPROPER_USE` | 用法错误 |
| 126 | `CANNOT_RUN` | 命令无法执行（权限问题等） |
| 127 | `NOT_FOUND` | 命令未找到 |

### 终端尺寸设置

使用 `setSize()` 方法通知 Shell 当前终端尺寸，这对于全屏命令（如 `vim`、`less`）正确渲染至关重要：

```typescript
// 方式一：传入 ISize 对象
shell.setSize({ rows: 24, columns: 80 });

// 方式二：传入行列数（兼容方式）
shell.setSize(24, 80);
```

### 主题切换

当页面主题切换时，调用 `themeChange()` 通知 Shell：

```typescript
// 自动检测当前主题
shell.themeChange();

// 显式指定暗色模式
shell.themeChange(true);

// 显式指定亮色模式
shell.themeChange(false);
```

## 配置选项说明

### 必填选项

创建 `Shell` 实例时必须提供以下三个选项 [F-110]：

| 选项 | 类型 | 说明 |
|------|------|------|
| `baseUrl` | `string` | Service Worker stdin 和 DriveFS 请求的基础 URL，通常设为页面根路径 `/` |
| `wasmBaseUrl` | `string` | WASM 命令包和 `cockle-config.json` 所在的 URL 路径，部署时需将 Cockle 资源放在此路径下 |
| `outputCallback` | `(output: string) => void` | 终端输出回调函数，Shell 所有输出都通过此回调传递给 UI |

### 常用可选选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `shellId` | `string` | 自动生成 UUID | Shell 唯一标识符，多 Shell 实例时需区分 |
| `color` | `boolean` | `true` | 是否启用彩色输出和交互特性 |
| `mountpoint` | `string` | `'/drive'` | DriveFS（宿主机文件系统）的挂载点 |
| `cwd` | `string` | 虚拟 FS 内 | 初始工作目录 |
| `browsingContextId` | `string` | - | Service Worker 请求的唯一标识，多标签页时推荐设置 |
| `aliases` | `Record<string, string>` | - | 启动时预设置的命令别名 |
| `environment` | `Record<string, string \| undefined>` | - | 启动时预设置的环境变量 |
| `externalCommands` | `IExternalCommand.IOptions[]` | - | 注册外部命令（在主线程执行的命令） |

### 设置初始别名和环境变量

```typescript
const shell = new Shell({
  baseUrl: '/',
  wasmBaseUrl: '/cockle-assets/',
  outputCallback: (data) => term.write(data),
  aliases: {
    ll: 'ls -la',
    gs: 'git status',
  },
  environment: {
    MY_VAR: 'hello',
    EDITOR: 'vim',
  },
});
```

启动后，直接输入 `ll` 即可执行 `ls -la`，`echo $MY_VAR` 输出 `hello`。

### 注册外部命令

外部命令（External Command）运行在主线程中，可以访问 DOM 和浏览器 API：

```typescript
const shell = new Shell({
  baseUrl: '/',
  wasmBaseUrl: '/cockle-assets/',
  outputCallback: (data) => term.write(data),
  externalCommands: [
    {
      name: 'open',
      command: async (context) => {
        const url = context.args[0];
        window.open(url, '_blank');
        return 0;  // 返回退出码
      },
    },
  ],
});
```

在 Shell 中执行 `open https://example.com` 会在新标签页打开 URL。

## 常见问题

### Worker 文件加载失败（404）

**症状**：Shell 创建时报错，提示 Worker 文件无法加载。

**原因**：`coincident.worker.js` 或 `comlink.worker.js` 文件路径不正确。Cockle 根据 `baseUrl` 加载 Worker 文件。

**解决方案**：确保打包工具将 Worker 文件输出到正确路径，或配置 `baseUrl` 指向包含 Worker 文件的目录。`initWorker` 方法会根据 Worker 类型选择加载 `coincident.worker.js` 或 `comlink.worker.js` [F-122-F124]。

### stdin 不可用错误

**症状**：Shell 启动时报错，提示 SharedArrayBuffer 和 Service Worker 均不可用。

**原因**：页面既没有设置跨域隔离头（COOP/COEP），也没有注册 Service Worker [F-143-F146]。

**解决方案**：二选一：
1. 推荐：在服务器上配置 COOP/COEP 头，启用跨域隔离
2. 备选：注册 Cockle 的 Service Worker 文件

### WASM 包 404 错误

**症状**：执行 WASM 命令（如 `ls`、`cat`）时命令未找到或资源加载失败。

**原因**：`wasmBaseUrl` 路径配置不正确，或 WASM 资源文件未部署到该路径。

**解决方案**：
1. 确认 `wasmBaseUrl` 以 `/` 结尾
2. 确认 `cockle-config.json` 文件位于 `wasmBaseUrl` 路径下
3. 确认 WASM 命令文件（如 `coreutils.wasm`、`git2cpp.wasm` 等）已部署

### 彩色输出不显示

**症状**：输出中出现 `[32m` 等乱码而非颜色。

**原因**：终端模拟器未解析 ANSI 转义序列，或 `color` 选项设为 `false`。

**解决方案**：
1. 确认 `color: true`（默认值）
2. 使用支持 ANSI 转义序列的终端组件（如 xterm.js）

### 外部命令无响应

**症状**：注册的外部命令执行后没有输出或 Shell 卡住。

**原因**：外部命令的 `command` 函数没有正确调用 `context` 上的 IO 方法或没有返回退出码。

**解决方案**：外部命令函数需要通过 context 的 stdin/stdout/stderr 进行 IO 操作，并返回一个 number（退出码）或 `Promise<number>`。External Command 执行时，Cockle 会创建 ExternalEnvironment、ExternalInput、ExternalOutput、ExternalTermios 并传入命令函数 [F-148]。

## 相关概念

- [Cockle 简介](00-introduction.md)
- [架构总览](02-architecture-overview.md)
- [命令系统](03-command-system.md)
- [IO 系统](05-io-system.md)
