---
type: concept
title: 08 - 内置命令详解
description: Cockle 12个TypeScript内置命令的完整用法：alias/cd/clear/cockle-config/exit/export/help/history/unset/which/true/false
tags: [builtin-commands, alias, cd, export, history, which, cockle-config]
generated:
  by: "agent:source-code-to-okf-wiki"
  at: "2026-08-22T00:00:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-22T00:00:00+08:00"
status: stable
stale_after: "2027-08-22"
sources:
  - id: builtin-source
    resource: /references/builtin-source.md
    title: 内置命令参考
---

# 内置命令详解

内置命令（Builtin Commands）是直接在 Cockle（浏览器Shell）Worker 线程中用 TypeScript 实现的命令，不需要下载 WASM（WebAssembly）包即可使用。它们提供 Shell 的核心功能：环境变量管理、目录切换、别名、历史记录、配置查询等。Cockle 目前内置了 12 个命令，全部在 Shell 初始化时自动注册。

## 内置命令总览

所有内置命令继承自 `BuiltinCommand` 基类，位于 src/builtin/ 目录下：

| 命令 | 功能 | 文件 |
|------|------|------|
| `alias` / `unalias` | 定义和删除命令别名 | alias_command.ts |
| `cd` | 切换工作目录 | cd_command.ts |
| `clear` | 清屏 | clear_command.ts |
| `cockle-config` | 查询和配置 Shell 参数 | cockle_config_command.ts |
| `exit` | 退出 Shell | exit_command.ts |
| `export` | 设置环境变量 | export_command.ts |
| `help` | 显示帮助信息 | help_command.ts |
| `history` | 显示命令历史 | history_command.ts |
| `unset` | 删除环境变量 | unset_command.ts |
| `which` | 查找命令位置 | which_command.ts |
| `true` / `false` | 返回 0/1 退出码 | bool_commands.ts |

### BuiltinCommand 基类

所有内置命令继承的基类定义了统一接口：

```typescript
abstract class BuiltinCommand {
  abstract readonly name: string;
  abstract readonly description: string;
  
  // 执行命令，返回退出码（0=成功，非0=失败）
  abstract run(
    args: string[],
    context: IRunContext
  ): Promise<number> | number;
  
  // 可选的Tab补全
  tabComplete?(
    args: string[],
    context: ITabCompleteContext
  ): ITabCompleteResult;
}
```

### 自动注册机制

内置命令通过 src/builtin/index.ts 自动注册到命令注册表（CommandRegistry）：

```typescript
// src/builtin/index.ts
import { CommandRegistry } from '../commands';
import { AliasCommand } from './alias_command';
import { CdCommand } from './cd_command';
import { ClearCommand } from './clear_command';
// ... 其他命令导入

export function registerBuiltinCommands(registry: CommandRegistry): void {
  registry.registerCommand(new AliasCommand());
  registry.registerCommand(new CdCommand());
  registry.registerCommand(new ClearCommand());
  registry.registerCommand(new CockleConfigCommand());
  registry.registerCommand(new ExitCommand());
  registry.registerCommand(new ExportCommand());
  registry.registerCommand(new HelpCommand());
  registry.registerCommand(new HistoryCommand());
  registry.registerCommand(new UnsetCommand());
  registry.registerCommand(new WhichCommand());
  registry.registerCommand(new TrueCommand());
  registry.registerCommand(new FalseCommand());
}
```

Shell 初始化时调用 `registerBuiltinCommands()` 完成注册。内置命令优先级最高，会覆盖同名的 WASM 或外部命令。

## alias / unalias

`alias` 命令用于定义命令别名，可以为长命令创建简写，或者为命令添加默认参数。`unalias` 删除已定义的别名。

### 基本用法

```bash
# 定义别名
alias ll='ls -la'
alias gs='git status'
alias grep='grep --color=auto'

# 查看所有别名
alias

# 查看特定别名
alias ll

# 使用别名
ll          # 等同于 ls -la
ll /drive   # 等同于 ls -la /drive

# 删除别名
unalias ll
unalias gs grep  # 一次删除多个
```

### 递归解析

Cockle 的别名支持递归解析（getRecursive），但有循环检测防止无限递归：

```typescript
// Alias.getRecursive 简化逻辑
getRecursive(name: string): string | undefined {
  const visited = new Set<string>();
  let current = name;
  
  while (this._aliases.has(current)) {
    if (visited.has(current)) {
      break;  // 检测到循环，停止解析
    }
    visited.add(current);
    current = this._aliases.get(current)!;
    // 别名值可能是"cmd args"格式，取第一个词继续解析
    current = current.split(/\s+/)[0];
  }
  
  return this._aliases.get(current) ?? this._aliases.get(name);
}
```

