---
type: Concept
title: Agent 编排引擎
description: @zleap/agent 包的 L2 编排层架构——ConversationService 对话服务、ChatEngine 执行引擎、Workspace 管线、Turn Loop 模型推理循环、内置工具集、MCP 运行时、记忆梦境整理与对话压缩机制。
tags: [zleap-agent, agent, orchestration, conversation, chat-engine, workspace, turn-loop, mcp, moa]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: agent-conversation
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/agent/src/conversation/service.ts
    title: ConversationService L2对话服务
  - id: agent-engine
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/agent/src/engine/index.ts
    title: ChatEngine 执行引擎
  - id: agent-tools
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/agent/src/tools.ts
    title: 内置工具集
  - id: agent-kernel
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/agent/src/kernel/kernel.ts
    title: Agent 内核
  - id: agent-mcp
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/agent/src/mcpRuntime.ts
    title: MCP 运行时
  - id: agent-soul
    resource: ../../../../../../external/libs/models/ai/Zleap-Agent/packages/agent/src/soul.ts
    title: Agent 人格配置
---

# Agent 编排引擎

@zleap/agent 是 Zleap-Agent 的核心业务引擎包，在 @zleap/core 的 Fiber 运行时之上构建了完整的 L2 编排层。它提供对话管理、模型推理循环（Turn Loop）、Workspace 管线、内置工具集、MCP 协议支持、记忆整理和对话压缩等能力，是 CLI/Web/Gateway/Tasks 所有入口共享的执行引擎。

## 分层架构

Agent 包在 Core 之上形成三层编排结构：

```
┌─────────────────────────────────────────────────────────────────────┐
│  L2 对话层 (Conversation)                                            │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ ConversationService                                          │   │
│  │  · 会话互斥 (KeyedMutex)                                      │   │
│  │  · 全局并发信号量 (Semaphore)                                  │   │
│  │  · 引擎缓存 (LRU, maxEngines=256)                             │   │
│  │  · 斜杠命令拦截 (/stop, /new, /model ...)                     │   │
│  │  · 历史加载/持久化                                            │   │
│  │  · 出站消息注册 (OutboundSenderRegistry)                      │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                             │                                        │
├─────────────────────────────┼────────────────────────────────────────┤
│  L1 引擎层 (Engine + Kernel)                                        │
│  ┌──────────────────────────▼───────────────────────────────────┐   │
│  │ ChatEngine                                                   │   │
│  │  · 上下文组装 (assembleContext)                               │   │
│  │  · Workspace 管线调度                                         │   │
│  │  · Turn Loop (模型推理↔工具调用循环)                           │   │
│  │  · 记忆编排 (MemoryOrchestrator)                              │   │
│  │  · 对话压缩 (CompactionService)                               │   │
│  │  · 运行时缓存 (RuntimeCacheManager)                           │   │
│  │  · MCP 工具注入                                               │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                             │                                        │
├─────────────────────────────┼────────────────────────────────────────┤
│  L0 核心层 (Core Runtime)                                            │
│  ┌──────────────────────────▼───────────────────────────────────┐   │
│  │ AgentRuntime (Run→Work→WorkStep Fiber)                       │   │
│  │  · 8 个注册中心 + 事件总线 + 钩子                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## ConversationService — L2 对话服务

ConversationService 是所有触发入口（Web/IM Gateway/定时任务）的统一调用点。它管理会话级别的互斥、并发控制、引擎生命周期和命令处理。

### 核心依赖与配置

```typescript
// conversation/service.ts L68-L92
export type ConversationServiceDeps = {
  store: ZleapStore | null;              // 共享持久化存储（PG 连接池）
  persistence?: PersistenceConfig;       // store=null 时的降级持久化
  resolveModel?: ModelResolver;          // 模型解析策略
  resolveActor?: ActorResolver;          // 身份映射策略
  avatarId?: string;                     // 默认 Avatar/Agent ID
  systemPrompt?: string;                 // 基础系统提示
  senders?: OutboundSenderRegistry;      // 出站消息发送器
  maxConcurrent?: number;                // 全局并发上限（0=不限制）
  maxEngines?: number;                   // 引擎缓存上限（默认 256）
};
```

### 会话级互斥与并发控制

ConversationService 使用 KeyedMutex 确保同一会话的 "load→run→persist" 序列不被并发打断，同时使用 Semaphore 控制全局跨会话并发：

```typescript
// conversation/service.ts L153-L154
private readonly mutex = new KeyedMutex();
private readonly semaphore: Semaphore;
```

- **KeyedMutex**：按 `threadId(channel, conversationId)` 加锁，确保同一聊天不会并发执行两次 run
- **Semaphore**：`maxConcurrent` 控制全局 agent-run 并发数，防止 LLM API 过载
- **AbortController 追踪**：`activeRuns` Map 允许 `/stop` 命令带外中止正在执行的 run

### 消息处理流程

`handle()` 方法是 ConversationService 的核心入口，以 AsyncGenerator 方式流式输出 ChatDelta：

```typescript
// conversation/service.ts L188-L200（简化）
async *handle(inbound: InboundMessage, opts: HandleOptions = {}): AsyncIterable<ChatDelta> {
  const actor = this.resolveActorFn(inbound);
  const { channel, conversationId } = inbound;
  const baseThreadId = threadIdOf(channel, conversationId);
  const commandsEnabled = opts.handleCommands ?? (inbound.kind !== 'schedule');

  // /stop 绕过互斥锁直接中止
  if (commandsEnabled && isStopCommand(inbound.text)) {
    const running = this.activeRuns.get(baseThreadId);
    if (running) {
      running.abort();
      yield { type: 'delta', text: '已请求中止当前回复。' };
    }
    return;
  }
  // ...后续流程：加锁→历史加载→引擎获取/创建→执行→流式输出
}
```

### 历史纪元（Epoch）机制

为支持 `/new` 命令开启新对话而不丢失历史记录，ConversationService 实现了纪元分隔机制：

```typescript
// conversation/service.ts L126-L136
const EPOCH_SEPARATOR = '.e';

