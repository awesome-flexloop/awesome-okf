---
type: reference
title: 内置命令源码参考
description: Cockle 12 个内置 TypeScript 命令的完整清单、命令名和功能说明
tags:
  - cockle
  - builtin
  - commands
generated:
  at: "2026-08-22T00:00:00+08:00"
  by: okf-gen
verified:
  at: "2026-08-22T00:00:00+08:00"
  by: source-extract
status: stable
stale_after: "2027-08-22"
sources:
  - id: builtin-index
    resource: /references/builtin-source.md
    title: src/builtin/index.ts
  - id: builtin-base
    resource: /references/builtin-source.md
    title: src/builtin/builtin_command.ts
---

## 概述

Cockle 浏览器 Shell 内置了 12 个使用 TypeScript 直接实现的内置命令（Builtin Command），覆盖了 Shell 运行所必需的核心功能：别名管理、目录切换、清屏、配置管理、退出、环境变量、帮助、历史记录、变量删除、命令定位、布尔常量。所有内置命令继承自 BuiltinCommand 抽象基类，在 Shell 初始化时通过 CommandRegistry（命令注册表）自动注册，无需外部模块加载即可使用。

## BuiltinCommand 基类

所有内置命令的公共基类位于 `src/builtin/builtin_command.ts`：

```typescript
abstract class BuiltinCommand implements ICommandRunner {
  commandType = CommandType.Builtin;
  moduleName = '<builtin>';
  packageName: string;

  abstract get name(): string;
  abstract _run(context: IRunContext): Promise<number>;

  names(): string[];
  async run(context: IRunContext): Promise<number>;
}
```

### 核心机制

- **name 属性**：抽象属性，子类必须返回命令的规范名称字符串
- **_run() 方法**：抽象方法，子类实现具体的命令执行逻辑，返回退出码
- **run() 方法**：模板方法，在调用 `_run()` 之前发送 `running` 状态通知，用于 UI 状态更新
- **names() 方法**：返回命令支持的所有名称（包括别名），默认返回 `[this.name]`
- **commandType**：固定为 `CommandType.Builtin`
- **moduleName**：固定为字符串 `'<builtin>'`，标识内置来源

子类只需实现 `name` getter 和 `_run()` 方法即可完成一个内置命令的定义。

## 自动注册机制

内置命令的注册由 CommandRegistry.registerBuiltinCommands() 方法完成。该方法遍历 `src/builtin/index.ts` 的导出，自动实例化每个命令类并注册到注册表：

```typescript
// src/builtin/index.ts 导出所有内置命令类
export { AliasCommand } from './alias_command';
export { BoolCommands } from './bool_commands';
export { CdCommand } from './cd_command';
export { ClearCommand } from './clear_command';
export { CockleConfigCommand } from './cockle_config_command';
export { ExitCommand } from './exit_command';
export { ExportCommand } from './export_command';
export { HelpCommand } from './help_command';
export { HistoryCommand } from './history_command';
export { UnsetCommand } from './unset_command';
export { WhichCommand } from './which_command';
```

注册流程遍历所有导出的类，对每个类进行实例化，并调用 `_register(runner)` 将其加入命令查找表。这一设计确保新增内置命令只需在 `src/builtin/` 下创建文件并在 `index.ts` 中导出，即可自动可用，无需修改注册表代码。

## 内置命令清单

### alias / unalias — 别名管理

**类名**：AliasCommand

- **alias**：定义或显示命令别名。不带参数时列出当前所有别名；带参数时设置别名，格式为 `alias name=value`
- **unalias**：删除已定义的别名，格式为 `unalias name`

别名在分词阶段被递归展开（详见[解析器源码参考](/references/parser-source.md)中的别名展开机制）。

### cd — 切换工作目录

**类名**：CdCommand

更改当前工作目录（Change Directory）。支持：
- `cd`（无参数）：切换到用户主目录
- `cd <path>`：切换到指定路径
- `cd -`：切换到上一个工作目录
- 相对路径和绝对路径解析

### clear — 清屏

**类名**：ClearCommand

清除终端屏幕内容，将光标移至左上角。

### cockle-config — 配置管理

