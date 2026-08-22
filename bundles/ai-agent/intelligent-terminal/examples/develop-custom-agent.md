---
type: Example
title: 开发自定义 ACP Agent
description: 实现符合 ACP（Agent Client Protocol）JSON-RPC 规范的自定义 Agent CLI，通过 stdio 与 WTA 通信，包括 initialize 握手、session 管理、prompt 流式响应、权限请求和终端操作。
tags:
  - intelligent-terminal
  - wta
  - acp
  - json-rpc
  - custom-agent
  - stdio
related:
  - "[ACP JSON-RPC Protocol](../concepts/acp-json-rpc-protocol.md)"
  - "[Named Pipe Transport](../concepts/named-pipe-transport.md)"
  - "[COM Protocol Server](../concepts/com-protocol-server.md)"
  - "[Agent Registry](../concepts/agent-registry.md)"
sources:
  - "tools/wta/src/protocol/acp/conn.rs"
  - "tools/wta/src/protocol/acp/spawn.rs"
  - "tools/wta/src/protocol/acp/mock_agent_tests.rs"
  - "tools/wta/src/agent_registry.rs"
---

## 场景说明

intelligent-terminal 的 WTA 通过 ACP（Agent Client Protocol）与 Agent CLI 通信。ACP 是基于 JSON-RPC 2.0 的 stdio 协议——Agent 从 stdin 读取请求，向 stdout 写入响应和通知。任何实现了 ACP 协议的可执行程序都可以作为自定义 Agent 接入 WTA，无需修改 WTA 源码。

ACP 协议的核心流程：
1. **握手（Initialize）**：WTA 发送 `initialize` 请求，Agent 返回协议版本和能力信息
2. **认证（Authenticate）**：如需要，WTA 发送 `authenticate` 请求
3. **会话（Session）**：WTA 通过 `session/new` 创建会话、`session/load` 恢复会话、`session/list` 列出会话
4. **提示（Prompt）**：WTA 发送 `prompt` 请求，Agent 流式返回 `session/update` 通知（包含文本块、工具调用、计划步骤等），最终返回 `prompt` 响应
5. **双向调用**：Agent 可以向 WTA 发送请求，如 `request_permission`（请求用户授权）、`create_terminal`（创建终端）、`terminal_output`（读写终端内容）

本示例演示如何用 Python 实现一个最小可用的 ACP Agent，并将其注册到 WTA 的 settings.json 中。

## 代码示例

### 示例 1：最小 ACP Agent（Python 实现）

创建文件 `my_agent.py`：

