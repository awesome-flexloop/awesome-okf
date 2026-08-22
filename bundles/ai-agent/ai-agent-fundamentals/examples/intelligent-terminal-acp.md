---
type: Example
title: Intelligent Terminal ACP 集成模式
description: Windows Terminal 如何通过 ACP 协议、COM 服务器、Named Pipe 和 OSC 转义序列实现原生 Agent 集成——C++/Rust 双语言架构深度解析
tags: [ai-agent, acp, intelligent-terminal, com, named-pipe, osc, rust, cpp, windows]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T02:15:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T02:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: src-register
    resource: /references/ai-agent-sources.md#intelligent-terminal
---

# Intelligent Terminal ACP 集成模式

Intelligent Terminal（微软 Windows Terminal 实验分支）展示了如何将 AI Agent **深度嵌入已有桌面应用**——不是启动一个独立的聊天窗口，而是让 Agent 与终端深度融合：自动检测命令错误、提供修复建议、通过 wtcli 控制终端。本示例解析其 C++/Rust 双语言架构、ACP 协议实现和关键集成模式。

## 1. 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Windows Terminal 进程                         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  C++/XAML 层 (TerminalApp)                              │    │
│  │  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐  │    │
│  │  │Terminal  │ │Command    │ │AgentPane │ │Tab       │  │    │
│  │  │Page.cpp  │ │Palette    │ │Content   │ │stash/    │  │    │
│  │  │(主入口)  │ │(?前缀触发)│ │(XAML封装)│ │restore  │  │    │
│  │  └────┬─────┘ └───────────┘ └──────────┘ └──────────┘  │    │
│  │       │ OSC 133 事件          ▲                         │    │
│  │       │                      │ XAML 绑定                 │    │
│  └───────┼──────────────────────┼──────────────────────────┘    │
│          │ COM (MTA/MBM)       │                               │
│  ┌───────▼──────────────────────┼──────────────────────────┐    │
│  │  TerminalProtocolComServer  │                           │    │
│  │  (进程外 COM 服务器)         │                           │    │
│  │  WT_COM_CLSID               │                           │    │
│  └───────┬──────────────────────┼──────────────────────────┘    │
│          │                     │                                │
│  ┌───────▼─────────────────────┴──────────────────────────┐    │
│  │  SharedWta (单例)                                        │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │  spawn → wta-master (Rust 进程)                   │  │    │
│  │  │  ┌────────────────────────────────────────────┐  │  │    │
│  │  │  │ ACP/JSON-RPC 2.0 over stdio                │  │  │    │
│  │  │  │ ▼                                            │  │  │    │
│  │  │  │ Agent CLI (Claude/Codex/Gemini/...)         │  │  │    │
│  │  │  └────────────────────────────────────────────┘  │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────┘    │
│              ▲  (每个标签页)                                    │
│              │ Named Pipe (ACP/JSON-RPC 2.0)                   │
│  ┌───────────┴────────────────────────────────────────────┐    │
│  │  wta-helper × N (Rust 进程, 每标签页一个, 预热启动)      │    │
│  │  - ACP 会话端点                                        │    │
│  │  - 连接到 wta-master                                   │    │
│  │  - Stash 保留（面板关闭不销毁）                          │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  wtcli (命令行工具)                                      │   │
│  │  - list-panes / capture-pane / listen / send-keys       │   │
│  │  - 通过 CoCreateInstance 调用 COM 接口                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 2. 双语言架构：C++ + Rust

Intelligent Terminal 采用双语言架构，C++ 和 Rust 各自处理最擅长的部分：

| 层 | 语言 | 职责 | 原因 |
|----|------|------|------|
| UI 层 | C++/XAML | 终端渲染、XAML 界面、标签页管理 | 复用 Windows Terminal 现有 C++ 代码库 |
| 协议层 | C++/COM | WinRT IDL 定义、进程外 COM 服务器 | Windows 平台原生 IPC 机制 |
| Agent 编排 | Rust | WTA master/helper 进程、ACP 协议 | 内存安全、异步 I/O、进程管理 |
| 工具层 | Rust (wtcli) | 命令行控制终端 | 与 wta-master 共享 Rust 代码 |

**安全边界设计**：Rust 处理网络/协议（内存安全，避免解析 JSON-RPC 时的内存漏洞），C++ 处理 UI/渲染（复用现有代码库，不重写）。

## 3. WT 协议：COM 作为唯一集成面

Windows Terminal 定义了 `IProtocolServer` WinRT 接口，这是 Agent 与终端交互的**唯一**集成面。

### IDL 定义

