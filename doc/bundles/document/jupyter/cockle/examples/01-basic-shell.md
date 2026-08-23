---
type: example
title: "01 - 创建基本 Shell"
description: 从零开始创建 Cockle Shell 实例，连接终端输出，发送命令并获取结果的完整可运行示例
tags: [example, basic, hello-world, shell-setup, integration]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: getting-started
    resource: /concepts/01-getting-started.md
    title: 快速开始
related_concepts: [/concepts/01-getting-started.md, /concepts/02-architecture-overview.md, /references/shell-api.md]
---

## 目标

本示例演示如何从零开始创建一个 Cockle Shell（浏览器 Shell）实例，完成以下核心任务：

1. 在 HTML 页面中准备终端容器和必要的跨域隔离配置
2. 注册 Service Worker（服务工作线程）以支持标准输入
3. 使用 `new Shell()` 构造函数创建 Shell 实例
4. 通过 `outputCallback`（输出回调）将 Shell 输出连接到终端显示
5. 监听 `commandStateChanged`（命令状态变化）信号
6. 等待 `ready`（就绪）Promise 并调用 `start()` 启动 Shell
7. 通过 `input()` 方法向 Shell 发送命令

## 完整代码

下面是一个完整的 HTML + TypeScript 示例，可以直接在支持 ES Module 的浏览器中运行：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <!-- COOP/COEP 头启用跨域隔离，支持 SharedArrayBuffer -->
  <meta http-equiv="Cross-Origin-Opener-Policy" content="same-origin">
  <meta http-equiv="Cross-Origin-Embedder-Policy" content="require-corp">
  <title>Cockle 基本 Shell 示例</title>
  <style>
    body { margin: 0; padding: 20px; background: #1e1e1e; font-family: monospace; }
    #terminal { width: 100%; height: 500px; background: #000; color: #ccc; padding: 10px; overflow-y: auto; white-space: pre-wrap; font-size: 14px; line-height: 1.4; }
    #status { color: #0f0; margin-bottom: 10px; font-size: 12px; }
  </style>
</head>
<body>
  <div id="status">正在初始化 Shell...</div>
  <div id="terminal"></div>

  <script type="module">
    import { Shell, ShellManager } from '@jupyterlite/cockle';

    const terminalEl = document.getElementById('terminal');
    const statusEl = document.getElementById('status');

    // 输出缓冲区，用于累积 Shell 输出
    let outputBuffer = '';

    /**
     * outputCallback: 接收 Shell 的所有输出（含 ANSI 转义序列）
     * 生产环境建议使用 xterm.js 等终端库来正确渲染 ANSI 颜色
     */
    function outputCallback(text) {
      // 简单处理：去除 ANSI 转义序列后显示
      const cleanText = text.replace(/\x1b\[[0-9;]*m/g, '');
      outputBuffer += cleanText;
      terminalEl.textContent = outputBuffer;
      terminalEl.scrollTop = terminalEl.scrollHeight;
    }

    async function initShell() {
      try {
        // 1. 创建 ShellManager 并注册 Service Worker
        const baseUrl = window.location.href;
        const shellManager = new ShellManager();
        const browsingContextId = await shellManager.installServiceWorker(baseUrl);

        statusEl.textContent = 'Service Worker 已注册，正在创建 Shell...';

        // 2. 构造 Shell 实例
        const shell = new Shell({
          baseUrl,                              // Service Worker 和 DriveFS 的基础 URL
          wasmBaseUrl: baseUrl,                 // WASM 包和 cockle-config.json 的基础 URL
          browsingContextId,                    // Service Worker stdin 必需
          shellManager,                         // Service Worker stdin 必需
          outputCallback,                       // 输出回调函数
          color: true,                          // 启用颜色输出（默认 true）
          mountpoint: '/drive',                 // 文件系统挂载点（默认 '/drive'）
          cwd: '/',                             // 初始工作目录
          aliases: {                            // 初始别名
            ll: 'ls -la',
            gs: 'git status'
          },
          environment: {                        // 初始环境变量
            MY_VAR: 'hello-cockle'
          }
        });

        // 3. 监听命令状态变化信号
        shell.commandStateChanged.connect((sender, args) => {
          const { commandId, state, name, exitCode } = args;
          switch (state) {
            case 'loading':
              statusEl.textContent = `[${commandId}] 正在加载命令: ${name}`;
              break;
            case 'running':
              statusEl.textContent = `[${commandId}] 命令执行中...`;
              break;
            case 'finished':
              statusEl.textContent = `[${commandId}] 命令完成，退出码: ${exitCode}`;
              break;
          }
        });

        // 4. 等待 Shell 就绪并启动
        await shell.ready;
        statusEl.textContent = 'Shell 就绪，正在启动...';
        await shell.start();

        // 5. 设置终端尺寸
        shell.setSize({ rows: 40, columns: 120 });

        statusEl.textContent = '✅ Shell 已启动！';

        // 6. 发送命令序列
        // Shell.input() 接受单个字符或字符串
        // 发送 "ls" 命令并回车（\r 或 \n 表示执行）
        await shell.input('ls\r');

        // 等待一会再发送下一个命令
        setTimeout(async () => {
          await shell.input('echo $MY_VAR\r');
        }, 500);

        setTimeout(async () => {
          await shell.input('pwd\r');
        }, 1000);

        setTimeout(async () => {
          await shell.input('help\r');
        }, 1500);

        // 获取最后一个命令的退出码
        setTimeout(async () => {
          const code = await shell.exitCode();
          console.log('最后一个命令的退出码:', code);
        }, 2500);

      } catch (err) {
        statusEl.textContent = '❌ 初始化失败: ' + err.message;
        console.error(err);
      }
    }

    initShell();
  </script>
</body>
</html>
```

## 代码解析

### HTML 准备

页面头部的两个 `<meta>` 标签设置了 COOP（Cross-Origin-Opener-Policy）和 COEP（Cross-Origin-Embedder-Policy）策略。这是启用跨域隔离（`crossOriginIsolated`）的关键。当页面处于跨域隔离状态时：

- `window.crossOriginIsolated === true`
- Cockle 自动选择 Coincident Worker（高性能模式）
- 支持 SharedArrayBuffer（共享数组缓冲区）实现同步 stdin
- 如果无法设置 meta 标签（如受服务器限制），Cockle 会降级到 Comlink Worker 模式，仅通过 Service Worker 处理 stdin

终端容器 `#terminal` 是一个简单的 `<div>`，用于显示 Shell 输出。生产环境推荐使用 [xterm.js](https://xtermjs.org/) 等专业终端库以获得完整的 ANSI 渲染支持。

### Shell 构造

`new Shell(options)` 接受 `IShell.IOptions` 接口的配置对象。必需参数包括：

| 参数 | 说明 |
|------|------|
| `baseUrl` | Service Worker 和虚拟文件系统请求的基础 URL |
| `wasmBaseUrl` | WASM 命令包和 `cockle-config.json` 所在目录的 URL |
| `outputCallback` | 接收 Shell 输出文本的回调函数 |
| `browsingContextId` | Service Worker stdin 的唯一标识，由 `ShellManager.installServiceWorker()` 获取 |
| `shellManager` | Shell 管理器实例，Service Worker stdin 所必需 |

可选参数包括 `color`（是否启用颜色）、`mountpoint`（挂载点）、`cwd`（初始目录）、`aliases`（别名映射）、`environment`（环境变量映射）、`externalCommands`（外部命令列表）等。

### 输出回调

`outputCallback(text: string)` 接收 Shell 产生的所有输出文本，包含 ANSI 转义序列（用于颜色和光标控制）。本示例使用简单的正则去除 ANSI 序列，实际项目中应使用 xterm.js 的 `term.write(text)` 方法来正确渲染。

### 启动流程

正确的启动顺序为：
1. `new Shell(options)` — 创建实例，此时开始初始化 Worker 和文件系统
2. `await shell.ready` — 等待初始化完成
3. `await shell.start()` — 启动 Shell 主循环
4. `shell.setSize({rows, columns})` — 设置终端尺寸
5. `shell.input(char)` — 开始发送输入

### 发送命令

`shell.input(char: string)` 接受字符串参数，可以是单个字符（如键盘输入）或完整字符串。回车键使用 `\r`（CR）或 `\n`（LF），Cockle 会自动处理换行符。发送完整命令时，命令文本加 `\r` 即可执行。

## 运行前提

1. **HTTP 服务器**：Cockle 必须通过 HTTP/HTTPS 协议访问（不能使用 `file://` 协议），因为 Service Worker 和 Worker 都需要 HTTP 上下文。可以使用任意静态服务器：

```bash
# 使用 Python
python -m http.server 8080

# 使用 Node.js (npx)
npx serve .

# 使用 Node.js http-server
npx http-server -p 8080 --cors
```

2. **跨域隔离配置**：推荐设置 COOP/COEP 头。如果使用 meta 标签方式无效（某些浏览器限制），需要在服务器端配置 HTTP 响应头。

3. **WASM 文件部署**：`wasmBaseUrl` 目录下需要部署 `cockle-config.json` 配置文件以及所需的 WASM 命令包（如 coreutils、grep 等）。这些文件位于 Cockle npm 包的 `wasm/` 目录中。

4. **Service Worker 文件**：`baseUrl` 目录下需要能访问到 Cockle 的 Service Worker 文件（`service-worker.js`）。

## 常见问题排查

**问题：Shell 初始化失败，提示 "Terminal needs either SharedArrayBuffer or ServiceWorker available"**

原因：页面既没有跨域隔离（SharedArrayBuffer 不可用），Service Worker 也未能成功注册。

解决方案：
- 确认 COOP/COEP 头已正确设置（在 DevTools → Application → Frames → top 中检查 `crossOriginIsolated` 是否为 `true`）
- 确认 Service Worker 文件存在且路径正确（在 DevTools → Application → Service Workers 中检查）
- 确认使用 HTTP 服务器访问，而非 `file://` 协议

**问题：命令发送后无输出**

原因：`outputCallback` 可能未正确绑定，或终端尺寸未设置导致命令无法执行。

解决方案：
- 确认 `outputCallback` 是函数且被正确传入构造参数
- 在 `start()` 之后立即调用 `setSize()` 设置有效行列数
- 使用 `commandStateChanged` 信号确认命令状态是否进入 `running`

**问题：WASM 命令加载失败（如 `ls: command not found`）**

原因：`wasmBaseUrl` 配置不正确或 WASM 文件未部署。

解决方案：
- 确认 `wasmBaseUrl` 指向包含 `cockle-config.json` 的目录
- 检查浏览器 Network 面板，确认 `.wasm` 和 `.data` 文件请求返回 200
- 确认服务器正确设置了 WASM 文件的 MIME 类型（`application/wasm`）

## 相关概念

- [快速开始](/concepts/01-getting-started.md)
- [架构概览](/concepts/02-architecture-overview.md)
- [Shell API 参考](/references/shell-api.md)