```python
#!/usr/bin/env python3
"""
Minimal ACP (Agent Client Protocol) Agent for intelligent-terminal WTA.
Communicates via JSON-RPC 2.0 over stdin/stdout.
"""

import sys
import json
import uuid
import asyncio
import argparse
from typing import Any, Optional


# ─── JSON-RPC 2.0 helpers ───────────────────────────────────────────────

def read_message() -> Optional[dict]:
    """Read a single JSON-RPC message from stdin (line-delimited JSON)."""
    line = sys.stdin.readline()
    if not line:
        return None
    line = line.strip()
    if not line:
        return read_message()
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def write_message(msg: dict) -> None:
    """Write a JSON-RPC message to stdout (line-delimited JSON)."""
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def send_result(id: Any, result: dict) -> None:
    """Send a JSON-RPC success response."""
    write_message({"jsonrpc": "2.0", "id": id, "result": result})


def send_error(id: Any, code: int, message: str, data: Any = None) -> None:
    """Send a JSON-RPC error response."""
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    write_message({"jsonrpc": "2.0", "id": id, "error": err})


def send_notification(method: str, params: dict) -> None:
    """Send a JSON-RPC notification (no id)."""
    write_message({"jsonrpc": "2.0", "method": method, "params": params})


# ─── ACP Method Handlers ────────────────────────────────────────────────

class SimpleAgent:
    """Minimal ACP agent implementation."""

    def __init__(self):
        self.sessions: dict[str, list[dict]] = {}  # session_id -> message history
        self.protocol_version = "2025-06-18"

    def handle_initialize(self, params: dict) -> dict:
        """Handle initialize request — return agent info and capabilities."""
        return {
            "protocolVersion": self.protocol_version,
            "agentInfo": {
                "name": "my-simple-agent",
                "version": "0.1.0",
                "title": "My Simple ACP Agent",
            },
            "capabilities": {
                "promptStreaming": True,
                "tools": [],  # No tools in this minimal agent
            },
        }

    def handle_authenticate(self, params: dict) -> dict:
        """Handle authenticate request — no auth needed for local agent."""
        return {}

    def handle_new_session(self, params: dict) -> dict:
        """Handle session/new — create a new session."""
        session_id = str(uuid.uuid4())
        cwd = params.get("cwd", "")
        self.sessions[session_id] = []
        return {"sessionId": session_id}

    def handle_load_session(self, params: dict) -> dict:
        """Handle session/load — resume an existing session."""
        session_id = params.get("sessionId", "")
        if session_id not in self.sessions:
            # Agent doesn't have this session — return error
            raise ValueError(f"Session {session_id} not found")
        return {"sessionId": session_id}

    def handle_list_sessions(self, params: dict) -> dict:
        """Handle session/list — return known sessions."""
        sessions = [
            {"sessionId": sid, "createdAt": 0, "summary": ""}
            for sid in self.sessions
        ]
        return {"sessions": sessions}

    async def handle_prompt(self, params: dict, request_id: Any) -> dict:
        """Handle prompt — process user message and stream response."""
        session_id = params.get("sessionId", "")
        prompt_blocks = params.get("prompt", [])
        is_autofix = params.get("isAutofix", False)

        # Extract text from prompt blocks
        user_text = ""
        for block in prompt_blocks:
            if block.get("type") == "text":
                user_text += block.get("text", "")

        # Store in session history
        if session_id in self.sessions:
            self.sessions[session_id].append({"role": "user", "text": user_text})

        # Generate a simple response (in a real agent, call an LLM here)
        if is_autofix:
            reply = f"[AutoFix] I detected an error. The command failed with: {user_text[:200]}"
        else:
            reply = f"Echo: {user_text}\n\n(This is a minimal ACP agent demo.)"

        # Stream response as AgentMessageChunk notifications
        chunk_size = 20
        for i in range(0, len(reply), chunk_size):
            chunk = reply[i:i+chunk_size]
            send_notification("session/update", {
                "sessionId": session_id,
                "update": {
                    "type": "agentMessageChunk",
                    "content": {"type": "text", "text": chunk},
                },
            })
            await asyncio.sleep(0.05)  # Simulate streaming delay

        # Store assistant reply
        if session_id in self.sessions:
            self.sessions[session_id].append({"role": "assistant", "text": reply})

        # Return final prompt response
        return {}

    def handle_set_session_model(self, params: dict) -> dict:
        """Handle session/set_model — model switching (optional)."""
        return {}

    def handle_cancel(self, params: dict) -> None:
        """Handle cancel notification — cancel in-flight prompt."""
        pass  # In a real agent, cancel the LLM generation here


# ─── Request Dispatcher ─────────────────────────────────────────────────

async def dispatch(agent: SimpleAgent, msg: dict) -> None:
    """Dispatch a JSON-RPC message to the appropriate handler."""
    method = msg.get("method", "")
    msg_id = msg.get("id")
    params = msg.get("params", {})

    # Notifications have no "id" field
    is_notification = "id" not in msg

    try:
        if method == "initialize":
            result = agent.handle_initialize(params)
            send_result(msg_id, result)

        elif method == "authenticate":
            result = agent.handle_authenticate(params)
            send_result(msg_id, result)

        elif method == "session/new":
            result = agent.handle_new_session(params)
            send_result(msg_id, result)

        elif method == "session/load":
            result = agent.handle_load_session(params)
            send_result(msg_id, result)

        elif method == "session/list":
            result = agent.handle_list_sessions(params)
            send_result(msg_id, result)

        elif method == "prompt":
            result = await agent.handle_prompt(params, msg_id)
            send_result(msg_id, result)

        elif method == "session/set_model":
            result = agent.handle_set_session_model(params)
            send_result(msg_id, result)

        elif method == "cancel":
            agent.handle_cancel(params)
            # Notification — no response

        else:
            if not is_notification:
                send_error(msg_id, -32601, f"Method not found: {method}")

    except ValueError as e:
        if not is_notification:
            send_error(msg_id, -32000, str(e))
    except Exception as e:
        if not is_notification:
            send_error(msg_id, -32603, f"Internal error: {e}")


async def main():
    parser = argparse.ArgumentParser(description="Simple ACP Agent")
    parser.add_argument("--acp", action="store_true", help="Run in ACP mode (stdio)")
    parser.add_argument("--stdio", action="store_true", help="Use stdio transport")
    parser.add_argument("--model", "-m", type=str, default="simple-v1", help="Model name")
    args = parser.parse_args()

    agent = SimpleAgent()

    # Main loop: read JSON-RPC messages from stdin
    while True:
        msg = read_message()
        if msg is None:
            break  # stdin closed
        await dispatch(agent, msg)


if __name__ == "__main__":
    asyncio.run(main())
```

