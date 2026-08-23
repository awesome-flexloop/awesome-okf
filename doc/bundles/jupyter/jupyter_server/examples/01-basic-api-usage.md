---
type: Example
title: "基础 API 使用"
description: "通过 REST API 管理 Notebook、内核和会话的完整示例，包括 Python requests 和 curl 两种方式"
tags: [api, rest, curl, python-requests, kernels, contents, sessions]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T15:10:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: contents
    resource: /references/contents-source.md
    title: 内容管理源码信源
  - id: kernels
    resource: /references/kernels-source.md
    title: 内核管理源码信源
---

# 基础 API 使用示例

本文展示如何通过 Jupyter Server REST API 执行常见操作。

## 前置条件

1. Jupyter Server 已启动并运行：
```bash
jupyter server --ServerApp.token=mytoken --port=8888 --no-browser
```

2. 记录服务器地址和 Token：`http://localhost:8888/?token=mytoken`

## 方式一：curl 命令行

### 1. 获取服务器信息

```bash
# API 根路径（列出可用 API 版本）
curl http://localhost:8888/api?token=mytoken

# 获取当前用户信息
curl http://localhost:8888/api/me?token=mytoken
```

### 2. 文件管理

```bash
# 列出根目录内容
curl "http://localhost:8888/api/contents?token=mytoken"

# 创建新 Notebook
curl -X PUT "http://localhost:8888/api/contents/my-notebook.ipynb?token=mytoken" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "notebook",
    "content": {
      "cells": [
        {
          "cell_type": "code",
          "execution_count": null,
          "metadata": {},
          "outputs": [],
          "source": ["print(\"Hello, Jupyter!\")"]
        }
      ],
      "metadata": {
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"}
      },
      "nbformat": 4,
      "nbformat_minor": 5
    }
  }'

# 读取 Notebook 内容
curl "http://localhost:8888/api/contents/my-notebook.ipynb?token=mytoken"

# 创建文本文件
curl -X PUT "http://localhost:8888/api/contents/hello.py?token=mytoken" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "file",
    "format": "text",
    "content": "print(\"Hello from Python!\")\n"
  }'

# 重命名文件
curl -X PATCH "http://localhost:8888/api/contents/hello.py?token=mytoken" \
  -H "Content-Type: application/json" \
  -d '{"path": "greetings.py"}'

# 创建目录
curl -X PUT "http://localhost:8888/api/contents/data?token=mytoken" \
  -H "Content-Type: application/json" \
  -d '{"type": "directory"}'

# 删除文件
curl -X DELETE "http://localhost:8888/api/contents/greetings.py?token=mytoken"
```

### 3. 内核管理

```bash
# 列出运行中的内核
curl "http://localhost:8888/api/kernels?token=mytoken"

# 启动新内核（Python 3）
curl -X POST "http://localhost:8888/api/kernels?token=mytoken" \
  -H "Content-Type: application/json" \
  -d '{"name": "python3", "path": "/"}'
# 返回: {"id": "kernel-id-xxx", "name": "python3", ...}

# 查看可用 kernelspecs
curl "http://localhost:8888/api/kernelspecs?token=mytoken"

# 重启内核
curl -X POST "http://localhost:8888/api/kernels/<kernel_id>/restart?token=mytoken"

# 中断内核（Ctrl+C）
curl -X POST "http://localhost:8888/api/kernels/<kernel_id>/interrupt?token=mytoken"

# 关闭内核
curl -X DELETE "http://localhost:8888/api/kernels/<kernel_id>?token=mytoken"
```

### 4. 会话管理

```bash
# 创建会话（关联 Notebook 和内核）
curl -X POST "http://localhost:8888/api/sessions?token=mytoken" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "my-notebook.ipynb",
    "type": "notebook",
    "kernel": {"name": "python3"}
  }'

# 列出所有会话
curl "http://localhost:8888/api/sessions?token=mytoken"

# 删除会话（关闭关联内核）
curl -X DELETE "http://localhost:8888/api/sessions/<session_id>?token=mytoken"
```

## 方式二：Python requests

```python
import requests
import json

BASE_URL = "http://localhost:8888"
TOKEN = "mytoken"

def api_url(path):
    return f"{BASE_URL}{path}"

headers = {"Authorization": f"token {TOKEN}"}

# 1. 获取服务器状态
resp = requests.get(api_url("/api/status"), headers=headers)
print("Server status:", resp.json())

# 2. 列出根目录
resp = requests.get(api_url("/api/contents"), headers=headers)
contents = resp.json()
print(f"Root directory has {len(contents['content'])} items")
for item in contents['content']:
    print(f"  {item['type']}: {item['name']}")

# 3. 创建并启动一个 Notebook + 内核
# 3a. 创建空 Notebook
nb_content = {
    "cells": [],
    "metadata": {
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"}
    },
    "nbformat": 4,
    "nbformat_minor": 5
}
resp = requests.put(
    api_url("/api/contents/test.ipynb"),
    headers={**headers, "Content-Type": "application/json"},
    data=json.dumps({"type": "notebook", "content": nb_content})
)
print("Created notebook:", resp.status_code)

# 3b. 创建会话（自动启动内核）
resp = requests.post(
    api_url("/api/sessions"),
    headers={**headers, "Content-Type": "application/json"},
    data=json.dumps({
        "path": "test.ipynb",
        "type": "notebook",
        "kernel": {"name": "python3"}
    })
)
session = resp.json()
kernel_id = session['kernel']['id']
session_id = session['id']
print(f"Started session {session_id} with kernel {kernel_id}")

# 4. 列出所有运行中的内核
resp = requests.get(api_url("/api/kernels"), headers=headers)
print(f"Running kernels: {len(resp.json())}")

# 5. 清理：删除会话（关闭内核）
resp = requests.delete(api_url(f"/api/sessions/{session_id}"), headers=headers)
print("Deleted session:", resp.status_code)

# 删除测试 Notebook
resp = requests.delete(api_url("/api/contents/test.ipynb"), headers=headers)
print("Deleted notebook:", resp.status_code)
```

## 方式三：jupyter_client 直接连接内核

```python
from jupyter_client import BlockingKernelClient

# 从 connection 文件连接到已运行的内核
# connection 文件位于 jupyter_runtime_dir/kernel-<id>.json
client = BlockingKernelClient()
client.load_connection_file("/path/to/kernel-<id>.json")
client.start_channels()

# 等待就绪
client.wait_for_ready()

# 发送代码执行请求
msg_id = client.execute("print('Hello from API client!')")

# 接收回复
while True:
    msg = client.get_iopub_msg(timeout=10)
    if msg['parent_header'].get('msg_id') == msg_id:
        if msg['msg_type'] == 'stream':
            print("Output:", msg['content']['text'])
        elif msg['msg_type'] == 'status' and msg['content']['execution_state'] == 'idle':
            break

client.stop_channels()
```

## 常见错误处理

```python
import requests

def safe_request(method, url, **kwargs):
    try:
        resp = requests.request(method, url, timeout=30, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 401:
            print("Authentication failed: check your token")
        elif resp.status_code == 403:
            print("Forbidden: check permissions and CORS")
        elif resp.status_code == 404:
            print("Not found:", url)
        else:
            print(f"HTTP {resp.status_code}:", resp.text)
        raise
    except requests.exceptions.ConnectionError:
        print("Cannot connect to server. Is it running?")
        raise
```

## 参考

- [内容管理服务](../concepts/07-contents-service.md) — Contents API 完整参考
- [内核管理](../concepts/08-kernel-management.md) — Kernel API 完整参考
- [会话管理](../concepts/09-sessions-service.md) — Session API 完整参考
