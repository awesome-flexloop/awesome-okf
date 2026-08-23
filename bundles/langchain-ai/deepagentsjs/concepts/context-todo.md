---
type: concept
scope: deepagentsjs
name: context-todo
version: "1.13.1"
source: https://github.com/langchain-ai/deepagentsjs
description: deepagentsjs 上下文管理与文件状态——摘要卸载、后端抽象、filesValue 状态归约、内存与技能系统
---

# 上下文与 Todo 管理

## 上下文管理挑战

长任务 agent 面临的核心问题是**上下文窗口有限**。随着多轮对话和工具调用积累，消息历史可能超出模型的 token 限制。deepagentsjs 通过多层机制管理上下文：

1. **自动摘要**：接近 token 限制时，将旧消息压缩为摘要
2. **历史卸载**：被摘要的消息持久化到后端文件系统
3. **工具结果驱逐**：过大的工具输出自动保存到文件，只保留预览
4. **子代理隔离**：独立任务在隔离的上下文中执行，不膨胀主对话

## 摘要中间件

`createSummarizationMiddleware` 扩展了 langchain 基础摘要中间件，增加了后端持久化能力。

### 触发与保留策略

通过 `ContextSize` 接口配置（`summarization.ts:83-88`）：

```typescript
interface ContextSize {
  type: "messages" | "tokens" | "fraction";
  value: number;
}
```

**默认值根据模型 profile 自动计算**（`summarization.ts:178-191`）：

| 场景 | trigger（触发摘要） | keep（保留） |
|---|---|---|
| 模型有 maxInputTokens profile | 0.85（85% 上下文） | 0.1（10%） |
| 无 profile（回退） | 170,000 tokens | 6 messages |

### 历史卸载

被摘要的消息以 Markdown 格式存储在 `/conversation_history/{thread_id}.md`（`summarization.ts:27`）。每次摘要事件追加新段落，形成所有被驱逐消息的运行日志。agent 后续可以通过 `read_file` 工具回溯历史。

### 工具参数截断

`TruncateArgsSettings`（`summarization.ts:93-117`）可配置旧消息中大型工具参数的截断：

- `trigger`：触发截断的阈值
- `keep`：保留策略（默认最后 20 条消息）
- `maxLength`：参数最大字符长度（默认 2000）
- `truncationText`：替换文本（默认 `"...(argument truncated)"`）

回退默认值：20 条消息触发截断，保留 20 条。

### 会话隔离

每个子代理获得独立的 `_summarizationSessionId`（格式 `session_{8位UUID}`，`subagents.ts:691`），确保摘要会话追踪不串扰。

## 文件状态管理（filesValue）

`filesValue`（`values.ts:34-40`）是 deepagentsjs 状态管理的核心抽象：

```typescript
export const filesValue = new ReducedValue(
  z.record(z.string(), FileDataSchema).default(() => ({})),
  {
    inputSchema: z.record(z.string(), FileDataSchema.nullable()).optional(),
    reducer: fileDataReducer,
  },
);
```

### 设计要点

- **Schema**：文件路径 → FileData 的记录，默认为空对象
- **输入允许 null**：null 值表示删除文件
- **自动归约**：`fileDataReducer` 合并并发更新，支持并行子代理安全写入
- **可复用**：类似 LangGraph 的 `messagesValue`，用户可在自定义 StateSchema 中直接使用

### FileData 格式

支持两种版本（`protocol.ts:119-146`）：

- **v1**（已废弃）：`content: string[]`（按行分割），仅文本
- **v2**（当前）：`content: string | Uint8Array`（文本或二进制），含 `mimeType`、`created_at`、`modified_at`

## 可插拔后端架构

所有文件操作通过 `BackendProtocolV2` 接口抽象，中间件通过 `resolveBackend` 获取实例。

### 内置后端

| 后端 | 存储位置 | 持久化范围 | 适用环境 |
|---|---|---|---|
| `StateBackend` | LangGraph agent state | 线程内（随 checkpoint） | 通用（默认） |
| `FilesystemBackend` | 本地文件系统 | 永久 | Node.js |
| `StoreBackend` | LangGraph BaseStore | 跨线程 | 通用 |
| `CompositeBackend` | 按前缀路由到多个后端 | 取决于子后端 | 通用 |
| `ContextHubBackend` | ContextHub 远程存储 | 远程 | 服务端 |
| `LocalShellBackend` | 本地 shell 执行 | 本地 | Node.js |
| `LangSmithSandbox` | LangSmith 沙箱环境 | 临时 | 云端 |

### StateBackend 的 Pregel 集成

StateBackend 在零参数构造模式下（`state.ts:94-144`），通过 LangGraph 内部通道读写状态：

- 读取：`getConfig().configurable.__pregel_read("files", true)`，fresh=true 确保应用待处理的写入
- 写入：`getConfig().configurable.__pregel_send([["files", update]])`，镜像 Python 版的 `CONFIG_KEY_SEND`

这使得文件操作无需返回 Command 对象即可更新状态，中间件代码更简洁。

