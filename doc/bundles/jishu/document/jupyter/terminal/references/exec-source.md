---
type: Reference
title: 无头命令执行API信源
description: HeadlessShellPool、命令注册、执行流程和结果格式的完整API参考
tags: [headless, exec, command, shell-pool, api, timeout]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: exec-ts
    resource: /../../../../../../external/libs/jupyter/terminal/src/exec.ts
    title: src/exec.ts
---

# 无头命令执行API信源

## 命令ID常量

```typescript
const COMMAND_IDS = {
  executeShell: '@jupyterlite/terminal:execute-shell',
  startShell: '@jupyterlite/terminal:start-shell',
  shutdownShell: '@jupyterlite/terminal:shutdown-shell',
  listShells: '@jupyterlite/terminal:list-shells'
} as const;
```

## 数据类型

### ShellExecutionStatus

```typescript
type ShellExecutionStatus = 'ok' | 'error' | 'timeout';
```

### IExecuteShellResult

```typescript
interface IExecuteShellResult {
  success: boolean;        // exitCode === 0
  status: ShellExecutionStatus;
  output: string;          // 清理后的命令输出
  exitCode: number | null; // 超时为null
  shellName: string;       // 执行命令的shell名称
  duration: number;        // 执行耗时（毫秒）
  message: string;         // 结果描述消息
}
```

### IShellListItem

```typescript
interface IShellListItem {
  name: string;
}
```

### IHeadlessSession（内部）

```typescript
interface IHeadlessSession {
  shell: IShell;
  output: string;   // 通过getter访问闭包累积的output
  busy: boolean;    // 是否正在执行命令
  timedOut: boolean; // 是否已超时（超时后不可复用）
}
```

## HeadlessShellPool 类

管理无头shell会话的池。

```typescript
class HeadlessShellPool {
  constructor(client: ILiteTerminalAPIClient);
  async create(options: { cwd?: string }): Promise<IHeadlessSession>;
  get(name: string): IHeadlessSession | undefined;
  names(): string[];
  async shutdown(name: string): Promise<void>;
}
```

### create

```typescript
async create(options: { cwd?: string }): Promise<IHeadlessSession>
```

1. 生成名称：`headless-${_nextId++}`（_nextId从1开始）
2. 调用`client.createHeadlessShell()`：
   - shellId: 生成的name
   - cwd: options.cwd
   - environment: `{ PS1: '' }`（空提示符，防止PS1污染输出）
   - outputCallback: 累积文本到局部变量output
   - readyTimeoutMs: 默认30000ms
3. 创建session对象（output通过getter引用闭包变量）
4. 存入`_sessions: Map<string, IHeadlessSession>`
5. 监听shell.disposed信号，从_sessions删除
6. 返回session

### get

```typescript
get(name: string): IHeadlessSession | undefined
```

从_sessions Map获取session。

### names

```typescript
names(): string[]
```

返回所有活跃session名称数组。

### shutdown

```typescript
async shutdown(name: string): Promise<void>
```

1. 获取session，不存在则throw Error(`No headless shell found with name '${name}'`)
2. 从_sessions删除
3. 调用session.shell.dispose()

## 工具函数

### cleanCapturedOutput

```typescript
function cleanCapturedOutput(captured: string, code: string): string
```

清理shell输出：
1. 将所有`\r\n`替换为`\n`
2. 如果输出以`code + '\n'`开头（回显的命令），则slice去掉该前缀
3. 返回清理后的字符串

### runOnSession

```typescript
async function runOnSession(
  session: IHeadlessSession,
  code: string,
  timeout: number
): Promise<IExecuteShellResult>
```

在指定session上执行命令：

1. 获取shellId
2. 规范化命令：`code.trim().replace(/\r\n?/g, '\n')`
3. 空命令返回error结果
4. **安全检查**：
   - session.timedOut === true → throw Error（超时shell不可复用）
   - session.busy === true → throw Error（不支持重叠执行）
5. 设置session.busy = true
6. 记录startTime和startLen（output起始长度）
7. **竞争执行**：
   - `inputDone = session.shell.input(command + '\r')`（发送命令，等待完成）
   - `timer = setTimeout(..., timeout)`（超时定时器）
   - `Promise.race([inputDone, timerPromise])`竞争
8. 超时处理：
   - session.timedOut = true
   - 返回status='timeout', exitCode=null, success=false
9. 正常完成：
   - 通过`await session.shell.exitCode()`获取exitCode
   - output为cleanCapturedOutput处理后的切片
   - 返回status='ok'或'error'

## 四个命令注册

### execute-shell

**命令参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 是 | 要执行的shell命令 |
| shellName | string | 否 | 复用现有shell的名称 |
| cwd | string | 否 | 新shell的工作目录（复用shell时忽略） |
| timeout | number | 否 | 超时毫秒数，默认30000 |

**执行逻辑**：
1. 参数校验：code为非空string、shellName为string或undefined、cwd为string或undefined、timeout为正有限数值
2. 如果提供shellName：从pool获取现有session，不存在则throw
3. 否则：创建新session，disposeAfter=true
4. 调用runOnSession执行
5. finally中：如果disposeAfter则pool.shutdown（best-effort，不屏蔽真实结果）

**返回值**：IExecuteShellResult

### start-shell

**命令参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| cwd | string | 否 | 新shell的工作目录 |

**返回值**：
```typescript
{
  success: true,
  message: `Headless shell '${shellName}' started successfully`,
  shellName: string
}
```

### shutdown-shell

**命令参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shellName | string | 是 | 要关闭的shell名称 |

**返回值**：
```typescript
{
  success: true,
  message: `Headless shell '${shellName}' shut down successfully`,
  shellName: string
}
```

### list-shells

**命令参数**：无

**返回值**：
```typescript
{
  success: true,
  shells: IShellListItem[],  // [{ name: string }]
  count: number,
  available: true
}
```

## 插件定义（terminalExecPlugin）

```typescript
export const terminalExecPlugin: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlite/terminal:exec',
  description: 'Headless shell exec commands backed by cockle',
  autoStart: true,
  requires: [ILiteTerminalAPIClient],
  activate: (app: JupyterFrontEnd, liteTerminalAPIClient: ILiteTerminalAPIClient): void => {
    const pool = new HeadlessShellPool(liteTerminalAPIClient);
    registerCommands(app.commands, pool);
  }
};
```

## 重要行为说明

1. **PS1环境变量**：create时设置PS1=''，shell不打印提示符，输出只包含命令结果
2. **命令回显**：cockle shell会回显输入的命令，cleanCapturedOutput函数负责去除
3. **换行符**：内部统一将\r\n和\r转换为\n处理
4. **超时不可恢复**：超时后的shell标记为timedOut=true，所有后续执行都throw
5. **busy互斥**：同一session不能同时执行多个命令
6. **一次性shell**：不传shellName时创建的shell在命令完成后自动dispose
7. **无头shell独立性**：HeadlessShellPool管理的shell不出现在终端Widget列表或listRunning()中
