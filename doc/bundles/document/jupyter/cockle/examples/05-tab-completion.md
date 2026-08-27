---
type: example
title: "05 - Tab 补全与交互增强"
description: 实现自定义 Tab 补全、监听命令状态变化、终端尺寸同步和主题切换
tags: [example, tab-completion, interactive, resize, theme, signals]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: io-system
    resource: /concepts/05-io-system.md
    title: IO系统
  - id: shell-api
    resource: /references/shell-api.md
    title: Shell API参考
related_concepts: [/concepts/05-io-system.md, /concepts/09-external-commands.md, /references/shell-api.md]
---

## 目标

本示例演示 Cockle Shell 的交互增强功能，包括：

1. **Tab 补全机制**：理解内置命令和文件名的 Tab 补全如何工作
2. **自定义 Tab 补全**：为外部命令和 JS 命令实现参数级 Tab 补全
3. **命令状态监听**：通过 `commandStateChanged` 信号实时感知命令执行状态
4. **终端尺寸同步**：监听窗口 resize 事件并同步到 Shell
5. **主题切换**：深色/浅色模式切换及 ANSI 颜色适配
6. **完整终端集成**：与 xterm.js 终端库的完整集成代码框架

## Tab 补全机制

Cockle 的 Tab 补全在输入处理过程中自动触发。当用户按下 Tab 键（`\t` 字符）时，Shell 的输入处理器会调用当前命令行上下文中注册的补全回调。

### 内置补全行为

Cockle 默认为以下场景提供 Tab 补全：

1. **命令名补全**：当光标位于命令位置（第一个词）时，按 Tab 会补全匹配的内置命令、外部命令、WASM 命令和 JS 命令名。
2. **文件名补全**：当光标位于参数位置时，按 Tab 会尝试补全文件系统中的文件名和目录名。
3. **内置命令参数补全**：部分内置命令（如 `cockle-config`）为其子命令和参数提供了专门的补全逻辑。

在使用 xterm.js 等终端库时，Tab 键的处理方式是将 Tab 字符（`\t`，ASCII 9）发送给 Shell，与发送其他字符一样：

```typescript
// xterm.js 的 onData 回调中，所有输入（包括 Tab、方向键）都以字符串形式发送
term.onData((data: string) => {
  shell.input(data); // data 可能是普通字符、\t(Tab)、\r(Enter)、\x1b[A(↑)等
});
```

方向键上/下（`\x1b[A`/`\x1b[B`）会触发历史记录浏览（history scroll），Shell 内部通过 `History.scrollCurrent(down: boolean)` 方法实现：
- `\x1b[A`（上箭头）：`scrollCurrent(false)`，浏览上一条历史命令
- `\x1b[B`（下箭头）：`scrollCurrent(true)`，浏览下一条历史命令

## 外部命令的自定义 Tab 补全

外部命令（External Command）通过在注册时提供 `tabComplete` 回调来自定义参数补全。补全回调接收 `IExternalTabCompleteContext`，返回 `IExternalTabCompleteResult`。

### 接口说明

```typescript
interface IExternalTabCompleteContext {
  name: string;      // 命令名称
  args: string[];    // 当前命令参数数组，最后一个元素是正在输入的部分（可能为空字符串）
  shellId: string;   // Shell 唯一标识
}

interface ITabCompleteResult {
  possibles?: string[];  // 候选补全列表
  pathType?: PathType;   // 路径类型提示（Any/Directory/File），可选
}

enum PathType {
  Any = 0,       // 任意路径
  Directory = 1, // 仅目录
  File = 2       // 仅文件
}
```

### 示例：为文件操作命令添加 Tab 补全

