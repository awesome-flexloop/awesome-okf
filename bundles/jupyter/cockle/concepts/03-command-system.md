---
type: concept
title: "03 - 命令系统"
description: ICommandRunner 接口、四种命令类型（Builtin/WASM/JS/External）、CommandRegistry 注册与查找机制
tags: [commands, registry, runner, builtin, wasm, external]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: cmd-source
    resource: /references/command-source.md
    title: 命令系统参考
---

## 命令系统架构

Cockle 的命令系统基于**统一接口 + 注册表模式**设计。所有命令——无论是内置的 TypeScript 命令、WASM 编译的 Unix 工具、动态加载的 JS 模块还是主线程桥接的外部命令——都实现相同的 `ICommandRunner` 接口，由 `CommandRegistry`（命令注册表）统一管理和调度。

这种设计的核心优势是**可扩展性**：添加新的命令类型只需要实现 `ICommandRunner` 接口并注册到注册表，Shell 的执行引擎不需要任何修改。命令查找、加载、执行的流程对所有命令类型一致。

```
┌──────────────────────────────────────────────────────┐
│                  CommandRegistry                      │
│  (命令注册表——统一管理所有命令)                         │
│                                                      │
│  _commands: Map<string, ICommandRunner>              │
│  get(name) → runner | null                           │
│  match(prefix) → string[]                            │
│  registerBuiltinCommands(...)                        │
│  registerCommandPackage(pkg)                         │
│  registerExternalCommand(name, ...)                  │
└───────┬──────────┬──────────┬──────────┬─────────────┘
        │          │          │          │
   ┌────▼───┐ ┌───▼────┐ ┌──▼─────┐ ┌──▼──────────┐
   │Builtin │ │Wasm    │ │JS      │ │External     │
   │Command │ │Command │ │Command │ │Command      │
   │Runner  │ │Runner  │ │Runner  │ │Runner       │
   └────────┘ └────────┘ └────────┘ └─────────────┘
   TypeScript  懒加载WASM  懒加载JS  主线程回调
```

## ICommandRunner 统一接口

`ICommandRunner`（命令运行器接口）是所有可执行命令必须实现的契约 [F-200]：

```typescript
interface ICommandRunner {
  commandType: CommandType;       // 命令类型（位掩码）
  moduleName: string;             // 所属模块名
  packageName: string;            // 所属包名
  names(): string[];              // 返回该运行器支持的所有命令名（含别名）
  run(context: IRunContext): Promise<number>;  // 执行命令，返回退出码
  tabComplete?(context: ITabCompleteContext): Promise<ITabCompleteResult>;  // 可选：Tab补全
}
```

**核心方法 `run(context)`** 是命令执行的入口。它接收一个 `IRunContext`（运行上下文）对象，其中包含了命令执行所需的全部环境：

```typescript
interface IRunContext {
  args: string[];           // 命令参数（args[0] 是命令名）
  stdin: IInput;            // 标准输入
  stdout: IOutput;          // 标准输出
  stderr: IOutput;          // 标准错误
  env: Environment;         // 环境变量
  cwd: string;              // 当前工作目录
  fs: FileSystem;           // 文件系统接口
  // ... 其他执行上下文字段
}
```

命令通过 `context.stdin` 读取输入，通过 `context.stdout`/`context.stderr` 写出输出，通过 `context.args` 获取参数，返回一个 `Promise<number>` 表示退出码。

## 四种命令类型详解

Cockle 支持四种命令类型 [F-003]，每种类型有不同的加载机制和执行环境：

### 1. Builtin TypeScript（内置命令）

内置命令直接在 Shell 核心中用 TypeScript 实现，Shell 启动时即注册可用，无需额外下载 [F-240-F253]。

```typescript
abstract class BuiltinCommand implements ICommandRunner {
  commandType = CommandType.Builtin;
  moduleName = '<builtin>';
  packageName: string;
  abstract get name(): string;
  abstract _run(context: IRunContext): Promise<number>;
  names(): string[];
  run(context: IRunContext): Promise<number>;
}
```

所有内置命令继承 `BuiltinCommand` 抽象基类，实现 `name` 属性和 `_run()` 方法。`run()` 方法在调用 `_run()` 前会发送 `running` 状态通知。

