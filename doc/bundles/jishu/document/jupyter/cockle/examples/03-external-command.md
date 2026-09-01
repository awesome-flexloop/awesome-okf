---
type: example
title: "03 - 注册外部命令"
description: 实现一个在主线程执行的自定义外部命令，访问浏览器 API 并返回结果到 Shell
tags: [example, external-command, custom-command, main-thread, browser-api]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: external-commands
    resource: /concepts/09-external-commands.md
    title: 外部命令
related_concepts: [/concepts/09-external-commands.md, /concepts/03-command-system.md, /references/shell-api.md]
---

## 目标

外部命令（External Command）是在浏览器主线程（UI 线程）中执行的自定义命令，与 WASM 命令（在 Web Worker 中运行）不同。通过外部命令，你可以：

1. 直接访问浏览器 API（DOM、Navigator、Clipboard、Fetch 等）
2. 与页面上的其他 JavaScript 代码交互
3. 实现自定义的业务逻辑
4. 可选地提供 Tab 补全支持

本示例实现三个实用的外部命令：浏览器信息查询、剪贴板读取、以及带 Tab 补全的问候命令。

## 示例 1：浏览器信息命令

`browserinfo` 命令输出当前浏览器的基本信息，使用 Navigator API 获取数据并写入 Shell 的 stdout：

```typescript
import type { IExternalRunContext } from '@jupyterlite/cockle';
import { ExitCode } from '@jupyterlite/cockle';

/**
 * browserinfo 命令：输出浏览器环境信息
 * 用法：browserinfo [--json]
 */
async function browserinfoCommand(context: IExternalRunContext): Promise<number> {
  const { args, stdout, environment } = context;
  const asJson = args.includes('--json');

  const info = {
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    languages: navigator.languages.join(', '),
    cookieEnabled: navigator.cookieEnabled,
    onLine: navigator.onLine,
    hardwareConcurrency: navigator.hardwareConcurrency,
    deviceMemory: (navigator as any).deviceMemory ?? 'unknown',
    vendor: navigator.vendor,
    screenSize: `${screen.width}x${screen.height}`,
    windowSize: `${window.innerWidth}x${window.innerHeight}`,
    crossOriginIsolated: window.crossOriginIsolated
  };

  if (asJson) {
    stdout.write(JSON.stringify(info, null, 2) + '\n');
  } else {
    stdout.write('=== 浏览器信息 ===\n');
    stdout.write(`User Agent: ${info.userAgent}\n`);
    stdout.write(`平台: ${info.platform}\n`);
    stdout.write(`语言: ${info.language} (${info.languages})\n`);
    stdout.write(`Cookie 启用: ${info.cookieEnabled}\n`);
    stdout.write(`在线状态: ${info.onLine ? '在线' : '离线'}\n`);
    stdout.write(`CPU 核心数: ${info.hardwareConcurrency}\n`);
    stdout.write(`设备内存: ${info.deviceMemory} GB\n`);
    stdout.write(`厂商: ${info.vendor}\n`);
    stdout.write(`屏幕尺寸: ${info.screenSize}\n`);
    stdout.write(`窗口尺寸: ${info.windowSize}\n`);
    stdout.write(`跨域隔离: ${info.crossOriginIsolated ? '是' : '否'}\n`);
  }

  // 将浏览器语言设置到环境变量中（演示 environment 修改）
  environment.set('BROWSER_LANG', info.language);

  return ExitCode.SUCCESS; // 返回 0 表示成功
}
```

关键点：
- 函数签名：`(context: IExternalRunContext) => Promise<number>`，返回退出码（0 表示成功）
- 使用 `context.stdout.write(text)` 向标准输出写入文本
- 使用 `context.environment.set(key, value)` 修改 Shell 环境变量（修改会自动同步回 Worker）
- 使用 `ExitCode.SUCCESS`（值为 0）表示命令成功执行

## 示例 2：剪贴板命令

`clip` 命令读取剪贴板文本内容并输出到 stdout。需要注意浏览器剪贴板 API 的异步特性和权限要求：