```typescript
import type {
  IExternalRunContext,
  IExternalTabCompleteContext,
  IExternalTabCompleteResult
} from '@jupyterlite/cockle';
import { ExitCode } from '@jupyterlite/cockle';

// 模拟的文件类型数据库
const CONTENT_TYPES = ['text/plain', 'text/html', 'application/json', 'image/png', 'image/jpeg'];
const OPERATIONS = ['list', 'read', 'write', 'delete', 'info'];

/**
 * myfs 命令：模拟文件操作，演示多级 Tab 补全
 * 用法：myfs <operation> [content-type]
 */
async function myfsCommand(context: IExternalRunContext): Promise<number> {
  const { args, stdout, stderr } = context;

  if (args.length === 0) {
    stdout.write('用法: myfs <operation> [content-type]\n');
    stdout.write('操作: ' + OPERATIONS.join(', ') + '\n');
    return ExitCode.GENERAL_ERROR;
  }

  const op = args[0];
  if (!OPERATIONS.includes(op)) {
    stderr.write(`未知操作: ${op}\n`);
    return ExitCode.GENERAL_ERROR;
  }

  stdout.write(`执行操作: ${op}\n`);
  if (args.length > 1) {
    stdout.write(`内容类型: ${args[1]}\n`);
  }

  return ExitCode.SUCCESS;
}

/**
 * myfs 命令的 Tab 补全回调
 * 第一级参数补全操作名，第二级参数补全内容类型
 */
async function myfsTabComplete(
  context: IExternalTabCompleteContext
): Promise<IExternalTabCompleteResult> {
  const { args } = context;

  // args[0] 是命令名后的第一个参数（操作名）
  if (args.length <= 1) {
    // 正在输入第一个参数（操作名）
    const partial = args[0] ?? '';
    return {
      possibles: OPERATIONS.filter(op => op.startsWith(partial))
    };
  }

  // args[1] 是第二个参数（内容类型）
  if (args.length === 2) {
    const partial = args[1] ?? '';
    return {
      possibles: CONTENT_TYPES.filter(ct => ct.startsWith(partial))
    };
  }

  // 没有更多补全
  return {};
}
```

### 注册带补全的外部命令

```typescript
const shell = new Shell({
  baseUrl,
  wasmBaseUrl: baseUrl,
  outputCallback: (text) => term.write(text),
  browsingContextId,
  shellManager,
  externalCommands: [
    { name: 'myfs', command: myfsCommand, tabComplete: myfsTabComplete }
  ]
});
```

用户在 Shell 中的交互体验：
```
js-shell: > myfs <Tab>
delete  info    list    read    write
js-shell: > myfs re<Tab>
js-shell: > myfs read <Tab>
application/json  image/jpeg      image/png       text/html       text/plain
js-shell: > myfs read text/<Tab>
text/html   text/plain
```

## 监听命令状态

`commandStateChanged` 信号（Signal）在命令生命周期的各个阶段触发，可用于显示加载指示器、命令耗时统计等功能。

### 状态类型

命令状态经历三个阶段：`loading` → `running` → `finished`。

| 状态 | 含义 | 可用字段 |
|------|------|----------|
| `loading` | 命令正在加载（WASM 模块下载、解析等） | `commandId`, `state`, `name`, `args` |
| `running` | 命令正在执行 | `commandId`, `state` |
| `finished` | 命令执行完成 | `commandId`, `state`, `exitCode` |

### 示例：命令执行指示器

