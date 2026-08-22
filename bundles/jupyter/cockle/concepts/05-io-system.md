---
type: concept
title: "05 - IO 系统"
description: IInput/IOutput 接口族——终端IO、文件IO、管道、Dummy IO和重定向实现
tags: [io, input, output, pipe, file, terminal, redirect]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: io-source
    resource: /references/io-source.md
    title: IO 系统参考
---

## IO 系统概述

Cockle 的 IO（输入/输出）系统是所有命令与外部世界交互的抽象层。它定义了两个核心接口——`IInput`（输入接口）和 `IOutput`（输出接口），所有数据读写都通过这两个接口进行。这种设计使得不同来源/目标的 IO 对象可以互换使用（interchangeable），无论是终端交互、文件读写、管道传输还是外部命令桥接，命令代码都只依赖 IInput/IOutput 抽象，不需要感知底层实现。

IO 系统的设计遵循 Unix 哲学——"一切皆字节流"。终端、文件、管道在命令看来都是统一的输入流和输出流，重定向和管道本质上就是替换命令的 stdin/stdout/stderr 指向不同的 IInput/IOutput 实现。

```
┌─────────────────────────────────────────────────────────────┐
│                    IInput / IOutput 接口                     │
│  统一抽象：read/write/flush/atEof/pollInput 等               │
├─────────┬──────────┬──────────┬──────────┬──────────────────┤
│Terminal │ File     │ Pipe     │ Dummy    │ External         │
│Input/   │ Input/   │ (双接口)  │ Input/   │ Input/           │
│Output   │ Output   │          │ Output   │ Output           │
├─────────┴──────────┴──────────┴──────────┴──────────────────┤
│  辅助类：BufferedOutput, InputAll, ConsoleOutput,            │
│          RedirectOutput                                     │
└─────────────────────────────────────────────────────────────┘
```

## IInput 接口

`IInput` 是所有输入源必须实现的契约 [F-260-F274]：

```typescript
interface IInput {
  read(maxChars: number | null): number[];
  readAsync(maxChars: number | null, timeoutMs?: number): Promise<number[]>;
  pollInput(timeoutMs: number): number[];
  atEof(): boolean;
  setRawMode?(rawMode: boolean): void;
}
```

各方法的功能和使用场景：

| 方法 | 说明 |
|------|------|
| `read(maxChars)` | **同步读取**。从输入流中读取最多 `maxChars` 个字符，返回字符编码的数值数组。传 `null` 表示读取全部可用输入。如果没有立即可用的数据，返回空数组。 |
| `readAsync(maxChars, timeoutMs?)` | **异步读取**。等待输入到达后返回字符数组，可选超时参数（毫秒）。适用于需要等待用户输入的场景。 |
| `pollInput(timeoutMs)` | **轮询输入**。在指定超时时间内等待输入，返回立即可用的字符数组。常用于交互式输入循环，避免忙等。 |
| `atEof()` | 返回是否已到达输入流末尾（End of File）。当返回 `true` 时，后续 read 将返回空数组。 |
| `setRawMode?(rawMode)` | **可选方法**。设置终端原始模式（raw mode）。在 raw mode 下，输入逐字符立即可用（不需要等待回车），行编辑功能（如 Backspace）由命令自身处理。这对于 `vim`、`nano` 等全屏编辑器至关重要。 |

**返回值说明**：输入数据以 `number[]`（字符编码数组）形式返回，而非字符串。这是因为 WASM 命令（通过 Emscripten 编译）期望接收字节/字符编码数组。字符串到数组的转换由具体实现类处理。

典型使用模式（命令内部读取输入）：

```typescript
// 逐字符读取直到 EOF
while (!context.stdin.atEof()) {
  const chars = context.stdin.read(1);  // 每次读一个字符
  for (const code of chars) {
    const ch = String.fromCharCode(code);
    context.stdout.write(ch.toUpperCase());  // 处理并输出
  }
}

// 异步读取一行（用户输入）
const inputChars = await context.stdin.readAsync(null);
const input = String.fromCharCode(...inputChars);
```

