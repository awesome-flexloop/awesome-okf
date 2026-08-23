---
type: Example
title: "REST API 使用"
description: "通过 HTTP API 与 Jupyverse 交互，包括文件操作、内核管理、代码执行等常用场景的 curl 示例。"
tags: [api, rest, curl, contents, kernels, execution]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T06:55:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: contents
    resource: /concepts/06-contents-service.md
    title: Contents 文件服务
  - id: kernels
    resource: /concepts/07-kernel-management.md
    title: 内核管理
---

# REST API 使用

本示例演示通过 HTTP API 与 Jupyverse 交互的常见操作。以下示例假设 Jupyverse 运行在 `http://127.0.0.1:8000`，使用 NoAuth 模式。

> 如需认证，在请求中添加查询参数 `?token=your-token` 或请求头 `Authorization: Token your-token`。

## 文件操作

### 列出根目录

```bash
curl http://127.0.0.1:8000/api/contents
```

### 创建 Notebook

```bash
curl -X POST "http://127.0.0.1:8000/api/contents" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "notebook",
    "path": "/my-notebook.ipynb"
  }'
```

### 读取文件内容

```bash
curl "http://127.0.0.1:8000/api/contents/my-notebook.ipynb?content=1"
```

### 保存文件

```bash
curl -X PUT "http://127.0.0.1:8000/api/contents/my-notebook.ipynb" \
  -H "Content-Type: application/json" \
  -d '{
    "content": {
      "cells": [],
      "metadata": {"kernelspec": {"display_name": "Python 3", "name": "python3"}},
      "nbformat": 4,
      "nbformat_minor": 5
    },
    "format": "json",
    "path": "/my-notebook.ipynb",
    "type": "notebook"
  }'
```

### 创建文本文件

```bash
curl -X PUT "http://127.0.0.1:8000/api/contents/hello.py" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "print(\"Hello, Jupyverse!\")",
    "format": "text",
    "path": "/hello.py",
    "type": "file"
  }'
```

### 删除文件

```bash
curl -X DELETE "http://127.0.0.1:8000/api/contents/my-notebook.ipynb"
```

### 创建检查点

```bash
curl -X POST "http://127.0.0.1:8000/api/contents/hello.py/checkpoints"
```

## 内核管理

### 列出可用内核规格

```bash
curl http://127.0.0.1:8000/api/kernelspecs
```

### 列出运行中内核

```bash
curl http://127.0.0.1:8000/api/kernels
```

### 启动新内核

内核通过创建会话来启动：

```bash
curl -X POST "http://127.0.0.1:8000/api/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/hello.py",
    "name": "Python 3",
    "type": "notebook",
    "kernel": {"name": "python3"}
  }'
```

返回包含 `kernel.id` 和 `session.id` 的 JSON，记录下 `kernel.id` 用于后续操作。

### 获取内核信息

```bash
curl http://127.0.0.1:8000/api/kernels/{kernel_id}
```

### 执行代码

```bash
curl -X POST "http://127.0.0.1:8000/api/kernels/{kernel_id}/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "x = 1 + 1\nprint(f\"x = {x}\")",
    "silent": false
  }'
```

### 中断内核

```bash
curl -X POST "http://127.0.0.1:8000/api/kernels/{kernel_id}/interrupt"
```

### 重启内核

```bash
curl -X POST "http://127.0.0.1:8000/api/kernels/{kernel_id}/restart"
```

### 关闭内核

```bash
curl -X DELETE "http://127.0.0.1:8000/api/kernels/{kernel_id}"
```

### 删除会话

```bash
curl -X DELETE "http://127.0.0.1:8000/api/sessions/{session_id}"
```

## 服务器状态

```bash
curl http://127.0.0.1:8000/api/status
```

## 会话管理

```bash
# 列出所有会话
curl http://127.0.0.1:8000/api/sessions

# 重命名会话
curl -X PATCH "http://127.0.0.1:8000/api/sessions/{session_id}" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Renamed Session", "path": "/renamed.ipynb"}'
```

## Python 客户端示例

```python
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# 启动内核（通过创建会话）
session_resp = requests.post(f"{BASE_URL}/api/sessions", json={
    "path": "/test.ipynb",
    "name": "Python 3",
    "type": "notebook",
    "kernel": {"name": "python3"}
})
session = session_resp.json()
kernel_id = session["kernel"]["id"]
print(f"Kernel started: {kernel_id}")

# 创建并执行一个简单文件
requests.put(f"{BASE_URL}/api/contents/test.py", json={
    "content": "result = 2 ** 10\nprint(f'2^10 = {result}')",
    "format": "text",
    "path": "/test.py",
    "type": "file"
})

# 执行代码
execute_resp = requests.post(
    f"{BASE_URL}/api/kernels/{kernel_id}/execute",
    json={"code": "print(1 + 1)", "silent": False}
)
print(f"Execute response: {execute_resp.status_code}")

# 关闭内核
requests.delete(f"{BASE_URL}/api/kernels/{kernel_id}")
print("Kernel stopped")
```
