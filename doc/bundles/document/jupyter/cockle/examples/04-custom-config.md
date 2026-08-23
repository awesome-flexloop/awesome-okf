---
type: example
title: "04 - 自定义命令配置"
description: 创建自定义 cockle-config.json，配置环境变量、别名和自定义 WASM/JS 命令包
tags: [example, config, cockle-config, wasm, custom-packages, aliases]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: wasm-js-commands
    resource: /concepts/10-wasm-js-commands.md
    title: WASM与JavaScript命令
  - id: config-source
    resource: /references/config-source.md
    title: 配置参考
related_concepts: [/concepts/10-wasm-js-commands.md, /concepts/06-filesystem.md, /references/config-source.md]
---

## 目标

`cockle-config.json` 是 Cockle Shell 的核心配置文件，Shell 启动时会从 `wasmBaseUrl` 指定的目录加载此文件。通过自定义配置文件，你可以：

1. 指定要加载的 WASM 和 JavaScript 命令包
2. 配置每个包中包含哪些命令
3. 设置默认的命令别名（Alias）
4. 设置默认的环境变量（Environment Variables）
5. 加载自定义的纯 JavaScript 命令模块

本示例演示如何创建一个完整的自定义配置文件，并部署自定义 JS 命令。

## cockle-config.json 完整示例

以下是一个功能完整的 `cockle-config.json` 配置文件，包含常用 WASM 包、默认别名和环境变量：

```json
{
  "packages": {
    "cockle_fs": {
      "modules": {
        "fs": {
          "commands": ""
        }
      }
    },
    "coreutils": {
      "modules": {
        "coreutils": {
          "commands": "basename,cat,chmod,cp,cut,date,dir,dircolors,dirname,du,echo,env,expr,head,id,join,ln,logname,ls,md5sum,mkdir,mv,nl,pwd,realpath,rm,rmdir,seq,sha1sum,sha256sum,sleep,sort,stat,stty,tail,tee,touch,tr,tty,uname,uniq,vdir,wc,echo"
        }
      }
    },
    "grep": {
      "modules": {
        "grep": {
          "commands": "grep,egrep,fgrep"
        }
      }
    },
    "less": {
      "modules": {
        "less": {
          "commands": "less"
        }
      }
    },
    "sed": {
      "modules": {
        "sed": {
          "commands": "sed"
        }
      }
    },
    "tree": {
      "modules": {
        "tree": {
          "commands": "tree"
        }
      }
    },
    "vim": {
      "modules": {
        "vim": {
          "commands": "vim,vi"
        }
      }
    },
    "nano": {
      "modules": {
        "nano": {
          "commands": "nano"
        }
      }
    },
    "lua": {
      "modules": {
        "lua": {
          "commands": "lua"
        }
      }
    },
    "git2cpp": {
      "modules": {
        "git": {
          "commands": "git"
        }
      }
    }
  },
  "aliases": {
    "ls": "ls --color=auto",
    "ll": "ls -la",
    "la": "ls -a",
    "grep": "grep --color=auto",
    "dir": "dir --color=auto",
    "vdir": "vdir --color=auto",
    "gs": "git status",
    "ga": "git add",
    "gc": "git commit",
    "gp": "git push",
    "..": "cd ..",
    "...": "cd ../.."
  },
  "environment": {
    "EDITOR": "vim",
    "PAGER": "less",
    "LANG": "en_US.UTF-8",
    "TERM": "xterm-256color"
  }
}
```

### 配置项说明

#### packages 节

`packages` 节定义了 Shell 启动时可用的命令包。每个包对应 `wasmBaseUrl` 目录下的一个子目录。

- **`cockle_fs`**：必需的文件系统基础包，必须始终包含。其 `commands` 字段为空字符串，表示不直接暴露命令给用户。
- **`coreutils`**：GNU 核心工具集，提供 `ls`、`cat`、`cp`、`mv`、`rm`、`echo`、`wc` 等常用命令。
- **`grep`**：文本搜索工具，支持正则表达式。
- **`less`**：分页查看器。
- **`sed`**：流编辑器，用于文本处理。
- **`tree`**：目录树显示工具。
- **`vim`**：Vim 文本编辑器。
- **`nano`**：Nano 文本编辑器。
- **`lua`**：Lua 脚本语言解释器。
- **`git2cpp`**：Git 版本控制系统（基于 libgit2 的 WASM 构建）。

每个包的 `modules` 节定义了该包包含的模块。每个模块的 `commands` 字段是逗号分隔的命令名列表，这些命令名就是用户在 Shell 中输入的命令名称。

包级别可选字段：
- `wasm`：布尔值，默认为 `true`。设为 `false` 表示该包是纯 JavaScript 模块（不需要 .wasm 文件）。
- `version`：包版本字符串。
- `build_string`：构建标识字符串。
- `channel`：来源频道（如 `emscripten-forge`）。

#### aliases 节

`aliases` 节定义 Shell 启动时自动设置的命令别名。格式为 `"别名": "实际命令"`。别名在 Shell 启动时通过构造函数 `aliases` 选项设置的别名会**覆盖**配置文件中的同名别名（构造函数优先级更高）。

