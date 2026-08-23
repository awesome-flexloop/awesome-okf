---
type: example
title: "02 - 使用命令：管道、重定向和别名"
description: 演示管道（|）、重定向（>/>>/<）、别名定义和环境变量的实际用法
tags: [example, pipe, redirect, alias, environment-variables, builtin]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: parsing-pipeline
    resource: /concepts/04-parsing-pipeline.md
    title: 命令解析管线
  - id: builtin-commands
    resource: /concepts/08-builtin-commands.md
    title: 内置命令详解
related_concepts: [/concepts/04-parsing-pipeline.md, /concepts/05-io-system.md, /concepts/08-builtin-commands.md, /concepts/03-command-system.md]
---

## 目标

本示例演示 Cockle Shell 中命令行的高级用法，涵盖：

1. **管道（Pipe）**：使用 `|` 将一个命令的输出连接到另一个命令的输入
2. **重定向（Redirect）**：使用 `>`、`>>`、`<` 控制命令的输入输出流向
3. **别名（Alias）**：使用 `alias` 和 `unalias` 定义和删除命令别名
4. **环境变量（Environment Variables）**：使用 `export`、`unset` 和 `$VAR` 语法管理环境变量

这些功能与传统 Unix Shell（如 Bash）类似，让你在浏览器中也能使用熟悉的命令行操作。

## 管道示例

管道操作符 `|` 将前一个命令的标准输出（stdout）连接到后一个命令的标准输入（stdin）。Cockle 支持多级管道串联。

### 示例：统计文件数量

```bash
# 列出当前目录文件，通过管道传给 wc -l 统计行数（即文件数）
ls | wc -l
```

### 示例：过滤文件内容

首先需要有一个文件用于测试。Cockle 启动时可以通过 `initialFiles` 选项预置文件，也可以通过 `echo` 命令创建：

```bash
# 创建一个包含多行文本的文件
echo -e "apple\nbanana\ncherry\napple\ndate" > fruits.txt

# 使用 grep 过滤包含 "apple" 的行
cat fruits.txt | grep apple
```

### 示例：多级管道

```bash
# 创建一个月份文件（预置或通过 echo 创建）
# 然后：列出内容 → 排序 → 去重 → 统计行数
cat months.txt | sort | uniq | wc -l
```

在 TypeScript 中发送管道命令的方式与普通命令相同，因为命令行解析由 Shell 内部完成：

```typescript
// 发送管道命令，Shell 会自动解析 | 并连接管道
await shell.input('ls | wc -l\r');
```

## 重定向示例

Cockle 支持标准的输入输出重定向语法。

### 输出重定向（覆盖写入）

使用 `>` 将命令输出写入文件，覆盖文件原有内容：

```bash
# 将 echo 的输出写入文件（覆盖）
echo "Hello, Cockle!" > greeting.txt

# 将 ls 的输出保存到文件列表
ls -la > file-list.txt

# 将多个命令的输出合并（通过子命令）
echo "=== System Info ===" > info.txt
```

### 输出追加重定向（追加写入）

使用 `>>` 将命令输出追加到文件末尾：

```bash
# 追加内容到文件
echo "First line" > log.txt
echo "Second line" >> log.txt
echo "Third line" >> log.txt
cat log.txt
# 输出：
# First line
# Second line
# Third line
```

### 输入重定向

使用 `<` 从文件读取内容作为命令的标准输入：

```bash
# 创建文件
echo -e "line1\nline2\nline3" > test.txt

# 从文件读取内容传给 wc 统计
wc -l < test.txt
# 输出：3

# 从文件读取内容传给 grep 过滤
grep line < test.txt
```

### 错误重定向

使用 `2>` 将标准错误（stderr）重定向：

```bash
# 将错误输出重定向到文件
ls non-existent-file 2> error.txt
cat error.txt
```

在 TypeScript 代码中，重定向命令的发送方式：

```typescript
// 创建文件并写入内容
await shell.input('echo "hello world" > test.txt\r');

// 等待命令执行完成后再发送下一个
setTimeout(async () => {
  await shell.input('cat < test.txt\r');
}, 300);
```

