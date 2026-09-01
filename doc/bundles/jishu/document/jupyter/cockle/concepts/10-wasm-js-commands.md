---
type: concept
title: 10 - WASM 与 JavaScript 命令
description: 通过 cockle-config.json 配置 Emscripten-forge 编译的 WASM 命令和纯 JS 命令包
tags: [wasm, javascript-commands, emscripten, emscripten-forge, config, dynamic-loading]
generated:
  by: "agent:source-code-to-okf-wiki"
  at: "2026-08-22T00:00:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-22T00:00:00+08:00"
status: stable
stale_after: "2027-08-22"
sources:
  - id: cmd-source
    resource: /references/command-source.md
    title: 命令系统参考
  - id: config-source
    resource: /references/config-source.md
    title: 配置参考
---

# WASM 与 JavaScript 命令

WASM（WebAssembly）命令和 JavaScript（JS）命令是 Cockle（浏览器Shell）通过 `cockle-config.json` 配置文件动态加载的命令包。WASM 命令是使用 Emscripten（编译工具链）从 C/C++ 代码编译的 Unix 工具（如 `ls`、`cat`、`vim`），JavaScript 命令是在 Worker（工作线程）中执行的纯 JavaScript 模块。这两类命令在首次执行时按需下载，实现了 Shell 核心精简而功能可扩展。

## WASM 命令概述