```typescript
import type { IExternalRunContext } from '@jupyterlite/cockle';
import { ExitCode } from '@jupyterlite/cockle';

/**
 * clip 命令：读取剪贴板内容
 * 用法：clip
 */
async function clipCommand(context: IExternalRunContext): Promise<number> {
  const { stdout, stderr } = context;

  try {
    // 检查浏览器是否支持 Clipboard API
    if (!navigator.clipboard || !navigator.clipboard.readText) {
      stderr.write('错误：当前浏览器不支持 Clipboard API\n');
      return ExitCode.GENERAL_ERROR;
    }

    // 读取剪贴板文本（需要用户授权）
    const text = await navigator.clipboard.readText();

    if (text.length === 0) {
      stdout.write('(剪贴板为空)\n');
    } else {
      stdout.write('--- 剪贴板内容 ---\n');
      stdout.write(text);
      if (!text.endsWith('\n')) {
        stdout.write('\n');
      }
      stdout.write('--- 结束 ---\n');
    }

    return ExitCode.SUCCESS;
  } catch (err: any) {
    stderr.write(`读取剪贴板失败: ${err.message}\n`);
    stderr.write('提示：请确保页面已获得剪贴板读取权限，且在 HTTPS 或 localhost 环境下运行\n');
    return ExitCode.GENERAL_ERROR;
  }
}
```

关键点：
- 使用 `context.stderr.write(text)` 向标准错误输出写入错误信息
- 错误输出会在终端中显示（通常为红色或独立显示）
- 浏览器 API 调用需要适当的错误处理和权限检查
- 返回非零退出码（如 `ExitCode.GENERAL_ERROR` = 1）表示执行失败

## 示例 3：带 Tab 补全的命令

`greet` 命令接受一个用户名参数并输出问候语，同时提供 Tab 补全功能，当用户输入 `greet <Tab>` 时会列出可补全的用户名：

```typescript
import type {
  IExternalRunContext,
  IExternalTabCompleteContext,
  IExternalTabCompleteResult
} from '@jupyterlite/cockle';
import { ExitCode } from '@jupyterlite/cockle';

// 可补全的用户列表
const KNOWN_USERS = ['alice', 'bob', 'charlie', 'diana', 'david', 'eve', 'frank', 'grace'];

/**
 * greet 命令的执行函数
 * 用法：greet <name>
 */
async function greetCommand(context: IExternalRunContext): Promise<number> {
  const { args, stdout, shellId, size, name: cmdName } = context;

  // 检查参数
  if (args.length === 0) {
    stdout.write(`用法: ${cmdName} <name>\n`);
    stdout.write('可用用户：' + KNOWN_USERS.join(', ') + '\n');
    return ExitCode.GENERAL_ERROR;
  }

  const userName = args[0];

  // 演示获取终端尺寸
  const { rows, columns } = size();
  stdout.write(`你好，${userName}！👋\n`);
  stdout.write(`当前终端尺寸: ${rows} 行 x ${columns} 列\n`);
  stdout.write(`Shell ID: ${shellId}\n`);

  // 如果用户不在已知列表中，给出友好提示
  if (!KNOWN_USERS.includes(userName)) {
    stdout.write(`(注意：${userName} 不在已知用户列表中)\n`);
  }

  return ExitCode.SUCCESS;
}

/**
 * greet 命令的 Tab 补全函数
 * 当用户在命令后按 Tab 键时调用
 */
async function greetTabComplete(
  context: IExternalTabCompleteContext
): Promise<IExternalTabCompleteResult> {
  const { args } = context;
  // args 的最后一个元素是当前正在输入的参数（可能为空字符串）
  const partial = args[args.length - 1] ?? '';

  // 过滤出以 partial 开头的用户名
  const matches = KNOWN_USERS.filter(u => u.startsWith(partial));

  return {
    possibles: matches
  };
}
```

关键点：
- Tab 补全函数签名：`(context: IExternalTabCompleteContext) => Promise<IExternalTabCompleteResult>`
- `context.args` 包含当前命令的所有参数，最后一个元素是正在补全的部分输入
- 返回 `{ possibles: string[] }` 提供匹配候选列表
- 如果只有一个匹配项，Cockle 会自动补全；如果有多个，会列出所有选项

## 完整代码

