---
type: Reference
title: JupyterLite 内容管理系统源码信源
description: BrowserStorageDrive、DriveFS、ContentsAPI、ServiceWorkerContentsAPI及Emscripten文件系统桥接的源码API登记
tags: [contents, drivefs, emscripten, service-worker, indexeddb, localforage]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:04:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: contents-drive
    resource: /references/contents-source.md
    title: packages/services/src/contents/drive.ts
  - id: contents-drivefs
    resource: /references/contents-source.md
    title: packages/services/src/contents/drivefs.ts
  - id: contents-emscripten
    resource: /references/contents-source.md
    title: packages/services/src/contents/emscripten.ts
---

## 源码位置

- `packages/services/src/contents/drive.ts` — BrowserStorageDrive（~1220行）
- `packages/services/src/contents/drivefs.ts` — DriveFS + ContentsAPI（~821行）
- `packages/services/src/contents/emscripten.ts` — Emscripten FS类型定义（~162行）
- `packages/services/src/contents/drivecontents.ts` — DriveContentsProcessor
- `packages/services/src/contents/sitedrive.ts` — SiteDrive（静态站点文件驱动）
- `packages/services/src/contents/tokens.ts` — 令牌与MIME类型定义

## 导出 API

### 常量（emscripten.ts / drivefs.ts）

| 常量 | 值 | 说明 |
|------|-----|------|
| `DIR_MODE` | 16895 (0o40777) | 默认目录权限 |
| `FILE_MODE` | 33206 (0o100666) | 默认文件权限 |
| `SEEK_CUR` | 1 | 从当前位置seek |
| `SEEK_END` | 2 | 从文件末尾seek |
| `DRIVE_NAME` | `'BrowserStorage'` | BrowserStorageDrive驱动器名 |
| `DRIVE_SEPARATOR` | `':'` | JupyterLab驱动器路径分隔符 |
| `BLOCK_SIZE` | 4096 | Emscripten FS块大小 |
| `DEFAULT_STORAGE_NAME` | `'JupyterLite Storage'` | LocalForage默认存储名 |
| `N_CHECKPOINTS` | 5 | 每个文件最大检查点数量 |

### BrowserStorageDrive（drive.ts，实现 Contents.IDrive）

| API | 签名 | 行号 |
|-----|------|------|
| `BrowserStorageDrive` | `class implements Contents.IDrive` | L140 |
| `constructor(options)` | `(options: IOptions)` | L144 |
| `name` | `get: string` → `'BrowserStorage'` | L187 |
| `serverSettings` | `get: ServerConnection.ISettings` | L194 |
| `fileChanged` | `get: ISignal<IDrive, IChangedArgs>` | L201 |
| `ready` | `get: Promise<void>` | L263 |
| `dispose()` | `() => void` | L169 |
| `getDownloadUrl(path)` | `(path: string) => Promise<string>` | L208 |
| `initialize()` | `async () => Promise<void>` | L246 |
| `newUntitled(options?)` | `(options?) => Promise<IModel>` | L354 |
| `copy(path, toDir)` | `(path, toDir) => Promise<IModel>` | L460 |
| `get(path, options?)` | `(path, options?) => Promise<IModel>` | L503 |
| `rename(oldPath, newPath)` | `(oldPath, newPath) => Promise<IModel>` | L608 |
| `save(path, options)` | `(path, options) => Promise<IModel>` | L657 |
| `delete(path)` | `async (path) => Promise<void>` | L817 |
| `createCheckpoint(path)` | `(path) => Promise<ICheckpointModel>` | L851 |
| `listCheckpoints(path)` | `(path) => Promise<ICheckpointModel[]>` | L879 |
| `restoreCheckpoint(path, id)` | `(path, id) => Promise<void>` | L896 |
| `deleteCheckpoint(path, id)` | `(path, id) => Promise<void>` | L912 |
| `clearStorage()` | `() => Promise<void>` | L339 |
| `contentProviderRegistry` | `readonly ContentProviderRegistry` | L164 |

### DriveFS（drivefs.ts）

| API | 签名 | 行号 |
|-----|------|------|
| `DriveFS` | `class` | L663 |
| `constructor(options)` | `(options: IOptions)` | L670 |
| `FS` | `FS` (Emscripten FS模块) | L664 |
| `API` | `ContentsAPI` | L665 |
| `node_ops` | `IEmscriptenNodeOps` (DriveFSEmscriptenNodeOps) | L682 |
| `stream_ops` | `IEmscriptenStreamOps` (DriveFSEmscriptenStreamOps) | L683 |
| `createAPI(options)` | `(options) => ContentsAPI` | L690 |
| `mount(mount)` | `(mount) => IEmscriptenFSNode` | L700 |
| `createNode(parent, name, mode, dev)` | `(...) => IEmscriptenFSNode` | L704 |
| `getMode(path)` | `(path) => number` | L720 |
| `realPath(node)` | `(node) => string` | L724 |

### ContentsAPI（drivefs.ts，抽象类）