### 后端工厂

中间件接受三种后端形式：
1. `AnyBackendProtocol` 实例
2. `BackendFactory` 工厂函数
3. `(config: { state, store? }) => StateBackend` 内联工厂

工厂模式使得同一个后端定义可以在不同执行上下文中实例化，每个请求获得独立实例。

## 文件系统中间件

`createFilesystemMiddleware` 注入8个工具（`fs.ts:100-109`）：

| 工具 | 功能 |
|---|---|
| `ls` | 列出目录内容（非递归） |
| `read_file` | 读取文件（支持分页 offset/limit，默认 100 行） |
| `write_file` | 写入文件 |
| `edit_file` | 字符串替换编辑文件 |
| `delete` | 删除文件 |
| `glob` | 文件名模式匹配 |
| `grep` | 文件内容正则搜索（默认最多 1000 匹配） |
| `execute` | 执行 shell 命令（沙箱环境） |

### 工具结果驱逐

当工具输出过大时，结果自动保存到文件系统，工具消息替换为包含文件路径和预览的提示（`fs.ts:166-177`）。驱逐排除 `execute` 以外的所有文件系统工具（`fs.ts:117-119`），因为这些工具已有内置截断或返回值很小。

### 二进制文件支持

read_file 支持二进制文件（图片、PDF、音频等），最大 10MB（`fs.ts:139`）。内容以 Base64 编码返回，MIME 类型自动检测。

### 参数名容错

`normalizeFilePathInput`（`fs.ts:54-65`）自动将 `path` 参数映射为 `file_path`，兼容不同能力水平的模型。

## 内存系统（AGENTS.md）

`createMemoryMiddleware` 实现了 [AGENTS.md 规范](https://agents.md/)，在 agent 启动时加载记忆文件并注入 system prompt。

### 工作方式

1. 从配置的 `sources` 路径数组按顺序读取 AGENTS.md 文件
2. 文件内容通过 `<agent_memory>` 标签包装注入 system prompt
3. 附带详细的记忆更新指南（何时保存、如何学习反馈）
4. 对于 Anthropic 模型，可添加 `cache_control: ephemeral` 断点启用提示缓存

### 与 agent-memory 的区别

`createAgentMemoryMiddleware`（`agent-memory.ts`）是**已废弃**的旧实现，直接使用 Node.js fs 模块访问文件系统，不可移植。新代码应使用 `createMemoryMiddleware`，它通过 BackendProtocol 抽象支持任意后端。

## 技能系统（Skills）

`createSkillsMiddleware` 实现了 Anthropic 的 [Agent Skills](https://agentskills.io/) 模式，支持渐进式披露。

### 核心概念

- **技能源**：后端中的路径，每个含 SKILL.md 的子目录被识别为一个技能
- **分层加载**：源按顺序加载，后加载的同名技能覆盖前者（last wins）
- **元数据约束**：技能名 1-64 字符（小写字母数字和连字符），描述 1-1024 字符
- **SKILL.md 限制**：最大 10MB，防止 DoS 攻击
- **模块入口**：支持 `.js`/`.ts`/`.jsx`/`.tsx` 等扩展名的可执行脚本

### 与 Memory 的区别

| 维度 | Memory（AGENTS.md） | Skills（SKILL.md） |
|---|---|---|
| 加载方式 | 启动时全部加载到 system prompt | 渐进式披露，按需加载 |
| 用途 | 持久上下文、偏好、项目说明 | 可复用的工作流、操作指南 |
| 结构 | 自由格式 Markdown | YAML frontmatter + Markdown 正文 |
| 更新 | agent 通过 edit_file 主动更新 | 通常由开发者预置 |

## 权限系统

`FilesystemPermission`（`permissions/types.ts:23-40`）提供文件操作的访问控制：

```typescript
interface FilesystemPermission {
  operations: readonly ("read" | "write")[];
  paths: string[];           // 绝对 glob 模式，必须以 / 开头
  mode?: "allow" | "deny";  // 默认 allow
}
```

- 规则按声明顺序求值，首次匹配优先
- 无匹配时默认允许（permissive default）
- 支持 `**`（任意深度）、`*`（单段内）、`{a,b}` 花括号展开
- 子代理可指定自己的权限（完全替换父代理权限，非合并）

## Todo 状态

Todo/规划功能通过 langchain 的 `todoListMiddleware` 提供，在 state 中添加 `todos` 字段。在 deepagentsjs 中：

- `todos` 被排除在子代理状态传递之外（`subagents.ts:51`），每个代理维护独立任务列表
- Codex harness profile 自动启用 todoListMiddleware（`openai-codex.ts:46`）
- 其他模型需通过 `middleware: [todoListMiddleware()]` 手动启用

## 相关阅读

- [总览](/langchain-ai/deepagentsjs/concepts/overview)
- [子代理与规划](/langchain-ai/deepagentsjs/concepts/subagent-planning)
- [API 参考](/langchain-ai/deepagentsjs/references/api)
