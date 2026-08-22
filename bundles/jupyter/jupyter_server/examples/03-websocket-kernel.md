---
type: Example
title: "WebSocket 内核通信"
description: "通过 WebSocket 连接内核、发送执行请求、接收输出的完整 Python/JavaScript 示例"
tags: [websocket, kernel, execute, zmq, messaging, real-time]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T15:10:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: websocket
    resource: /references/websocket-base-source.md
    title: WebSocket 基类源码信源
  - id: kernels
    resource: /references/kernels-source.md
    title: 内核管理源码信源
---

# WebSocket 内核通信示例

本示例展示如何通过 WebSocket 连接 Jupyter 内核，发送代码执行请求并实时接收输出。

## 内核消息协议概述

WebSocket 消息是一个 JSON 数组：`[channel, header, parent_header, metadata, content, buffers]`

| 字段 | 说明 |
|------|------|
| channel | 消息通道：`shell`/`iopub`/`stdin`/`control` |
| header | 消息头：包含 msg_id、msg_type、session 等 |
| parent_header | 父消息头（响应关联到请求） |
| metadata | 元数据（通常为空 dict） |
| content | 消息内容（根据 msg_type 不同） |
| buffers | 二进制数据（如图片） |

常见 msg_type：
- 请求：`execute_request`、`kernel_info_request`、`complete_request`
- 回复：`execute_reply`、`kernel_info_reply`、`complete_reply`
- IOPub：`stream`、`display_data`、`execute_result`、`error`、`status`

## 示例一：Python WebSocket 客户端

