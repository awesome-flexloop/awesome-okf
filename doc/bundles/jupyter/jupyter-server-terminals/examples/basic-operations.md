---
type: Example
title: 基础终端操作
description: 通过 REST API 完成终端的创建、列表查询、信息获取和删除的完整 CRUD 示例
tags: [jupyter, terminals, REST, API, CRUD, example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T06:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T07:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jst-source
    resource: /references/jupyter-server-terminals-source.md
---

# 基础终端操作

本示例演示如何通过 REST API 对 Jupyter 终端执行完整的 CRUD（创建、读取、列表、删除）操作。

## 前置条件

- Jupyter Server 正在运行（默认端口 8888）
- 已安装并启用 jupyter_server_terminals
- 获取了访问 token（从启动日志中查找，或通过 `jupyter server list` 查看）

为简化示例，以下代码中假设 token 已通过环境变量 `JUPYTER_TOKEN` 设置，或通过 `~/.jupyter/jupyter_server_config.py` 禁用了认证（仅开发环境）。

## 使用 Python requests 操作终端

```python
import requests
import json

BASE_URL = "http://localhost:8888"
# 如果需要认证，添加 token
# TOKEN = "your-token-here"
# HEADERS = {"Authorization": f"token {TOKEN}"}
HEADERS = {}

# ============ 1. 列出所有终端 ============
print("=== 列出终端 ===")
resp = requests.get(f"{BASE_URL}/api/terminals", headers=HEADERS)
terminals = resp.json()
print(f"当前终端数: {len(terminals)}")
print(json.dumps(terminals, indent=2))
# 初始状态: []

# ============ 2. 创建新终端 ============
print("\n=== 创建终端 ===")
resp = requests.post(f"{BASE_URL}/api/terminals", headers=HEADERS)
terminal = resp.json()
term_name = terminal["name"]
print(f"终端名称: {term_name}")
print(json.dumps(terminal, indent=2))
# 返回: {"name": "1", "last_activity": "2026-08-22T06:00:00.000000Z"}

# ============ 3. 再次列出终端 ============
print("\n=== 再次列出终端 ===")
resp = requests.get(f"{BASE_URL}/api/terminals", headers=HEADERS)
terminals = resp.json()
print(f"当前终端数: {len(terminals)}")
# 此时应该有 1 个终端

# ============ 4. 获取特定终端信息 ============
print(f"\n=== 获取终端 {term_name} 信息 ===")
resp = requests.get(f"{BASE_URL}/api/terminals/{term_name}", headers=HEADERS)
terminal_info = resp.json()
print(json.dumps(terminal_info, indent=2))
# 返回: {"name": "1", "last_activity": "..."}

# ============ 5. 删除终端 ============
print(f"\n=== 删除终端 {term_name} ===")
resp = requests.delete(f"{BASE_URL}/api/terminals/{term_name}", headers=HEADERS)
print(f"删除状态码: {resp.status_code}")  # 204 表示成功
assert resp.status_code == 204

# ============ 6. 验证删除 ============
print("\n=== 验证删除 ===")
resp = requests.get(f"{BASE_URL}/api/terminals", headers=HEADERS)
terminals = resp.json()
print(f"删除后终端数: {len(terminals)}")
# 应该回到 0
```

## 使用 curl 命令行操作

```bash
# 设置 Jupyter Server 地址和 token
SERVER="http://localhost:8888"
TOKEN="your-token-here"
AUTH_HEADER="Authorization: token ${TOKEN}"

# 1. 列出终端
curl -s -H "$AUTH_HEADER" $SERVER/api/terminals

# 2. 创建终端
curl -s -X POST -H "$AUTH_HEADER" $SERVER/api/terminals
# 返回: {"name": "1", "last_activity": "..."}

# 3. 获取终端信息
curl -s -H "$AUTH_HEADER" $SERVER/api/terminals/1

# 4. 删除终端
curl -s -X DELETE -H "$AUTH_HEADER" -w "%{http_code}" $SERVER/api/terminals/1
# 返回 204
```

## 使用 JavaScript fetch 操作终端

```javascript
const baseUrl = 'http://localhost:8888';
const token = 'your-token-here';
const headers = {
    'Authorization': `token ${token}`,
    'Content-Type': 'application/json'
};

// 创建终端
async function createTerminal() {
    const resp = await fetch(`${baseUrl}/api/terminals`, {
        method: 'POST',
        headers: headers
    });
    return await resp.json();
}

// 列出终端
async function listTerminals() {
    const resp = await fetch(`${baseUrl}/api/terminals`, { headers });
    return await resp.json();
}

// 获取终端
async function getTerminal(name) {
    const resp = await fetch(`${baseUrl}/api/terminals/${name}`, { headers });
    return await resp.json();
}

// 删除终端
async function deleteTerminal(name) {
    const resp = await fetch(`${baseUrl}/api/terminals/${name}`, {
        method: 'DELETE',
        headers: headers
    });
    return resp.status === 204;
}

// 使用示例
(async () => {
    const terminal = await createTerminal();
    console.log('已创建:', terminal.name);

    const list = await listTerminals();
    console.log('终端列表:', list);

    await deleteTerminal(terminal.name);
    console.log('已删除:', terminal.name);
})();
```

## HTTP 状态码说明

| 状态码 | 含义 | 出现场景 |
|--------|------|---------|
| 200 | 请求成功 | GET 列表/查询、POST 创建 |
| 204 | 删除成功 | DELETE 终端 |
| 403 | 未授权 | 未登录或无 permissions |
| 404 | 终端不存在 | 查询/删除不存在的终端名 |

## 终端命名规则

- 终端名称是从 `"1"` 开始递增的数字字符串
- 第一个终端为 `"1"`，第二个为 `"2"`，以此类推
- 删除终端后，已使用过的名称不会立即复用
- 名称由 terminado 的 `NamedTermManager` 自动分配，客户端无法自定义名称

## 注意事项

1. **先创建后连接**：REST API 只负责终端的生命周期管理，实际的终端 I/O 需要通过 WebSocket 连接（参见 [WebSocket 实时通信示例](/examples/websocket-interaction.md)）
2. **认证**：所有 API 请求都需要有效认证（token 或 cookie），测试环境可用 `--ServerApp.token=''` 禁用认证（仅限本地开发）
3. **幂等性**：GET 和 DELETE 操作是幂等的；POST 创建终端每次调用都会创建新终端
4. **异步删除**：DELETE 返回 204 后，终端进程可能还在清理中，立即重建同名终端可能需要短暂等待

## 相关概念

- [REST API 处理器](/concepts/04-rest-api.md)
- [TerminalManager 终端管理器](/concepts/03-terminal-manager.md)
- [WebSocket 实时通信示例](/examples/websocket-interaction.md)
- [配置自动清理与指定工作目录](/examples/culler-and-cwd.md)
- [jupyter_server_terminals 源码信源登记](/references/jupyter-server-terminals-source.md)

[^jst-source]: jupyter_server_terminals 源码信源，见 [jupyter-server-terminals-source.md](/references/jupyter-server-terminals-source.md)。