| API | 签名 | 行号 |
|-----|------|------|
| `ContentsAPI` | `abstract class` | L451 |
| `lookup(path)` | `(path: string) => DriveFS.ILookup` | L460 |
| `getmode(path)` | `(path: string) => number` | L464 |
| `mknod(path, mode)` | `(path, mode) => null` | L468 |
| `rename(oldPath, newPath)` | `(oldPath, newPath) => null` | L476 |
| `readdir(path)` | `(path) => string[]` | L484 |
| `rmdir(path)` | `(path) => null` | L494 |
| `get(path)` | `(path) => DriveFS.IFile` | L498 |
| `put(path, value)` | `(path, value) => null` | L535 |
| `getattr(path)` | `(path) => IStats` | L564 |
| `normalizePath(path)` | `(path) => string` | L588 |
| `request(data)` | `abstract (data) => TDriveResponse` | L602 |

### ServiceWorkerContentsAPI（drivefs.ts，继承ContentsAPI）

| API | 签名 | 行号 |
|-----|------|------|
| `ServiceWorkerContentsAPI` | `class extends ContentsAPI` | L614 |
| `request(data)` | 同步XHR：`POST {baseUrl}api/drive` | L625 |
| `endpoint` | `get: string` → `{baseUrl}api/drive` | L655 |

### DriveFSEmscriptenNodeOps（drivefs.ts，实现IEmscriptenNodeOps）

| API | 说明 |
|-----|------|
| `getattr(node)` | 获取文件属性（委托给ContentsAPI.getattr） |
| `setattr(node, attr)` | 设置文件属性（mode/timestamp/atime/mtime/ctime/size） |
| `lookup(parent, name)` | 查找路径下的节点 |
| `mknod(parent, name, mode, dev)` | 创建文件/目录节点 |
| `rename(oldNode, newDir, newName)` | 重命名/移动 |
| `unlink(parent, name)` | 删除文件（委托给API.rmdir） |
| `rmdir(parent, name)` | 删除目录（委托给API.rmdir） |
| `readdir(node)` | 读取目录列表（委托给API.readdir） |
| `symlink(...)` | 抛出 EPERM（不支持符号链接） |
| `readlink(...)` | 抛出 EINVAL（不支持符号链接） |

### DriveFSEmscriptenStreamOps（drivefs.ts，实现IEmscriptenStreamOps）

| API | 说明 |
|-----|------|
| `open(stream)` | 打开文件流：通过API.get获取内容，写入模式下自动创建 |
| `close(stream)` | 关闭流：写模式下通过API.put回写内容 |
| `read(stream, buffer, offset, length, position)` | 同步读取数据 |
| `write(stream, buffer, offset, length, position)` | 同步写入数据，自动扩容 |
| `llseek(stream, offset, whence)` | 文件定位（支持SEEK_CUR/SEEK_END） |

### 格式转换函数（drive.ts）

| 函数 | 说明 |
|------|------|
| `convertToJSON(model)` | 将Contents模型转为json格式 |
| `convertToText(model)` | 将Contents模型转为text格式 |
| `convertToBase64(model)` | 将Contents模型转为base64格式 |

### IStats 接口（emscripten.ts）

| 字段 | 类型 |
|------|------|
| `dev` | `number` |
| `ino` | `number?` |
| `mode` | `number?` |
| `nlink` | `number` |
| `uid` | `number` |
| `gid` | `number` |
| `rdev` | `number` |
| `size` | `number` |
| `blksize` | `number` |
| `blocks` | `number` |
| `atime` | `Date \| string` |
| `mtime` | `Date \| string` |
| `ctime` | `Date \| string` |

## 内容存储架构

```
┌──────────────────────────────────────────────────────────────────┐
│                       主线程 (Main Thread)                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  JupyterLab ContentsManager                                │  │
│  │     ↕ 标准Contents API (get/save/rename/delete)            │  │
│  │  BrowserStorageDrive (drive.ts)                            │  │
│  │     ↕ LocalForage (IndexedDB)                               │  │
│  │  files store / counters store / checkpoints store          │  │
│  └────────────────────────────────────────────────────────────┘  │
│         ↕ Service Worker (POST /api/drive 同步XHR)               │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  ServiceWorkerContentsAPI                                  │  │
│  │     ↕ TDriveRequest/TDriveResponse (JSON消息)               │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
         ↕ Emscripten FS挂载 (DriveFS)
┌──────────────────────────────────────────────────────────────────┐
│                    Web Worker (Pyodide内核)                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  DriveFS (Emscripten FS实现)                                │  │
│  │  ├─ DriveFSEmscriptenNodeOps (lookup/mknod/readdir/...)   │  │
│  │  └─ DriveFSEmscriptenStreamOps (open/close/read/write)    │  │
│  │     ↓ 所有文件操作通过同步XHR请求主线程                       │  │
│  │  Pyodide / Xeus Python 内核                                 │  │
│  │  os.open / os.read / os.write → Emscripten FS → DriveFS    │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## TDriveMethod 请求类型

| 方法 | 用途 | 数据字段 |
|------|------|----------|
| `readdir` | 列出目录 | - |
| `rmdir` | 删除文件/目录 | - |
| `rename` | 重命名 | `{ newPath }` |
| `getmode` | 获取权限模式 | - |
| `lookup` | 查找节点 | - |
| `mknod` | 创建节点 | `{ mode }` |
| `getattr` | 获取属性 | - |
| `get` | 读取文件 | - |
| `put` | 写入文件 | `{ data, format }` |