```python
import asyncio
import json
import uuid
import websockets
import requests

# 配置
BASE_URL = "http://localhost:8888"
WS_BASE = "ws://localhost:8888"
TOKEN = "mytoken"

class JupyterKernelClient:
    def __init__(self, base_url=BASE_URL, token=TOKEN, kernel_name="python3"):
        self.base_url = base_url
        self.token = token
        self.kernel_name = kernel_name
        self.kernel_id = None
        self.session_id = uuid.uuid4().hex
        self.ws = None
        self.msg_counter = 0

    def _headers(self):
        return {"Authorization": f"token {self.token}"}

    def _msg_id(self):
        self.msg_counter += 1
        return f"msg-{self.session_id}-{self.msg_counter}"

    async def start_kernel(self):
        """启动新内核"""
        resp = requests.post(
            f"{self.base_url}/api/kernels",
            headers=self._headers(),
            json={"name": self.kernel_name},
        )
        resp.raise_for_status()
        self.kernel_id = resp.json()["id"]
        print(f"Started kernel: {self.kernel_id}")

    async def connect_ws(self):
        """连接 WebSocket"""
        ws_url = f"{self.ws_base}/api/kernels/{self.kernel_id}/channels?token={self.token}"
        self.ws = await websockets.connect(
            ws_url,
            subprotocols=["v1.kernel.websocket.jupyter.org"],
        )
        print("WebSocket connected")

    async def send_execute_request(self, code, silent=False):
        """发送代码执行请求"""
        msg_id = self._msg_id()
        msg = [
            "shell",  # channel
            {
                "msg_id": msg_id,
                "msg_type": "execute_request",
                "session": self.session_id,
                "date": "",
                "version": "5.3",
                "username": "api-client",
            },
            {},  # parent_header
            {},  # metadata
            {
                "code": code,
                "silent": silent,
                "store_history": not silent,
                "user_expressions": {},
                "allow_stdin": False,
                "stop_on_error": True,
            },
            [],  # buffers
        ]
        await self.ws.send(json.dumps(msg))
        return msg_id

    async def wait_for_execute_result(self, msg_id, timeout=30):
        """等待执行结果，收集所有输出"""
        outputs = []
        execution_count = None

        while True:
            raw = await asyncio.wait_for(self.ws.recv(), timeout=timeout)
            msg = json.loads(raw)
            channel = msg[0]
            header = msg[1]
            parent = msg[2]
            content = msg[4]

            # 只处理与我们请求相关的消息
            if parent.get("msg_id") != msg_id and header["msg_type"] != "status":
                continue

            msg_type = header["msg_type"]

            if channel == "iopub":
                if msg_type == "status":
                    state = content.get("execution_state")
                    if state == "idle":
                        break  # 执行完成
                    elif state == "busy":
                        continue
                elif msg_type == "stream":
                    outputs.append({"type": "stream", "name": content["name"], "text": content["text"]})
                    print(f"[{content['name']}] {content['text']}", end="")
                elif msg_type == "execute_result":
                    execution_count = content.get("execution_count")
                    outputs.append({"type": "result", "data": content["data"]})
                    print(f"[Out[{execution_count}]] {content['data'].get('text/plain', '')}")
                elif msg_type == "display_data":
                    outputs.append({"type": "display", "data": content["data"]})
                elif msg_type == "error":
                    outputs.append({"type": "error", "ename": content["ename"], "evalue": content["evalue"]})
                    print(f"Error: {content['ename']}: {content['evalue']}")
                    break
            elif channel == "shell":
                if msg_type == "execute_reply":
                    execution_count = content.get("execution_count", execution_count)

        return {"execution_count": execution_count, "outputs": outputs}

    async def execute(self, code):
        """执行代码并返回结果"""
        msg_id = await self.send_execute_request(code)
        return await self.wait_for_execute_result(msg_id)

    async def shutdown_kernel(self):
        """关闭内核"""
        if self.ws:
            await self.ws.close()
        if self.kernel_id:
            requests.delete(
                f"{self.base_url}/api/kernels/{self.kernel_id}",
                headers=self._headers(),
            )
            print(f"Shutdown kernel: {self.kernel_id}")


async def main():
    client = JupyterKernelClient()
    try:
        await client.start_kernel()
        await client.connect_ws()

        # 等待内核启动
        await asyncio.sleep(2)

        # 执行简单代码
        print("\n>>> print('Hello, World!')")
        result = await client.execute("print('Hello, World!')")

        # 执行数学计算
        print("\n>>> 1 + 2 * 3")
        result = await client.execute("1 + 2 * 3")

        # 执行多行代码
        print("\n>>> for i in range(3): ...")
        result = await client.execute("""
import sys
for i in range(3):
    print(f"Loop {i}", file=sys.stderr)
""")

        # 绘图（需要 matplotlib）
        print("\n>>> 绘图...")
        result = await client.execute("""
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.title("Test Plot")
    plt.savefig('/tmp/plot.png')
    print("Plot saved!")
except ImportError:
    print("matplotlib not installed")
""")

    finally:
        await client.shutdown_kernel()


if __name__ == "__main__":
    asyncio.run(main())
```

## 示例二：JavaScript 浏览器客户端