### 别名包含管道和重定向

别名的值可以包含管道和重定向，解析时会正确处理：

```bash
alias mkcd='mkdir -p $1 && cd $1'
alias log='echo "[$(date)]" >> /drive/shell.log'
alias lsg='ls | grep'
```

注意：别名不支持参数占位符（如 `$1`），上述 `mkcd` 只是示例。如果需要参数化的命令封装，请使用外部命令或 JavaScript 命令。

### 别名持久化

别名在当前 Shell 会话中有效，页面刷新后会重置。要持久化别名，可以在初始化时通过 `initialFiles` 创建启动脚本或使用 `cockle-config.json` 的 `aliases` 字段：

```json
{
  "aliases": {
    "ll": "ls -la",
    "gs": "git status",
    "la": "ls -a"
  }
}
```

## cd

`cd`（change directory）命令切换当前工作目录。

### 基本用法

```bash
# 切换到指定目录
cd /drive/documents

# 切换到上一个目录（OLDPWD）
cd -

# 无参数：切换到初始工作目录（即启动Shell时的cwd）
cd

# 相对路径
cd ../projects
cd ./notes
```

### 实现要点

`cd` 命令修改 Shell 的当前工作目录状态：

```typescript
class CdCommand extends BuiltinCommand {
  name = 'cd';
  
  run(args: string[], context: IRunContext): number {
    const { env, fs } = context;
    const oldCwd = fs.cwd();
    let target: string;
    
    if (args.length === 0) {
      // 无参数：回到初始目录
      target = context.initialCwd;
    } else if (args[0] === '-') {
      // cd -：回到上一个目录
      target = env.get('OLDPWD') || oldCwd;
      context.stdout.write(target + '\n');
    } else {
      target = args[0];
    }
    
    try {
      fs.chdir(target);
      env.set('OLDPWD', oldCwd);
      env.set('PWD', fs.cwd());
      return 0;
    } catch (e) {
      context.stderr.write(`cd: no such file or directory: ${target}\n`);
      return 1;
    }
  }
}
```

### 路径解析规则

- 绝对路径以 `/` 开头，从根目录解析
- 相对路径相对于当前工作目录（`PWD`）解析
- `..` 表示上一级目录
- `.` 表示当前目录
- 路径中的 `~` 不会自动展开为 HOME（Cockle 没有 HOME 目录概念）

## clear

`clear` 命令清空终端屏幕。

### 基本用法

```bash
clear
```

### 实现原理

`clear` 命令发送 ANSI 转义序列 `\x1b[2J\x1b[H`（清屏并移动光标到左上角）：

```typescript
class ClearCommand extends BuiltinCommand {
  name = 'clear';
  
  run(_args: string[], context: IRunContext): number {
    // \x1b[2J = 清除整个屏幕
    // \x1b[H  = 光标移到左上角 (1,1)
    context.stdout.write('\x1b[2J\x1b[H');
    return 0;
  }
}
```

这个 ANSI 序列被 xterm.js 终端识别并执行清屏操作。用户也可以使用 Ctrl+L 快捷键清屏（xterm.js 内置绑定）。

## cockle-config

`cockle-config` 是 Cockle 特有的配置命令，用于查询 Shell 运行状态和动态切换配置。

### 子命令

```bash
# 检查当前Worker类型
cockle-config worker
# 输出: "comlink" 或 "coincident"

# 检查当前stdin后端
cockle-config stdin
# 输出: "sab" 或 "sw"

# 切换stdin后端为SAB模式
cockle-config stdin sab

# 切换stdin后端为Service Worker模式
cockle-config stdin sw
```

### worker 子命令

`cockle-config worker` 返回当前使用的 Worker 通信模式：

- **comlink**：使用 Comlink 库的 RPC（远程过程调用）模式，兼容性好，端口 4500
- **coincident**：使用 Coincident 库的直接代理模式，支持 SAB 同步 stdin，端口 4501

### stdin 子命令

`cockle-config stdin` 用于查询和切换 stdin 后端。切换时会自动处理 IO 的禁用/启用流程，确保不会丢失输入。

注意：切换到 `sab` 需要页面处于 crossOriginIsolated 状态（发送了 COOP/COEP 头），否则会报错。

## exit

`exit` 命令退出当前 Shell 会话。

### 基本用法

```bash
# 以0（成功）状态退出
exit

# 以指定退出码退出
exit 1
exit 42
```

### 实现要点

```typescript
class ExitCommand extends BuiltinCommand {
  name = 'exit';
  
  run(args: string[], context: IRunContext): number {
    const exitCode = args.length > 0 ? parseInt(args[0], 10) : 0;
    // 设置退出码，通知Shell退出
    context.exit(exitCode);
    return exitCode;
  }
}
```