### 示例 2：使用 Node.js 实现 ACP Agent（支持工具调用和权限请求）

创建文件 `my-agent.mjs`：

```javascript
#!/usr/bin/env node
/**
 * ACP Agent with tool support and permission requests (Node.js).
 */

import * as readline from 'node:readline';
import { v4 as uuidv4 } from 'uuid';

// ─── JSON-RPC Transport ────────────────────────────────────────────────

const rl = readline.createInterface({ input: process.stdin });

function writeMessage(msg) {
  process.stdout.write(JSON.stringify(msg) + '\n');
}

function sendResult(id, result) {
  writeMessage({ jsonrpc: '2.0', id, result });
}

function sendNotification(method, params) {
  writeMessage({ jsonrpc: '2.0', method, params });
}

function sendError(id, code, message, data) {
  const err = { code, message };
  if (data !== undefined) err.data = data;
  writeMessage({ jsonrpc: '2.0', id, error: err });
}

// ─── Pending requests (agent → client) ─────────────────────────────────

const pendingRequests = new Map();
let requestIdCounter = 1;

function sendClientRequest(method, params) {
  return new Promise((resolve, reject) => {
    const id = `agent-${requestIdCounter++}`;
    pendingRequests.set(id, { resolve, reject });
    writeMessage({ jsonrpc: '2.0', id, method, params });
  });
}

// ─── Agent State ───────────────────────────────────────────────────────

const sessions = new Map();
const pendingCancels = new Set();

// ─── Handlers ──────────────────────────────────────────────────────────

function initialize(params) {
  return {
    protocolVersion: '2025-06-18',
    agentInfo: {
      name: 'my-tool-agent',
      version: '0.2.0',
      title: 'My Tool-Enabled ACP Agent',
    },
    capabilities: {
      promptStreaming: true,
      tools: [
        {
          name: 'execute_command',
          description: 'Execute a shell command in the terminal',
          inputSchema: {
            type: 'object',
            properties: {
              command: { type: 'string', description: 'The command to execute' },
              cwd: { type: 'string', description: 'Working directory' },
            },
            required: ['command'],
          },
        },
      ],
    },
  };
}

function newSession(params) {
  const sessionId = uuidv4();
  sessions.set(sessionId, { cwd: params.cwd || '', messages: [] });
  return { sessionId };
}

async function prompt(params) {
  const { sessionId, prompt: blocks, context } = params;
  const session = sessions.get(sessionId);

  // Extract user text
  let userText = '';
  for (const block of blocks) {
    if (block.type === 'text') userText += block.text;
  }

  // Check for cancel
  if (pendingCancels.has(sessionId)) {
    pendingCancels.delete(sessionId);
    return { stopped: true };
  }

  // Example: analyze the user's request and potentially propose a command
  const toolCallId = uuidv4();

  // Stream: announce thinking/plan
  sendNotification('session/update', {
    sessionId,
    update: {
      type: 'agentMessageChunk',
      content: { type: 'text', text: 'Let me help you with that.\n\n' },
    },
  });

  // If the message looks like a command request, propose a tool call
  if (userText.toLowerCase().includes('run') || userText.toLowerCase().includes('execute')) {
    // Request permission before executing
    const permResponse = await sendClientRequest('request/permission', {
      sessionId,
      title: 'Execute Command',
      message: `The agent wants to run: echo "Hello from ACP"`,
      options: [
        { id: 'allow', label: 'Allow once' },
        { id: 'deny', label: 'Deny' },
      ],
    });

    if (permResponse.optionId === 'allow') {
      // Create a terminal and run the command
      const termResponse = await sendClientRequest('terminal/create', {
        sessionId,
        cwd: session?.cwd || '.',
      });

      // Send the command
      sendNotification('session/update', {
        sessionId,
        update: {
          type: 'terminal/input',
          terminalId: termResponse.terminalId,
          data: 'echo "Hello from my ACP agent"\n',
        },
      });

      // Wait for output (in a real agent, listen for terminal/output notifications)
      sendNotification('session/update', {
        sessionId,
        update: {
          type: 'agentMessageChunk',
          content: { type: 'text', text: 'Command executed. Check the terminal for output.' },
        },
      });
    } else {
      sendNotification('session/update', {
        sessionId,
        update: {
          type: 'agentMessageChunk',
          content: { type: 'text', text: 'Command execution was denied.' },
        },
      });
    }
  } else {
    // Simple echo response
    sendNotification('session/update', {
      sessionId,
      update: {
        type: 'agentMessageChunk',
        content: { type: 'text', text: `You said: ${userText}` },
      },
    });
  }

  return {};
}

function cancel(params) {
  pendingCancels.add(params.sessionId);
}

// ─── Main Loop ─────────────────────────────────────────────────────────

const handlers = {
  initialize: (p) => initialize(p),
  authenticate: () => ({}),
  'session/new': (p) => newSession(p),
  'session/load': (p) => ({ sessionId: p.sessionId }),
  'session/list': () => ({ sessions: [] }),
  'session/set_model': () => ({}),
  'session/set_mode': () => ({}),
  'session/cancel': (p) => cancel(p),
  'prompt': (p) => prompt(p),
};

rl.on('line', async (line) => {
  if (!line.trim()) return;
  let msg;
  try {
    msg = JSON.parse(line);
  } catch {
    return;
  }

  // Handle responses to our agent→client requests
  if (msg.id && pendingRequests.has(msg.id)) {
    const { resolve, reject } = pendingRequests.get(msg.id);
    pendingRequests.delete(msg.id);
    if (msg.error) reject(new Error(msg.error.message));
    else resolve(msg.result);
    return;
  }

  const method = msg.method;
  const id = msg.id;
  const params = msg.params || {};
  const isNotification = id === undefined;

  try {
    if (handlers[method]) {
      const result = await handlers[method](params);
      if (!isNotification) {
        sendResult(id, result);
      }
    } else if (!isNotification) {
      sendError(id, -32601, `Unknown method: ${method}`);
    }
  } catch (err) {
    if (!isNotification) {
      sendError(id, -32603, err.message);
    }
  }
});

rl.on('close', () => process.exit(0));
```

