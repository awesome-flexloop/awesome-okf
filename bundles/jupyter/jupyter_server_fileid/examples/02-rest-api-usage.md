---
okf_version: "0.2"
type: example
title: "REST API 使用示例"
description: "通过 HTTP 请求调用 jupyter_server_fileid 的 REST API 端点，实现路径与文件 ID 的双向查询，包含 curl、Python requests 和前端 fetch 示例。"
tags: [jupyter, fileid, example, rest-api, http, curl, requests, fetch]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: handler-py
    resource: "../../../../../external/libs/jupyter/jupyter_server_fileid/jupyter_server_fileid/handler.py"
    title: "handler.py"
---

# REST API 使用示例

jupyter_server_fileid 扩展为 Jupyter Server 注册了两个 REST API 端点，可以通过 HTTP 进行路径和文件 ID 的双向查询。

## 前置条件

1. Jupyter Server 已启动并安装了 jupyter_server_fileid 扩展
2. 获取服务器的认证 token（启动日志中显示，或 `jupyter server list` 查看）

```bash
# 启动 Jupyter Server（启用 fileid 扩展）
jupyter server --ServerApp.token=my-secret-token
# 服务器地址: http://localhost:8888
```

## 示例 1：使用 curl 查询

### 路径 → ID 查询

```bash
# 查询 notebooks/example.ipynb 的文件 ID
curl -H "Authorization: Token my-secret-token" \
  "http://localhost:8888/api/fileid/id?path=notebooks/example.ipynb"
```

成功响应：
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "path": "notebooks/example.ipynb"
}
```

### ID → 路径查询

```bash
# 通过 ID 查询当前路径
curl -H "Authorization: Token my-secret-token" \
  "http://localhost:8888/api/fileid/path?id=a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

成功响应：
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "path": "notebooks/example.ipynb"
}
```

### 错误情况

```bash
# 缺少参数（400 Bad Request）
curl -H "Authorization: Token my-secret-token" \
  "http://localhost:8888/api/fileid/id"
# {"status": 400, "message": "'path' parameter was not provided in the request."}

# 文件未索引或不存在（404 Not Found）
curl -H "Authorization: Token my-secret-token" \
  "http://localhost:8888/api/fileid/id?path=nonexistent.txt"
# {"status": 404, "message": "The ID for file, nonexistent.txt, could not be found."}
```

### 使用 cookie 认证（浏览器环境）

在已登录的 JupyterLab 中，浏览器会自动携带 session cookie，无需显式传 token：

```bash
# 先登录获取 cookie
curl -c cookies.txt -X POST \
  "http://localhost:8888/login?next=%2F" \
  --data "password=my-secret-token"

# 使用 cookie 访问 API
curl -b cookies.txt \
  "http://localhost:8888/api/fileid/id?path=notebooks/example.ipynb"
```

## 示例 2：使用 Python requests 库

```python
"""使用 requests 库调用 File ID REST API"""

import requests

class FileIdClient:
    """Jupyter File ID API 客户端封装"""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Token {token}"}

    def get_id(self, path: str) -> dict:
        """通过路径查询文件 ID"""
        resp = requests.get(
            f"{self.base_url}/api/fileid/id",
            params={"path": path},
            headers=self.headers,
        )
        resp.raise_for_status()
        return resp.json()

    def get_path(self, file_id: str) -> dict:
        """通过 ID 查询文件路径"""
        resp = requests.get(
            f"{self.base_url}/api/fileid/path",
            params={"id": file_id},
            headers=self.headers,
        )
        resp.raise_for_status()
        return resp.json()


# --- 使用示例 ---
client = FileIdClient("http://localhost:8888", "my-secret-token")

# 查询文件 ID
try:
    result = client.get_id("notebooks/analysis.ipynb")
    print(f"文件路径: {result['path']}")
    print(f"文件 ID:   {result['id']}")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("文件尚未索引或不存在")
    else:
        raise

# 通过 ID 查询路径（即使文件被移动也能找到）
file_id = result["id"]
try:
    result = client.get_path(file_id)
    print(f"当前路径: {result['path']}")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("文件已被删除")
    else:
        raise
