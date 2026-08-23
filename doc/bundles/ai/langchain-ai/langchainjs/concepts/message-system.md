---
type: concept
scope: langchainjs
name: message-system
version: "0.1.0"
source: https://github.com/langchain-ai/langchainjs
description: LangChain.js 消息系统——BaseMessage 类型层次、tool_call 一等公民与多模态内容块
---

# 消息系统

## 消息在 LLM 应用中的角色

消息（Message）是与聊天模型交互的基本数据单元。一次对话由一系列消息组成，每条消息有角色（role）和内容（content）。LangChain.js 将消息建模为强类型的类层次结构，而非简单的 `{ role, content }` 对象，以支持工具调用、多模态内容、使用量元数据等复杂场景。

## 类型层次

所有消息类继承自 `BaseMessage`，通过 `readonly type` 字面量类型区分角色：

```
BaseMessage (abstract)
├── HumanMessage      type = "human"    / HumanMessageChunk
├── SystemMessage     type = "system"   / SystemMessageChunk
├── AIMessage         type = "ai"       / AIMessageChunk
├── ToolMessage       type = "tool"     / ToolMessageChunk
└── ChatMessage       type = "chat"     / ChatMessageChunk (自定义角色)
```

每个具体消息类都有对应的 Chunk 类（如 `AIMessageChunk`），用于流式传输中的增量拼接，通过 `concat` 方法合并。

## BaseMessage

**源码位置**：`messages/base.ts`

```typescript
abstract class BaseMessage<TStructure, TRole extends MessageType> {
  content: MessageContent;
  additional_kwargs?: Record<string, unknown>;
  response_metadata?: Record<string, unknown>;
  id?: string;
  name?: string;
  abstract readonly type: MessageType;
}
```

### content：string 或内容块数组

`MessageContent = string | Array<ContentBlock>`（base.ts:52）。这是消息系统最重要的设计决策：

- **简单场景**使用纯字符串 content
- **多模态/工具调用场景**使用 ContentBlock 数组，每个块有 `type` 字段区分（text、image、tool_call、tool_result 等）

这种设计让简单场景保持简洁，复杂场景无需额外字段。

### additional_kwargs（已废弃）

早期版本中，模型 provider 特有的字段（如 OpenAI 的 tool_calls、function_call）存放在 `additional_kwargs` 中。当前版本已将 `tool_calls` 提升为 `AIMessage` 的一等字段，但 `additional_kwargs` 仍保留用于向后兼容。

### response_metadata

模型响应的元数据，如 token 使用量、模型名称、响应头、finish_reason 等。

## 各消息类型详解

### HumanMessage

**源码位置**：`messages/human.ts:18`

代表用户输入。最简单的消息类型：

```typescript
const msg = new HumanMessage("你好");
// 或
const msg = new HumanMessage({ content: "你好", name: "alice" });
```

也可以使用 `[role, content]` 元组形式，通过 `coerceMessageLikeToMessage` 转换：

```typescript
const msg = coerceMessageLikeToMessage(["human", "你好"]);
```

### SystemMessage

**源码位置**：`messages/system.ts:18`

代表系统指令，用于设定模型行为。提供 `concat` 方法支持字符串拼接：

```typescript
const sys = new SystemMessage("你是一个翻译助手");
const combined = sys.concat("将中文翻译为英文");
```

### AIMessage

**源码位置**：`messages/ai.ts:46`

代表模型响应，是功能最丰富的消息类型：

```typescript
class AIMessage extends BaseMessage {
  readonly type = "ai";
  tool_calls?: ToolCall[];
  invalid_tool_calls?: InvalidToolCall[];
  usage_metadata?: UsageMetadata;
}
```

**tool_calls** 是模型发起的工具调用请求，是 Agent 循环的核心。AIMessage 构造函数（ai.ts:68-126）会：
1. 检查 `additional_kwargs.tool_calls` 是否存在，若 `tool_calls` 未设置则调用 `defaultToolCallParser` 解析并发出弃用警告
2. 处理 `response_metadata.output_version === "v1"` 时将 content 转换为 contentBlocks
3. 将 tool_calls 作为 `tool_call` 类型的 ContentBlock 添加到 contentBlocks

**ToolCall 结构**（tool.ts:228）：

```typescript
interface ToolCall<TName = string, TArgs = Record<string, any>> {
  readonly type?: "tool_call";
  id?: string;
  name: TName;
  args: TArgs;
}
```

### ToolMessage

**源码位置**：`messages/tool.ts:53`

代表工具执行结果，通过 `tool_call_id` 与 AIMessage 的工具调用关联：

```typescript
class ToolMessage extends BaseMessage implements DirectToolOutput {
  readonly type = "tool";
  lc_direct_tool_output = true;
  tool_call_id: string;
  status?: "success" | "error";
  artifact?: any;
  metadata?: Record<string, unknown>;
}
```

关键设计：
- **`tool_call_id` 必填**，建立请求-响应关联，Agent 据此将工具结果匹配回对应的调用
- **`status`** 原生表达成功/失败，无需用异常控制流
- **`artifact`** 存放不发送给模型的完整工具输出（如文件内容），content 只放摘要
- **`DirectToolOutput`** 标记（`lc_direct_tool_output = true`）告诉框架此对象已是消息，无需自动包装

## 内容合并：mergeContent

**源码位置**：`messages/base.ts:110`

流式传输需要将多个 chunk 合并为完整消息。`mergeContent` 处理字符串与数组的所有组合：

| first | second | 结果 |
|---|---|---|
| string | string | 直接拼接 |
| string "" | any | 返回 second |
| string | array | 转为 text block 后追加 |
| array | array | 调用 `_mergeLists` 或展开合并 |
| any | string "" | 返回 first |

这是消息 Chunk 类 `concat` 方法的基础，确保流式 token 可以正确累积。

## 消息的序列化

所有消息继承 `Serializable`，具有跨语言序列化能力。`lc_aliases` 覆盖确保 snake_case 字段名（如 `tool_calls`、`tool_call_id`、`usage_metadata`）在序列化时保持与 Python 一致。

`StoredMessageData`（base.ts:23-34）定义了序列化后的存储格式：

```typescript
interface StoredMessageData {
  content: string;
  role: string | undefined;
  name: string | undefined;
  tool_call_id: string | undefined;
  additional_kwargs?: Record<string, any>;
  response_metadata?: Record<string, any>;
  id?: string;
}
```

## 消息在 Agent 循环中的流转

在 ReAct Agent 中，消息形成如下对话序列：

```
SystemMessage          → 设定角色和指令
HumanMessage           → 用户问题
AIMessage (tool_calls) → 模型决定调用工具
ToolMessage            → 工具执行结果
AIMessage (tool_calls) → 模型继续调用工具
ToolMessage            → 工具结果
AIMessage (content)    → 最终回答（无 tool_calls）
```

`AgentNode` 检测 AIMessage 是否包含 `tool_calls`：有则路由到 `ToolNode`，无则结束循环。`ToolNode` 为每个 tool_call 执行工具并生成对应的 `ToolMessage`（含匹配的 `tool_call_id`）。

## 相关文档

- [工具定义](/ai/langchain-ai/langchainjs/concepts/tool-definition) — 工具如何生成 ToolMessage
- [ReAct Agent](/ai/langchain-ai/langchainjs/concepts/react-agent) — 消息在 Agent 循环中的流转
- [Message 与 Tool API](/ai/langchain-ai/langchainjs/references/messages-tools) — 完整 API 参考