Cockle 内置了以下命令 [F-240-F253]：

| 命令 | 功能 |
|------|------|
| `alias` | 定义或显示命令别名 |
| `cd` | 切换工作目录 |
| `clear` | 清屏 |
| `cockle-config` | 查看/修改 Cockle 配置（如 Worker 类型、stdin 后端） |
| `exit` | 退出 Shell |
| `export` | 设置环境变量 |
| `help` | 显示帮助信息 |
| `history` | 显示命令历史 |
| `unset` | 移除环境变量 |
| `which` | 查找命令位置 |
| `true` | 返回退出码 0（布尔真值） |
| `false` | 返回退出码 1（布尔假值） |

内置命令直接操作 Shell 的内部状态（如修改 `cwd`、操作 `env`、管理 `aliases`），执行速度快，是 Shell 启动后立即可用的核心命令。

### 2. WebAssembly / Emscripten（WASM 命令）

WASM 命令是通过 Emscripten 编译器将 C/C++ 程序编译为 WebAssembly 模块的命令 [F-004]。这类命令在 Worker 线程中通过 Emscripten 运行时实例化执行，与 TypeScript 核心通过 Emscripten 的文件系统（FS）和函数调用表互操作。

Cockle 支持的 WASM 包包括：

| 包名 | 提供的命令 |
|------|-----------|
| **coreutils** | `cat`、`cp`、`echo`、`ls`、`mkdir`、`mv`、`rm`、`touch`、`uname`、`wc` |
| **git2cpp** | `git` |
| **grep** | `grep` |
| **less** | `less` |
| **lua** | `lua` |
| **nano** | `nano` |
| **sed** | `sed` |
| **tree** | `tree` |
| **vim** | `vim` |

从 v1.4.0 开始使用 Emscripten 4.0.9 和 prefix.dev 的 emscripten-forge-4x 渠道 [F-005]。

WASM 命令通过 `WasmCommandRunner` 执行，它继承自 `DynamicallyLoadedCommandRunner`，采用**惰性加载**策略——命令模块代码仅在首次执行时才通过网络下载和实例化，避免启动时加载所有 WASM 包导致的长时间等待。

### 3. JavaScript 模块命令

JavaScript 命令是纯 JavaScript 编写的命令模块（不含 WASM 二进制），通过动态 `import()` 加载 [F-003]。

```typescript
class JavascriptCommandRunner extends DynamicallyLoadedCommandRunner {
  commandType = CommandType.JavaScript;
}
```

JS 命令通过 `JavascriptCommandRunner` 执行，同样继承自 `DynamicallyLoadedCommandRunner`，支持惰性加载。这类命令适合用 JavaScript 实现的工具，不需要 C/C++ 编译步骤，可以直接利用浏览器 API 和 npm 生态。

### 4. External（外部命令/主线程命令）

外部命令运行在浏览器**主线程**（UI 线程）中 [F-003]，而非 Worker 线程。这使得外部命令可以直接访问 DOM、浏览器 API 和主线程上的其他对象。

```typescript
class ExternalCommandRunner implements ICommandRunner {
  commandType = CommandType.External;
  // 执行委托给 callExternalCommand 回调
}
```

外部命令在构造 Shell 时通过 `externalCommands` 选项注册 [F-319]：

```typescript
interface IExternalCommand.IOptions {
  name: string;                                  // 命令名
  command: (context: IExternalCommandContext) => Promise<number> | number;  // 命令函数
  tabComplete?: (request: ITabCompleteRequest) => Promise<ITabCompleteResult>;  // 可选补全
}
```

当 ShellImpl 执行外部命令时，请求通过 Worker 通信层传回主线程 [F-148]。主线程创建 `ExternalEnvironment`、`ExternalInput`、`ExternalOutput`、`ExternalTermios` 四个桥接对象，然后调用注册的命令函数 `command(context)`。命令的输入/输出通过这些桥接对象在主线程和 Worker 之间转发。

外部命令的典型应用场景：打开 URL、操作 DOM、调用浏览器 API（如 Notification、Clipboard）、与页面上的其他 JavaScript 库交互。

## CommandRegistry 命令注册表