```idl
// TerminalProtocol.idl (概念性)
namespace Microsoft.Terminal.Protocol;

[contract(WindowsTerminalContract, 1)]
interface IPane : IInspectable
{
    UInt32 Id { get; };
    String Title { get; };
    String CaptureText();
    void SendInput(String input);
    void Resize(UInt32 rows, UInt32 cols);
    event EventHandler<Object> OutputRecieved;
    event EventHandler<Int32> CommandCompleted;  // exit code
}

[contract(WindowsTerminalContract, 1)]
interface IProtocolServer : IInspectable
{
    Windows.Foundation.Collections.IVector<IPane> ListPanes();
    IPane GetFocusedPane();
    Object GetPane(UInt32 paneId);
    event EventHandler<Object> PaneCreated;
    event EventHandler<UInt32> PaneClosed;
}

[contract(WindowsTerminalContract, 1)]
runtimeclass TerminalProtocolServer
{
    TerminalProtocolServer();
    static IProtocolServer GetInstance();
}
```

### COM 进程外服务器

```cpp
// TerminalProtocolComServer.cpp (概念性)
class TerminalProtocolComServer : public winrt::implements<
    TerminalProtocolComServer,
    ITerminalProtocolServer,
    IClassFactory,
    FtmBase  // Free Threaded Marshaler (MTA)
>
{
public:
    // COM 类工厂
    IFACEMETHODIMP CreateInstance(IUnknown* pUnkOuter, REFIID riid, void** ppv) {
        // 返回单例 SharedWta
        return SharedWta::get_instance().QueryInterface(riid, ppv);
    }
    
    // IPane 枚举
    IFACEMETHODIMP ListPanes(IVector<IPane>** panes) {
        auto result = winrt::single_threaded_vector<IPane>();
        for (const auto& tab : _tabs) {
            for (const auto& pane : tab->GetPanes()) {
                result.Append(pane.As<IPane>());
            }
        }
        *panes = result.as<IVector<IPane>>().detach();
        return S_OK;
    }
};
```

选择 COM 进程外服务器（LocalServer32）而非进程内 DLL 的原因：
1. **稳定性**：Agent 代码崩溃不影响终端主进程
2. **安全性**：COM 权限控制 Agent 能做什么
3. **语言无关**：任何语言都可以通过 COM 调用（Rust 的 wtcli 就是例子）
4. **MBM（Marshaled-by-Value）**：跨进程数据封送

## 4. WTA：Rust 编写的 Agent 编排器

WTA（Windows Terminal Agent）是整个系统的核心，分为 master 和 helper 两个二进制。

### wta-master：单例 Agent 生命周期管理器

```rust
// tools/wta/src/master/mod.rs (概念性)
pub struct WtaMaster {
    agent_process: Option<Child>,           // Agent CLI 子进程
    agent_stdin: Option<ChildStdin>,         // Agent 标准输入（发送 ACP 消息）
    agent_stdout: Option<ChildStdout>,       // Agent 标准输出（接收 ACP 消息）
    helpers: HashMap<PaneId, WtaHelperConnection>,  // 连接的 helpers
    pending_requests: HashMap<RequestId, oneshot::Sender<Response>>,
}

impl WtaMaster {
    /// 启动 Agent CLI 进程
    pub async fn spawn_agent(&mut self, config: AgentConfig) -> Result<()> {
        let mut cmd = Command::new(&config.command);
        cmd.args(&config.args)
           .stdin(Stdio::piped())
           .stdout(Stdio::piped())
           .stderr(Stdio::inherit())
           .env("ACP_PROTOCOL", "json-rpc-2.0");
        
        let mut child = cmd.spawn()?;
        self.agent_stdin = child.stdin.take();
        self.agent_stdout = child.stdout.take();
        self.agent_process = Some(child);
        
        // 发送 ACP initialize 请求
        self.send_acp_initialize().await?;
        
        Ok(())
    }
    
    /// 处理来自 helper 的 ACP 请求（named pipe 上的 JSON-RPC）
    async fn handle_helper_message(&mut self, pane_id: PaneId, msg: JsonRpcMessage) {
        match msg.method.as_str() {
            "session/create" => {
                // 为该 pane 创建 ACP 会话
                let session = self.create_session(pane_id, msg.params).await?;
                self.forward_to_agent(session).await?;
            }
            "session/send" => {
                // 转发用户消息到 Agent
                self.forward_to_agent(msg.params).await?;
            }
            "pane/capture" => {
                // 请求捕获终端内容（通过 COM 接口）
                let content = self.capture_pane_via_com(msg.params.pane_id)?;
                self.send_response(msg.id, content).await?;
            }
            _ => {}
        }
    }
    
    /// 处理来自 Agent CLI 的 ACP 响应（stdio 上的 JSON-RPC）
    async fn handle_agent_message(&mut self, msg: JsonRpcMessage) {
        match msg.method.as_str() {
            "tool/call" => {
                // Agent 请求调用工具（如 wtcli list-panes）
                let result = self.handle_tool_call(msg.params).await?;
                self.send_to_agent(msg.id, result).await?;
            }
            "message/delta" => {
                // Agent 流式输出 → 转发到对应 helper
                if let Some(helper) = self.helpers.get(&msg.pane_id) {
                    helper.send_delta(msg.params).await?;
                }
            }
            _ => {}
        }
    }
}
```