调用 `exit` 后，Shell 会停止接受新命令，触发 `onExit` 回调，宿主应用可以据此进行清理操作。

### 退出码约定

- `0`：成功
- `1`：一般错误
- `2`：误用命令（语法错误等）
- `127`：命令未找到
- `130`：被 Ctrl+C 中断

## export

`export` 命令设置和查看环境变量。环境变量是传递给子命令的键值对。

### 基本用法

```bash
# 设置环境变量
export MY_VAR=hello
export PATH=/usr/local/bin:/usr/bin
export COCKLE_DARK_MODE=1

# 设置包含空格的值
export GREETING="Hello World"

# 查看单个变量
export MY_VAR
echo $MY_VAR

# 查看所有环境变量
export

# 在命令中使用环境变量
echo "My var is: $MY_VAR"
```

### 环境变量命名规则

环境变量名必须匹配正则 `/^[A-Za-z_][A-Za-z0-9_]*]/`：
- 以字母或下划线开头
- 后续可以是字母、数字、下划线
- 小写变量名是合法的，但按惯例使用大写

### Environment 类

环境变量由 `Environment` 类管理，它继承自 `Map<string, string>`：

```typescript
class Environment extends Map<string, string> {
  // 默认环境变量
  constructor() {
    super();
    this.set('TERM', 'xterm-256color');
    this.set('TERMINFO', '/usr/local/share/terminfo');
    // PS1: 绿色的 "js-shell: " 提示符
    this.set('PS1', '\x1b[32mjs-shell: \x1b[0m');
  }
  
  // 复制环境变量到命令上下文
  copyIntoCommand(env: Record<string, string>): void {
    for (const [key, value] of this) {
      env[key] = value;
    }
  }
  
  // 获取数字类型的环境变量
  getNumber(key: string, defaultValue: number = 0): number {
    const value = this.get(key);
    if (value === undefined) return defaultValue;
    const num = parseInt(value, 10);
    return isNaN(num) ? defaultValue : num;
  }
  
  // 获取提示符字符串（解析PS1中的转义）
  getPrompt(): string {
    return this.get('PS1') || '$ ';
  }
  
  // 获取是否支持彩色输出
  get color(): boolean {
    const term = this.get('TERM') || '';
    return term.includes('xterm') || term.includes('color');
  }
  
  // 获取所有合法的环境变量名
  names(): string[] {
    return Array.from(this.keys()).filter(k => /^[A-Za-z_]/.test(k));
  }
  
  // 设置终端大小
  setSize(lines: number, columns: number): void {
    this.set('LINES', String(lines));
    this.set('COLUMNS', String(columns));
  }
}
```

### 默认环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `COCKLE_SHELL_ID` | 自动生成 | Shell 实例唯一 ID |
| `COCKLE_BROWSING_CONTEXT_ID` | 构造参数 | 浏览上下文 ID |
| `PS1` | 绿色提示符 | 主提示符字符串 |
| `TERM` | `xterm-256color` | 终端类型，启用 256 色 |
| `TERMINFO` | `/usr/local/share/terminfo` | terminfo 数据库路径 |
| `?` | `0` | 上一个命令的退出码 |
| `LINES` / `COLUMNS` | 终端尺寸 | 终端行列数 |
| `COCKLE_DARK_MODE` | `0` | 暗色模式（`1`=开启） |

## help

`help` 命令显示所有可用命令的帮助信息。

### 基本用法

```bash
# 显示所有命令列表和简要说明
help

# 显示特定命令的帮助
help cd
help export
```

### 输出示例

```
js-shell: help
Builtin commands:
  alias       Define or display aliases
  cd          Change the working directory
  clear       Clear the terminal screen
  cockle-config  Configure Cockle shell settings
  exit        Exit the shell
  export      Set or display environment variables
  help        Display help information
  history     Display command history
  unset       Remove environment variables
  which       Locate a command
  true        Return 0 exit code
  false       Return 1 exit code

WASM commands:
  cat, cp, echo, git, grep, ls, mkdir, mv, ...

External commands:
  (registered external commands)
```

`help` 命令从 `CommandRegistry` 获取所有已注册的命令（包括内置、WASM、外部），按类型分组显示。

## history

`history` 命令显示命令历史记录。

### 基本用法

```bash
# 显示所有历史记录
history

# 显示最近N条记录
history 10
```

### 历史导航

除了 `history` 命令，用户还可以使用键盘快捷键浏览历史：

- **↑ / Ctrl+P**：上一条命令
- **↓ / Ctrl+N**：下一条命令
- **Ctrl+R**：反向搜索历史

### History 类

历史记录由 `History` 类管理：