```html
<!DOCTYPE html>
<html>
<head>
    <title>Kernel WS Client</title>
    <style>
        body { font-family: monospace; max-width: 800px; margin: 20px auto; padding: 20px; }
        #output { background: #f5f5f5; padding: 15px; border-radius: 4px; min-height: 200px; }
        #code { width: 100%; height: 80px; font-family: monospace; padding: 10px; }
        button { padding: 8px 16px; margin: 10px 0; cursor: pointer; }
        .out-stdout { color: #000; }
        .out-stderr { color: #c00; }
        .out-result { color: #00c; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Jupyter Kernel WebSocket Client</h1>
    <textarea id="code" placeholder="Enter Python code...">print("Hello from browser!")
x = 42
print(f"x = {x}")
x ** 2</textarea>
    <button onclick="executeCode()">Run Code (Shift+Enter)</button>
    <div id="output"></div>

    <script>
        const BASE = location.origin;
        const TOKEN = new URLSearchParams(location.search).get('token') || '';
        let kernelId = null;
        let ws = null;
        let sessionId = crypto.randomUUID().replace(/-/g, '');
        let msgCounter = 0;

        function msgId() {
            return `msg-${sessionId}-${++msgCounter}`;
        }

        async function startKernel() {
            const resp = await fetch(`${BASE}/api/kernels?token=${TOKEN}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: 'python3'})
            });
            const data = await resp.json();
            kernelId = data.id;
            log(`Kernel started: ${kernelId}`, 'info');
        }

        function connectWS() {
            return new Promise((resolve, reject) => {
                const wsUrl = `${BASE.replace('http', 'ws')}/api/kernels/${kernelId}/channels?token=${TOKEN}`;
                ws = new WebSocket(wsUrl, ['v1.kernel.websocket.jupyter.org']);
                ws.onopen = () => { log('WS connected', 'info'); resolve(); };
                ws.onerror = (e) => reject(e);
                ws.onmessage = onMessage;
            });
        }

        function onMessage(event) {
            const msg = JSON.parse(event.data);
            const [channel, header, parent, , content] = msg;
            const msgType = header.msg_type;

            if (msgType === 'status') {
                const state = content.execution_state;
                if (state === 'idle') log('✓ Done', 'info');
                return;
            }

            if (channel === 'iopub') {
                if (msgType === 'stream') {
                    log(content.text, content.name === 'stderr' ? 'err' : 'out');
                } else if (msgType === 'execute_result') {
                    const text = content.data['text/plain'] || JSON.stringify(content.data);
                    log(text, 'result');
                } else if (msgType === 'error') {
                    log(`${content.ename}: ${content.evalue}`, 'err');
                    content.traceback.forEach(tb => log(tb, 'err'));
                }
            }
        }

        function executeCode() {
            const code = document.getElementById('code').value;
            if (!ws || ws.readyState !== WebSocket.OPEN) return;

            const id = msgId();
            const msg = [
                'shell',
                {
                    msg_id: id, msg_type: 'execute_request',
                    session: sessionId, date: '', version: '5.3', username: 'web'
                },
                {}, {},
                { code: code, silent: false, store_history: true,
                  user_expressions: {}, allow_stdin: false, stop_on_error: true },
                []
            ];
            ws.send(JSON.stringify(msg));
            log(`>>> ${code.split('\n')[0]}${code.includes('\n')?'...':''}`, 'info');
        }

        function log(text, cls='') {
            const div = document.getElementById('output');
            const p = document.createElement('pre');
            p.className = `out-${cls}`;
            p.textContent = text;
            p.style.margin = '2px 0';
            div.appendChild(p);
            div.scrollTop = div.scrollHeight;
        }

        // Shift+Enter to run
        document.getElementById('code').addEventListener('keydown', e => {
            if (e.key === 'Enter' && e.shiftKey) { e.preventDefault(); executeCode(); }
        });

        // Init
        (async () => {
            await startKernel();
            await connectWS();
            await new Promise(r => setTimeout(r, 2000));
            log('Ready! Write code and press Shift+Enter.', 'info');
        })();
    </script>
</body>
</html>
```

## 使用说明

### Python 客户端运行

```bash
# 安装依赖
pip install websockets requests

# 确保 Jupyter Server 运行
jupyter server --ServerApp.token=mytoken --no-browser

# 运行客户端
python kernel_ws_client.py
```

### JavaScript 客户端

1. 将 HTML 文件放到 Jupyter Server 可访问的位置
2. 或通过扩展提供静态页面
3. 在浏览器中打开，URL 加上 `?token=xxx` 参数

## 注意事项

1. **内核启动延迟**：WebSocket 连接建立后，内核可能还在 starting 状态，消息会被缓冲
2. **消息关联**：通过 `parent_header.msg_id` 将 IOPub 输出关联到 shell 请求
3. **idle 信号**：`status: idle` 表示本次执行完成，是消息流的结束标志
4. **二进制数据**：图片等二进制数据通过 buffers 字段传递
5. **连接关闭**：所有 WebSocket 断开后，内核仍运行，需要显式调用 DELETE /api/kernels

## 参考

- [WebSocket 通信](../concepts/11-websocket-communication.md) — WebSocket 架构详解
- [内核管理](../concepts/08-kernel-management.md) — 内核生命周期
