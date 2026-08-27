---
type: concept
title: 06 - 文件系统
description: Emscripten MEMFS 内存文件系统、PROXYFS 代理挂载和 DriveFS 浏览器持久存储的工作原理
tags: [filesystem, memfs, proxyfs, drivefs, emscripten, wasm, mount]
generated:
  by: "agent:source-code-to-okf-wiki"
  at: "2026-08-22T00:00:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-22T00:00:00+08:00"
status: stable
stale_after: "2027-08-22"
sources:
  - id: config-source
    resource: /references/config-source.md
    title: 配置参考
---

# 文件系统

Cockle（浏览器Shell）的文件系统采用三层架构设计：底层是 Emscripten（编译工具链）提供的 MEMFS（内存文件系统），中间层通过 PROXYFS（代理文件系统）桥接，上层对接 JupyterLite 的 DriveFS（浏览器持久化存储）实现数据持久化。这种分层设计既满足了 WASM（WebAssembly）命令对同步文件操作的需求，又实现了浏览器环境下的数据持久存储。

## 文件系统架构概述

Cockle 的文件系统初始化在 shell_impl.ts 的 `_initFileSystem` 方法中完成，整个架构包含三个核心层次：

1. **MEMFS 基础层**：Emscripten 编译时默认启用的内存文件系统，所有文件操作在内存中执行，速度极快但刷新后数据丢失
2. **PROXYFS 代理层**：Emscripten 提供的代理文件系统，将文件操作转发到主线程处理
3. **DriveFS 持久层**：JupyterLite 提供的浏览器持久化存储实现，基于 IndexedDB（浏览器数据库）或其他后端

初始化流程如下：

```typescript
// _initFileSystem 核心流程（简化）
private async _initFileSystem(): Promise<void> {
  // 1. 创建挂载点目录
  this._fileSystem.FS.mkdir(this._mountpoint, 0o777);
  
  // 2. 调用主线程回调初始化 DriveFS
  await this._initDriveFSCallback({
    fileSystem: this._fileSystem,
    mountpoint: this._mountpoint,
    baseUrl: this._baseUrl,
    browsingContextId: this._browsingContextId
  });
  
  // 3. 切换到挂载点目录
  this._fileSystem.FS.chdir(this._mountpoint);
  
  // 4. 如果配置了初始工作目录，切换到该目录
  if (this._cwd) {
    this._fileSystem.FS.chdir(this._cwd);
  }
}
```

挂载点（mountpoint）默认是 `/drive`，这是 PROXYFS 与 DriveFS 对接的入口点。

## Emscripten MEMFS

MEMFS（Memory File System）是 Emscripten 的默认文件系统，所有文件存储在 JavaScript 堆内存中。Cockle 通过 `_fileSystem` 属性暴露 MEMFS 的核心 API：

```typescript
// _fileSystem 存储的核心对象（来自 cockle_fs WASM模块）
this._fileSystem = {
  FS,           // 文件系统API
  PATH,         // 路径处理工具
  ERRNO_CODES,  // 错误码常量
  PROXYFS       // 代理文件系统构造器
};
```

### 常用 FS API

在外部命令和 TypeScript 代码中，可以通过 `FS` 对象操作文件系统：

```typescript
// 读取目录内容
const files = FS.readdir('/drive');
// 返回: ['.', '..', 'documents', 'notes.txt']

// 分析路径
const info = FS.analyzePath('/drive/notes.txt');
// 返回: { exists: true, name: 'notes.txt', path: '/drive/notes.txt', object: {...} }

// 写入文件
FS.writeFile('/drive/hello.txt', 'Hello, Cockle!', { encoding: 'utf8' });

// 读取文件
const content = FS.readFile('/drive/hello.txt', { encoding: 'utf8' });

// 创建目录
FS.mkdir('/drive/newdir', 0o755);

// 删除文件
FS.unlink('/drive/temp.txt');

// 改变工作目录
FS.chdir('/drive/documents');

// 获取当前工作目录
const cwd = FS.cwd();
```

### 临时目录

除了挂载的 `/drive` 持久化目录，MEMFS 中还有一些标准的 Unix 临时目录：