### wta-helper：每标签页的 ACP 会话端点

```rust
// tools/wta/src/app.rs (概念性)
pub struct WtaHelper {
    pane_id: PaneId,
    master_pipe: Option<NamedPipeClient>,   // 到 master 的 named pipe
    acp_session: Option<AcpSession>,
    stashed: bool,                          // 是否 stash 状态
}

impl WtaHelper {
    /// 预热启动：创建标签页时就启动 helper，但不显示面板
    pub async fn pre_warmed_start(pane_id: PaneId) -> Result<Self> {
        let mut helper = Self {
            pane_id,
            master_pipe: None,
            acp_session: None,
            stashed: true,  // 初始为 stash 状态
        };
        
        // 后台连接到 master（不阻塞 UI）
        helper.connect_to_master_async().await?;
        
        Ok(helper)
    }
    
    /// 用户打开 Agent 面板时激活
    pub async fn activate(&mut self) -> Result<()> {
        if self.stashed {
            // 如果是 stash 状态，恢复会话
            self.acp_session = Some(
                self.master_pipe.as_ref().unwrap()
                    .create_session(self.pane_id).await?
            );
            self.stashed = false;
        }
        Ok(())
    }
    
    /// 用户关闭面板时 stash（不销毁）
    pub fn stash(&mut self) {
        self.stashed = true;
        // 不断开连接、不销毁会话、保留聊天历史
    }
}
```

## 5. ACP 协议：JSON-RPC 2.0

ACP 使用 JSON-RPC 2.0 作为序列化协议，在两个通道上运行：

### 通道 1：master ↔ Agent CLI（stdio）

```json
// → Agent: initialize
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "0.1",
    "capabilities": {
      "tools": true,
      "streaming": true
    }
  },
  "id": 1
}

// ← Agent: response
{
  "jsonrpc": "2.0",
  "result": {
    "capabilities": {
      "tools": [
        {"name": "wtcli", "description": "Control Windows Terminal"},
        {"name": "shell_exec", "description": "Execute shell command"}
      ]
    }
  },
  "id": 1
}

// Agent 工具调用 →
{
  "jsonrpc": "2.0",
  "method": "tool/call",
  "params": {
    "name": "wtcli",
    "arguments": {"command": "capture-pane", "paneId": 0}
  },
  "id": 2
}

// 工具结果 ←
{
  "jsonrpc": "2.0",
  "result": {"output": "PS C:\\workspace> ...", "exitCode": 0},
  "id": 2
}
```

### 通道 2：helper ↔ master（Named Pipe）

Named Pipe 用于 helper 和 master 之间的通信，每个 helper 有独立的 pipe 连接：

```json
// Helper → Master: 发送用户消息
{
  "jsonrpc": "2.0",
  "method": "session/send",
  "params": {
    "paneId": 0,
    "message": {"role": "user", "content": "fix this error"},
    "context": {
      "capturedOutput": "...",
      "shell": "powershell",
      "cwd": "C:\\workspace"
    }
  },
  "id": 5
}

// Master → Helper: 流式响应
{
  "jsonrpc": "2.0",
  "method": "message/delta",
  "params": {
    "paneId": 0,
    "delta": {"type": "text", "content": "The error is caused by..."}
  }
}
```

## 6. 关键集成模式

### 模式一：预热启动（Pre-warmed Startup）

**问题**：启动 Agent CLI 进程（加载模型、初始化）需要数秒，用户打开面板时等待会造成糟糕体验。

**解决方案**：
1. 创建标签页时就启动 wta-helper（后台运行，不显示 UI）
2. Helper 预连接到 master，ACP 会话在后台建立
3. 用户按 `Ctrl+Shift+.` 时，helper 已经是 ACTIVE 状态
4. 面板瞬间打开，无需等待

### 模式二：Stash 而非 Destroy

**问题**：用户关闭 Agent 面板后再打开，如果完全销毁状态（进程、连接、历史），再次启动需要等待且丢失上下文。

**解决方案**：
- `Ctrl+Shift+.` 切换面板时，helper/conpty/ACP/聊天历史**全部保留**（stash）
- XAML 面板只是隐藏，不是销毁
- 再次打开时从 stash 恢复，瞬间回到之前的状态
- 标签页关闭时才真正销毁 helper

