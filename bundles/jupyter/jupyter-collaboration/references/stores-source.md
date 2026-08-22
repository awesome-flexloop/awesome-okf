---
type: Reference
title: CRDT持久化存储源码分析
description: SQLiteYStore 和 TempFileYStore 的配置与API，CRDT更新持久化机制
tags: [backend, persistence, sqlite, ystore]
sources:
  - id: stores-py
    title: jupyter_server_ydoc/stores.py
    resource: file:///d:/spaces/SpecWeave/external/libs/jupyter/jupyter-collaboration/projects/jupyter-server-ydoc/jupyter_server_ydoc/stores.py
generated: { by: source-code-to-okf-wiki/agent, at: "2026-04-21T00:00:00Z" }
status: stable
---

# CRDT 持久化存储源码分析

## 文件定位

- **源码路径**：`projects/jupyter-server-ydoc/jupyter_server_ydoc/stores.py`
- **包含类**：`SQLiteYStore`、`TempFileYStore`

这两个类都继承自 pycrdt 提供的基类，并混入 `LoggingConfigurable` 以支持 Jupyter 的 Traitlets 配置系统。

---

## TempFileYStore

**继承**：`LoggingConfigurable, pycrdt.store.TempFileYStore`

使用元类 `TempFileYStoreMetaclass` 解决多重继承的 metaclass 冲突。

| 属性 | 值 | 说明 |
|---|---|---|
| `prefix_dir` | `"jupyter_ystore_"` | 临时文件目录前缀 |

临时存储适用于测试和不需要持久化的场景，服务重启后所有协作历史丢失。

---

## SQLiteYStore

**继承**：`LoggingConfigurable, pycrdt.store.SQLiteYStore`

使用元类 `SQLiteYStoreMetaclass` 解决多重继承的 metaclass 冲突。

SQLiteYStore 是默认的持久化后端，将 CRDT 文档更新（Yjs updates）存储在 SQLite 数据库中。

### 可配置 Traitlets

| Traitlet | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `db_path` | Unicode | `".jupyter_ystore.db"` | SQLite数据库文件路径，相对于当前工作目录 |
| `squash_after_inactivity_of` | Int | `None` | 文档不活跃多久后压缩历史（秒），None表示永不压缩 |
| `document_ttl` | Int | `None` | **已废弃**，使用 `squash_after_inactivity_of` 代替 |

### 工作机制

SQLiteYStore 来自 pycrdt 库，核心功能：

1. **增量存储**：每次CRDT更新（Yjs update）都作为一条记录追加到数据库
2. **启动时重放**：房间初始化时，通过 `ystore.apply_updates(ydoc)` 从数据库重放所有更新重建文档状态
3. **状态向量编码**：`ystore.encode_state_as_update(ydoc)` 将完整文档状态编码为更新写入数据库
4. **历史读取**：`ystore.read()` 异步迭代所有 `(update, timestamp)` 对，用于时间线功能

### 元类模式

由于同时继承 `LoggingConfigurable`（使用 `MetaHasTraits`）和 `_SQLiteYStore`（可能有自己的metaclass），需要创建组合元类：

```python
class SQLiteYStoreMetaclass(type(LoggingConfigurable), type(_SQLiteYStore)):
    pass

class SQLiteYStore(LoggingConfigurable, _SQLiteYStore, metaclass=SQLiteYStoreMetaclass):
    ...
```

这种模式解决了Python的"metaclass conflict"错误。

### 配置绑定

在 `YDocExtension.initialize_handlers()` 中，通过 `partial` 将 Jupyter 配置绑定到 YStore 类：

```python
ystore_class = partial(self.ystore_class, config=self.config)
```

这样当 handler 实例化 YStore 时，自动传入当前的 Jupyter 配置对象。

### 每个文档的YStore实例

在 `YDocWebSocketHandler.prepare()` 中，每个 DocumentRoom 创建独立的 YStore 实例：

```python
updates_file_path = f".{file_type}:{file_id}.y"
ystore = self._ystore_class(
    path=updates_file_path,
    log=self.log,
)
```

注意：`db_path` Traitlet 配置的是数据库文件名，但实例化时传入的 `path` 参数是 pycrdt 基类使用的路径参数。SQLiteYStore 的实际数据库位置取决于 pycrdt 的实现。

## 自定义YStore

要实现自定义的YStore后端（如Redis、PostgreSQL），需要：

1. 继承 `pycrdt.store.BaseYStore`
2. 实现异步方法：`start()`, `apply_updates()`, `encode_state_as_update()`, `read()`
3. 混入 `LoggingConfigurable`（如需要Traitlets配置）
4. 通过 `c.YDocExtension.ystore_class` 配置替换

## 相关概念

- [CRDT持久化存储](../concepts/04-ystore-persistence.md)
- [YDocExtension后端扩展配置](../concepts/02-ydoc-extension.md)
- [文档房间管理](../concepts/03-document-room.md)
