---
type: Concept
title: 浏览器存储
description: LocalForage/IndexedDB存储架构、三store设计、文件/计数器/检查点分离存储策略
tags: [storage, localforage, indexeddb, offline, checkpoint, persistence]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:20:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: contents-source
    resource: /references/contents-source.md
    title: 内容管理信源
---

## LocalForage 存储层

JupyterLite 使用 [LocalForage](https://localforage.github.io/localForage/) 作为浏览器持久化存储层。LocalForage 是一个封装了 IndexedDB、WebSQL 和 localStorage 的库，提供类似 `localStorage` 的简单API，但支持异步、大容量存储（IndexedDB通常有几百MB到几GB的配额）。

### 存储实例配置

BrowserStorageDrive 在初始化时创建三个独立的 LocalForage 实例：

```typescript
protected createDefaultStorage(): LocalForage {
  return this._localforage.createInstance({
    description: 'Offline Storage for Notebooks and Files',
    storeName: 'files',
    version: 1,
    name: this._storageName,  // 'JupyterLite Storage'
    ...this.defaultStorageOptions,
  });
}
```

三个实例共享 `name: 'JupyterLite Storage'`（同一个IndexedDB数据库），但使用不同的 `storeName`（对象仓库）：

| Store Name | 实例变量 | 用途 | Key格式 |
|------------|----------|------|---------|
| `'files'` | `_storage` | 文件和Notebook内容 | 文件路径字符串（如 `notebooks/test.ipynb`） |
| `'counters'` | `_counters` | 新建文件计数器 | 文件类型（`'notebook'`/`'file'`/`'directory'`） |
| `'checkpoints'` | `_checkpoints` | 文件检查点历史 | 文件路径字符串 |

### 存储驱动选择

默认情况下 LocalForage 自动选择最佳驱动（优先 IndexedDB），可通过 `storageDrivers` 选项指定：

```typescript
// 默认选项
{ version: 1, name: 'JupyterLite Storage' }
// 可指定驱动
{ driver: ['indexeddb', 'webSQL', 'localstorage'] }
```

## 文件存储模型

每个文件在 LocalForage 中存储为一个 `Contents.IModel` 对象：

```typescript
interface IModel {
  name: string;           // 文件名
  path: string;           // 完整路径
  last_modified: string;  // ISO时间戳
  created: string;        // ISO时间戳
  format: 'json' | 'text' | 'base64';
  mimetype: string;       // MIME类型
  content: any;           // 文件内容（null表示不返回内容）
  size: number;           // 字节大小
  writable: boolean;      // 是否可写
  type: 'notebook' | 'file' | 'directory';
}
```

### 不同文件类型的存储

| 文件类型 | format | content类型 | mimetype示例 |
|----------|--------|-------------|-------------|
| Notebook (`.ipynb`) | `'json'` | INotebookContent对象 | `application/json` |
| Python脚本 (`.py`) | `'text'` | 字符串 | `text/x-python` |
| Markdown (`.md`) | `'text'` | 字符串 | `text/markdown` |
| JSON文件 | `'json'` | JSON对象 | `application/json` |
| 图片/二进制 | `'base64'` | Base64编码字符串 | `image/png`等 |
| 目录 | `'json'` | IModel[]（子文件列表） | `application/json` |

### 空Notebook模板

新建Notebook时使用的空模板（`Private.EMPTY_NB`）：

```json
{
  "metadata": { "orig_nbformat": 4 },
  "nbformat_minor": 5,
  "nbformat": 4,
  "cells": []
}
```

## 检查点系统

检查点（Checkpoint）提供类似"版本历史"的功能，每个文件最多保留 **5个检查点**（`N_CHECKPOINTS = 5`）。

### 检查点存储结构

检查点存储在 `checkpoints` store 中，key是文件路径，value是IModel数组：

```typescript
// checkpoints[path] = [IModel, IModel, ...]
// 最多保留5个，超出时删除最旧的
copies.push(item);
if (copies.length > N_CHECKPOINTS) {
  copies.splice(0, copies.length - N_CHECKPOINTS);
}
```

### 检查点API

| API | 说明 |
|-----|------|
| `createCheckpoint(path)` | 创建新检查点（保存当前文件快照） |
| `listCheckpoints(path)` | 列出所有检查点（返回id和last_modified） |
| `restoreCheckpoint(path, id)` | 恢复到指定检查点（id是数组索引） |
| `deleteCheckpoint(path, id)` | 删除指定检查点 |

注意：重命名文件时会删除旧路径的检查点，但不会迁移到新路径。

## 计数器机制

为了避免新文件命名冲突（如 `Untitled.ipynb`、`Untitled1.ipynb`），`counters` store 记录每种文件类型的递增计数器：

| 类型 | 命名格式 | 计数器key |
|------|----------|-----------|
| Notebook | `Untitled{N}.ipynb` | `'notebook'` |
| 文件 | `untitled{N}{ext}` | `'file'` |
| 目录 | `Untitled Folder{N}` | `'directory'` |

计数器从-1开始，每次创建新文件时递增：

```typescript
private async _incrementCounter(type: Contents.ContentType): Promise<number> {
  const counters = await this.counters;
  const current = ((await counters.getItem(type)) as number) ?? -1;
  const counter = current + 1;
  await counters.setItem(type, counter);
  return counter;
}
```

## 服务器文件分层

BrowserStorageDrive 不仅访问本地IndexedDB文件，还合并了**站点静态文件**：

```
文件读取优先级：
1. 本地IndexedDB (BrowserStorage) — 用户创建/修改的文件
2. 服务器静态文件 (Site Drive)   — 部署时打包的示例文件
```

### 服务器文件获取

通过 `_getServerContents()` 和 `_getServerDirectory()` 获取：

1. 查找 `__all__.json` 索引文件（由构建系统生成，列出目录内容）
2. 对于非目录文件，通过 `fetch('/files/{path}')` 获取内容
3. 根据MIME类型和扩展名自动判断format（json/text/base64）

### 文件合并逻辑

在 `get()` 和 `_getFolder()` 中，本地文件优先于服务器文件：

```typescript
// 目录列表合并
const contentMap = new Map<string, IModel>();
// 先加本地文件
await storage.iterate((file, key) => { contentMap.set(file.name, file); });
// 再加服务器文件（不覆盖本地文件）
for (const file of serverContents) {
  if (!contentMap.has(file.name)) {
    contentMap.set(file.name, file);
  }
}
```

## 存储生命周期

### 初始化

1. 构造函数创建 PromiseDelegate 作为 ready promise
2. `initialize()` 调用 `initStorage()`
3. `initStorage()` 并行创建三个 LocalForage 实例
4. resolve ready promise

### 清理

`clearStorage()` 并行清空三个store：

```typescript
async clearStorage(): Promise<void> {
  await Promise.all([
    (await this.storage).clear(),
    (await this.counters).clear(),
    (await this.checkpoints).clear(),
  ]);
}
```

### 删除文件

`delete(path)` 删除指定路径及其所有子路径（前缀匹配）：

```typescript
async delete(path: string): Promise<void> {
  const slashed = `${path}/`;
  const toDelete = (await storage.keys()).filter(
    (key) => key === path || key.startsWith(slashed),
  );
  await Promise.all(toDelete.map(this.forgetPath, this));
}
```

`forgetPath()` 同时从 files 和 checkpoints 中移除。

## 相关概念

- [内容管理与文件系统](/concepts/03-contents-and-filesystem.md)
- [Service Worker桥接](/concepts/04-service-worker-bridge.md)
- [整体架构](/concepts/01-architecture-overview.md)
- [Python构建系统](/concepts/06-build-system.md)