### 示例 3：打包自定义 Agent 为可执行文件

**Python 版本**：创建 `my-agent.cmd` 包装脚本（Windows）：

```batch
@echo off
python "C:\tools\my_agent.py" --acp --stdio %*
```

**Node.js 版本**：在 `package.json` 中配置 bin 入口：

```json
{
  "name": "my-acp-agent",
  "version": "0.2.0",
  "type": "module",
  "bin": {
    "my-agent": "./my-agent.mjs"
  },
  "dependencies": {
    "uuid": "^9.0.0"
  }
}
```

全局安装：

```bash
npm install -g .
# 或直接使用 node 运行
node my-agent.mjs --acp --stdio
```

### 示例 4：在 settings.json 中注册自定义 Agent

将自定义 Agent 配置到 Windows Terminal 的 settings.json：

```json
{
  "agentCliPath": "C:\\tools\\my-agent.cmd --acp --stdio",
  "agentId": "custom:my-agent"
}
```

或者使用 Node.js 版本：

```json
{
  "agentCliPath": "node C:\\tools\\my-agent.mjs --acp --stdio",
  "agentId": "custom:my-tool-agent"
}
```

> **重要**：`agentId` 使用 `custom:` 前缀时，WTA 将其识别为自定义 Agent，不匹配内置 Profile。命令行必须包含 ACP 模式标志（`--acp --stdio`），以确保 Agent 以 ACP 协议模式启动。

### 示例 5：验证自定义 Agent 连接

使用 wta CLI 测试自定义 Agent：

```powershell
# 探测 Agent 模型列表
wta probe-models --agent "C:\tools\my-agent.cmd --acp --stdio"

# 直接启动 WTA 使用自定义 Agent
wta --agent "C:\tools\my-agent.cmd --acp --stdio" --agent-id "custom:my-agent"

# 启动并发送初始提示
wta --agent "C:\tools\my-agent.cmd --acp --stdio" "Hello from custom agent!"
```