## IOutput 接口

`IOutput` 是所有输出目标必须实现的契约 [F-260-F274]：

```typescript
interface IOutput {
  write(text: string): void;
  flush(): void;
  canList(): boolean;
  list(): string[];
  clone(): IOutput;
}
```

各方法的功能：

| 方法 | 说明 |
|------|------|
| `write(text)` | 向输出目标写入文本字符串。写入可能被缓冲，调用 `flush()` 确保数据被实际写出。 |
| `flush()` | 刷新输出缓冲区，将所有缓冲数据推送到目标设备/文件/回调。 |
| `canList()` | 返回此输出是否支持列出内容。主要用于特殊场景（如目录列表输出）。大多数实现返回 `false`。 |
| `list()` | 当 `canList()` 返回 `true` 时，返回输出内容的字符串列表。 |
| `clone()` | 克隆当前输出实例，创建一个独立的副本。两个副本写入互不影响。 |

**write 方法接受 string 而非 number[]**：输出方向统一使用字符串，因为 TypeScript 层面的命令处理文本输出更自然。WASM 命令的字节输出通过 Emscripten 的终端回调机制桥接到 string。

典型使用模式（命令内部输出）：

```typescript
// 输出文本
context.stdout.write('Hello, World!\n');

// 输出错误信息到 stderr
context.stderr.write('Error: file not found\n');

// 缓冲写入后刷新
context.stdout.write('Processing...');
// ... 一些处理 ...
context.stdout.write(' done!\n');
context.stdout.flush();
```

## 终端 IO

终端 IO 是用户与 Shell 交互的主要通道，由 `TerminalInput` 和 `TerminalOutput` 组成。

### TerminalInput

`TerminalInput` 实现 `IInput` 接口，用于交互式终端场景下的用户输入。它不持有输入缓冲区，而是完全委托给构造时传入的回调函数 [F-260-F274]：

```typescript
class TerminalInput implements IInput {
  constructor(
    pollInput: (timeoutMs: number) => number[],
    read: (maxChars: number | null) => number[],
    readAsync: (maxChars: number | null, timeoutMs?: number) => Promise<number[]>
  );
}
```

三个回调分别对应 `pollInput`、`read`、`readAsync` 三种读取模式。在 Worker 端，这些回调通过 Buffered IO 层（SAB 或 Service Worker）从主线程获取用户键盘输入。在主线程端，这些回调直接从终端 UI 组件（如 xterm.js）获取输入。

TerminalInput 支持 `setRawMode`，用于全屏应用（vim、less 等）切换到逐字符输入模式。

### TerminalOutput

`TerminalOutput` 实现 `IOutput` 接口，用于向终端界面写入文本 [F-260-F274]：

```typescript
class TerminalOutput implements IOutput {
  constructor(
    outputCallback: (text: string) => void,
    prefix?: string,
    suffix?: string
  );
}
```

- **outputCallback**：实际输出文本的回调函数。在 Worker 端，此回调通过 Worker 通信层（Comlink/Coincident）将输出传回主线程，主线程再转发给 `outputCallback`（即 Shell 构造时传入的那个回调）。
- **prefix / suffix**：可选的 ANSI 转义序列前缀和后缀。每次 `write()` 调用时，自动在文本前后添加这些转义序列。典型用途：
  - stderr 输出添加红色 ANSI 前缀（如 `\x1b[31m`）和重置后缀（`\x1b[0m`），使错误信息显示为红色
  - 提示符（prompt）添加加粗或颜色前缀

示例：Shell 启动时创建 stdout 和 stderr：

```typescript
// stdout: 普通输出，无前缀后缀
const stdout = new TerminalOutput(outputCallback);

// stderr: 红色输出
const stderr = new TerminalOutput(outputCallback, '\x1b[31m', '\x1b[0m');
```

