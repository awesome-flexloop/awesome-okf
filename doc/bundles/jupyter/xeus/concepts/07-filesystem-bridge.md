---
type: Concept
title: 文件系统桥接
description: xeus内核的Emscripten虚拟文件系统三层架构——MEMFS内核层、DriveFS/JupyterLite桥接层、构建时打包挂载层，以及工作目录切换策略
tags: [filesystem, emscripten, memfs, drivefs, sharedbuffercontentsapi, mount]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: insight-5
    resource: /concepts/07-filesystem-bridge.md
    title: 洞察I-5 三层FS架构
  - id: worker-modes
    resource: /references/worker-modes-source.md
    title: 双Worker模式
  - id: kernel-impl
    resource: /references/kernel-impl-source.md
    title: empack内核实现
---

## Emscripten 文件系统基础

Emscripten 编译的C/C++代码使用虚拟文件系统（VFS），默认提供：

| 文件系统类型 | 说明 | 持久化 |
|------------|------|--------|
| **MEMFS** | 内存文件系统，所有数据存在RAM中 | ❌ 页面刷新丢失 |
| **IDBFS** | 基于IndexedDB的持久化文件系统 | ✅ 可持久化 |
| **NODEFS** | Node.js本地文件系统映射（仅Node环境） | ✅ |
| **WORKERFS** | 提供Worker内的File/Blob访问 | ⚠️ |
| **自定义FS** | 通过FS.createNode/FS.mount挂载自定义实现 | 取决于实现 |

xeus 使用 MEMFS 作为内核文件系统，通过**自定义FS挂载**将JupyterLite Contents API桥接进来。

## 三层文件系统架构

```
┌──────────────────────────────────────────────────────────────┐
│ Layer 3: 构建时打包挂载层 (Packed Mounts)                      │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ /home/xeus/data/ ← data.tar.gz (构建时pack_directory)    │ │
│ │ /etc/myapp/      ← config.json (构建时pack_file)         │ │
│ │ /files/          ← JupyterLite files/ 目录               │ │
│ │ (启动时自动解压到MEMFS)                                    │ │
│ └──────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│ Layer 2: JupyterLite Contents API 桥接层 (Mounted FS)         │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ /drive/ ──→ DriveFS / SharedBufferContentsAPI           │ │
│ │              ↓                                            │ │
│ │         JupyterLite Contents API                          │ │
│ │              ↓                                            │ │
│ │         Service Worker / IndexedDB / 内存                 │ │
│ └──────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│ Layer 1: 内核MEMFS层 (Core MEMFS)                             │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ /usr/local/  ← bootstrapEmpackPackedEnvironment 解压     │ │
│ │   ├── bin/python (Python解释器)                          │ │
│ │   ├── lib/python3.12/ (标准库+第三方包)                   │ │
│ │   └── lib/ (共享库 .so 文件)                              │ │
│ │ /tmp/        ← Emscripten默认临时目录                     │ │
│ │ /home/       ← 用户home目录                               │ │
│ │ /files/      ← (如果mount_jupyterlite_content=true)       │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Layer 1: 内核MEMFS

这是WASM内核"看到"的根文件系统，由 [bootstrapEmpackPackedEnvironment()](../references/kernel-impl-source.md#initializefilesystem-实现) 初始化：

1. 从 `_pkgRootUrl`（`{baseUrl}xeus/{envName}/kernel_packages/`）下载所有conda包tar.gz
2. 按empack_env_meta.json中记录的文件列表解压到 `_prefix`（通常是 `/usr/local`）
3. 这包括Python解释器、标准库、预装的第三方包、共享库等
4. 所有文件都在内存中——MEMFS

内核二进制本身（xpython.js/.wasm/.data）由Emscripten的 `locateFile` 机制定位，通过 `importScripts()` 和 WebAssembly.compile() 加载。

### Layer 2: Contents API 桥接层

这是xeus与JupyterLite文件系统（用户的Notebook文件）交互的关键：

```typescript
// Worker端 mount 调用
await this.mount('drive', '/drive', baseUrl, browsingContextId);
```

两种模式使用不同的桥接实现：

#### coincident模式：SharedBufferContentsAPI

```typescript
const drive = new SharedBufferContentsAPI({
  baseUrl,
  contentsApiUrl: baseUrl + 'api/contents/'
});
drive.activate(this.workerThis, browsingContextId);
FS.mkdir(mountpoint);
FS.mount(drive, {}, mountpoint);
```

- 基于 SharedArrayBuffer + Atomics 实现**同步**文件操作
- Worker线程调用FS.read()时，通过SAB将请求传递给主线程，主线程调用Contents API后通过SAB返回结果
- Worker线程通过Atomics.wait阻塞等待，对C++代码来说是同步调用
- 不需要Service Worker参与文件桥接

#### comlink模式：DriveFS

```typescript
const drive = new DriveFS({
  FS: this.Module.FS,
  driveName,
  mountpoint,
  contents: comlinkProxy.contents(browsingContextId),
});
await drive.ready;
FS.mkdir(mountpoint);
FS.mount(drive, {}, mountpoint);
```

- JupyterLite提供的标准文件系统桥接
- 通过postMessage/comlink异步通信，但在FS层通过内部同步机制转为同步调用
- 需要DriveFS初始化完成（`await drive.ready`）
- 底层依赖Service Worker处理Contents API请求

### Layer 3: 构建时打包挂载

构建时配置的mounts在WASM内核启动时自动解压到MEMFS：

```python
# add_on.py pack_prefix()
for mount in mounts:
    if mount['from'].is_dir():
        pack_directory(path=mount['from'], mount_path=mount['to'])
    else:
        pack_file(filename=mount['from'], mount_path=mount['to'])