## 别名示例

别名（Alias）允许你为常用命令创建简短的替代名称。Cockle 提供了内置的 `alias` 和 `unalias` 命令。

### 定义别名

```bash
# 定义 ll 为 ls -la（详细列表）
alias ll='ls -la'

# 定义常用快捷命令
alias gs='git status'
alias la='ls -a'
alias l='ls -CF'

# 定义后直接使用别名即可
ll
```

### 查看已定义的别名

```bash
# 直接输入 alias 不带参数，列出所有别名
alias
```

### 删除别名

```bash
# 删除 ll 别名
unalias ll

# 再次使用 ll 将报错：command not found
```

### 通过 Shell 选项预定义别名

在创建 Shell 实例时，可以通过 `aliases` 选项预定义别名，这样 Shell 启动后立即可用：

```typescript
const shell = new Shell({
  baseUrl,
  wasmBaseUrl: baseUrl,
  outputCallback,
  browsingContextId,
  shellManager,
  aliases: {
    ll: 'ls -la',
    la: 'ls -a',
    gs: 'git status',
    grep: 'grep --color=auto',
    ls: 'ls --color=auto'
  }
});
```

此外，`cockle-config.json` 配置文件中也可以定义全局别名（详见 [/examples/04-custom-config.md](/examples/04-custom-config.md)）。

## 环境变量示例

环境变量用于存储 Shell 和命令的配置信息。Cockle 提供 `export`（设置）、`unset`（删除）命令，并支持 `$VAR_NAME` 变量替换语法。

### 设置环境变量

```bash
# 设置环境变量
export MY_NAME="Cockle Browser"
export EDITOR=vim
export PAGER=less

# 使用 $ 前缀引用变量
echo $MY_NAME
# 输出：Cockle Browser

# 在命令中使用变量
echo "Editor is $EDITOR, Pager is $PAGER"
```

### 查看环境变量

```bash
# env 命令列出所有环境变量
env

# echo 查看单个变量
echo $TERM
# 默认输出：xterm-256color

echo $PS1
# 默认输出包含绿色 "js-shell: " 提示符配置
```

### 删除环境变量

```bash
# 设置变量
export TEMP_VAR=test
echo $TEMP_VAR  # 输出 test

# 删除变量
unset TEMP_VAR
echo $TEMP_VAR  # 输出空行
```

### 通过 Shell 选项预定义环境变量

创建 Shell 时可以通过 `environment` 选项预设环境变量：

```typescript
const shell = new Shell({
  baseUrl,
  wasmBaseUrl: baseUrl,
  outputCallback,
  browsingContextId,
  shellManager,
  environment: {
    EDITOR: 'vim',
    PAGER: 'less',
    MY_APP_DIR: '/drive/app',
    // 设置为 undefined 表示不设置（或取消继承的变量）
    // UNWANTED_VAR: undefined
  }
});
```

Cockle 默认设置的环境变量包括：
- `PS1`：Shell 提示符（绿色 "js-shell: "）
- `TERM=xterm-256color`：终端类型声明
- `COCKLE_DARK_MODE`：由 `themeChange()` 控制，影响颜色方案

## 完整交互脚本

下面是一个完整的 TypeScript 示例，演示如何按序发送一系列命令并观察管道、重定向、别名和环境变量的效果：