示例中的别名：
- `ls --color=auto`：让 `ls` 默认启用彩色输出
- `ll='ls -la'`：详细列表的快捷方式
- `gs='git status'`：Git 状态快捷方式
- `..='cd ..'`：快速返回上级目录

#### environment 节

`environment` 节定义 Shell 启动时自动设置的环境变量。格式为 `"变量名": "值"`。与别名类似，构造函数 `environment` 选项设置的变量会覆盖配置文件中的同名变量。

常用环境变量：
- `EDITOR`：默认文本编辑器，影响 `vipw`、`crontab -e` 等命令调用的编辑器
- `PAGER`：默认分页器，`man`、`git log` 等命令使用
- `LANG`：区域设置，影响字符编码和排序规则
- `TERM`：终端类型声明，Cockle 默认为 `xterm-256color`

## 部署说明

### 目录结构

将 `cockle-config.json` 和 WASM 命令包文件部署到 HTTP 服务器上，`wasmBaseUrl` 应该指向包含 `cockle-config.json` 的目录。推荐的目录结构：

```
wasm/
├── cockle-config.json        # 配置文件
├── cockle_fs/                # 文件系统基础包
│   ├── fs.js
│   └── fs.wasm
├── coreutils/                # 核心工具包
│   ├── coreutils.js
│   ├── coreutils.wasm
│   └── coreutils.data
├── grep/                     # grep 包
│   ├── grep.js
│   ├── grep.wasm
│   └── grep.data
├── less/                     # less 包
│   ├── less.js
│   ├── less.wasm
│   └── less.data
├── sed/                      # sed 包
│   ├── sed.js
│   ├── sed.wasm
│   └── sed.data
├── tree/                     # tree 包
│   ├── tree.js
│   └── tree.wasm
├── vim/                      # vim 包
│   ├── vim.js
│   ├── vim.wasm
│   └── vim.data
├── nano/                     # nano 包
│   ├── nano.js
│   ├── nano.wasm
│   └── nano.data
├── lua/                      # lua 包
│   ├── lua.js
│   ├── lua.wasm
│   └── lua.data
└── git2cpp/                  # git 包
    ├── git.js
    ├── git.wasm
    └── git.data
```

每个 WASM 包目录下通常包含三个文件：
- `<module>.js`：Emscripten 生成的 JavaScript 加载器
- `<module>.wasm`：WebAssembly 二进制文件
- `<module>.data`：虚拟文件系统数据包（包含命令的依赖文件等）

### TypeScript 中指定 wasmBaseUrl

```typescript
const shell = new Shell({
  baseUrl: window.location.href,
  wasmBaseUrl: new URL('./wasm/', window.location.href).toString(),
  outputCallback: (text) => term.write(text),
  browsingContextId,
  shellManager,
  // 构造函数别名会覆盖配置文件中的同名别名
  aliases: {
    // 这里的 ll 会覆盖 cockle-config.json 中的 ll
    ll: 'ls -alF'
  },
  // 构造函数环境变量会覆盖配置文件中的同名变量
  environment: {
    // 这里的 EDITOR 会覆盖配置文件中的 EDITOR
    EDITOR: 'nano'
  }
});
```

Shell 会自动 fetch `wasmBaseUrl + 'cockle-config.json'`，解析其中的包、别名和环境变量配置。如果 fetch 失败（如文件不存在），Shell 会在控制台输出错误但不会崩溃（只是没有可用命令）。

## 自定义 JS 命令

除了 WASM 命令包，Cockle 还支持纯 JavaScript 命令模块。JS 命令在 Web Worker 中运行（与外部命令不同，外部命令在主线程运行），可以访问文件系统 API，但不能直接访问 DOM。

### 创建 JS 命令模块

在 WASM 目录下创建一个自定义包目录，例如 `mycmds/hello.js`：

```javascript
// mycmds/hello.js
// 纯 JavaScript 命令模块，运行在 Web Worker 中
//
// 模块必须将自身赋值给 self.Module
// 导出 run 函数（必需）和 tabComplete 函数（可选）

self.Module = {
  /**
   * 命令执行函数
   * @param {object} context - 命令执行上下文
   * @param {string} context.name - 命令名称
   * @param {string[]} context.args - 命令参数
   * @param {Map} context.environment - 环境变量 Map
   * @param {object} context.fileSystem - 文件系统操作对象
   * @param {string} context.shellId - Shell 唯一标识
   * @param {object} context.stdin - 标准输入（readAsync 方法）
   * @param {object} context.stdout - 标准输出（write 方法）
   * @param {object} context.stderr - 标准错误（write 方法）
   * @param {Function} context.size - 返回终端尺寸 {rows, columns}
   * @param {object} context.termios - 终端模式控制
   * @returns {Promise<number>} 退出码（0 表示成功）
   */
  run: async function (context) {
    const { args, stdout, environment } = context;
    const name = args.length > 0 ? args.join(' ') : 'World';

    stdout.write(`Hello, ${name}!\n`);
    stdout.write(`当前目录: ${environment.get('PWD')}\n`);

    return 0; // ExitCode.SUCCESS
  },

  /**
   * Tab 补全函数（可选）
   * @param {object} context - 补全上下文
   * @param {string} context.name - 命令名称
   * @param {string[]} context.args - 当前参数
   * @param {string} context.shellId - Shell 唯一标识
   * @returns {Promise<{possibles?: string[]}>} 补全候选列表
   */
  tabComplete: async function (context) {
    const greetings = ['world', 'friend', 'stranger', 'developer'];
    const partial = context.args[context.args.length - 1] || '';
    const matches = greetings.filter(g => g.startsWith(partial));
    return { possibles: matches };
  }
};
```