`CommandRegistry`（命令注册表）是命令系统的中央调度器，维护命令名到 `ICommandRunner` 的映射 [F-200]。

### 构造函数

```typescript
constructor(
  commandStateChangedCallback: () => void,        // 命令状态变化回调
  callExternalCommand: (name: string, args: string[]) => Promise<number>,      // 外部命令调用回调
  callExternalTabComplete: (request: ITabCompleteRequest) => Promise<ITabCompleteResult>  // 外部命令补全回调
)
```

注册表在构造时接收三个回调，用于状态通知和外部命令桥接。

### 命令注册

注册表提供三种注册方法，对应不同来源的命令：

**registerBuiltinCommands(commands)**：批量注册内置命令实例。在 Shell 初始化时调用，将所有 `BuiltinCommand` 子类的实例注册到表中。

**registerCommandPackage(pkg: CommandPackage)**：注册一个命令包（CommandPackage）。命令包描述了一个可分发的命令集合，包含一个或多个 `CommandModule`（命令模块）：

```typescript
class CommandPackage {
  name: string;           // 包名（如 "coreutils"）
  version: string;        // 版本号
  build_string: string;   // 构建标识
  channel: string;        // 渠道（如 "emscripten-forge-4x"）
  platform: string;       // 平台标识
  wasm: boolean;          // 是否为 WASM 包
  modules: CommandModule[];  // 包内的命令模块列表
}
```

每个 `CommandModule` 代表一个可加载的模块，包含模块名、命令名列表和懒加载的 `runner` getter：

```typescript
class CommandModule {
  constructor(
    loader: CommandModuleLoader,  // 模块加载器
    name: string,                 // 模块名
    commands: string[],           // 模块提供的命令名
    packageName: string,          // 所属包名
    wasm: boolean                 // 是否 WASM 模块
  );
  get runner(): ICommandRunner;   // 懒初始化，首次访问时加载
}
```

WASM/JS 命令包的信息来自 `cockle-config.json` 配置文件，Shell 初始化时 `_initWasmPackages` 方法 fetch 该配置并调用 `registerCommandPackage` 注册 [F-184]。

**registerExternalCommand(name, hasTabComplete)**：注册单个外部命令。创建 `ExternalCommandRunner` 并注册到表中。

内部方法 `_register(runner)` 将运行器注册到其 `names()` 返回的所有名称下——一个运行器可以支持多个命令名（例如通过别名）。命令名通过正则 `/^[\w-]+$/` 验证合法性，仅允许字母数字、下划线和连字符。

### 命令查找与匹配

| 方法 | 说明 |
|------|------|
| `get(name: string): ICommandRunner \| null` | 按精确名称查找命令运行器，未找到返回 `null` |
| `match(start: string, commandType?: CommandType): string[]` | 按前缀匹配命令名列表，可按类型过滤 |
| `commandNames(commandType?: CommandType): string[]` | 获取所有已注册命令名，可按类型过滤 |

命令执行流程中，ShellImpl 首先通过 `registry.get(name)` 查找命令，找到后调用 `runner.run(context)` 执行。Tab 补全时使用 `registry.match(prefix)` 获取前缀匹配的命令名列表。

## 惰性加载机制

WASM 和 JavaScript 命令采用**惰性加载（Lazy Loading）**策略，通过 `DynamicallyLoadedCommandRunner` 实现：

```
用户输入命令
    │
    ▼
CommandRegistry.get("ls")
    │ 返回 DynamicallyLoadedCommandRunner（壳对象）
    ▼
runner.run(context)
    │ 首次访问时触发加载
    ├─ CommandModuleLoader 加载模块（网络下载 .wasm/.js）
    ├─ 创建实际的 WasmCommandRunner/JavascriptCommandRunner
    ├─ 缓存 runner 实例
    └─ 委托给实际 runner.run(context)
    │
    ▼
命令执行，返回退出码
```

`CommandModuleLoader` 负责从 `wasmBaseUrl` 加载模块代码，并维护加载缓存以避免重复下载同一模块。首次执行某个 WASM/JS 命令时，用户可能会感觉到短暂的加载延迟（取决于网络速度），但后续执行同一命令时直接使用缓存的实例，没有额外开销。