export function epochConversationId(conversationId: string, epoch: number): string {
  return epoch > 0 ? `${conversationId}${EPOCH_SEPARATOR}${epoch}` : conversationId;
}
```

纪元 ID 通过 `.e{N}` 后缀附加到 conversationId 上，分隔符选择 `[\w:.-]` 安全字符集以兼容存储层 sanitizeId。

## ChatEngine — L1 执行引擎

ChatEngine 是 Agent 包中最核心的类，负责单次对话 run 的完整生命周期。它在 engine/index.ts 中实现，整合了上下文组装、Workspace 调度、Turn Loop、记忆管理、MCP 工具注入等所有子系统。

### 引擎常量与阈值

ChatEngine 定义了大量调优常量来控制上下文窗口管理、记忆抽取、压缩等行为：

```typescript
// engine/index.ts L150-L191
const EVENT_REFRESH_TRIGGER_MESSAGES = 30;        // 30 条消息触发事件刷新
const EVENT_REFRESH_TRIGGER_TOKENS = 10_000;      // 10K tokens 触发事件刷新
const COMPACT_KEEP_RECENT_TOKENS = 1_000;         // 压缩保留最近 1K tokens
const RECALL_LIMIT = 10;                          // 记忆召回上限
const RECALL_MIN_SCORE = 0.15;                    // 记忆相似度阈值
const WORKSPACE_HANDOFF_MAX_DEPTH = 4;            // Workspace 切换最大深度
const DREAM_EXTRACT_MAX_CHARS = 24_000;           // 梦境整理最大输入字符
```

### 系统提示组装

ChatEngine 通过 XML 标签分段组装系统提示词，每段对应一个 MainSystemSection：

```typescript
// engine/index.ts L246-L258
type MainSystemSection = {
  sub: ContextBlockSub;
  promptLabel: string;    // XML 标签名（role/project_context/time/memory_rules/...）
  label: string;          // UI 显示标签
  storage: string;
  meaning: string;
  line?: 'A' | 'B';      // A线=人笔记 / B线=事件图记忆
  text: string;
  items?: ContextBlockItem[];
  count?: number;
};
```

系统提示段落通过 `<role>`、`<project_context>`、`<time>`、`<main_space>`、`<memory_rules>`、`<available_workspaces>`、`<skill_index>` 等 XML 标签组织，每个段落的内容和顺序在 UI 的上下文检查器中一一对应，确保展示与实际发送给模型的内容一致。

### 工具集层次

ChatEngine 为每个 Workspace 构建分层工具集：

```
┌──────────────────────────────────────────────────────┐
│  工具集层次                                           │
│                                                      │
│  SESSION_ONLY_TOOLS (仅 Main Space)                   │
│  ├─ switchWorkspace — 切换到其他 Workspace            │
│  └─ task_manage — 定时任务 CRUD                       │
│                                                      │
│  DEFAULT_WORKSPACE_TOOLS (所有 Workspace)             │
│  ├─ get_time — 获取时间                               │
│  └─ readMessage — 读取原始消息                        │
│                                                      │
│  MEMORY_PLUGIN_TOOLS (记忆插件)                       │
│  ├─ remember — 写入记忆                               │
│  └─ recall — 检索记忆                                 │
│                                                      │
│  BUILTIN_TOOLS (@zleap/agent/tools.ts)               │
│  ├─ ls / read / write / edit / bash ...              │
│                                                      │
│  MCP_TOOLS (MCP 服务器动态注入)                       │
│  └─ MCP 服务器声明的工具                               │
│                                                      │
│  SKILL_TOOLS (Skill 包附带的工具)                     │
│  └─ 技能包中声明的可执行脚本/引用                      │
└──────────────────────────────────────────────────────┘
```

高风险工具（bash/write/append/edit）标记为 `DENIED_WITHOUT_HITL`，在无交互式审批界面的渠道（IM Gateway/定时任务）中默认被拒绝。

## Workspace 管线

Workspace 是 Zleap-Agent 的任务空间抽象，每个 Workspace 是一个独立的 Handler 函数，接收 WorkContext 并返回 Artifact。ChatEngine 管理 Main Space 与其他 Workspace 的切换和协作。

### 默认 Workspace

- **Main Space**（`main`/`CANONICAL_MAIN_SPACE_ID`）：默认对话空间，包含 switchWorkspace、task_manage 等控制工具
- **FALLBACK_WORKSPACE_ID**：兜底空间，当指定空间不存在时使用

### Workspace 切换

模型通过 `switchWorkspace` 工具发起 Workspace 切换，形成 Mixture-of-Agents (MoA) 风格的协作模式：

```
用户消息
    │
    ▼
