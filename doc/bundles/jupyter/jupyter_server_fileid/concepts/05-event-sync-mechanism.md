---
okf_version: "0.2"
type: concept
title: "事件驱动同步与带外检测"
description: "详解 jupyter_events 事件监听机制、contents service 事件格式、事件处理器映射，以及 LocalFileIdManager 的带外移动检测算法。"
tags: [jupyter, fileid, events, sync, oob-detection, inode-tracking]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: extension-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/extension.py"
    title: "extension.py"
  - id: manager-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/manager.py"
    title: "manager.py"
---

# 事件驱动同步与带外检测

jupyter_server_fileid 采用两种机制维护 ID↔路径映射的一致性：**事件驱动同步**（in-band）和**带外变更检测**（out-of-band，仅 LocalFileIdManager）。

## 事件驱动同步（In-Band）

当用户通过 JupyterLab/Notebook 界面操作文件时，jupyter_server 的 contents service 会发出结构化事件。File ID 扩展监听这些事件并自动更新索引。

### 事件注册流程

```python
# FileIdExtension.initialize_event_listeners()
handlers_by_action = self.file_id_manager.get_handlers_by_action()

async def cm_listener(logger, schema_id, data):
    handler = handlers_by_action[data["action"]]
    if handler:
        handler(data)

self.settings["event_logger"].add_listener(
    schema_id="https://events.jupyter.org/jupyter_server/contents_service/v1",
    listener=cm_listener,
)
```

1. 从管理器获取 `handlers_by_action` 字典
2. 定义异步监听器 `cm_listener`
3. 向 `EventLogger` 注册监听器，监听 contents service v1 schema
4. 事件到达时，根据 `data["action"]` 分发到对应 handler

### Contents Service 事件

监听的事件 schema：`https://events.jupyter.org/jupyter_server/contents_service/v1`

事件数据包含 `action` 字段标识操作类型：

| Action | 触发时机 | 事件数据字段 | Arbitrary Handler | Local Handler |
|--------|---------|-------------|-------------------|---------------|
| `get` | 获取文件内容 | `path` | None（忽略） | None（忽略） |
| `save` | 保存文件 | `path` | None（忽略） | `save(data["path"])` |
| `rename` | 重命名/移动 | `source_path`, `path` | `move(source_path, path)` | `move(source_path, path)` |
| `copy` | 复制文件 | `source_path`, `path` | `copy(source_path, path)` | `copy(source_path, path)` |
| `delete` | 删除文件 | `path` | `delete(path)` | `delete(path)` |

### handler 映射实现

**ArbitraryFileIdManager**：
```python
def get_handlers_by_action(self):
    return {
        "get": None,
        "save": None,           # 不跟踪 stat 变化
        "rename": lambda data: self.move(data["source_path"], data["path"]),
        "copy": lambda data: self.copy(data["source_path"], data["path"]),
        "delete": lambda data: self.delete(data["path"]),
    }
```

**LocalFileIdManager**：
```python
def get_handlers_by_action(self):
    return {
        "get": None,
        "save": lambda data: self.save(data["path"]),   # 更新 mtime
        "rename": lambda data: self.move(data["source_path"], data["path"]),
        "copy": lambda data: self.copy(data["source_path"], data["path"]),
        "delete": lambda data: self.delete(data["path"]),
    }
```

### 为什么 get 和 save 被忽略？

- **get**：仅读取文件，不改变文件位置或状态，无需更新索引
- **Arbitrary 的 save**：ArbitraryFileIdManager 不存储 stat 信息，保存文件不影响纯路径映射
- **Local 的 save**：更新 mtime 以保持 stat 信息一致，确保后续 get_path() 验证通过

## 带外变更检测（Out-of-Band）

当用户通过文件管理器、命令行或其他程序操作文件时（不经过 Jupyter），jupyter_events 不会发出事件。LocalFileIdManager 通过基于 inode 的检测机制处理这种情况。

### 核心原理：inode 身份

在类 Unix 文件系统和 NTFS 中，每个文件有一个唯一的 inode（或文件索引）号。即使文件被重命名或移动到同一文件系统的其他位置，inode 号保持不变。LocalFileIdManager 利用这一特性：

1. 记录文件的 `ino`（inode 号）作为身份标识
2. 记录 `crtime`（创建时间）防止 inode 重用导致误判
3. 当路径与记录不匹配时，通过 ino 查找文件的新路径

### _sync_file() — 单文件同步

这是带外检测的核心方法：

```python
def _sync_file(self, path: str, stat_info: StatStruct) -> Optional[str]:
    # 1. 符号链接不处理
    if stat_info.is_symlink:
        return None

    # 2. 通过 ino 查找旧记录
    src = self.con.execute(
        "SELECT id, path, crtime FROM Files WHERE ino = ?", (stat_info.ino,)
    ).fetchone()

    # 3. ino 未找到 → 新文件，返回 None（由调用方 _create）
    if src is None:
        return None
    id, old_path, crtime = src

    # 4. crtime 不匹配 → inode 被重用（文件删除后新文件用了同 inode）
    if crtime != stat_info.crtime:
        self.con.execute("DELETE FROM Files WHERE id = ?", (id,))
        return None

    # 5. crtime 匹配 → 同一文件被移动了，更新路径
    self._update(id, path=path)

    # 6. 如果是目录且路径变化 → 递归更新子路径
    if stat_info.is_dir and old_path != path:
        self._move_recursive(old_path, path)
        self._update_cursor = True  # 通知 _sync_all 重新查询

    return id
```