- `/tmp`：临时文件目录，适合存放会话期间的临时数据
- `/home`：用户主目录（默认不创建持久化）
- `/dev`：设备文件目录（WASM命令需要）

这些目录中的数据在 Shell 会话结束或页面刷新后会丢失，只有 `/drive` 下的数据通过 DriveFS 持久化。

## PROXYFS 代理文件系统

PROXYFS 是 Emscripten 提供的一种特殊文件系统类型，它本身不存储数据，而是将所有文件系统操作通过 Worker 的消息机制转发到主线程处理。这是连接 Worker 内 WASM 代码与主线程持久化存储的关键桥梁。

### 代理原理

当 WASM 命令在 Worker 中执行文件操作（如 `open()`、`read()`、`write()`）时，PROXYFS 会：

1. 拦截文件系统调用
2. 将操作序列化（serialize）为消息
3. 通过 postMessage 发送到主线程
4. 主线程执行实际的文件操作（对接 DriveFS）
5. 将结果序列化后发回 Worker
6. Worker 中的 PROXYFS 反序列化结果并返回给 WASM 代码

### initDriveFSCallback 桥接

Cockle 通过 `initDriveFSCallback` 回调函数让主线程完成 PROXYFS 到 DriveFS 的挂载：

```typescript
// Shell 初始化时传入回调
const shell = new CockleShell({
  initDriveFSCallback: async ({ fileSystem, mountpoint, baseUrl, browsingContextId }) => {
    const { FS, PROXYFS } = fileSystem;
    
    // 在主线程创建 DriveFS 实例
    const driveFs = await createDriveFS({
      baseUrl,
      browsingContextId,
      // DriveFS 具体实现由宿主应用（如 JupyterLab）提供
    });
    
    // 将 DriveFS 挂载为 PROXYFS
    FS.mount(PROXYFS, {
      root: mountpoint,
      fs: driveFs  // DriveFS 实现了标准文件系统接口
    }, mountpoint);
  }
});
```

这个回调必须在主线程执行，因为 DriveFS 的 IndexedDB 操作只能在主线程中进行。

## DriveFS 浏览器持久化

DriveFS 是 JupyterLite 提供的浏览器端持久化文件系统，是 Cockle 实现数据持久化的核心。它将文件操作映射到浏览器的 IndexedDB 或其他持久化存储后端。

### mountpoint 配置

挂载点通过 Shell 构造函数的 `mountpoint` 选项配置，默认为 `/drive`：

```typescript
const shell = new CockleShell({
  mountpoint: '/drive',  // 持久化存储挂载点
  cwd: '/drive',         // 初始工作目录
  baseUrl: 'https://example.com/cockle-assets/',
  browsingContextId: 'notebook-123'  // 用于隔离不同会话的存储
});
```

### baseUrl 与 browsingContextId 参数

- **baseUrl**：WASM 包和静态资源的基础 URL，DriveFS 可能用它定位资源
- **browsingContextId**：浏览上下文 ID，用于在共享 IndexedDB 中隔离不同 Shell 实例的文件系统，避免多个 notebook 之间的文件冲突

### DriveFS 的标准接口

DriveFS 需要实现 Emscripten 文件系统的标准接口，主要方法包括：

```typescript
interface DriveFS {
  // 节点操作
  lookup(parent: INode, name: string): INode;
  mknod(parent: INode, name: string, mode: number, dev: any): INode;
  mkdir(parent: INode, name: string, mode: number): INode;
  rmdir(parent: INode, name: string): void;
  unlink(parent: INode, name: string): void;
  rename(oldParent: INode, oldName: string, newParent: INode, newName: string): void;
  
  // 文件IO
  open(node: INode, flags: number): FileStream;
  read(stream: FileStream, buffer: Uint8Array, offset: number, length: number, position: number): number;
  write(stream: FileStream, buffer: Uint8Array, offset: number, length: number, position: number): number;
  close(stream: FileStream): void;
  
  // 目录遍历
  readdir(node: INode): string[];
  getattr(node: INode): Stats;
}
```