```typescript
import type { IShell } from '@jupyterlite/cockle';

class CommandIndicator {
  private indicatorEl: HTMLElement;
  private startTimeMap = new Map<number, number>();

  constructor(indicatorId: string) {
    this.indicatorEl = document.getElementById(indicatorId)!;
  }

  attach(shell: IShell) {
    shell.commandStateChanged.connect((_, args) => {
      this.onStateChanged(args);
    });
  }

  private onStateChanged(args: IShell.ICommandStateChangedArgs) {
    const { commandId, state, name, exitCode } = args;

    switch (state) {
      case 'loading':
        // 命令开始加载
        this.startTimeMap.set(commandId, Date.now());
        this.indicatorEl.textContent = `⏳ 加载中: ${name}...`;
        this.indicatorEl.style.color = '#ffa500';
        break;

      case 'running':
        // 命令开始执行
        this.indicatorEl.textContent = `▶ 执行中... (命令 #${commandId})`;
        this.indicatorEl.style.color = '#4af';
        break;

      case 'finished': {
        // 命令完成
        const startTime = this.startTimeMap.get(commandId);
        const elapsed = startTime ? Date.now() - startTime : 0;
        this.startTimeMap.delete(commandId);

        if (exitCode === 0) {
          this.indicatorEl.textContent = `✅ 完成 (${elapsed}ms)`;
          this.indicatorEl.style.color = '#4f4';
        } else {
          this.indicatorEl.textContent = `❌ 退出码 ${exitCode} (${elapsed}ms)`;
          this.indicatorEl.style.color = '#f44';
        }

        // 3 秒后清除状态
        setTimeout(() => {
          if (this.indicatorEl.textContent.includes(`#${commandId}`) ||
              this.indicatorEl.textContent.includes('完成') ||
              this.indicatorEl.textContent.includes('退出码')) {
            this.indicatorEl.textContent = '就绪';
            this.indicatorEl.style.color = '#888';
          }
        }, 3000);
        break;
      }
    }
  }
}

// 使用方式
const indicator = new CommandIndicator('status-indicator');
indicator.attach(shell);
```

HTML 中添加状态指示器元素：
```html
<div id="status-indicator" style="color: #888; font-size: 12px; padding: 4px 8px;">就绪</div>
```

## 终端尺寸同步

正确设置终端尺寸对于命令输出格式化（如表格布局、分页器）至关重要。Cockle 使用 `shell.setSize({rows, columns})` 方法设置尺寸。

### 监听窗口和容器尺寸变化

使用 `ResizeObserver` 监听终端容器尺寸变化，结合 xterm.js 的 FitAddon 自动计算行列数：

```typescript
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import type { IShell, ISize } from '@jupyterlite/cockle';

class TerminalResizeHandler {
  private fitAddon: FitAddon;

  constructor(
    private term: Terminal,
    private shell: IShell,
    private container: HTMLElement
  ) {
    this.fitAddon = new FitAddon();
    this.term.loadAddon(this.fitAddon);
  }

  attach() {
    // 监听容器尺寸变化
    const resizeObserver = new ResizeObserver(() => {
      this.fitAndSync();
    });
    resizeObserver.observe(this.container);

    // 监听窗口 resize 事件（备用）
    window.addEventListener('resize', () => {
      this.fitAndSync();
    });

    // xterm.js 自身的 onResize 事件
    this.term.onResize((size: { rows: number; cols: number }) => {
      this.syncToShell(size);
    });

    // 初始同步
    setTimeout(() => this.fitAndSync(), 100);
  }

  private fitAndSync() {
    try {
      this.fitAddon.fit();
      const size = { rows: this.term.rows, columns: this.term.cols };
      this.syncToShell(size);
    } catch (e) {
      // fitAddon 在容器不可见时可能抛错，忽略即可
      console.warn('FitAddon fit failed:', e);
    }
  }

  private syncToShell(size: { rows: number; cols: number } | ISize) {
    const rows = 'rows' in size ? size.rows : size.rows;
    const cols = 'cols' in size ? size.cols : (size as ISize).columns;
    this.shell.setSize({ rows, columns: cols });
  }
}

// 使用方式
const term = new Terminal({ fontSize: 14 });
const container = document.getElementById('terminal-container')!;
term.open(container);

