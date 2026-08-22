---
okf_version: "0.2"
type: concept
title: "REST API 端点"
description: "详解 jupyter_server_fileid 提供的两个 REST API 端点：/api/fileid/id（路径查ID）和 /api/fileid/path（ID查路径），包括请求参数、响应格式和错误处理。"
tags: [jupyter, fileid, rest-api, http, endpoints, tornado]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: handler-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/handler.py"
    title: "handler.py"
  - id: test-handler-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/tests/test_handler.py"
    title: "tests/test_handler.py"
---

# REST API 端点

jupyter_server_fileid 提供两个只读 REST API 端点，基于 Tornado Web 框架和 Jupyter Server 的 APIHandler 基类。

## API 概览

| 端点 | 方法 | 功能 | 参数 |
|------|------|------|------|
| `/api/fileid/id` | GET | 通过路径查询文件 ID | `path` (string, required) |
| `/api/fileid/path` | GET | 通过 ID 查询文件路径 | `id` (string, required) |

**基础 URL**：`http://<host>:<port>/api/fileid/`

**认证**：所有端点需要 Jupyter Server 认证（token 或 password），复用 contents 服务的权限（`auth_resource = "contents"`）。

**Content-Type**：`application/json`

## 端点一：路径查 ID

`GET /api/fileid/id`

### 请求参数

| 参数 | 类型 | 位置 | 必填 | 说明 |
|------|------|------|------|------|
| `path` | string | query | 是 | 文件的 API 路径（相对于 Jupyter Server root_dir，正斜杠分隔） |

### 成功响应 (200 OK)

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "path": "notebooks/example.ipynb"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string (UUID v4) | 文件的唯一标识符 |
| `path` | string | 请求的路径（回显） |

### 错误响应

**400 Bad Request** — 缺少 path 参数：

```json
{
  "status": 400,
  "message": "'path' parameter was not provided in the request."
}
```

**404 Not Found** — 路径未索引或不存在：

```json
{
  "status": 404,
  "message": "The ID for file, nonexistent.ipynb, could not be found."
}
```

### 示例

```bash
# 查询文件 ID
curl -H "Authorization: Token abc123" \
  "http://localhost:8888/api/fileid/id?path=notebooks/example.ipynb"
```

```python
# Python 示例
import requests

API_URL = "http://localhost:8888/api/fileid"
TOKEN = "your-token-here"
headers = {"Authorization": f"Token {TOKEN}"}

# 路径 → ID
resp = requests.get(f"{API_URL}/id", params={"path": "notebooks/example.ipynb"}, headers=headers)
data = resp.json()
file_id = data["id"]
print(f"File ID: {file_id}")
```

## 端点二：ID 查路径

`GET /api/fileid/path`

### 请求参数

| 参数 | 类型 | 位置 | 必填 | 说明 |
|------|------|------|------|------|
| `id` | string | query | 是 | 文件 ID（UUID v4 字符串） |

### 成功响应 (200 OK)

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "path": "notebooks/example.ipynb"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 请求的 ID（回显） |
| `path` | string | 文件当前的 API 路径（相对于 root_dir，正斜杠分隔） |

### 错误响应

**400 Bad Request** — 缺少 id 参数：

```json
{
  "status": 400,
  "message": "'id' parameter was not provided in the request."
}
```

**404 Not Found** — ID 不存在或文件已删除：

```json
{
  "status": 404,
  "message": "The path for file, a1b2c3d4-e5f6-7890-abcd-ef1234567890, could not be found."
}
```

### 示例

```bash
# 通过 ID 查询路径
curl -H "Authorization: Token abc123" \
  "http://localhost:8888/api/fileid/path?id=a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

```python
# Python 示例
resp = requests.get(f"{API_URL}/path", params={"id": file_id}, headers=headers)
data = resp.json()
current_path = data["path"]
print(f"Current path: {current_path}")
```

## Handler 实现细节

### BaseHandler 基类

```python
class BaseHandler(APIHandler):
    auth_resource = "contents"

    @property
    def file_id_manager(self) -> BaseFileIdManager:
        manager = self.settings.get("file_id_manager")
        assert isinstance(manager, BaseFileIdManager)
        return manager
```

- 继承 `jupyter_server.base.handlers.APIHandler`，自动获得：
  - Tornado Web 请求处理能力
  - Jupyter Server 认证体系
  - JSON 写入和错误处理
- `auth_resource = "contents"` 表示与 contents 服务共享权限模型
- `file_id_manager` 属性从 `self.settings["file_id_manager"]` 获取由 ExtensionApp 注入的管理器实例

### 认证装饰器

两个端点都使用双重装饰器：

```python
@web.authenticated    # Tornado 认证检查（未登录重定向到登录页）
@authorized           # Jupyter Server 授权检查（验证 auth_resource 权限）
def get(self) -> None:
```

### 错误处理模式

两个 Handler 采用相同的错误处理模式：

1. **MissingArgumentError**：`self.get_argument()` 在参数缺失时抛出 `tornado.web.MissingArgumentError`，被捕获并转换为 400 响应
2. **None 返回值**：管理器方法返回 None 时（文件未找到），抛出 `web.HTTPError(404, ...)`
3. **Tornado 自动处理**：未捕获的异常由 Tornado 的错误处理机制转换为适当的 HTTP 响应

### FileIDHandler vs FilePathHandler 对称性

两个 Handler 的代码结构完全对称：

| 方面 | FileIDHandler | FilePathHandler |
|------|--------------|----------------|
| 参数 | `path` | `id` |
| 管理器方法 | `get_id(path)` | `get_path(id)` |
| 404 消息 | "The ID for file, {path}, could not be found." | "The path for file, {id}, could not be found." |
| 响应字段 | `{"id": id, "path": path}` | `{"id": id, "path": path}` |

## 在前端扩展中使用

前端扩展（JupyterLab 插件等）可以通过这两个 API 实现文件引用的稳定性：

```typescript
// JupyterLab 扩展示例
async function getFileId(path: string): Promise<string> {
  const response = await fetch(`/api/fileid/id?path=${encodeURIComponent(path)}`, {
    headers: { Authorization: `Token ${token}` }
  });
  if (!response.ok) throw new Error(`Failed to get file ID: ${response.status}`);
  const data = await response.json();
  return data.id;
}

async function getFilePath(id: string): Promise<string> {
  const response = await fetch(`/api/fileid/path?id=${id}`, {
    headers: { Authorization: `Token ${token}` }
  });
  if (!response.ok) throw new Error(`Failed to get file path: ${response.status}`);
  const data = await response.json();
  return data.path;
}

// 使用场景：存储引用时存 ID 而非路径，使用时通过 ID 反查当前路径
const fileId = await getFileId("notebooks/analysis.ipynb");
// ... 之后即使文件被移动 ...
const currentPath = await getFilePath(fileId);  // 返回新路径
```

---

**相关文档：**
- [handler.py 源码解析](../references/handler-source.md) — Handler 完整源码
- [抽象基类与核心 API](03-file-id-manager.md) — get_id/get_path 方法
- [事件驱动同步机制](05-event-sync-mechanism.md) — 文件移动后路径更新