WASM 命令是通过 [emscripten-forge](https://github.com/emscripten-forge) 项目将标准 Unix 工具编译为 WebAssembly 格式。它们在 Worker 线程中运行，拥有完整的 libc（C标准库）环境，可以执行文件操作、进程管理、终端交互等，与原生 Unix 命令行为高度一致。

### 与 JS 命令的区别

| 特性 | WASM 命令 | JavaScript 命令 |
|------|-----------|----------------|
| 源代码语言 | C/C++ | JavaScript |
| 文件格式 | `.wasm` + `.js` 加载器 | `.js` (ES模块) |
| 运行时 | Emscripten 模拟的 POSIX 环境 | 原生 JS 环境 |
| 文件IO | 通过 libc 调用 Emscripten FS | 通过 FS API 直接调用 |
| 性能 | 接近原生 | 取决于JS引擎 |
| 适合场景 | 移植现有 Unix 工具 | 轻量逻辑、快速原型 |

两种命令共享 `DynamicallyLoadedCommandRunner`（动态加载命令运行器）基类，加载和缓存机制相同。

## 支持的 WASM 包清单

Cockle 当前预装了以下 WASM 包（通过 cockle-config.json 配置）：

| 包名 | 提供的命令 | 说明 |
|------|-----------|------|
| **coreutils** | `cat`, `cp`, `echo`, `ls`, `mkdir`, `mv`, `rm`, `touch`, `uname`, `wc` | GNU coreutils 核心工具集 |
| **git2cpp** | `git` | Git 版本控制系统（C++重制版） |
| **grep** | `grep` | 文本搜索工具 |
| **less** | `less` | 分页查看器 |
| **lua** | `lua` | Lua 脚本语言解释器 |
| **nano** | `nano` | 简单的文本编辑器 |
| **sed** | `sed` | 流编辑器 |
| **tree** | `tree` | 目录树显示工具 |
| **vim** | `vim` | Vi IMproved 文本编辑器 |

### 命令示例

这些 WASM 命令的行为与原生版本基本一致：

```bash
# coreutils
ls -la /drive
cp file1.txt file2.txt
mkdir -p /drive/projects/new
echo "Hello World"
rm temp.txt
wc -l notes.md
uname -a

# git（需要CORS代理支持clone）
git init
git add .
git commit -m "initial commit"
git status

# 编辑器
nano /drive/notes.txt
vim /drive/script.py

# 其他
grep "pattern" file.txt
sed 's/foo/bar/g' input.txt
tree /drive
cat README.md | less
```

### 与内置命令的优先级

内置命令优先级高于 WASM 命令。例如 `cd`、`echo` 等命令在内置命令中已有实现，会优先使用 TypeScript 版本而非 WASM 版本。这是为了性能考虑（内置命令不需要加载 WASM 模块）。

## cockle-config.json 配置格式

`cockle-config.json` 是 WASM 和 JS 命令的配置文件，定义了要加载哪些包、包的版本、包含哪些命令模块等。Shell 初始化时通过 `_initWasmPackages` 方法 fetch 此配置。

### 顶层结构

```json
{
  "packages": {
    "<package-name>": {
      "version": "<version-string>",
      "build_string": "<build-identifier>",
      "channel": "<emscripten-forge-channel>",
      "platform": "wasm32-unknown-emscripten",
      "wasm": true,
      "modules": {
        "<module-name>": {
          "commands": "<command1,command2,...>"
        }
      }
    }
  },
  "aliases": {
    "<alias-name>": "<alias-value>"
  },
  "environment": {
    "<ENV_VAR>": "<value>"
  }
}
```

### packages 字段详解

每个包配置包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `version` | string | 包版本号（如 `"9.4-r1"`） |
| `build_string` | string | 构建标识，包含 Emscripten 版本信息（如 `"h_*_emscripten_4_0_9"`） |
| `channel` | string | conda 频道，必须为 `emscripten-forge-4x`（Emscripten 4.x 版本） |
| `platform` | string | 目标平台，固定为 `wasm32-unknown-emscripten` |
| `wasm` | boolean | 是否为 WASM 包（JS 命令包为 `false`） |
| `modules` | object | 该包包含的模块定义 |

### modules 字段

每个模块定义该模块提供的命令列表：

```json
{
  "modules": {
    "coreutils": {
      "commands": "cat,cp,echo,ls,mkdir,mv,rm,touch,uname,wc"
    },
    "coreutils-extra": {
      "commands": "head,tail,dirname,basename"
    }
  }
}
```

`commands` 是逗号分隔的命令名字符串。每个命令对应一个 WASM 可执行文件，首次调用时按需下载。

### 完整配置示例

以下是一个典型的 `cockle-config.json` 示例：

```json
{
  "packages": {
    "cockle_fs": {
      "version": "1.0.0",
      "build_string": "emscripten_4_0_9",
      "channel": "emscripten-forge-4x",
      "platform": "wasm32-unknown-emscripten",
      "wasm": true,
      "modules": {}
    },
    "coreutils": {
      "version": "9.4-r1",
      "build_string": "h_0_emscripten_4_0_9",
      "channel": "emscripten-forge-4x",
      "platform": "wasm32-unknown-emscripten",
      "wasm": true,
      "modules": {
        "coreutils": {
          "commands": "cat,cp,echo,ls,mkdir,mv,rm,touch,uname,wc"
        }
      }
    },
    "grep": {
      "version": "3.11-r0",
      "build_string": "h_0_emscripten_4_0_9",
      "channel": "emscripten-forge-4x",
      "platform": "wasm32-unknown-emscripten",
      "wasm": true,
      "modules": {
        "grep": {
          "commands": "grep,egrep,fgrep"
        }
      }
    },
    "vim": {
      "version": "9.0-r2",
      "build_string": "h_0_emscripten_4_0_9",
      "channel": "emscripten-forge-4x",
      "platform": "wasm32-unknown-emscripten",
      "wasm": true,
      "modules": {
        "vim": {
          "commands": "vim,vi,view"
        }
      }
    }
  },
  "aliases": {
    "ll": "ls -la",
    "la": "ls -a"
  },
  "environment": {
    "EDITOR": "vim",
    "PAGER": "less"
  }
}
```

### aliases 默认别名

`aliases` 字段定义启动时自动加载的命令别名，格式与 `alias` 命令一致：

```json
{
  "aliases": {
    "ll": "ls -la",
    "gs": "git status",
    "grep": "grep --color=auto"
  }
}
```

### environment 默认环境变量

`environment` 字段定义启动时自动设置的环境变量：

```json
{
  "environment": {
    "EDITOR": "nano",
    "PATH": "/usr/local/bin:/usr/bin",
    "COCKLE_DARK_MODE": "1"
  }
}
```

这些环境变量在 Shell 初始化时通过 `export` 等效逻辑设置。

## 命令模块加载

WASM 和 JS 命令采用惰性加载（lazy loading）策略：Shell 启动时只注册命令元数据，首次执行命令时才下载对应的 WASM/JS 文件。

### CommandModule 惰性加载

`CommandModule` 代表一个可加载的命令模块，管理模块的下载和缓存：

```typescript
class CommandModule {
  private _loaded: boolean = false;
  private _moduleExports: any = null;
  
  constructor(
    private _package: CommandPackage,
    private _moduleName: string,
    private _commands: string[]
  ) {}
  
  async load(): Promise<void> {
    if (this._loaded) return;
    
    // 构造模块URL
    const url = this._package.getModuleUrl(this._moduleName);
    
    // 下载并实例化模块
    // WASM模块：import() JS加载器，JS加载器再加载.wasm文件
    // JS模块：直接import()
    this._moduleExports = await this._package.importModule(url);
    this._loaded = true;
  }
  
  get commands(): string[] {
    return this._commands;
  }
}
```

### CommandModuleLoader 缓存

`CommandModuleLoader` 管理所有模块的加载，确保每个模块只下载一次：

```typescript
class CommandModuleLoader {
  private _cache = new Map<string, CommandModule>();
  private _loading = new Map<string, Promise<void>>();
  
  async loadModule(pkg: CommandPackage, moduleName: string): Promise<CommandModule> {
    const key = `${pkg.name}/${moduleName}`;
    
    // 已缓存
    if (this._cache.has(key)) {
      const mod = this._cache.get(key)!;
      await mod.load();
      return mod;
    }
    
    // 正在加载中，等待同一个Promise
    if (this._loading.has(key)) {
      await this._loading.get(key);
      return this._cache.get(key)!;
    }
    
    // 开始加载
    const mod = new CommandModule(pkg, moduleName, pkg.getCommands(moduleName));
    const loadPromise = mod.load().then(() => {
      this._loading.delete(key);
      this._cache.set(key, mod);
    });
    this._loading.set(key, loadPromise);
    await loadPromise;
    return mod;
  }
}
```

这种设计避免了重复下载，即使多个命令来自同一个模块也只加载一次。

### DownloadTracker 进度显示

下载 WASM 文件时，`DownloadTracker` 在终端显示进度条，提升用户体验：

```
Downloading vim.wasm...
[████████████████░░░░░░░░] 68% (1.2/1.8 MB)
```

```typescript
class DownloadTracker {
  track(url: string, fetchPromise: Promise<Response>): Promise<Response> {
    const filename = url.split('/').pop()!;
    this._write(`Downloading ${filename}...\n`);
    
    return fetchPromise.then(response => {
      const reader = response.body!.getReader();
      const contentLength = parseInt(response.headers.get('content-length') || '0');
      let received = 0;
      
      // 创建进度流
      const stream = new ReadableStream({
        async start(controller) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            received += value.length;
            this._updateProgress(filename, received, contentLength);
            controller.enqueue(value);
          }
          controller.close();
          this._clearProgress();
        }
      });
      
      return new Response(stream, response);
    });
  }
}
```

## WASM 运行时要求

WASM 命令的运行有严格的版本和依赖要求，配置不当会导致加载失败。

### cockle_fs 必须最先加载

`cockle_fs` 不是一个命令包，而是**文件系统运行时包**。它提供 Emscripten 的 FS、PATH、ERRNO_CODES、PROXYFS 等核心对象，所有其他 WASM 命令共享这个文件系统实例。

在 `cockle-config.json` 中，`cockle_fs` 必须配置且 `modules` 为空对象（因为它不提供任何命令）：

```json
{
  "packages": {
    "cockle_fs": {
      "version": "1.0.0",
      "build_string": "emscripten_4_0_9",
      "channel": "emscripten-forge-4x",
      "platform": "wasm32-unknown-emscripten",
      "wasm": true,
      "modules": {}
    }
  }
}
```

Shell 初始化流程：
1. `_initWasmPackages()` 首先 fetch `cockle-config.json`
2. 加载 `cockle_fs` 包，获取 FS/PATH 等对象
3. `_initFileSystem()` 使用这些 FS 对象挂载 PROXYFS 和 DriveFS
4. 注册其他包的命令元数据（但不加载）
5. 首次执行 WASM 命令时才加载对应模块

### Emscripten 版本匹配

**所有 WASM 包必须使用与 Cockle 相同版本的 Emscripten 编译**。当前 Cockle 使用 Emscripten **4.0.9**，因此：

- `build_string` 必须包含 `emscripten_4_0_9`
- `channel` 必须是 `emscripten-forge-4x`（对应 Emscripten 4.x 的 conda 频道）

如果版本不匹配，会出现以下问题：

1. **内存布局不一致**：不同版本的 Emscripten 运行时内存布局不同，共享 FS 时会崩溃
2. **FS API 不兼容**：FS 的内部结构可能变化
3. **符号解析失败**：WASM 模块导入的函数签名可能不匹配

### prefix.dev 频道

WASM 包托管在 prefix.dev 的 emscripten-forge 频道上。包的 URL 构造规则大致为：

```
{wasmBaseUrl}/{channel}/{platform}/{package-name}-{version}-{build_string}.tar.zst
```

解压后包含：
- `.wasm` 文件：WebAssembly 二进制
- `.js` 文件：Emscripten 生成的加载器
- 数据文件（如 terminfo 数据库、locale 文件等）

`wasmBaseUrl` 通过 Shell 构造函数传入，默认为 Cockle 包的 CDN 地址。

## JavaScript 命令

JavaScript 命令是在 Worker 中执行的纯 JavaScript 模块，不需要 `.wasm` 文件。它们适合实现轻量级逻辑，不需要 POSIX 环境的场景。

### JavascriptCommandRunner

`JavascriptCommandRunner` 负责执行 JS 命令模块：

```typescript
class JavascriptCommandRunner extends DynamicallyLoadedCommandRunner {
  protected async _runCommand(
    module: any,
    args: string[],
    context: RunContext
  ): Promise<number> {
    // JS模块默认导出一个异步函数
    const fn = module.default || module;
    if (typeof fn !== 'function') {
      throw new Error('JS command module must export a function');
    }
    return await fn(args, context);
  }
}
```

### JS 命令模块格式

JS 命令模块是一个 ES 模块，默认导出一个命令函数：

```javascript
// hello.js - 示例JS命令模块
export default async function hello(args, context) {
  const name = args[0] || 'World';
  context.stdout.write(`Hello, ${name}!\n`);
  
  // 可以访问FS API
  if (args.includes('--cwd')) {
    context.stdout.write(`Current directory: ${context.fs.cwd()}\n`);
  }
  
  // 可以读取环境变量
  context.stdout.write(`Shell ID: ${context.env.get('COCKLE_SHELL_ID')}\n`);
  
  return 0;  // 退出码
}
```

### JS 命令配置

在 `cockle-config.json` 中，JS 命令包配置 `wasm: false`：

```json
{
  "packages": {
    "my-js-commands": {
      "version": "1.0.0",
      "build_string": "js",
      "channel": "custom",
      "platform": "javascript",
      "wasm": false,
      "modules": {
        "hello": {
          "commands": "hello"
        },
        "utils": {
          "commands": "now,uuid"
        }
      }
    }
  }
}
```

### 与 WASM 命令共享基类

`JavascriptCommandRunner` 和 `WasmCommandRunner` 都继承自 `DynamicallyLoadedCommandRunner`：

```
DynamicallyLoadedCommandRunner (抽象基类)
├── WasmCommandRunner (执行.wasm模块)
│   └── 创建Emscripten运行时实例
│   └── 调用main()函数
│   └── 处理stdin/stdout/stderr重定向
└── JavascriptCommandRunner (执行.js模块)
    └── import() ES模块
    └── 调用默认导出函数
```

基类负责模块的加载、缓存、命令查找等公共逻辑。

## 自定义 WASM 包

你可以使用 emscripten-forge 编译自己的 WASM 命令包并添加到 Cockle 中。

### 使用 Emscripten-forge 编译

1. **安装 emscripten-forge 工具链**：

```bash
# 使用 conda/mamba 安装
mamba create -n emscripten-forge python=3.11
mamba activate emscripten-forge
pip install emscripten-forge-build
```

2. **创建 recipe**：

```yaml
# emforge-recipes/mycommand/recipe.yaml
package:
  name: mycommand
  version: "1.0.0"

source:
  git_url: https://github.com/example/mycommand.git
  git_tag: v1.0.0

build:
  number: 0
  script: |
    emconfigure ./configure
    emmake make
    emmake make install

requirements:
  build:
    - {{ compiler('c') }}
    - {{ compiler('cxx') }}
```

3. **编译**：

```bash
emforge build mycommand --platform wasm32-unknown-emscripten
```

4. **上传到可访问的 HTTP 服务器**（需要支持 CORS 头）。

### 添加到 cockle-config.json

```json
{
  "packages": {
    "mycommand": {
      "version": "1.0.0",
      "build_string": "h_0_emscripten_4_0_9",
      "channel": "custom-channel",
      "platform": "wasm32-unknown-emscripten",
      "wasm": true,
      "modules": {
        "mycommand": {
          "commands": "mycommand"
        }
      }
    }
  }
}
```

确保 `build_string` 中的 Emscripten 版本与 Cockle 使用的版本一致（`4_0_9`）。

### 部署到 wasmBaseUrl

将编译产物（`.wasm`、`.js`、数据文件）部署到 `wasmBaseUrl` 对应的目录结构下。`wasmBaseUrl` 通过 Shell 构造函数配置：

```typescript
const shell = new CockleShell({
  wasmBaseUrl: 'https://your-cdn.com/cockle-wasm/',
  // ...
});
```

## wasmUrlQueryParams 回调

`wasmUrlQueryParams` 回调函数允许为 WASM/JS 文件的下载 URL 添加查询参数，常用于缓存控制或身份验证。

### 配置方式

```typescript
const shell = new CockleShell({
  wasmUrlQueryParams: (url: string) => {
    // 为所有WASM请求添加版本号和令牌
    return {
      v: '2024-01-15',          // 缓存版本号
      token: authToken           // 身份验证令牌
    };
  }
});
```

返回的对象会被序列化为 URL 查询参数追加到请求 URL：

```
https://cdn.example.com/coreutils/ls.wasm?v=2024-01-15&token=abc123
```

### 典型用途

1. **缓存破坏**（Cache Busting）：更新 WASM 包时修改版本号参数，强制浏览器重新下载
2. **访问控制**：为需要认证的 WASM 资源添加令牌参数
3. **CDN 配置**：传递 CDN 特定的参数（如区域、缓存策略）
4. **调试**：添加 `debug=1` 等参数触发服务器返回调试版本

```typescript
// 示例：根据文件名使用不同策略
wasmUrlQueryParams: (url: string) => {
  if (url.includes('.wasm')) {
    return { v: WASM_VERSION };
  }
  if (url.includes('.js')) {
    return { v: JS_VERSION };
  }
  return {};
}
```

## 相关概念

- [03 - 命令系统](03-command-system.md)：CommandRegistry、CommandRunner 的整体架构
- [06 - 文件系统](06-filesystem.md)：cockle_fs、PROXYFS、DriveFS 的关系
- [07 - 缓冲 IO 系统](07-buffered-io.md)：WASM 命令的同步 stdin 读取机制
- [08 - 内置命令详解](08-builtin-commands.md)：TypeScript 内置命令（优先级高于WASM）
- [09 - 外部命令](09-external-commands.md)：主线程执行的自定义命令
- [命令系统参考](../references/command-source.md)：CommandModule/CommandPackage 完整 API
- [配置参考](../references/config-source.md)：cockle-config.json 完整字段说明