关键判断流程：

```
文件 at path X, ino=100, crtime=T1
  → 查 DB: ino=100 → 找到记录: id=A, path=Y, crtime=T1
  → crtime 匹配?
    ├─ 是 → 文件从 Y 移动到了 X → UPDATE path, _move_recursive → 返回 id=A
    └─ 否 → inode 重用（旧文件已删除，新文件用了 ino=100）→ DELETE 旧记录 → 返回 None
  → 查 DB: ino=100 不存在 → 新文件 → 返回 None
```

### _sync_all() — 全量目录同步

当 get_path() 乐观查询失败时触发全量同步：

```python
def _sync_all(self) -> None:
    now = time.time()
    cursor = self.con.execute("SELECT path, mtime FROM Files WHERE is_dir = 1")
    self._update_cursor = False
    dir = cursor.fetchone()

    while dir:
        path, old_mtime = dir
        stat_info = self._stat(path)

        if stat_info is None:
            # 目录已删除，跳过
            dir = cursor.fetchone()
            continue

        new_mtime = stat_info.mtime
        dir_dirty = new_mtime != old_mtime

        if dir_dirty:
            self._sync_dir(path)              # 同步目录内容
            self.index(path, stat_info, commit=False)  # 更新目录记录

        if self._update_cursor:
            # 目录移动导致路径变化，需要重新查询游标
            self._update_cursor = False
            cursor = self.con.execute("SELECT path, mtime FROM Files WHERE is_dir = 1")

        dir = cursor.fetchone()

    self._last_sync = now
```

算法逻辑：
1. 查询所有已索引目录（`is_dir=1`）的 path 和 mtime
2. 对每个目录，stat 获取当前 mtime
3. 如果 mtime 不同（脏目录）：
   - 调用 `_sync_dir()` 遍历目录内容，对每个 entry 调用 `_sync_file()`
   - 重新 index 该目录更新 mtime 记录
4. 如果 `_update_cursor=True`（某个目录被移动了），重新查询游标
5. 更新 `_last_sync` 时间戳

### _sync_dir() — 目录内容同步

```python
def _sync_dir(self, dir_path: str) -> None:
    with os.scandir(dir_path) as scan_iter:
        for entry in scan_iter:
            stat_info = self._stat(entry.path)
            if stat_info is None:
                continue
            id = self._sync_file(entry.path, stat_info)

            # 未索引的目录 → 创建记录并递归同步
            if stat_info.is_dir and id is None:
                self._create(entry.path, stat_info)
                self._sync_dir(entry.path)
```

使用 `os.scandir()`（高效目录遍历）扫描每个子项：
- 对每个 entry 调用 `_sync_file()` 尝试匹配已有记录
- 如果是目录且未被索引（id is None），创建新记录并递归同步其子内容

### get_path() 乐观策略

```python
def get_path(self, id: str) -> Optional[str]:
    for retry in [True, False]:
        row = self.con.execute(
            "SELECT path, ino, crtime FROM Files WHERE id = ?", (id,)
        ).fetchone()

        if not row:
            return None

        path, ino, crtime = row
        stat_info = self._stat(path)

        if stat_info and ino == stat_info.ino and crtime == stat_info.crtime:
            # 快速路径：文件仍在原位，直接返回
            return self._from_normalized_path(path)

        # 第一次失败 → 全量同步后重试
        if retry:
            self._sync_all()

    # 同步后仍找不到 → 文件确实不存在了
    return None
```

这是一个经典的"乐观锁+回退"模式：
- **最佳情况**（大多数时候）：文件没动，直接返回，不触发全量扫描
- **最坏情况**：文件被移动，一次全量同步（遍历所有脏目录）后找到新路径
- **失败情况**：文件已删除（ino 不存在或 crtime 不匹配且同步后仍找不到），返回 None

### 启动全量索引

LocalFileIdManager 初始化时调用 `_index_all()`，递归扫描 root_dir 下所有目录和文件：

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # ... 创建表和索引 ...
    self._index_all()       # 启动时递归索引
    self.con.commit()

def _index_all(self):
    stat_result = self._stat(self.root_dir)
    if stat_result is not None:
        self._index_dir_recursively(self.root_dir, stat_result)
```

这确保服务启动时所有文件都已被索引，不会因为重启丢失索引记录。

## 事务边界

两种管理器在公开方法中使用 `with self.con:` 上下文管理器确保事务原子性：

```python
def move(self, old_path, new_path):
    with self.con:
        old_path = self._normalize_path(old_path)
        new_path = self._normalize_path(new_path)
        # ... 多个 SQL 操作 ...
        return id
```

`with self.con:` 在进入时开始隐式事务，退出时自动 commit（若异常则 rollback）。私有辅助方法（`_create`、`_update`、`_sync_file` 等）不自行 commit，由调用方控制事务边界。

---

**相关文档：**
- [抽象基类与核心 API](03-file-id-manager.md) — 方法接口定义
- [双管理器对比](04-arbitrary-vs-local.md) — Arbitrary vs Local 差异
- [REST API 端点](06-http-api.md) — HTTP 查询接口