下面是一个完整的 HTML 示例，注册上述三个外部命令并启动 Shell：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Cross-Origin-Opener-Policy" content="same-origin">
  <meta http-equiv="Cross-Origin-Embedder-Policy" content="require-corp">
  <title>Cockle 外部命令示例</title>
  <style>
    body { margin: 0; padding: 20px; background: #1e1e1e; color: #ccc; font-family: monospace; }
    #terminal { width: 100%; height: 500px; background: #000; padding: 10px; overflow-y: auto; white-space: pre-wrap; font-size: 14px; line-height: 1.4; border: 1px solid #333; }
    #hint { color: #888; margin-bottom: 10px; font-size: 12px; }
    h2 { color: #4af; }
  </style>
</head>
<body>
  <h2>Cockle 外部命令演示</h2>
  <div id="hint">可用命令：browserinfo [--json] | clip | greet &lt;name&gt; | 其他内置命令(ls, echo, help等)</div>
  <div id="terminal"></div>

  <script type="module">
    import { Shell, ShellManager, ExitCode } from '@jupyterlite/cockle';

    const terminalEl = document.getElementById('terminal');
    let outputBuffer = '';

    function outputCallback(text) {
      // 简单处理 ANSI 序列
      const cleanText = text.replace(/\x1b\[[0-9;]*m/g, '');
      outputBuffer += cleanText;
      terminalEl.textContent = outputBuffer;
      terminalEl.scrollTop = terminalEl.scrollHeight;
    }

    // ============ 外部命令定义 ============

    async function browserinfoCommand(context) {
      const { args, stdout, environment } = context;
      const asJson = args.includes('--json');

      const info = {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        cookieEnabled: navigator.cookieEnabled,
        onLine: navigator.onLine,
        cores: navigator.hardwareConcurrency,
        screen: `${screen.width}x${screen.height}`,
        crossOriginIsolated: window.crossOriginIsolated
      };

      if (asJson) {
        stdout.write(JSON.stringify(info, null, 2) + '\n');
      } else {
        stdout.write('=== 浏览器信息 ===\n');
        for (const [key, value] of Object.entries(info)) {
          stdout.write(`${key}: ${value}\n`);
        }
      }
      environment.set('BROWSER_LANG', info.language);
      return ExitCode.SUCCESS;
    }

    async function clipCommand(context) {
      const { stdout, stderr } = context;
      try {
        if (!navigator.clipboard?.readText) {
          stderr.write('错误：浏览器不支持 Clipboard API\n');
          return ExitCode.GENERAL_ERROR;
        }
        const text = await navigator.clipboard.readText();
        stdout.write(text ? text + '\n' : '(剪贴板为空)\n');
        return ExitCode.SUCCESS;
      } catch (err) {
        stderr.write(`读取剪贴板失败: ${err.message}\n`);
        return ExitCode.GENERAL_ERROR;
      }
    }

    const KNOWN_USERS = ['alice', 'bob', 'charlie', 'diana', 'david', 'eve'];

    async function greetCommand(context) {
      const { args, stdout, size } = context;
      if (args.length === 0) {
        stdout.write('用法: greet <name>\n');
        return ExitCode.GENERAL_ERROR;
      }
      const { rows, columns } = size();
      stdout.write(`你好，${args[0]}！终端 ${rows}x${columns}\n`);
      return ExitCode.SUCCESS;
    }

    async function greetTabComplete(context) {
      const partial = context.args[context.args.length - 1] ?? '';
      const matches = KNOWN_USERS.filter(u => u.startsWith(partial));
      return { possibles: matches };
    }

    // ============ 初始化 Shell ============

    async function init() {
      const baseUrl = window.location.href;
      const shellManager = new ShellManager();
      const browsingContextId = await shellManager.installServiceWorker(baseUrl);

      const shell = new Shell({
        baseUrl,
        wasmBaseUrl: baseUrl,
        browsingContextId,
        shellManager,
        outputCallback,
        color: true,
        externalCommands: [
          { name: 'browserinfo', command: browserinfoCommand },
          { name: 'clip', command: clipCommand },
          { name: 'greet', command: greetCommand, tabComplete: greetTabComplete }
        ]
      });

      shell.commandStateChanged.connect((_, args) => {
        if (args.state === 'finished' && args.exitCode !== 0) {
          console.log(`命令 ${args.name} 退出码: ${args.exitCode}`);
        }
      });

      await shell.ready;
      await shell.start();
      shell.setSize({ rows: 30, columns: 100 });

      // 简单的键盘输入处理（实际项目建议使用 xterm.js）
      document.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          await shell.input('\r');
        }
      });

      // 演示：自动执行 browserinfo 命令
      setTimeout(() => shell.input('browserinfo\r'), 500);
    }

    init();
  </script>
