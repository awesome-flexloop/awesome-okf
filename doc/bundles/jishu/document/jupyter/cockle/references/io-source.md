---
type: reference
title: IO 系统源码参考
description: IInput/IOutput 接口、TerminalInput/Output、FileInput/Output、Pipe 等 IO 类 API 参考
tags:
  - cockle
  - io
  - input
  - output
  - pipe
generated:
  at: "2026-08-22T00:00:00+08:00"
  by: okf-gen
verified:
  at: "2026-08-22T00:00:00+08:00"
  by: source-extract
status: stable
stale_after: "2027-08-22"
sources:
  - id: io-index
    resource: /references/io-source.md
    title: src/io/index.ts
  - id: io-input
    resource: /references/io-source.md
    title: src/io/input.ts
  - id: io-output
    resource: /references/io-source.md
    title: src/io/output.ts
---

## 概述

Cockle 浏览器 Shell 的 IO（输入/输出）系统定义了统一的 IInput（输入接口）和 IOutput（输出接口）抽象，所有数据读写都通过这两个接口进行。IO 系统为终端交互、文件读写、管道传输、外部命令桥接、控制台输出等场景提供了对应的实现类，并通过抽象基类统一缓冲管理和单字符读取逻辑。

## IInput 接口

IInput（输入接口）定义了所有输入源必须实现的契约：

```typescript
interface IInput {
  read(maxChars: number | null): number[];
  readAsync(maxChars: number | null, timeoutMs?: number): Promise<number[]>;
  pollInput(timeoutMs: number): number[];
  atEof(): boolean;
  setRawMode?(rawMode: boolean): void;
}
```

各方法说明：
- **read(maxChars)**：同步读取最多 `maxChars` 个字符（以字符编码数值数组形式返回），传 `null` 表示读取全部可用输入
- **readAsync(maxChars, timeoutMs?)**：异步读取，可选超时参数，返回 Promise
- **pollInput(timeoutMs)**：轮询输入，在指定超时内等待输入到达，返回立即可用的字符数组
- **atEof()**：返回是否已到达输入流末尾（End of File）
- **setRawMode?(rawMode)**：可选方法，设置终端原始模式（raw mode），用于逐字符输入场景

## IOutput 接口

IOutput（输出接口）定义了所有输出目标必须实现的契约：

```typescript
interface IOutput {
  write(text: string): void;
  flush(): void;
  canList(): boolean;
  list(): string[];
  clone(): IOutput;
}
```

各方法说明：
- **write(text)**：写入文本字符串到输出目标
- **flush()**：刷新输出缓冲区，确保所有缓冲数据被写出
- **canList()**：返回此输出是否支持列出内容（如目录列表场景）
- **list()**：返回输出目标中的内容列表字符串数组
- **clone()**：克隆当前输出实例，创建独立副本

## 终端 IO

### TerminalInput

TerminalInput（终端输入）实现 IInput 接口，用于交互式终端场景下的用户输入：

```typescript
class TerminalInput implements IInput {
  constructor(
    pollInput: (timeoutMs: number) => number[],
    read: (maxChars: number | null) => number[],
    readAsync: (maxChars: number | null, timeoutMs?: number) => Promise<number[]>
  );
}
```

构造函数接收三个回调函数，分别对应 `pollInput`、`read`、`readAsync` 三种读取模式，由调用方（主线程或 Worker）提供实际的输入获取逻辑。TerminalInput 本身不持有输入缓冲区，而是完全委托给回调。

### TerminalOutput

TerminalOutput（终端输出）实现 IOutput 接口，用于向终端界面写入文本：

```typescript
class TerminalOutput implements IOutput {
  constructor(
    outputCallback: (text: string) => void,
    prefix?: string,
    suffix?: string
  );
}
```

- **outputCallback**：实际输出文本的回调函数
- **prefix**：可选的 ANSI 转义前缀（如颜色设置），在每次写入前自动添加
- **suffix**：可选的 ANSI 转义后缀（如颜色重置），在每次写入后自动添加

支持可选的前缀/后缀机制，便于实现带颜色的提示符（prompt）输出和错误输出（stderr）着色。

## 文件 IO

### FileInput

FileInput（文件输入）从虚拟文件系统读取数据：

```typescript
class FileInput implements IInput {
  constructor(fileSystem: IFileSystem, path: string);
}
```

- **fileSystem**：文件系统实例
- **path**：要读取的文件路径

FileInput 实现 IInput 接口，将文件内容作为字符流提供给命令，支持 `<` 输入重定向。

### FileOutput

FileOutput（文件输出）将数据写入虚拟文件系统：

```typescript
class FileOutput implements IOutput {
  constructor(fileSystem: IFileSystem, path: string, append?: boolean);
}
```

- **fileSystem**：文件系统实例
- **path**：目标文件路径
- **append**：是否以追加模式打开（`true` 对应 `>>`，`false` 对应 `>` 覆盖）