这使得命令调用 `context.stderr.write("error")` 时，终端上显示红色的 "error" 文本。

## 文件 IO

文件 IO 实现与虚拟文件系统（Emscripten MEMFS / DriveFS）的交互，支持输入/输出重定向。

### FileInput

`FileInput` 从虚拟文件系统读取数据，实现 `<` 输入重定向 [F-177][F-260-F274]：

```typescript
class FileInput implements IInput {
  constructor(fileSystem: IFileSystem, path: string);
}
```

构造时传入文件系统实例和文件路径。FileInput 在首次读取时打开文件，将文件内容作为字符流提供给命令。当读取到文件末尾时，`atEof()` 返回 `true`。

典型场景：`sort < unsorted.txt` 命令中，ShellImpl 创建 `new FileInput(fs, 'unsorted.txt')` 替换 sort 命令的 stdin，sort 从文件而非终端读取输入。

### FileOutput

`FileOutput` 将数据写入虚拟文件系统，实现 `>`/`>>`/`2>`/`2>>` 输出重定向 [F-177][F-260-F274]：

```typescript
class FileOutput implements IOutput {
  constructor(fileSystem: IFileSystem, path: string, append?: boolean);
}
```

参数说明：
- **fileSystem**：文件系统实例
- **path**：目标文件路径
- **append**：是否以追加模式打开。`true` 对应 `>>`/`2>>`（追加到文件末尾），`false`（默认）对应 `>`/`2>`（覆盖已有内容）

典型场景：
- `ls > files.txt` → `new FileOutput(fs, 'files.txt', false)` 替换 stdout
- `echo "log" >> app.log` → `new FileOutput(fs, 'app.log', true)` 替换 stdout
- `cmd 2> err.txt` → `new FileOutput(fs, 'err.txt', false)` 替换 stderr

## 管道

`Pipe`（管道）是 Cockle 实现 Shell 管道机制（`|`）的核心类，它**同时实现 `IInput` 和 `IOutput` 两个接口** [F-175][F-260-F274]：

```typescript
class Pipe implements IInput, IOutput {
  // 内部维护一个 FIFO 缓冲区
  // write() → 将数据追加到缓冲区尾部
  // read()  → 从缓冲区头部读取数据
}
```

Pipe 的工作原理：
1. ShellImpl 创建 Pipe 实例
2. 将前一个命令的 stdout 设置为 Pipe（作为 IOutput 写入端）
3. 将后一个命令的 stdin 设置为同一个 Pipe（作为 IInput 读取端）
4. 前一个命令写入的数据通过内部缓冲区传递给后一个命令读取

管道内部维护一个 FIFO（先进先出）缓冲区，平衡生产者（写入命令）和消费者（读取命令）之间的速度差异。当缓冲区满时，写入方阻塞等待；当缓冲区为空时，读取方阻塞等待有数据到达。

管道链（多命令管道）的连接方式：

```
ls -la          grep .md         wc -l
stdout → Pipe1 → stdin
                stdout → Pipe2 → stdin
                                stdout → TerminalOutput（用户终端）
```

ShellImpl 的 `_runCommands` 方法在遇到 PipeNode 时，为每对相邻命令创建一个 Pipe 对象，依次连接形成管道链 [F-175]。

## 特殊 IO 实现

### DummyInput / DummyOutput（空操作 IO）

`DummyInput` 和 `DummyOutput` 是空操作（no-op）实现，用于不需要真实 IO 的场景 [F-260-F274]：

```typescript
class DummyInput implements IInput {
  read(): number[] { return []; }
  readAsync(): Promise<number[]> { return Promise.resolve([]); }
  pollInput(): number[] { return []; }
  atEof(): boolean { return true; }
}

class DummyOutput implements IOutput {
  write(_text: string): void {}
  flush(): void {}
  canList(): boolean { return false; }
  list(): string[] { return []; }
  clone(): IOutput { return new DummyOutput(); }
}
```

