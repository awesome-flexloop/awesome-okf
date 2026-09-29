---
type: spec
scope: openwork
name: insights
version: "0.1.0"
source: https://github.com/langchain-ai/openwork
description: openwork 深度洞察——架构设计决策与安全模型分析
---

# openwork 深度洞察

## 1. "桌面壳 + deepagents 内核"的分层架构

openwork 的本质是一个 **Electron 桌面 GUI 壳**，将 deepagentsjs 的深度代理能力包装为可视化交互界面。其架构呈现清晰的三层分离：

```
┌─────────────────────────────────────────────┐
│  Renderer（React 19 + Radix UI + Zustand）  │  ← 聊天、看板、文件面板、Todo
├─────────────────────────────────────────────┤
│  Preload（contextBridge IPC 桥）             │
├─────────────────────────────────────────────┤
│  Main Process                                │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐ │
│  │ Agent    │ │ Thread   │ │ Model/WS    │ │  ← IPC 处理器
│  │ Runtime  │ │ CRUD     │ │ Handlers    │ │
│  └────┬─────┘ └────┬─────┘ └─────────────┘ │
│       │            │                        │
│  ┌────▼────────────▼─────────────────────┐  │
│  │  deepagents (createDeepAgent)          │  │  ← 代理内核
│  │  ├─ LocalSandbox (fs + shell)          │  │
│  │  ├─ SqlJsSaver (LangGraph checkpoints) │  │
│  │  └─ LangGraph (streaming + HITL)       │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

关键设计决策：

- **代理逻辑零自研**：openwork 不实现代理推理、工具调用、规划循环，全部委托给 `deepagents` 包的 `createDeepAgent()`。自身代码聚焦于桌面体验——窗口管理、IPC 通信、流式渲染、工作区文件浏览、密钥存储。
- **sql.js 而非 better-sqlite3**：选择纯 JavaScript 的 sql.js（WebAssembly SQLite）而非原生模块，是为了规避 Electron 的原生模块编译问题（ABI 不兼容、node-gyp 构建链）。代价是数据库全量加载到内存、通过防抖批量写盘（100ms），以及 100MB 文件大小上限。这对单用户桌面应用的检查点场景是可接受的权衡。
- **每线程独立检查点文件**：与 LangGraph 常见的单库多线程模式不同，openwork 为每个对话线程创建独立的 SQLite 文件（`~/.openwork/threads/{threadId}.sqlite`），并在内存中缓存 `SqlJsSaver` 实例。这简化了线程删除（直接删文件）和隔离性，但意味着长对话会累积多个内存数据库实例。
- **双流模式**：IPC 层同时使用 `streamMode: ["messages", "values"]`——messages 模式提供逐 token 的实时流（用于打字机效果），values 模式提供完整状态快照（todos、文件、子代理）。渲染进程收到原始 `[mode, data]` 元组后自行解析分类。

## 2. 安全模型：HITL 审批作为唯一沙箱边界

openwork 的安全设计极为直白——**LocalSandbox 没有内置沙箱隔离**，代理直接在用户机器上执行 shell 命令和文件操作。安全边界完全依赖 human-in-the-loop（HITL）审批：

- `createDeepAgent` 配置 `interruptOn: { execute: true }`，所有 shell 命令在执行前中断，等待用户 approve/reject/edit。
- 文件操作（read/write/edit/ls/glob/grep）**不触发中断**——代理可直接读写工作区内的文件。
- 工作区路径遍历防护仅存在于渲染进程的 IPC 文件读取接口（`resolvedPath.startsWith(resolvedWorkspace)`），代理自身通过 deepagents 的 `FilesystemBackend` 操作文件时，`virtualMode: false` 使用绝对路径，没有额外的路径沙箱。
- README 顶部用 `> [!CAUTION]` 块明确警告："openwork gives AI agents direct access to your filesystem and the ability to execute shell commands."

这一设计体现了 deepagents 生态的理念：**信任用户对自身工作区的控制能力**，将安全决策交给人类判断而非技术沙箱。与沙箱化方案（如 Docker 容器、微虚拟机）相比，这种方式零配置开销、完全透明，但要求用户具备审查命令的能力。系统提示词中专门有"HITL Tool Approval"章节，指导代理在被拒绝后不得重试相同命令。
