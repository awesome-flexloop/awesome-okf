---
type: concept
scope: deepagents
name: todo-context
version: "0.7.8"
source: https://github.com/langchain-ai/deepagents
description: Deep Agents 上下文管理——摘要压缩、消息卸载、技能、内存与 DeltaChannel 检查点优化
---

# Todo 与上下文管理

长周期代理面临的核心挑战是上下文窗口有限。Deep Agents 通过多层机制管理上下文：自动摘要压缩、工具输出卸载、技能按需加载、内存持久注入，以及检查点增量存储。

## 摘要压缩（Summarization）

### 自动压缩：SummarizationMiddleware

当 token 使用量超过可配置阈值时，`SummarizationMiddleware` 自动压缩对话：

1. 计数当前消息的 token 数
2. 超过阈值时，用 LLM 摘要旧消息
3. 完整历史卸载到后端存储
4. 摘要替换上下文中的旧消息

关键配置：

- `trigger=("fraction", 0.85)`：当 token 使用达到上下文窗口的85%时触发
- `keep=("fraction", 0.10)`：保留最近10%的消息不压缩

### 按需压缩：SummarizationToolMiddleware

暴露 `compact_conversation` 工具，让代理（或人工审批流程）按需触发压缩。它组合 `SummarizationMiddleware` 实例并复用其摘要引擎。

### 存储格式

卸载的消息存储为 Markdown 文件：

```
/conversation_history/{session_id}.md
```

每次摘要事件向该文件追加新章节，创建所有被驱逐消息的运行日志。Base64 媒体（图片等）单独写入：

```
<artifacts_root>/conversation_history/media/{hash}.{ext}
```

Markdown 中通过 XML 引用标签引用：

```xml
<image url="/conversation_history/media/abc123.png" />
```

### 摘要提示

`DEEPAGENTS_DEFAULT_SUMMARY_PROMPT` 在 LangChain 的 `DEFAULT_SUMMARY_PROMPT` 基础上插入媒体引用说明，位于 `<messages>` 标记之前。这段 addendum 告诉摘要模型：

- 媒体引用标签表示原始消息包含保存在后端路径的媒体
- 将标签和路径视为对话上下文的一部分
- 不要从周围文本推断不可用的视觉细节
- 媒体对未来上下文重要时，在摘要中保留引用
- 消费摘要的模型可通过 `read_file` 检查引用路径的媒体

### 溢出裁剪

`_overflow_clip` 和 `_aclip_overflow_tail`（同步/异步版本）处理上下文溢出时的尾部裁剪，作为摘要压缩的补充安全网。

## 工具消息卸载

大型工具输出（如读取大文件、grep 搜索结果）会快速消耗上下文。`_message_eviction` 模块提供：

- `_offload_tool_message_content()` / `_aoffload_tool_message_content()`：将大工具消息内容写入后端，用内容预览替换
- `_create_content_preview()`：创建截断预览
- `_extract_text_from_message()`：从消息中提取文本
- `TOO_LARGE_TOOL_MSG`：过大工具消息的标记常量

这确保代理不会因单个巨大工具输出而耗尽上下文窗口。

## 技能系统（Skills）

技能是代理可按需加载的可复用行为，实现 Anthropic 的 Agent Skills 模式（渐进式披露）。

### 技能结构

```
/skills/user/web-research/
├── SKILL.md          # 必需：YAML frontmatter + Markdown 指令
└── helper.py         # 可选：支持文件
```

SKILL.md 格式：

```markdown
---
name: web-research
description: Structured approach to conducting thorough web research
license: MIT
---

# Web Research Skill

## When to Use
- User asks you to research a topic
...
```

### 元数据字段

- `name`：技能标识符（最大64字符，小写字母数字和连字符）
- `description`：技能描述（最大1024字符）
- `path`：后端中 SKILL.md 的路径
- 可选：`license`、`compatibility`、`metadata`、`allowed_tools`

### 源与分层

技能从一个或多个源加载，源是后端中技能目录的路径：

