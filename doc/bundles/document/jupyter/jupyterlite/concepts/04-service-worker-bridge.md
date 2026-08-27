---
type: Concept
title: Service Worker 桥接机制
description: Service Worker在JupyterLite中的双重角色：离线资源缓存与内核文件系统同步桥接
tags: [service-worker, offline, cache, drive-api, synchronous-bridge]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:18:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: contents-source
    resource: /references/contents-source.md
    title: 内容管理信源
  - id: app-source
    resource: /references/app-source.md
    title: 应用框架信源
---

## Service Worker 的双重角色

JupyterLite 中的 Service Worker 承担两个核心职责：

1. **离线缓存**：缓存应用静态资源（JS、CSS、WASM、Python包等），实现离线可用
2. **文件系统桥接**：作为 Web Worker 内核对主线程内容管理器的同步请求中介

## 为什么需要 Service Worker 桥接？

JupyterLite 的文件系统桥接面临一个根本性的异步-同步不匹配问题：

| 上下文 | API特性 | 可使用的通信方式 |
|--------|---------|-----------------|
| **Web Worker（内核）** | Emscripten POSIX API 是**同步**的 | postMessage（异步）、**同步XHR**（同步） |
| **主线程** | IndexedDB/LocalForage 是**异步**的 | postMessage（异步） |

Web Worker 中的同步 POSIX 调用（如 `open()`、`read()`）需要**立即**得到结果，但主线程的存储API是异步的。解决方案是：

1. Web Worker 使用**同步 XMLHttpRequest**（Worker 中允许，不阻塞主线程UI）
2. Service Worker 拦截该 XHR 请求
3. Service Worker 通过 `postMessage` 向主线程转发请求
4. 主线程异步完成 BrowserStorageDrive 操作后返回结果
5. Service Worker 将结果作为 XHR 响应返回给 Worker
6. Worker 中的同步 XHR 解除阻塞，获得结果

## /api/drive 端点

Service Worker 拦截的核心端点是 `POST {baseUrl}api/drive`。

### 请求格式

ServiceWorkerContentsAPI 发送的请求体（JSON）：

```json
{
  "data": {
    "method": "get|put|readdir|rmdir|rename|lookup|mknod|getattr|getmode",
    "path": "BrowserStorage:notebooks/test.ipynb",
    "data": { ... },
    "requestId": "uuid"
  },
  "browsingContextId": "...",
  "requestId": "uuid"
}
```

- `method`：要执行的文件操作类型
- `path`：JupyterLab格式的路径（`DriveName:relative/path`）
- `data`：方法特定参数（put的文件内容、rename的新路径、mknod的mode等）
- `requestId`：UUID，用于请求-响应关联
- `browsingContextId`：标识发起请求的浏览器上下文

### 响应格式

响应是 JSON 格式的 TDriveResponse，类型取决于 method：

| method | 响应类型 |
|--------|----------|
| `readdir` | `string[]`（文件名列表） |
| `get` | `{content: any, format: 'json'\|'text'\|'base64'} \| null` |
| `getattr` | `IStats`（文件属性） |
| `lookup` | `{ok: boolean, mode?: number}` |
| `getmode` | `number` |
| `mknod/rmdir/rename/put` | `null` |

## 同步XHR请求实现

`ServiceWorkerContentsAPI.request()` 使用同步XHR：

```typescript
request<T extends TDriveMethod>(data: TDriveRequest<T>): TDriveResponse<T> {
  const xhr = new XMLHttpRequest();
  xhr.open('POST', encodeURI(this.endpoint), false);  // false = 同步!
  // 添加 requestId 和 browsingContextId
  xhr.send(JSON.stringify(requestWithMetadata));

  if (xhr.status >= 400) {
    throw new this.FS.ErrnoError(this.ERRNO_CODES['EINVAL']);
  }

  return JSON.parse(xhr.responseText);
}
```

注意点：
- `open()` 的第三个参数 `async` 设为 `false`，启用同步模式
- 使用 `UUID.uuid4()` 生成唯一 requestId
- 错误状态码映射到 Emscripten ERRNO_CODES（EINVAL/ENOENT/EPERM等）

## 离线缓存策略

Service Worker 还负责缓存静态资源以支持离线使用。典型策略包括：

1. **App Shell缓存**：首次加载时缓存HTML/CSS/JS/WASM核心文件
2. **Python包缓存**：缓存从PyPI/Conda下载的WASM Python包
3. **Stale-While-Revalidate**：缓存优先，后台更新
4. **缓存版本化**：部署新版本时更新缓存key

## 相关概念

- [整体架构](01-architecture-overview.md)
- [内容管理与文件系统](03-contents-and-filesystem.md)
- [浏览器存储](05-browser-storage.md)
- [内核系统](02-kernel-system.md)
