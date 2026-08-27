---
type: Concept
title: 5分钟快速上手
description: 安装 jupyter_server_terminals、启用扩展、验证终端功能、基本配置入门
tags: [jupyter, terminals, getting-started, installation, configuration]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T06:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T07:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jst-source
    resource: /references/jupyter-server-terminals-source.md
---

# 5分钟快速上手

## 安装

jupyter_server_terminals 要求 Python ≥ 3.8 且 Jupyter Server ≥ 2.0.0。

通过 pip 安装：

```bash
pip install jupyter_server_terminals
```

Windows 平台会自动安装 `pywinpty` 作为 PTY 后端；Linux/macOS 使用系统自带的 PTY。

通常你不需要单独安装它——安装 JupyterLab (`pip install jupyterlab`) 或 Notebook 7+ 时，jupyter_server_terminals 会作为依赖自动安装。

## 验证安装

安装后启动 Jupyter Server：

```bash
jupyter server
```

在日志中应该能看到终端扩展被加载。也可以通过 API 验证：

```bash
# 获取终端列表（应该返回空数组 []）
curl -s http://localhost:8888/api/terminals
```

如果返回 `[]` 且无认证错误（带 token 的话需加上），说明终端扩展已正常运行。

## 快速体验

### 通过 JupyterLab

1. 启动 JupyterLab：`jupyter lab`
2. 在启动器中点击 "Terminal" 卡片，或菜单 File → New → Terminal
3. 一个终端标签页打开，可以直接输入 Shell 命令

### 通过 REST API

使用 API 直接创建和操作终端：

```bash
# 1. 创建新终端
curl -X POST http://localhost:8888/api/terminals
# 返回: {"name": "1", "last_activity": "2026-08-22T06:00:00.000Z"}

# 2. 列出所有终端
curl http://localhost:8888/api/terminals
# 返回: [{"name": "1", "last_activity": "..."}]

# 3. 查询特定终端
curl http://localhost:8888/api/terminals/1
# 返回: {"name": "1", "last_activity": "..."}

# 4. 删除终端
curl -X DELETE http://localhost:8888/api/terminals/1
# 返回: 204 No Content
```

### 通过 WebSocket 连接终端

创建终端后，通过 WebSocket 连接进行实时交互：

```javascript
// 浏览器 JavaScript 示例
const ws = new WebSocket('ws://localhost:8888/terminals/websocket/1');

ws.onmessage = function(event) {
    const msg = JSON.parse(event.data);
    if (msg[0] === 'stdout') {
        console.log('终端输出:', msg[1]);
    }
};

ws.onopen = function() {
    // 发送命令（stdin 类型）
    ws.send(JSON.stringify(['stdin', 'echo "Hello Terminal"\r\n']));
};
```

WebSocket 消息是 JSON 数组格式，第一个元素是消息类型（`stdin`/`stdout` 等），第二个是数据内容。

## 基本配置

jupyter_server_terminals 的配置通过 Jupyter Server 的配置系统（`jupyter_server_config.py`）进行。

### 禁用终端

```python
c.ServerApp.terminals_enabled = False
```

禁用后，`terminals_available` 设置为 `False`，API 返回 404 或空列表，WebSocket 连接被拒绝。

### 配置闲置终端自动清理

```python
# 闲置超过 10 分钟（600秒）的终端自动关闭
c.TerminalManager.cull_inactive_timeout = 600

# 每 2 分钟（120秒）检查一次
c.TerminalManager.cull_interval = 120
```

默认值：`cull_inactive_timeout = 0`（不自动清理），`cull_interval = 300`（5分钟检查间隔）。

### 自定义 Shell 命令

```python
c.ServerApp.terminado_settings = {
    'shell_command': ['/bin/zsh', '-l']
}
```

如果不配置，扩展会使用合理默认值：
- Windows：`powershell.exe`
- Linux/macOS：使用 `$SHELL` 环境变量，否则使用 `sh`
- 非 TTY 环境（如 JupyterHub 派生）且无自定义 Shell：自动使用 login shell（追加 `-l` 参数）

## 终端可用状态检测

终端功能是否真正可用由三态门控决定：

```python
# 检查配置开关
serverapp.terminals_enabled  # True/False

# 检查最终可用性（考虑 terminado 是否可用、初始化是否成功）
serverapp.web_app.settings['terminals_available']  # True/False
```

只有当 `terminals_enabled = True`、terminado 已安装、且扩展初始化成功三者都满足时，`terminals_available` 才为 `True`。

## 相关概念

- [jupyter_server_terminals 简介](00-introduction.md)
- [TerminalsExtensionApp 扩展应用](02-extension-app.md)
- [TerminalManager 终端管理器](03-terminal-manager.md)
- [REST API 处理器](04-rest-api.md)
- [基础终端操作示例](../examples/basic-operations.md)

[^jst-source]: jupyter_server_terminals 源码信源，见 [jupyter-server-terminals-source.md](../references/jupyter-server-terminals-source.md)。
