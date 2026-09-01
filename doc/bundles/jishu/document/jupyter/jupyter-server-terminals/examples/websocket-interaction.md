---
type: Example
title: WebSocket 实时通信
description: 通过 WebSocket 连接终端、发送命令、接收输出的完整实时交互示例
tags: [jupyter, terminals, websocket, realtime, I/O, example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T06:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T07:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jst-source
    resource: /references/jupyter-server-terminals-source.md
---

# WebSocket 实时通信

本示例演示如何通过 WebSocket 与 Jupyter 终端进行实时交互——连接终端、发送命令、接收输出、处理消息协议。

## 消息协议

WebSocket 使用 JSON 数组格式的简单消息协议：

| 方向 | 格式 | 说明 |
|------|------|------|
| 客户端→服务端 | `["stdin", "data"]` | 向终端发送输入（按键/命令） |
| 服务端→客户端 | `["stdout", "data"]` | 终端输出数据 |

发送命令时，每条命令末尾需要加 `\r\n`（回车换行）来执行。

## 前置条件

- 已通过 REST API 创建了一个终端（参见 [基础终端操作](basic-operations.md)）
- 知道目标终端的 `name`（如 `"1"`）
- WebSocket 连接使用 `ws://` 或 `wss://` 协议

## 浏览器 JavaScript 示例

```javascript
class JupyterTerminal {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.token = token;
        this.ws = null;
        this.onOutput = null;  // 输出回调
    }

    async connect(termName) {
        // 构建 WebSocket URL（注意路径为 /terminals/websocket/{name}）
        const wsUrl = `${this.baseUrl.replace('http', 'ws')}/terminals/websocket/${termName}`;

        // 添加 token 到 URL 参数（WebSocket 不支持自定义 headers）
        const url = new URL(wsUrl);
        if (this.token) {
            url.searchParams.set('token', this.token);
        }

        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(url.toString());

            this.ws.onopen = () => {
                console.log('WebSocket 连接已建立');
                resolve();
            };

            this.ws.onmessage = (event) => {
                const msg = JSON.parse(event.data);
                const [type, data] = msg;

                if (type === 'stdout') {
                    // 终端输出
                    if (this.onOutput) {
                        this.onOutput(data);
                    }
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket 错误:', error);
                reject(error);
            };

            this.ws.onclose = () => {
                console.log('WebSocket 连接已关闭');
            };
        });
    }

    send(data) {
        // 向终端发送输入
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(['stdin', data]));
        }
    }

    executeCommand(command) {
        // 执行命令（追加回车换行）
        this.send(command + '\r\n');
    }

    close() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// 使用示例
(async () => {
    const term = new JupyterTerminal('http://localhost:8888', 'your-token-here');

    // 收集所有输出
    let output = '';
    term.onOutput = (data) => {
        output += data;
        // 在页面上显示输出
        console.log('输出:', data);
    };

    try {
        // 先创建终端
        const resp = await fetch('http://localhost:8888/api/terminals', {
            method: 'POST',
            headers: { 'Authorization': 'token your-token-here' }
        });
        const { name } = await resp.json();
        console.log('已创建终端:', name);

        // 连接 WebSocket（终端创建后可能需要短暂等待就绪）
        await new Promise(r => setTimeout(r, 500));
        await term.connect(name);

        // 发送命令
        term.executeCommand('echo "Hello from Jupyter Terminal!"');
        term.executeCommand('pwd');
        term.executeCommand('ls -la');

        // 等待输出收集
        await new Promise(r => setTimeout(r, 2000));

        console.log('\n=== 全部输出 ===');
        console.log(output);

    } finally {
        term.close();
    }
})();
```

## Python websockets 库示例

```python
import asyncio
import json
import websockets

async def terminal_interaction():
    base_url = "ws://localhost:8888"
    token = "your-token-here"
    term_name = "1"  # 先通过 REST API 创建

    uri = f"{base_url}/terminals/websocket/{term_name}?token={token}"

    async with websockets.connect(uri) as ws:
        print("WebSocket 已连接")

        # 接收消息的任务
        async def receive():
            output = ""
            try:
                while True:
                    message = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    msg = json.loads(message)
                    if msg[0] == "stdout":
                        output += msg[1]
                        print(msg[1], end="")
            except asyncio.TimeoutError:
                pass
            return output

        # 发送命令
        async def send_command(cmd):
            await ws.send(json.dumps(["stdin", cmd + "\r\n"]))

        # 执行命令并收集输出
        await send_command("echo 'Hello from Python!'")
        await send_command("whoami")
        await send_command("pwd")

        # 等待输出
        output = await receive()
        print("\n=== 完成 ===")

asyncio.run(terminal_interaction())
```

## Python tornado 客户端示例

测试代码中使用的 `jp_ws_fetch` 模式（pytest-jupyter 插件）：

```python
import json
import asyncio

async def test_terminal_websocket(jp_fetch, jp_ws_fetch):
    # 1. 创建终端
    resp = await jp_fetch("api", "terminals", method="POST", allow_nonstandard_methods=True)
    term_name = json.loads(resp.body.decode())["name"]

    # 2. 等待终端就绪（轮询重试）
    while True:
        try:
            ws = await jp_ws_fetch("terminals", "websocket", term_name)
            break
        except Exception as e:
            if e.code != 404:
                raise
            await asyncio.sleep(1)

    # 3. 发送命令
    ws.write_message(json.dumps(["stdin", "pwd\r\n"]))

    # 4. 读取输出
    output = ""
    while True:
        try:
            msg = await asyncio.wait_for(ws.read_message(), timeout=5.0)
            data = json.loads(msg)
            if data[0] == "stdout":
                output += data[1]
        except asyncio.TimeoutError:
            break

    # 5. 验证输出包含当前目录
    assert "home" in output or "Users" in output

    ws.close()
```

## 终端大小调整

terminado 支持通过 WebSocket 消息调整终端窗口大小：

```javascript
// 设置终端大小为 80 列 x 24 行
ws.send(JSON.stringify(['set_size', 24, 80]));
```

## 常见问题

### 连接返回 404

终端创建后需要短暂时间（通常 < 1 秒）初始化 PTY 进程。测试中常见的重试模式：

```python
while True:
    try:
        ws = await connect_websocket(term_name)
        break
    except HTTPClientError as e:
        if e.code != 404:
            raise
        await asyncio.sleep(1)
```

### WebSocket 认证

浏览器中 WebSocket 构造函数不支持自定义 headers。认证方式有两种：
1. **URL 参数**：`ws://localhost:8888/terminals/websocket/1?token=xxx`
2. **Cookie**：如果先通过 REST API 登录（Jupyter 会设置 cookie），WebSocket 连接会自动携带 cookie

### Windows 上的换行符

Windows 终端使用 `\r\n` 作为行分隔符，与 Linux/macOS 一致。发送命令时统一使用 `\r\n`。

### 输出包含控制字符

终端输出可能包含 ANSI 转义序列（颜色、光标移动等）。如果需要纯文本输出，需要在客户端过滤 ANSI 转义码：

```javascript
function stripAnsi(str) {
    return str.replace(/\x1b\[[0-9;]*[a-zA-Z]/g, '');
}
```

## 消息流示例

一次简单的 `echo hello` 交互的消息流：

```
客户端                                服务端
  │                                     │
  │  ["stdin", "echo hello\r\n"]        │── 写入 PTY
  │────────────────────────────────────►│
  │                                     │── Shell 执行命令
  │                                     │── PTY 输出
  │  ["stdout", "echo hello\r\n"]       │  (回显输入)
  │◄────────────────────────────────────│
  │  ["stdout", "hello\r\n"]            │  (命令输出)
  │◄────────────────────────────────────│
  │  ["stdout", "$ "]                   │  (新提示符)
  │◄────────────────────────────────────│
```

## 相关概念

- [WebSocket 处理器](../concepts/05-websocket.md)
- [REST API 处理器](../concepts/04-rest-api.md)
- [基础终端操作](basic-operations.md)
- [jupyter_server_terminals 源码信源登记](../references/jupyter-server-terminals-source.md)

[^jst-source]: jupyter_server_terminals 源码信源，见 [jupyter-server-terminals-source.md](../references/jupyter-server-terminals-source.md)。
