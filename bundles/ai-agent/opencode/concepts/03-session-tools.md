---
type: Concept
title: 会话模型与工具系统
description: OpenCode V2 会话模型（SessionV2）、Context Epoch、自动压缩、工具注册表、内置工具和权限系统
tags: [session, tool, context-epoch, compaction, permission, agent]
generated:
  by: "reference_agent/trae-cn"
  at: 2026-08-23T10:00:00+08:00
verified:
  by: "process:grep-verification"
  at: 2026-08-23T10:00:00+08:00
status: stable
stale_after: 2027-08-23
sources:
  - /references/source.md
---

# 会话模型与工具系统

## V2 会话模型

V2 会话核心将 prompt 录入与模型执行严格分离。核心 API 定义在 `specs/v2/session.md`。

### 会话生命周期 API

```text
sessions.create({ id?, location, ... })
  -> 省略 ID 时自动生成内部会话 ID
  -> 提供 ID 时在不存在时创建会话
  -> 复用 ID 时返回现有会话身份

sessions.prompt({ id?, sessionID, prompt, delivery?, resume? })
  -> 省略 ID 时自动生成消息 ID
  -> 提供 ID 时在不存在时插入持久化收件箱行
  -> 精确复用返回相同录入回执
  -> resume 省略或 true 时录入后调度执行
  -> resume: false 时仅录入不执行

sessions.interrupt(sessionID)
  -> 中断当前进程上的活跃执行
  -> 等待运行器清理和结算
  -> 空闲或缺失会话为空操作

sessions.active()
  -> 快照当前进程拥有的前台会话排干
  -> 返回活跃会话 ID 及 { type: "running" }
  -> 进程重启后为空
```

### 持久化录入与提升

- `session_input` 表是持久化录入收件箱
- `PromptAdmitted` 事件记录已接受的输入，待处理队列状态可被重放、复制和观察
- 已录入输入在序列化运行器发布 `Prompted` 事件前不属于模型可见的会话历史
- `Prompted` 事件的投影器在同一事件事务中原子地写入可见用户消息并标记收件箱行已提升

### 投递模式

- **steer**：在当前排干需要继续时，在下一个安全 provider-turn 边界提升
- **queue**：在当前排干需要继续时保持在 FIFO 队列中；会话空闲时逐个提升

### 执行路由

```text
SessionExecution.resume(sessionID)
-> SessionStore.get(sessionID)
-> LocationServiceMap.get(session.location)
-> SessionRunner.run({ sessionID, force? })
```

- `SessionExecution` 和 `SessionStore` 为进程全局
- `SessionRunner`、目录、模型解析器、工具注册表、权限状态、文件系统按 Location 缓存
- 进程全局 `SessionRunCoordinator` 序列化每个本地会话的执行，允许不同会话并发

## Context Epoch（上下文纪元）

V2 会话持久化展示给模型的精确特权 System Context。一个 Context Epoch 存储：

- 一个不可变的 provider-cache 基线（Baseline System Context）
- 一个模型隐藏的结构化快照（Context Snapshot），用于比较独立观察的 Context Source

### 初始上下文来源

1. 环境事实（Environment facts）
2. 主机本地日期
3. 全局和向上项目 `AGENTS.md` 文件
4. 选中 agent 的可用技能引导

### 上下文变更流程

- 第一次完整观察在任何待处理 prompt 变为模型可见前初始化纪元
- 如果初始上下文暂时不可用，执行停止，prompt 保持待处理可重试
- 在后续 provider turn 中，运行器先提升合格输入，再在安全边界协调当前来源
- 变更的上下文成为一条持久化的时序系统消息（Mid-Conversation System Message）
- 其事件提交原子地推进纪元快照

### 纪元终止条件

- 完成压缩（compaction）后开始新纪元
- 会话移动（Location move）后清除纪元，目标位置在下次运行时初始化完整基线
- 模型/provider 切换保留当前纪元

## 自动压缩

在每个 provider turn 前，运行器估算完整的模型可见请求，并与所选模型的上下文窗口减去预留空间进行比较。

- 预留空间为请求/模型输出配额和配置的 `compaction.buffer` 中的较大值
- 压缩保留完整转录的持久性，同时将其活跃模型表示替换为一个隐藏检查点
- Provider-native 的 assistant、reasoning 和 tool 消息不会跨越边界存活
- 压缩事件 `session.next.compaction.started.1` 和 `session.next.compaction.ended.1` 持久化标识
- 当 provider 以上下文溢出拒绝请求时，运行器尝试一次溢出触发的压缩