```python
skills=["/skills/user/", "/skills/project/"]
```

源按顺序加载，同名技能后加载者覆盖前者（last one wins），支持分层：base → user → project → team skills。

源可以是裸路径或 `(path, label)` 元组。裸路径的标签从最后一个路径组件派生（如 `/skills/user/` → `User`）。

### 与中间件的关系

`SkillsMiddleware` 仅在 `skills` 参数提供时添加到中间件栈。它通过后端 API 加载技能索引（不直接访问文件系统），在每次模型调用时将技能索引注入系统提示，使模型知道有哪些技能可用。技能的完整内容按需加载。

## 内存系统（Memory）

内存提供始终加载的持久上下文，与技能（按需工作流）形成对比。

### AGENTS.md 规范

`MemoryMiddleware` 实现 [AGENTS.md 规范](https://agents.md/)，从可配置源加载内存文件并注入系统提示：

```python
memory=["/memory/AGENTS.md", "~/.deepagents/AGENTS.md"]
```

### 加载行为

- 多个源按顺序加载并拼接，后出现的源位于组合提示后面
- HTML 注释（`<!-- ... -->`）在注入前被剥离，可用于创作笔记或机器管理标记
- 显示名称从路径自动派生
- 内存在代理启动时加载并添加到系统提示

### 与技能的对比

| 维度 | 技能（Skills） | 内存（Memory） |
|---|---|---|
| 加载时机 | 按需（模型决定使用时） | 始终加载（启动时） |
| 用途 | 可复用工作流和过程 | 项目上下文和指令 |
| 内容 | SKILL.md + 支持文件 | AGENTS.md 文件 |
| 注入方式 | 技能索引注入提示，内容按需读取 | 完整内容注入系统提示 |

## Todo 管理

Todo 列表功能由 LangChain 的 `TodoListMiddleware` 提供（非 Deep Agents 自定义中间件）。在 `create_deep_agent()` 中，该中间件的系统提示被特意设为空字符串 `system_prompt=""` 以精简输出——因为工具使用指导散文与工具自身的 schema 描述重复。

Todo 状态存储在 LangGraph 状态的 `todos` 键中。子代理调用时，`todos` 被排除在状态传播之外（`_EXCLUDED_STATE_KEYS`），因为它没有定义的 reducer，且从子代理返回 todos 给主代理没有明确语义。

## DeltaChannel 检查点优化

`DeepAgentState` 的核心优化是 `messages` 字段的 `DeltaChannel`：

```python
class DeepAgentState(AgentState):
    messages: Required[Annotated[
        list[AnyMessage],
        DeltaChannel(_messages_delta_reducer, snapshot_frequency=50)
    ]]
```

### 问题

标准 LangGraph 检查点在每次状态更新时存储完整消息列表。对于长对话，这导致 O(N²) 的存储增长（N 条消息，第 k 次更新存储 k 条消息）。

### 解决方案

`DeltaChannel` 使用增量存储：

- 每50条消息生成一次完整快照（`snapshot_frequency=50`）
- 快照之间只存储增量（新增/修改的消息）
- 将检查点增长从 O(N²) 降至 O(N)

这对于长周期代理（可能运行数百轮对话）至关重要。

## 私有状态字段

中间件可通过 `state_schema` 贡献额外的类型化状态字段。`private_state_field_names()` 函数识别标记为 `PrivateStateAttr` 的字段，这些字段：

- 不会泄漏到子代理状态中
- 在子代理返回结果时被排除
- 仅对拥有它们的中间件可见

这防止了内部中间件状态意外传播到子代理或返回给父代理。

## 相关概念

- [规划与子代理](/langchain-ai/deepagents/concepts/planning-subagents) — 子代理状态隔离机制
- [后端系统](/langchain-ai/deepagents/references/backends) — 摘要卸载和技能加载依赖的存储抽象
- [中间件栈](/langchain-ai/deepagents/references/middleware-stack) — 摘要/技能/内存中间件在栈中的位置