**类名**：CockleConfigCommand

Cockle 运行时配置管理命令，支持：
- 检查当前 Worker 类型（coincident 或 comlink）
- 切换标准输入（stdin）后端（SharedArrayBuffer / Service Worker）
- 查询和修改 Shell 运行时配置参数

### exit — 退出 Shell

**类名**：ExitCommand

退出当前 Shell 会话，可指定退出码：
- `exit`：使用最后一条命令的退出码
- `exit <code>`：使用指定的数字退出码

### export — 设置环境变量

**类名**：ExportCommand

设置或导出环境变量（Environment Variable），格式为 `export NAME=value`。不带参数时列出所有已导出的环境变量。设置的变量可被子进程（外部命令）继承。

### help — 显示帮助

**类名**：HelpCommand

显示 Shell 和内置命令的帮助信息。
- `help`：显示所有可用命令列表
- `help <command>`：显示指定命令的详细帮助

### history — 命令历史

**类名**：HistoryCommand

显示命令历史记录。支持上下方向键在交互式输入时浏览历史命令。不带参数时列出全部历史条目。

### unset — 删除环境变量

**类名**：UnsetCommand

删除指定的环境变量或 Shell 变量，格式为 `unset NAME`。与 `export` 相反，移除变量后子进程不再继承该变量。

### which — 定位命令

**类名**：WhichCommand

查找指定命令的来源和位置，显示命令是内置命令、外部命令还是 JavaScript/Wasm 动态加载命令。格式为 `which <name>`。

### true / false — 布尔常量

**类名**：BoolCommands

提供 Shell 布尔常量：
- **true**：返回退出码 0（成功）
- **false**：返回退出码 1（失败）

主要用于 Shell 脚本中的条件测试和逻辑运算。BoolCommands 类通过 `names()` 返回 `['true', 'false']` 两个名称，在一个类中实现两个命令。

## 命令汇总表

| 命令名 | 类名 | 功能 |
|--------|------|------|
| `alias` | AliasCommand | 定义/显示命令别名 |
| `unalias` | AliasCommand | 删除命令别名 |
| `cd` | CdCommand | 切换工作目录 |
| `clear` | ClearCommand | 清屏 |
| `cockle-config` | CockleConfigCommand | 配置管理与 stdin 后端切换 |
| `exit` | ExitCommand | 退出 Shell |
| `export` | ExportCommand | 设置/导出环境变量 |
| `help` | HelpCommand | 显示帮助信息 |
| `history` | HistoryCommand | 显示命令历史 |
| `unset` | UnsetCommand | 删除环境变量 |
| `which` | WhichCommand | 定位命令来源 |
| `true` | BoolCommands | 返回退出码 0 |
| `false` | BoolCommands | 返回退出码 1 |

## 执行流程

内置命令的完整执行路径：

1. 用户输入命令行字符串
2. [解析器](/references/parser-source.md)分词并构建 AST
3. Shell 遍历 AST 节点，为每个 CommandNode 查找命令
4. `CommandRegistry.get(name)` 返回对应的 BuiltinCommand 实例
5. Shell 构建 IRunContext（包含 IO、环境变量、文件系统等上下文）
6. 调用 `runner.run(context)`，基类发送 `running` 状态
7. 子类 `_run(context)` 执行具体逻辑
8. 返回数字退出码（0 表示成功，非 0 表示错误）

```typescript
// 内置命令实现示意
class MyCommand extends BuiltinCommand {
  get name(): string { return 'mycmd'; }

  async _run(context: IRunContext): Promise<number> {
    const { args, stdout } = context;
    stdout.write(`Hello from mycmd, args: ${args.join(' ')}\n`);
    return ExitCode.SUCCESS; // 0
  }
}
```

## 相关概念

- [命令系统源码参考](/references/command-source.md)：BuiltinCommand 基类与 CommandRegistry 注册机制
- [配置与环境源码参考](/references/config-source.md)：环境变量、历史记录、退出码常量
- [解析器源码参考](/references/parser-source.md)：别名展开在分词阶段的处理
- [Worker 通信源码参考](/references/worker-source.md)：命令在 Worker 中的执行环境