宿主应用（如 JupyterLab、Retrolab）负责提供具体的 DriveFS 实现。

## cockle_fs WASM 模块

`cockle_fs` 是一个特殊的 WASM 包，它不包含任何可执行命令，而是提供 Emscripten 文件系统运行时。它必须在 `cockle-config.json` 中配置，并且必须最先加载。

### 文件系统运行时

`cockle_fs` 导出 Emscripten 运行时的核心组件：

```javascript
// cockle_fs 模块导出内容（简化）
Module({
  // ... Emscripten 运行时
}).then(module => {
  return {
    FS: module.FS,           // 文件系统API
    PATH: module.PATH,       // 路径工具
    ERRNO_CODES: module.ERRNO_CODES,  // 错误码
    PROXYFS: module.PROXYFS  // 代理文件系统
  };
});
```

这些对象在所有 WASM 命令之间共享，确保它们操作同一个文件系统视图。

### 版本匹配要求

`cockle_fs` 和所有 WASM 命令包必须使用**相同版本的 Emscripten** 编译（当前版本 4.0.9）。如果版本不匹配，会出现内存布局不一致、FS API 不兼容等问题：

```json
// cockle-config.json 中的版本要求示例
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

Emscripten 版本不一致会导致难以调试的运行时错误，配置时务必确认所有包的 `build_string` 匹配。

## 文件操作

Cockle 的 IO 系统提供了 `FileInput` 和 `FileOutput` 类，用于在命令中实现文件重定向。

### FileInput 实现

`FileInput` 类读取文件内容作为命令的标准输入：

```typescript
// FileInput 简化实现
class FileInput implements Input {
  private _decoder: TextDecoder;
  private _data: Uint8Array;
  private _position: number = 0;

  constructor(FS: any, path: string) {
    this._data = FS.readFile(path);  // 读取整个文件
    this._decoder = new TextDecoder('utf-8');
  }

  async read(): Promise<string> {
    if (this._position >= this._data.length) {
      return '';  // EOF
    }
    // 读取剩余内容
    const remaining = this._data.slice(this._position);
    this._position = this._data.length;
    return this._decoder.decode(remaining);
  }
}
```

### FileOutput 实现

`FileOutput` 类将命令输出写入文件：

```typescript
// FileOutput 简化实现
class FileOutput implements Output {
  private _encoder: TextEncoder;
  private _chunks: Uint8Array[] = [];
  private _append: boolean;

  constructor(
    private FS: any,
    private _path: string,
    append: boolean = false
  ) {
    this._append = append;
    this._encoder = new TextEncoder();
  }

  write(data: string): void {
    this._chunks.push(this._encoder.encode(data));
  }

  close(): void {
    // 合并所有数据块
    const totalLength = this._chunks.reduce((sum, chunk) => sum + chunk.length, 0);
    const merged = new Uint8Array(totalLength);
    let offset = 0;
    for (const chunk of this._chunks) {
      merged.set(chunk, offset);
      offset += chunk.length;
    }
    
    // 写入文件
    if (this._append) {
      const existing = this.FS.readFile(this._path);
      const combined = new Uint8Array(existing.length + merged.length);
      combined.set(existing, 0);
      combined.set(merged, existing.length);
      this.FS.writeFile(this._path, combined);
    } else {
      this.FS.writeFile(this._path, merged);
    }
  }
}
```

这两个类支撑了 Shell 的重定向语法：

```bash
# 输出重定向
echo "hello" > /drive/hello.txt
cat /drive/hello.txt >> /drive/log.txt