┌────────┐  switchWorkspace(task="写代码", space="coding")  ┌────────┐
│  Main  │───────────────────────────────────────────────▶│ coding │
│ Space  │◀─────────── Artifact(代码结果) ────────────────│ Space  │
└────────│                                                 └────────┘
    │
    ▼
  整合回复 → 用户
```

Workspace 切换有最大深度限制 `WORKSPACE_HANDOFF_MAX_DEPTH = 4`，防止无限递归委派。

### WorkspaceHandler 签名

```typescript
// types.ts L519
export type WorkSpaceHandler = (
  context: WorkContext,
  signal: AbortSignal
) => Promise<Omit<Artifact, 'id' | 'workspaceId' | 'createdAt'>>;
```

Handler 返回 draft Artifact（不含 id/workspaceId/createdAt），运行时自动补充这些字段。

## Turn Loop — 模型推理循环

Turn Loop 是 Agent 与 LLM 交互的核心循环：模型输出文本/工具调用 → 执行工具 → 将结果返回模型 → 模型继续输出，直到模型产出最终回复或达到工具调用上限。

### Turn Loop 核心接口

```typescript
// workspace-turn/turnLoop.ts L16-L18
export type WorkspaceTurnRuntime<TResult extends WorkspaceTurnResult = WorkspaceTurnResult> = {
  runModelTurn(input: WorkspaceTurnInput): Promise<TResult>;
};
```

```typescript
// workspace-turn/turnLoop.ts L20-L29
export async function runWorkspaceTurn<TResult extends WorkspaceTurnResult>(
  runtime: WorkspaceTurnRuntime<TResult>,
  input: WorkspaceTurnInput,
): Promise<TResult> {
  const result = await runtime.runModelTurn(input);
  if (workspaceTurnHitToolLimit(result.toolCallCount, input.maxToolCalls)) {
    return { ...result, stopReason: 'max-tool-calls' };
  }
  return result;
}
```

### Turn 停止原因

```typescript
// workspace-turn/turnLoop.ts L1
export type WorkspaceTurnStopReason = 'completed' | 'max-tool-calls' | 'model-stopped';
```

- `completed`：模型产出最终文本回复（无更多工具调用）
- `max-tool-calls`：达到 `maxToolCalls` 上限，防止无限工具调用循环
- `model-stopped`：模型主动停止（length/finish_reason 等）

### WorkspaceDelta 实时流

在 Turn Loop 执行期间，Handler 通过 `emit()` 函数实时推送进度事件：

```typescript
// types.ts L493-L500
export type WorkspaceDelta =
  | { kind: 'text'; text: string }                                    // 流式文本
  | { kind: 'tool'; name: string; phase: 'start' | 'end'; detail: string; isError?: boolean; toolCallId?: string }
  | { kind: 'approval'; status: 'needs_approval' | 'approved'; ... }  // HITL 审批
  | ProviderLifecycleDelta                                            // Provider 生命周期
  | TurnLifecycleDelta;                                               // Turn 开始/结束