```

- 目录打包为tar.gz，启动时解压到指定路径
- 单个文件直接打包
- mount_jupyterlite_content启用时，`{output_dir}/files/` 被打包到 `/files`
- 这些内容在bootstrapEmpackPackedEnvironment阶段加载

**重要**：Layer 3的内容是只读快照——构建后修改不会反映到运行时。用户运行时创建的文件通过Layer 2的DriveFS持久化。

## 工作目录策略

内核启动完成后，[WebWorkerKernelBase.initFileSystem()](../references/kernel-base-source.md#webworkerkernelbase-类) 自动切换到合适的工作目录：

```typescript
const tryCd = async (path: string) => {
  if (await this.remoteKernel.isDir(path)) {
    await this.remoteKernel.cd(path);
  }
};

// 优先级从高到低
await tryCd('/files/' + localPath);  // 1. /files/{notebook目录}
await tryCd('/files');               // 2. /files（JupyterLite内容挂载）
await tryCd('/drive/' + localPath);  // 3. /drive/{notebook目录}
// 4. 默认保持在内核启动目录（通常是/或/home/xeus）
```

`localPath` 是Notebook所在的相对路径。

### 为什么优先/files？

- `/files` 对应 mount_jupyterlite_content 打包的JupyterLite内容目录
- 如果该目录存在（构建时启用了挂载），优先使用
- `/drive` 通过DriveFS挂载，始终可用，但性能不如直接MEMFS访问

## 文件操作路径解析

用户在Notebook中执行文件操作时，路径解析规则：

| 路径示例 | 解析到 | 持久化 | 性能 |
|---------|--------|--------|------|
| `./data.csv` | 当前工作目录（优先/files，其次/drive） | ✅（通过Contents API） | 取决于模式 |
| `/files/my.ipynb` | Layer 3打包或Layer 2桥接 | ⚠️ Layer3只读，Layer2可写 | Layer3快，Layer2中 |
| `/drive/notebooks/` | Layer 2 DriveFS/SharedBuffer | ✅ | 取决于模式 |
| `/tmp/test.txt` | Layer 1 MEMFS临时目录 | ❌ | 最快（内存） |
| `/usr/local/lib/` | Layer 1 MEMFS（conda包） | ❌ | 最快 |
| `~/data.json` | `/home/xeus/data.json`（MEMFS） | ❌ | 最快 |

## 文件持久化策略

### 默认持久化（DriveFS/Contents API）

- `/drive/` 下的文件通过JupyterLite Contents API存储
- JupyterLite默认使用Service Worker + IndexedDB存储
- 这些文件在页面刷新后仍然存在
- 在JupyterLab界面中可以看到和编辑

### 非持久化（MEMFS）

- `/tmp/`、`/usr/local/`、`/home/` 等MEMFS目录
- 运行时%conda install安装的包文件
- 页面刷新后丢失

### 只读快照（Packed Mounts）

- Layer 3打包的挂载内容
- 构建时固定，运行时不可修改
- 如果尝试写入，可能成功（写到MEMFS上层）但不会持久化

## 共享库文件

共享库（.so文件）有特殊处理：

1. **预链接库**：内核WASM编译时链接的核心库（libxeus、libpython等），直接在WASM模块内
2. **预装包库**：empack打包的conda包中的.so，通过 `loadSharedLibs()` 在启动时加载
3. **运行时安装的库**：%conda install后通过 `_reloadPackagesInFS()` → `loadSharedLibs()` 动态加载

`_sharedLibsToNotLink` 集合排除了核心库，避免重复加载。

## Emscripten版本差异

### Emscripten >= 4

- 支持原生动态链接（dlopen）
- `loadSharedLibs()` 不需要手动调用，动态链接器自动处理
- shared library加载更可靠

### Emscripten < 4

- 需要手动调用 `loadSharedLibs()` 加载共享库
- 通过 `Module.dlopen()` 显式加载每个.so文件
- 新安装包的共享库也需要手动加载

版本检测通过lock文件中的 `emscripten-abi` 包版本号判断。

## 文件系统操作注意事项

1. **避免在/drive下做大量小文件IO**：每次操作都经过主线程通信（尤其是comlink模式），性能较差
2. **大文件处理建议**：先复制到/tmp处理，再写回/drive
3. **路径不要硬编码/drive前缀**：使用相对路径或先检查/files是否存在
4. **crossOriginIsolated环境下FS更快**：SharedBufferContentsAPI同步调用比DriveFS异步+轮询更高效
5. **不要依赖MEMFS持久化**：重要数据通过DriveFS存储（/drive或/files下）

## 相关API

- [bootstrapEmpackPackedEnvironment()](../references/kernel-impl-source.md#initializefilesystem-实现)
- [XeusCoincidentKernel.mount()](../references/worker-modes-source.md#mount-实现)
- [XeusComlinkKernel.mount()](../references/worker-modes-source.md#mount-实现-1)
- [WebWorkerKernelBase.initFileSystem()](../references/kernel-base-source.md#webworkerkernelbase-类)
- [pack_prefix() mounts处理](../references/python-addon-source.md#pack_prefix)

## 相关概念

- [双Worker通信模式](03-dual-worker-modes.md)
- [内核生命周期](04-kernel-lifecycle.md)
- [包管理](06-package-management.md)
