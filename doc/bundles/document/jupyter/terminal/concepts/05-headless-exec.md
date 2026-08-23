---
type: Concept
title: 无头命令执行
description: HeadlessShellPool的设计、四个编程式命令的用法、shell复用机制、超时处理和输出清理
tags: [headless, exec, command, shell-pool, timeout, programmatic-api, output-callback]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: exec-source
    resource: /references/exec-source.md
    title: 无头命令执行API信源
  - id: client-source
    resource: /references/client-source.md
    title: LiteTerminalAPIClient API信源
---

# 无头命令执行

无头（Headless）Shell 是不绑定xterm.js UI的shell会话，通过编程方式执行命令并捕获输出。这为其他JupyterLite扩展提供了在浏览器中执行shell命令的能力，类似于后端的`subprocess.run()`。

## 命令总览

| 命令ID | 功能 | 是否复用Shell |
|--------|------|--------------|
| `@jupyterlite/terminal:execute-shell` | 执行单条命令并返回结果 | 可选 |
| `@jupyterlite/terminal:start-shell` | 启动持久化shell会话 | 创建新 |
| `@jupyterlite/terminal:shutdown-shell` | 关闭shell会话 | - |
| `@jupyterlite/terminal:list-shells` | 列出活跃shell会话 | - |

## HeadlessShellPool

HeadlessShellPool管理无头shell的生命周期，是exec插件在activate时创建的单例：

```typescript
class HeadlessShellPool {
  constructor(client: ILiteTerminalAPIClient);
  async create(options: { cwd?: string }): Promise<IHeadlessSession>;
  get(name: string): IHeadlessSession | undefined;
  names(): string[];
  async shutdown(name: string): Promise<void>;
}
```

### Session命名

每个session自动命名为`headless-N`（N从1递增），确保唯一且与交互式终端的数字命名不冲突（交互式终端命名为"1","2","3"...）。

### Session状态

每个IHeadlessSession包含：

```typescript
interface IHeadlessSession {
  shell: IShell;           // cockle shell实例
  output: string;         // 累积输出（getter实时读取闭包变量）
  busy: boolean;          // 是否正在执行命令
  timedOut: boolean;      // 是否已超时（超时后不可复用）
}
```

### Shell创建细节

创建headless shell时，LiteTerminalAPIClient.createHeadlessShell()设置：

```typescript
{
  shellId: name,
  cwd: options.cwd,
  environment: { PS1: '' },  // 关键：清空PS1避免提示符污染输出
  outputCallback: (text) => { output += text; },  // 累积到闭包变量
  readyTimeoutMs: 30000  // 默认30秒就绪超时
}
```

**PS1=''的重要性**：清空shell提示符，使得输出只包含命令结果而不包含`$`等提示符。

**ready超时**：如果shell在30秒内未就绪（WASM加载失败、Worker初始化超时等），创建会reject并dispose shell。

## execute-shell 命令

这是最常用的命令，用于执行shell命令并返回结果。

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `code` | string | **必填** | 要执行的shell命令 |
| `shellName` | string | undefined | 复用现有shell的名称；不提供则创建一次性shell |
| `cwd` | string | undefined | 新shell的工作目录（复用shell时忽略） |
| `timeout` | number | 30000 | 超时毫秒数（最小100ms） |

### 返回值

```typescript
interface IExecuteShellResult {
  success: boolean;         // exitCode === 0
  status: 'ok' | 'error' | 'timeout';
  output: string;           // 清理后的命令输出
  exitCode: number | null;  // 超时为null
  shellName: string;        // 执行命令的shell名称
  duration: number;         // 执行耗时（毫秒）
  message: string;          // 结果描述
}
```

### 执行流程

```
参数校验 → 获取/创建session → 命令规范化 → 安全检查
    ↓
 发送命令(shell.input()) ──┐
                           ├─ Promise.race
 超时定时器 ───────────────┘
    ↓
 超时? → timedOut=true, 返回timeout结果
    ↓
 正常完成 → 获取exitCode → 清理输出 → 返回结果
    ↓
 finally: 如果是一次性shell(disposeAfter)，shutdown
```

### 安全检查

执行前有两个防护检查：
1. `session.timedOut === true` → throw Error("Shell timed out and cannot be reused...")
2. `session.busy === true` → throw Error("Shell is busy...")

这确保了超时的shell不会被意外复用，同一shell不会重叠执行命令。

## start-shell / shutdown-shell 命令

### start-shell

启动一个持久化shell会话，可以后续通过shellName复用：

```typescript
// 参数：{ cwd?: string }
// 返回：
{
  success: true,
  message: "Headless shell 'headless-1' started successfully",
  shellName: "headless-1"
}
```

