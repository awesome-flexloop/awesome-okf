---
type: reference
title: 命令系统源码参考
description: CommandRegistry、ICommandRunner、DynamicallyLoadedCommandRunner 等命令系统核心类 API 参考
tags:
  - cockle
  - commands
  - api
generated:
  at: "2026-08-22T00:00:00+08:00"
  by: okf-gen
verified:
  at: "2026-08-22T00:00:00+08:00"
  by: source-extract
status: stable
stale_after: "2027-08-22"
sources:
  - id: cmd-runner
    resource: /references/command-source.md
    title: src/commands/command_runner.ts
  - id: cmd-registry
    resource: /references/command-source.md
    title: src/commands/command_registry.ts
  - id: cmd-type
    resource: /references/command-source.md
    title: src/commands/command_type.ts
  - id: cmd-module
    resource: /references/command-source.md
    title: src/commands/command_module.ts
---

## 概述

Cockle 浏览器 Shell（浏览器 Shell）的命令系统由一组核心类和接口构成，负责命令的注册、查找、加载与执行。命令类型（CommandType）通过位掩码区分内置命令（Builtin）、外部命令（External）、JavaScript 命令（JavaScript）和 WebAssembly 命令（Wasm）四类来源。命令注册表（CommandRegistry）统一管理所有可用命令的运行器（ICommandRunner）实例，动态加载的命令通过懒加载机制按需获取模块代码。

## ICommandRunner 接口

ICommandRunner（命令运行器接口）是所有可执行命令必须实现的契约：

```typescript
interface ICommandRunner {
  commandType: CommandType;
  moduleName: string;
  names(): string[];
  packageName: string;
  run(context: IRunContext): Promise<number>;
  tabComplete?(context: ITabCompleteContext): Promise<ITabCompleteResult>;
}
```

各成员含义：
- **commandType**：命令所属类型，使用位掩码标识
- **moduleName**：命令所属模块名称字符串
- **names()**：返回该运行器支持的所有命令名数组（支持别名）
- **packageName**：命令所属包名称字符串
- **run()**：在指定运行上下文（IRunContext）中执行命令，返回退出码的 Promise
- **tabComplete()**：可选方法，用于 Tab 补全（Tab Complete）

## CommandType 枚举

CommandType（命令类型枚举）使用位运算标志组合：

```typescript
enum CommandType {
  None = 0,
  Unknown = 1 << 0,
  Builtin = 1 << 1,
  External = 1 << 2,
  JavaScript = 1 << 3,
  Wasm = 1 << 4,
  All = Unknown | Builtin | External | JavaScript | Wasm
}
```

使用位掩码设计允许通过 `commandType & CommandType.Builtin` 快速判断类型，`All` 常量表示所有已知命令类型的集合。

## CommandRegistry 类

CommandRegistry（命令注册表）是命令系统的中央调度器。

### 构造函数

```typescript
constructor(
  commandStateChangedCallback: () => void,
  callExternalCommand: (name: string, args: string[]) => Promise<number>,
  callExternalTabComplete: (request: ITabCompleteRequest) => Promise<ITabCompleteResult>
)
```

接收三个回调参数：
- **commandStateChangedCallback**：命令状态变化时触发
- **callExternalCommand**：调用主线程外部命令的回调
- **callExternalTabComplete**：外部命令 Tab 补全回调

### 核心方法

| 方法 | 说明 |
|------|------|
| `get(name: string): ICommandRunner \| null` | 按名称查找命令运行器，未找到返回 null |
| `match(start: string, commandType?: CommandType): string[]` | 按前缀匹配命令名，可按类型过滤 |
| `commandNames(commandType?: CommandType): string[]` | 获取所有已注册命令名，可按类型过滤 |
| `registerBuiltinCommands(commands)` | 批量注册内置命令实例 |
| `registerCommandPackage(pkg: CommandPackage)` | 注册一个命令包及其所有模块 |
| `registerExternalCommand(name: string, hasTabComplete: boolean)` | 注册单个外部命令 |

