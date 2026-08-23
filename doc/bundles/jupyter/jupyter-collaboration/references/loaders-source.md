---
type: Reference
title: 文件加载器源码分析
description: FileLoader 和 FileLoaderMapping 的实现：文件读写、轮询监听、外带变更检测、订阅通知
tags: [backend, file, loader, polling]
sources:
  - id: loaders-py
    title: jupyter_server_ydoc/loaders.py
    resource: file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter-collaboration/projects/jupyter-server-ydoc/jupyter_server_ydoc/loaders.py
generated: { by: source-code-to-okf-wiki/agent, at: "2026-04-21T00:00:00Z" }
status: stable
---

# 文件加载器源码分析

## 文件定位

- **源码路径**：`projects/jupyter-server-ydoc/jupyter_server_ydoc/loaders.py`
- **包含类**：`FileLoader`、`FileLoaderMapping`

---

## FileLoader

`FileLoader` 封装了对单个文件的所有操作，是连接 Jupyter ContentsManager 和 DocumentRoom 的桥梁。

### 构造参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `file_id` | str | 文件的唯一ID（由FileIdManager管理） |
| `file_id_manager` | BaseFileIdManager | 文件ID↔路径映射管理器 |
| `contents_manager` | AsyncContentsManager \| ContentsManager | Jupyter内容管理器 |
| `log` | Logger | 日志器 |
| `poll_interval` | float \| None | 文件轮询间隔（秒），None则不轮询 |
| `max_consecutive_logs` | int | 连续错误日志最大条数（默认3），超出后抑制 |
| `stop_poll_on_errors_after` | float \| None | 连续错误多久后停止轮询（秒） |

### 核心属性

- `path`：通过 `file_id_manager.get_path(file_id)` 动态获取文件路径（支持重命名）
- `number_of_subscriptions`：订阅该文件的房间数量
- `last_modified`：最后已知的文件修改时间

### 核心方法

#### load_content(format, file_type)

从磁盘加载文件内容：

1. 获取异步锁 `_lock`
2. 调用 `contents_manager.get(path, format=format, type=file_type, content=True)`
3. 对文本文件标准化换行符（`\r\n` → `\n`）
4. 更新 `last_modified` 时间戳
5. 返回文件模型字典

#### maybe_save_content(model)

保存内容到磁盘，带外带变更检测：

1. 获取异步锁
2. 先查询文件元信息（不含内容）检查 `last_modified`
3. **如果文件不可写**（`m["writable"] == False`）：返回 `None`，跳过保存
4. **如果 last_modified 一致**：执行保存
   - 使用 `asyncio.shield` 保护保存任务不被取消（防止文件损坏）
   - 调用 `contents_manager.save(model, path)`
   - 保存后额外get一次获取hash值
   - 返回 `{**m, "hash": hash}`
5. **如果 last_modified 不一致**：抛出 `OutOfBandChanges` 异常

#### observe(id, callback, filepath_callback=None)

订阅文件外带变更通知：

- `id`：房间ID
- `callback`：文件内容变更时的回调（协程函数）
- `filepath_callback`：文件路径变更（重命名）时的回调

#### unobserve(id)

取消订阅。

### 文件轮询机制（_watch_file）

当 `poll_interval > 0` 时，启动后台轮询任务：

```python
async def _watch_file(self):
    while True:
        await asyncio.sleep(self._poll_interval)
        try:
            await self.maybe_notify()
        except HTTPError as e:
            # 404/401错误：记录连续错误时长，超时后停止轮询
            if e.status_code in {404, 401}:
                if consecutive_errors_duration > stop_poll_on_errors_after:
                    break
        except Exception:
            # 其他错误：日志抑制机制（最多3条连续错误）
```

### 外带变更通知（maybe_notify）

```python
async def maybe_notify(self):
    do_notify = False
    filepath_change = False
    async with self._lock:
        # 检测路径变化（重命名）
        if self._current_path != path:
            filepath_change = True
        # 检测last_modified变化
        if self.last_modified < model["last_modified"]:
            do_notify = True
    
    # 锁外执行回调（避免死锁，因为callback可能需要加载内容）
    if filepath_change:
        for callback in self._filepath_subscriptions.values():
            await callback()
    if do_notify:
        for callback in self._subscriptions.values():
            await callback()
```

### clean()

停止轮询任务：

```python
async def clean(self):
    if self._watcher:
        self._watcher.cancel()
        await self._watcher  # 等待CancelledError
```

---

## FileLoaderMapping

管理多个 FileLoader 实例的映射，实现懒加载和自动清理。

### 核心方法

#### `__getitem__(file_id)` → FileLoader

获取或创建文件加载器：

1. 通过 `file_id_manager.get_path(file_id)` 获取路径
2. 如果加载器不存在，创建新的 `FileLoader` 实例
3. 返回加载器

#### `__contains__(file_id)` → bool

检查文件是否已有加载器。

#### `remove(file_id)`

移除加载器并调用其 `clean()` 方法停止轮询。

#### `clear()`

清除所有加载器，并行等待所有clean()完成。

### 设计要点

1. **懒加载**：文件加载器仅在第一个客户端连接时创建
2. **自动清理**：当最后一个订阅房间离开时，FileLoader被移除，轮询停止
3. **锁保护**：`load_content` 和 `maybe_save_content` 使用异步锁防止并发读写
4. **不可取消保存**：使用 `asyncio.shield` 确保文件写入不被任务取消中断
5. **错误容忍**：轮询遇到临时错误（超时、500等）不会停止，仅日志抑制；遇到404/401且持续过久才停止
6. **换行符标准化**：加载文本内容时自动将 `\r\n` 转换为 `\n`，避免CRDT同步问题

## OutOfBandChanges 异常

当保存时检测到文件已被外部修改（last_modified不匹配），抛出此异常。DocumentRoom 捕获后重新加载文件内容并覆盖房间状态。

## 相关概念

- [文件加载与变更监听](../concepts/07-file-loading.md)
- [文档房间管理](../concepts/03-document-room.md)
- [YDocExtension后端扩展配置](../concepts/02-ydoc-extension.md)