## V2 工具系统

工具系统规范定义在 `specs/v2/tools.md`。

### 工具定义

```ts
type Definition<Input, Output>

const make = <Input extends Schema.Codec, Output extends Schema.Codec>(config: {
  readonly description: string
  readonly input: Input
  readonly output: Output
  readonly execute: (input, context: Tool.Context) => Effect.Effect<Output, ToolFailure>
  readonly toModelOutput?: (input, output) => ReadonlyArray<Tool.Content>
}) => Definition<Input, Output>
```

- `Tool.Definition` 是不透明类型，只有一个执行器
- 输入和输出编解码器是自包含的，Schema 转换不需要服务
- 工具依赖在构造期间获取并由 `execute` 捕获

### 调用上下文

```ts
interface Tool.Context {
  readonly sessionID: Session.ID
  readonly agent: Agent.ID
  readonly assistantMessageID: Session.MessageID
  readonly toolCallID: ToolCall.ID
}
```

### 注册与作用域

- 工具在注册时命名，record key 为模型面向名称
- 进程应用工具和 Location 工具使用相同的 `register` 操作但保留独立的服务和存储
- Location 注册优先于进程应用注册
- 同一位置中，最新活跃注册获胜；关闭注册仅移除该注册

### 执行流程

1. 解析一个有效的命名注册
2. 使用输入编解码器解码 provider 输入
3. 使用运行器提供的上下文调用工具
4. 使用输出编解码器编码返回的输出
5. 将编码输出投影为模型面向内容
6. 限制完整模型面向输出的大小
7. 将结算和托管输出引用返回给运行器持久化

### 输出限制

- 工具返回完整的经验证领域输出，不自行截断
- 在投影后，一个通用结算边界限制实际发送给 provider 的通道
- 超大文本或结构化输出保留在托管存储中，替换为有界文本预览
- 结构化元数据和媒体保持不变
- 如果完整保留失败，结算在操作层面失败

### 失败语义

- `ToolFailure`：预期的模型可见失败
- 中断（Interruption）：取消调用，不是工具结果
- 意外类型错误和缺陷：遵循运行器的操作失败策略
- 未知、无效和过期调用：显式的模型可见结算错误，不调用处理器

### 七条法则

1. **单一执行器**：`Tool.make(config)` 只能调用 `config.execute`
2. **编解码器边界**：执行观察解码后输入；投影观察编码后输出
3. **持久化身份**：调用拥有的记录使用运行器提供的精确 Session、agent、assistant message 和 call ID
4. **作用域注册**：关闭 Scope 精确移除其注册并揭示先前的活跃覆盖
5. **捕获执行**：注册变更不能在有效查找后改变调用
6. **过期拒绝**：调用永不执行非其 provider turn 所通告的注册
7. **存储封装**：领域输出不因模型输出限制或保留策略而改变

## 内置工具

OpenCode 包含以下内置工具（源码位于 `packages/opencode/src/tool/`）：

| 工具 | 说明 |
|------|------|
| `bash` | Shell 命令执行，使用权限语义（ask 为默认） |
| `read` | 文件/目录读取，支持分页和路径转义防护 |
| `write` | 文件写入 |
| `edit` | 文件编辑 |
| `apply_patch` | 补丁应用（add/update/delete hunks） |
| `grep` | 文件内容搜索 |
| `glob` | 文件名模式匹配 |
| `webfetch` | 网页内容获取 |
| `websearch` | Web 搜索 |
| `todo` | 待办事项管理 |
| `todowrite` | 待办事项写入 |
| `task` | 子任务执行 |
| `skill` | 技能调用（权限过滤） |
| `lsp` | 语言服务器协议工具 |

## 权限系统

V2 权限使用有序规则集：

```jsonc
{
  "permissions": [
    { "action": "bash", "resource": "*", "effect": "ask" },
    { "action": "bash", "resource": "git status", "effect": "allow" }
  ]
}
```

- effect 支持 `"allow"`、`"deny"`、`"ask"`
- 与 `experimental.policies`（仅 allow/deny，用于 provider 控制）不同
- Bash 不做沙箱化：生成的 shell 以主机用户的文件系统、进程和网络权限运行
- 外部 `workdir` 解析需要 `external_directory` 权限检查

## 相关概念

- [OpenCode 简介](/concepts/00-introduction.md)
- [架构概览](/concepts/01-architecture.md)
- [配置系统](/concepts/02-config-system.md)
- [部署与基础设施](/concepts/04-deployment-infra.md)