这种设计的好处是：
- **快速启动**：Shell 不需要等待所有 WASM 包下载完成即可开始交互
- **按需加载**：只加载用户实际使用的命令，节省带宽和内存
- **缓存复用**：模块加载后缓存，后续命令执行快速

## CommandType 位掩码

`CommandType` 使用**位掩码（Bitmask）**设计，允许通过位运算快速判断和组合命令类型 [F-200]：

```typescript
enum CommandType {
  None = 0,
  Unknown    = 1 << 0,  // 1   - 未知类型
  Builtin    = 1 << 1,  // 2   - 内置 TypeScript 命令
  External   = 1 << 2,  // 4   - 外部主线程命令
  JavaScript = 1 << 3,  // 8   - JavaScript 模块命令
  Wasm       = 1 << 4,  // 16  - WebAssembly 命令
  All = Unknown | Builtin | External | JavaScript | Wasm  // 31
}
```

位掩码的使用方式：

```typescript
// 判断命令是否为内置命令
if (runner.commandType & CommandType.Builtin) {
  // 是内置命令
}

// 只查找 WASM 和 JS 命令（动态加载的命令）
const dynamicCmds = registry.match('git', CommandType.Wasm | CommandType.JavaScript);

// 查找所有命令
const allCmds = registry.commandNames(CommandType.All);
```

## ExitCode 退出码

命令执行完成后返回一个数字退出码，遵循 Unix 惯例 [F-215]：

| 退出码 | 常量名 | 含义 | 典型场景 |
|--------|--------|------|----------|
| 0 | `SUCCESS` | 成功 | 命令正常完成 |
| 1 | `GENERAL_ERROR` | 一般错误 | 命令执行遇到错误（如文件不存在） |
| 2 | `IMPROPER_USE` | 用法错误 | 命令参数不正确 |
| 126 | `CANNOT_RUN` | 无法执行 | 命令存在但无法执行（权限问题等） |
| 127 | `NOT_FOUND` | 命令未找到 | 输入的命令不存在 |

内置命令和 WASM 命令都遵循这些退出码约定。外部命令的退出码由命令函数自行返回。`exitCode()` 方法可以获取最后一条命令的退出码，Shell 脚本中可以通过 `$?` 变量访问（如果支持的话）。

## 命令执行流程

一条命令从输入到执行完成的完整流程：

1. **解析**：ShellImpl 调用 `parse(cmdText, aliases, throwErrors=true)` 将命令行字符串解析为 AST [F-174]
2. **查找**：遍历 AST 中的 CommandNode，对每个命令调用 `CommandRegistry.get(name)` 查找对应的 ICommandRunner
3. **加载**：如果是 DynamicallyLoadedCommandRunner，首次执行时触发惰性加载，下载模块并创建实际 runner
4. **IO 设置**：根据 AST 中的 RedirectNode 创建 FileInput/FileOutput，PipeNode 创建 Pipe 对象连接命令
5. **执行**：创建 RunContext（包含 stdin/stdout/stderr/env/cwd/fs），调用 `runner.run(context)`
6. **状态通知**：命令开始时触发 `running` 状态，结束后触发 `finished` 状态（带 exitCode）
7. **管道调度**：对于管道链（`cmd1 | cmd2 | cmd3`），依次创建每个命令的 RunContext，用 Pipe 连接，按顺序执行

```
用户输入: ls -la | grep .md | wc -l
    │
    ▼
parse() → PipeNode(
           CommandNode("ls", ["-la"]),
           CommandNode("grep", [".md"]),
           CommandNode("wc", ["-l"])
         )
    │
    ▼
创建 Pipe 对象：
  ls.stdout → Pipe → grep.stdin
  grep.stdout → Pipe → wc.stdin
  wc.stdout → TerminalOutput（用户终端）
    │
    ▼
依次执行：
  1. ls.run(context1)  → 输出写入 Pipe1
  2. grep.run(context2) → 从 Pipe1 读取，输出写入 Pipe2
  3. wc.run(context3)   → 从 Pipe2 读取，输出到终端
```

## 相关概念

- [架构总览](/concepts/02-architecture-overview.md)
- [命令解析管线](/concepts/04-parsing-pipeline.md)
- [IO 系统](/concepts/05-io-system.md)
