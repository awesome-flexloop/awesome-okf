---
type: reference
title: 配置与环境源码参考
description: Environment、Aliases、History、Termios、cockle-config.json 配置格式参考
tags:
  - cockle
  - environment
  - config
  - aliases
  - history
  - termios
generated:
  at: "2026-08-22T00:00:00+08:00"
  by: okf-gen
verified:
  at: "2026-08-22T00:00:00+08:00"
  by: source-extract
status: stable
stale_after: "2027-08-22"
sources:
  - id: env
    resource: /references/config-source.md
    title: src/environment.ts
  - id: exit-codes
    resource: /references/config-source.md
    title: src/exit_code.ts
  - id: ansi
    resource: /references/config-source.md
    title: src/ansi.ts
---

## 概述

Cockle 浏览器 Shell 的配置与环境系统管理 Shell 运行时的全局状态，包括环境变量（Environment）、命令别名（Aliases）、命令历史（History）、终端属性（Termios）以及 ANSI 转义序列工具。配置通过 `cockle-config.json` 文件声明命令包、别名和环境变量的初始值，在 Shell 初始化时加载。环境变量类继承自 `Map<string, string>`，提供类型安全的访问方法和默认值设置。

## Environment 类

Environment（环境）类继承自 `Map<string, string>`，存储 Shell 环境变量。

### 构造函数与默认值

Environment 构造函数自动设置以下默认环境变量：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `COCKLE_SHELL_ID` | 自动生成 | 当前 Shell 实例的唯一标识符 |
| `COCKLE_BROWSING_CONTEXT_ID` | 自动生成 | 浏览上下文 ID，用于 Service Worker 路由 |
| `PS1` | 绿色 `"js-shell: "`（彩色模式）/ 纯文本（无色模式） | 主提示符字符串 |
| `TERM` | `xterm-256color`（彩色模式）/ 未设置（无色模式） | 终端类型声明 |
| `TERMINFO` | `/usr/local/share/terminfo` | Terminfo 数据库路径（供 nano 等命令使用） |
| `?` | `"0"` | 最后一条命令的退出码（字符串形式） |

彩色模式取决于 `TERM` 变量是否设置。PS1 提示符在彩色模式下包含 ANSI 绿色转义序列。

### 方法

```typescript
class Environment extends Map<string, string> {
  copyIntoCommand(target: Record<string, string>): void;
  getNumber(key: string): number | null;
  getPrompt(): string;
  get color(): boolean;
  names(): string[];
  setSize(size: { rows: number; cols: number }): void;
}
```

- **copyIntoCommand(target)**：将当前环境变量复制到目标对象中，用于外部命令执行时传递环境
- **getNumber(key)**：获取环境变量的数值形式，若不存在或无法解析为数字则返回 `null`
- **getPrompt()**：获取当前提示符字符串（PS1），用于每次命令输入前的显示
- **color**：只读属性，返回是否启用彩色模式（`TERM` 变量已设置即为彩色）
- **names()**：返回所有合法环境变量名的数组，仅包含以字母或下划线开头（匹配 `/^[A-Za-z_]/`）的变量
- **setSize(size)**：设置终端窗口大小，更新 `LINES` 和 `COLUMNS` 环境变量

### 特殊环境变量

- **`?`**：存储上一条命令的退出码，以字符串形式保存。每次命令执行完毕后自动更新
- **COCKLE_DARK_MODE**：深色模式标志，`'1'` 表示深色主题，`'0'` 表示浅色主题。由主题切换事件更新
- **LINES / COLUMNS**：终端行数和列数，通过 `setSize()` 设置，供需要感知终端尺寸的命令使用

## Aliases 类

Aliases（别名）类管理命令别名映射：

```typescript
class Aliases {
  get(key: string): string | undefined;
  set(key: string, value: string): void;
  delete(key: string): boolean;
  getRecursive(value: string): string;
}
```

核心方法是 **getRecursive(value)**：在分词阶段用于别名递归展开。当别名值本身引用另一个别名时，该方法递归解析直到得到最终的命令字符串，防止无限递归。

别名展开机制详见[解析器源码参考](/references/parser-source.md)。

## History 类

History（历史记录）类管理命令行历史：

```typescript
class History {
  add(cmdText: string): void;
  at(index: number): string;
  scrollCurrent(down: boolean): string | null;
}
```

- **add(cmdText)**：向历史记录添加一条命令文本
- **at(index)**：获取指定索引位置的历史命令
- **scrollCurrent(down)**：用于上下方向键导航历史记录。`down=false` 向上浏览更早的命令，`down=true` 向下浏览更近的命令，返回当前选中的历史命令文本或 `null`（表示已到边界）

历史记录在交互式输入时通过上下箭头键调用 `scrollCurrent()` 实现快速调用之前的命令。

## ExitCode 常量

ExitCode（退出码）模块定义了标准退出码常量：

```typescript
namespace ExitCode {
  const SUCCESS = 0;
  const GENERAL_ERROR = 1;
  const IMPROPER_USE = 2;
  const CANNOT_RUN_COMMAND = 126;
  const CANNOT_FIND_COMMAND = 127;
}
```

