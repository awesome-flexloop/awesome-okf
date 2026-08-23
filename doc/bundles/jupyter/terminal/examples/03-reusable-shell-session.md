---
type: Example
title: 复用Shell会话
description: 使用start-shell/execute-shell/shutdown-shell管理持久化shell会话，保持工作目录和状态
tags: [shell-session, reusable, stateful, start-shell, shutdown-shell, list-shells, cwd]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-08-22
prerequisites:
  - "已阅读[执行shell命令示例](02-execute-shell-command.md)"
  - "理解[无头命令执行](../concepts/05-headless-exec.md)中的shell复用机制"
---

# 复用Shell会话

一次性shell（不传shellName）每次执行都创建新shell，适合简单命令。需要保持状态（工作目录、环境变量、alias）或高频执行命令时，应使用持久化shell会话。

## 基本流程

```
start-shell → execute-shell(shellName) → execute-shell(shellName) → ... → shutdown-shell
```

## 启动持久化Shell

```typescript
// 启动shell，使用默认工作目录
const started = await app.commands.execute(
  '@jupyterlite/terminal:start-shell'
);
console.log(started.shellName);  // "headless-1"
console.log(started.message);    // "Headless shell 'headless-1' started successfully"

// 启动shell并指定工作目录
const started2 = await app.commands.execute(
  '@jupyterlite/terminal:start-shell',
  { cwd: '/drive' }
);
```

## 在同一个Shell中执行多条命令

```typescript
// 启动shell
const { shellName } = await app.commands.execute(
  '@jupyterlite/terminal:start-shell'
);

// 第1条命令：切换目录
const r1 = await app.commands.execute(
  '@jupyterlite/terminal:execute-shell',
  {
    code: 'cd /drive',
    shellName
  }
);
// r1.output 为空（cd不产生输出），r1.success === true

// 第2条命令：在/drive下创建文件（状态保持！）
const r2 = await app.commands.execute(
  '@jupyterlite/terminal:execute-shell',
  {
    code: 'echo "stateful" > test.txt',
    shellName
  }
);

// 第3条命令：在/drive下列出文件
const r3 = await app.commands.execute(
  '@jupyterlite/terminal:execute-shell',
  {
    code: 'ls',
    shellName
  }
);
console.log(r3.output);  // 包含 "test.txt"

// 第4条命令：读取刚创建的文件
const r4 = await app.commands.execute(
  '@jupyterlite/terminal:execute-shell',
  {
    code: 'cat test.txt',
    shellName
  }
);
console.log(r4.output);  // "stateful\n"

// 用完关闭
await app.commands.execute(
  '@jupyterlite/terminal:shutdown-shell',
  { shellName }
);
```

对比一次性shell（不传shellName）：

```typescript
// 一次性shell中，cd不会保持
await app.commands.execute('@jupyterlite/terminal:execute-shell', { code: 'cd /drive' });
const r = await app.commands.execute('@jupyterlite/terminal:execute-shell', { code: 'pwd' });
// r.output 可能是 "/home/pyodide"（新shell，cd状态丢失）
```

## 列出活跃Shell

```typescript
const list = await app.commands.execute(
  '@jupyterlite/terminal:list-shells'
);
console.log(`Active shells (${list.count}):`);
list.shells.forEach(s => console.log(` - ${s.name}`));
// Active shells (2):
//  - headless-1
//  - headless-2
```

## 完整示例：批量文件处理

```typescript
async function processFiles(app: JupyterFrontEnd, directory: string) {
  // 启动shell并切换到目标目录
  const { shellName } = await app.commands.execute(
    '@jupyterlite/terminal:start-shell',
    { cwd: directory }
  );
  
  try {
    // 步骤1：列出文件
    const lsResult = await app.commands.execute(
      '@jupyterlite/terminal:execute-shell',
      { code: 'ls -1', shellName }
    );
    const files = lsResult.output.trim().split('\n').filter(Boolean);
    
    // 步骤2：逐个处理文件
    const results = [];
    for (const file of files) {
      // 检查是否是.txt文件
      const checkResult = await app.commands.execute(
        '@jupyterlite/terminal:execute-shell',
        {
          code: `test -f "${file}" && echo FILE || echo DIR`,
          shellName,
          timeout: 5000
        }
      );
      
      if (checkResult.output.trim() === 'FILE' && file.endsWith('.txt')) {
        // 统计行数
        const wcResult = await app.commands.execute(
          '@jupyterlite/terminal:execute-shell',
          {
            code: `wc -l < "${file}"`,
            shellName,
            timeout: 5000
          }
        );
        results.push({ file, lines: parseInt(wcResult.output.trim()) });
      }
    }
    
    // 步骤3：生成汇总
    const summaryCmd = results
      .map(r => `echo "${r.file}: ${r.lines} lines"`)
      .join('; ');
    await app.commands.execute(
      '@jupyterlite/terminal:execute-shell',
      { code: `${summaryCmd} > summary.txt`, shellName }
    );
    
    return results;
  } finally {
    // 确保shell被关闭
    await app.commands.execute(
      '@jupyterlite/terminal:shutdown-shell',
      { shellName }
    ).catch(console.error);
  }
}

// 使用
const results = await processFiles(app, '/drive');
console.log('Processed files:', results);
```