`wta probe-models` 成功输出（自定义 Agent 可以返回空模型列表）：

```json
{"available_models":[],"current_model_id":""}
```

### 示例 6：Rust 中实现 ACP Agent（使用 agent-client-protocol crate）

对于 Rust 项目，可以直接使用 WTA 依赖的 `agent-client-protocol` crate：

```rust
// Cargo.toml dependencies:
// agent-client-protocol = { git = "https://github.com/agent-client-protocol/rust" }
// tokio = { version = "1", features = ["full"] }
// serde = { version = "1", features = ["derive"] }
// serde_json = "1"

use agent_client_protocol as acp;
use acp::schema::v1::*;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};

#[derive(Clone)]
struct MyAgent;

#[acp::async_trait]
impl acp::Agent for MyAgent {
    async fn initialize(
        &self,
        args: InitializeRequest,
    ) -> acp::Result<InitializeResponse> {
        Ok(InitializeResponse::new(args.protocol_version)
            .agent_info(Implementation::new("my-rust-agent", "0.1.0")
                .title("My Rust ACP Agent")))
    }

    async fn authenticate(
        &self,
        _args: AuthenticateRequest,
    ) -> acp::Result<AuthenticateResponse> {
        Ok(AuthenticateResponse::default())
    }

    async fn new_session(
        &self,
        _args: NewSessionRequest,
    ) -> acp::Result<NewSessionResponse> {
        Ok(NewSessionResponse::new(SessionId::new("session-1")))
    }

    async fn prompt(
        &self,
        args: PromptRequest,
        conn: acp::ConnectionTo<acp::Client>,
    ) -> acp::Result<PromptResponse> {
        let text = args.prompt.iter()
            .filter_map(|b| match b {
                ContentBlock::Text(t) => Some(t.text.as_str()),
                _ => None,
            })
            .collect::<Vec<_>>()
            .join("");

        let sid = args.session_id.clone();
        // Stream response
        conn.session_notification(SessionNotification::new(
            sid,
            SessionUpdate::AgentMessageChunk(
                ContentChunk::new(ContentBlock::Text(TextBlock::new(
                    format!("Rust agent received: {}", text)
                )))
            )
        )).await?;

        Ok(PromptResponse::default())
    }
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let stdin = tokio::io::stdin();
    let stdout = tokio::io::stdout();
    let agent = MyAgent;

    acp::connect_with(
        acp::Transport::stdio(stdin, stdout),
        agent,
        |_conn| async { Ok(()) },
    ).await?;

    Ok(())
}
```

## 逐步解释