| 常量 | 值 | 含义 |
|------|----|------|
| SUCCESS | 0 | 命令成功执行 |
| GENERAL_ERROR | 1 | 一般性错误 |
| IMPROPER_USE | 2 | 命令使用不当（参数错误等） |
| CANNOT_RUN_COMMAND | 126 | 找到命令但无法执行（权限不足等） |
| CANNOT_FIND_COMMAND | 127 | 找不到指定命令 |

退出码遵循 POSIX 惯例，其中 126 和 127 与 Bash 行为一致。

## Termios 类

Termios（终端 I/O 设置）类管理终端的输入输出属性：

```typescript
class Termios {
  setDefaultShell(): void;
  setDefaultWasm(): void;
  setRawMode(enable: boolean): void;
  set(flags: TermiosFlags): void;
}
```

- **setDefaultShell()**：设置 Shell 内置命令的默认终端模式（行缓冲、回显等）
- **setDefaultWasm()**：设置 WASM 外部命令的默认终端模式
- **setRawMode(enable)**：启用/禁用原始模式（raw mode）。原始模式下输入字符立即传递给程序，不进行行缓冲和回显，用于 vim、nano 等全屏编辑器
- **set(flags)**：设置具体的 termios 标志位

## cockle-config.json 配置格式

cockle-config.json 是 Cockle 的主配置文件，定义可用命令包、初始别名和环境变量：

```json
{
  "packages": {
    "<package-name>": {
      "version": "1.0.0",
      "build_string": "h1234567_0",
      "channel": "conda-forge",
      "platform": "emscripten-wasm32",
      "wasm": true,
      "modules": {
        "<module-name>": {
          "commands": "cmd1,cmd2,cmd3"
        }
      }
    }
  },
  "aliases": {
    "ll": "ls -la",
    "gs": "git status"
  },
  "environment": {
    "PATH": "/usr/local/bin:/usr/bin",
    "EDITOR": "vim"
  }
}
```

各字段说明：
- **packages**：命令包定义字典，键为包名。每个包包含版本、构建标识、发布渠道、目标平台、是否为 WASM、以及模块列表
- **modules**：包内模块字典，键为模块名。每个模块的 `commands` 字段是逗号分隔的命令名列表
- **aliases**：可选，初始别名字典 `{别名: 展开值}`
- **environment**：可选，初始环境变量字典 `{变量名: 值}`
- **cockle_fs 包**：配置中必须包含 `cockle_fs` 包，提供文件系统运行时支持

配置在 Shell 初始化时加载，packages 中的命令通过 CommandModuleLoader 按需加载，aliases 和 environment 在 Environment/Aliases 初始化时应用。

## DownloadTracker 类

DownloadTracker（下载追踪器）类在 WASM 模块加载过程中显示下载进度：

```typescript
class DownloadTracker {
  // 监听模块下载进度
  // 在终端中显示进度条或状态信息
}
```

当 WASM 命令首次执行触发模块懒加载时，DownloadTracker 负责向用户显示下载状态，避免因大文件下载导致用户误以为 Shell 无响应。

## ansi 工具对象

ansi 对象提供常用的 ANSI 转义序列生成方法：

```typescript
namespace ansi {
  function cursorLeft(n: number): string;
  function cursorRight(n: number): string;
  function eraseEndLine(): string;
  function eraseStartLine(): string;
  const styleRed: string;
  const styleGreen: string;
  const styleReset: string;
  const styleBoldRed: string;
  const styleBoldGreen: string;
  const styleBrightRed: string;
}
```

| 方法/常量 | 用途 |
|-----------|------|
| `cursorLeft(n)` | 光标左移 n 个字符 |
| `cursorRight(n)` | 光标右移 n 个字符 |
| `eraseEndLine()` | 从光标位置擦除到行尾 |
| `eraseStartLine()` | 从行首擦除到光标位置 |
| `styleRed` | 设置红色文本样式 |
| `styleGreen` | 设置绿色文本样式 |
| `styleReset` | 重置所有样式 |
| `styleBoldRed` | 设置粗体红色文本 |
| `styleBoldGreen` | 设置粗体绿色文本 |
| `styleBrightRed` | 设置亮红色文本 |

这些工具函数/常量返回 ANSI 转义字符串，主要用于 PS1 提示符着色、错误信息高亮和终端清屏/光标移动操作。

## 初始化流程

1. 创建 Environment 实例，设置默认变量
2. 加载 cockle-config.json，合并 environment 字段中的自定义变量
3. 创建 Aliases 实例，加载配置中的 aliases
4. 创建 History 实例
5. 创建 Termios 实例，设置默认 Shell 终端模式
6. 命令包信息存入 CommandModuleLoader，等待按需加载

## 相关概念

- [内置命令源码参考](/references/builtin-source.md)：export/unset/cockle-config 等操作环境变量的命令
- [命令系统源码参考](/references/command-source.md)：CommandModuleLoader 从配置加载命令包
- [Worker 通信源码参考](/references/worker-source.md)：Worker 端环境初始化与 Termios 跨线程同步
- [缓冲 IO 源码参考](/references/buffered-io-source.md)：stdin 后端切换与环境配置的关联
