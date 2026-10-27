---
type: Concept
title: MCP Skills 与工作事件契约
date: 2026-10-27
stale_after: 2026-12-31
sources:
  - id: mcp
    resource: https://modelcontextprotocol.io/docs/learn/architecture
  - id: skills
    resource: https://agentskills.io/specification
  - id: security
    resource: https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices
  - id: event
    resource: https://www.kanzan.top/zh/blog/agent-eventtype-work-language
  - id: feed
    resource: https://www.kanzan.top/zh/blog/event-feed-ai-workspace
  - id: facts
    resource: ../references/facts.md
---

# MCP Skills 与工作事件契约

MCP 接口、Skill 方法与 EventType 组织规则解决不同问题。把三者分开，才能判断一次 Agent 行为究竟缺少连接能力、任务指导，还是执行授权。

本页依据 2026-10-27 取得的动态 MCP 架构与固定 `2025-11-25` 安全参考，不把两者拼成同版完整实现。执行前核对宿主支持的协议与权限；来源口径与复核触发器见[核验记录](../references/verification.md)。

## MCP 的连接角色

官方架构定义三个参与方：[F-015～F-017](../references/facts.md)

| 角色 | 职责 | 教学例子 |
|---|---|---|
| Host | 协调和管理 MCP Clients 的 AI 应用 | 用户使用的工作台 |
| Client | 维护与某个 Server 的连接 | 工作台为资料服务建立的连接组件 |
| Server | 提供上下文和操作能力的程序 | 资料检索或业务工具服务 |

Server 可提供 Tools、Resources、Prompts。Tools 用于操作，Resources 提供上下文数据，Prompts 是可复用交互模板。提供 Prompt 不意味着它已执行，更不意味着系统可以越权发布或写数据库。

MCP 标准化上下文交换，不规定模型如何推理或应用如何管理上下文。换模型后仍需验证工具选择、参数、失败处理和输出质量；接入多个 Server 后仍需确认支持的功能与版本。不要把“协议一致”解释为“行为一致”。

## Skill 的方法包装

Agent Skills 权威规范要求目录至少有 `SKILL.md`，其中 YAML frontmatter 包含 `name`、`description`，后接 Markdown 指令。`scripts/`、`references/`、`assets/` 是可选资源；元数据、完整指令与附加资源按需加载。[F-018、F-019](../references/facts.md)

Kanzan 博文使用的 `Skill.md` 应校正为标准文件名 `SKILL.md`。格式规范中的建议长度不是所有宿主共有的上下文上限。Skill 能说明“什么时候做、怎样做、怎样验收”，但实际工具能否使用、文件能否读取，仍由宿主和执行环境决定。

| 问题 | 主要对应层 | 仍需补齐什么 |
|---|---|---|
| 能否检索某类资料 | MCP 或其他数据接口 | 数据授权和实际连通验证 |
| 怎样整理一份材料 | Skill 或任务工作流 | 输入质量和结果验收 |
| 能否修改组织事件类型 | 业务治理规则 | 服务端权限与审批 |
| 能否自动对外发布 | 发布权限和风险策略 | 审核、审计、撤回路径 |

## 安全不能由文件格式代办

MCP 安全参考要求本地 Server 启动前取得同意，并建议隔离进程、限制文件和网络访问、采用最小权限。[F-050](../references/facts.md) 启动同意不等于每次工具调用都需要相同的确认流程。因此，MCP 本身不会自动沙箱执行或脱敏。Skill 包携带脚本也不表示脚本可信。

本包的安全设计建议是先只授予必要读取权限，对高风险操作另行确认后再提升权限；这不是从启动同意推导出的逐次确认规范。令牌不得因方便而混用受众，私密内容不应先送到模型后才尝试删除。执行授权要在实际执行点检查，不靠自然语言约定兜底。

## 从交流到事件再到记忆

OPC Feed 的作者设计区分 Message、Event、MemoryFact：[F-020](../references/facts.md)

| 层次 | 意义 | 本包教学示例 |
|---|---|---|
| Message | 一次交流的原料 | “也许下周可以交付” |
| Event | 需要记录的工作变化 | 负责人确认交付日期 |
| MemoryFact | 可持续使用的稳定事实 | 已确认的长期业务规则 |

示例不是产品实测数据。把一句试探当承诺、把一次意见当永久偏好，都会让记忆偏离上下文。建议先保留出处、确认状态与有效期，再决定是否提升为事件或稳定事实。不同类别的撤销、更正和失效应可追踪。

## EventType 的权力边界

作者讨论 EventType 对可见性、创建、审批、通知和触发的影响，并主张普通 Agent 使用既有类型，修改类型则走治理审批。[F-021、F-022](../references/facts.md) 类型变更会影响后续解释和执行，不能视为普通内容编辑。

下表是本包教学设计，不是 OPC Feed 已发布 API：

| 动作 | 建议权限 | 验收 |
|---|---|---|
| 列出允许的事件类型 | 普通读取权限 | 不暴露无权查看的类型或内容 |
| 按既有类型创建事件 | 任务范围内权限 | 输入校验、来源记录、查重 |
| 提议新增类型 | 提案权限 | 说明用途、影响与版本 |
| 修改类型规则 | 治理权限 | 审批、旧事件兼容与回退 |
| 从事件提炼长期记忆 | 独立确认规则 | 支撑事件、争议处理、失效条件 |

博文讨论的工具名称不能作为经验证的接口直接调用。实际接入前要查产品文档、权限模型与返回值，本次没有进行这些运行验证。

下一篇：[产品与工业边界](03-products-and-industrial-boundaries.md)。返回[总览](../index.md)。