```typescript
class History {
  private _entries: string[] = [];
  private _current: number = -1;
  
  // 添加命令到历史
  add(command: string): void {
    // 不添加空命令和重复命令
    if (command.trim() && 
        (this._entries.length === 0 || 
         this._entries[this._entries.length - 1] !== command)) {
      this._entries.push(command);
    }
    this._current = this._entries.length;
  }
  
  // 获取指定索引的历史记录
  at(index: number): string | undefined {
    return this._entries[index];
  }
  
  // 获取当前滚动位置的条目（上下键浏览）
  scrollCurrent(direction: 'up' | 'down'): string | undefined {
    if (direction === 'up' && this._current > 0) {
      this._current--;
      return this._entries[this._current];
    }
    if (direction === 'down' && this._current < this._entries.length - 1) {
      this._current++;
      return this._entries[this._current];
    }
    return undefined;
  }
  
  get entries(): string[] {
    return [...this._entries];
  }
}
```

历史记录仅在当前会话中保存，页面刷新后清空。

## unset

`unset` 命令删除环境变量。

### 基本用法

```bash
# 设置变量
export MY_VAR=hello
echo $MY_VAR  # 输出: hello

# 删除变量
unset MY_VAR
echo $MY_VAR  # 输出: （空字符串）

# 删除多个变量
unset VAR1 VAR2 VAR3
```

### 实现要点

```typescript
class UnsetCommand extends BuiltinCommand {
  name = 'unset';
  
  run(args: string[], context: IRunContext): number {
    for (const name of args) {
      if (context.env.has(name)) {
        context.env.delete(name);
      }
    }
    return 0;
  }
}
```

`unset` 不能删除只读变量（目前 Cockle 没有实现只读变量，但会保留部分核心变量如 `TERM`）。

## which

`which` 命令查找命令的位置，显示命令类型。

### 基本用法

```bash
which cd       # 输出: cd: shell builtin
which ls       # 输出: ls: wasm command (coreutils)
which mycmd    # 输出: mycmd: external command
which nosuch   # 无输出，返回退出码1
```

### 命令类型

`which` 返回的命令类型包括：

| 类型 | 说明 |
|------|------|
| `shell builtin` | 内置命令，TypeScript 实现 |
| `wasm command (<package>)` | WASM 命令，来自指定包 |
| `javascript command (<module>)` | JavaScript 命令 |
| `external command` | 外部命令，主线程注册 |
| `aliased to <value>` | 别名，展开为指定值 |

### 查找顺序

命令查找遵循以下优先级：

1. 别名（alias）
2. 内置命令（builtin）
3. 外部命令（external）
4. WASM/JavaScript 命令（dynamically loaded）

`which` 按这个顺序查找，返回第一个匹配的类型。

## true / false

`true` 和 `false` 是两个简单的布尔命令，分别返回 0（成功）和 1（失败）退出码，用于 Shell 脚本中的条件测试。

### 基本用法

```bash
# true 总是返回0
true
echo $?  # 输出: 0

# false 总是返回1
false
echo $?  # 输出: 1

# 用于条件
if true; then
  echo "This always runs"
fi

# 用于无限循环
while true; do
  echo "looping..."
  break
done
```

### 实现要点

```typescript
class TrueCommand extends BuiltinCommand {
  name = 'true';
  run(): number { return 0; }
}

class FalseCommand extends BuiltinCommand {
  name = 'false';
  run(): number { return 1; }
}
```

## 退出码含义

Cockle 定义了标准退出码常量，位于 exit_code.ts：

```typescript
enum ExitCode {
  SUCCESS = 0,           // 命令成功执行
  GENERAL_ERROR = 1,     // 一般错误
  MISUSE = 2,            // 命令误用（参数错误等）
  CANNOT_EXECUTE = 126,  // 无法执行（权限问题等）
  NOT_FOUND = 127,       // 命令未找到
  INVALID_EXIT = 128,    // 无效的exit参数
  INTERRUPTED = 130,     // 被Ctrl+C中断（SIGINT）
}
```

上一个命令的退出码存储在特殊环境变量 `?` 中：

```bash
ls /nonexistent
echo $?  # 输出: 1（因为文件不存在）

true
echo $?  # 输出: 0

false
echo $?  # 输出: 1
```

## 相关概念

- [03 - 命令系统](03-command-system.md)：命令注册表和命令运行器
- [09 - 外部命令](09-external-commands.md)：主线程注册的自定义命令
- [10 - WASM 与 JavaScript 命令](10-wasm-js-commands.md)：动态加载的 WASM/JS 命令
- [Shell API 参考](../references/shell-api.md)：Shell 构造函数和 API
- [内置命令参考](../references/builtin-source.md)：内置命令完整接口定义