const resizeHandler = new TerminalResizeHandler(term, shell, container);
resizeHandler.attach();
```

注意事项：
- 在 `shell.start()` **之后**再调用 `setSize()`，确保 Shell 已就绪
- 初始尺寸同步建议延迟 100ms 左右，等 DOM 布局稳定后再 fit
- FitAddon 需要容器有明确的高度才能正确计算行列数

## 主题切换

Cockle 支持深色/浅色主题切换，通过 `shell.themeChange(isDark?)` 方法通知 Shell 当前主题模式。这会影响 ANSI 颜色渲染和 `COCKLE_DARK_MODE` 环境变量。

### themeChange 方法

```typescript
// 通知 Shell 切换到深色模式
shell.themeChange(true);

// 通知 Shell 切换到浅色模式
shell.themeChange(false);

// 不传入参数，Shell 会通过检测终端背景色自动判断
shell.themeChange();
```

### 完整主题切换示例

```typescript
class ThemeManager {
  private isDark = true;

  constructor(
    private term: Terminal,
    private shell: IShell
  ) {}

  toggle() {
    this.isDark = !this.isDark;
    this.apply();
  }

  setDark(dark: boolean) {
    this.isDark = dark;
    this.apply();
  }

  private apply() {
    // 1. 更新 xterm.js 主题
    const theme = this.isDark
      ? {
          foreground: '#cccccc',
          background: '#1e1e1e',
          cursor: '#ffffff',
          black: '#000000',
          red: '#e06c75',
          green: '#98c379',
          yellow: '#d19a66',
          blue: '#61afef',
          magenta: '#c678dd',
          cyan: '#56b6c2',
          white: '#ffffff',
          brightBlack: '#5c6370',
          brightRed: '#e06c75',
          brightGreen: '#98c379',
          brightYellow: '#d19a66',
          brightBlue: '#61afef',
          brightMagenta: '#c678dd',
          brightCyan: '#56b6c2',
          brightWhite: '#ffffff'
        }
      : {
          foreground: '#333333',
          background: '#ffffff',
          cursor: '#000000',
          black: '#000000',
          red: '#d32f2f',
          green: '#388e3c',
          yellow: '#f9a825',
          blue: '#1976d2',
          magenta: '#7b1fa2',
          cyan: '#0097a7',
          white: '#ffffff',
          brightBlack: '#808080',
          brightRed: '#d32f2f',
          brightGreen: '#388e3c',
          brightYellow: '#f9a825',
          brightBlue: '#1976d2',
          brightMagenta: '#7b1fa2',
          brightCyan: '#0097a7',
          brightWhite: '#c0c0c0'
        };

    this.term.options.theme = theme;

    // 2. 通知 Shell 主题变化（影响 ANSI 颜色和 COCKLE_DARK_MODE）
    this.shell.themeChange(this.isDark);

    // 3. 更新页面背景色
    document.body.style.background = this.isDark ? '#1e1e1e' : '#ffffff';
    document.body.style.color = this.isDark ? '#cccccc' : '#333333';
  }
}

// 使用方式
const themeManager = new ThemeManager(term, shell);

// 绑定主题切换按钮
document.getElementById('theme-toggle')?.addEventListener('click', () => {
  themeManager.toggle();
});

