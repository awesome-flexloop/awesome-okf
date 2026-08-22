---
type: Concept
title: "Contents 文件服务"
description: "Contents 服务提供 Jupyter 文件系统 REST API，支持文件/目录的 CRUD、检查点管理和 Notebook 读写，所有操作通过 ResourceLock 进行并发控制。"
tags: [contents, files, crud, checkpoints, rest-api, file-system]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: contents_api
    resource: /references/contents-api-source.md
    title: Contents API 信源
  - id: auth
    resource: /references/auth-api-source.md
    title: Auth API 信源
---

# Contents 文件服务

Contents 服务是 Jupyverse 的文件管理核心，提供兼容 Jupyter 的 `/api/contents` REST API，支持 Notebook 和普通文件的创建、读取、更新、删除、重命名以及检查点（checkpoint）管理。

## REST API 端点

Contents 继承 Router 和 ABC，在基类 `__init__` 中注册所有端点：

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/contents` | contents:read | 获取根目录内容列表 |
| GET | `/api/contents/{path}` | contents:read | 获取指定路径的文件/目录内容 |
| POST | `/api/contents{path}` | contents:write | 创建新文件或目录 |
| PUT | `/api/contents/{path}` | contents:write | 保存/更新文件内容 |
| PATCH | `/api/contents/{path}` | contents:write | 重命名文件/目录 |
| DELETE | `/api/contents/{path}` | contents:write | 删除文件/目录 |
| GET | `/api/contents/{path}/checkpoints` | contents:read | 获取文件的检查点列表 |
| POST | `/api/contents/{path}/checkpoints` | contents:write | 创建新检查点 |

### 端点行为细节

#### 获取内容（GET）

```
GET /api/contents/{path}?content=1
```

- `content=0` 时仅返回文件元数据（名称、路径、类型、大小、修改时间）
- `content=1`（默认）时同时返回文件内容
- 对于目录（type="directory"），`content` 字段是子文件/子目录的列表
- 对于 Notebook（type="notebook"），`content` 是 JSON 格式的 notebook 结构
- 对于普通文件（type="file"），`content` 是文本内容

#### 保存文件（PUT）

```
PUT /api/contents/{path}
Content-Type: application/json

{
  "content": "...",
  "format": "text" | "base64" | "json",
  "path": "/example.ipynb",
  "type": "notebook" | "file" | "directory"
}
```

#### 创建检查点（POST）

检查点是文件的版本快照，用于"还原到上次保存"功能：

```
POST /api/contents/{path}/checkpoints
```

返回 `Checkpoint` 对象（id + last_modified）。

## 数据模型

### Content 模型

```python
class Content(BaseModel):
    name: str                                    # 文件/目录名
    path: str                                    # 完整路径
    last_modified: str | None = None             # 最后修改时间
    created: str | None = None                   # 创建时间
    content: list[dict] | str | dict | None = None  # 文件内容
    format: str | None = None                    # 格式（text/base64/json）
    mimetype: str | None = None                  # MIME 类型
    size: int | None = None                      # 文件大小（字节）
    writable: bool                               # 是否可写
    type: str                                    # file/directory/notebook
```

### Checkpoint 模型

```python
class Checkpoint(BaseModel):
    id: str                 # 检查点 ID
    last_modified: str      # 检查点创建时间
```

### SaveContent 模型

```python
class SaveContent(BaseModel):
    content: str | dict | None = None
    format: str             # text/base64/json
    path: str
    type: str               # file/notebook/directory
```

## 抽象方法

Contents 定义了以下抽象方法，由 `fps-contents` 插件实现：

| 方法 | 职责 |
|------|------|
| `read_content(path, get_content, file_format, untrust)` | 读取文件内容（底层实现） |
| `write_content(content)` | 写入文件内容（底层实现） |
| `get_root_content(content, user)` | 获取根目录 |
| `get_content(path, content, user)` | 获取指定路径内容 |
| `save_content(path, request, response, user)` | 保存内容 |
| `create_content(path, request, user)` | 创建新文件/目录 |
| `delete_content(path, user)` | 删除文件/目录 |
| `rename_content(path, request, user)` | 重命名 |
| `create_checkpoint(path, user)` | 创建检查点 |
| `get_checkpoint(path, user)` | 获取检查点列表 |

## 并发控制

Contents 使用 `anyioutils.ResourceLock` 进行文件级并发控制：

```python
class Contents(Router, ABC):
    def __init__(self, app: App, auth: Auth):
        super().__init__(app=app)
        self.file_lock = ResourceLock()
```

`ResourceLock` 提供基于键的锁机制，确保同一文件的并发操作不会导致数据损坏。读操作可以并发执行，写操作需要排他锁。

## 插件实现

Contents 的具体实现由 `fps-contents` 插件提供：

```python
class ContentsModule(Module):
    async def prepare(self) -> None:
        app = await self.get(App)
        auth = await self.get(Auth)
        contents = _Contents(app, auth)
        self.put(contents, Contents)
```

`_Contents` 类继承 Contents ABC，实现所有抽象方法，提供基于本地文件系统的存储。通过替换这个插件，也可以实现基于 S3、数据库等其他存储后端。

## 文件监视

Contents 服务与 `FileWatcher`（由 fps-file-watcher 插件提供）协作，当文件系统发生外部变化时通知前端刷新。这通过 `jupyverse_file_watcher` 抽象层实现。

## 相关概念

- [认证授权系统](05-auth-system.md) — Contents 端点的权限控制
- [App 与 Router 基础设施](04-app-and-router.md) — Contents 如何继承 Router
- [内核管理](07-kernel-management.md) — 内核服务与文件服务的关联
- [插件开发指南](12-plugin-development.md) — 开发自定义 Contents 后端