使用场景：
- 命令不需要 stdin 时，用 DummyInput 代替（避免 null 检查）
- 需要丢弃输出时（如 `cmd > /dev/null` 的等价场景），用 DummyOutput
- 测试时使用，不产生任何副作用

### ExternalInput / ExternalOutput（外部命令 IO）

`ExternalInput` 和 `ExternalOutput` 专为在主线程运行的外部命令（External Command）设计 [F-148][F-260-F274]：

```typescript
class ExternalInput implements IInput {
  // readAsync 返回 Promise<string> 而非 number[]
  // 适配主线程外部命令的字符串输入格式
}

class ExternalOutput implements IOutput {
  constructor(write: (text: string) => void, isTerminal: boolean);
}
```

- **ExternalInput**：与其他 IInput 不同，它的 `readAsync` 返回 `Promise<string>` 而非 `number[]`，更适合主线程 JavaScript 代码的使用习惯。
- **ExternalOutput**：接收一个 `isTerminal` 布尔参数，标识输出目标是否为终端。某些命令（如 `ls`）在终端输出时会使用列对齐格式，在管道/文件输出时使用单列表格格式，这个标志用于区分。

当 ShellImpl 执行外部命令时 [F-148]，创建 `ExternalEnvironment`（包含 ExternalInput/ExternalOutput/ExternalTermios），通过 Worker 通信层桥接到主线程，调用注册的外部命令函数。

### ConsoleOutput（控制台输出）

`ConsoleOutput` 将输出写入 JavaScript 的 `console.log` 或 `console.error`，主要用于调试和开发环境 [F-260-F274]：

```typescript
class ConsoleOutput implements IOutput {
  // write() → console.log 或 console.error
}
```

开发调试时，可以临时将 stdout 替换为 ConsoleOutput，在浏览器开发者工具的 Console 面板中直接查看命令输出。

## 辅助基类

### BufferedOutput（缓冲输出基类）

`BufferedOutput` 是一个抽象类，为输出实现提供内部字符串缓冲区管理 [F-260-F274]：

```typescript
abstract class BufferedOutput implements IOutput {
  protected buffer: string = '';
  write(text: string): void {
    this.buffer += text;  // 追加到内部缓冲区
  }
  abstract flush(): void;  // 子类实现实际写出逻辑
  // ... 其他方法
}
```

子类只需实现 `flush()` 方法，定义缓冲区内容的实际输出目标（如调用回调、写入文件等）。TerminalOutput 等类可以基于此类实现带缓冲的输出。

### InputAll（全量输入基类）

`InputAll` 是一个抽象类，实现 IInput 接口，提供逐字符读取的基础逻辑 [F-260-F274]：

```typescript
abstract class InputAll implements IInput {
  // read() 每次读取一个字符
  // 子类提供底层数据源访问
}
```

对于需要一次性读取全部输入的场景，继承 InputAll 可以简化实现，子类只需提供数据源访问方法。

### RedirectOutput（重定向输出）

`RedirectOutput` 是一个包装器，将所有输出操作重定向到另一个 IOutput 实例 [F-260-F274]：

```typescript
class RedirectOutput implements IOutput {
  constructor(target: IOutput);
  // 所有方法委托给 target
}
```

这允许在运行时动态切换输出目标。例如，一个命令在执行过程中可以将输出从终端切换到文件，不需要创建新的 IOutput 引用。

## IO 重定向机制

当 ShellImpl 执行命令时，`_runCommand` 方法根据 AST 中的 `RedirectNode` 数组替换命令的默认 stdin/stdout/stderr [F-176][F-177]。默认情况下，命令的三个标准流指向：