# 输入重定向
cat < /drive/hello.txt
```

## 通配符展开

Cockle 在解析命令行参数时会自动进行文件名通配符展开（globbing），实现位于 shell_impl.ts 的 `_filenameExpansion` 方法。

### 支持的通配符

| 通配符 | 含义 | 正则等效 |
|--------|------|----------|
| `*` | 匹配任意数量的任意字符（除了路径分隔符 `/`） | `[^/]*` |
| `?` | 匹配单个任意字符（除了路径分隔符 `/`） | `[^/]` |

### 展开规则

```typescript
// _filenameExpansion 核心逻辑
private _filenameExpansion(pattern: string): string[] {
  // 1. 将通配符模式转换为正则表达式
  const regexPattern = pattern
    .replace(/\./g, '\\.')
    .replace(/\*/g, '[^/]*')
    .replace(/\?/g, '[^/]');
  const regex = new RegExp(`^${regexPattern}$`);
  
  // 2. 确定要搜索的目录
  const dir = this._fileSystem.PATH.dirname(pattern);
  const base = this._fileSystem.PATH.basename(pattern);
  
  // 3. 读取目录内容
  let entries: string[];
  try {
    entries = this._fileSystem.FS.readdir(dir);
  } catch {
    return [pattern];  // 目录不存在，返回原模式
  }
  
  // 4. 过滤匹配项（默认排除隐藏文件，除非模式以.开头）
  const includeHidden = base.startsWith('.');
  const matches = entries.filter(name => {
    if (name === '.' || name === '..') return false;
    if (!includeHidden && name.startsWith('.')) return false;
    return regex.test(name);
  });
  
  // 5. 排序并返回完整路径
  matches.sort();
  return matches.map(name => this._fileSystem.PATH.join(dir, name));
}
```

使用示例：

```bash
# 列出所有.txt文件
ls *.txt

# 匹配单个字符：file1.txt, file2.txt, fileA.txt
ls file?.txt

# 嵌套目录通配符
ls /drive/documents/*.md
```

### 隐藏文件过滤

默认情况下，以 `.` 开头的隐藏文件不会被 `*` 匹配。如果需要匹配隐藏文件，模式必须以 `.` 开头：

```bash
ls .*  # 列出所有隐藏文件
ls *   # 不显示隐藏文件
```

## 初始目录和文件

Cockle 支持在 Shell 初始化时创建初始目录和文件，通过 `initialDirectories` 和 `initialFiles` 选项配置。这些初始化操作在 MEMFS 中执行，在挂载 DriveFS 之前完成。

### initialDirectories

`initialDirectories` 是一个目录路径数组，Shell 启动时会递归创建这些目录：

```typescript
const shell = new CockleShell({
  initialDirectories: [
    '/drive/projects',
    '/drive/documents/notes',
    '/tmp/cache'
  ]
});
```

这些目录以 `0o755` 权限创建。如果 `/drive` 已经通过 DriveFS 挂载，这些目录会持久化；否则在 MEMFS 中临时存在。

### initialFiles

`initialFiles` 是一个键值对对象，键是文件路径，值是文件内容：

```typescript
const shell = new CockleShell({
  initialFiles: {
    '/drive/README.md': '# Welcome to Cockle\n\nThis is your browser shell.',
    '/drive/projects/hello.py': 'print("Hello from Cockle!")\n',
    '/tmp/.bashrc': 'export PS1="cockle> "\n'
  }
});
```

文件以 `0o644` 权限创建。如果文件所在目录不存在，初始化时会自动创建父目录。

### 初始化顺序

初始目录和文件的创建顺序在文件系统挂载流程中：

1. 加载 cockle_fs WASM 模块（获取 FS/PATH 等对象）
2. 在 MEMFS 中创建 mountpoint 目录
3. 调用 initDriveFSCallback 挂载 DriveFS
4. chdir 到 mountpoint
5. 创建 initialDirectories 中的目录
6. 写入 initialFiles 中的文件
7. chdir 到配置的 cwd

这确保了初始文件在持久化存储挂载后写入，数据能够正确保存。

## 相关概念

- [05 - IO 系统](05-io-system.md)：标准输入输出、重定向和管道的实现
- [07 - 缓冲 IO 系统](07-buffered-io.md)：stdin 的同步阻塞读取机制
- [10 - WASM 与 JavaScript 命令](10-wasm-js-commands.md)：WASM 命令的加载和执行
- [11 - Worker 通信机制](11-worker-communication.md)：Worker 与主线程的消息传递
- [Shell API 参考](../references/shell-api.md)：Shell 构造函数完整选项
- [配置参考](../references/config-source.md)：cockle-config.json 完整格式