## 超时恢复

如果shell超时，需要关闭并重建：

```typescript
async function safeExecute(app: JupyterFrontEnd, shellName: string, code: string) {
  try {
    return await app.commands.execute(
      '@jupyterlite/terminal:execute-shell',
      { code, shellName, timeout: 10000 }
    );
  } catch (err) {
    const msg = (err as Error).message;
    if (msg.includes('timed out') || msg.includes('cannot be reused')) {
      // Shell已超时，关闭旧shell
      try {
        await app.commands.execute(
          '@jupyterlite/terminal:shutdown-shell',
          { shellName }
        );
      } catch (e) { /* 忽略关闭错误 */ }
      
      // 创建新shell（需要外部管理shellName引用）
      throw new Error('Shell timed out, needs recreation');
    }
    throw err;
  }
}
```

## 管理多个Shell

可以同时运行多个headless shell，每个保持独立状态：

```typescript
// Shell 1: 在/drive中操作文件
const s1 = await app.commands.execute('@jupyterlite/terminal:start-shell', { cwd: '/drive' });

// Shell 2: 在/tmp中操作临时文件
const s2 = await app.commands.execute('@jupyterlite/terminal:start-shell', { cwd: '/tmp' });

// 并行执行（注意：同一shell不能并行，但不同shell可以）
const [r1, r2] = await Promise.all([
  app.commands.execute('@jupyterlite/terminal:execute-shell', {
    code: 'ls', shellName: s1.shellName
  }),
  app.commands.execute('@jupyterlite/terminal:execute-shell', {
    code: 'echo hello > temp.txt && ls', shellName: s2.shellName
  })
]);

// 列出所有
const list = await app.commands.execute('@jupyterlite/terminal:list-shells');
// list.count === 2

// 关闭所有
for (const s of list.shells) {
  await app.commands.execute('@jupyterlite/terminal:shutdown-shell', { shellName: s.name });
}
```

## 封装：ShellSession辅助类

可以封装一个辅助类简化shell管理：

```typescript
class ShellSession {
  private shellName: string | null = null;
  
  constructor(private app: JupyterFrontEnd, private cwd?: string) {}
  
  async start(): Promise<void> {
    const result = await this.app.commands.execute(
      '@jupyterlite/terminal:start-shell',
      { cwd: this.cwd }
    );
    this.shellName = result.shellName;
  }
  
  async exec(code: string, timeout?: number): Promise<any> {
    if (!this.shellName) throw new Error('Session not started');
    return this.app.commands.execute(
      '@jupyterlite/terminal:execute-shell',
      { code, shellName: this.shellName, timeout }
    );
  }
  
  async stop(): Promise<void> {
    if (this.shellName) {
      await this.app.commands.execute(
        '@jupyterlite/terminal:shutdown-shell',
        { shellName: this.shellName }
      );
      this.shellName = null;
    }
  }
}

// 使用
const session = new ShellSession(app, '/drive');
await session.start();
try {
  const files = await session.exec('ls -1');
  console.log(files.output);
} finally {
  await session.stop();
}
```

## 最佳实践

1. **总是shutdown**：使用try/finally确保shell被关闭，避免资源泄漏
2. **合理设置timeout**：根据命令预期执行时间设置timeout，避免无意义等待
3. **避免嵌套调用**：同一shell不要嵌套执行（busy互斥），使用await串行或多shell并行
4. **超时即销毁**：超时后的shell标记为不可用，应shutdown后重建
5. **定期list-shells**：长时间运行的应用应定期检查并清理泄漏的shell

## 相关示例

- [执行shell命令](02-execute-shell-command.md)：一次性命令执行
- [自定义外部命令](04-custom-command.md)：扩展shell能力
- [无头命令执行概念](../concepts/05-headless-exec.md)：超时和复用机制详解