1. **传输层**：ACP 协议使用 stdio（stdin/stdout）作为传输层。WTA 启动 Agent 进程后，通过 [`spawn_agent_process()`](file:///d:/spaces/SpecWeave/external/libs/models/ai/intelligent-terminal/tools/wta/src/protocol/acp/spawn.rs#L202-L325) 将子进程的 stdin/stdout/stderr 连接到管道，然后在管道上进行 JSON-RPC 通信。每条消息是一行 JSON（line-delimited JSON）。

2. **JSON-RPC 2.0**：所有消息遵循 JSON-RPC 2.0 格式。请求包含 `jsonrpc`、`id`、`method`、`params`；响应包含 `jsonrpc`、`id`、`result`（或 `error`）；通知包含 `jsonrpc`、`method`、`params`（无 `id`）。

3. **握手流程**：WTA 连接后首先发送 `initialize` 请求，Agent 必须返回 `protocolVersion` 和 `agentInfo`。随后 WTA 发送 `authenticate` 请求（对于需要认证的 Agent）。WTA 使用 [`conn.spawn_client()`](file:///d:/spaces/SpecWeave/external/libs/models/ai/intelligent-terminal/tools/wta/src/protocol/acp/conn.rs) 中的 `ClientLink` 来驱动这些请求。

4. **会话管理**：每个 Agent 面板（标签页）对应一个 ACP Session。`session/new` 创建新会话并返回 `sessionId`；`session/load` 恢复历史会话；`session/list` 返回可恢复的会话列表。会话 ID 由 Agent 生成。

5. **流式响应**：`prompt` 请求的响应通过 `session/update` 通知流式返回。Agent 可以发送多个 `AgentMessageChunk` 来构建回复，每个 chunk 包含文本、图片、工具调用等内容块。最终的 `prompt` 响应只需要是空对象 `{}`。

6. **Agent→Client 请求**：Agent 可以向 WTA（client）发送请求，如：
   - `request/permission`：请求用户授权执行操作
   - `terminal/create`：创建新终端
   - `terminal/input`：向终端发送输入
   - `terminal/output`：读取终端输出
   - `terminal/wait_for_exit`：等待终端进程退出
   - `fs/read_text_file` / `fs/write_text_file`：读写文件

   这些请求是双向的——Agent 发送带 `id` 的请求，WTA 返回响应。[`AgentLink`](file:///d:/spaces/SpecWeave/external/libs/models/ai/intelligent-terminal/tools/wta/src/protocol/acp/conn.rs#L200) 封装了这些 client→agent 的方法。

7. **自定义 Agent 识别**：WTA 通过 [`resolve_agent_id_from_cmd()`](file:///d:/spaces/SpecWeave/external/libs/models/ai/intelligent-terminal/tools/wta/src/agent_registry.rs#L291-L312) 解析 Agent ID。如果命令行不匹配任何内置 Agent，ID 为 `"unknown"`。使用 `--agent-id custom:<name>` 显式指定自定义 ID。

8. **进程生命周期**：Agent 进程由 wta-master 管理，使用 `kill_on_drop=true` 在连接断开时自动终止。stderr 被捕获用于日志记录，启动失败时前 32 行 stderr 会被提升到 warn 级别日志。

## 输出结果

配置自定义 Agent 并重启 Terminal 后：

1. 按 `Ctrl+Shift+.` 打开 Agent 面板，面板标题显示自定义 Agent 名称
2. 输入消息发送后，自定义 Agent 的回复流式显示在聊天区域
3. 如果 Agent 支持工具调用和权限请求，会弹出权限确认对话框
4. `wta probe-models` 成功返回 JSON 结果表示 ACP 握手正常
5. 命令失败时（需 OSC 133 集成），Autofix 会向自定义 Agent 发送带 `isAutofix: true` 的 prompt

验证步骤输出：

```
> wta --agent "C:\tools\my-agent.cmd --acp --stdio" "hello"
# Agent 面板显示:
# Echo: hello
#
# (This is a minimal ACP agent demo.)
```

## 注意事项

- **必须实现的最小方法集**：`initialize`、`authenticate`、`session/new`、`prompt`。缺少任何一个方法 WTA 都会在握手阶段报错。
- **行分隔 JSON**：每条 JSON 消息必须是单行，以 `\n` 结尾。不要输出格式化（pretty-printed）的 JSON，否则 WTA 的行读取器会将一条消息拆成多行。
- **stdout 只用于 JSON-RPC**：Agent 的 stdout 必须 exclusively 用于 JSON-RPC 消息。任何调试输出必须写到 stderr（`console.error`、`sys.stderr.write`、`eprintln!`），否则会破坏 JSON-RPC 解析。
- **`--acp --stdio` 标志**：自定义 Agent 应该支持这两个标志，以便与内置 Agent 的命令行格式保持一致。WTA 解析命令行时会原样传递所有参数给 Agent。
- **异步和取消**：`prompt` 处理必须支持取消——当 WTA 发送 `cancel` 通知（`session/cancel`）时，Agent 应尽快停止生成并返回。如果不处理取消，用户按 Ctrl+C 后 Agent 可能继续运行浪费资源。
- **npx 路径**：如果自定义 Agent 通过 npx 启动，WTA 会自动延长 initialize 超时时间（首次 npx 运行需要下载包）。直接使用本地路径的 Agent 使用默认超时。
- **PATH 环境**：WTA 启动 Agent 时会将自己的目录添加到 PATH 最前面，确保 Agent 可以调用 `wta.exe` CLI 工具。
- **CLAUDECODE 环境变量**：WTA 启动 Agent 时会移除 `CLAUDECODE` 环境变量（防止 Claude Code 适配器的递归保护误触发）。如果你的 Agent 不使用该变量，无需关心。
- **会话隔离**：每个标签页的会话是独立的。wta-master 通过 N:1 多路复用将多个 helper（面板）的会话复用到单个 Agent 进程上，Agent 需要正确处理并发的多个 sessionId。