### shutdown-shell

关闭指定的持久化shell：

```typescript
// 参数：{ shellName: string }（必填）
// 返回：
{
  success: true,
  message: "Headless shell 'headless-1' shut down successfully",
  shellName: "headless-1"
}
```

如果shellName不存在，throw Error(`No headless shell found with name '${name}'`)。

## list-shells 命令

列出所有活跃的headless shell会话：

```typescript
// 无参数
// 返回：
{
  success: true,
  shells: [{ name: "headless-1" }, { name: "headless-2" }],
  count: 2,
  available: true
}
```

注意：交互式终端（用户打开的终端Widget）不会出现在此列表中，因为它们存储在另一个Map（Private.shells）中。

## 输出清理机制

`cleanCapturedOutput`函数处理shell输出的两个问题：

1. **换行符统一**：所有`\r\n`替换为`\n`
2. **命令回显去除**：cockle shell会回显用户输入的命令（如输入`ls\r`，输出以`ls\n`开头）。函数检测输出是否以`code + '\n'`开头，如果是则slice去掉

```typescript
function cleanCapturedOutput(captured: string, code: string): string {
  let output = captured.replace(/\r\n/g, '\n');
  if (output.startsWith(code + '\n')) {
    output = output.slice(code.length + 1);
  }
  return output;
}
```

输出切片使用`startLen`（命令发送前的output长度）确保只截取当前命令产生的输出，而非整个session历史。

## 超时机制

```typescript
const timer = new Promise<never>((_, reject) => {
  setTimeoutId = window.setTimeout(() => reject(new Error('timeout')), timeout);
});

await Promise.race([inputDone, timer]);
```

超时后：
1. `session.timedOut = true`（标记为不可复用）
2. `clearTimeout(setTimeoutId)`清除定时器
3. 返回`{ success: false, status: 'timeout', exitCode: null }`
4. 后续任何在该session上的执行都throw错误

> **注意**：超时后shell进程可能仍在运行（cockle shell没有强制终止机制），但session标记为timedOut后拒绝所有新命令。建议超时后调用shutdown-shell释放资源。

## Shell复用 vs 一次性Shell

### 一次性Shell（不传shellName）

```typescript
const result = await commands.execute('@jupyterlite/terminal:execute-shell', {
  code: 'ls /drive'
});
// 命令完成后shell自动关闭
```

- 适合：单次命令执行
- 优点：无资源泄漏风险
- 缺点：每次启动shell有WASM加载开销

### 复用Shell（指定shellName）

```typescript
// 先启动
const { shellName } = await commands.execute('@jupyterlite/terminal:start-shell');

// 多次执行
const r1 = await commands.execute('@jupyterlite/terminal:execute-shell', {
  code: 'cd /drive && ls', shellName
});
const r2 = await commands.execute('@jupyterlite/terminal:execute-shell', {
  code: 'cat file.txt', shellName  // 在/drive目录下（cd状态保持）
});

// 用完关闭
await commands.execute('@jupyterlite/terminal:shutdown-shell', { shellName });
```

- 适合：需要保持状态（工作目录、环境变量、alias）的多命令序列
- 优点：避免重复WASM加载，状态持久化
- 缺点：需要手动管理生命周期，超时后需要shutdown重建

## 全局配置共享

HeadlessShellPool创建的shell与交互式终端共享全局配置：

- `registerAlias()`：别名对所有shell生效（包括后续创建的）
- `registerEnvironmentVariable()`：环境变量对新shell生效
- `registerExternalCommand()`：外部命令对所有shell可见

这意味着在交互式终端中设置的alias在headless shell中也能使用。

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| code为空或非字符串 | throw Error("code must be a non-empty string") |
| timeout为非正数/NaN/Infinity | throw Error("timeout must be a positive finite number") |
| shellName不存在 | throw Error(`No headless shell found with name '${name}'`) |
| shell正在busy | throw Error("Shell is busy...") |
| shell已超时 | throw Error("Shell timed out and cannot be reused...") |
| shell创建超时(30s) | reject错误并dispose |
| 命令执行超时 | 返回timeout结果 |

建议调用方使用try/catch捕获这些错误。

## 相关概念

- [示例：执行shell命令](/examples/02-execute-shell-command.md)：execute-shell的完整用法
- [示例：复用shell会话](/examples/03-reusable-shell-session.md)：持久化shell模式
- [Shell与Worker机制](04-shell-and-worker.md)：shell底层实现
- [无头命令执行API信源](/references/exec-source.md)：完整类型定义
