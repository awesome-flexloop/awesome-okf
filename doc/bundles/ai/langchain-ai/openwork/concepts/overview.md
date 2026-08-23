---
type: concept
scope: openwork
name: overview
version: "0.1.0"
source: https://github.com/langchain-ai/openwork
description: openwork 总览——基于 deepagentsjs 的桌面 AI 代理界面
---

# openwork 总览

## 什么是 openwork

openwork 是 LangChain 团队开发的桌面应用，为 [deepagentsjs](https://github.com/langchain-ai/deepagentsjs) 提供图形化交互界面。deepagentsjs 是一个"有主见的"深度代理构建框架，内置文件系统操作、任务规划和子代理委派能力。openwork 将这些能力包装为 Electron 桌面应用，使用户可以通过聊天界面驱动 AI 代理在本地工作区中执行编码、研究和分析任务。

- **版本**：0.1.0
- **作者**：LangChain
- **许可证**：MIT
- **运行时**：Electron + Node.js >= 18
- **核心依赖**：deepagents、LangGraph、LangChain

## 解决的问题

deepagentsjs 作为一个 TypeScript 代理框架，本身只提供命令行或编程接口。openwork 填补了以下空白：

1. **可视化交互**：提供聊天界面、流式 token 渲染、工具调用展示、Todo 列表和子代理看板。
2. **多模型管理**：统一配置 Anthropic Claude、OpenAI GPT、Google Gemini 三大提供商的 20+ 个模型，API 密钥本地加密存储。
3. **工作区集成**：将代理的文件系统操作可视化，提供文件树、代码查看器（含语法高亮）、图片/PDF 预览。
4. **对话持久化**：基于 LangGraph checkpointer 的线程级状态持久化，支持中断恢复和历史回溯。
5. **HITL 审批**：所有 shell 命令执行前需用户批准，支持 approve/reject/edit 三种决策。

## 核心机制

### 代理创建与流式调用

```
用户发送消息
      │
      ▼
ipcMain: agent:invoke
      │
      ▼
createAgentRuntime({ threadId, workspacePath, modelId })
      │
      ├─ getModelInstance()     → ChatAnthropic / ChatOpenAI / ChatGoogleGenerativeAI
      ├─ getCheckpointer()      → SqlJsSaver (per-thread SQLite)
      ├─ new LocalSandbox()     → FilesystemBackend + shell execute
      └─ createDeepAgent()      → deepagents 内核
      │
      ▼
agent.stream(input, { streamMode: ["messages", "values"] })
      │
      ├─ "messages" mode  → 逐 token 流式文本
      └─ "values" mode    → 完整状态（todos、files、subagents）
      │
      ▼
IPC channel: agent:stream:{threadId}
      │
      ▼
渲染进程 Zustand store → React 组件渲染
```

### 人机协作（HITL）

代理执行 shell 命令时，deepagents 的 HITL 中间件触发中断：

1. 流事件 `interrupt` 发送到渲染进程，展示命令详情。
2. 用户选择 **approve**（批准）、**reject**（拒绝）或 **edit**（编辑参数）。
3. 渲染进程通过 `agent:interrupt` IPC 发送决策。
4. 主进程使用 `Command({ resume: { decisions: [{ type: decisionType }] } })` 从检查点恢复执行。

### 每线程检查点

每个对话线程拥有独立的 SQLite 检查点文件（`~/.openwork/threads/{threadId}.sqlite`），由 `SqlJsSaver` 管理。这种设计：

- 实现线程级状态隔离
- 删除线程时直接删除文件即可清理
- 支持通过 `checkpointer.list()` 获取历史检查点（限制 50 条）

### 本地沙箱

`LocalSandbox` 继承 deepagents 的 `FilesystemBackend`，在其文件操作能力基础上增加 `execute()` 方法：

- **文件工具**：ls、read_file、write_file、edit_file、glob、grep（继承自父类）
- **Shell 工具**：execute（在工作区目录执行命令，2 分钟超时，100KB 输出限制）
- **路径模式**：`virtualMode: false`，使用绝对系统路径

## 架构概览

```
openwork/
├── bin/cli.js                 # CLI 启动器（npx openwork）
├── src/
│   ├── main/                  # Electron 主进程
│   │   ├── index.ts           # 应用入口、窗口创建
│   │   ├── types.ts           # 主进程类型定义
│   │   ├── storage.ts         # 数据目录与密钥管理
│   │   ├── agent/
│   │   │   ├── runtime.ts     # 代理运行时创建
│   │   │   ├── local-sandbox.ts  # 本地 shell 执行
│   │   │   └── system-prompt.ts # 基础系统提示词
│   │   ├── ipc/
│   │   │   ├── agent.ts       # 代理 IPC（invoke/resume/interrupt/cancel）
│   │   │   ├── threads.ts     # 线程 CRUD IPC
│   │   │   └── models.ts      # 模型与工作区 IPC
│   │   ├── db/index.ts        # 应用数据库（threads/runs/assistants）
│   │   ├── checkpointer/
│   │   │   └── sqljs-saver.ts # LangGraph SQLite 检查点
│   │   └── services/
│   │       ├── title-generator.ts
│   │       └── workspace-watcher.ts
│   ├── preload/               # contextBridge IPC 桥
│   └── renderer/              # React 19 + Radix UI + Tailwind 4
│       └── src/
│           ├── components/    # chat、kanban、panels、tabs、sidebar、ui
│           └── lib/           # store、electron-transport、utils
└── package.json
```

## 支持的模型

| 提供商 | 模型 |
|---|---|
| Anthropic | Claude Opus 4.5、Sonnet 4.5、Haiku 4.5、Opus 4.1、Sonnet 4 |
| OpenAI | GPT-5.2、GPT-5.1、o3、o3 Mini、o4 Mini、o1、GPT-4.1、GPT-4o |
| Google | Gemini 3 Pro/Flash Preview、Gemini 2.5 Pro/Flash/Flash Lite |

默认模型为 Claude Sonnet 4.5（`claude-sonnet-4-5-20250929`）。

## 安全提示

openwork 赋予 AI 代理直接访问文件系统和执行 shell 命令的能力。安全边界完全依赖用户审批——所有 shell 命令在执行前需人工确认。建议仅在受信任的工作区中运行。

详见 [信源登记](/ai/langchain-ai/openwork/references/source-registry) 和 [事实清单](/ai/langchain-ai/openwork/spec/facts)。