### 在 cockle-config.json 中注册 JS 包

在 `packages` 节添加自定义 JS 包，设置 `wasm: false`：

```json
{
  "packages": {
    "cockle_fs": {
      "modules": { "fs": { "commands": "" } }
    },
    "coreutils": {
      "modules": {
        "coreutils": {
          "commands": "ls,cat,echo,pwd,wc,mkdir,touch,rm,cp,mv,cd"
        }
      }
    },
    "mycmds": {
      "wasm": false,
      "modules": {
        "hello": {
          "commands": "hello,hi,greet"
        }
      }
    }
  },
  "aliases": {
    "ls": "ls --color=auto",
    "ll": "ls -la"
  }
}
```

这里 `mycmds` 是包名（对应 `wasm/mycmds/` 目录），`hello` 是模块名（对应 `hello.js` 文件），`commands` 列表中 `hello,hi,greet` 表示这三个命令名都映射到该模块。设置 `"wasm": false` 告诉 Cockle 这是一个纯 JS 模块，不需要加载 .wasm 文件。

### JS 命令的文件系统访问

JS 命令可以通过 `context.fileSystem` 访问 Cockle 的虚拟文件系统。文件系统基于 Emscripten 的 MEMFS（内存文件系统），支持标准 POSIX 风格的操作：

```javascript
// JS 命令中的文件操作示例
self.Module = {
  run: async function (context) {
    const { args, stdout, stderr, fileSystem } = context;

    // 写入文件
    if (args[0] === 'write') {
      const content = args.slice(1).join(' ');
      // fileSystem 提供 FS 操作接口
      // 具体 API 参考 Emscripten FS 文档
      stdout.write(`写入内容: ${content}\n`);
    }

    // 读取文件
    if (args[0] === 'read') {
      const filename = args[1];
      try {
        // 使用 FS.readFile 读取文件内容
        const content = fileSystem.readFile(filename, { encoding: 'utf8' });
        stdout.write(content);
        if (!content.endsWith('\n')) stdout.write('\n');
      } catch (e) {
        stderr.write(`无法读取文件: ${e.message}\n`);
        return 1;
      }
    }

    return 0;
  }
};
```

## 版本兼容性注意

### Emscripten 版本匹配

所有 WASM 包必须使用与 Cockle 兼容的 Emscripten 版本编译。不同 Emscripten 版本生成的 JS/WASM 文件之间存在 ABI 不兼容。官方 Cockle 发布的 WASM 包使用统一版本的 Emscripten 构建，如果自行编译 WASM 包，需要确保版本一致。

### cockle_fs 包必须存在

`cockle_fs` 包是 Cockle 文件系统的基础模块，所有配置文件的 `packages` 节都必须包含它。如果缺少此包，Shell 将无法正常初始化文件系统，会在控制台输出错误信息。

### 命令名冲突

如果多个包中定义了相同的命令名，后加载的包会覆盖先前的包。建议在组织包时避免命令名冲突，或通过模块划分明确职责。

## 使用 cockle-config 命令

Cockle 内置的 `cockle-config` 命令可以检查当前配置状态。在 Shell 中使用以下子命令：

```bash
# 查看完整配置信息（版本、包、模块、stdin 后端）
cockle-config

# 查看版本
cockle-config -v
# 或
cockle-config --version

# 查看当前 Worker 类型（coincident 或 comlink）
cockle-config -w
# 或
cockle-config --worker

# 查看所有包信息
cockle-config package

# 查看特定包信息
cockle-config package coreutils

# 查看所有模块信息
cockle-config module

# 查看所有命令（按类型过滤）
cockle-config command              # 所有命令
cockle-config command --builtin    # 仅内置命令
cockle-config command --external   # 仅外部命令
cockle-config command --javascript # 仅 JS 命令
cockle-config command --wasm       # 仅 WASM 命令

# 查看同步 stdin 配置
cockle-config stdin

# 切换 stdin 后端（sab = SharedArrayBuffer, sw = Service Worker）
# 注意：仅当两种后端都可用时才能切换
cockle-config stdin sab
cockle-config stdin sw
```

`cockle-config stdin` 命令会显示一个表格，列出可用的 stdin 后端、简称和当前启用状态。SharedArrayBuffer（SAB）模式性能更好但需要 COOP/COEP 头；Service Worker（SW）模式兼容性更好但需要额外的 Worker 注册。

## 相关概念

- [WASM与JavaScript命令](/concepts/10-wasm-js-commands.md)
- [文件系统](/concepts/06-filesystem.md)
- [配置参考](/references/config-source.md)
