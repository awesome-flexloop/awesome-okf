---
okf_version: "0.2"
type: concept
title: "工作区管理"
description: "深入理解多工作区布局持久化、slugify安全文件名转换、WorkspacesManager CRUD操作、WorkspacesHandler REST API和工作区CLI工具。"
tags: [workspaces, layout, persistence, slugify, crud, cli, workspace-manager]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: workspaces-handler-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/workspaces_handler.py"
    title: "jupyterlab_server/workspaces_handler.py"
  - id: workspaces-app-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/workspaces_app.py"
    title: "jupyterlab_server/workspaces_app.py"
---

# 工作区管理

工作区（Workspace）是 JupyterLab 中用于保存和恢复界面布局的机制。每个工作区保存了当前打开的文件、面板位置、标签页排列等状态信息，用户可以在不同工作区间切换以适应不同的工作场景。

## 工作区概念

### 什么是工作区？

一个工作区对应一个JSON文件，保存JupyterLab前端的完整布局状态。典型工作区数据结构：

```json
{
  "data": {
    "layout-restorer": { "main": {...}, "left": {...}, "right": {...} },
    "file-browser": { "path": "" },
    ...
  },
  "metadata": {
    "id": "/lab/workspaces/my-project",
    "name": "my-project",
    "last_modified": "2024-01-01T00:00:00.000000Z",
    "created": "2024-01-01T00:00:00.000000Z"
  }
}
```

### 默认工作区

ID为 `/` 的工作区是默认工作区，保存在 `default.jupyterlab-workspace` 文件中。访问 `/lab` URL时自动加载默认工作区。

## slugify 文件名安全化

```python
def slugify(text, base=""):
```

将工作区名称（可能包含URL特殊字符）转换为安全的文件名：

1. 移除非字母数字字符
2. 生成 `unidecoded` ASCII表示
3. 转换为小写
4. 去除首尾空白和非字母数字
5. 重复字符去重
6. 超过32字符截断并加上8字符SHA256 hash（避免碰撞）
7. 如果base参数不为空，附加base目录

例如：`"My Project!"` → `"my-project"`, `"Very Long Workspace Name"` → `"very-long-workspace-<hash>"`

## WorkspacesManager CRUD

```python
class WorkspacesManager(LoggingConfigurable):
```

工作区数据管理器，通过traitlets配置：

| Trait | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| `workspaces_dir` | Unicode | jupyter_path("lab") | 工作区保存目录 |

### 核心方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `list_workspaces()` | `() -> tuple(list, str)` | 列出所有工作区，返回 (workspaces_list, error_msg) |
| `workspace_path(space_name)` | `(str) -> str` | 工作区名→文件名转换 |
| `delete(space_name)` | `(str) -> None` | 删除工作区 |
| `get(space_name, ...)` | `(str, **kwargs) -> dict` | 获取工作区数据（不含data字段） |
| `save(space_name, data)` | `(str, dict) -> None` | 保存/更新工作区 |

### 工作区文件格式

- 扩展名：`.jupyterlab-workspace`（常量 `WORKSPACE_EXTENSION`）
- 格式：JSON（通过 json5 解析，支持注释）
- 编码：UTF-8
- 元数据自动管理：last_modified（UTC）、created（首次保存时）

### 错误处理

| 异常 | HTTP状态码 | 场景 |
|------|-----------|------|
| `coroutine_return_error` (400) | 400 | 请求体data不是JSON |
| `coroutine_return_error` (409) | 409 | PUT时data.metadata.id与URL路径不匹配 |
| `tornado.web.HTTPError(404)` | 404 | 获取/删除不存在的工作区 |
| `tornado.web.HTTPError(404)` | 404 | 工作区目录不存在 |

## WorkspacesHandler REST API

```python
class WorkspacesHandler(APIHandler):
```

### 路由

- `GET /lab/api/workspaces/` — 列出所有工作区
- `GET /lab/api/workspaces/{space_name}` — 获取单个工作区
- `PUT /lab/api/workspaces/{space_name}` — 保存/创建工作区
- `DELETE /lab/api/workspaces/{space_name}` — 删除工作区

### GET /lab/api/workspaces/

返回所有工作区列表（不含data字段，减小payload）：
```json
{
  "workspaces": [
    { "metadata": { "id": "/", "name": "default", "last_modified": "...", "created": "..." } },
    { "metadata": { "id": "/lab/workspaces/my-project", ... } }
  ],
  "ids": ["/", "/lab/workspaces/my-project"]
}
```

### PUT /lab/api/workspaces/{space_name}

保存工作区：
1. 验证请求体是有效JSON
2. 验证 `data.metadata.id` 与URL路径中的space_name匹配（409 Conflict）
3. 调用 `workspaces_manager.save()` 写入文件
4. 返回保存后的工作区数据

## 工作区CLI工具

`workspaces_app.py` 提供三个CLI命令，均继承自 `LabWorkspacesApp` 基类（提供公共路径配置）。

### WorkspaceListApp

列出所有工作区：

```bash
python -m jupyterlab_server.workspaces list
python -m jupyterlab_server.workspaces list --workspaces-dir /path/to/workspaces
python -m jupyterlab_server.workspaces list --LabServerApp.workspaces_dir=/path/to
```

输出格式：
```
{
  "workspaces": [ ... ],
  "ids": ["/", "/workspace1", ...]
}
```

### WorkspaceExportApp

导出工作区到stdout或文件：

```bash
# 导出默认工作区到stdout
python -m jupyterlab_server.workspaces export

# 导出指定工作区到stdout
python -m jupyterlab_server.workspaces export my-workspace

# 导出到文件
python -m jupyterlab_server.workspaces export --output-dir ./exports
python -m jupyterlab_server.workspaces export my-workspace --output /path/to/output.json
```

文件名规则：
- 默认工作区：`default.jupyterlab-workspace`
- 命名工作区：`{slugify(name)}.jupyterlab-workspace`

### WorkspaceImportApp

从JSON文件导入工作区：

```bash
# 导入文件（使用文件中metadata.id作为工作区名）
python -m jupyterlab_server.workspaces import workspace.json

# 导入并重命名
python -m jupyterlab_server.workspaces import workspace.json --name new-name
```

导入逻辑：
1. 读取JSON文件
2. 如果指定了--name参数，重命名工作区
3. 调用manager.save()保存
4. 输出导入的工作区名

---

**下一步阅读：**
- [主题、列表与许可证](07-themes-listings-licenses.md)
- [国际化](08-internationalization.md)