支持标准输出 `>`/`>>` 和标准错误 `2>`/`2>>` 重定向到文件。

## 管道

Pipe（管道）同时实现 IInput 和 IOutput 两个接口，用于命令间数据传输：

```typescript
class Pipe implements IInput, IOutput {
  // 内部维护缓冲区
  // write() 将数据写入缓冲区
  // read() 从缓冲区读取数据
}
```

Pipe 是 Shell 管道机制（`|`）的核心组件。前一个命令的输出端写入 Pipe，后一个命令的输入端从 Pipe 读取，实现进程间（命令间）的数据流通。管道内部维护一个缓冲区，平衡生产者和消费者之间的速度差异。

## 外部命令 IO

### ExternalInput

ExternalInput（外部命令输入）专为在主线程运行的外部命令设计：

```typescript
class ExternalInput implements IInput {
  // readAsync 返回 Promise<string> 而非 number[]
}
```

与其他 IInput 实现不同，ExternalInput 的 `readAsync` 返回 `Promise<string>`（字符串）而非字符编码数组（`number[]`），适配主线程外部命令的输入数据格式。

### ExternalOutput

ExternalOutput（外部命令输出）用于外部命令的输出接收：

```typescript
class ExternalOutput implements IOutput {
  constructor(write: (text: string) => void, isTerminal: boolean);
}
```

- **write**：输出回调函数
- **isTerminal**：标识输出目标是否为终端，影响某些命令的输出格式（如 `ls` 在终端输出列对齐，在管道输出单列表）

## 抽象基类与工具类

### BufferedOutput

BufferedOutput（缓冲输出）是一个抽象类，为输出实现提供内部缓冲区管理：

```typescript
abstract class BufferedOutput implements IOutput {
  protected buffer: string;
  write(text: string): void;    // 追加到缓冲区
  flush(): void;                // 刷新缓冲区（子类实现具体写出逻辑）
}
```

子类需实现 `flush()` 方法以定义缓冲区内容的实际输出目标。

### InputAll

InputAll（全量输入）是一个抽象类，实现 IInput 接口，提供逐字符读取的基础逻辑：

```typescript
abstract class InputAll implements IInput {
  // read() 每次读取一个字符
  // 子类提供底层数据源访问
}
```

作为需要全量读取输入场景的基类，`read()` 方法每次返回单个字符，简化子类实现。

### ConsoleOutput

ConsoleOutput（控制台输出）将数据写入 JavaScript 标准 `console.*` 方法：

```typescript
class ConsoleOutput implements IOutput {
  // write() 调用 console.log 或 console.error
}
```

主要用于调试和开发环境，将 Shell 输出映射到浏览器开发者工具控制台。

### DummyInput

DummyInput（空输入）是一个无操作（no-op）输入实现：

```typescript
class DummyInput implements IInput {
  read(): number[] { return []; }
  readAsync(): Promise<number[]> { return Promise.resolve([]); }
  pollInput(): number[] { return []; }
  atEof(): boolean { return true; }
}
```

始终返回空数组，`atEof()` 始终返回 `true`。用于没有输入源的命令场景，避免 null 检查。

### DummyOutput

DummyOutput（空输出）是一个无操作输出实现：

```typescript
class DummyOutput implements IOutput {
  write(_text: string): void {}
  flush(): void {}
  canList(): boolean { return false; }
  list(): string[] { return []; }
  clone(): IOutput { return new DummyOutput(); }
}
```

`write()` 和 `flush()` 均为空操作，用于丢弃输出或作为占位符。

### RedirectOutput

RedirectOutput（重定向输出）将输出重定向到另一个 IOutput 实例：

```typescript
class RedirectOutput implements IOutput {
  constructor(target: IOutput);
  // 所有方法委托给 target
}
```

作为输出重定向的包装器，允许在运行时动态切换输出目标。

## IO 组合关系

在典型命令执行中，IO 对象按以下方式组合：

- **终端交互**：TerminalInput ↔ TerminalOutput
- **文件读取**：FileInput → 命令 → TerminalOutput
- **文件写入**：TerminalInput → 命令 → FileOutput
- **管道连接**：TerminalOutput → Pipe → CommandNode1 → Pipe → CommandNode2 → TerminalOutput
- **外部命令**：ExternalInput ↔ ExternalOutput

Shell 实现根据解析器生成的 AST 中的 RedirectNode 和 PipeNode，自动组装对应的 IO 对象链。

## 相关概念

- [命令系统源码参考](command-source.md)：命令运行器中的 IRunContext 包含 IO 引用
- [缓冲 IO 源码参考](buffered-io-source.md)：SAB 和 Service Worker 两种跨线程 IO 后端
- [解析器源码参考](parser-source.md)：重定向和管道节点的 AST 结构
- [Worker 通信源码参考](worker-source.md)：Worker 端 IO 与主线程的协调