// 检测系统深色模式偏好
const darkModeMedia = window.matchMedia('(prefers-color-scheme: dark)');
themeManager.setDark(darkModeMedia.matches);
darkModeMedia.addEventListener('change', (e) => {
  themeManager.setDark(e.matches);
});
```

当调用 `themeChange(true)` 后，Shell 会设置环境变量 `COCKLE_DARK_MODE=1`，命令可以通过检查此变量来决定使用深色还是浅色配色。

## 完整终端集成示例

下面是一个将 xterm.js、Cockle Shell、尺寸同步、状态指示和主题切换整合在一起的完整 HTML 示例：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Cross-Origin-Opener-Policy" content="same-origin">
  <meta http-equiv="Cross-Origin-Embedder-Policy" content="require-corp">
  <title>Cockle 终端完整集成示例</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@xterm/xterm@5.3.0/css/xterm.min.css">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #1e1e1e;
      color: #ccc;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      padding: 16px;
      transition: background 0.3s, color 0.3s;
    }
    body.light { background: #f5f5f5; color: #333; }
    .toolbar {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
      padding: 8px 12px;
      background: #2d2d2d;
      border-radius: 6px;
    }
    body.light .toolbar { background: #e0e0e0; }
    #status-indicator { font-size: 12px; color: #888; flex: 1; }
    #status-indicator.running { color: #4af; }
    #status-indicator.success { color: #4f4; }
    #status-indicator.error { color: #f44; }
    #theme-toggle {
      padding: 4px 12px;
      border: 1px solid #555;
      border-radius: 4px;
      background: #3d3d3d;
      color: #ccc;
      cursor: pointer;
      font-size: 12px;
    }
    body.light #theme-toggle {
      border-color: #aaa; background: #fff; color: #333;
    }
    #terminal-container {
      width: 100%;
      height: calc(100vh - 100px);
      border-radius: 6px;
      overflow: hidden;
      border: 1px solid #444;
    }
    body.light #terminal-container { border-color: #ccc; }
    .xterm { padding: 8px; height: 100% !important; }
    .xterm-viewport { overflow-y: auto !important; }
  </style>
</head>
<body class="dark">
  <div class="toolbar">
    <span style="font-weight: bold;">🐚 Cockle Terminal</span>
    <span id="status-indicator">初始化中...</span>
    <button id="theme-toggle">🌙 深色模式</button>
  </div>
  <div id="terminal-container"></div>

  <script type="module">
    import { Shell, ShellManager, ExitCode } from '@jupyterlite/cockle';
    import { Terminal } from '@xterm/xterm';
    import { FitAddon } from '@xterm/addon-fit';

    // ============ 初始化终端 ============
    const term = new Terminal({
      fontSize: 14,
      fontFamily: '"Cascadia Code", "Fira Code", "JetBrains Mono", monospace',
      cursorBlink: true,
      theme: {
        foreground: '#cccccc',
        background: '#1e1e1e',
        cursor: '#ffffff'
      },
      allowProposedApi: true
    });

    const container = document.getElementById('terminal-container');
    term.open(container);
    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);

    const statusEl = document.getElementById('status-indicator');
    const themeBtn = document.getElementById('theme-toggle');

    // ============ 初始化 Shell ============
    let isDark = true;
    let shell;

    async function init() {
      try {
        const baseUrl = window.location.href;
        const shellManager = new ShellManager();
        const browsingContextId = await shellManager.installServiceWorker(baseUrl);

        // 自定义外部命令：演示 Tab 补全
        const COMMANDS = ['open', 'save', 'close', 'refresh'];
        const TARGETS = ['file', 'folder', 'tab', 'window'];

        shell = new Shell({
          baseUrl,
          wasmBaseUrl: baseUrl,
          browsingContextId,
          shellManager,
          outputCallback: (text) => term.write(text),
          color: true,
          externalCommands: [
            {
              name: 'cmd',
              command: async (ctx) => {
                const { args, stdout } = ctx;
                if (args.length === 0) {
                  stdout.write('用法: cmd <action> [target]\n');
                  return ExitCode.GENERAL_ERROR;
                }
                stdout.write(`执行: ${args.join(' ')}\n`);
                return ExitCode.SUCCESS;
              },
              tabComplete: async (ctx) => {
                const { args } = ctx;
                if (args.length <= 1) {
                  const p = args[0] ?? '';
                  return { possibles: COMMANDS.filter(c => c.startsWith(p)) };
                }
                if (args.length === 2) {
                  const p = args[1] ?? '';
                  return { possibles: TARGETS.filter(t => t.startsWith(p)) };
                }
                return {};
              }
            }
          ]
        });

        // 命令状态监听
        const startTimes = new Map();
        shell.commandStateChanged.connect((_, args) => {
          const { commandId, state, name, exitCode } = args;
          switch (state) {
            case 'loading':
              startTimes.set(commandId, Date.now());
              statusEl.textContent = `⏳ ${name}...`;
              statusEl.className = 'running';
              break;
            case 'running':
              statusEl.textContent = `▶ 执行中 (#${commandId})`;
              statusEl.className = 'running';
              break;
            case 'finished': {
              const t = startTimes.get(commandId);
              const ms = t ? Date.now() - t : 0;
              startTimes.delete(commandId);
              if (exitCode === 0) {
                statusEl.textContent = `✅ 完成 (${ms}ms)`;
                statusEl.className = 'success';
              } else {
                statusEl.textContent = `❌ 退出码 ${exitCode} (${ms}ms)`;
                statusEl.className = 'error';
              }
              setTimeout(() => {
                statusEl.textContent = '就绪';
                statusEl.className = '';
              }, 2000);
              break;
            }
          }
        });

        // 连接终端输入到 Shell
        term.onData((data) => shell.input(data));

        // 启动 Shell
        await shell.ready;
        await shell.start();

        // 尺寸同步
        function fit() {
          try {
            fitAddon.fit();
            shell.setSize({ rows: term.rows, columns: term.cols });
          } catch (e) { /* ignore */ }
        }
        const ro = new ResizeObserver(fit);
        ro.observe(container);
        window.addEventListener('resize', fit);
        setTimeout(fit, 200);

        // 主题切换
        themeBtn.addEventListener('click', () => {
          isDark = !isDark;
          term.options.theme = isDark
            ? { foreground: '#ccc', background: '#1e1e1e', cursor: '#fff' }
            : { foreground: '#333', background: '#fff', cursor: '#000' };
          shell.themeChange(isDark);
          document.body.className = isDark ? 'dark' : 'light';
          themeBtn.textContent = isDark ? '🌙 深色模式' : '☀️ 浅色模式';
        });

        // 检测系统主题
        const dm = window.matchMedia('(prefers-color-scheme: dark)');
        if (!dm.matches) themeBtn.click();

        // 欢迎信息
        term.writeln('\x1b[1;36m欢迎使用 Cockle Terminal!\x1b[0m');
        term.writeln('输入 \x1b[1mhelp\x1b[0m 查看可用命令，输入 \x1b[1mcmd <Tab>\x1b[0m 体验自定义补全\n');

      } catch (err) {
        statusEl.textContent = '❌ 初始化失败: ' + err.message;
        statusEl.className = 'error';
        console.error(err);
      }
    }

    init();
  </script>