### 内部方法

- **_register(runner: ICommandRunner)**：将运行器注册到其所有 `names()` 返回的名称下
- **_validName(name: string)**：使用正则 `/^[\w-]+$/` 验证命令名合法性，仅允许字母数字、下划线和连字符

## 动态加载命令运行器

DynamicallyLoadedCommandRunner（动态加载命令运行器）是一个抽象类，实现了 ICommandRunner，通过懒加载机制延迟获取实际的 `_runner` 实例。其 `commandType` 根据 `wasm` 标志决定是 JavaScript 还是 Wasm 类型。

### WasmCommandRunner

WasmCommandRunner（Wasm 命令运行器）继承自 DynamicallyLoadedCommandRunner，`commandType` 固定为 `CommandType.Wasm`，用于加载和执行 WebAssembly 格式的命令模块。

### JavascriptCommandRunner

JavascriptCommandRunner（JavaScript 命令运行器）继承自 DynamicallyLoadedCommandRunner，`commandType` 固定为 `CommandType.JavaScript`，用于加载和执行 JavaScript 格式的命令模块。

### ExternalCommandRunner

ExternalCommandRunner（外部命令运行器）直接实现 ICommandRunner 接口，`commandType` 为 `CommandType.External`。它不自行执行命令，而是将调用委托给构造时传入的 `callExternalCommand` 回调函数，在主线程中处理外部命令的执行。

## 命令模块与包

### CommandModule 类

CommandModule（命令模块）代表一个可加载的命令模块：

```typescript
class CommandModule {
  constructor(
    loader: CommandModuleLoader,
    name: string,
    commands: string[],
    packageName: string,
    wasm: boolean
  );
  get runner(): ICommandRunner; // 懒初始化，首次访问时加载模块
}
```

构造参数：
- **loader**：用于加载模块的 CommandModuleLoader 实例
- **name**：模块名称
- **commands**：模块提供的命令名列表
- **packageName**：所属包名称
- **wasm**：是否为 WebAssembly 模块

`runner` getter 实现懒初始化——首次访问时才通过 loader 实际加载模块代码。

### CommandPackage 类

CommandPackage（命令包）描述一个可分发的命令集合：

```typescript
class CommandPackage {
  name: string;
  version: string;
  build_string: string;
  channel: string;
  platform: string;
  wasm: boolean;
  modules: CommandModule[];
}
```

各字段对应 cockle-config.json 中的包配置信息。

### CommandModuleLoader 类

CommandModuleLoader（命令模块加载器）负责从 `wasmBaseUrl` 加载 WASM 和 JS 模块，并维护加载缓存以避免重复加载。

## BuiltinCommand 抽象类

BuiltinCommand（内置命令基类）为所有 TypeScript 内置命令提供基础实现：

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

子类必须实现：
- **name** 属性：返回命令名称
- **_run()** 方法：包含实际的命令执行逻辑

`run()` 方法在调用 `_run()` 之前发送 `running` 状态通知。

## 命令执行流程

典型命令执行流程：

1. **查找**：`CommandRegistry.get(name)` 根据命令名检索对应的 ICommandRunner
2. **加载**：若为 DynamicallyLoadedCommandRunner，首次执行时通过 CommandModuleLoader 懒加载模块并创建实际运行器
3. **执行**：调用 `runner.run(context)` 执行命令
4. **返回**：命令执行完毕后以 `Promise<number>` 形式返回退出码

内置命令在 Shell 初始化时通过 `registerBuiltinCommands()` 批量注册，外部命令在配置加载后通过 `registerCommandPackage()` 或 `registerExternalCommand()` 注册。

## 相关概念

- [解析器源码参考](/references/parser-source.md)：命令行分词与 AST 构建
- [内置命令源码参考](/references/builtin-source.md)：12 个内置命令完整清单
- [IO 系统源码参考](/references/io-source.md)：命令输入输出接口与实现
- [配置与环境源码参考](/references/config-source.md)：cockle-config.json 包配置格式
