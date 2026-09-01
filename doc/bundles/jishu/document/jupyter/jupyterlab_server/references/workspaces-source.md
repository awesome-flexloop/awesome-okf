---
okf_version: "0.2"
type: reference
title: "工作区管理源码（workspaces_handler.py + workspaces_app.py）"
description: "jupyterlab_server 工作区系统的完整 API：WorkspacesManager CRUD、slugify 文件名安全转换、WorkspacesHandler REST端点、工作区CLI子命令"
tags: [workspaces, workspace-manager, slugify, cli, workspace-import, workspace-export]
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

# 工作区管理源码

本信源登记工作区系统两个核心文件的API：
- `workspaces_handler.py`（约226行）：核心逻辑和REST处理器
- `workspaces_app.py`（约192行）：CLI子命令

## 常量

```python
WORKSPACE_EXTENSION = ".jupyterlab-workspace"
DEFAULT_WORKSPACE = "default"
```

## slugify() 函数

```python
def slugify(
    raw: str,
    base: str = "",
    sign: bool = True,
    max_length: int = 128 - len(WORKSPACE_EXTENSION)
) -> str:
```

将工作区名称转换为文件系统安全的文件名：

1. 确保路径以 `/` 开头
2. 如果 `sign=True`，计算SHA256哈希（取前4字符）作为后缀防碰撞
3. 提取base和raw的公共前缀，减少路径长度
4. URL解码、NFKC规范化、ASCII编码（丢弃非ASCII）
5. 移除非字母数字/下划线/连字符的字符
6. 将连续空白和连字符合并为单个 `-`
7. 截断到max_length，附加签名后缀

该算法修改自Django的 `slugify` 实用函数。

## WorkspacesManager 类

```python
class WorkspacesManager(LoggingConfigurable):
```

工作区数据管理器。

### __init__(path)

```python
def __init__(self, path: str) -> None:
```

初始化管理器。path为空字符串时抛出 `ValueError("Workspaces directory is not set")`。存储为 `Path` 对象。

### delete(space_name)

```python
def delete(self, space_name: str) -> None:
```

删除工作区：
1. slugify工作区名称
2. 检查文件是否存在，不存在则抛出 `FileNotFoundError`
3. 删除文件（`Path.unlink()`）

### list_workspaces()

```python
def list_workspaces(self) -> list:
```

列出所有工作区：
1. 使用空前缀（`slugify("", sign=False)`）匹配所有 `.jupyterlab-workspace` 文件
2. 调用 `_list_workspaces()` 返回加载后的工作区列表

### load(space_name)

```python
def load(self, space_name: str) -> dict:
```

加载单个工作区：
1. slugify名称，查找对应文件
2. 文件存在：调用 `_load_with_file_times()` 加载并注入文件时间元数据
3. 文件不存在：返回空工作区 `{"data": {}, "metadata": {"id": "/{space_name}"}}`

### save(space_name, raw)

```python
def save(self, space_name: str, raw: str) -> Path:
```

保存工作区：
1. 确保workspaces_dir存在（递归创建）
2. JSON解析raw数据
3. 验证metadata.id与space_name匹配（支持可选的前导`/`和URL编码），不匹配则抛出ValueError
4. slugify名称生成文件路径
5. 写入文件（UTF-8编码）
6. 返回文件路径

## 内部函数

### _list_workspaces(directory, prefix)

```python
def _list_workspaces(directory: Path, prefix: str) -> list[dict[str, Any]]:
```

列出目录中以prefix开头、以 `.jupyterlab-workspace` 结尾的文件，按文件名排序，加载每个工作区。

### _load_with_file_times(workspace_path)

```python
def _load_with_file_times(workspace_path: Path) -> dict:
```

加载工作区JSON，用文件stat信息覆盖metadata中的 `last_modified` 和 `created` 字段（UTC ISO格式时间戳）。

## WorkspacesHandler 类

```python
class WorkspacesHandler(ExtensionHandlerMixin, ExtensionHandlerJinjaMixin, APIHandler):
```

工作区REST API处理器。

### initialize(name, manager, **kwargs)

注入WorkspacesManager实例。

### DELETE /lab/api/workspaces/{space_name}

```python
@web.authenticated
def delete(self, space_name: str) -> None:
```

删除工作区：
- space_name为空 → 400
- 文件不存在 → 404
- 成功 → 204

### GET /lab/api/workspaces/ 或 /lab/api/workspaces/{space_name}

```python
@web.authenticated
async def get(self, space_name: str = "") -> Any:
```

获取工作区：
- 无space_name：返回 `{"workspaces": {"ids": [...], "values": [...]}}`
- 有space_name：返回单个工作区JSON

### PUT /lab/api/workspaces/{space_name}

```python
@web.authenticated
def put(self, space_name: str = "") -> None:
```

保存/创建工作区：
- space_name为空 → 400
- body为JSON字符串
- JSON解析失败或metadata.id不匹配 → 400
- 成功 → 204

## CLI 应用（workspaces_app.py）

### WorkspaceListApp

```python
class WorkspaceListApp(JupyterApp, LabConfig):
```

列出工作区CLI命令。

**Flags：**
- `--json`：输出JSON数组
- `--jsonlines`：输出JSON Lines（每行一个工作区对象）
- 默认：输出工作区ID列表，每行一个

### WorkspaceExportApp

```python
class WorkspaceExportApp(JupyterApp, LabConfig):
```

导出工作区CLI命令：
- 无参数：导出"default"工作区
- 一个参数：导出指定名称的工作区
- 输出JSON到stdout

### WorkspaceImportApp

```python
class WorkspaceImportApp(JupyterApp, LabConfig):
```

导入工作区CLI命令：
- 需要一个参数：JSON文件路径（`-`表示stdin）
- 配置项 `workspace_name`（`--name`）：覆盖导入工作区的ID
- 验证JSON包含 `data` 字段和 `metadata.id`
- 保存到workspaces_dir，输出保存路径

[F-204]
