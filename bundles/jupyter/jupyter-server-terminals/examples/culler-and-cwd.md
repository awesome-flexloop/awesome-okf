---
type: Example
title: 配置自动清理与指定工作目录
description: 配置闲置终端自动清理（Culling）、创建终端时指定初始工作目录的实用示例
tags: [jupyter, terminals, culler, cwd, configuration, example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T06:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T07:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jst-source
    resource: /references/jupyter-server-terminals-source.md
---

# 配置自动清理与指定工作目录

本示例包含两个实用场景：配置闲置终端自动清理（Culling）和创建终端时指定初始工作目录（cwd）。

## 场景一：配置闲置终端自动清理

默认情况下，终端不会自动关闭——即使用户关闭浏览器标签页，终端进程仍在后台运行。长时间运行的空闲终端会占用系统资源。通过 Culling 配置可以自动回收闲置终端。

### 配置方法

在 Jupyter Server 配置文件（`jupyter_server_config.py`）中：

```python
# 闲置 10 分钟（600秒）后自动关闭终端
c.TerminalManager.cull_inactive_timeout = 600

# 每 2 分钟（120秒）检查一次
c.TerminalManager.cull_interval = 120
```

或者通过命令行参数启动：

```bash
jupyter server --TerminalManager.cull_inactive_timeout=600 \
               --TerminalManager.cull_interval=120
```

### 配置说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `cull_inactive_timeout` | 0（禁用） | 终端闲置超过此秒数后被回收，0 或负值禁用清理 |
| `cull_interval` | 300（5分钟） | 检查闲置终端的时间间隔（秒） |

### 验证 Culling 工作

```python
import asyncio
import json
import time
import requests

BASE_URL = "http://localhost:8888"

# 1. 创建终端
resp = requests.post(f"{BASE_URL}/api/terminals")
term = resp.json()
term_name = term["name"]
print(f"创建终端: {term_name}")

# 2. 连接 WebSocket（保持活动状态会刷新 last_activity）
# 如果不连接或不发送消息，终端会因闲置被清理

# 3. 等待超过 cull_inactive_timeout 时间
print(f"等待终端被 cull (配置的 timeout 秒数)...")

# 4. 轮询检查终端是否被清理
culled = False
for i in range(20):  # 最多等待 20 个间隔
    time.sleep(cull_interval + 1)
    try:
        resp = requests.get(f"{BASE_URL}/api/terminals/{term_name}")
        if resp.status_code == 404:
            culled = True
            print(f"终端 {term_name} 已在第 {i+1} 次检查时被清理")
            break
        else:
            print(f"第 {i+1} 次检查: 终端仍存活")
    except Exception as e:
        print(f"检查出错: {e}")

if not culled:
    print("终端未被清理（可能有活动保持其存活）")
```

### Culling 机制要点

1. **双层活动追踪**：
   - WebSocket 消息收发时更新 `last_activity`
   - PTY 数据读取时通过 `pre_pty_read_hook` 更新 `last_activity`

2. **安全遍历**：culler 遍历终端列表的副本（`list(self.terminals)`），避免迭代过程中终端被删除导致的异常

3. **容错处理**：单个终端清理失败不影响其他终端的检查

4. **仅首次创建时启动**：culler 在第一个终端创建时初始化并启动 PeriodicCallback，不会重复启动

### 推荐配置

不同使用场景的推荐配置：

| 场景 | cull_inactive_timeout | cull_interval |
|------|----------------------|---------------|
| 个人开发机 | 0（禁用）或 3600（1小时） | 300（5分钟） |
| 共享 JupyterHub | 600（10分钟） | 120（2分钟） |
| CI/测试环境 | 60（1分钟） | 30（30秒） |
| 教学环境 | 1800（30分钟） | 300（5分钟） |

---

## 场景二：创建终端时指定工作目录

创建终端时可以通过 `cwd` 参数指定初始工作目录。

### 使用绝对路径

```bash
curl -X POST http://localhost:8888/api/terminals \
  -H "Content-Type: application/json" \
  -d '{"cwd": "/home/user/projects/myproject"}'
```

```python
import requests

resp = requests.post(
    "http://localhost:8888/api/terminals",
    json={"cwd": "/home/user/projects/myproject"}
)
terminal = resp.json()
print(f"终端在 {terminal['name']} 创建，工作目录已设置")
```

### 使用相对路径

相对路径会相对于 Jupyter Server 的根目录（`root_dir`）解析：

```bash
# 如果 Jupyter Server 以 /home/user 启动
# 相对路径 "projects/myproject" 会被解析为 /home/user/projects/myproject
curl -X POST http://localhost:8888/api/terminals \
  -H "Content-Type: application/json" \
  -d '{"cwd": "projects/myproject"}'
```

### 路径解析逻辑

cwd 参数的三级解析策略：

```
cwd 参数
  │
  ├─ 作为绝对路径，路径存在? → 使用该绝对路径
  │
  ├─ 作为相对路径，相对于 server_root_dir 存在?
  │   └─ 使用 server_root_dir / cwd 的绝对路径
  │
  └─ 路径都不存在? → 静默删除 cwd 参数，使用默认工作目录
```

这种"优雅降级"设计确保无效路径不会导致终端创建失败。

### 验证 cwd 生效

```python
import asyncio
import json
import requests
import websockets

BASE_URL = "http://localhost:8888"
WS_URL = "ws://localhost:8888"
TOKEN = ""  # 填入你的 token

# 1. 在指定目录创建终端
target_dir = "/tmp"  # 或其他存在的目录
resp = requests.post(
    f"{BASE_URL}/api/terminals",
    json={"cwd": target_dir}
)
term_name = resp.json()["name"]
print(f"终端 {term_name} 已创建")

# 2. 等待终端就绪
await asyncio.sleep(1)

# 3. 通过 WebSocket 执行 pwd 验证工作目录
uri = f"{WS_URL}/terminals/websocket/{term_name}"
if TOKEN:
    uri += f"?token={TOKEN}"

async with websockets.connect(uri) as ws:
    # 发送 pwd 命令
    await ws.send(json.dumps(["stdin", "pwd\r\n"]))

    # 收集输出
    output = ""
    try:
        while True:
            msg = await asyncio.wait_for(ws.recv(), timeout=3.0)
            data = json.loads(msg)
            if data[0] == "stdout":
                output += data[1]
    except asyncio.TimeoutError:
        pass

    # 验证输出包含目标目录名
    import os
    assert os.path.basename(target_dir) in output or target_dir in output
    print(f"工作目录验证成功！输出包含: {target_dir}")

# 4. 清理
requests.delete(f"{BASE_URL}/api/terminals/{term_name}")
```

### 不存在路径的处理

如果指定的 cwd 不存在，终端仍会成功创建，但使用默认工作目录：

```python
resp = requests.post(
    "http://localhost:8888/api/terminals",
    json={"cwd": "/path/that/does/not/exist"}
)
# 返回 200，终端创建成功，但 cwd 参数被忽略
# 服务端日志会记录 debug 信息:
# "Failed to find requested terminal cwd: /path/that/does/not/exist"
```

### Windows 路径注意事项

Windows 上路径分隔符为反斜杠，JSON 中需要转义：

```python
# Windows 上使用正斜杠或双反斜杠
requests.post(
    "http://localhost:8888/api/terminals",
    json={"cwd": "C:/Users/YourName/projects"}  # 正斜杠也能被 Path 识别
)
```

## 完整配置示例

一个包含常用终端配置的 `jupyter_server_config.py`：

```python
c = get_config()  # noqa

# 启用终端（默认启用）
c.ServerApp.terminals_enabled = True

# 自动清理闲置终端
c.TerminalManager.cull_inactive_timeout = 1800  # 30分钟
c.TerminalManager.cull_interval = 300           # 5分钟检查一次

# 自定义 Shell（可选）
c.ServerApp.terminado_settings = {
    "shell_command": ["/bin/bash", "-l"]  # 使用 login bash
}
```

## 相关概念

- [TerminalManager 终端管理器](/concepts/03-terminal-manager.md)
- [Shell 配置与平台差异](/concepts/06-shell-configuration.md)
- [REST API 处理器](/concepts/04-rest-api.md)
- [基础终端操作](/examples/basic-operations.md)
- [WebSocket 实时通信](/examples/websocket-interaction.md)
- [jupyter_server_terminals 源码信源登记](/references/jupyter-server-terminals-source.md)

[^jst-source]: jupyter_server_terminals 源码信源，见 [jupyter-server-terminals-source.md](/references/jupyter-server-terminals-source.md)。