</body>
</html>
```

### 集成要点总结

1. **xterm.js 连接**：通过 `term.onData()` 将所有键盘输入转发给 `shell.input()`，包括特殊字符（Tab、方向键、Ctrl+C 等）。输出通过 `outputCallback` 回调到 `term.write(text)`。
2. **Service Worker 注册**：使用 `ShellManager.installServiceWorker(baseUrl)` 获取 `browsingContextId`，这是 Service Worker stdin 正常工作的前提。
3. **尺寸同步**：使用 `ResizeObserver` + `FitAddon` 自动适配容器尺寸，在 Shell 启动后调用 `setSize()`。
4. **状态指示**：监听 `commandStateChanged` 信号，在工具栏显示加载/运行/完成状态和耗时。
5. **主题切换**：通过 `shell.themeChange(isDark)` 通知 Shell 切换主题模式，同时更新 xterm.js 的 ANSI 颜色配置。
6. **Tab 补全**：在外部命令的 `tabComplete` 回调中根据参数位置返回不同的候选列表，Shell 会自动处理补全逻辑（唯一匹配自动补全、多匹配显示列表）。

## 相关概念

- [IO 系统](/concepts/05-io-system.md)
- [外部命令](../concepts/09-external-commands.md)
- [Shell API 参考](../references/shell-api.md)