```

Delta 事件通过 fire-and-forget 方式发射到事件总线，CLI TUI 和 Web UI 通过观察事件实现实时渲染。

## 内置工具集

@zleap/agent/tools.ts 定义了完整的内置工具集（~1150 行），涵盖文件系统操作、命令执行、网络请求等基础能力。

### 工具分类

| 类别 | 工具 ID | 能力 | HITL 要求 |
|------|---------|------|----------|
| 文件系统 | `ls` | 列出目录内容 | 无 |
| 文件系统 | `read` | 读取文件内容 | 无 |
| 文件系统 | `write` | 写入文件 | 需要审批 |
| 文件系统 | `edit` | 编辑文件 | 需要审批 |
| 文件系统 | `append` | 追加写入 | 需要审批 |
| 命令执行 | `bash` | 执行 shell 命令 | 需要审批 |
| 时间 | `get_time` | 获取当前时间 | 无 |
| 会话控制 | `switchWorkspace` | 切换工作空间 | 无 |
| 会话控制 | `readMessage` | 读取历史消息 | 无 |
| 任务管理 | `task_manage` | 定时任务 CRUD | 无 |
| 记忆 | `remember`/`recall` | 记忆读写 | 无 |
| 技能发现 | `findSkill` | 搜索本地技能 | 无 |

每个工具都遵循 `ToolDefinition` 接口，包含 id、description、parameters（JSON Schema）、handler、promptSnippet 等字段。

## MCP 运行时

MCP（Model Context Protocol）支持允许 Agent 动态连接外部工具服务器。

```typescript
// agent/src/index.ts L12
export { createMcpRuntimeTool, mcpRuntimeToolId, type McpToolExecutor } from './mcpRuntime.js';
```

MCP 运行时管理 MCP 服务器的连接、工具发现和调用：

- **MCP 服务器连接**：通过 stdio 或 SSE 连接外部 MCP 服务器
- **密钥处理**：`mcpSecrets.ts` 管理 MCP 服务器的认证凭据
- **SDK 执行器**：`sdkMcpExecutor.ts` 提供基于 MCP SDK 的工具执行器
- **配置安全存储**：MCP 配置通过 `sanitizeMcpConfigForStorage()` 过滤敏感字段后存入数据库

MCP 工具在 ChatEngine 初始化时被动态注入到 Workspace 的可用工具列表中。

## 记忆系统

Agent 包实现了双层记忆架构，通过 MemoryOrchestrator 协调：

### A/B 双线记忆

- **A 线**：`agent_memory` 存储对人的印象笔记（impression/experience kind），通过 `AgentNoteStore` 管理
- **B 线**：Core 事件图引擎（source/event/entity 五表），存储通用事件记忆，支持向量+词法+实体+图多路召回融合（RRF 排序）

### 记忆梦境整理（Memory Dream）

```typescript
// agent/src/memoryDream.ts
// 记忆"梦境"整理功能
```

`runLazyMemoryDream()` 在会话空闲时后台运行，将会话片段抽取为结构化的 event/entity 记忆。阈值控制：

- 最大输入字符：`DREAM_EXTRACT_MAX_CHARS = 24,000`
- 最大输出 tokens：`DREAM_EXTRACT_MAX_OUTPUT_TOKENS = 1,800`

### 事件抽取管线

当对话达到 `EVENT_REFRESH_TRIGGER_MESSAGES=30` 条或 `EVENT_REFRESH_TRIGGER_TOKENS=10,000` tokens 时，引擎触发事件抽取，将旧消息折叠为持久化 event/entity：

- 抽取窗口：最近 `EVENT_REFRESH_KEEP_RECENT=5` 条消息保留，更旧的消息经 LLM 抽取后持久化
- 调和决策：`reconciler` 对重复记忆做出 `skip/keep_both/replace_old/keep_old` 四种决策

## 对话压缩（Compaction）

CompactionService 负责对话历史的压缩，防止上下文窗口溢出：

```typescript
// agent/src/compaction/service.ts
export class CompactionService {
  // 对话压缩和摘要生成
}
```

触发条件与参数：
- `COMPACT_KEEP_RECENT_TOKENS = 1,000`：压缩后保留最近 1K tokens
- `COMPACT_RECENT_CONTEXT_RATIO = 0.08`：近期上下文比例
- Workspace 摘要：`WORKSPACE_SUMMARY_MAX_OUTPUT_TOKENS = 1,800`

压缩通过 LLM 生成对话摘要，将旧消息替换为摘要条目，同时保留工具调用的关键信息。

## Kernel 内核

`kernel/kernel.ts` 实现 Agent 的核心内核逻辑，是 ChatEngine 与底层 AgentRuntime 之间的桥梁，负责 Provider 调用编排、消息格式转换和工具结果处理。

## SOUL 人格系统

`soul.ts` 定义 Agent 的基础人格配置 `SOUL`，并通过 `composeSystemPersona()` 将 Avatar 配置与基础人格合成最终的系统角色设定：

```typescript
// agent/src/soul.ts
export const SOUL = /* 基础人格提示词 */;
export function composeSystemPersona(avatarConfig?, customInstructions?) {
  // 合成 Avatar 人格 + 自定义指令
}
```

## 权限模式

Agent 的权限系统通过 `permissions.ts` 定义，与 Gateway 的 `GatewayPermissionMode` 协作：

- **request_approval**（默认安全模式）：自动批准无风险工具，需要 HITL 的工具在无交互界面时拒绝
- **full_access**：自动批准所有工具调用

无风险工具自动批准列表由 `shouldAutoApproveToolWithoutHitl()` 决定，高风险工具（bash/write/edit/append）在 IM 渠道默认被拒绝。

## 出站消息

OutboundSenderRegistry 管理多渠道消息发送，Gateway 的 PlatformAdapter 和 Web 的 SSE 推送都通过这个注册器实现 deliver 动作的统一分发。

## 相关概念

- [Fiber 执行生命周期](fiber-lifecycle.md) — Run→Work→WorkStep 三级状态机
- [AI 抽象层](ai-abstraction.md) — ProviderAdapter 接口与流式推理
- [状态持久化存储](store-persistence.md) — PgStore 与 A/B 双线记忆存储
- [Gateway 网关服务](gateway-server.md) — IM 渠道如何调用 ConversationService
- [Avatar 人格系统](avatar-persona.md) — Avatar 输入组装与人格配置
- [任务调度系统](tasks-scheduling.md) — 定时任务如何触发 Agent 执行