</body>
</html>
```

## 关键点说明

### IExternalRunContext 接口

外部命令的执行上下文（Context）提供以下属性和方法：

| 属性 | 类型 | 说明 |
|------|------|------|
| `name` | `string` | 被调用的命令名称（可能与注册名不同，如果有别名解析） |
| `args` | `string[]` | 命令参数数组（不含命令名本身） |
| `environment` | `ExternalEnvironment` | 环境变量 Map，可通过 `set()`/`delete()`/`get()` 修改 |
| `shellId` | `string` | 当前 Shell 的唯一标识 |
| `stdin` | `IExternalInput` | 标准输入流 |
| `stdout` | `IExternalOutput` | 标准输出流 |
| `stderr` | `IExternalOutput` | 标准错误流 |
| `size()` | `() => ISize` | 返回当前终端尺寸 `{rows, columns}` |
| `termios` | `Termios` | 终端模式控制对象 |

### stdin 读取：返回 string 而非 number[]

`stdin.readAsync(maxChars)` 返回 `Promise<string>`，直接返回字符串而非字节数组。`maxChars` 为 `null` 时表示读取尽可能多的字符（直到换行或缓冲区满）：

```typescript
// 读取一行输入
const input = await context.stdin.readAsync(null);
```

### 输出写入

`stdout.write(text)` 和 `stderr.write(text)` 接受字符串参数。写入后不需要手动 flush，ExternalOutput 会自动将数据传递到 Worker 端。如果输出包含多行，确保每行以 `\n` 结尾以正确换行。

### Termios 终端模式控制

`termios` 对象用于控制终端的输入模式，例如切换原始模式（逐字符输入）和规范模式（行缓冲输入）：

```typescript
import { Termios } from '@jupyterlite/cockle';

async function rawModeCommand(context: IExternalRunContext): Promise<number> {
  const { stdin, stdout, termios } = context;

  // 保存原始终端设置
  const oldFlags = termios.get();

  // 切换到原始模式（关闭 ICANON，逐字符读取）
  const newFlags = Termios.cloneFlags(oldFlags);
  newFlags.c_lflag &= ~Termios.LocalFlag.ICANON;
  newFlags.c_lflag &= ~Termios.LocalFlag.ECHO;
  termios.set(newFlags);

  stdout.write('按任意键（q 退出）...\n');
  while (true) {
    const ch = await stdin.readAsync(1);
    if (ch === 'q' || ch === 'Q' || ch === '\x04') break;
    stdout.write(`收到字符: ${ch} (charCode: ${ch.charCodeAt(0)})\n`);
  }

  // 恢复原始设置
  termios.set(oldFlags);
  return ExitCode.SUCCESS;
}
```

### 环境变量同步

通过 `context.environment.set(key, value)` 设置的环境变量会在命令执行完成后自动同步回 Shell 的 Worker 环境，后续命令可以通过 `$KEY` 访问。使用 `environment.delete(key)` 删除变量。这些修改通过 `ExternalEnvironment.changed` 属性追踪，只传输变更的变量。

### 退出码约定

外部命令应返回 `Promise<number>`，遵循 Unix 约定：
- `0`（`ExitCode.SUCCESS`）：成功
- `1`（`ExitCode.GENERAL_ERROR`）：一般错误
- `127`（`ExitCode.CANNOT_FIND_COMMAND`）：命令未找到（由 Shell 内部使用）

导入 `ExitCode` 枚举可以使用预定义的退出码常量。

## 相关概念

- [外部命令](../concepts/09-external-commands.md)
- [命令系统](../concepts/03-command-system.md)
- [Shell API 参考](../references/shell-api.md)