| 流 | 默认指向 | 说明 |
|----|----------|------|
| stdin | TerminalInput | 用户键盘输入 |
| stdout | TerminalOutput | 终端屏幕（带可选 ANSI 前缀/后缀） |
| stderr | TerminalOutput | 终端屏幕（通常带红色前缀） |

重定向替换规则：

```typescript
// 默认 IO
let stdin: IInput = terminalInput;
let stdout: IOutput = terminalStdout;
let stderr: IOutput = terminalStderr;

// 遍历重定向节点
for (const redirect of commandNode.redirects) {
  switch (redirect.token.value) {
    case '>':
      stdout = new FileOutput(fs, redirect.target.value, false);
      break;
    case '>>':
      stdout = new FileOutput(fs, redirect.target.value, true);
      break;
    case '<':
      stdin = new FileInput(fs, redirect.target.value);
      break;
    case '2>':
      stderr = new FileOutput(fs, redirect.target.value, false);
      break;
    case '2>>':
      stderr = new FileOutput(fs, redirect.target.value, true);
      break;
  }
}
```

多个重定向可以同时存在。例如 `cmd < input.txt > output.txt 2> error.txt` 会同时替换 stdin、stdout 和 stderr。

## 管道数据流

对于管道链（PipeNode），ShellImpl 的 `_runCommands` 方法创建 Pipe 对象连接相邻命令 [F-175]。以 `ls | grep .md | wc -l` 为例：

```typescript
const pipe1 = new Pipe();  // ls → grep
const pipe2 = new Pipe();  // grep → wc

// ls: stdout → pipe1
const lsContext = { stdin: terminalInput, stdout: pipe1, stderr: terminalStderr, ... };
await lsRunner.run(lsContext);
pipe1.closeWriteEnd();  // 通知写入结束

// grep: stdin ← pipe1, stdout → pipe2
const grepContext = { stdin: pipe1, stdout: pipe2, stderr: terminalStderr, ... };
await grepRunner.run(grepContext);
pipe2.closeWriteEnd();

// wc: stdin ← pipe2, stdout → terminal
const wcContext = { stdin: pipe2, stdout: terminalStdout, stderr: terminalStderr, ... };
await wcRunner.run(wcContext);
```

每个 Pipe 作为上游命令的 IOutput（写入端）和下游命令的 IInput（读取端），数据在内存中通过 FIFO 缓冲区流动。管道链中的最后一个命令的 stdout 通常指向 TerminalOutput（用户终端），除非另有重定向。

## IO 组合模式总结

Cockle 的 IO 系统通过统一接口实现了灵活的组合能力：

| 场景 | stdin | stdout | stderr |
|------|-------|--------|--------|
| **终端交互** | TerminalInput | TerminalOutput | TerminalOutput(red) |
| **输入重定向** (`< file`) | FileInput | TerminalOutput | TerminalOutput(red) |
| **输出覆盖** (`> file`) | TerminalInput | FileOutput(append=false) | TerminalOutput(red) |
| **输出追加** (`>> file`) | TerminalInput | FileOutput(append=true) | TerminalOutput(red) |
| **错误重定向** (`2> file`) | TerminalInput | TerminalOutput | FileOutput(append=false) |
| **全重定向** (`< in > out 2> err`) | FileInput | FileOutput(false) | FileOutput(false) |
| **管道** (`a \| b`) | Pipe ← a | Pipe → b | TerminalOutput(red) |
| **丢弃输出** (`> /dev/null`) | TerminalInput | DummyOutput | DummyOutput |
| **外部命令** | ExternalInput | ExternalOutput | ExternalOutput |

所有这些组合都是通过在命令执行前替换 IInput/IOutput 引用实现的，命令代码本身不需要知道数据来自哪里、去向何方——这就是 IO 抽象的力量。

## 相关概念

- [命令系统](/concepts/03-command-system.md)
- [命令解析管线](/concepts/04-parsing-pipeline.md)
- [架构总览](/concepts/02-architecture-overview.md)