### 模式三：OSC 133 错误事件总线

**问题**：Agent 如何知道命令执行失败了？轮询终端输出既慢又不可靠。

**解决方案**：利用 Shell 集成（OSC 133 转义序列）：

```
Shell 提示符配置（PowerShell profile）:
  命令开始 → 发送 OSC 133;A
  命令结束 → 发送 OSC 133;D;<exit_code>
  提示符开始 → 发送 OSC 133;B

例如命令失败（exit_code=1）时，Shell 发送:
  ESC ] 133 ; D ; 1 ST

TerminalPage 捕获这个序列:
  → 触发 CommandCompleted 事件
  → COM 转发给 WTA
  → WTA 分类错误（exit code + 捕获的输出）
  → 如果面板打开 → 显示修复建议
  → 如果面板 stash → 静默准备建议，打开面板时立即可见
  → 如果面板未打开 → 标签页显示"AI 建议"指示器
```

OSC（Operating System Command）序列是终端标准的一部分，不需要额外的 IPC 通道——Shell 已经在输出这些信息，Terminal 只需要监听。

### 模式四：wtcli 让 Agent 控制终端

Agent 通过 shell out 调用 `wtcli` 来控制终端：

```rust
// wtcli 命令
wtcli list-panes                    // 列出所有面板
wtcli capture-pane --id 0           // 捕获面板 0 的内容
wtcli capture-pane --id 0 --last 50 // 只捕获最后 50 行
wtcli listen --events               // 监听终端事件
wtcli send-keys --pane 0 "ls\r"    // 向面板发送按键
wtcli focus-pane --id 1             // 切换焦点
wtcli new-pane --profile PowerShell // 创建新面板
```

wtcli 通过 `CoCreateInstance(CLSCTX_LOCAL_SERVER)` 连接到 COM 服务器，调用 `IProtocolServer` 接口。这形成了一个双向通道：
- Terminal → Agent：通过 OSC/ACP 推送事件
- Agent → Terminal：通过 wtcli/COM 执行操作

### 模式五：双维度会话路由

Intelligent Terminal 使用 `window_id` + `tab_id` 双维度路由 Agent 会话：

- **多窗口**：每个 WT 窗口有独立的 SharedWta 实例
- **多标签页**：每个标签页有独立的 wta-helper 和 ACP 会话
- **单 master**：每个 WT 窗口只有一个 wta-master 管理一个 Agent CLI 进程

这意味着一个窗口中所有标签页共享同一个 Agent 进程（节省内存），但每个标签页有独立的会话上下文（隔离对话）。

## 7. 错误自动检测流程（Autofix）

完整的自动错误检测到修复建议流程：

```
1. 用户在 PowerShell 中执行命令（失败）
   │
   ▼
2. PowerShell 发送 OSC 133;D;1 (exit_code=1)
   │
   ▼
3. TerminalPage 收到 OSC 序列，触发 CommandCompleted 事件
   │  同时捕获最后 N 行输出
   │
   ▼
4. TerminalPage 通过 COM 调用转发给 SharedWta
   │
   ▼
5. wta-master 接收事件，分类错误：
   │  - exit_code
   │  - 命令文本
   │  - 错误输出
   │  - CWD
   │
   ▼
6a. 如果 Agent 面板打开 → 发送 agent/suggest 到 helper
   │  → Agent 分析错误 → 流式返回修复建议
   │
   6b. 如果面板 stash/未打开 → 后台预取建议
      → helper 缓存建议
      → 标签页显示"有 AI 建议"指示器
      → 用户打开面板时显示预取的建议
```

## 关键收获

Intelligent Terminal 展示了桌面应用集成 Agent 的参考架构：

1. **进程隔离**：Agent 运行在独立进程（wta-master），通过 stdio/JSON-RPC 通信，崩溃不影响宿主
2. **预热+Stash**：解决 Agent 启动延迟和状态保留问题
3. **OSC 作为事件总线**：利用终端已有的 Shell 集成协议，不需要额外的轮询或 IPC
4. **双语言安全边界**：Rust 处理网络/协议（内存安全），C++ 处理 UI/渲染（复用代码）
5. **COM 作为通用集成面**：任何语言都可以通过 COM 与 Terminal 交互（wtcli 是 Rust 写的）
6. **ACP 标准化**：通过 ACP 协议，同一个 Agent CLI 可以在支持 ACP 的任何宿主中运行
7. **双维度路由**：窗口级单 Agent 进程 + 标签页级独立会话，兼顾内存效率和上下文隔离
8. **后台预取**：在用户打开面板前就准备好建议，消除感知延迟