```

## 示例 3：批量查询辅助函数

```python
"""批量查询文件 ID 和路径"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def batch_get_ids(base_url: str, token: str, paths: list[str], max_workers=5) -> dict:
    """批量查询多个路径的文件 ID，返回 {path: id} 字典"""
    headers = {"Authorization": f"Token {token}"}
    results = {}

    def fetch(path):
        try:
            resp = requests.get(
                f"{base_url}/api/fileid/id",
                params={"path": path},
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                return path, data["id"]
            return path, None
        except requests.RequestException:
            return path, None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch, p): p for p in paths}
        for future in as_completed(futures):
            path, file_id = future.result()
            results[path] = file_id

    return results


# --- 使用示例 ---
paths = [
    "notebooks/analysis.ipynb",
    "notebooks/visualization.ipynb",
    "data/sample.csv",
    "README.md",
]
ids = batch_get_ids("http://localhost:8888", "my-secret-token", paths)
for path, file_id in ids.items():
    status = file_id[:8] + "..." if file_id else "NOT FOUND"
    print(f"  {path:40s} -> {status}")
```

## 示例 4：前端 JavaScript（JupyterLab 插件）

```typescript
// JupyterLab 插件中使用 File ID API

/**
 * 查询文件的稳定 ID
 * 在 JupyterLab 中，服务器设置会自动提供 token/baseUrl
 */
async function getFileId(path: string): Promise<string | null> {
  const settings = ServerConnection.makeSettings();
  // settings.baseUrl 例如 "http://localhost:8888/"
  // settings.token 是认证 token

  try {
    const response = await ServerConnection.makeRequest(
      `${settings.baseUrl}api/fileid/id?path=${encodeURIComponent(path)}`,
      { method: "GET" },
      settings
    );

    if (response.ok) {
      const data = await response.json();
      return data.id;
    } else if (response.status === 404) {
      console.warn(`File not indexed: ${path}`);
      return null;
    } else {
      throw new Error(`API error: ${response.status}`);
    }
  } catch (error) {
    console.error("Failed to get file ID:", error);
    return null;
  }
}

/**
 * 通过 ID 查询当前路径（文件移动后仍能找到）
 */
async function getFilePath(fileId: string): Promise<string | null> {
  const settings = ServerConnection.makeSettings();

  try {
    const response = await ServerConnection.makeRequest(
      `${settings.baseUrl}api/fileid/path?id=${fileId}`,
      { method: "GET" },
      settings
    );

    if (response.ok) {
      const data = await response.json();
      return data.path;
    } else if (response.status === 404) {
      console.warn(`File deleted or ID not found: ${fileId}`);
      return null;
    } else {
      throw new Error(`API error: ${response.status}`);
    }
  } catch (error) {
    console.error("Failed to get file path:", error);
    return null;
  }
}

// --- 使用场景：存储稳定引用 ---
async function saveBookmark(path: string) {
  // 存 ID 而非路径，文件移动后引用仍然有效
  const fileId = await getFileId(path);
  if (fileId) {
    localStorage.setItem(`bookmark:${path}`, fileId);
    console.log(`Bookmarked ${path} as ${fileId}`);
  }
}

async function openBookmark(storedPath: string) {
  // 通过存储的 ID 查找当前路径
  const fileId = localStorage.getItem(`bookmark:${storedPath}`);
  if (fileId) {
    const currentPath = await getFilePath(fileId);
    if (currentPath) {
      console.log(`Opening file at current path: ${currentPath}`);
      // 在 JupyterLab 中打开文件
      // await docManager.open(currentPath);
      return currentPath;
    } else {
      console.log("File has been deleted");
    }
  }
  return null;
}
```

## 示例 5：纯 JavaScript（浏览器 fetch）

```javascript
// 在已登录 Jupyter 的浏览器控制台中直接使用
// （浏览器自动携带认证 cookie，无需 token）

async function getFileId(path) {
  const resp = await fetch(`/api/fileid/id?path=${encodeURIComponent(path)}`);
  if (!resp.ok) {
    if (resp.status === 404) return null;
    throw new Error(`HTTP ${resp.status}`);
  }
  const data = await resp.json();
  return data.id;
}

async function getFilePath(id) {
  const resp = await fetch(`/api/fileid/path?id=${id}`);
  if (!resp.ok) {
    if (resp.status === 404) return null;
    throw new Error(`HTTP ${resp.status}`);
  }
  const data = await resp.json();
  return data.path;
}

// 测试
getFileId("notebooks/example.ipynb").then(id => {
  console.log("File ID:", id);
  return getFilePath(id);
}).then(path => {
  console.log("Current path:", path);
});
```

---

**下一步阅读：**
- [自定义管理器示例](03-custom-manager.md) — 创建自己的 File ID 管理器
- [编程接口基础使用](01-basic-usage.md) — 直接使用 Python API
- [REST API 端点](../concepts/06-http-api.md) — API 完整文档