```typescript
import { Shell, ShellManager } from '@jupyterlite/cockle';

async function runCommandsDemo(outputCallback: (text: string) => void) {
  const baseUrl = window.location.href;
  const shellManager = new ShellManager();
  const browsingContextId = await shellManager.installServiceWorker(baseUrl);

  const shell = new Shell({
    baseUrl,
    wasmBaseUrl: baseUrl,
    outputCallback,
    browsingContextId,
    shellManager,
    color: true,
    initialFiles: {
      'months.txt': 'January\nFebruary\nMarch\nApril\nMay\nJune\n'
    },
    aliases: {
      ll: 'ls -la'
    },
    environment: {
      GREETING: 'Hello from Cockle'
    }
  });

  // 监听命令状态
  shell.commandStateChanged.connect((_, args) => {
    if (args.state === 'finished') {
      console.log(`命令 #${args.commandId} 完成，退出码: ${args.exitCode}`);
    }
  });

  await shell.ready;
  await shell.start();
  shell.setSize({ rows: 40, columns: 120 });

  // 辅助函数：发送命令并等待一段时间
  const send = (cmd: string, delayMs = 400) =>
    new Promise<void>(resolve => {
      shell.input(cmd + '\r');
      setTimeout(resolve, delayMs);
    });

  // --- 别名演示 ---
  await send('alias');                          // 列出所有别名
  await send('ll');                             // 使用预定义别名
  await send("alias gs='git status'");          // 定义新别名
  await send('alias');                          // 确认别名已添加
  await send('unalias gs');                     // 删除别名

  // --- 环境变量演示 ---
  await send('echo $GREETING');                 // 使用预定义变量
  await send('export MY_VAR=world');            // 设置新变量
  await send('echo "Hello, $MY_VAR!"');         // 变量替换
  await send('env | grep MY_VAR');              // 管道：env 输出过滤
  await send('unset MY_VAR');                   // 删除变量
  await send('echo $MY_VAR');                   // 验证已删除（空）

  // --- 重定向演示 ---
  await send('echo "line one" > out.txt');      // 创建文件
  await send('echo "line two" >> out.txt');     // 追加
  await send('echo "line three" >> out.txt');   // 追加
  await send('cat out.txt');                    // 查看文件内容
  await send('wc -l < out.txt');                // 输入重定向统计行数

  // --- 管道演示 ---
  await send('ls');                             // 列出文件
  await send('ls | wc -l');                     // 管道统计文件数
  await send('cat months.txt | wc -w');         // 统计月份文件的单词数
  await send('cat months.txt | grep J');        // 过滤以 J 开头的月份

  // --- 组合演示：管道 + 重定向 ---
  await send('cat months.txt | sort > sorted.txt');  // 排序后保存
  await send('cat sorted.txt');                      // 查看排序结果

  // 获取最后退出码
  const exitCode = await shell.exitCode();
  console.log('最终退出码:', exitCode);
}

// 使用方式
runCommandsDemo((text) => {
  const clean = text.replace(/\x1b\[[0-9;]*m/g, '');
  const terminal = document.getElementById('terminal') as HTMLElement;
  terminal.textContent += clean;
  terminal.scrollTop = terminal.scrollHeight;
});
```

## 注意事项

### 通配符

Cockle 支持基本的文件名通配符（Globbing）：
- `*`：匹配任意数量的任意字符
- `?`：匹配单个任意字符

```bash
ls *.txt          # 列出所有 .txt 文件
ls ?.txt          # 列出单字符文件名的 .txt 文件
```

### 引号处理

当文件名或参数包含空格时，需要使用引号包裹：

```bash
# 文件名包含空格需要引号
echo "content with spaces" > "my file.txt"
cat "my file.txt"

# 单引号内不进行变量替换
echo '$HOME'     # 输出 $HOME（字面量）
echo "$HOME"     # 输出变量值
```

### 内置命令

Cockle 的内置命令（builtin commands）包括：`alias`、`cd`、`clear`、`cockle-config`、`exit`、`export`、`help`、`history`、`unset`、`which`、`true`、`false`。这些命令在 Shell 内部直接执行，不依赖 WASM 包。其他命令（如 `ls`、`cat`、`grep`、`wc` 等）来自 coreutils 等 WASM 命令包，需要确保 `wasmBaseUrl` 目录中包含相应的包文件。

### 管道中的错误处理

管道中每个命令独立运行，最后一个命令的退出码即为整个管道的退出码。如果需要前面命令失败时停止执行，Cockle 暂不支持 Bash 的 `set -o pipefail` 选项，可以在外部 TypeScript 代码中通过 `shell.exitCode()` 检查每个命令的结果。

## 相关概念

- [命令解析管线](/concepts/04-parsing-pipeline.md)
- [IO 系统](/concepts/05-io-system.md)
- [内置命令详解](/concepts/08-builtin-commands.md)
- [命令系统](/concepts/03-command-system.md)
