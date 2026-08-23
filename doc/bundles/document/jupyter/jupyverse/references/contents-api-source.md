---
type: Reference
title: "Contents API 信源"
description: "文件内容服务抽象层，定义 Contents ABC 和相关 Pydantic 模型，提供 Jupyter 内容管理 REST API。"
tags: [contents, files, api, rest, crud, checkpoints]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: contents_init
    resource: /external/libs/jupyter/jupyverse/api/contents/src/jupyverse_contents/__init__.py
    title: jupyverse_contents/__init__.py
  - id: contents_models
    resource: /external/libs/jupyter/jupyverse/api/contents/src/jupyverse_contents/models.py
    title: jupyverse_contents/models.py
---

# Contents API 信源

## Contents 抽象基类

`Contents` 继承 `Router` 和 `ABC`，在 `__init__` 中注册所有文件操作 REST 端点。

### REST API 端点

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/contents` | contents:read | 获取根目录内容 |
| GET | `/api/contents/{path}` | contents:read | 获取指定路径内容 |
| POST | `/api/contents{path}` | contents:write | 创建新文件/目录 |
| PUT | `/api/contents/{path}` | contents:write | 保存文件内容 |
| PATCH | `/api/contents/{path}` | contents:write | 重命名文件/目录 |
| DELETE | `/api/contents/{path}` | contents:write | 删除文件/目录 |
| GET | `/api/contents/{path}/checkpoints` | contents:read | 获取检查点列表 |
| POST | `/api/contents/{path}/checkpoints` | contents:write | 创建检查点 |

### 抽象方法

| 方法 | 说明 |
|------|------|
| `read_content(path, get_content, file_format, untrust)` | 读取文件内容 |
| `write_content(content)` | 写入文件内容 |
| `create_checkpoint(path, user)` | 创建检查点 |
| `create_content(path, request, user)` | 创建新文件 |
| `get_root_content(content, user)` | 获取根目录 |
| `get_checkpoint(path, user)` | 获取检查点列表 |
| `get_content(path, content, user)` | 获取指定路径内容 |
| `save_content(path, request, response, user)` | 保存内容 |
| `delete_content(path, user)` | 删除文件 |
| `rename_content(path, request, user)` | 重命名 |

### file_lock

Contents 维护一个 `ResourceLock`（来自 anyioutils）用于文件操作的并发控制。

## 数据模型

### Content

```python
class Content(BaseModel):
    name: str
    path: str
    last_modified: str | None = None
    created: str | None = None
    content: list[dict] | str | dict | None = None
    format: str | None = None
    mimetype: str | None = None
    size: int | None = None
    writable: bool
    type: str  # "file" | "directory" | "notebook"
```

### Checkpoint

```python
class Checkpoint(BaseModel):
    id: str
    last_modified: str
```

### SaveContent

```python
class SaveContent(BaseModel):
    content: str | dict | None = None
    format: str
    path: str
    type: str
```

### CreateContent

```python
class CreateContent(BaseModel):
    ext: str | None = None
    path: str
    type: str
```
